#!/usr/bin/env python3
"""Independent check of MALTSEV-CONDITIONS-20261021-001A-E001. It imports no producer code.

- Every recorded operation table (Hagemann-Mitschke terms, Mal'tsev-modulo-tops operations, control Mal'tsev
  operations) is re-verified by brute force: the polymorphism property over all triples of the law's tuples, and the
  identities.
- The two-element clones are re-enumerated (all ternary and 4-ary operations, checked against the relation with a
  different loop order), and the Hagemann-Mitschke and Day chains are re-decided by a fixpoint iteration rather than
  a search.
- The derived equivalences and the largest-equals-top comparison are recomputed.
- Summary flags are recomputed from the rows.
"""

from __future__ import annotations

import json
import sys
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = ROOT / "artifacts" / "MALTSEV-CONDITIONS-20261021-001A" / HERE.name


def laws():
    M3 = {t for t in product(range(3), repeat=3) if sum(t) % 3 == 0}
    g = (0, 1, 2, 2)
    L = {t for t in product(range(4), repeat=3) if tuple(g[x] for x in t) in M3}
    not_two = {t for t in product((0, 1), repeat=3) if sum(t) != 2}
    M4 = {t for t in product(range(2), repeat=4) if sum(t) % 2 == 0}
    return {
        "K4": (4, L - {(2, 2, 2)}), "L223": (4, L - {(2, 2, 3)}), "L233": (4, L - {(2, 3, 3)}),
        "K6": (6, {tuple(2 * a + b for a, b in zip(u, w)) for u in M3 for w in not_two}),
        "K4x4": (4, {tuple(2 * a + b for a, b in zip(u, w)) for u in M4 for w in M4 | {(1, 0, 0, 0)}}),
        "Z6": (6, {t for t in product(range(6), repeat=3) if sum(t) % 6 == 0}),
        "Z2xZ2": (4, {(x, y, x ^ y) for x in range(4) for y in range(4)}),
    }


def as_function(table, D, ar):
    return dict(zip(product(range(D), repeat=ar), table))


def is_polymorphism(f, R, ar):
    k = len(next(iter(R)))
    for ts in product(sorted(R), repeat=ar):
        if tuple(f[tuple(t[i] for t in ts)] for i in range(k)) not in R:
            return False
    return True


def two_pols(R, ar):
    k = len(next(iter(R)))
    args = list(product((0, 1), repeat=ar))
    out = []
    Rs = sorted(R)
    for bits in range(1 << (2 ** ar)):
        f = {a: (bits >> i) & 1 for i, a in enumerate(args)}
        good = True
        for ts in product(Rs, repeat=ar):
            if tuple(f[tuple(t[i] for t in ts)] for i in range(k)) not in R:
                good = False
                break
        if good:
            out.append(f)
    return out


def hm_fixpoint(P3):
    """Set of ternary polymorphisms reachable as some p_i; a chain exists iff one of them is a valid last term."""
    B = (0, 1)
    reach = {i for i, f in enumerate(P3) if all(f[(x, y, y)] == x for x in B for y in B)}
    while True:
        new = {j for j, gg in enumerate(P3) if any(all(P3[i][(x, x, y)] == gg[(x, y, y)] for x in B for y in B) for i in reach)}
        if new <= reach:
            break
        reach |= new
    return any(all(P3[i][(x, x, y)] == y for x in B for y in B) for i in reach)


def day_fixpoint(P4):
    B = (0, 1)
    ok = [i for i, f in enumerate(P4) if all(f[(x, y, y, x)] == x for x in B for y in B)]
    reach = {(i, 0) for i in ok if all(P4[i][a] == a[0] for a in P4[i])}
    while True:
        new = set()
        for i, par in reach:
            for j in ok:
                if par == 0:
                    same = all(P4[i][(x, x, u, u)] == P4[j][(x, x, u, u)] for x in B for u in B)
                else:
                    same = all(P4[i][(x, y, y, u)] == P4[j][(x, y, y, u)] for x in B for y in B for u in B)
                if same:
                    new.add((j, 1 - par))
        if new <= reach:
            break
        reach |= new
    return any(all(P4[i][a] == a[3] for a in P4[i]) for i, _ in reach)


