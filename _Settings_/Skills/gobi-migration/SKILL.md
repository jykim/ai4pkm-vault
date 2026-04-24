---
name: gobi-migration
description: >-
  Set up a new AI4PKM vault from scratch or migrate an existing vault
  to the latest template version. Detects current state, generates a
  plan, and applies changes with full backup safety.
metadata:
  version: 1.2.0
  author: lifidea
  created: 2026-03-18
  target_version: 0.0.30
---

# Gobi Migration Skill

Set up a new AI4PKM vault from scratch **or** migrate an existing vault to v0.0.30. The skill operates in two modes:

- **Fresh Install**: For new users — scaffolds the full vault structure, fetches all template files from GitHub, and runs onboarding
- **Upgrade**: For existing users — detects the current version, identifies which structural epochs are needed, and applies changes incrementally with full backup safety

## Prerequisites

- **GitHub CLI (`gh`)** must be installed and authenticated — used to fetch template files
- **Gobi CLI (`gobi`)** must be installed for community features (spaces, brains, sessions)
  ```bash
  npm install -g @gobi-ai/cli
  # or: brew tap gobi-ai/tap && brew install gobi
  ```
  Verify: `gobi --version` — see [gobi-cli repo](https://github.com/gobi-ai/gobi-cli) for details
- **Template repo**: `jykim/ai4pkm-vault` (public)
- This skill runs **standalone in any user vault** — it does NOT require being inside the template repo

## When to Use

- User says "볼트 마이그레이션", "vault migration", or "migrate vault"
- User asks to upgrade an older vault to the latest template
- User cloned the template long ago and wants new Gobi features
- After `vault-update` (file-level) when structural changes are also needed
- User says "볼트 설정", "vault setup", or "set up vault"
- User says "새 볼트", "new vault", or "fresh install"
- User is in an empty directory and asks for help setting up a PKM vault

## Quick Commands

```markdown
"볼트 설정" / "setup vault" → Fresh install flow
"마이그레이션" / "migrate" → Upgrade flow (existing)
"마이그레이션 상태" / "migration status" → Detect version and show what's needed
"마이그레이션 검증" / "verify migration" → Run verification checklist
```

## Relationship to vault-update

| Concern | vault-update (ai4pkm-cli) | gobi-migration (this skill) |
|---------|--------------------------|----------------------------|
| Scope | File-level: fetch/overwrite files from GitHub release | Structural: merge configs, create folders, add nodes |
| When | New release available | Vault structure outdated |
| Prompts/Skills | Downloads latest versions | Delegates to vault-update or fetches from GitHub |
| orchestrator.yaml | Overwrites (with conflict check) | Merges (preserves custom nodes) |
| AGENTS.md | Overwrites (with conflict check) | Section-level merge |

**Recommended order**: Run `gobi-migration` first (structural), then `vault-update` (file content).

## Fetching Template Files from GitHub

When the migration needs a template file (prompt, base, config), fetch it from the repo:

```bash
# Fetch a single file's content (decoded from base64)
gh api "repos/jykim/ai4pkm-vault/contents/{path}?ref=main" -q '.content' | base64 -d

# Examples:
gh api "repos/jykim/ai4pkm-vault/contents/orchestrator.yaml?ref=main" -q '.content' | base64 -d
gh api "repos/jykim/ai4pkm-vault/contents/AGENTS.md?ref=main" -q '.content' | base64 -d
gh api "repos/jykim/ai4pkm-vault/contents/BRAIN.md?ref=main" -q '.content' | base64 -d
gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Prompts/Post%20Brain%20Update%20(PBU).md?ref=main" -q '.content' | base64 -d

# List directory contents
gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Prompts?ref=main" -q '.[].name'
gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Bases?ref=main" -q '.[].name'
```

**Important**: Always wrap `gh api` URLs in double quotes. URLs containing `?ref=main` will cause shell glob expansion errors if unquoted, potentially resulting in empty responses and 0-byte files.

**Always fetch from `main` branch** to get the latest template state. URL-encode spaces as `%20` in paths.

---

## Migration Flow

### Step 0: Vault Root Detection

Before anything else, confirm we're operating in the correct directory.

**Detection logic**:

1. Check CWD for `orchestrator.yaml` or `.obsidian/`
2. If not found, walk parent directories (max 5 levels) looking for the same markers
3. Interpret results:

| Found | Where | Interpretation |
|-------|-------|---------------|
| `orchestrator.yaml` | CWD | Confirmed vault root — proceed |
| `orchestrator.yaml` | Parent dir | Ask user to confirm path before proceeding |
| `.obsidian/` only | CWD or parent | Existing Obsidian vault without AI4PKM — likely fresh install candidate |
| Nothing | Anywhere | Empty/new directory — fresh install candidate |

4. If ambiguous, ask user to confirm the vault root path
5. **Warning**: If CWD is inside the `jykim/ai4pkm-vault` template repo itself (check for `.git/` remote pointing to `jykim/ai4pkm-vault`), warn the user — they probably want to operate in their own vault, not the template

### Step 1: Mode Detection

After confirming the vault root, determine which flow to use.

**Decision tree**:

- **Fresh Install**: No `orchestrator.yaml` AND no `_Settings_/` folder → run Fresh Install Flow
- **Upgrade**: `orchestrator.yaml` exists, version < `0.0.30` → run existing epoch-based migration
- **Up-to-date**: `orchestrator.yaml` exists, version == `0.0.30` → verify only, suggest `vault-update` for latest file content

**For Upgrade mode**, read `orchestrator.yaml` to determine the vault's current version.

**Primary signal**: `version` field
- `"1.0"` → original template (pre-epoch 1)
- `"0.0.13"` through `"0.0.19"` → epoch 1 done, needs epoch 2+
- `"0.0.20"` through `"0.0.25"` → epochs 1-2 done, needs epoch 3
- `"0.0.26"` through `"0.0.30"` → fully up to date

**Fallback signals** (if `version` is missing or `"1.0"`):

| Signal | Indicates |
|--------|-----------|
| `.gobi/` directory exists | At least partial epoch 1 |
| `BRAIN.md` exists | At least partial epoch 1 |
| `VAULTS.md` exists | At least partial epoch 1 |
| EDM/GDR/TIU/ACB nodes in orchestrator | Epoch 1 complete |
| `captures_dir` in orchestrator | Epoch 2+ |
| `capture_prompt_path` in orchestrator | Epoch 3 |
| Prompts: DDO, ICB, DRB exist | Epoch 1 complete |
| Prompts: PBU exists | Epoch 2 complete |
| Bases: Participants, Publish, Skills exist | Epoch 2 complete |

### Step 2: Backup (Conditional)

**Fresh Install**: Skip backup — nothing to back up. Offer `git init` if the user wants version control from the start (this happens at the end of the fresh install flow).

**Upgrade**: This step is mandatory — migration must not proceed without user confirming their backup choice.

Present the following to the user:

```
마이그레이션을 시작하기 전에 백업을 권장합니다. 어떤 방식을 선호하시나요?
1. Git 리포지토리 초기화 (git init + initial commit) — 변경 이력 추적 가능
2. 압축 파일로 백업 (zip) — 간단한 스냅샷
3. 이미 백업했으므로 건너뛰기
```

**Action by choice**:

1. **Git backup**:
   - If `.git/` already exists → create a pre-migration commit: `git add -A && git commit -m "Pre-migration backup"`
   - If no `.git/` → `git init && git add -A && git commit -m "Initial commit (pre-migration backup)"`

2. **Zip backup**:
   - Create `{vault_name}_backup_{timestamp}.zip` in the **parent directory** of the vault
   ```bash
   cd .. && zip -r "{vault_name}_backup_$(date +%Y%m%d_%H%M%S).zip" "{vault_name}/" && cd "{vault_name}"
   ```

3. **Skip** — user confirms they already have a backup

### Step 3: Generate Plan & Confirm

**Fresh Install**: Show a summary of what will be created (directories, config files, prompts, skills) and ask for confirmation.

**Upgrade**: Based on detected version, determine which epochs apply. For each epoch, check every step's precondition and mark:
- ✅ Already done (precondition met)
- ⬜ TODO (needs to be applied)

Present the plan to the user. User can:
- Approve all
- Select specific epochs (upgrade only)
- Skip individual steps

### Step 4: Execute

**Fresh Install** → run the Fresh Install Flow (see below)

**Upgrade** → apply changes epoch by epoch, step by step. Back up any modified files. Track progress in `.gobi/migrations.yaml`.

### Step 5: Verify

Run the verification checklist to confirm everything is correct.

### Step 6: Auto-invoke gobi-onboarding

After verification completes, automatically hand off to gobi-onboarding.

**Fresh install** → always full onboarding (BRAIN.md is a placeholder template):
```
마이그레이션이 완료됐어요! 이제 온보딩을 시작할게요.
```
→ Read `_Settings_/Skills/gobi-onboarding/SKILL.md` and begin full onboarding flow

**Upgrade** → route based on BRAIN.md state:

```
1. Check if BRAIN.md exists
   ├── No → "BRAIN.md가 없어요. 온보딩을 통해 프로필을 만들어볼까요?"
   │        → Read gobi-onboarding SKILL.md, invoke full flow
   └── Yes → Read BRAIN.md content
             ├── Template/placeholder (<100 words real content)
             │   → "마이그레이션이 완료됐어요! 프로필이 아직 기본 템플릿이에요. 온보딩을 시작할게요."
             │   → Read gobi-onboarding SKILL.md, invoke Step 4 (Community Onboarding)
             └── Rich content (>100 words, personalized)
                 → Check publish status (two-layer approach):
                   1. Read vaultSlug from .gobi/settings.yaml
                      └── If vaultSlug missing → "먼저 gobi init으로 볼트를 연결해주세요." → Suggest: gobi init
                   2. Primary: `gobi --json brain list-updates --mine --limit 1`
                      └── If data array non-empty → Already published (confirmed)
                   3. Fallback: `gobi --json brain search --query {vaultSlug}`
                      └── Parse JSON; check if any item in data has vaultSlug EXACTLY matching
                 ├── Already published (either check confirms)
                 │   → "마이그레이션이 완료됐어요! 프로필이 이미 커뮤니티에 공유돼 있어요."
                 │   → Suggest: gobi brain post-update (share what's new)
                 └── Not yet published (both checks negative)
                     → "마이그레이션이 완료됐어요! 프로필이 잘 갖춰져 있어요. 커뮤니티에 공유해볼까요?"
                     → Suggest: gobi brain publish
```

---

## Fresh Install Flow

*Creates a complete AI4PKM vault from scratch using the latest template files from GitHub.*

### FI-1: Scaffold Directories

Create the full directory structure:

```bash
mkdir -p _Settings_/{Prompts,Bases,Templates,Skills,Tasks,Guidelines,History,History/Ambient,History/Capture,Logs}
mkdir -p AI/{Analysis,Briefing,Canvas,Roundup,Summary,Writeup}
mkdir -p Ingest/{Clippings,Documents}
mkdir -p Journal
mkdir -p Topics
mkdir -p _Outbox_/BrainUpdates
mkdir -p .gobi
mkdir -p .claude
```

### FI-2: Fetch Root Config Files

Fetch these files from the template repo into the vault root:

```bash
# Root configuration files
for file in orchestrator.yaml AGENTS.md CLAUDE.md GEMINI.md BRAIN.md BRAIN_PROMPT.md VAULTS.md README.md .gitignore; do
  gh api "repos/jykim/ai4pkm-vault/contents/${file}?ref=main" -q '.content' | base64 -d > "${file}"
done
```

**Conflict handling**: If any file already exists:
- Identical to template → skip silently
- Differs from template → ask user: overwrite / skip / merge
- `orchestrator.yaml` → always use merge logic (see Orchestrator Merge Rules)
- `.gobi/settings.yaml` → never overwrite, only add missing keys

### FI-3: Fetch .gobi/ Config

```bash
# settings.yaml
gh api "repos/jykim/ai4pkm-vault/contents/.gobi/settings.yaml?ref=main" -q '.content' | base64 -d > .gobi/settings.yaml

# syncfiles
gh api "repos/jykim/ai4pkm-vault/contents/.gobi/syncfiles?ref=main" -q '.content' | base64 -d > .gobi/syncfiles
```

After creating `settings.yaml`, update user-specific values:
- `claudePath` — set via: `which claude` (or user's actual path)
- `vaultSlug` — will be set by `gobi init` during onboarding

**If `.gobi/settings.yaml` already exists**: Preserve as-is, only add missing keys by merging.

### FI-4: Fetch Prompts, Bases, Templates

Use `gh api` directory listing to discover files dynamically (forward-compatible with new files added to the template):

```bash
# Fetch all prompts (use while-read to handle filenames with spaces)
gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Prompts?ref=main" -q '.[].name' | while IFS= read -r file; do
  encoded=$(echo "$file" | sed 's/ /%20/g')
  gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Prompts/${encoded}?ref=main" -q '.content' | base64 -d > "_Settings_/Prompts/${file}"
done

# Fetch all bases
gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Bases?ref=main" -q '.[].name' | while IFS= read -r file; do
  encoded=$(echo "$file" | sed 's/ /%20/g')
  gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Bases/${encoded}?ref=main" -q '.content' | base64 -d > "_Settings_/Bases/${file}"
done

# Fetch all templates
gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Templates?ref=main" -q '.[].name' | while IFS= read -r file; do
  encoded=$(echo "$file" | sed 's/ /%20/g')
  gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Templates/${encoded}?ref=main" -q '.content' | base64 -d > "_Settings_/Templates/${file}"
done
```

### FI-5: Fetch Skills (Recursive)

Skills are organized in subdirectories. List each skill directory, then fetch its files:

```bash
# List skill directories (use while-read to handle names with spaces)
gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Skills?ref=main" -q '.[] | select(.type=="dir") | .name' | while IFS= read -r skill_dir; do
  mkdir -p "_Settings_/Skills/${skill_dir}"
  encoded_dir=$(echo "$skill_dir" | sed 's/ /%20/g')
  # Fetch files in each skill directory
  gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Skills/${encoded_dir}?ref=main" -q '.[] | select(.type=="file") | .name' | while IFS= read -r file; do
    encoded_file=$(echo "$file" | sed 's/ /%20/g')
    gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Skills/${encoded_dir}/${encoded_file}?ref=main" -q '.content' | base64 -d > "_Settings_/Skills/${skill_dir}/${file}"
  done
done
```

### FI-6: Create .claude/skills Symlink

```bash
mkdir -p .claude
ln -sf ../../_Settings_/Skills .claude/skills
```

### FI-7: Optional Git Init

Offer to initialize version control:

```
볼트 설정이 완료됐어요! Git으로 버전 관리를 시작할까요?
1. Git 초기화 + 초기 커밋
2. 건너뛰기 (나중에 직접 설정)
```

If user chooses option 1:
```bash
git init
git add -A
git commit -m "Initial AI4PKM vault setup (v0.0.30)"
```

### Fresh Install Conflict Handling

When a file already exists in the target directory during fresh install:

| File | Behavior |
|------|----------|
| Identical to template | Skip silently |
| Differs from template | Ask user: overwrite / skip / merge |
| `orchestrator.yaml` | Always use merge logic (preserve custom nodes) |
| `.gobi/settings.yaml` | Never overwrite — only add missing keys |
| `.gobi/syncfiles` | Never overwrite — skip with message |
| User content (`Journal/`, `Topics/`, etc.) | Never touch |

---

## Epoch 1: Foundation (v1.0 → v0.0.13)

*Adds Gobi 3.0 infrastructure: `.gobi/` config, brain files, new orchestrator nodes, new prompts, folder restructuring.*

### 1.0 Verify Prerequisites

**Check**: `gh --version` and `gobi --version` both succeed

**Action**: If `gobi` is not installed, install it before proceeding:
```bash
npm install -g @gobi-ai/cli
# or: brew tap gobi-ai/tap && brew install gobi
```
After install, run `gobi init` to authenticate and link the vault. This is required for community features (spaces, brain publish, sessions).

### 1.1 Remove Deprecated Orchestrator Fields

**Check**: `orchestrator.yaml` contains any of: `stt_provider`, `stt_language`, `tts_provider`, `orchestrator_language`, `wakeword_enabled`, `wakeword_mode`, `manual_end_detection`, `periodic_processing`, `periodic_prompt`, `periodic_seconds`, `mic_gain`

**Action**: Remove these fields from the `orchestrator` section. Back up file first.

### 1.2 Add Orchestrator Directory Fields

**Check**: `orchestrator.yaml` has `chat_history_dir`, `ambient_recording_dir`, `file_extensions`

**Action**: Add missing fields to the `orchestrator` section:
```yaml
orchestrator:
  # ... existing fields ...
  chat_history_dir: _Settings_/History
  ambient_recording_dir: _Settings_/History/Ambient
  file_extensions:
    - .md
    - .pdf
    - .docx
    - .doc
    - .txt
    - .epub
```

### 1.3 Add Orchestrator Nodes

**Check**: For each node below, check if a node with that name exists in `nodes:`

**Action**: Add missing nodes:

```yaml
  - type: agent
    name: Extract Document to Markdown (EDM)
    input_path: Ingest/Documents
    output_path: AI/Summary
    executor: claude_code
    input_type: new_file
    input_pattern: "*.pdf|*.docx|*.doc|*.txt|*.epub"
    trigger_exclude_pattern: "*.md"
    output_naming: "{title}.md"
    enabled: true
  - type: agent
    name: Generate Daily Roundup (GDR)
    cron: 0 4 * * *
    output_path: AI/Roundup
  - type: agent
    name: Topic Index Update (TIU)
    cron: 30 4 * * *
    input_path: AI/Roundup
    output_path: Topics
  - type: agent
    name: Ambient Canvas Brainstorming (ACB)
    input_path: _Settings_/History/Ambient
    output_path: AI/Canvas
    input_type: new_file
    output_naming: "{datetime} {title}.canvas"
    enabled: true
```

### 1.4 Create .gobi/ Directory and Settings

**Check**: `.gobi/settings.yaml` exists

**⚠️ Never overwrite existing server-related .gobi/ files.**

**Action**:
- **If `.gobi/settings.yaml` does NOT exist** → Create `.gobi/` directory, fetch template, then prompt user to customize:
  ```bash
  mkdir -p .gobi
  gh api "repos/jykim/ai4pkm-vault/contents/.gobi/settings.yaml?ref=main" -q '.content' | base64 -d > .gobi/settings.yaml
  ```
  Then update user-specific values:
  - `vaultSlug` — will be set by `gobi init`
  - `claudePath` — set to user's actual Claude CLI path (e.g., `which claude`)

- **If `.gobi/settings.yaml` already exists** → **Preserve as-is**. Only add missing keys by merging (do not replace). Compare with template and add any keys that don't exist in the user's file.

Default template content:
```yaml
vaultSlug: ai4pkm-vault
selectedSpaceSlug: cmds
orchestratorEnabled: true
voiceSettings:
  primaryLanguage: ko
  secondaryLanguage: en
  llmProvider: claude-cli
  llmConfig:
    cli:
      claudePath: /usr/local/bin/claude
```

> **Note**: User should run `gobi init` to properly set `vaultSlug`, and update `claudePath` to their actual path.

### 1.5 Create .gobi/syncfiles

**Check**: `.gobi/syncfiles` exists

**⚠️ Never overwrite existing server-related .gobi/ files.**

**Action**:
- **If `.gobi/syncfiles` does NOT exist** → Create from template:
  ```bash
  gh api "repos/jykim/ai4pkm-vault/contents/.gobi/syncfiles?ref=main" -q '.content' | base64 -d > .gobi/syncfiles
  ```
- **If `.gobi/syncfiles` already exists** → **Skip entirely** with message: "기존 syncfiles를 유지합니다"

Default content (for new creation only):
```
/BRAIN.jpg
/BRAIN.md
/BRAIN_PROMPT.md
```

### 1.6 Create BRAIN.md

**Check**: `BRAIN.md` exists in vault root

**Action**: If `BRAIN.md` doesn't exist, **defer to gobi-onboarding skill Step 1** for interactive profile creation rather than writing a placeholder template. The onboarding flow creates a personalized BRAIN.md through conversation, which is far more valuable than a generic template.

**Fallback** (if onboarding is not available or user prefers manual setup): Fetch template from repo:
```bash
gh api "repos/jykim/ai4pkm-vault/contents/BRAIN.md?ref=main" -q '.content' | base64 -d > BRAIN.md
```

Then user should customize. Template content:

```markdown
---
title: "홍길동의 Second Brain"
description: "의적 홍길동 — 전쟁사·전략/전술·무기·정보 수집 전문"
thumbnail: "[[BRAIN.jpg]]"
prompt: "[[BRAIN_PROMPT.md]]"
tags:
  - profile
  - second-brain
created: 2024-01-01 00:00:00
---

## Welcome to My Second Brain

**홍길동** | 의적

### 전문 분야
- 전쟁사 — 역사 속 전쟁의 원인, 전개, 결과 분석
- 전략/전술 — 군사 전략과 전투 전술 연구
- 무기 — 고대부터 현대까지 무기 체계

### 핵심 역량
- 정보 수집 — 의적 활동을 위한 정보 수집과 분석

### 목표
- 지식 구축 — 전쟁사와 전략/전술 관련 지식을 체계적으로 정리
```

> **Note**: User should customize name, description, expertise, and goals to match their profile.

### 1.7 Create BRAIN_PROMPT.md

**Check**: `BRAIN_PROMPT.md` exists in vault root

**Action**: Fetch from repo:
```bash
gh api "repos/jykim/ai4pkm-vault/contents/BRAIN_PROMPT.md?ref=main" -q '.content' | base64 -d > BRAIN_PROMPT.md
```

Template content:

```markdown

## Rules of Engagement
- Use [[BRAIN.md]] and files linked from there to answer questions
  - Minimize the use of internal knowledge
  - Answer should be grounded by user's documents
- Adjust the tone / language to the person asking
- Speak as if you're the owner of this brain
  - When asked about your identity, make clear you're AI agent representing the owner
- Invite to connect the owner himself if the question is outside your scope
```

### 1.8 Create VAULTS.md

**Check**: `VAULTS.md` exists in vault root

**Action**: Fetch from repo:
```bash
gh api "repos/jykim/ai4pkm-vault/contents/VAULTS.md?ref=main" -q '.content' | base64 -d > VAULTS.md
```

Template content:

```markdown
---
description: Vault registry for ai4pkm-vault
---

# Vault Registry

## Registered Vaults

### CV2601 (AI4PKM Community Vault)

| Property    | Value                        |
| ----------- | ---------------------------- |
| ID          | `CV2601`                     |
| Path        | [TBA]                        |
| Type        | `community`                  |
| Role        | `sub`                        |
| Description | AI4PKM 커뮤니티 볼트 - 지식 공유 및 Q&A |
| Access      | `read-write`                 |

#### Personal Vault Access Rules (for Community Prompts)

커뮤니티 프롬프트가 개인 볼트 콘텐츠를 읽을 때의 접근 규칙.

| Type      | Folders    |
| --------- | ---------- |
| Blacklist | `Journal/` |

---

### [Vault Name] (Template)

| Property | Value |
|----------|-------|
| ID | `` |
| Path | `` |
| Type | `` |
| Role | `` |
| Description | |
| Access | `` |
```

### 1.9 Create Required Folders

**Check**: Each folder exists

**Action**: Create missing folders:
- `_Settings_/History/`
- `_Settings_/History/Ambient/`
- `Ingest/Documents/`
- `AI/Canvas/`
- `AI/Roundup/`
- `_Outbox_/`

### 1.10 Add Skills Symlink

**Check**: `.claude/skills` symlink exists pointing to `_Settings_/Skills`

**Action**: Create symlink:
```bash
mkdir -p .claude
ln -sf ../../_Settings_/Skills .claude/skills
```

### 1.11 Add New Prompts (DDO, ICB, DRB, EDM, ACB)

**Check**: These prompt files exist in `_Settings_/Prompts/`:
- `Daily Downloads Organizer (DDO).md`
- `Interactive Canvas Brainstorm (ICB).md`
- `Daily Research Briefing (DRB).md`
- `Extract Document to Markdown (EDM).md`
- `Ambient Canvas Brainstorming (ACB).md`

**Action**: Fetch each missing prompt from GitHub:
```bash
# Example for each prompt (URL-encode spaces as %20):
gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Prompts/Daily%20Downloads%20Organizer%20(DDO).md?ref=main" -q '.content' | base64 -d > "_Settings_/Prompts/Daily Downloads Organizer (DDO).md"
gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Prompts/Interactive%20Canvas%20Brainstorm%20(ICB).md?ref=main" -q '.content' | base64 -d > "_Settings_/Prompts/Interactive Canvas Brainstorm (ICB).md"
gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Prompts/Daily%20Research%20Briefing%20(DRB).md?ref=main" -q '.content' | base64 -d > "_Settings_/Prompts/Daily Research Briefing (DRB).md"
gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Prompts/Extract%20Document%20to%20Markdown%20(EDM).md?ref=main" -q '.content' | base64 -d > "_Settings_/Prompts/Extract Document to Markdown (EDM).md"
gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Prompts/Ambient%20Canvas%20Brainstorming%20(ACB).md?ref=main" -q '.content' | base64 -d > "_Settings_/Prompts/Ambient Canvas Brainstorming (ACB).md"
```

### 1.12 Remove Deprecated Prompts

**Check**: These files do NOT exist in `_Settings_/Prompts/`:
- `Personal Brain Chat (PBC).md`
- `Create Topic Page (CTP).md`

**Action**: If they exist, back up and remove them (they were replaced by ICB and TIU respectively).

### 1.13 Update Version

**Action**: Set `version: "0.0.13"` in `orchestrator.yaml` (only if all steps above complete).

---

## Epoch 2: Capture (v0.0.13 → v0.0.20)

*Adds capture infrastructure, PBU prompt, new bases, Outbox, and AGENTS.md expansion.*

### 2.1 Add Captures Configuration

**Check**: `orchestrator.yaml` contains `captures_dir`

**Action**: Add to the `orchestrator` section:
```yaml
orchestrator:
  # ... existing fields ...
  captures_dir: _Settings_/History/Capture
  capture_prompt_path: _Settings_/Prompts/Ambient Canvas Brainstorming (ACB).md
```

### 2.2 Create Capture Folders

**Check**: `_Settings_/History/Capture/` exists

**Action**: Create the folder:
```bash
mkdir -p "_Settings_/History/Capture"
```

### 2.3 Add PBU Prompt

**Check**: `_Settings_/Prompts/Post Brain Update (PBU).md` exists

**Action**: Fetch from GitHub:
```bash
gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Prompts/Post%20Brain%20Update%20(PBU).md?ref=main" -q '.content' | base64 -d > "_Settings_/Prompts/Post Brain Update (PBU).md"
```

### 2.4 Add New Bases

**Check**: These base files exist in `_Settings_/Bases/`:
- `Participants.base`
- `Publish.base`
- `Skills.base`

**Action**: Fetch each from GitHub:
```bash
gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Bases/Participants.base?ref=main" -q '.content' | base64 -d > "_Settings_/Bases/Participants.base"
gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Bases/Publish.base?ref=main" -q '.content' | base64 -d > "_Settings_/Bases/Publish.base"
gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Bases/Skills.base?ref=main" -q '.content' | base64 -d > "_Settings_/Bases/Skills.base"
```

### 2.5 Create BrainUpdates Outbox

**Check**: `_Outbox_/BrainUpdates/` folder exists

**Action**: Create the folder:
```bash
mkdir -p "_Outbox_/BrainUpdates"
```

### 2.6 Expand AGENTS.md

**Check**: `AGENTS.md` contains sections for Skills, Search over files, and Gobi Space Features

**Action**: Fetch latest `AGENTS.md` from GitHub template and do a section-level merge:
```bash
gh api "repos/jykim/ai4pkm-vault/contents/AGENTS.md?ref=main" -q '.content' | base64 -d > /tmp/AGENTS_latest.md
```
Then compare sections and add any missing ones while preserving user customizations. See **AGENTS.md Merge Rules** below.

### 2.7 Update Version

**Action**: Set `version: "0.0.20"` in `orchestrator.yaml`.

---

## Epoch 3: Polish (v0.0.20 → v0.0.30)

*Version bump, AGENTS.md Gobi sections, CLAUDE.md refinements, onboarding skill updates.*

### 3.1 Update AGENTS.md Gobi Sections

**Check**: `AGENTS.md` contains "Gobi Space Features" section with `gobi-cli` references

**Action**: If missing, add the Gobi Space Features section from the latest template (see AGENTS.md merge rules).

### 3.2 Update CLAUDE.md

**Check**: `CLAUDE.md` references `AGENTS.md` for generic rules

**Action**: Fetch latest `CLAUDE.md` from GitHub and compare. If the user has a monolithic CLAUDE.md (all rules inline), suggest splitting into CLAUDE.md (agent-specific) + AGENTS.md (generic). See **CLAUDE.md Merge Rules** below.

### 3.3 Update Onboarding Skill

**Check**: `_Settings_/Skills/gobi-onboarding/SKILL.md` exists and is recent

**Action**: Fetch latest from GitHub. The onboarding skill changes frequently, so always pull the current version:
```bash
# Fetch the entire gobi-onboarding skill directory
for file in $(gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Skills/gobi-onboarding?ref=main" -q '.[].name'); do
  gh api "repos/jykim/ai4pkm-vault/contents/_Settings_/Skills/gobi-onboarding/${file}?ref=main" -q '.content' | base64 -d > "_Settings_/Skills/gobi-onboarding/${file}"
done
```

### 3.4 Update Version to Target

**Action**: Set `version: "0.0.30"` in `orchestrator.yaml`.

### 3.5 Add id/name Fields

**Check**: `orchestrator.yaml` has `id` and `name` fields at root level

**Action**: Add if missing:
```yaml
id: ai4pkm_vault
name: ai4pkm_vault
```

---

## Orchestrator Merge Rules

When merging `orchestrator.yaml`, follow these rules:

### Preserve
- **User-custom nodes**: Any node name not in the template → keep as-is
- **User-modified fields on template nodes**: If user changed `output_path`, `cron`, `enabled`, etc. on a template node → keep user's values
- **Pollers**: User's poller configuration is always preserved

### Add
- **Missing template nodes**: Match by `name` field. If a template node name is not found in user's config, add it
- **Missing orchestrator fields**: Add new fields (e.g., `captures_dir`) without removing existing ones

### Remove
- **Deprecated fields**: Remove fields listed in epoch 1.1 (STT/TTS/wakeword settings)
- **Deprecated nodes**: None currently — no template nodes have been removed

### Version
- Only update `version` field after all epoch steps are verified

---

## AGENTS.md Merge Rules

AGENTS.md is section-based (H2 headers). Merge strategy:

1. **Parse both files into sections** (split on `## ` headers)
2. **For each section in template**:
   - If section header exists in user's file → keep user's version (they may have customized)
   - If section header is missing → add it at the appropriate position
3. **For each section only in user's file** → keep it (user-added content)
4. **Flag conflicts**: If a section exists in both but content differs significantly, show both and let user choose

**Key sections to ensure exist** (as of v0.0.30):
- `## Core Mission & Principles`
- `## Prompts & Workflows`
- `## Skills`
- `## Search over files`
- `## 📝 Content Creation Requirements`
- `## 🔄 Additional Principles`
- `## Quality Standards`
- `## Multi-Vault Operations`
- `## Gobi Space Features`

---

## CLAUDE.md Merge Rules

CLAUDE.md should be agent-specific (Claude Code only), referencing AGENTS.md for generic rules.

1. **Check structure**: If CLAUDE.md has generic rules that belong in AGENTS.md, suggest moving them
2. **Ensure reference**: First line after frontmatter should be: `**All generic rules are defined in @AGENTS.md`
3. **Keep agent-specific sections**: Task Management, Version Control, Tool Usage, etc.
4. **Add missing sections**: Compare with template and add any missing Claude-specific sections

---

## Target orchestrator.yaml Structure (v0.0.30)

```yaml
version: 0.0.30
orchestrator:
  prompts_dir: _Settings_/Prompts
  tasks_dir: _Settings_/Tasks
  logs_dir: _Settings_/Logs
  skills_dir: .claude/skills
  bases_dir: _Settings_/Bases
  chat_history_dir: _Settings_/History
  ambient_recording_dir: _Settings_/History/Ambient
  system_prompt_file: _Settings_/Prompts/Real-time Voice Assistant (RVA).md
  max_concurrent: 3
  poll_interval: 1
  file_extensions:
    - .md
    - .pdf
    - .docx
    - .doc
    - .txt
    - .epub
  captures_dir: _Settings_/History/Capture
  capture_prompt_path: _Settings_/Prompts/Ambient Canvas Brainstorming (ACB).md
defaults:
  executor: claude_code
  timeout_minutes: 30
  max_parallel: 3
  task_create: true
  task_priority: medium
  task_archived: false
nodes:
  - type: agent
    name: Enrich Ingested Content (EIC)
    input_path: Ingest/Clippings
    output_path: AI/Summary
    output_type: new_file
  - type: agent
    name: Extract Document to Markdown (EDM)
    input_path: Ingest/Documents
    output_path: AI/Summary
    executor: claude_code
    input_type: new_file
    input_pattern: "*.pdf|*.docx|*.doc|*.txt|*.epub"
    trigger_exclude_pattern: "*.md"
    output_naming: "{title}.md"
    enabled: true
  - type: agent
    name: Generate Daily Roundup (GDR)
    cron: 0 4 * * *
    output_path: AI/Roundup
  - type: agent
    name: Topic Index Update (TIU)
    cron: 30 4 * * *
    input_path: AI/Roundup
    output_path: Topics
  - type: agent
    name: Ambient Canvas Brainstorming (ACB)
    input_path: _Settings_/History/Ambient
    output_path: AI/Canvas
    input_type: new_file
    output_naming: "{datetime} {title}.canvas"
    enabled: true
  # User-custom nodes are preserved here
id: ai4pkm_vault
name: ai4pkm_vault
```

---

## Migration Tracking

Track applied migrations in `.gobi/migrations.yaml`:

```yaml
migrations:
  - epoch: 1
    name: Foundation
    applied_at: 2026-03-18T10:00:00-07:00
    from_version: "1.0"
    to_version: "0.0.13"
    steps_applied: [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 1.13]
    steps_skipped: []
  - epoch: 2
    name: Capture
    applied_at: 2026-03-18T10:05:00-07:00
    from_version: "0.0.13"
    to_version: "0.0.20"
    steps_applied: [2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7]
    steps_skipped: []
  - epoch: 3
    name: Polish
    applied_at: 2026-03-18T10:10:00-07:00
    from_version: "0.0.20"
    to_version: "0.0.30"
    steps_applied: [3.1, 3.2, 3.3, 3.4, 3.5]
    steps_skipped: []
```

For fresh installs, track as:

```yaml
migrations:
  - epoch: fresh_install
    name: Fresh Install
    applied_at: 2026-03-18T10:00:00-07:00
    from_version: null
    to_version: "0.0.30"
    steps_applied: [FI-1, FI-2, FI-3, FI-4, FI-5, FI-6, FI-7]
    steps_skipped: []
```

---

## Verification Checklist

After migration completes, verify:

### Prerequisites
- [ ] `gh --version` succeeds (GitHub CLI installed)
- [ ] `gobi --version` succeeds (Gobi CLI installed)
- [ ] `gobi auth status` shows authenticated

### Structure
- [ ] `.gobi/settings.yaml` exists with `vaultSlug` and `selectedSpaceSlug`
- [ ] `.gobi/syncfiles` exists with brain file paths
- [ ] `BRAIN.md` exists with valid YAML frontmatter
- [ ] `BRAIN_PROMPT.md` exists
- [ ] `VAULTS.md` exists
- [ ] `.claude/skills` symlink points to `_Settings_/Skills`

### Folders
- [ ] `_Settings_/History/` exists
- [ ] `_Settings_/History/Ambient/` exists
- [ ] `_Settings_/History/Capture/` exists
- [ ] `Ingest/Documents/` exists
- [ ] `AI/Canvas/` exists
- [ ] `AI/Roundup/` exists
- [ ] `_Outbox_/` exists
- [ ] `_Outbox_/BrainUpdates/` exists

### Orchestrator
- [ ] `version` is `0.0.30`
- [ ] No deprecated fields (STT/TTS/wakeword)
- [ ] Has `chat_history_dir`, `ambient_recording_dir`, `file_extensions`
- [ ] Has `captures_dir`, `capture_prompt_path`
- [ ] Has nodes: EIC, EDM, GDR, TIU, ACB
- [ ] Has `id` and `name` at root level
- [ ] User-custom nodes preserved

### Prompts
- [ ] DDO, ICB, DRB, EDM, ACB, PBU prompts exist
- [ ] Deprecated prompts (PBC, CTP) removed

### Bases
- [ ] Participants.base, Publish.base, Skills.base exist

### Config Files
- [ ] AGENTS.md has all required sections
- [ ] CLAUDE.md references AGENTS.md

---

## Safety Rules

1. **Non-destructive**: Always back up modified files as `{name}.bak.{timestamp}` before changes
2. **No user content deletion**: Never modify files in `Ingest/`, `Journal/`, `Topics/`, `AI/` (except creating folders)
3. **Incremental**: Apply one epoch at a time, verify before proceeding
4. **Idempotent**: Each step checks preconditions — running migration twice is safe
5. **User approval**: Always show plan before executing; never auto-apply
6. **Preserve customizations**: User-added nodes, settings, and content are never removed
7. **Track everything**: Log all changes to `.gobi/migrations.yaml`
8. **Protected files**: Never overwrite existing `.gobi/` server-related files (`syncfiles`, `settings.yaml`, `sync_state_v3.db`) — these contain user-specific configuration and sync state. Only create if missing; merge missing keys if needed.
9. **Backup required**: Always offer backup (git commit or zip) before starting migration (see Step 2)
10. **Quote all URLs**: All `gh api` URL arguments must be wrapped in double quotes to prevent shell glob expansion of `?` characters
11. **Never silently overwrite**: During fresh install, if an existing file differs from the template, always ask the user before overwriting (overwrite / skip / merge)
12. **Dynamic file discovery**: Use `gh api` directory listing to discover template files rather than hardcoding filenames — this ensures forward-compatibility when new files are added to the template

---

## Troubleshooting

### "orchestrator.yaml has no version field"

This means the vault predates versioning. Treat as `v1.0` and start from epoch 1.

### "Migration says TODO but the file already exists"

The precondition check may be looking for specific content, not just file existence. Check the step details for what exactly is being verified.

### "I have custom nodes that disappeared"

This should not happen — the merge preserves all user-custom nodes. Check `.gobi/migrations.yaml` for what was applied and restore from `orchestrator.yaml.bak.*`.

### "AGENTS.md merge conflict"

If sections differ between user's file and template, the migration will flag the conflict and show both versions. Choose which to keep, or manually merge.

### "vault-update vs migration — which first?"

Run `gobi-migration` first for structural changes, then `vault-update` for latest file content. Migration sets up the structure; vault-update fills in the latest prompt/skill content.

### "Can I roll back?"

All modified files have `.bak.{timestamp}` backups. To roll back an epoch:
1. Restore backed-up files
2. Remove the epoch entry from `.gobi/migrations.yaml`
3. Revert the version in `orchestrator.yaml`

### "Vault root not detected"

The skill looks for `orchestrator.yaml` or `.obsidian/` in the current directory and up to 5 parent directories. If neither is found:
- Confirm you're in the right directory
- For fresh install: any empty directory is fine — the skill will create everything
- For upgrade: navigate to your vault root first, or specify the path when prompted

### "gh api rate limit during fresh install"

Fresh install makes many API calls to fetch all template files. If you hit GitHub's rate limit:
- Wait a few minutes and retry
- Use a GitHub Personal Access Token (PAT) for higher rate limits: `gh auth login --with-token`
- The skill tracks progress, so retrying will skip already-fetched files

### "Fresh install in non-empty directory"

If the target directory already has files, the skill uses conflict handling:
- Files identical to the template are skipped silently
- Files that differ trigger a prompt: overwrite / skip / merge
- User content directories (`Journal/`, `Topics/`, etc.) are never touched
- `.gobi/settings.yaml` is never overwritten — only missing keys are added
