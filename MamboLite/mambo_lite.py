#!/usr/bin/env python3
"""
MamboLite - Single CSV Contact Formatter (Phase 1)

Features (Phase 1):
- Single CSV input → unified schema CSV output
- Header alias mapping via lookups/column_map_lookup.csv
- Name parsing (prefix/suffix, basic compound last names)
- Email/phone normalization
- Optional deduplication by exact email
- Optional SMTP send of the result

Out of scope: multi-file merging, fuzzy dedupe, Excel M1–M4, external API importers
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import smtplib
import sys
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd


TARGET_COLUMNS: List[str] = [
    "source",
    "full_name",
    "prefix",
    "first_name",
    "middle_name",
    "last_name",
    "suffix",
    "email",
    "email_2",
    "phone_mobile",
    "phone_work",
    "phone_home",
    "company",
    "title",
    "street",
    "street2",
    "city",
    "state",
    "postal_code",
    "country",
    "website",
    "linkedin_profile",
    "notes",
]


def log(msg: str, stream=None) -> None:
    if stream is None:
        print(msg)
    else:
        stream.write(str(msg) + "\n")
        stream.flush()


def resource_path(*relative: str) -> str:
    """Get absolute path to resource, works for dev and PyInstaller."""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return os.path.join(base, *relative)
    # fallback relative to this file
    return os.path.join(os.path.dirname(__file__), *relative)


def read_csv_with_fallback(path: str) -> pd.DataFrame:
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            continue
    # last attempt default
    return pd.read_csv(path)


def load_alias_map(lookups_dir: str) -> Dict[str, str]:
    """Load alias -> target mapping from lookups/column_map_lookup.csv

    CSV expected columns: alias,target (case-insensitive headers)
    """
    path = os.path.join(lookups_dir, "column_map_lookup.csv")
    if not os.path.exists(path):
        return {}
    df = read_csv_with_fallback(path)
    cols = {c.lower(): c for c in df.columns}
    alias_col = cols.get("alias")
    target_col = cols.get("target")
    if not alias_col or not target_col:
        return {}
    mapping: Dict[str, str] = {}
    for _, row in df.iterrows():
        alias = str(row.get(alias_col, "")).strip()
        target = str(row.get(target_col, "")).strip()
        if alias and target:
            mapping[alias.lower()] = target.lower()
    return mapping


def load_set_file(path: str) -> Set[str]:
    s: Set[str] = set()
    if not os.path.exists(path):
        return s
    df = read_csv_with_fallback(path)
    if df.empty:
        return s
    first = df.columns[0]
    for v in df[first].dropna().astype(str):
        s.add(v.strip().lower())
    return s


@dataclass
class Lookups:
    prefixes: Set[str]
    suffixes: Set[str]
    compound_tokens: Set[str]


def load_lookups(lookups_dir: str) -> Lookups:
    prefixes = load_set_file(os.path.join(lookups_dir, "prefixes.csv"))
    suffixes = load_set_file(os.path.join(lookups_dir, "suffixes.csv"))
    compound_tokens = load_set_file(os.path.join(lookups_dir, "compound_names.csv"))
    return Lookups(prefixes=prefixes, suffixes=suffixes, compound_tokens=compound_tokens)


def normalize_email(value: str) -> str:
    if not value or str(value).lower() == "nan":
        return ""
    return str(value).strip().lower()


def normalize_phone(value: str) -> str:
    if not value or str(value).lower() == "nan":
        return ""
    digits = re.sub(r"\D+", "", str(value))
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return f"{digits[0:3]}-{digits[3:6]}-{digits[6:10]}"
    # otherwise return stripped original
    return str(value).strip()


def map_headers(df: pd.DataFrame, alias_map: Dict[str, str]) -> pd.DataFrame:
    col_map: Dict[str, str] = {}
    for col in df.columns:
        key = str(col).strip().lower()
        target = alias_map.get(key)
        if target:
            col_map[col] = target
        else:
            # allow direct pass-through if already a target name
            if key in TARGET_COLUMNS:
                col_map[col] = key
    if col_map:
        df = df.rename(columns=col_map)
    return df


def split_full_name(full_name: str, lookups: Lookups) -> Tuple[str, str, str, str, str]:
    """Return prefix, first, middle, last, suffix from a full name string.
    Heuristics only; adequate for Phase 1.
    """
    if not full_name or str(full_name).lower() == "nan":
        return "", "", "", "", ""
    name = str(full_name).strip()
    suffix = ""
    prefix = ""

    # handle comma-separated Last, First Middle Suffix
    if "," in name:
        left, right = [p.strip() for p in name.split(",", 1)]
        # detect suffix on rightmost token
        right_tokens = right.split()
        if right_tokens and right_tokens[-1].lower().rstrip(".") in lookups.suffixes:
            suffix = right_tokens[-1]
            right_tokens = right_tokens[:-1]
        # detect prefix on right tokens start
        if right_tokens and right_tokens[0].lower().rstrip(".") in lookups.prefixes:
            prefix = right_tokens[0]
            right_tokens = right_tokens[1:]
        first = right_tokens[0] if right_tokens else ""
        middle = " ".join(right_tokens[1:]) if len(right_tokens) > 1 else ""
        last = left
        return prefix, first, middle, last, suffix

    # space-separated
    tokens = name.split()
    if not tokens:
        return "", "", "", "", ""

    # prefix
    if tokens and tokens[0].lower().rstrip(".") in lookups.prefixes:
        prefix = tokens[0]
        tokens = tokens[1:]

    # suffix
    if tokens and tokens[-1].lower().rstrip(".") in lookups.suffixes:
        suffix = tokens[-1]
        tokens = tokens[:-1]

    if not tokens:
        return prefix, "", "", "", suffix

    # Identify last name including compound tokens before the last part
    last_parts = [tokens[-1]]
    i = len(tokens) - 2
    while i >= 0 and tokens[i].lower() in lookups.compound_tokens:
        last_parts.insert(0, tokens[i])
        i -= 1
    first = tokens[0] if tokens else ""
    middle = " ".join(tokens[1 : i + 1]) if i >= 1 else (tokens[1] if len(tokens) == 3 else "")
    last = " ".join(last_parts)
    return prefix, first, middle, last, suffix


def ensure_columns(df: pd.DataFrame, source_label: str) -> pd.DataFrame:
    for col in TARGET_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    if source_label:
        df["source"] = source_label
    return df


def apply_normalization(df: pd.DataFrame, lookups: Lookups, source_label: str) -> pd.DataFrame:
    df = ensure_columns(df, source_label)

    # Name parsing when first/last missing but full_name exists
    for idx, row in df.iterrows():
        first = str(row.get("first_name", "")).strip()
        last = str(row.get("last_name", "")).strip()
        full = str(row.get("full_name", "")).strip()
        if (not first or first.lower() == "nan") or (not last or last.lower() == "nan"):
            if full:
                pfx, fn, mn, ln, sfx = split_full_name(full, lookups)
                if not first:
                    df.at[idx, "first_name"] = fn
                if not row.get("middle_name"):
                    df.at[idx, "middle_name"] = mn
                if not last:
                    df.at[idx, "last_name"] = ln
                if not row.get("prefix") and pfx:
                    df.at[idx, "prefix"] = pfx
                if not row.get("suffix") and sfx:
                    df.at[idx, "suffix"] = sfx

    # Email normalization and fallback mapping
    for idx, row in df.iterrows():
        for col in ("email", "email_2"):
            df.at[idx, col] = normalize_email(row.get(col, ""))

    # Phone normalization
    for idx, row in df.iterrows():
        for col in ("phone_mobile", "phone_work", "phone_home"):
            df.at[idx, col] = normalize_phone(row.get(col, ""))

    # Title case for names where applicable (keep lowercase for emails)
    for col in ("prefix", "first_name", "middle_name", "last_name", "suffix"):
        df[col] = df[col].fillna("").apply(lambda s: s.title() if isinstance(s, str) else s)

    return df


def dedupe_by_email(df: pd.DataFrame) -> pd.DataFrame:
    if "email" not in df.columns:
        return df
    return df.sort_index().drop_duplicates(subset=["email"], keep="first")


def write_csv(df: pd.DataFrame, path: str) -> None:
    # Ensure consistent column order
    for col in TARGET_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df[TARGET_COLUMNS].to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL)


def send_email_with_attachment(smtp_config_path: str, recipient: str, attachment_path: str, logger=None) -> None:
    with open(smtp_config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    host = cfg.get("host")
    port = int(cfg.get("port", 587))
    user = cfg.get("username")
    password = cfg.get("password")
    use_tls = bool(cfg.get("use_tls", True))
    use_ssl = bool(cfg.get("use_ssl", False))
    sender = cfg.get("sender") or user
    subject = cfg.get("subject", "MamboLite formatted contacts")
    body = cfg.get("body", "Please find the formatted contacts attached.")

    if not host or not sender:
        raise ValueError("SMTP config must include host and sender (or username).")

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    with open(attachment_path, "rb") as f:
        data = f.read()
    msg.add_attachment(data, maintype="text", subtype="csv", filename=os.path.basename(attachment_path))

    if use_ssl:
        server = smtplib.SMTP_SSL(host, port)
    else:
        server = smtplib.SMTP(host, port)
    try:
        server.ehlo()
        if use_tls and not use_ssl:
            server.starttls()
            server.ehlo()
        if user and password:
            server.login(user, password)
        server.send_message(msg)
    finally:
        server.quit()
    if logger:
        log(f"Email sent to {recipient}", logger)


def send_via_outlook(recipient: str, attachment_path: str, subject: str, body: str, logger=None) -> None:
    try:
        import win32com.client  # type: ignore
    except Exception as e:
        raise RuntimeError("Outlook (pywin32) is not installed or unavailable.") from e

    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.To = recipient
    mail.Subject = subject
    mail.Body = body
    if attachment_path and os.path.exists(attachment_path):
        mail.Attachments.Add(os.path.abspath(attachment_path))
    mail.Send()
    if logger:
        log(f"Outlook email sent to {recipient}", logger)


def process(
    input_path: str,
    lookups_dir: str,
    output_path: str,
    source_label: str,
    dedupe_email: bool,
    email_to: Optional[str] = None,
    smtp_config_path: Optional[str] = None,
    email_method: str = "smtp",
    logger=None,
) -> str:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input CSV not found: {input_path}")
    if not os.path.isdir(lookups_dir):
        raise FileNotFoundError(f"Lookups folder not found: {lookups_dir}")

    alias_map = load_alias_map(lookups_dir)
    lookups = load_lookups(lookups_dir)

    log("Loading CSV...", logger)
    df = read_csv_with_fallback(input_path)
    log(f"Loaded {len(df)} rows", logger)

    log("Mapping headers...", logger)
    df = map_headers(df, alias_map)

    log("Normalizing fields...", logger)
    df = apply_normalization(df, lookups, source_label)

    if dedupe_email:
        before = len(df)
        df = dedupe_by_email(df)
        log(f"Deduplicated by email: {before} -> {len(df)}", logger)

    # Ensure directory exists for output
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    log(f"Writing CSV -> {output_path}", logger)
    write_csv(df, output_path)

    if email_to:
        log("Sending email...", logger)
        if email_method.lower() == "outlook":
            send_via_outlook(
                recipient=email_to,
                attachment_path=output_path,
                subject="MamboLite formatted contacts",
                body="Please find the formatted contacts attached.",
                logger=logger,
            )
        else:
            if not smtp_config_path:
                raise ValueError("SMTP method selected but --smtp not provided")
            send_email_with_attachment(smtp_config_path, email_to, output_path, logger)

    log("Done.", logger)
    return output_path


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="MamboLite - single CSV contact formatter")
    p.add_argument("--input", required=True, help="Path to input contacts CSV")
    p.add_argument("--output", default="formatted_contacts.csv", help="Path to output CSV")
    p.add_argument("--lookups", default=resource_path("lookups"), help="Path to lookups folder")
    p.add_argument("--source", default="", help="Source label (e.g., Gmail, iPhone)")
    p.add_argument("--no-dedupe", action="store_true", help="Disable deduplication by email")
    p.add_argument("--email", default=None, help="Recipient email address to send result")
    p.add_argument("--smtp", default=None, help="Path to SMTP JSON config (when --email-method smtp)")
    p.add_argument("--email-method", choices=["smtp", "outlook"], default="smtp", help="Email method: smtp or outlook (Windows)")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        process(
            input_path=args.input,
            lookups_dir=args.lookups,
            output_path=args.output,
            source_label=args.source,
            dedupe_email=not args.no_dedupe,
            email_to=args.email,
            smtp_config_path=args.smtp,
            email_method=args.email_method,
        )
        return 0
    except Exception as e:
        log(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
