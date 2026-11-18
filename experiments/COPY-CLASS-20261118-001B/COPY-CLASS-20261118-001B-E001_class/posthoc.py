"""COPY-CLASS-20261118-001B-E001: post hoc (labelled), after the frozen rule CR failed on every absorbing fill.  For each
crossing-making knot set: where SEED's model lies (among the crossed splits separating which end pair, if any), the variant CRSWAP that
seeks the model among the crossed splits separating the end pair NOT sharing a distinction with the middle pair, CRBOTH (either end
pair), and the model's crosser count against the number of splits.  Same starts and seeds as run.py: every fifth start first (where
CRSWAP was found), then, with --rest, the other four fifths as a held-out score of CRSWAP fixed on the first."""
import json
import multiprocessing as mp
import os
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import classlib as C  # noqa: E402
import run as RUN  # noqa: E402

M, P, K, L, KL = C.M, C.P, C.K, C.L, C.KL
OUT = RUN.OUT


def roles(ks, n):
    ends = [k for k in ks if k[1] != n]
    mids = [k for k in ks if k[1] == n]
    pe = [tuple(x for x in k if x != n) for k in ends]
    mp_ = set(x for x in mids[0] if x != n) if mids else set()
    share = [t for t, p in enumerate(pe) if mp_ & set(p)]
    other = [t for t in range(len(pe)) if t not in share]
    return pe, share, other


def job(arg):
    n0, i, ks0, seed = arg
    rng = random.Random(seed)
    S, G, knots, n = M.base(n0, ks0), M.pairs_of(ks0), list(ks0), n0
    T = Counter()
    sizes = []
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
                new = set(P.new_crossings(S, n, a1)[0])
                if not new:
                    continue
                e = ext.setdefault((a0, a1), {"seed": (a0, a1) in acc, "swap": False, "both": False, "where": set()})
                if any(i_ in active and j in active for i_, j in new):
                    continue
                newN = {}
                for i_, j in new:
                    newN.setdefault(i_, set()).add(j)
                    newN.setdefault(j, set()).add(i_)
                gained = [u for u in newN if u not in active]
                after = {v: set(Gc[v]) | newN.get(v, set()) for v in Gc}
                pe, share, other = roles(ks, n)
                sep = [set(C.separating(sp, *p)) for p in pe]
                cand_swap = set().union(*[sep[t] for t in other]) & active if other else set()
                cand_both = set().union(*sep) & active
                okswap = all(any(after[m] == after[u] for m in cand_swap) for u in gained)
                okboth = all(any(after[m] == after[u] for m in cand_both) for u in gained)
                e["swap"] |= okswap
                e["both"] |= okboth
                if e["seed"]:
                    for u in gained:
                        ms = [m for m in active if after[m] == after[u]]
                        where = "share-pair" if any(m in set().union(*[sep[t] for t in share]) for m in ms) else (
                            "other-pair" if any(m in cand_swap for m in ms) else "elsewhere")
                        e["where"].add(where)
                        if ms:
                            sizes.append((len(Gc[ms[0]]), len(sp)))
            for e in ext.values():
                T[f"seed={int(e['seed'])} swap={int(e['swap'])} both={int(e['both'])}"] += 1
                for w in e["where"]:
                    T["model " + w] += 1
        a0, a1, ks = rng.choice(ops)
        S, G, knots, n = M.apply(S, n, a0, a1), G | M.pairs_of(ks), knots + list(ks), n + 1
    return dict(T), sizes


def main():
    rest = "--rest" in sys.argv
    J = [j for k, j in enumerate(RUN.jobs()) if (k % 5 != 0) == rest]
    with mp.Pool(8) as pool:
        res = pool.map(job, J, chunksize=1)
    T = Counter()
    sizes = []
    for t, s in res:
        T.update(t)
        sizes += s
    out = {"starts": len(J), "tally": dict(T), "model_crossers": dict(Counter(a for a, b in sizes)),
           "model_crossers_over_splits_median": sorted(a / b for a, b in sizes)[len(sizes) // 2] if sizes else None}
    json.dump(out, open(os.path.join(OUT, "posthoc_rest.json" if rest else "posthoc.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
