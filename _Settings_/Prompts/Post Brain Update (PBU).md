---
title: "Post Brain Update (PBU)"
abbreviation: PBU
category: publish
created: "2026-03-08"
---
Gobi 커뮤니티에 공유할 Brain Update 드래프트를 소스 파일 기반으로 작성한다.

## Input
- **Source file(s)**: 볼트 내 아무 콘텐츠 (Clippings, Summary, Roundup, Lifelog, Events, Analysis 등)
- **Optional**: 포커스할 토픽/앵글 (소스에 여러 주제가 있을 때)
- **Optional**: 대상 독자 컨텍스트
- **Optional**: --social (소셜 미디어 동시 발행)

## Output
- 드래프트 파일: `_Outbox_/BrainUpdates/YYYY-MM-DD [제목] - Claude Code.md`
- Frontmatter에 `approve_for_publish: false` 포함
- 작성 후 Obsidian에서 파일 열기

## Main Process
```
1. SOURCE ANALYSIS
   - 소스 파일 전체 읽기
   - 핵심 인사이트, 스토리, 인용구 식별
   - 토픽/앵글이 지정되지 않은 경우 가장 임팩트 있는 주제 선택

2. CONTENT CRAFTING
   - 400-800 단어의 에세이 스타일로 작성
   - H2 제목 없이 바로 본문 시작 (frontmatter title이 제목 역할)
   - 오프닝 훅 (1-2 패러그래프): 독자의 관심을 끄는 도입
   - 본론 (2-3 패러그래프): 분석, 맥락, 의미 설명
   - 원문 인용은 블록쿼트(>) 형식으로 포함
   - 마무리에 심층 분석 링크: → **관련 분석**: [[path|표시 텍스트]]
   - 링크는 항상 처리된 노트(AI/Summary, AI/Analysis 등)로 연결 (원본 Ingest/Clippings가 아님)

3. DRAFT CREATION
   - _Outbox_/BrainUpdates/에 파일 생성
   - Frontmatter 작성 (아래 형식 참조)
   - 소스에서 참조하는 파일/이미지를 .gobi/syncfiles에 추가

4. POST-CREATION
   - Obsidian에서 파일 열기
   - 유저 확인 후 approve_for_publish: true로 변경 시 gobi brain post-update로 발행
   - 유저 확인 후 approve_for_thread: true로 변경 시 Thread Posting 생성 (아래 가이드라인 참조)

5. SOCIAL POSTING (--social 플래그 시에만)
   - upload-post 스킬 사용
   - 본문을 플랫폼 제한에 맞게 축약 (X: 280자, LinkedIn: 3000자)
   - 이미지 포함 시 upload_photos, 텍스트만일 시 upload_text
   - Frontmatter의 social_platforms에 따라 발행
   - timezone: America/Los_Angeles
```

## Caveats
### 중복 방지 (Dedup Check)
새 파일 생성 전 반드시 중복 확인:
1. `_Outbox_/BrainUpdates/`에서 오늘 날짜 + 동일 소스 파일 기반 드래프트가 있는지 확인
2. 매칭되면 → 기존 파일을 **업데이트** (새로 만들지 않음)
3. Frontmatter에 `source_file` 필드를 추가하여 소스 추적:
   ```yaml
   source_file: "AI/Summary/2026-03-17 블러프 - Claude Code.md"
   ```
4. 매칭 기준: 같은 날짜 + `source_file` 값이 동일하거나, 소스 파일명의 핵심 키워드가 기존 드래프트 제목에 포함

### Frontmatter 형식
```yaml
---
title: "업데이트 제목"
date: YYYY-MM-DD
source_file: "소스 파일 경로"
approve_for_publish: false
approve_for_thread: false
social_platforms:  # optional, --social 사용 시에만
  - x
  - linkedin
tags:
  - tag1
  - tag2
  - tag3
---
```
- 태그는 3-5개, plain text

### 글쓰기 원칙
- **에세이 스타일**: 불릿 포인트 나열이 아닌 산문체로 작성
- **패러그래프 응집력**: 각 패러그래프 최소 2-3문장, 한 문장짜리 패러그래프 금지
- **짧은 항목은 헤딩 대신 볼드**: 번호 항목이 1-2문장 수준이면 `### 제목` 대신 `**제목.** 본문...` 형태로 작성 (헤딩은 충분한 분량이 있을 때만)
- **언어**: 한국어 기본, 영어 원문 인용은 그대로 보존
- **원문 인용**: 블록쿼트(>) 형식 필수

