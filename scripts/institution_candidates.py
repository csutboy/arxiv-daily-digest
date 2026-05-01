#!/usr/bin/env python3
"""Fetch institutional AI economy/society candidates from Anthropic and benchmark sources."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_STATE_FILE = "~/.local/state/arxiv-daily-digest/institution-seen.json"


def run_child(script_name: str, args: list[str]) -> dict[str, Any]:
    command = [sys.executable, str(SCRIPT_DIR / script_name), *args]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.stderr:
        sys.stderr.write(result.stderr)
    if result.returncode != 0:
        return {
            "source": script_name,
            "candidate_count": 0,
            "skipped_seen": 0,
            "skipped_old": 0,
            "source_errors": [{"script": script_name, "error": result.stderr or result.stdout}],
            "candidates": [],
        }
    return json.loads(result.stdout)


def fetch_candidates(args: argparse.Namespace) -> int:
    common = ["--state-file", args.state_file]
    if args.include_seen:
        common.append("--include-seen")

    anthropic = run_child(
        "anthropic_candidates.py",
        ["fetch", "--days", str(args.anthropic_days), *common],
    )
    benchmark = run_child(
        "benchmark_candidates.py",
        [
            "fetch",
            "--days",
            str(args.benchmark_days),
            "--include-scores",
            args.benchmark_scores,
            *common,
        ],
    )

    candidates = []
    candidates.extend(anthropic.get("candidates", []))
    candidates.extend(benchmark.get("candidates", []))

    output = {
        "source": "Institution Monitor",
        "anthropic": {
            "candidate_count": anthropic.get("candidate_count", 0),
            "skipped_seen": anthropic.get("skipped_seen", 0),
            "skipped_old": anthropic.get("skipped_old", 0),
            "skipped_keyword": anthropic.get("skipped_keyword", 0),
        },
        "benchmark": {
            "candidate_count": benchmark.get("candidate_count", 0),
            "skipped_seen": benchmark.get("skipped_seen", 0),
            "skipped_old": benchmark.get("skipped_old", 0),
            "skipped_score": benchmark.get("skipped_score", 0),
            "source_errors": benchmark.get("source_errors", []),
        },
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


def mark_seen(args: argparse.Namespace) -> int:
    anthropic_ids = [source_id for source_id in args.source_ids if source_id.startswith("anthropic:")]
    benchmark_ids = [source_id for source_id in args.source_ids if source_id.startswith("benchmark:")]
    unknown_ids = [source_id for source_id in args.source_ids if source_id not in {*anthropic_ids, *benchmark_ids}]

    if anthropic_ids:
        run_child("anthropic_candidates.py", ["mark-seen", "--state-file", args.state_file, *anthropic_ids])
    if benchmark_ids:
        run_child("benchmark_candidates.py", ["mark-seen", "--state-file", args.state_file, *benchmark_ids])
    if unknown_ids:
        print(json.dumps({"unknown_source_ids": unknown_ids}, ensure_ascii=False), file=sys.stderr)

    print(json.dumps({"marked": args.source_ids, "state_file": args.state_file}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch institutional AI economy/society candidates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch = subparsers.add_parser("fetch", help="Fetch Anthropic and benchmark institution candidates")
    fetch.add_argument("--anthropic-days", type=float, default=7.0)
    fetch.add_argument("--benchmark-days", type=float, default=30.0)
    fetch.add_argument("--benchmark-scores", default="High,Eligible")
    fetch.add_argument("--state-file", default=DEFAULT_STATE_FILE)
    fetch.add_argument("--include-seen", action="store_true")
    fetch.set_defaults(func=fetch_candidates)

    mark = subparsers.add_parser("mark-seen", help="Mark institution source IDs as seen")
    mark.add_argument("--state-file", default=DEFAULT_STATE_FILE)
    mark.add_argument("source_ids", nargs="+")
    mark.set_defaults(func=mark_seen)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
