# Changelog

The kit's own decision record: what changed, why, and the options not taken. Dated entries, newest first. A project that installs the kit keeps its own decisions in its plan registries, ADRs or handoffs — not here.

## 2026-11-25 — Kit gaps closed: setup, plan register, hook quoting, fresh-install checks

The owner listed what to close now and what waits (2026-11-25): close the kit's own gaps; the evidence from the legacy Java project's dispatch runs, the `ROTATE`-vs-`PARTIAL` choice, and a second model family wait for the end of that project's headless extraction.

- **`/setup` asks for the new settings.** Existing projects: the scan lists `git status --short` paths as leave-alone candidates and Round 2 asks which are standing local changes (Q4); `--refresh` adds the Leave-alone line and the name-based staging sentence to an older `CLAUDE.md`. Greenfield writes `Leave-alone files: (none)`. The guardrails extra and the existing-project settings step mention the hook-alone choice (`git-guardrails` 3b). *Not taken:* asking greenfield projects (a fresh repo has no standing changes).
- **`/plan-interview` writes a stage register** (`WORKFLOW.md` §2.1) whenever the plan has more than one ticket: stages and tickets, test kind per ticket by the kind of work (PIN / PROOF / none), checkable Done when, tickets sized to ~40 % of an agent's window, open fields (branch) asked one at a time; dispatch closes with the exact `/next-ticket <plan> <stage>` line. *Not taken:* a register only when dispatch is chosen (it keeps a manual run honest too).
- **Hook quoting fixed** (the false positive documented yesterday). The splitter and tokenizer now follow the running shell's escape rules, taken from the hook input's tool name: bash `\`, PowerShell backtick (where `\"` really ends a string, so applying bash rules there would hide a later `; git push`); a nested `bash -c` / `powershell -Command` / `cmd /c` uses its own shell's rules. Found on the way: `cmd /c git push` was not caught at all (`/c` was not read as a command flag); now it is. Self-test: 9 new shell cases plus every existing case run under both shells, and a PowerShell end-to-end case; 0 failures. The new cases fail against the old script (3 of 4 checked), so they bite. *Not taken:* bash rules for both tools (a PowerShell false negative).
- **Fresh install fixed:** nothing created `docs/Supplementary AI md files/Conversations/`, and `save_conversation.py` refuses to write without it, so a fresh project's first dispatch ticket close would fail at `save-agent`. `install.py` now ships its `.gitkeep` (38 files), and `/setup` scaffolds it.
- Touched: `.claude/skills/setup/skill.md`, `.claude/skills/setup/ONBOARD-SCAN.md`, `.claude/skills/plan-interview/SKILL.md`, `.claude/skills/git-guardrails/SKILL.md` and both scripts, `install.py`, `docs/Supplementary AI md files/Conversations/.gitkeep` (new).

