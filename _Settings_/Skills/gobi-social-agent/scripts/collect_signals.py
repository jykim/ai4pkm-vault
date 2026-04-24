#!/usr/bin/env python3
"""
GSA (Gobi Social Agent) 시그널 수집기

두 종류의 시그널을 수집하여 JSON으로 stdout에 출력한다:
  1. my_signals: 내 최근 볼트 활동 (지난 --hours 시간 내 수정된 파일)
  2. community_signals: Gobi 커뮤니티 BrainUpdate/Thread (지난 --days 일)

Usage:
  # 볼트 루트에서 실행
  python3 _Settings_/Tools/gsa/collect_signals.py --hours 24 --days 3

  # 명시적 볼트 경로
  python3 collect_signals.py --vault /path/to/vault --hours 6
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

MY_SIGNAL_DIRS = [
    "Journal",
    "AI/Roundup",
    "AI/Summary",
    "AI/Analysis",
    "AI/Events",
    "AI/Sharable",
    "_Outbox_/BrainUpdates",
]

COMMUNITY_DIRS = [
    "_Gobi_/BrainUpdates",
    "_Gobi_/Threads",
]

SKIP_DIRS = {"_files_", "_archive_", "deprecated", "cmds"}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    data: dict = {}
    current_key = None
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            data.setdefault(current_key, []).append(line.strip()[2:].strip('"'))
        elif ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"')
            current_key = key
            data[key] = value if value else []
    return data


def extract_title(path: Path, text: str, fm: dict) -> str:
    if fm.get("title"):
        return str(fm["title"])
    for line in text.splitlines()[:50]:
        if line.startswith("# "):
            return line[2:].strip()
        if line.startswith("## "):
            return line[3:].strip()
    return path.stem


def extract_preview(text: str, max_chars: int = 400) -> str:
    body = FRONTMATTER_RE.sub("", text, count=1).strip()
    body = re.sub(r"^#+\s+.*$", "", body, count=1, flags=re.MULTILINE).strip()
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body[:max_chars].strip()


def collect_files(vault: Path, subdirs: list[str], since: datetime) -> list[dict]:
    results: list[dict] = []
    since_ts = since.timestamp()
    for sub in subdirs:
        root = vault / sub
        if not root.exists():
            continue
        for md in root.rglob("*.md"):
            if any(part in SKIP_DIRS for part in md.parts):
                continue
            try:
                mtime = md.stat().st_mtime
            except OSError:
                continue
            if mtime < since_ts:
                continue
            try:
                text = md.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            fm = parse_frontmatter(text)
            rel = md.relative_to(vault).as_posix()
            results.append({
                "path": rel,
                "title": extract_title(md, text, fm),
                "modified": datetime.fromtimestamp(mtime, tz=timezone.utc).astimezone().isoformat(timespec="minutes"),
                "tags": fm.get("tags", []) if isinstance(fm.get("tags"), list) else [],
                "preview": extract_preview(text),
                "size": md.stat().st_size,
            })
    results.sort(key=lambda r: r["modified"], reverse=True)
    return results


def load_seen(state_path: Path) -> set[str]:
    if not state_path.exists():
        return set()
    try:
        return set(json.loads(state_path.read_text()).get("used_sources", []))
    except (json.JSONDecodeError, OSError):
        return set()


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect signals for Gobi Social Agent")
    parser.add_argument("--vault", type=Path, default=Path.cwd(),
                        help="vault root path (default: current working directory)")
    parser.add_argument("--hours", type=int, default=24, help="window for my_signals")
    parser.add_argument("--days", type=int, default=3, help="window for community_signals")
    parser.add_argument("--limit-my", type=int, default=15)
    parser.add_argument("--limit-community", type=int, default=20)
    parser.add_argument("--state", type=Path, default=None, help="state file path for dedup")
    args = parser.parse_args()

    vault: Path = args.vault.resolve()
    if not vault.exists():
        print(json.dumps({"error": f"vault not found: {vault}"}), file=sys.stderr)
        return 1

    now = datetime.now(tz=timezone.utc).astimezone()
    my_since = now - timedelta(hours=args.hours)
    comm_since = now - timedelta(days=args.days)

    state_path = args.state or (vault / "_Settings_/Skills/gobi-social-agent/state/_state.json")
    used = load_seen(state_path)

    my_signals = collect_files(vault, MY_SIGNAL_DIRS, my_since)[: args.limit_my]
    community_signals = collect_files(vault, COMMUNITY_DIRS, comm_since)[: args.limit_community]

    for sig in my_signals:
        sig["already_used"] = sig["path"] in used

    output = {
        "collected_at": now.isoformat(timespec="minutes"),
        "vault": str(vault),
        "windows": {"my_hours": args.hours, "community_days": args.days},
        "my_signals": my_signals,
        "community_signals": community_signals,
        "state_path": str(state_path),
    }
    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
