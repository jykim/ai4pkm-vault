---
title: Ambient Canvas Brainstorming (ACB)
abbreviation: ACB
category: visualization
created: 2025-12-31
updated: 2026-02-24
---

앰비언트모드 음성 녹취를 실시간으로 분석하여 Obsidian Canvas에 브레인스토밍 맵을 자동 생성/업데이트하는 프롬프트.

## Overview

앰비언트모드로 녹취된 사용자의 생각을 실시간으로 시각화. 주제를 추출하고, 카테고리별로 분류하여 캔버스에 표시. 파일 변경 시마다 자동 업데이트.

## Input
- AmbientMode 녹취 파일: `_Settings_/History/Ambient/{{datetime}}.md`
- 기존 캔버스 (있는 경우): `AI/Canvas/{{datetime}} {{main_topic}}.canvas`

## Output
- 브레인스토밍 캔버스: `AI/Canvas/{{datetime}} {{main_topic}}.canvas`

## Process

### Phase 0: 소스 파일 수신 및 모니터링

```
1. RECEIVE SOURCE FILE
   - Orchestrator가 새 AmbientMode 파일 생성 시 트리거
   - 소스 파일 경로: _Settings_/History/AmbientMode/{{datetime}}.md
   - 파일 내용을 읽고 Phase 1-3 실행 (초기 캔버스 생성)
   - canvas_path = Phase 1-3에서 생성한 캔버스 파일 경로 기억

2. MONITOR LOOP
   last_content = 현재 파일 내용
   while true:
     - 10초 대기 (sleep 10)
     - 파일 다시 읽기
     - IF 파일에 "RECORDING COMPLETED" 라인 존재:
       → Phase 1-3 최종 실행 (canvas_path 재사용) 후 EXIT
     - IF 내용이 last_content와 다름:
       → last_content 갱신
       → Phase 1-3 실행 (canvas_path 재사용하여 캔버스 업데이트)
       → 타이머 리셋
     - IF 60초간 변경 없음:
       → EXIT (타임아웃)

3. EXIT
   - 종료 전 최종 캔버스 상태 저장 확인
   - 로그: "ACB 세션 종료 (사유: timeout|recording_completed)"
```

### Phase 1: 콘텐츠 분석

```
1. READ SOURCE FILE
   - 전체 내용 읽기
   - 타임스탬프별 발화 추출

2. EXTRACT TOPICS
   FOR EACH timestamped utterance:
     - 핵심 주제/요청 식별
     - 관련 카테고리 분류
     - 우선순위/중요도 판단

3. CATEGORIZE TOPICS
   자동 카테고리 예시:
   - 🛠️ 도구/개발: 기술, 코딩, 도구 관련
   - 📋 프로젝트/일: 업무, 할일, 프로젝트 관련
   - 💑 관계: 가족, 인간관계, 감정 관련
   - 💡 아이디어: 새로운 생각, 브레인스토밍
   - 📚 학습: 배움, 리서치 관련

4. DERIVE CANVAS NAME
   - 추출된 토픽 중 가장 핵심적인 주제를 1-3단어로 요약
   - 캔버스 파일명에 사용: AI/Canvas/{{datetime}} {{main_topic}}.canvas
   - 예시: "고비 브랜딩 논의", "스타트업 결심", "커뮤니티 비전"
   - 한국어 기본, 핵심 키워드 중심으로 간결하게

5. FIND EXISTING CANVAS
   - IF canvas_path가 이미 설정됨 (MONITOR LOOP 재실행):
     → canvas_path의 캔버스에 MERGE (Phase 3 step 4)
   - ELSE (최초 실행):
     → AI/Canvas/ 에서 이 소스 파일의 정확한 경로를 참조하는 캔버스만 검색
     → 찾으면: MERGE + canvas_path 설정
     → 못 찾으면: 새 캔버스 생성 + canvas_path 설정
   - ⚠️ 다른 소스 파일의 캔버스에 merge 절대 금지 (같은 날짜여도)
```

### Phase 2: 캔버스 레이아웃 생성

