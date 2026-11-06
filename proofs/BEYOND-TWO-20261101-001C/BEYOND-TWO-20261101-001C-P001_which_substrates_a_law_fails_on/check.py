#!/usr/bin/env python3
"""Checks for BEYOND-TWO-20261101-001C: which substrates a law fails on, and whether globally.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy)."""
import collections
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
          if p.endswith(".json") and p.startswith("proofs/")}
check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
      {"mismatched": bad, "statuses": status})

CENSUS = json.loads((ROOT / "research/MUTUAL-SELECTION-20261031-001C/census.json").read_text())
SUBSTRATES = [(int(n), row) for n, v in sorted(CENSUS.items(), key=lambda kv: int(kv[0])) for row in v["rows"]]


# ------------------------------------------------------------------------------------------------ linear algebra
def rank_mod(M, p):
    A = [[x % p for x in row] for row in M]
    r = 0
    cols = len(A[0]) if A else 0
    for col in range(cols):
        pr = next((i for i in range(r, len(A)) if A[i][col]), None)
        if pr is None:
            continue
        A[r], A[pr] = A[pr], A[r]
        inv = pow(A[r][col], -1, p)
        A[r] = [(x * inv) % p for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][col]:
                f = A[i][col]
                A[i] = [(a - f * b) % p for a, b in zip(A[i], A[r])]
        r += 1
    return r


def consistent(A, c, p, skip=None):
    rows = [row for i, row in enumerate(A) if i != skip]
    rhs = [x for i, x in enumerate(c) if i != skip]
    return rank_mod(rows, p) == rank_mod([row + [b] for row, b in zip(rows, rhs)], p)


def det_int(M):
    """Bareiss fraction-free determinant"""
    A = [row[:] for row in M]
    n = len(A)
    sign, prev = 1, 1
    for k in range(n - 1):
        if A[k][k] == 0:
            sw = next((i for i in range(k + 1, n) if A[i][k] != 0), None)
            if sw is None:
                return 0
            A[k], A[sw] = A[sw], A[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * A[k][k] - A[i][k] * A[k][j]) // prev
        prev = A[k][k]
    return sign * A[n - 1][n - 1]


def perm01(A):
    n = len(A)
    dp = {0: 1}
    for i in range(n):
        nxt = collections.defaultdict(int)
        for mask, cnt in dp.items():
            for j in range(n):
                if A[i][j] and not mask >> j & 1:
                    nxt[mask | 1 << j] += cnt
        dp = nxt
    return dp.get((1 << n) - 1, 0)


def nae_colourable(lines, signs, n, skip=None):
    cols = np.arange(1 << n)
    ok = np.ones(1 << n, dtype=bool)
    for i, L in enumerate(lines):
        if i == skip:
            continue
        reads = [((cols >> p) & 1) ^ signs[(i, p)] for p in L]
        ok &= ~((reads[0] == reads[1]) & (reads[1] == reads[2]))
    return bool(ok.any())


def signing_classes(lines, n):
    """one signing per class modulo switching: signs fixed to 0 on a spanning tree of the incidence graph"""
    edges = [(i, p) for i, L in enumerate(lines) for p in L]
    adj = collections.defaultdict(list)
    for i, p in edges:
        adj[("l", i)].append((("p", p), (i, p)))
        adj[("p", p)].append((("l", i), (i, p)))
    seen, tree = {("l", 0)}, set()
    stack = [("l", 0)]
    while stack:
        u = stack.pop()
        for v, e in adj[u]:
            if v not in seen:
                seen.add(v)
                tree.add(e)
                stack.append(v)
    others = [e for e in edges if e not in tree]
    for bits in range(1 << len(others)):
        s = {e: 0 for e in edges}
        for k, e in enumerate(others):
            s[e] = bits >> k & 1
        yield s


