---
title: Gobi Social Agent (GSA)
abbreviation: GSA
category: agent
created: 2026-04-23
tags:
  - prompt
  - social
  - gobi
  - ai4pkm
---

> 이 프롬프트는 [[_Settings_/Skills/gobi-social-agent/SKILL|gobi-social-agent 스킬]]을 호출하는 워크플로우 커맨드. 실제 로직·스크립트는 스킬에 있음.

## Purpose

Gobi Space와 Gobi Desktop에서 동작하는 소셜 에이전트. 30분마다 실행되면서 **내 최근 볼트 활동**과 **Gobi 커뮤니티 시그널**(다른 사용자의 Brain Update/Thread)을 종합하여 소셜 포스팅 드래프트(Brain Update 또는 Thread)를 자동 생성한다.

기존 PBU/CTP는 "사용자가 소스를 지정해서 한 번 생성"하는 반면, GSA는 "스스로 시그널을 찾아 조건부로 드래프트 생성"하는 상시 반응형 에이전트다.

## Trigger
- Cron: 30분마다 (`*/30 * * * *`)
- 수동 실행: "GSA 돌려줘", "소셜 에이전트 한 번 돌려"

## Input
- **내 시그널 소스** (지난 24시간 수정): `Journal/`, `AI/Roundup/`, `AI/Summary/`, `AI/Analysis/`, `AI/Events/`, `AI/Sharable/`, `_Outbox_/BrainUpdates/`
- **커뮤니티 시그널 소스** (지난 3일): `_Gobi_/BrainUpdates/`, `_Gobi_/Threads/`
- **State**: `_Settings_/Skills/gobi-social-agent/scripts/_state.json` — 마지막 실행, 이미 사용한 소스 히스토리

## Output
- **BU 드래프트**: `_Outbox_/BrainUpdates/YYYY-MM-DD [제목] - Agent.md` (PBU와 동일 경로/형식)
- **Thread 드래프트**: `AI/Sharable/YYYY-MM-DD [제목] Threads - Agent.md` (CTP와 동일)
- **Skip 로그**: 생성하지 않을 경우 `_state.json`에 `kind: skip` + 이유 기록
- Frontmatter의 `approve_for_publish: false` 유지 (발행은 항상 사용자 승인 후)

## Main Process

### Step 1: 시그널 수집 (Python)

```bash
python3 _Settings_/Skills/gobi-social-agent/scripts/collect_signals.py --hours 24 --days 3
```

출력 JSON:
- `my_signals`: 내 최근 파일 (path, title, modified, tags, preview, already_used)
- `community_signals`: `_Gobi_` 폴더의 BU/Thread (타 사용자 포스트)

### Step 2: 생성 여부 판단 (Agent)

**SKIP 조건** (아무것도 생성하지 않고 종료):
- `my_signals` 중 `already_used: false`인 항목이 없음
- 마지막 드래프트 생성이 2시간 이내 (너무 자주 찍어내지 않기)
- 의미 있는 인사이트가 없는 파일뿐 (Journal만 있고 Roundup/Analysis 없음)

SKIP 시:
```bash
python3 _Settings_/Skills/gobi-social-agent/scripts/update_state.py --kind skip --draft "" --note "이유"
```

### Step 3: 소스 선정 & 형식 결정

**내 시그널 중 가장 강한 1개**를 골라 소스로 사용:
- 우선순위: `AI/Analysis/` > `AI/Summary/` > `AI/Roundup/` > `AI/Events/` > `Journal/`
- `already_used: true`인 소스는 제외
- 커뮤니티 시그널은 **반응 타겟과 참고용**: 어떤 토픽이 지금 대화되고 있는지, 어떤 질문에 답할 수 있는지

**BU vs Thread vs Reply 결정**:
- **Brain Update**: 에세이성 인사이트, 400-800단어 분량으로 풀 수 있는 주제
- **새 Thread**: 짧은 관찰, 인용구, 대화 스니펫 (1k자 이하)
- **Reply (댓글)**: 커뮤니티 스레드에 직접 답글 — 가장 반응형 액션
- 커뮤니티 스레드 중 "내가 답할 수 있는" 것이 있으면 Reply 우선

