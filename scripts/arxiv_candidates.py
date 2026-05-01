#!/usr/bin/env python3
"""Fetch arXiv candidates and maintain a local seen-ID state file."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"
# arXiv documents this Atom API over HTTP. Using HTTP avoids failures on
# macOS Python installs whose OpenSSL certificate bundle is not initialized.
API_URL = "http://export.arxiv.org/api/query"


def parse_dt(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return dt.datetime.fromisoformat(value)
    except ValueError:
        return None


def arxiv_id_from_url(url: str) -> str:
    tail = url.rstrip("/").split("/")[-1]
    if "v" in tail:
        base, version = tail.rsplit("v", 1)
        if version.isdigit():
            return base
    return tail


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"seen": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"seen": {}}
    if not isinstance(data, dict):
        return {"seen": {}}
    if not isinstance(data.get("seen"), dict):
        data["seen"] = {}
    return data


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def build_query(categories: list[str]) -> str:
    return " OR ".join(f"cat:{category.strip()}" for category in categories if category.strip())


def fetch_feed(categories: list[str], max_results: int) -> bytes:
    params = {
        "search_query": build_query(categories),
        "start": "0",
        "max_results": str(max_results),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = API_URL + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "arxiv-daily-digest/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return response.read()
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", None)
        if not isinstance(reason, ssl.SSLCertVerificationError):
            raise

    try:
        import certifi  # type: ignore

        context = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(request, timeout=45, context=context) as response:
            return response.read()
    except (ImportError, urllib.error.URLError):
        print(
            "warning: local Python certificate verification failed; "
            "retrying arXiv public metadata request without certificate verification",
            file=sys.stderr,
        )
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(request, timeout=45, context=context) as response:
            return response.read()


def parse_entry(entry: ET.Element) -> dict[str, Any]:
    entry_id = entry.findtext(f"{ATOM}id") or ""
    title = " ".join((entry.findtext(f"{ATOM}title") or "").split())
    summary = " ".join((entry.findtext(f"{ATOM}summary") or "").split())
    published_raw = entry.findtext(f"{ATOM}published")
    updated_raw = entry.findtext(f"{ATOM}updated")
    published = parse_dt(published_raw)
    updated = parse_dt(updated_raw)
    authors = [a.findtext(f"{ATOM}name") or "" for a in entry.findall(f"{ATOM}author")]
    authors = [a for a in authors if a]
    primary_el = entry.find(f"{ARXIV}primary_category")
    primary = primary_el.attrib.get("term", "") if primary_el is not None else ""
    categories = [c.attrib.get("term", "") for c in entry.findall(f"{ATOM}category")]
    categories = [c for c in categories if c]
    abs_url = entry_id
    pdf_url = ""
    for link in entry.findall(f"{ATOM}link"):
        attrs = link.attrib
        if attrs.get("title") == "pdf" or attrs.get("type") == "application/pdf":
            pdf_url = attrs.get("href", "")
        elif attrs.get("rel") == "alternate":
            abs_url = attrs.get("href", abs_url)
    paper_id = arxiv_id_from_url(entry_id)
    return {
        "arxiv_id": paper_id,
        "title": title,
        "authors": authors,
        "published": published.isoformat() if published else published_raw,
        "updated": updated.isoformat() if updated else updated_raw,
        "primary_category": primary,
        "categories": categories,
        "abstract_url": abs_url,
        "pdf_url": pdf_url,
        "summary": summary,
    }


def fetch_candidates(args: argparse.Namespace) -> int:
    categories = [c.strip() for c in args.categories.split(",") if c.strip()]
    if not categories:
        print("No categories supplied", file=sys.stderr)
        return 2

    state_path = Path(os.path.expanduser(args.state_file))
    state = load_state(state_path)
    seen = set(state.get("seen", {}).keys())
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=args.days)

    feed = fetch_feed(categories, args.max_results)
    root = ET.fromstring(feed)
    entries = []
    duplicate_count = 0
    old_count = 0
    for entry in root.findall(f"{ATOM}entry"):
        item = parse_entry(entry)
        paper_id = item["arxiv_id"]
        dates = [parse_dt(item.get("published")), parse_dt(item.get("updated"))]
        recent_dates = [d for d in dates if d is not None]
        if recent_dates and max(recent_dates) < cutoff:
            old_count += 1
            continue
        if paper_id in seen and not args.include_seen:
            duplicate_count += 1
            continue
        item["matched_categories"] = sorted(set(categories).intersection(item.get("categories", [])))
        entries.append(item)

    output = {
        "categories": categories,
        "days": args.days,
        "candidate_count": len(entries),
        "skipped_seen": duplicate_count,
        "skipped_old": old_count,
        "candidates": entries,
    }
    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


def mark_seen(args: argparse.Namespace) -> int:
    state_path = Path(os.path.expanduser(args.state_file))
    state = load_state(state_path)
    seen = state.setdefault("seen", {})
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    for paper_id in args.arxiv_ids:
        seen[paper_id] = {"marked_at": now}
    save_state(state_path, state)
    print(json.dumps({"marked": args.arxiv_ids, "state_file": str(state_path)}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch arXiv candidates and manage seen IDs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch = subparsers.add_parser("fetch", help="Fetch recent arXiv candidates")
    fetch.add_argument("--categories", required=True, help="Comma-separated arXiv categories")
    fetch.add_argument("--days", type=float, default=2.0, help="Lookback window in days")
    fetch.add_argument("--max-results", type=int, default=100, help="Max arXiv API results")
    fetch.add_argument("--state-file", default="~/.local/state/arxiv-daily-digest/seen.json")
    fetch.add_argument("--include-seen", action="store_true", help="Do not filter local seen IDs")
    fetch.set_defaults(func=fetch_candidates)

    mark = subparsers.add_parser("mark-seen", help="Mark arXiv IDs as seen")
    mark.add_argument("--state-file", default="~/.local/state/arxiv-daily-digest/seen.json")
    mark.add_argument("arxiv_ids", nargs="+")
    mark.set_defaults(func=mark_seen)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
