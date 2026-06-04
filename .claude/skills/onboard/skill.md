---
name: onboard
description: "TRIGGER on first conversation in an EXISTING project, when CLAUDE.md is missing or full of [FILL] placeholders, or when user says 'learn the codebase', 'onboard', 'study this project', 'figure out what we have'. Scans the repo, infers stack/conventions/risk surfaces from real signals, mines git history for anti-patterns, and drafts CLAUDE.md sections so the user only edits, not authors."
argument-hint: "[--deep | --quick | --refresh]"
---

# Onboard — Learn an Existing Codebase

The starter kit was originally written for greenfield projects. `/onboard` is what makes it work for repos that already have code, conventions, history, and opinions. It runs **before** anything else (including `/setup`) and produces the inputs every other skill depends on.

**When to run:**
- First time the kit is dropped into an existing project
- Whenever CLAUDE.md feels out of sync with the code
- After a major refactor or framework change (`/onboard --refresh`)

**What it produces:**
- A drafted CLAUDE.md with real values (not `[FILL]` placeholders)
- An updated `.claude/settings.json` permissions list with the project's actual commands
- A `.claude/onboarding.md` report showing what was found, what's confident, and what needs the user to confirm
- A list of detected risk surfaces, "don't touch" paths, and accepted-risk patterns

---

## Modes

| Mode | When | Time |
|------|------|------|
| `--quick` | Small repo (<50 files), or you want a first pass | ~30 sec |
| *(default)* | Most projects | 2-4 min |
| `--deep` | Large monorepo, or you want maximum accuracy | 5-10 min |
| `--refresh` | CLAUDE.md exists but is stale — update without overwriting user edits | 1-2 min |

---

## Phase 1: Pre-flight (always)

Before any scanning, detect conflicts so we don't clobber existing setup.

1. **Check for existing AI tooling.** Look for: `CLAUDE.md`, `.cursorrules`, `.cursor/rules/`, `.aider.conf.yml`, `.github/copilot-instructions.md`, `.continue/`, `.windsurfrules`, `AGENTS.md`. If any exist, **read them first** — they encode rules the team has already agreed on.

2. **Check for existing `.claude/` content.** If `.claude/skills/`, `.claude/agents/`, or `.claude/settings.json` already exist with non-kit content, surface this immediately to the user via `AskUserQuestion`:

```
Q: "I found existing Claude config in this repo. How should I handle it?"
  - "Merge — keep your customizations, add what's missing"
  - "Preview diff first — show me what would change"
  - "Replace — overwrite with the kit's defaults"
  - "Abort — I want to look myself"
```

3. **Detect repo root.** Use `git rev-parse --show-toplevel`. If not a git repo, ask the user to confirm the root before scanning further.

4. **Detect default branch.** `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'`. Fall back to checking which of `main`, `master`, `develop`, `trunk` exists. Record for hooks.

---

## Phase 2: Codebase Scan (parallel)

Run these in a single batch — they're independent and fast.

### 2a. Stack & framework detection

Read in priority order, stop after first hit *per language*:

| File | Tells us |
|------|----------|
| `package.json` | Node/JS/TS, package manager (npm/pnpm/yarn/bun via lockfile), framework (deps), scripts (test/build/dev/lint) |
| `pnpm-lock.yaml` / `yarn.lock` / `bun.lockb` | Confirms package manager |
| `tsconfig.json` | TypeScript present, strict mode, paths |
| `requirements.txt` / `pyproject.toml` / `Pipfile` / `setup.py` | Python, framework, test runner |
| `Cargo.toml` | Rust, workspace structure |
| `go.mod` | Go, module name, deps |
| `pom.xml` / `build.gradle` / `build.gradle.kts` | Java/Kotlin, build tool |
| `Gemfile` | Ruby, framework (Rails detected via deps) |
| `composer.json` | PHP |
| `mix.exs` | Elixir |
| `Dockerfile` / `docker-compose.yml` | Service topology, ports, env conventions |
| `Makefile` / `justfile` / `Taskfile.yml` | Project-blessed commands (these override defaults — always prefer them) |

For each match, extract: framework name + version, test command, lint command, build command, dev/run command, type-check command.

### 2b. Project shape

```bash
# Top-level structure (one level deep)
ls -la

# File count + total LOC per language (sample, not exhaustive)
git ls-files | head -2000

# Largest source files (signal of where the action is)
git ls-files | xargs -I{} wc -l {} 2>/dev/null | sort -rn | head -20

# Entry points (heuristic)
ls src/index.* src/main.* main.* index.* app.* server.* 2>/dev/null
```

Identify:
- **Entry points** — what runs first
- **Top modules** — largest/most-imported directories
- **Tests directory** — where they live, naming convention
- **Config directory** — env handling, secrets pattern

### 2c. Convention extraction

Sample 5-10 of the largest source files. Look for:

