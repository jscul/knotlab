"""Lane B (MUTUAL-SELECTION-20261031-001B): parity and the clauses, with signs, on cubic systems.

1. Parity: a signed system with law "even" (or "odd") is a linear system A x = b over GF(2), A the line-point incidence matrix. Its
   unsolvable signings exist exactly when A is singular, and then they are the right-hand sides outside the column space; the census
   graphs of lane C (n <= 7) confirm the count 2^n - 2^rank per graph (signings modulo point switching act on b only through line sums).
   The coupling family f_lam = [1, lam, 1, lam] (weight 1 on even views, lam on odd ones) has Hadamard transform supported on {000, 111}
   for every lam: a generalized equality, affine, polynomial on every graph. So parity selects nothing beyond the universally easy.
2. Clauses (three literals, each variable in exactly three clauses): every instance is satisfiable (Tovey 1984): a cubic bipartite graph
   has a perfect matching (Hall), so each clause owns a variable and sets it. Checked on every signing of the census graphs (n <= 6).
Run: .venv/bin/python -B parity_clause.py [--write]"""
import itertools
import json
import sys
import time
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
T0 = time.time()
OUT = {}
census = json.loads((ROOT / "research/MUTUAL-SELECTION-20261031-001C/census.json").read_text())


def gf2_rank(rows):
    piv = []
    for r in rows:
        for p in piv:
            r = min(r, r ^ p)
        if r:
            piv.append(r)
    return len(piv)


res = {}
for n_str, block in census.items():
    n = int(n_str)
    if n > 7:
        continue
    for gi, row in enumerate(block["rows"]):
        lines = row["lines"]
        rows = [sum(1 << p for p in l) for l in lines]
        rank = gf2_rank(rows)
        # unsolvable right-hand sides b of A x = b (b in GF(2)^n): count directly
        unsolv = 0
        for b in range(1 << n):
            ok = False
            for x in range(1 << n):
                if all(bin(rows[i] & x).count("1") % 2 == (b >> i) & 1 for i in range(n)):
                    ok = True
                    break
            unsolv += not ok
        res[f"n = {n}, graph {gi}"] = {"GF(2) rank": rank, "unsolvable right-hand sides": unsolv, "predicted 2^n - 2^rank": 2 ** n - 2 ** rank}
OUT["1 parity: unsolvable right-hand sides = 2^n - 2^rank"] = res
lam = sp.Symbol('lam')
fhat = []
for y in itertools.product((0, 1), repeat=3):
    fhat.append(sp.factor(sum((-1) ** (sum(a * b for a, b in zip(s, y))) * (1 if sum(s) % 2 == 0 else lam) for s in itertools.product((0, 1), repeat=3))))
OUT["1 parity family [1, lam, 1, lam]: Hadamard transform by y"] = {"".join(map(str, y)): str(v) for y, v in zip(itertools.product((0, 1), repeat=3), fhat)}
support_ok = all(v == 0 for y, v in zip(itertools.product((0, 1), repeat=3), fhat) if y not in ((0, 0, 0), (1, 1, 1)))
# 2. clauses
sat_all, checked = True, 0
for n_str, block in census.items():
    n = int(n_str)
    if n > 6:
        continue
    for row in block["rows"]:
        lines = row["lines"]
        for signs in itertools.product((0, 1), repeat=3 * n):
            checked += 1
            ok = any(all(any(((x >> p) & 1) ^ signs[3 * i + k] for k, p in enumerate(l)) for i, l in enumerate(lines)) for x in range(1 << n))
            if not ok:
                sat_all = False
                break
OUT["2 clauses: every signing of every census graph with n <= 6 is satisfiable"] = {"signings checked": checked, "all satisfiable": sat_all}
ok = all(v["unsolvable right-hand sides"] == v["predicted 2^n - 2^rank"] for v in res.values()) and support_ok and sat_all
OUT["seconds"] = round(time.time() - T0, 1)
print(json.dumps(OUT, indent=1)[:4000])
print("ALL OK" if ok else "FAIL")
if "--write" in sys.argv:
    (HERE / "results.json").write_text(json.dumps(OUT, indent=1) + "\n")
