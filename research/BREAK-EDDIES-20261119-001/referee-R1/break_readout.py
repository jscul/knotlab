"""Readout of the referee's BREAK-EDDIES check (runs/referee-break-eddies, from job_break.py), against the study's run records
(runs/break-eddies, runs/break-eddies-ref) read as data.

Recurrences: the referee's own exact Berlekamp-Massey over the rationals, from each start offset t0 = 0..13, taking the least
order L whose recurrence holds on every remaining term with at least 2L + 4 terms after t0; its characteristic polynomial is
factored over Q (sympy), and the rate is its largest real root.  The catalogue's family (the study's posthoc.py range: W = y^L
(1 + y)^a (1 + y + y^2)^b (1 + y(1 + y)^2)^c / (1 - y)^d, L = 1..7, a = 0..4, b, c, d = 0..1, two ways round or more) is
listed exactly: every member whose 1 - W has the rate's minimal polynomial as a factor (exact division over Q), so ties in the
rate are seen, not hidden by taking the first.

  ../../../.venv/bin/python -B break_readout.py > referee_break.json
"""
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[3]
x, y = sp.symbols("x y")


def bm(seq):
    """Berlekamp-Massey over Q: the connection polynomial C (C[0] = 1) and its length L."""
    s = [Fraction(v) for v in seq]
    C, B = [Fraction(1)], [Fraction(1)]
    L, m, b = 0, 1, Fraction(1)
    for n in range(len(s)):
        d = s[n] + sum(C[i] * s[n - i] for i in range(1, L + 1))
        if d == 0:
            m += 1
            continue
        T = list(C)
        coef = d / b
        C = C + [Fraction(0)] * max(0, len(B) + m - len(C))
        for i, v in enumerate(B):
            C[i + m] -= coef * v
        if 2 * L <= n:
            L, B, b, m = n + 1 - L, T, d, 1
        else:
            m += 1
    return C[:L + 1] + [Fraction(0)] * max(0, L + 1 - len(C)), L


def recurrence(c, spare=4):
    best = None
    for t0 in range(0, 14):
        tail = c[t0:]
        if len(tail) < 8:
            break
        C, L = bm(tail)
        if len(tail) < 2 * L + spare or L == 0:
            continue
        holds = all(sum(C[i] * tail[n - i] for i in range(L + 1)) == 0 for n in range(L, len(tail)))
        if holds and (best is None or L < best[1]):
            best = (C, L, t0)
    return best


def family():
    rows = []
    for L, a, b, c, d in itertools.product(range(1, 8), range(5), range(2), range(2), range(2)):
        if not d and (2 ** a) * (3 ** b) * (5 ** c) < 2:
            continue
        num = y ** L * (1 + y) ** a * (1 + y + y ** 2) ** b * (1 + y * (1 + y) ** 2) ** c
        W = num / (1 - y) ** d
        p = sp.Poly(sp.expand(sp.numer(sp.together(1 - W)).subs(y, 1 / x) * x ** (L + a + 2 * b + 3 * c + d)), x)
        name = f"y^{L}" + (f" (1+y)^{a}" if a else "") + (" (1+y+y^2)" if b else "") + (" (1+y(1+y)^2)" if c else "") + \
            (" / (1-y)" if d else "")
        rows.append((name, p))
    return rows


FAM = family()


def read(c):
    rec = recurrence(c)
    if rec is None:
        return None
    C, L, t0 = rec
    P = sp.Poly(sum(sp.Rational(C[i].numerator, C[i].denominator) * x ** (L - i) for i in range(L + 1)), x)
    facs = [f for f, _ in sp.factor_list(P.as_expr())[1]]
    best = None
    for f in facs:
        roots = [complex(r) for r in sp.Poly(f, x).nroots(n=30)]
        real = [r.real for r in roots if abs(r.imag) < 1e-12]
        if real and (best is None or max(real) > best[0]):
            best = (max(real), sp.Poly(f, x))
    if best is None:
        return {"order": L, "from": t0}
    members = [name for name, p in FAM if sp.rem(p, best[1]) == 0]
    # every factor other than x - 1 (an endless chain's 1 - y) must divide 1 - W in the one-loop transfer form
    need = [sp.Poly(f, x) for f in facs if sp.Poly(f, x) != sp.Poly(x - 1, x)]
    full = [name for name, p in FAM if all(sp.rem(p, f) == 0 for f in need)]
    return {"order": L, "from": t0, "rate": round(best[0], 9), "factor": str(best[1].as_expr()),
            "factors": [str(f) for f in facs], "family members with this factor": members,
            "family members whose 1 - W holds every factor": full}


