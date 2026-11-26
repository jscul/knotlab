"""Compare uniform accepted starts with the same maximal blocks and loose distinctions."""
import argparse
from collections import Counter, defaultdict
import gzip
from itertools import combinations, groupby, islice, permutations, product
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent


def structure(stars, with_places):
    knots = list(map(set, stars))
    use = Counter(d for knot in knots for d in knot)
    loose = [sum(use[d] == 1 for d in knot) for knot in knots]
    live = [i for i, n in enumerate(loose) if n]
    candidates = {frozenset(i for i in live if i != j and k & knots[i]) for j,k in enumerate(knots)}
    blocks = [a for a in candidates if len(a) >= 2 and not any(a < b for b in candidates)]
    # Sort only by invariants. Enumerate every ordering within an invariant class.
    def label(i):
        return loose[i], (len(knots[i]) if with_places else 0), tuple(sorted(len(b) for b in blocks if i in b))
    groups = [tuple(g) for _,g in groupby(sorted(live, key=label), key=label)]
    colors = tuple(label(i) for g in groups for i in g)
    def encode(parts):
        position = {v:i for i,v in enumerate(v for part in parts for v in part)}
        return tuple(sorted(tuple(sorted(position[v] for v in b)) for b in blocks))
    return colors, min(encode(parts) for parts in product(*(permutations(g) for g in groups)))


def counts(with_places, rows):
    groups = defaultdict(list)
    for x in rows:
        groups[structure(x['stars'], with_places)].append(x)
    out = Counter()
    examples = []
    for arr in groups.values():
        out['distinct maps'] += 1
        out['starts'] += len(arr)
        hetero = False
        for x, y in combinations(arr, 2):
            out['same map pairs'] += 1
            first = [i for i,(a,b) in enumerate(zip(x['rows'], y['rows']), start=1) if a['sig1'] != b['sig1']]
            if first:
                hetero = True
                out['different first parent reading'] += 1
                if len(examples) < 2:
                    examples.append({'indices': [x['index'], y['index']], 'differing_rounds': first,
                                     'stars': [x['stars'], y['stars']],
                                     'first_parent_readings': [x['rows'][0]['sig1'], y['rows'][0]['sig1']]})
            if any(a['sig0'] != b['sig0'] for a,b in zip(x['rows'],y['rows'])):
                out['different first reading without parent descriptions'] += 1
            if x['end'] != y['end'] or len(x['rows']) != len(y['rows']):
                out['different recorded end'] += 1
            if any(t > 1 for t in first):
                out['different parent reading past round one'] += 1
        if hetero:
            out['maps split by parent reading'] += 1
    return {'tallies': out, 'example_pairs': examples}


def run(limit):
    accepted = set()
    with gzip.open(STUDY / 'predictions.jsonl.gz', 'rt') as f:
        for line in f:
            p = json.loads(line)
            if (p['set'], p['knot law'], p['read']) == ('uniform','nae','predicted'):
                accepted.add(p['index'])
    with gzip.open(STUDY / 'held_out_nae.jsonl.gz', 'rt') as f:
        rows = list(islice((x for x in map(json.loads,f) if x['index'] in accepted), limit))
    return {'uniform not-all-equal, same map without starting places': counts(False, rows),
            'uniform not-all-equal, same map including starting places': counts(True, rows)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    t = time.monotonic()
    out = run(32 if args.pilot else None)
    out['elapsed_seconds'] = round(time.monotonic()-t,3)
    name = 'start_places_pilot.json' if args.pilot else 'start_places.json'
    (HERE / name).write_text(json.dumps(out,indent=2)+'\n')
    print(name, out['elapsed_seconds'])
