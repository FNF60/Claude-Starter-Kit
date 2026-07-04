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

## 6. Windows / PowerShell rules

The profile ships **both** `Bash(...)` and `PowerShell(...)` rules so it works whichever shell Claude Code uses. Which one is active depends on the machine:

- **Git for Windows installed** → Claude Code uses the **Bash tool** (Git Bash); the `Bash(...)` rules apply.
- **No Git for Windows**, or you set `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` **and** `defaultShell: "powershell"` → it uses the **PowerShell tool**; the `PowerShell(...)` rules apply.

Since this kit expects Git for Windows, most installs default to Bash. Shipping both lists means you're covered either way — nothing to toggle. To confirm which tool is live, run `claude doctor` or read the startup banner (it names the active shell).

Two behaviours of the `PowerShell(...)` matcher worth knowing:

- **Aliases are matched automatically**, case-insensitively. `PowerShell(Get-ChildItem *)` also covers `gci`/`ls`/`dir`; `PowerShell(Remove-Item *)` covers `rm`/`del`/`ri`. So the `ask` rule on `Remove-Item` is the real backstop — the `-Recurse -Force` deny is only advisory (arg order defeats it), exactly like the Bash `rm -rf` denies.
- **Pipelines are AST-parsed.** `|`, `;`, and (PS7+) `&&`/`||` split a line into subcommands, and **every** subcommand must be allowed or the whole line prompts. That's why the pipeline glue (`Where-Object`, `Select-Object`, `ForEach-Object`, `Sort-Object`, `Format-*`) is in the allow list.

**Known Windows bug:** clicking *"approve & don't ask again"* on a PowerShell prompt currently fails to persist — you get re-prompted and `settings.json` fills with dead rules ([anthropics/claude-code#57013](https://github.com/anthropics/claude-code/issues/57013)). The workaround is what this kit already does: **pre-write the rules into `settings.json` by hand** rather than relying on the interactive approve-and-remember flow.

## 7. Allowing specific download URLs

Shell downloads (`curl`, `wget`, `Invoke-WebRequest`) are in the `ask` tier, so they prompt every time by default. Because of the persistence bug above, you can't reliably build a trusted-URL list by clicking "don't ask again" — so maintain it **by hand**: add one allow rule per URL you trust. Add the `Bash(...)` form, the `PowerShell(...)` form, or both, depending on your shell:

```jsonc
"allow": [
  "Bash(curl https://raw.githubusercontent.com/your-org/*)",
  "PowerShell(Invoke-WebRequest https://raw.githubusercontent.com/your-org/*)"
]
```

Notes:

- One `Invoke-WebRequest` rule also covers the `curl`/`wget`/`iwr` aliases in PowerShell — you don't need separate entries for those spellings.
- Match the URL as a **prefix ending in `*`**. A plain `curl https://host/path` matches cleanly; flag-heavy forms like `curl -L https://...` shift the URL's position and may still prompt — that's intended (unusual invocations get eyeballed).
- This governs **downloading files** in the shell. Claude's own page reads use the separate `WebFetch(domain:…)` allowlist in the same file.
- Keep this list curated and small — every entry is a standing grant to reach that host without asking.
