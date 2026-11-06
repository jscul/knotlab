#!/usr/bin/env python3
"""Checks for BEYOND-TWO-20261101-001B: blurring makes counts hard and keeps failures and composition.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy)."""
import collections
import hashlib
import itertools
import json
import math
import random
import sys
import time
from fractions import Fraction
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
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"] if p.endswith(".json")}
check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
      {"mismatched": bad, "statuses": status})


# ------------------------------------------------------------------------------------------------ the two blurred laws
class Law:
    """a base law x1 + x2 + x3 = c over Z_p (p = 2: signed parity; p = 3: signed Z3) and its blur phi (value 0 doubled)"""

    def __init__(self, p):
        self.p = p
        self.base = list(range(p))
        self.phi = [0, 0] + list(range(1, p))           # blurred values 0 and 1 both map to 0
        self.dom = list(range(p + 1))
        self.weight = [self.phi.count(a) for a in self.base]

    def base_rel(self, c):
        return {t for t in itertools.product(self.base, repeat=3) if sum(t) % self.p == c}

    def blur_rel(self, c):
        return {t for t in itertools.product(self.dom, repeat=3) if sum(self.phi[x] for x in t) % self.p == c}

    def solve(self, n, system, blurred):
        dom = self.dom if blurred else self.base
        rels = {c: (self.blur_rel(c) if blurred else self.base_rel(c)) for c in range(self.p)}
        return [t for t in itertools.product(dom, repeat=n) if all(tuple(t[v] for v in vs) in rels[c] for vs, c in system)]

    def eliminate(self, n, system):
        """decide the image system by Gaussian elimination over Z_p (coefficients summed for repeated variables)"""
        rows = []
        for vs, c in system:
            r = [0] * (n + 1)
            for v in vs:
                r[v] = (r[v] + 1) % self.p
            r[n] = c % self.p
            rows.append(r)
        piv = 0
        for col in range(n):
            pr = next((i for i in range(piv, len(rows)) if rows[i][col]), None)
            if pr is None:
                continue
            rows[piv], rows[pr] = rows[pr], rows[piv]
            inv = pow(rows[piv][col], -1, self.p)
            rows[piv] = [(x * inv) % self.p for x in rows[piv]]
            for i in range(len(rows)):
                if i != piv and rows[i][col]:
                    f = rows[i][col]
                    rows[i] = [(a - f * b) % self.p for a, b in zip(rows[i], rows[piv])]
            piv += 1
        return all(any(r[:n]) or r[n] == 0 for r in rows)


def circuits(sol, n):
    ranges = [len({t[v] for t in sol}) for v in range(n)]

    def constrained(Y):
        return len({tuple(t[v] for v in Y) for t in sol}) < math.prod(ranges[v] for v in Y)
    cons = [frozenset(Y) for r in range(1, n + 1) for Y in itertools.combinations(range(n), r) if constrained(Y)]
    circ = [C for C in cons if not any(D < C for D in cons)]
    return set(cons), circ, constrained


def random_system(law, n, rng):
    return [(tuple(rng.choice(range(n)) for _ in range(3)), rng.randrange(law.p)) for _ in range(rng.randint(2, 4))]


PAR, Z3 = Law(2), Law(3)
rng = random.Random(20261101)

# ------------------------------------------------------------------------------------------------ 1. the blurring lemma
info1, ok1 = {}, True
for name, law in (("parity, 0 doubled (3 values)", PAR), ("Z3, 0 doubled (4 values)", Z3)):
    tally = collections.Counter()
    for _ in range(120):
        n = rng.choice([3, 4, 5])
        system = random_system(law, n, rng)
        base = law.solve(n, system, blurred=False)
        blur = law.solve(n, system, blurred=True)
        same_failure = (len(base) == 0) == (len(blur) == 0)
        weighted = sum(math.prod(law.weight[a] for a in t) for t in base)
        same_count = weighted == len(blur)
        if base:
            cb, _, _ = circuits(base, n)
            cl, _, _ = circuits(blur, n)
            same_circuits = cb == cl
        else:
            same_circuits = True
        ok1 &= same_failure and same_count and same_circuits
        tally["failing" if not base else "solvable"] += 1
    info1[name] = dict(tally)
check("1 the blurring lemma on 240 random systems: the blurred system fails exactly when its image does, has exactly the image's "
      "constrained sets (so the same circuits), and has as many solutions as the image's solutions weighted by preimage sizes", ok1, info1)

