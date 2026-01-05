---
title: "Topic Index Update"
abbreviation: "TIU"
category: "workflow"
created: "2025-12-06"
updated: "2026-01-04"
---
임의의 문서에 대해 Topic 인덱스 업데이트, 신규 Topic 생성, 품질 검증을 수행한다.

## Input
- 입력 문서: 임의의 마크다운 파일들
	- 단일 파일 또는 여러 파일
	- 날짜 범위: `start_date` ~ `end_date` (배치 처리 시)
- 기존 Topics: `Topics/` 디렉토리

## Output
- 업데이트된 Topic 파일
- 신규 Topic 파일
- 처리 로그:

| 항목 | 내용 |
|------|------|
| Topics Updated | count (list) |
| Topics Created | count (list) |
| Topics Skipped | count (reason) |
| Topics Verified | count (matched/total) |
| Frontmatter Fixed | count |

## Process
```
1. SOURCE ANALYSIS
   - 입력 문서에서 [[Topics/...]] 링크 추출
   - 기존 Topic에 매핑되지 않는 주제 식별
   - 입력 파일들 먼저 일괄 읽기 (병렬)

2. TOPIC UPDATES
   A. 기존 Topic 업데이트:
      - 중복 확인: 동일 소스 엔트리 존재 시 스킵
      - 새 엔트리 추가 (one-line-per-source)
      - Experiences: 개인 경험 (Journal, Lifelog)
      - Learnings: 외부 학습 (Articles, Clippings)
      - Frontmatter 포맷 검증 및 수정

   B. 신규 Topic 생성:
      - Wikipedia 기준: 보편적 개념인가?
      - 3+ 엔트리 축적 가능성
      - 기존 Topic과 중복 없음
      - Topic Template으로 생성 + 초기 엔트리

3. QUALITY VALIDATION
   - wiki 링크 유효성 검증
   - 중복 엔트리 제거
   - 모든 수정된 Topic 파일 frontmatter 검증 (수정 시 자동 표준화)

4. VERIFICATION
   - 입력 문서의 Topic 언급과 실제 Topic 파일 엔트리 교차 검증
   - 누락된 Topic 있으면 경고 및 추가
   - 검증 로그: | Source | Topic Mentioned | Entry Added? |
```

## Entry Format
```markdown
- [[source#Section]] - 한 줄 요약
```
- 반드시 섹션까지 링크: `[[source#Section]]`
- 새 주제군 (3+ 엔트리) → 새 subsection `### 주제명 (YYYY년 M월)`

## Frontmatter 표준
```yaml
---
aliases: Topic Name
tags:
  - tag1
  - tag2
related:
  - "[[Related Topic]]"
---

## Summary
```

**금지**: `subtopics:`, `links:`, 빈 값 필드

## Rules
- PKM 내 콘텐츠만 사용 (외부 지식 금지)
- 원본 소스에 링크 (Topic index 아닌)
- Topic 파일들 병렬 읽기/업데이트
- 모든 언급된 Topic 처리 (빈도 무관) - 저빈도 Topic도 누락 없이 업데이트
