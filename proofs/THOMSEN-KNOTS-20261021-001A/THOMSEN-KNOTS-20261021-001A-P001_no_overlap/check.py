#!/usr/bin/env python3
"""Checks for THOMSEN-KNOTS-20261021-001A-P001. The statements are in proof.md.

Checks:
- Lemma 1 and Theorem 2 (the construction, replayed). Random knots with three and four variables on two and three
  values, and the overlapping laws of census KNOT-IMAGES-20261021-001A-E001 (e = x + yH over Z5 and Z7, the equality
  indicator). At every variable where a knot overlaps, S2 = K(a, e) & K(a, e') either violates elimination at once, or
  contains a circuit D through e and e' whose part Z = D - {e, e'} is nonempty and on which e' = e is always allowed;
  two copies of D sharing e and e' then violate elimination at e and at e'. Knots that do not overlap are counted.
- Theorem 4. All Latin squares of orders 2 to 4, 60 random squares each of orders 5, 6 and 7, every 3-net square of the
  census, and the groups Z2 to Z8, Z2xZ2, Z2xZ4, Z3xZ3, S3, D4, Q8, D5, A4, D6 and Dic3:
  - T' (Thomsen's configuration with one column visible) by its formula and by enumerating the hidden columns;
  - every tuple with two equal rows is allowed;
  - T' is full exactly when Thomsen's closure condition holds (brute force), and exactly when the square is isotopic
    to an abelian group (its principal loop isotope is an abelian group);
  - when Thomsen fails, T or T' is a knot that overlaps at every variable, and the doubled system is built and
    verified by brute force to violate elimination;
  - for groups, T' does not depend on its column, and T is the commuting-differences relation.
- Proposition 5 (Q8). Q8 is rebuilt as (sign, class) pairs with the cocycle f(a, b) = a1b1 + a2b2 + a2b1 and matched
  to the census square. T is the commuting-differences relation with 320 triples, saturated by +-1, and its census top
  is mod +-1. Its top image is omega(c1 + c2, c1 + c3) = 0, 40 of 64 triples, and three of its triples sum outside it.
  The system T(x1, x2, x3) & T(x1, x2, x3') violates elimination at x1 and at x2.

Controls, each of which must be rejected:
- 'two copies of any knot sharing two variables violate elimination' (x + y + z = 0 over Z3);
- 'the three-row configuration T detects every square that violates Thomsen's condition' (an order-6 square with T
  full and T' a knot);
- 'Thomsen's configuration is a knot in every group's 3-net law' (Z5);
- 'every top image of the Q8 3-net law is closed under x + y + z' (the top image of T).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS = ROOT / "artifacts" / "KNOT-IMAGES-20261021-001A" / "KNOT-IMAGES-20261021-001A-E001_latin_census"


# ------------------------------------------------------------------ relations and circuits

def ranges(S, n):
    return [{s[v] for s in S} for v in range(n)]


def proj(S, Y):
    return {tuple(s[v] for v in Y) for s in S}


def free(S, Y, rg):
    need = 1
    for v in Y:
        need *= len(rg[v])
    return len(proj(S, Y)) == need


def is_circuit(S, C, rg):
    return not free(S, C, rg) and all(free(S, tuple(u for u in C if u != w), rg) for w in C)


def elimination_failures(S, n):
    rg = ranges(S, n)
    fr = {Y: free(S, Y, rg) for k in range(1, n + 1) for Y in combinations(range(n), k)}
    cs = [Y for Y, f in fr.items() if len(Y) > 1 and not f and all(fr[tuple(u for u in Y if u != w)] for w in Y)]
    out = []
    for C1, C2 in combinations(cs, 2):
        for y in sorted(set(C1) & set(C2)):
            if fr[tuple(sorted((set(C1) | set(C2)) - {y}))]:
                out.append((C1, C2, y))
    return cs, out


def overlaps_at(K, e):
    fib = {}
    for t in K:
        fib.setdefault(t[:e] + t[e + 1:], set()).add(t[e])
    lam = {(u, v) for F in fib.values() for u in F for v in F}
    return len(lam) == len({t[e] for t in K}) ** 2


def is_knot(K, k):
    return is_circuit(K, tuple(range(k)), ranges(K, k))


# ------------------------------------------------------------------ Lemma 1 and Theorem 2

def doubled(rho, nZ):
    """Two copies of rho on (Z, t, t') sharing t and t'; coordinates (Z1, Z2, t, t')."""
    fib = {}
    for t in rho:
        fib.setdefault(t[nZ:], []).append(t[:nZ])
    return {z1 + z2 + tt for tt, zs in fib.items() for z1 in zs for z2 in zs}


def doubling_fails(Sig, nZ):
    rg = ranges(Sig, 2 * nZ + 2)
    t, t2 = 2 * nZ, 2 * nZ + 1
    D1 = tuple(range(nZ)) + (t, t2)
    D2 = tuple(range(nZ, 2 * nZ)) + (t, t2)
    return (is_circuit(Sig, D1, rg) and is_circuit(Sig, D2, rg)
            and free(Sig, tuple(range(2 * nZ)) + (t2,), rg) and free(Sig, tuple(range(2 * nZ)) + (t,), rg))


def theorem2_construction(K, k, e):
    """Run the proof of Theorem 2 on a knot K overlapping at e. Returns (route, verified)."""
    order = [v for v in range(k) if v != e] + [e]
    K = {tuple(t[v] for v in order) for t in K}
    fib = {}
    for t in K:
        fib.setdefault(t[:-1], set()).add(t[-1])
    S2 = {t + (u,) for t in K for u in fib[t[:-1]]}
    rg = ranges(S2, k + 1)
    E, E2 = k - 1, k
    ok = is_circuit(S2, tuple(range(k)), rg) and is_circuit(S2, tuple(range(k - 1)) + (E2,), rg)
    y = 0
    U = tuple(v for v in range(k + 1) if v != y)
    if free(S2, U, rg):
        return "S2 violates elimination at once", ok
    D = next(D for r in range(2, len(U) + 1) for D in combinations(U, r) if is_circuit(S2, D, rg))
    Z = [v for v in D if v not in (E, E2)]
    ok = ok and E in D and E2 in D and len(Z) > 0
    rho = proj(S2, D)
    selector = all(z + (s, s) in rho for z in product(*[sorted(rg[v]) for v in Z]) for s in rg[E])
    ok = ok and selector and doubling_fails(doubled(rho, len(Z)), len(Z))
    return f"doubled circuit of {len(D)} variables", ok


# ------------------------------------------------------------------ Latin squares and groups

def cayley(elems, mul):
    idx = {x: i for i, x in enumerate(elems)}
    return [[idx[mul(a, b)] for b in elems] for a in elems]


def latin_squares(n):
    out = []
    rows = list(permutations(range(n)))

    def go(sq):
        if len(sq) == n:
            out.append([list(r) for r in sq])
            return
        for r in rows:
            if all(r[j] != s[j] for s in sq for j in range(n)):
                go(sq + [r])
    go([])
    return out


def random_latin(n, rng):
    while True:
        rows = []
        for _ in range(n):
            for _ in range(500):
                r = list(range(n))
                rng.shuffle(r)
                if all(r[j] != row[j] for row in rows for j in range(n)):
                    rows.append(r)
                    break
            else:
                break
        if len(rows) == n:
            return rows


def tprime_formula(L):
    n = len(L)
    rs = [[0] * n for _ in range(n)]
    for x in range(n):
        for y in range(n):
            rs[x][L[x][y]] = y
    return {(x1, x2, x3, y1) for x1, x2, x3, y1 in product(range(n), repeat=4)
            if L[x2][rs[x1][L[x3][y1]]] == L[x3][rs[x1][L[x2][y1]]]}


def tprime_literal(L):
    """Enumerate the hidden columns y2, y3; the hidden labels are the products."""
    n = len(L)
    out = set()
    for x1, x2, x3, y1 in product(range(n), repeat=4):
        found = False
        for y2 in range(n):
            if L[x1][y2] != L[x2][y1]:
                continue
            for y3 in range(n):
                if L[x1][y3] == L[x3][y1] and L[x2][y3] == L[x3][y2]:
                    found = True
                    break
            if found:
                break
        if found:
            out.add((x1, x2, x3, y1))
    return out


def thomsen(L):
    n = len(L)
    for x1, x2, x3, y1 in product(range(n), repeat=4):
        for y2 in range(n):
            if L[x1][y2] != L[x2][y1]:
                continue
            for y3 in range(n):
                if L[x1][y3] == L[x3][y1] and L[x2][y3] != L[x3][y2]:
                    return False
    return True


def abelian_group_isotope(L):
    n = len(L)
    R = {L[x][0]: x for x in range(n)}
    C = {L[0][y]: y for y in range(n)}
    op = lambda x, y: L[R[x]][C[y]]
    return (all(op(op(x, y), z) == op(x, op(y, z)) for x in range(n) for y in range(n) for z in range(n))
            and all(op(x, y) == op(y, x) for x in range(n) for y in range(n)))


def doubled_T(T):
    fib = {}
    for a, b, c in T:
        fib.setdefault((a, b), []).append(c)
    Sig = {(a, b, c, d) for (a, b), cs in fib.items() for c in cs for d in cs}
    rg = ranges(Sig, 4)
    return (is_circuit(Sig, (0, 1, 2), rg) and is_circuit(Sig, (0, 1, 3), rg)
            and free(Sig, (1, 2, 3), rg) and free(Sig, (0, 2, 3), rg))


def doubled_Tp(Tp):
    fib = {}
    for a, b, c, y in Tp:
        fib.setdefault((a, b), []).append((c, y))
    Sig = {(a, b) + p + q for (a, b), ps in fib.items() for p in ps for q in ps}
    rg = ranges(Sig, 6)
    return (is_circuit(Sig, (0, 1, 2, 3), rg) and is_circuit(Sig, (0, 1, 4, 5), rg)
            and free(Sig, (1, 2, 3, 4, 5), rg) and free(Sig, (0, 2, 3, 4, 5), rg))


def analyse_square(L, literal=True):
    n = len(L)
    Tp = tprime_formula(L)
    T = {t[:3] for t in Tp}
    row = {"order": n, "T_prime_size": len(Tp), "T_size": len(T)}
    row["literal_agrees"] = (tprime_literal(L) == Tp) if literal else None
    row["equal_rows_allowed"] = all(t in Tp for t in product(range(n), repeat=4) if len({t[0], t[1], t[2]}) < 3)
    row["thomsen"] = thomsen(L)
    row["T_prime_full"] = len(Tp) == n ** 4
    row["abelian_group_isotope"] = abelian_group_isotope(L)
    row["consistent"] = row["thomsen"] == row["T_prime_full"] == row["abelian_group_isotope"] and row["equal_rows_allowed"] \
        and row["literal_agrees"] is not False
    if not row["thomsen"]:
        if len(T) < n ** 3:
            row["gadget"] = "T"
            row["knot"] = is_knot(T, 3)
            row["overlaps_everywhere"] = all(overlaps_at(T, e) for e in range(3))
            row["doubled_fails"] = doubled_T(T)
        else:
            row["gadget"] = "T'"
            row["knot"] = is_knot(Tp, 4)
            row["overlaps_everywhere"] = all(overlaps_at(Tp, e) for e in range(4))
            row["doubled_fails"] = doubled_Tp(Tp)
        row["consistent"] = row["consistent"] and row["knot"] and row["overlaps_everywhere"] and row["doubled_fails"]
    return row, T, Tp


def groups():
    cyc = lambda n: cayley(list(range(n)), lambda a, b: (a + b) % n)
    out = {f"Z{n}": (cyc(n), True) for n in range(2, 9)}
    out["Z2xZ2"] = (cayley([(a, b) for a in range(2) for b in range(2)], lambda u, v: ((u[0] + v[0]) % 2, (u[1] + v[1]) % 2)), True)
    out["Z2xZ4"] = (cayley([(a, b) for a in range(2) for b in range(4)], lambda u, v: ((u[0] + v[0]) % 2, (u[1] + v[1]) % 4)), True)
    out["Z3xZ3"] = (cayley([(a, b) for a in range(3) for b in range(3)], lambda u, v: ((u[0] + v[0]) % 3, (u[1] + v[1]) % 3)), True)
    comp = lambda a, b: tuple(a[b[i]] for i in range(len(b)))
    out["S3"] = (cayley(list(permutations(range(3))), comp), False)

    def dihedral(m):
        return cayley([(r, f) for f in range(2) for r in range(m)],
                      lambda u, v: ((u[0] + (v[0] if u[1] == 0 else -v[0])) % m, (u[1] + v[1]) % 2))
    out["D4"], out["D5"], out["D6"] = (dihedral(4), False), (dihedral(5), False), (dihedral(6), False)
    unit = {("1", "1"): (1, "1"), ("1", "i"): (1, "i"), ("1", "j"): (1, "j"), ("1", "k"): (1, "k"),
            ("i", "1"): (1, "i"), ("i", "i"): (-1, "1"), ("i", "j"): (1, "k"), ("i", "k"): (-1, "j"),
            ("j", "1"): (1, "j"), ("j", "i"): (-1, "k"), ("j", "j"): (-1, "1"), ("j", "k"): (1, "i"),
            ("k", "1"): (1, "k"), ("k", "i"): (1, "j"), ("k", "j"): (-1, "i"), ("k", "k"): (-1, "1")}
    out["Q8"] = (cayley([(sg, e) for sg in (1, -1) for e in "1ijk"],
                        lambda u, v: (u[0] * v[0] * unit[(u[1], v[1])][0], unit[(u[1], v[1])][1])), False)
    even = [p for p in permutations(range(4)) if sum(p[i] > p[j] for i in range(4) for j in range(i + 1, 4)) % 2 == 0]
    out["A4"] = (cayley(even, comp), False)
    # Dic3 = <a, x | a^6 = 1, x^2 = a^3, x a x^-1 = a^-1>, elements a^k x^s
    out["Dic3"] = (cayley([(k, s) for s in range(2) for k in range(6)],
                          lambda u, v: ((u[0] + (v[0] if u[1] == 0 else -v[0]) + (3 if u[1] == v[1] == 1 else 0)) % 6,
                                        (u[1] + v[1]) % 2)), False)
    return out


def is_group(L):
    n = len(L)
    return all(L[L[a][b]][c] == L[a][L[b][c]] for a in range(n) for b in range(n) for c in range(n))


# ------------------------------------------------------------------ run

def run():
    checks, controls, failures = {}, {}, []
    census_rows = {}
    for line in (CENSUS / "raw_rows.jsonl").read_text().splitlines():
        r = json.loads(line)
        census_rows[r["law"]] = r

    # Lemma 1 and Theorem 2: random knots
    rng = random.Random("thomsen-knots-theorem-2")
    routes, knots, overlapping, bad = {}, 0, 0, 0
    while knots < 400:
        D = rng.choice((2, 3))
        k = rng.choice((3, 4))
        full = list(product(range(D), repeat=k))
        K = set(rng.sample(full, rng.randint(len(full) // 2, len(full) - 1)))
        if not is_knot(K, k) or any(len({t[v] for t in K}) < D for v in range(k)):
            continue
        knots += 1
        for e in range(k):
            if not overlaps_at(K, e):
                continue
            overlapping += 1
            route, ok = theorem2_construction(K, k, e)
            routes[route] = routes.get(route, 0) + 1
            bad += not ok
    census_overlap = {}
    for name, r in census_rows.items():
        if r["family"] != "overlapping":
            continue
        if name.startswith("e=x+yH"):
            p = int(name.split("p=")[1].split()[0])
            H = [int(h) for h in name.split("H=")[1].split(",")]
            K = {(x, y, (x + y * h) % p) for x in range(p) for y in range(p) for h in H}
        else:
            K = {(int(a != b), a, b) for a in range(3) for b in range(3)}
        res = {"knot": is_knot(K, 3)}
        for e in range(3):
            if overlaps_at(K, e):
                res[f"variable {e}"] = theorem2_construction(K, 3, e)
        census_overlap[name] = res
    ok_census = all(v["knot"] and any(k.startswith("variable") for k in v)
                    and all(x[1] for k, x in v.items() if k.startswith("variable")) for v in census_overlap.values())
    checks["theorem_2_construction"] = {"random_knots": knots, "overlapping_knot_variables": overlapping,
                                        "routes": routes, "unverified": bad, "census_overlapping_laws": census_overlap}
    if bad or not ok_census or overlapping == 0:
        failures.append("Theorem 2 construction")

    # Theorem 4: Latin squares and groups
    rng = random.Random("thomsen-knots-theorem-4")
    squares = [("all", L) for n in (2, 3, 4) for L in latin_squares(n)]
    squares += [("random", random_latin(n, rng)) for n in (5, 6, 7) for _ in range(60)]
    squares += [("census " + name, r["square"]) for name, r in census_rows.items() if r["family"] == "3-net"]
    summary, inconsistent, census_detail = {}, [], {}
    t_full_tprime_knot = None
    for src, L in squares:
        row, T, Tp = analyse_square(L)
        key = f"{src.split()[0]} squares of order {row['order']}: " + \
            ("Thomsen" if row["thomsen"] else f"not Thomsen, fails via {row['gadget']}")
        summary[key] = summary.get(key, 0) + 1
        if not row["consistent"]:
            inconsistent.append((src, L))
        if t_full_tprime_knot is None and row.get("gadget") == "T'" and row["order"] == 6 and src == "random":
            t_full_tprime_knot = (src, L, row)
        if src.startswith("census"):
            census_detail[src[7:]] = {k: row.get(k) for k in ("order", "thomsen", "abelian_group_isotope", "gadget", "doubled_fails")}
    group_rows = {}
    for name, (L, abelian) in groups().items():
        row, T, Tp = analyse_square(L)
        n = len(L)
        inv = [next(b for b in range(n) if L[a][b] == 0) for a in range(n)]
        comm = {(x1, x2, x3) for x1, x2, x3 in product(range(n), repeat=3)
                if L[L[inv[x2]][x1]][L[inv[x3]][x1]] == L[L[inv[x3]][x1]][L[inv[x2]][x1]]}
        row["is_group"] = is_group(L)
        row["abelian"] = abelian
        row["T_prime_independent_of_column"] = Tp == {t + (y,) for t in T for y in range(n)}
        row["T_is_commuting_differences"] = T == comm
        row["consistent"] = row["consistent"] and row["is_group"] and row["T_prime_independent_of_column"] \
            and row["T_is_commuting_differences"] and row["thomsen"] == abelian and (abelian or row["gadget"] == "T")
        group_rows[name] = row
    checks["theorem_4"] = {"squares": len(squares), "summary": summary, "inconsistent": len(inconsistent),
                           "census_squares": census_detail, "groups": group_rows}
    if inconsistent or not all(r["consistent"] for r in group_rows.values()):
        failures.append("Theorem 4")

    # Proposition 5: Q8
    def f(a, b):
        a1, a2, b1, b2 = a & 1, a >> 1, b & 1, b >> 1
        return (a1 * b1 + a2 * b2 + a2 * b1) % 2
    qmul = lambda u, v: ((u[0] + v[0] + f(u[1], v[1])) % 2, u[1] ^ v[1])
    elems = [(sg, c) for sg in (0, 1) for c in range(4)]          # census index i = 4 * sign + class
    to_i = {x: 4 * x[0] + x[1] for x in elems}
    q8row = census_rows["3-net Q8"]
    Q8 = q8row["square"]
    matches = all(Q8[to_i[u]][to_i[v]] == to_i[qmul(u, v)] for u in elems for v in elems)
    n = 8
    T_lit = set()
    for x1, x2, x3 in product(range(n), repeat=3):
        if any(Q8[x1][y2] == Q8[x2][y1] and Q8[x1][y3] == Q8[x3][y1] and Q8[x2][y3] == Q8[x3][y2]
               for y1, y2, y3 in product(range(n), repeat=3)):
            T_lit.add((x1, x2, x3))
    inv = [next(b for b in range(n) if Q8[a][b] == 0) for a in range(n)]
    comm = {(x1, x2, x3) for x1, x2, x3 in product(range(n), repeat=3)
            if Q8[Q8[inv[x2]][x1]][Q8[inv[x3]][x1]] == Q8[Q8[inv[x3]][x1]][Q8[inv[x2]][x1]]}
    saturated = all(tuple(x ^ (4 if i == j else 0) for i, x in enumerate(t)) in T_lit for t in T_lit for j in range(3))
    omega = lambda u, v: ((u & 1) * (v >> 1) + (u >> 1) * (v & 1)) % 2
    image = {tuple(x & 3 for x in t) for t in T_lit}
    predicted = {(c1, c2, c3) for c1, c2, c3 in product(range(4), repeat=3) if omega(c1 ^ c2, c1 ^ c3) == 0}
    triple = [(0, 1, 0), (0, 0, 0), (0, 0, 2)]
    summed = tuple(a ^ b ^ c for a, b, c in zip(*triple))
    tops_pm1 = all(sorted(sorted(b) for b in blocks) == [[0, 4], [1, 5], [2, 6], [3, 7]] for blocks in q8row["tops"].values())
    prop5 = {"rebuilt_matches_census": matches, "T_literal_is_commuting_differences": T_lit == comm, "T_size": len(T_lit),
             "T_knot": is_knot(T_lit, 3), "T_overlaps_everywhere": all(overlaps_at(T_lit, e) for e in range(3)),
             "saturated_by_pm1": saturated, "census_tops_mod_pm1": tops_pm1, "certified": all(q8row["certified"].values()),
             "top_image_size": len(image), "top_image_is_omega": image == predicted,
             "triple_in_image": all(t in image for t in triple), "sum": summed, "sum_outside_image": summed not in image,
             "doubled_system_fails_at_x1_and_x2": doubled_T(T_lit), "group_row": group_rows["Q8"]["thomsen"] is False}
    prop5["failing_system_circuits"], prop5["failing_system_failures"] = [], []
    fib = {}
    for a, b, c in T_lit:
        fib.setdefault((a, b), []).append(c)
    Sig = {(a, b, c, d) for (a, b), cs in fib.items() for c in cs for d in cs}
    cs, fl = elimination_failures(Sig, 4)
    prop5["failing_system_circuits"], prop5["failing_system_failures"] = cs, fl
    checks["proposition_5"] = prop5
    if not (matches and prop5["T_literal_is_commuting_differences"] and len(T_lit) == 320 and prop5["T_knot"]
            and prop5["T_overlaps_everywhere"] and saturated and tops_pm1 and prop5["certified"] and len(image) == 40
            and prop5["top_image_is_omega"] and prop5["triple_in_image"] and prop5["sum_outside_image"]
            and prop5["doubled_system_fails_at_x1_and_x2"] and fl):
        failures.append("Proposition 5")

    # controls
    K = {(z, t, u) for z, t, u in product(range(3), repeat=3) if (z + t + u) % 3 == 0}
    cs, fl = elimination_failures(doubled(K, 1), 4)
    controls["two_copies_of_any_knot_fail"] = {"circuits": cs, "failures": fl, "rejected": is_knot(K, 3) and not fl}
    controls["three_row_configuration_suffices"] = {
        "square": t_full_tprime_knot[1] if t_full_tprime_knot else None, "source": t_full_tprime_knot[0] if t_full_tprime_knot else None,
        "rejected": bool(t_full_tprime_knot) and t_full_tprime_knot[2]["T_size"] == 216 and t_full_tprime_knot[2]["knot"]
        and t_full_tprime_knot[2]["doubled_fails"]}
    z5 = group_rows["Z5"]
    controls["thomsen_configuration_always_a_knot"] = {"rejected": z5["T_prime_full"] and z5["T_size"] == 125}
    controls["q8_top_images_closed_under_sum"] = {"rejected": prop5["triple_in_image"] and prop5["sum_outside_image"]}
    for k, v in controls.items():
        if not v["rejected"]:
            failures.append(f"control not rejected: {k}")
    return checks, controls, failures


def main() -> int:
    write = "--write" in sys.argv[1:]
    checks, controls, failures = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"], "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"], "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"], "checks": checks, "controls": controls, "failures": failures,
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n"
    if write:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: failures {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
