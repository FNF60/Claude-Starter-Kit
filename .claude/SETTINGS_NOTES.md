# settings.json — notes for existing projects

The kit ships **two** files:

- **`settings.json`** — the active permissions profile Claude Code reads. Valid JSON, so the installer can merge it.
- **`settings.jsonc`** — the *same* profile with inline comments explaining every block. Reference only; Claude Code doesn't load it. Read it to understand a rule before you change it, then mirror the change into `settings.json`.

This profile is a scoped "middle ground": routine read/inspect/build commands auto-run, state-changing or destructive commands prompt or are blocked. There are **no hooks** — git safety comes from the `ask`/`deny` permission rules, and if you want hard git-command blocking you can install it on demand with the `git-guardrails` skill.

## 1. How evaluation works

Order is **deny → ask → allow → defaultMode**, first match wins. A trailing `*` is optional, so `Bash(git status *)` also matches bare `git status`. Matching is shell-operator aware: `Bash(cat *)` will **not** match `cat x && rm y` — chained commands fall through to a prompt. That's why the plain `allow` rules stay safe.

- `allow` — read-only/inspection shell, package managers, test/lint/build runners, git read + `git add`, and a doc-domain WebFetch allowlist.
- `ask` — reversible-but-consequential actions you want to eyeball: `git commit`/`push`/`reset`/`checkout`/`rebase`/`merge`, `rm`/`mv`/`chmod`, `docker run`/`exec`/`rm`, and publishes.
- `deny` — catastrophic or exfiltration commands (`rm -rf /`, `dd`, `curl … | sh`) and reads of common secret locations (`.env`, `.ssh`, `*.pem`, cloud creds).

## 2. Merge, don't overwrite

If you already have a `.claude/settings.json`, `install.py` (and `/setup`) will show a diff and offer **merge** (union `allow`/`ask`/`deny`, keep your entries), **replace**, or **abort**. Hand-installing? Treat this file's lists as *additions* to yours.

## 3. Project-specific permissions

The `allow` list is generic — it doesn't know your exact test/lint/build commands, though it already covers the common runners (`npm`/`pnpm`/`yarn`/`bun`, `pytest`, `cargo`, `go`, `mvn`/`gradle`). After `/setup`, expect entries tailored to the project's actual commands. Hand-edit if anything is missing.

## 4. Letting the Read tool see outside the project

The native Read/Edit/Write tools are confined to the project directory plus whatever you add to `permissions.additionalDirectories`. Bash read commands (`cat`/`head`/`grep`/`find`/`ls`) are **not** gated by that list, so you already get broad read via Bash. Add a path to `additionalDirectories` only if you want the structured Read tool to reach outside the project. See the commented `settings.jsonc` for platform examples.

## 5. Hand-editing checklist

After editing, confirm the JSON still parses:

```bash
python3 -c "import json; json.load(open('.claude/settings.json'))"
```

No output means valid. If it errors, fix the syntax before reopening Claude Code. (Edit `settings.json`, not `settings.jsonc` — the `.jsonc` file has comments and is intentionally not valid JSON.)
