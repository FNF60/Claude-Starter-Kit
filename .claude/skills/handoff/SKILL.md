---
name: handoff
description: Write the handoff document that lets a fresh session continue the work — when the task continues in a new session (context budget near) or when a ticket is done and a clear next ticket exists. Uses template.md in this folder; also archives the handoff this session started from.
argument-hint: "What will the next session be used for?"
---

Write a handoff so a fresh agent with an empty context can continue. The handoff is the session-close step: there is no separate wrap-up.

## When

Exactly two cases write one unprompted (`WORKFLOW.md` §4):

- **The same task continues in a new session** because this one has filled up (the rotation point — about 40 % of the model's window). The handoff states exactly where the work stopped.
- **The task is done and a clear next step exists** — the next ticket in plan order. Say in the recap that you wrote it.

A finished topic with no successor gets **no handoff**: archive the one this session started from (below), put any loose fact in auto-memory, and stop. Never invent a next session (a review the owner is doing live is not one).

The owner can also ask for one; their arguments describe what the next session will focus on — tailor the "Next session" section to them.

**In dispatch mode** (`WORKFLOW.md` §4.1) the `ticket-agent` writes the case-2 handoff when it finishes its ticket; the dispatcher session writes none of its own, because the live ticket handoff already carries `Mode: dispatch`.

## Where and how to name

- Save under `docs/handoff/` in the repo root. Never outside the project — a fresh session must find it.
- Name the file after the ticket the next session will implement, not the one just finished: finishing T0.3 with T0.4 next produces `HANDOFF-T0.4.md`. Several parallel tickets → the primary one. No ticket → a short topic slug, `HANDOFF-<topic>.md`.

## Shape

- **Follow `template.md` in this folder.** It is the template of record; do not model the file on a previous handoff.
- Reference, never duplicate: PRDs, plan lines, ADRs, issues, commits and diffs are cited by path, URL or SHA.
- **Verification record is facts only.** A row comes from a command run in this session. Anything not re-run is listed under "Not verified", never asserted. If something failed once and passed on retry, say so.
- **Carry the mode.** Fill the header's `Mode:` line (`manual` or `dispatch`, `WORKFLOW.md` §4.1): copy it from the handoff this session started from, unless the owner switched this session; a `ticket-agent` always writes `dispatch`. If no mode was ever chosen, ask the owner rather than default.
- Ratifications are the owner's words, dated, with the options not taken.
- **"Dead ends and refusals" is mandatory.** The next session retries anything not written there.
- The "Next session" section opens with the template's distrust clause (the repo is the record, the file is a claim) and the clarification line.
- Redact secrets, keys and personal data. Issue ids are read off the tracker, never inferred — a wrong id can auto-close an unrelated issue.

## Archive the consumed handoff

`docs/handoff/` holds only live handoffs. When you write the new one, move the handoff this session started from into `docs/handoff/archive/` with `git mv`, then repoint any live reference to it:

```bash
grep -rn "docs/handoff/HANDOFF-<name>.md" --include="*.md" . | grep -v node_modules | grep -v "docs/handoff/"
```

Edit those paths to `docs/handoff/archive/…`. Files already inside `docs/handoff/archive/` and saved transcripts are history: leave them as written.

## Finish

Stage the new file, the move and the repointed references. Committing follows the project's commit policy in `CLAUDE.md` (the kit default is stage-only: prompt the owner with a proposed message). State in the recap that the handoff was written and which file was archived.
