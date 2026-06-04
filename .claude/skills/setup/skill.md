---
name: setup
description: "TRIGGER on first conversation in a project, or when user says 'setup', 'configure', 'customize this'. Routes to /onboard for existing codebases or runs the greenfield questionnaire for new ones. Tailors CLAUDE.md, hooks, permissions, skills, and agents to this specific project."
---

# Setup — Project Configuration

Two paths through this skill. Pick the right one in Phase 0 and don't ask redundant questions.

## Phase 0: Route — new or existing?

**Before any other question**, check whether the project has content:

```bash
git ls-files | head -1
ls -la
```

- If there are tracked source files **other than** `README.md` / `LICENSE` / `.gitignore` / `CLAUDE.md` / `.claude/`: it's an **existing project** → call `/onboard` and stop. `/onboard` will run its own questionnaire and produce the artifacts setup would have. Setup is done.
- If there are no source files yet (or only the kit's own files + README/LICENSE): it's a **new project** → continue with Phase 1 below.

If ambiguous, ask one question:

```
AskUserQuestion:
Q: "Is this a fresh start or an existing codebase?" (header: "Project state")
  - "Fresh start — no code yet, plan and build from zero"
  - "Existing — there's already code I want Claude to learn"
  - "Hybrid — some code, but mostly new direction"
```

`Existing` and `Hybrid` both route to `/onboard`. `Fresh` continues here.

---

## Greenfield Track (no existing code)

Walk the user through structured questionnaires to configure CLAUDE.md, hooks, permissions, skills, and agents.

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
  - "Full test suite (jest, pytest, etc.) — run on every change"
  - "Some tests — run manually"
  - "No tests yet — help me set them up"
  - "No tests needed for this project"

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
- Update `.claude/settings.json` permissions based on answers
- Write the chosen commit policy into CLAUDE.md "Commit & Workflow Policy"
- "Push to default branch" guardrail → keep the kit's push hook active
- "Commit secrets" guardrail → enable a secret-scan pre-commit hook (note in settings)

## Phase 3: Workflow Preferences (Round 3)

```
AskUserQuestion:

Q1: "Which skills do you want active?" (header: "Skills", multiSelect: true)
  - "/plan — Feature planning with intensity tiers"
  - "/wrap — Autonomous session close"
  - "/check — Post-build health validation"
  - "/guard — Pre-edit safety check"
  - "/diff — Smart change review with risk levels"
  - "/undo — Targeted rollback with safety nets"
  - "/look — Visual QA with Playwright"
  - "All of them (recommended)"

Q2: "Should I auto-trigger skills or wait for you?" (header: "Auto-trigger")
  - "Auto-trigger — run /check after builds, /guard before risky edits"
  - "Manual only — I'll call skills when I want them"
  - "Auto for safety (/guard, /check), manual for planning"

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

  Project type: [stack]
  Commit policy: [chosen]
  Communication: [chosen]
  Skills active: [list]
  Risk surfaces seeded: [from Q1]
  Next: Use /plan to design your first feature.
===
```

## Phase 5: Optional Extras (Round 4)

```
AskUserQuestion:

Q: "Want any of these extras?" (header: "Extras", multiSelect: true)
  - "Additional agents (error-trap-monitor, security-reviewer run proactively)"
  - "Playwright visual QA (/look skill with browser screenshots)"
  - "Custom hooks (auto-lint on save, auto-test on commit)"
  - "None — the basics are fine"
```

Configure selected extras.

---

## Key Rules

- **Route first**: existing → `/onboard`, fresh → questionnaire. Never run greenfield questions against an existing codebase — that's what `/onboard` exists to prevent.
- **Never skip questionnaires** in the greenfield track — the whole point is guided setup.
- **Save answers to memory** so future sessions know the project context.
- **Update files based on answers** — don't just ask and forget. CLAUDE.md, settings.json, and skill descriptions should reflect the user's choices.
- **Re-runnable** — if the user re-runs setup, route again in Phase 0. For existing projects, prefer `/onboard --refresh` over re-running setup.
