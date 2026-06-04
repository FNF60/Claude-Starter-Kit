#!/usr/bin/env python3
"""
Save Current Claude Code Session as a Verbatim Markdown Transcript

Commands
  list-sessions [--cwd PATH]            List recent .jsonl sessions as JSON
  save SESSION_ID SLUG [--cwd PATH]     Parse JSONL + write markdown transcript

The script is invoked by the /save-conversation skill. It handles all file I/O;
the skill (SKILL.md) handles slug validation and the interactive session picker.

Output path: <cwd>/Supplementary AI md files/Conversations/YYYY-MM-DD-HHMM-<slug>.md

Transcript dir: ~/. claude/projects/<encoded-cwd>/<session-id>.jsonl
  Path encoding: drive letter lowercased, then ':' '\\' '/' ' ' each → '-'
  Example: C:\\Users\\Facu\\...\\CRM Asesoria Financiera
        → c--Users-Facu-...-CRM-Asesoria-Financiera
"""

import json
import os
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


def _parse_events(jsonl_path: Path) -> tuple:
    """
    Parse a .jsonl transcript into an ordered list of rendering events.

    Returns (events, session_id) where events is a list of dicts:
      {'kind': 'user',           'text': str}
      {'kind': 'assistant',      'blocks': list}   — text + tool_use blocks merged
      {'kind': 'tool_result',    'tool_name': str, 'content': str, 'is_error': bool}
      {'kind': 'system_reminder','hook_name': str, 'body': str}
    """
    # Load all lines
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
            # Extract session_id from first record that has it
            if 'sessionId' in obj and obj['sessionId']:
                session_id = obj['sessionId']

    # First pass: build tool_use_id → tool_name map for correlating tool results
    tool_name_map = {}
    for obj in raw_lines:
        if obj.get('type') == 'assistant':
            for block in obj.get('message', {}).get('content', []):
                if isinstance(block, dict) and block.get('type') == 'tool_use':
                    tool_name_map[block['id']] = block['name']

    # Second pass: build events in chronological order.
    # Assistant turns are split across multiple records sharing the same message.id
    # (one record per content block: text, tool_use). We merge them.
    events = []
    cur_asst_msg_id = None
    cur_asst_blocks = []

    def _flush_assistant():
        nonlocal cur_asst_msg_id, cur_asst_blocks
        if cur_asst_msg_id and cur_asst_blocks:
            events.append({'kind': 'assistant', 'blocks': list(cur_asst_blocks)})
        cur_asst_msg_id = None
        cur_asst_blocks = []

    for obj in raw_lines:
        t = obj.get('type')

        if t == 'assistant':
            msg = obj.get('message', {})
            if msg.get('role') != 'assistant':
                _flush_assistant()
                continue

            msg_id = msg.get('id', '')
            if msg_id != cur_asst_msg_id:
                _flush_assistant()
                cur_asst_msg_id = msg_id

            for block in msg.get('content', []):
                if not isinstance(block, dict):
                    continue
                btype = block.get('type')
                if btype == 'thinking':
                    continue  # internal chain-of-thought; not user-visible
                if btype in ('text', 'tool_use'):
                    cur_asst_blocks.append(block)

        else:
            _flush_assistant()

            if t == 'user':
                msg = obj.get('message', {})
                if msg.get('role') != 'user':
                    continue

                for block in msg.get('content', []):
                    if not isinstance(block, dict):
                        continue
                    btype = block.get('type')

                    if btype == 'text':
                        text = block.get('text', '')
                        if text.strip():
                            events.append({'kind': 'user', 'text': text})

                    elif btype == 'tool_result':
                        tool_id = block.get('tool_use_id', '')
                        events.append({
                            'kind': 'tool_result',
                            'tool_name': tool_name_map.get(tool_id, 'unknown'),
                            'tool_id': tool_id,
                            'content': _extract_text(block.get('content', '')),
                            'is_error': bool(block.get('is_error', False)),
                        })

            elif t == 'attachment':
                att = obj.get('attachment', {})
                if att.get('type') == 'hook_additional_context':
                    body_raw = att.get('content', [])
                    body = (
                        '\n'.join(str(x) for x in body_raw)
                        if isinstance(body_raw, list)
                        else str(body_raw)
                    )
                    if body.strip():
                        events.append({
                            'kind': 'system_reminder',
                            'hook_name': att.get('hookName', ''),
                            'body': body,
                        })

    _flush_assistant()
    return events, session_id


# ── markdown rendering ─────────────────────────────────────────────────────────

def _render_markdown(events: list, session_id: str) -> str:
    """Render the event list as a verbatim markdown transcript."""
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

        elif kind == 'assistant':
            parts.append('## Assistant')
            parts.append('')
            for block in ev['blocks']:
                btype = block.get('type')
                if btype == 'text':
                    text = block.get('text', '').strip()
                    if text:
                        parts.append(text)
                        parts.append('')
                elif btype == 'tool_use':
                    name = block.get('name', 'unknown')
                    inp = block.get('input', {})
                    inp_json = json.dumps(inp, indent=2, ensure_ascii=False)
                    parts.append(f'```tool_use:{name}')
                    parts.append(inp_json)
                    parts.append('```')
                    parts.append('')

        elif kind == 'tool_result':
            name = ev['tool_name']
            err = ' (ERROR)' if ev['is_error'] else ''
            parts.append(f'### Tool result: {name}{err}')
            parts.append('')
            parts.append('```')
            parts.append(ev['content'])
            parts.append('```')
            parts.append('')

        elif kind == 'system_reminder':
            hook = ev['hook_name']
            label = f'System reminder: {hook}' if hook else 'System reminder'
            parts.append(f'<details>')
            parts.append(f'<summary>{label}</summary>')
            parts.append('')
            parts.append(ev['body'])
            parts.append('')
            parts.append('</details>')
            parts.append('')

    return '\n'.join(parts)


# ── output path helpers ────────────────────────────────────────────────────────

def _output_dir(cwd: Path) -> Path:
    return cwd / 'Supplementary AI md files' / 'Conversations'


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
