#!/usr/bin/env python3
"""Checks for RIGID-SELECTION-20261101-001A: where selection is rigid, and the criterion over Z_(p^k).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx)."""
import collections
import hashlib
import itertools
import json
import math
import random
import sys
import time
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import zlocal as Z  # noqa: E402

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

rng = random.Random(20261101)


def random_substrate(n, k):
    for _ in range(20000):
        slots = [p for p in range(n) for _ in range(k)]
        rng.shuffle(slots)
        lines = [tuple(slots[k * i:k * i + k]) for i in range(n)]
        if all(len(set(L)) == k for L in lines):
            g = nx.Graph([(("l", i), ("p", p)) for i, L in enumerate(lines) for p in L])
            if nx.is_connected(g):
                return lines
    return None


def random_system(p, kk, k, n, plain=False):
    q = p ** kk
    lines = random_substrate(n, k)
    if lines is None:
        return None
    units = [u for u in range(1, q) if math.gcd(u, q) == 1]
    return [[((1 if plain else rng.choice(units)) if pt in L else 0) for pt in range(n)] for L in lines]


def global_rhs(A, p, kk):
    """a right-hand side for each global class (a multiple of the unit vector of a line of least order), or []"""
    n = len(A)
    g, gens, glob = Z.global_classes(A, p, kk)
    if not glob:
        return g, []
    _, cls = Z.coker(A, p, kk)
    orders = [Z.order_of(x, g) for x in gens]
    L0 = min(range(n), key=lambda L: orders[L])
    out = []
    for x in glob:
        t = next(t for t in range(1, p ** kk) if cls([t if j == L0 else 0 for j in range(n)]) == x)
        out.append([t if j == L0 else 0 for j in range(n)])
    return g, out


def removal(A, c, p, kk, i):
    n = len(A)
    rows = [r for j, r in enumerate(A) if j != i]
    rhs = [b for j, b in enumerate(c) if j != i]
    return Z.solutions(rows, rhs, p, kk, n), Z.solutions(rows, [0] * len(rhs), p, kk, n)


