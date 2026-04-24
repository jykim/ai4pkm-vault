---
name: gobi-social-agent
description: >-
  Reactive social agent for Gobi Space and Gobi Desktop. Invoked as the final
  step of the DDW (Daily Driver Workflow) pipeline or on demand. Scans the
  user's recent vault activity and the Gobi community folder, then drafts a
  social post that responds to what the community is discussing. Produces
  Brain Update drafts, new Thread drafts, or Reply drafts to existing community
  threads in `_Gobi_/GSA/` — always gated by user approval. Use when the user
  wants to monitor community context and surface draft responses, or says
  "GSA 돌려줘" / "run the social agent" / "draft a reply to community threads".
allowed-tools: Bash(python3:*), Read, Glob, Grep, Write, Edit
metadata:
  author: ai4pkm
  version: "0.2.0"
---

# Gobi Social Agent (GSA)

커뮤니티 컨텍스트에 반응하여 소셜 포스트 드래프트를 주기적으로 생성하는 에이전트. 사용자가 "혼자 올리는 일방 포스팅"이 아니라 "커뮤니티 대화에 실시간으로 참여"할 수 있도록 돕는다.

## When to use

- DDW 파이프라인의 마지막 단계로 자동 호출 (`MCE → PLL → MER → ULC → GSA`)
- 사용자가 "GSA 돌려줘", "소셜 에이전트 한 번 돌려", "커뮤니티에 뭐 답할 거 있나 봐줘"라고 요청할 때
- 사용자가 최근 커뮤니티 스레드/BU에 대해 "내가 뭘 답할 수 있나"를 물을 때

## When NOT to use

- 특정 소스 파일 하나로 BU를 만들고 싶을 때 → `Post Brain Update (PBU)` 프롬프트 사용
- 외부 플랫폼(X/Threads)에서 관련 콘텐츠 발견 → `Social Discovery Bot (SDB)` 사용
- 드래프트 없이 바로 발행 → 본 스킬은 항상 `approve_for_publish: false`로 드래프트만 생성

## Inputs

- **My signals** (지난 24h 수정): `Journal/`, `AI/Roundup/`, `AI/Summary/`, `AI/Analysis/`, `AI/Events/`, `AI/Sharable/`, `_Outbox_/BrainUpdates/`
- **Community signals** (지난 3일): `_Gobi_/BrainUpdates/`, `_Gobi_/Threads/`
- **State**: `_Settings_/Skills/gobi-social-agent/state/_state.json` — 마지막 실행 시각, 이미 사용한 소스 히스토리

## Outputs

모든 드래프트는 `_Gobi_/GSA/` 한 폴더에 모인다 (리뷰·승인 편의).

| 종류 | 파일명 형식 | 참고 |
|---|---|---|
| BU 드래프트 | `_Gobi_/GSA/YYYY-MM-DD [제목] - BU.md` | PBU 포맷 |
| Thread 드래프트 | `_Gobi_/GSA/YYYY-MM-DD [제목] - Thread.md` | CTP 포맷 |
| Reply 드래프트 | `_Gobi_/GSA/YYYY-MM-DD [제목] - Reply-<thread-id>.md` | `reply_to_thread` 포함 |
| Skip 로그 | `_state.json`에 `kind: skip` + note | 파일 생성 안 함 |

리뷰 뷰: `_Settings_/Bases/GSA Drafts.base` (Pending Review / Approved / All 탭).

Frontmatter는 항상 `approve_for_publish: false` — 발행은 사용자 승인 후 수동.

## Workflow

### Step 1 — Collect signals

볼트 루트에서 실행:

```bash
python3 _Settings_/Skills/gobi-social-agent/scripts/collect_signals.py \
  --hours 24 --days 3
```

출력 JSON:
- `my_signals`: 내 최근 파일 (path, title, modified, tags, preview, already_used)
- `community_signals`: `_Gobi_/BrainUpdates/`, `_Gobi_/Threads/` (타 사용자 포스트)

옵션:
- `--vault <path>`: 볼트 루트 명시 (기본: CWD)
- `--hours <N>` / `--days <N>`: 수집 윈도우
- `--limit-my` / `--limit-community`: 결과 개수 제한
- `--state <path>`: state 파일 경로 (기본: `_Settings_/Skills/gobi-social-agent/state/_state.json`)

### Step 2 — Decide: draft or skip

**SKIP 조건** (아무것도 생성하지 않고 종료):
- `my_signals` 중 `already_used: false`가 없음
- 마지막 드래프트 생성이 2시간 이내 (스팸 방지)
- 의미 있는 인사이트 파일이 없음 (Journal-only이고 Roundup/Analysis 없음)
- `community_signals`에서 반응할 만한 새 스레드/BU가 없음

SKIP 기록:

```bash
python3 _Settings_/Skills/gobi-social-agent/scripts/update_state.py \
  --kind skip --draft "" --note "no new signals"
```

### Step 3 — Pick source & format

**가장 강한 내 시그널 1개** 선정:
- 우선순위: `AI/Analysis/` > `AI/Summary/` > `AI/Roundup/` > `AI/Events/` > `Journal/`
- `already_used: true` 제외

**형식 결정 (Reply 우선)**:
- **Reply (댓글)**: 커뮤니티 스레드에 직접 답할 수 있으면 최우선 — 가장 반응형
- **New Thread**: 커뮤니티 논의와 연관된 새 관찰·질문 (1k자 이하)
- **Brain Update**: 에세이성 인사이트 (400–800단어)

