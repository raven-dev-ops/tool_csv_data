#!/usr/bin/env python3
"""
Export timeline and tasks into a GitHub Project (classic), with columns, milestones,
and issues created from a YAML plan. Requires a GitHub token.

Usage:
  export GH_TOKEN=ghp_yourtoken
  python export_kanban.py --repo owner/repo --project-name "MamboLite Phase 1" --plan project_plan.yml

Notes:
- This uses classic Projects (REST API). Ensure the repo has Projects enabled.
- Token scopes: repo, project
"""

import argparse
import os
import sys
from typing import Any, Dict, List, Optional

import requests

try:
    import yaml  # type: ignore
except Exception:  # lightweight loader fallback
    yaml = None


API = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github.inertia+json",
}


def auth_headers(token: str) -> Dict[str, str]:
    h = dict(HEADERS)
    h["Authorization"] = f"token {token}"
    return h


def load_yaml(path: str) -> Dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML not installed. pip install pyyaml or provide JSON.")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_or_create_project(session: requests.Session, owner: str, repo: str, name: str, desc: str) -> Dict[str, Any]:
    # list existing
    r = session.get(f"{API}/repos/{owner}/{repo}/projects")
    r.raise_for_status()
    for p in r.json():
        if p.get("name") == name:
            return p
    # create
    r = session.post(f"{API}/repos/{owner}/{repo}/projects", json={"name": name, "body": desc})
    r.raise_for_status()
    return r.json()


def ensure_columns(session: requests.Session, project_id: int, names: List[str]) -> Dict[str, int]:
    r = session.get(f"{API}/projects/{project_id}/columns")
    r.raise_for_status()
    existing = {c["name"]: c["id"] for c in r.json()}
    result: Dict[str, int] = {}
    for n in names:
        if n in existing:
            result[n] = existing[n]
        else:
            rr = session.post(f"{API}/projects/{project_id}/columns", json={"name": n})
            rr.raise_for_status()
            result[n] = rr.json()["id"]
    return result


def ensure_milestone(session: requests.Session, owner: str, repo: str, title: str, due_on: Optional[str]) -> Dict[str, Any]:
    r = session.get(f"{API}/repos/{owner}/{repo}/milestones?state=all")
    r.raise_for_status()
    for m in r.json():
        if m.get("title") == title:
            return m
    payload = {"title": title}
    if due_on:
        payload["due_on"] = due_on
    r = session.post(f"{API}/repos/{owner}/{repo}/milestones", json=payload)
    r.raise_for_status()
    return r.json()


def create_issue(session: requests.Session, owner: str, repo: str, title: str, body: str, labels: List[str], milestone_number: Optional[int]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"title": title, "body": body, "labels": labels}
    if milestone_number:
        payload["milestone"] = milestone_number
    r = session.post(f"{API}/repos/{owner}/{repo}/issues", json=payload)
    r.raise_for_status()
    return r.json()


def add_issue_to_column(session: requests.Session, column_id: int, issue_id: int) -> None:
    r = session.post(f"{API}/projects/columns/{column_id}/cards", json={"content_id": issue_id, "content_type": "Issue"})
    r.raise_for_status()


def parse_repo(repo: str) -> (str, str):
    if "/" not in repo:
        raise ValueError("--repo must be in the form owner/repo")
    owner, name = repo.split("/", 1)
    return owner, name


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Export tasks into a GitHub Project (classic)")
    ap.add_argument("--repo", required=True, help="owner/repo")
    ap.add_argument("--project-name", required=True, help="Project name")
    ap.add_argument("--plan", required=True, help="YAML plan file")
    ap.add_argument("--token", default=os.environ.get("GH_TOKEN"), help="GitHub token (or set GH_TOKEN)")
    ap.add_argument("--dry-run", action="store_true", help="Print actions without calling API")
    args = ap.parse_args(argv)

    if not args.token and not args.dry_run:
        print("ERROR: Provide --token or set GH_TOKEN", file=sys.stderr)
        return 2

    plan = load_yaml(args.plan)
    owner, repo = parse_repo(args.repo)

    project_name = plan.get("project", {}).get("name") or args.project_name
    description = plan.get("project", {}).get("description", "")
    columns = plan.get("project", {}).get("columns", ["Backlog", "Ready", "In Progress", "In Review", "Done"])
    milestones = plan.get("milestones", [])
    issues = plan.get("issues", [])

    if args.dry_run:
        print(f"Would create project '{project_name}' with columns {columns}")
        print(f"Would create {len(milestones)} milestones and {len(issues)} issues")
        return 0

    session = requests.Session()
    session.headers.update(auth_headers(args.token))

    project = get_or_create_project(session, owner, repo, project_name, description)
    project_id = project["id"]
    column_ids = ensure_columns(session, project_id, columns)

    milestone_numbers: Dict[str, int] = {}
    for m in milestones:
        mi = ensure_milestone(session, owner, repo, m.get("title"), m.get("due_on"))
        milestone_numbers[mi["title"]] = mi["number"]

    for it in issues:
        title = it.get("title")
        body = it.get("body", "")
        labels = it.get("labels", [])
        ms_title = it.get("milestone")
        col_name = it.get("column", columns[0])
        ms_number = milestone_numbers.get(ms_title)

        created = create_issue(session, owner, repo, title, body, labels, ms_number)
        issue_id = created.get("id")
        col_id = column_ids.get(col_name)
        if col_id and issue_id:
            add_issue_to_column(session, col_id, issue_id)
        print(f"Created issue #{created.get('number')}: {title} → column '{col_name}'")

    print("All done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
