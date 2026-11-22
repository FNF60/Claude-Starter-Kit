---
name: tdd
description: Test-driven development, and its counterpart for refactors. Use when the user wants to build features or fix bugs test-first, mentions "red-green-refactor", wants integration tests, or is about to refactor, extract or move code and needs tests that pin today's behavior first (characterization / golden-master / snapshot tests).
---

# Test-Driven Development

TDD is the red → green loop. This skill is the reference that makes that loop produce tests worth keeping: what a good test is, where tests go, the anti-patterns, and the rules of the loop. Every section applies on every cycle — consult them before and during the loop, not after.

## Which kind of test is this work?

There are two kinds, and the kind of work decides which one you write. Decide this first.

| Work | Kind | Order | Expected value comes from |
|---|---|---|---|
| New behavior, a changed rule, a bug fix, logic taken from a spec or spreadsheet | **PROOF** (red first) | Write it, watch it fail, change the code, watch it pass | A source outside the code |
| Refactor, extraction, move, rename, dead-code deletion, dependency swap | **PIN** (green first) | Write it against today's code, watch it pass, prove it can fail, change the code, it must still pass | What today's code produces, right or wrong |

The red → green loop and everything below it is the **PROOF** loop. For the PIN loop, the rules for mixed work, and the anti-patterns of both kinds, read [pin-and-proof.md](pin-and-proof.md). Never mix the two in one step: a refactor that finds a bug pins the bug and fixes it later as its own proof step.

When exploring the codebase, read `CONTEXT.md` (if it exists) so test names and interface vocabulary match the project's domain language, and respect ADRs in the area you're touching.

## What a good test is

Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification — "user can checkout with valid cart" tells you exactly what capability exists — and survives refactors because it doesn't care about internal structure.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

## Seams — where tests go

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

**Test only at pre-agreed seams.** Before writing any test, write down the seams under test and confirm them with the user. No test is written at an unconfirmed seam. You can't test everything — agreeing the seams up front is how testing effort lands on the critical paths and complex logic instead of every edge case.

Ask: "What's the public interface, and which seams should we test?"

## Anti-patterns

- **Implementation-coupled** — mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks when you refactor but behavior hasn't changed.
- **Tautological** — the assertion recomputes the expected value the way the code does (`expect(add(a, b)).toBe(a + b)`, a snapshot derived by hand the same way, a constant asserted equal to itself), so it passes by construction and can never disagree with the code. Expected values must come from an independent source of truth — a known-good literal, a worked example, the spec.
- **Horizontal slicing** — writing all tests first, then all implementation. Bulk tests verify _imagined_ behavior: you test the _shape_ of things rather than user-facing behavior, the tests go insensitive to real changes, and you commit to test structure before understanding the implementation. Work in **vertical slices** instead — one test → one implementation → repeat, each test a **tracer bullet** that responds to what the last cycle taught you.

## Rules of the loop

- **Red before green.** Write the failing test first, then only enough code to pass it. Don't anticipate future tests or add speculative features.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Refactoring is not part of the loop.** It belongs to the review stage (see the `code-review` skill), not the red → green implementation cycle.
