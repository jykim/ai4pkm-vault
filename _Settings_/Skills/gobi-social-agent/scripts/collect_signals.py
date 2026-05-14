#!/usr/bin/env python3
"""
GSA (Gobi Social Agent) 시그널 수집기

두 종류의 시그널을 수집하여 JSON으로 stdout에 출력한다:
  1. my_signals: 내 최근 볼트 활동 (지난 --hours 시간 내 수정된 파일)
  2. community_signals: Gobi 커뮤니티 포스트 (지난 --days 일)
     a. live API: `gobi space feed` per space — 다른 사용자 포스트 (Reply 후보)
     b. vault mirror fallback: `_Gobi_/BrainUpdates/`, `_Gobi_/Threads/`

Usage:
  # 볼트 루트에서 실행 (live API 자동 사용)
  python3 _Settings_/Skills/gobi-social-agent/scripts/collect_signals.py --hours 24 --days 3

  # API 사용 X (vault mirror만)
  python3 collect_signals.py --no-api
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
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


def load_replied_post_ids(state_path: Path) -> set[str]:
    if not state_path.exists():
        return set()
    try:
        return set(str(x) for x in json.loads(state_path.read_text()).get("replied_to_posts", []))
    except (json.JSONDecodeError, OSError):
        return set()


def _gobi_json(args: list[str], timeout: int = 15) -> dict | None:
    """Run `gobi --json <args>` and return parsed data, or None on failure."""
    try:
        proc = subprocess.run(
            ["gobi", "--json", *args],
            capture_output=True, text=True, timeout=timeout
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    if not out.get("success"):
        return None
    return out.get("data")


def _self_vault_slug() -> str | None:
    data = _gobi_json(["auth", "status"], timeout=5)
    if not data:
        return None
    return data.get("vaultSlug")


def _list_spaces() -> list[dict]:
    data = _gobi_json(["space", "list"], timeout=10)
    if not data:
        return []
    return data if isinstance(data, list) else data.get("items", [])


def _space_feed(space_slug: str, limit: int = 30) -> list[dict]:
    data = _gobi_json(
        ["space", "--space-slug", space_slug, "feed", "--limit", str(limit)],
        timeout=15,
    )
    if not data:
        return []
    return data.get("items", []) if isinstance(data, dict) else []


def fetch_live_community_signals(
    cutoff: datetime,
    self_slug: str | None,
    replied_post_ids: set[str],
    per_space_limit: int = 30,
) -> list[dict]:
    """Pull recent space-post candidates from Gobi API for Reply targeting.

    Returns space-posts authored by *others*, created since `cutoff`, not yet
    in the user's `replied_to_posts` state list.
    """
    signals: list[dict] = []
    spaces = _list_spaces()
    if not spaces:
        return signals

    for space in spaces:
        slug = space.get("slug")
        if not slug:
            continue
        for post in _space_feed(slug, per_space_limit):
            primary = post.get("primaryVault") or {}
            author_vault = post.get("authorVault") or {}
            # Skip own posts (primaryVault or authorVault matches self)
            if self_slug and (primary.get("slug") == self_slug
                              or author_vault.get("slug") == self_slug):
                continue
            # Skip already replied
            post_id = str(post.get("id", ""))
            if post_id in replied_post_ids:
                continue
            # Time filter
            created_raw = post.get("createdAt", "")
            try:
                created_dt = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
            except ValueError:
                continue
            if created_dt < cutoff:
                continue

            author = post.get("author") or {}
            content = post.get("content") or ""
            signals.append({
                "kind": "space_post",
                "post_id": post_id,
                "space_slug": slug,
                "space_name": space.get("name", slug),
                "author": author.get("name", "Unknown"),
                "author_vault": (author_vault or primary).get("slug"),
                "title": (post.get("title") or "")[:200],
                "preview": content[:400],
                "created": created_raw,
                "reply_count": post.get("replyCount", 0),
                "share_url": f"https://gobispace.com/spaces/{slug}?postId={post_id}",
            })
    # Newest first
    signals.sort(key=lambda s: s["created"], reverse=True)
    return signals


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect signals for Gobi Social Agent")
    parser.add_argument("--vault", type=Path, default=Path.cwd(),
                        help="vault root path (default: current working directory)")
    parser.add_argument("--hours", type=int, default=24, help="window for my_signals")
    parser.add_argument("--days", type=int, default=3, help="window for community_signals")
    parser.add_argument("--limit-my", type=int, default=15)
    parser.add_argument("--limit-community", type=int, default=20)
    parser.add_argument("--state", type=Path, default=None, help="state file path for dedup")
    parser.add_argument("--no-api", action="store_true",
                        help="skip live gobi API calls; use vault-mirror community dirs only")
    parser.add_argument("--api-per-space-limit", type=int, default=30,
                        help="max posts to pull from each space feed")
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
    replied = load_replied_post_ids(state_path)

    my_signals = collect_files(vault, MY_SIGNAL_DIRS, my_since)[: args.limit_my]
    mirror_signals = collect_files(vault, COMMUNITY_DIRS, comm_since)
    for sig in mirror_signals:
        sig["kind"] = "vault_mirror"

    api_signals: list[dict] = []
    api_status = "skipped"
    if not args.no_api:
        self_slug = _self_vault_slug()
        if self_slug is None:
            api_status = "auth_failed"
        else:
            api_signals = fetch_live_community_signals(
                cutoff=comm_since,
                self_slug=self_slug,
                replied_post_ids=replied,
                per_space_limit=args.api_per_space_limit,
            )
            api_status = "ok"

    community_signals = (api_signals + mirror_signals)[: args.limit_community]

    for sig in my_signals:
        sig["already_used"] = sig["path"] in used

    output = {
        "collected_at": now.isoformat(timespec="minutes"),
        "vault": str(vault),
        "windows": {"my_hours": args.hours, "community_days": args.days},
        "my_signals": my_signals,
        "community_signals": community_signals,
        "community_api_status": api_status,
        "community_counts": {
            "api": len(api_signals),
            "vault_mirror": len(mirror_signals),
            "replied_to_known": len(replied),
        },
        "state_path": str(state_path),
    }
    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
