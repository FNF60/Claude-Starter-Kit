# Dispatch log

The lasting record of how dispatch mode runs in this project (`WORKFLOW.md` §4.1), kept so runs can be compared and the workflow improved. Two tables: **Tickets** (one row per ticket) and **Runs** (one summary row per dispatcher run, which is the run's report). The dispatcher fills the factual columns; the owner fills the judgment columns (Avoidable, Rework, Hand fixes) and reviews each Runs row. Newest at the bottom. Created by `/next-ticket` from `.claude/skills/next-ticket/dispatch-log-template.md` when missing; it lives in `docs/`, not `docs/handoff/`, because it is never consumed.

| Column | Meaning |
|---|---|
| Ticket | id, date |
| Models | dispatcher and agent |
| Phase 1 questions | how many the agent returned |
| Avoidable | how many the owner marks as "the agent could have decided this" |
| Mid-build blocks | how many times the agent stopped with a new question |
| Parts | how many agent runs the ticket took (rotations, approved splits) |
| Review findings | fixed / dropped, with a word on each dropped one |
| Rework | rounds of changes after the owner looked at the result |
| Tripwires | test count different from baseline + added; snapshot diffs and their attribution |
| Handoff vs repo | did the distrust check find the handoff or register wrong, and how |
| Hand fixes | what the owner corrected by hand afterwards |
| Tokens | the agent's last `subagent_tokens` per phase |
| Review tokens | `subagent_tokens` of the `/code-review` run(s) for the ticket |
| Notes | dispatcher mistakes the owner named when asked at the hand-over ("Dispatcher mistake: …", or "none"), guard refusals, anything that surprised anyone |

## Tickets

| Ticket | Models | Phase 1 questions | Avoidable | Mid-build blocks | Parts | Review findings | Rework | Tripwires | Handoff vs repo | Hand fixes | Tokens | Review tokens | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Runs

| Column | Meaning |
|---|---|
| Run | tickets covered, dates, dispatcher session(s) |
| Tickets | how many ran |
| Multi-part | tickets that took two or more agent runs (rotations, approved splits) |
| Blocked / failed | `BLOCKED` reports; agents that failed on a ticket |
| Dispatcher mistakes | how many the owner named, with the kinds |
| Peak tokens | highest agent and review `subagent_tokens`; whether "Rotate" was sent |
| Guards | stage-only held; hook refusals seen; name-based staging held |
| Notes | anything to change in the workflow |

| Run | Tickets | Multi-part | Blocked / failed | Dispatcher mistakes | Peak tokens | Guards | Notes |
|---|---|---|---|---|---|---|---|