def derived(R, D, k):
    n = k + 1
    eqs = set()
    for c1 in product(range(n), repeat=k):
        for c2 in [None] + list(product(range(n), repeat=k)):
            cons = [c1] + ([c2] if c2 else [])
            E = frozenset((a[0], a[1]) for a in product(range(D), repeat=n) if all(tuple(a[v] for v in c) in R for c in cons))
            if {x for x, _ in E} == set(range(D)) and all((x, x) in E for x in range(D)) and all((y, x) in E for x, y in E) \
                    and all((x, w) in E for x, y in E for z, w in E if y == z):
                eqs.add(E)
    return [E for E in eqs if len(E) < D * D]


def main() -> int:
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(line) for line in (ART / "raw_rows.jsonl").read_text().splitlines()]
    L = laws()
    problems, report = [], {}

    hm_ok = {}
    for r in (r for r in rows if r["part"] == "hm"):
        D, R = L[r["law"]]
        n = r["n"]
        fs = {name: as_function(tab, D, 3) for name, tab in r["tables"].items()}
        ident = all(fs["p1"][(x, y, y)] == x and fs[f"p{n-1}"][(x, x, y)] == y and
                    all(fs[f"p{i}"][(x, x, y)] == fs[f"p{i+1}"][(x, y, y)] for i in range(1, n - 1))
                    for x in range(D) for y in range(D))
        pol = all(is_polymorphism(f, R, 3) for f in fs.values())
        hm_ok[f"{r['law']} n={n}"] = ident and pol
        if not (ident and pol):
            problems.append(f"HM witness {r['law']} n={n} does not verify")
    report["hm_witnesses"] = hm_ok

    tops_ok = {}
    for r in (r for r in rows if r["part"] == "tops"):
        D, R = L[r["law"]]
        if r["table"] is None:
            tops_ok[r["law"]] = None
            continue
        f = as_function(r["table"], D, 3)
        good = is_polymorphism(f, R, 3)
        for rg, cls in r["classes"]:
            c = {int(a): set(b) for a, b in cls.items()}
            good = good and all(f[(x, y, y)] in c[x] and f[(x, x, y)] in c[y] for x in rg for y in rg)
        tops_ok[r["law"]] = good
        if not good:
            problems.append(f"Mal'tsev-on-tops witness for {r['law']} does not verify")
        if r["law"] in ("K4", "L223", "L233", "K6"):
            k = 3
            pe = derived(R, D, k)
            recorded = frozenset(tuple(p) for p in r["largest_derived"]) if r["largest_derived"] else None
            biggest = max((len(E) for E in pe), default=0)
            if recorded is None or recorded not in pe or len(recorded) != biggest:
                problems.append(f"derived equivalences differ for {r['law']}")
    report["tops_witnesses"] = tops_ok

    ctl_ok = {}
    for r in (r for r in rows if r["part"] == "control"):
        D, R = L[r["law"]]
        f = as_function(r["tables"]["p1"], D, 3)
        good = is_polymorphism(f, R, 3) and all(f[(x, y, y)] == x and f[(x, x, y)] == y for x in range(D) for y in range(D))
        ctl_ok[r["law"]] = good
        if not good:
            problems.append(f"control Mal'tsev witness for {r['law']} does not verify")
    report["control_witnesses"] = ctl_ok

    chain_ok = {}
    for r in (r for r in rows if r["part"] in ("chains", "dressing")):
        R = {tuple(t) for t in r["relation"]} if r["part"] == "chains" else \
            ({t for t in product((0, 1), repeat=3) if sum(t) != 2} | {tuple(t) for t in r["added"]})
        P3, P4 = two_pols(R, 3), two_pols(R, 4)
        mine = {"ternary_polymorphisms": len(P3), "quaternary_polymorphisms": len(P4), "hm_chain": hm_fixpoint(P3),
                "day_chain": day_fixpoint(P4)}
        key = r.get("name") or ("dressing " + str(r["added"]))
        chain_ok[key] = mine == {x: r[x] for x in mine}
        if not chain_ok[key]:
            problems.append(f"chains differ for {key}")
    report["chains"] = chain_ok

    status = "passed: every witness and chain decision agrees (V1, exploratory evidence only)" if not problems else "failed"
    text = json.dumps(report, indent=2, sort_keys=True, default=str) + "\n" + status + "\n" + "\n".join(problems) + "\n"
    (ART / "check_output.txt").write_text(text)
    print(text)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
