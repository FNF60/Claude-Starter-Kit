#!/usr/bin/env python3
"""
Claude Code Starter Kit — installer.

Copies the kit into a target project directory with conflict awareness:
- Detects existing CLAUDE.md, .claude/, and other AI tooling configs
- Shows diffs and offers merge / replace / skip / abort per file
- After install, prints a one-liner for the user to run /onboard or /setup

Usage:
    python install.py [target_dir]
    python install.py --dry-run [target_dir]
    python install.py --force [target_dir]    # take kit version on every conflict (DANGEROUS)

Default target_dir is the current working directory.
"""

import argparse
import difflib
import json
import os
import shutil
import sys
from pathlib import Path


# Files the kit ships. Paths are relative to the kit's own directory.
KIT_FILES = [
    "CLAUDE.md",
    ".claude/settings.json",
    ".claude/SETTINGS_NOTES.md",
    ".claude/bin/plan_status.py",
    ".claude/bin/save_conversation.py",
    ".claude/skills/onboard/skill.md",
    ".claude/skills/setup/skill.md",
    ".claude/skills/plan/skill.md",
    ".claude/skills/wrap/skill.md",
    ".claude/skills/check/skill.md",
    ".claude/skills/guard/skill.md",
    ".claude/skills/diff/skill.md",
    ".claude/skills/undo/skill.md",
    ".claude/skills/look/skill.md",
    ".claude/skills/save-conversation/SKILL.md",
    ".claude/agents/code-reviewer.md",
    ".claude/agents/error-trap-monitor.md",
    ".claude/agents/security-reviewer.md",
    ".claude/plans/.gitkeep",
]

# Other AI tooling configs we want to surface — not to overwrite, just to mention.
KNOWN_AI_CONFIGS = [
    ".cursorrules",
    ".cursor/rules",
    ".aider.conf.yml",
    ".github/copilot-instructions.md",
    ".continue",
    ".windsurfrules",
    "AGENTS.md",
]


def kit_root():
    return Path(__file__).resolve().parent


def detect_existing_ai_tooling(target):
    found = []
    for p in KNOWN_AI_CONFIGS:
        if (target / p).exists():
            found.append(p)
    return found


def show_diff(existing_text, new_text, label):
    diff = difflib.unified_diff(
        existing_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile=f"{label} (yours)",
        tofile=f"{label} (kit)",
        n=3,
    )
    sys.stdout.writelines(diff)


def prompt(message, choices, default=None):
    """Tiny CLI prompt. choices is a list of (key, label) tuples."""
    while True:
        print()
        print(message)
        for k, lbl in choices:
            marker = "*" if k == default else " "
            print(f"  [{k}]{marker} {lbl}")
        raw = input("> ").strip().lower()
        if not raw and default is not None:
            return default
        for k, _ in choices:
            if raw == k or raw == k[0]:
                return k
        print("Try one of:", ", ".join(k for k, _ in choices))


def merge_json_settings(existing, new):
    """Shallow-merge .claude/settings.json. Lists in permissions are union-merged
    (preserving order, kit entries appended after user entries). Hooks are
    appended (user hooks come first); duplicates by exact-equal dict are skipped."""
    result = json.loads(json.dumps(existing))  # deep copy

    # Permissions
    if 'permissions' in new:
        result.setdefault('permissions', {})
        for key in ('allow', 'deny', 'ask'):
            ex_list = result['permissions'].get(key, []) or []
            new_list = new['permissions'].get(key, []) or []
            seen = set(ex_list)
            merged = list(ex_list)
            for item in new_list:
                if item not in seen:
                    merged.append(item)
                    seen.add(item)
            result['permissions'][key] = merged

    # Hooks
    if 'hooks' in new:
        result.setdefault('hooks', {})
        for event, new_handlers in new['hooks'].items():
            ex_handlers = result['hooks'].get(event, []) or []
            seen_serialized = {json.dumps(h, sort_keys=True) for h in ex_handlers}
            merged = list(ex_handlers)
            for h in new_handlers:
                if json.dumps(h, sort_keys=True) not in seen_serialized:
                    merged.append(h)
            result['hooks'][event] = merged

    return result


