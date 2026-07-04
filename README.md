# Claude Code Starter Kit

A ready-to-drop `.claude/` folder and `CLAUDE.md` template that works for **new projects and existing codebases**. Copy into your project root, run one command, and Claude Code will have the project context, conventions, and safety nets it needs from the start.

> **New to this / not a developer?** Read [QUICKSTART.md](QUICKSTART.md) first — it's the three-step, plain-language version.

## What's Included

```
your-project/
├── CLAUDE.md                           <- Project instructions, filled by /setup
├── QUICKSTART.md                       <- Plain-language 3-step guide for non-programmers
├── install.py                          <- Merge-aware installer (handles conflicts)
├── .claude/
│   ├── settings.json                   <- Scoped allow/ask/deny permissions (merges into existing settings)
│   ├── settings.jsonc                  <- Annotated, commented copy of the same profile (reference only)
│   ├── SETTINGS_NOTES.md               <- Merge + hand-edit guidance
│   ├── bin/
│   │   └── save_conversation.py        <- Transcript exporter used by /save-conversation
│   └── skills/
│       ├── setup/skill.md              <- /setup — configures new projects and learns existing ones
│       ├── setup/ONBOARD-SCAN.md       <-   the existing-codebase scan /setup runs (referenced on demand)
│       ├── wrap/skill.md               <- /wrap — autonomous session close, commit-policy aware
│       ├── save-conversation/SKILL.md  <- /save-conversation — verbatim session transcript export
│       ├── plan-interview/SKILL.md     <- /plan-interview — interview → step-by-step plan (+ CONTEXT.md/ADRs)
│       ├── codebase-design/            <- /codebase-design — deep-module / interface / seam design
│       ├── domain-modeling/            <- /domain-modeling — domain language + ADRs
│       ├── improve-codebase-architecture/ <- /improve-codebase-architecture — deepening report
│       ├── diagnosing-bugs/            <- /diagnosing-bugs — structured hard-bug diagnosis loop
│       ├── tdd/                        <- /tdd — red → green test-driven implementation
│       ├── code-review/SKILL.md        <- /code-review — two-axis (standards + spec) review
│       ├── handoff/SKILL.md            <- /handoff — write a session/agent handoff
│       ├── loop-me/SKILL.md            <- /loop-me — stateful interview that outputs workflow specs
│       ├── obsidian-vault/SKILL.md     <- /obsidian-vault — read/write an Obsidian notes vault
│       └── git-guardrails/             <- /git-guardrails — block dangerous git commands
```

There are no bundled agents and no `plans/` directory — the engineering skills below cover review, design, and diagnosis, and Claude plans well on its own when asked.

## Setup — one command, either track

`/setup` detects whether it's landing in a fresh project or an existing codebase and does the right thing. You always run the same command.

```
1. Copy this folder's contents into your project root (or run python install.py)
2. Open Claude Code in the project
3. Run /setup
```

**Existing project** — `/setup` runs its Existing-Project Scan (`setup/ONBOARD-SCAN.md`):
- Checks for existing AI config (`.cursorrules`, old `CLAUDE.md`, etc.) and offers to merge
- Scans your stack, conventions, risk surfaces, and git history
- Asks only what the code can't tell it (commit policy, team size, risk tolerance)
- Drafts CLAUDE.md from real signals and merges into your `.claude/settings.json`

Scan modes: `/setup --quick` (fast first pass), `/setup` (default, 2-4 min), `/setup --deep` (large monorepo, max accuracy), `/setup --refresh` (re-run later to pick up drift, preserves your edits).

**New project** — `/setup` runs a short guided questionnaire (3-4 rounds), then pre-populates CLAUDE.md and settings.json for your chosen stack.

