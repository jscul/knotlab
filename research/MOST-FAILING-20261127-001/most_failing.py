"""most_failing.py: a principle for the free sign (MOST-FAILING-20261127-001; README.md, frozen predictions G, P1-P3).

At each closure where birth choices attain an odd close (LOCAL-COMMUTE-20261127-001), the birth choices form a binary
linear code over the decidable pairs, with one parity check per pair of knots, and the closing sign is a linear
functional on it. The principle takes the code's maximum-weight words (the most failing pairs); the control takes its
minimum-weight nonzero words (the least departure from classical). For each: is the sign the same on every such word?
Exact integer programs (scipy milp, HiGHS), each parity check an even sum with one integer variable; exhaustive
enumeration where the code has at most ENUM free directions.
    most_failing.py [--limit N] [--enum 14]
Writes results.jsonl, summary.json and gates.json next to this file.
"""
import argparse
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix, lil_matrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LC = ROOT / "research" / "LOCAL-COMMUTE-20261127-001"
sys.path.insert(0, str(LC))
sys.path.insert(0, str(ROOT / "research" / "FORBID-EDITS-20261126-001"))
import forbid  # noqa: E402
import local_commute as lc  # noqa: E402  (the birth choices: Structure, rows, cost)


def code_of(st):
    pairs = st.local
    rows, _ = st.rows(pairs)
    H = [r for r in rows.values() if r]
    return len(pairs), H, st.cost(pairs)


def popcount(x):
    return bin(x).count("1")


class Unsettled(Exception):
    pass


