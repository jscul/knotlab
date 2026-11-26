"""Prior-work searches and ordinary ancestry in the later matched first-meeting records."""
import argparse
from collections import Counter, defaultdict
import gzip
import json
import re
from pathlib import Path
import shlex
import subprocess
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EPIC = HERE.parent.name
MATCHED = next((ROOT / 'artifacts/WIDENING-ROSTERS-20261125-001D').glob('*E001*'))


def command(*args):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def searches():
    output = {}
    for ticket in ('B', 'A'):
        path = Path('research') / (EPIC + ticket) / 'preregistration.md'
        section = (ROOT / path).read_text().split('## Prior work in the program')[1].split('\n## ')[0]
        gate = command(sys.executable, '-B', 'scripts/track.py', 'objects-gate', str(path))
        queries = [shlex.split(m)[1:] for m in re.findall(r'`python3 -B scripts/track.py (objects [^\n`]+)`', section)]
        extra = ('two made parts meet through an ancestral common knot under a law that uses no names' if ticket == 'B'
                 else 'ordinary growth meeting changes a newborn fresh distinctions eighteen fifteen generator count')
        queries.append([extra, '--until', '2026-11-25', '--exclude', EPIC])
        results = []
        for args in queries:
            raw = command(sys.executable, '-B', 'scripts/track.py', 'objects', *args, '--json', '--limit', '3')
            raw.check_returncode()
            top = [row['id'] for row in json.loads(raw.stdout)['index']]
            results.append({'arguments': args, 'first_three_index_rows': top})
        freeze = command('git', 'log', '--diff-filter=A', '--format=%H', '--', str(path)).stdout.strip().splitlines()[0]
        gate_message = (gate.stdout + gate.stderr).strip()
        changed = {}
        for ident in re.findall(r'missing epic `([^`]+)`', gate_message):
            other = f'research/{ident}/decision.md'
            first = command('git', 'log', '--diff-filter=A', '--format=%H', '--', other).stdout.strip().splitlines()
            if first:
                changed[ident] = {'first_decision_commit': first[0], 'frozen_before_that_decision': command(
                    'git', 'merge-base', '--is-ancestor', freeze, first[0]).returncode == 0}
        output[ticket] = {'freeze': freeze, 'gate_exit': gate.returncode, 'gate_output': gate_message,
                          'new_to_top_three': changed, 'searches': results}
    return output


def read_gzip(path):
    with gzip.open(path, 'rt') as stream:
        yield from map(json.loads, stream)


def ordinary_ancestry(record):
    supports = {}
    parents = {}
    start_distinctions = set()
    for round_ in read_gzip(MATCHED / 'producer' / record['support_file']):
        if round_['round'] == 0:
            supports.update(enumerate(map(frozenset, round_['supports'])))
            start_distinctions.update(d for places in supports.values() for d in places)
        else:
            assert len(round_['births']) == len(round_['supports'])
            for birth, places in zip(round_['births'], round_['supports']):
                supports[birth['id']] = frozenset(places)
                parents[birth['id']] = frozenset(birth['parents'])
    ancestors = {}
    for knot in sorted(supports):
        anc = set()
        for parent in parents.get(knot, ()):
            anc.add(parent)
            anc.update(ancestors[parent])
        ancestors[knot] = anc

    counts = Counter()
    example = None
    for event in read_gzip(MATCHED / 'producer' / record['events_file']):
        counts['first_meetings'] += 1
        links = event['linking_knots']
        if not links or any(k['knot'] not in parents for k in links):
            continue
        if any(d['d'] in start_distinctions for k in links for d in k['linking_distinctions']):
            continue
        counts['made_links_without_start_held_distinction'] += 1
        seen = set()
        for route in event['routes']:
            w, u, v = route['w'], route['u'], route['v']
            if w is None or (w, u, v) in seen:
                continue
            seen.add((w, u, v))
            left, right = supports[w] & supports[u], supports[w] & supports[v]
            counts['common_witness_occurrences'] += 1
            counts['ancestor_of_both'] += w in ancestors[u] and w in ancestors[v]
            counts['parent_of_both'] += w in parents.get(u, ()) and w in parents.get(v, ())
            counts['different_distinctions'] += bool(left and right and left.isdisjoint(right))
            if record['start'] == 'ringk:3,3,3,3,4' and (w,u,v) == (85,94,95):
                example = {'start': record['start'], 'split': event['s'], 'meeting': event['t'],
                           'first_part': event['X'], 'second_part': event['Y'], 'common_knot': w,
                           'endpoints': [u,v], 'parents': [sorted(parents[u]), sorted(parents[v])],
                           'shared_with_each': [sorted(left), sorted(right)]}
    return counts, example


def matched(smoke):
    rows = [json.loads(line)['result'] for line in (MATCHED / 'producer/results.jsonl').read_text().splitlines()]
    cases = sorted((r for r in rows if r['rule'] == 'MOST'), key=lambda r:(r['case'], r['kl']))
    if smoke:
        cases = [next(r for r in cases if r['start'] == 'ringk:3,3,3,3,4' and r['kl'] == 'nae')]
    totals = defaultdict(Counter)
    example = None
    for row in cases:
        count, ex = ordinary_ancestry(row)
        totals[row['kl']].update(count)
        totals[row['kl']]['matched_settings'] += 1
        if ex:
            example = ex
    return {'by_knot_law': dict(totals), 'example': example}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    t = perf_counter()
    ancestry = matched(args.smoke)
    if args.smoke:
        print(json.dumps(ancestry), 'seconds', round(perf_counter() - t, 4))
    else:
        result = {'matched_later_records': ancestry, 'prior_work': searches()}
        (HERE / 'record_checks.json').write_text(json.dumps(result, indent=2) + '\n')
