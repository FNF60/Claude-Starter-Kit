---
name: next-ticket
description: Dispatch mode (WORKFLOW.md §4.1). Run this session as a dispatcher that gives each ticket to a fresh ticket-agent: plan → the owner decides here → build → review → stage + handoff → the owner commits and replies "next" → the next ticket. Use when the owner says "/next-ticket", "dispatch", "switch to dispatch", or the live handoff says `Mode: dispatch`.
argument-hint: "[<plan path>] [<stage or ticket id>] (default: the plan's stage register, else the live handoff's next ticket)"
---

Run this session as the **dispatcher**. Each ticket gets a fresh `ticket-agent` (`.claude/agents/ticket-agent.md`), so every ticket still starts from a clean context. The owner keeps every decision and every commit. This session only routes. It never reads or edits code. It reads the plan's register (or the live handoff), the agents' reports and git; it asks the owner; it saves transcripts. That keeps its own context small enough to run many tickets.

**Files this session may edit, and nothing else:**
- the plan's stage register: `Status:` lines, and a ticket split the owner approved
- `docs/dispatch-log.md`: one Tickets row per ticket, one Runs row per run
- the live handoff's `Mode:` line ("go manual")
- `docs/kit-delta.md`, when the project's dispatch workflow itself changes (`WORKFLOW.md` §12)
- auto-memory: ratifications (or the project's rulings log, if `CLAUDE.md` names one)

## Arguments

`[<plan path>] [<id>]`. If the plan has a **stage register** (`WORKFLOW.md` §2.1), the id is a stage (`S2`) or a ticket (`S2-3`); a stage id means its first ticket with no **Done** mark. Read only what you need: the register's notes and the one stage block (find its `### <id>` heading, then read by offset). Never read the whole plan. Without a register, the live handoff in `docs/handoff/` (not `archive/`) names the next ticket; if there are several, or none, ask the owner.

## Start (before every pass)

1. **Ticket.** Find the ticket line. It is done when it carries a **Done <date>** paragraph.
2. **Gates.** Stop and tell the owner why if any of these fail:
   - the ticket's (or its stage's) `Dep:` are not done, or it is marked blocked on the owner (⛔)
   - **branch:** `git branch --show-current` is not the stage's `Branch:` (when the register names one). The owner creates branches: ask, then check again
   - **clean tree:** `git status --short` shows anything staged, or anything modified outside the **leave-alone list** in `CLAUDE.md` ("Don't Touch" → leave-alone files: the owner's standing local changes). Ask what it is. A ticket never starts on top of unexplained changes
3. **Check the whole milestone (or stage), not only the pick.** List every open ticket of the current milestone or stage whose `Dep:` are done. A handoff often names the next ticket on the critical path, and a ticket off that path is easily skipped. If the pick would leave one behind, ask the owner which runs first.
4. **Status.** At a stage's first ticket, set its `Status:` to `in progress`.
5. **Model.** Pick the agent's model (`WORKFLOW.md` §9): the mid tier for docs-only tickets (`Tests: none`), the top tier for anything touching code or a risk surface. Tell the owner in one line; they may override.

## The loop (one ticket per pass)

1. **Plan.** Start the agent: `Agent(subagent_type: "ticket-agent", model: <pick>, description: "<ticket id> ticket-agent", prompt: <brief>)`. The description is how its transcript is found later, so keep it exactly that. The brief contains:
   - the ticket id, and the plan path and stage id, or the live handoff's path
   - "Phase 1 only: plan, no writes. Do not run the test suite."
   - any ratification from earlier in this session that applies

   Meanwhile, run the Quality Bar's test command yourself, in the background, as the baseline (agents and you never run the suite at the same time: shared build output). If `ticket-agent` isn't an available type (agent files load when a session starts), use `general-purpose` and start the brief with "Read `.claude/agents/ticket-agent.md` and follow it as your instructions." Wait for the completion notification. Never predict a report.
2. **Decide.** Show the owner the plan in a few lines: files, risk surfaces, test kind, dependencies. Then:
   - **Split proposed** (the agent's `Fit:` says the ticket will not fit its budget): show the parts (`S2-3a`, `S2-3b`, each with scope, test kind, Done when). If the owner approves, edit the register, then start a fresh agent on the first part. The agent that proposed the split is not resumed.
   - **Questions:** ask with `AskUserQuestion`, putting each alternative's explanation **inside its option**. When the owner answers, write each ratification immediately, in their words, dated, with the options not taken. Say where you wrote it.
3. **Build.** `SendMessage` the same agent the owner's answers, any change they asked for, and "Approved: phase 2." For a ticket whose test kind is not `none`, or that touches a risk surface, add: "Return REVIEW_NEEDED before staging." Wait.

   **Budget check before every resume** (here, after `BLOCKED`, after `REVIEW_NEEDED`). The completion notification's usage shows the agent's `subagent_tokens`, a close stand-in for its context size. Above about **300K**, do not send the next phase. Send "Rotate" instead (the agent writes a same-ticket handoff and returns `ROTATE`), then handle it as below. This leaves room under the 40 % point (≈400K) for the phase that follows.
4. **Act on the report's status:**
   - `BLOCKED`: ask the owner as in step 2, send the answer, wait again. A snapshot or golden diff always comes back as `BLOCKED`, with the agent's attribution: show the owner the diff; agents never regenerate fixtures.
   - `REVIEW_NEEDED`: run `/code-review` here, in this session, so the builder never reviews its own work. Review the working-tree diff **and the untracked files**: the agent has not staged yet, so a new file is not in the diff (list them with `git status --short --untracked-files=all`, minus the leave-alone list). Judge findings against the ticket's Done when and scope. Send the rest to the agent with "Fix, re-verify, then finalize." Wait.
   - `ROTATE`: the agent stopped mid-ticket at its budget, or because you sent "Rotate". Start a fresh agent with the **same** description, `<ticket id> ticket-agent`, so both runs land in one transcript. Its brief holds the same-ticket handoff's path, "part <n>", the phase to run, and everything that phase needs (the owner's answers, the review findings, "Approved: phase 2" if it was given). The tree is dirty by design here; do not apply the clean-tree gate. A rotation is not a failure.
   - `STAGED`: go to step 5.
5. **Check.** Agent reports are claims; git and your own run are the record.
   - `git diff --cached --name-only` matches the report's `Changed:` list; nothing is left unstaged; nothing from the leave-alone list is staged.
   - **Run every command in `CLAUDE.md`'s Quality Bar yourself**: tests, lint, format check, type check, and each package's or front end's own checks when the ticket staged files there. A slow check (end-to-end, live calls) may be left to the agent's report when the ticket did not touch its area; say so. A test count different from the baseline plus the tests the ticket added is a tripwire: tell the owner, do not explain it away.
   - Snapshot / golden fixtures show no change, unless the owner approved one.
   - Save the agent's transcript and stage it with the ticket. Get this session's id from `python .claude/bin/save_conversation.py list-sessions` (several sessions may be live; pick by preview), then:

     ```bash
     python .claude/bin/save_conversation.py save-agent <session-id> "<ticket id> ticket-agent" "<ticket id> implementation"
     git add "<path the script printed>"
     ```

     See `/save-conversation`, "At a ticket close".
6. **Log.** Add the ticket's row to the Tickets table of `docs/dispatch-log.md` (if it does not exist, create it from `dispatch-log-template.md` in this skill's folder). Fill the factual columns, including the agent's `subagent_tokens` per phase and the `/code-review` run's `subagent_tokens` (from its completion notification); leave the judgment columns for the owner.
7. **Hand over.** Show the owner, briefly:
   - what changed
   - the verification lines, split into **run by me** and **reported by the agent, not re-run**
   - the handoff and transcript paths
   - the proposed commit message

   Then ask one line: "Any dispatcher mistakes on this ticket (wrong file, skipped check, wrong status, mis-read report)?" Log each one the owner names in the row's Notes as "Dispatcher mistake: …"; log "none" too, so a zero means "asked, none", not "never asked". End with: "Commit and push, then reply **next** (or **stop** / **go manual**)."
