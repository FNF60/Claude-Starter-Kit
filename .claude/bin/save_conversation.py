#!/usr/bin/env python3
"""
Save Current Claude Code Session as a Condensed Markdown Transcript

Commands
  list-sessions [--cwd PATH]            List recent .jsonl sessions as JSON
  save SESSION_ID SLUG [--cwd PATH]     Parse JSONL + write markdown transcript

The script is invoked by the /save-conversation skill. It handles all file I/O;
the skill (SKILL.md) handles slug validation and the interactive session picker.

The transcript keeps only the conversation's main turns:
  - user prompts (plus reasons typed when rejecting a tool call)
  - the final assistant response of each turn
  - AskUserQuestion exchanges (questions, option labels, chosen answers)
Dropped: tool calls & results, thinking, hook/system reminders, IDE context
(<ide_selection>, <ide_opened_file>), command stdout,
interruption boilerplate, mid-turn assistant narration.

Output path: <cwd>/docs/Supplementary AI md files/Conversations/YYYY-MM-DD-HHMM-<slug>.md

Transcript dir: ~/. claude/projects/<encoded-cwd>/<session-id>.jsonl
  Path encoding: drive letter lowercased, then ':' '\\' '/' ' ' each → '-'
  Example: C:\\Users\\Facu\\...\\CRM Asesoria Financiera
        → c--Users-Facu-...-CRM-Asesoria-Financiera
"""

import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


# ── path encoding ──────────────────────────────────────────────────────────────

def _encode_project_path(cwd: Path) -> str:
    """Convert an absolute path to the Claude Code project dir name."""
    s = str(cwd)
    result = []
    for ch in s:
        if ch in r':/\\ ' or ch == '\t':
            result.append('-')
        else:
            result.append(ch)
    encoded = ''.join(result)
    # Lowercase the drive letter (first character on Windows paths)
    if encoded:
        encoded = encoded[0].lower() + encoded[1:]
    return encoded


def _transcript_dir(cwd: Path) -> Path:
    return Path.home() / '.claude' / 'projects' / _encode_project_path(cwd)


# ── session listing ────────────────────────────────────────────────────────────

def list_sessions(cwd: Path) -> list:
    """Return metadata for .jsonl files modified in the last hour, newest first."""
    tdir = _transcript_dir(cwd)
    if not tdir.exists():
        return []

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=1)

    sessions = []
    for f in tdir.glob('*.jsonl'):
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        if mtime < cutoff:
            continue

        turn_count = 0
        first_preview = ''
        try:
            with open(f, encoding='utf-8', errors='replace') as fp:
                for line in fp:
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if obj.get('type') == 'user':
                        msg = obj.get('message', {})
                        if msg.get('role') == 'user':
                            for block in msg.get('content', []):
                                if isinstance(block, dict) and block.get('type') == 'text':
                                    turn_count += 1
                                    if not first_preview:
                                        first_preview = (
                                            block.get('text', '')[:100]
                                            .replace('\n', ' ')
                                        )
        except OSError:
            continue

        sessions.append({
            'session_id': f.stem,
            'path': str(f),
            'mtime': mtime.astimezone().strftime('%H:%M'),
            'mtime_iso': mtime.isoformat(),
            'turns': turn_count,
            'preview': first_preview,
        })

    sessions.sort(key=lambda s: s['mtime_iso'], reverse=True)
    return sessions


# ── JSONL parsing ──────────────────────────────────────────────────────────────

def _extract_text(content_val) -> str:
    """Coerce a tool_result content value (str or list of blocks) to plain text."""
    if isinstance(content_val, str):
        return content_val
    if isinstance(content_val, list):
        parts = []
        for item in content_val:
            if isinstance(item, dict):
                t = item.get('type', '')
                if t == 'text':
                    parts.append(item.get('text', ''))
                elif t == 'image':
                    src = item.get('source', {})
                    url = src.get('url') or src.get('data', '')
                    if isinstance(url, str) and url.startswith('data:'):
                        parts.append('[image: base64 data omitted]')
                    else:
                        parts.append(f'[image: {url}]')
                else:
                    parts.append(json.dumps(item, ensure_ascii=False))
            else:
                parts.append(str(item))
        return '\n'.join(parts)
    return str(content_val)


_INTERRUPT_BOILERPLATE = {
    '[Request interrupted by user]',
    '[Request interrupted by user for tool use]',
}

