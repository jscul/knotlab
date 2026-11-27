"""Compare individual parent rosters with ordinary growth, before comparing readouts."""
import argparse
import json
from collections import Counter, defaultdict
from itertools import combinations
from reading import HERE, alike, allocations, core, map_data, predict, observed
from overlaps import case


def twins(births):
    out = []
    for a, b in combinations(births, 2):
        if births[a].grade != births[b].grade:
            continue
        for c, d in combinations(sorted(set(births[a].parents) & set(births[b].parents)), 2):
            for f in sorted(set(births[c].parents) & set(births[d].parents)):
                if births[f].base_chains:
                    out.append(dict(grade=births[a].grade, pair=[a, b], shared=[c, d], ancestor=f,
                                    chains=births[f].base_chains))
    return out


def configs(bs, t):
    for i, b in bs.items():
        if b.grade > t:
            continue
        for l in allocations(b.base_chains, t - b.grade):
            yield i, l


def parents(bs, i, l):
    e = {a for a, n in l}
    ps = [(p, l) for p in bs[i].parents if e <= set(bs[p].base_chains)]
    for j, (a, n) in enumerate(l):
        shorter = ((a, n - 1),) if n > 1 else ()
        ps.append((i, l[:j] + shorter + l[j+1:]))
    return ps


def label(config):
    i, l = config
    return str(i) + ''.join(f'+{a[0]}.{a[1]}x{n}' for a, n in l)


def trace(stars, law, depth):
    bs = core(stars, law, depth)
    mapped = {k: (k, ()) for k in bs if bs[k].grade == 0}
    state = alike.eng.from_stars(stars)
    ordinary = alike.eng.Law('ORD', 'CANCEL-WAIT', None, law)
    step = alike.eng.Guard(100)
    pred = predict(stars, law, depth)
    growth = alike.grow(stars, depth, knot_law=law)
    first = []
    for t, row in enumerate(growth['rows'], 1):
        g = observed(row)
        if g != pred[t - 1]:
            for a, b in zip(g, pred[t - 1]):
                first.append(dict(actual_only=list((a-b).items()), predicted_only=list((b-a).items())))
            break
    out = dict(first_readings=first, twins=twins(bs))
    for t in range(1, depth + 1):
        expected, grown = defaultdict(list), defaultdict(list)
        for c in configs(bs, t):
            expected[tuple(sorted(parents(bs, *c)))].append(c)
        record = alike.eng.play_round(state, ordinary, step)
        for b in record['births']:
            grown[tuple(sorted(mapped[p] for p in b['parents']))].append(b['id'])
        want, got = Counter({k:len(v) for k,v in expected.items()}), Counter({k:len(v) for k,v in grown.items()})
        if got != want:
            def show(diff):
                return [([label(c) for c in k], m) for k, m in diff.items()]
            out['roster'] = dict(grade=t, actual_only=show(got-want), predicted_only=show(want-got))
            disputed = {c for k in (got-want) for c in k} | {c for k in (want-got) for c in k}
            out['previous'] = {label(c): [label(p) for p in parents(bs,*c)] for c in sorted(disputed)}
            break
        for k, cc in expected.items():
            for bid, cfg in zip(sorted(grown[k]), sorted(cc)):
                mapped[bid] = cfg
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--depth', type=int, default=8)
    p.add_argument('--limit', type=int, default=3)
    args = p.parse_args()
    cases = [('ten knots, two groups with two shared knots', case(2)[0])]
    with (HERE.parent/'replays.jsonl').open() as f:
        cases.append(('six-knot census miss', json.loads(next(f))['stars']))
    with (HERE.parent/'held_grow.jsonl').open() as f:
        cases.append(('seven-knot held-out miss', next(r['stars'] for r in map(json.loads,f) if r['draw']==257587)))
    for name, stars in cases[:args.limit]:
        for law in ('nae','parity'):
            print(json.dumps(dict(start=name, stars=stars, law=law, **trace(stars,law,args.depth))), flush=True)
