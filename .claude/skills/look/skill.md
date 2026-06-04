---
name: look
description: "TRIGGER PROACTIVELY after completing any UI/CSS/HTML task, or when user says 'check the app', 'how does it look', 'show me'. Console errors + state checks always, screenshot only for visual changes. Reads CLAUDE.md Service/URL map to inspect the right endpoint when projects have multiple services."
argument-hint: "[service-name | route | service:route | all]"
---

# Look — Visual QA

Inspect the running app in the browser. Zero user prompts — runs autonomously.

**Auto-trigger after:** Any task that touched HTML, CSS, templates, or UI rendering.
**Manual trigger:** User says "check the app", "how does it look", "show me".

## Step 0: Load CLAUDE.md Service / URL map

CLAUDE.md "Service / URL map" lists named services with their URLs. If the map has more than one entry, `$ARGUMENTS` selects which:

| `$ARGUMENTS` | Behavior |
|--------------|----------|
| *(empty)* | Inspect the first service in the map (typically frontend) |
| `frontend` / `api` / `admin` / any service name | Inspect that service's URL |
| `/route` (starts with `/`) | Append to the default service's URL |
| `service:/route` | Append the route to the named service |
| `all` | Cycle through every service in the map |

If no Service/URL map exists in CLAUDE.md, fall back to `http://localhost:[PORT]` where PORT comes from `package.json` scripts, Dockerfile EXPOSE, or `.env` — note in report which assumption was used.

## Execution

### 1. Ensure App Running (silent)

Check the target service:
```bash
curl -s -m 2 <url> >/dev/null 2>&1
```

If not responding, note it and suggest the user starts the service (mention the Service / URL map's `Started by` column). Don't auto-start.

### 2. Navigate

If a route was provided, use `browser_navigate` to go there. Otherwise use the service URL root.

Use `browser_snapshot` first to understand the current page state.

### 3. Console Error Check (always)

Call `browser_console_messages` to catch JS exceptions and errors.

Also run via `browser_evaluate`:
```js
(function() {
  const errors = [];
  document.querySelectorAll('.error, .alert-danger, [role="alert"]').forEach(el => {
    if (el.offsetParent !== null) errors.push('Visible error: ' + el.textContent.trim().slice(0, 100));
  });
  return { errors, url: location.href, title: document.title };
})()
```

### 4. State Checks (always)

```js
(function() {
  const checks = {};
  checks.readyState = document.readyState;
  checks.brokenImages = [...document.images].filter(img => !img.complete || img.naturalWidth === 0).length;
  const badValues = [];
  document.querySelectorAll('*').forEach(el => {
    if (el.children.length === 0) {
      const t = el.textContent.trim();
      if (t === 'NaN' || t === 'undefined' || t === 'null') badValues.push(el.tagName + ': ' + t);
    }
  });
  checks.badValues = badValues.slice(0, 10);
  return checks;
})()
```

### 5. Screenshot (conditional)

Take a screenshot ONLY if ANY of these are true:
- The task that triggered /look touched CSS, HTML, or template code
- Console errors were found in step 3
- State checks found issues in step 4
- User explicitly said "show me", "screenshot", "how does it look"

If screenshotting: use `browser_take_screenshot` and analyze visually.

If NOT screenshotting: skip — console/state data is sufficient.

### 6. Report

**If clean (no issues):**
```
App OK — [service name | page title], 0 errors, 0 broken images
```

**If issues found:**
```
App Issues ([service name]):
  - [console error description]
  - [broken image or bad value]
  Screenshot: [taken/skipped]
```

**For `all` mode:**
```
Services:
  frontend (http://localhost:5173)  OK  — 0 errors
  api (http://localhost:3000/health) OK  — 200
  admin (http://localhost:4000)     DOWN — connection refused
```

## Key Rules

- **Zero user prompts.** Read-only inspection.
- **Service-aware** — read CLAUDE.md URL map, support `service:/route` syntax.
- **Screenshot is expensive** — only take when visual verification matters.
- **Console + state checks are cheap** — always run them.
- **Report in 1-3 lines** unless issues found.
- **When triggered proactively** (after a task), keep it fast.
- **Requires Playwright MCP** — if not available, fall back to curl + basic checks only.