- **Naming**: camelCase vs snake_case vs kebab-case (functions, files, constants)
- **Imports**: relative vs absolute, named vs default exports, barrel files
- **Error handling**: throw vs Result-type vs error-as-value vs callbacks
- **Async style**: async/await vs promises vs callbacks
- **Logging**: console vs project-shared logger (look for `import { logger }`, `from .log import`, etc.)
- **Type usage** (if typed): `any`/`Object` tolerance, generics conventions

Record these as **descriptive observations**, not prescriptive rules. The user confirms or overrides in Phase 3.

### 2d. Existing tooling detection

| Tool | Signal |
|------|--------|
| Linter | `.eslintrc*`, `.prettierrc*`, `ruff.toml`, `pyproject.toml [tool.ruff]`, `.rubocop.yml`, `.golangci.yml`, `clippy.toml` |
| Formatter | `.prettierrc`, `.editorconfig`, `pyproject.toml [tool.black]`, `rustfmt.toml`, `gofmt` (implicit) |
| Type-checker | `tsconfig.json`, `mypy.ini`, `pyrightconfig.json`, `flow-typed/` |
| Pre-commit | `.pre-commit-config.yaml`, `.husky/`, `lefthook.yml`, `lint-staged` in package.json |
| CI | `.github/workflows/`, `.gitlab-ci.yml`, `.circleci/`, `azure-pipelines.yml`, `Jenkinsfile` |
| Test runner | jest/vitest/mocha/playwright/cypress in package.json, `pytest.ini`/`tox.ini`, `go test`, `cargo test` |
| Dependency mgmt | renovate.json, dependabot.yml |

For each found, record the **command** the project uses (e.g., `pnpm lint` not just "eslint exists").

### 2e. Risk surface detection

Grep for filenames and content patterns that mark sensitive areas:

| Surface | Filename patterns | Content patterns |
|---------|-------------------|------------------|
| Auth | `auth*`, `login*`, `session*`, `jwt*`, `oauth*`, `passport*` | `bcrypt`, `argon2`, `jwt.sign`, `signin`, `permissions` |
| Payments | `payment*`, `billing*`, `stripe*`, `checkout*`, `invoice*` | `stripe.`, `charge`, `subscription`, currency math |
| Migrations | `migrations/`, `migrate/`, `schema.*`, `*.sql` | `ALTER TABLE`, `DROP`, `CREATE INDEX` |
| Secrets | `.env*`, `secrets/`, `credentials*` | `process.env`, `os.environ`, `Secret`, API key constants |
| External APIs | `clients/`, `integrations/`, `vendors/` | `fetch(`, `axios`, `requests.get`, retry/timeout logic |
| User data / PII | `users/`, `profile*`, `account*` | email, phone, ssn, address handling |

Output the list. Each entry gets called out in CLAUDE.md so other skills can elevate caution.

### 2f. "Don't touch" detection

Auto-add these to a Don't Touch list (the user can prune):

- `node_modules/`, `vendor/`, `target/`, `dist/`, `build/`, `.next/`, `__pycache__/`, `.venv/`, `venv/`
- Anything in `.gitignore` that's also tracked (oddities — ask the user)
- Files >5K lines that look generated (no spaces in identifiers, repeating patterns, `// GENERATED`, `# autogenerated`, `eslint-disable`)
- Vendored copies — directories named `third_party/`, `external/`, `lib/vendor/`
- Database migration files older than 30 days (changing them is almost always a bug)

### 2g. Process & ownership detection

| File | What we learn |
|------|---------------|
| `CODEOWNERS` | Who reviews what — record as module ownership |
| `CONTRIBUTING.md` | PR rules, commit format, branch naming |
| `.github/PULL_REQUEST_TEMPLATE.md` | Required PR sections (mention in /wrap) |
| `CHANGELOG.md` | Whether to update on every change |
| `.github/ISSUE_TEMPLATE/` | How bugs/features are reported |

### 2h. Git history mining (anti-patterns from real history)

```bash
# Recent fixes — the "what tends to break" signal
git log --oneline -300 --grep="fix\|bug\|revert\|hotfix\|regression" -i

# Files touched most in fix commits (= hot spots)
git log --since="6 months ago" --grep="fix" --name-only --pretty=format: | sort | uniq -c | sort -rn | head -15

# Reverts (= things that shouldn't have shipped)
git log --oneline --grep="^Revert" -i

# Commit message format (sample 30)
git log --oneline -30 | awk '{$1=""; print}'
```

From this, draft 3-5 **anti-pattern candidates** for CLAUDE.md. Format: "this kind of change has been reverted/hot-fixed N times in the last 6 months — likely fragile." Present to user for confirmation; don't add unconfirmed entries.

Also extract the **commit message convention** the project actually uses. Examples:
- `[PROJ-123] description` -> Jira-prefixed
- `feat: description` / `fix: description` -> Conventional Commits
- `Component: description` -> component-prefixed
- prose -> no fixed convention

