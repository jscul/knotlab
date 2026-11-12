#!/usr/bin/env python3
"""Referee COMMON-FOLD-R1, ticket B: the last bases of U(100) and U(200), regenerated from the census's growth seeds
(random.Random(50000 + run)) with the referee's own generator and solver (ref_fates.py of the RANDOM-FATES referee folder), read with
the referee's own code: the largest tie class's share, and for 20 co-knotted pairs drawn with the referee's own seed, the forced
fraction (the larger over the pair's two patterns, as frozen), the part beyond the members' tie classes, and whether a member lies in
the largest tie class. Writes result_b.json."""
import itertools
import json
import random
import statistics as st
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "RANDOM-FATES-20261112-001" / "referee-R1"))
import ref_fates as F  # noqa: E402
from pysat.solvers import Glucose4  # noqa: E402


def grow(n, run):
    rng = random.Random(50000 + run)
    g = F.gen_uniform(n, rng)
    knots = []
    with Glucose4() as s:
        while True:
            t = next(g)
            knots.append(t)
            for c in F.nae_clauses(t):
                s.add_clause(c)
            if not s.solve():
                return knots[:-1], len(knots)


def backbone(s, n, assum, used):
    if not s.solve(assumptions=assum):
        return None
    m = s.get_model()
    val = {abs(x) - 1: x > 0 for x in m if abs(x) <= n}
    cand = set(used) - {abs(a) - 1 for a in assum}
    out = set()
    while cand:
        v = cand.pop()
        if s.solve(assumptions=assum + [-(v + 1) if val[v] else (v + 1)]):
            m2 = {abs(x) - 1: x > 0 for x in s.get_model() if abs(x) <= n}
            cand = {u for u in cand if m2[u] == val[u]}
        else:
            out.add(v)
    return out


def main():
    rows = []
    for n in (100, 200):
        for run in range(int(sys.argv[1]) if len(sys.argv) > 1 else 6):
            t0 = time.time()
            base, death = grow(n, run)
            B = F.Base(n, base, samples=300, seed=run)
            classes = B.ties()
            big = max(classes, key=len) if classes else []
            share = len(big) / n
            used = B.used
            s = B.s
            pairs = sorted({q for t in base for q in itertools.combinations(t, 2)})
            rng = random.Random(77000 + run)
            recs = []
            tieset = {}
            for (a, b) in rng.sample(pairs, 20):
                best = None
                for pat in ((0, 0), (0, 1)):
                    assum = [(a + 1) if pat[0] else -(a + 1), (b + 1) if pat[1] else -(b + 1)]
                    f = backbone(s, n, assum, used)
                    if f is None:
                        continue
                    ties = set()
                    for v, bit in ((a, pat[0]), (b, pat[1])):
                        key = (v, bit)
                        if key not in tieset:
                            tieset[key] = backbone(s, n, [(v + 1) if bit else -(v + 1)], used) or set()
                        ties |= tieset[key]
                    ties -= {a, b}
                    rec = {"forced": len(f) / n, "beyond ties": len(f - ties) / n}
                    if best is None or rec["forced"] > best["forced"]:
                        best = rec
                best["member in the largest class"] = a in big or b in big
                recs.append(best)
            B.close()
            rows.append({"n": n, "run": run, "death knot": death, "largest tie class share": share,
                         "pair forced mean": st.mean(r["forced"] for r in recs), "beyond ties mean": st.mean(r["beyond ties"] for r in recs),
                         "pairs with a member in the largest class": sum(r["member in the largest class"] for r in recs),
                         "forced mean, pairs with a member in it": st.mean([r["forced"] for r in recs if r["member in the largest class"]] or [0]),
                         "seconds": round(time.time() - t0, 1)})
            print(rows[-1], flush=True)
    (HERE / "result_b.json").write_text(json.dumps({"rows": rows}, indent=1) + "\n")


if __name__ == "__main__":
    main()
