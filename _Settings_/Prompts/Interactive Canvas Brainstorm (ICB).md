---
title: Interactive Canvas Brainstorm
abbreviation: ICB
category: visualization
created: 2026-01-22
tags:
  - prompt
  - canvas
  - brainstorming
  - visualization
---

## Purpose

Analyze voice recordings or active conversations in real-time, automatically generating and updating an Obsidian Canvas brainstorming map.

## Overview

Visualize user thoughts in real-time. Supports both passive mode transcripts and active conversations. Extracts topics, categorizes them, and displays on canvas with automatic updates on file changes.

## Input

**Source files (auto-detected):**
- Passive mode: `{{history_path}}/PassiveMode/{{datetime}}.md`
- Active conversation: `{{history_path}}/{{session-id}}.md`
- Existing canvas: `{{canvas_path}}/{{date}} *.canvas`

**Mode auto-detection:**
- PassiveMode/ path → Passive mode
- History/*.md → Active conversation mode
- User can specify manually

## Output

- Brainstorming canvas: `{{canvas_path}}/{{date}} {{topic}}.canvas`

## Process

### Phase 0: Source File Detection

```
1. FIND SOURCE FILE
   Passive mode:
     - Check most recent file in PassiveMode/ folder
     - Start one-shot monitoring with file watcher

   Active conversation:
     - Check latest conversation file in History/
     - Manual execution ("update canvas")
     - Optional file monitoring

2. AUTO-DETECT MODE
   - Determine mode from file path
   - PassiveMode/ → Passive mode
   - History/*.md → Active conversation mode

3. FILE CHANGE DETECTION (passive only)
   while true:
     - Wait for file change with file watcher
     - Execute Phase 1 on change
     - Update canvas and resume monitoring
```

### Phase 1: Content Analysis

```
1. READ SOURCE FILE
   - Read entire content
   - Auto-detect format

2. DETECT FORMAT
   Passive mode format:
     User|HH:MM:SS> utterance content

   Active conversation format:
     User|HH:MM:SS PM> user message
     Assistant|HH:MM:SS PM> AI response

3. EXTRACT TOPICS
   FOR EACH conversation turn:

     Passive mode:
       - Analyze user utterances only
       - Extract by timestamp
       - Identify key topics/requests

     Active conversation:
       - Analyze User + Assistant together
       - Track question-answer flow
       - Extract decisions/agreements
       - Extract generated document references

     Common:
       - Identify key topics/requests
       - Classify into categories
       - Determine priority/importance

4. CATEGORIZE TOPICS
   Auto categories (common):
     - Tools/Dev: Technology, coding, tools
     - Projects/Work: Tasks, projects, work items
     - Relationships: Team, collaboration
     - Ideas: New thoughts, brainstorming
     - Learning: Research, study topics

   Additional categories (active conversation):
     - Decisions: Agreed conclusions, next actions
     - Workflow: Process, system design
     - In Discussion: Unresolved topics
     - Analysis: Data, comparison, evaluation
```

### Phase 2: Canvas Layout Generation

```
1. LAYOUT PRINCIPLES
   - Place source file at center
   - Categories as large container boxes (530-640px width)
   - Box height under 850px (visible at a glance)
   - 2-column layout within categories by default
   - Horizontal connections between related nodes

2. NODE POSITIONING (reference)

   Source file (center):
   - x: -150, y: -100
   - width: 300, height: 200

   Category containers (example):
     Left category:
       - Container: x: -750, y: -400, 530x850
       - Left column nodes: x: -710 (container+40)
       - Right column nodes: x: -460 (container+290)

     Top-right category:
       - Container: x: 200, y: -500, 640x650
       - Left column nodes: x: 240 (container+40)
       - Right column nodes: x: 520 (container+320)

     Bottom-right category:
       - Container: x: 200, y: 200, 640x540
       - Full-width nodes: x: 240, width: 540

3. NODE DIMENSIONS
   - Standard topic: 220-260px width, 140-180px height
   - Full-width nodes: 480-540px width
   - File references: 230-260px width, 100-180px height

4. CROSS-CONNECTIONS
   - Horizontal connections for same-row nodes (fromSide: right → toSide: left)
   - Connect insights → actions
   - Use horizontal connections to compress vertical height
```

### Phase 3: Canvas Update

```
1. GENERATE CANVAS JSON
   {
     "nodes": [...],
     "edges": [...]
   }

2. NODE TYPES
   Common:
     - source-file: file type, source reference
     - cat-*: text type, category container
     - topic-*: text type, individual topic
     - insight-*: text type, insight/conclusion
     - action-*: text type, action item

   Active conversation additional:
     - decision-*: text type, decision (green highlight)
     - question-*: text type, unresolved question (yellow)
     - reference-*: file type, generated document reference

3. COLOR SCHEME
   | Color | ID | Usage |
   |-------|-----|-------|
   | Red | 1 | Priority/Important |
   | Orange | 2 | Relationships |
   | Yellow | 3 | In Progress |
   | Purple | 4 | References |
   | Green | 5 | Insights/Decisions |
   | Cyan | 6 | Meta/PKM |

4. WRITE CANVAS FILE
   - Save to {{canvas_path}}/{{date}} {{topic}}.canvas
```

## Node Templates

### Standard Topic Node

```json
{
  "id": "topic-1",
  "type": "text",
  "text": "### Topic Title\n\n\"Original quote from source\"\n\n→ Key insight\n→ Action item",
  "x": -710, "y": -330,
  "width": 230, "height": 160,
  "color": "2"
}
```

### Decision Node (Active Mode)

```json
{
  "id": "decision-1",
  "type": "text",
  "text": "### Decision: Project Name\n\n**Agreement:**\n• Point 1\n• Point 2",
  "x": 240, "y": 270,
  "width": 260, "height": 180,
  "color": "5"
}
```

### Reference Node (Active Mode)

```json
{
  "id": "reference-1",
  "type": "file",
  "file": "AI/Analysis/document.md",
  "x": 540, "y": 270,
  "width": 260, "height": 100,
  "color": "4"
}
```

## Layout Pattern

```
     Left Category               Top-Right Category
     530x850                     640x650
┌───────────────────┐      ┌───────────────────────┐
│ topic-1 │ topic-2 │      │ topic-3 │ reference-1 │
│    ↓    │    ↓    │      │    ↓    │      ↓      │
│ topic-4 │ action  │  ◉   │ topic-5 │ decision-1  │
│    ↓    │         │ src  │    ↓    │             │
│ topic-6─┼─→───────│      │ topic-7 │             │
│    ↓    │         │      └─────────┴─────────────┘
│ insight │         │
└─────────┴─────────┘      Bottom-Right Category
                           640x540
                     ┌───────────────────────┐
                     │ topic-8 ──┼─→ topic-9 │
                     │     ↓     │      ↓    │
                     │ topic-10 (540px full-width) │
                     └───────────────────────┘
```

## Best Practices

### Compact Layout
- Keep category box height under 900px
- Entire canvas should be visible at once
- Use 2-column layout when content grows

### Deduplication
- Merge similar content
- Remove unnecessary nodes
- Keep only essentials

### Horizontal Connections
- Don't just stack vertically
- Add cross-connections for related nodes
- Reduces vertical space

### Real-time Feedback
- Apply user layout feedback immediately
- "Box too tall" → Convert to 2 columns
- "Add connection" → Add cross-connection

### Mode-Specific Processing

**Passive mode:**
- Focus on utterance flow
- Track emotional/thought changes
- Emphasize continuity

**Active conversation:**
- Clearly mark decisions
- Add generated document references
- Visualize discussion → decision flow
- Separately show unresolved questions

## Caveats

### Skip Conditions
- Only meaningless utterances (interjections, language tests)
- Same content as existing canvas
- Insufficient content right after conversation start

### File Size
- Prioritize recent content for large transcripts
- Summarize/merge older utterances

### Mode Detection Failure
- Default: Active conversation mode
- Ask user to confirm

## Quality Checklist

Before generating canvas:

- [ ] Mode correctly detected (passive/active)
- [ ] Unique ID assigned to all nodes
- [ ] No node overlap (30-50px minimum gap)
- [ ] Consistent color scheme
- [ ] Center source node clearly marked
- [ ] Edges don't unnecessarily cross
- [ ] Wiki links validated
- [ ] Active mode: Decisions highlighted green
- [ ] Active mode: Document references added
- [ ] Renders without error in Obsidian

## Related

- [[obsidian-canvas]] - Canvas creation base skill
