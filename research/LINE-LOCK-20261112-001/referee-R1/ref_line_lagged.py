#!/usr/bin/env python3
"""Referee LINE-LOCK-R1, lagged stitches on one set of states: the lagged stitch R_l(x, y, z) = R(x, s^l1 y, s^l2 z) (s the harmony's
shift, lags l = (l1, l2) in Z_P^2; a lag translates the stitch pairs by shifts, as in the census). For every harmony of the census
(presentation as rebuilt by ref_line.py) with at most 128 states, every set S of 2 states, every lag: does R_l hold a permutive
sub-stitch on S (a Latin square of order 2 inside R_l on S^3), and how many of the 8 triples of S^3 does R_l hold: 4 means R_l on S is
exactly the additive law z = x + y (+ e) over F_2, Ledrappier's; 8 means S is free under R_l (copies choose either state freely).
The same at order 3 (12 Latin squares, 27 triples; 9 means exactly a Latin square) where C(n, 3) P^2 <= 6e7.
The census's lagged search covers cosets of cyclic subgroups at odd primes; a set S = {u, h u} with h of order more than 2, or a
3-set that is not a coset of an order-3 subgroup, is outside it.

    python3 -B ref_line_lagged.py      (writes result_lagged.json)"""
import itertools
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ref_line as L  # noqa: E402
import ref_line_ranges as G  # noqa: E402

LAT3 = [s for s in (list(map(list, p)) for p in itertools.product(itertools.permutations(range(3)), repeat=3))
        if all(len({s[i][j] for i in range(3)}) == 3 for j in range(3))]


def main():
    t0 = time.time()
    hs = L.span8_harmonies() + [L.odd_harmony(n, S) for n, S in L.ODD_SETS]
    rows = []
    for h in hs:
        W, P = h["W"], h["P"]
        n = len(W)
        if n > 128:
            rows.append({"harmony": h["name"], "states": n, "skipped": True})
            continue
        ok = G.relation(h)
        idx = {w: i for i, w in enumerate(W)}
        pm = np.array([[idx[L.rot(w, l, P)] for w in W] for l in range(P)])   # pm[l, x] = index of s^l x
        row = {"harmony": h["name"], "P": P, "states": n, "kinds": [list(k) for k in h["kinds"]]}
        hist2, ex2 = Counter(), []
        for a in itertools.combinations(range(n), 2):
            M = {(j, k, m): ok[a[j]][np.ix_(pm[:, a[k]], pm[:, a[m]])] for j in range(2) for k in range(2) for m in range(2)}
            cnt = sum(M.values()).astype(int)
            lat = np.zeros((P, P), dtype=bool)
            for e in (0, 1):
                lat |= M[0, 0, e] & M[0, 1, 1 ^ e] & M[1, 0, 1 ^ e] & M[1, 1, e]
            for l1, l2 in zip(*np.nonzero(lat)):
                c = int(cnt[l1, l2])
                hist2[c] += 1
                if c < 8 and len(ex2) < 5:
                    ex2.append({"states": [format(W[i], f"0{P}b")[::-1] for i in a], "lag": [int(l1), int(l2)], "triples held": c})
        row["order 2: permutive (S, lag) by triples held"] = dict(sorted(hist2.items()))
        row["order 2: examples not free"] = ex2
        if len(list(itertools.combinations(range(n), 3))) * P * P <= 6e7:
            hist3, ex3 = Counter(), []
            for a in itertools.combinations(range(n), 3):
                M = {(j, k, m): ok[a[j]][np.ix_(pm[:, a[k]], pm[:, a[m]])] for j in range(3) for k in range(3) for m in range(3)}
                lat = np.zeros((P, P), dtype=bool)
                for s in LAT3:
                    t = np.ones((P, P), dtype=bool)
                    for j in range(3):
                        for k in range(3):
                            t &= M[j, k, s[j][k]]
                    lat |= t
                if lat.any():
                    cnt = sum(M.values()).astype(int)
                    for l1, l2 in zip(*np.nonzero(lat)):
                        hist3[int(cnt[l1, l2])] += 1
                        if len(ex3) < 5:
                            ex3.append({"states": [format(W[i], f"0{P}b")[::-1] for i in a], "lag": [int(l1), int(l2)],
                                        "triples held": int(cnt[l1, l2])})
            row["order 3: permutive (S, lag) by triples held"] = dict(sorted(hist3.items()))
            row["order 3: examples"] = ex3
        else:
            row["order 3"] = "not searched (size)"
        rows.append(row)
        print(h["name"][:50], n, P, row["order 2: permutive (S, lag) by triples held"], row.get("order 3: permutive (S, lag) by triples held", "-"),
              round(time.time() - t0), "s", flush=True)
    srch = [r for r in rows if not r.get("skipped")]
    summ = {"harmonies searched at order 2": len(srch), "skipped": [r["harmony"] for r in rows if r.get("skipped")],
            "harmonies with a lagged permutive pair": sum(1 for r in srch if r["order 2: permutive (S, lag) by triples held"]),
            "of them exactly additive somewhere (4 triples)": sum(1 for r in srch if r["order 2: permutive (S, lag) by triples held"].get(4)),
            "of them with a pair neither additive nor free (5 to 7)": sum(1 for r in srch if any(r["order 2: permutive (S, lag) by triples held"].get(c) for c in (5, 6, 7))),
            "harmonies searched at order 3": sum(1 for r in srch if "order 3: permutive (S, lag) by triples held" in r),
            "harmonies with a lagged permutive 3-set": sum(1 for r in srch if r.get("order 3: permutive (S, lag) by triples held")),
            "of them exactly a Latin square somewhere (9 triples)": sum(1 for r in srch if (r.get("order 3: permutive (S, lag) by triples held") or {}).get(9))}
    (HERE / "result_lagged.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1) + "\n")
    print(json.dumps(summ, indent=1))
    print("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
