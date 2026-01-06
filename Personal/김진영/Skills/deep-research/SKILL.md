---
name: deep-research
participant: 김진영
description: OpenAI Deep Research API를 활용한 학술 리서치. 논문, 아티클 등 깊이 있는 조사가 필요할 때 사용.
allowed-tools:
  - Bash
  - Write
  - Read
license: MIT
version: 1.0.0
---

# Deep Research Skill

OpenAI의 o3-deep-research 모델을 활용하여 웹 검색과 코드 분석을 결합한 깊이 있는 리서치를 수행합니다.

## 사용 시점

- 학술 논문 동향 파악
- 기술 개념 심층 분석
- 최신 연구 트렌드 조사
- 복잡한 주제의 종합적 리서치

**트리거**: "deep research", "심층 조사", "논문 리서치", "DR"

## 사용법

### CLI 직접 실행

```bash
# 기본 (o3 모델)
python _Settings_/Skills/deep-research/deep_research.py "연구 질문"

# 빠른 모델 사용
python _Settings_/Skills/deep-research/deep_research.py "질문" --model o4-mini

# 파일로 저장
python _Settings_/Skills/deep-research/deep_research.py "질문" -o AI/Analysis/결과.md

# JSON 출력
python _Settings_/Skills/deep-research/deep_research.py "질문" --json
```

### Claude Code에서

```
DR "LLM-as-Judge 평가 방법론의 최신 연구 동향"
```

## 모델 옵션

| 모델 | 설명 | 용도 |
|------|------|------|
| `o3` | o3-deep-research-2025-06-26 | 고품질, 깊이 있는 분석 (기본값) |
| `o4-mini` | o4-mini-deep-research-2025-06-26 | 빠른 응답, 간단한 조사 |

## 출력 형식

### Markdown (기본)

```markdown
---
title: Deep Research - [질문]
created: 2025-12-10T23:00:00
model: o3-deep-research-2025-06-26
tags:
  - deep-research
  - ai-generated
---

## 연구 질문
> [입력한 질문]

## 연구 결과
[리서치 리포트]

## 출처
1. [제목](URL)
2. ...

## 추론 과정
- [모델이 수행한 추론 요약]
```

## 환경 요구사항

- `OPENAI_API_KEY` 환경변수 설정
- Python 3.10+
- `openai` 패키지

## 참고 자료

- [OpenAI Deep Research Guide](https://platform.openai.com/docs/guides/deep-research)
- [OpenAI Cookbook](https://cookbook.openai.com/examples/deep_research_api/introduction_to_deep_research_api)