Then start building — describe a feature and run `/plan-interview` to turn it into a step-by-step plan (with `/tdd` if you're testing first).

## Skills Overview

### Core workflow

| Command | When | What it does |
|---------|------|-------------|
| `/setup` | First time in a project | Detects new vs. existing; scans + drafts CLAUDE.md, or runs the greenfield wizard |
| `/wrap` | End of session | Review, auto-fix, commit (per policy), memory, report |
| `/save-conversation <slug>` | When you want a record | Saves verbatim transcript to `Supplementary AI md files/Conversations/YYYY-MM-DD-HHMM-<slug>.md` |

### Engineering skill set

| Command | When | What it does |
|---------|------|-------------|
| `/plan-interview` | Before building | Relentless one-question-at-a-time interview that turns a rough idea into a step-by-step plan (and sharpens domain terms/decisions into `CONTEXT.md`/ADRs) |
| `/codebase-design` | Designing a module | Design on the bench using deep-module / interface / seam / adapter vocabulary |
| `/domain-modeling` | Terms getting fuzzy | Sharpen domain language; record hard-to-reverse decisions as ADRs |
| `/improve-codebase-architecture` | Spare cycles | Scan for deepening opportunities, present an HTML report, plan-interview the one you pick |
| `/diagnosing-bugs` | Something's broken/slow | Structured diagnosis loop built around a tight pass/fail signal |
| `/tdd` | Implementing | Red → green test-driven cycle |
| `/code-review` | Reviewing a diff | Two-axis review — standards + spec — via parallel sub-agents |
| `/handoff` | Passing work on | Write a handoff another session or agent can pick up |
| `/loop-me` | Defining workflows | Stateful interview whose only output is workflow specs |
| `/obsidian-vault` | Notes work | Read and write notes in your Obsidian vault |
| `/git-guardrails` | Want hard git safety | Install a hook that blocks push / reset --hard / clean / branch -D |

## Permissions (no hooks by default)

`settings.json` is a scoped **allow / ask / deny** profile: routine read/inspect/build commands auto-run, state-changing or destructive commands prompt, and catastrophic or secret-reading commands are blocked. Evaluation order is deny → ask → allow. `settings.jsonc` is the same profile annotated with comments — read it to understand a rule, then mirror any change into `settings.json`.

The kit ships **no hooks**. Git safety comes from the `ask`/`deny` rules; if you want hard blocking of dangerous git commands, run the `/git-guardrails` skill, which installs a PreToolUse hook on demand and tells you exactly what it changed. See `.claude/SETTINGS_NOTES.md` for merge and hand-edit guidance.

## Philosophy

- **Learn before asking.** `/setup` reads the codebase first so questions are informed and few.
- **Structured questions, not open chat** — setup forks use AskUserQuestion.
- **Project commands win over generic guesses** — skills call the project's lint/test/typecheck, not what they think it should be.
- **Risk Surfaces are project-defined.** Skills elevate caution based on YOUR risk areas, not a hardcoded list.
- **Sharpen before you build.** `/plan-interview` resolves the decision tree and writes the plan down before code gets written.
- **Design with a shared vocabulary.** `/codebase-design` and `/domain-modeling` keep architecture and domain language precise.
- **Commits respect your policy.** `/wrap` is auto-commit by default but obeys stage-only / draft-PR / never-commit if your CLAUDE.md says so.

## Customizing

After `/setup`, you can:

- **Hand-edit CLAUDE.md** — every section is labeled `[discovered]` (from scan) or `[declared]` (your answer). Edit either, but discovered values may get refreshed by `/setup --refresh`.
- **Tune permissions** in `.claude/settings.json` — see `.claude/SETTINGS_NOTES.md` for merge guidance, and `settings.jsonc` for a commented walkthrough.
- **Add git guardrails** by running `/git-guardrails`.
- **Add domain-specific skills** in `.claude/skills/` (`/deploy`, `/migrate`, `/benchmark`, …).

## Conflict handling

If your project already has any of these, the installer / `/setup` will detect them and ask before doing anything:

- An existing `CLAUDE.md`
- An existing `.claude/` folder with skills/settings
- `.cursorrules`, `AGENTS.md`, `.aider.conf.yml`, `.github/copilot-instructions.md`
- An existing `.claude/settings.json` with hand-tuned rules

Options offered: merge, preview diff, replace, or abort.

## Requirements

- Claude Code CLI or IDE extension
- Git (for /wrap, /setup, /code-review, /diagnosing-bugs)
- Python 3 (for save_conversation.py and install.py)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                               