_REJECTION_MARKER = 'The user provided the following reason for the rejection:'

# Context the IDE/harness injects into the user turn. None of it was typed by
# the user, so none of it belongs in a transcript. Stripped wherever it appears
# (a whole message, or wrapped around real text).
_ENVELOPE_TAGS = (
    'ide_selection',
    'ide_opened_file',
    'ide_diagnostics',
    'system-reminder',
    'local-command-caveat',
    'local-command-stdout',
)
_ENVELOPE_RE = re.compile(
    r'<(%s)\b.*?</\1>' % '|'.join(_ENVELOPE_TAGS),
    re.S,
)
# An unclosed envelope (truncated in the log) — drop to end of message.
_ENVELOPE_OPEN_RE = re.compile(
    r'<(?:%s)\b.*\Z' % '|'.join(_ENVELOPE_TAGS),
    re.S,
)


def _strip_envelopes(text: str) -> str:
    text = _ENVELOPE_RE.sub('', text)
    text = _ENVELOPE_OPEN_RE.sub('', text)
    return text


def _filter_user_text(text: str):
    """Clean a user text block for display. Returns text, or None to drop it."""
    stripped = _strip_envelopes(text).strip()
    if not stripped:
        return None
    if stripped in _INTERRUPT_BOILERPLATE:
        return None
    if stripped.startswith('<local-command-stdout>'):
        return None
    if stripped.startswith('Caveat: the messages below were generated by the user'):
        return None
    if '<command-name>' in stripped:
        # Slash-command invocation — render compactly as `/name args`
        name = re.search(r'<command-name>(.*?)</command-name>', stripped, re.S)
        args = re.search(r'<command-args>(.*?)</command-args>', stripped, re.S)
        if not name:
            return None
        cmd = name.group(1).strip()
        arg = args.group(1).strip() if args else ''
        return f'`{cmd} {arg}`' if arg else f'`{cmd}`'
    return stripped


# A real rejection result opens with the harness's standard sentence. Requiring
# it stops file contents that merely quote the marker (e.g. reading this script)
# from being rendered as a user rejection.
_REJECTION_OPENERS = (
    "The user doesn't want to",
    "The user doesn\u2019t want to",
    'The user rejected',
)


def _rejection_reason(content: str):
    """Extract the user's typed reason from a rejected-tool-call result, if any."""
    head = content.lstrip()
    if not head.startswith(_REJECTION_OPENERS):
        return None
    if _REJECTION_MARKER in head:
        return head.split(_REJECTION_MARKER, 1)[1].strip() or None
    return None


def _parse_answers_fallback(content: str) -> dict:
    """Best-effort parse of answers from the AskUserQuestion result text.

    Used only when the record lacks a structured toolUseResult.answers map.
    Result text looks like: Your questions have been answered: "Q"="A", "Q2"="A2".
    """
    if 'questions have been answered' not in content:
        return {}
    return dict(re.findall(r'"(.+?)"="(.+?)"', content, re.S))