def program(n, H, cost, maximize, parity=None, nonzero=False, types=None, rhs=None):
    """Optimal weight of a code word (max or min), with the sign fixed to `parity` if given. With `types` (a list of
    position lists), the weight counts each type once (a type counts when any of its positions is chosen). With `rhs`,
    the checks are H x = rhs (round-by-round systems). Returns (weight, word) or None if infeasible; raises Unsettled if
    not solved to proven optimality. Every optimum is checked against the parity checks."""
    m = len(H)
    extra = 1 if parity is not None else 0
    nt = len(types) if types else 0
    nv = n + m + extra + nt
    rhs = rhs or [0] * m
    c = np.zeros(nv)
    if types:
        c[n + m + extra:] = -1.0 if maximize else 1.0
    else:
        c[:n] = -1.0 if maximize else 1.0
    nrows = m + extra + (1 if nonzero else 0) + nt
    A = lil_matrix((nrows, nv))
    lo, hi = [], []
    for i, r in enumerate(H):
        for j in range(n):
            if (r >> j) & 1:
                A[i, j] = 1
        A[i, n + i] = -2
        lo.append(rhs[i])
        hi.append(rhs[i])
    if parity is not None:
        for j in range(n):
            if (cost >> j) & 1:
                A[m, j] = 1
        A[m, n + m] = -2
        lo.append(parity)
        hi.append(parity)
    base = m + extra
    if nonzero:
        for j in range(n):
            A[base, j] = 1
        lo.append(1)
        hi.append(np.inf)
        base += 1
    for q, positions in enumerate(types or []):        # t_q <= sum of the type's positions
        A[base + q, n + m + extra + q] = 1
        for j in positions:
            A[base + q, j] = -1
        lo.append(-np.inf)
        hi.append(0)
    upper = np.concatenate([np.ones(n), [popcount(r) // 2 for r in H], [popcount(cost) // 2] * extra, np.ones(nt)])
    res = milp(c, constraints=LinearConstraint(csr_matrix(A), lo, hi), integrality=np.ones(nv),
               bounds=Bounds(np.zeros(nv), upper), options={"mip_rel_gap": 0, "time_limit": 60})
    if res.status == 2:
        return None
    if res.status != 0:
        raise Unsettled(res.message)
    x = np.round(res.x[:n]).astype(int)
    word = sum(1 << j for j in range(n) if x[j])
    assert all(popcount(r & word) % 2 == b for r, b in zip(H, rhs)), "an optimum breaks a parity check"
    if types:
        tw = sum(1 for positions in types if any(x[j] for j in positions))
        assert tw == int(round(-res.fun if maximize else res.fun))
        return tw, word
    if parity is not None:
        assert popcount(cost & word) % 2 == parity
    if nonzero:
        assert word
    return int(x.sum()), word


def verdict(best, odd, even):
    """the sign on every optimal word: forced odd, forced even, or free"""
    if odd is not None and odd[0] == best and (even is None or even[0] != best):
        return "forced odd"
    if even is not None and even[0] == best and (odd is None or odd[0] != best):
        return "forced even"
    assert odd is not None and even is not None and odd[0] == even[0] == best
    return "free"


def holder_types(st):
    """positions grouped by the holders of their two members"""
    groups = {}
    for j, (a, b) in enumerate(st.local):
        key = tuple(sorted((tuple(st.holders[a]), tuple(st.holders[b]))))
        groups.setdefault(key, []).append(j)
    return list(groups.values())


def principles(n, H, cost, types=None):
    out = {}
    try:
        mx = program(n, H, cost, True)
        mx_odd = program(n, H, cost, True, parity=1)
        mx_even = program(n, H, cost, True, parity=0)
        out.update({"max weight": mx[0], "max with odd sign": None if mx_odd is None else mx_odd[0],
                    "max with even sign": None if mx_even is None else mx_even[0],
                    "max principle": verdict(mx[0], mx_odd, mx_even), "max word": mx[1]})
    except Unsettled:
        out["max principle"] = "unsettled"
    try:
        mn = program(n, H, cost, False, nonzero=True)
        mn_odd = program(n, H, cost, False, parity=1, nonzero=True)
        mn_even = program(n, H, cost, False, parity=0, nonzero=True)
        out.update({"min nonzero weight": mn[0], "min with odd sign": None if mn_odd is None else mn_odd[0],
                    "min nonzero with even sign": None if mn_even is None else mn_even[0],
                    "min principle": verdict(mn[0], mn_odd, mn_even)})
    except Unsettled:
        out["min principle"] = "unsettled"
    if types is not None:
        try:
            ty = program(n, H, cost, True, types=types)
            ty_odd = program(n, H, cost, True, parity=1, types=types)
            ty_even = program(n, H, cost, True, parity=0, types=types)
            out.update({"max holder types": ty[0], "holder-type principle": verdict(ty[0], ty_odd, ty_even)})
        except Unsettled:
            out["holder-type principle"] = "unsettled"
    return out


def round_by_round_max(st):
    """at each round, the most failing pairs among choices consistent with the earlier rounds (first optimum as the
    tie-break); returns the closing sign"""
    decided = {}
    def round_of(p):
        return max(st.dround[p[0]], st.dround[p[1]])
    for t in range(st.T + 1):
        new = [p for p in st.local if round_of(p) == t]
        idx = {p: i for i, p in enumerate(new)}
        cons, rhs = {}, {}
        for p in st.local:
            if round_of(p) > t:
                continue
            a, b = p
            for u in st.holders[a]:
                for v in st.holders[b]:
                    if u == v or st.kround[u] > t or st.kround[v] > t or max(st.kround[u], st.kround[v]) != t:
                        continue
                    key = (min(u, v), max(u, v))
                    if p in idx:
                        cons[key] = cons.get(key, 0) ^ (1 << idx[p])
                    else:
                        rhs[key] = rhs.get(key, 0) ^ decided[p]
                    cons.setdefault(key, 0)
        keys = [k for k in sorted(cons) if cons[k] or rhs.get(k, 0)]
        if any(cons[k] == 0 and rhs.get(k, 0) for k in keys):
            return "dead end"
        keys = [k for k in keys if cons[k]]
        if new:
            res = program(len(new), [cons[k] for k in keys], 0, True, rhs=[rhs.get(k, 0) for k in keys])
            if res is None:
                return "dead end"
            word = res[1]
        else:
            word = 0
        for p, i in idx.items():
            decided[p] = (word >> i) & 1
    gamma = sorted(p for p, v in decided.items() if v)
    return "odd" if st.cost_in_order(gamma, range(len(st.knots))) else "even"


def nullspace(n, H):
    piv = {}
    for r in H:
        for pc, pr in piv.items():
            if (r >> pc) & 1:
                r ^= pr
        if r:
            pc = r.bit_length() - 1
            for k in list(piv):
                if (piv[k] >> pc) & 1:
                    piv[k] ^= r
            piv[pc] = r
    basis = []
    for f in range(n):
        if f in piv:
            continue
        v = 1 << f
        for pc, pr in piv.items():
            if (pr >> f) & 1:
                v |= 1 << pc
        basis.append(v)
    return basis


def enumerate_code(n, H, cost):
    basis = nullspace(n, H)
    assert all(popcount(r & b) % 2 == 0 for r in H for b in basis)
    best_max, best_min = -1, None
    max_signs, min_signs = set(), set()
    max_count = min_count = 0
    word = 0
    for i in range(1, 1 << len(basis)):
        word ^= basis[(i & -i).bit_length() - 1]          # Gray code step
        w = popcount(word)
        s = popcount(word & cost) % 2
        if w > best_max:
            best_max, max_signs, max_count = w, {s}, 1
        elif w == best_max:
            max_signs.add(s)
            max_count += 1
        if best_min is None or w < best_min:
            best_min, min_signs, min_count = w, {s}, 1
        elif w == best_min:
            min_signs.add(s)
            min_count += 1
    if best_max < 0:                                      # only the zero word
        best_max, max_signs = 0, {0}
    v = lambda S: "free" if S == {0, 1} else ("forced odd" if S == {1} else "forced even")
    return {"free directions": len(basis), "max weight": best_max, "max principle": v(max_signs),
            "min nonzero weight": best_min, "min principle": v(min_signs) if best_min is not None else None,
            "maximum words": max_count, "minimum words": min_count}


def doubled_meeting(st):
    """two knots share at least two distinctions"""
    count = {}
    for d, h in st.holders.items():
        if len(h) == 2:
            key = tuple(h)
            count[key] = count.get(key, 0) + 1
    return any(c >= 2 for c in count.values())


def static(knots):
    return lc.Structure([tuple(tuple(k) for k in knots)], [])


def wheel(n):
    """n rim knots, each holding its spoke and the rim distinctions it shares with its two neighbours, and a hub holding
    every spoke"""
    rim = [[i, n + i, n + (i + 1) % n] for i in range(n)]
    return rim + [list(range(n))]


def study_closure(st, args, extra=None):
    n, H, cost = code_of(st)
    t1 = time.time()
    row = dict(extra or {})
    row.update({"decidable pairs": n, "doubled meeting": doubled_meeting(st)})
    row.update(principles(n, H, cost, types=holder_types(st)))
    if "max word" in row:
        word = row.pop("max word")
        gamma = [p for j, p in enumerate(st.local) if (word >> j) & 1]
        order = list(range(len(st.knots)))[::-1]
        row["second-order sign check"] = (st.cost_in_order(gamma, order) == popcount(cost & word) % 2)
    k = len(nullspace(n, H))
    row["free choices"] = k
    if k <= args.enum:
        row["enumerated"] = enumerate_code(n, H, cost)
    row["seconds"] = round(time.time() - t1, 3)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--enum", type=int, default=14)
    ap.add_argument("--out", default=str(HERE))
    args = ap.parse_args()
    out = Path(args.out)
    t0 = time.time()
    source = [json.loads(line) for line in (LC / "results.jsonl").read_text().splitlines()]
    pop = [r for r in source if r["end"] == "closed" and not r.get("closed at round 0") and r["birth choices attain odd"]]
    pop = pop[: args.limit]
    starts = forbid.starts()
    gates = {}
    stages, births, _ = lc.grow(lc.RING3, 4, 40)
    st = lc.Structure(stages, births)
    n, H, cost = code_of(st)
    best = program(n, H, cost, True)
    ring = principles(n, H, cost)
    gates["ring: maximum is the readers' matching, forced odd"] = (
        ring["max principle"] == "forced odd" and ring["max weight"] == 3
        and sorted(pr for j, pr in enumerate(st.local) if (best[1] >> j) & 1) == [(0, 4), (1, 5), (2, 3)])
    rows = []
    with (out / "results.jsonl").open("w") as fh:
        for r in pop:
            stages, births, _ = lc.grow(forbid.supports_of(starts[r["start"]]), 4, 40)
            st = lc.Structure(stages, births)
            row = study_closure(st, args, {"start": r["start"], "closing round": r["closing round"], "knots": r["knots"],
                                           "natural rule keeps a state": r["natural rule: first round without a state"] is None,
                                           "natural rule closing sign": r.get("natural rule closing sign")})
            if r["closing round"] >= 2:
                try:
                    row["round-by-round maximum closing sign"] = round_by_round_max(st)
                except Unsettled:
                    row["round-by-round maximum closing sign"] = "unsettled"
            rows.append(row)
            fh.write(json.dumps(row) + "\n")
    enum_rows = [x for x in rows if "enumerated" in x]
    gates["enumeration agrees with the programs (agree, of)"] = [sum(
        x["enumerated"]["max weight"] == x.get("max weight") and x["enumerated"]["max principle"] == x["max principle"]
        and x["enumerated"]["min nonzero weight"] == x.get("min nonzero weight")
        and x["enumerated"]["min principle"] == x["min principle"] for x in enum_rows), len(enum_rows)]
    gates["second-order sign check holds (of settled maxima)"] = [sum(x.get("second-order sign check", False) for x in rows),
                                                                 sum("second-order sign check" in x for x in rows)]
    nat = [x for x in rows if x["natural rule keeps a state"]]
    gates["natural-rule closures: maximum is every pair, verdict its sign (agree, of)"] = [sum(
        x.get("max weight") == x["decidable pairs"] and x["max principle"] == "forced " + str(x["natural rule closing sign"])
        for x in nat), len(nat)]
    gates["unsettled programs"] = {k: sum(x.get(k) == "unsettled" for x in rows)
                                   for k in ("max principle", "min principle", "holder-type principle")}
    (out / "gates.json").write_text(json.dumps(gates, indent=1) + "\n")
    # P1: the reviewer's hand cases
    by_start = {x["start"]: x for x in rows}
    hand = {}
    for s_, want in ((17, ("forced odd", "forced odd")), (24, ("forced odd", "forced even")), (43, ("forced even", None)),
                     (57, ("forced even", None))):
        x = by_start.get(s_)
        hand[f"start {s_}"] = None if x is None else {
            "max principle": x["max principle"], "min principle": x["min principle"], "max weight": x.get("max weight"),
            "min nonzero weight": x.get("min nonzero weight"), "natural rule keeps a state": x["natural rule keeps a state"],
            "as predicted": x["max principle"] == want[0] and (want[1] is None or x["min principle"] == want[1])}
    hand["start 24: weights 3 and 2"] = by_start.get(24) is not None and (by_start[24].get("max weight"),
                                                                          by_start[24].get("min nonzero weight")) == (3, 2)
    hand["start 57: natural rule keeps a state"] = by_start.get(57) is not None and by_start[57]["natural rule keeps a state"]
    for nrim in (4, 5):
        S = static(wheel(nrim))
        n_, H_, c_ = code_of(S)
        e = enumerate_code(n_, H_, c_)
        hand[f"wheel of {nrim}"] = {"max weight": e["max weight"], "max principle": e["max principle"],
                                    "maximum words": e["maximum words"], "min nonzero weight": e["min nonzero weight"],
                                    "min principle": e["min principle"], "minimum words": e["minimum words"]}
    two = [x for x in rows if x.get("min nonzero weight") == 2]
    hand["control with 2 failing pairs: doubled meeting and forced even (agree, of)"] = [
        sum(x["doubled meeting"] and x["min principle"] == "forced even" for x in two), len(two)]
    # second weighting: the 173 census types, one vote per type
    census = json.loads(lc.CENSUS.read_text())
    types_rows = []
    for q, tp in enumerate(census):
        ends = [tuple(e) for e in tp["sharing"]]
        nk = 1 + max(v for e in ends for v in e)
        S = static([tuple(i for i, e in enumerate(ends) if u in e) for u in range(nk)])
        if not lc.odd_attainable(S, S.local):
            types_rows.append({"type": q, "odd attainable": False})
            continue
        tr = study_closure(S, args, {"type": q, "odd attainable": True, "knots": nk})
        types_rows.append(tr)
    with (out / "census_types.jsonl").open("w") as fh:
        for tr in types_rows:
            fh.write(json.dumps(tr) + "\n")
    V = ("forced odd", "forced even", "free", "unsettled")
    s = {"closures": len(rows)}
    for key in ("max principle", "min principle", "holder-type principle"):
        s[key] = {v: sum(x.get(key) == v for x in rows) for v in V}
    for label, sel in (("natural rule loses its state", [x for x in rows if not x["natural rule keeps a state"]]),
                       ("natural rule keeps a state", nat)):
        s[label + ": closures"] = len(sel)
        s[label + ": max principle"] = {v: sum(x.get("max principle") == v for x in sel) for v in V}
    s["by closing round: max principle"] = {str(rd): {v: sum(x["max principle"] == v for x in rows if x["closing round"] == rd)
                                                      for v in V} for rd in sorted({x["closing round"] for x in rows})}
    forced = [x for x in rows if x["max principle"] in ("forced odd", "forced even")]
    for other in ("min principle", "holder-type principle"):
        both = [x for x in forced if x.get(other) in ("forced odd", "forced even")]
        s[f"max and {other} both force a sign"] = len(both)
        s[f"max and {other} force different signs"] = sum(x["max principle"] != x[other] for x in both)
    later = [x for x in rows if x["closing round"] >= 2]
    s["round by round at later closures (odd, even, dead end, unsettled)"] = [
        sum(x.get("round-by-round maximum closing sign") == v for x in later) for v in ("odd", "even", "dead end", "unsettled")]
    s["round by round agrees with a forced maximum (agree, of)"] = [sum(
        x.get("round-by-round maximum closing sign") == x["max principle"].split()[-1] for x in later
        if x["max principle"] in ("forced odd", "forced even")),
        sum(x["max principle"] in ("forced odd", "forced even") for x in later)]
    sizes = [x["enumerated"]["maximum words"] for x in enum_rows]
    s["maximum words where enumerated (1, 2, 3 or more)"] = [sum(z == 1 for z in sizes), sum(z == 2 for z in sizes),
                                                             sum(z >= 3 for z in sizes)]
    s["P2 forced by the maximum"] = len(forced)
    tset = [tr for tr in types_rows if tr.get("odd attainable")]
    s["census types (one vote per type): odd attainable"] = len(tset)
    for key in ("max principle", "min principle", "holder-type principle"):
        s["census types: " + key] = {v: sum(tr.get(key) == v for tr in tset) for v in V}
    s["hand cases"] = hand
    s["seconds"] = round(time.time() - t0, 1)
    s["peak KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    (out / "summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print(json.dumps({"gates": gates, "summary": s}, indent=1))


if __name__ == "__main__":
    main()
