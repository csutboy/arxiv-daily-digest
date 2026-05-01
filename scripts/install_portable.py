#!/usr/bin/env python3
"""Install this skill into compatible local agent skill directories."""

from __future__ import annotations

import argparse
from pathlib import Path


SKILL_NAME = "arxiv-daily-digest"


def destinations() -> list[Path]:
    home = Path.home()
    return [
        home / ".claude" / "skills" / SKILL_NAME,
        home / ".openclaw" / "skills" / SKILL_NAME,
        home / ".hermes" / "skills" / SKILL_NAME,
    ]


def install(root: Path, force: bool, dry_run: bool) -> int:
    for dest in destinations():
        if dest.exists() or dest.is_symlink():
            if dest.is_symlink() and dest.resolve() == root.resolve():
                print(f"ok: {dest} already points to {root}")
                continue
            if not force:
                print(f"skip: {dest} exists; use --force to replace")
                continue
            print(f"replace: {dest}")
            if not dry_run:
                if dest.is_dir() and not dest.is_symlink():
                    raise SystemExit(f"Refusing to remove real directory without manual review: {dest}")
                dest.unlink()
        else:
            print(f"link: {dest} -> {root}")

        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.symlink_to(root, target_is_directory=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Symlink arxiv-daily-digest into local agent skill folders.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]), help="Skill root directory")
    parser.add_argument("--force", action="store_true", help="Replace existing symlinks only")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    return install(Path(args.root).resolve(), args.force, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
