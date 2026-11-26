"""Compare the implication tested after adding one loose distinction with the current knot equations."""
import argparse
import json
import random
from collections import Counter
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import parity
from archive import STUDY, key, read_rows

core = parity.shortage
eng = core.eng


def insert(pivots, word):
    while word:
        place = (word & -word).bit_length() - 1
        if place not in pivots:
            pivots[place] = word
            return True
        word ^= pivots[place]
    return False


def holds(pivots, word):
    while word:
        term = pivots.get((word & -word).bit_length() - 1)
        if term is None:
            return False
        word ^= term
    return True


def equation(places):
    return sum(1 << d for d in places)


def check(row, through):
    a, b, law = row['A'], row['B'], core.law_of(*row['law'])
    places, roles, _ = core.jam.changed(a, b, 3, None, 'meeting')
    base = core.ring_line.Growth(places, roles, law)
    base.run(3, 1500)
    assert len(base.rows) == 3
    targets = []
    for linked, count in [(True,5),(False,2)]:
        knots, _ = core.linked.far_members(base, 3, linked)
        targets.extend(knots[:count])
    assert len(targets) == len(row['changes'])
    discrepancies = []
    checks = Counter()
    for u, change in zip(targets, row['changes']):
        fork = core.ring_line.fork_at(base, 3)
        core.ring_line.mark(fork, u)
        state = fork.S
        correct = {}
        for ps in state.places:
            insert(correct, equation(ps))
        assert not eng.basis_contains(state.basis, equation(state.places[u]))
        checks['placements'] += 1
        for t in range(4, min(through, change['rounds']) + 1):
            before = len(state.places)
            rec = eng.play_round(state, law, fork.G)
            checks['placement rounds'] += 1
            mismatch = []
            for birth in rec['births']:
                actual = holds(correct, equation(birth['inputs']))
                checks['tested birth inputs'] += 1
                if actual != birth['implied']:
                    mismatch.append({'id': birth['id'], 'kind': birth['kind'], 'parents': birth['parents'],
                                     'inputs': birth['inputs'], 'archived rule': birth['implied'],
                                     'rule of current places': actual, 'demand': birth['D']})
            if mismatch:
                discrepancies.append({'target': u, 'first differing round': t, 'births': mismatch,
                                      'archive reading': change})
                break
            for ps in state.places[before:]:
                insert(correct, equation(ps))
    return {'A': a, 'B': b, 'law': row['law'], 'checks': checks, 'discrepancies': discrepancies}


def control():
    source = (STUDY / 'referee-R1' / 'argument_witnesses.jsonl').read_text().splitlines()
    case = next(item['result'] for line in source if (item := json.loads(line))['case'] == 'parity')
    places = case['stars']
    initial = core.ring_line.Growth(places, ['control'] * len(places), core.law_of('ORD','MET','OLDEST'))
    core.ring_line.mark(initial, 0)
    result = {}
    for name in ('recorded', 'rebuilt'):
        state = initial.S.copy()
        if name == 'rebuilt':
            state.basis = {}
            for ps in state.places:
                eng.basis_insert(state.basis, equation(ps))
        rec = eng.play_round(state, initial.law, eng.Guard(4))
        result[name] = [{k: b[k] for k in ('id','parents','inputs','implied','D','f')} for b in rec['births']]
    first, second = (result[name][0] for name in ('recorded', 'rebuilt'))
    assert first['inputs'] == second['inputs'] == [10, 11, 2]
    assert (first['implied'], first['f'], second['implied'], second['f']) == (True, 0, False, 1)
    return result


def summary():
    def load_lines(name):
        return list(map(json.loads, (HERE / name).read_text().splitlines()))

    fourth = load_lines('mark_round4.jsonl')
    seeded = load_lines('mark_sample.jsonl')
    fifth = load_lines('mark_heard5.jsonl')
    paired = json.loads((HERE / 'replay.json').read_text())['cases']
    complete = {(r['key'][0], r['key'][1], tuple(r['key'][2][1:])) for r in paired}
    complete.update(key(r) for r in seeded + fifth)
    counts = Counter()
    for r in read_rows(STUDY / 'parity_runs.jsonl.gz', None):
        for c in r.get('changes', []):
            if key(r) not in complete and c['rounds'] > 4:
                counts['full changed window not covered'] += 1
                if c['heard'] is None:
                    counts['unheard full changed window not covered'] += 1
    result = {}
    for name, arm in [('fourth round', fourth), ('whole-window sample', seeded), ('round five hearings', fifth)]:
        checks = Counter()
        for r in arm:
            checks.update(r['checks'])
        result[name] = dict(checks, records=len(arm),
                            discrepant_placements=sum(len(r['discrepancies']) for r in arm))
    return dict(coverage=counts, tests=result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--summary', action='store_true', help='combine completed checks')
    parser.add_argument('--heard-five', action='store_true', help='retain records with a first hearing in round five')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--through', type=int, default=4)
    parser.add_argument('--seed', type=int, default=20261127)
    parser.add_argument('--skip', type=int, default=0)
    args = parser.parse_args()
    if args.summary:
        print(json.dumps(summary(), indent=2))
        raise SystemExit(0)
    if args.control:
        print(json.dumps(control(), indent=2))
        raise SystemExit(0)
    core.receivers.register()
    rows = [r for r in read_rows(STUDY / 'parity_runs.jsonl.gz', None) if r.get('changes')]
    if args.heard_five:
        rows = [r for r in rows if any(c['heard'] == 5 for c in r['changes'])]
    random.Random(args.seed).shuffle(rows)
    for r in rows[args.skip:][:args.limit]:
        print(json.dumps(check(r,args.through)), flush=True)
