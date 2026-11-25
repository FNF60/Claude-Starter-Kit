#!/usr/bin/env python3
"""PreToolUse hook for the Bash and PowerShell tools: blocks dangerous git commands.

Exit code 2 blocks the call and the message on stderr goes back to the model.

How it works: it splits the command into segments (on ; & | and newlines, outside quotes,
following the quoting rules of the shell that runs it: bash escapes with a backslash, PowerShell
with a backtick; the tool name in the hook input says which), finds the git call in each segment, skips git's global options (-C <dir>, -c k=v, --no-pager
...) and checks the subcommand. Quoted text (a commit message, a grep pattern) is never
mistaken for a git call, `git -C repo push` is caught, and `bash -c "git push"` /
`powershell -Command git push` are looked into. It is a guardrail against accidents, not a
security boundary: `eval`, shell variables holding the subcommand, aliases, and scripts that
run git internally are not seen.

Always blocked: push, reset --hard, clean -f, branch -D, checkout or restore of ".",
checkout -f.
Also blocked when COMMIT_POLICY is "stage-only" (the kit default: agents stage, the human
commits): commit, rebase, am, and cherry-pick / revert unless given --no-commit / -n.
Never blocked: add, merge, stash, tag, branch switching, anything read-only.

Edit COMMIT_POLICY below ("auto-commit" lets agents commit and rebase).

Test:  python test_block_dangerous_git.py
"""
import json
import re
import sys

COMMIT_POLICY = "stage-only"  # or "auto-commit"

SHELLS = {"bash", "sh", "zsh", "powershell", "powershell.exe", "pwsh", "pwsh.exe", "cmd", "cmd.exe"}
PREFIXES = {"env", "command", "nohup", "time", "call", "exec", "sudo"}
OPTIONS_WITH_VALUE = {"-c", "--namespace", "--exec-path"}  # -C is matched through .lower()


# The escape character of each shell: bash escapes with a backslash (outside quotes and inside
# double quotes), PowerShell with a backtick; inside single quotes neither escapes anything.
# In PowerShell a backslash is a plain character, so `"C:\dir\"` ends at the last quote; reading
# it with bash rules would keep the string open and hide a later `; git push`. cmd: none.
ESCAPES = {"bash": "\\", "powershell": "`", "cmd": None}


def shell_of(head):
    """The quoting rules a nested shell (bash -c, powershell -Command, cmd /c) uses."""
    head = head[:-4] if head.endswith(".exe") else head
    if head in ("powershell", "pwsh"):
        return "powershell"
    if head == "cmd":
        return "cmd"
    return "bash"


def split_segments(command, shell="bash"):
    """Split on ; & | and newlines that are outside quotes (escaped quotes do not close them)."""
    esc = ESCAPES.get(shell)
    segments, current, quote = [], [], None
    i, n = 0, len(command)
    while i < n:
        ch = command[i]
        if esc and ch == esc and quote != "'" and i + 1 < n:
            current.append(ch + command[i + 1])  # escaped character: never a quote or separator
            i += 2
            continue
        if quote:
            current.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            current.append(ch)
        elif ch in ";&|\n\r":
            segments.append("".join(current))
            current = []
        else:
            current.append(ch)
        i += 1
    segments.append("".join(current))
    return [s.strip() for s in segments if s.strip()]


def tokenize(segment, shell="bash"):
    esc = ESCAPES.get(shell)
    if not esc:
        return re.findall(r'''"[^"]*"|'[^']*'|[^\s"']+''', segment)
    e = re.escape(esc)
    return re.findall(r'''"(?:%s.|[^"%s])*"|'[^']*'|(?:%s.|[^\s"'%s])+''' % (e, e, e, e), segment, re.S)


def unquote(token):
    if len(token) >= 2 and token[0] == token[-1] and token[0] in ("'", '"'):
        return token[1:-1]
    return token


def basename(token):
    return re.split(r"[\\/]", unquote(token))[-1].lower()


def check_git(args):
    """args = tokens after the git executable. Returns a reason string or None."""
    i = 0
    while i < len(args):
        tok = unquote(args[i])
        if tok.lower() in OPTIONS_WITH_VALUE:
            i += 2
        elif tok.startswith("-"):
            i += 1
        else:
            break
    if i >= len(args):
        return None
    sub = unquote(args[i]).lower()
    rest = [unquote(a) for a in args[i + 1:]]
    rest_lower = [a.lower() for a in rest]
    stage_only = COMMIT_POLICY == "stage-only"

    if sub == "push":
        return "git push"
    if stage_only and sub in ("commit", "rebase", "am"):
        return "git " + sub + " (commit policy is stage-only)"
    if stage_only and sub in ("cherry-pick", "revert") and not ({"--no-commit", "-n"} & set(rest_lower)):
        return "git " + sub + " (creates a commit; use --no-commit)"
    if sub == "reset" and "--hard" in rest_lower:
        return "git reset --hard"
    if sub == "clean" and any(re.match(r"^-[a-z]*f", a) or a == "--force" for a in rest_lower):
        return "git clean -f"
    if sub == "branch" and "-D" in rest:
        return "git branch -D"
    if sub == "checkout" and ("." in rest or "-f" in rest_lower or "--force" in rest_lower):
        return "git checkout of '.' or with --force"
    if sub == "restore" and "." in rest:
        only_unstaging = bool({"--staged", "-S"} & set(rest)) and not ({"--worktree", "-W"} & set(rest))
        if not only_unstaging:
            return "git restore ."
    return None


def check_segment(segment, depth=0, shell="bash"):
    tokens = tokenize(segment, shell)
    i = 0
    while i < len(tokens) and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[i]) or basename(tokens[i]) in PREFIXES):
        i += 1
    if i >= len(tokens):
        return None
    head = basename(tokens[i])
    if head in ("git", "git.exe"):
        return check_git(tokens[i + 1:])
    if head in SHELLS and depth < 3:
        inner = shell_of(head)
        rest = tokens[i + 1:]
        for k, tok in enumerate(rest):
            text = unquote(tok)
            if re.search(r"\s", text):
                reason = check_command(text, depth + 1, inner)
                if reason:
                    return reason
            if text.lower() in ("-command", "-c", "/c") and k + 1 < len(rest):
                reason = check_command(" ".join(unquote(t) for t in rest[k + 1:]), depth + 1, inner)
                if reason:
                    return reason
    return None


def check_command(command, depth=0, shell="bash"):
    for segment in split_segments(command, shell):
        reason = check_segment(segment, depth, shell)
        if reason:
            return reason
    return None


def main():
    try:
        data = json.load(sys.stdin)
        command = (data.get("tool_input") or {}).get("command") or ""
        shell = "powershell" if data.get("tool_name") == "PowerShell" else "bash"
    except Exception:
        return 0  # nothing we can read, nothing to check
    try:
        reason = check_command(command, 0, shell)
    except Exception as error:  # fail closed when git is involved
        if re.search(r"\bgit\b", command):
            print("BLOCKED: the git guard hook failed (%s) on: %s" % (error, command), file=sys.stderr)
            return 2
        return 0
    if reason:
        print(
            "BLOCKED: '%s' is not allowed here. The project owner has prevented you from running "
            "it (git-guardrails hook). Stage only what you were asked to and propose a commit "
            "message as text; the owner runs the command. Command was: %s" % (reason, command),
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
