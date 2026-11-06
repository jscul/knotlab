#!/usr/bin/env python3
"""Check HOLES-COHOMOLOGY-20261019-001C-P001: where local reasoning fails.

For every declared network of permutation contact this builds the certificate
that the prose proof describes and verifies it by substitution into the
relaxation's equations, rebuilt here from scratch:

- level 2 over R when 1 is in the orbit-size ideal: a solution built from an
  H-invariant vector with coordinate sum 1, transported along a spanning tree;
- level 2 over Z or F_p when it is not: the orbit-sum combination, whose
  variables all carry multiples of d (the gcd of the orbit sizes, or p) while
  its constant is 1, so it reads 0 = 1 mod d;
- level 2 pinned at u: a point-mass solution if u is a common fixed point,
  otherwise the lasso combination reading 0 = 1 over Z (hence every ring);
- level 3: a point-mass solution if the network is possible, otherwise the
  three-witness walk combination reading 0 = 1 over Z (hence every ring).

It also confirms the census HOLES-COHOMOLOGY-20261019-001A-E001 found the same
verdicts with a general solver.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import json
import math
import random
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS = ROOT / "artifacts/HOLES-COHOMOLOGY-20261019-001A/HOLES-COHOMOLOGY-20261019-001A-E001_holonomy_census"
SEED = 20261020


def compose(p, q):
    """p after q."""
    return tuple(p[x] for x in q)


def inverse(p):
    out = [0] * len(p)
    for x, y in enumerate(p):
        out[y] = x
    return tuple(out)


def from_cycles(n, cycles):
    out = list(range(n))
    for points in cycles:
        for i, x in enumerate(points):
            out[x] = points[(i + 1) % len(points)]
    return tuple(out)


def ring_edges(length):
    return [(i, (i + 1) % length) for i in range(length)]


GRAPHS = {
    "theta": (5, [(0, 2), (2, 1), (0, 3), (3, 1), (0, 4), (4, 1)]),
    "K4": (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]),
    "K23": (5, [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4)]),
    "prism": (6, [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5), (0, 3), (1, 4), (2, 5)]),
    "bouquet2": (5, [(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0)]),
    "bouquet3": (7, [(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0), (0, 5), (5, 6), (6, 0)]),
    "grid3": (9, [(r * 3 + c, r * 3 + c + 1) for r in range(3) for c in range(2)]
              + [(r * 3 + c, (r + 1) * 3 + c) for r in range(2) for c in range(3)]),
}


class Network:
    def __init__(self, vertices, edges, perms, n):
        self.vertices, self.edges, self.perms, self.n = vertices, list(edges), list(perms), n
        self.walk = {0: []}
        order = [0]
        for x in order:
            for e, (a, b) in enumerate(self.edges):
                for here, there, forward in ((a, b, True), (b, a, False)):
                    if here == x and there not in self.walk:
                        self.walk[there] = self.walk[x] + [(e, forward)]
                        order.append(there)
        assert len(order) == vertices
        tree = {walk[-1][0] for walk in self.walk.values() if walk}
        self.lassos = []
        for e, (a, b) in enumerate(self.edges):
            if e not in tree:
                back = [(f, not forward) for f, forward in reversed(self.walk[b])]
                self.lassos.append(self.walk[a] + [(e, True)] + back)

    def step(self, e, forward, x):
        p = self.perms[e]
        return p[x] if forward else inverse(p)[x]

    def ends(self, e, forward):
        a, b = self.edges[e]
        return (a, b) if forward else (b, a)

    def transport(self, walk, x):
        for e, forward in walk:
            x = self.step(e, forward, x)
        return x

    def holonomy(self, walk):
        return tuple(self.transport(walk, x) for x in range(self.n))

    def orbits(self):
        hol = [self.holonomy(l) for l in self.lassos]
        seen, out = set(), []
        for start in range(self.n):
            if start in seen:
                continue
            orbit, frontier = [start], [start]
            seen.add(start)
            while frontier:
                x = frontier.pop()
                for h in hol:
                    for y in (h[x], inverse(h)[x]):
                        if y not in seen:
                            seen.add(y)
                            orbit.append(y)
                            frontier.append(y)
            out.append(orbit)
        return out

    def common_fixed(self):
        return [x for x in range(self.n) if all(self.transport(l, x) == x for l in self.lassos)]


# ---------------------------------------------------------------- the relaxation, rebuilt

def name_var(bag, f):
    return "v:" + ",".join(map(str, bag)) + "|" + ",".join(map(str, f))


def local(net, bag):
    """Assignments of a bag that satisfy the copies inside it (memoized per network)."""
    cache = net.__dict__.setdefault("_local", {})
    if bag not in cache:
        inside = [(a, b, p) for (a, b), p in zip(net.edges, net.perms) if a in bag and b in bag]
        out = []
        for f in product(range(net.n), repeat=len(bag)):
            value = dict(zip(bag, f))
            if all(value[b] == p[value[a]] for a, b, p in inside):
                out.append(f)
        cache[bag] = out
    return cache[bag]


def equation(net, name, pin):
    if name == "n:":
        return {name_var((), ()): 1}, 1
    if name.startswith("p:"):
        w = int(name[2:])
        return {name_var((0,), (w,)): 1}, int(w == pin)
    big_text, v_text, f_text = name[2:].split("|")
    big = tuple(int(t) for t in big_text.split(","))
    v = int(v_text)
    f = tuple(int(t) for t in f_text.split(",")) if f_text else ()
    small = tuple(x for x in big if x != v)
    assert f in local(net, small), name
    form = Counter({name_var(small, f): 1})
    at = big.index(v)
    for g in local(net, big):
        if g[:at] + g[at + 1:] == f:
            form[name_var(big, g)] -= 1
    return {k: c for k, c in form.items() if c}, 0


def system(net, level, pin=None):
    names = ["n:"]
    for size in range(1, level + 1):
        for big in combinations(range(net.vertices), size):
            for v in big:
                small = tuple(x for x in big if x != v)
                names += ["m:" + ",".join(map(str, big)) + "|" + str(v) + "|" + ",".join(map(str, f))
                          for f in local(net, small)]
    if pin is not None:
        names += [f"p:{w}" for w in range(net.n)]
    return {name: equation(net, name, pin) for name in names}


def solves(eqs, x, modulus=None):
    for form, c in eqs.values():
        total = sum(a * x.get(v, 0) for v, a in form.items()) - c
        if (total % modulus if modulus else total) != 0:
            return False
    return True


def refutes(net, y, pin, modulus=None):
    """A combination of equations: every variable cancels (mod modulus) and the constant does not."""
    combined, constant = Counter(), 0
    for name, coefficient in y.items():
        if coefficient == 0:
            continue
        form, c = equation(net, name, pin)
        for v, a in form.items():
            combined[v] += coefficient * a
        constant += coefficient * c
    if modulus:
        return all(a % modulus == 0 for a in combined.values()) and constant % modulus != 0
    return all(a == 0 for a in combined.values()) and constant != 0


# ---------------------------------------------------------------- certificates

def m_name(big, removed, f):
    return "m:" + ",".join(map(str, big)) + "|" + str(removed) + "|" + ",".join(map(str, f))


def add(y, other, scale=1):
    for k, v in other.items():
        y[k] = y.get(k, 0) + scale * v


def lasso_difference(net, lasso, x):
    """Equations combining to mu_0(x) - mu_0(h(x)), from the edge bags along the lasso."""
    y = {}
    for e, forward in lasso:
        s, t = net.ends(e, forward)
        xs, xt = x, net.step(e, forward, x)
        big = tuple(sorted((s, t)))
        add(y, {m_name(big, t, (xs,)): 1})
        add(y, {m_name(big, s, (xt,)): -1})
        x = xt
    return y


def level2_solution(net, mu, reduce):
    """A level-2 solution from an H-invariant vector mu with coordinate sum 1."""
    x = {name_var((), ()): reduce(1)}
    at = {}
    for v in range(net.vertices):
        g = net.holonomy(net.walk[v])
        back = inverse(g)
        at[v] = {w: mu[back[w]] for w in range(net.n)}
        for w in range(net.n):
            x[name_var((v,), (w,))] = reduce(at[v][w])
    adjacent = {}
    for (a, b), p in zip(net.edges, net.perms):
        adjacent[tuple(sorted((a, b)))] = (a, b, p)
    for u, v in combinations(range(net.vertices), 2):
        if (u, v) in adjacent:
            a, b, p = adjacent[(u, v)]
            for w in range(net.n):
                f = (w, p[w]) if a == u else (p[w], w)
                x[name_var((u, v), f)] = reduce(at[a][w])
        else:
            for w, z in product(range(net.n), repeat=2):
                x[name_var((u, v), (w, z))] = reduce(at[u][w] * (z == 0) + (w == 0) * (at[v][z] - (z == 0)))
    return x


def point_mass(net, u, level):
    sigma = {v: net.transport(net.walk[v], u) for v in range(net.vertices)}
    x = {}
    for size in range(level + 1):
        for bag in combinations(range(net.vertices), size):
            x[name_var(bag, tuple(sigma[v] for v in bag))] = 1
    return x


def orbit_refutation(net, orbits):
    """Combination with form sum over orbits of |O| mu_0(w_O) and constant 1."""
    y = {"n:": 1, m_name((0,), 0, ()): -1}
    hol = [net.holonomy(l) for l in net.lassos]
    for orbit in orbits:
        base = orbit[0]
        path = {base: {}}
        frontier = [base]
        while frontier:
            w = frontier.pop()
            for lasso, h in zip(net.lassos, hol):
                forward_to, backward_to = h[w], inverse(h)[w]
                if forward_to not in path:
                    step = dict(path[w])
                    add(step, lasso_difference(net, lasso, w))
                    path[forward_to] = step
                    frontier.append(forward_to)
                if backward_to not in path:
                    step = dict(path[w])
                    add(step, lasso_difference(net, lasso, backward_to), -1)
                    path[backward_to] = step
                    frontier.append(backward_to)
        for w in orbit:
            if w != base:
                add(y, path[w])
    return y


def pinned_refutation(net, u):
    for lasso in net.lassos:
        hu = net.transport(lasso, u)
        if hu != u:
            y = {f"p:{u}": 1, f"p:{hu}": -1}
            add(y, lasso_difference(net, lasso, u), -1)
            return y
    return None


def local_on_pair(net, v, f):
    return f in local(net, tuple(sorted((0, v)))) if v != 0 else True


def pair_values(v, w, y):
    return (w, y) if 0 < v else (y, w)


def level3_refutation(net):
    """The three-witness walk: for each value w, mu_0(w) = 0 along a lasso that moves w."""
    y = {"n:": 1, m_name((0,), 0, ()): -1}
    for w in range(net.n):
        lasso = next(l for l in net.lassos if net.transport(l, w) != w)
        verts = [0]
        for e, forward in lasso:
            verts.append(net.ends(e, forward)[1])
        m = len(lasso)
        last_e, last_forward = lasso[-1]
        back = inverse(net.perms[last_e]) if last_forward else net.perms[last_e]
        current = back[w]                       # the value at v_{m-1} compatible with w across the last edge
        i = m - 1                               # position of the current pair variable z[{0, v_i}](w, current)
        part = {m_name(tuple(sorted((0, verts[i]))), verts[i], (w,)): 1}
        while True:
            assert i >= 2, "the walk never returns to the base before its last step"
            e, forward = lasso[i - 1]           # step from v_{i-1} to v_i
            previous = net.step(e, not forward, current)
            vi, vprev = verts[i], verts[i - 1]
            big = tuple(sorted({0, vprev, vi}))
            f_here = pair_values(vi, w, current)
            add(part, {m_name(big, vprev, f_here): 1})
            f_prev = pair_values(vprev, w, previous)
            if i - 1 >= 1 and local_on_pair(net, vprev, f_prev):
                add(part, {m_name(big, vi, f_prev): -1})
                current, i = previous, i - 1
                continue
            break
        add(y, part, -1)
    return y


def contains_one(sizes, ring):
    if ring == "Q":
        return True
    if ring == "Z":
        return math.gcd(*sizes) == 1
    return any(s % int(ring[1:]) for s in sizes)


def invariant_vector(orbits, ring):
    sizes = [len(o) for o in orbits]
    mu = {}
    if ring == "Q":
        for x in orbits[0]:
            mu[x] = Fraction(1, len(orbits[0]))
    elif ring == "Z":
        coefficients = bezout(sizes)
        for orbit, c in zip(orbits, coefficients):
            for x in orbit:
                mu[x] = c
    else:
        p = int(ring[1:])
        orbit = next(o for o in orbits if len(o) % p)
        for x in orbit:
            mu[x] = pow(len(orbit), p - 2, p)
    for orbit in orbits:
        for x in orbit:
            mu.setdefault(x, 0)
    return mu


def bezout(sizes):
    """Integers c with sum c_i sizes_i = gcd(sizes)."""
    g, coefficients = sizes[0], [1] + [0] * (len(sizes) - 1)
    for i in range(1, len(sizes)):
        a, b = g, sizes[i]
        old_r, r, old_s, s, old_t, t = a, b, 1, 0, 0, 1
        while r:
            q = old_r // r
            old_r, r = r, old_r - q * r
            old_s, s = s, old_s - q * s
            old_t, t = t, old_t - q * t
        coefficients = [c * old_s for c in coefficients]
        coefficients[i] = old_t
        g = old_r
    assert sum(c * s for c, s in zip(coefficients, sizes)) == g
    return coefficients


RINGS = ("F2", "F3", "F5", "Q", "Z")


def instances(rng):
    out = []
    types = {2: [[1, 1], [2]], 3: [[1, 1, 1], [1, 2], [3]], 4: [[1, 1, 1, 1], [1, 1, 2], [1, 3], [2, 2], [4]],
             5: [[1, 1, 1, 1, 1], [1, 1, 1, 2], [1, 2, 2], [1, 1, 3], [2, 3], [1, 4], [5]]}
    for length in range(3, 8):
        for n, shapes in types.items():
            for sizes in shapes:
                cycles, start = [], 0
                for size in sorted(sizes, reverse=True):
                    cycles.append(tuple(range(start, start + size)))
                    start += size
                h = from_cycles(n, cycles)
                g = tuple(rng.sample(range(n), n))
                target = compose(g, compose(h, inverse(g)))
                perms = [tuple(rng.sample(range(n), n)) for _ in range(length - 1)]
                walked = tuple(range(n))
                for p in perms:
                    walked = compose(p, walked)
                perms.append(compose(target, inverse(walked)))
                out.append((f"C{length} n={n} type={sizes}", length, ring_edges(length), perms, n))
    for name, (vertices, edges) in GRAPHS.items():
        for n in (3, 4, 5):
            for index in range(8 if name == "grid3" else 20):
                perms = [tuple(rng.sample(range(n), n)) for _ in edges]
                out.append((f"{name} n={n} random {index}", vertices, edges, perms, n))
    return out


def run() -> dict[str, object]:
    rng = random.Random(SEED)
    tallies = Counter()
    failures: list[str] = []
    for label, vertices, edges, perms, n in instances(rng):
        net = Network(vertices, edges, perms, n)
        orbits = net.orbits()
        sizes = [len(o) for o in orbits]
        common = net.common_fixed()
        possible = bool(common)
        tallies["instances"] += 1
        tallies["impossible"] += not possible
        level2 = system(net, 2)
        for ring in RINGS:
            if contains_one(sizes, ring):
                reduce = (lambda a: a) if ring in ("Q", "Z") else (lambda a, p=int(ring[1:]): a % p)
                x = level2_solution(net, invariant_vector(orbits, ring), reduce)
                ok = solves(level2, x, None if ring in ("Q", "Z") else int(ring[1:]))
                tallies[f"level2_{ring}_solutions"] += 1
                tallies[f"level2_{ring}_fooled"] += not possible
            else:
                modulus = math.gcd(*sizes) if ring == "Z" else int(ring[1:])
                ok = refutes(net, orbit_refutation(net, orbits), None, modulus)
                tallies[f"level2_{ring}_refutations"] += 1
            if not ok:
                failures.append(f"{label}: level 2 over {ring}")
        for u in range(n):
            if u in common:
                ok = solves(system(net, 2, pin=u), point_mass(net, u, 2))
                tallies["pinned_solutions"] += 1
            else:
                ok = refutes(net, pinned_refutation(net, u), u)
                tallies["pinned_refutations"] += 1
            if not ok:
                failures.append(f"{label}: pinned at {u}")
        if possible:
            ok = solves(system(net, 3), point_mass(net, common[0], 3))
            tallies["level3_solutions"] += 1
        else:
            ok = refutes(net, level3_refutation(net), None)
            tallies["level3_refutations"] += 1
        if not ok:
            failures.append(f"{label}: level 3")
    census = json.loads((CENSUS / "result.json").read_text())
    controls = verifier_controls(random.Random(SEED + 1))
    checks = {
        "controls_rejected": controls,
        "instances": tallies["instances"],
        "tallies": dict(sorted(tallies.items())),
        "all_certificates_verified": not failures,
        "census_agrees": census["predictions"]["P5"] and census["controls"]["every_linear_verdict_has_certificate"],
        "smallest_integer_fooling_holonomy": smallest_integer_fooling(),
    }
    expected = ["all_certificates_verified", "census_agrees"]
    failed = [name for name in expected if checks.get(name) is not True] + failures[:20]
    failed += [f"control {name}" for name, rejected in controls.items() if not rejected]
    if checks["smallest_integer_fooling_holonomy"] != {"values": 5, "orbit_sizes": [2, 3]}:
        failed.append("smallest integer-fooling holonomy")
    return {"checks": checks, "failures": failed}


def verifier_controls(rng):
    """Broken certificates on a ring of length 5 with holonomy (01)(234) must be rejected."""
    n, length = 5, 5
    h = from_cycles(n, [(0, 1), (2, 3, 4)])
    perms = [tuple(rng.sample(range(n), n)) for _ in range(length - 1)]
    walked = tuple(range(n))
    for q in perms:
        walked = compose(q, walked)
    perms.append(compose(h, inverse(walked)))
    net = Network(length, ring_edges(length), perms, n)
    orbits = net.orbits()
    certificate = level3_refutation(net)
    first = sorted(k for k, v in certificate.items() if v)[0]
    broken = dict(certificate)
    broken[first] = 0
    solution = level2_solution(net, invariant_vector(orbits, "Z"), lambda a: a)
    perturbed = dict(solution)
    perturbed[name_var((0,), (0,))] += 1
    return {
        "level3_certificate_missing_an_equation": refutes(net, certificate, None) and not refutes(net, broken, None),
        "orbit_refutation_mod_2_with_an_odd_orbit": not refutes(net, orbit_refutation(net, orbits), None, 2),
        "integer_solution_with_one_value_changed": (solves(system(net, 2), solution)
                                                    and not solves(system(net, 2), perturbed)),
    }


def smallest_integer_fooling():
    """The fewest witness values on which some orbit partition has no fixed point and coprime sizes."""
    for n in range(1, 8):
        for sizes in partitions(n):
            if 1 not in sizes and math.gcd(*sizes) == 1:
                return {"values": n, "orbit_sizes": sorted(sizes)}
    return None


def partitions(n, largest=None):
    largest = n if largest is None else largest
    if n == 0:
        yield []
        return
    for first in range(min(n, largest), 0, -1):
        for rest in partitions(n - first, first):
            yield [first] + rest


def main() -> int:
    outcome = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3,
        "artifact_id": manifest["artifact_id"],
        "kind": "proof",
        "ticket": manifest["ticket"],
        "proof": manifest["proof"],
        "status": "passed" if not outcome["failures"] else "failed",
        "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"],
        "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"],
        "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"],
        "checks": outcome["checks"],
        "failures": outcome["failures"],
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if "--write" in sys.argv[1:]:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != result:
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: {outcome['checks']['instances']} instances, every certificate verified, "
          f"{sum(outcome['checks']['controls_rejected'].values())}/3 broken certificates rejected"
          if result["status"] == "passed" else f"failed: {outcome['failures'][:10]}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
