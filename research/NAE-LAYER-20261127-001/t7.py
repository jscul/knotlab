"""t7.py OUT.json: the advisor's smallest concrete case under not-all-equal (README.md, "Frozen").  NAE-LAYER-20261127-001.

T7: knots (0,1,2), (0,3,6), (1,4,7), (2,5,8), (3,9,10), (4,11,12), (5,13,14).  Its allowed states under not-all-equal
are enumerated exactly.  Read: the number of states (N1); the joint patterns of the loose distinctions (N2); the three
facts g_i on (6+i, 9+2i, 10+2i), + at (1,0,0), - at (0,1,1), 0 otherwise, their triples and pairs (N3); the ring
control, 11 renamed 9 (N4); growth: T7's first round, and T7 with 15, 16, 17 added to its three middle knots, its states,
loose patterns, and the loose patterns of its stage after one round (N5)."""
import sys, json, itertools
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
for d in ('BUILT-BINDING-20261126-001',): sys.path.insert(0, str(ROOT / 'research' / d))
import repro as RP
from pysat.solvers import Minisat22
forbid = RP.forbid


def states(sup):
    names = sorted({x for r in sup for x in r}); idx = {x: i for i, x in enumerate(names)}
    masks = [sum(1 << idx[x] for x in r) for r in sup]; out = []
    for s in range(1 << len(names)):
        if all(0 < bin(s & m).count('1') < bin(m).count('1') for m in masks): out.append(s)
    return names, idx, out


def loose_of(sup):
    h = forbid.holders(sup); return sorted(x for x, v in h.items() if len(v) == 1)


def patterns_enum(sup):
    names, idx, sol = states(sup); lo = loose_of(sup)
    return len({tuple((s >> idx[x]) & 1 for x in lo) for s in sol}), 2 ** len(lo), len(sol)


def patterns_sat(sup):
    """the loose patterns that occur, by a solver call per pattern (for stages too large to enumerate)"""
    names = sorted({x for r in sup for x in r}); idx = {x: i + 1 for i, x in enumerate(names)}; lo = loose_of(sup)
    base = []
    for r in sup:
        v = [idx[x] for x in r]; base.append(v); base.append([-u for u in v])
    n = 0
    for vals in itertools.product((0, 1), repeat=len(lo)):
        s = Minisat22(bootstrap_with=base)
        ok = s.solve(assumptions=[idx[x] if b else -idx[x] for x, b in zip(lo, vals)]); s.delete(); n += ok
    return n, 2 ** len(lo)


if __name__ == '__main__':
    T7 = ((0, 1, 2), (0, 3, 6), (1, 4, 7), (2, 5, 8), (3, 9, 10), (4, 11, 12), (5, 13, 14))
    out = {}
    names, idx, sol = states(T7)
    out['N1 states'] = len(sol)
    p, of, _ = patterns_enum(T7); out['N2 loose patterns'] = [p, of]
    def g(s, i):
        a, b, c = ((s >> idx[6 + i]) & 1, (s >> idx[9 + 2 * i]) & 1, (s >> idx[10 + 2 * i]) & 1)
        return '+' if (a, b, c) == (1, 0, 0) else '-' if (a, b, c) == (0, 1, 1) else '0'
    trip = {(g(s, 0), g(s, 1), g(s, 2)) for s in sol}
    out['N3 triples of (g0, g1, g2)'] = len(trip); out['N3 missing triples'] = sorted(set(itertools.product('+-0', repeat=3)) - trip)
    out['N3 pairs'] = [len({(t[a], t[b]) for t in trip}) for a, b in ((0, 1), (0, 2), (1, 2))]
    ring = tuple(tuple(9 if x == 11 else x for x in r) for r in T7)
    p, of, n = patterns_enum(ring); out['N4 ring control: loose patterns'] = [p, of]; out['N4 ring control: states'] = n
    st, status, births = forbid.grown(T7, 'nae', 'ordinary'); out['N5 T7 round 1'] = status
    T7b = ((0, 1, 2), (0, 3, 6, 15), (1, 4, 7, 16), (2, 5, 8, 17), (3, 9, 10), (4, 11, 12), (5, 13, 14))
    p, of, n = patterns_enum(T7b); out['N5 T7 with 15, 16, 17: states'] = n; out['N5 T7 with 15, 16, 17: loose patterns'] = [p, of]
    st, status, births = forbid.grown(T7b, 'nae', 'ordinary'); out['N5 its round 1'] = status
    if status == 'funded':
        out['N5 loose patterns after one round'] = list(patterns_sat(st)); out['N5 stage after one round: knots'] = len(st)
    json.dump(out, open(sys.argv[1], 'w'), indent=1, default=list); print(json.dumps(out, indent=1, default=list))
