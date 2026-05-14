---
name: gobi-social-agent
description: >-
  Reactive social agent for Gobi Space and Gobi Desktop. Invoked on demand.
  Scans the user's recent vault activity and the Gobi community folder, then
  drafts a social post that responds to what the community is discussing.
  Produces Brain Update drafts, new Thread drafts, or Reply drafts to existing
  community threads in `_Gobi_/GSA/` — always gated by user approval. Use when
  the user wants to monitor community context and surface draft responses, or
  says "GSA 돌려줘" / "run the social agent" / "draft a reply to community
  threads".
allowed-tools: Bash(python3:*), Read, Glob, Grep, Write, Edit
metadata:
  author: ai4pkm
  version: "0.5.0"
---

# Gobi Social Agent (GSA)

커뮤니티 컨텍스트에 반응하여 소셜 포스트 드래프트를 주기적으로 생성하는 에이전트. 사용자가 "혼자 올리는 일방 포스팅"이 아니라 "커뮤니티 대화에 실시간으로 참여"할 수 있도록 돕는다.

## When to use

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

추가로, **Gobi 드래프트 카드**가 함께 생성된다 (Step 4 참고) — 클라이언트에서 *Approve & publish* / *Edit before posting* / *Discard* 액션이 보임. 드래프트 카드는 알림용이지 본문 미리보기가 아니라 `[[wikilinks]]`를 렌더링하지 않음 (실제 본문은 vault markdown).

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

**선택: 커뮤니티 컨텍스트 보강** (gobi-cli v2.0.16+) — `gobi space list-topics` / `gobi space list-topic-posts <slug>`로 토픽별 최근 포스트를 가져와 community_signals에 더할 수 있다. 현재 구현은 vault-mirror(`_Gobi_/`)만 보지만, topic feed가 더 빠른 신호일 수 있음.

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
reply_to_thread: ""        # reply일 때만 값 채움
community_context:
  - "_Gobi_/... — 비슷한 토픽"
  - "_Gobi_/... — 관련 논의 중"
tags: [...]
# === added after publish (Step 4 below) ===
# published_post_id: <id>
# published_at: YYYY-MM-DD HH:MM:SS PDT
# published_target: "global" | "space:<slug>"
---
```

`post_kind`, `reply_to_thread`, `published_post_id`, `published_at`, `published_target`는 `_Settings_/Bases/GSA Drafts.base`의 컬럼/필터로 사용되니 발행 단계에서 반드시 채울 것 (Pending Review / Approved-not-published / Published 탭 분기).

`community_context`는 승인자가 "커뮤니티에 이미 돌고 있는 얘기인지" 판단하기 위한 주석.

### Step 5 — Push Gobi draft + Update state

**드래프트 작성 후 즉시** Gobi 클라이언트에도 드래프트 카드를 푸시 (gobi-cli v2.0.16+):

```bash
draft_id=$(gobi --json draft add "GSA: <title>" - \
  --priority 5 \
  --action "Approve & publish::approve_for_publish: true 로 flip 후 발행" \
  --action "Edit before posting::파일을 열어 검토" \
  --action "Discard::파일 삭제" \
  < "_Gobi_/GSA/<file>.md" | jq -r '.data.id')
