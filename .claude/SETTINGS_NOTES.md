# settings.json — notes for existing projects

`settings.json` ships with kit defaults that work everywhere but are tuned for nothing in particular. The installer and `/onboard` will adjust it for your project. Three things to know:

## 1. Merge, don't overwrite

If you already have a `.claude/settings.json` from a previous setup, the installer (`install.py`) will:
1. Show you a diff before doing anything.
2. Offer to **merge** (keep your customizations, add what's missing), **replace** (use kit defaults), or **abort**.

If you're hand-installing without the installer, look at the kit's settings.json as a set of *additions*, not a replacement. The keys to focus on:
- `permissions.allow` — add the kit's git/utility entries to yours
- `permissions.deny` — add the kit's destructive-command blocks
- `hooks.PreCompact` and `hooks.Stop` — these add session continuity features that almost certainly don't conflict with what you have

## 2. Project-specific permissions

The kit's `permissions.allow` is generic — it doesn't know your test/lint/build commands. After `/onboard` runs, expect to see entries like:

```json
"Bash(pnpm test*)",
"Bash(pnpm lint*)",
"Bash(pnpm typecheck*)",
"Bash(pnpm build*)"
```

added to `allow`. If your project uses a different runner (`make test`, `pytest`, `cargo test`, etc.), `/onboard` adds the right entries for you. Hand-edit if anything is missing.

## 3. Default branch in the push hook

The kit's `PreToolUse` push hook warns on direct pushes to **main, master, develop, or trunk**. If your project's default branch has a different name (`production`, `trunk-stable`, etc.), `/onboard` rewrites the hook prompt to use the detected branch. You can also edit it directly — look for the `PRE-PUSH` prompt string.

## 4. CDN `@latest` check — frontend only

The `Edit` hook that blocks `@latest` CDN URLs is for projects with browser-loaded scripts. If your project is purely backend (CLI, API server with no embedded frontend), `/onboard` will offer to drop this hook entirely. You can also remove the entire `PreToolUse > matcher: "Edit"` block by hand.

## 5. Hand-editing checklist

If you're merging by hand, after edits run:

```bash
python3 -c "import json; json.load(open('.claude/settings.json'))"
```

If that prints nothing, the JSON is valid. If it errors, fix the syntax before reopening Claude Code.
