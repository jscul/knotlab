"""Referee R1 for COPY-CLASS-20261118-001: a cross-check ON THE STUDY'S OWN ENGINE (imports the study's classlib.py and run.py, read
only; writes nothing there), so that the referee's main finding is not an artifact of its own engine.

  ../../../.venv/bin/python -B referee_class_crosscheck.py > referee_class_crosscheck.json      (from this directory)

On all 135 starts of the frozen run, with the study's seeds and moves and the same candidate sets as posthoc.py: for every knot set
(one end pair touching the middle pair) of every extension SEED accepts that makes a new crossing, whether the crossed splits
separating the far end pair (CRSWAP's candidates) are all the crossed splits (SEED's candidates); and, for every crossing-making
extension, whether some such knot set has that sign, against SEED's verdict.
"""
import json
import os
import random
import sys
from collections import Counter
from multiprocessing import Pool

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
EXP = os.path.join(ROOT, "experiments", "COPY-CLASS-20261118-001B", "COPY-CLASS-20261118-001B-E001_class")
sys.path.insert(0, EXP)
import classlib as C  # noqa: E402
import run as RUN  # noqa: E402
import posthoc as PH  # noqa: E402

M, P, K, L = C.M, C.P, C.K, C.L


def job(arg):
    n0, i, ks0, seed = arg
    rng = random.Random(seed)
    S, G, knots, n = M.base(n0, ks0), M.pairs_of(ks0), list(ks0), n0
    T = Counter()
    while n < RUN.NMAX:
        b = K.betti(n, knots)
        ops, kind = K.seedk_options(S, n, G, b["b2"])
        if not ops:
            break
        if b["b2"] > 0:
            acc = {x[:2] for x in ops} if kind == "fill" else set()
            sp, Gc = P.crossing_graph(S, n)
            active = {v for v in Gc if Gc.degree(v) > 0}
            ext = {}
            for a0, a1, ks in [x for x in L.moves(S, n, G) if P.pc(x[0]) + P.pc(x[1]) == len(S)]:
                if (a0, a1) not in ext:
                    new = set(P.new_crossings(S, n, a1)[0])
                    if not new:
                        ext[(a0, a1)] = None
                        continue
                    clause_a = not any(i_ in active and j in active for i_, j in new)
                    ext[(a0, a1)] = {"seed": (a0, a1) in acc, "a": clause_a, "sign": False}
                e = ext[(a0, a1)]
                if e is None:
                    continue
                pe, share, other = PH.roles(ks, n)
                if len(share) != 1:
                    continue
                sep = [set(C.separating(sp, *p)) for p in pe]
                cand_swap = set().union(*[sep[t] for t in other]) & active
                if e["seed"]:
                    T["copy step: knot sets with one touching end pair"] += 1
                    T["copy step: ... whose far pair's crossed splits = all crossed splits"] += cand_swap == active
                e["sign"] |= cand_swap == active
            for e in ext.values():
                if e is not None:
                    T[f"extensions seed={int(e['seed'])} sign={int(e['sign'])}" + ("" if e["seed"] else f" clause_a={int(e['a'])}")] += 1
        a0, a1, ks = rng.choice(ops)
        S, G, knots, n = M.apply(S, n, a0, a1), G | M.pairs_of(ks), knots + list(ks), n + 1
    return dict(T)


if __name__ == "__main__":
    J = RUN.jobs()
    with Pool(16) as pool:
        res = pool.map(job, J, chunksize=1)
    T = Counter()
    for t in res:
        T.update(t)
    print(json.dumps({"starts": len(J), "tally": dict(sorted(T.items()))}, indent=1))
