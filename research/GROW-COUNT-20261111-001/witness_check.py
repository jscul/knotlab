"""Independent checks for GROW-COUNT-20261111-001, written apart from the frozen library:
(1) the tetrahedron lemma: adding any knot to the tetrahedron {0,1,2,3} under NAE makes a non-knot triple constrained (brute force);
(2) three grown worlds re-read by a separate SAT encoding: a free NAE world with a pair in three knots, an open NAE world with a
    pinched link, and a disc NAE world with a closed distinction of degree 3: every pair free, every knot a bond, every other triple free.
Writes witness_check.json beside this file."""
import itertools, json, os, sys
from collections import Counter, defaultdict
from pysat.solvers import Minisat22
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

def nae_states(V, T):
    out = []
    for x in range(1 << V):
        if all(0 < ((x >> a) & 1) + ((x >> b) & 1) + ((x >> c) & 1) < 3 for a, b, c in T):
            out.append(x)
    return out

def faithful_brute(V, T):
    st = nae_states(V, T)
    knots = {tuple(sorted(t)) for t in T}
    def pats(S): return {tuple((x >> v) & 1 for v in S) for x in st}
    if not st: return False
    if any(len(pats(p)) < 4 for p in itertools.combinations(range(V), 2)): return False
    return all((len(pats(t)) < 8) == (t in knots) for t in itertools.combinations(range(V), 3))

def faithful_sat(V, T):
    cl = [c for a, b, d in T for c in ([a + 1, b + 1, d + 1], [-(a + 1), -(b + 1), -(d + 1)])]
    knots = {tuple(sorted(t)) for t in T}
    with Minisat22(bootstrap_with=cl) as s:
        if not s.solve(): return False
        def ok(S, p): return s.solve(assumptions=[(v + 1) if b else -(v + 1) for v, b in zip(S, p)])
        for S in itertools.combinations(range(V), 2):
            if not all(ok(S, p) for p in itertools.product((0, 1), repeat=2)): return False
        for S in itertools.combinations(range(V), 3):
            free = all(ok(S, p) for p in itertools.product((0, 1), repeat=3))
            if free == (S in knots): return False
    return True

out = {}
tet = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
out["tetrahedron faithful"] = faithful_brute(4, tet)
out["tetrahedron plus any knot on a pair, third distinction new: faithful"] = [faithful_brute(5, tet + [tuple(sorted(e + (4,)))]) for e in itertools.combinations(range(4), 2)]
census = json.load(open(os.path.join(ROOT, "artifacts", "GROW-COUNT-20261111-001A", "GROW-COUNT-20261111-001A-E001_count_from_growth", "census.json")))
def compact(r):
    T = [tuple(t) for t in r["T"]]
    used = sorted({v for t in T for v in t}); idx = {v: i for i, v in enumerate(used)}
    return len(used), [tuple(sorted(idx[v] for v in t)) for t in T]
picks = {}
for r in census["runs"]:
    if r["law"] != "NAE": continue
    V, T = compact(r)
    m = Counter(e for t in T for e in itertools.combinations(t, 2))
    if r["rule"] == "free" and "fin" not in picks and any(c >= 3 for c in m.values()) and V <= 40: picks["fin"] = (r, V, T)
    if r["rule"] == "open" and "pinch" not in picks and r["pinched links"] and V <= 40: picks["pinch"] = (r, V, T)
    if r["rule"] == "disc" and "degree 3" not in picks and r["closed degrees"].get("3") and V <= 60 and len(T) > 4: picks["degree 3"] = (r, V, T)
for k, (r, V, T) in picks.items():
    out[k] = {"run": [r["rule"], r["bias"], r["seed"]], "distinctions": V, "knots": len(T), "faithful by separate SAT": faithful_sat(V, T)}
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(HERE, "witness_check.json"), "w"), indent=1)