def is_cyclic(K, q):
    if len(K) <= 1:
        return True
    return max(math.lcm(*[q // math.gcd(x, q) for x in v]) for v in K) == len(K)


# ------------------------------------------------------------------------------------------------ 1. fields
info1, ok1 = collections.Counter(), True
for p in (3, 5, 7):
    for k in (3, 4):
        found = 0
        for _ in range(400):
            A = random_system(p, 1, k, rng.randint(k + 1, 8 if k == 3 else 7))
            if A is None:
                continue
            g, rhss = global_rhs(A, p, 1)
            if not rhss:
                continue
            found += 1
            ok1 &= g == [p]
            c = rhss[0]
            for i in range(len(A)):
                sol, K = removal(A, c, p, 1, i)
                ok1 &= bool(sol) and len(K) == p and max((len(C) for C in Z.circuits(sol, len(A))), default=0) <= 2
        info1["GF(%d), arity %d: global failures" % (p, k)] = found
        ok1 &= found > 0
check("1 over a field every global failure has corank 1 (cokernel of order p) and leaves, after any line is removed, p solutions whose "
      "circuits are all ties: rigid (random knot systems over GF(3), GF(5), GF(7) at arities 3 and 4)", ok1, dict(info1))

# ------------------------------------------------------------------------------------------------ 2. the criterion over Z_(p^k)
info2, ok2 = collections.Counter(), True
for trial in range(120):
    p, kk = rng.choice([(2, 2), (2, 3), (3, 2)])
    q = p ** kk
    n = rng.randint(2, 3)
    A = [[rng.randrange(q) for _ in range(n)] for _ in range(n)]
    g, gens, glob = Z.global_classes(A, p, kk)
    _, cls = Z.coker(A, p, kk)
    G = set(glob)
    order_coker = math.prod(g) if g else 1
    for L in range(n):
        ann = sum(1 for t in range(q) if all((t * x) % gi == 0 for x, gi in zip(gens[L], g)))
        K = Z.solutions([r for j, r in enumerate(A) if j != L], [0] * (n - 1), p, kk, n)
        ok2 &= len(K) == order_coker * ann
    for c in itertools.product(range(q), repeat=n):
        c = list(c)
        if Z.solutions(A, c, p, kk, n):
            continue
        direct = all(removal(A, c, p, kk, i)[0] for i in range(n))
        ok2 &= direct == (cls(c) in G)
        info2["failing right-hand sides checked"] += 1
        info2["global"] += direct
check("2 over Z4, Z8 and Z9 (random square systems, every right-hand side): a failure is global exactly when its class lies in every "
      "cyclic subgroup generated by a line's class, and after removing line L the solution group has order |cokernel| x |ann(class of L)|",
      ok2, dict(info2))

# ------------------------------------------------------------------------------------------------ 3. cyclic kernels carry no knot
info3, ok3 = collections.Counter(), True
for trial in range(1500):
    p, kk, k = rng.choice([(2, 2, 3), (2, 3, 3), (3, 2, 3), (5, 2, 3), (3, 3, 3), (2, 2, 4), (2, 3, 4)])
    n = rng.randint(k + 1, 9 if k == 3 else 7)
    A = random_system(p, kk, k, n, plain=rng.random() < 0.3)
    if A is None:
        continue
    g, rhss = global_rhs(A, p, kk)
    if not rhss:
        continue
    c = rhss[0]
    for i in range(n):
        sol, K = removal(A, c, p, kk, i)
        big = max((len(C) for C in Z.circuits(sol, n)), default=0)
        if is_cyclic(K, p ** kk):
            info3["removals with a cyclic solution group"] += 1
            ok3 &= big <= 2
        else:
            info3["removals with a non-cyclic solution group"] += 1
            info3["of which keep a knot"] += big >= 3
check("3 on random global failures over Z4, Z8, Z9, Z25, Z27 (arities 3 and 4), every removal leaving a cyclic solution group leaves only "
      "ties; knots appear only with non-cyclic groups (ticket B)", ok3 and info3["of which keep a knot"] > 0, dict(info3))

# ------------------------------------------------------------------------------------------------ 4. S3
els = list(itertools.permutations(range(3)))
eidx = {e: i for i, e in enumerate(els)}
mul = [[eidx[tuple(a[b[t]] for t in range(3))] for b in els] for a in els]
sgn = [1 if sum(1 for i in range(3) for j in range(i + 1, 3) if e[i] > e[j]) % 2 == 0 else -1 for e in els]
G3 = list(itertools.product(range(6), repeat=3))


def closure(gens):
    H = {(0, 0, 0)}
    frontier = [(0, 0, 0)]
    while frontier:
        new = []
        for h in frontier:
            for x in gens:
                y = tuple(mul[a][b] for a, b in zip(h, x))
                if y not in H:
                    H.add(y)
                    new.append(y)
        frontier = new
    return frozenset(H)


subs = {closure([a, b]) for a in G3 for b in G3}
full2 = [H for H in subs if all(len({(h[i], h[j]) for h in H}) == 36 for i, j in ((0, 1), (0, 2), (1, 2)))]
sign_parity = frozenset(h for h in G3 if sgn[h[0]] * sgn[h[1]] * sgn[h[2]] == 1)
info4 = {"subgroups of S3^3 generated by two elements": len(subs), "with full 2-projections (orders)": sorted(len(H) for H in full2),
         "all of them the sign-parity subgroup": all(H == sign_parity for H in full2)}
check("4 S3: every subgroup of S3^3 generated by two elements with full 2-projections is the sign-parity subgroup (order 108); the "
      "order argument in proof.md covers all subgroups and D_p", bool(full2) and info4["all of them the sign-parity subgroup"], info4)

# ------------------------------------------------------------------------------------------------ 5. simple three-element algebras
trip = list(itertools.product(range(3), repeat=3))
tidx = {t: i for i, t in enumerate(trip)}
free = [i for i, (x, y, z) in enumerate(trip) if x != y and y != z]


def op_from(code):
    table = [0] * 27
    for i, (x, y, z) in enumerate(trip):
        if x == y:
            table[i] = z
        elif y == z:
            table[i] = x
    for k, i in enumerate(free):
        table[i] = (code // 3 ** k) % 3
    return table


def congruence_count(table):
    cnt = 0
    for (a, b), c in (((0, 1), 2), ((0, 2), 1), ((1, 2), 0)):
        cls = [0 if v in (a, b) else 1 for v in range(3)]
        good = all(cls[table[tidx[tuple(o[:pos] + (a,) + o[pos:])]]] == cls[table[tidx[tuple(o[:pos] + (b,) + o[pos:])]]]
                   for pos in range(3) for o in itertools.product(range(3), repeat=2))
        cnt += good
    return cnt


affine = [None] * 27
for i, (x, y, z) in enumerate(trip):
    affine[i] = (x - y + z) % 3
sampled, violations, checked = 0, 0, 0
while sampled < 200:
    table = op_from(rng.randrange(3 ** len(free)))
    if congruence_count(table) or table == affine:
        continue
    sampled += 1
    tab = np.array(table)
    M3 = np.zeros((27, 27, 27), dtype=np.int64)          # index of m(t_a, t_b, t_c), coordinatewise
    arr = np.array(trip)
    for j in range(3):
        col = tab[(arr[:, None, None, j] * 9 + arr[None, :, None, j] * 3 + arr[None, None, :, j])]
        M3 += col * 3 ** (2 - j)
    for t1, t2 in itertools.combinations(range(27), 2):
        S = np.zeros(27, dtype=bool)
        S[[t1, t2]] = True
        while True:
            idx = np.flatnonzero(S)
            new = np.zeros(27, dtype=bool)
            new[np.unique(M3[np.ix_(idx, idx, idx)])] = True
            if (new | S).sum() == S.sum():
                break
            S |= new
        checked += 1
        members = [trip[i] for i in np.flatnonzero(S)]
        full = all(len({(s[i], s[j]) for s in members}) == 9 for i, j in ((0, 1), (0, 2), (1, 2)))
        violations += full and len(members) < 27
check("5 simple non-affine Mal'tsev algebras on three values (200 sampled): no subuniverse of A^3 generated by two tuples has full "
      "2-projections except A^3, so no knot on full ranges (in line with the skew-free argument)", violations == 0,
      {"algebras": sampled, "subuniverses checked": checked, "proper ones with full 2-projections": violations})

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
