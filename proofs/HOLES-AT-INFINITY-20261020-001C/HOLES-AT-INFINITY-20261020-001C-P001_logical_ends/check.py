#!/usr/bin/env python3
"""Checks for HOLES-AT-INFINITY-20261020-001C-P001: the ends of a constraint system.

A locally finite constraint system is studied through its truncations: the
constraints anchored in a box of radius R, with all their variables. By
compactness, the relation among finitely many variables is the relation of
every large enough truncation (Proposition 3); the checks confirm stability in
R.

- Linear systems (Theorem 2): Tseitin on the square grid and Ledrappier's
  system on Z^2. The homogeneous solutions supported inside a box are the
  system's finite loops; together with the projection onto the variables near
  the origin they give the type of every parity: fixed, loop-supplied or
  end-supplied.
- Two-literal systems (Proposition 4): random planted two-literal systems on Z
  and an equality chain, with a three-literal parity as the control.
- Rigid legs: a not-all-equal knot whose variables equality rays make rigid.
- Trends (Theorem 5): the implication chain; proper 3-colourings of the square
  grid (the flat class is dense by height-function patching, and the plane
  colouring is frozen); and the boundary circle of the one-way ladder.

Each check is also run on a deliberately wrong input, which it must reject.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from knotlab.knots import check_knot  # noqa: E402
from knotlab.relations import Relation  # noqa: E402


def parity(x: int) -> int:
    return bin(x).count("1") & 1


# ------------------------------------------------------------------ GF(2), as in ticket B

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


def reduce(v, basis):
    while v:
        top = v.bit_length() - 1
        if top not in basis:
            return v
        v ^= basis[top]
    return 0


def compress(vec, positions):
    return sum(1 << j for j, k in enumerate(positions) if vec >> k & 1)


class Projection:
    def __init__(self, x0, basis, positions):
        self.n = len(positions)
        self.span = span_basis(compress(b, positions) for b in basis)
        self.x0 = reduce(compress(x0, positions), self.span)

    def constant(self, f):
        if any(parity(f & b) for b in self.span.values()):
            return None
        return parity(f & self.x0)

    def same(self, other):
        if self.n != other.n or len(self.span) != len(other.span):
            return False
        if any(reduce(b, other.span) for b in self.span.values()):
            return False
        return reduce(self.x0 ^ other.x0, self.span) == 0

    def points(self):
        vecs = list(self.span.values())
        out = set()
        for bits in product((0, 1), repeat=len(vecs)):
            v = self.x0
            for b, on in zip(vecs, bits):
                if on:
                    v ^= b
            out.add(v)
        return out


# ------------------------------------------------------------------ linear systems on Z^2

def box(radius):
    return [(i, j) for i in range(-radius, radius + 1) for j in range(-radius, radius + 1)]


def ekey(u, v):
    return (u, v) if u <= v else (v, u)


class TseitinGrid:
    name = "Tseitin system on the square grid"

    def constraint(self, v):
        x, y = v
        return [ekey(v, w) for w in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))], int(v == (0, 0))

    def near(self, r):
        return sorted({e for v in box(r) for e in self.constraint(v)[0]})

    def radius(self, e):
        return max(max(abs(a), abs(b)) for a, b in e)


class Ledrappier:
    name = "Ledrappier's system on Z^2"

    def constraint(self, v):
        i, j = v
        return [(i, j), (i + 1, j), (i, j + 1)], 0

    def near(self, r):
        return box(r)

    def radius(self, s):
        return max(abs(s[0]), abs(s[1]))


def truncation(system, radius):
    cons = [system.constraint(a) for a in box(radius)]
    variables = sorted({x for vs, _ in cons for x in vs})
    index = {x: k for k, x in enumerate(variables)}
    rows = [(sum(1 << index[x] for x in vs), rhs) for vs, rhs in cons]
    return variables, index, rows


def linear_type_check(system, r, radius, interior_only=True):
    keys = system.near(r)
    projections = []
    for extra in range(3):
        variables, index, rows = truncation(system, radius + extra)
        projections.append(Projection(*solve(len(variables), rows), [index[k] for k in keys]))
    stable = all(p.same(projections[0]) for p in projections[1:])
    proj = projections[0]
    variables, index, rows = truncation(system, radius)
    homogeneous = [(mask, 0) for mask, _ in rows]
    if interior_only:
        homogeneous += [(1 << index[x], 0) for x in variables if system.radius(x) > radius - 1]
    _, inner = solve(len(variables), homogeneous)
    loops = span_basis(compress(b, [index[k] for k in keys]) for b in inner)
    counts = {"fixed": 0, "loop": 0, "end": 0}
    inconsistent = 0
    for f in range(1 << len(keys)):
        value = proj.constant(f)
        loop = any(parity(f & b) for b in loops.values())
        if value is not None:
            counts["fixed"] += 1
            inconsistent += loop
        elif loop:
            counts["loop"] += 1
        else:
            counts["end"] += 1
    return {"system": system.name, "near_variables": len(keys), "inner_loop_dimension": len(inner),
            "counts": counts, "loop_on_fixed_parity": inconsistent, "stable_in_radius": stable,
            "radius": radius}, proj, keys


def ledrappier_triangle_knot():
    system = Ledrappier()
    keys = [(0, 0), (1, 0), (0, 1)]
    variables, index, rows = truncation(system, 4)
    proj = Projection(*solve(len(variables), rows), [index[k] for k in keys])
    names = ("s00", "s10", "s01")
    relation = Relation(names, frozenset(tuple(bool(p >> j & 1) for j in range(3)) for p in proj.points()))
    report = check_knot(relation, names[:2], names[2])
    return {"states": len(relation.rows), "is_knot": report.is_knot, "pairwise_definable": report.pairwise_definable}


# ------------------------------------------------------------------ small Boolean systems

def solutions(variables, clauses, fixed=None):
    """Every satisfying assignment, as a dict, by depth-first search; a clause is tested when its last free variable is set."""
    fixed = dict(fixed or {})
    order = [v for v in variables if v not in fixed]
    position = {v: k for k, v in enumerate(order)}
    by_last = {v: [] for v in order}
    upfront = []
    for clause in clauses:
        free = [x for x, _ in clause if x not in fixed]
        if free:
            by_last[max(free, key=position.get)].append(clause)
        else:
            upfront.append(clause)

    def sat(clause, assign):
        return any(assign[x] == pos for x, pos in clause)

    if not all(sat(c, fixed) for c in upfront):
        return []
    out = []
    assign = dict(fixed)

    def rec(k):
        if k == len(order):
            out.append(dict(assign))
            return
        var = order[k]
        for val in (False, True):
            assign[var] = val
            if all(sat(c, assign) for c in by_last[var]):
                rec(k + 1)
        del assign[var]

    rec(0)
    return out


def planted_two_literal(seed, radius):
    """A satisfiable two-literal system on Z, generated anchor by anchor; truncated to anchors in [-radius, radius]."""
    def planted(i):
        return random.Random(f"{seed}:a:{i}").random() < 0.5

    clauses = []
    for i in range(-radius, radius + 1):
        rng = random.Random(f"{seed}:c:{i}")
        for step in (1, 2):
            a, b = f"x{i}", f"x{i + step}"
            sa, sb = rng.random() < 0.5, rng.random() < 0.5
            if planted(i) != sa and planted(i + step) != sb:
                sa = not sa
            clauses.append(((a, sa), (b, sb)))
    variables = [f"x{i}" for i in range(-radius, radius + 3)]
    return variables, clauses


def relation_of(sols, names):
    return Relation(tuple(names), frozenset(tuple(s[n] for n in names) for s in sols))


def two_literal_check(seeds, add_parity=False):
    knots = not_closed = unstable = triples = 0
    for seed in seeds:
        rels = []
        for radius in (5, 6, 7):
            variables, clauses = planted_two_literal(seed, radius)
            if add_parity:
                variables = variables + ["y1", "y2", "y3"]
                clauses = clauses + [tuple((f"y{k + 1}", bool(s >> k & 1)) for k in range(3))
                                     for s in range(8) if bin(s).count("1") % 2 == 1]
            sols = solutions(variables, clauses)
            names = [f"x{i}" for i in range(-2, 3)] + (["y1", "y2", "y3"] if add_parity else [])
            rels.append({t: relation_of(sols, t) for t in combinations(names, 3)})
        for t, rel in rels[0].items():
            triples += 1
            unstable += any(r[t] != rel for r in rels[1:])
            if not rel.is_majority_closed():
                not_closed += 1
            if len(rel.rows) and check_knot(rel, t[:2], t[2]).is_knot:
                knots += 1
    return {"systems": len(seeds), "triples": triples, "knots": knots, "not_majority_closed": not_closed,
            "unstable": unstable}


def equality_chain(length, free=False):
    variables = [f"x{i}" for i in range(length)]
    clauses = [] if free else [c for i in range(length - 1)
                               for c in (((f"x{i}", False), (f"x{i + 1}", True)), ((f"x{i}", True), (f"x{i + 1}", False)))]
    open_bit = {s["x0"] for s in solutions(variables, clauses)} == {False, True}
    tail = {variables[-1]: False, variables[-2]: False}
    changes = len(solutions(variables, clauses, tail))
    return {"x0_open": open_bit, "solutions_with_tail_fixed": changes}


def rigid_legs(length, centre="nae"):
    names = {leg: [f"{leg}{i}" for i in range(1, length + 1)] for leg in "abc"}
    variables = [v for leg in "abc" for v in names[leg]]
    if centre == "nae":
        clauses = [(("a1", True), ("b1", True), ("c1", True)), (("a1", False), ("b1", False), ("c1", False))]
    else:
        clauses = [(("a1", True), ("b1", True))]
    for leg in "abc":
        for u, w in zip(names[leg], names[leg][1:]):
            clauses += [((u, False), (w, True)), ((u, True), (w, False))]
    sols = solutions(variables, clauses)
    rel = relation_of(sols, ["a1", "b1", "c1"])
    report = check_knot(rel, ("a1", "b1"), "c1")
    ref = sols[0]
    tails = {names[leg][-1]: ref[names[leg][-1]] for leg in "abc"}
    return {"centre": centre, "states": len(rel.rows), "is_knot": report.is_knot,
            "majority_closed": rel.is_majority_closed(),
            "solutions_with_leg_ends_fixed": len(solutions(variables, clauses, tails))}


# ------------------------------------------------------------------ trends

def implication_chain(radius):
    variables = [f"x{i}" for i in range(-radius, radius + 1)]
    clauses = [((f"x{i}", False), (f"x{i + 1}", True)) for i in range(-radius, radius)]
    window = [f"x{i}" for i in range(-2, 3)]
    allowed = {tuple(s[n] for n in window) for s in solutions(variables, clauses)}
    thresholds = {tuple(i >= k for i in range(-2, 3)) for k in range(-3, 4)}
    zero = len(solutions(variables, clauses, {f"x{radius}": False}))
    one = len(solutions(variables, clauses, {f"x{-radius}": True}))
    middle = len(solutions(variables, clauses, {f"x{-radius}": False, f"x{radius}": True}))
    return {"window_patterns": len(allowed), "thresholds_cover_window": allowed == thresholds,
            "finite_changes_of_all_zero": zero - 1, "finite_changes_of_all_one": one - 1,
            "finite_changes_of_a_threshold": middle - 1}


def height_of(colours, cells):
    """Lift a proper 3-colouring of a box to a height function (adjacent heights differ by 1, height = colour mod 3)."""
    start = cells[0]
    h = {start: colours[start]}
    stack = [start]
    while stack:
        u = stack.pop()
        for w in ((u[0] + 1, u[1]), (u[0] - 1, u[1]), (u[0], u[1] + 1), (u[0], u[1] - 1)):
            if w in colours and w not in h:
                h[w] = h[u] + (1 if (colours[w] - colours[u]) % 3 == 1 else -1)
                stack.append(w)
    for u in cells:
        for w in ((u[0] + 1, u[1]), (u[0], u[1] + 1)):
            if w in colours and abs(h[u] - h[w]) != 1:
                return None
    return h


def random_colouring(rng, cells):
    colours = {}

    def rec(k):
        if k == len(cells):
            return True
        u = cells[k]
        for c in rng.sample(range(3), 3):
            if all(colours.get(w) != c for w in ((u[0] - 1, u[1]), (u[0], u[1] - 1))):
                colours[u] = c
                if rec(k + 1):
                    return True
                del colours[u]
        return False

    rec(0)
    return colours


def patch(base, window_colours, radius):
    """max(H, base) with H the cone from the shifted window heights; returns the patched heights on the box."""
    cells = sorted(window_colours)
    h = height_of(window_colours, cells)
    if (h[cells[0]] - base(cells[0])) % 2:
        h = {u: v + 3 for u, v in h.items()}
    shift = 0
    while min(h[u] + shift - base(u) for u in cells) < 1:
        shift += 6
    out = {}
    for v in box(radius):
        cone = max(h[w] + shift - abs(v[0] - w[0]) - abs(v[1] - w[1]) for w in cells)
        out[v] = max(cone, base(v))
    return out


def patch_check(base, patterns, seed, radius=24):
    rng = random.Random(seed)
    window = [(i, j) for j in range(-1, 3) for i in range(-1, 3)]
    valid = matches = finite = 0
    reach = 0
    for _ in range(patterns):
        t = random_colouring(rng, window)
        g = patch(base, t, radius)
        ok = all(abs(g[u] - g[w]) == 1 for u in g for w in ((u[0] + 1, u[1]), (u[0], u[1] + 1)) if w in g)
        valid += ok
        matches += all(g[u] % 3 == t[u] for u in window)
        changed = [max(abs(u[0]), abs(u[1])) for u in g if g[u] != base(u)]
        r = max(changed, default=0)
        reach = max(reach, r)
        finite += r < radius - 2
    return {"patterns": patterns, "valid": valid, "match_window": matches, "change_inside_box": finite,
            "largest_change_radius": reach, "box_radius": radius}


def frozen_count(colour, n, cap=2):
    """Proper 3-colourings of an n-by-n box agreeing with colour on its boundary ring (counted up to cap)."""
    cells = [(i, j) for j in range(n) for i in range(n)]
    ring = {u for u in cells if u[0] in (0, n - 1) or u[1] in (0, n - 1)}
    inner = [u for u in cells if u not in ring]
    assign = {u: colour(u) for u in ring}
    count = 0

    def rec(k):
        nonlocal count
        if count >= cap:
            return
        if k == len(inner):
            count += 1
            return
        u = inner[k]
        for c in range(3):
            if all(assign.get(w) != c for w in ((u[0] + 1, u[1]), (u[0] - 1, u[1]), (u[0], u[1] + 1), (u[0], u[1] - 1))):
                assign[u] = c
                rec(k + 1)
                del assign[u]

    rec(0)
    return count


def ladder_circle(radius):
    """The boundary double ray of the one-way ladder is even everywhere and meets every fixed parity evenly."""
    def nbrs(v):
        i, s = v
        out = {(i + 1, s), (i, 1 - s)}
        if i > 0:
            out.add((i - 1, s))
        return out

    verts = [(i, s) for i in range(radius + 1) for s in (0, 1)]
    edges = sorted({tuple(sorted((u, w))) for u in verts for w in nbrs(u)})
    index = {e: k for k, e in enumerate(edges)}
    rows = [(sum(1 << index[tuple(sorted((u, w)))] for w in nbrs(u)), int(u == (0, 0))) for u in verts]
    circle = {e for e in edges if e[0][1] == e[1][1]} | {((0, 0), (0, 1))}
    near = [e for e in edges if max(e[0][0], e[1][0]) <= 2]
    proj = Projection(*solve(len(edges), rows), [index[e] for e in near])
    dmask = sum(1 << j for j, e in enumerate(near) if e in circle)
    fixed = [f for f in range(1 << len(near)) if proj.constant(f) is not None]
    even_degree = all(sum(1 for w in nbrs(u) if tuple(sorted((u, w))) in circle) % 2 == 0 for u in verts if u[0] < radius)
    return {"near_edges": len(near), "fixed_parities": len(fixed), "even_degree_inside": even_degree,
            "meets_every_fixed_parity_evenly": all(parity(f & dmask) == 0 for f in fixed),
            "readable_difference": any(parity(f & dmask) for f in range(1 << len(near)))}


# ------------------------------------------------------------------ run

def run():
    checks, controls, failures = {}, {}, []

    grid_row, _, _ = linear_type_check(TseitinGrid(), 1, 5)
    led_row, _, _ = linear_type_check(Ledrappier(), 1, 5)
    checks["theorem_2_linear_types"] = [grid_row, led_row]
    if grid_row["counts"]["end"] or not grid_row["counts"]["loop"] or grid_row["loop_on_fixed_parity"] or not grid_row["stable_in_radius"]:
        failures.append("Theorem 2 on the Tseitin grid")
    if led_row["inner_loop_dimension"] or led_row["counts"]["loop"] or not led_row["counts"]["end"] or not led_row["stable_in_radius"]:
        failures.append("Theorem 2 on Ledrappier's system")
    dims = {r: linear_type_check(Ledrappier(), 1, r)[0]["inner_loop_dimension"] for r in (3, 4, 6, 7)}
    checks["ledrappier_no_finite_loops"] = dims
    if any(dims.values()):
        failures.append("Ledrappier's system has a finitely supported homogeneous solution")
    tri = ledrappier_triangle_knot()
    checks["ledrappier_triangle"] = tri
    if not tri["is_knot"] or tri["states"] != 4:
        failures.append("Ledrappier's triangle is not a parity knot")
    boundary, _, _ = linear_type_check(Ledrappier(), 1, 5, interior_only=False)
    controls["theorem_2_boundary_supported_solutions_counted_as_loops"] = {
        "inner_loop_dimension": boundary["inner_loop_dimension"], "loop": boundary["counts"]["loop"],
        "rejected": boundary["counts"]["loop"] > 0}

    seeds = list(range(12))
    two = two_literal_check(seeds)
    checks["proposition_4_two_literal"] = two
    if two["knots"] or two["not_majority_closed"] or two["unstable"]:
        failures.append("Proposition 4")
    with_parity = two_literal_check(seeds[:3], add_parity=True)
    controls["proposition_4_three_literal_parity_added"] = {**with_parity, "rejected": with_parity["knots"] > 0}
    chain = equality_chain(9)
    checks["proposition_4_equality_chain"] = chain
    if not chain["x0_open"] or chain["solutions_with_tail_fixed"] != 1:
        failures.append("the equality chain's bit is not open and rigid")
    free = equality_chain(9, free=True)
    controls["rigidity_on_an_unconstrained_chain"] = {**free, "rejected": free["solutions_with_tail_fixed"] != 1}

    legs = rigid_legs(5)
    checks["rigid_legs_not_all_equal"] = legs
    if not legs["is_knot"] or legs["majority_closed"] or legs["solutions_with_leg_ends_fixed"] != 1:
        failures.append("the not-all-equal knot with rigid legs")
    pair = rigid_legs(5, centre="pair")
    controls["rigid_legs_two_literal_centre"] = {**pair, "rejected": not pair["is_knot"]}

    chain_trend = implication_chain(6)
    checks["theorem_5_implication_chain"] = chain_trend
    if not (chain_trend["thresholds_cover_window"] and chain_trend["finite_changes_of_all_zero"] == 0
            and chain_trend["finite_changes_of_all_one"] == 0 and chain_trend["finite_changes_of_a_threshold"] > 0):
        failures.append("Theorem 5 on the implication chain")

    flat = lambda v: (v[0] + v[1]) % 2  # noqa: E731
    plane = lambda v: v[0] + v[1]  # noqa: E731
    dense = patch_check(flat, 150, 20261020)
    checks["theorem_5_colourings_flat_class_dense"] = dense
    if not (dense["valid"] == dense["match_window"] == dense["change_inside_box"] == dense["patterns"]):
        failures.append("Theorem 5: patching into the flat colouring")
    steep = patch_check(plane, 20, 7)
    controls["theorem_5_patching_into_the_frozen_plane"] = {**steep, "rejected": steep["change_inside_box"] < steep["patterns"]}
    frozen = {n: frozen_count(lambda v: (v[0] + v[1]) % 3, n) for n in (4, 5, 6)}
    flexible = {n: frozen_count(lambda v: (v[0] + v[1]) % 2, n) for n in (4, 5, 6)}
    checks["theorem_5_plane_frozen"] = {"plane_colourings_with_boundary": frozen, "flat_colourings_with_boundary": flexible}
    if any(c != 1 for c in frozen.values()):
        failures.append("Theorem 5: the plane colouring is not frozen")
    controls["theorem_5_frozen_test_on_flat"] = {"counts": flexible, "rejected": any(c != 1 for c in flexible.values())}

    circle = ladder_circle(12)
    checks["theorem_5_ladder_circle"] = circle
    if not (circle["even_degree_inside"] and circle["meets_every_fixed_parity_evenly"] and circle["readable_difference"]):
        failures.append("Theorem 5: the ladder's boundary circle")

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
