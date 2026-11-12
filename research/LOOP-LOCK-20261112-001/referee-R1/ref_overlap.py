#!/usr/bin/env python3
"""Referee LOOP-LOCK-R1: collective locks, with the referee's own code (ref_endless.py's clause builder and SAT, the referee's).

    python3 -B ref_overlap.py      (writes result_overlap.json)

For the 7 harmonies whose step relation has a girth g above 2: the crossed pair (loop 1: x -> y in 1 knot, back in 3; loop 2: x -> y
in 3 knots, back in 1), and circulants of n copies stepped by +1 and by +2 (n = 3 to 2g + 1, as far as size allows), each knot with
its own hanging copy. Measured by SAT: whether every shared copy equals copy 0 in every state. Beside it, the shortest coherently
oriented closed walk of the pattern's steps (a loop that locks alone when shorter than g): for the crossed pair 2 (x -> y -> x
through the two one-knot halves), for the circulant ceil(n/2)."""
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "ENDLESS-BLOCK-20261112-001" / "referee-R1"))
import ref_endless as E  # noqa: E402
import ref_lib as R  # noqa: E402
from pysat.solvers import Glucose4  # noqa: E402


def locked_all(h, Ppat, shared):
    cl, nv, var = E.clauses_one_order(h, Ppat)
    P = h["P"]
    with Glucose4(bootstrap_with=cl) as s:
        if not s.solve():
            return None
        for c in shared[1:]:
            aux, extra, nxt = [], [], nv + 1
            for i in range(P):
                y = nxt
                nxt += 1
                a, b = var(shared[0], i), var(c, i)
                extra += [[-y, a, b], [-y, -a, -b]]       # y -> (a != b)
                aux.append(y)
            with Glucose4(bootstrap_with=cl + extra + [aux]) as s2:
                if s2.solve():
                    return False
    return True


def crossed():
    k = []
    nxt = [6]

    def hang():
        nxt[0] += 1
        return nxt[0] - 1
    x, y, a1, a2, b1, b2 = range(6)
    for p, q in ((x, y), (y, a1), (a1, a2), (a2, x), (x, b1), (b1, b2), (b2, y), (y, x)):
        k.append((p, hang(), q))
    return (nxt[0], k), [x, y, a1, a2, b1, b2]


def circulant(n):
    k = []
    nxt = [n]

    def hang():
        nxt[0] += 1
        return nxt[0] - 1
    for i in range(n):
        k.append((i, hang(), (i + 1) % n))
    for i in range(n):
        k.append((i, hang(), (i + 2) % n))
    return (nxt[0], k), list(range(n))


def main():
    one = json.loads((HERE.parents[1] / "ENDLESS-BLOCK-20261112-001" / "referee-R1" / "result_one.json").read_text())["rows"]
    hs = R.harmonies()
    out = []
    for row in one:
        g = row["shortest closed walk with a step (girth)"]
        if g is None or g <= 2:
            continue
        h = hs[row["i"]]
        t0 = time.time()
        P, shared = crossed()
        item = {"i": row["i"], "orbits": h["orbits"], "P": h["P"], "girth": g,
                "crossed pair locks": locked_all(h, P, shared), "crossed pair's shortest coherent loop": 2, "circulants": []}
        for n in range(3, 2 * g + 2):
            if n * 3 * h["P"] > 2400:
                break
            P, shared = circulant(n)
            item["circulants"].append({"n": n, "locks": locked_all(h, P, shared), "shortest coherent loop": math.ceil(n / 2),
                                       "a single loop explains it": math.ceil(n / 2) < g})
        item["seconds"] = round(time.time() - t0, 1)
        out.append(item)
        print(item["orbits"][:2], g, item["crossed pair locks"], [(c["n"], c["locks"], c["a single loop explains it"]) for c in item["circulants"]], flush=True)
    (HERE / "result_overlap.json").write_text(json.dumps({"rows": out}, indent=1) + "\n")
    print("wrote result_overlap.json")


if __name__ == "__main__":
    main()
