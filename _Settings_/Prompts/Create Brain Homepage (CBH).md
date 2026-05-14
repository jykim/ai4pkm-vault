---
title: "Create Brain Homepage (CBH)"
abbreviation: CBH
category: creation
created: "2026-04-10"
updated: "2026-05-13"
---

> **Skill wrapper.** This prompt now delegates to the `create-gobi-homepage` skill, which ships 4 style templates (neon-terminal, minimal-editorial, magazine, brutalist), an interview for hero links / gobi.* feature opt-in / brand overrides, and an up-to-date `window.gobi` API reference.

**Skill location**: [[_Settings_/Skills/create-gobi-homepage/SKILL]]
**API reference**: [[_Settings_/Skills/create-gobi-homepage/reference/gobi-api]]

## How to invoke

- `/create-gobi-homepage` — full interview, default output `_Gobi_/app/home.html`
- `/CBH` — same, via legacy abbreviation
- `/create-gobi-homepage --style=minimal-editorial --features=kgraph,chat` — skip interview with CLI args

## Why this changed

The original CBH prompt always produced a single neon-terminal style and referenced now-deprecated APIs (`gobi.listBrainUpdates`, `?brainUpdateId=`). The skill makes style a choice, makes features opt-in, and uses current API names (`gobi.listPersonalPosts`, `?postId=`).
