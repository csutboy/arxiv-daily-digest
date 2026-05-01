#!/usr/bin/env python3
"""Fetch Anthropic Research candidates and maintain a shared seen-ID state file."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import http.client
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_SOURCES = [
    "https://www.anthropic.com/research",
    "https://www.anthropic.com/research/team/economic-research",
    "https://www.anthropic.com/research/team/societal-impacts",
]

DEFAULT_KEYWORDS = [
    "economic",
    "economics",
    "labor",
    "labour",
    "work",
    "workforce",
    "productivity",
    "market",
    "business",
    "job",
    "professionals",
    "enterprise",
    "geography",
    "societal",
    "society",
    "social",
    "values",
    "personal guidance",
    "autonomy",
    "ai use",
    "impact",
]

MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


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


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 arxiv-daily-digest/1.0",
            "Accept-Encoding": "identity",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return response.read().decode("utf-8", "replace")
    except http.client.IncompleteRead as exc:
        return exc.partial.decode("utf-8", "replace")
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", None)
        if not isinstance(reason, ssl.SSLError):
            raise

    print(
        "warning: local Python TLS verification/handshake failed; "
        "retrying Anthropic public page request without certificate verification",
        file=sys.stderr,
    )
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(request, timeout=45, context=context) as response:
        try:
            return response.read().decode("utf-8", "replace")
        except http.client.IncompleteRead as exc:
            return exc.partial.decode("utf-8", "replace")


def strip_tags(value: str) -> str:
    value = re.sub(r"<script\b.*?</script>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<style\b.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return " ".join(html.unescape(value).split())


def slug_from_url(url: str) -> str:
    return urllib.parse.urlparse(url).path.rstrip("/").split("/")[-1]


def infer_team(text: str, source_url: str) -> str:
    if "Economic Research" in text or "economic-research" in source_url:
        return "Economic Research"
    if "Societal Impacts" in text or "societal-impacts" in source_url:
        return "Societal Impacts"
    return "Anthropic Research"


def parse_date(text: str) -> str | None:
    match = re.search(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),\s+(20\d{2})\b", text)
    if not match:
        return None
    month, day, year = match.groups()
    return dt.date(int(year), MONTHS[month], int(day)).isoformat()


def clean_title(text: str) -> str:
    leading_date = re.match(r"\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+20\d{2}\b", text)
    if leading_date:
        text = text[leading_date.end() :]

    team_match = re.search(r"\b(Economic Research|Societal Impacts|Policy|Science|Alignment|Interpretability)\b", text)
    if team_match and team_match.start() > 0 and text[: team_match.start()].strip():
        return " ".join(text[: team_match.start()].split())

    text = re.sub(r"\b(Economic Research|Societal Impacts|Policy|Science|Alignment|Interpretability)\b", " ", text)
    text = re.sub(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+20\d{2}\b", " ", text)

    teaser_markers = [
        " This report",
        " This paper",
        " In this paper",
        " In this report",
        " Anthropic's",
        " We surveyed",
        " We present",
        " We introduce",
        " We’re",
        " We're",
        " In June",
        " Powered by",
        " Analyzing",
        " Large models",
        " These classifiers",
        " All modern",
    ]
    for marker in teaser_markers:
        index = text.find(marker)
        if index > 12:
            text = text[:index]
            break

    # Listing cards usually put title before the first sentence of the teaser.
    sentence_match = re.search(r"(?<=[a-z0-9\)])\.\s+[A-Z]", text)
    if sentence_match:
        text = text[: sentence_match.start() + 1]
    return " ".join(text.split())


def parse_links(source_url: str, html_text: str) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    pattern = re.compile(r'<a\b[^>]*href="(?P<href>/research/(?!team/)[^"#?]+)"[^>]*>(?P<body>.*?)</a>', re.I | re.S)
    for match in pattern.finditer(html_text):
        href = match.group("href")
        text = strip_tags(match.group("body"))
        if not text:
            continue
        url = urllib.parse.urljoin("https://www.anthropic.com", href)
        slug = slug_from_url(url)
        title = clean_title(text)
        if not title:
            continue
        date = parse_date(text)
        team = infer_team(text, source_url)
        candidates.append(
            {
                "source": "Anthropic Research",
                "source_id": f"anthropic:{slug}",
                "title": title,
                "published": date,
                "team": team,
                "url": url,
                "summary_hint": text,
                "source_page": source_url,
            }
        )
    return candidates


def is_recent(published: str | None, days: float) -> bool:
    if not published:
        return True
    try:
        date = dt.date.fromisoformat(published)
    except ValueError:
        return True
    cutoff = dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=days)
    return date >= cutoff


def matches_keywords(candidate: dict[str, Any], keywords: list[str]) -> bool:
    if candidate.get("team") in {"Economic Research", "Societal Impacts"}:
        return True
    if not keywords:
        return True
    haystack = f"{candidate.get('title', '')} {candidate.get('team', '')} {candidate.get('summary_hint', '')}".lower()
    return any(keyword.lower() in haystack for keyword in keywords)


def dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    output = []
    for item in items:
        key = item["source_id"]
        if key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


def fetch_candidates(args: argparse.Namespace) -> int:
    state_path = Path(os.path.expanduser(args.state_file))
    state = load_state(state_path)
    seen_ids = set(state.get("seen", {}).keys())
    source_urls = [url.strip() for url in args.sources.split(",") if url.strip()]
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]

    items: list[dict[str, Any]] = []
    for source_url in source_urls:
        html_text = fetch_text(source_url)
        items.extend(parse_links(source_url, html_text))

    candidates = []
    skipped_seen = 0
    skipped_old = 0
    skipped_keyword = 0
    for item in dedupe(items):
        if not is_recent(item.get("published"), args.days):
            skipped_old += 1
            continue
        if item["source_id"] in seen_ids and not args.include_seen:
            skipped_seen += 1
            continue
        if not matches_keywords(item, keywords):
            skipped_keyword += 1
            continue
        candidates.append(item)

    output = {
        "source": "Anthropic Research",
        "source_urls": source_urls,
        "days": args.days,
        "candidate_count": len(candidates),
        "skipped_seen": skipped_seen,
        "skipped_old": skipped_old,
        "skipped_keyword": skipped_keyword,
        "candidates": candidates,
    }
    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


def mark_seen(args: argparse.Namespace) -> int:
    state_path = Path(os.path.expanduser(args.state_file))
    state = load_state(state_path)
    seen = state.setdefault("seen", {})
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    for source_id in args.source_ids:
        seen[source_id] = {"marked_at": now}
    save_state(state_path, state)
    print(json.dumps({"marked": args.source_ids, "state_file": str(state_path)}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Anthropic Research candidates and manage seen IDs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch = subparsers.add_parser("fetch", help="Fetch Anthropic Research candidates")
    fetch.add_argument("--sources", default=",".join(DEFAULT_SOURCES), help="Comma-separated Anthropic Research listing URLs")
    fetch.add_argument("--days", type=float, default=7.0, help="Lookback window in days")
    fetch.add_argument("--keywords", default=",".join(DEFAULT_KEYWORDS), help="Comma-separated relevance keywords")
    fetch.add_argument("--state-file", default="~/.local/state/arxiv-daily-digest/seen.json")
    fetch.add_argument("--include-seen", action="store_true", help="Do not filter local seen IDs")
    fetch.set_defaults(func=fetch_candidates)

    mark = subparsers.add_parser("mark-seen", help="Mark Anthropic source IDs as seen")
    mark.add_argument("--state-file", default="~/.local/state/arxiv-daily-digest/seen.json")
    mark.add_argument("source_ids", nargs="+")
    mark.set_defaults(func=mark_seen)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
