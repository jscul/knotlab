"""FAR-SIGN-20261118-001B-E001 gate checks.

1. Proposition 7's base: the states allowed by every betweenness knot it implies are exactly its constant states and both sides of
   its four splits; its crossed splits form two orders.
2. Proposition 7 (A) and (B): the two fills exist (fills on any pairs), with the stated knot sets, SEED verdicts, signs and moved sets;
   every knot set of fill (B) of the treated shape lacks the sign. Also the number of orders after (B).
3. On one SEEDK run (a bracketing of 6 to n = 20): this library's SEED verdict equals knotlib's on every crossing-making extension,
   and L1, L2 and K1 hold on every knot set of the treated shape.
Run: python -B checks.py
"""
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import signlib as SL  # noqa: E402

M, L, P = SL.M, SL.L, SL.P


def ok(s, k):
    x, y, z = ((s >> k[0]) & 1, (s >> k[1]) & 1, (s >> k[2]) & 1)
    return not (x == z != y)


def prop7_base():
    n = 7
    halves = [0b0111000, 0b0001001, 0b0100100, 0b1000000]        # {3,4,5}, {0,3}, {2,5}, {6} (bit u = distinction u)
    full = (1 << n) - 1
    S = tuple(sorted({0, full} | set(halves) | {full ^ h for h in halves}))
    implied = [(x, y, z) for x, z in itertools.combinations(range(n), 2) for y in range(n) if y not in (x, z)
               and all(ok(s, (x, y, z)) for s in S)]
    allowed = tuple(s for s in range(1 << n) if all(ok(s, k) for k in implied))
    return S, n, allowed


def check_base():
    S, n, allowed = prop7_base()
    sp, Gc, active, orders = SL.base_view(S, n)
    good = allowed == S and orders is not None and sorted(len(o) for o in orders) == [1, 2] and len(sp) == 4
    return good, {"states": len(S), "allowed_by_implied_knots": len(allowed), "orders": sorted(len(o) for o in orders) if orders else None}


def check_prop7():
    S, n, _ = prop7_base()
    sp, Gc, active, orders = SL.base_view(S, n)
    allp = set(itertools.combinations(range(n), 2))
    byext = {}
    for a0, a1, ks in L.moves(S, n, allp):
        if P.pc(a0) + P.pc(a1) == len(S):
            byext.setdefault((a0, a1), []).append(tuple(sorted(ks)))
    want = {"A": tuple(sorted(((3, 7, 6), (1, 6, 7), (5, 0, 7)))), "B": tuple(sorted(((3, 7, 6), (0, 6, 7), (0, 4, 7))))}
    rep = {}
    for name, ks in want.items():
        hit = [(e, c) for e, c in byext.items() if ks in c]
        if len(hit) != 1:
            rep[name] = {"found": len(hit)}
            continue
        (a0, a1), cert = hit[0]
        new = P.new_crossings(S, n, a1)[0]
        gained = sorted({v for e in new for v in e if v not in active})
        seed, why = SL.seed_verdict(sp, Gc, active, new)
        A = SL.analyse(S, n, a1, ks, sp, Gc, active, orders, new, gained)
        moved = sorted(i for i, s in enumerate(sp) if ((a1 >> S.index(s)) & 1) != ((s >> 6) & 1))
        others = [SL.analyse(S, n, a1, k, sp, Gc, active, orders, new, gained) for k in cert]
        rep[name] = {"seed": seed, "why": why, "sign": A["sign"], "moved": [bin(sp[i]) for i in moved], "T2": A["T2"],
                     "L1": A["L1"], "L2": A["L2"], "any_set_with_sign": any(o and o["sign"] for o in others),
                     "a1": a1}
        if name == "B":
            S2 = M.apply(S, n, a0, a1)
            rep[name]["orders_after"] = M.measure(S2, n + 1)["lam"]
    good = (rep["A"].get("seed") is False and rep["A"].get("sign") is True and rep["A"].get("why") == "b"
            and rep["B"].get("seed") is True and rep["B"].get("any_set_with_sign") is False
            and all(rep[x].get("L1") and rep[x].get("L2") for x in "AB"))
    return good, rep


def check_engine():
    ks = M.bracketings(0, 5)[7]
    rows, _ = SL.run(ks, 6, 20, 424242, closure=False)
    agree = sum(r["mine"] == r["seed"] for r in rows)
    sets = [s for r in rows for s in r["sets"] if s and "L1" in s]
    lem = sum(s["L1"] and s["L2"] and s["K1"] for s in sets)
    return agree == len(rows) and lem == len(sets) and len(rows) > 0, {"extensions": len(rows), "seed_agree": agree,
                                                                        "knot_sets": len(sets), "lemmas_hold": lem}


if __name__ == "__main__":
    allok = True
    for name, f in (("base", check_base), ("prop7", check_prop7), ("engine", check_engine)):
        good, info = f()
        allok &= good
        print(name, "PASS" if good else "FAIL", info)
    print("ALL PASS" if allok else "SOME FAIL")
