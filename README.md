# AI4PKM Vault Template

An Obsidian vault template for the AI4PKM (AI for Personal Knowledge Management) system.

## Structure

```
ai4pkm_vault/
├── .claude/
│   └── skills/           # Claude skills (subtree)
├── _Settings_/           # Configuration and system files
│   ├── Prompts/          # AI agent prompts
│   ├── Templates/        # Markdown templates
│   ├── Guidelines/       # PKM guidelines
│   └── Logs/             # Execution logs
├── Bases/                # Obsidian database definitions
├── AI/                   # AI-generated content
│   ├── Summary/          # Enriched articles
│   ├── Analysis/         # Analysis outputs
│   ├── Tasks/            # Knowledge tasks
│   └── Canvas/           # Visual canvases
├── Ingest/               # Input content
│   └── Clippings/        # Web clippings
├── Journal/              # Daily journals
├── Projects/             # Project notes
├── _Inbox_/              # Unsorted items
├── _Archive_/            # Archived content
├── _Sandbox_/            # Experimental area
├── orchestrator.yaml     # Agent orchestration config
├── AGENTS.md             # Generic AI agent rules
├── CLAUDE.md             # Claude-specific rules
└── GEMINI.md             # Gemini-specific rules
```

## Skills Subtree

The `.claude/skills/` folder is managed as a git subtree from [claude-obsidian-skills](https://github.com/jykim/claude-obsidian-skills).

### Update Skills

```bash
git subtree pull --prefix=ai4pkm_vault/.claude/skills https://github.com/jykim/claude-obsidian-skills.git main --squash
```

### Push Changes to Skills Repo

If you modify skills and want to push back:

```bash
git subtree push --prefix=ai4pkm_vault/.claude/skills https://github.com/jykim/claude-obsidian-skills.git main
```

## Usage

1. Clone this repository
2. Open `ai4pkm_vault` folder as an Obsidian vault
3. Configure `secrets.yaml` based on `secrets.yaml.example`
4. Run AI4PKM CLI with this vault path

## Configuration

- `orchestrator.yaml` - Agent routing and automation settings
- `secrets.yaml` - API keys and credentials (not tracked)

## Related Projects

- [AI4PKM](https://github.com/jykim/AI4PKM) - Main CLI and orchestrator
- [claude-obsidian-skills](https://github.com/jykim/claude-obsidian-skills) - Reusable Claude skills
