#!/usr/bin/env python3
"""Check of NATIVE-HARDNESS-20261024-001B-P001 (standard library only, seed 20261024).

Networks: n knots (three-place relations with every pair of places unconstrained), each with three slots; slots are paired into
internal edges or left as legs pinned to 0 or 1 (closed networks, no free legs, no loops). A network is encoded by one clause per
excluded tuple of each knot, with the pinned values substituted, so the variables are the internal edges.
Checks:
- counting: every non-parity knot allows at least five of the eight tuples; every nonempty three-place relation with pairwise
  non-adjacent excluded tuples allows at least four, exactly four only for the two parity relations;
- Theorem 2 (surrounded knots): in random unsatisfiable networks, every knot with three distinct edges and no bridge among them is a
  parity knot, and the rest of the network allows exactly the complementary parity class on its edges; the rest's relation is
  co-independent;
- Corollary 3 and Theorem 4: random unsatisfiable networks without parity knots are cacti, every cycle is an odd wire cycle (the
  pendant parts force constants on the third slots, every face on the cycle is a wire, an odd number of them unequal), and each is
  refuted by resolution with derived clauses of at most two literals; constructed necklaces of one, two and three odd rings;
- Theorem 5 (wide refutations): minimal unsatisfiability at the knot level on random networks; with one odd and the other knots even
  parity on the Petersen graph, the cube graph and the complete bipartite graph on three and three vertices, the balanced edge boundary
  is 5, 4 and 4, and saturation with derived clauses of fewer literals than the boundary finds no refutation;
- Corollary 6: on the Petersen and cube graphs with one edge cut into two pinned legs, the network of one parity knot is unsatisfiable
  exactly when the pins differ (tested for both parity knots).
Controls: a non-parity knot whose three edges are bridges can be unsatisfiable (connectivity is needed); parity knots do occur
surrounded in unsatisfiable networks (the count is sharp); with hubs (not-all-equal on all ten triples of five places) a surrounded
non-parity knot is unsatisfiable, the rest allowing only two tuples; the parity networks are not refuted with derived clauses of
at most two literals.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CUBE = list(itertools.product((0, 1), repeat=3))


def knots():
    out = []
    for m in range(256):
        R = frozenset(CUBE[i] for i in range(8) if m >> i & 1)
        if 0 < len(R) < 8 and all(len({(t[i], t[j]) for t in R}) == 4 for i, j in ((0, 1), (0, 2), (1, 2))):
            out.append(R)
    return out


def excluded(R):
    return [t for t in CUBE if t not in R]


def is_parity(R):
    return len(excluded(R)) == 4


def name(R):
    return ",".join("".join(map(str, t)) for t in excluded(R))


# ---------------------------------------------------------------- encoding and a small solver

def clauses_of(scopes, pins, Rs, skip=()):
    out = []
    for k, (sc, R) in enumerate(zip(scopes, Rs)):
        if k in skip:
            continue
        for t in excluded(R):
            if any(v in pins and pins[v] != b for v, b in zip(sc, t)):
                continue
            out.append([v if b == 0 else -v for v, b in zip(sc, t) if v not in pins])
    return out


def satisfiable(clauses):
    if any(not c for c in clauses):
        return False
    return _dpll([list(c) for c in clauses], {})


def _dpll(clauses, assign):
    while True:
        unit, new = None, []
        for c in clauses:
            rest, done = [], False
            for lit in c:
                a = assign.get(abs(lit))
                if a is None:
                    rest.append(lit)
                elif (lit > 0) == a:
                    done = True
                    break
            if done:
                continue
            if not rest:
                return False
            if len(rest) == 1 and unit is None:
                unit = rest[0]
            new.append(rest)
        clauses = new
        if unit is None:
            break
        assign = dict(assign)
        assign[abs(unit)] = unit > 0
    if not clauses:
        return True
    count = {}
    for c in clauses:
        for lit in c:
            count[abs(lit)] = count.get(abs(lit), 0) + 1
    v = max(count, key=count.get)
    return any(_dpll(clauses, {**assign, v: val}) for val in (True, False))


def refutable(clauses, w, limit=400000):
    """bounded resolution: all initial clauses, resolvents kept only with at most w literals; True if the empty clause appears"""
    S = {frozenset(c) for c in clauses}
    if frozenset() in S:
        return True
    by_lit = {}
    for c in S:
        for lit in c:
            by_lit.setdefault(lit, set()).add(c)
    frontier = list(S)
    while frontier:
        new = []
        for c in frontier:
            for lit in c:
                for d in list(by_lit.get(-lit, ())):
                    r = (c - {lit}) | (d - {-lit})
                    if len(r) > w or any(-x in r for x in r):
                        continue
                    r = frozenset(r)
                    if not r:
                        return True
                    if r not in S:
                        S.add(r)
                        new.append(r)
                        for x in r:
                            by_lit.setdefault(x, set()).add(r)
                        if len(S) > limit:
                            return None
        frontier = new
    return False


# ---------------------------------------------------------------- networks and their graphs

def random_network(rng, n, L):
    """connected closed network without loops: n knots, L pinned legs, the other slots paired at random"""
    while True:
        slots = [(v, p) for v in range(n) for p in range(3)]
        rng.shuffle(slots)
        legs, rest = slots[:L], slots[L:]
        pairs = [(rest[i], rest[i + 1]) for i in range(0, len(rest), 2)]
        if any(a[0] == b[0] for a, b in pairs):
            continue
        parent = list(range(n))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        for a, b in pairs:
            parent[find(a[0])] = find(b[0])
        if len({find(v) for v in range(n)}) != 1:
            continue
        var, nv, pins = {}, 0, {}
        for a, b in pairs:
            nv += 1
            var[a] = var[b] = nv
        for s in legs:
            nv += 1
            var[s] = nv
            pins[nv] = rng.randint(0, 1)
        return [tuple(var[(v, p)] for p in range(3)) for v in range(n)], pins


def edges_of(scopes, pins):
    occ = {}
    for k, sc in enumerate(scopes):
        for v in sc:
            if v not in pins:
                occ.setdefault(v, []).append(k)
    return {v: tuple(ks) for v, ks in occ.items()}


def bridges(n, E):
    adj = {k: [] for k in range(n)}
    for v, (a, b) in E.items():
        adj[a].append((b, v))
        adj[b].append((a, v))
    disc, low, out, clock = {}, {}, set(), [0]

    def dfs(u, pe):
        disc[u] = low[u] = clock[0]
        clock[0] += 1
        for w, e in adj[u]:
            if e == pe:
                continue
            if w in disc:
                low[u] = min(low[u], disc[w])
            else:
                dfs(w, e)
                low[u] = min(low[u], low[w])
                if low[w] > disc[u]:
                    out.add(e)
    dfs(0, None)
    return out


def side(n, E, k, f):
    """knots on the far side of bridge f from knot k"""
    a, b = E[f]
    start = b if a == k else a
    seen, stack = {start}, [start]
    while stack:
        u = stack.pop()
        for v, (x, y) in E.items():
            if v == f:
                continue
            for p, q in ((x, y), (y, x)):
                if p == u and q not in seen:
                    seen.add(q)
                    stack.append(q)
    return seen


def cycle_blocks(n, E, br):
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for v, (a, b) in E.items():
        if v not in br:
            parent[find(a)] = find(b)
    blocks = {}
    for v, (a, b) in E.items():
        if v not in br:
            blocks.setdefault(find(a), []).append(v)
    return list(blocks.values())


def leg_relation(scopes, pins, Rs, keep, legs):
    """allowed values of `legs` in the sub-network formed by the knots in `keep` (all other variables of those knots are internal
    to it or pinned)"""
    skip = set(range(len(scopes))) - set(keep)
    base = clauses_of(scopes, pins, Rs, skip)
    return {t for t in itertools.product((0, 1), repeat=len(legs))
            if satisfiable(base + [[v] if b else [-v] for v, b in zip(legs, t)])}


def is_cactus(n, E, br):
    deg = [0] * n
    for v, (a, b) in E.items():
        if v not in br:
            deg[a] += 1
            deg[b] += 1
    return all(d <= 2 for d in deg)


def odd_wire_cycles(scopes, pins, Rs, n, E, br):
    """every cycle block: pendant parts force constants, every face on the cycle is a wire, an odd number of them unequal"""
    for block in cycle_blocks(n, E, br):
        knots_in = {k for v in block for k in E[v]}
        unequal = 0
        for k in knots_in:
            sc = scopes[k]
            cyc = [i for i, v in enumerate(sc) if v in block]
            if len(cyc) != 2:
                return False
            (third,) = [i for i in range(3) if i not in cyc]
            f = sc[third]
            if f in pins:
                c = pins[f]
            else:
                far = side(n, E, k, f)
                rel = leg_relation(scopes, pins, Rs, far, [f])
                if len(rel) != 1:
                    return False
                (c,) = next(iter(rel))
            face = {(t[cyc[0]], t[cyc[1]]) for t in excluded(Rs[k]) if t[third] == c}
            if face == {(0, 0), (1, 1)}:
                unequal += 1
            elif face != {(0, 1), (1, 0)}:
                return False
        if unequal % 2 == 0:
            return False
    return True


def minimal_at_knot_level(scopes, pins, Rs):
    return all(satisfiable(clauses_of(scopes, pins, Rs, skip={k})) for k in range(len(scopes)))


# ---------------------------------------------------------------- checks

def counting_checks(K):
    co_independent = []
    for m in range(1, 256):
        S = frozenset(CUBE[i] for i in range(8) if m >> i & 1)
        Z = [t for t in CUBE if t not in S]
        if all(sum(a != b for a, b in zip(s, t)) != 1 for s in Z for t in Z):
            co_independent.append(S)
    four = [S for S in co_independent if len(S) == 4]
    return {"fewest tuples allowed by a non-parity knot": min(len(R) for R in K if not is_parity(R)),
            "co-independent three-place relations": len(co_independent),
            "fewest tuples allowed by one of them": min(len(S) for S in co_independent),
            "those allowing exactly four are the two parity relations": len(four) == 2 and all(
                len({sum(t) % 2 for t in S}) == 1 for S in four)}


def surrounded_checks(rng, K):
    PAR = [R for R in K if is_parity(R)]
    NON = [R for R in K if not is_parity(R)]
    out = {"networks": 0, "unsatisfiable": 0, "surrounded knots in unsatisfiable networks": 0,
           "of which non-parity": 0, "of which parity with the complementary class as the rest": 0,
           "rest relations co-independent": True}
    for _ in range(20000):
        n = rng.randint(3, 10)
        L = rng.randint(0, n)
        if (3 * n - L) % 2:
            L += 1
        scopes, pins = random_network(rng, n, L)
        mode = rng.random()
        Rs = [rng.choice(PAR) if (mode > 0.4 and rng.random() < 0.7) else rng.choice(NON) for _ in range(n)]
        out["networks"] += 1
        if satisfiable(clauses_of(scopes, pins, Rs)):
            continue
        out["unsatisfiable"] += 1
        E = edges_of(scopes, pins)
        br = bridges(n, E)
        for k, sc in enumerate(scopes):
            if any(v in pins for v in sc) or any(v in br for v in sc):
                continue
            out["surrounded knots in unsatisfiable networks"] += 1
            Q = leg_relation(scopes, pins, Rs, [j for j in range(n) if j != k], list(sc))
            Z = [t for t in CUBE if t not in Q]
            out["rest relations co-independent"] &= bool(Q) and all(
                sum(a != b for a, b in zip(s, t)) != 1 for s in Z for t in Z)
            if not is_parity(Rs[k]):
                out["of which non-parity"] += 1
            elif Q == set(excluded(Rs[k])):
                out["of which parity with the complementary class as the rest"] += 1
    return out


def necklace_checks(rng, K):
    NON = [R for R in K if not is_parity(R)]
    out = {"networks": 0, "unsatisfiable": 0, "cacti": 0, "every cycle an odd wire cycle": 0,
           "refuted with derived clauses of at most two literals": 0, "minimal at the knot level": 0,
           "largest number of cycles": 0}
    for _ in range(100000):
        n = rng.randint(3, 11)
        L = rng.randint(max(0, n - 4), n + 2)
        if (3 * n - L) % 2:
            L += 1
        if L > 3 * n - 2:
            continue
        scopes, pins = random_network(rng, n, L)
        Rs = [rng.choice(NON) for _ in range(n)]
        out["networks"] += 1
        cls = clauses_of(scopes, pins, Rs)
        if satisfiable(cls):
            continue
        out["unsatisfiable"] += 1
        E = edges_of(scopes, pins)
        br = bridges(n, E)
        out["cacti"] += is_cactus(n, E, br)
        out["every cycle an odd wire cycle"] += odd_wire_cycles(scopes, pins, Rs, n, E, br)
        out["refuted with derived clauses of at most two literals"] += refutable(cls, 2) is True
        out["minimal at the knot level"] += minimal_at_knot_level(scopes, pins, Rs)
        out["largest number of cycles"] = max(out["largest number of cycles"], len(cycle_blocks(n, E, br)))
    return out


def build(knot_list, pins_by_name):
    """knot_list: (relation, (name_x, name_y, name_z)); names shared by two knots are edges, pinned names are legs"""
    names = sorted({s for _, sc in knot_list for s in sc})
    V = {s: i + 1 for i, s in enumerate(names)}
    return [tuple(V[s] for s in sc) for _, sc in knot_list], {V[s]: b for s, b in pins_by_name.items()}, [R for R, _ in knot_list]


def necklaces(R):
    """R excludes 000 and 110 (z or x != y, control third). Odd rings of three knots with two controls pinned to 0 force the third
    control to 1; a combiner excludes all ones."""
    def ring(i):
        return [(R, (f"r{i}a", f"r{i}b", f"p{i}a")), (R, (f"r{i}b", f"r{i}c", f"p{i}b")), (R, (f"r{i}c", f"r{i}a", f"c{i}"))], \
               {f"p{i}a": 0, f"p{i}b": 0}
    out = {}
    k1, p1 = ring(1)
    out[1] = build([(R, (s[0], s[1], f"q{j}")) for j, (_, s) in enumerate(k1)], {"q0": 0, "q1": 0, "q2": 0})
    k1, p1 = ring(1)
    k2, p2 = ring(2)
    out[2] = build(k1 + k2 + [(R, ("c1", "c2", "m"))], {**p1, **p2, "m": 0})
    k3, p3 = ring(3)
    out[3] = build(k1 + k2 + k3 + [(R, ("c1", "c2", "z")), (R, ("c3", "z", "w"))], {**p1, **p2, **p3, "w": 0})
    return out


def necklace_family(K):
    R = frozenset(t for t in CUBE if t not in {(0, 0, 0), (1, 1, 0)})
    assert R in K
    rows = {}
    for k, (scopes, pins, Rs) in necklaces(R).items():
        n = len(scopes)
        E = edges_of(scopes, pins)
        br = bridges(n, E)
        cls = clauses_of(scopes, pins, Rs)
        rows[f"{k} ring(s)"] = {"knots": n, "unsatisfiable": not satisfiable(cls),
                                "minimal at the knot level": minimal_at_knot_level(scopes, pins, Rs),
                                "cycles": len(cycle_blocks(n, E, br)), "cactus": is_cactus(n, E, br),
                                "every cycle an odd wire cycle": odd_wire_cycles(scopes, pins, Rs, n, E, br),
                                "refuted with derived clauses of at most two literals": refutable(cls, 2) is True}
    return rows


PETERSEN = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 5), (1, 6), (2, 7), (3, 8), (4, 9), (5, 7), (7, 9), (9, 6), (6, 8), (8, 5)]
CUBE_GRAPH = [(a, a ^ (1 << i)) for a in range(8) for i in range(3) if a < a ^ (1 << i)]
K33 = [(a, b) for a in range(3) for b in range(3, 6)]


def balanced_boundary(n, edges):
    best = None
    for h in range(1, n):
        if not (n / 3 <= h < 2 * n / 3):
            continue
        for H in itertools.combinations(range(n), h):
            Hs = set(H)
            b = sum((a in Hs) != (c in Hs) for a, c in edges)
            best = b if best is None else min(best, b)
    return best


def parity_network_checks(K, n, edges):
    """one odd and n - 1 even parity knots on a cubic graph: unsatisfiable; no refutation narrower than the balanced boundary"""
    even = frozenset(t for t in CUBE if sum(t) % 2 == 0)
    odd = frozenset(t for t in CUBE if sum(t) % 2 == 1)
    assert even in K and odd in K
    slots = {v: [] for v in range(n)}
    for i, (a, b) in enumerate(edges):
        slots[a].append(i + 1)
        slots[b].append(i + 1)
    scopes = [tuple(slots[v]) for v in range(n)]
    Rs = [odd] + [even] * (n - 1)
    cls = clauses_of(scopes, {}, Rs)
    b = balanced_boundary(n, edges)
    return {"balanced edge boundary": b, "unsatisfiable": not satisfiable(cls),
            "minimal at the knot level": minimal_at_knot_level(scopes, {}, Rs),
            "refuted with derived clauses of fewer literals than the boundary": refutable(cls, b - 1),
            "refuted with derived clauses of at most two literals": refutable(cls, 2)}


def cut_edge_checks(K):
    """Corollary 6: one edge of a cubic graph cut into two legs pinned to different values; every knot the same parity knot"""
    out = {}
    for label, n, edges in (("Petersen graph", 10, PETERSEN), ("cube graph", 8, CUBE_GRAPH)):
        for par in (0, 1):
            P = frozenset(t for t in CUBE if sum(t) % 2 == par)
            assert P in K
            slots = {v: [] for v in range(n)}
            for i, (a, b) in enumerate(edges[1:]):
                slots[a].append(i + 1)
                slots[b].append(i + 1)
            a, b = edges[0]
            slots[a].append(100)
            slots[b].append(101)
            scopes = [tuple(slots[v]) for v in range(n)]
            unequal = not satisfiable(clauses_of(scopes, {100: 0, 101: 1}, [P] * n))
            equal = satisfiable(clauses_of(scopes, {100: 1, 101: 1}, [P] * n))
            out[f"{label}, {'even' if par == 0 else 'odd'} knots: unsatisfiable with unequal pins, satisfiable with equal"] = unequal and equal
    return out


def boundary_lemma_checks(rng, K):
    """minimal unsatisfiability at the knot level for random unsatisfiable networks (any knots)"""
    PAR = [R for R in K if is_parity(R)]
    tested = minimal = 0
    for _ in range(3000):
        n = rng.randint(3, 9)
        L = rng.randint(0, n)
        if (3 * n - L) % 2:
            L += 1
        scopes, pins = random_network(rng, n, L)
        Rs = [rng.choice(PAR) if rng.random() < 0.6 else rng.choice(K) for _ in range(n)]
        if satisfiable(clauses_of(scopes, pins, Rs)):
            continue
        tested += 1
        minimal += minimal_at_knot_level(scopes, pins, Rs)
    return {"unsatisfiable networks": tested, "minimal at the knot level": minimal}


def controls(K, petersen):
    R = frozenset(t for t in CUBE if t not in {(0, 0, 0), (1, 1, 0)})
    # a knot whose three edges are bridges: each pendant knot (control pinned 0, one wire pinned 1) forces its edge to 0
    scopes, pins, Rs = build([(R, ("x", "y", "z")), (R, ("x", "u1", "k1")), (R, ("y", "u2", "k2")), (R, ("z", "u3", "k3"))],
                             {"u1": 1, "u2": 1, "u3": 1, "k1": 0, "k2": 0, "k3": 0})
    E = edges_of(scopes, pins)
    br = bridges(len(scopes), E)
    Q = leg_relation(scopes, pins, Rs, [1, 2, 3], list(scopes[0]))
    bridged = (not satisfiable(clauses_of(scopes, pins, Rs)) and all(v in br for v in scopes[0])
               and not is_parity(Rs[0]) and Q == {(0, 0, 0)})
    # hubs: not-all-equal on all ten triples of five places is unsatisfiable; the rest of any one triple allows only 000 and 111
    nae = frozenset(t for t in CUBE if 0 < sum(t) < 3)
    triples = list(itertools.combinations(range(1, 6), 3))
    hub_cls = clauses_of(triples, {}, [nae] * 10)
    rest = clauses_of(triples, {}, [nae] * 10, skip={0})
    Qh = {t for t in CUBE if satisfiable(rest + [[v] if b else [-v] for v, b in zip(triples[0], t)])}
    hub = not satisfiable(hub_cls) and Qh == {(0, 0, 0), (1, 1, 1)}
    return {"a non-parity knot whose edges are bridges can be unsatisfiable (connectivity is needed)": bridged,
            "with hubs a surrounded non-parity knot can be unsatisfiable (rest allows only 000 and 111)": hub,
            "parity networks are not refuted with derived clauses of at most two literals": all(
                r["refuted with derived clauses of at most two literals"] is False for r in petersen.values())}


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    rng = random.Random(20261024)
    K = knots()
    counting = counting_checks(K)
    surrounded = surrounded_checks(rng, K)
    neck = necklace_checks(rng, K)
    family = necklace_family(K)
    pet = {"Petersen graph": parity_network_checks(K, 10, PETERSEN), "cube graph": parity_network_checks(K, 8, CUBE_GRAPH),
           "complete bipartite graph on three and three": parity_network_checks(K, 6, K33)}
    lemma = boundary_lemma_checks(rng, K)
    cut = cut_edge_checks(K)
    ctl = controls(K, pet)
    ok = (counting["fewest tuples allowed by a non-parity knot"] == 5 and counting["fewest tuples allowed by one of them"] == 4
          and counting["those allowing exactly four are the two parity relations"]
          and surrounded["of which non-parity"] == 0 and surrounded["rest relations co-independent"]
          and surrounded["of which parity with the complementary class as the rest"]
          == surrounded["surrounded knots in unsatisfiable networks"] > 0
          and neck["unsatisfiable"] > 0
          and neck["cacti"] == neck["every cycle an odd wire cycle"] == neck["minimal at the knot level"]
          == neck["refuted with derived clauses of at most two literals"] == neck["unsatisfiable"]
          and all(r["unsatisfiable"] and r["minimal at the knot level"] and r["cactus"] and r["every cycle an odd wire cycle"]
                  and r["refuted with derived clauses of at most two literals"] for r in family.values())
          and [r["cycles"] for r in family.values()] == [1, 2, 3]
          and [r["balanced edge boundary"] for r in pet.values()] == [5, 4, 4]
          and all(r["unsatisfiable"] and r["minimal at the knot level"]
                  and r["refuted with derived clauses of fewer literals than the boundary"] is False for r in pet.values())
          and lemma["minimal at the knot level"] == lemma["unsatisfiable networks"] > 0 and all(cut.values())
          and all(ctl.values()))
    result["checks"] = {"counting": counting, "surrounded knots": surrounded, "random networks without parity knots": neck,
                        "necklaces of odd rings": family, "parity networks on cubic graphs": pet,
                        "minimal unsatisfiability at the knot level": lemma, "cut-edge parity networks": cut}
    result["controls"] = ctl
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        ok = ok and old == text
    print(json.dumps({"status": result["status"], "checks": result["checks"], "controls": ctl}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