```
1. LAYOUT PRINCIPLES
   - 소스 파일을 정중앙에 배치
   - 카테고리는 큰 컨테이너 박스로 (530-640px 너비)
   - 박스 높이 850px 이하 (한눈에 보이도록)
   - 카테고리 내 2열 레이아웃 기본 적용
   - 관련 노드 간 가로 연결로 높이 줄이기

2. EXACT NODE POSITIONING (2025-12-31 기준)

   소스 파일 (정중앙):
   - x: -150, y: -150
   - width: 300, height: 300

   💑 관계 카테고리 (좌측):
   - 컨테이너: x: -750, y: -400, 530x850
   - 좌측 열 노드: x: -710 (컨테이너+40)
   - 우측 열 노드: x: -460 (컨테이너+290)

   🛠️ 도구/개발 카테고리 (우상단):
   - 컨테이너: x: 200, y: -500, 640x650
   - 좌측 열 노드: x: 240 (컨테이너+40)
   - 우측 열 노드: x: 520 (컨테이너+320)

   📋 프로젝트/일 카테고리 (우하단):
   - 컨테이너: x: 200, y: 200, 640x540
   - 좌측 열 노드: x: 240
   - 우측 열 노드: x: 520
   - 전체 너비 노드: x: 240, width: 540

3. CATEGORY BOX STRUCTURE
   - 카테고리 내 토픽들을 박스 안에 2열 배치
   - 좌측 열: 컨테이너 x + 40
   - 우측 열: 컨테이너 x + 290~320
   - 전체 너비 노드: 하단에 540px 너비로 배치
   - 열 간격: ~250-280px

4. NODE DIMENSIONS
   - 표준 토픽: 220-260px 너비, 140-180px 높이
   - 전체 너비 노드: 480-540px 너비
   - 파일 참조: 230-260px 너비, 100-180px 높이

5. CROSS-CONNECTIONS
   - 같은 행의 노드끼리 가로 연결 (fromSide: right → toSide: left)
   - 통찰 → 액션 연결
   - 관련 토픽 간 가로 연결로 박스 높이 압축
```

### Phase 3: 캔버스 업데이트

```
1. GENERATE CANVAS JSON
   {
     "nodes": [...],
     "edges": [...],
     "metadata": {
       "version": "1.0-1.0"
     }
   }

2. NODE TYPES
   - source-file: file 타입, 원본 앰비언트모드 노트 참조
   - cat-*: text 타입, 카테고리 컨테이너 박스
   - topic-*: text 타입, 개별 주제 노드
   - insight-*: text 타입, 통찰/결론 노드
   - action-*: text 타입, 액션 아이템 노드

3. COLOR SCHEME
   | Color | ID | 용도 |
   |-------|-----|------|
   | Red | 1 | 핵심/우선순위 높음 |
   | Orange | 2 | 관계/감정 |
   | Yellow | 3 | 진행중/프로젝트 |
   | Purple | 4 | 참조/연결 문서 |
   | Green | 5 | 통찰/인사이트 |
   | Cyan | 6 | PKM/메타 |

4. CANVAS MERGE (기존 캔버스가 있는 경우)
   1) 기존 캔버스 JSON 로드
   2) 기존 노드 ID/내용 매핑 생성
   3) Ambient 파일에서 새 토픽 추출
   4) 새 토픽만 추가 (기존과 유사한 토픽은 SKIP)
   5) 카테고리 컨테이너 크기 확장 (필요 시)
   6) 소스 파일 노드에 새 Ambient 파일 참조 추가
   7) 겹침 방지 체크 후 저장

5. WRITE CANVAS FILE
   - AI/Canvas/{{datetime}} {{main_topic}}.canvas에 저장
   - Phase 1 step 5에서 매칭된 기존 캔버스가 있으면 MERGE (4번)
   - 매칭 안 되면 새 캔버스 생성 (같은 날짜의 다른 캔버스와 merge 금지)
   - 반드시 Atomic Write 패턴 사용 (tmp → rename)
   - [[obsidian-brainstorming]] 스킬의 "Safe Canvas Writing" 참조

6. METADATA (필수)
   - 모든 캔버스에 metadata.version = "1.0-1.0" 포함 필수
   - Obsidian이 캔버스를 인식하려면 이 필드가 반드시 있어야 함

7. VALIDATION (저장 전 필수)
   - JSON parse 성공 확인
   - 모든 node에 id, type, x, y, width, height 존재 확인
   - 모든 edge의 fromNode/toNode가 실제 node id를 참조하는지 확인
   - metadata.version 존재 확인
   - 중복 node id 없는지 확인
```

## Layout Patterns

### 기본 레이아웃 (실제 좌표 기준)

```
     💑 관계 (-750)              🛠️ 도구/개발 (200)
     530x850                     640x650
┌───────────────────┐      ┌───────────────────────┐
│ -710    │  -460   │      │  240    │   520       │
│ topic-5 │ yester  │      │ topic-1 │ prompt-file │
│    ↓    │    ↓    │      │    ↓    │      ↓      │
│ topic-7 │ action  │  ◉   │ topic-2 │ skill-file  │
│    ↓    │         │ src  │    ↓    │             │
│ topic-8─┼─→───────│(-150)│ topic-3 │             │
│    ↓    │         │      └─────────┴─────────────┘
│ insight │         │
└─────────┴─────────┘      📋 프로젝트 (200, y:200)
                           640x540
                     ┌───────────────────────┐
                     │  240      │   520     │
                     │ topic-9 ──┼─→ topic-10│
                     │     ↓     │      ↓    │
                     │ topic-11 (540px 전체너비) │
                     └───────────────────────┘
```

