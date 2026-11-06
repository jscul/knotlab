#!/usr/bin/env python3
"""Independent check of HOLES-COHOMOLOGY-20261019-001A-E001; imports no producer code.

- Composites by the covering-graph criterion: a pattern is allowed when the
  label-extended graph (vertex, witness value) has a component that meets every
  vertex exactly once. Holonomy orbits at vertex 0 are read off the same
  components (root values in one component form one orbit), so neither
  backtracking nor spanning trees are used here.
- Every linear-algebra verdict is re-verified by substitution into equations
  rebuilt from their names: solutions must satisfy every equation of the
  system; refutations must cancel every variable and leave a nonzero constant
  (mod p for F_p and for the Z refutations).
- Group counts, P6 type pairs, complexes and the size bound are recomputed in
  full; exhaustive selector cases are recomputed with fresh decoys (the shape
  should not depend on them); sampled cases and the relational control are
  re-run with an independent seed.
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACT = ROOT / "artifacts" / "HOLES-COHOMOLOGY-20261019-001A" / HERE.name
sys.path.insert(0, str(ROOT / "tools"))

from knotlab import Relation, check_knot  # noqa: E402

GRAPHS = {
    "C3": (3, [(0, 1), (1, 2), (2, 0)]),
    "C4": (4, [(0, 1), (1, 2), (2, 3), (3, 0)]),
    "C5": (5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]),
    "C6": (6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]),
    "theta": (5, [(0, 2), (2, 1), (0, 3), (3, 1), (0, 4), (4, 1)]),
    "K4": (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]),
    "K23": (5, [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4)]),
    "prism": (6, [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5), (0, 3), (1, 4), (2, 5)]),
    "bouquet2": (5, [(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0)]),
    "bouquet3": (7, [(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0), (0, 5), (5, 6), (6, 0)]),
}


def components(vertices, edges, perms, n):
    """Connected components of the label-extended graph, as lists of (vertex, value)."""
    parent = {(v, x): (v, x) for v in range(vertices) for x in range(n)}

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    for (a, b), p in zip(edges, perms):
        for x in range(n):
            ra, rb = find((a, x)), find((b, p[x]))
            if ra != rb:
                parent[ra] = rb
    groups = defaultdict(list)
    for node in parent:
        groups[find(node)].append(node)
    return list(groups.values())


def covering(vertices, edges, perms, n):
    """(allowed, orbit sizes at vertex 0, common fixed points at vertex 0)."""
    comps = components(vertices, edges, perms, n)
    sections = [c for c in comps if len(c) == vertices and len({v for v, _ in c}) == vertices]
    sizes = sorted(sum(1 for v, _ in c if v == 0) for c in comps)
    fixed_root = sorted(x for c in sections for v, x in c if v == 0)
    return bool(sections), [s for s in sizes if s], fixed_root


def compose(p, q):
    return tuple(p[x] for x in q)


def closure(gens, n):
    seen = {tuple(range(n))}
    todo = list(seen)
    while todo:
        g = todo.pop()
        for h in gens:
            k = compose(h, g)
            if k not in seen:
                seen.add(k)
                todo.append(k)
    return sorted(seen)


def cyc(n, points):
    out = list(range(n))
    for i, x in enumerate(points):
        out[x] = points[(i + 1) % len(points)]
    return tuple(out)


GROUPS = {
    "Z2": (2, closure([(1, 0)], 2)),
    "Z3": (3, closure([(1, 2, 0)], 3)),
    "S3": (3, sorted(permutations(range(3)))),
    "C6": (5, closure([(1, 0, 3, 4, 2)], 5)),
    "S4": (4, sorted(permutations(range(4)))),
}


def ctype(p):
    sizes, seen = [], set()
    for x in range(len(p)):
        if x not in seen:
            size = 0
            while x not in seen:
                seen.add(x)
                x = p[x]
                size += 1
            sizes.append(size)
    return tuple(sorted(sizes))


# ---------------------------------------------------------------- linear systems, rebuilt from names

def solutions_on(bag, edges, perms, n):
    """Assignments of a bag satisfying the copies inside it, built by extending one vertex at a time."""
    partial = [()]
    for i, v in enumerate(bag):
        nxt = []
        for f in partial:
            for x in range(n):
                g = f + (x,)
                ok = True
                for (a, b), p in zip(edges, perms):
                    if a in bag[:i + 1] and b in bag[:i + 1] and v in (a, b):
                        if g[bag.index(b)] != p[g[bag.index(a)]]:
                            ok = False
                            break
                if ok:
                    nxt.append(g)
        partial = nxt
    return partial


def vname(bag, f):
    return "v:" + ",".join(map(str, bag)) + "|" + ",".join(map(str, f))


def parse_ints(text):
    return tuple(int(t) for t in text.split(",")) if text else ()


def equation(name, inst, pin):
    """The linear form and constant of a named equation."""
    edges, perms, n = inst["edges"], inst["perms"], inst["values"]
    if name == "n:":
        return {vname((), ()): 1}, 1
    if name.startswith("p:"):
        w = int(name[2:])
        return {vname((0,), (w,)): 1}, int(w == pin)
    _, rest = name.split(":", 1)
    big_text, v_text, f_text = rest.split("|")
    big, v, f = parse_ints(big_text), int(v_text), parse_ints(f_text)
    small = tuple(x for x in big if x != v)
    form = Counter({vname(small, f): 1})
    for g in solutions_on(big, edges, perms, n):
        if tuple(g[big.index(x)] for x in small) == f:
            form[vname(big, g)] -= 1
    return {k: c for k, c in form.items() if c}, 0


def all_equation_names(inst, level, pin):
    names = ["n:"]
    V = inst["vertices"]
    for size in range(1, level + 1):
        for big in combinations(range(V), size):
            for v in big:
                small = tuple(x for x in big if x != v)
                for f in solutions_on(small, inst["edges"], inst["perms"], inst["values"]):
                    names.append("m:" + ",".join(map(str, big)) + "|" + str(v) + "|" + ",".join(map(str, f)))
    if pin is not None:
        names += [f"p:{w}" for w in range(inst["values"])]
    return names


def value(text, ring):
    if ring == "Q":
        return Fraction(text)
    return int(text)


def verify(verdict, inst, level, pin, ring, cache):
    """Re-verify a verdict's certificate; return (feasible, ok)."""
    modulus = {"F2": 2, "F3": 3}.get(ring)
    key = (level, pin)
    if key not in cache:
        cache[key] = {name: equation(name, inst, pin) for name in all_equation_names(inst, level, pin)}
    eqs = cache[key]
    if verdict["feasible"]:
        x = {v: value(a, ring) for v, a in verdict["solution"].items()}
        for form, c in eqs.values():
            total = sum(a * x.get(v, 0) for v, a in form.items()) - c
            if (total % modulus if modulus else total) != 0:
                return True, False
        return True, True
    if ring == "Z":
        cert = verdict.get("mod_p_refutation")
        if cert is None:
            return False, False
        modulus, coefficients = cert["p"], {e: int(a) for e, a in cert["refutation"].items()}
    else:
        coefficients = {e: value(a, ring) for e, a in verdict["refutation"].items()}
    combined, constant = Counter(), 0
    for e, y in coefficients.items():
        if e not in eqs:
            return False, False
        form, c = eqs[e]
        for v, a in form.items():
            combined[v] += y * a
        constant += y * c
    if modulus:
        cancels = all(a % modulus == 0 for a in combined.values())
        return False, cancels and constant % modulus != 0
    return False, all(a == 0 for a in combined.values()) and constant != 0


