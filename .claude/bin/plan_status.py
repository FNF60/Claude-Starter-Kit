#!/usr/bin/env python3
"""
Plan Status Scanner

Scans plan documents from multiple sources:
  - .claude/plans/*.md           (kit-managed plans from /plan tier 2-3)
  - TODO.md (repo root)
  - ROADMAP.md / docs/roadmap.md
  - docs/plans/*.md

External issue trackers (Linear, Jira, GitHub Issues) are NOT scanned here —
they're noted in the output with a hint to use the appropriate MCP if desired.

Usage:
    python plan_status.py [--json] [--stale-days N] [--include-external]

Options:
    --json                Output raw JSON instead of formatted table
    --stale-days N        Configure staleness threshold (default: 14 days)
    --include-external    Note external trackers detected (no fetch, just hint)
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path


def get_repo_root():
    """Walk up from the script's location to find the repo root."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".claude").is_dir() or (current / ".git").is_dir():
            return str(current)
        current = current.parent
    return os.getcwd()


def extract_status_field(content, field_name):
    """Extract a 'Field: value' line from plan markdown."""
    for line in content.split('\n'):
        if line.startswith(f"{field_name}:"):
            value = line.split(":", 1)[1].strip()
            if value:
                return value
        # Also accept bold markdown: **Field:** value
        if line.startswith(f"**{field_name}:**"):
            value = line.split("**", 2)[2].strip()
            if value.startswith(":"):
                value = value[1:].strip()
            if value:
                return value
    return None


def extract_scope(content, max_chars=60):
    """Extract Scope field or fall back to first heading body line."""
    scope = extract_status_field(content, "Scope") or extract_status_field(content, "Goal")
    if scope and len(scope) > max_chars:
        return scope[:max_chars] + "..."
    return scope


def collect_plan_files(repo_root):
    """Collect plan files from all known local sources."""
    plans = []
    root = Path(repo_root)

    # Kit-managed plans
    claude_plans_dir = root / ".claude" / "plans"
    if claude_plans_dir.exists():
        for md_file in sorted(claude_plans_dir.glob("*.md")):
            plans.append(('kit', md_file))

    # Top-level TODO and roadmap files
    for name in ("TODO.md", "ROADMAP.md"):
        candidate = root / name
        if candidate.exists():
            plans.append(('repo-root', candidate))

    # docs/ planning files
    for path in (root / "docs" / "roadmap.md",
                 root / "docs" / "ROADMAP.md"):
        if path.exists():
            plans.append(('docs', path))

    docs_plans = root / "docs" / "plans"
    if docs_plans.exists():
        for md_file in sorted(docs_plans.glob("*.md")):
            plans.append(('docs/plans', md_file))

    return plans


def detect_external_trackers(repo_root):
    """Detect signals that an external issue tracker is in use. No fetching."""
    root = Path(repo_root)
    detected = []

    # Linear
    if (root / ".linearrc").exists() or any(root.glob(".linear*")):
        detected.append("Linear (config detected)")
    # Jira (CONTRIBUTING.md hints or commit messages with [PROJ-NN] pattern - rough)
    contributing = root / "CONTRIBUTING.md"
    if contributing.exists():
        try:
            text = contributing.read_text(encoding='utf-8', errors='ignore').lower()
            if 'jira' in text:
                detected.append("Jira (mentioned in CONTRIBUTING.md)")
            if 'linear' in text and "Linear (config detected)" not in detected:
                detected.append("Linear (mentioned in CONTRIBUTING.md)")
        except Exception:
            pass
    # GitHub Issues — assume yes if .github/ exists and project is on GitHub
    if (root / ".github").exists() or (root / ".github" / "ISSUE_TEMPLATE").exists():
        detected.append("GitHub Issues (.github/ present)")

    return detected


def prettify_filename(filename):
    name = Path(filename).stem
    return name.replace('_', ' ').replace('-', ' ').title()