### 이미지 링크 형식
- **Vault root 기준 상대 경로 사용** (markdown 형식)
- **한글/공백이 포함된 파일명은 반드시 URL 인코딩** (GobiSpace 렌더링 필수)
  - ASCII 파일명: `![](_Outbox_/BrainUpdates/_files_/miller.jpg)` — 그대로 사용 OK
  - 한글/공백 파일명: 경로의 파일명 부분을 URL 인코딩
    - ✅ `![](_Outbox_/BrainUpdates/_files_/2026-03-22%206600%EB%A7%8C%20...png)`
    - ❌ `![](_Outbox_/BrainUpdates/_files_/2026-03-22 6600만 년 전...png)`
  - 폴더 구분자(`/`)는 인코딩하지 않고 파일명만 인코딩
- 이미지 위치에 따른 경로:
  - `_Outbox_/BrainUpdates/_files_/` 폴더: `![](_Outbox_/BrainUpdates/_files_/filename)`
  - `_files_/` 폴더 (vault root): `![](_files_/filename)`
- `gobi brain post-update --auto-attachments` 사용 시 `![[파일명]]` 형식의 wiki link를 자동으로 업로드하고 변환
- ❌ `https://webdrive.joingobi.com/...` — 전체 URL 사용 금지 (sync 전 404 발생)
- ❌ `![[image.png]]` — `--auto-attachments` 없이 wiki link 형식 사용 금지
- 이미지 경로는 반드시 `.gobi/syncfiles`에도 추가해야 백엔드 sync 후 표시됨

### 참조 파일 동기화
- 드래프트에서 참조하는 파일 경로를 `.gobi/syncfiles`에 추가
- 이미지(`_files_/` 등)도 포함
- 관련 도서 요약 등 링크된 콘텐츠 파일도 syncfiles에 추가

### 발행 워크플로우
- 생성 시 항상 `approve_for_publish: false`
- 유저가 Obsidian에서 확인 후 `true`로 변경
- 발행: `gobi brain post-update --auto-attachments --title "제목" --content "본문 전체"`
- `--auto-attachments`: 본문 내 `![[파일명]]` wiki link를 webdrive에 자동 업로드
- **--title**: frontmatter의 `title` 값 사용
- **--content**: frontmatter 제외, 본문만 전달 — `## 제목` 헤딩 포함 금지 (title 필드와 중복됨)
- 발행 시 드래프트 본문 전체를 그대로 사용 (누락 금지)

### 발행 후 수정
- `gobi brain edit-update <updateId> --auto-attachments --content "수정된 본문"` 사용
- 삭제: `gobi brain delete-update <updateId>`
- 이미지/링크 문제 발생 시 edit-update로 즉시 수정 가능

### Thread Posting 가이드라인
- **명확한 의견, 질문, 대조점**으로 시작 — 모호한 도입 금지
- **한 문장으로 답할 수 있게** 포스트를 구성 (댓글 유도)
- **초기 댓글에 빠르게 답글** 달기
- **토픽 태그 활용**: 관련 topic이 있으면 포함
- **발행 타이밍**: 주중 오전이 최적 (주말 회피)
- Thread 출력은 `AI/Sharable/YYYY-MM-DD Brain Update Threads - Claude Code.md`에 저장
- Social Media Template 형식 (Overview → Contents → Sources)
- 각 thread는 자체 완결형, 플랫폼 제한 준수 (X: 280자, Threads: 500자, LinkedIn: 3000자)

### 소셜 미디어 발행 (--social)
- `upload-post` 스킬의 API를 사용
- Gobi 발행 완료 후에만 소셜 발행 진행
- 각 플랫폼 글자 수 제한에 맞게 본문 축약
- 스케줄링이 필요하면 `scheduled_date` (ISO-8601) 사용
- **Gobi 링크 포함**: 본문 끝에 `https://www.gobispace.com/@<vault-slug>?brainUpdateId=<id>` 추가
- 이미지가 있으면 `upload_photos` 엔드포인트 사용 (텍스트+이미지)

### 미디어 생성 (선택)

#### 이미지
- `gobi media image-generate`로 이미지 생성
- 또는 `gemini-image-skill` 스킬로 Gemini 3.0 Pro 인포그래픽 생성 가능
- 모델: `gemini-3-pro-image-preview` (한글 지원 최고, $0.06/장)
- 스타일: `"clean infographic with labeled sections, icons, and visual hierarchy"`
- 출력: `media/` 또는 `_files_/YYYY-MM-DD [topic] Infographic.png`
- 생성 후 `.gobi/syncfiles`에 경로 추가 필수
- BU 본문에 마크다운 이미지로 삽입: `![alt](_files_/filename.png)`

#### 비디오 → GIF 변환 (필수)
- `gobi media cinematic-create`로 비디오 생성 후 **반드시 GIF로 변환**하여 업로드
- Brain Update에서 MP4는 인라인 렌더링되지 않으므로 GIF만 사용
- 변환 명령: `ffmpeg -i input.mp4 -vf "fps=12,scale=800:-1:flags=lanczos" -loop 0 output.gif`
- GIF는 `![[media/filename.gif]]` 형식으로 삽입 (`--auto-attachments` 사용)
- 원본 MP4는 별도 보관 (필요 시 고해상도 공유용)
