#!/usr/bin/env python3
"""DISTANCE-20261108-001 stress test: each computed claim of ticket B one size past where its check stopped, and the frozen test of A40
one length and one spacing past its roster.

    .venv/bin/python3 -B research/DISTANCE-20261108-001/stress_test.py   writes stress_test.json beside this file
- check 9: D = ceil(delta / 3) on triangular tori of side 11 and 12 (checked to 10); the honeycomb band on sides 10 and 11 (to 9);
- check 10: full reach on honeycomb tori, ring to ring, on sides 6, 8, 10, 11, 12 and 13 (checked on 3, 4, 5, 7, 9);
- check 8: translates on square tori of side 11 and 12, triangular 10 and 11, honeycomb 9 and 10 (checked to 10, 9 and 8);
- check 6: closed forms and D = ceil(delta / 2) on square tori of side 14 and 15 (checked to 13);
- A40's frozen test: routes of 11 and 12 contacts at spacing 5 on the square torus of side 8 and the Klein quartic network."""
import json
import random
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
B = ROOT / "proofs/DISTANCE-20261108-001B/DISTANCE-20261108-001B-P001_distance_across_time_is_native_as_a_cone"
sys.path.insert(0, str(B))
import check as C  # noqa: E402

D, LN, T = C.D, C.LN, C.T


def never_rings(n):
    W = C.Net("honeycomb torus %d" % n, 2)
    ins = T.in_sets(W.sizes, W.contacts)
    reach = [T.reach(ins, c)[0] for c in range(W.n)]
    masks = {X: sum(1 << e for e in cs) for X, cs in W.rc.items()}
    per = Counter()
    for X in W.rc:
        for Y in W.rc:
            if not any(reach[c] & masks[X] for c in W.rc[Y]):
                per[Y] += 1
    return n, len(W.rc), sum(per.values()), sorted(Counter(per.values()).items())


def frozen_past(args):
    name, g = args
    W = C.Net(name, g)
    rng = random.Random("%d/stress/%s/%d" % (C.SEED, name, g))
    rings = sorted(W.rc)
    tested = ok = 0
    for L in (11, 12):
        for kind in ("shortest", "chordless"):
            got = 0
            for _ in range(200):
                if got == 3:
                    break
                X = rng.choice(rings)
                r = (D.shortest_route(rng, W.out, W.inn, W.rc, W.n, X, L) if kind == "shortest"
                     else D.random_route(rng, W.out, W.rc, W.n, X, L))
                if r is None or not D.valid_route(W.out, W.rc, W.contacts, r, X):
                    continue
                got += 1
                tested += 1
                ok += D.isolated_first_need(W.sizes, W.contacts, r, X, 2 * (g * L + 1)) == g * L + 1
    return name, g, tested, ok


def main():
    out = {}
    with Pool(16) as pool:
        bands = dict(pool.map(C.task_band, ["triangular torus 11", "triangular torus 12", "honeycomb torus 10", "honeycomb torus 11"]))
        tri = all(D_ == (d + 2) // 3 for nm, tab in bands.items() if nm.startswith("triangular") for (D_, d), k in tab)
        hc = all(-(-3 * D_ // 2) - 1 <= d <= -(-3 * D_ // 2) for nm, tab in bands.items() if nm.startswith("honeycomb") for (D_, d), k in tab)
        out["check 9 one size past"] = {"pass": tri and hc, "triangular D = ceil(delta/3), sides 11 and 12": tri,
                                        "honeycomb band, sides 10 and 11": hc}
        nv = pool.map(never_rings, [6, 8, 10, 11, 12, 13])
        out["check 10 one size past: rings each ring never needs, honeycomb tori"] = [
            {"side": n, "rings": r, "pairs never": t, "rings by how many rings they never need": h} for n, r, t, h in nv]
        tr = pool.map(C.task_translates, [("square", 11), ("square", 12), ("triangular", 10), ("triangular", 11), ("honeycomb", 9),
                                          ("honeycomb", 10)])
        out["check 8 one size past"] = {"pass": all(x[3] == 0 for x in tr), "pairs": sum(x[2] for x in tr), "failures": sum(x[3] for x in tr)}
        sq = pool.map(C.task_square, [14, 15])
        out["check 6 one size past"] = {"pass": all(x[1] == 0 and x[2] == 0 and x[4] == 0 for x in sq),
                                        "sides": [x[0] for x in sq], "same-kind pairs": sum(x[3] for x in sq)}
        fp = pool.map(frozen_past, [("square torus 8", 5), (C.G3, 5)])
        out["A40 frozen test one length and one spacing past"] = {"pass": all(x[2] == x[3] for x in fp),
                                                                   "runs": [{"network": x[0], "g": x[1], "routes": x[2], "affine": x[3]} for x in fp]}
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
