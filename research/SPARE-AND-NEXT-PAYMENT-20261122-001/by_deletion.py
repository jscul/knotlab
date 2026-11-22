"""Reconstruct the archived pair from connected sets and independent deletion parents.

The integers below are names in a checking representation. The continued
families and the added opening are identified only when comparing the results.
"""
from collections import Counter, defaultdict
from itertools import combinations, product
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = next((ROOT / "artifacts" / "COPIES-AND-MEETINGS-20261120-001A").rglob("mediator.json"))
ATTACHED = 1000
START = range(6)
LAUNCHES = (frozenset((-1, 0)), frozenset((5, 6)))


def levels(extra):
    current = {frozenset((k,)) for k in START}
    result = [current]
    for _ in range(9):
        larger = set()
        for cell in current:
            for k in cell:
                adjacent = (4,) if k == ATTACHED else (k - 1, k + 1)
                if k == 4 and extra:
                    adjacent += (ATTACHED,)
                larger.update(cell | {j} for j in adjacent if j not in cell)
        result.append(larger)
        current = larger
    return result


def deletion_parents(cell, previous):
    return [cell - {k} for k in cell if cell - {k} in previous]


def common(cell):
    return all(launch <= cell for launch in LAUNCHES)


def block_forecast(families):
    """Propose groups using only their older parent incidence, before any grant."""
    groups = {k: frozenset(v) for k, v in families.items()}
    neighbors = {k: {j for j in groups if k != j and groups[k] & groups[j]} for k in groups}
    complete = set()
    for k, adjacent in neighbors.items():
        later = sorted(j for j in adjacent if j > k)
        for n in range(2, len(later) + 1):
            for rest in combinations(later, n):
                row = (k, *rest)
                if all(j in neighbors[i] for i, j in combinations(row, 2)):
                    complete.add(frozenset(row))
    large = {s for s in complete if not any(s < t for t in complete) and not set.intersection(*(set(groups[k]) for k in s))}
    pairs = {frozenset((k,j)) for k in groups for j in neighbors[k] if k < j
             and not any(k in s and j in s for s in large)}
    return sorted(tuple(sorted(s)) for s in large | pairs)


