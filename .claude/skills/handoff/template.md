# Handoff template

The shape of every handoff. Keep the section order; drop a section only when it is truly empty and say so in one line ("No ratifications this ticket."). Replace every `<…>`. Reference other artifacts by path; never paste what the plan, a commit, a diff or an ADR already records.

---

# Handoff — <ticket just finished> complete (<staged | committed>) → next: <next ticket, or topic>

**Date:** <YYYY-MM-DD> · **Repo:** `<remote>` · **Branch:** `<branch>` · **Version:** <from the project's version file, if any>
**Issue:** <#id and title, read off the tracker this session — or "not read: look it up before writing a `Closes` line; never infer it">

## State

<Two to four sentences. What is done. Staged or committed. Migration / env var / dependency added, or "none of the three". Anything the owner must do before the next ticket can start.>

### Ratifications (<owner>, <date>)

<Numbered. One per decision the owner made this session, in the words used, with the options not taken. "Stated as defaults and not objected to" is a separate line, never mixed in. If none: "No ratifications this ticket.">

### What landed

<Bulleted by area. Every bullet names its file paths. Describe the shape, not the diff.>

### Verification record

<Facts only. A row is written from a command run in THIS session; anything else goes under "Not verified".>

| Check | Command | Result |
|---|---|---|
| HEAD | `git rev-parse --short HEAD` | `<sha>` (<n> files staged, +<a>/−<d>) |
| Typecheck | `<typecheck command>` | <clean / N errors> |
| Lint | `<lint command>` | <0 errors, N warnings (baseline N)> |
| Format | `<format check command>` | <clean> |
| Unit | `<test command>` | <N/N> |
| <project gate> | `<command>` | <result, or "not run — why"> |
| Build | `<build command>` | <ok, or "not run — why"> |

<Manual checks, each with how it was done and on which code (final or earlier).>

**Not verified:** <everything the next session must not assume: deployment, dark mode, phone width, a path that only exists in principle, a flaky first run. If a run failed once and passed on retry, say so here.>

### Review outcomes (`/code-review`, both axes)

**Fixed in the diff:** <bullets>
**Left as is, on purpose:** <bullets, each with the reason — these are decisions the next session must not reopen>

### Dead ends and refusals

<What was tried and abandoned, and why. What the owner refused, in their words. What was blocked (permission, tool, missing key) and how it was worked around. A fresh session retries anything not written here.>

## Next session: <ticket> — <title>

> **Before acting on anything in this file:** run `git status`, `git log -1`, and `<test command>`. This file is a claim about the repo; the repo is the record. Where they disagree, the repo wins and this file gets corrected.
>
> **Ask the user clarification questions whenever you are not sure of something or an open decision comes up, and explain the alternatives in simple terms.**

<Scope in two to five bullets. Point to the plan line, the spec sections (by offset, never whole-file when large), the `CLAUDE.md` conventions and the `.claude/rules/<area>.md` files that apply, and the open questions to put to the owner before building.>

### Rules that carry

<Short bullets. One ticket per session; the commit policy; prompt the owner for the commit message; anything ticket-specific.>

### Suggested skills

<Optional. `/code-review` before staging a risk-surface change, `/tdd` for engine work, … Omit the section if nothing beyond the defaults applies.>

## Pending on the owner's plate

<Bulleted, verified this session or marked "carried, not re-verified". Deploys, env vars, board moves, external items.>
