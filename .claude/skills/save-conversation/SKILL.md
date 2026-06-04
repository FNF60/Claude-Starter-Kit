---
name: save-conversation
description: "Save the current Claude Code session as a verbatim markdown transcript. Invocation: /save-conversation <slug>. Slug is required."
argument-hint: "<slug>"
---

# Save Conversation — Export Session Transcript

Saves the current Claude Code session as a verbatim markdown transcript.

**Output path:** `Supplementary AI md files/Conversations/YYYY-MM-DD-HHMM-<slug>.md`

Re-saving the same slug replaces the existing file (one file per slug at any time).

**Slug is required.** Stop immediately if `$ARGUMENTS` is blank.

---

## Execution

### 0. Validate slug

Read `$ARGUMENTS`. If empty or blank:

```
Usage: /save-conversation <slug>
Example: /save-conversation onboarding-session
Slug must be a short identifier, e.g. "feature-x", "setup-2026-05-12".
```

Stop. Do not continue.

### 1. Identify the current session

Run:

```bash
python .claude/bin/save_conversation.py list-sessions
```

Parse the JSON array output. Each element:
```json
{
  "session_id": "<uuid>",
  "mtime": "HH:MM",
  "turns": <N>,
  "preview": "<first user message, truncated>"
}
```

**Route by count:**

| Candidates | Action |
|-----------|--------|
| 0 | Print error: "No session file found modified in the last hour." Stop. |
| 1 | Use that `session_id` silently — no prompt needed. |
| 2+ | Use `AskUserQuestion` to present a picker. Label each option: `[HH:MM] <id-short> — <preview>`. Use the chosen `session_id`. |

`<id-short>` = first 8 chars of the UUID.

### 2. Write the transcript

```bash
python .claude/bin/save_conversation.py save <session-id> <slug>
```

Parse stdout:
- `Saved: <absolute-path>`
- `Lines: <N>`
- `Suggest: git add "<relative-path>"`

If the script exits non-zero, print its stderr and stop.

### 3. Report

```
Saved:  Supplementary AI md files/Conversations/YYYY-MM-DD-HHMM-<slug>.md
Lines:  <N>

To stage:  git add "Supplementary AI md files/Conversations/YYYY-MM-DD-HHMM-<slug>.md"
```

Do not run `git add`. Do not commit. Per project policy (stage-only), the user decides.

---

## Key Rules

- **Slug is mandatory.** Hard stop if missing — no guessing.
- **Single session only.** The script targets the most-recently-modified .jsonl in the last hour. No bulk modes.
- **Re-save replaces.** The script deletes any `*-<slug>.md` before writing the new file.
- **No git ops.** Print the `git add` suggestion; never execute it.
- **Output dir must exist.** The script errors if `Supplementary AI md files/Conversations/` is missing — don't create it; surface the error to the user.
- **Transcript file format.** Each turn renders as:
  - `## User` — verbatim user text
  - `## Assistant` — verbatim assistant text; tool calls as fenced `` ```tool_use:<name> `` blocks
  - `### Tool result: <name>` — verbatim result content
  - `<details><summary>System reminder: …</summary>…</details>` — hook injection notices
