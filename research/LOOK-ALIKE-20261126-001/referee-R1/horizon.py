"""Check what the settled polynomials alone distinguish on dimension-two pairs."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
import gzip
from itertools import combinations, combinations_with_replacement
import json
from math import comb
from pathlib import Path
from time import monotonic

HERE = Path(__file__).resolve().parent


def nested(left, right):
    return (all(right.get(k, 0) >= v for k, v in left.items()) or
            all(left.get(k, 0) >= v for k, v in right.items()))


def coefficients(rows):
    a, b = rows[-2:]
    t = len(rows)
    return tuple(sorted((k, slope, b.get(k, 0) - t * slope)
                        for k in a.keys() | b.keys()
                        for slope in (b.get(k, 0) - a.get(k, 0),)))


def pattern_comparison(left, right, last_round):
    # For affine multiplicities, sign changes occur only at a real root.
    # One integer before, at, and after each root, plus the following
    # integer if the root is between rounds, covers all signs and zeros.
    delta = {k: (m, c) for k, m, c in left}
    for k, m, c in right:
        earlier_m, earlier_c = delta.get(k, (0, 0))
        delta[k] = earlier_m - m, earlier_c - c
    rounds = {last_round, last_round+1}
    for m, c in delta.values():
        if m:
            below = (-c) // m
            rounds.update(t for t in range(below-1, below+3) if t >= last_round)
    flags = []
    for t in sorted(rounds):
        signs = [m*t+c for m,c in delta.values()]
        flags.append((t, min(signs) >= 0 or max(signs) <= 0))
    return flags


def examine(records, reading):
    groups = defaultdict(list)
    for x in records:
        rows = [{json.dumps(k): v for k,v in row[reading]} for row in x['rows']]
        groups[coefficients(rows)].append((x['index'],rows))
    onset_example = None
    for group in groups.values():
        visited = {}
        for (i,a),(j,b) in combinations(group,2):
            r0 = 1 + max((t for t,(left,right) in enumerate(zip(a,b),1) if not nested(left,right)), default=0)
            visited.setdefault(r0,[i,j])
            if len(visited) >= 2:
                onset_example = {'same_polynomials_for_all_starts': True,'onsets_to_census_pair': visited}
                break
        if onset_example:
            break
    totals, examples = Counter(), {}
    for left, right in combinations_with_replacement(groups, 2):
        a,b = groups[left], groups[right]
        multiplicity = comb(len(a),2) if left==right else len(a)*len(b)
        if not multiplicity:
            continue
        flags = pattern_comparison(left, right, 24)
        category = ('nested_at_24' if flags[0][1] else 'incomparable_at_24')
        change = next(((t,v) for t,v in flags if v != flags[0][1]),None)
        key = category+('_changes_later' if change else '_unchanged_later')
        totals[key] += multiplicity
        if change and key not in examples:
            examples[key] = {'indices':[a[0][0],b[0][0]],'first_different_round':change[0],
                             'round_24_nested':flags[0][1], 'round_24_rows':[a[0][1][-1],b[0][1][-1]]}
    return {'five_knot_starts':len(records),'pairs':sum(totals.values()),'distinct_affine_views':len(groups),
            'same_polynomials_different_onsets':onset_example, 'conditional_counts':dict(totals),
            'conditional_examples': examples}


if __name__ == '__main__':
    p = ArgumentParser(description=__doc__)
    p.add_argument('--pilot',action='store_true')
    pilot=p.parse_args().pilot
    start=monotonic()
    records=[]
    with gzip.open(HERE.parent/'phase2_grown.jsonl.gz','rt') as data:
        for line in data:
            x=json.loads(line)
            if x['kind']=='dim 2':
                assert len(x['rows']) == 24
                records.append(x)
                if pilot and len(records)==100:
                    break
    result = {r:examine(records,r) for r in ('sig0','sig1')}
    result['interpretation'] = 'After round 24 these are conditional extrapolations of the final two recorded rounds. No later growth was used.'
    result['seconds']=round(monotonic()-start,3)
    name = 'horizon_pilot.json' if pilot else 'horizon.json'
    (HERE/name).write_text(json.dumps(result,indent=2)+'\n')
    print(name, result['seconds'])