**Verified (2026-11-25), settling items from the 2026-11-24 "Still not verified" list:**
- **Clean install, partly:** `install.py` into an empty `git init` repo: 38 files, settings parse, hook self-test passes, `next-ticket` and its log template present. Not yet: a new interactive session there running `/next-ticket` on one small ticket (needs the owner's session).
- **The hook through a fresh install + `/git-guardrails`, settled:** steps followed as written in the fresh repo (project scope, stage-only, hook alone), then a headless `claude -p` session there: the main session's `git -C . branch -D guardrail-probe-does-not-exist` and a `general-purpose` subagent's `git commit -m guard-probe` were both refused by the hook (exit 2, the kit's message); the repo still had no commits. Side note: the workspace was untrusted, so its allow list was ignored, but the hook still ran.
- **Guards inside subagents, settled for the hook** (`git commit` refused inside a subagent, above; `git push` had been seen in the legacy project). The deny-list half stays untested: under the hook-alone choice there is no deny rule to hit.
- **The overview page in a browser, settled:** rendered in headless Chrome from a local server; all four diagrams draw, section 3 with the 2026-11-24 changes, no Mermaid errors.

**Still not verified:** the session part of the clean install (above); "an agent fails twice" (only real use produces it); a register written by `/plan-interview` driving a real dispatch run; every item the legacy project's runs will settle (see the 2026-11-24 entries); a second model family.

## 2026-11-24 (later) — The legacy Java project's dispatch variant carried back

The 2026-11-21 entry deferred the legacy Java project's dispatch changes until its extraction was done. The same day as the entry below, the owner compared that project's setup with the kit both ways and chose to carry back now every item that is not specific to the project (owner, 2026-11-24, item by item; all generic items approved). That project ran one pilot ticket (P0-1) under its variant; its evidence is that one run plus its kit-delta list, so everything below is **adopted, not verified in the kit**. In the other direction, the project took this kit's dispatcher budget check (with its own `PARTIAL` instead of `ROTATE`), transcripts, the review of untracked files, the split hand-over, the stage-level milestone check, and this hook with its self-test.

**Agent discipline** (`ticket-agent.md`, `next-ticket/SKILL.md`):
- **Review keyed on the test kind, not only on risk surfaces.** Every ticket whose test kind is not `none` (or that touches a risk surface) returns `REVIEW_NEEDED`; Finalize runs only after the findings arrive, and the Build message says "Return REVIEW_NEEDED before staging." Evidence: the pilot agent read "Approved: phase 2" as permission to stage and skipped the review. *Not taken:* keep risk-surface-only review.
- **No test suite in Phase 1.** The dispatcher runs the baseline in the background while the agent plans; the agent's distrust check is git only. Saves a full suite run per ticket and avoids two runs on shared build output. *Not taken:* the agent running tests in its distrust check (the kit's old step 3).
- **Snapshot / golden diff = `BLOCKED`** with an attribution; agents never regenerate fixtures.
- **`Found:`** in the report: bugs seen on the way are listed, never fixed inside the ticket.

**Ticket shape and measurement:**
- **`Fit:` line in Phase 1**, with a proposed split into lettered parts; the owner approves and the dispatcher edits the register; a fresh agent takes part a. Complements `ROTATE` (which still handles a misjudged fit).
- **Model per ticket** (§4.1, §9): mid tier for `Tests: none`, top tier for code and risk surfaces, shown to the owner.
- **Dispatcher mistakes asked, review tokens logged:** at every hand-over the dispatcher asks the owner one line about its own mistakes and logs the answer, "none" included (the kit's 11-24 table counted only mistakes the owner happened to volunteer); the `/code-review` run's `subagent_tokens` gets its own column (the legacy project's pilot review used 90K, invisible in the old log).
- **Dispatch log:** `docs/dispatch-log.md` (in `docs/`, not `docs/handoff/`: it is never consumed), with a Tickets table (one row per ticket) and a Runs table (one summary row per run, which is the run's report; no separate report file), created from `next-ticket/dispatch-log-template.md` (a template in the skill folder, because `install.py` has no create-only mode and a seeded log would conflict on every refresh).
- **Stage register** (`WORKFLOW.md` §2.1, new): fixed per-stage fields (ID, Dep, Branch, Status, Scope, Spec, Tests, Verify, Done when, Tickets, Done); `/next-ticket [<plan>] [<stage or ticket id>]` reads only the register notes and one stage block. A plan without a register still dispatches from the live handoff. *Not taken:* waiting for the project's extraction to finish (the 2026-11-21 plan).

**Git and settings:**
- **Name-based staging:** `git add -A` / `--all` / `.` / `-u` denied in `settings.json` and `.jsonc` (both tools), stated in `CLAUDE.md` and `WORKFLOW.md` §7.
- **Branch gate** and **leave-alone list** (`CLAUDE.md` "Don't Touch"): the clean-tree check ignores the owner's standing local changes instead of demanding a fully clean tree.
- **`Write(**)` / `MultiEdit(**)` removed** from the allow list: `Edit(**)` already covers every file tool, so they were redundant, not broken.
- **`git-guardrails` step 3b:** the owner chooses hook plus permission rules (default) or the hook alone, which makes the hook's firing observable in the main session and inside subagents. Also documented: a **known false positive** (a backslash-escaped double quote inside a bash double-quoted string ends the quote early for the splitter, so a quoted pattern containing a blocked git command can be blocked); left unfixed because the escape rules differ between bash and PowerShell.

**Practices:**
- **The dispatcher's named edit list** (register `Status:` lines and approved splits, the dispatch log, the handoff's `Mode:` line, `docs/kit-delta.md`, ratifications) replaces "never edits project files", which "go manual" already contradicted.
- **`docs/kit-delta.md`** (`WORKFLOW.md` §12): a project that adapts the kit keeps one dated line per difference, so carrying back starts from a list.

**Fix found while porting, affects the session picker:** `save_conversation.py list-sessions` counted only list-shaped user content, so a session whose prompts are stored as plain strings showed 0 turns and no preview, and it counted meta records (skill bodies) as turns. Now it counts both shapes, skips sidechain and meta records, and previews the first real prompt. The 2026-10-28 parser fix had covered the transcript body only.

- Touched: `.claude/agents/ticket-agent.md`, `.claude/skills/next-ticket/SKILL.md` and `dispatch-log-template.md` (new), `.claude/bin/save_conversation.py`, `.claude/settings.json`, `.claude/settings.jsonc`, `.claude/SETTINGS_NOTES.md`, `.claude/skills/git-guardrails/SKILL.md`, `CLAUDE.md`, `WORKFLOW.md` (§2.1 new, §4.1 diagram and text, §7, §9, §12), `docs/workflow-overview.html` (section 3), `README.md`, `install.py`.
- **Not verified:** any of the above in a kit install or a dispatch run under the kit's own files; the stage register with a plan that also uses milestones; `dispatch-log-template.md` creation by the dispatcher. The legacy project's next dispatch run is measured against the table below.

## 2026-11-24 — Dispatch mode verified in use; four fixes carried back

The 2026-10-27 entry left dispatch mode "not verified in the kit: an end-to-end dispatch run". It has since run a whole build in its source project (a Python + React greenfield app). That project's copy grew fixes the kit never got, so the copy that ran is newer than the kit's. The owner chose to port them now rather than wait for the legacy Java project's dispatch version announced on 2026-11-21 (owner, 2026-11-24: "Port now"). *Not taken:* record the evidence only and port later; wait and do both projects in one pass. That project's version merges on top of this one when it is done.

**Evidence from the source project** (saved ticket and dispatcher transcripts, 2026-10-28 to 2026-11-12):

| Measure | Result |
|---|---|
| Tickets run in dispatch mode | 47, over 10+ dispatcher sessions |
| Tickets that ran in two or more agent parts (rotation) | about 22; every hand-over resumed cleanly |
| `BLOCKED` reports, or an agent failing on a ticket | 0 |
| Builder never reviewing its own work | held: a dispatcher `/code-review` round on most risk-surface tickets |
| Ratifications written when made | held: one memory file per ticket |
| Stage-only | held: the owner asked the dispatcher to commit from a phone; the settings deny list refused, and the dispatcher did not work around it |
| Dispatcher mistakes caught by the owner | 1: a ticket off the handoff's critical path was skipped inside its milestone |
| Agent size (`subagent_tokens`) | before the budget rule, one agent ended at ≈422K; after it, the four largest recorded phases ended at 333K, 340K, 352K and 376K, none past the ≈400K rotation point |

**Fixes carried back:**
- **A ticket-agent's context budget** (owner, 2026-10-30, after the ≈422K agent: quality drops before the window fills and nothing bound agents to the 40 % rule). Two checks, both chosen: the agent stops at a safe point near the rotation point, leaves its work unstaged, writes a same-ticket handoff and returns the new status `ROTATE`; the dispatcher reads `subagent_tokens` before every resume and sends "Rotate" above about 300K. A fresh agent with the same description continues as "part <n>", so `save-agent` writes all parts into one transcript. *Not taken:* the dispatcher check only; the agent self-check only. Limit, now written down: the dispatcher check runs only between phases, so a long phase can finish past 300K (four did); the gap to 400K is the margin.
- **`/code-review` includes untracked files** at `REVIEW_NEEDED`: the agent has not staged yet, so a review of `HEAD` alone missed new files.
- **The whole-milestone check** (new; the rule was in the source project's memory only). Before each pass the dispatcher lists every open ticket of the current milestone whose dependencies are met, and asks when the handoff's pick would leave one behind. The skipped ticket left two commits without an issue number.
- **The dispatcher re-runs the whole Quality Bar** (new). It re-ran only the tests and took the agent's word for lint and format, and the transcripts say so repeatedly, against the skill's own "agent reports are claims" rule. It now runs every Quality Bar command, may leave a slow check (end-to-end, live calls) to the agent when the ticket did not touch that area, and the hand-over splits "run by me" from "reported by the agent".
- Touched: `.claude/agents/ticket-agent.md`, `.claude/skills/next-ticket/SKILL.md`, `WORKFLOW.md` §4.1 (diagram, "Who does what", the budget paragraph) and §8, `docs/workflow-overview.html` section 3.

**The `git-guardrails` hook in a second project** (the same day, the source project took the 2026-11-21 hook, stage-only, `Bash|PowerShell`; copied by hand from the skill, not through `install.py`):
- **Verified there:** the self-test (`failures 0`), the settings file still parsing, and a live block in the main session of `git -C . branch -D …`, a form the deny list cannot catch.
- **The skill's probe was wrong for stage-only projects, now fixed.** Step 5 said to probe with `git push --dry-run`. That project denies `git push` in its settings, and the permission check refused the command before the hook ran, so the probe proved nothing. The probe is now `git -C . branch -D guardrail-probe-does-not-exist`: no permission rule matches it, it does nothing when the hook is off, and it tests the `-C` parsing. *Not taken:* `git -C . push --dry-run` (contacts the remote if the hook is off).
- **`.gitignore` added to the kit** (`__pycache__/`, `*.pyc`): running the self-test leaves bytecode next to the scripts. `install.py` copies a fixed file list, so the bytecode never reached a project.
- Touched: `.claude/skills/git-guardrails/SKILL.md` (step 5), `.gitignore` (new).

**Still not verified:**
- **This kit copy, from a clean install:** `install.py` into an empty repo, a new session, `/next-ticket` on one small ticket (the agent file loads, the brief and report formats hold, `save-agent` finds the transcript).
- **Guards inside subagents:** that a ticket-agent is refused `git commit` by the deny list and by the `git-guardrails` hook. Only the dispatcher has been seen refused.
- **The paths never taken:** "go manual" in the middle of a run, and "an agent fails twice, offer manual mode".
- **A second project:** one project and one model family so far.
- **The two new fixes** have not run yet.
- **The overview page in a browser:** its diagrams were never opened after the 2026-10-27 change, and section 3's diagram changed again here.
- **The hook through a fresh `install.py` + `/git-guardrails`** (still open from 2026-11-21; the second project copied it by hand).

## 2026-11-21 — Two generic fixes carried back from the first long-running project

Came from a legacy Java project that ran on the kit for a month while it refactored and added rules from a spreadsheet. Only the changes that are not specific to that project were carried back; the owner chose the scope (2026-11-21: "update the kit with some of the improvements made here, provided they are generic rather than specific to [the project]"). Dispatch mode changes wait: the project builds its plan-parameter version first and the kit gets it once that project's extraction is done.

- **`git-guardrails` hook rewritten in Python** (`block-dangerous-git.py` plus a self-test, replacing the bash script). Three defects of the old script, found while installing it on a machine that has both the Bash and PowerShell tools: (1) it matched the text "git push" anywhere in the command, so `git -C repo push` and `git -c k=v push` were not blocked, while a commit message or `grep 'git push'` was; (2) the registered matcher was `Bash` only, so the same command through the PowerShell tool bypassed it; (3) it needed `jq`. The new script splits the command into segments, finds the git call, skips global options and checks the real subcommand (and looks inside `bash -c` / `powershell -Command`). It adds `COMMIT_POLICY` (`stage-only` default, matching the kit's own commit policy): under stage-only it also blocks commit, rebase, am, and cherry-pick / revert without `--no-commit`. The skill now asks the commit policy, registers `Bash|PowerShell`, runs the self-test, probes the live hook with `git push --dry-run`, and says plainly that subagents are not covered by that check. *Not taken:* keeping the bash script and patching its patterns (still a text search); blocking `merge` / `add` / `stash` by default (owners ask for those routinely; the lists are editable).
- **`/tdd` gains the other half: pin-first tests** (`tdd/pin-and-proof.md`, a section at the top of `SKILL.md`, wording in the description). The skill covered red-first only, which does not fit a refactor or extraction: there the tests must pass on day one against today's code and keep the behavior unchanged. The two kinds are now named (PIN green-first, PROOF red-first), chosen by the kind of work, never mixed in one step, with the rules for mixed work (pin the bug, fix it later as its own proof step) and a line each ticket or handoff declares. *Not taken:* a separate skill (the choice belongs at the start of the same decision); making pin-first the default (greenfield work is red-first).
- Touched: `.claude/skills/git-guardrails/SKILL.md` and `scripts/`, `.claude/skills/tdd/SKILL.md` and `pin-and-proof.md`, `.claude/skills/setup/skill.md` (extras wording), `install.py` (new files; the old script listed as retired), `README.md`, `WORKFLOW.md` §11.
- **Verified:** the hook self-test (20 always-blocked, 10 stage-only, 25 allowed cases, both policies, plus an end-to-end run through the JSON entry point) passes; the same logic runs in the source project, where a live probe in the main session was blocked.
- **Not verified in the kit:** a fresh install through `install.py` and `/git-guardrails`; that the hook also fires inside subagents (matters for dispatch mode, where agents run unattended).
- **Not carried back, on purpose** (specific to the source project): its handoff-skill changes (file naming, no archiving, reply-with-path), its `diagnosing-bugs` adaptations, its path-scoped rules file, and its testing-policy document (the generic part is now `pin-and-proof.md`).

## 2026-10-28 — A transcript per ticket

- **Every finished ticket saves its transcript** as `<ticket id> implementation` (owner, 2026-10-28: "on finishing each ticket, it must run the save-conversation skill with a slug "[ticket number] implementation""), staged with the ticket so it lands in the same commit. Manual mode: the session saves itself after `/handoff`; a ticket spanning sessions saves `… part <n>` because a re-saved slug replaces the file.
- **Dispatch mode saves the ticket-agent's own transcript**, not the dispatcher's session: "Can't it save the corresponding subagent sessions, which are the ones that actually implement each ticket? And then only save the "main" dispatch one once that has a filled up context window … and needs the user to start a new one." The dispatcher names each agent `<ticket id> ticket-agent` and saves its own session once, as `dispatch <first>-<last>`, when it ends. *Not taken:* a `--since` cut of the dispatcher's session per ticket; saving the whole dispatcher session at every ticket (overlapping files).
- **`save_conversation.py` gains `list-agents` and `save-agent`**, reading `<session>/subagents/agent-<id>.jsonl` and its `.meta.json` (sidechain records allowed; a `SubagentHandback` report rendered as the agent's reply; several runs with one description written as sections, so a restarted agent loses nothing).
- **Parser fix, affects every transcript:** user messages stored as a plain string were dropped, losing some real prompts and every slash command (e.g. `/model opus`, despite the documented compact rendering), and with them the assistant reply that preceded one. Re-rendering seven existing sessions: nothing removed, only those turns restored. Transcripts are now also written with LF on every OS (they came out CRLF on Windows).
- Touched: `.claude/bin/save_conversation.py`, `save-conversation/SKILL.md` ("At a ticket close"), `handoff/SKILL.md` (Finish), `next-ticket/SKILL.md`, `agents/ticket-agent.md`, `WORKFLOW.md` (§3, §4 diagram, §4.1, §5), the `CLAUDE.md` template, `README.md`, `docs/workflow-overview.html`.

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
