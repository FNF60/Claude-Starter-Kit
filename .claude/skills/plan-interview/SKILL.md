---
name: plan-interview
description: "Team up with the user to turn a rough idea into a comprehensive, refined plan through a relentless one-question-at-a-time interview — and capture it as a step-by-step plan (plus any domain terms/decisions that surface). Use when the user wants to plan or spec something before building, or says 'let's plan', 'plan something', 'ask me questions', 'interview me', 'grill me', or any similar 'plan'/'grill' trigger phrase."
---

# Plan Interview

Refine a plan or design **together** by interviewing the user relentlessly, one question at a time, until you both reach a shared understanding — then write it down as a plan they (or an implementer agent) can follow without re-asking.

## The interview

Interview the user about every aspect of the plan until you reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one by one. For each question, **provide your recommended answer**.

Ask questions **one at a time**, waiting for feedback on each before continuing. Asking multiple questions at once is bewildering.

If a question can be answered by exploring the codebase, **explore the codebase** instead of asking.

Do not start building until the user confirms you've reached a shared understanding.

## Sharpen the domain as you go

Run the `/domain-modeling` skill alongside the interview so the project's language and hard decisions stay current as they surface:

- When a term is fuzzy or overloaded (one word doing three jobs), sharpen it and record it in `CONTEXT.md` — create the file lazily, only once there's something to write.
- When a hard-to-reverse decision lands, offer to record it as an ADR in `docs/adr/`, framed as: *"Want me to record this as an ADR so it doesn't get re-litigated later?"*

## The output: a written plan

Once the interview reaches shared understanding, **write the result down** so it can be acted on — this written plan is the deliverable of the skill, not the implementation:

- At minimum, a **step-by-step plan**: an ordered list of concrete steps to implement, each specific enough that an implementer agent could follow it without asking a single question. Include what's being built, the sequence, and any decisions/constraints resolved during the interview.
- Where the conversation produced them, also leave the domain artifacts from the `/domain-modeling` pass (`CONTEXT.md` entries, ADRs).
- **A stage register** (`WORKFLOW.md` §2.1) at the end of the plan whenever it has more than one ticket. It is what `/next-ticket` reads, and it keeps a manual run honest too. Group the steps into stages (dependency-ordered, each with a one-line goal) and tickets (`<stage>-<n>`, one focused commit each), then write one `### <stage id> <title>` block per stage with the fixed fields: ID, Dep, Branch, Status (`not started`), Scope (In / Out), Spec (pointers only), Tests, Verify, Done when, Tickets, Done (empty). Fill them from the interview:
  - **Tests** per ticket, by the kind of work (`/tdd`, pin-and-proof): refactor, move or delete → PIN; new rule or bug fix → PROOF; docs, design or measurement → `none`. Never PIN and PROOF in one ticket.
  - **Done when**: checkable conditions only (a test passes, a command's output, a file exists), never "works well".
  - **Size**: a ticket a fresh agent can plan and build inside about 40 % of its window. When unsure, split it now.
  - **Branch** and anything else the interview did not settle are questions: ask them like any other, one at a time, with your recommendation. Far-off stages may mark their tickets *provisional*, to be re-cut when the stage starts.
  - Add the register's notes above the first block: what "Spec" pointers refer to, where the Quality Bar lives, and that sizes are a first cut.

Save the plan where the project keeps planning docs (e.g. `docs/` or `.scratch/`); if there's no obvious home, ask the user where they want it. State the path when you're done.

## Close: choose how the plan will run

When the plan is written, ask the owner which mode to run it in (`WORKFLOW.md` §4.1), with each explanation inside its option:

- **Manual** — one session per ticket, as before: the owner opens each session from its handoff.
- **Dispatch** — one session runs `/next-ticket` and gives each ticket to a fresh agent; the owner answers questions, approves plans and commits in that one session, and replies "next" between tickets.

Record the answer in the `Mode:` line of the handoff that closes this session (or, if none is written, in auto-memory). For dispatch, also give the exact start line: `/next-ticket <plan path> <first stage id>`. The owner can switch later at any time by asking.

## Key rules

- **One question at a time**, each with your recommended answer.
- **Explore before you ask** — answer your own questions from the codebase where you can.
- **Nothing is settled while an open question remains** — grill until the plan is complete.
- **Don't enact the plan until the user confirms.** The deliverable is the shared understanding and the written step-by-step plan, not the code.