### 2열 카테고리 내부 구조

```
┌─────────────────────────────────────────────┐
│  💑 관계 (x:-750, 530x850)                   │
│                                             │
│  ┌─────────────┐  ┌─────────────┐          │
│  │ 좌측 (x:-710)│  │우측 (x:-460)│          │
│  │ 230px 너비   │  │ 220px 너비  │          │
│  │             │  │             │          │
│  │ topic-5     │  │ yesterday-1 │          │
│  │ 160px 높이  │  │ 160px 높이  │          │
│  │      ↓      │  │      ↓      │          │
│  │ topic-7     │→→│ action-1    │          │
│  │ 140px 높이  │  │ 220px 높이  │          │
│  │      ↓      │  │             │          │
│  │ topic-8     │  │             │          │
│  │ 100px (file)│  │             │          │
│  │      ↓      │  │             │          │
│  │ insight-1 ──│→→│             │          │
│  └─────────────┘  └─────────────┘          │
│                                             │
└─────────────────────────────────────────────┘
```

## Node Templates

### 토픽 노드 (좌측 열)
```json
{
  "id": "topic-5",
  "type": "text",
  "text": "### 가족 협력의 어려움\n\n\"내가 뭘 하려면 아내가 도와줘야 되는데 쉽지가 않네\"\n\n→ 공동 목표 설정 필요\n→ 작은 것보다 큰 그림에서 서포트",
  "x": -710, "y": -330,
  "width": 230, "height": 160,
  "color": "2"
}
```

### 토픽 노드 (우측 열)
```json
{
  "id": "topic-10",
  "type": "text",
  "text": "### 네이버 업데이트\n\n\"메일을 보내놨으니까 답변을 기다리면서 다음 주 미팅도 스케줄해야 돼\"\n\n✅ 메일 발송 완료\n→ 답변 대기 중\n→ 다음 주 미팅 스케줄",
  "x": 520, "y": 270,
  "width": 260, "height": 180,
  "color": "3"
}
```

### 전체 너비 노드 (하단)
```json
{
  "id": "topic-11",
  "type": "text",
  "text": "### 💡 멀티플렉싱 전략\n\n\"한 가지 일을 해서 여러 프로젝트를 도움받을 수 있게\"\n\n**애플리케이션:**\n• 커뮤니티 빌딩\n• 제품 개발\n• 자체 쇼케이스",
  "x": 240, "y": 470,
  "width": 540, "height": 230,
  "color": "5"
}
```

### 통찰 노드
```json
{
  "id": "insight-1",
  "type": "text",
  "text": "### 💡 핵심 통찰\n\n커리어 압박 = 관심/사랑 부족의 대리 표현\n\n→ **정서적 니즈 충족**이 근본적 해결책",
  "x": -710, "y": 130,
  "width": 230, "height": 140,
  "color": "5"
}
```

### 파일 참조 노드
```json
{
  "id": "topic-8",
  "type": "file",
  "file": "AI/Canvas/2025-12-28 부부 우선순위 갈등 분석.canvas",
  "x": -710, "y": 10,
  "width": 230, "height": 100,
  "color": "4"
}
```

## Best Practices

### 컴팩트 레이아웃 유지
- 카테고리 박스 높이 900px 이하 권장
- 한눈에 전체가 보여야 함
- 너무 길어지면 2열 적용

### 중복 제거
- 비슷한 내용은 통합
- 불필요한 노드 삭제
- 핵심만 유지

### 가로 연결 적극 활용
- 세로로만 나열하지 말고
- 관련 노드 간 가로 연결 추가
- 세로 길이 줄이는 효과

### 실시간 피드백 반영
- 사용자가 레이아웃 피드백 주면 반영
- "박스가 너무 길어" → 2열로 변환
- "연결 추가해줘" → cross-connection 추가

### 사용자 수동 편집 학습
- 사용자가 캔버스를 직접 수정하면 해당 패턴 학습
- "내가 업데이트한 내용 참고해서 다음에 이렇게 좀 해줄래?" → 새 치수/위치 반영
- 학습된 패턴은 이 프롬프트의 Phase 2와 Node Templates에 업데이트
- 다음 캔버스 생성 시 학습된 레이아웃 적용

## Integration

