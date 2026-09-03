#!/usr/bin/env python3
"""Daily refresh: fetch latest jobs, rebuild the site, commit, and push to
the main branch (which GitHub Pages serves from docs/). Run by launchd
(see launchd/com.james.ai-agent-jobs.plist).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    run([sys.executable, "tools/fetch.py"])
    run([sys.executable, "tools/build.py"])
    status = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout
    if not status.strip():
        print("No changes, skipping commit.")
        return 0
    run(["git", "add", "-A"])
    run([
        "git", "commit", "-m", "Daily job refresh",
        "-m", "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>",
    ])
    run(["git", "push", "origin", "main"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
