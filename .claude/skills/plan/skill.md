---
name: plan
description: "TRIGGER when user says 'plan', 'let me think about', 'how should we build', 'design this', or describes a feature they want to plan before building. Structured planning with 3 intensity tiers. ALWAYS starts with intake questionnaire via AskUserQuestion. Reads CLAUDE.md Architecture and Conventions so plans follow existing patterns."
argument-hint: "[feature description]"
---

# Plan — Tiered Feature Planning

Plan a feature before building it. **Always starts with an intake questionnaire** — never auto-detect tier or assume scope. For existing projects, **read CLAUDE.md first** so the questionnaire and the plan can reference real modules instead of inventing new ones.

## Step 0: Load project context (before any question)

Read these from CLAUDE.md:
- **Architecture** — directories and roles, for the Domain question
- **Key Conventions / Code Style** — to fold into the plan
- **Risk Surfaces** — to flag if the feature touches them
- **Don't Touch** — to refuse plans that target those paths
- **Module Ownership** — for cross-team awareness

If CLAUDE.md is missing or all-placeholder, ask the user to run `/onboard` first, or proceed with a flag that the plan will be generic.

## Step 1: Intake Questionnaire (MANDATORY)

Use `AskUserQuestion` with up to 4 questions per call. Chain multiple rounds.

### Round 1 — Scope & Intensity

```
AskUserQuestion:

Q1: "What are you building?" (header: "Feature")
  - Options based on what the user said, reworded into 2-3 concrete interpretations
  - Always include "Other" (built-in)

Q2: "How deep should we plan this?" (header: "Intensity")
  - "Tier 1 — Quick" / "30-sec scan, bullets in chat, then build"
  - "Tier 2 — Detailed" / "Explore codebase, write plan file, design decisions before coding"
  - "Tier 3 — Architectural" / "Full spec: phases, schema, research, compatibility notes"

Q3: "Which area does this touch?" (header: "Domain", multiSelect: true)
  - Pull options from CLAUDE.md Architecture table (real module names)
  - Add "New module — doesn't fit existing structure" as the last option

Q4: "Any constraints I should know?" (header: "Constraints", multiSelect: true)
  - "Performance-critical (hot path)"
  - "Touches a Risk Surface listed in CLAUDE.md"
  - "Must maintain backward compatibility"
  - "Has a deadline / time-boxed"
  - "No constraints"
```

If a chosen Domain is in CLAUDE.md "Don't Touch", **stop and ask the user to confirm** before proceeding. If a chosen constraint is "Touches a Risk Surface", auto-bump to Tier 2 minimum.

### Round 1.5 — Pattern Reuse (existing projects only, skip if Domain is "New module")

This is the round that prevents Claude from reinventing patterns the project already has. Pull 2-4 existing modules that resemble what's being built (same Domain area) and ask:

```
AskUserQuestion:

Q1: "Which existing module is the closest analog?" (header: "Pattern")
  - "src/[module-a] — [one-line description]"
  - "src/[module-b] — [one-line description]"
  - "src/[module-c] — [one-line description]"
  - "None close enough — design from scratch"

Q2: "What should the new feature inherit from the analog?" (header: "Inherit", multiSelect: true)
  - "File organization and naming"
  - "Error handling style"
  - "Test structure"
  - "Public API shape"
  - "Logging / observability"
  - "None — same domain but new style"
```

Record the chosen analog in the plan. Other skills will use it as a reference when implementing.

### Round 2 — Design Preferences (Tier 2-3 only)

After Round 1 (and 1.5 if existing), if Tier 2 or 3 was selected, ask a second round tailored to the specific feature. **Concrete design forks**, not generic. Examples:

```
AskUserQuestion:

Q1: "Where should this live?" (header: "Placement")
  - Option A with description (path, why it fits)
  - Option B with description

Q2: "Data source?" (header: "Data")
  - "Use existing data (no API changes)"
  - "New data source required"
  - "Computed from existing data"

Q3: "How should it interact with existing features?" (header: "Integration")
  - "Standalone — new module, no dependencies"
  - "Extends existing module ([chosen analog])"
  - "Replaces existing implementation"
```

Use **previews** on options whenever comparing layouts, code approaches, or visual designs.

### Round 3 — Priorities & Tradeoffs (Tier 3 only)

```
AskUserQuestion:

Q1: "What's the priority order for this feature?" (header: "Priority")
  - "Ship fast, polish later"
  - "Get it right first time, take longer"
  - "MVP now, iterate based on usage"

Q2: "Phase boundaries — where can we stop and still have something useful?" (header: "Phases")
  - Option A: "[phase 1 scope] is useful alone"
  - Option B: "[phase 1+2 scope] is the minimum viable"
  - Option C: "All-or-nothing, partial doesn't help"
```

---

## After Intake: Execute the Chosen Tier

### Tier 1 — Quick Plan (30 seconds)