def build(source, extra):
    shapes = levels(extra)
    prior = {frozenset((k,)): k for k in START}
    degrees = Counter(d for row in source for d in row)
    opens = {k: [d for d in row if degrees[d] == 1] for k, row in enumerate(source)}
    fresh_id, child_id = max(degrees) + 1, len(source)
    records = []
    for step in range(1,9):
        before, now, following = shapes[step-1:step+2]
        names = {s: tuple(sorted(prior[p] for p in deletion_parents(s, before))) for s in now}
        demand = Counter(p for child in following for p in deletion_parents(child, now))
        def roster_key(s):
            row = names[s]
            return ((0 if len(row) > 2 else 1 if len(row) == 2 else 2),row)
        remaining = {k: iter(sorted(ds)) for k, ds in opens.items()}
        current, fresh, rows = {}, {}, []
        for cell in sorted(now, key=roster_key):
            parents = names[cell]
            paid = [next(remaining[k]) for k in parents]
            grant = demand[cell]
            assert grant >= max(1, 3-len(parents))
            bank = list(range(fresh_id, fresh_id+grant))
            rows.append(dict(knot=child_id, parents=list(parents), inputs=paid, fresh=bank,
                             shape=sorted(cell), common=common(cell)))
            current[cell], fresh[child_id] = child_id, bank
            child_id += 1
            fresh_id += grant
        assert all(next(q, None) is None for q in remaining.values())
        records.append(rows)
        prior, opens = current, fresh
    eighth, ninth = records[-2:]
    holder, = [row for row in eighth if row['common']]
    older_parents = {r['knot']:r['parents'] for r in eighth}
    forecast = block_forecast(older_parents)
    offers = [list(row) for row in forecast if holder['knot'] in row]
    children = [row for row in ninth if holder['knot'] in row['parents']]
    assert {tuple(p) for p in offers} == {tuple(r['parents']) for r in children}
    assert children == [r for r in ninth if r['common']]
    flags = {r['knot']:sum(1<<i for i, launch in enumerate(LAUNCHES) if launch <= set(r['shape'])) for r in eighth}
    grants = sum((r['fresh'] for r in eighth), [])
    realized = {v: r['knot'] for r in ninth for v in r['inputs']}
    assert len(grants) == len(realized) and set(grants) == set(realized)
    for child in children:
        child['parent_ancestry'] = [flags[p] for p in child['parents']]
        child['older_witnesses_by_pair'] = [[i,j,sorted(set(older_parents[i]) & set(older_parents[j]))] for i,j in combinations(child['parents'],2)]
    pure = [next(r['knot'] for r in ninth if r['shape'] == sorted(c)) for c in
            (set(range(-8,1)),set(range(5,14)))]
    receipt = {'first_common':holder,'next_common':children,'forecast_before_grant':offers,
               'other_size_nine_births':len(ninth)-len(children),'pure_next':pure,
               'whole_roster_sizes':[len(layer) for layer in records],
               'arities':sorted({len(r['parents'])+len(r['fresh']) for layer in records for r in layer} | set(map(len,source)))}
    launches = {r['knot']: {r['knot']} for r in records[0]}
    for rows in records[1:]:
        for r in rows:
            launches[r['knot']] = set.union(*(launches[p] for p in r['parents']))
    if extra:
        spare = next(r for r in records[0] if r['shape'] == [4, ATTACHED])
        joint, = [r for r in children if len(r['parents']) == 3]
        receipt['extra_source_route'] = {'first_payment':spare,
            'size_two_ancestors_of_H':sorted(launches[holder['knot']]),
            'size_two_ancestors_of_three_payers':{p:sorted(launches[p]) for p in joint['parents']}}
    return receipt, records


def canonical(law, arity):
    names = [f'x{k}' for k in range(arity)]
    def allowed(bits):
        return sum(bits)%2 == 0 if law == 'parity' else len(set(bits)) == 2
    forbidden = [bits for bits in product((0,1),repeat=arity) if not allowed(bits)]
    clauses = [' '.join(('~' if bit else '')+name for name,bit in zip(names,bits)) for bits in forbidden]
    cmd = [sys.executable,'-B','-m','knotlab','check','--cnf',';'.join(clauses),
           '--loops',*names[:-1],'--contact',names[-1],'--json']
    result = json.loads(subprocess.check_output(cmd,cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT/'tools')}))
    assert result['is_knot']
    return {'arity':arity,'allowed':2**arity-len(forbidden),'is_knot':True}


def main():
    archive = json.loads(ARCHIVE.read_text())['both_laws']
    out = {}
    for law in ('parity','nae'):
        old = archive[law]['near_right_spare']
        arms = {}
        for i, arm in enumerate(('base','extra')):
            result, _ = build(old['sources'][i], bool(i))
            h, original = result['first_common'],old['first_mixed'][i]
            for left, right in [('knot','knot'),('inputs','consumed'),('parents','parents'),('fresh','fresh')]:
                assert h[left] == original[right]
            assert result['whole_roster_sizes'] == [row['births'][i] for row in old['by_size']]
            assert len(result['next_common']) == old['by_size'][-1]['both_launches'][i]
            result['canonical_relations'] = [canonical(law,n) for n in result['arities']]
            arms[arm] = result
        out[law] = arms
    (HERE/'by_deletion.json').write_text(json.dumps(out,indent=2)+'\n')
    for arm,result in out['parity'].items():
        print(arm,result['first_common'],result['forecast_before_grant'])
        for child in result['next_common']:
            print(child['knot'],child['parents'],child['inputs'],child['fresh'],child['parent_ancestry'],child['older_witnesses_by_pair'])


if __name__ == '__main__':
    main()
