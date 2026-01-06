---
title: Newsletter Briefing (NBR)
abbreviation: NBR
category: batch
participant: 김진영
version: 1.0
created: 2025-12-11
tags:
  - prompt
  - briefing
  - newsletter
  - gmail
---

## Purpose

매일 아침 Gmail로 수신된 뉴스레터를 수집하고 카테고리별로 정리한 브리핑을 생성합니다.

## Input

- Gmail 뉴스레터 (MCP tools: `search_gmail_messages`, `get_gmail_messages_content_batch`)

## Output

- `AI/Briefings/YYYY-MM-DD Newsletter Briefing - [Agent].md` - 브리핑 문서
- Voice Mode 브리핑 (핵심 뉴스 음성 요약)

## Workflow

### 1단계: Gmail 뉴스레터 검색
`search_gmail_messages` 도구로 최근 뉴스레터 검색:

```
query: newer_than:2d (newsletter OR 뉴스레터 OR digest OR daily OR weekly)
page_size: 50
```

### 2단계: 광고/프로모션 필터링
다음 발신자 제외:
- 광고성 이메일
- 프로모션/마케팅 이메일
- 정기 알림 (월간지 등)

### 3단계: 메시지 내용 수집
`get_gmail_messages_content_batch`로 뉴스레터 본문 수집:
- 첫 번째 배치: metadata로 제목/발신자 확인
- 두 번째 배치: 핵심 뉴스레터 full content 수집

### 4단계: 카테고리 분류
수집된 뉴스레터를 다음 카테고리로 분류:

| 카테고리 | 키워드/발신자 예시 |
|----------|-------------------|
| 🔴 Top Stories | 중요도 높은 뉴스 (AI 신제품, 대형 인수 등) |
| 📱 AI & Technology | OpenAI, AI Daily Brief, Data Science Weekly |
| 💼 Business & Startup | 스타트업 뉴스, 비즈니스 인사이트 |
| 🇰🇷 Korean News | 국내 뉴스레터 |
| 🎭 Culture & Lifestyle | 문화, 라이프스타일 콘텐츠 |

### 5단계: 브리핑 문서 생성
다음 구조로 브리핑 문서 작성:

```markdown
---
title: YYYY-MM-DD Newsletter Briefing
created: YYYY-MM-DD HH:MM:SS
source: Gmail newsletters
tags:
  - briefing
  - newsletter
  - daily
---

## 오늘의 핵심 뉴스

### 🔴 Top Stories

**1. [제목]**
→ 원문: [메일 제목](Gmail 링크) (발신자)

[요약 내용]

> "원문 인용" - 출처

### 📱 AI & Technology
...

## 원문 링크

| 발신자 | 제목 | 링크 |
|--------|------|------|
| ... | ... | [Gmail](링크) |
```

**중요**: 본문 중간에 Gmail 원문 링크를 `→ 원문:` 형식으로 삽입하여 바로 원문 확인 가능하게 함

### 6단계: Voice Mode 브리핑
`mcp__voice-mode__converse` 도구로 핵심 뉴스 3개 음성 브리핑:
- Top Stories 위주로 간결하게 요약
- 30초~1분 분량
- 자세한 내용은 문서 참조 안내

## Example Output

```markdown
## 오늘의 핵심 뉴스

### 🔴 Top Stories

**1. OpenAI GPT-5.2 API 출시 - 코딩·비전·도구 사용 SOTA 달성**
→ 원문: [GPT-5.2 is Here](https://mail.google.com/mail/...) (AI Daily Brief)

OpenAI가 GPT-5.2 API를 출시했다. SWE-bench에서 72.1%로 코딩 벤치마크 SOTA를 달성했으며, 비전과 도구 사용 능력도 크게 향상되었다.

> "GPT-5.2 combines cutting-edge coding capabilities with enhanced vision and tool-use skills." - OpenAI
```

## Notes

- **검색 전략**: `newer_than:2d`로 최근 2일 뉴스레터 수집 (주말 고려)
- **중복 방지**: 이미 브리핑된 내용은 다음 날 브리핑에서 제외
- **Gmail 링크**: 메시지 ID 기반 직접 링크
- **Voice 브리핑**: Top Stories 3개 위주로 간결하게 요약
