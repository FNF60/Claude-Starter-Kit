---
name: git-guardrails
description: Set up a Claude Code hook that blocks dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they execute. Use when the user wants to prevent destructive git operations, add git safety hooks, block git push/reset, or says something like "block git's dangerous permissions" / "lock down git".
---

# Set Up Git Guardrails

Installs a PreToolUse hook that intercepts and blocks dangerous git commands before Claude executes them. This is stronger than the kit's default permissions, which only *prompt* on these commands — the hook turns them into a hard block.

## What Gets Blocked

- `git push` (all variants including `--force`)
- `git reset --hard`
- `git clean -f` / `git clean -fd`
- `git branch -D`
- `git checkout .` / `git restore .`

When blocked, Claude sees a message telling it that it does not have authority to run these commands.

## Steps

### 1. Ask scope

Ask the user: install for **this project only** (`.claude/settings.json`) or **all projects** (`~/.claude/settings.json`)?

### 2. Copy the hook script

The bundled script is at: [scripts/block-dangerous-git.sh](scripts/block-dangerous-git.sh)

Copy it to the target location based on scope:

- **Project**: `.claude/hooks/block-dangerous-git.sh`
- **Global**: `~/.claude/hooks/block-dangerous-git.sh`

Make it executable with `chmod +x`.

### 3. Add hook to settings

Add to the appropriate settings file:

**Project** (`.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

**Global** (`~/.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

If the settings file already exists, merge the hook into the existing `hooks.PreToolUse` array — don't overwrite other settings. Note that the kit ships with **no hooks** by default, so on a fresh kit this adds a `hooks` block that wasn't there before.

### 4. Ask about customization

Ask if the user wants to add or remove any patterns from the blocked list. Edit the copied script accordingly.

### 5. Verify

Run a quick test:

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | <path-to-script>
```

Should exit with code 2 and print a BLOCKED message to stderr.

### 6. Tell the user exactly what changed

**Always report the settings change explicitly** — the user must know their permissions were altered. State plainly:

- **Which file** was edited (`.claude/settings.json` for this project, or `~/.claude/settings.json` globally).
- **What was added** — a `PreToolUse` Bash hook pointing at `block-dangerous-git.sh`.
- **The exact list of git commands now hard-blocked** (from "What Gets Blocked" above, plus any the user customized).
- **How to undo it** — remove the hook entry from that settings file and delete `hooks/block-dangerous-git.sh`.
