"""Referee R1 for LOOP-CATALOGUE-20261119-001 (own growth and tests; the study's starts, counts and recorded round-weights are
read from runs/loop-catalogue as data; no study code imported or run).

  ../../../.venv/bin/python -B referee_loop.py <part> > referee_loop_<part>.json      (from this directory)

Growth: the referee's own engine (FRESH-COUNT-R1 / FIRST-KNOT-R1: complete rounds, the fewest counts, GF(2) implication), from
stars built by the referee (its TOUCH-CENSUS-R1 convention).  Classes: a tail is quasi-polynomial when (1 - y^p)^k annihilates its
last rounds for some period p <= 12 and order k <= 5; a rising tail that is not is called exponential.

Parts:
  series   every catalogue entry (C), ring (R), even-ring placement (R8) and interface start (I): the referee's counts against the
           study's; the recorded round-weight W (a series; an eventually constant tail is read as c y^m / (1 - y), the endless
           chain's form) made exact; whether the referee's counts are annihilated, after a transient, by num(1 - W) (1 - y)^2, the
           denominator the transfer argument gives; and the root of W = 1 against the referee's last ratio.  Even rings with one
           spare (W not recorded: two loops) are tested against (1 - y^L - y^(L+1)) (1 - y^L) (1 - y)^2, L = n / 2.
  roots    the real roots above 1 of x^(L + 1) = x + 1 for the listed L, against the listed rates.
  minimal  each catalogue entry with one spare place removed, or one knot removed (sizes recomputed as bare plus the remaining
           spares), grown 36 rounds: is any reduction still exponential?
  eddies   the 49 rule-eddies of part E and every 8th grown non-eddy, regrown and classified by the referee.
  partu    part U's starts with meeting groups of three that the study calls exponential (and the six-knot theta), regrown and
           classified by the referee.
"""
import json
import os
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
import referee_first as RFK  # noqa: E402
import referee_touch as RT  # noqa: E402

RUN = ROOT / "runs/loop-catalogue/results.jsonl"


def grow(sizes, edges, rounds=36, maxj=30000):
    n = len(sizes)
    M = [[0] * n for _ in range(n)]
    for a, b in edges:
        M[a][b] += 1
        M[b][a] += 1
    G = RFK.Start(RT.stars(sizes, M))
    out = "alive"
    for _ in range(rounds):
        r = G.step(RFK.fewest, None, None)
        if r != "ok":
            out = r
            break
        if len(G.bits) > maxj:
            out = "cap"
            break
    return G.counts(), out


def annihilated_from(c, poly, need=8):
    """poly: coefficients of D(y) (constant first, D(0) = 1).  Least t0 with sum_i poly[i] c(t - i) = 0 for every t >= t0, if at
    least `need` rounds are tested; else None."""
    d = len(poly) - 1
    bad = [t for t in range(d, len(c)) if sum(poly[i] * c[t - i] for i in range(d + 1)) != 0]
    t0 = (bad[-1] + 1) if bad else d
    return t0 if len(c) - t0 >= need else None


def pmul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def exact_W(coeffs):
    """W as (numerator, denominator) polynomials: a series whose last 4 recorded coefficients are equal and nonzero is read as
    poly + c y^m / (1 - y)."""
    w = list(coeffs)
    while w and w[-1] == 0:
        w.pop()
    if len(w) >= len(coeffs) - 1 and len(w) >= 4 and len(set(w[-4:])) == 1 and w[-1] != 0:
        c = w[-1]
        m = len(w) - 1
        while m > 0 and w[m - 1] == c:
            m -= 1
        head = w[:m] + [0]
        # poly + c y^m / (1 - y) = (head (1 - y) + c y^m) / (1 - y)
        num = pmul(head, [1, -1])
        num = num + [0] * max(0, m + 1 - len(num))
        num[m] += c
        return num, [1, -1], True
    return w, [1], False


def one_minus(num, den):
    n = max(len(num), len(den))
    a = den + [0] * (n - len(den))
    b = num + [0] * (n - len(num))
    return [x - y for x, y in zip(a, b)]


def root_of(poly_x):
    """Real root above 1 of the polynomial (coefficients constant first, in x), by bisection."""
    def f(x):
        return sum(c * x ** i for i, c in enumerate(poly_x))
    lo, hi = 1.0 + 1e-12, 4.0
    if f(lo) * f(hi) > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return lo


def w_root(num, den):
    """Root y* in (0, 1) of W(y) = 1, returned as 1 / y*."""
    def W(y):
        return sum(c * y ** i for i, c in enumerate(num)) / sum(c * y ** i for i, c in enumerate(den))
    lo, hi = 1e-9, 0.999999
    if W(hi) < 1:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if W(mid) < 1:
            lo = mid
        else:
            hi = mid
    return 1 / lo


