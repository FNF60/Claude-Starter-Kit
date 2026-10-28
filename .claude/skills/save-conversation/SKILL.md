---
name: save-conversation
description: "Save the current Claude Code session as a condensed markdown transcript (user prompts, final responses, AskUserQuestion exchanges — no tool calls/results or thinking). Invocation: /save-conversation <slug>. Slug is required."
argument-hint: "<slug>"
---

# Save Conversation — Export Session Transcript

Saves the current Claude Code session as a condensed markdown transcript containing only the main turns: user prompts, the final assistant response of each turn, and AskUserQuestion exchanges.

**Output path:** `docs/Supplementary AI md files/Conversations/YYYY-MM-DD-HHMM-<slug>.md`

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
Saved:  docs/Supplementary AI md files/Conversations/YYYY-MM-DD-HHMM-<slug>.md
Lines:  <N>

To stage:  git add "docs/Supplementary AI md files/Conversations/YYYY-MM-DD-HHMM-<slug>.md"
```

Do not run `git add`. Do not commit. Per project policy (stage-only), the user decides — **except at a ticket close** (below), where the closing step stages the transcript together with the ticket.

---

## At a ticket close (`WORKFLOW.md` §4, §4.1)

Every finished ticket leaves a transcript with the slug **`<ticket id> implementation`** (e.g. `C0.1 implementation`), staged with the ticket so it lands in the same commit.

- **Manual mode:** the session runs this skill with that slug right after `/handoff`. A ticket that continues into another session (handoff case 1) uses `<ticket id> implementation part <n>`, because re-saving a slug replaces the file.
- **Dispatch mode:** the dispatcher saves the ticket-agent's own transcript instead of its session, which spans many tickets:

  ```bash
  python .claude/bin/save_conversation.py list-agents <session-id>
  python .claude/bin/save_conversation.py save-agent <session-id> "<ticket id> ticket-agent" "<ticket id> implementation"
  ```

  The agent is found by the `description` the dispatcher gave it. The user turns are the dispatcher's brief and the owner's forwarded answers; the agent turns are its reports. The dispatcher's own session is saved once, when it ends (`/next-ticket`).
- A `ticket-agent` never runs this skill.

---

## Key Rules

- **Slug is mandatory.** Hard stop if missing — no guessing.
- **Single session only.** The script targets the most-recently-modified .jsonl in the last hour. No bulk modes. (`save-agent` targets one subagent of a session; several runs with the same description are written as sections of one file.)
- **Re-save replaces.** The script deletes any `*-<slug>.md` before writing the new file.
- **No git ops** in the skill itself: print the `git add` suggestion. Only the ticket-close step (above) stages the file.
- **Output dir must exist.** The script errors if `docs/Supplementary AI md files/Conversations/` is missing — don't create it; surface the error to the user.
- **Transcript file format.** Main turns only:
  - `## User` — verbatim user prompt (slash-command invocations render compactly as `` `/name args` ``)
  - `## User (tool rejection)` — the reason the user typed when rejecting a tool call
  - `## Question (AskUserQuestion)` — per question: `**Q:**` text, `_Options:_` labels, `**A:**` chosen answer
  - `## Assistant` — the turn's **final** response only (text after the turn's last tool call)
  - Dropped entirely: tool calls & results, thinking, hook/system reminders, command stdout, interruption boilerplate, mid-turn narration