def _parse_events(jsonl_path: Path) -> tuple:
    """
    Parse a .jsonl transcript into a condensed list of rendering events.

    Returns (events, session_id) where events is a list of dicts:
      {'kind': 'user',           'text': str}   — a real user prompt
      {'kind': 'user_rejection', 'text': str}   — reason typed when rejecting a tool call
      {'kind': 'question',       'questions': list, 'answers': dict}
                                                — an AskUserQuestion exchange
      {'kind': 'assistant',      'text': str}   — the turn's final response text

    Everything else (tool calls & results, thinking, hook/system reminders,
    command stdout, interruption boilerplate, mid-turn narration) is dropped.
    """
    raw_lines = []
    session_id = jsonl_path.stem
    with open(jsonl_path, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            raw_lines.append(obj)
            if 'sessionId' in obj and obj['sessionId']:
                session_id = obj['sessionId']

    # Chronological stream of candidate events; assistant text is condensed
    # to the final run per turn afterwards.
    stream = []
    pending_ask = {}  # tool_use_id → AskUserQuestion input

    for obj in raw_lines:
        if obj.get('isSidechain') or obj.get('isMeta'):
            continue
        t = obj.get('type')

        if t == 'assistant':
            msg = obj.get('message', {})
            if msg.get('role') != 'assistant':
                continue
            for block in msg.get('content', []):
                if not isinstance(block, dict):
                    continue
                btype = block.get('type')
                if btype == 'text':
                    text = block.get('text', '').strip()
                    if text:
                        stream.append({'kind': 'atext', 'text': text})
                elif btype == 'tool_use':
                    if block.get('name') == 'AskUserQuestion':
                        pending_ask[block.get('id', '')] = block.get('input', {})
                    # Any tool call ends the current text run, so that only
                    # text written after the turn's last tool call survives.
                    stream.append({'kind': 'break'})

        elif t == 'user':
            msg = obj.get('message', {})
            if msg.get('role') != 'user':
                continue
            for block in msg.get('content', []):
                if not isinstance(block, dict):
                    continue
                btype = block.get('type')

                if btype == 'text':
                    text = _filter_user_text(block.get('text', ''))
                    if text:
                        stream.append({'kind': 'user', 'text': text})

                elif btype == 'tool_result':
                    tid = block.get('tool_use_id', '')
                    content_text = _extract_text(block.get('content', ''))
                    if tid in pending_ask:
                        ask_input = pending_ask.pop(tid)
                        tur = obj.get('toolUseResult')
                        if isinstance(tur, dict) and isinstance(tur.get('answers'), dict):
                            answers = tur['answers']
                        else:
                            answers = _parse_answers_fallback(content_text)
                        stream.append({
                            'kind': 'question',
                            'questions': ask_input.get('questions', []),
                            'answers': answers,
                        })
                    reason = _rejection_reason(content_text)
                    if reason:
                        stream.append({'kind': 'user_rejection', 'text': reason})

    return _condense(stream), session_id


def _condense(stream: list) -> list:
    """Per turn, keep all question events but only the final assistant text run.

    A turn spans from one user event (prompt or rejection) to the next. Within
    it, consecutive 'atext' events form runs; 'break' (tool call) and 'question'
    events terminate a run. Only the last run survives — merged into a single
    assistant event — so mid-turn narration before tool calls is dropped.
    Question events keep their position; breaks render nothing.
    """
    events = []
    segment = []

    def _flush():
        nonlocal segment
        if not segment:
            return
        last_run, run = [], []
        for i, ev in enumerate(segment):
            if ev['kind'] == 'atext':
                run.append(i)
            else:
                if run:
                    last_run = run
                run = []
        if run:
            last_run = run
        for i, ev in enumerate(segment):
            if ev['kind'] == 'atext':
                if last_run and i == last_run[0]:
                    text = '\n\n'.join(segment[j]['text'] for j in last_run)
                    events.append({'kind': 'assistant', 'text': text})
            elif ev['kind'] != 'break':
                events.append(ev)
        segment = []

    for ev in stream:
        if ev['kind'] in ('user', 'user_rejection'):
            _flush()
            events.append(ev)
        else:
            segment.append(ev)
    _flush()
    return events


# ── markdown rendering ─────────────────────────────────────────────────────────

def _render_markdown(events: list, session_id: str) -> str:
    """Render the condensed event list as a markdown transcript."""
    parts = [
        f'# Session: {session_id}',
        f'',
        f'_Exported: {datetime.now().strftime("%Y-%m-%d %H:%M")}_',
        '',
        '---',
        '',
    ]

    for ev in events:
        kind = ev['kind']

        if kind == 'user':
            parts.append('## User')
            parts.append('')
            parts.append(ev['text'])
            parts.append('')

        elif kind == 'user_rejection':
            parts.append('## User (tool rejection)')
            parts.append('')
            parts.append(ev['text'])
            parts.append('')

        elif kind == 'assistant':
            parts.append('## Assistant')
            parts.append('')
            parts.append(ev['text'])
            parts.append('')

        elif kind == 'question':
            parts.append('## Question (AskUserQuestion)')
            parts.append('')
            answers = ev.get('answers') or {}
            for q in ev.get('questions', []):
                if not isinstance(q, dict):
                    continue
                qtext = ' '.join(str(q.get('question', '')).split())
                parts.append(f'**Q: {qtext}**')
                labels = [
                    o.get('label', '') for o in q.get('options', [])
                    if isinstance(o, dict) and o.get('label')
                ]
                if labels:
                    parts.append(f'_Options: {" / ".join(labels)}_')
                ans = answers.get(q.get('question', ''))
                if isinstance(ans, list):
                    ans = ', '.join(str(a) for a in ans)
                if ans:
                    parts.append(f'**A:** {ans}')
                else:
                    parts.append('**A:** _(no answer recorded)_')
                parts.append('')

    return '\n'.join(parts)


# ── output path helpers ────────────────────────────────────────────────────────

def _output_dir(cwd: Path) -> Path:
    return cwd / 'docs' / 'Supplementary AI md files' / 'Conversations'


def _output_path(slug: str, cwd: Path) -> Path:
    ts = datetime.now().strftime('%Y-%m-%d-%H%M')
    return _output_dir(cwd) / f'{ts}-{slug}.md'


def _delete_slug(slug: str, out_dir: Path) -> list:
    """Delete all *-<slug>.md files; return list of deleted paths."""
    deleted = []
    for f in out_dir.glob(f'*-{slug}.md'):
        f.unlink()
        deleted.append(str(f))
    return deleted


# ── commands ───────────────────────────────────────────────────────────────────

def cmd_list_sessions(argv: list):
    """list-sessions [--cwd PATH]  →  JSON array of session metadata"""
    cwd = Path.cwd()
    i = 0
    while i < len(argv):
        if argv[i] == '--cwd' and i + 1 < len(argv):
            cwd = Path(argv[i + 1])
            i += 2
        else:
            i += 1

    # Honour CLAUDE_SESSION_ID if the runtime injects it
    env_id = os.environ.get('CLAUDE_SESSION_ID')
    if env_id:
        tdir = _transcript_dir(cwd)
        jsonl = tdir / f'{env_id}.jsonl'
        mtime_str = ''
        if jsonl.exists():
            mtime_str = datetime.fromtimestamp(
                jsonl.stat().st_mtime, tz=timezone.utc
            ).astimezone().strftime('%H:%M')
        sessions = [{
            'session_id': env_id,
            'path': str(jsonl),
            'mtime': mtime_str,
            'mtime_iso': '',
            'turns': -1,
            'preview': '(current session via CLAUDE_SESSION_ID)',
        }]
    else:
        sessions = list_sessions(cwd)

    print(json.dumps(sessions, indent=2, ensure_ascii=False))


def cmd_save(argv: list):
    """save SESSION_ID SLUG [--cwd PATH]  →  write transcript, print path + lines"""
    if len(argv) < 2:
        print('Usage: save SESSION_ID SLUG [--cwd PATH]', file=sys.stderr)
        sys.exit(1)

    session_id = argv[0]
    slug = argv[1]
    cwd = Path.cwd()
    i = 2
    while i < len(argv):
        if argv[i] == '--cwd' and i + 1 < len(argv):
            cwd = Path(argv[i + 1])
            i += 2
        else:
            i += 1

    tdir = _transcript_dir(cwd)
    jsonl_path = tdir / f'{session_id}.jsonl'
    if not jsonl_path.exists():
        print(f'ERROR: transcript not found: {jsonl_path}', file=sys.stderr)
        sys.exit(1)

    out_dir = _output_dir(cwd)
    if not out_dir.exists():
        print(f'ERROR: output dir does not exist: {out_dir}', file=sys.stderr)
        sys.exit(1)

    # Remove any previous file for this slug (one file per slug at a time)
    _delete_slug(slug, out_dir)

    events, resolved_id = _parse_events(jsonl_path)
    markdown = _render_markdown(events, resolved_id)

    out_file = _output_path(slug, cwd)
    out_file.write_text(markdown, encoding='utf-8')

    line_count = markdown.count('\n') + 1
    print(f'Saved: {out_file}')
    print(f'Lines: {line_count}')

    try:
        rel = out_file.relative_to(cwd)
        print(f'Suggest: git add "{rel}"')
    except ValueError:
        print(f'Suggest: git add "{out_file}"')


# ── entry point ────────────────────────────────────────────────────────────────

def main():
    argv = sys.argv[1:]
    if not argv:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    cmd = argv[0]
    rest = argv[1:]

    if cmd == 'list-sessions':
        cmd_list_sessions(rest)
    elif cmd == 'save':
        cmd_save(rest)
    else:
        print(f'ERROR: unknown command: {cmd}', file=sys.stderr)
        print('Commands: list-sessions, save', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
