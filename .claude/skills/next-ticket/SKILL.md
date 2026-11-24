---
name: next-ticket
description: Dispatch mode (WORKFLOW.md §4.1). Run this session as a dispatcher that gives each ticket to a fresh ticket-agent: plan → the owner decides here → build → review → stage + handoff → the owner commits and replies "next" → the next ticket. Use when the owner says "/next-ticket", "dispatch", "switch to dispatch", or the live handoff says `Mode: dispatch`.
argument-hint: "Optional: the ticket id to start from (default: the live handoff's next ticket)"
---

Run this session as the **dispatcher**. Each ticket gets a fresh `ticket-agent` (`.claude/agents/ticket-agent.md`), so every ticket still starts from a clean context. The owner keeps every decision and every commit. This session only routes: it never reads the code and never edits project files. It reads the agents' reports, asks the owner, writes ratifications to auto-memory, saves transcripts, and checks git. That keeps its own context small enough to run many tickets.

## Start

1. Find the live handoff in `docs/handoff/` (not `archive/`). If there are several, or none, ask the owner which ticket to start from.
2. Check that git is clean: `git status` and `git log -1`. If anything is staged or modified, stop and ask the owner to commit it or say what it is. A ticket never starts on top of uncommitted work.
3. Read the next ticket's plan line. If its `Dep:` tickets aren't done, or it is marked blocked on the owner (⛔), stop and tell them why.
4. **Check the whole milestone, not only the handoff's pick.** List every open ticket of the current milestone whose `Dep:` tickets are done. A handoff often names the next ticket on the critical path, and a ticket off that path is easily skipped. If the handoff's ticket would leave one of these behind, ask the owner which runs first. Run this check before every pass, not only at the start.

## The loop (one ticket per pass)

1. **Plan.** Start the agent: `Agent(subagent_type: "ticket-agent", description: "<ticket id> ticket-agent", prompt: <brief>)`. The description is how its transcript is found later, so keep it exactly that. The brief contains:
   - the ticket id and the live handoff's path
   - "Phase 1 only: plan, no writes."
   - any ratification from earlier in this session that applies

   If `ticket-agent` isn't an available type (agent files load when a session starts), use `general-purpose` and start the brief with "Read `.claude/agents/ticket-agent.md` and follow it as your instructions." Wait for the completion notification. Never predict a report.
2. **Decide.** Show the owner the plan in a few lines: files, risk surfaces, dependencies. Ask its questions with `AskUserQuestion`, putting each alternative's explanation **inside its option**. When the owner answers, write each ratification to auto-memory immediately, in their words, dated, with the options not taken.
3. **Build.** `SendMessage` the same agent the owner's answers, any change they asked for, and "Approved: phase 2." Wait.

   **Budget check before every resume** (here, after `BLOCKED`, after `REVIEW_NEEDED`). The completion notification's usage shows the agent's `subagent_tokens`, a close stand-in for its context size. Above about **300K**, do not send the next phase. Send "Rotate" instead (the agent writes a same-ticket handoff and returns `ROTATE`), then handle it as below. This leaves room under the 40 % point (≈400K) for the phase that follows.
4. **Act on the report's status:**
   - `BLOCKED`: ask the owner as in step 2, send the answer, wait again.
   - `REVIEW_NEEDED`: run `/code-review` against `HEAD` here, in this session, so the builder never reviews its own work. Include the untracked files: the agent has not staged yet. Send the findings to the agent with "Fix, re-verify, then finalize." Wait.
   - `ROTATE`: the agent stopped mid-ticket at its budget, or because you sent "Rotate". Start a fresh agent with the **same** description, `<ticket id> ticket-agent`, so both runs land in one transcript. Its brief holds the same-ticket handoff's path, "part <n>", the phase to run, and everything that phase needs (the owner's answers, the review findings, "Approved: phase 2" if it was given). The tree is dirty by design here; do not apply the git-clean check. A rotation is not a failure.
   - `STAGED`: run `git status` to confirm what's staged, and nothing is left unstaged. Then **run every command in `CLAUDE.md`'s Quality Bar yourself**: tests, lint, format check, type check, and each package's or front end's own checks when the ticket staged files there. A slow check (end-to-end, live calls) may be left to the agent's report when the ticket did not touch its area; say so. Then save the agent's transcript and stage it with the ticket. Get this session's id from `python .claude/bin/save_conversation.py list-sessions`, then:

     ```bash
     python .claude/bin/save_conversation.py save-agent <session-id> "<ticket id> ticket-agent" "<ticket id> implementation"
     git add "<path the script printed>"
     ```

     See `/save-conversation`, "At a ticket close".
5. **Hand over.** Show the owner, briefly:
   - what changed
   - the verification lines, split into **run by you** and **reported by the agent, not re-run**
   - the handoff and transcript paths
   - the proposed commit message

   End with: "Commit and push, then reply **next** (or **stop** / **go manual**)."
6. **Next.** When the owner replies, check that `git log -1` shows a new commit and `git status` shows nothing staged. If not, say what is still there and wait. Then start the next pass from the new live handoff, with the milestone check (Start, step 4).

## Stop when

- The owner says stop.
- A milestone closes. Ask before starting the next milestone.
- The next ticket is blocked on the owner, or no next ticket exists.
- An agent fails twice on the same ticket. Report it, and offer manual mode with the same handoff.
- This session reaches about 40 % of the window. Tell the owner to open a new session. The live handoff already says `Mode: dispatch`, so the new session resumes the loop. The dispatcher writes no handoff of its own.

**Save this session once, when it ends.** Run `/save-conversation "dispatch <first ticket>-<last ticket>"` (e.g. `dispatch C0.2-C1.3`).
- **At the rotation point:** do it at the last hand-over, before the owner commits, and stage it with that ticket.
- **At any other stop:** stage it and ask the owner to commit it, so the next session starts on a clean tree.

## Switching modes

- **"Go manual":** finish or abandon the current pass as the owner says. Change the live handoff's `Mode:` line to `manual` (a one-line edit, then stage it) and stop dispatching. From then on, each session works its ticket itself (`WORKFLOW.md` §4).
- **Switching into dispatch from a manual session:** run this skill.

## Rules that carry

- Stage-only: agents stage, the owner commits. Never commit or push, and never tell an agent to.
- One ticket per agent. Never two agents on the same ticket at once (a rotated ticket's parts run one after the other), and never two tickets at once: commits and schema migrations are ordering points.
- The 40 % rotation point binds ticket-agents as well as this session: the agent watches itself, and you check `subagent_tokens` before every resume.
- Agents' reports are claims. `git status`, `git log` and your own run of the Quality Bar are the record.
