#!/usr/bin/env python3
"""Referee LINE-LOCK-R1, three ranges: the theorem needs the three entries of a permutive sub-stitch to range over one set S. Lagged
stitches and stitches across orbits give three ranges S1, S2, S3 instead. This searches every harmony of the census with at most 128
states (census presentation as rebuilt by ref_line.py) for permutive sub-stitches of order 2 with three arbitrary ranges:
a0 != a1, b0 != b1, c0 != c1 with R(a_j, b_k, c_(j xor k)) for all j, k (both Latin squares of order 2, up to naming the c's).
This covers order 2 at every lag and across orbits: the case F_2, Ledrappier's own field.

    python3 -B ref_line_ranges.py      (writes result_ranges.json)"""
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ref_line as L  # noqa: E402


def relation(h):
    W, P, kinds = h["W"], h["P"], h["kinds"]
    n = len(W)
    full = (1 << P) - 1
    ok = np.ones((n, n, n), dtype=bool)
    Wa = np.array([[(w >> i) & 1 for i in range(P)] for w in W], dtype=np.int8)
    for a, b in kinds:
        U = Wa[:, None, None, :]
        V = np.roll(Wa, -a, axis=1)[None, :, None, :]
        Z = np.roll(Wa, -b, axis=1)[None, None, :, :]
        s = U + V + Z
        ok &= ((s != 0) & (s != 3)).all(axis=3)
    return ok


def order2(ok):
    n = ok.shape[0]
    found = []
    for a0 in range(n):
        for a1 in range(a0 + 1, n):
            M0, M1 = ok[a0], ok[a1]
            V0 = M0[:, None, :] & M1[None, :, :]        # [b0, b1, c]: R(a0, b0, c) and R(a1, b1, c)
            V1 = V0.transpose(1, 0, 2)                   # [b0, b1, c]: R(a0, b1, c) and R(a1, b0, c)
            n0, n1 = V0.sum(2), V1.sum(2)
            good = (n0 >= 1) & (n1 >= 1)
            np.fill_diagonal(good, False)
            same = (n0 == 1) & (n1 == 1) & (V0.argmax(2) == V1.argmax(2))
            good &= ~same
            for b0, b1 in zip(*np.nonzero(good)):
                found.append((a0, a1, int(b0), int(b1)))
                if len(found) >= 50:
                    return found
    return found


def main():
    t0 = time.time()
    hs = L.span8_harmonies() + [L.odd_harmony(n, S) for n, S in L.ODD_SETS]
    rows = []
    for h in hs:
        if len(h["W"]) > 128:
            rows.append({"harmony": h["name"], "states": len(h["W"]), "skipped": True})
            continue
        ok = relation(h)
        # the referee's bitmask stitch and this array agree on a sample
        assert all(ok[x, y, z] == L.stitch(h["W"][x], h["W"][y], h["W"][z], h["kinds"], h["P"])
                   for x in range(0, len(h["W"]), 3) for y in range(0, len(h["W"]), 5) for z in range(0, len(h["W"]), 7))
        f = order2(ok)
        rows.append({"harmony": h["name"], "P": h["P"], "states": len(h["W"]), "order-2 three-range sub-stitches (first 50)": len(f),
                     "examples": [[format(h["W"][i], f"0{h['P']}b")[::-1] for i in e] for e in f[:3]]})
        print(h["name"][:50], len(h["W"]), len(f), round(time.time() - t0), "s", flush=True)
    summ = {"harmonies searched": sum(1 for r in rows if not r.get("skipped")), "skipped (more than 128 states)": [r["harmony"] for r in rows if r.get("skipped")],
            "harmonies with an order-2 three-range sub-stitch": sum(1 for r in rows if r.get("order-2 three-range sub-stitches (first 50)"))}
    (HERE / "result_ranges.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1) + "\n")
    print(json.dumps(summ, indent=1))
    print("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
