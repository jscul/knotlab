"""After the run, not registered (PERIODIC-READ-20261111-001, ticket B): G1 failed on 7 of the 98 global bases. Are the global added
sets that are not removed source knots derived from them: once the removed knots are put back as knots, does a proper ball of knots
around each such set force it? Writes derived_global.json beside this file."""
import json, os, sys, tempfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "OVERLAP-READ-20261111-001A", "OVERLAP-READ-20261111-001A-E001_emergence_census"))
import census as c  # noqa: E402
c.OUT = tempfile.mkdtemp()
tori = c.ns_faithful_tori(c.NS_V)
index = {(t["V"], tuple(t["lattice"])): i for i, t in enumerate(tori)}
res = json.load(open(os.path.join(ROOT, "proofs", "PERIODIC-READ-20261111-001B", "PERIODIC-READ-20261111-001B-P001_two_classes", "result.json")))
out = []
for x in [x for x in res["rows"] if not x["G1"]]:
    n = index[(x["V"], tuple(x["torus"]))]
    tor = tori[n]
    src = {tuple(sorted(t)) for t in tor["T"]}
    W = c.ns_swap_worlds(tor["V"], [tuple(t) for t in tor["T"]], x["swaps"], seed=c.NS_SEED + 1000 * n + 10 * x["swaps"] + x["rep"])
    removed = sorted(src - {tuple(sorted(t)) for t in W})
    V = tor["V"]
    b = c.SatBase(V, W)
    fr, ti, ex, na = b.emergent()
    b.close()
    glob = [tuple(S) for S in fr + ti + ex
            if not any(c.forced(V, c.ball_knots(W, S, r), S) and len(c.ball_knots(W, S, r)) < len(W) for r in range(1, 10))]
    others = [S for S in glob if S not in removed]
    W2 = list(W) + removed
    rows = []
    for S in others:
        r_found = None
        for r in range(1, 10):
            ball = c.ball_knots(W2, S, r)
            if len(ball) == len(W2):
                break
            if c.forced(V, ball, S):
                r_found = r
                break
        rows.append({"S": list(S), "radius with the removed knots back": r_found})
    rec = {"V": V, "torus": tor["lattice"], "swaps": x["swaps"], "rep": x["rep"], "other global sets": rows,
           "all derived": all(r["radius with the removed knots back"] is not None for r in rows)}
    out.append(rec)
    print(rec, flush=True)
json.dump(out, open(os.path.join(ROOT, "research", "PERIODIC-READ-20261111-001", "derived_global.json"), "w"), indent=1)
print("all derived in", sum(r["all derived"] for r in out), "of", len(out))