Record this so `/wrap` follows it instead of imposing Conventional Commits.

---

## Phase 3: Targeted Questionnaire (only what code can't tell us)

Skip questions the scan already answered. Ask only these via `AskUserQuestion`, in 1-2 rounds:

### Round 1 — Intent & policy

```
Q1: "Who's working on this project?" (header: "Team")
  - "Just me — solo project"
  - "Small team (2-5)"
  - "Larger team — strict review"
  - "Open source — external contributors"

Q2: "What's your commit policy?" (header: "Commits")
  - "Auto-commit on /wrap (current kit default)"
  - "Stage only — I review and commit manually"
  - "Draft PR — open a PR but never push to main"
  - "Never commit — only edit working tree"

Q3: "Risk tolerance for this codebase?" (header: "Risk")
  - "Move fast — it's a side project / prototype"
  - "Standard — usual professional caution"
  - "High caution — production, paying users, regulated"

Q4: "Default branch protection?" (header: "Branch")
  - "Block direct pushes to <detected-default> entirely"
  - "Warn on direct push, allow if I confirm"
  - "No protection — I push directly"
```

### Round 2 — Confirm inferences (skip if scan was high-confidence)

Present detected items grouped and confirm in one multi-select:

```
Q1: "I detected these as sensitive areas — keep them flagged?" (header: "Risk surfaces", multiSelect)
  - [list of risk surfaces from 2e]

Q2: "Anti-patterns I mined from git history — confirm any that are real?" (header: "Anti-patterns", multiSelect)
  - [candidates from 2h, max 5]
  - "None — these were one-offs"

Q3: "Don't-touch list — anything to remove?" (header: "Off-limits", multiSelect)
  - [candidates from 2f]
  - "All correct"
```

**Hard rule: never ask the user something the scan already answered.** If `package.json` says `"test": "jest"`, don't ask "what test framework do you use." Just record it.

---

## Phase 4: Draft CLAUDE.md

Write `CLAUDE.md` at the repo root with sections populated from the scan. Every value is either **discovered** (auto-filled, marked as such) or **declared** (from user answers). No empty `[FILL]` placeholders.

Use the new CLAUDE.md template structure (see the kit's `CLAUDE.md` — it's been redesigned to map to this output).

For each section, if the data is missing, **leave a one-line prompt explaining what's needed and why** — never a generic `[FILL]`.

---

## Phase 5: Update settings.json (merge, don't overwrite)

If `.claude/settings.json` exists with non-kit content, **merge**:

1. Read existing `permissions.allow`, `permissions.deny`, `permissions.ask`, `hooks`.
2. Add project-specific entries from the scan:
   - Test command -> `Bash(<cmd>*)` to allow
   - Lint/format/type-check commands -> allow
   - Build/dev commands -> allow
   - Detected dangerous commands (e.g., `npm publish`, deploy scripts) -> deny or ask
3. Adjust the `git push` hook to use the detected default branch, not hardcoded `main|master`.
4. Drop the CDN `@latest` hook if no web/frontend code was detected.
5. Save. Diff-print what changed.

---

## Phase 6: Onboarding Report

Write `.claude/onboarding.md`:

```markdown
# Onboarding Report — [project name]
**Date:** [YYYY-MM-DD]
**Mode:** [quick|default|deep|refresh]

## What I found
- Stack: [list with versions]
- Package manager: [name]
- Test command: `[cmd]` ([N] tests detected)
- Lint command: `[cmd]`
- Type-check: `[cmd]` (or "none")
- Default branch: [name]
- Commit convention: [pattern]
- CI: [provider, N workflows]

## Risk surfaces (flagged in CLAUDE.md)
- [list]

## Don't-touch list
- [list]

## Anti-patterns mined from git history
- [list, each with evidence: "N reverts in last 6 months"]

## High-confidence
- [things the scan was certain about]

## Needs your eyes
- [things the scan inferred but isn't sure about]

## Skipped
- [files/dirs we deliberately didn't scan and why]
```

Print a 6-line summary in chat with a link to the full report.

---

## Key Rules

- **Read before write.** Phase 1 (conflict detection) is non-negotiable. If we'd overwrite something, ask first.
- **Discovered != Declared.** Auto-filled values are marked as such so the user knows what came from the scan vs what they confirmed.
- **Never ask what the code already answered.** This is the entire reason `/onboard` exists.
- **Confidence labels.** When something is inferred (not certain), label it `(inferred)` in CLAUDE.md.
- **Idempotent.** Re-running `/onboard --refresh` updates discovered values but preserves user edits to declared sections.
- **Respect existing AI config.** If `.cursorrules` or `AGENTS.md` exists, surface their content in the report so the user can decide what to port over.
- **No silent assumptions.** Every section in CLAUDE.md should be traceable to either a scan finding or a user answer.
