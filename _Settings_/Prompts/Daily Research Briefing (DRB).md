---
title: Daily Research Briefing
abbreviation: DRB
category: batch
created: 2026-01-22
tags:
  - prompt
  - briefing
  - research
  - web-search
  - daily
---

## Purpose

Generate a daily briefing on topics you're actively researching, based on your recently updated Topics files. Uses WebSearch to find the latest news, papers, and updates.

## Input

- `Topics/` folder (auto-detect recently modified files)
- Maximum 5 topics per run

## Output

- `{{output_path}}/YYYY-MM-DD Daily Research Briefing - [Agent].md`
- Default output_path: `AI/Briefings`

## Workflow

### Step 1: Identify Active Topics

Scan `Topics/` folder for recently modified files (last 7 days):

```bash
# Find recently modified topic files
find Topics/ -name "*.md" -mtime -7 | sort -t/ -k2
```

**Selection criteria:**
1. Sort by modification date (most recent first)
2. Select up to 5 topics
3. Extract topic name and key interests from each file

### Step 2: Extract Search Keywords

For each topic file, identify:
- Main topic name (from title/filename)
- Key subtopics (from H2/H3 headers)
- Recent additions (content added in last update)

**Example extraction:**
```yaml
topic: Machine Learning
keywords:
  - LLM evaluation
  - prompt engineering
  - RAG systems
last_focus: "LLM-as-a-judge evaluation methods"
```

### Step 3: WebSearch for Updates

Use **WebSearch** for each topic:

```
# Research papers
"[keyword]" 2026 site:arxiv.org OR site:scholar.google.com

# Industry news
"[keyword]" latest news 2026

# Technical blogs
"[keyword]" tutorial guide 2026
```

**Search strategy:**
- 2-3 searches per topic
- Focus on recent content (current year)
- Prioritize authoritative sources

### Step 4: Filter and Rank Results

For each topic, select top 2-3 most relevant results:

| Priority | Criteria |
|----------|----------|
| High | New research papers, breaking news |
| Medium | Tutorial updates, tool releases |
| Low | General articles, opinion pieces |

### Step 5: Deep Fetch Key Content (Optional)

Use **WebFetch** for high-priority items:
- Extract key quotes
- Summarize main findings
- Note action items

### Step 6: Generate Briefing Document

```markdown
---
title: YYYY-MM-DD Daily Research Briefing
created: YYYY-MM-DD HH:MM:SS
topics_covered:
  - Topic 1
  - Topic 2
tags:
  - briefing
  - research
  - daily
---

## Summary

Brief overview of today's key findings across all topics.

## Topic Updates

### 1. [Topic Name]
**Active Interest**: [What you've been researching]

#### Key Updates
- **[Title]** - [Source]
  [1-2 sentence summary]
  → [Link](URL)

- **[Title]** - [Source]
  [1-2 sentence summary]
  → [Link](URL)

#### Implications
[How this relates to your research/work]

---

### 2. [Topic Name]
...

## Quick Reference

| Topic | Key Update | Action |
|-------|------------|--------|
| Topic 1 | [One-line summary] | [Read/Save/None] |
| Topic 2 | [One-line summary] | [Read/Save/None] |

## Sources

- [Source Title](URL) - Topic 1
- [Source Title](URL) - Topic 2
```

## Configuration

```yaml
# orchestrator.yaml example
- type: agent
  name: Daily Research Briefing (DRB)
  cron: 0 8 * * *  # Daily at 8 AM
  output_path: AI/Briefings
  agent_params:
    max_topics: 5
    lookback_days: 7
    search_depth: standard  # standard | deep
    include_voice: false
```

## Example Output

```markdown
## Summary

Today's briefing covers 3 active research areas: LLM Evaluation (new benchmark paper), PKM Tools (Obsidian plugin update), and Search Technology (algorithm changes).

## Topic Updates

### 1. LLM Evaluation
**Active Interest**: LLM-as-a-judge methods

#### Key Updates
- **"JudgeBench: A Comprehensive Benchmark for LLM Evaluators"** - arXiv
  New benchmark comparing 15 LLM judges across diverse tasks. Claude and GPT-4 show highest correlation with human judgments.
  → [Paper](https://arxiv.org/abs/...)

- **"Multi-turn Evaluation with Synthetic Dialogues"** - Google AI Blog
  Proposes using synthetic conversations to stress-test LLM evaluators.
  → [Blog](https://ai.googleblog.com/...)

#### Implications
Consider JudgeBench for validating evaluation pipeline. Synthetic dialogue approach could improve coverage.
```

## Notes

- **Topic detection**: Uses file modification time, not content analysis
- **Search freshness**: Prioritizes current year content
- **Deduplication**: Skip content already saved in vault
- **Language**: Search in English, summarize in your preferred language
- **Voice option**: Can add voice summary via Voice Mode MCP
