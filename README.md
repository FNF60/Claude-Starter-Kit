# Claude Code Starter Kit

A ready-to-drop `.claude/` folder and `CLAUDE.md` template that works for **new projects and existing codebases**. Copy into your project root, run one command, and Claude Code will have the project context, conventions, and safety nets it needs from the start.

## What's Included

```
your-project/
├── CLAUDE.md                           <- Project instructions, fills from /onboard or /setup
├── install.py                          <- Merge-aware installer (handles conflicts)
├── .claude/
│   ├── settings.json                   <- Hooks + permissions (merges into existing settings)
│   ├── SETTINGS_NOTES.md               <- Merge guidance for hand-editors
│   ├── bin/
│   │   └── plan_status.py             <- Plan scanner across .claude/plans/, TODO.md, docs/plans/
│   ├── skills/
│   │   ├── onboard/skill.md          <- /onboard — learn an existing codebase (NEW)
│   │   ├── setup/skill.md            <- /setup — routes to onboard or greenfield wizard
│   │   ├── plan/skill.md             <- /plan  — tiered feature planning (3 tiers, pattern-aware)
│   │   ├── wrap/skill.md             <- /wrap  — autonomous session close, commit-policy aware
│   │   ├── check/skill.md            <- /check — health validation using project commands
│   │   ├── guard/skill.md            <- /guard — pre-edit safety with language-aware deps
│   │   ├── diff/skill.md             <- /diff  — risk classified via CLAUDE.md Risk Surfaces
│   │   ├── undo/skill.md             <- /undo  — adds git-revert path for committed work
│   │   ├── look/skill.md             <- /look  — service-aware visual QA
│   │   └── save-conversation/SKILL.md <- /save-conversation — verbatim session transcript export
│   ├── agents/
│   │   ├── code-reviewer.md          <- Reads CLAUDE.md conventions, language-aware
│   │   ├── error-trap-monitor.md     <- Multi-language silent-failure detection
│   │   └── security-reviewer.md      <- Stack-aware security scan
│   └── plans/                          <- Plan documents from /plan Tier 2-3
```

## Setup — pick the right track

### Track A: Existing project (most common)

You already have code, conventions, maybe a `.cursorrules` or an old `CLAUDE.md`, and a git history with some opinions.

```
1. Copy this folder's contents into your project root (or run python install.py)
2. Open Claude Code in the project
3. Run /onboard
   - Phase 1 checks for existing AI config and offers to merge
   - Phase 2 scans your stack, conventions, risk surfaces, git history
   - Phase 3 asks only what the code can't tell us (commit policy, team size, risk tolerance)
   - Phase 4 drafts CLAUDE.md from real signals
   - Phase 5 merges into your existing .claude/settings.json
4. Skim CLAUDE.md, edit anything the scan got wrong
5. Start building. Use /plan for your next feature.
```

`/onboard` modes:
- `/onboard --quick` — fast first pass for small repos
- `/onboard` — default, 2-4 min
- `/onboard --deep` — large monorepo, max accuracy, 5-10 min
- `/onboard --refresh` — re-run later to pick up codebase drift, preserves your edits

### Track B: New project (greenfield)

You're starting from zero or near-zero. No code, or just a README.

```
1. Copy this folder's contents into your project root
2. Open Claude Code in the project
3. Run /setup
   - Routes to greenfield wizard automatically (detects empty repo)
   - 3-4 rounds of structured questions
   - Pre-populates CLAUDE.md and settings.json based on chosen stack
4. Use /plan to design your first feature
```

`/setup` auto-routes to `/onboard` if it detects existing source files, so running `/setup` is always safe — it picks the right track.

## Skills Overview

| Command | When | What it does |
|---------|------|-------------|
| `/onboard` | First time in an existing project | Scan, infer, draft CLAUDE.md from signals |
| `/setup` | First time anywhere | Route to onboard (existing) or wizard (greenfield) |
| `/plan` | Before building | 3-tier planning; for existing projects, asks which module is the analog |
| `/wrap` | End of session | Review, auto-fix, commit (per policy), memory, report |
| `/check` | After any change | Health check using *project's* test/lint/typecheck commands |
| `/guard` | Before risky edits | Snapshot, language-aware dep map, Risk-Surface warnings |
| `/diff` | Review changes | Group by module, risk via CLAUDE.md Risk Surfaces, anti-pattern hits |
| `/undo` | Something broke | Working-tree revert or git-revert (per branch state) |
| `/look` | After UI changes | Console/state checks; service-aware via URL map |
| `/save-conversation <slug>` | When you want a record | Saves verbatim transcript to `Supplementary AI md files/Conversations/YYYY-MM-DD-HHMM-<slug>.md` |

## Agents

Background reviewers, called explicitly or triggered by hooks. All three read CLAUDE.md for project context.

- **code-reviewer** — bugs, regressions, convention violations; language-aware patterns + project rules
- **error-trap-monitor** — silent failures across JS/TS, Python, Go, Rust, Java, Ruby
- **security-reviewer** — stack-aware checklists (server / client-web / cli / data-ml / mobile)

## Hooks (automatic)

| When | What |
|------|------|
| Edit any file | CDN `@latest` blocked — pin versions (kept active only on frontend projects) |
| `git push` | Warn if pushing to project's default branch directly |
| `git commit` | Reminder to run /wrap at end of session |
| Context compaction | Preserves work state through compression |
| Session stop | Warns about uncommitted changes, shows plan status |

## Philosophy

- **Learn before asking.** `/onboard` reads the codebase first so questions are informed and few.
- **Structured questions, not open chat** — every fork uses AskUserQuestion.
- **Project commands win over generic guesses** — skills call the project's lint/test/typecheck, not what they think it should be.
- **Risk Surfaces are project-defined.** Agents and skills elevate caution based on YOUR risk areas, not a hardcoded list.
- **Safety nets are automated** — hooks catch mistakes before they land.
- **Plans follow patterns.** `/plan` asks which existing module is the analog, so new code looks like existing code.
- **Commits respect your policy.** `/wrap` is auto-commit by default but obeys stage-only / draft-PR / never-commit if your CLAUDE.md says so.

## Customizing

After `/onboard` or `/setup`, you can:

- **Hand-edit CLAUDE.md** — every section is labeled `[discovered]` (from scan) or `[declared]` (your answer). Edit either, but discovered values may get refreshed by `/onboard --refresh`.
- **Add project-specific hooks** in `.claude/settings.json` (auto-lint, auto-test, secret scanning)
- **Add domain-specific agents** in `.claude/agents/` (database-reviewer, API-contract-checker)
- **Add domain-specific skills** in `.claude/skills/` (/deploy, /migrate, /benchmark)
- **Tune permissions** in `.claude/settings.json` — see `.claude/SETTINGS_NOTES.md` for merge guidance

## Conflict handling

If your project already has any of these, the installer / `/onboard` will detect them and ask before doing anything:

- An existing `CLAUDE.md`
- An existing `.claude/` folder with skills/agents/settings
- `.cursorrules`, `AGENTS.md`, `.aider.conf.yml`, `.github/copilot-instructions.md`
- An existing `.claude/settings.json` with hand-tuned rules

Options offered: merge, preview diff, replace, or abort.

## Requirements

- Claude Code CLI or IDE extension
- Git (for /wrap, /diff, /undo, /guard, /onboard)
- Python 3 (for plan_status.py and install.py)
- Playwright MCP (optional, for /look screenshots)
