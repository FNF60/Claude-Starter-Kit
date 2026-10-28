---
name: next-ticket
description: Dispatch mode (WORKFLOW.md §4.1). Run this session as a dispatcher that gives each ticket to a fresh ticket-agent: plan → the owner decides here → build → review → stage + handoff → the owner commits and replies "next" → the next ticket. Use when the owner says "/next-ticket", "dispatch", "switch to dispatch", or the live handoff says `Mode: dispatch`.
argument-hint: "Optional: the ticket id to start from (default: the live handoff's next ticket)"
---

Run this session as the **dispatcher**. Each ticket gets a fresh `ticket-agent` (`.claude/agents/ticket-agent.md`), so every ticket still starts from a clean context. The owner keeps every decision and every commit. This session only routes: it never reads the code and never edits project files. It reads the agents' reports, asks the owner, writes ratifications to auto-memory, and checks git. That keeps its own context small enough to run many tickets.

## Start

1. Find the live handoff in `docs/handoff/` (not `archive/`). If there are several, or none, ask the owner which ticket to start from.
2. Check that git is clean: `git status` and `git log -1`. If anything is staged or modified, stop and ask the owner to commit it or say what it is. A ticket never starts on top of uncommitted work.
3. Read the next ticket's plan line. If its `Dep:` tickets aren't done, or it is marked blocked on the owner (⛔), stop and tell them why.

## The loop (one ticket per pass)

1. **Plan.** Start the agent: `Agent(subagent_type: "ticket-agent", prompt: <brief>)`. The brief contains:
   - the ticket id and the live handoff's path
   - "Phase 1 only: plan, no writes."
   - any ratification from earlier in this session that applies

   If `ticket-agent` isn't an available type (agent files load when a session starts), use `general-purpose` and start the brief with "Read `.claude/agents/ticket-agent.md` and follow it as your instructions." Wait for the completion notification. Never predict a report.
2. **Decide.** Show the owner the plan in a few lines: files, risk surfaces, dependencies. Ask its questions with `AskUserQuestion`, putting each alternative's explanation **inside its option**. When the owner answers, write each ratification to auto-memory immediately, in their words, dated, with the options not taken.
3. **Build.** `SendMessage` the same agent the owner's answers, any change they asked for, and "Approved: phase 2." Wait.
4. **Act on the report's status:**
   - `BLOCKED`: ask the owner as in step 2, send the answer, wait again.
   - `REVIEW_NEEDED`: run `/code-review` against `HEAD` here, in this session, so the builder never reviews its own work. Send the findings to the agent with "Fix, re-verify, then finalize." Wait.
   - `STAGED`: run `git status` to confirm what's staged, and run the test command once yourself.
5. **Hand over.** Show the owner, briefly:
   - what changed
   - the verification lines
   - the handoff path
   - the proposed commit message

   End with: "Commit and push, then reply **next** (or **stop** / **go manual**)."
6. **Next.** When the owner replies, check that `git log -1` shows a new commit and `git status` shows nothing staged. If not, say what is still there and wait. Then start the next pass from the new live handoff.

## Stop when

- The owner says stop.
- A milestone closes. Ask before starting the next milestone.
- The next ticket is blocked on the owner, or no next ticket exists.
- An agent fails twice on the same ticket. Report it, and offer manual mode with the same handoff.
- This session reaches about 40 % of the window. Tell the owner to open a new session. The live handoff already says `Mode: dispatch`, so the new session resumes the loop. The dispatcher writes no handoff of its own.

## Switching modes

- **"Go manual":** finish or abandon the current pass as the owner says. Change the live handoff's `Mode:` line to `manual` (a one-line edit, then stage it) and stop dispatching. From then on, each session works its ticket itself (`WORKFLOW.md` §4).
- **Switching into dispatch from a manual session:** run this skill.

## Rules that carry

- Stage-only: agents stage, the owner commits. Never commit or push, and never tell an agent to.
- One ticket per agent. Never two agents on the same ticket, and never two tickets at once: commits and schema migrations are ordering points.
- Agents' reports are claims. `git status`, `git log` and the test run are the record.
