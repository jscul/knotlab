"""COPY-READ-20261118-001B-E001: SEED's copy clause in knot terms.

After SEED's switch, the fills that make a new crossing (all with two end knots, MID-RULE-20261118-001A, E1) are either accepted by
SEED (they absorb a split that crossed nothing, giving it exactly the crossers of a crossed split, and keep two orders) or refused
(they raise the orders or make a crossing between crossed splits).  Each is given its pictures at tier 0 (its own knots), the
closure tier (implied betweenness among its distinctions) and tier 1 (presented knots within one step), as in KEEP-READ-20261118-001B
(keeplib.py, pinned), and the share of the base its radius-one ball covers.
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.append(os.path.join(ROOT, "experiments", "KEEP-READ-20261118-001B", "KEEP-READ-20261118-001B-E001_keep"))
import keeplib as KL  # noqa: E402

K, M, L, P = KL.K, KL.M, KL.L, KL.P


def run(knots0, n0, nmax, seed_value):
    """A SEEDK run; after the switch, every zero-cost move that makes a new crossing, with its label and pictures; and, per tier,
    the in-run look-alike pairs (an absorbing and a raising move with isomorphic pictures)."""
    rng = random.Random(seed_value)
    S, G, knots, n = M.base(n0, knots0), M.pairs_of(knots0), list(knots0), n0
    rows = []                                   # absorbing moves, in full
    refused = {t: {} for t in ("0", "c", "1")}  # refused moves: picture hash -> count
    n_refused = 0
    reps = {t: {} for t in ("0", "c", "1")}
    while n < nmax:
        b = K.betti(n, knots)
        ops, kind = K.seedk_options(S, n, G, b["b2"])
        if not ops:
            break
        if b["b2"] > 0:
            acc = {x[:2] for x in ops} if kind == "fill" else set()
            mv = L.moves(S, n, G)
            memo = {}
            for a0, a1, ks in [x for x in mv if P.pc(x[0]) + P.pc(x[1]) == len(S)]:
                if (a0, a1) not in memo:
                    memo[(a0, a1)] = bool(P.new_crossings(S, n, a1)[0])
                if not memo[(a0, a1)]:
                    continue
                lab = "absorb" if (a0, a1) in acc else "refuse"
                row = {"n": n, "ext": [a0, a1], "label": lab, "ends": sum(1 for k in ks if k[1] != n),
                       "cov1": KL.coverage(knots, ks, n, 1)}
                for t in ("0", "c", "1"):
                    pic = KL.picture_closure(S, n, ks) if t == "c" else KL.picture(knots, ks, n, int(t))
                    h = KL.wl(pic)[:12]
                    row["h" + t] = h
                    if lab == "refuse":
                        refused[t][h] = refused[t].get(h, 0) + 1
                    reps[t].setdefault(h, {}).setdefault(lab, pic)
                if lab == "absorb":
                    rows.append(row)
                else:
                    n_refused += 1
        a0, a1, ks = rng.choice(ops)
        S, G, knots, n = M.apply(S, n, a0, a1), G | M.pairs_of(ks), knots + list(ks), n + 1
    verified = {}
    for t in reps:
        mixed = [h for h, d in reps[t].items() if len(d) == 2]
        ok = [h for h in mixed if KL.same(reps[t][h]["absorb"], reps[t][h]["refuse"])]
        verified[t] = {"mixed": len(mixed), "isomorphic": len(ok), "hashes": ok,
                       "example": ({"absorb": KL.serial(reps[t][ok[0]]["absorb"]),
                                    "refuse": KL.serial(reps[t][ok[0]]["refuse"])} if ok else None)}
    return rows, refused, n_refused, verified
