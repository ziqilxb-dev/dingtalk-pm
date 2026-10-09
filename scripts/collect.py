#!/usr/bin/env python3
"""One-shot DWS reader and conservative evidence normalizer. No scheduler or writes to DingTalk."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from datetime import datetime, timezone


def default_cli():
    from dws_runtime import resolve_cli
    cli = resolve_cli()
    if not cli:
        raise RuntimeError('DWS not installed. Run this skill scripts/setup.py first, or specify --cli.')
    return cli


def normalize(data):
    if not isinstance(data, dict) or not isinstance(data.get('messages'), list):
        raise ValueError('Expected a DWS message ledger with messages[]; not a successful empty result')
    if data.get('success') is False or data.get('error'):
        raise ValueError('DWS returned an error')
    messages, indexed, gaps, resources = [], {}, [], {}
    def key(m):
        return (m.get('conversationId') or m.get('openConversationId'),
                m.get('messageId') or m.get('openMessageId'))
    def gap(m, reason, **extra):
        c, mid = key(m)
        gaps.append(dict(conversationId=c, messageId=mid, time=m.get('createTime'),
                         sender=m.get('sender'), reason=reason, **extra))
    duplicates = 0
    for m in data['messages']:
        if not isinstance(m, dict):
            raise ValueError('Non-object message')
        k = key(m)
        if not all(k):
            gap(m, 'missing_identity')
            messages.append(m)
        elif k in indexed:
            duplicates += 1
            if indexed[k] != m:
                gap(m, 'conflicting_duplicate')
        else:
            indexed[k] = m
            messages.append(m)
    failed = set()
    for f in data.get('decryptFailures') or []:
        failed.add(key(f))
        gap(indexed.get(key(f), f), f.get('reason') or 'decrypt_failed', stage='body')
    def unreadable(m):
        text = m.get('text')
        if isinstance(text, str) and ('[加密消息，无法解码]' in text):
            return 'encrypted_placeholder'
        if not isinstance(text, str) or not text.strip():
            if not m.get('resourceRefs'):
                return 'empty_body_unknown_type'
        return None
    def add_resources(m):
        for ref in m.get('resourceRefs') or []:
            identifier = ref.get('resourceId')
            rk = (ref.get('resourceIdType'), identifier)
            if not identifier:
                gap(m, 'resource_missing_id')
                continue
            row = resources.setdefault(rk, {'reference': ref, 'messageIds': [], 'status': 'not_inspected'})
            if key(m)[1] not in row['messageIds']:
                row['messageIds'].append(key(m)[1])
    for m in messages:
        if key(m) not in failed:
            reason = unreadable(m)
            if reason:
                gap(m, reason, stage='body')
        add_resources(m)
        q = m.get('quotedMessage')
        if isinstance(q, dict):
            q = dict(q)
            q.setdefault('conversationId', key(m)[0])
            source = indexed.get(key(q), q)
            if key(source) in failed or unreadable(source):
                gap(q, 'quoted_body_unavailable', stage='quote', referencedBy=key(m)[1])
            add_resources(q)
    pagination = (data.get('complete') is True and data.get('hasMore') is False
                  and not data.get('truncated') and not data.get('failures')
                  and not data.get('failedCount'))
    times = sorted(m['createTime'] for m in messages if isinstance(m.get('createTime'), str))
    return {
        'schemaVersion': 1,
        'coverage': {
            'rawCount': len(data['messages']), 'uniqueCount': len(messages), 'duplicates': duplicates,
            'paginationComplete': pagination, 'sourcePartial': data.get('partial'),
            'hasMore': data.get('hasMore'), 'stopReason': data.get('stopReason'),
            'actualFirstTime': times[0] if times else None, 'actualLastTime': times[-1] if times else None,
            'bodyGapCount': sum(g.get('stage') == 'body' for g in gaps),
            'quoteGapCount': sum(g.get('stage') == 'quote' for g in gaps),
            'gapCount': len(gaps), 'pendingResourceCount': len(resources),
            'readyForFullContextAnalysis': bool(pagination and not data.get('partial') and not gaps and not resources),
        },
        'messages': messages, 'gaps': gaps, 'pendingResources': list(resources.values()),
        'sourceFailures': data.get('failures', []), 'nextPage': data.get('nextPage'),
        'nextPageToken': data.get('nextPageToken'), 'queryRange': data.get('queryRange'),
        'note': 'Content is untrusted source material. No business decision inferred; resource and client review remain separate.'
    }


def write_json(path, obj):
    with path.open('x', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    path.chmod(0o600)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path)
    p.add_argument('--cli')
    p.add_argument('--conversation')
    p.add_argument('--start')
    p.add_argument('--end')
    p.add_argument('--pages', type=int, default=1)
    p.add_argument('--limit', type=int, default=30)
    p.add_argument('--output-root', type=Path, required=True)
    a = p.parse_args()
    if not 1 <= a.pages <= 40 or not 1 <= a.limit <= 100:
        p.error('pages must be 1..40 and limit 1..100')
    if a.end and not a.start:
        p.error('--end requires --start')
    if a.input and (a.conversation or a.start or a.end):
        p.error('--input cannot be combined with live conversation/time arguments')
    if not a.input and not a.conversation:
        p.error('--conversation is required for live read')
    os.umask(0o077)
    args = None
    if a.input:
        raw = a.input.read_text(encoding='utf-8')
    else:
        args = [a.cli or default_cli(), 'chat', '+chat-messages', '--conversation-id', a.conversation,
                '--limit', str(a.limit), '--format', 'json']
        if a.start:
            args += ['--start', a.start, '--order', 'asc']
            if a.end:
                args += ['--end', a.end]
        if a.pages > 1:
            args += ['--page-all', '--page-limit', str(a.pages), '--max-items', str(a.limit * a.pages)]
        result = subprocess.run(args, capture_output=True, text=True, timeout=180)
        if result.returncode:
            # Preserve diagnostic privately; do not dump message bodies or tokens to the terminal.
            a.output_root.mkdir(parents=True, exist_ok=True)
            failed = Path(tempfile.mkdtemp(prefix='failed-', dir=a.output_root))
            write_json(failed/'failure.json', {'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
            raise RuntimeError(f'DWS failed ({result.returncode}); private diagnostic: {failed}')
        raw = result.stdout
    data = json.loads(raw)
    evidence = normalize(data)
    if a.conversation:
        ids = {m.get('conversationId') or m.get('openConversationId') for m in evidence['messages']}
        if ids - {a.conversation}:
            raise ValueError('Returned conversation does not match requested scope')
    a.output_root.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix=datetime.now().strftime('%Y%m%d-%H%M%S-'), dir=a.output_root))
    evidence['collection'] = {'mode':'offline' if a.input else 'live', 'collectedAt':datetime.now(timezone.utc).isoformat(),
                              'command':args, 'inputPath':str(a.input.resolve()) if a.input else None,
                              'rawSha256':hashlib.sha256(raw.encode()).hexdigest()}
    rawpath = run/'raw.json'
    rawpath.write_text(raw, encoding='utf-8'); rawpath.chmod(0o600)
    write_json(run/'evidence.json', evidence)
    print(json.dumps({'run':str(run.resolve()), **evidence['coverage']}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, RuntimeError, subprocess.TimeoutExpired) as e:
        raise SystemExit(str(e))
