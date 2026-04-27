---
title: cmds-system-files Philosophy Cheat-sheet
source: "https://github.com/johnfkoo951/cmds-system-files"
source_commit: "a74e17aa1f3edb770f252311f6fd67d6aa979708"
status: active-reference
tags:
  - guidelines
  - cross-framework
  - cmds
---

## Purpose

One-page summary of which [cmds-system-files](https://github.com/johnfkoo951/cmds-system-files) principles ai4pkm has **absorbed** into its skill rules — and where they live now. Use this when you want to know "what did we adopt" without reading the full mirrored rule files.

For the framing on _why_ adopt vs _why_ not, see the owner's analysis at `OVM/AI/Analysis/2026-04-21 CMDS x ai4pkm Compatibility Analysis - Claude Code.md`. For the complete cmds rules verbatim, see `_Settings_/Guidelines/cmds-system-files/`.

## 5 Adopted Principles

### 1. Description as LLM Hint

**Definition**: One-line English `description` in frontmatter as a routing signal for AI agents — not a human summary.

**Source** — `cmds-system-files/frontmatter-standard.md` rule #6:
> "`description` must be in English: 1-2 sentences describing what the note contains and when an LLM should reference it. This is a machine-readable hint for AI agents (Claude Code, Gemini CLI, ChatGPT, etc.) to decide relevance in future sessions. Write it as a skill/tool description — specific, action-oriented, no fluff."

**ai4pkm location**: [`obsidian-yaml-frontmatter` skill](../Skills/obsidian-yaml-frontmatter/SKILL.md) → `## Optional: cmds-Aligned Properties` → "description" subsection. Marked **opt-in** for analysis docs and prompts; never required for daily content.

**Difference from cmds**: cmds requires `description` on every note. ai4pkm leaves it optional (recommended for cross-session-relevant docs only) — daily Journal/Roundup don't need it.

### 2. Atomic Compression

**Definition**: Prefer small, single-idea notes. Long monoliths should be split. Permanent notes ~9–50 lines.

**Source** — implicit across `cmds-system-files/directory-structure.md` (separate `Permanent Notes` folder) + general atomic-note philosophy from Zettelkasten tradition.

**ai4pkm location**: Mental model only. Mentioned in `AGENTS.md` "Cross-Framework Philosophy" section. No enforcement, no skill rule (deliberately).

**Difference from cmds**: cmds bakes this into folder structure (300 Permanent Notes ≠ 200 Literature). ai4pkm uses functional folders (`Topics/`, `Ingest/`) without enforcing note size.

### 3. Artifact Separation

**Definition**: Keep `node_modules/`, render outputs, build artifacts, venvs **outside** the vault. Reduces Obsidian indexing cost and search noise.

**Source** — `cmds-system-files/video-project-workflow.md`:
> "node_modules + render outputs bloat the vault (519MB / 30k files → indexing slowdown). Keep at /DEV/ outside vault, link via tracking MD."

**ai4pkm location**: `AGENTS.md` "Cross-Framework Philosophy" section. Generalized beyond just video — applies to any heavy build artifact.

**Difference from cmds**: cmds prescribes `/DEV/` exact path. ai4pkm only states the principle ("outside vault"); user picks the location.

### 4. 4-Stage Document Lifecycle

**Definition**: Every note moves through Connect → Merge → Develop → Share. Mental model for "where is this doc in its life," not runtime commands.

**Source** — `cmds-system-files/directory-structure.md` (00 Inbox → 20 Literature → 30 Permanent → 50 Outputs) and the cmds README pipeline diagram.

**ai4pkm location**: [`obsidian-markdown-structure` skill](../Skills/obsidian-markdown-structure/SKILL.md) → `## Optional: 4-Stage Pipeline as Document Lifecycle`. Maps to existing prompts (EIC/PPC/DDO at Connect, GDR/GWR at Merge, TIU/ARP at Develop, PBU/CTP/PWV at Share). Optional `stage:` frontmatter key.

**Difference from cmds**: cmds has explicit slash commands (`/connect`, `/merge`, `/develop`, `/share`). ai4pkm uses prompts that group into these stages but doesn't require declaring stage. Slash command ports are a planned follow-up (see 2026-04-21 analysis Phase 2).

### 5. Whitespace Formalization

**Definition**: Indentation, blank-line, and YAML rules are explicit and not negotiable per file. Prevents Obsidian/Mermaid renderer ambiguity.

**Source** — `cmds-system-files/indentation-rules.md` (YAML 2-space, MD body TAB) + `mermaid-rules.md` (label quoting).

**ai4pkm location**: Already in [`obsidian-yaml-frontmatter` skill](../Skills/obsidian-yaml-frontmatter/SKILL.md) (YAML 2-space, list format with dashes) and `obsidian-mermaid` skill (label safety). Plus `AGENTS.md` "Markdown Table Formatting" rule (blank line before tables).

**Difference from cmds**: cmds prescribes TAB for MD body; ai4pkm doesn't enforce a body indent (Obsidian renders both consistently). The principle ("formalize whitespace") is shared; specific values differ.

## What ai4pkm Did NOT Adopt

These cmds choices are **convention/taste** — neither is right; ai4pkm picks the other side:

- **Numeric folder taxonomy (100–900)** — ai4pkm uses functional folders (`AI/`, `Ingest/`, `Topics/`, `Journal/`)
- **Kebab-case filenames** (`YYYY-MM-DD-description.md`) — ai4pkm uses spaces (`YYYY-MM-DD Description.md`)
- **Emoji-prefix wikilinks** — required in cmds, not in ai4pkm-native files (but respected on cross-vault links — see `obsidian-links` skill)
- **Split `date created`/`date modified`** — ai4pkm uses single `created` (with optional `updated` for non-trivial drift)
- **camelCase compound keys** (`myRate`, `totalPage`) — ai4pkm keeps lowercase
- **English-first description** — ai4pkm has `primaryLanguage` setting (Korean default for body); only optional `description` field is English

## Conflicts Requiring Coordination

These cause real friction when content crosses vaults:

| Conflict | ai4pkm side | cmds side | Resolution |
|----------|-------------|-----------|------------|
| Frontmatter key set | `created`, `tags`, ... | `date created`, `date modified`, `type`, `aliases`, `description` | Translation layer at boundary (planned skill `cmds-compat`) |
| Wikilink emoji prefix | not required | required exact match | `obsidian-links` opt-in section preserves emoji on cross-vault links |
| Folder taxonomy | functional | numeric | Mapping table only — both stay native |

For the full coordination proposal sent to John Koo (cmds author), see `OVM/AI/Analysis/2026-04-26 요한께 cmds × ai4pkm 융합 제안 - Claude Code.md` (owner's vault).

## Refresh Source Mirror

```bash
cd ~/dev/cmds-system-files && git pull
cp ~/dev/cmds-system-files/rules/*.md \
   /Users/lifidea/dev/ai4pkm-vault/_Settings_/Guidelines/cmds-system-files/
```

Then bump `source_commit` in `_Settings_/Guidelines/cmds-system-files/README.md` and re-check this cheat-sheet for drift.
