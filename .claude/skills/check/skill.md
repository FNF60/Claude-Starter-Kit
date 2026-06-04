---
name: check
description: "TRIGGER PROACTIVELY after completing any feature, fix, or refactor. Quick health validation using the project's own commands from CLAUDE.md. Read-only, fast, safe to run often."
argument-hint: "[fast|full]"
---

# Check — Health Validation Using Project Commands

Fast, read-only health check after any change. Uses the **project's actual commands** from CLAUDE.md "Quick Start" and "Existing Tooling" — does not guess by language.

**Default mode:** `fast` (under 5 seconds). Use `full` if the user wants the complete suite including slow tests.

## Step 0: Load commands from CLAUDE.md

Read from CLAUDE.md:
- **Quick Start** → install/run/test/lint/typecheck/build commands
- **Existing Tooling** → linter, formatter, type-checker, pre-commit
- **Service / URL map** → ports/URLs to probe

If a command is missing or marked `(none configured)`, **skip that check gracefully** — do not invent a fallback. Note "skipped: no command" in the report.

If CLAUDE.md is missing entirely, fall back to language-guess only as last resort and flag in report: `WARN: CLAUDE.md missing — running guess-based checks`.

## Run All Checks in Parallel

### 1. Syntax / Compile Check

For each file in `git diff --name-only`, run the language's syntax-check. Prefer the *project's* type-checker if defined:

- If CLAUDE.md "Existing Tooling" defines `type-checker` → run it on changed files
- Else fall back to per-file syntax check (`node -c`, `python -m py_compile`, `go vet`, etc.)

### 2. Lint (if defined and `fast` allows it)

If CLAUDE.md defines `lint command`:
- `fast` mode: run on changed files only if the linter supports it (`eslint <files>`, `ruff check <files>`)
- `full` mode: run on whole project

Cap at 10 seconds. Beyond that, abort and note "lint timed out".

### 3. Test Status

If CLAUDE.md defines `test command`:
- `fast` mode: look for a fast-subset target. Heuristics:
  - `npm test` with `--findRelatedTests <files>` (jest)
  - `pytest <files>` (only test files in changed dirs)
  - `go test ./<changed-package>/...`
  - If no fast subset is detectable, **skip in `fast` mode** and report "tests skipped: full suite required"
- `full` mode: run the full test command, capped at 60 seconds

### 4. Server / App Responding (if URL map exists)

For each service in CLAUDE.md "Service / URL map":
```bash
curl -s -m 3 <url> -o /dev/null -w "%{http_code}"
```
- 200 = OK; timeout/error = service down (note it, don't fix — not /check's job)

### 5. Debug Artifact Scan

Search for common debug leftovers in changed files:
- Tagged debug logs: `console.log('[DEBUG`, `print("DEBUG`, `logger.debug` with debug tags
- Debugger breakpoints: `debugger;`, `breakpoint()`, `import pdb`
- Comment markers: `TODO`, `HACK`, `TEMP`, `FIXME` **introduced in this diff** (not pre-existing)

Report file:line for each.

### 6. CLAUDE.md Drift

Quick checks:
- Skills listed in CLAUDE.md exist in `.claude/skills/`
- Architecture entries point at files that still exist
- "Service / URL map" entries actually respond (if `full` mode)

### 7. Git State

```bash
git status -s
git diff --stat
```
- Count uncommitted changes
- Flag untracked files that look accidental (not in .gitignore)

## Output Format

Compact single report:

```
=== Check ([mode]) =====================================
  syntax/types   OK
  lint           OK (changed files only)
  tests          12 passed, 0 failed
  services       api: 200, frontend: 200
  debug          2 found
    src/api.js:751  tagged debug log
    src/api.js:758  tagged debug log
  CLAUDE.md      OK
  git status     3 files modified, 0 untracked
=========================================================
```

All-pass shorthand:

```
=== Check (fast) === ALL OK ============================
  syntax OK | lint OK | tests OK | services OK
  0 debug artifacts | CLAUDE.md OK | git: 3 modified
=========================================================
```

## Severity Levels

- **FAIL**: Syntax/type error, test failure. Lead with it.
- **WARN**: Debug artifacts, CLAUDE.md drift, service down. Fix before committing.
- **INFO**: Git status. Awareness only.

If any FAIL exists, lead with it:
```
!! FAIL: typecheck error in src/api.ts at line 1247
   ... rest of checks ...
```

## Important Notes

- **NEVER modify any file. NEVER start/stop any process.** Read-only.
- **Use project commands**, not language guesses.
- If a check can't run (no command, command timed out), skip gracefully and say why.
- `fast` mode should feel instant. If any check takes >3 seconds in `fast`, timeout and move on.
- The user should be able to run `/check` 20 times in a session without friction.
- Don't repeat information the user already knows.
- If CLAUDE.md is missing or unhelpful, recommend `/onboard --refresh` in the report rather than carrying on with bad guesses.