def quasi_poly(c, tail=15):
    t = c[-tail:]
    for p in range(1, 13):
        for k in range(1, 6):
            poly = [1]
            for _ in range(k):
                poly = pmul(poly, [1] + [0] * (p - 1) + [-1])
            d = len(poly) - 1
            if d >= len(t):
                continue
            if all(sum(poly[i] * t[s - i] for i in range(d + 1)) == 0 for s in range(d, len(t))):
                return f"quasi-polynomial (p {p}, k {k})"
    return "exponential" if t[-1] > t[0] else "not rising"


def classify(c, out):
    if out == "stall":
        return "stall"
    if out == "closed":
        return "closed"
    if len(c) < 18:
        return f"short ({out})"
    return quasi_poly(c)


def records():
    rows = defaultdict(list)
    for line in open(RUN):
        r = json.loads(line)
        if r.get("status") != "ok":
            continue
        rows[r["case"].split("-")[0]].append((r["case"], r["result"]))
    return rows


def _series(item):
    name, sizes, edges, theirs, W, even_L = item
    c, out = grow(sizes, edges, rounds=max(30, len(theirs) - 1), maxj=40000)
    m = min(len(c), len(theirs))
    row = {"case": name, "rounds": len(c) - 1, "outcome": out, "counts equal the study's": c[:m] == theirs[:m],
           "last ratio": round(c[-1] / c[-2], 6) if len(c) > 2 and c[-2] else None}
    if W is not None:
        num, den, chain = exact_W(W)
        D = pmul(one_minus(num, den), [1, -2, 1])
        row["W read with an endless-chain tail"] = chain
        row["root of W = 1"] = round(w_root(num, den), 6) if w_root(num, den) else None
        row["annihilated by num(1 - W)(1 - y)^2 from round"] = annihilated_from(c, D)
    if even_L:
        L = even_L
        D = pmul(pmul([1] + [0] * (L - 1) + [-1, -1], [1] + [0] * (L - 1) + [-1]), [1, -2, 1])
        row["even ring: annihilated by (1 - y^L - y^(L+1))(1 - y^L)(1 - y)^2 from round"] = annihilated_from(c, D)
        row["root of x^(L+1) = x + 1"] = round(root_of([-1, -1] + [0] * (L - 1) + [1]), 6)
    return row


def part_series():
    rec = records()
    items = []
    for name, r in rec["C"]:
        e = r["entry"]
        items.append((name, e["sizes"], e["edges"], r["parity"], (r.get("W") or {}).get("W"), None))
    for name, r in rec["R"]:
        n = r["n"]
        edges = [[i, (i + 1) % n] for i in range(n)]
        even = n // 2 if (n % 2 == 0 and r["spare"]) else None
        items.append((name, r["sizes"], edges, r["counts"], (r.get("W") or {}).get("W"), even))
    for name, r in rec["R8"]:
        pass                                              # their stars are not recorded with edges; covered by the C and R parts
    for name, r in rec["I"]:
        for it in r["interfaces"]:
            items.append((f"{name} {it['kind']} at {it['knot']}", it["sizes"], it["edges"], it["counts"],
                          (it.get("W") or {}).get("W"), None))
    with Pool(int(os.environ.get("WORKERS", "10"))) as pool:
        rows = pool.map(_series, items, chunksize=1)
    withW = [r for r in rows if "annihilated by num(1 - W)(1 - y)^2 from round" in r]
    ev = [r for r in rows if "even ring: annihilated by (1 - y^L - y^(L+1))(1 - y^L)(1 - y)^2 from round" in r]
    return {"starts": len(rows), "counts equal the study's": sum(r["counts equal the study's"] for r in rows),
            "with a recorded W": len(withW),
            "... annihilated by num(1 - W)(1 - y)^2": sum(r["annihilated by num(1 - W)(1 - y)^2 from round"] is not None for r in withW),
            "... W read with an endless-chain tail": sum(r["W read with an endless-chain tail"] for r in withW),
            "even rings with one spare": len(ev),
            "... annihilated by the two-loop denominator": sum(r["even ring: annihilated by (1 - y^L - y^(L+1))(1 - y^L)(1 - y)^2 from round"] is not None for r in ev),
            "not annihilated": [r for r in withW if r["annihilated by num(1 - W)(1 - y)^2 from round"] is None],
            "rows": rows}


def part_roots():
    listed = {"ring of eight, one spare (L = 4)": (4, 1.1673), "ring of five (L = 5)": (5, 1.1347), "ring of seven (L = 7)": (7, 1.0970),
              "ring of 9 (L = 9)": (9, 1.0758), "ring of 10 (L = 5)": (5, 1.1347), "ring of 11 (L = 11)": (11, 1.0622),
              "ring of 12 (L = 6)": (6, 1.1128), "ring of 13 (L = 13)": (13, 1.0527)}
    out = {}
    for k, (L, rate) in listed.items():
        r = root_of([-1, -1] + [0] * (L - 1) + [1])
        out[k] = {"root of x^(L+1) = x + 1": round(r, 6), "listed": rate, "agrees to 4 places": round(r, 4) == rate}
    return out