```

성공 시 markdown frontmatter에 `gobi_draft_id: <draft_id>` 추가. 발행 단계에서 `--draft-id <id>`로 전달하면 Gobi 클라이언트가 자동으로 "Open post" 버튼을 렌더링.

**Caveat**: Gobi 드래프트 본문은 plain stdin이고 `[[wikilinks]]`를 렌더링하지 않음 — *알림 + 액션* 용도이지 미리보기 아님.

그다음 vault-side state 업데이트:

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

## Pre-publish preflight (gobi-cli ≥ 2.0.16)

발행 전에 항상 다음을 확인. 실패하면 발행 멈추고 사용자에게 알릴 것.

0. **Auth 상태**: `gobi --json auth status` → `{success: true}`. 실패면 `gobi auth login` 후 device-code flow 진행 (v2.0.16부터 auth는 namespaced — `gobi login` 아닌 `gobi auth login`).
1. **Vault 공개 상태**: `gobi --json vault status --vault-slug jyk` → `isPublished: true`. `false`면 `gobi vault publish` 먼저 (PUBLISH.md의 title/description 필수). 비공개 vault에 `--auto-attachments`로 올리면 webdrive에 파일은 가지만 `gobispace.com/@jyk`에서 도달 불가 → 독자가 broken `[[wikilinks]]` 봄.
2. **`source_file` 존재**: frontmatter의 `source_file` 경로가 실제로 있는지 `ls "$source"` 확인. (2026-04-28 Karpathy BU 사례: 파일명에 `?`/`Sonnet` 누락된 채 발행되어 링크 깨졌음.)
3. **본문 위키링크 모두 resolve**: 각 `[[...]]`가 vault root 기준 실제 파일 가리키는지. `.md` 확장자는 없어도 됨 (CLI 자동 추가).
4. **위키링크는 bare 형식만**: `[[path]]` ✅ — `[[path|alias]]` ❌ (gobi-cli `attachments.js` `extractWikiLinks` 정규식이 alias까지 path로 캡처해서 항상 fail; v2.0.16까지 미수정). 표시 텍스트 필요하면 `[[path]] (display text)` 또는 markdown link `[text](URL)`.
5. **어퍼스트로피/물음표 파일명**: `'` (ASCII apostrophe) 또는 `?` 가 들어간 파일을 위키링크로 가리키면 Gobi 서버가 viewer URL 생성 시 ASCII `'` → 타이포그래픽 `'` (`%E2%80%99`)로 자동 변환 → 404. 이 경우 explicit markdown link 사용: `[표시 텍스트](https://gobispace.com/@jyk?file=경로%20%27%20%3F%20인코딩됨)`.

## Review & Approval Flow

1. GSA가 `_Gobi_/GSA/`에 드래프트 생성 (`approve_for_publish: false`)
2. 사용자가 `_Settings_/Bases/GSA Drafts.base`의 **Pending Review** 탭에서 일괄 조망
3. 파일 열어 검토 후 frontmatter 플래그 flip: `approve_for_publish: true` → **Approved (not yet published)** 탭으로 이동
4. 발행 (Pre-publish preflight 통과 후, gobi-cli ≥ 2.0.16). 드래프트에 `gobi_draft_id`가 있으면 `--draft-id <id>` 옵션을 추가해 Gobi 카드와 자동 연결:
   - **`bu` 브로드캐스트** (default — 모든 vault 공개 피드) → `gobi global create-post --auto-attachments --title "..." --content - --draft-id <gobi_draft_id> < <file>`
     - 결과 share URL: `https://gobispace.com/@jyk?postId={id}`
   - **`bu` space 타겟** 또는 **`thread`** → `gobi space --space-slug <slug> create-post --auto-attachments --title "..." --content - --draft-id <gobi_draft_id> < <file>`
     - 결과 share URL: `https://gobispace.com/spaces/<slug>?postId={id}` (overlay) 또는 `/spaces/<slug>/posts/{id}` (dedicated)
   - **`reply`** → `gobi space --space-slug <slug> create-reply <postId> --content - < <file>` (첨부 있으면 `--auto-attachments` 추가, v2.0.5+)
   - **이미 발행된 포스트 재편집** → `gobi global edit-post <id> --auto-attachments --content -` 또는 `gobi space --space-slug <slug> edit-post <id> --auto-attachments --content -` (v2.0.8부터 `vault sync` 우회 불필요).
5. **BU-to-BU 참조** (본문에서 다른 발행된 BU를 가리킬 때): `[[Outbox/BrainUpdates/...]]` 위키링크 ❌ → `gobi global list-posts --mine`으로 post id 찾아 `[BU 제목](https://gobispace.com/@jyk?postId=<id>)` markdown link 사용.
6. 승인+발행 후 **After-publish bookkeeping**:
   - 드래프트 frontmatter에 `published_post_id`, `published_at`, `published_target` 추가 → **Published** 탭으로 자동 이동 (base filter)
   - `update_state.py --kind bu --source "published:<id> (<target>)" --draft "<file>" --note "..."` 로 `_state.json.history` 기록
   - **syncfiles 보정**: `--auto-attachments`가 `.gobi/syncfiles`에 추가하는 라인이 leading `/` 누락 (CLI 버그, v2.0.16까지 미수정). 발행 후 정리: `sed -i.bak -E 's|^([^/#].*)$|/\1|' .gobi/syncfiles`. 안 하면 다음 sync에서 HTTP 400.