def format_relative_time(mtime):
    now = datetime.now()
    mod_time = datetime.fromtimestamp(mtime)
    delta = now - mod_time
    days = delta.days
    if days == 0:
        return "today"
    elif days == 1:
        return "1d ago"
    elif days < 7:
        return f"{days}d ago"
    elif days < 30:
        return f"{days // 7}w ago"
    else:
        return f"{days // 30}mo ago"


def get_line_count(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    except Exception:
        return 0


def scan_plans(repo_root, stale_days=14):
    plan_entries = collect_plan_files(repo_root)
    plans_data = []
    now = datetime.now()
    stale_threshold = timedelta(days=stale_days)

    for source, plan_file in plan_entries:
        try:
            with open(plan_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            mtime = os.path.getmtime(plan_file)
            mod_time = datetime.fromtimestamp(mtime)
            is_stale = (now - mod_time) > stale_threshold

            plans_data.append({
                'name': prettify_filename(plan_file.name),
                'filename': plan_file.name,
                'source': source,
                'path': str(plan_file),
                'status': extract_status_field(content, 'Status'),
                'created': extract_status_field(content, 'Created') or extract_status_field(content, 'Date'),
                'scope': extract_scope(content, 60),
                'modified': format_relative_time(mtime),
                'mtime': mtime,
                'lines': get_line_count(plan_file),
                'is_stale': is_stale,
                'stale_days': (now - mod_time).days,
            })
        except Exception as e:
            print(f"Error processing {plan_file}: {e}", file=sys.stderr)

    plans_data.sort(key=lambda x: x['mtime'], reverse=True)
    return plans_data


def format_status_display(status):
    return status if status is not None else "[no status]"


def print_table(plans_data, externals, stale_days=14):
    if not plans_data and not externals:
        print("No plans found.")
        return

    if plans_data:
        print(f"PLAN STATUS ({len(plans_data)} plans)\n")
        name_w = max(30, max(len(p['name']) for p in plans_data))
        status_w = max(20, max(len(format_status_display(p['status'])) for p in plans_data))
        src_w = max(10, max(len(p['source']) for p in plans_data))

        print(f"  {'Name':<{name_w}}  {'Source':<{src_w}}  {'Status':<{status_w}}  {'Modified':<12}  {'Lines':<6}")
        print(f"  {'-' * name_w}  {'-' * src_w}  {'-' * status_w}  {'-' * 12}  {'-' * 6}")

        for plan in plans_data:
            print(f"  {plan['name']:<{name_w}}  {plan['source']:<{src_w}}  {format_status_display(plan['status']):<{status_w}}  {plan['modified']:<12}  {plan['lines']:>5} L")

        stale = [p for p in plans_data if p['is_stale']]
        if stale:
            print(f"\nStale (not modified in {stale_days}+ days): {', '.join(p['name'] for p in stale)}")

    if externals:
        print("\nExternal trackers detected (not fetched here):")
        for hint in externals:
            print(f"  - {hint}")
        print("  Hint: install the relevant MCP connector to query these from Claude.")


def print_json(plans_data, externals):
    output = {
        'plans': [
            {k: v for k, v in p.items() if k != 'mtime'} for p in plans_data
        ],
        'external_trackers_detected': externals,
    }
    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Scan and display plan document status from multiple local sources')
    parser.add_argument('--json', action='store_true', help='Output raw JSON instead of formatted table')
    parser.add_argument('--stale-days', type=int, default=14, help='Staleness threshold in days (default: 14)')
    parser.add_argument('--include-external', action='store_true', help='Note external trackers detected (no fetch)')
    args = parser.parse_args()

    repo_root = get_repo_root()
    plans_data = scan_plans(repo_root, args.stale_days)
    externals = detect_external_trackers(repo_root) if args.include_external else []

    if args.json:
        print_json(plans_data, externals)
    else:
        print_table(plans_data, externals, args.stale_days)


if __name__ == '__main__':
    main()
