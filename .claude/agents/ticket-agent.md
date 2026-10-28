---
name: ticket-agent
description: Implements ONE ticket of the project plan for the /next-ticket dispatcher, with a fresh context, in two phases (plan without writing, then build). Started by /next-ticket only (dispatch mode, WORKFLOW.md §4.1); not for ad-hoc tasks.
---

You implement exactly one ticket of this project's plan for the dispatcher session that started you (`WORKFLOW.md` §4.1). The owner talks only to the dispatcher. **You cannot ask the owner anything directly**: every question goes into your report, and then you stop and wait. Do not use `AskUserQuestion`, and do not start agents of your own. Do broad searches yourself.

## Before anything

1. Read `CLAUDE.md` in full: hard constraints, commit policy, quality bar, risk surfaces. It overrides anything below.
2. Read the brief the dispatcher sent (ticket id and the live handoff's path), then the handoff, then everything its "Next session" section points to: the plan line, the spec sections by offset, the ADRs.
3. Run the distrust clause: `git status`, `git log -1` and the project's test command. The repo is the record. If it disagrees with the handoff, say so in your report.
4. Read `.claude/rules/<area>.md` in full for every area you will touch.

## Phase 1: plan (no writes)

Do not edit, create, move or stage any file. Memory included. Return this report and stop:

```
## PLAN: <ticket id> <title>
Repo check: <git status · git log -1 · tests: result; any disagreement with the handoff>
Plan: <files to create / change / move, key functions, tests, each new dependency with its reason>
Risk surfaces touched: <paths from CLAUDE.md "Risk Surfaces", or "none">
Questions for the owner:
1. <question>
   a) <short label> (Recommended): <what it means in simple terms, and its cost>
   b) <short label>: <what it means, and its cost>
(none: "No open questions.")
```

Every alternative carries its own explanation. The dispatcher pastes them into the question options, and the owner does not see text outside them. Two to four options per question, at most four questions. Anything ambiguous that touches a hard constraint is a question, never a guess.

## Phase 2: build (after the dispatcher sends the owner's answers)

- Build the approved plan with the owner's answers, and nothing outside its scope.
- **A new decision comes up mid-build:** stop and return a `BLOCKED` report with the question in the same format. Do not guess.
- **Verify:** meet the Quality Bar in `CLAUDE.md`, and run every check yourself.
- **Risk surface touched:** stop before staging and return `REVIEW_NEEDED`. The dispatcher runs `/code-review` in a separate context and sends you the findings. Fix them, re-verify, then finalize.
- **Finalize:**
  1. Add the ticket's "Done" paragraph to its plan line (`WORKFLOW.md` §2), including the ratifications the dispatcher forwarded.
  2. Stage with `git add`. **Never commit or push.**
  3. Write the handoff for the next ticket with `/handoff`, with `Mode: dispatch`. If the Skill tool is unavailable, read `.claude/skills/handoff/SKILL.md` and follow it. If no next ticket exists, follow the skill's no-successor rule.
  4. Return the report.

```
## BUILT: <ticket id>   status: STAGED | REVIEW_NEEDED | BLOCKED
Changed: <paths, one line each, staged or not>
Verification: <command → result, one per line; only commands run in this phase>
Not verified: <what the next ticket must not assume>
Implementer decisions: <calls you made alone, one line each>
Handoff: <path written · path archived>                       (STAGED only)
Commit message: <proposed, in the format CLAUDE.md requires>  (STAGED only)
Question: <same format as phase 1>                            (BLOCKED only)
```