def contains_one(sizes, ring):
    from math import gcd
    if ring == "Q":
        return True
    if ring == "Z":
        g = 0
        for s in sizes:
            g = gcd(g, s)
        return g == 1
    p = int(ring[1:])
    return any(s % p for s in sizes)


def path_consistent(inst):
    n, V = inst["values"], inst["vertices"]
    rel = {(u, v): {(x, y) for x in range(n) for y in range(n)} for u in range(V) for v in range(V) if u != v}
    for (a, b), p in zip(inst["edges"], inst["perms"]):
        rel[(a, b)] &= {(x, p[x]) for x in range(n)}
        rel[(b, a)] &= {(p[x], x) for x in range(n)}
    while True:
        changed = False
        for u in range(V):
            for v in range(V):
                for w in range(V):
                    if len({u, v, w}) < 3:
                        continue
                    keep = {(x, z) for x, z in rel[(u, v)]
                            if any((x, y) in rel[(u, w)] and (y, z) in rel[(w, v)] for y in range(n))}
                    if keep != rel[(u, v)]:
                        rel[(u, v)], rel[(v, u)] = keep, {(z, x) for x, z in keep}
                        changed = True
        if not changed:
            return all(rel.values())


# ---------------------------------------------------------------- selectors and complexes

def bouquet_allowed(holonomies, n, rng):
    """Selector patterns allowed by the bouquet network, by the covering criterion, with fresh decoys."""
    k = len(holonomies)
    edges = []
    for i in range(k):
        edges += [(0, 1 + 2 * i), (1 + 2 * i, 2 + 2 * i), (2 + 2 * i, 0)]
    decoys = [(tuple(rng.sample(range(n), n)), tuple(rng.sample(range(n), n))) for _ in range(k)]
    allowed = set()
    for s in product((0, 1), repeat=k):
        perms = []
        for i in range(k):
            a, b = decoys[i]
            ba = compose(b, a)
            back = [0] * n
            for x, y in enumerate(ba):
                back[y] = x
            close = tuple(back)
            perms += [a, b, compose(holonomies[i], close) if s[i] else close]
        if covering(2 * k + 1, edges, perms, n)[0]:
            allowed.add(s)
    return allowed