# ------------------------------------------------------------------------------------------------ 2. all Mal'tsev operations on three values
trip = list(itertools.product(range(3), repeat=3))
tidx = {t: i for i, t in enumerate(trip)}
fixed = {}
for (x, y, z) in trip:
    if x == y:
        fixed[tidx[(x, y, z)]] = z
    elif y == z:
        fixed[tidx[(x, y, z)]] = x
free = [i for i in range(27) if i not in fixed]
N = 3 ** len(free)
ops = np.zeros((N, 27), dtype=np.int8)
for i, v in fixed.items():
    ops[:, i] = v
codes = np.arange(N)
for k, i in enumerate(free):
    ops[:, i] = (codes // (3 ** k)) % 3
is_cong = {}
for (a, b), c in (((0, 1), 2), ((0, 2), 1), ((1, 2), 0)):
    cls = np.array([0 if v in (a, b) else 1 for v in range(3)], dtype=np.int8)
    good = np.ones(N, dtype=bool)
    for pos in range(3):
        for others in itertools.product(range(3), repeat=2):
            t1 = list(others)
            t1.insert(pos, a)
            t2 = list(others)
            t2.insert(pos, b)
            good &= cls[ops[:, tidx[tuple(t1)]]] == cls[ops[:, tidx[tuple(t2)]]]
    is_cong[(a, b)] = good
ncong = sum(v.astype(int) for v in is_cong.values())
affine = np.zeros(N, dtype=bool)
for perm in itertools.permutations(range(3)):
    inv = {perm[v]: v for v in range(3)}
    target = np.array([inv[(perm[x] - perm[y] + perm[z]) % 3] for (x, y, z) in trip], dtype=np.int8)
    affine |= (ops == target).all(axis=1)


def preserves_rows(rel, rows):
    rel = list(rel)
    ok = np.ones(len(rows), dtype=bool)
    for t1, t2, t3 in itertools.product(rel, repeat=3):
        res = [rows[:, tidx[(t1[j], t2[j], t3[j])]] for j in range(3)]
        hit = np.zeros(len(rows), dtype=bool)
        for r in rel:
            hit |= (res[0] == r[0]) & (res[1] == r[1]) & (res[2] == r[2])
        ok &= hit
    return ok


quot_affine = preserve_blur = both = 0
for (a, b), c in (((0, 1), 2), ((0, 2), 1), ((1, 2), 0)):
    rows = ops[np.where(is_cong[(a, b)])[0]]
    ph = [0 if v in (a, b) else 1 for v in range(3)]
    q010 = np.array([ph[v] for v in rows[:, tidx[(a, c, a)]]])
    q101 = np.array([ph[v] for v in rows[:, tidx[(c, a, c)]]])
    qa = (q010 == 1) & (q101 == 0)
    S0 = {t for t in trip if sum(ph[x] for x in t) % 2 == 0}
    S1 = {t for t in trip if sum(ph[x] for x in t) % 2 == 1}
    pb = preserves_rows(S0, rows) & preserves_rows(S1, rows)
    quot_affine += int(qa.sum())
    preserve_blur += int(pb.sum())
    both += int((qa == pb).all())
info2 = {"Mal'tsev operations on {0,1,2}": N, "with no nontrivial congruence (simple)": int((ncong == 0).sum()),
         "with exactly one (blocks 2+1)": int((ncong == 1).sum()), "with two or more": int((ncong >= 2).sum()),
         "affine (x - y + z over Z3)": int(affine.sum()), "affine among the simple": int((affine & (ncong == 0)).sum()),
         "non-simple with an affine (minority) quotient": quot_affine, "non-simple preserving blurred parity": preserve_blur,
         "these two sets coincide on every partition": both == 3}
ok2 = (ncong >= 2).sum() == 0 and info2["with exactly one (blocks 2+1)"] == 1020 and quot_affine == 48 and preserve_blur == 48 and both == 3
check("2 every Mal'tsev operation on three values has at most one nontrivial congruence, so every subalgebra has a unique maximal "
      "congruence and every Mal'tsev law on three values composes like cycles (Theorem 1); of the 1020 non-simple ones exactly the 48 "
      "with an affine quotient preserve blurred parity", ok2, info2)


# ------------------------------------------------------------------------------------------------ 3-4. the two blurred laws
def lift(law):
    D = law.dom

    def m(x, y, z):
        if x == y:
            return z
        if y == z:
            return x
        target = (law.phi[x] - law.phi[y] + law.phi[z]) % law.p
        return law.phi.index(target)
    return {(x, y, z): m(x, y, z) for x in D for y in D for z in D}


def preserves(rel, m):
    return all(tuple(m[(a[j], b[j], c[j])] for j in range(3)) in rel for a in rel for b in rel for c in rel)


def is_knot(R, k):
    return bool(R) and len(R) < len({x for t in R for x in t}) ** k and all(
        len({t[:j] + t[j + 1:] for t in R}) == len({x for t in R for x in t}) ** (k - 1) for j in range(k))


def count_matrix(rel, dom):
    return [[sum(1 for z in dom if (x, y, z) in rel) for y in dom] for x in dom]


def rank(M):
    A = [[Fraction(v) for v in row] for row in M]
    r = 0
    for col in range(len(A[0])):
        pr = next((i for i in range(r, len(A)) if A[i][col] != 0), None)
        if pr is None:
            continue
        A[r], A[pr] = A[pr], A[r]
        for i in range(len(A)):
            if i != r and A[i][col] != 0:
                f = A[i][col] / A[r][col]
                A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        r += 1
    return r


def law_report(law, label, rng):
    m = lift(law)
    rels = {c: law.blur_rel(c) for c in range(law.p)}
    maltsev = all(m[(x, x, y)] == y and m[(y, x, x)] == y for x in law.dom for y in law.dom)
    rep = {"Mal'tsev lift is Mal'tsev and preserves every relation": maltsev and all(preserves(R, m) for R in rels.values()),
           "every relation is a knot": all(is_knot(R, 3) for R in rels.values())}
    mats = {c: count_matrix(R, law.dom) for c, R in rels.items()}
    rep["count matrices (z counted)"] = mats
    rep["their ranks"] = {c: rank(M) for c, M in mats.items()}
    base_mats = {c: count_matrix(law.base_rel(c), law.base) for c in range(law.p)}
    rep["unblurred count matrices' ranks (control)"] = {c: rank(M) for c, M in base_mats.items()}
    rep["a failing system: R_0(x,y,z) and R_1(x,y,z)"] = law.solve(3, [((0, 1, 2), 0), ((0, 1, 2), 1)], blurred=True) == []
    agree = elim_fail = 0
    for _ in range(150):
        n = rng.choice([3, 4, 5, 6])
        system = random_system(law, n, rng)
        brute = bool(law.solve(n, system, blurred=True))
        agree += brute == law.eliminate(n, system)
        elim_fail += not brute
    rep["recognition by Gaussian elimination agrees with brute force"] = "%d/150 (%d failing)" % (agree, elim_fail)
    tested = viol = 0
    for _ in range(150):
        n = rng.choice([4, 5])
        system = random_system(law, n, rng)
        sol = law.solve(n, system, blurred=True)
        if not sol:
            continue
        _, circ, constrained = circuits(sol, n)
        for C1, C2 in itertools.combinations(circ, 2):
            for e in C1 & C2:
                tested += 1
                viol += not constrained(sorted((C1 | C2) - {e}))
    rep["circuit elimination on random systems: pairs tested, violations"] = [tested, viol]
    ok = (rep["Mal'tsev lift is Mal'tsev and preserves every relation"] and rep["every relation is a knot"]
          and all(r >= 2 for r in rep["their ranks"].values()) and all(r == 1 for r in rep["unblurred count matrices' ranks (control)"].values())
          and rep["a failing system: R_0(x,y,z) and R_1(x,y,z)"] and agree == 150 and elim_fail > 0 and tested > 0 and viol == 0)
    return ok, rep


ok3, rep3 = law_report(PAR, "blurred parity", rng)
check("3 blurred signed parity on three values (0 doubled): a Mal'tsev lift preserves it; its relations are knots; it fails (R_0 and "
      "R_1 on one triple), recognisably (Gaussian elimination on the image agrees with brute force); its count matrices have rank 2 "
      "while parity's have rank 1, so it is not strongly balanced and its count is #P-complete (Dyer-Richerby); circuit elimination "
      "holds on random systems", ok3, rep3)
ok4, rep4 = law_report(Z3, "blurred Z3", rng)
check("4 blurred signed Z3 on four values (0 doubled): the same in every respect (count matrices of rank 3 against Z3's rank 1)",
      ok4, rep4)

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