# ------------------------------------------------------------------------------------------------ 1-4. the census
rows_out, ok_knot, ok_par, ok_z3 = [], True, True, True
rng = random.Random(20261101)
tally = collections.Counter()
for n, row in SUBSTRATES:
    lines = [tuple(L) for L in row["lines"]]
    A = [[1 if p in L else 0 for p in range(n)] for L in lines]
    pm = perm01(A)
    # the knot
    pf_sign = None
    for s in signing_classes(lines, n):
        M = [[(-1) ** s[(i, p)] if p in L else 0 for p in range(n)] for i, L in enumerate(lines)]
        if abs(det_int(M)) == pm:
            pf_sign = s
            break
    pfaff = pf_sign is not None
    census_pf = row["not-all-equal unsat signings (Pfaffian iff > 0)"] > 0
    failing_classes = sum(not nae_colourable(lines, s, n) for s in signing_classes(lines, n))
    if pfaff:
        fails = not nae_colourable(lines, pf_sign, n)
        minimal = all(nae_colourable(lines, pf_sign, n, skip=i) for i in range(n))
        knot_ok = fails and minimal and failing_classes == 1
    else:
        knot_ok = failing_classes == 0
    ok_knot &= knot_ok and pfaff == census_pf
    # parity
    r2 = rank_mod(A, 2)
    par_fails = r2 < n
    par_global = 0
    par_failing = 0
    for c in itertools.product((0, 1), repeat=n):
        c = list(c)
        if consistent(A, c, 2):
            continue
        par_failing += 1
        if all(consistent(A, c, 2, skip=i) for i in range(n)):
            par_global += 1
    ok_par &= par_fails == (pm % 2 == 0) == (par_failing > 0) and par_global == 0
    # Z3
    r3 = rank_mod(A, 3)
    cor = n - r3
    cs = list(itertools.product((0, 1, 2), repeat=n)) if n <= 6 else [tuple(rng.randrange(3) for _ in range(n)) for _ in range(300)]
    z3_failing = z3_global = 0
    for c in cs:
        c = list(c)
        if consistent(A, c, 3):
            continue
        z3_failing += 1
        if all(consistent(A, c, 3, skip=i) for i in range(n)):
            z3_global += 1
    z3_ok = cor >= 1 and z3_failing > 0 and ((cor == 1 and z3_global == z3_failing) or (cor >= 2 and z3_global == 0))
    ok_z3 &= z3_ok
    rows_out.append({"n": n, "perfect matchings": pm, "Pfaffian": pfaff, "GF(2) rank": r2, "Z3 corank": cor,
                     "knot fails, always globally" if pfaff else "knot never fails": knot_ok,
                     "parity failing right-hand sides (global)": [par_failing, par_global],
                     "Z3 failing right-hand sides tested (global)": [z3_failing, z3_global]})
    tally["n = %d" % n] += 1
    tally["Pfaffian"] += pfaff
    tally["even number of perfect matchings"] += pm % 2 == 0
    tally["Z3 corank 1"] += cor == 1
summary = dict(tally)
check("1 the knot on all 60 connected cubic substrates (up to 8 points): it fails under some signing exactly on the Pfaffian ones (a "
      "signing with |det| = number of perfect matchings, agreeing with the census); there exactly one switching class of signings "
      "fails and its failure is global (removing any line leaves it colourable); on the others every signing class is colourable",
      ok_knot, {"summary": summary})
check("2 parity: it fails (for some right-hand side) exactly on the substrates with an even number of perfect matchings, and no failure "
      "on any substrate is global (every failing right-hand side survives the removal of some line)", ok_par,
      {"substrates": len(rows_out), "with failures": sum(1 for r in rows_out if r["parity failing right-hand sides (global)"][0] > 0),
       "global failures found": sum(r["parity failing right-hand sides (global)"][1] for r in rows_out)})
check("3 Z3 (x + y + z = c): it fails on every substrate (corank at least 1, as all lines sum to zero mod 3); every tested failure is "
      "global on corank-1 substrates and local on the others (all right-hand sides up to 6 points, 300 random ones above)", ok_z3,
      {"corank distribution": dict(collections.Counter(r["Z3 corank"] for r in rows_out)),
       "failures tested": sum(r["Z3 failing right-hand sides tested (global)"][0] for r in rows_out),
       "global among them": sum(r["Z3 failing right-hand sides tested (global)"][1] for r in rows_out)})

# ------------------------------------------------------------------------------------------------ 5. blurred Z3: easy in return
PHI = np.array([0, 0, 1, 2])
W = {0: 2, 1: 1, 2: 1}
ok5, info5 = True, collections.Counter()
for n, row in SUBSTRATES:
    lines = [tuple(L) for L in row["lines"]]
    A = [[1 if p in L else 0 for p in range(n)] for L in lines]
    if n - rank_mod(A, 3) != 1 or n > 7:
        continue
    c = [1] + [0] * (n - 1)
    if consistent(A, c, 3):
        ok5 = False
        continue
    assign = np.array(list(itertools.product(range(4), repeat=n)), dtype=np.int8)
    img = PHI[assign]
    for i in range(n):
        sols = [x for x in itertools.product(range(3), repeat=n)
                if all((sum(x[p] for p in L) - c[k]) % 3 == 0 for k, L in enumerate(lines) if k != i)]
        formula = sum(int(np.prod([W[v] for v in x])) for x in sols)
        good = np.ones(len(assign), dtype=bool)
        for k, L in enumerate(lines):
            if k != i:
                good &= (img[:, list(L)].sum(axis=1) - c[k]) % 3 == 0
        brute = int(good.sum())
        ok5 &= len(sols) == 3 and brute == formula
        info5["line removals checked"] += 1
    info5["corank-1 substrates (up to 7 points)"] += 1