def faces_of(allowed, k):
    return {frozenset(c) for size in range(k + 1) for c in combinations(range(k), size)
            if len({tuple(s[i] for i in c) for s in allowed}) == 2 ** size}


def fixed_set(p):
    return {x for x in range(len(p)) if p[x] == x}


def nerve_of(hol, n):
    k = len(hol)
    return {frozenset(c) for size in range(k + 1) for c in combinations(range(k), size)
            if set(range(n)).intersection(*[fixed_set(hol[i]) for i in c])}


def selector_stats(tuples, n, rng):
    stats = Counter()
    for hol in tuples:
        k = len(hol)
        allowed = bouquet_allowed(hol, n, rng)
        faces = faces_of(allowed, k)
        stats["tuples"] += 1
        stats["shape_mismatches"] += faces != nerve_of(hol, n)
        free = all(h == tuple(range(n)) or not fixed_set(h) for h in hol)
        stats["free_contact_tuples"] += free
        for size in range(2, k + 1):
            for c in combinations(range(k), size):
                S = frozenset(c)
                if S in faces or not all(S - {i} in faces for i in S):
                    continue
                if size == 2:
                    stats["ties"] += 1
                    stats["ties_under_free_contact"] += free
                    continue
                names = tuple(f"s{i}" for i in c)
                rows = frozenset(tuple(bool(s[i]) for i in c) for s in allowed)
                report = check_knot(Relation(names, rows), names[:-1], names[-1])
                stats[f"knots_among_{size}_loops"] += 1
                stats["knot_check_failures"] += not report.is_knot
                stats["non_atom_knots"] += set(product((False, True), repeat=size)) - rows != {(True,) * size}
                stats["knots_under_free_contact"] += free
    return stats