### 관련 스킬
- [[obsidian-canvas]] - 캔버스 생성 기본 스킬
- [[daily-driver-agent]] - 앰비언트모드 녹취 관리

### 실행 예시
```bash
# Orchestrator가 새 AmbientMode 파일 감지 시 ACB 자동 실행
# ACB는 내부 루프로 파일 변경을 모니터링하며 캔버스 업데이트
# 종료 조건: 60초 비활성 또는 "RECORDING COMPLETED" 감지
```

## Caveats

### One Recording = One Canvas
- AmbientMode 녹음 파일 1개 = 캔버스 1개 (1:1 매핑, 엄격)
- 캔버스 파일명은 콘텐츠 기반 동적 생성: `AI/Canvas/{{datetime}} {{main_topic}}.canvas`
- 같은 녹음 파일의 업데이트만 기존 캔버스에 merge (ACB가 내부 루프로 모니터링)
- 다른 녹음 파일은 같은 날짜여도 별도 캔버스 생성 (주제별 분리)
- 다른 프롬프트(ICB 등)가 동일 소스로 별도 캔버스를 생성하지 않도록 ACB가 AmbientMode의 유일한 캔버스 생성 주체

### Skip Conditions
- 의미없는 발화만 있는 경우 (감탄사, 외국어 테스트 등)
- 기존 캔버스와 동일한 내용

### 언어 처리
- 한국어 기본, 영어 원문 유지
- 다국어 감탄사는 무시 (Ciao, Merhaba 등)

### 파일 크기
- 대용량 녹취는 최신 발화 우선 처리
- 오래된 발화는 요약/통합

## 2025-12-31 Session Lessons Learned

### 노드 가시성 핵심
1. **H3 헤더 (###) 필수** - H1/H2는 너무 커서 실제 내용 안 보임
2. **충분한 노드 높이** - 콘텐츠 양에 맞춰 최소 120-180px
3. **카테고리 박스 높이 제한** - 700px 이하로 한눈에 보이게

### 레이아웃 조정 피드백 루프
- 사용자 피드백 즉시 반영 (예: "내용이 안 보여")
- 박스 크기 = 콘텐츠 양 반영
- 겹침 발생 시 즉각 좌표 재계산

### 리스닝 모드 개선 방향
- **배치 처리**: 매 발화마다 반응 X → 발화 종료 후 한꺼번에
- **듀얼 모니터링**: 소스 파일 + 캔버스 동시 감시
- 사용자 캔버스 직접 편집 → 학습 후 반영

### 실제 적용 좌표 (검증됨)
```
source-file: x:-150, y:-100, 300x200
cat-relationship: x:-750, y:-350, 530x650
cat-tools: x:200, y:-450, 640x700
cat-projects: x:200, y:300, 640x500
cat-entertainment: x:-750, y:400, 530x400
```

## Phase 4: 대화록 정리 (Post-Processing)

세션 종료 후 원본 트랜스크립트를 카테고리별로 정리하여 가독성 향상.

### 정리 프로세스
```
1. 원본 발화를 시간순으로 읽기
2. 카테고리별 H2 섹션 생성:
   - ## 세션 시작
   - ## 💑 관계 - [주제]
   - ## 📋 프로젝트/일 - [주제]
   - ## 💡 멀티플렉싱 전략
   - ## 🛠️ 캔버스/도구 개발 - [세부]
   - ## 🎧 노드 가시성 피드백
   - ## 🎬 엔터테인먼트 카테고리
   - ## 🔄 듀얼 모니터링 & 리스닝 모드
   - ## 정리 요청
3. 각 발화를 해당 카테고리 아래로 이동
4. 타임스탬프와 원본 텍스트 유지
5. 의미없는 발화 (감탄사, 외국어 테스트) 제거
```

### 카테고리 헤더 이모지 규칙

| 이모지 | 카테고리 |
|--------|----------|
| 💑 | 관계/감정 |
| 📋 | 프로젝트/업무 |
| 💡 | 인사이트/전략 |
| 🛠️ | 도구/개발 |
| 🎧 | 피드백/조정 |
| 🎬 | 엔터테인먼트 |
| 🔄 | 프로세스 개선 |

### 정리된 파일 예시
```markdown
# Ambient Mode Recording - YYYY-MM-DD HH:MM:SS PM

## 세션 시작
User|HH:MM:SS PM> 첫 발화...

## 💑 관계 - 아내 서포트 문제
User|HH:MM:SS PM> 관계 관련 발화...
User|HH:MM:SS PM> 추가 발화...

## 📋 프로젝트/일 - 1월 콜트 & 네이버
User|HH:MM:SS PM> 업무 관련 발화...
```
