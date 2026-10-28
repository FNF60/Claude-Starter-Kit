# Claude Code Starter Kit

A ready-to-drop `.claude/` folder, a `CLAUDE.md` template and a `WORKFLOW.md` template that work for **new projects and existing codebases**. Copy into your project root, run one command, and Claude Code has the project context, the conventions, the safety nets and a session-to-session way of working from the start.

> **New to this / not a developer?** Read [QUICKSTART.md](QUICKSTART.md) first — it's the three-step, plain-language version.
>
> **Want the picture first?** Open [docs/workflow-overview.html](docs/workflow-overview.html) — one page, three diagrams: how the kit installs and updates, how a session runs, where context lives. The same diagrams are in [WORKFLOW.md](WORKFLOW.md) as Mermaid.

## What's Included

```
your-project/
├── CLAUDE.md                           <- Project instructions, filled by /setup (pins only, < 200 lines)
├── WORKFLOW.md                         <- How work flows: session lifecycle, context stack, handoff rule, tiering
├── QUICKSTART.md                       <- Plain-language 3-step guide (kit repo only — not installed)
├── CHANGELOG.md                        <- The kit's own decision record (kit repo only — not installed)
├── install.py                          <- Merge-aware installer; also the update path for an older install
├── docs/
│   ├── workflow-overview.html          <- One-page visual overview of the workflow (kit repo only)
│   ├── mermaid.min.js                  <- Mermaid 11.17.2 (official npm build), vendored so the page renders offline
│   └── handoff/archive/.gitkeep        <- Live handoffs go in docs/handoff/, consumed ones in archive/
├── .claude/
│   ├── settings.json                   <- Scoped allow/ask/deny permissions + autoCompactWindow (merges into existing settings)
│   ├── settings.jsonc                  <- Annotated, commented copy of the same profile (reference only)
│   ├── SETTINGS_NOTES.md               <- Merge + hand-edit guidance, incl. the compaction window
│   ├── rules/.gitkeep                  <- Path-scoped convention files, one per area (every file carries `paths:`)
│   ├── bin/
│   │   └── save_conversation.py        <- Transcript exporter used by /save-conversation
│   ├── agents/
│   │   └── ticket-agent.md             <- Implements one ticket for the /next-ticket dispatcher (plan, then build)
│   └── skills/
│       ├── setup/skill.md              <- /setup — configures new projects, learns existing ones, --refresh updates
│       ├── setup/ONBOARD-SCAN.md       <-   the existing-codebase scan /setup runs (referenced on demand)
│       ├── handoff/SKILL.md            <- /handoff — the session-close step (two-case rule, archive)
│       ├── handoff/template.md         <-   the handoff template of record
│       ├── next-ticket/SKILL.md        <- /next-ticket — dispatch mode: a fresh agent per ticket, owner decides + commits
│       ├── save-conversation/SKILL.md  <- /save-conversation — condensed session transcript export
│       ├── plan-interview/SKILL.md     <- /plan-interview — interview → step-by-step plan (+ CONTEXT.md/ADRs)
│       ├── codebase-design/            <- /codebase-design — deep-module / interface / seam design
│       ├── domain-modeling/            <- /domain-modeling — domain language + ADRs
│       ├── improve-codebase-architecture/ <- /improve-codebase-architecture — deepening report
│       ├── diagnosing-bugs/            <- /diagnosing-bugs — structured hard-bug diagnosis loop
│       ├── tdd/                        <- /tdd — red → green test-driven implementation
│       ├── code-review/SKILL.md        <- /code-review — two-axis (standards + spec) review
│       ├── loop-me/SKILL.md            <- /loop-me — stateful interview that outputs workflow specs
│       ├── obsidian-vault/SKILL.md     <- /obsidian-vault — read/write an Obsidian notes vault
│       └── git-guardrails/             <- /git-guardrails — block dangerous git commands
```

There are no bundled agents and no `plans/` directory: the engineering skills cover review, design and diagnosis, and Claude plans well on its own when asked. There is no `/wrap` either — the handoff is the one session-close step (see below).

## Setup — one command, either track

`/setup` detects whether it's landing in a fresh project or an existing codebase and does the right thing. First get the kit into the project, then run it.

**1. Add the kit to your project:**