def bare(n, edges, spares):
    """Bare sizes: max(3, shared + round-1 demand), demand read from the referee's own engine's round-1 groups."""
    nb = defaultdict(set)
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    shared = Counter()
    for a, b in edges:
        shared[a] += 1
        shared[b] += 1
    big = [shared[k] + 9 for k in range(n)]
    M = [[0] * n for _ in range(n)]
    for a, b in edges:
        M[a][b] += 1
        M[b][a] += 1
    G = RFK.Start(RT.stars(big, M))
    live = [j for j in G.live if G.loose(j)]
    d = Counter(j for g in G.groups(live, None) for j in g)
    return [max(3, shared[k] + d[k]) + spares[k] for k in range(n)]


def _min(item):
    name, sizes, edges = item
    c, out = grow(sizes, edges)
    return name, classify(c, out), len(c) - 1


def part_minimal():
    rec = records()
    items = []
    for name, r in rec["C"]:
        e = r["entry"]
        n, edges, spares = e["n"], [tuple(x) for x in e["edges"]], e["spares"]
        items.append((f"{name} itself", e["sizes"], edges))
        for k in range(n):
            if spares[k]:
                s2 = list(spares)
                s2[k] -= 1
                items.append((f"{name} minus a spare at {k}", bare(n, edges, s2), edges))
        for k in range(n):
            keep = [v for v in range(n) if v != k]
            idx = {v: i for i, v in enumerate(keep)}
            e2 = [(idx[a], idx[b]) for a, b in edges if a != k and b != k]
            s2 = [spares[v] for v in keep]
            items.append((f"{name} minus knot {k}", bare(n - 1, e2, s2), e2))
    with Pool(int(os.environ.get("WORKERS", "10"))) as pool:
        rows = pool.map(_min, items, chunksize=1)
    return {"starts": len(rows), "reductions still exponential": [r for r in rows if r[1] == "exponential" and "itself" not in r[0]],
            "entries themselves": [r for r in rows if "itself" in r[0]], "rows": rows}


def _cls(item):
    name, sizes, edges, theirs = item
    c, out = grow(sizes, edges, rounds=36, maxj=30000)
    m = min(len(c), len(theirs))
    return {"case": name, "mine": classify(c, out), "theirs": theirs and None, "equal": c[:m] == theirs[:m], "rounds": len(c) - 1,
            "last ratio": round(c[-1] / c[-2], 4) if len(c) > 2 and c[-2] else None}


def part_eddies():
    rec = records()
    eddies, non = [], []
    for name, r in rec["E"] + rec["S"]:
        for i, g in enumerate(r["grown"]):
            item = (f"{name} {i}", g["sizes"], g["edges"], g["counts"])
            (eddies if g["rule"] == "True" else non).append((item, g["growth"]))
    sample = non[::8]
    with Pool(int(os.environ.get("WORKERS", "10"))) as pool:
        re_ = pool.map(_cls, [x for x, _ in eddies], chunksize=1)
        rn = pool.map(_cls, [x for x, _ in sample], chunksize=1)
    return {"rule-eddies": len(eddies), "... the referee's class": dict(Counter(r["mine"] for r in re_)),
            "... counts equal the study's": sum(r["equal"] for r in re_),
            "non-eddies sampled (every 8th)": len(rn), "... the referee's class": dict(Counter(r["mine"].split(" (")[0] for r in rn)),
            "... counts equal the study's": sum(r["equal"] for r in rn),
            "non-eddies the referee calls exponential": [r for r in rn if r["mine"] == "exponential"]}


def part_partu():
    rec = records()
    items = []
    for name, r in rec["U"]:
        for i, s in enumerate(r["starts"]):
            if s.get("meet") and str(s.get("growth", "")).startswith("exp"):
                items.append((f"{name} {i}", s["sizes"], s["edges"], s["counts"]))
            elif s["n"] == 6 and str(s.get("growth", "")).startswith("exp"):
                items.append((f"{name} {i} (six knots)", s["sizes"], s["edges"], s["counts"]))
    with Pool(int(os.environ.get("WORKERS", "10"))) as pool:
        rows = pool.map(_cls, items, chunksize=1)
    return {"starts": len(rows), "the referee's class": dict(Counter(r["mine"].split(" (")[0] for r in rows)),
            "counts equal the study's": sum(r["equal"] for r in rows), "rows": rows}


if __name__ == "__main__":
    print(json.dumps({"series": part_series, "roots": part_roots, "minimal": part_minimal, "eddies": part_eddies,
                      "partu": part_partu}[sys.argv[1]](), indent=1, default=str))
