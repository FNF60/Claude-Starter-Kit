---
name: setup
description: "TRIGGER on the first conversation in a project, or when the user says 'setup', 'configure', 'customize this', 'onboard', 'learn the codebase', 'study this project'. Detects whether the project is greenfield or an existing codebase and handles both: for existing repos it scans and drafts CLAUDE.md from real signals; for new ones it runs a guided questionnaire. Tailors CLAUDE.md, permissions, and skills to this project."
argument-hint: "[--deep | --quick | --refresh]"
---

# Setup — Project Configuration

One skill, two paths. Phase 0 decides which; don't ask redundant questions.

## Phase 0: Route — new or existing?

**Before any other question**, check whether the project already has content:

```bash
git ls-files | head -1
ls -la
```

- If there are tracked source files **other than** `README.md` / `LICENSE` / `.gitignore` / `CLAUDE.md` / `.claude/`: it's an **existing project** → run the **Existing-Project Scan** in [ONBOARD-SCAN.md](ONBOARD-SCAN.md) and stop when it finishes. That procedure has its own questionnaire and produces CLAUDE.md, the settings merge, and `.claude/onboarding.md`. Pass through any `--quick` / `--deep` / `--refresh` flag the user gave.
- If there are no source files yet (or only the kit's own files + README/LICENSE): it's a **new project** → continue with Phase 1 below.

If ambiguous, ask one question:

```
AskUserQuestion:
Q: "Is this a fresh start or an existing codebase?" (header: "Project state")
  - "Fresh start — no code yet, plan and build from zero"
  - "Existing — there's already code I want Claude to learn"
  - "Hybrid — some code, but mostly new direction"
```

`Existing` and `Hybrid` both route to the Existing-Project Scan. `Fresh` continues here.

---

## Greenfield Track (no existing code)

Walk the user through structured questionnaires to configure CLAUDE.md, permissions, and skills.

## Phase 1: Project Identity (Round 1)

```
AskUserQuestion:

Q1: "What kind of project is this?" (header: "Stack")
  - "Web app (HTML/JS/CSS, browser-based)"
  - "Node.js backend (Express, API, CLI)"
  - "Python project (Django, Flask, FastAPI, scripts)"
  - "Full-stack (frontend + backend)"
  - "Other (I'll describe)"

Q2: "How big do you expect this to get?" (header: "Scale")
  - "Small (< 5 files, < 1K lines) — script or single-purpose tool"
  - "Medium (5-20 files, 1K-10K lines) — typical app"
  - "Large (20+ files, 10K+ lines) — production-grade"
  - "Monorepo / multi-package"

Q3: "What's your role?" (header: "Role")
  - "Solo developer — I make all decisions"
  - "Team lead — I steer but others contribute"
  - "Contributor — I work within existing patterns"
  - "Learning — I'm building skills, explain things"

Q4: "How do you prefer to work with AI?" (header: "Style")
  - "Max speed — decide fast, fix later"
  - "Careful — plan first, verify everything"
  - "Balanced — plan big things, move fast on small ones"
```

**After Round 1:**
- Save user role to memory (`user_profile.md`)
- Save project type to memory (`project_overview.md`)

## Phase 2: Safety & Quality (Round 2)

```
AskUserQuestion:

Q1: "What's the riskiest part of this project?" (header: "Risk", multiSelect: true)
  - "Money/payments — wrong numbers = real cost"
  - "User data — privacy, auth, security"
  - "External APIs — rate limits, costs, breaking changes"
  - "Complex math — formulas that must be exact"
  - "Nothing critical — it's a personal/learning project"

Q2: "What testing approach?" (header: "Tests")
  - "Test-driven — write the test first (use the /tdd skill)"
  - "Full test suite (jest, pytest, etc.) — run on every change"
  - "Some tests — run manually"
  - "No tests yet — help me set them up"

Q3: "Commit policy?" (header: "Commits")
  - "Auto-commit on /wrap"
  - "Stage only — I review and commit manually"
  - "Draft PR — open a PR but never push to main"
  - "Never commit — only edit working tree"

Q4: "What should NEVER happen?" (header: "Guardrails", multiSelect: true)
  - "Push to default branch without review"
  - "Deploy/publish without testing"
  - "Commit secrets or API keys"
  - "Break backward compatibility without warning"
```

**After Round 2:**
- Update `.claude/settings.json` permissions based on answers (add stack-appropriate `allow` entries; move risky commands to `ask`/`deny`).
- Write the chosen commit policy into CLAUDE.md "Commit & Workflow Policy".
- "Push to default branch" guardrail → record it in CLAUDE.md's Critical Rules; the settings profile already routes `git push` through `ask`. For hard blocking, offer to run the `git-guardrails` skill.
- "Commit secrets" guardrail → note it in CLAUDE.md "Security Notes"; the settings `deny` list already blocks reading common secret files (`.env`, `*.pem`, cloud creds).

## Phase 3: Workflow Preferences (Round 3)

All skills in `.claude/skills/` are always available; this round is about which ones you want to lean on, and how proactive Claude should be.

```
AskUserQuestion:

Q1: "Which skills do you expect to use most?" (header: "Skills", multiSelect: true)
  - "/plan-interview — get interviewed hard to turn a rough idea into a step-by-step plan"
  - "/wrap — autonomous session close (review, commit, memory)"
  - "/tdd — red → green test-driven implementation"
  - "/code-review — two-axis (standards + spec) review of a diff"
  - "/diagnosing-bugs — structured loop for hard bugs and regressions"
  - "/codebase-design & /domain-modeling — architecture + domain language"
  - "/improve-codebase-architecture — scan for deepening opportunities"
  - "/handoff & /loop-me — session handoff and workflow specs"
  - "/save-conversation — export a verbatim session transcript"
  - "All of them (recommended)"

Q2: "Should I auto-trigger skills or wait for you?" (header: "Auto-trigger")
  - "Auto-trigger — e.g. suggest /plan-interview before a big build, /code-review after a feature"
  - "Manual only — I'll call skills when I want them"
  - "Auto for safety (plan before risky work), manual for the rest"

Q3: "How should I communicate?" (header: "Communication")
  - "Terse — just do the work, minimal commentary"
  - "Explain as you go — I want to understand the changes"
  - "Ask me before decisions — I want to approve everything"

Q4: "Session memory — how much should I remember?" (header: "Memory")
  - "Everything — decisions, progress, preferences, patterns"
  - "Just preferences and feedback — skip session logs"
  - "Minimal — only remember what I explicitly ask you to"
```

## Phase 4: Initial Scaffold

After questionnaires, prep the repo:

1. **Fill CLAUDE.md** with selected stack, commit policy, communication style.
2. **Pre-populate the project commands** in CLAUDE.md "Quick Start" / "Existing Tooling" based on the chosen stack (e.g., `npm test` for Node, `pytest` for Python). Mark them as defaults the user should adjust once they pick concrete tools.
3. **Configure permissions** — add stack-appropriate `Bash(...)` allow entries.
4. **Set default branch** in CLAUDE.md to `main` (greenfield default; user can change).

5. **Report:**

```
=== Setup Complete (greenfield) ===

  Project type:  [stack]
  Commit policy: [chosen]
  Communication: [chosen]
  Skills favored: [list]
  Risk surfaces seeded: [from Q1]
  Next: Describe your first feature — run /plan-interview to turn it into a
        step-by-step plan, then build it, using /tdd if you chose test-first.
===
```

## Phase 5: Optional Extras (Round 4)

```
AskUserQuestion:

Q: "Want any of these extras?" (header: "Extras", multiSelect: true)
  - "Hard git guardrails — block push/reset --hard/clean/branch -D via a hook (runs the /git-guardrails skill)"
  - "Obsidian vault integration — let Claude read/write your notes vault (/obsidian-vault)"
  - "Session transcripts — remember /save-conversation for a verbatim record"
  - "None — the basics are fine"
```

Configure selected extras. For "Hard git guardrails", run the `git-guardrails` skill.

---

## Key Rules

- **Route first**: existing → the Existing-Project Scan, fresh → questionnaire. Never run greenfield questions against an existing codebase — that's what the scan exists to prevent.
- **Never skip questionnaires** in the greenfield track — the whole point is guided setup.
- **Save answers to memory** so future sessions know the pr