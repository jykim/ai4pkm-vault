---
title: Post-Process Capture (PPC)
abbreviation: PPC
category: ingestion
created: 2026-04-08
---
Process a new capture file from `_Gobi_/Captures/` and produce either a meeting summary in `AI/Events/` or an analysis document in `AI/Analysis/`.

## Input
- Capture file path in `_Gobi_/Captures/` (optional)
- If not provided: use the most recently modified `.md` file in `_Gobi_/Captures/`
  ```bash
  ls -t /Users/lifidea/Vaults/OVM/_Gobi_/Captures/*.md | head -1
  ```

## Output
- **Meeting** → `AI/Events/YYYY-MM-DD [Title] - OJ.md`
- **Analysis** → `AI/Analysis/YYYY-MM-DD [Title] - Claude Code.md`
- **Canvas** → `AI/Canvas/YYYY-MM-DD [Title].canvas` (if paired canvas exists)

## Main Process

```
1. LOAD FILE
   - Read the capture file fully (chunk if >200 lines)
   - Extract creation date from filename (YYYY-MM-DD-HH-MM-SS prefix)

2. CLASSIFY CONTENT
   Meeting indicators (→ AI/Events):
     - Multiple speakers (timestamp > lines), conversation-style transcript
     - Mentions attendees, agenda, or action items
     - Gobi session header with sessionCount > 1
   Analysis indicators (→ AI/Analysis):
     - Single author notes, monologue, brainstorming
     - Research, ideas, concepts, frameworks
     - No clear conversational back-and-forth

3A. IF MEETING → AI/Events/
   a. Extract: title, date, attendees, key topics, action items
   b. Check Google Calendar (MCP) for matching event if date is recent
   c. Output file: AI/Events/YYYY-MM-DD [Title] - OJ.md
   d. Frontmatter (required fields):
      - scheduled_time: YYYY-MM-DD HH:MM
      - status: completed
      - event_type: meeting
      - attendees: [list]
      - tags: [meeting, ...]
      - created: YYYY-MM-DD HH:MM:SS
      - source: "[[_Gobi_/Captures/filename]]"
   e. Content structure:
      ## Overview
      (2-3 sentences: venue, duration, attendees with brief roles/context)
      ## Key Discussion Points
      (H3 per topic; each section includes verbatim quotes in blockquote format,
       specific details/numbers, and contrasting perspectives where they exist)
      ## Action Items
      (table with 항목 | 담당 | 기한 columns)
      ## Notes
      (key quotes, peripheral context, memorable moments)

3B. IF ANALYSIS → AI/Analysis/
   a. Extract: title, main thesis, key insights, themes
   b. Output file: AI/Analysis/YYYY-MM-DD [Title] - Claude Code.md
   c. Frontmatter (required fields):
      - title: "Descriptive title"
      - created: YYYY-MM-DD HH:MM:SS
      - tags: [analysis, ...]
      - source: "[[_Gobi_/Captures/filename]]"
   d. Content structure:
      ## Summary
      ## Key Insights
      ## Analysis (themes, frameworks, implications)

4. CANVAS PROCESSING (if paired .canvas exists)
   a. Locate paired canvas: same timestamp prefix as the .md
      → `_Gobi_/Captures/[timestamp]-[Title].canvas`
   b. Read and analyze existing canvas nodes/groups
   c. Reorganize using 2-COLUMN CHRONOLOGICAL layout:

      STRUCTURE:
      - Title node: spans full width (both columns), top
      - Left column (width ~470): one node per topic — title + timestamp + 2-3 sentence summary
        with enough context for someone who wasn't present to understand why it matters
      - Right column (width ~800): matching detail node — H3 sections with specific details,
        verbatim quotes (exact wording from transcript), contrasting perspectives, numbers
      - Reference node: spans full width (both columns), bottom

      LAYOUT:
      - Left column x: -800, right column x: -282
      - Title node x: -800, width: 1320
      - Reference node x: -800, width: 1320
      - Rows top-to-bottom in chronological order (y increases downward)
      - Match row heights: left and right node same y and height per row
      - Gap between rows: ~50px

      COLOR-CODE by topic type (apply to BOTH left and right nodes in same row):
          💡 아이디어/전략 → color "6" (cyan)
          🏗️ 시스템/아키텍처 → color "5" (green)
          🔄 프로세스/온보딩 → color "3" (yellow)
          ⚠️ 문제점/한계 → color "2" (orange)
          🚀 다음 단계/액션 → color "1" (red)
          💬 소통/참조 → color "4" (purple)

      EDGES (required):
      - Title → first left node (bottom→top)
      - Each left node → its right node (right→left, showing main→detail)
      - Each left node → next left node (bottom→top, showing chronological flow)
      - Last left node → reference node (bottom→top)

      CONTENT QUALITY:
      - Left node: enough context that a non-attendee understands the topic and stakes
      - Right node: direct quotes from transcript, specific names/numbers, competing views
      - Do NOT use generic labels like "주요 포인트" — be specific about what was said

   d. Save cleaned canvas to `AI/Canvas/YYYY-MM-DD [Title].canvas`
   e. Reference node text: `→ 미팅 노트: [[AI/Events/YYYY-MM-DD [Title] - OJ]]`

5. POST-CREATION
   - Open the output document in Obsidian
   - If canvas was created: also open canvas (`obsidian://open?vault=OVM&file=AI/Canvas/YYYY-MM-DD [Title].canvas`)
   - Add link to today's journal under "완료한 작업" or "Background Tasks"
   - Do NOT open the original capture files
```

## Classification Rules

### Meeting Signals (score each +1)
- Transcript timestamps with `AM>` or `PM>` format
- More than 2 distinct speakers/voices
- Words: "attendees", "agenda", "action item", "sync", "미팅", "회의"
- Gobi `sessionCount` ≥ 1 with multiple conversation turns

### Analysis Signals (score each +1)
- Single continuous narrative or monologue
- Ideas/frameworks/concepts without conversational replies
- Words: "분석", "전략", "아이디어", "리서치", "framework"
- Title implies ideation (e.g. "차별점", "방향", "전략")

**If score is tied**: prefer Meeting if any timestamps found, else Analysis.

## Caveats

### Existing File Check
- Always check if output file already exists before creating
- If exists: update rather than overwrite

### Language
- Korean default; English if capture is predominantly English
- Preserve original quotes in source language

### Title Extraction
- Use Gobi `title:` field from frontmatter if present
- Else derive from filename (strip date prefix and timestamp suffix)
- Else derive from first meaningful line of content

### Date Accuracy
- Use date from filename prefix (YYYY-MM-DD), not today's date
- Cross-check with Gobi `createdAt` field in frontmatter

### Canvas Processing
- Only process canvas if a paired `.canvas` file exists at the same path
- Skip canvas step silently if no paired canvas found
- Output canvas to `AI/Canvas/`, NOT to `_Gobi_/Captures/`
- Open canvas with full `.canvas` extension: `obsidian://open?vault=OVM&file=AI/Canvas/YYYY-MM-DD%20[Title].canvas`
- Do NOT open the original Gobi canvas from `_Gobi_/Captures/`
- If canvas is mostly empty (< 3 nodes): skip canvas processing
