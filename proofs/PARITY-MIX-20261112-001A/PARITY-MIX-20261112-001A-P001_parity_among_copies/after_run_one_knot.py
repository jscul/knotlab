#!/usr/bin/env python3
"""After the run (descriptive; not frozen): why one parity knot among not-all-equal stitches on 3 x 3 leaves no state, and which
placements on 3 x 3 keep a state.

    .venv/bin/python3 -B after_run_one_knot.py [--write]
For each harmony with a flip-blind triple: (a) the flip-blind triples that the not-all-equal stitch also allows; (b) whether, on 3 x 3,
the eight not-all-equal knots left when one cell is removed already force the ninth cell's triple into the stitch (every state of the
eight-knot arrangement satisfies the ninth knot); (c) the 3 x 3 placements (as cell sets) that keep a state, by k."""
import json
import sys
from pathlib import Path

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def main():
    import parity_lib as L
    census = json.loads((HERE / "result_census.json").read_text())["checks"]["result"]["rows"]
    p3 = {r["harmony"]: r for r in json.loads((HERE / "result_p3.json").read_text())["checks"]["result"]["rows"]}
    hs = L.harmonies()
    out = []
    for c in census:
        if not c["flip-blind triples"]:
            continue
        h = hs[c["i"]]
        st = L.setup(h)
        W, P = st["W"], st["P"]
        mask = (1 << P) - 1
        fb_in_R = sum(1 for (u, v, w) in st["R"] if (W[u] ^ W[v] ^ W[w]) in (0, mask))
        # (b): eight NAE knots (cell 0 removed), is the ninth knot (at cell 0, NAE) implied?
        n = m = 3
        ks = L.knots(n, m)
        eight = [k for j, k in enumerate(ks) if j != 0]
        cl, nv, var = L.E.build((9, eight), h, "one order")
        # the ninth knot violated at some kind and place: a fresh selector per (kind, place) clause pair
        x, y, z = ks[0]
        viol, nxt = [], nv + 1
        extra = []
        for (_, a, b) in h["kinds"]:
            for i in range(P):
                for val in (1, -1):  # all three equal to 1, or all three equal to 0
                    s = nxt
                    nxt += 1
                    viol.append(s)
                    for lit in (var(x, i), var(y, i + a), var(z, i + b)):
                        extra.append([-s, val * lit])
        extra.append(viol)
        with Solver(name="cadical153", bootstrap_with=cl + extra) as sv:
            implied = not sv.solve()
        surviving = {}
        for row in p3[c["harmony"]]["rows"]:
            pass
        out.append({"harmony": c["harmony"], "flip-blind triples": c["flip-blind triples"], "of them allowed by the stitch": fb_in_R,
                    "on 3 x 3, eight stitches force the ninth": implied})
    # (c) the surviving placements on 3 x 3, as cell sets (recomputed for the first harmony with a flip-blind triple)
    c0 = [c for c in census if c["flip-blind triples"]][0]
    st = L.setup(hs[c0["i"]])
    func = L.functional_slots(st)
    surv = {}
    for K in L.placements_all(3, 3):
        r = L.reach(st, 3, 3, K)
        if r["state"]:
            surv.setdefault(len(K), []).append(sorted(K))
    res = {"rows": out, "surviving placements on 3 x 3 for %s (cells numbered r * 3 + c)" % c0["harmony"]: surv}
    print(json.dumps(res, indent=1)[:3000])
    if "--write" in sys.argv:
        (HERE / "result_after_run_one_knot.json").write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    main()
