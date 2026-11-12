"""After the run, not registered (BOND-BALLS-20261111-001): the referee's travelling triple on base 16, reproduced with the census's
own bounds. For k = 3 .. 12, is S_k = {(-k, k-2), (-k, k-1), (-k, k), origin} a bond of four: some value pattern refuted in a window
around it, and every three-element part free (finite repeats or one-shift repeats realize all eight patterns)? Writes
travelling_triple.json."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "BOND-BALLS-20261111-001A", "BOND-BALLS-20261111-001A-E001_bond_balls"))
import census as bb  # noqa: E402
pr = bb.pr
src = json.load(open(bb.PR_OUT))
bases = [r for r in src["F2"] if r.get("faithful")]
knots = bases[16]["knots"]
P = pr.Pattern(2, 1, [tuple((v, tuple(s)) for v, s in kn) for kn in knots])
rows = []
for k in range(3, 13):
    rd = pr.Reader(P, k + 4, pr.F2_LATTICES, window_exact=False, strips=pr.F2_STRIPS)
    adj, _ = pr.adjacency(P, k + 4)
    o = (0, (0, 0))
    steps = pr.ball(adj, [o], k + 1)
    S = [(0, (-k, k - 2)), (0, (-k, k - 1)), (0, (-k, k)), o]
    import itertools
    refuted = ["".join(map(str, p)) for p in itertools.product((0, 1), repeat=4) if rd.extends(S, p) is False]
    parts = [rd.status(tuple(sorted(set(S) - {u}))) for u in S]
    rows.append({"k": k, "steps from the origin": [steps.get(x) for x in S[:3]], "refuted patterns (far triple, origin)": refuted,
                 "parts": parts, "bond of four": bool(refuted) and all(p == "free" for p in parts)})
    print(rows[-1], flush=True)
    rd.close()
json.dump({"base": 16, "knots": knots, "rows": rows}, open(os.path.join(os.path.dirname(__file__), "travelling_triple.json"), "w"), indent=1)
