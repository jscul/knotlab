"""Find the first meeting for every wholly apart pair in selected independently regrown runs."""
import argparse
from collections import Counter, defaultdict
from functools import reduce
import gzip
from itertools import combinations, product
import json
from operator import or_
from pathlib import Path
from time import perf_counter

from b_growth import Law, bar, grow

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = next((ROOT / 'artifacts' / (HERE.parent.name + 'B')).glob('*E001*'))


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask -= bit


def eligible(parts, state):
    owners = defaultdict(set)
    for i, part in enumerate(parts):
        for member in part:
            for d in state.knots[member].places:
                owners[d].add(i)
    classes = [{i} for i in range(len(parts))]
    for share in owners.values():
        if len(share) > 1:
            cls = set().union(*(classes[i] for i in share))
            for i in cls:
                classes[i] = cls
    return {(i, j) for i, j in combinations(range(len(parts)), 2) if j not in classes[i]}


def first_meetings(run, s):
    parts = run.steps[s + 1].roster.parts
    pending = eligible(parts, run.states[s])
    apart = pending.copy()
    knots = run.states[-1].knots
    membership = [0] * len(knots)
    for i, part in enumerate(parts):
        for k in part:
            membership[k] = 1 << i
    for k in range(len(run.states[s].knots), len(knots)):
        membership[k] = reduce(or_, (membership[p] for p in knots[k].parents), 0)
    found = {}
    for t in range(s + 1, len(run.states)):
        if not pending:
            break
        step = run.steps[t]
        stage = run.states[t - 1]
        meetings = set()
        for group in (*step.groups, *step.demand_groups):
            mask = reduce(or_, (membership[k] for k in group), 0)
            meetings.update(pair for pair in combinations(indices(mask), 2) if pair in pending)
        suppliers = defaultdict(set)
        for birth in step.births.values():
            for d in birth.takes:
                for holder in stage.holders[d]:
                    for i, j in product(indices(membership[birth.knot]), indices(membership[holder])):
                        if i == j:
                            continue
                        pair = tuple(sorted((i,j)))
                        if pair in pending:
                            meetings.add(pair)
                            suppliers[pair].add(holder)
        linkers = {pair: set(suppliers[pair]) for pair in meetings}
        if meetings:
            for roster in (step.roster, step.demand_roster):
                for w, met in roster.met_sets.items():
                    if w >= len(stage.knots):
                        continue
                    mask = reduce(or_, (membership[k] for k in met), 0)
                    for pair in combinations(indices(mask), 2):
                        if pair in meetings:
                            linkers[pair].add(w)
        for (i,j), links in linkers.items():
            for a,b in ((i,j),(j,i)):
                found[a,b] = (t, tuple(sorted(links)))
        pending -= meetings
    return apart, found


def knot_sample(run, law):
    """Project onto each knot. With fresh births the earlier stages retain all old states."""
    from pysat.solvers import Solver
    stage = run.states[-1]
    if law.knot_law == 'nae':
        def clauses(places):
            pos = [d+1 for d in places]
            return [pos, [-v for v in pos]]
        start = run.states[0]
        checked = 0
        failures = []
        with Solver(bootstrap_with=[cl for k in start.knots for cl in clauses(k.places)]) as solver:
            for i, knot in enumerate(start.knots):
                results = [solver.solve(assumptions=[(1 if b else -1)*(d+1) for d,b in zip(knot.places, bits)])
                           == (len(set(bits)) == 2) for bits in product((0,1), repeat=len(knot.places))]
                checked += 1
                if not all(results):
                    failures.append(i)
            for t, step in sorted(run.steps.items()):
                for i, birth in step.births.items():
                    assert birth.fresh
                    if not all(solver.solve(assumptions=[(1 if b else -1)*(d+1) for d,b in zip(birth.inputs,bits)])
                               for bits in product((0,1), repeat=len(birth.inputs))):
                        failures.append(i)
                    checked += 1
                for i in step.births:
                    for cl in clauses(stage.knots[i].places):
                        solver.add_clause(cl)
    else:
        # Each original distinction is a linear function of the free variables.
        pivots = {}
        for knot in stage.knots:
            row = sum(1 << d for d in knot.places)
            while row:
                p = row.bit_length()-1
                if p not in pivots:
                    pivots[p] = row ^ (1 << p)
                    break
                row ^= pivots[p] | (1 << p)
        expr = {}
        for d in sorted(stage.holders):
            if d not in pivots:
                expr[d] = 1 << d
            else:
                expr[d] = 0
                for v in indices(pivots[d]):
                    expr[d] ^= expr[v]
        failures = []
        for i, knot in enumerate(stage.knots):
            basis = {}
            for d in knot.places:
                value = expr[d]
                while value:
                    p = value.bit_length()-1
                    if p not in basis:
                        basis[p] = value
                        break
                    value ^= basis[p]
            if len(basis) != len(knot.places)-1:
                failures.append(i)
        checked = len(stage.knots)
    return {'different_knots_checked': checked, 'failed_knots': failures}


