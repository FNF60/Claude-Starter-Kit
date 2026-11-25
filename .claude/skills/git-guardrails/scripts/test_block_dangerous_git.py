#!/usr/bin/env python3
"""Self-test for block-dangerous-git.py. Run:  python test_block_dangerous_git.py
Exit code 0 = every case behaved as expected. Run it again after editing the hook."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parent / "block-dangerous-git.py"

spec = importlib.util.spec_from_file_location("hook", HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

# Blocked whatever the commit policy.
ALWAYS_BLOCK = [
    "git push",
    "git push --force origin main",
    "cd foo && git push",
    "git -C 'C:/some dir/repo' push",
    "git -c user.name=a push",
    "git reset --hard HEAD~1",
    "git clean -fd",
    "git clean -xf",
    "git branch -D old",
    "git checkout .",
    "git checkout -f main",
    "git restore .",
    "git restore --worktree .",
    'bash -c "git push origin x"',
    "powershell -Command git push",
    '& git push',
    '& "C:\\Program Files\\Git\\cmd\\git.exe" push',
    "GIT_SSH_COMMAND=ssh git push",
    "git.exe push",
    "echo hi\ngit push",
]

# Blocked only when COMMIT_POLICY is "stage-only".
STAGE_ONLY_BLOCK = [
    "git commit -m 'x'",
    "git commit --amend",
    "git -C repo commit -m x",
    "git add a.txt; git commit -m x",
    "git rebase main",
    "git am patch.mbox",
    "git cherry-pick abc123",
    "git revert abc123",
    'pwsh -NoProfile -Command "git commit -m x"',
    "git commit -m \"it's fine\" && echo done",
]

# Never blocked.
ALLOW = [
    "git status",
    "git log --oneline -5",
    "git log --grep='git push'",
    "git diff HEAD~1",
    "git add docs/a.md",
    "git branch --list",
    "git branch -d merged",
    "git checkout -b new-branch",
    "git checkout main",
    "git checkout -- file.txt",
    "git restore --staged .",
    "git restore file.txt",
    "git clean -n",
    "git reset HEAD file",
    "git cherry-pick --no-commit abc",
    "git revert -n abc",
    "git merge --no-commit other",
    "git stash list",
    "git -C 'C:/some dir/repo' status --short",
    "echo git push",
    "echo 'git commit' > note.txt",
    "grep -rn 'git push' docs",
    "ls -la",
    "gh pr create --title push",
    "Get-Content notes.txt | Select-String 'git push'",
]

# Quoting that depends on the shell running the command: (shell, command, expect_blocked).
# Bash escapes a quote with a backslash; PowerShell with a backtick, and there "\" is plain text.
SHELL_CASES = [
    ("bash", r'grep -n "a\|\"x\|git push" f.txt', False),  # escaped quote kept the string open
    ("bash", r'echo "say \"hi\"" ; git push', True),
    ("bash", r'echo a\;git push', False),                   # escaped ';' is not a separator
    ("bash", r'bash -c "echo \"x\"; git push"', True),
    ("powershell", r'Write-Output "C:\dir\"; git push', True),  # \" does not escape in PowerShell
    ("powershell", 'Write-Output "a`"; git push"', False),      # `" does
    ("powershell", r'Select-String -Pattern "x\" | git push"', True),
    ("bash", 'cmd /c git push', True),
    ("bash", 'cmd.exe /c "git commit -m x"', True),
]

failures = 0


def check(command, expect_blocked, policy, shell="bash"):
    global failures
    hook.COMMIT_POLICY = policy
    blocked = hook.check_command(command, 0, shell) is not None
    if blocked != expect_blocked:
        failures += 1
        print("FAIL [%s/%s] expected %s: %r" % (policy, shell, "BLOCK" if expect_blocked else "ALLOW", command))


for policy in ("stage-only", "auto-commit"):
    for shell in ("bash", "powershell"):
        for c in ALWAYS_BLOCK:
            check(c, True, policy, shell)
        for c in ALLOW:
            check(c, False, policy, shell)
for c in STAGE_ONLY_BLOCK:
    check(c, True, "stage-only")
    check(c, False, "auto-commit")
for shell, c, expected in SHELL_CASES:
    check(c, expected, "stage-only", shell)

# End to end through the real entry point (JSON on stdin, exit code), default policy.
hook.COMMIT_POLICY = "stage-only"


def run(payload_text):
    return subprocess.run([sys.executable, str(HOOK)], input=payload_text, capture_output=True, text=True).returncode


if run(json.dumps({"tool_input": {"command": "git push origin main"}})) != 2:
    failures += 1
    print("FAIL end-to-end: git push was not blocked with exit code 2")
if run(json.dumps({"tool_input": {"command": "git status"}})) != 0:
    failures += 1
    print("FAIL end-to-end: git status was blocked")
if run("not json") != 0:
    failures += 1
    print("FAIL end-to-end: unreadable input must not block")
ps_trap = 'Write-Output "C:\\dir\\"; git push'
if run(json.dumps({"tool_name": "PowerShell", "tool_input": {"command": ps_trap}})) != 2:
    failures += 1
    print("FAIL end-to-end: PowerShell tool name did not switch to PowerShell quoting")
if run(json.dumps({"tool_name": "Bash", "tool_input": {"command": r'grep "a\"x|git push" f'}})) != 0:
    failures += 1
    print("FAIL end-to-end: Bash escaped quote still a false positive")

print("always-block %d, stage-only %d, allow %d, shell %d, failures %d" % (len(ALWAYS_BLOCK), len(STAGE_ONLY_BLOCK), len(ALLOW), len(SHELL_CASES), failures))
sys.exit(1 if failures else 0)
