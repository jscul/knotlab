"""MEET-ORDERS-20261118-001B frozen run, for the shared runner (docs/tooling/shared-runner.md).

Cases:
  M1|n0|i  Lemma B's finite check: every bracketing of a line of n0 (n0 = 4..11) in shard i, every first knot: KF3's
           second-step options classified (F, E or other), verdicts, and the exact two-order chance against Theorem 1.
  P5|n0    The fewest-knot presentations of a line of n0 (n0 = 5..9): every choice of one knot (a_c, c, b_c) per interior
           distinction c; which present the line, and are they exactly the bracketings.
  C|n0|d|j Exact KF3 order distributions from presentation j (one per mirror pair) of a line of n0, to n0 + d.
  X|n0|d|j Labelled run from presentation j: per level the number of labelled bases, the mass by the largest odd set of a
           new distinction (or "state added"), and Lemma C's two-order criterion against the measured number of orders on
           every base whose new distinctions are all fills of triples.
"""
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import melib as M

SHARD = 25
CENSUS = [(5, 5), (6, 4), (7, 4), (8, 4), (9, 4)]


def reps(n0):
    """One presentation per mirror pair, in a fixed order."""
    seen = set()
    out = []
    m = n0 - 1
    for T in M.bracketings(0, m):
        key = tuple(sorted(T))
        if tuple(M.mirror(T, m)) in seen or key in seen:
            continue
        seen.add(key)
        out.append(sorted(T))
    return out


def cases():
    for n0 in range(4, 12):
        nb = len(M.bracketings(0, n0 - 1))
        for i in range(0, nb, SHARD):
            yield f"M1|{n0}|{i // SHARD}", {"n0": n0, "lo": i, "hi": min(nb, i + SHARD)}
    for n0 in range(5, 10):
        yield f"P5|{n0}", {"n0": n0}
    for n0, d in CENSUS:
        for j, T in enumerate(reps(n0)):
            yield f"C|{n0}|{d}|{j}", {"n0": n0, "depth": d, "knots": T}
    for n0, d in ((5, 4), (6, 4), (7, 3)):
        for j, T in enumerate(reps(n0)):
            yield f"X|{n0}|{d}|{j}", {"n0": n0, "depth": d, "knots": T}


def run_m1(p):
    n0 = p["n0"]
    Ts = M.bracketings(0, n0 - 1)[p["lo"]:p["hi"]]
    out = []
    for T in Ts:
        per = []
        allok = True
        for k in T:
            r = M.classify_second_step(T, k)
            allok &= r["ok"]
            per.append({"first": list(k), "ok": r["ok"], "options": r["options"], "good": r["good"],
                        "kinds": sorted([x["kind"], x["two"]] for x in r["rows"])})
        exact = sum(M.Fraction(x["good"], x["options"]) for x in per) / len(T)
        out.append({"knots": T, "nesting": M.nesting(T, 0, n0 - 1), "ok": bool(allok),
                    "exact": str(exact), "formula": str(M.formula(T)), "match": exact == M.formula(T), "per_first": per})
    return {"n0": n0, "bracketings": out}


def run_p5(p):
    n0 = p["n0"]
    m = n0 - 1
    line = M.base(n0, [(0, i, i + 1) for i in range(1, m)])
    mask = {}
    for a, c, b in itertools.combinations(range(n0), 3):
        mask[(a, c, b)] = sum(1 << s for s in range(1 << n0) if M.ok_btw(s, a, c, b))
    target = sum(1 << s for s in line)
    choices = [[(a, c, b) for a in range(c) for b in range(c + 1, n0)] for c in range(1, m)]
    found = []
    total = 0
    for combo in itertools.product(*choices):
        total += 1
        x = (1 << (1 << n0)) - 1
        for k in combo:
            x &= mask[k]
        if x == target:
            found.append(sorted(combo))
    brs = sorted(sorted(T) for T in M.bracketings(0, m))
    return {"n0": n0, "candidate_sets": total, "presentations": len(found), "bracketings": len(brs),
            "equal_to_bracketings": sorted(found) == brs}


def run_c(p):
    n0, d, T = p["n0"], p["depth"], [tuple(k) for k in p["knots"]]
    lv = M.exact(n0, T, n0 + d)
    feats = []
    for L in lv:
        cr = {}
        for (S, G), q in L["dist"].items():
            mm = M.measure(S, L["n"])
            key = f'{mm["N"]},{mm["splits"]},{mm["crossings"]}'
            cr[key] = cr.get(key, 0) + q
        feats.append({k: str(v) for k, v in sorted(cr.items())})
    return {"n0": n0, "depth": d, "knots": T, "nesting": M.nesting(T, 0, n0 - 1),
            "ordered": M.nesting(T, 0, n0 - 1, ordered=True), "levels": M.order_dist(lv), "coarse": feats}


def criterion(sets):
    """Lemma C: on the line with fills of triples, two orders iff some fill exists and no fill's middle lies strictly inside
    another fill's span except at that fill's own middle."""
    if not sets:
        return False
    for (u, v, w) in sets:
        for (x, y, z) in sets:
            if x < v < z and v != y:
                return False
    return True


def run_x(p):
    n0, d, T = p["n0"], p["depth"], [tuple(k) for k in p["knots"]]
    lv = M.exact(n0, T, n0 + d, use_canon=False)
    out = []
    for L in lv:
        by = {}
        two_by = {}
        agree = disagree = 0
        for (S, G), q in L["dist"].items():
            sets = M.odd_sets(S, L["n"], n0)
            key = "state added" if sets is None else ("line" if not sets else f"largest odd set {max(map(len, sets))}")
            by[key] = by.get(key, 0) + q
            if M.two_orders(M.measure(S, L["n"])):
                two_by[key] = two_by.get(key, 0) + q
            if sets is not None and all(len(s) == 3 for s in sets):
                if criterion(sets) == M.two_orders(M.measure(S, L["n"])):
                    agree += 1
                else:
                    disagree += 1
        out.append({"n": L["n"], "labelled": L["classes"], "mass": {k: str(v) for k, v in sorted(by.items())},
                    "two_orders_mass": {k: str(v) for k, v in sorted(two_by.items())},
                    "criterion_agree": agree, "criterion_disagree": disagree, "two": str(L["two"])})
    return {"n0": n0, "depth": d, "knots": T, "nesting": M.nesting(T, 0, n0 - 1),
            "ordered": M.nesting(T, 0, n0 - 1, ordered=True), "levels": out}


def run(case_id, payload):
    kind = case_id.split("|")[0]
    return {"M1": run_m1, "P5": run_p5, "C": run_c, "X": run_x}[kind](payload)


if __name__ == "__main__":
    n = sum(1 for _ in cases())
    print(n, "cases")
