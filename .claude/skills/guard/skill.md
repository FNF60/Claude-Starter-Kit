---
name: guard
description: "TRIGGER PROACTIVELY before any edit touching 3+ files, critical code paths, or sensitive areas. Pre-flight safety check: snapshots state, maps dependencies using project-aware tools, warns about risks, checks for uncommitted tangles. Reads CLAUDE.md for Risk Surfaces, Don't Touch, and Existing Tooling."
argument-hint: "[file-or-module-name]"
---

# Guard: $ARGUMENTS

Pre-flight safety system. Assess risk BEFORE a change and give the developer the information they need to make the change safely. **Uses the project's language-aware tools when available** instead of grep, which produces too many false positives in large codebases.

## Step 0: Load CLAUDE.md context

- **Risk Surfaces** — any of these in the change path? Elevate caution.
- **Don't Touch** — refuse to proceed if the target is on this list (or require explicit override).
- **Existing Tooling** — for the dependency-map step, prefer the recorded reference-lookup tool over grep:
  - JS/TS: `tsc --noEmit` cross-file errors, or `eslint --print-config` for path resolution
  - Go: `go list -deps ./...`
  - Python: `python -m modulefinder`, or `pyright --outputjson`
  - Rust: `cargo tree` / `cargo check`
  - Universal fallback: `ripgrep` with type filters (`rg --type ts <name>`)

## Step 1: Uncommitted Changes Check

```bash
git status -s
git diff --stat
```

**If there are uncommitted changes:**
- Show them grouped by file
- Determine if they're related to what the user is about to change
- If UNRELATED changes exist, warn clearly:
  ```
  !! Uncommitted changes from a different concern:
     src/api.js: +47 -12 (database logic)
     You're about to edit: src/components/ (UI)
     Consider committing or stashing first to keep changes isolated.
  ```
- If related: "Existing uncommitted changes in same area — building on top."

## Step 2: File State Snapshot

For each file that will be touched, record:
- Current line count
- Git status (clean/modified/untracked)
- Quick syntax/type check (use project's type-checker if defined in CLAUDE.md)
- Don't Touch / Risk Surface flag

Report:
```
File snapshots:
  src/api.js       1,319 lines  modified  types OK      [Risk Surface: API]
  src/index.html   8,247 lines  clean     n/a
  third_party/x.js              -         -            [Don't Touch — abort]
```

If any target is in Don't Touch, **stop here** and require explicit user override.

## Step 3: Dependency Map (project-aware)

If `$ARGUMENTS` specifies a file or module, do targeted analysis using the project's tools.

1. **Find the target.** Use the language-aware reference tool first; fall back to grep with type filters.
2. **Map scope.** Where is the symbol defined? What scope level (private, module, exported)?
3. **Find all references** using the reference tool, not raw grep. This avoids matching variable names that share the symbol's text but aren't actual references.
4. **Cross-file warnings:** if the target is imported/referenced from other files, list them with line numbers.
5. **Dependency chain:** what does this code depend on?
6. **Dependents:** what depends on this code?

Report:
```
Target: UserService (src/services/user.js)
  Tool used: tsc (TypeScript references)
  Imports: DatabaseClient, Logger, Config
  Imported by (3 sites):
    - src/routes/auth.js:12,84 (login, register)
    - src/routes/admin.js:5,71,93 (listUsers, deleteUser)
    - src/middleware/auth.js:8 (validateToken)
  Tests touching this:
    - tests/services/user.test.js
    - tests/integration/auth.test.js

  If you RENAME or CHANGE the interface:
    - 3 files + 2 test files will need updates
```

If the project's reference tool isn't available, fall back to ripgrep with type filter and note in report: `Tool used: ripgrep (no language reference tool available)`.

## Step 4: Risk-Surface Cross-check

If any touched file is in CLAUDE.md "Risk Surfaces":
- Increase warning prominence
- Suggest enabling the relevant agent proactively (security-reviewer for auth, error-trap-monitor for data writes)
- Recommend Tier 2+ /plan if no plan exists for this change

## Step 5: Summary

```
=== Guard: [target] ================================
  Files:       src/api.js (modified, types OK)
  Uncommitted: +47 -12 in src/api.js (related)
  References:  3 import sites across 2 files (via tsc)
  Tests:       2 test files touch this
  Dependencies: DatabaseClient, Logger
  Dependents:  auth.js, admin.js, middleware/auth.js
  Risk Surfaces: API (elevated caution)
  Warnings:    none
=====================================================
```

If there are warnings, make them prominent:

```
  !! Cross-file dependency: 3 files import UserService
  !! Uncommitted unrelated changes in src/components/
  !! Risk Surface: this is in the auth path — security-reviewer recommended
  !! Don't Touch: target/legacy/oldservice.js — change requires explicit override
```

## Important Notes

- **READ-ONLY.** Never modify files. Never start/stop processes.
- **Project-aware tool first, grep fallback** — large codebases drown grep in noise.
- Be specific about line numbers so the developer can verify.
- When flagging risks, explain WHY it's risky, not just that it is.
- For empty `$ARGUMENTS`, do the general uncommitted check + syntax check only. No deep analysis without a target.
- Keep output concise. 2-3 seconds to read, not 2 minutes.
- If CLAUDE.md is missing, note that depth is reduced and recommend `/onboard`.
