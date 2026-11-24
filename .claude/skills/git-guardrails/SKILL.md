---
name: git-guardrails
description: Set up a Claude Code hook that blocks dangerous git commands (push, reset --hard, clean -f, branch -D, and commit / rebase under a stage-only policy) before they execute, in both the Bash and PowerShell tools. Use when the user wants to prevent destructive git operations, add git safety hooks, block git push/commit, or says something like "block git's dangerous permissions" / "lock down git".
---

# Set Up Git Guardrails

Installs a PreToolUse hook that intercepts and blocks dangerous git commands before Claude executes them. This is stronger than the kit's default permissions, which only *prompt* on these commands: the hook turns them into a hard block.

## What Gets Blocked

Always:

- `git push` (all variants including `--force`)
- `git reset --hard`
- `git clean -f` / `-fd` / `-xf`
- `git branch -D`
- `git checkout .` / `git checkout -f` / `git restore .` (but not `git restore --staged .`)

Additionally when the commit policy is **stage-only** (the kit default: agents stage, the human commits):

- `git commit` (including `--amend`), `git rebase`, `git am`
- `git cherry-pick` and `git revert`, unless given `--no-commit` / `-n` (they create commits)

Never blocked: `git add`, `git merge`, `git stash`, `git tag`, switching branches, and anything read-only. If a project needs more or fewer, edit the lists in the copied script.

When blocked, Claude sees a message telling it the owner has prevented the command.

## How the script decides

It does not search the command text for "git push". It splits the command into separate commands (on `;`, `&`, `|` and newlines, outside quotes), finds the `git` call in each, skips git's global options (`-C <dir>`, `-c key=value`, `--no-pager`), and checks the real subcommand. So `git -C repo push` is caught (a text search for "git push" misses it), a commit message or `grep 'git push'` is not mistaken for a push, and `bash -c "git push"` / `powershell -Command git push` are looked into. It is a guardrail against accidents, not a security boundary: `eval`, a shell variable holding the subcommand, aliases, and scripts that run git internally are not seen.

## Steps

### 1. Ask scope and commit policy

Ask the user two things:

- Install for **this project only** (`.claude/settings.json`) or **all projects** (`~/.claude/settings.json`)?
- Commit policy: **stage-only** (agents never commit; the default) or **auto-commit** (agents may commit and rebase; push is still blocked)? If the project's `CLAUDE.md` already declares a commit policy, propose that one.

### 2. Copy the scripts

The bundled scripts are in [scripts/](scripts/): `block-dangerous-git.py` (the hook) and `test_block_dangerous_git.py` (its self-test).

Copy both to the target location:

- **Project**: `.claude/hooks/`
- **Global**: `~/.claude/hooks/`

Then set `COMMIT_POLICY` at the top of the copied `block-dangerous-git.py` to the user's answer (`"stage-only"` or `"auto-commit"`).

The hook needs Python on the PATH (the kit already uses it for `install.py` and `/save-conversation`). Check with `python --version`; if only `python3` exists, use `python3` in the command below.

### 3. Add the hook to settings

The matcher covers **both** shell tools, because a command run through the PowerShell tool would otherwise bypass a `Bash`-only hook.

**Project** (`.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|PowerShell",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/block-dangerous-git.py\""
          }
        ]
      }
    ]
  }
}
```

**Global** (`~/.claude/settings.json`): the same block, with the command `python "<absolute path to ~/.claude/hooks/block-dangerous-git.py>"` (use the absolute path; do not rely on `~` expanding).

If the settings file already exists, merge the hook into the existing `hooks.PreToolUse` array. Do not overwrite other settings. Note that the kit ships with **no hooks** by default, so on a fresh kit this adds a `hooks` block that was not there before. Confirm the file still parses afterwards (`python -c "import json; json.load(open('<file>'))"`).

### 4. Ask about customization

Ask whether the user wants to add or remove any patterns. Edit the copied script accordingly, then re-run the self-test.

### 5. Verify

Run the self-test; it must end with `failures 0`:

```bash
python <hooks dir>/test_block_dangerous_git.py
```

Then probe the live hook once with a harmless command. Deleting a branch that does not exist is blocked under every policy, does nothing if the hook turns out not to be active, and the `-C` form also proves the hook reads past git's global options:

```bash
git -C . branch -D guardrail-probe-does-not-exist
```

Do not probe with `git push` or `git commit`. A permission rule refuses or prompts for those before the hook runs (a project that denies push in its settings refuses `git push --dry-run` outright), so the probe proves nothing about the hook. No permission rule matches the `-C` form, so it reaches the hook.

You should get a `BLOCKED:` message from the hook. If the command runs instead (git answers that the branch was not found), the hook is not active in this session: settings may need a restart or `/hooks` review to take effect, so tell the user rather than assuming it works. (This checks the main session only. Whether the hook also fires inside subagents has not been verified in the kit.)

### 6. Tell the user exactly what changed

**Always report the settings change explicitly**: the user must know their permissions were altered. State plainly:

- **Which file** was edited (`.claude/settings.json` for this project, or `~/.claude/settings.json` globally).
- **What was added**: a `PreToolUse` hook on `Bash|PowerShell` pointing at `block-dangerous-git.py`, plus the two scripts copied into `hooks/`.
- **The commit policy chosen** and the exact list of git commands now hard-blocked (from "What Gets Blocked" above, plus any customization).
- **How to undo it**: remove the hook entry from that settings file and delete `hooks/block-dangerous-git.py` and `hooks/test_block_dangerous_git.py`.
