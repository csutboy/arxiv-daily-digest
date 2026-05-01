#!/usr/bin/env python3
"""Fetch Anthropic-like benchmark institution candidates and maintain seen state."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import http.client
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_SOURCES: list[dict[str, str]] = [
    {"institution": "OpenAI Signals", "tier": "frontier_ai_company", "url": "https://openai.com/signals/"},
    {"institution": "Google AI & Economy", "tier": "frontier_ai_company", "url": "https://ai.google/economy/"},
    {
        "institution": "Google Research TASC / Society-Centered AI",
        "tier": "frontier_ai_company",
        "url": "https://research.google/blog/responsible-ai-at-google-research-technology-ai-society-and-culture/",
    },
    {
        "institution": "Google DeepMind sociotechnical evaluation",
        "tier": "frontier_ai_company",
        "url": "https://deepmind.google/blog/evaluating-social-and-ethical-risks-from-generative-ai/",
    },
    {
        "institution": "Microsoft AI Economy Institute",
        "tier": "frontier_ai_company",
        "url": "https://www.microsoft.com/en-us/corporate-responsibility/topics/ai-economy-institute/",
    },
    {"institution": "Stanford HAI", "tier": "academic", "url": "https://hai.stanford.edu/about"},
    {"institution": "Stanford AI Index", "tier": "academic", "url": "https://hai.stanford.edu/ai-index/2025-ai-index-report%E2%80%8B"},
    {"institution": "Stanford Digital Economy Lab", "tier": "academic", "url": "https://digitaleconomy.stanford.edu/research/"},
    {"institution": "MIT Shaping the Future of Work / Stone Center", "tier": "academic", "url": "https://shapingwork.mit.edu/"},
    {"institution": "MIT Work of the Future / GenAI & Work", "tier": "academic", "url": "https://workofthefuture-taskforce.mit.edu/gen-ai/"},
    {"institution": "MIT FutureTech", "tier": "academic", "url": "https://futuretech.mit.edu/research"},
    {"institution": "Oxford Internet Institute AI & Work", "tier": "academic", "url": "https://www.oii.ox.ac.uk/research/projects/research-programme-on-ai-work/"},
    {"institution": "Partnership on AI: AI, Labor, and the Economy", "tier": "policy_labor", "url": "https://partnershiponai.org/program/ai-labor-and-the-economy/"},
    {"institution": "Brookings AI and Emerging Technology Initiative", "tier": "policy_labor", "url": "https://www.brookings.edu/projects/artificial-intelligence-and-emerging-technology-initiative/"},
    {"institution": "AI Now Institute", "tier": "policy_labor", "url": "https://ainowinstitute.org/publications/research/executive-summary-artificial-power"},
    {"institution": "Ada Lovelace Institute", "tier": "policy_labor", "url": "https://www.adalovelaceinstitute.org/about/our-strategy/"},
    {"institution": "ILO generative AI and jobs", "tier": "multilateral", "url": "https://www.ilo.org/publications/generative-ai-and-jobs-2025-update"},
    {
        "institution": "OECD AI and labor market",
        "tier": "multilateral",
        "url": "https://www.oecd.org/en/publications/oecd-employment-outlook-2023_08785bba-en/full-report/artificial-intelligence-and-the-labour-market-introduction_ea35d1c5.html",
    },
    {"institution": "IMF artificial intelligence", "tier": "multilateral", "url": "https://www.imf.org/en/topics/artificial-intelligence"},
    {"institution": "World Bank WDR 2026", "tier": "multilateral", "url": "https://www.worldbank.org/en/publication/wdr2026"},
]

DIMENSION_KEYWORDS = {
    "real_usage_data": [
        "usage",
        "survey",
        "interview",
        "data",
        "dataset",
        "evidence",
        "empirical",
        "index",
        "measurement",
        "measure",
        "workplace",
        "enterprise",
        "case study",
        "occupational",
        "task",
        "statistics",
        "exposure",
        "adoption",
    ],
    "labor_productivity_social_risk": [
        "labor",
        "labour",
        "job",
        "jobs",
        "work",
        "worker",
        "workforce",
        "wage",
        "skill",
        "productivity",
        "growth",
        "inequality",
        "inclusion",
        "power",
        "risk",
        "social",
        "societal",
        "economy",
        "economic",
        "automation",
    ],
    "policy_governance_translation": [
        "policy",
        "governance",
        "regulation",
        "recommendation",
        "framework",
        "assessment",
        "evaluation",
        "responsible",
        "public interest",
        "worker participation",
        "shared prosperity",
        "government",
        "regulatory",
        "institution",
        "strategy",
    ],
}

CORE_DOMAIN_KEYWORDS = [
    "ai use",
    "artificial intelligence",
    "generative ai",
    "genai",
    "economy",
    "economic",
    "labor",
    "labour",
    "work",
    "worker",
    "workforce",
    "job",
    "productivity",
    "skill",
    "organization",
    "enterprise",
    "business",
    "adoption",
    "automation",
    "social",
    "societal",
    "inequality",
    "power",
    "public interest",
    "governance",
    "policy",
    "impact assessment",
]

EXCLUDE_CANDIDATE_KEYWORDS = [
    "msc in",
    "dphil",
    "student",
    "degree",
    "course",
    "classroom",
    "series on",
    "newsletter",
    "donate",
    "careers",
    "privacy policy",
]

GENERIC_TITLES = {
    "about us",
    "case study",
    "learn more",
    "read more",
    "research",
    "research briefs",
    "working papers",
    "projects",
    "other publications",
    "past events",
    "our people",
    "people",
    "team",
    "report",
    "paper",
    "publication",
}

MONTHS = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"


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
    except Exception as first_exc:  # noqa: BLE001 - CLI fallback should report original source failures.
        curl = shutil_which("curl")
        if curl:
            result = subprocess.run(
                [
                    curl,
                    "-L",
                    "-k",
                    "--max-time",
                    "45",
                    "--user-agent",
                    "Mozilla/5.0 arxiv-daily-digest/1.0",
                    "--silent",
                    "--show-error",
                    url,
                ],
                check=False,
                capture_output=True,
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout.decode("utf-8", "replace")

        if isinstance(first_exc, urllib.error.URLError):
            reason = getattr(first_exc, "reason", None)
            if not isinstance(reason, ssl.SSLError):
                raise

    print(
        f"warning: TLS verification/handshake failed for {url}; retrying public page without certificate verification",
        file=sys.stderr,
    )
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(request, timeout=45, context=context) as response:
        try:
            return response.read().decode("utf-8", "replace")
        except http.client.IncompleteRead as exc:
            return exc.partial.decode("utf-8", "replace")


def shutil_which(binary: str) -> str | None:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        path = Path(directory) / binary
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
    return None


def strip_tags(value: str) -> str:
    value = re.sub(r"<script\b.*?</script>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<style\b.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return " ".join(html.unescape(value).split())


def normalize_source_id(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.strip("/") or "home"
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", f"{parsed.netloc}-{path}").strip("-").lower()
    return f"benchmark:{slug[:180]}"


def infer_date(text: str) -> str | None:
    iso_match = re.search(r"\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b", text)
    if iso_match:
        year, month, day = map(int, iso_match.groups())
        try:
            return dt.date(year, month, day).isoformat()
        except ValueError:
            pass
    named_match = re.search(rf"\b({MONTHS})\s+(\d{{1,2}}),\s+(20\d{{2}})\b", text)
    if named_match:
        month_names = MONTHS.split("|")
        month, day, year = named_match.groups()
        return dt.date(int(year), month_names.index(month) + 1, int(day)).isoformat()
    return None


def clean_title(text: str, fallback: str) -> str:
    text = re.sub(rf"\b({MONTHS})\s+\d{{1,2}},\s+20\d{{2}}\b", " ", text)
    text = re.sub(r"\b20\d{2}[-/]\d{1,2}[-/]\d{1,2}\b", " ", text)
    text = " ".join(text.split())
    if len(text) > 180:
        sentence_match = re.search(r"(?<=[a-z0-9\)])\.\s+[A-Z]", text)
        if sentence_match and sentence_match.start() > 24:
            text = text[: sentence_match.start() + 1]
        else:
            text = text[:177].rstrip() + "..."
    title = text or fallback
    if title.lower() in GENERIC_TITLES:
        title = fallback
    return title


def fallback_title_for_url(url: str, institution: str) -> str:
    path = urllib.parse.urlparse(url).path.strip("/")
    slug = path.split("/")[-1] if path else institution
    return " ".join(part for part in re.split(r"[-_]+", urllib.parse.unquote(slug)) if part) or institution


def should_exclude_candidate(text: str) -> bool:
    lower = text.lower()
    return any(keyword in lower for keyword in EXCLUDE_CANDIDATE_KEYWORDS)


def dimensions_for(text: str) -> list[str]:
    lower = text.lower()
    dimensions = []
    for dimension, keywords in DIMENSION_KEYWORDS.items():
        if any(keyword in lower for keyword in keywords):
            dimensions.append(dimension)
    return dimensions


def score_for(dimensions: list[str]) -> str:
    present = set(dimensions)
    if len(present) == 3:
        return "High"
    if "real_usage_data" in present and (
        "labor_productivity_social_risk" in present or "policy_governance_translation" in present
    ):
        return "Eligible"
    if {"labor_productivity_social_risk", "policy_governance_translation"}.issubset(present):
        return "Review"
    return "Exclude"


def is_core_domain(text: str) -> bool:
    lower = text.lower()
    return any(keyword in lower for keyword in CORE_DOMAIN_KEYWORDS)


def parse_candidates(source: dict[str, str], html_text: str) -> list[dict[str, Any]]:
    source_url = source["url"]
    parsed_source = urllib.parse.urlparse(source_url)
    candidates: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    link_pattern = re.compile(r'<a\b[^>]*href=["\'](?P<href>[^"\']+)["\'][^>]*>(?P<body>.*?)</a>', re.I | re.S)
    for match in link_pattern.finditer(html_text):
        href = html.unescape(match.group("href")).strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        url = urllib.parse.urljoin(source_url, href)
        parsed = urllib.parse.urlparse(url)
        if parsed.netloc and parsed.netloc != parsed_source.netloc:
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)

        text = strip_tags(match.group("body"))
        context = f"{text} {url}"
        dimensions = dimensions_for(context)
        score = score_for(dimensions)
        if score != "Exclude" and not is_core_domain(context):
            score = "Exclude"
        title = clean_title(text, fallback_title_for_url(url, source["institution"]))
        if (
            score == "Exclude"
            or len(title) < 8
            or title.lower() in GENERIC_TITLES
            or should_exclude_candidate(f"{title} {text} {url}")
        ):
            continue

        candidates.append(
            {
                "source": "Benchmark Institution",
                "source_id": normalize_source_id(url),
                "institution": source["institution"],
                "tier": source["tier"],
                "title": title,
                "published": infer_date(context),
                "url": url,
                "source_page": source_url,
                "anthropic_like_dimensions": dimensions,
                "benchmark_score": score,
                "summary_hint": text,
            }
        )

    page_text = strip_tags(html_text[:20000])
    page_dimensions = dimensions_for(page_text)
    page_score = score_for(page_dimensions)
    if page_score != "Exclude" and not is_core_domain(page_text):
        page_score = "Exclude"
    if page_score != "Exclude":
        candidates.append(
            {
                "source": "Benchmark Institution",
                "source_id": normalize_source_id(source_url),
                "institution": source["institution"],
                "tier": source["tier"],
                "title": source["institution"],
                "published": infer_date(page_text),
                "url": source_url,
                "source_page": source_url,
                "anthropic_like_dimensions": page_dimensions,
                "benchmark_score": page_score,
                "summary_hint": page_text[:700],
            }
        )

    return dedupe(candidates)


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


def is_recent(published: str | None, days: float) -> bool:
    if not published:
        return True
    try:
        date = dt.date.fromisoformat(published)
    except ValueError:
        return True
    cutoff = dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=days)
    return date >= cutoff


def load_sources(path: str | None) -> list[dict[str, str]]:
    if not path:
        return DEFAULT_SOURCES
    source_path = Path(path)
    data = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("sources file must contain a JSON array")
    return data


def fetch_candidates(args: argparse.Namespace) -> int:
    state_path = Path(os.path.expanduser(args.state_file))
    state = load_state(state_path)
    seen_ids = set(state.get("seen", {}).keys())
    sources = load_sources(args.sources_file)

    candidates: list[dict[str, Any]] = []
    source_errors = []
    for source in sources:
        try:
            html_text = fetch_text(source["url"])
            candidates.extend(parse_candidates(source, html_text))
        except Exception as exc:  # noqa: BLE001 - command-line report should continue across sources.
            source_errors.append({"institution": source.get("institution"), "url": source.get("url"), "error": str(exc)})

    output_candidates = []
    skipped_seen = 0
    skipped_old = 0
    skipped_score = 0
    allowed_scores = set(args.include_scores.split(","))
    for item in dedupe(candidates):
        if item["source_id"] in seen_ids and not args.include_seen:
            skipped_seen += 1
            continue
        if not is_recent(item.get("published"), args.days):
            skipped_old += 1
            continue
        if item.get("benchmark_score") not in allowed_scores:
            skipped_score += 1
            continue
        output_candidates.append(item)

    json.dump(
        {
            "source": "Benchmark Institution",
            "days": args.days,
            "candidate_count": len(output_candidates),
            "skipped_seen": skipped_seen,
            "skipped_old": skipped_old,
            "skipped_score": skipped_score,
            "source_errors": source_errors,
            "candidates": output_candidates,
        },
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
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
    parser = argparse.ArgumentParser(description="Fetch Anthropic-like benchmark institution candidates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch = subparsers.add_parser("fetch", help="Fetch benchmark source candidates")
    fetch.add_argument("--days", type=float, default=30.0, help="Lookback window in days when a date can be inferred")
    fetch.add_argument("--include-scores", default="High,Eligible", help="Comma-separated scores to include")
    fetch.add_argument("--sources-file", help="Optional JSON source list override")
    fetch.add_argument("--state-file", default="~/.local/state/arxiv-daily-digest/institution-seen.json")
    fetch.add_argument("--include-seen", action="store_true", help="Do not filter local seen IDs")
    fetch.set_defaults(func=fetch_candidates)

    mark = subparsers.add_parser("mark-seen", help="Mark benchmark source IDs as seen")
    mark.add_argument("--state-file", default="~/.local/state/arxiv-daily-digest/institution-seen.json")
    mark.add_argument("source_ids", nargs="+")
    mark.set_defaults(func=mark_seen)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
