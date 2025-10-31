#!/usr/bin/env python3
"""
Create a GitHub Release and upload assets.

Usage:
  export GH_TOKEN=ghp_yourtoken
  python create_release.py --repo owner/repo --tag v0.1.0 --title "MamboLite v0.1.0" \
      --notes "Phase 1: CLI + GUI + SMTP/Outlook" \
      --assets dist/MamboLite.exe dist/MamboLiteCLI.exe MamboLite/docs/SOW.pdf
"""

import argparse
import os
import sys
from typing import List

import requests


def parse_repo(repo: str):
    if "/" not in repo:
        raise ValueError("--repo must be owner/repo")
    return repo.split("/", 1)


def create_release(session: requests.Session, owner: str, repo: str, tag: str, title: str, notes: str):
    r = session.post(
        f"https://api.github.com/repos/{owner}/{repo}/releases",
        json={
            "tag_name": tag,
            "name": title,
            "body": notes,
            "draft": False,
            "prerelease": False,
        },
    )
    r.raise_for_status()
    return r.json()


def upload_asset(session: requests.Session, upload_url: str, path: str):
    url = upload_url.split("{", 1)[0]
    name = os.path.basename(path)
    with open(path, "rb") as f:
        data = f.read()
    headers = {"Content-Type": "application/octet-stream"}
    r = session.post(f"{url}?name={name}", headers=headers, data=data)
    r.raise_for_status()
    return r.json()


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Create GitHub release and upload assets")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--notes", default="")
    ap.add_argument("--assets", nargs="*", default=[])
    ap.add_argument("--token", default=os.environ.get("GH_TOKEN"))
    args = ap.parse_args(argv)

    if not args.token:
        print("ERROR: Provide --token or set GH_TOKEN", file=sys.stderr)
        return 2
    owner, repo = parse_repo(args.repo)
    session = requests.Session()
    session.headers.update({
        "Authorization": f"token {args.token}",
        "Accept": "application/vnd.github+json",
    })

    rel = create_release(session, owner, repo, args.tag, args.title, args.notes)
    upload_url = rel.get("upload_url")
    for asset in args.assets:
        if not os.path.exists(asset):
            print(f"WARN: asset not found: {asset}")
            continue
        print(f"Uploading {asset}...")
        upload_asset(session, upload_url, asset)
    print(f"Release created: {rel.get('html_url')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

