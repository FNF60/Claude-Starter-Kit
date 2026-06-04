---
name: undo
description: "TRIGGER when user says 'undo', 'revert', 'go back', 'that broke it', or 'roll back'. Targeted rollback: reverts specific files, last edit, last commit (via git revert when on a shared branch), or entire session. Shows diff and confirms before reverting."
argument-hint: "[last-edit|file <path>|last-commit|session]"
---

# Undo: $ARGUMENTS

Targeted rollback system. Safely revert changes when something breaks, with ZERO collateral damage. Routes to `git checkout` (working-tree only) or `git revert` (creates a new commit, PR-friendly) depending on context.

## Golden Rule

**ALWAYS show what will be lost BEFORE reverting. ALWAYS require confirmation. NEVER auto-revert.**

## Step 0: Load CLAUDE.md context

- **Commit & Workflow Policy** — if `commit_policy` is `draft-PR` or branch protection is on, prefer `git revert` for committed work over `git checkout`/`git reset` so history stays intact.
- **Default branch** — never check out or reset commits on the default branch.

## Parse Arguments

| Arguments | Action |
|---|---|
| `last-edit` | Revert the most recently modified file in the working tree |
| `file <path>` | Revert a specific file in the working tree |
| `last-commit` | Revert the latest commit on the current branch (uses `git revert` if commit is already pushed or branch is shared, else `git reset --soft HEAD~1` after explicit confirmation) |
| `session` | Revert ALL working-tree changes since session start |
| *(empty)* | Show what's changed and ask what to undo |

## Step 1: Assess Current State

```bash
git status -s
git diff --stat
git stash list
git log --oneline -10
git rev-parse --abbrev-ref HEAD
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null  # detect upstream / pushed state
```

## Step 2: Route by Target

### `last-edit` — Revert Most Recent Working-Tree Change

Find the most recently modified tracked file from `git diff --name-only`.

Show:
```
Most recent change: src/api.js (modified 2 minutes ago)

Changes that will be LOST:
[show git diff for this file]

Revert to last committed state? (y/n)
```

If confirmed: `git checkout -- <file>`

### `file <path>` — Revert Specific File

Show full diff, then confirm, then revert.

After reverting:
- Run syntax check on the reverted file (use project's checker from CLAUDE.md if available)
- Note if a running service needs restart (check Service / URL map)

### `last-commit` — Revert the Latest Commit

Check whether the commit is already pushed (upstream exists and contains the SHA):

```bash
git branch --remotes --contains HEAD
```

**If pushed OR commit_policy = draft-PR OR on a shared branch:**
- Prefer `git revert HEAD --no-edit` — creates a new "Revert ..." commit
- Show the full diff that will be reversed
- Confirm
- Run `git revert HEAD`
- Report new commit SHA

**If unpushed AND solo branch:**
- Offer two options via `AskUserQuestion`:
  - "git revert (recommended) — adds a revert commit, preserves history"
  - "git reset --soft HEAD~1 — undo commit but keep changes staged"
- Default to revert. Reset only on explicit choice.

### `session` — Revert Everything to Savepoint

Nuclear option. Extra care.

1. Find the savepoint (stash or commit at session start)
2. Show EVERYTHING that will be lost (full diff)
3. Require explicit confirmation
4. **Create a safety stash first**: `git stash push -m "pre-undo-session $(date +%Y-%m-%d_%H:%M)"`
5. Then revert working tree: `git checkout -- .`
6. Report: "Session reverted. Your changes are saved in stash if you need them back: `git stash pop`"

### *(empty)* — Interactive

Show current state and present options via `AskUserQuestion`. Include `last-commit` only if there have been commits in this session.

## Step 3: Post-Undo Verification

After any revert:
1. Syntax/type check the affected files (use project tooling from CLAUDE.md)
2. Quick health check — is the app still working? (curl Services from URL map)
3. Report what was reverted and current state

## Safety Rails

### Things this skill NEVER does:
- `git reset --hard` — too broad, affects staging area
- `git clean -f` — deletes untracked files permanently
- Revert without showing the diff first
- Revert without explicit confirmation
- Delete stashes or reflog entries
- Force push anything
- `git checkout` / `git reset` on the default branch
- Rewrite history on a pushed commit (always prefer `git revert`)

### Before every destructive action:
- Create a safety stash (labeled clearly)
- Show full diff of what will be lost
- Require confirmation
- After revert, verify the result is syntactically valid