## Stale-draft rewriting before publish

드래프트가 24시간 이상 묵었으면 발행 전 본문 시점 표현과 frontmatter `date`를 보정. 청중이 "오늘"을 발행일 기준으로 읽기 때문.

| 패턴 | 교체 |
|---|---|
| `오늘 아침` / `오늘` | `지난주 (M/D)` 또는 `M/D` |
| `어제·오늘` | `최근` |
| `어제 <name>이 제안한` | `<name>이 제안한` |
| frontmatter `date: <원래>` | `date: <발행일>` |

세션 사례: 04-24 Builder BU와 05-01 Progressive Disclosure를 5/6 발행하며 적용 (커밋된 본문은 `_Gobi_/GSA/2026-04-24 …`, `_Gobi_/GSA/2026-05-01 …` 참조).

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
- 발행은 별도 단계: post_kind에 따라 `gobi global create-post` (bu broadcast) / `gobi space --space-slug <slug> create-post` (bu space-targeted, thread) / `gobi space --space-slug <slug> create-reply <postId>` (reply). 모두 `--auto-attachments` 권장. 발행 전 `gobi vault status`로 `isPublished` 확인 필수.

### Rate limit
- 실제 생성은 하루 2–4개 수준이 적정
- 2시간 쿨다운 (마지막 드래프트 후)
- 야간 시간대는 내부 SKIP 판단으로 억제

## Manual invocation

```bash
python3 _Settings_/Skills/gobi-social-agent/scripts/collect_signals.py --hours 24 --days 3
# Agent가 Step 2~4 판단 & 작성
python3 _Settings_/Skills/gobi-social-agent/scripts/update_state.py --kind bu --source ... --draft ...
```

## Heartbeat invocation (OpenClaw, v0.5.0+)

OpenClaw가 매 heartbeat tick마다 이 스킬을 자동 호출. 설정:
- `_Claw_/home/openclaw.json#skills.load.extraDirs`에 `_Settings_/Skills`가 등록되어 있어야 함
- `_Claw_/HEARTBEAT.md`에 GSA 태스크 블록 존재
- 2시간 cooldown은 본 스킬이 `state/_state.json`으로 자체 관리 — heartbeat가 매 분 트리거해도 SKIP 처리됨
- 야간 cutoff (23:00–07:00 PT)은 HEARTBEAT.md 측에서 guard, 본 스킬도 내부 SKIP 적용

## Approval watcher (review-session pattern)

리뷰 세션 시작 시 별도 셸/Claude Monitor에서 실행. 사용자가 frontmatter `approve_for_publish: false → true`로 flip하는 순간 알림 라인을 stdout으로 출력 (notification-only, 자동 발행 안 함).

```bash
./_Settings_/Skills/gobi-social-agent/scripts/watch_approvals.sh
```

출력 라인 종류:
- `BACKLOG <HH:MM:SS> — <basename>` — watcher 시작 시점에 이미 "approved-but-not-published" 상태인 드래프트 (한 번만 보고)
- `FLIPPED <HH:MM:SS> — <basename>` — watcher 가동 후 새로 flip된 드래프트
- `WATCH-START` / `WATCH-EXIT` — heartbeat / 종료

조건: `approve_for_publish: true` AND `published_post_id` 부재. 발행 후 `published_post_id` 채우면 자동 dedup.

요구사항: `bash 4+`, `fswatch` (`brew install fswatch`).

Claude Code 세션에서 쓰는 패턴: `Monitor` 툴로 위 스크립트를 persistent 모드로 띄워두면 사용자가 base에서 일괄 검토하다가 flag flip 할 때마다 알림이 와서 Claude가 Step 4 발행 명령으로 이어받음. 세션 종료 시 watcher도 같이 사라짐 — 영구 백그라운드용 아님.

## Related

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
│   ├── update_state.py
│   └── watch_approvals.sh   # FSEvents-based approval watcher (review sessions)
└── state/
    ├── _state.json          # runtime-generated
    └── _log.md              # append-only execution log

_Gobi_/GSA/                  # drafts live here
_Settings_/Bases/GSA Drafts.base   # review view

# Back-symlink in _Settings_/Skills/gobi-social-agent/ → _Settings_/Skills/gobi-social-agent/
# (for shared-skill discovery from Hermes / agents pointing at _Settings_/Skills/)
```
