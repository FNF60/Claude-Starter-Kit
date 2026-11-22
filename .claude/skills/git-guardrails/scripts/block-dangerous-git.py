#!/usr/bin/env python3
"""PreToolUse hook for the Bash and PowerShell tools: blocks dangerous git commands.

Exit code 2 blocks the call and the message on stderr goes back to the model.

How it works: it splits the command into segments (on ; & | and newlines, outside quotes),
finds the git call in each segment, skips git's global options (-C <dir>, -c k=v, --no-pager
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


def split_segments(command):
    """Split on ; & | and newlines that are outside quotes."""
    segments, current, quote = [], [], None
    for ch in command:
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
    segments.append("".join(current))
    return [s.strip() for s in segments if s.strip()]


def tokenize(segment):
    return re.findall(r'''"[^"]*"|'[^']*'|[^\s"']+''', segment)


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


def check_segment(segment, depth=0):
    tokens = tokenize(segment)
    i = 0
    while i < len(tokens) and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[i]) or basename(tokens[i]) in PREFIXES):
        i += 1
    if i >= len(tokens):
        return None
    head = basename(tokens[i])
    if head in ("git", "git.exe"):
        return check_git(tokens[i + 1:])
    if head in SHELLS and depth < 3:
        rest = tokens[i + 1:]
        for k, tok in enumerate(rest):
            text = unquote(tok)
            if re.search(r"\s", text):
                reason = check_command(text, depth + 1)
                if reason:
                    return reason
            if text.lower() in ("-command", "-c") and k + 1 < len(rest):
                reason = check_command(" ".join(unquote(t) for t in rest[k + 1:]), depth + 1)
                if reason:
                    return reason
    return None


def check_command(command, depth=0):
    for segment in split_segments(command):
        reason = check_segment(segment, depth)
        if reason:
            return reason
    return None


def main():
    try:
        data = json.load(sys.stdin)
        command = (data.get("tool_input") or {}).get("command") or ""
    except Exception:
        return 0  # nothing we can read, nothing to check
    try:
        reason = check_command(command)
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
