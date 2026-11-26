"""multi_class.py OUT.json: the census starts that keep two or more independent classes after one round of ordinary
growth under parity (8 on the canonical engine in TWO-CLASS-SIGN-20261126-001's census, 10 on the other), read for the
tower's first step: are their class labels whole-held, or can each be read inside one knot?  A label is readable inside
knot k when some functional supported on k's distinctions has even overlap with every move and is not fixed by the
knots' laws.  LAYERS-20261126-001 (a check by the thread, not registered)."""
import sys, json, gzip, collections, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import layers as LY
classes = LY.classes; forbid = LY.forbid
LY.TIE_CAP = 10 ** 6


def moves_of(supports):
    names = sorted({x for r in supports for x in r}); idx = {x: i for i, x in enumerate(names)}
    holders = collections.defaultdict(list)
    for k, r in enumerate(supports):
        for x in r: holders[x].append(k)
    U = len(supports); adj = collections.defaultdict(list)
    for x, h in holders.items():
        a, b = (h[0], h[1]) if len(h) == 2 else (h[0], U); adj[a].append((b, idx[x])); adj[b].append((a, idx[x]))
    moves = []
    for x, h in holders.items():
        a, b = (h[0], h[1]) if len(h) == 2 else (h[0], U); e = idx[x]
        dist = {a: 0}; Q = [a]
        for v in Q:
            for w, f in adj[v]:
                if f != e and w not in dist: dist[w] = dist[v] + 1; Q.append(w)
        if b not in dist: continue
        paths = [(b, 0)]
        while paths:
            v, mask = paths.pop()
            if v == a: moves.append(mask | (1 << e)); continue
            for w, f in adj[v]:
                if f != e and dist.get(w, -9) == dist[v] - 1: paths.append((w, mask | (1 << f)))
    return names, idx, moves


def read(supports):
    names, idx, moves = moves_of(supports); n = len(names)
    rows = [sum(1 << idx[x] for x in r) for r in supports]
    Z = classes.nullspace(rows, n); dH = classes.rank(moves)
    Hperp = classes.nullspace(moves, n)                        # functionals even on every move
    R = rows; rR = classes.rank(R)
    labels = [L for L in Hperp]
    dim_labels = classes.rank(R + Hperp) - rR                  # = dim Z - dim H
    out = {'classes': 2 ** (len(Z) - dH), 'label space': dim_labels, 'readable in one knot': []}
    for k, r in enumerate(supports):
        mask = sum(1 << idx[x] for x in r)
        # functionals supported on knot k, even on every move: solve on k's distinctions only
        ks = [idx[x] for x in r]
        mrows = [sum(((m >> i) & 1) << j for j, i in enumerate(ks)) for m in moves]
        sol = classes.nullspace(mrows, len(ks))
        vec = [sum(((v >> j) & 1) << i for j, i in enumerate(ks)) for v in sol]
        dim = classes.rank(R + vec) - rR                        # labels this knot can read, modulo the laws
        if dim: out['readable in one knot'].append([k, dim])
    out['one knot reads the whole label space'] = any(d == dim_labels for _, d in out['readable in one knot'])
    # the labels all knots together read, one at a time (the span of the per-knot readable labels)
    allvec = []
    for k, r in enumerate(supports):
        ks = [idx[x] for x in r]
        mrows = [sum(((m >> i) & 1) << j for j, i in enumerate(ks)) for m in moves]
        allvec += [sum(((v >> j) & 1) << i for j, i in enumerate(ks)) for v in classes.nullspace(mrows, len(ks))]
    out['labels read knot by knot'] = classes.rank(R + allvec) - rR
    return out


if __name__ == '__main__':
    S = forbid.census(); res = []
    data = [json.loads(l) for l in gzip.open(HERE.parent / 'TWO-CLASS-SIGN-20261126-001' / 'census_canonical.jsonl.gz', 'rt')]
    cand = [x for x in data if isinstance(x.get('after one round'), dict) and x['after one round']['loose free'].get('classes', 0) >= 4]
    start_multi = [x for x in data if isinstance(x.get('start'), dict) and x['start']['loose free'].get('classes', 0) >= 4]
    for x in cand + start_multi:
        i = int(x['structure'].split()[-1]); sup = forbid.supports_of(S[i])
        when = 'after one round' if x in cand else 'start'
        st = sup
        if when == 'after one round':
            st, status, births = forbid.grown(sup, 'parity', 'ordinary')
        r = read(st); r.update({'census index': i, 'when': when, 'knots': len(sup)})
        res.append(r); print(json.dumps(r), flush=True)
    json.dump(res, open(sys.argv[1], 'w'), indent=1)
