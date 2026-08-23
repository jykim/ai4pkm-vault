---
name: meeting-dictation
description: Silently capture and organize a live meeting from voice transcript input. Use when the user asks for meeting dictation, a quiet live transcript, rolling meeting notes, or a post-meeting summary without assistant interruptions.
---

# Meeting Dictation

## Start

Confirm the capture mode once, then remain silent until the user explicitly asks to stop, summarize, or extract actions. Do not acknowledge partial transcript updates, offer suggestions, ask routine questions, or provide progress reports.

Ask for the meeting title only if it is necessary to name the final note. Preserve the user's language.

## Capture

Treat each incoming transcript segment as sequential meeting content. Accumulate it without correcting or interpreting unclear speech in real time.

Do not claim to record audio or guarantee uninterrupted capture. Work only from transcript content received in the active session. If the session or input stops, retain only the content actually received.

Keep speaker labels only when they are explicitly supplied or reliably identified. Mark uncertain names, terms, and numbers as `[확인 필요]` rather than inventing them.

## Finish

On a clear request such as “그만”, “정리해줘”, “회의록 만들어줘”, or “할 일만 뽑아줘”, produce the requested result from the captured content.

Unless the user requests another destination, save completed meeting notes in `AI/Events` using the existing event-note format. Use a filename of `YYYY-MM-DD {meeting title}.md`; omit unavailable date or title only after asking once. Do not write or modify the file during capture.

Default completed-note format:

```markdown
---
title: "{meeting title}"
event_type: meeting
status: completed
is_summarized: true
scheduled_time: {YYYY-MM-DD HH:MM or 미정}
duration_minutes: {minutes or 미정}
category: {category or 미정}
source: meeting-dictation
created: {current local timestamp}
attendees:
tags:
  - meeting
---

## Overview

- **일시**: {date/time or 미정}
- **성격**: {meeting title or 미정}
- **참석자**: {known attendees or 미정}

## Meeting Minutes

## Action Items

## Related Links
```

For a summary requested only in chat, retain the same section order but omit frontmatter and empty sections.

Write each action item as a task sentence. Include a responsible person or deadline only when explicitly established. Do not infer decisions, owners, deadlines, links, tags, or commitments. Record uncertainty as `미정` in Overview or a concise note in Meeting Minutes.

## Privacy

Before capture begins, remind the user once to obtain any required consent from meeting participants. Do not repeat the reminder during the meeting.
