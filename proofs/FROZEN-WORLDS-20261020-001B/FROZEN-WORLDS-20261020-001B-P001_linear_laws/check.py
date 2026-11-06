#!/usr/bin/env python3
"""Checks for FROZEN-WORLDS-20261020-001B-P001: a linear law is frozen everywhere or nowhere.

Each law is shift-invariant on Z^2: n variable types per site and a list of
constraint types, each a set of (type, offset) terms that must sum to 0 over
GF(2). The checks compute:

- the generic rank of the law's polynomial matrix, from its values at random
  points of GF(2^31) (the maximum over five points; Schwartz-Zippel);
- the finite moves: homogeneous solutions supported inside a box, subject to
  every constraint that touches the box (exact GF(2) elimination);
- box entropy: the dimension of the projection onto a box, bounded below by
  the finite moves inside it and above by an open truncation;
- knots: every subset of the variables near the origin, the minimal supports of
  fixed parities among them, knotlab's K1-K3 verdicts, and whether each knot's
  variables lie in the supports of finite moves;
- world-independence: whether a variable can be flipped by a finite change at
  two different solutions, solved at each solution separately.

Each check also runs on a deliberately wrong input, which it must reject.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from knotlab.knots import check_knot  # noqa: E402
from knotlab.relations import Relation  # noqa: E402


def parity(x: int) -> int:
    return bin(x).count("1") & 1


# ------------------------------------------------------------------ GF(2) elimination

def solve(nvars, rows):
    piv = []
    for mask, rhs in rows:
        for col, pm, pr in piv:
            if mask >> col & 1:
                mask ^= pm
                rhs ^= pr
        if mask == 0:
            if rhs:
                return None
            continue
        col = (mask & -mask).bit_length() - 1
        piv = [(c, pm ^ mask, pr ^ rhs) if pm >> col & 1 else (c, pm, pr) for c, pm, pr in piv]
        piv.append((col, mask, rhs))
    pivcols = {c for c, _, _ in piv}
    x0 = sum(1 << c for c, _, pr in piv if pr)
    basis = []
    for f in range(nvars):
        if f not in pivcols:
            vec = 1 << f
            for c, pm, _ in piv:
                if pm >> f & 1:
                    vec |= 1 << c
            basis.append(vec)
    return x0, basis


def span_basis(vectors):
    basis = {}
    for v in vectors:
        while v:
            top = v.bit_length() - 1
            if top in basis:
                v ^= basis[top]
            else:
                basis[top] = v
                break
    return basis


def compress(vec, positions):
    return sum(1 << j for j, k in enumerate(positions) if vec >> k & 1)


# ------------------------------------------------------------------ GF(2^31)

POLY = (1 << 31) | (1 << 3) | 1


def gmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> 31 & 1:
            a ^= POLY
    return r


def gpow(a, e):
    r = 1
    while e:
        if e & 1:
            r = gmul(r, a)
        a = gmul(a, a)
        e >>= 1
    return r


def ginv(a):
    return gpow(a, (1 << 31) - 2)


def field_is_valid():
    """x^31 + x^3 + 1 has no root, and x^(2^31) = x modulo it, so every factor has degree 31: it is irreducible."""
    no_root = (POLY & 1) == 1 and bin(POLY).count("1") % 2 == 1
    return no_root and gpow(2, 1 << 31) == 2


def rank_over_field(matrix):
    rows = [list(r) for r in matrix]
    rank, cols = 0, len(rows[0]) if rows else 0
    for c in range(cols):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][c]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = ginv(rows[rank][c])
        rows[rank] = [gmul(inv, x) for x in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][c]:
                f = rows[i][c]
                rows[i] = [x ^ gmul(f, y) for x, y in zip(rows[i], rows[rank])]
        rank += 1
    return rank


# ------------------------------------------------------------------ laws

class Law:
    def __init__(self, name, ntypes, constraints):
        self.name, self.n, self.constraints = name, ntypes, constraints

    def matrix_at(self, u, v):
        rows = []
        for terms in self.constraints:
            row = [0] * self.n
            for t, (a, b) in terms:
                ua = gpow(u, a) if a >= 0 else gpow(ginv(u), -a)
                vb = gpow(v, b) if b >= 0 else gpow(ginv(v), -b)
                row[t] ^= gmul(ua, vb)
            rows.append(row)
        return rows

    def generic_rank(self, rng, points=5, fixed=None):
        if fixed is not None:
            return rank_over_field(self.matrix_at(*fixed))
        best = 0
        for _ in range(points):
            u, v = rng.randrange(2, 1 << 31), rng.randrange(2, 1 << 31)
            best = max(best, rank_over_field(self.matrix_at(u, v)))
        return best

    def constraint_sets(self, radius):
        out = []
        for p in box(radius):
            for terms in self.constraints:
                out.append([(t, (p[0] + a, p[1] + b)) for t, (a, b) in terms])
        return out


def box(r):
    return [(i, j) for i in range(-r, r + 1) for j in range(-r, r + 1)]


def window(law, r):
    return [(t, s) for s in box(r) for t in range(law.n)]


def system(law, radius):
    cons = law.constraint_sets(radius)
    variables = sorted({x for c in cons for x in c})
    index = {x: k for k, x in enumerate(variables)}
    rows = []
    for c in cons:
        mask = 0
        for x in c:
            mask ^= 1 << index[x]
        rows.append((mask, 0))
    return variables, index, rows


def finite_moves(law, radius):
    """Homogeneous solutions supported on sites within radius - 1, subject to every constraint anchored within radius."""
    variables, index, rows = system(law, radius)
    rows = rows + [(1 << index[x], 0) for x in variables if max(abs(x[1][0]), abs(x[1][1])) > radius - 1]
    _, basis = solve(len(variables), rows)
    return variables, index, basis


def projection(law, radius, keys):
    variables, index, rows = system(law, radius)
    x0, basis = solve(len(variables), rows)
    pos = [index[k] for k in keys]
    return span_basis(compress(b, pos) for b in basis)


def same_span(a, b):
    def red(v, basis):
        while v:
            top = v.bit_length() - 1
            if top not in basis:
                return v
            v ^= basis[top]
        return 0
    return len(a) == len(b) and not any(red(x, b) for x in a.values())


def entropy_profile(law):
    rows = []
    for n in (2, 3, 4):
        keys = window(law, n)
        upper = len(projection(law, n + 1, keys))
        variables, index, basis = finite_moves(law, n + 1)
        lower = len(span_basis(compress(b, [index[k] for k in keys]) for b in basis))
        rows.append({"box_radius": n, "variables": len(keys), "lower": lower, "upper": upper})
    return rows


def knot_census(law, use_inner=True, cap=40):
    keys = window(law, 1)
    proj = [projection(law, r, keys) for r in (4, 5)]
    stable = same_span(proj[0], proj[1])
    span = proj[0]
    if use_inner:
        variables, index, moves = finite_moves(law, 4)
    else:
        variables, index, rows = system(law, 4)
        _, moves = solve(len(variables), rows)
    native = 0
    for j, k in enumerate(keys):
        if any(m >> index[k] & 1 for m in moves):
            native |= 1 << j
    nvars = len(keys)
    fixed = [f for f in range(1, 1 << nvars) if not any(parity(f & b) for b in span.values())]
    fixed_set = set(fixed)
    minimal = []
    for f in sorted(fixed, key=lambda x: bin(x).count("1")):
        sub = (f - 1) & f
        proper = False
        while sub:
            if sub in fixed_set:
                proper = True
                break
            sub = (sub - 1) & f
        if not proper:
            minimal.append(f)
    big = [f for f in minimal if bin(f).count("1") >= 3]
    vecs = list(span.values())
    verdicts = mismatches = 0
    for f in big[:cap]:
        members = [j for j in range(nvars) if f >> j & 1]
        pts = set()
        for bits in product((0, 1), repeat=len(vecs)):
            v = 0
            for b, on in zip(vecs, bits):
                if on:
                    v ^= b
            pts.add(tuple(bool(v >> j & 1) for j in members))
        names = tuple(f"v{j}" for j in members)
        verdict = check_knot(Relation(names, frozenset(pts)), names[:-1], names[-1]).is_knot
        verdicts += 1
        mismatches += not verdict
    non_minimal = [f for f in fixed if f not in set(minimal) and bin(f).count("1") >= 3][:10]
    false_knots = 0
    for f in non_minimal:
        members = [j for j in range(nvars) if f >> j & 1]
        pts = set()
        for bits in product((0, 1), repeat=len(vecs)):
            v = 0
            for b, on in zip(vecs, bits):
                if on:
                    v ^= b
            pts.add(tuple(bool(v >> j & 1) for j in members))
        names = tuple(f"v{j}" for j in members)
        false_knots += check_knot(Relation(names, frozenset(pts)), names[:-1], names[-1]).is_knot
    native_knots = sum(1 for f in big if f & native == f)
    return {"window_variables": nvars, "stable": stable, "native_variables": bin(native).count("1"),
            "open_variables": sum(1 for j in range(nvars) if (1 << j) not in fixed_set),
            "minimal_fixed_supports": len(big), "smallest": min((bin(f).count("1") for f in big), default=None),
            "knotlab_checked": verdicts, "knotlab_rejected_minimal": mismatches,
            "non_minimal_checked": len(non_minimal), "non_minimal_called_knots": false_knots,
            "native_knots": native_knots}


def world_independence(law, seed):
    """Solve, at two random solutions, which window variables a change inside the box can flip."""
    rng = random.Random(seed)
    variables, index, rows = system(law, 4)
    x0, basis = solve(len(variables), rows)
    keys = window(law, 1)
    outside = [x for x in variables if max(abs(x[1][0]), abs(x[1][1])) > 3]
    answers = []
    for _ in range(2):
        s = x0
        for b in basis:
            if rng.random() < 0.5:
                s ^= b
        flippable = []
        for k in keys:
            extra = [(1 << index[x], s >> index[x] & 1) for x in outside]
            extra.append((1 << index[k], 1 - (s >> index[k] & 1)))
            flippable.append(solve(len(variables), rows + extra) is not None)
        answers.append(flippable)
    return {"same_at_two_worlds": answers[0] == answers[1], "flippable": sum(answers[0])}


def colouring_worlds():
    """The same procedure on a non-linear law: 3-colourings of a 5x5 box, flat world against plane world."""
    n = 5
    cells = [(i, j) for j in range(n) for i in range(n)]

    def flippable(colour):
        out = 0
        for target in [(2, 2)]:
            for c in range(3):
                if c == colour(target):
                    continue
                assign = {u: colour(u) for u in cells if u[0] in (0, n - 1) or u[1] in (0, n - 1)}
                inner = [u for u in cells if u not in assign]
                found = False

                def rec(k):
                    nonlocal found
                    if found:
                        return
                    if k == len(inner):
                        found = True
                        return
                    u = inner[k]
                    choices = [c] if u == target else range(3)
                    for col in choices:
                        if all(assign.get(w) != col for w in ((u[0] + 1, u[1]), (u[0] - 1, u[1]), (u[0], u[1] + 1), (u[0], u[1] - 1))):
                            assign[u] = col
                            rec(k + 1)
                            del assign[u]

                rec(0)
                out += found
        return out > 0

    flat = flippable(lambda v: (v[0] + v[1]) % 2)
    plane = flippable(lambda v: (v[0] + v[1]) % 3)
    return {"flat_world_flippable": flat, "plane_world_flippable": plane, "same_at_two_worlds": flat == plane}


def laws():
    tseitin = Law("Tseitin", 2, [[(0, (0, 0)), (0, (-1, 0)), (1, (0, 0)), (1, (0, -1))]])
    gauge = Law("gauge (plaquette)", 2, [[(0, (0, 0)), (0, (0, 1)), (1, (0, 0)), (1, (1, 0))]])
    ledrappier = Law("Ledrappier", 1, [[(0, (0, 0)), (0, (1, 0)), (0, (0, 1))]])
    combined = Law("Tseitin and gauge together", 2, tseitin.constraints + gauge.constraints)
    shifted = Law("gauge with a shifted copy", 2, gauge.constraints + [[(t, (a + 1, b)) for t, (a, b) in gauge.constraints[0]]])
    out = [tseitin, gauge, ledrappier, combined, shifted]
    rng = random.Random(20261020)
    offsets = [(0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1)]
    for k, (n, m) in enumerate([(1, 1), (1, 1), (2, 1), (2, 1), (2, 2), (2, 2)]):
        cons = []
        for _ in range(m):
            terms = rng.sample([(t, o) for t in range(n) for o in offsets], 3 + rng.randrange(2))
            cons.append(sorted(terms))
        out.append(Law(f"random law {k} ({n} types, {m} constraints)", n, cons))
    return out


def run():
    checks, controls, failures = {}, {}, []
    rng = random.Random(7)
    checks["field_irreducible"] = field_is_valid()
    if not checks["field_irreducible"]:
        failures.append("GF(2^31) modulus is not irreducible")
    rows = []
    for law in laws():
        rank = law.generic_rank(rng)
        moves = {r: len(finite_moves(law, r)[2]) for r in (3, 4)}
        deficit = rank < law.n
        row = {"law": law.name, "types": law.n, "constraints": len(law.constraints), "generic_rank": rank,
               "rank_deficit": deficit, "finite_moves_by_radius": moves, "entropy": entropy_profile(law)}
        row["moves_iff_deficit"] = (moves[4] > 0) == deficit
        if not row["moves_iff_deficit"]:
            failures.append(f"Theorem 3 on {law.name}")
        ent = row["entropy"]
        if deficit and not ent[-1]["lower"] >= ent[0]["lower"] > 0:
            failures.append(f"positive entropy lower bound on {law.name}")
        if not deficit and not (ent[-1]["upper"] / ent[-1]["variables"] < ent[0]["upper"] / ent[0]["variables"]
                                and all(e["lower"] == 0 for e in ent)):
            failures.append(f"zero entropy trend on {law.name}")
        rows.append(row)
    checks["theorem_3_laws"] = rows

    census = {}
    for law in laws()[:5]:
        c = knot_census(law)
        census[law.name] = c
        if not c["stable"] or c["knotlab_rejected_minimal"] or c["non_minimal_called_knots"]:
            failures.append(f"Theorem 2 on {law.name}")
    checks["theorem_2_knots"] = census
    if not (census["Tseitin"]["native_knots"] == census["Tseitin"]["minimal_fixed_supports"] > 0
            and census["gauge (plaquette)"]["native_knots"] == census["gauge (plaquette)"]["minimal_fixed_supports"] > 0
            and census["Ledrappier"]["minimal_fixed_supports"] > 0 and census["Ledrappier"]["native_knots"] == 0
            and census["Tseitin and gauge together"]["minimal_fixed_supports"] > 0
            and census["Tseitin and gauge together"]["native_knots"] == 0):
        failures.append("native knots: expected all native for Tseitin and gauge, none for Ledrappier and the combined law")

    worlds = {law.name: world_independence(law, 3) for law in laws()[:5]}
    checks["theorem_1_world_independence"] = worlds
    if not all(w["same_at_two_worlds"] for w in worlds.values()):
        failures.append("Theorem 1: a linear law's flippable variables depend on the world")

    bad_rank = laws()[3].generic_rank(rng, fixed=(1, 1))
    controls["rank_at_a_point_where_entries_vanish"] = {"law": laws()[3].name, "rank": bad_rank,
                                                         "rejected": (bad_rank < 2) != (len(finite_moves(laws()[3], 4)[2]) > 0)}
    wrong = knot_census(laws()[2], use_inner=False)
    controls["nativity_from_boundary_supported_solutions"] = {"law": "Ledrappier", "native_knots": wrong["native_knots"],
                                                             "rejected": wrong["native_knots"] > 0}
    colour = colouring_worlds()
    controls["world_independence_on_a_non_linear_law"] = {**colour, "rejected": not colour["same_at_two_worlds"]}
    for name, control in controls.items():
        if not control.get("rejected"):
            failures.append(f"control not rejected: {name}")
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
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if write:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: failures {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
