# Pin tests and proof tests

Two kinds of test, chosen by the kind of work, never by preference. Ported from a production project that refactored a large legacy codebase while also adding rules from a spreadsheet.

| | **PIN test (green first)** | **PROOF test (red first)** |
|---|---|---|
| Used for | Work that must leave results exactly as they are: refactor, extraction, move, rename, dead-code deletion, dependency swap, a speed-up with the same output | Work meant to change or add results: a new rule, a changed rule, a bug fix, logic from a spec or spreadsheet |
| Order | Write it against the current code. It passes on day one. Change the code. It must still pass. | Write it against the current code. It must fail. Change the code. It must pass. |
| Expected value comes from | What the current code produces (even if that is wrong) | A source outside the code: a spreadsheet cell, a dated decision by the owner, a documented rule |
| A failure means | The change altered behavior: a regression, or it needs a ruling | The code does not yet do what the source says |
| It proves | "Unchanged." Not "correct." | "Matches the source." |

The two never mix in one step. A refactor that finds a bug pins the bug and moves on; the fix is a later step with its own proof test.

## Choosing

1. Must results stay exactly as they are today? Yes: **PIN**.
2. No (new rule, changed rule, bug fix): is there a source for the expected value outside the code? Yes: **PROOF**. No: stop and ask the owner. Do not invent an expected value.
3. A bug fix is test-first only if a **correct seam** exists, meaning the test exercises the real bug pattern where it occurs. Races, threading and click-order bugs often have none. Then raise the reproduction rate (a stress loop) or record "no seam" in the handoff. A missing seam is a finding, not something to hide.

## PIN tests (green first)

1. Write the test against the current, unchanged code. Run it. It must be green.
2. **Prove it bites.** Break the rule on purpose, see a clear failure, revert. Restore reverted files with a new timestamp or some build tools keep the broken compiled class. A pin that cannot go red guards nothing.
3. Change the code.
4. Run the pins again. Green, with no edit to the tests or their expected values.

Rules:

- **Pin what the code does, at a seam.** Observable results (tables, files, bytes, names), not internals. A checksum of the whole result plus a few readable spot values, so a failure says what moved.
- **Build the pins one slice at a time.** Pin one case end to end and run it green before building the whole set. The first slice shows whether the test rig works at all while changing the plan is still cheap.
- **Run the real code**, not a copy of a rule inside a test harness.
- **Known wrong behavior is pinned as it is**, named or commented "known difference", and logged. Do not fix it inside the refactor.
- **Snapshots and golden files are pins.** A diff must be attributed to a specific change before anything is regenerated. A golden diff you cannot explain is a bug, not a stale baseline. During a refactor they do not change at all, or every change traces to a written decision.
- **Never** edit an expected value to get green. **Never** delete a pin during the refactor. Retiring old tests and replacing them with tests at the new interfaces is a separate decision for after the whole refactor.

## PROOF tests (red first)

1. **Name the source of the expected value** in the test (cell address, decision and date, or the document). No source, no test: ask.
2. Write the test with the expected value as a literal taken from that source.
3. Run it. It must fail, and **for the right reason**: it shows the value the source disagrees with, or the exact symptom of the bug. Keep the output for the handoff.
4. Write the least code that makes it pass.
5. Run it green. For a bug fix, also re-run the original reproduction.

Rules:

- **Never compute the expected value the way the code does**, and never copy it from the code's output. That test can only agree with the code.
- **Spreadsheet-derived logic:** the sheet is the source. Export scenarios from the sheet (what the sheet must show for each) into fixtures and compare the code to them. A rule that exists only in code is labeled code-only, not tested against the sheet.
- **After it passes, a proof test is also a pin.** From then on nobody edits its expected value without a new decision.
- **If a fix changes values that snapshots cover**, they fail by design: attribute the diff to the fix, then regenerate on purpose. This is the one place the two kinds meet.

## Mixed work

A refactor often uncovers a bug:

1. Finish the refactor with its pins green and unchanged. The bug stays, pinned as a "known difference".
2. Log it (and ask the owner if a decision is needed).
3. Fix it as its own step: a PROOF test that fails on the pinned behavior, the fix, then update that one pinned value on purpose with the decision named.

## Anti-patterns (both kinds)

| Anti-pattern | Why it fails | Instead |
|---|---|---|
| Expected value computed like the code, or pasted from its output, in a PROOF test | Passes by construction | A literal from the independent source |
| Reading a green snapshot as "correct" | Snapshots prove unchanged only | Say "unchanged"; use PROOF tests for "correct" |
| Regenerating a snapshot to get green | Bakes a regression into the baseline | Attribute the diff first |
| Fixing a bug inside a refactor step | The pins can no longer prove "unchanged" | Pin, log, fix later |
| A pin never seen failing | It may guard nothing | Do the bite check |
| Testing a copy of the rule | The real code can drift unseen | Drive the real code |
| Tests that leave shared state behind (singletons, static caches, session) | Later tests pass or fail by order | Set up and clear shared state inside the test |
| Inventing an expected value when the truth is the owner's call | Writes a guess into the suite | Ask, then write the PROOF test after the decision |

## What a ticket or handoff declares

State `Tests: PIN` or `Tests: PROOF` (or both, listed separately). For PIN: what is pinned, the command that showed it green before the change, and the bite check done. For PROOF: each test's source of expected value and the failing output seen before the fix. A dispatched ticket's plan lists these before any code is written, so the owner can correct a source up front.