def main() -> int:
    result = json.loads((ARTIFACT / "result.json").read_text())
    rows = [json.loads(line) for line in (ARTIFACT / "raw_rows.jsonl").read_text().splitlines()]
    failures: list[str] = []

    def expect(condition, message):
        if not condition:
            failures.append(message)

    # P1, P2, P6: group links recomputed in full
    group_rows = {(r["graph"], r["group"]): r for r in rows if r["part"] == "group"}
    for (graph, gname), row in group_rows.items():
        n, group = GROUPS[gname]
        vertices, edges = GRAPHS[graph]
        b1 = len(edges) - vertices + 1
        allowed = 0
        by_types = defaultdict(set)
        for pattern in product(group, repeat=len(edges)):
            ok, _, _ = covering(vertices, edges, pattern, n)
            allowed += ok
            if b1 == 2:
                by_types[two_loop_types(graph, pattern, n)].add(ok)
        expect(allowed == row["allowed"], f"{graph} {gname}: allowed count")
        inclusion = Fraction(0)
        for size in range(1, n + 1):
            for T in combinations(range(n), size):
                fixers = sum(1 for g in group if all(g[x] == x for x in T))
                inclusion += (-1) ** (size + 1) * Fraction(fixers, len(group)) ** b1
        expect(inclusion * len(group) ** len(edges) == allowed, f"{graph} {gname}: P2 formula")
        if b1 == 2:
            mixed = sorted([list(map(list, k)) for k, v in by_types.items() if len(v) > 1])
            expect(mixed == row["p6_mixed_type_pairs"], f"{graph} {gname}: P6 mixed type pairs")
    fractions = defaultdict(set)
    for (graph, gname), row in group_rows.items():
        fractions[(gname, row["b1"])].add(Fraction(row["allowed"], row["patterns"]))
    expect(all(len(v) == 1 for v in fractions.values()), "P2: fraction depends on b1 only")
    s4 = [r for r in rows if r["part"] == "group_gauge_fixed"][0]
    n, group = GROUPS["S4"]
    vertices, edges = GRAPHS["theta"]
    tree = set(s4["tree_edges_identity"])
    free_edges = [e for e in range(len(edges)) if e not in tree]
    by_types, allowed = defaultdict(set), 0
    for choice in product(group, repeat=len(free_edges)):
        perms = [tuple(range(n))] * len(edges)
        for e, p in zip(free_edges, choice):
            perms[e] = p
        ok, _, _ = covering(vertices, edges, perms, n)
        allowed += ok
        by_types[two_loop_types("theta", perms, n)].add(ok)
    expect(allowed == s4["allowed"], "S4 gauge-fixed theta: allowed count")
    expect(sorted([list(map(list, k)) for k, v in by_types.items() if len(v) > 1]) == s4["p6_mixed_type_pairs"],
           "S4 gauge-fixed theta: P6")

    # P1: random links recomputed from the stored links
    for r in (r for r in rows if r["part"] == "random_links"):
        vertices, edges = GRAPHS[r["graph"]]
        count = 0
        for pattern in product((0, 1), repeat=len(edges)):
            perms = [tuple(r["links"][e][m]) for e, m in enumerate(pattern)]
            count += covering(vertices, edges, perms, r["values"])[0]
        expect(count == r["allowed"] and r["p1_mismatches"] == 0, f"random links {r['graph']} {r['index']}")

    # P3: exhaustive selector cases with fresh decoys; sampled cases re-sampled
    rng = random.Random(7)
    perms_of = {n: sorted(permutations(range(n))) for n in (3, 4, 5)}
    for r in (r for r in rows if r["part"] == "selector"):
        k, n = r["loops"], r["values"]
        if r["exhaustive"]:
            stats = selector_stats(list(product(perms_of[n], repeat=k)), n, rng)
            for key in ("tuples", "shape_mismatches", "ties", "knot_check_failures", "non_atom_knots",
                        "ties_under_free_contact", "knots_under_free_contact", "free_contact_tuples",
                        "knots_among_3_loops"):
                expect(stats.get(key, 0) == r.get(key, 0), f"selector k={k} n={n}: {key}")
        else:
            stats = selector_stats([tuple(rng.choice(perms_of[n]) for _ in range(k)) for _ in range(600)], n, rng)
            for key in ("shape_mismatches", "knot_check_failures", "non_atom_knots",
                        "ties_under_free_contact", "knots_under_free_contact"):
                expect(stats.get(key, 0) == 0 and r.get(key, 0) == 0, f"sampled selector k={k} n={n}: {key}")

    # P4: complexes and the size bound
    counts = {}
    for k in range(1, 5):
        total = 0
        for family in range(2 ** (2 ** k)):
            members = [S for S in range(2 ** k) if family >> S & 1]
            if 0 not in members or any((S & ~(1 << i)) not in members for S in members for i in range(k) if S >> i & 1):
                continue
            total += 1
            facets = [S for S in members if not any(T != S and (S | T) == T for T in members)]
            n = len(facets) + 2
            hol = [cyc(n, [j for j, F in enumerate(facets) if not F >> i & 1] + [n - 2, n - 1]) for i in range(k)]
            faces = faces_of(bouquet_allowed(hol, n, rng), k)
            expect(faces == {frozenset(i for i in range(k) if S >> i & 1) for S in members},
                   f"complex {members} on {k} vertices")
        counts[k] = total
    expect(counts == {int(k): v for k, v in result["complexes"]["counts_by_vertices"].items()}, "complex counts")
    for k in (2, 3, 4):
        knots = 0
        for hol in product(perms_of.get(k, sorted(permutations(range(k)))), repeat=k):
            fixes = [fixed_set(h) for h in hol]
            if not set(range(k)).intersection(*fixes) and all(
                    set(range(k)).intersection(*[fixes[i] for i in range(k) if i != j]) for j in range(k)):
                knots += 1
        star = [cyc(k + 1, [j, k]) for j in range(k)]
        fixes = [fixed_set(h) for h in star]
        star_ok = not set(range(k + 1)).intersection(*fixes) and all(
            set(range(k + 1)).intersection(*[fixes[i] for i in range(k) if i != j]) for j in range(k))
        expect(knots == 0 and star_ok, f"size bound k={k}")
        expect(result["size_bound"][str(k)]["knots_on_k_values"] == knots, f"size bound record k={k}")

    # P5: every certificate re-verified; predictions re-derived from the covering components
    verified = Counter()
    for r in (r for r in rows if r["part"] == "local"):
        inst = {"vertices": r["vertices"], "edges": [tuple(e) for e in r["edges"]],
                "perms": [tuple(p) for p in r["perms"]], "values": r["values"]}
        possible, sizes, common = covering(inst["vertices"], inst["edges"], inst["perms"], inst["values"])
        expect(possible == r["possible"], f"{r['label']}: possible")
        expect(sizes == r["prediction_side"]["orbit_sizes"], f"{r['label']}: orbit sizes")
        expect(common == r["prediction_side"]["common_fixed_points"], f"{r['label']}: fixed points")
        cache: dict = {}
        for key, verdict in r["verdicts"].items():
            if not isinstance(verdict, dict):
                continue
            kind, ring = key.split("_")
            if kind == "level2":
                level, pin, expected = 2, None, contains_one(sizes, ring)
            elif kind == "level3":
                level, pin, expected = 3, None, possible
            else:
                level, pin = 2, int(kind[len("pinned"):])
                expected = pin in common
            feasible, ok = verify(verdict, inst, level, pin, ring, cache)
            expect(ok, f"{r['label']} {key}: certificate")
            expect(feasible == expected, f"{r['label']} {key}: prediction")
            verified[kind.rstrip("0123456789")] += 1
        expect(r["verdicts"]["arc_consistency_accepts"] is True, f"{r['label']}: arc consistency")
        expect(path_consistent(inst) == possible == r["verdicts"]["path_consistency_accepts"],
               f"{r['label']}: path consistency")

    # control: relational links break the per-loop rule, re-run with an independent seed on theta
    expect(result["controls"]["relational_links_break_the_loop_rule"], "relational control (producer)")
    vertices, edges = GRAPHS["theta"]
    walks = [[(0, True), (1, True), (3, False), (2, False)], [(0, True), (1, True), (5, False), (4, False)]]
    broken = 0
    for _ in range(20):
        links = []
        for _ in edges:
            pair = []
            for _ in range(2):
                p = rng.sample(range(3), 3)
                pair.append({(x, p[x]) for x in range(3)} | {(rng.randrange(3), rng.randrange(3))})
            links.append(pair)
        for pattern in product((0, 1), repeat=len(edges)):
            rels = [links[e][m] for e, m in enumerate(pattern)]
            truth = any(all((w[a], w[b]) in rel for (a, b), rel in zip(edges, rels))
                        for w in product(range(3), repeat=vertices))
            naive = False
            for u in range(3):
                closes = True
                for walk in walks:
                    reach = {u}
                    for e, forward in walk:
                        reach = {y for x, y in rels[e] if x in reach} if forward else {x for x, y in rels[e] if y in reach}
                    closes &= u in reach
                naive |= closes
            if truth != naive:
                broken += 1
                break
    expect(broken > 0, "relational control (independent re-run)")
    expect(result["signal"], "producer reports no signal")
    print(json.dumps({"certificates_verified": dict(verified), "complex_counts": counts,
                      "local_instances": sum(1 for r in rows if r["part"] == "local")}, indent=1))
    print(f"{'passed' if not failures else 'FAILED'}: recomputation agrees (V1, exploratory evidence only)")
    for failure in failures[:30]:
        print("  failed:", failure)
    return 0 if not failures else 1


def two_loop_types(graph, perms, n):
    """Cycle types of the holonomies of two independent loops at vertex 0, walking declared cycles."""
    walks = {
        # theta: loop through paths 0-2-1 and 0-3-1, loop through 0-2-1 and 0-4-1
        "theta": [[(0, True), (1, True), (3, False), (2, False)], [(0, True), (1, True), (5, False), (4, False)]],
        "K23": [[(0, True), (3, False), (4, True), (1, False)], [(0, True), (3, False), (5, True), (2, False)]],
        "bouquet2": [[(0, True), (1, True), (2, True)], [(3, True), (4, True), (5, True)]],
    }[graph]
    types = []
    for walk in walks:
        h = tuple(range(n))
        for e, forward in walk:
            p = perms[e]
            if not forward:
                back = [0] * n
                for x, y in enumerate(p):
                    back[y] = x
                p = tuple(back)
            h = compose(p, h)
        types.append(ctype(h))
    return tuple(types)


if __name__ == "__main__":
    raise SystemExit(main())