**For:** Small features, bug fixes, UI tweaks, single-file changes.

1. **Scan** (parallel, fast):
   - Grep for related code in the chosen Domain
   - Identify affected files and line ranges
   - Check if the chosen analog has patterns to follow

2. **Present** — a compact plan directly in chat (no plan file):

```
## Plan: [feature name]
**Tier:** 1 (Quick) | **Files:** [list] | **~Lines:** [estimate] | **Analog:** [module or "none"]

### Changes
1. [what] in [file] (~line N)
2. [what] in [file] (~line N)

### Follows from analog
- [pattern reused]

### Risks
- [any gotchas, or "None"]
```

3. **Confirm** via `AskUserQuestion`:
   - "Good to build?" -> "Yes, go" / "Adjust something" / "Upgrade to Tier 2"

---

### Tier 2 — Detailed Plan (2-5 minutes)

**For:** Medium features, refactors, new modules, multi-file changes.

1. **Enter Plan Mode** — Call `EnterPlanMode`

2. **Explore** (use Explore agent or direct reads):
   - Read files in the chosen Domain and the chosen analog
   - Map dependencies
   - Identify integration points
   - Note conventions from CLAUDE.md to follow

3. **Design Decisions** — Use `AskUserQuestion` for every fork:
   - Placement (with previews)
   - Data flow alternatives
   - Naming
   - **Never guess — always ask. 2-4 concrete options each.**

4. **Write Plan** to `.claude/plans/[feature-name].md`:

```markdown
# Plan: [Feature Name]

**Tier:** 2 (Detailed)
**Date:** [YYYY-MM-DD]
**Status:** Draft
**Analog:** [module path or "none"]

## Goal
[1-2 sentences — what and why]

## User Decisions
- [Decision 1]: [what user chose]
- [Decision 2]: [what user chose]

## Pattern Inheritance (from analog)
- [list of items from Round 1.5 Q2]

## File Impact Map
| File | Change Type | Lines (est.) |
|------|------------|-------------|
| [path] | modify     | ~20         |
| [path] | new        | ~80         |

## Risk Surfaces touched
- [list, or "None"]

## Implementation Steps
1. [ ] [Step with specific detail — what function, what data]
2. [ ] [Step]

## Data Flow
[How data moves: input -> transform -> output]

## Risks & Mitigations
- [Risk]: [Mitigation]

## Testing
- [How to verify]
```

5. **Exit Plan Mode** — Call `ExitPlanMode` for user approval

6. **After approval** — Convert plan steps into TodoWrite tasks and start building.

---

### Tier 3 — Architectural Plan (5-10 minutes)

**For:** Large features, breaking changes, schema changes, many files.

1-5. **Everything from Tier 2**, plus:

6. **Phased Implementation** using Round 3's phase-boundary answer:

```markdown
## Phases

### Phase 1: [name] (~session 1)
- [ ] [core structures]
- **Checkpoint:** [what should work]
- **Shippable alone?** [yes/no]

### Phase 2: [name] (~session 1-2)
- [ ] [wire in]
- **Checkpoint:** [what should work]

### Phase 3: [name] (~session 2)
- [ ] [edge cases, tests, polish]
- **Checkpoint:** [feature complete]
```

7. **Compatibility Notes**:
   - What breaks if this ships half-done?
   - Can phases ship independently?
   - Backward compatibility with existing data/config?
   - Module Ownership: are reviewers across the touched files all available?

8. **Write Plan** to `.claude/plans/[feature-name].md`

9. **Final Review** via `AskUserQuestion`:
   - "Plan looks complete. Ready to build?" -> "Yes, start Phase 1" / "Revise [section]" / "Save plan, build later"

10. **Exit Plan Mode** for approval

---

## Key Rules

- **ALWAYS start by loading CLAUDE.md context** — Architecture, Risk Surfaces, Don't Touch.
- **ALWAYS start with intake questionnaire** — never skip, never auto-detect without asking.
- **Round 1.5 (pattern reuse) is non-negotiable for existing projects** — this is what prevents reinventing patterns.
- **Use AskUserQuestion liberally** — every design fork, every ambiguity, every tradeoff.
- **Use previews** on options whenever comparing visual layouts, code patterns, or architectures.
- **Tier 1 never creates a plan file** — chat-only, fast, disposable.
- **Tier 2-3 always save to `.claude/plans/`** — persistent, referenceable.
- **Never start coding before the plan is approved** (Tier 2-3).
- **Record user decisions in the plan file** — so future sessions know what was chosen and why.
- **If the user says "just build it"** during planning — stop planning, switch to building.
- **Chain AskUserQuestion rounds** — don't dump 8 questions at once. 3-4 per round.
- **Refuse plans that target Don't Touch paths** without explicit confirmation.
- **Auto-bump to Tier 2 minimum if a Risk Surface is touched.**
