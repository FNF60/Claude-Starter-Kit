---
name: wrap
description: "TRIGGER when user says 'wrap', 'done', 'close session', 'save progress', 'let's stop', 'commit everything', or 'clean'. Autonomous session close: review, auto-fix, commit (per project's commit policy), memory, report. Zero prompts unless policy requires confirmation."
argument-hint: "[quick|clean]"
---

# Wrap — Autonomous Session Close

Close a coding session. **Zero user prompts by default** — review, fix, commit (per policy), memory, report.

**Read CLAUDE.md "Commit & Workflow Policy" before anything else.** It determines whether step 4 commits, stages, opens a draft PR, or stops.

**If the user says "quick wrap":** Skip code review, go straight to memory + commit step.

## Execution: Single Flow

### 0. Load policy (no user prompt)

From CLAUDE.md "Commit & Workflow Policy":
- `commit_policy`: auto-commit | stage-only | draft-PR | never-commit (default: `auto-commit` if CLAUDE.md is silent — but `/onboard` should have set this)
- `commit_convention`: regex or template extracted from git history
- `default_branch`: detected branch name
- `pr_template_path`: path to `.github/PULL_REQUEST_TEMPLATE.md` if it exists
- `changelog_required`: whether CHANGELOG.md must be updated

Also load CLAUDE.md "Existing Tooling" — use *those* commands for the lint/typecheck step, not generic guesses.

### 1. Gather (parallel)

Run ALL in a single message:
- `git status -s`
- `git diff --stat`
- `git log --oneline --since="3 hours ago"`
- `git branch --show-current`

If on the default branch and `commit_policy` is `draft-PR` or branch protection is set: **warn and switch behavior** — don't commit to default branch even on auto-commit policy.

### 2. Review + Auto-Fix (no user prompt)

**If quick-wrap:** Skip this step entirely, jump to step 3.

Only review files in the diff. Scale to diff size:
- **< 50 lines:** Grep for debug artifacts only
- **50-300:** Standard checklist (below)
- **300+:** Use Explore agent

**Auto-fix list — read from CLAUDE.md "Quality Bar" if it defines one, else use this default:**
- `console.log('[DEBUG'` / `[debug]` -> remove
- `debugger;` -> remove
- `// TEMP` / `// HACK` lines -> remove
- Trailing whitespace in changed lines -> remove

**Project-specific auto-fix:** If CLAUDE.md "Code Style" says the project uses a shared logger, also remove bare `console.log` in changed code. If the project has a linter command, run it with `--fix` (or equivalent) before commit.

**Checklist (only for files that changed):**
- No `@latest` CDN URLs (pin versions) — only if frontend code is in the diff
- No hardcoded API keys or secrets
- No broken imports/references
- Lint clean (run `<lint command>` from CLAUDE.md if defined)
- Type-check clean (run `<typecheck command>` from CLAUDE.md if defined and diff includes typed files)
- Risk-surface check: if the diff touches a path in CLAUDE.md "Risk Surfaces", note it in the report (do not auto-fix risk-surface changes)

Report findings in 1-2 lines. If non-trivial issues found and they're in `Auto-fix list`, fix them; otherwise note in the final report — **do not ask**.

### 3. Memory (no user prompt)

Write a session memory file to the project memory directory (`.claude/memory/` or wherever the project keeps memories).

**Filename:** Check existing session files. Next letter suffix:
- None today -> `session_YYYY-MM-DD.md`
- `session_...-d.md` exists -> `session_...-e.md`

**Write the memory file:**

```markdown
---
name: Session [date] - [1-line summary]
description: [accomplished + next — for future session context]
type: project
---

## Accomplished
- [bullets]

## Issues Encountered
- [or "None"]

## Decisions Made
- [with reasoning, or "None"]

## Current State
- Uncommitted: [yes/no]
- Tests: [passing/failing/not run]
- Risk surfaces touched: [list or "None"]

## Next Steps
- [prioritized]

**Why:** [one sentence]
**How to apply:** [for next session startup]
```

Update MEMORY.md index — append, don't replace today's earlier entries.

### 4. Commit / Stage / PR (per policy)

If there are no uncommitted changes: skip, note in report.

#### 4.0 Route by policy