- **New / empty project:** run `python install.py <target>` from this kit folder (or copy the folder's contents, minus the kit-only files, into the project root).
- **Existing project** (already has code, a `README.md`, maybe a `CLAUDE.md`): run `python install.py <target>` — or point Claude at this kit *and* your project and ask it to set things up. Either way it installs **only** `CLAUDE.md`, `WORKFLOW.md`, the `.claude/` folder and the empty `docs/handoff/archive/` scaffold, so **your project's `README.md` is never touched**, and it prompts to **merge / show diff / replace / skip** if a `CLAUDE.md` or `.claude/settings.json` already exists. Don't hand-copy the raw folder into an existing project — that would overwrite its README.

**2. Open Claude Code in the project and run `/setup`.**

**Existing project** — `/setup` runs its Existing-Project Scan (`setup/ONBOARD-SCAN.md`):
- Checks for existing AI config (`.cursorrules`, old `CLAUDE.md`, etc.) and offers to merge
- Scans your stack, conventions, risk surfaces, and git history
- Asks only what the code can't tell it (commit policy, team size, risk tolerance)
- Drafts CLAUDE.md from real signals and merges into your `.claude/settings.json`

Scan modes: `/setup --quick` (fast first pass), `/setup` (default, 2-4 min), `/setup --deep` (large monorepo, max accuracy), `/setup --refresh` (re-run later to pick up drift, preserves your edits).

**New project** — `/setup` runs a short guided questionnaire (3-4 rounds), then pre-populates CLAUDE.md and settings.json for your chosen stack and fills the `[declared]` lines of WORKFLOW.md.

Then start building — describe a feature and run `/plan-interview` to turn it into a step-by-step plan (with `/tdd` if you're testing first).

## Updating a project that already has an older kit

The kit changes; projects installed from it should not drift forever. Two steps, both safe to repeat:

1. **`python install.py <target>`** from the new kit folder. The installer notices an existing `CLAUDE.md` + `.claude/skills/` and runs as an update: new files (`WORKFLOW.md`, `handoff/template.md`, the `.claude/rules/` and `docs/handoff/archive/` scaffolds) are created, changed files prompt for merge / diff / skip, and retired files (`wrap/`) are reported, never deleted.
2. **`/setup --refresh`** in Claude Code. It adds the CLAUDE.md sections the template gained since your install — Area conventions, Compact Instructions, the Handoffs rule, the clarification instruction — without touching your `[declared]` text, and proposes which long area bullets to move into `.claude/rules/<area>.md`.

## The way of working (WORKFLOW.md)

What the kit installs is not only files; it is a session-to-session rhythm, refined over ~50 agent sessions on a production project. The short version — the long one, with diagrams, is [WORKFLOW.md](WORKFLOW.md):

- **One ticket per session.** A session opens from a handoff, runs `git status` and the tests before trusting it, reads the area's rules file in full, works, and closes.
- **Or dispatch mode.** One session runs `/next-ticket` and hands each ticket to a fresh `ticket-agent`; the owner answers questions, approves plans and commits in that one session, then replies "next". The owner picks the mode (at the close of `/plan-interview`, in the handoff's `Mode:` line, or by asking) and can switch at any time.
- **Handoffs, two cases only.** A handoff is written when the same task continues in a new session (the chat is at ~40 % of the model's window) or when a ticket is done and the next one is clear. A finished topic with no successor writes none. `/handoff` uses `handoff/template.md`; consumed handoffs move to `docs/handoff/archive/`.
- **Context in layers.** `CLAUDE.md` (always loaded, under 200 lines, pins only) → `.claude/rules/<area>.md` (loaded when a matching file is opened) → the handoff (between sessions) → auto-memory (durable facts, outside the repo) → compaction only as a fallback, with `autoCompactWindow` set above the rotation point.
- **Stage only, by default.** Agents stage and propose a commit message; the human commits. Risk-surface changes get `/code-review` before they are staged for push.
- **Decisions are written when they happen** — into the plan's ticket line, the handoff draft or auto-memory, with the options not taken — never held for the end of a session.
- **Ask when unsure.** Every session carries the standing instruction to ask a clarification question when an open decision comes up, with the alternatives explained in simple terms.

## Skills Overview

### Core workflow

| Command | When | What it does |
|---------|------|-------------|
| `/setup` | First time in a project; `--refresh` later | Detects new vs. existing; scans + drafts CLAUDE.md, or runs the greenfield wizard; refresh adds new sections without losing edits |
| `/handoff` | Session close (two-case rule) | Writes the handoff from `template.md`, archives the consumed one, stages |
| `/next-ticket` | Dispatch mode: a run of tickets without a new session each | Gives each ticket to a fresh `ticket-agent` (plan → owner decides → build → review → stage + handoff); waits for the owner's commit and "next" |
| `/save-conversation <slug>` | At every ticket close (`<ticket id> implementation`), or whenever you want a record | Saves a condensed transcript to `Supplementary AI md files/Conversations/YYYY-MM-DD-HHMM-<slug>.md` |

### Engineering skill set

| Command | When | What it does |
|---------|------|-------------|
| `/plan-interview` | Before building | Relentless one-question-at-a-time interview that turns a rough idea into a step-by-step plan (and sharpens domain terms/decisions into `CONTEXT.md`/ADRs) |
| `/codebase-design` | Designing a module | Design on the bench using deep-module / interface / seam / adapter vocabulary |
| `/domain-modeling` | Terms getting fuzzy | Sharpen domain language; record hard-to-reverse decisions as ADRs |
| `/improve-codebase-architecture` | Spare cycles | Scan for deepening opportunities, present an HTML report, plan-interview the one you pick |
| `/diagnosing-bugs` | Something's broken/slow | Structured diagnosis loop built around a tight pass/fail signal |
| `/tdd` | Implementing | Red → green test-driven cycle |
| `/code-review` | Reviewing a diff; always before pushing a risk-surface change | Two-axis review — standards + spec — via parallel sub-agents |
| `/loop-me` | Defining workflows | Stateful interview whose only output is workflow specs |
| `/obsidian-vault` | Notes work | Read and write notes in your Obsidian vault |
| `/git-guardrails` | Want hard git safety | Install a hook that blocks push / reset --hard / clean / branch -D |

## Permissions (no hooks by default)

`settings.json` is a scoped **allow / ask / deny** profile: routine read/inspect/build commands auto-run, state-changing or destructive commands prompt, and catastrophic or secret-reading commands are blocked. Evaluation order is deny → ask → allow. `settings.jsonc` is the same profile annotated with comments — read it to understand a rule, then mirror any change into `settings.json`.

The kit ships **no hooks**. Git safety comes from the `ask`/`deny` rules; if you want hard blocking of dangerous git commands, run the `/git-guardrails` skill, which installs a PreToolUse hook on demand and tells you exactly what it changed. See `.claude/SETTINGS_NOTES.md` for merge and hand-edit guidance.

**Compaction window.** The profile also sets `autoCompactWindow` to 500K tokens — above the ~40 % rotation point of a 1M-context model, so auto-compaction is a safety net rather than the normal path. On a smaller model, lower it (`.claude/SETTINGS_NOTES.md` §8).

**Windows / PowerShell.** The profile ships parallel `PowerShell(...)` rules next to the `Bash(...)` ones, so it works whether Claude Code runs through Git Bash or the native PowerShell tool — no toggle needed. The PowerShell matcher also matches cmdlet *aliases* (`Remove-Item` catches `rm`/`del`) and requires every stage of a pipeline to be allowed. See `.claude/SETTINGS_NOTES.md` §6 for the details and a known Windows caveat.

**Allowing specific download URLs.** `curl`/`wget`/`Invoke-WebRequest` prompt every time by default. To pre-approve a host you trust, add one allow rule per URL by hand — `Bash(curl https://host/path/*)` and/or `PowerShell(Invoke-WebRequest https://host/path/*)`. This is separate from the `WebFetch(domain:…)` list, which governs Claude's own page reads. Format and caveats are in `.claude/SETTINGS_NOTES.md` §7.

## Philosophy

- **Learn before asking.** `/setup` reads the codebase first so questions are informed and few.
- **Structured questions, not open chat** — setup forks use AskUserQuestion.
- **Project commands win over generic guesses** — skills call the project's lint/test/typecheck, not what they think it should be.
- **Risk Surfaces are project-defined.** Skills elevate caution based on YOUR risk areas, not a hardcoded list.
- **Sharpen before you build.** `/plan-interview` resolves the decision tree and writes the plan down before code gets written.
- **Design with a shared vocabulary.** `/codebase-design` and `/domain-modeling` keep architecture and domain language precise.
- **The human commits.** Stage-only is the default; a proposed message is a prompt, not a commit.
- **Written state beats summarized state.** A handoff the next session can verify against git and tests, not a compaction summary, carries the work forward.
- **Pins in CLAUDE.md, mechanics in rules files.** The always-loaded file stays small; the detail loads when the matching file is opened.

## Customizing

After `/setup`, you can:

- **Hand-edit CLAUDE.md** — every section is labeled `[discovered]` (from scan), `[declared]` (your answer) or `(confirm)` (an unratified default). Edit any, but discovered values may get refreshed by `/setup --refresh`.
- **Split an area into a rules file** — when an area's conventions outgrow a bullet, move them verbatim into `.claude/rules/<area>.md` with `paths:` frontmatter and leave a one-line pin (`WORKFLOW.md` §6).
- **Tune permissions** in `.claude/settings.json` — see `.claude/SETTINGS_NOTES.md` for merge guidance, and `settings.jsonc` for a commented walkthrough.
- **Add git guardrails** by running `/git-guardrails`.
- **Add domain-specific skills** in `.claude/skills/` (`/deploy`, `/migrate`, `/benchmark`, …).

## Conflict handling

If your project already has any of these, the installer / `/setup` will detect them and ask before doing anything:

- An existing `CLAUDE.md`
- An existing `.claude/` folder with skills/settings
- `.cursorrules`, `AGENTS.md`, `.aider.conf.yml`, `.github/copilot-instructions.md`
- An existing `.claude/settings.json` with hand-tuned rules

Options offered: merge, preview diff, replace, or abort. Retired kit files (`wrap/`) are reported, never removed.

## Requirements

- Claude Code CLI or IDE extension
- Git (for /setup, /handoff, /code-review, /diagnosing-bugs)
- Python 3 (for save_conversation.py and install.py)

## The kit's own history

`CHANGELOG.md` records what changed in the kit and why, with the options not taken. Start there before changing a template.
