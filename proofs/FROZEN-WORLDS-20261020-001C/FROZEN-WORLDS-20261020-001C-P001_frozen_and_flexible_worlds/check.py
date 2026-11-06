#!/usr/bin/env python3
"""Checks for FROZEN-WORLDS-20261020-001C-P001: colourings have frozen and flexible worlds.

A world is a solution. A vertex is flexible at a world if some solution that
differs from it in finitely many vertices recolours it. On a finite box this is
tested by fixing the world on the box's boundary ring and searching the inside
for a completion that recolours the vertex. Every proper colouring of a box of
Z^2 extends to all of Z^2 (HOLES-AT-INFINITY-20261020-001C-P001, Theorem 5(b)),
and every proper colouring of a finite subtree extends to the whole tree, so
relations computed on boxes and subtrees are the infinite ones.

- Z^2: the star knot among three neighbours of a vertex; the plane colouring is
  frozen and the flat colouring flexible; flexibility at random worlds of the
  flat class; the knot's nativity at both kinds of world.
- The 3-regular tree: a frozen colouring and a flexible one; the star knot; a
  height-function patch into the flexible colouring.
- The hard-core law: every vertex flexible at random worlds; no K1-K3 knot among
  three variables near the origin.

Each check also runs on a deliberately wrong input, which it must reject.

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


def knot_finite(rows, domains):
    """K1-K3 for a relation over finite domains: constrained, every one-variable-forgotten projection full, nonempty."""
    rows = set(rows)
    full = 1
    for d in domains:
        full *= d
    k1 = len(rows) < full
    k3 = bool(rows)
    k2 = True
    for i in range(len(domains)):
        rest = {r[:i] + r[i + 1:] for r in rows}
        size = full // domains[i]
        k2 &= len(rest) == size
    return k1 and k2 and k3


# ------------------------------------------------------------------ colourings of Z^2

def grid_nbrs(v):
    x, y = v
    return ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))


def complete(cells, nbrs, fixed, forced=None, cap=1):
    """Count (up to cap) proper 3-colourings of cells that agree with fixed and avoid forced[v] at each v.

    Depth-first search choosing the cell with the fewest remaining colours and removing each chosen colour from
    the free neighbours (forward checking)."""
    forced = forced or {}
    cellset = set(cells)
    for u in fixed:
        if any(w in fixed and fixed[w] == fixed[u] for w in nbrs(u)):
            return 0
    domains = {}
    for u in cells:
        if u in fixed:
            continue
        dom = {0, 1, 2} - set(forced.get(u, ()))
        dom -= {fixed[w] for w in nbrs(u) if w in fixed}
        if not dom:
            return 0
        domains[u] = frozenset(dom)
    adjacent = {u: {w for w in nbrs(u) if w in domains and w in cellset} for u in domains}
    count = 0

    def rec(doms):
        nonlocal count
        if count >= cap:
            return
        if not doms:
            count += 1
            return
        u = min(doms, key=lambda x: (len(doms[x]), repr(x)))
        for c in sorted(doms[u]):
            new = {}
            ok = True
            for w, d in doms.items():
                if w == u:
                    continue
                if w in adjacent[u] and c in d:
                    d = d - {c}
                    if not d:
                        ok = False
                        break
                new[w] = d
            if ok:
                rec(new)
            if count >= cap:
                return

    rec(domains)
    return count


def rect(x0, x1, y0, y1):
    return [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)]


def projection_z2(triple, cells):
    allowed = set()
    for colours in product(range(3), repeat=3):
        fixed = dict(zip(triple, colours))
        if any(fixed[a] == fixed[b] for a, b in combinations(triple, 2) if b in grid_nbrs(a)):
            continue
        if complete(cells, grid_nbrs, fixed):
            allowed.add(colours)
    return allowed


def ring_of(cells):
    xs = [c[0] for c in cells]
    ys = [c[1] for c in cells]
    return {c for c in cells if c[0] in (min(xs), max(xs)) or c[1] in (min(ys), max(ys))}


def flexible_vertices(world, cells, targets, nbrs=grid_nbrs, ring=None):
    """Which targets some completion of the box, with the boundary ring fixed to the world, recolours."""
    ring = ring_of(cells) if ring is None else ring
    fixed = {u: world[u] for u in ring}
    out = []
    for t in targets:
        out.append(complete(cells, nbrs, fixed, {t: (world[t],)}) > 0)
    return out


def random_flat_class_world(rng, radius, moves=40):
    world = {v: (v[0] + v[1]) % 2 for v in rect(-radius, radius, -radius, radius)}
    inner = [v for v in world if max(abs(v[0]), abs(v[1])) <= radius - 3]
    for _ in range(moves):
        v = rng.choice(inner)
        options = [c for c in range(3) if c != world[v] and all(world.get(w) != c for w in grid_nbrs(v))]
        if options:
            world[v] = rng.choice(options)
    return world


# ------------------------------------------------------------------ the 3-regular tree

def tree_nbrs(w):
    out = [w + (a,) for a in range(3) if not w or a != w[-1]]
    if w:
        out.append(w[:-1])
    return out


def tree_ball(depth):
    out, frontier = [()], [()]
    for _ in range(depth):
        frontier = [c for w in frontier for c in tree_nbrs(w) if len(c) > len(w)]
        out += frontier
    return out


def frozen_tree_colouring(depth):
    col = {(): 0}
    for w in tree_ball(depth):
        kids = [c for c in tree_nbrs(w) if len(c) > len(w)]
        if not w:
            colours = [1, 2, 1]
        else:
            colours = [(col[w] + 1) % 3, (col[w] + 2) % 3]
        for c, k in zip(kids, colours):
            col[c] = k
    return col


def tree_complete_count(depth, colouring, cap=2):
    cells = tree_ball(depth)
    fixed = {w: colouring[w] for w in cells if len(w) == depth}
    in_ball = set(cells)
    return complete(cells, lambda w: [c for c in tree_nbrs(w) if c in in_ball], fixed, cap=cap)


def tree_distance(a, b):
    k = 0
    while k < min(len(a), len(b)) and a[k] == b[k]:
        k += 1
    return len(a) + len(b) - 2 * k


def tree_patch(rng, patterns, window_depth=2):
    """Patch random colourings of a small ball into the depth-parity colouring with the height cone.

    Below a leaf of the window every path to the window passes through that leaf, so the cone there equals the
    leaf's cone minus the depth below it: the patched heights depend only on the leaf and the depth. Checking one
    descending path per leaf, down to where the cone is negative, therefore checks the whole infinite tree."""
    window = tree_ball(window_depth)
    leaves = [w for w in window if len(w) == window_depth]
    base = lambda w: len(w) % 2  # noqa: E731
    valid = finite = matches = 0
    deepest = 0
    for _ in range(patterns):
        t = {}
        for w in window:
            options = [c for c in range(3) if all(t.get(n) != c for n in tree_nbrs(w))]
            t[w] = rng.choice(options)
        h = {(): t[()]}
        for w in window[1:]:
            p = w[:-1]
            h[w] = h[p] + (1 if (t[w] - t[p]) % 3 == 1 else -1)
        if (h[()] - base(())) % 2:
            h = {w: x + 3 for w, x in h.items()}
        shift = -60
        while min(h[w] + shift - base(w) for w in window) < 1:
            shift += 6
        top = max(h[w] + shift for w in window)
        cells = list(window)
        ends = []
        for leaf in leaves:
            v = leaf
            while len(v) < top + window_depth + 3:
                v = next(c for c in tree_nbrs(v) if len(c) > len(v))
                cells.append(v)
            ends.append(v)
        cone = {v: max(h[w] + shift - tree_distance(v, w) for w in window) for v in cells}
        g = {v: max(cone[v], base(v)) for v in cells}
        in_cells = set(cells)
        ok = all(abs(g[v] - g[c]) == 1 for v in cells for c in tree_nbrs(v) if c in in_cells)
        valid += ok
        matches += all(g[w] % 3 == t[w] for w in window)
        finite += all(cone[v] < 0 for v in ends)
        deepest = max([deepest] + [len(v) for v in cells if g[v] != base(v)])
    return {"patterns": patterns, "valid": valid, "match_window": matches, "change_inside_ball": finite,
            "deepest_change": deepest}


# ------------------------------------------------------------------ the hard-core law

def hard_core_sets(cells):
    order = list(cells)
    out = []
    assign = {}

    def rec(k):
        if k == len(order):
            out.append(dict(assign))
            return
        u = order[k]
        for val in (0, 1):
            if val and any(assign.get(w) == 1 for w in grid_nbrs(u)):
                continue
            assign[u] = val
            rec(k + 1)
            del assign[u]

    rec(0)
    return out


def hard_core_flexible(rng, worlds=20, radius=4):
    """At random independent sets, every window vertex is changed by setting it and clearing its neighbours (or clearing it)."""
    cells = rect(-radius, radius, -radius, radius)
    flexible = total = 0
    for _ in range(worlds):
        world = {}
        for v in rng.sample(cells, len(cells)):
            world[v] = int(rng.random() < 0.5 and all(world.get(w) != 1 for w in grid_nbrs(v)))
        for v in rect(-1, 1, -1, 1):
            total += 1
            new = dict(world)
            if world[v]:
                new[v] = 0
            else:
                for w in grid_nbrs(v):
                    new[w] = 0
                new[v] = 1
            ok = all(not (new[u] and any(new.get(w) == 1 for w in grid_nbrs(u))) for u in cells)
            changed = {u for u in cells if new[u] != world[u]}
            flexible += ok and v in changed and all(max(abs(u[0] - v[0]), abs(u[1] - v[1])) <= 1 for u in changed)
    return {"window_vertices_checked": total, "flexible": flexible}


def hard_core_knots():
    cells = rect(-2, 2, -2, 2)
    sets = hard_core_sets(cells)
    names = rect(-1, 1, -1, 1)
    knots = not_closed = 0
    triples = 0
    for t in combinations(names, 3):
        rel = Relation(tuple(f"v{u}" for u in t), frozenset(tuple(bool(s[u]) for u in t) for s in sets))
        triples += 1
        knots += check_knot(rel, rel.variables[:2], rel.variables[2]).is_knot
        not_closed += not rel.is_majority_closed()
    return {"triples": triples, "knots": knots, "not_majority_closed": not_closed}


# ------------------------------------------------------------------ run

def run():
    checks, controls, failures = {}, {}, []
    rng = random.Random(20261020)

    star = [(0, 0), (1, 1), (2, 0)]
    proj = projection_z2(star, rect(-1, 3, -2, 2))
    not_distinct = {c for c in product(range(3), repeat=3) if len(set(c)) < 3}
    checks["theorem_2_star_knot_z2"] = {"allowed": len(proj), "equals_not_all_distinct": proj == not_distinct,
                                        "knot": knot_finite(proj, (3, 3, 3))}
    if not (proj == not_distinct and knot_finite(proj, (3, 3, 3))):
        failures.append("Theorem 2: star knot on Z^2")
    far = projection_z2([(0, 0), (2, 0), (4, 0)], rect(-1, 5, -2, 2))
    path = projection_z2([(0, 0), (1, 0), (2, 0)], rect(-1, 3, -2, 2))
    controls["theorem_2_triples_without_a_common_neighbour"] = {
        "spread_allowed": len(far), "spread_knot": knot_finite(far, (3, 3, 3)),
        "path_allowed": len(path), "path_knot": knot_finite(path, (3, 3, 3)),
        "rejected": not knot_finite(far, (3, 3, 3)) and not knot_finite(path, (3, 3, 3))}

    plane = lambda v: (v[0] + v[1]) % 3  # noqa: E731
    antiplane = lambda v: (v[0] - v[1]) % 3  # noqa: E731
    flat = lambda v: (v[0] + v[1]) % 2  # noqa: E731
    frozen = {}
    for name, colouring in (("plane", plane), ("antiplane", antiplane), ("flat", flat)):
        counts = {}
        for n in (4, 5, 6, 7):
            cells = rect(0, n - 1, 0, n - 1)
            ring = ring_of(cells)
            counts[n] = complete(cells, grid_nbrs, {u: colouring(u) for u in ring}, cap=2)
        frozen[name] = counts
    checks["theorem_1_frozen_boxes"] = frozen
    if any(c != 1 for c in frozen["plane"].values()) or any(c != 1 for c in frozen["antiplane"].values()):
        failures.append("Theorem 1: a plane colouring has a second completion")
    controls["theorem_1_frozen_test_on_flat"] = {"counts": frozen["flat"], "rejected": any(c != 1 for c in frozen["flat"].values())}

    window = rect(-1, 1, -1, 1)
    box6 = rect(-6, 6, -6, 6)
    flex_rows = []
    for _ in range(8):
        world = random_flat_class_world(rng, 6)
        flex_rows.append(all(flexible_vertices(world, box6, window)))
    plane_world = {v: plane(v) for v in box6}
    plane_flex = flexible_vertices(plane_world, box6, window)
    checks["theorem_1_flexible_flat_class"] = {"worlds": len(flex_rows), "all_window_vertices_flexible": all(flex_rows)}
    checks["theorem_1_plane_world"] = {"window_vertices_flexible": sum(plane_flex)}
    if not all(flex_rows) or any(plane_flex):
        failures.append("Theorem 1: flexibility at flat-class worlds or frozenness at the plane world")
    star_native_flat = all(flexible_vertices(random_flat_class_world(rng, 6), box6, star))
    star_native_plane = any(flexible_vertices(plane_world, box6, star))
    checks["theorem_2_star_knot_nativity"] = {"native_at_a_flat_class_world": star_native_flat,
                                              "native_at_the_plane_world": star_native_plane}
    if not star_native_flat or star_native_plane:
        failures.append("Theorem 2: star knot nativity")

    tree_frozen = {d: tree_complete_count(d, frozen_tree_colouring(d)) for d in (3, 4, 5)}
    bip = {w: len(w) % 2 for w in tree_ball(6)}
    tree_flexible = {d: tree_complete_count(d, bip) for d in (3, 4, 5)}
    children = [c for c in tree_nbrs(()) if c]
    tree_cells = tree_ball(2)
    in_tree = set(tree_cells)
    tree_proj = set()
    for colours in product(range(3), repeat=3):
        if complete(tree_cells, lambda w: [c for c in tree_nbrs(w) if c in in_tree], dict(zip(children, colours))):
            tree_proj.add(colours)
    patch = tree_patch(rng, 60)
    checks["theorem_3_tree"] = {"frozen_colouring_completions": tree_frozen, "two_colouring_completions": tree_flexible,
                                "star_knot_equals_not_all_distinct": tree_proj == not_distinct,
                                "star_knot": knot_finite(tree_proj, (3, 3, 3)), "patching": patch}
    if any(c != 1 for c in tree_frozen.values()) or tree_proj != not_distinct or not knot_finite(tree_proj, (3, 3, 3)):
        failures.append("Theorem 3: tree frozen colouring or star knot")
    if not (patch["valid"] == patch["match_window"] == patch["change_inside_ball"] == patch["patterns"]):
        failures.append("Theorem 3: patching on the tree")
    controls["theorem_3_frozen_test_on_the_two_colouring"] = {"counts": tree_flexible,
                                                              "rejected": any(c != 1 for c in tree_flexible.values())}

    hc_flex = hard_core_flexible(rng)
    hc_knots = hard_core_knots()
    checks["theorem_4_hard_core"] = {**hc_flex, **hc_knots}
    if hc_flex["flexible"] != hc_flex["window_vertices_checked"] or hc_knots["knots"] or hc_knots["not_majority_closed"]:
        failures.append("Theorem 4: hard-core law")
    controls["theorem_4_flexibility_test_at_the_plane_colouring"] = {"window_vertices_flexible": sum(plane_flex),
                                                                     "rejected": sum(plane_flex) < len(window)}

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
