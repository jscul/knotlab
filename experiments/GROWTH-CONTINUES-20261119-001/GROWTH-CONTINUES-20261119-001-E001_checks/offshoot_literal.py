"""Reconstruct two complete rounds directly on distinct parity supports for each positive witness."""
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
TICKET = 'GROWTH-CONTINUES-20261119-001'
sys.path.insert(0, str(next((ROOT / 'experiments/GROWN-END-SWAP-20261119-001').glob('*-E001_reached'))))
from verify import Arrangement, groups, round_replay, start_audit

def initial(row):
    sizes = row['sizes']
    stars = [[] for _ in sizes]
    for label, (u, v) in enumerate(row['edges']):
        stars[u].append(label)
        stars[v].append(label)
    label = len(row['edges'])
    for target, star in zip(sizes, stars):
        count = target - len(star)
        star.extend(range(label, label + count))
        label += count
    return Arrangement.parse(stars)


def one_round(stage):
    loose = defaultdict(list)
    for label, v in sorted(stage.loose.items()):
        loose[v].append(label)
    legal = sorted(groups(stage.neighbors, stage.live), key=lambda g: tuple(sorted(g)))
    usage = Counter(v for g in legal for v in g)
    assert all(usage[v] <= len(loose[v]) for v in stage.live)
    parents = [*legal, *(frozenset((v,)) for v in sorted(stage.live) for _ in range(len(loose[v])-usage[v]))]
    assert len(parents) >= 2
    first = len(stage.stars)
    neighbors = [set(s) for s in stage.neighbors] + [set(s) for s in parents]
    for i, group in enumerate(parents, first):
        for v in group:
            neighbors[v].add(i)
    fresh_demand = Counter(v for g in groups(neighbors, set(range(first, len(neighbors)))) for v in g)
    stars = [sorted(s) for s in stage.stars]
    name = max(stage.labels) + 1
    for i, group in enumerate(parents, first):
        used = [loose[v].pop(0) for v in sorted(group)]
        count = max(fresh_demand[i], 3 - len(group), 1)
        stars.append(used + list(range(name, name + count)))
        name += count
    nxt = Arrangement.parse(stars)
    checked = round_replay(stage, nxt)
    assert len(checked) == len(parents) and all(not r['implied'] for r in checked)
    return nxt, list(map(sorted, parents))


def parity_gate(arity):
    names = [f'x{i}' for i in range(arity - 1)] + ['c']
    clauses = [' '.join('~'+name if value else name for name, value in zip(names, bits))
               for bits in product((0, 1), repeat=arity) if sum(bits) % 2]
    run = subprocess.run([sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', '; '.join(clauses),
                          '--loops', *names[:-1], '--contact', 'c', '--erasure', 'forgetting', '--json'],
                         check=True, capture_output=True, text=True, cwd=ROOT,
                         env={**os.environ, 'PYTHONPATH': str(ROOT/'tools')})
    row = json.loads(run.stdout)
    assert row['is_knot'] and len(row['allowed']) == 2**(arity-1)
    return {k: row[k] for k in ('binding', 'invisible_in_parts', 'coexistence', 'is_knot', 'erasure')}


def main():
    old = next((ROOT / 'artifacts/HUB-GUIDED-SAMPLE-20261119-001').glob('*/stages.json'))
    starts = json.loads(old.read_text())['literal_starts']
    out = {}
    for key in ('start-03', 'start-14'):
        stage = initial(starts[key])
        audit = start_audit(stage)
        assert audit['census_open_legal']
        v = next(v for v in sorted(stage.live)
                 if list(stage.loose.values()).count(v) == 2 and
                 sum(v in g for g in groups(stage.neighbors, stage.live)) == 1)
        witness = {'initial_junction': v, 'initial_loose': sorted(x for x,j in stage.loose.items() if j == v),
                   'start_audit': audit, 'rounds': []}
        for t in (1, 2):
            first = len(stage.stars)
            nxt, parents = one_round(stage)
            siblings = [(first+i,g) for i,g in enumerate(parents) if v in g]
            assert len(siblings) == 2
            offshoot, = (j for j,g in siblings if len(g) == 1)
            other, = (j for j,g in siblings if len(g) >= 2)
            assert {j for j in nxt.live if j != offshoot and nxt.neighbors[j] & nxt.neighbors[offshoot]} == {other}
            fresh = sorted(x for x, j in nxt.loose.items() if j == offshoot)
            assert len(fresh) == 2
            witness['rounds'].append({'round': t, 'all_parents': parents, 'first_child_name': first,
                                      'offshoot': offshoot, 'only_candidate': other,
                                      'fresh_distinctions_on_offshoot': fresh})
            v, stage = offshoot, nxt
        out[key] = witness
    restricted = {key: start_audit(initial(starts[key])) for key in ('start-08', 'start-15')}
    assert [restricted[k]['non_outside_cut_holders'] for k in restricted] == [[3], [4]]
    out['two_restricted_starting_presentations'] = restricted
    arities = {n for key in ('start-03', 'start-14') for n in starts[key]['sizes']}
    out['projected_parity_by_arity'] = {n: parity_gate(n) for n in sorted(arities)}
    path = ROOT/'artifacts'/TICKET/(TICKET+'-E001_checks')/'offshoot_literal.json'
    path.write_text(json.dumps(out, indent=2)+'\n')


if __name__ == '__main__':
    main()

