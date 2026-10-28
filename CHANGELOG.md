# Changelog

The kit's own decision record: what changed, why, and the options not taken. Dated entries, newest first. A project that installs the kit keeps its own decisions in its plan registries, ADRs or handoffs — not here.

## 2026-10-27 — Dispatch mode

Came from the first project running on the kit: after a ticket closed, the owner asked how the jump to the next session could be automated, keeping only decisions and commits for themselves. Decisions (owner, 2026-10-27), each with the alternatives considered:

- **Dispatch mode added beside manual mode**, not instead of it: "we want both workflows to be possible … the user [is] presented with the question of (or decide[s] by prompting) that he/she wants to either do manual ticket-to-ticket sessions like now, or use the dispatch for more automation." *Not taken:* dispatch replacing manual sessions.
- **Shape: one dispatcher session + a fresh subagent per ticket.** `/next-ticket` (new skill) routes; `.claude/agents/ticket-agent.md` (new, the kit's first agent definition) plans without writing, then builds, verifies, stages and writes the case-2 handoff. Every ticket still gets a clean context; the dispatcher keeps only reports, so it lasts many tickets. *Not taken:* a shell loop over headless `claude -p` (no way to answer questions or approve plans, which breaks plan-before-build); one long session doing ticket after ticket (context fills after two or three tickets and quality drops).
- **Questions travel through the dispatcher.** A subagent cannot talk to the owner, so the agent stops at the plan and returns its questions with every alternative explained; the dispatcher asks with the explanations inside the options and writes each ratification to auto-memory the moment it is given.
- **`/code-review` runs in the dispatcher**, never in the ticket-agent: the builder never reviews itself, and nested subagents are not relied on.
- **Next-ticket trigger: the owner replies "next"** after committing; the dispatcher checks `git log` / `git status` before moving on. *Not taken:* a background watcher that starts the next ticket on the commit (starts work before the owner decides to stop; one more moving part).
- **Mode selection in three places:** a closing question in `/plan-interview`, a `Mode: manual | dispatch` line in the handoff template (a session finding no mode asks), and switching by asking at any time. *Not taken:* a one-time choice in `/setup` (the mode belongs to a run of work, not to the kit's configuration).
- **Sequential only.** The dispatcher runs one ticket at a time; parallel lanes stay manual sessions in worktrees, because stage-only commits and schema migrations are serialization points.
- Touched: `WORKFLOW.md` (§3, new §4.1, §5, §8, §11), the `CLAUDE.md` template (Handoffs bullet, Automation), `handoff/SKILL.md` and `template.md` (`Mode:`), `plan-interview/SKILL.md` (closing question), `setup/skill.md`, `install.py` (two new files), `README.md`, `QUICKSTART.md`, `docs/workflow-overview.html` (new section 3).
- **Not verified in the kit:** an end-to-end dispatch run (agent definitions load at session start; the first real run is the source project's next ticket), and the overview page's new diagram in a browser.

## 2026-10-07 — The workflow port

Ported the way of working refined over ~50 agent sessions on one production project back into the kit, so it applies to other projects, greenfield and legacy. Decisions (owner, 2026-10-07), each with the alternatives considered:

- **`WORKFLOW.md` template added** at the kit root for the mechanics (session lifecycle, context stack, ticket line, handoff rule, model tiering, install paths), with Mermaid diagrams; `CLAUDE.md` keeps the pins and points to it. *Not taken:* sections inside the `CLAUDE.md` template (always loaded, breaks the size discipline); a reference file inside the handoff skill folder (hidden from humans).
- **`/wrap` removed.** The handoff is the one session-close step. Wrap's auto-commit default contradicted the stage-only lesson and its per-session memory files duplicated handoffs plus auto-memory. *Not taken:* keeping it as an opt-in for projects without handoffs; keeping it as is with a "when to use which" note.
- **`/handoff` rewritten** as the session-close skill, agent-invocable, with a `template.md` of record: verification record from commands run this session, mandatory "Dead ends and refusals", the distrust clause and the clarification line at the top of "Next session", the two-case "when" rule, and the archive step (`docs/handoff/archive/`). The old skill saved to the OS temp directory and had no template.
- **`CLAUDE.md` template gains:** an "Area conventions" section (one pin per area, mechanics in path-scoped `.claude/rules/<area>.md`), "Compact Instructions", the "Handoffs" bullet (two-case rule), "prompt the owner for the commit message" under stage-only, the standing clarification instruction in "Output Preferences", and an explicit under-200-lines discipline. Sections folded to make room (service map into Architecture, module ownership into Architecture, the skills table into a paragraph).
- **Defaults: rotation at ~40 % of the window, `autoCompactWindow: 500000`** shipped in `settings.json` (comment in `settings.jsonc`, note in `SETTINGS_NOTES.md` §8). Sized for 1M-context models; a 200K-model user lowers or removes the key. *Not taken:* documenting without shipping the key; asking the model size at `/setup` and deriving a percentage.
- **Diagrams in Mermaid inside the Markdown, plus a one-page HTML overview** (`docs/workflow-overview.html`) for reading on any device. *Not taken:* Mermaid only; PNGs (not diffable).
- **This `CHANGELOG.md`** is where the kit records its own decisions. *Not taken:* ADRs under `docs/decisions/` (heavier than a single-maintainer kit needs); no record (reasoning lost).
- **Legacy update path:** re-run `install.py` (new files created, changed files prompt; `.claude/rules/` and `docs/handoff/archive/` scaffolded), then `/setup --refresh` adds the new `CLAUDE.md` sections without touching declared text. *Not taken:* installer only (CLAUDE.md drift stays manual); `/setup` only (depends on Claude knowing where the kit lives).
- **The source project stays the reference instance**, untouched by this port; a drift check between its skills and the kit's is a separate task. *Not taken:* re-deriving it from the kit as the first legacy test; syncing only the shared skills back.
- Auto-memory (durable facts and preferences in Claude Code's own memory directory) is a harness feature, not a file: the kit documents the practice in `WORKFLOW.md` §5 and cannot ship it.

## Earlier

See `git log` for the kit's history before this file existed (permissions profile for Bash and PowerShell, the `/save-conversation` exporter, the two-track `/setup`).