def main():
    mine = {}
    for line in open(ROOT / "runs/referee-break-eddies/results.jsonl"):
        r = json.loads(line)
        mine[r["case"]] = r
    theirs = {}
    for run in ("break-eddies", "break-eddies-ref"):
        for line in open(ROOT / "runs" / run / "results.jsonl"):
            r = json.loads(line)
            theirs[r["case"]] = r
    rows = {}
    for case in sorted(mine):
        r = mine[case]
        if r["status"] != "ok":
            rows[case] = {"status": r["status"]}
            continue
        m = r["result"]
        t = theirs.get(case, {}).get("result") or {}
        tc = t.get("counts") or []
        k = min(len(tc), len(m["counts"]))
        rd = read(m["counts"]) if len(m["counts"]) >= 12 else None
        trec = t.get("recurrence") or {}
        rows[case] = {
            "sizes": m["start"]["sizes"], "edges": m["start"]["edges"], "rounds (referee)": len(m["counts"]) - 1, "stop (referee)": m["stop"],
            "rounds (study)": len(tc) - 1 if tc else None, "stop (study)": t.get("stop"),
            "counts equal on common rounds": tc[:k] == m["counts"][:k] if tc else None, "common rounds": k - 1,
            "largest group equal on common rounds": (t.get("group") or [])[:k - 1] == m["group"][:k - 1] if t else None,
            "round-1 group (referee)": m["group"][0] if m["group"] else None,
            "group (referee)": m["group"], "last counts (referee)": m["counts"][-4:],
            "recurrence (referee)": rd, "study factor": trec.get("factor"), "study W (frozen)": trec.get("W"),
            "stage test": m["stage"]}
    rat = {c: v for c, v in rows.items() if v.get("recurrence (referee)") and v["recurrence (referee)"].get("rate")}
    smallest = {c: v["recurrence (referee)"]["family members with this factor"][0] if
                v["recurrence (referee)"]["family members with this factor"] else None for c, v in rat.items()}
    st = [v["stage test"] for v in rows.values() if isinstance(v.get("stage test"), dict)]
    full = {c: (v["recurrence (referee)"]["family members whose 1 - W holds every factor"] or [None])[0] for c, v in rat.items()}
    short = [c for c in rat if full[c] and full[c].startswith(("y^1", "y^2", "y^3"))]
    def loop(name):
        return int(name.split()[0][2:]) if name else None
    b7 = []
    for a in rat:
        for b in rat:
            if a != b and rows[a]["edges"] == rows[b]["edges"] and full[a] and full[b]:
                d = [q - p for p, q in zip(rows[a]["sizes"], rows[b]["sizes"])]
                if sorted(d) == [0] * (len(d) - 1) + [1]:
                    b7.append(loop(full[b]) <= loop(full[a]))
    summary = {
        "cases": len(rows), "not ok": sorted(c for c, v in rows.items() if "status" in v),
        "counts equal to the study's on every common round": sum(1 for v in rows.values() if v.get("counts equal on common rounds")),
        "largest groups equal on every common round": sum(1 for v in rows.values() if v.get("largest group equal on common rounds")),
        "rational (referee's recurrence)": len(rat),
        "rational with a family member": sum(1 for c in rat if smallest[c]),
        "same factor as the study's": sum(1 for c, v in rat.items() if v["study factor"] and
                                          sp.simplify(sp.sympify(v["study factor"]) - sp.sympify(v["recurrence (referee)"]["factor"])) == 0),
        "smallest family member": dict(Counter(smallest.values())),
        "family members sharing the factor (the ambiguity), by smallest member": {
            k: sorted({tuple(rat[c]["recurrence (referee)"]["family members with this factor"]) for c in rat if smallest[c] == k})
            for k in set(smallest.values())},
        "loop of at most 3 steps by the smallest member: starts, with a round-1 group of three": [
            sum(1 for c in rat if smallest[c] and smallest[c].startswith(("y^1", "y^2", "y^3"))),
            sum(1 for c in rat if smallest[c] and smallest[c].startswith(("y^1", "y^2", "y^3")) and (rows[c]["round-1 group (referee)"] or 0) >= 3)],
        "smallest family member whose 1 - W holds every factor of the minimal recurrence": dict(Counter(map(str, full.values()))),
        "smallest member (dominant factor) -> smallest member (every factor)": {f"{a} -> {b}": n for (a, b), n in
                                                                               Counter((smallest[c], full[c]) for c in rat).items()},
        "loop of at most 3 steps by every factor: starts, with a round-1 group of three": [
            len(short), sum(1 for c in short if (rows[c]["round-1 group (referee)"] or 0) >= 3)],
        "B7 recounted on the every-factor reading: pairs, held": [len(b7), sum(b7)],
        "frozen W with lowest power at most 3 (the study's B6 set)": sum(
            1 for v in rows.values() if v.get("study W (frozen)") and next(k for k, w in enumerate(v["study W (frozen)"]) if w) <= 3),
        "stage test: (s, equal) counts": dict(Counter(f"s={s}: {d[s]['equal'] if isinstance(d[s], dict) else d[s]}"
                                                     for d in st for s in d)),
    }
    print(json.dumps({"summary": summary, "rows": rows}, indent=1, default=str))


if __name__ == "__main__":
    main()