8. **Next.** When the owner replies, check that `git log -1` shows a new commit and `git status` shows nothing staged. If not, say what is still there and wait. When a stage's last ticket closes, set its `Status:` to `done <date>`. Then start the next pass at Start.

## Stop when

- The owner says stop.
- A milestone or stage closes. Ask before starting the next one.
- The next ticket is blocked on the owner, or no next ticket exists.
- An agent fails twice on the same ticket. Report it, and offer manual mode with the same handoff.
- This session reaches about 40 % of the window. Tell the owner to open a new session and run `/next-ticket` again (with the same plan and stage, when there is a register). The register, or the live handoff's `Mode: dispatch`, carries the state. The dispatcher writes no handoff of its own.

**When the run ends,** write the run's row in the Runs table of `docs/dispatch-log.md` (from the Tickets rows; it is the run's report, no separate file) and ask the owner to review it.

**Save this session once, when it ends.** Run `/save-conversation "dispatch <first ticket>-<last ticket>"` (e.g. `dispatch C0.2-C1.3`).
- **At the rotation point:** do it at the last hand-over, before the owner commits, and stage it with that ticket.
- **At any other stop:** stage it and ask the owner to commit it, so the next session starts on a clean tree.

## Switching modes

- **"Go manual":** finish or abandon the current pass as the owner says. Change the next handoff's `Mode:` line to `manual` (a one-line edit, then stage it) and stop dispatching. From then on, each session works its ticket itself (`WORKFLOW.md` §4).
- **Switching into dispatch from a manual session:** run this skill.

## Rules that carry

- Stage-only: agents stage, the owner commits. Never commit or push, and never tell an agent to. Agents stage named paths only; never `git add -A`, `--all`, `.` or `-u`.
- One ticket per agent. Never two agents on the same ticket at once (a rotated ticket's parts run one after the other), and never two tickets at once: commits, schema migrations and shared build output are ordering points.
- The 40 % rotation point binds ticket-agents as well as this session: the agent watches itself, and you check `subagent_tokens` before every resume.
- Agents' reports are claims. `git status`, `git log` and your own run of the Quality Bar are the record.
