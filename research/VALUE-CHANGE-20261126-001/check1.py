"""check1.py: the advisor's first check (README.md, part A). Under rule R read off the whole structure, two births
(knots beyond the start) commute exactly when, by the advisor's hand argument:
    born in one round           |u| |v| = common parents + common children   (mod 2)
    parent and child            not both with an even number of places
    two rounds apart            |u| |v| = knots that are a child of one and a parent of the other   (mod 2)
    three or more rounds apart  not both with an odd number of places
and so R fails on every structure with six rounds of births. A fifth class the table leaves out, one round apart but
not parent and child, is checked with the rule of pairs three or more apart (not both odd). Grown: the 300 sampled census starts of
EVENTUAL-R-20261126-001 (seed 20261128), ordinary parity growth on the canonical engine, up to six rounds; a structure
over CAP knots is cut at the last round under it (reported). Pairs are compared only where both knots are settled
(a pair with an open place pair, both loose in different newest knots, is left out).
    check1.py COUNT ROUNDS CAP"""
import sys, json, random, itertools, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'EVENTUAL-R-20261126-001')); sys.path.insert(0, str(HERE.parent / 'FORBID-EDITS-20261126-001'))
import ops, forbid            # noqa: E402


def grow(start, rounds, cap):
    stages = [tuple(tuple(k) for k in start)]; births = []; end = 'growing'
    for r in range(1, rounds + 1):
        new, status, bs = forbid.grown(stages[-1], 'parity', 'ordinary')
        if status != 'funded': end = status if status in ('closed',) else 'stalled'; break
        if len(new) > cap: end = 'cut at the cap'; break
        stages.append(tuple(tuple(k) for k in new)); births.append(bs)
    return stages, births, end


def check(stages, births, end):
    F = [list(k) for k in stages[-1]]; n = len(F)
    rnd = {}
    for t, st in enumerate(stages):
        for u in range(len(st)): rnd.setdefault(u, t)
    parents = collections.defaultdict(set); children = collections.defaultdict(set)
    for t, bs in enumerate(births):
        for b in bs:
            for p in b['parents']: parents[b['knot']].add(p); children[p].add(b['knot'])
    h = ops.holders(F); loose = {d for d, hs in h.items() if len(hs) == 1}; co = ops.coheld(F)
    final = end in ('closed', 'stalled')
    last = len(stages) - 1
    tally = collections.Counter(); fails_settled = 0
    for u, v in itertools.combinations(range(n), 2):
        anti = 0; open_ = False
        for e in F[u]:
            for f in F[v]:
                if e == f or (min(e, f), max(e, f)) in co: continue
                if not final and e in loose and f in loose: open_ = True
                anti += 1
        if open_: tally['open'] += 1; continue
        commute = anti % 2 == 0
        fails_settled += not commute
        if rnd[u] == 0 or rnd[v] == 0: tally['a start knot (not covered)'] += 1; continue
        a, b = (u, v) if rnd[u] <= rnd[v] else (v, u)
        gap = rnd[b] - rnd[a]; pu, pv = len(F[a]), len(F[b])
        if gap == 0:
            kind = 'one round'; pred = (pu * pv) % 2 == (len(parents[a] & parents[b]) + len(children[a] & children[b])) % 2
        elif gap == 1 and a in parents[b]:
            kind = 'parent and child'; pred = not (pu % 2 == 0 and pv % 2 == 0)
        elif gap == 2:
            mids = len({w for w in children[a] if b in children[w]})
            kind = 'two rounds apart'; pred = (pu * pv) % 2 == mids % 2
        elif gap >= 3:
            kind = 'three or more apart'; pred = not (pu % 2 == 1 and pv % 2 == 1)
        else:
            # not in the advisor's table: no knot can hold a place of each (every parent of a birth is a newest knot),
            # so every place pair fails to commute, as for pairs three or more rounds apart
            kind = 'one round apart, not parent and child'; pred = not (pu % 2 == 1 and pv % 2 == 1)
        tally[(kind, 'pairs')] += 1
        if pred is not None: tally[(kind, 'formula right')] += pred == commute
    return {'end': end, 'rounds': last, 'knots': n, 'settled failing pairs': fails_settled,
            **{(' / '.join(k) if isinstance(k, tuple) else k): v for k, v in tally.items()}}


if __name__ == '__main__':
    count, rounds, cap = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    S = forbid.census(); picks = sorted(random.Random(20261128).sample(range(len(S)), count))
    for i in picks:
        print(json.dumps({'start': i, **check(*grow(forbid.supports_of(S[i]), rounds, cap))}), flush=True)
