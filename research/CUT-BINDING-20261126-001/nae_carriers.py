"""nae_carriers.py OUT.jsonl: not-all-equal carriers tested with a solver.  CUT-BINDING-20261126-001; README.md.

Under not-all-equal the allowed states are not a linear space, and the record found one class wherever it read
(TWO-CLASS-SIGN-20261126-001, nae_classes.py), so no fact is kept by small changes there.  This reads the nearest
question a solver can answer: on the layers referee's witnesses built from rings of four knots (two, three and four
rings), grown 0 to 2 rounds by ordinary growth under not-all-equal, the carriers are the rings' parities of their own
shared distinctions (each unchanged by flipping every value, since a ring of four has four), and for every tuple of
carrier values a SAT call (every knot not all equal, each carrier's parity fixed) says whether some allowed state has
it.  A binding would be a set of three or more carriers whose values miss some tuple while every proper sub-family takes
every tuple (K1 to K3 on the carriers' values, checked by the knot checker)."""
import sys, os, json, itertools, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research' / 'BINDING-20261126-001'))
import binding as BD
forbid = BD.forbid
from pysat.solvers import Minisat22


def ring_parities(source):
    """the shared distinctions of each four-knot ring among the start's knots (cycles of four knots in the meeting graph)"""
    holders = {}
    for k, r in enumerate(source):
        for x in r: holders.setdefault(x, []).append(k)
    edge = {}
    for x, h in holders.items():
        if len(h) == 2: edge.setdefault(tuple(sorted(h)), []).append(x)
    nb = {}
    for (a, b) in edge: nb.setdefault(a, set()).add(b); nb.setdefault(b, set()).add(a)
    rings = set()
    for a in nb:
        for b, c in itertools.combinations(sorted(nb[a]), 2):
            for d in nb.get(b, ()) & nb.get(c, ()):
                if d != a and d not in nb[a] and b not in nb.get(c, ()):
                    cyc = frozenset([a, b, d, c])
                    rings.add(cyc)
    out = []
    for cyc in sorted(rings, key=sorted):
        ks = sorted(cyc); xs = []
        for p, q in itertools.combinations(ks, 2):
            xs += edge.get((p, q), []) if (p, q) in edge and len(set(nb[p]) & cyc) >= 1 else []
        # keep the four cycle distinctions only: edges between consecutive members
        out.append(sorted(set(xs)))
    out = [r for r in out if len(r) == 4]
    keep = []                                        # pairwise disjoint supports: each carried on its own
    for r in out:
        if all(not (set(r) & set(q)) for q in keep): keep.append(r)
    return keep


def sat_tuple(supports, carriers, values):
    names = sorted({x for r in supports for x in r}); idx = {x: i + 1 for i, x in enumerate(names)}
    top = [len(names)]
    def new():
        top[0] += 1; return top[0]
    s = Minisat22()
    for r in supports:
        v = [idx[x] for x in r]; s.add_clause(v); s.add_clause([-u for u in v])
    for car, val in zip(carriers, values):
        acc = idx[car[0]]
        for x in car[1:]:
            y = idx[x]; z = new()                          # z = acc xor y
            s.add_clause([-z, acc, y]); s.add_clause([-z, -acc, -y]); s.add_clause([z, -acc, y]); s.add_clause([z, acc, -y])
            acc = z
        s.add_clause([acc] if val else [-acc])
    ok = s.solve(); s.delete(); return ok


if __name__ == '__main__':
    out = sys.argv[1]
    b = json.load(open(ROOT / 'research/LAYERS-20261126-001/referee-R1/built_search.json'))
    with open(out, 'w') as f:
        for i in (0, 17, 20):
            source = tuple(tuple(k) for k in b[i]['source']); cars = ring_parities(source)
            rec = {'start': 'referee built %d' % i, 'carriers': cars, 'rounds': []}
            st = source
            for t in range(0, 3):
                if t:
                    st, status, births = forbid.grown(st, 'nae', 'ordinary')
                    if status != 'funded': rec['rounds'].append({'round': t, 'end': status}); break
                k = len(cars); occ = [v for v in itertools.product((0, 1), repeat=k) if sat_tuple(st, cars, v)]
                missing = [list(v) for v in itertools.product((0, 1), repeat=k) if tuple(v) not in set(occ)]
                pairs_free = all(len({(v[a], v[c]) for v in occ}) == 4 for a, c in itertools.combinations(range(k), 2))
                rec['rounds'].append({'round': t, 'tuples occurring': len(occ), 'of': 2 ** k, 'missing': missing[:8],
                                      'every pair free': pairs_free})
            f.write(json.dumps(rec) + '\n'); f.flush(); print(json.dumps(rec)[:500], flush=True)
