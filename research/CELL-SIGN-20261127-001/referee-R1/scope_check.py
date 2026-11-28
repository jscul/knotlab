"""Enumerate the strict minimal choices at holdings omitted from the signed listings."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from time import monotonic

from pysat.solvers import Minicard

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
INPUT = RESEARCH / "READER-SPLIT-20261127-001/referee-R1/rebuilt_inputs.jsonl"
PRIOR = RESEARCH / "ENCODED-READERS-20261127-001/referee-R1/meetings.json"


def require_even(solver, variables, next_id):
    """Encode each successive partial sum, with the last sum required to be zero."""
    if not variables:
        return next_id
    previous, *rest = variables
    for literal in rest:
        z = next_id
        next_id += 1
        for a, b, c in [(1, 1, -1), (-1, -1, -1), (1, -1, 1), (-1, 1, 1)]:
            solver.add_clause([a * previous, b * literal, c * z])
        previous = z
    solver.add_clause([-previous])
    return next_id


def dependencies(indices, columns):
    """Return a circuit inside a dependent set, eliminating in its listed order."""
    pivots = {}
    for pos in indices:
        checks, used = columns[pos], {pos}
        while checks:
            p = checks.bit_length()
            if p not in pivots:
                pivots[p] = (checks, used)
                break
            term, prior = pivots[p]
            checks ^= term
            used = used ^ prior
        else:
            # All preceding pivot columns form an independent set, so the
            # dependence containing this column has no dependent proper subset.
            return sorted(used)
    return []


def strict_words(source, *, minimal_only):
    keeping = defaultdict(list)
    for i, support in enumerate(source['supports']):
        for value in support:
            keeping[value].append(i)
    patterns, at_value, at_pair = [], defaultdict(list), defaultdict(list)
    for index, (x, y) in enumerate(source['pairs']):
        a, b = keeping[x]
        c, d = keeping[y]
        assert len({a,b,c,d}) == 4
        patterns.append((a,c,b,d))
        for value in (x,y):
            at_value[value].append(index + 1)
        for u in (a,b):
            for v in (c,d):
                at_pair[tuple(sorted([u,v]))].append(index + 1)
    columns = [0] * len(patterns)
    with Minicard() as solver:
        next_id = len(patterns) + 1
        for i, variables in enumerate(at_pair.values()):
            for var in variables:
                columns[var - 1] |= 1 << i
            next_id = require_even(solver, variables, next_id)
        for variables in at_value.values():
            if len(variables) > 1:
                solver.add_atmost(variables, 1)
        solver.add_clause(list(range(1,len(patterns) + 1)))
        while solver.solve():
            indices = [v - 1 for v in solver.get_model() if 0 < v <= len(patterns)]
            chosen = dependencies(indices, columns)
            assert chosen
            if minimal_only:
                # A circuit and its supersets cannot contain a new minimal word
                # as a subset of this circuit. Every other circuit remains feasible.
                selected = chosen
                blocking = [-(i+1) for i in chosen]
            else:
                selected = sorted(indices)
                included = set(indices)
                blocking = [-(i+1) if i in included else i+1 for i in range(len(patterns))]
            yield [patterns[i] for i in selected], [source['pairs'][i] for i in selected], len(chosen) == len(selected)
            solver.add_clause(blocking)


def can_orient(cycles):
    counts = defaultdict(list)
    for i, c in enumerate(cycles):
        for u, v in zip(c, c[1:] + c[:1]):
            counts[min(u,v),max(u,v)].append((1 << i, u < v))
    eqs = [(len(terms)//2, sum(bit for bit,_ in terms), sum(bit for bit,forward in terms if forward))
           for terms in counts.values()]
    assert all(len(t) % 2 == 0 for t in counts.values())
    # Global reversal preserves balance. Keep the final cycle's order fixed.
    orientable = any(all(((assignment ^ forward) & used).bit_count() == half for half,used,forward in eqs)
                     for assignment in range(1 << (len(cycles)-1)))
    return orientable


def run(probe):
    prior = { (pop, row['id']):row for pop, group in json.loads(PRIOR.read_text()).items() for row in group['rows'] }
    rows, first, totals = [], {}, defaultdict(Counter)
    considered = [r for r in map(json.loads, INPUT.read_text().splitlines())
                  if (r['population'], r['key']) in prior and prior[r['population'],r['key']]['strict_min'] is None]
    if probe:
        considered = [considered[0], max((r for r in considered if r['population']=='birth'),key=lambda r:len(r['pairs'])),
                      max((r for r in considered if r['population']=='type'),key=lambda r:len(r['pairs']))]
    for r in considered:
        pop, key = r['population'], r['key']
        tally = Counter()
        bound = len({d for s in r['supports'] for d in s}) // 2
        for lists, pairs, is_minimal in strict_words(r, minimal_only=True):
            assert is_minimal
            sign = sum((min(a,b)<c<max(a,b)) != (min(a,b)<d<max(a,b)) for a,c,b,d in lists) % 2
            assert not sign, (pop,key,pairs)
            oriented = can_orient(lists)
            result = 'orientable' if oriented else 'nonorientable'
            tally[f'{len(pairs)} pairs, {result}'] += 1
            totals[pop][result] += 1
            if not oriented and pop not in first:
                first[pop] = dict(id=key, failing_pairs=pairs, cycles=lists, planar=prior[pop,key]['minor'] is None)
        rows.append(dict(population=pop, id=key, natural_size_bound=bound, minimal_strict_even=dict(tally)))
        if probe:
            print(pop,key,bound,tally,flush=True)
    result = dict(scope="Every strict minimal choice at each studied holding without a strict odd choice; all cardinalities",
                  input="Earlier independent readers' rebuilt holdings and eligible failing pairs. Selection uses the encoded-readers referee's per-row strict minima.",
                  weighting="One per labelled choice at a given holding; each grown census start and each finished census type appears once in its own population.",
                  totals={k:dict(v) for k,v in totals.items()}, first_nonorientable_even=first, rows=rows)
    if not probe:
        (HERE / 'scope_check.json').write_text(json.dumps(result, indent=1)+'\n')
    print(result['totals'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe',action='store_true')
    opts = parser.parse_args()
    start = monotonic()
    run(opts.probe)
    print(f'{monotonic()-start:.3f} s')
