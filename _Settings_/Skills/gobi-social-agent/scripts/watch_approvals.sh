#!/usr/bin/env bash
# Watch _Gobi_/GSA/ for approve_for_publish flips (false → true) via FSEvents.
#
# Emits one line per flip detected after watch start:
#   FLIPPED <HH:MM:SS> — <basename>
#
# A draft is "ready to publish" when it has `approve_for_publish: true` AND lacks
# `published_post_id:` (i.e. flipped by the user but not yet handed to gobi-cli).
#
# Files already in that state at start (backlog) are reported once with `BACKLOG`
# so the operator can decide whether to publish them.
#
# Usage (from vault root):
#   ./_LifeOS_/Skills/gobi-social-agent/scripts/watch_approvals.sh
#
# Stops with Ctrl-C or by killing the process.
#
# Requires: bash 4+ (associative arrays) and fswatch (`brew install fswatch`).

set -u

VAULT_ROOT="${VAULT_ROOT:-$(pwd)}"
WATCH_DIR="${VAULT_ROOT}/_Gobi_/GSA"

if ! command -v fswatch >/dev/null 2>&1; then
  echo "ERROR: fswatch not found. Install with: brew install fswatch" >&2
  exit 1
fi

if [ ! -d "$WATCH_DIR" ]; then
  echo "ERROR: watch dir not found: $WATCH_DIR" >&2
  exit 1
fi

cd "$VAULT_ROOT"

declare -A reported

# Snapshot: report files currently in the "approved-but-not-published" state
# (backlog), then watch for new transitions into that state.
shopt -s nullglob
for f in _Gobi_/GSA/*.md; do
  if grep -qE "^approve_for_publish: true$" "$f" 2>/dev/null \
     && ! grep -qE "^published_post_id:" "$f" 2>/dev/null; then
    echo "BACKLOG $(date '+%H:%M:%S') — $(basename "$f")"
    reported["$f"]=1
  fi
done
shopt -u nullglob

echo "WATCH-START $(date '+%H:%M:%S') — listening on $WATCH_DIR via FSEvents"

while IFS= read -r -d $'\0' path; do
  [[ "$path" == *.md ]] || continue
  rel=${path#"${VAULT_ROOT}/"}
  [ -n "${reported["$rel"]:-}" ] && continue
  if grep -qE "^approve_for_publish: true$" "$path" 2>/dev/null \
     && ! grep -qE "^published_post_id:" "$path" 2>/dev/null; then
    echo "FLIPPED $(date '+%H:%M:%S') — $(basename "$path")"
    reported["$rel"]=1
  fi
done < <(fswatch -0 -r --latency=0.3 "$WATCH_DIR")

echo "WATCH-EXIT $(date '+%H:%M:%S') — fswatch exited (status=$?)"
