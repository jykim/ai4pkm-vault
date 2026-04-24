#!/usr/bin/env python3
"""
GSA state 파일 업데이트.

드래프트 생성 후 호출하여 사용한 소스와 타임스탬프를 기록한다.

Usage:
  # 볼트 루트에서 실행
  python3 _Settings_/Skills/gobi-social-agent/scripts/update_state.py \
    --source "AI/Roundup/YYYY-MM-DD - Agent.md" \
    --draft "_Outbox_/BrainUpdates/YYYY-MM-DD title - Agent.md" \
    --kind bu

  # 스킵 기록
  python3 update_state.py --kind skip --draft "" --note "no new signals"
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

MAX_HISTORY = 200


def main() -> int:
    parser = argparse.ArgumentParser(description="Update GSA state after draft creation")
    parser.add_argument("--source", action="append", default=[], help="source file path (repeatable)")
    parser.add_argument("--draft", required=True, help="created draft path")
    parser.add_argument("--kind", choices=["bu", "thread", "skip"], required=True)
    parser.add_argument("--state", type=Path, default=None,
                        help="state file path (default: <cwd>/_Settings_/Skills/gobi-social-agent/state/_state.json)")
    parser.add_argument("--note", default="", help="optional note (e.g. skip reason)")
    args = parser.parse_args()

    state_path: Path = args.state or (Path.cwd() / "_Settings_/Skills/gobi-social-agent/state/_state.json")
    state_path.parent.mkdir(parents=True, exist_ok=True)

    if state_path.exists():
        try:
            state = json.loads(state_path.read_text())
        except json.JSONDecodeError:
            state = {}
    else:
        state = {}

    now = datetime.now(tz=timezone.utc).astimezone().isoformat(timespec="minutes")
    state["last_run"] = now
    if args.kind != "skip":
        state["last_draft_at"] = now

    used = list(dict.fromkeys((state.get("used_sources") or []) + args.source))
    state["used_sources"] = used[-MAX_HISTORY:]

    history = state.setdefault("history", [])
    history.append({
        "ts": now,
        "kind": args.kind,
        "draft": args.draft,
        "sources": args.source,
        "note": args.note,
    })
    state["history"] = history[-MAX_HISTORY:]

    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    print(json.dumps({"ok": True, "state": str(state_path), "last_run": now}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