### Step 4: 드래프트 생성

**BU인 경우** → PBU 프롬프트 로직 따름:
- `_Outbox_/BrainUpdates/YYYY-MM-DD [제목] - Agent.md` 생성
- 400-800단어 에세이 스타일, H2 없이 본문 시작
- 원문 인용은 블록쿼트, 마무리에 `→ **관련 분석**: [[...]]` 링크
- Frontmatter: `approve_for_publish: false`, `source_file`, `generated_by: GSA`

**Thread/Reply인 경우** → CTP 프롬프트 로직 따름:
- `AI/Sharable/YYYY-MM-DD [제목] Threads - Agent.md` 생성
- Social Media Template 구조 (Overview → Contents → Sources)
- 각 thread 1k자 이하, 자체 완결형
- Reply인 경우 frontmatter에 `reply_to_thread: <thread-id>` 기록

### Step 5: 커뮤니티 컨텍스트 주석

드래프트 frontmatter에 참고한 커뮤니티 시그널 기록:
```yaml
community_context:
  - "_Gobi_/BrainUpdates/YYYY_MM_DD_... - 비슷한 토픽 최근 등장"
  - "_Gobi_/Threads/... - 관련 논의 진행 중"
```

이유: 사용자가 승인 전에 "이게 커뮤니티에 이미 돌고 있는 얘기인지" 판단 가능.

### Step 6: State 업데이트

```bash
python3 _Settings_/Skills/gobi-social-agent/scripts/update_state.py \
  --kind bu \
  --source "AI/Roundup/YYYY-MM-DD - Agent.md" \
  --draft "_Outbox_/BrainUpdates/YYYY-MM-DD 제목 - Agent.md"
```

### Step 7: Obsidian에서 열기

```bash
open "obsidian://open?vault=<VAULT_NAME>&file=_Outbox_/BrainUpdates/..."
```

## Caveats

### 생성 빈도 조절
- 30분 cron이지만 실제 생성은 하루 2-4개 수준이 적정
- SKIP 조건을 엄격히 적용 — "뭔가 만들기 위해 억지로 만들지 말 것"
- 같은 소스로 두 번 생성 금지 (`used_sources` 체크)

### 커뮤니티 시그널 사용 원칙
- **복제 금지**: 타 사용자 BU 내용을 그대로 가져오지 않음
- **반응형 우선**: 커뮤니티 질문이나 논의에 답하는 Reply가 일방 포스팅보다 가치 높음
- **크레딧**: 영감을 받은 경우 `community_context`에 기록, 본문에서도 원 작성자 언급 가능

### 승인 워크플로우 (PBU와 동일)
- 생성 시 항상 `approve_for_publish: false`
- 사용자가 Obsidian에서 확인 후 `true`로 변경
- Gobi 발행: `gobi brain post-update --auto-attachments --title "..." --content "..."`
- Thread/Reply는 별도 수동 포스팅 (또는 `--social` 플래그)

### Cron 등록 (참고)
`orchestrator.yaml` 예시:
```yaml
- type: agent
  name: Gobi Social Agent (GSA)
  cron: "*/30 * * * *"
  working_hours: "09:00-22:00"  # 밤에는 생성 안 함
  agent_params:
    hours: 24
    days: 3
```

### 레퍼런스
- `_Settings_/Skills/gobi-social-agent/scripts/collect_signals.py` — 시그널 수집
- `_Settings_/Skills/gobi-social-agent/scripts/update_state.py` — state 기록
- `_Settings_/Prompts/Post Brain Update (PBU).md` — BU 생성 로직
- `_Settings_/Prompts/Create Thread Postings (CTP).md` — Thread 생성 로직
- `_Settings_/Prompts/Social Discovery Bot (SDB).md` — 외부(X/Threads) 발견용 (GSA는 내부 커뮤니티 전용)
