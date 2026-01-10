---
description:
globs:
alwaysApply: true
---

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation or README files. 

# Generic AI Agent Rules

*These rules apply to all AI agents (Claude Code, Gemini, Codex) working in this PKM vault.*

## Core Mission & Principles
- **Your mission is to enhance and organize user's knowledge**
	- Don't add your internal knowledge unless explicitly asked to do so
- Most commands are based on existing prompts and workflows (locations below)
	- But note that default settings (e.g. input/output) can be overridden for each run
- You're expected to run autonomously for most prompts & workflow runs
	- Use your judgment to complete the task unless asked otherwise

## Prompts & Workflows
- Orchestrator config in `orchestrator.yaml` (root)
- Prompts can be found in `_Settings_/Prompts`
- Workflows (of prompts) in `_Settings_/Workflows`
- Templates (of md docs) in `_Settings_/Templates`
- Knowledge Tasks in `AI/Tasks` (only when requested)
- Each command can be called using abbreviations
- Check this first for new command (especially if it's abbreviations)

## Skills
- Skills are located in `.claude/skills/`
- Each skill folder contains a `SKILL.md` with instructions
- To use a skill, read the corresponding `SKILL.md` file first
- Available skills include:
  - `obsidian-links` - Wiki link formatting
  - `obsidian-yaml-frontmatter` - YAML frontmatter standards
  - `obsidian-markdown-structure` - Markdown structure guidelines
  - `markdown-video` - Video generation from markdown
  - `gemini-image-skill` - Image generation with Gemini
  - `ai4pkm-helper` - AI4PKM specific helpers

## Search over files
- For searching over topic or dates, start from `Topics` or `Roundup` folder
- Follow markdown link to find related files (use `find` to find exact location)
* **Consider `.gitignore` when searching files**: When finding file lists or searching content, use `respect_git_ignore=False` option to include all relevant files that might otherwise be excluded by `.gitignore`.

## 📝 Content Creation Requirements
### General Guidelines
- **Include original quotes** in blockquote format
- **Add detailed analysis** explaining significance
- Structure by themes with clear categories
- **Use wiki links with full filenames**: `[[YYYY-MM-DD Filename]]`
- **Tags use plain text in YAML frontmatter**: `tag` not `#tag` in YAML
  - Example:
```yaml
tags:
  - journal
  - daily
```

### Writing Style
- **Tight layout**: Do not use horizontal dividers (`---`) between sections
- **Paragraph cohesion**: Write related sentences as a single paragraph (minimum 2-3 sentences)
  - Avoid paragraphs with only one sentence standing alone
  - Combine short sentences logically into one

### Markdown Table Formatting
- **Blank line required before tables**: Markdown tables must have a blank line immediately before them to render properly

### Diagram Standards
> **Detailed guide**: See `.claude/skills/obsidian-mermaid/SKILL.md`

- **Write diagrams in Mermaid**: Use Mermaid instead of ASCII art

### Table vs Diagram Selection
- **Use tables for**: Attribute-value mappings, comparisons, option listings (structured data)
- **Use Mermaid for**: Flows, processes, relationships, time sequences (visual flows)
- **Optimize document length**: Choose the format that expresses the same information more compactly

### Link Format Standards
> **Detailed guide**: See `.claude/skills/obsidian-links/SKILL.md`

- Use Link Format below for page properties:
```yaml
  - "[[Page Title]]"
```
- For files in AI folder, omit "AI/" prefix for brevity
- Example: `[[Roundup/2025-08-03 - Claude Code]]` not `[[AI/Roundup/2025-08-03 - Claude Code]]`

### 📁 Output File Management
- Create analysis files in `AI/*/` folder unless instructed otherwise
- Naming: `YYYY-MM-DD [Project Name] by [Agent Name].md`
- Include source attribution for every insight

### Inline Links for Research Documents
- **Insert related links throughout the body of research/analysis documents**
- Add contextual links where relevant content is mentioned, not just in the References section
- **Link format**:
  - `→ **Deep analysis**: [[path/to/file|display text]]`
  - `→ **Related research**: [[path/to/file#section-name|display text]]`

### Properties & Frontmatter Standards
> **Detailed guide**: See `.claude/skills/obsidian-yaml-frontmatter/SKILL.md`

- Use a single YAML block at top (`---` … `---`). Leave one blank line after it.
- Keys are lowercase and consistent: `title`, `source` (URL), `author` (list), `created` (YYYY-MM-DD HH:MM:SS), `tags` (list)
- **created property includes actual creation time**: When AI generates a document, record both date and time
- Avoid duplicates like `date` vs `created`
- Tags are plain text (no `#`) and indented list; authors may be wiki links wrapped in quotes
- Quote values that contain colons, hashes, or look numeric to avoid YAML casting
- After frontmatter, start with a section heading — no loose text or embeds before the first heading

## 🔄 Additional Principles

### Update over duplicated creation
- If a file already exists for that date, update it (do not create a new one)
  - When updating, don't just append new content; revise with overall consistency in mind (duplication is a sin)

### Language Preferences
- Use Korean as default language (English is fine, say, to quote original note)

### 🔗 Critical: Wiki Links Must Be Valid
- **All wiki links must point to existing files**
- Use complete filename: `[[2025-04-09 세컨드 브레인]]` not `[[세컨드 브레인]]`
  - Add section links when possible (using `#` suffix)
- **Section-level links required when citing sources**
  - When quoting or referencing content from other documents, always link to the specific section
  - Example: `[[2025-12-01 Meeting Notes#2. Discussion Items|Meeting Notes]]`
- Verify file existence before linking
  - Fix broken links immediately
- **Link to original sources, not topic indices**
  - Topic files (e.g., `Topics/Business & Career/Career.md`) are indices/aggregations
  - Always link to the original article, clipping, or document where content first appeared
  - Example: Link to `[[Ingest/Articles/2025-08-15 역스킬 현상]]` not `[[Topics/Business & Career/Career#역스킬]]`
  - This maintains proper source attribution and traceability

## Source/Prompt-specific Guidelines
### Limitless Link Format
- **Correct path**: `[[Limitless/YYYY-MM-DD#section]]` (no Ingest prefix)
- **Always verify section exists**: Check exact header text in source file
- **Section headers are usually Korean**: Match them exactly as written
- **If unsure about section**: Link to file only `[[Limitless/YYYY-MM-DD]]`

### Heading Structure Guidelines
> **Detailed guide**: See `.claude/skills/obsidian-markdown-structure/SKILL.md`

- Clippings (EIC/ICT): begin with `## Summary`, then `## Improve Capture & Transcript (ICT)`, then transcript
- ICT means improve the transcript (correct grammar, translate to Korean, structure with h3), not summarize. Keep length comparable to source; summaries live only under `## Summary`
- Lifelog: use H1 `# YYYY-MM-DD Lifelog - <Assistant>` then H2 sections (Monologues, Conversations, etc.)
- Topics/Projects: start with H2 summary; avoid duplicating title as H1

## Quality Standards
- Validate all wiki links resolve to existing files/sections; fix broken links immediately
- Focus on meaningful content over metadata files
- Don't ask permission for any non-file-changing operations (search/list/echo etc)
- Always use local time (usually in Seattle area) for processing requests

## Multi-Vault Operations
- **Registry**: Vault information is defined in `VAULTS.md` - read before cross-vault operations

---
*For agent-specific rules, refer to individual agent configuration files: CLAUDE.md, GEMINI.md, AGENTS.md*