def inspect(item):
    law = Law(**item['law'])
    run = grow(item['stars'], law)
    counts = Counter()
    mismatches = []
    tested = []
    for s in range(1, min(5, len(run.states)-1)):
        apart, found = first_meetings(run, s)
        archived = {(p['X_part'],p['Y_part']): (p['meeting_round'], tuple(sorted(w['knot'] for w in p['linking'])))
                    for p in item['pairs'] if p['s'] == s}
        recorded = item['s'][str(s)]
        negatives = {tuple(pair) for pair in recorded['no_meeting_pairs']}
        if found != archived or set(archived) | negatives != (apart | {(j,i) for i,j in apart}):
            mismatches.append({'split': s, 'reconstructed': len(found), 'archived': len(archived)})
        counts['wholly_apart_ordered_pairs'] += 2*len(apart)
        counts['ordered_meetings'] += len(found)
        counts['made_only'] += sum(bool(links) and all(run.states[t].knots[k].made > 0 for k in links)
                                   for t,links in found.values())
        # One named positive per knot law. Branch selection is lexicographic among
        # independently recovered meetings on the specified cyclic five-knot start.
        if found and s == 4 and item['start'] == 'Ring(5,3)' and item['law_id'] == 'L10':
            i,j = min(found)
            x,y = (run.steps[s+1].roster.parts[n] for n in (i,j))
            for usable in [(),(y[0],),(y[1],),y]:
                variant = bar(run,s,set(y)-set(usable),law)
                focus = next(b for b in variant.steps[5].births.values() if set(b.parents) == set(x))
                off = [b for b in variant.steps[6].births.values() if b.parents == (focus.knot,)]
                tested.append({'x': x, 'y': y, 'y_usable': usable, 'round5_demand': focus.demand,
                               'round5_fresh': len(focus.fresh), 'round6_offshoot_fresh': [len(b.fresh) for b in off],
                               **knot_sample(variant, law)})
    return {'start': item['start'], 'law': item['law_name'], 'counts': counts, 'mismatches': mismatches,
            'projection_sample': tested}


def main(smoke):
    keep = {'L02','L05','L10'}
    cases = []
    for filename in ('run1a.jsonl.gz', 'runU1.jsonl.gz'):
        with gzip.open(DATA / filename, 'rt') as stream:
            cases.extend(item for item in map(json.loads,stream) if item['law_id'] in keep)
    selected = [r for r in cases if r['start']=='Ring(5,3)' and r['law_id']=='L10'] if smoke else cases
    result = [inspect(r) for r in selected]
    total = Counter()
    for row in result:
        total.update(row['counts'])
    summary = {'configurations':len(result), 'counts':total, 'configs_with_mismatches':sum(bool(r['mismatches']) for r in result)}
    if not smoke:
        (HERE / 'b_meetings.json').write_text(json.dumps({'summary':summary, 'rows':result}, indent=2)+'\n')
    print(summary)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--smoke', action='store_true')
    start = perf_counter()
    main(parser.parse_args().smoke)
    print('seconds', round(perf_counter()-start, 3))