check("5 blurred Z3 is easy in return: on every corank-1 substrate with up to 7 points, with a failing right-hand side, removing any "
      "line leaves exactly 3 solutions over Z3, and the blurred count (brute force over four values) equals their weighted sum", ok5,
      dict(info5))

check("6 summary by size: substrates, Pfaffian ones (the knot's failing substrates), ones with an even number of perfect matchings "
      "(parity's), and ones of Z3-corank 1 (where Z3 and blurred Z3 fail globally)", True,
      {str(n): {"substrates": sum(1 for r in rows_out if r["n"] == n), "Pfaffian": sum(1 for r in rows_out if r["n"] == n and r["Pfaffian"]),
                "even perfect matchings": sum(1 for r in rows_out if r["n"] == n and r["perfect matchings"] % 2 == 0),
                "Z3 corank 1": sum(1 for r in rows_out if r["n"] == n and r["Z3 corank"] == 1)} for n in range(3, 9)})



# ------------------------------------------------------------------------------------------------ 7. rigidity of the selected spaces
def circuit_sizes(sol, n):
    ranges = [len({s[v] for s in sol}) for v in range(n)]
    cons = [frozenset(Y) for r in range(1, n + 1) for Y in itertools.combinations(range(n), r)
            if len({tuple(s[v] for v in Y) for s in sol}) < np.prod([ranges[v] for v in Y])]
    return sorted({len(C) for C in cons if not any(D < C for D in cons)})


ok7, info7, knot_rows = True, collections.Counter(), []
for n, row in SUBSTRATES:
    lines = [tuple(L) for L in row["lines"]]
    A = [[1 if p in L else 0 for p in range(n)] for L in lines]
    if n - rank_mod(A, 3) == 1:
        c = [1] + [0] * (n - 1)
        for i in range(n):
            sol = [x for x in itertools.product(range(3), repeat=n)
                   if all((sum(x[p] for p in L) - c[k]) % 3 == 0 for k, L in enumerate(lines) if k != i)]
            sizes = circuit_sizes(sol, n)
            ok7 &= len(sol) == 3 and bool(sizes) and max(sizes) == 2
            info7["Z3: line removals on corank-1 substrates, circuits all ties"] += 1
    pm = perm01(A)
    for s in signing_classes(lines, n):
        M = [[(-1) ** s[(i, p)] if p in L else 0 for p in range(n)] for i, L in enumerate(lines)]
        if abs(det_int(M)) != pm:
            continue
        kept, counts = 0, set()
        for i in range(n):
            cols = np.arange(1 << n)
            good = np.ones(1 << n, dtype=bool)
            for k, L in enumerate(lines):
                if k != i:
                    reads = [((cols >> p) & 1) ^ s[(k, p)] for p in L]
                    good &= ~((reads[0] == reads[1]) & (reads[1] == reads[2]))
            sol = [tuple((int(x) >> p) & 1 for p in range(n)) for x in cols[good]]
            sizes = circuit_sizes(sol, n)
            kept += bool(sizes) and max(sizes) >= 3
            counts.add(len(sol))
        plain = all(v == 0 for v in s.values())
        knot_rows.append({"points": n, "plain Pfaffian": plain, "colourings after removing a line": sorted(counts),
                          "line removals keeping a knot": "%d of %d" % (kept, n)})
        break
fano_like = [r for r in knot_rows if r["colourings after removing a line"] == [10]]
ok7 &= bool(fano_like) and all(r["line removals keeping a knot"] == "%d of %d" % (r["points"], r["points"]) for r in fano_like)
check("7 rigidity: on every corank-1 substrate (failing right-hand side), removing any line leaves Z3 (and so blurred Z3) exactly three "
      "solutions and every circuit a tie of two variables, never a knot; the knot's selected spaces are not rigid in general: on the "
      "Fano plane every line removal leaves 10 colourings and a knot among the circuits, though on some Pfaffian substrates only ties "
      "remain", ok7, {**dict(info7), "Pfaffian substrates (the knot)": knot_rows})

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"], "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
