---
name: diff
description: "TRIGGER when user asks 'what changed', 'show me the diff', 'review changes', or wants to see what was modified. Groups changes by file/module, flags risk level using CLAUDE.md Risk Surfaces and Don't Touch lists, summarizes impact."
argument-hint: "[ref]"
---

# Diff: $ARGUMENTS

Smart code diff tool. Shows what changed and assesses risk level using **this project's** Risk Surfaces and Don't Touch list — not a generic hardcoded list.

## Parameters

- No args: Diff HEAD (latest commit) vs working directory
- `last-edit`: Diff previous commit vs working directory
- `<ref>`: Diff `<ref>` vs working directory (e.g., `diff session-start`)

## Step 0: Load CLAUDE.md context

- **Risk Surfaces** — paths that mark sensitive areas in this project
- **Don't Touch** — paths that should not appear in any diff
- **Module Ownership** — to surface review-routing info
- **Anti-Patterns** — to flag if the diff contains a known-bad pattern

## Analysis

Run `git diff` to get the raw changes, then analyze:

### 1. Group by Area

Identify which logical areas were touched. Group by:
- Source files (by directory or module)
- Config/build files
- Documentation
- Tests
- Skills/agents/hooks

For each group, note the module owner from CLAUDE.md if recorded.

### 2. Risk Assessment

For each area, assess risk level using CLAUDE.md Risk Surfaces:

```
HIGH RISK (red)
  - Path matches CLAUDE.md "Risk Surfaces" (e.g., auth, payments, migrations, secrets)
  - Path matches CLAUDE.md "Don't Touch" — ALARM (should not have been edited)
  - API contract changes (breaking)
  - Database schema changes
  - Error-handling changes in risk-surface code

MEDIUM RISK (yellow)
  - New endpoints or functions (need testing)
  - Changes to existing interfaces
  - Conditional logic changes in non-risk-surface code
  - Dependencies between touched files

LOW RISK (green)
  - Comments, documentation, config values
  - Safe refactors with no behavioral change
  - New functions not yet called
  - Test files (unless they're snapshot-comparing risk-surface output)
```

### 3. Anti-Pattern Match

Scan the diff against CLAUDE.md "Anti-Patterns" table. Flag any matches inline:
```
src/billing.ts:142 — matches anti-pattern "raw Date.now() in tests" (4 reverts in 2025)
```

### 4. Test Coverage

Check if changes are tested:

```
TESTED:
  - Modified functions with test cases
  - Changes to documented features

NOT TESTED:
  - New code paths
  - Edge cases in conditionals
  - Error handling
```

## Output Format

```
=== Diff Summary ===

[area]: [file] (RISK LEVEL) [Risk Surface: name] [Owner: team]
  - [change description]
  - Status: [needs testing / safe / review required]
  - Anti-pattern hits: [list]

=== Action Items ===
- [specific things to verify]
- [review routing if Module Ownership crosses teams]

=== Overall Risk ===
[Level] — [1-line summary of why]
```

## Edge Cases

- **Don't Touch hit**: lead with this. Output should start with `!! Don't Touch path modified:` and show the file before any other summary.
- **Many files changed:** Flag as "large changeset", suggest splitting commits.
- **Cross-team changes:** If Module Ownership shows multiple owners, flag for multi-team review.
- **Conflicting changes:** Flag if same code touched twice, suggest clarifying intent.

## Commands Used

```bash
git diff [ref]          # Get changes
git show <commit>       # See specific commit
git log --oneline -N    # Recent commits
```

## Notes

- If CLAUDE.md is missing or has empty Risk Surfaces, fall back to a generic auth/payments/data classifier and note in report: `WARN: CLAUDE.md Risk Surfaces empty — using generic classifier; run /onboard for project-tuned risk.`