| `commit_policy` | Action |
|-----------------|--------|
| `auto-commit` | Continue with 4a–4c below |
| `stage-only` | `git add <files>` only — print "Staged, awaiting your review" |
| `draft-PR` | Commit on feature branch + `gh pr create --draft` if `gh` is available, else commit + print PR-creation reminder |
| `never-commit` | Skip entirely. Report unstaged diff size. |

If on the default branch and policy isn't `never-commit`: refuse to commit. Suggest `git switch -c <branch>` first.

#### 4a. Detect Commit Type

If CLAUDE.md `commit_convention` is set, follow it. Examples:
- Conventional Commits: emit `feat|fix|refactor|style|docs|chore: subject`
- Jira-prefixed: prompt for ticket ID via working-tree branch name (extract from branch like `PROJ-123-feature` -> `[PROJ-123] subject`)
- Component-prefixed: pick the top-level changed directory (`src/api/users.ts` -> `users: subject`)
- prose / no convention: write a plain imperative subject

If no convention is recorded, default to Conventional Commits.

For Conventional Commits, scan changed files to infer the type. **First match wins:**

| Type | Detection Rule |
|------|---|
| `fix` | Bug-related words in diff hunks: "fix", "bug", "issue", "leak", "resolve" |
| `refactor` | Files changed but no additions (only moved/reorganized), OR major restructuring |
| `style` | Only CSS/HTML/template files changed, OR visual tweaks only |
| `docs` | Only documentation files changed |
| `feat` | New files added, OR substantial new logic |
| `chore` | Dependencies, config files, CI/CD changes |

If multiple types match, pick `feat` > `fix` > `refactor` > `style` > `docs` > `chore`.

#### 4b. Draft Commit Message

- **Title (required):** per convention, under 70 chars
- **Body (optional):** If the change is substantial (100+ lines), add 1-2 lines explaining *why*
- **Risk-surface note:** If the diff touched paths in CLAUDE.md "Risk Surfaces", add a one-line marker in the body (e.g., `Touches: auth/session`)
- **Footer (required):** Always end with `Co-Authored-By: [active model name] <noreply@anthropic.com>`

#### 4c. Stage and Commit

- `git add [file1] [file2] ...` — **stage only changed files by name**, never `git add -A`
- Create the commit using a heredoc for the message

If `changelog_required` is true and the diff doesn't touch CHANGELOG.md: add a CHANGELOG entry and re-stage.

If `pr_template_path` is set and we're on a feature branch with no open PR: when policy is `draft-PR`, fill the template's sections with the session memory summary before creating the draft PR.

### 5. Report

```
=== Session Wrapped =====================================
  Policy:     [commit_policy]
  Reviewed:   [N files, issues found/fixed]
  Progress:   [1-line summary]
  Committed:  [hash — message] (or "Staged" / "Draft PR #N" / "Skipped per policy")
  Memory:     [filename] written
  Touches:    [risk surfaces if any]
  Next:       [1-line]
=========================================================
```

## Key Rules

- **Zero user prompts** by default — the user said "wrap", that IS the approval. The exception: policy violations (committing to default branch, missing PR template fields) which require confirmation.
- **Read policy from CLAUDE.md** — never assume auto-commit.
- **Auto-fix only what's safe** — debug artifacts, trailing whitespace. Project-specific fixes only when CLAUDE.md authorizes.
- **Never `git add -A`** — stage only reviewed files by name.
- **Never read plan docs** — waste of context during wrap.
- **Memory is non-negotiable** — always written, even if nothing to commit.
- **Risk surfaces are not auto-fixed** — only flagged.
- **Multiple sessions per day are normal** — use letter suffixes, don't overwrite.

---

## Clean Mode

If `$ARGUMENTS` is `clean`, skip the full wrap flow and just do workspace cleanup. No commit, no memory.

### 1. Report untracked files

```bash
git status -s | grep "^??"
```

### 2. Check for debug artifacts in modified files

```bash
git diff --name-only | xargs grep -n "console\.log.*DEBUG\|debugger;\|// TODO\|// HACK\|// TEMP\|// FIXME" 2>/dev/null || echo "Clean"
```

### 3. Summary

```
Clean: [N] untracked files, [clean|N debug artifacts]
```

**Rules:** Never delete files — only report. Never modify source code in clean mode.
