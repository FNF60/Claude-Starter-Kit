# Changelog

The kit's own decision record: what changed, why, and the options not taken. Dated entries, newest first. A project that installs the kit keeps its own decisions in its plan registries, ADRs or handoffs — not here.

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