커뮤니티 시그널은 **반응 타겟과 참고용**. 어떤 질문이 열려 있는지, 어떤 BU에 코멘트가 필요한지 파악.

### Step 4 — Generate draft

파일은 모두 `_Gobi_/GSA/`에 생성. 파일명 suffix(` - BU.md` / ` - Thread.md` / ` - Reply-<id>.md`)로 종류 구분.

**BU** → `Post Brain Update (PBU)` 프롬프트 로직:
- 400–800단어 에세이, H2 없이 본문 시작
- 원문 인용 블록쿼트, 마무리 `→ **관련 분석**: [[...]]`

**Thread/Reply** → `Create Thread Postings (CTP)` 프롬프트 로직:
- Social Media Template (Overview → Contents → Sources)
- 각 thread 1k자 이하, 자체 완결형
- Reply면 frontmatter에 `reply_to_thread: <thread-id>` 기록

**Frontmatter 필수 필드**:

```yaml
---
title: "..."
date: YYYY-MM-DD
post_kind: bu              # bu | thread | reply
source_file: "path/to/source"
generated_by: GSA
approve_for_publish: false
approve_for_thread: false
reply_to_thread: ""        # reply일 때만 값 채움
community_context:
  - "_Gobi_/... — 비슷한 토픽"
  - "_Gobi_/... — 관련 논의 중"
tags: [...]
---
```

`post_kind`와 `reply_to_thread`는 `_Settings_/Bases/GSA Drafts.base`의 컬럼으로 사용되니 항상 포함.

`community_context`는 승인자가 "커뮤니티에 이미 돌고 있는 얘기인지" 판단하기 위한 주석.

### Step 5 — Update state

```bash
python3 _Settings_/Skills/gobi-social-agent/scripts/update_state.py \
  --kind bu \
  --source "AI/Analysis/YYYY-MM-DD ... - Agent.md" \
  --draft "_Gobi_/GSA/YYYY-MM-DD ... - BU.md"
```

`--kind` 값: `bu` | `thread` | `skip`

### Step 6 — Open draft (optional)

```bash
open "obsidian://open?vault=<VAULT_NAME>&file=_Gobi_/GSA/..."
```

또는 사용자가 `_Settings_/Bases/GSA Drafts.base` 뷰에서 일괄 리뷰.

## Review & Approval Flow

1. GSA가 `_Gobi_/GSA/`에 드래프트 생성 (`approve_for_publish: false`)
2. 사용자가 `_Settings_/Bases/GSA Drafts.base`의 **Pending Review** 탭에서 일괄 조망
3. 파일 열어 검토 후 frontmatter 플래그 flip:
   - `approve_for_publish: true` → Gobi 발행 대상
   - `approve_for_thread: true` → Thread 발행 대상
4. 발행은 별도 수동 단계: `gobi brain post-update --auto-attachments ...`
5. 승인된 항목은 **Approved** 탭으로 이동 (동일 base 필터)

## Principles

### Reactive over broadcast
커뮤니티 질문·논의에 답하는 Reply가 일방적 포스팅보다 가치 높음. 매 실행에서 "이 시점에 열려 있는 커뮤니티 질문이 있는가"를 먼저 체크.

### No duplication
- 타 사용자 BU 내용을 그대로 복사 금지
- `used_sources`에 기록된 내 시그널 재사용 금지
- 같은 스레드에 이미 답글을 달았으면 스킵

### Credit, don't copy
영감을 받은 커뮤니티 포스트는 `community_context`에 기록하고, 본문에서 원 작성자를 명시적으로 언급.

### Always human approval
- 자동 발행 금지. 모든 드래프트는 `approve_for_publish: false` 유지
- 사용자가 Obsidian에서 확인 후 `true`로 변경
- 발행은 별도 단계: `gobi brain post-update --auto-attachments ...`

### Rate limit
- DDW가 30분마다 부르지만 실제 생성은 하루 2–4개 수준이 적정
- 2시간 쿨다운 (마지막 드래프트 후)
- 야간 시간대는 내부 SKIP 판단으로 억제

## DDW integration

GSA는 DDW 파이프라인의 마지막 단계로 호출된다:

```
MCE → PLL → MER → ULC → GSA
```

DDW prompt (`_Settings_/Prompts/Daily Driver Workflow (DDW).md`)의 Step 5 참고. 별도 cron 등록 불필요.

수동 실행 시에도 동일한 scripts + 워크플로우:

```bash
python3 _Settings_/Skills/gobi-social-agent/scripts/collect_signals.py --hours 24 --days 3
# Agent가 Step 2~4 판단 & 작성
python3 _Settings_/Skills/gobi-social-agent/scripts/update_state.py --kind bu --source ... --draft ...
```

## Related

- `Daily Driver Workflow (DDW)` — GSA를 자동 호출하는 상위 파이프라인
- `Post Brain Update (PBU)` — 단일 소스 BU 생성 (GSA의 Step 4에서 재사용)
- `Create Thread Postings (CTP)` — Thread 후보 생성 (GSA의 Step 4에서 재사용)
- `Social Discovery Bot (SDB)` — 외부 플랫폼(X/Threads) 발견용 (GSA는 내부 커뮤니티 전용, 보완 관계)
- `_Settings_/Bases/GSA Drafts.base` — 리뷰·승인 뷰

## Files

```
_Settings_/Skills/gobi-social-agent/
├── SKILL.md
├── scripts/
│   ├── collect_signals.py
│   └── update_state.py
└── state/
    └── _state.json       # runtime-generated

_Gobi_/GSA/               # drafts live here
_Settings_/Bases/GSA Drafts.base   # review view
```
