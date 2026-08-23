---
name: obsidian-yaml-frontmatter
description: Manage YAML frontmatter properties with consistent formatting, property names, and value types. Use when creating or updating frontmatter in markdown files.
allowed-tools:
  - Read
  - Edit
license: MIT
---

# YAML Frontmatter Management

Standardize YAML frontmatter properties across all vault content.

## When to Use This Skill

Activate when you need to:
- Add or update frontmatter in markdown files
- Ensure consistent property naming and formatting
- Format tags, dates, or other property values
- Validate frontmatter structure

> **Note**: This skill manages frontmatter **PROPERTIES** (keys, values, types, formatting).
> For document **STRUCTURE** (heading hierarchy, section order, frontmatter position), use `obsidian-markdown-structure` skill.

## Core Frontmatter Rules

### 1. Single YAML Block at Top

**Structure**:
```yaml
---
property: value
---

## First Section Header
```

**Critical Rules**:
- One YAML block at top of file
- Blank line after closing `---`
- No content before first heading (after frontmatter)

### 2. Standard Property Names

**Use lowercase, consistent keys**:
```yaml
✅ CORRECT:
title: Document Title
created: 2025-10-31
tags:
  - tag1
source: https://example.com
author: Author Name

❌ INCORRECT:
Title: Document Title (capitalized)
date: 2025-10-31 (use "created" not "date")
tag: tag1 (use "tags" plural)
```

**No Duplicate Properties**:
- Use `created` (not both `date` and `created`)
- Use `tags` (not both `tag` and `tags`)

### 3. Tag Formatting

**CRITICAL: Plain text in YAML, NO hashtags**:
```yaml
✅ CORRECT:
tags:
  - journal
  - daily
  - reflection

❌ INCORRECT:
tags:
  - #journal
  - #daily
```

**Always use list format with dashes**:
```yaml
✅ CORRECT (list format):
tags:
  - tag1
  - tag2

❌ INCORRECT (inline):
tags: [tag1, tag2]
```

### 4. Date Format

**Use YYYY-MM-DD consistently**:
```yaml
✅ CORRECT:
created: 2025-10-31
updated: 2025-11-01

❌ INCORRECT:
created: 10/31/2025
created: 2025-10-31T10:30:00
```

### 5. Link Lists

**Wrap wiki links in quotes**:
```yaml
✅ CORRECT:
sources:
  - "[[Journal/2025-10-31]]"
  - "[[Articles/2025-10-31 Title]]"

links:
  - "[[Roundup/2025-10-31]]"

attendees:
  - "[[People/John]]"
  - Jane

❌ INCORRECT:
sources:
  - [[Journal/2025-10-31]] (missing quotes)
```

### 6. Quote Values with Special Characters

**Quote values containing**: `:` `#` `"` or numeric-looking strings

**Single quote wrapping (easiest for values with `"`)**:
```yaml
✅ CORRECT:
title: 'He said, "Hello."'
note: 'It\'s called "PKM".'
```

**Double quote wrapping with escaping**:
```yaml
✅ CORRECT:
title: "He said, \"Hello.\""
source: "https://example.com"
version: "2.0"
```

**Literal double-quote character**:
```yaml
✅ CORRECT:
quote_char: '"'
```

**Mixed quotes preference**: Use double quotes, escape only `"` (single quotes don't need escaping):
```yaml
✅ CORRECT:
note: "It's called \"PKM\"."

❌ INCORRECT:
title: AI Era: Thriving Framework (unquoted colon)
version: 2.0 (parsed as number, not string)
```

**Multiline values (no escaping needed)**:
```yaml
✅ CORRECT:
description: |
  He said, "Hello."
  New line preserved.
```

## Standard Property Set

### Core Properties (All Content)
```yaml
---
title: Document Title
created: YYYY-MM-DD
tags:
  - category
  - type
---
```

### Content with Sources
```yaml
---
title: Article Title
created: YYYY-MM-DD
source: https://url or file path
author: Author Name
tags:
  - clipping
  - topic
---
```

### Relational Content
```yaml
---
title: Document Title
created: YYYY-MM-DD
tags:
  - category
sources:
  - "[[Source File 1]]"
  - "[[Source File 2]]"
links:
  - "[[Related Topic]]"
---
```

### Events/Meetings
```yaml
---
title: Meeting Name
created: YYYY-MM-DD
event_date: YYYY-MM-DD
attendees:
  - "[[Person 1]]"
  - Person 2
sources:
  - "[[Journal/YYYY-MM-DD#Section]]"
tags:
  - meeting
  - event
---
```

## Workflow

### Step 1: Determine Content Type
- Daily content (Journal, Notes)
- Ingested content (Clippings, Articles)
- Created content (Analysis, Tasks, Events)
- Topic/Project pages

### Step 2: Select Property Set
- Core properties (title, created, tags)
- Add source/author if applicable
- Add relational links (sources, links, attendees)
- Add content-specific properties

### Step 3: Format Values
- Dates: YYYY-MM-DD format
- Tags: Plain text list (no #)
- Links: Quoted wiki links
- Special chars: Quote values with `:` or `#`

### Step 4: Structure Check
- Single YAML block at top
- Blank line after `---`
- Consistent property names (lowercase)
- No duplicate properties

## Quality Checklist

Before completing frontmatter:
- [ ] Single YAML block at top with blank line after
- [ ] All property keys lowercase and consistent
- [ ] Tags are plain text (NO hashtags)
- [ ] Dates in YYYY-MM-DD format
- [ ] Wiki links wrapped in quotes
- [ ] Special characters quoted appropriately
- [ ] No duplicate properties (created vs date, tags vs tag)

## Optional: cmds-Aligned Properties

Adopted from [cmds-system-files](https://github.com/johnfkoo951/cmds-system-files) `frontmatter-standard.md`. These are **opt-in** — recommended for analysis docs, prompts, and notes likely to be referenced by AI agents in future sessions, but never required for daily content.

### `description` (recommended for analysis docs)

A one-line English summary acting as an **LLM routing signal** — not a human summary. Treat it like a tool description: action-oriented, specific, no fluff.

```yaml
✅ GOOD:
description: "Meeting minutes from 2026-04-07 LG AX camp retrospective. Contains CEO feedback summary and next-action items."

❌ BAD:
description: "회의록입니다"           # non-descriptive, Korean only
description: "This is a note"        # no signal for relevance
```

**Why English?** AI agents (Claude, Gemini, GPT) use this field cross-language to decide whether a note is relevant to a future query. A specific English description survives translation drift and tokenization differences. Body text remains free (Korean default per `.gobi/settings.yaml`).

### `aliases` (optional, for notes with multiple names)

```yaml
aliases:
  - "Old Name"
  - "Korean Title"
```

### Date imports from cmds (`date created` / `date modified`)

cmds uses split date keys; ai4pkm uses single `created`. When importing cmds content:

| cmds key | ai4pkm key |
|----------|------------|
| `date created` | `created` (preserve as-is) |
| `date modified` | `updated` (new key — only add if non-trivial drift) |

**Do not** introduce camelCase keys (`myRate`, `totalPage`) — keep ai4pkm lowercase. cmds-style camelCase fields can stay quoted as imports but should not propagate into native ai4pkm content.

### Quality additions

- [ ] If document is analysis/prompt/reference: consider adding `description` (English, ≤140 chars, action-oriented)
- [ ] If imported from cmds: convert `date created` → `created`, drop camelCase compound fields unless meaningful
