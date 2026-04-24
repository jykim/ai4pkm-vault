---
title: "cmds-system-files (mirrored rules)"
source: "https://github.com/johnfkoo951/cmds-system-files"
source_commit: "a74e17aa1f3edb770f252311f6fd67d6aa979708"
mirrored_at: "2026-04-21"
status: "reference-only"
tags:
  - guidelines
  - cross-framework
---

## Purpose

Read-only mirror of the 7 shared rule files from [cmds-system-files](https://github.com/johnfkoo951/cmds-system-files) by John Koo. Kept here so AI agents working in `ai4pkm-vault` can recognize and respect CMDS conventions when reading content authored against that framework.

**These rules are NOT authoritative for this vault.** The authoritative rules live in `/AGENTS.md` and `/CLAUDE.md` at the vault root. See `_Settings_/Guidelines/CMDS-COMPAT.md` for the gap analysis and translation cheat-sheet.

## Contents

- `frontmatter-standard.md` — 7 required YAML properties (cmds schema)
- `indentation-rules.md` — YAML 2-space, Markdown TAB
- `wikilink-rules.md` — Obsidian wikilink syntax incl. emoji-prefix rule
- `directory-structure.md` — 9 numeric-category folder taxonomy (100–900)
- `file-creation-rules.md` — `YYYY-MM-DD-kebab-case.ext` naming, output folders
- `mermaid-rules.md` — Mermaid diagram formatting
- `video-project-workflow.md` — Video project placement

## Refresh

To pull the latest from upstream:

```bash
cd ~/dev/cmds-system-files && git pull
cp ~/dev/cmds-system-files/rules/*.md \
   /Users/lifidea/dev/ai4pkm-vault/_Settings_/Guidelines/cmds-system-files/
```

Then bump `source_commit` and `mirrored_at` in this file.
