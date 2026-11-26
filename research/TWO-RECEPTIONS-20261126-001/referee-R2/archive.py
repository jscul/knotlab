"""Recount the delivered rows, the sampled design and the available comparison rounds."""
import argparse
import gzip
import json
import random
import sys
from collections import Counter, defaultdict
from itertools import islice, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
sys.path.insert(0, str(STUDY.parent / 'SWITCH-RECEIVERS-20261126-001'))
import receivers

SETTINGS = [(None, None), ('MET', 'OLDEST'), ('MET', 'NEWEST'), ('MET-SOLE', None),
            ('STEPS1-SOLE', None), ('STEPS2-SOLE', None), ('J-EACH-PART', None)]


def read_rows(path, limit):
    with gzip.open(path, 'rt') as lines:
        for line in islice(lines, limit):
            yield json.loads(line)


def key(row):
    return row['A'], row['B'], tuple(row['law'][1:])


def summarize(rows):
    changes = [c for r in rows for c in r['changes']]
    hearings = [c for c in changes if c['heard'] is not None]
    return {
        'records': len(rows),
        'receivers': len({r['A'] for r in rows}),
        'pairs with a hearing': sum(any(c['heard'] for c in r['changes']) for r in rows),
        'pairs compared': sum(bool(r['changes']) for r in rows),
        'linked after round 3': sum(r['linked'][2:3] == [True] for r in rows),
        'linked after round 8': sum(r['linked'][7:8] == [True] for r in rows),
        'stops': Counter(r['ended'] for r in rows),
        'unchanged rounds read': sum(r['rounds'] for r in rows),
        'unchanged endpoint': Counter(r['rounds'] for r in rows),
        'short observations of made members': sum(sum(r['made short']) for r in rows),
        'records with a made shortage': sum(any(r['made short']) for r in rows),
        'placements': len(changes),
        'linked placements': sum(c['linked'] for c in changes),
        'unlinked placements': sum(not c['linked'] for c in changes),
        'heard by linked,unlinked': [sum(c['linked'] == value for c in hearings) for value in [True,False]],
        'first heard': Counter(c['heard'] for c in hearings),
        'first heard, sharings': Counter(c['sharings'] for c in hearings),
        'common endpoint': Counter(c['rounds'] for c in changes),
        'comparisons reaching round 7': sum(c['rounds'] >= 7 for c in changes),
        'heard comparisons reaching round 7': sum(c['rounds'] >= 7 for c in hearings),
        'unheard comparisons reaching round 7': sum(c['rounds'] >= 7 and c['heard'] is None for c in changes),
        'unheard at common round 3': sum(c['rounds'] == 3 and c['heard'] is None for c in changes)
    }


def check_start(a, b):
    knots, _, _ = receivers.jam.changed(a, b, 3, None, 'meeting')
    holders = defaultdict(list)
    for i, row in enumerate(knots):
        for d in row:
            holders[d].append(i)
    seen = {0}
    todo = [0]
    while todo:
        u = todo.pop()
        for d in knots[u]:
            for v in holders[d]:
                if v not in seen:
                    seen.add(v)
                    todo.append(v)
    return len(seen) == len(knots), max(map(len,holders.values()))


def main(limit):
    sample = random.Random(20261126).sample(range(646), 100)
    catalogue = receivers.register()
    assert len(catalogue) == 646
    names = [catalogue[i][0] for i in sorted(sample)]
    design = set(product(names, receivers.SENDERS, SETTINGS))
    starts = [check_start(a,b) for a,b in islice(product(names,receivers.SENDERS),limit)]
    assert all(connected and largest == 2 for connected,largest in starts)
    entries = list(read_rows(STUDY / 'parity_runs.jsonl.gz', limit))
    runs = [r for r in entries if 'law' in r]
    stopped = [r for r in entries if 'not run' in r]
    by_key = {key(r): r for r in runs}
    assert len(by_key) == len(runs)
    assert not by_key.keys() - design
    for r in runs:
        assert r['knot law'] == 'parity' and r['law'][0] == 'ORD'
        assert len(r['made short']) == len(r['linked']) == r['rounds'] <= 12
        assert all(type(n) == int and n >= 0 for n in r['made short'])
        assert sum(c['linked'] for c in r['changes']) <= 5
        assert sum(not c['linked'] for c in r['changes']) <= 2
        for c in r['changes']:
            assert 3 <= c['rounds'] <= r['rounds']
            assert c['heard'] is None or 3 < c['heard'] <= c['rounds']
    if limit is None:
        expected_missing = set()
        for event in stopped:
            a, b = event['job']
            chunk = list(product(names[a:b], receivers.SENDERS, SETTINGS))
            k = event['lines read']
            assert set(chunk[:k]) <= by_key.keys()
            expected_missing.update(chunk[k:])
        assert expected_missing == design - by_key.keys()

    common = []
    hearing_changes = []
    for other in read_rows(STUDY / 'shortage_runs.jsonl.gz', limit):
        if other.get('law', [''])[0] != 'ORD' or key(other) not in by_key:
            continue
        r = by_key[key(other)]
        readings = [sum(c['heard'] is not None for c in row['changes']) for row in (r, other)]
        if readings[0] != readings[1]:
            hearing_changes.append({'key': key(r), 'parity, not-all-equal': readings})
        common.append([f for f in ('rounds', 'ended', 'made short', 'linked', 'changes') if r[f] != other[f]])

    groups = defaultdict(list)
    for r in runs:
        groups[' '.join(v for v in r['law'] if v)].append(r)
    return {'all': summarize(runs), 'settings': {k: summarize(v) for k,v in groups.items()},
            'sample': {'seed': 20261126, 'catalogue': len(catalogue), 'drawn': len(names),
                       'start preparations checked connected with at most two holders': len(starts),
                       'drawn with any record': len({k[0] for k in by_key}),
                       'drawn with all 35 records': sum(all((a,b,l) in by_key for b,l in product(receivers.SENDERS, SETTINGS)) for a in names),
                       'distinct receiver and sender combinations': len({k[:2] for k in by_key}),
                       'interrupted jobs': stopped},
            'comparison with not-all-equal on common keys': {
                'differing hearing counts': hearing_changes, 'common': len(common), 'identical summaries': common.count([]),
                'differing fields': Counter(f for fs in common for f in fs)}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, help='prefix of each input for the timing trial')
    args = parser.parse_args()
    print(json.dumps(main(args.limit), indent=2))
