"""Independent check of the smallest faithful non-surface world of NAE-SURFACE-20261111-001A-E001, written apart from the frozen
library: brute force over all 2^V states, then every pair, every triple and the knots through knotlab's canonical checker.
Usage: witness_check.py <witness.json>; writes witness_check.json beside this file."""
import itertools, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from knotlab.relations import Relation
from knotlab.patterns import hides_from_parts
w = json.load(open(sys.argv[1])); V, T = w["V"], [tuple(t) for t in w["T"]]
states = []
for start in range(0, 1 << V, 1 << 21):
    x = np.arange(start, min(start + (1 << 21), 1 << V), dtype=np.int64)
    ok = np.ones(len(x), dtype=bool)
    for a, b, c in T:
        s = ((x >> a) & 1) + ((x >> b) & 1) + ((x >> c) & 1)
        ok &= (s == 1) | (s == 2)
    states.append(x[ok])
st = np.concatenate(states)
names = tuple(f"v{i}" for i in range(V))
rel = Relation(names, frozenset(tuple(bool((int(s) >> i) & 1) for i in range(V)) for s in st))
deg = [sum(v in t for t in T) for v in range(V)]
mult = {}
for t in T:
    for e in itertools.combinations(sorted(t), 2):
        mult[e] = mult.get(e, 0) + 1
knots = {tuple(sorted(t)) for t in T}
pairs_full = all(rel.project([f"v{a}", f"v{b}"]).is_full() for a, b in itertools.combinations(range(V), 2))
knots_bonds = all(hides_from_parts(rel.project([f"v{x}" for x in t])) for t in knots)
others_free = all(rel.project([f"v{x}" for x in t]).is_full() for t in itertools.combinations(range(V), 3) if t not in knots)
out = {"V": V, "knots": len(T), "regular": sorted(set(deg)), "states": int(len(st)),
       "pairs in one knot": sum(1 for c in mult.values() if c == 1), "pairs in three or more": sum(1 for c in mult.values() if c >= 3),
       "every pair free (no frozen, no tie)": pairs_full, "every knot a bond (knotlab)": knots_bonds,
       "every other triple free": others_free, "faithful": pairs_full and knots_bonds and others_free}
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(HERE, "witness_check.json"), "w"), indent=1)
