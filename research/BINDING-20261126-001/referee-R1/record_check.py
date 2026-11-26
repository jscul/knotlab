"""Check the public-count provenance and prior-work searches from the repository root."""
import argparse
import hashlib
import json
import resource
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STUDY = HERE.parent.relative_to(ROOT)
FREEZE = '24bc18768e'
CLOSURE = 'fd6b445e0f'
QUERIES = ('relations forced cycle parity cut space', 'whole-held facts ordinary growth shortest changes',
           'birth fresh count keep clause old states', 'nesting bases within bases', 'forbidding joins parity')
LIMIT = 2 * 1024 ** 3
resource.setrlimit(resource.RLIMIT_AS, (LIMIT, LIMIT))


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def track(*args):
    command = [sys.executable, '-B', 'scripts/track.py', *args]
    p = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stdout.strip() or p.stderr.strip()


def counts(raw):
    rows = [json.loads(line) for line in raw.splitlines()]
    return {'rows': len(rows), 'keys': len({(r['start'], r['round']) for r in rows}),
            'at_least_three': sum(r['most cycles in a split'] >= 3 for r in rows),
            'positive': sum(bool(r['bindings']) for r in rows),
            'sha256': hashlib.sha256(raw).hexdigest()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pilot', action='store_true')
    args = ap.parse_args()
    start = time.monotonic()
    basefile = str(STUDY / 'README.md')
    judge = str(STUDY / 'judge.jsonl')
    code, message = track('objects-gate', basefile)
    close = git('show', CLOSURE + ':' + judge)
    live = (ROOT / judge).read_bytes()
    result = {'gate': {'file': basefile, 'exit': code, 'message': message},
              'freeze': FREEZE, 'closure': CLOSURE,
              'freeze_note_unchanged_as_prefix': (ROOT / basefile).read_bytes().startswith(git('show', FREEZE + ':' + basefile)),
              'freeze_files': git('ls-tree', '-r', '--name-only', FREEZE, str(STUDY)).decode().splitlines(),
              'judge_closed': counts(close), 'judge_at_reported_prefix': counts(b''.join(close.splitlines(keepends=True)[:7713])),
              'judge_in_checkout': counts(live), 'checkout_starts_with_committed_bytes': live.startswith(close), 'searches': []}
    for query in QUERIES[:1] if args.pilot else QUERIES:
        flags = ['objects', query, '--until', '2026-11-26', '--exclude', STUDY.name, '--limit', '10', '--json']
        status, printed = track(*flags)
        if status:
            raise ValueError(printed)
        results = json.loads(printed)
        found = []
        for entry in results['index']:
            epic = entry['epic']
            existed = subprocess.run(['git', 'cat-file', '-e', FREEZE + ':tickets/' + epic + '.json'],
                                     cwd=ROOT, stderr=subprocess.DEVNULL).returncode == 0
            found.append({'id': entry['id'], 'record': entry['record'], 'ticket_in_freeze': existed})
        result['searches'].append({'args': flags, 'index': found, 'other_epics': [e['id'] for e in results['other_epics']]})
    result['direct_prior_searches'] = []
    relevant = [('FRESH-COUNT-20261118-001', 'fresh count'), ('NAE-GROWTH-20261119-001', 'keep clause'),
                ('FORBIDDING-JOIN-20261120-001', 'old states'), ('LAYERS-20261126-001','whole-held facts'),
                ('BASES-WITHIN-20261112-001','outer states'), ('RECURSION-LEAD-20261126-001','shortest changes')]
    for epic, query in relevant[:1] if args.pilot else relevant:
        flags = ['objects', query, '--epic', epic, '--until', '2026-11-26', '--json']
        rc, raw = track(*flags)
        assert rc == 0
        result['direct_prior_searches'].append({'args':flags,'rows':[row['id'] for row in json.loads(raw)['index']],
              'ticket_in_freeze':subprocess.run(['git','cat-file','-e',FREEZE+':tickets/'+epic+'.json'],cwd=ROOT,
                                               stderr=subprocess.DEVNULL).returncode==0})
    result['seconds'] = round(time.monotonic() - start, 3)
    (HERE / ('record_pilot.json' if args.pilot else 'record.json')).write_text(json.dumps(result, indent=2) + '\n')
    print(result['gate'], result['seconds'])
    for item in result['searches']:
        print(item['args'][1], [e['id'] for e in item['index'][:3]])
    print(result['judge_closed'], result['judge_at_reported_prefix'], result['judge_in_checkout'])


if __name__ == '__main__':
    main()