def install_file(kit_path, target_path, kit_text, args):
    """Handle a single file install. Returns one of: 'installed', 'merged', 'skipped', 'aborted'."""
    if not target_path.exists():
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if args.dry_run:
            print(f"  [dry-run] would create {target_path}")
            return 'installed'
        target_path.write_text(kit_text, encoding='utf-8')
        print(f"  created {target_path.relative_to(args.target)}")
        return 'installed'

    # File exists — decide
    existing_text = target_path.read_text(encoding='utf-8', errors='ignore')
    if existing_text == kit_text:
        print(f"  unchanged {target_path.relative_to(args.target)}")
        return 'skipped'

    rel = target_path.relative_to(args.target)
    print(f"\nConflict: {rel}")

    if args.force:
        if args.dry_run:
            print(f"  [dry-run] would overwrite {rel} (--force)")
            return 'installed'
        target_path.write_text(kit_text, encoding='utf-8')
        print(f"  overwrote {rel} (--force)")
        return 'installed'

    # JSON merge path for settings.json
    if target_path.name == 'settings.json' and target_path.parent.name == '.claude':
        try:
            existing_json = json.loads(existing_text)
            new_json = json.loads(kit_text)
            merged = merge_json_settings(existing_json, new_json)
            merged_text = json.dumps(merged, indent=2)
            print("  options for settings.json:")
            choice = prompt(
                f"How to handle {rel}?",
                [
                    ('m', "Merge (union allow/deny/ask, append hooks)"),
                    ('d', "Show diff first"),
                    ('r', "Replace with kit version"),
                    ('s', "Skip"),
                    ('a', "Abort install"),
                ],
                default='m',
            )
            if choice == 'd':
                show_diff(existing_text, merged_text, str(rel))
                choice = prompt(
                    "After diff:",
                    [
                        ('m', "Apply merged version"),
                        ('r', "Replace with kit version instead"),
                        ('s', "Skip"),
                        ('a', "Abort"),
                    ],
                    default='m',
                )
            if choice == 'a':
                return 'aborted'
            if choice == 's':
                return 'skipped'
            if choice == 'r':
                if args.dry_run:
                    print(f"  [dry-run] would replace {rel}")
                    return 'installed'
                target_path.write_text(kit_text, encoding='utf-8')
                print(f"  replaced {rel}")
                return 'installed'
            # merge
            if args.dry_run:
                print(f"  [dry-run] would merge {rel}")
                return 'merged'
            target_path.write_text(merged_text, encoding='utf-8')
            print(f"  merged {rel}")
            return 'merged'
        except json.JSONDecodeError as e:
            print(f"  settings.json is not valid JSON ({e}); falling back to text handling")

    # Generic text file
    choice = prompt(
        f"How to handle {rel}?",
        [
            ('d', "Show diff"),
            ('r', "Replace with kit version"),
            ('s', "Skip (keep yours)"),
            ('a', "Abort install"),
        ],
        default='s',
    )
    if choice == 'd':
        show_diff(existing_text, kit_text, str(rel))
        choice = prompt(
            "After diff:",
            [
                ('r', "Replace with kit version"),
                ('s', "Skip (keep yours)"),
                ('a', "Abort"),
            ],
            default='s',
        )
    if choice == 'a':
        return 'aborted'
    if choice == 's':
        return 'skipped'
    if args.dry_run:
        print(f"  [dry-run] would replace {rel}")
        return 'installed'
    target_path.write_text(kit_text, encoding='utf-8')
    print(f"  replaced {rel}")
    return 'installed'


def main():
    parser = argparse.ArgumentParser(description="Install the Claude Code Starter Kit into a project.")
    parser.add_argument("target", nargs="?", default=".", help="Target project directory (default: cwd)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without writing")
    parser.add_argument("--force", action="store_true", help="Overwrite without prompting (DANGEROUS)")
    args = parser.parse_args()
    args.target = Path(args.target).resolve()

    if not args.target.exists():
        print(f"Target does not exist: {args.target}", file=sys.stderr)
        sys.exit(1)

    root = kit_root()
    print(f"Kit:    {root}")
    print(f"Target: {args.target}")
    if args.dry_run:
        print("Mode:   DRY RUN — no files will be written")
    if args.force:
        print("Mode:   --force — kit version will overwrite on every conflict")

    # Detect other AI tooling
    other_tooling = detect_existing_ai_tooling(args.target)
    if other_tooling:
        print("\nExisting AI tooling detected:")
        for p in other_tooling:
            print(f"  - {p}")
        print("These are NOT touched by the installer. /onboard will read them and surface their content.")
        choice = prompt(
            "Continue?",
            [('y', "Yes, install alongside"), ('n', "No, abort")],
            default='y',
        )
        if choice == 'n':
            print("Aborted.")
            sys.exit(0)

    summary = {'installed': 0, 'merged': 0, 'skipped': 0, 'aborted': 0}
    for rel in KIT_FILES:
        src = root / rel
        if not src.exists():
            print(f"  warning: kit file missing — {rel}")
            continue
        kit_text = src.read_text(encoding='utf-8', errors='ignore')
        dest = args.target / rel
        result = install_file(src, dest, kit_text, args)
        summary[result] = summary.get(result, 0) + 1
        if result == 'aborted':
            print("\nAborted by user.")
            sys.exit(0)

    print("\n=== Install summary ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\nNext step:")
    if any(p in other_tooling for p in (".cursorrules", "AGENTS.md")) or (args.target / "CLAUDE.md").exists():
        print("  Run /onboard in Claude Code — it will read your existing AI config and merge as needed.")
    else:
        print("  Run /setup in Claude Code — it will detect whether this is a fresh start or existing codebase.")

    print()


if __name__ == '__main__':
    main()
