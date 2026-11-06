#!/usr/bin/env python3
"""Checks for GALLAI-KNOTS-20261020-001B-P001. The statements are in proof.md.

Notation:
- W is a connected witness graph with maximum degree at most q.
- Each vertex v of W carries q - deg(v) pendant leaves.
- R_W is the set of leaf colourings that extend to a proper q-colouring.
- Bad_q(W) is the set of list assignments, with L(v) a subset of [q] of size
  deg(v), from which W is not colourable.

Checks:
- Lemma 1 (greedy). Random instances.
- Lemma 2. The excluded leaf colourings are exactly the realizations of
  Bad_q(W), each in prod (q - deg v)! leaf orders. Checked on every witness
  graph on at most 6 vertices, up to isomorphism, within the leaf caps.
- Lemma 3. K2 and K3 hold on the same networks. The proof's construction is
  also run on random larger networks.
- Lemma 4. On 2-connected graphs, every bad assignment is constant, and
  Bad_q is nonempty exactly for complete graphs and odd cycles. Exhaustive on
  at most 6 vertices, random on 7 and 8.
- Theorem 1 (gluing law). On random pairs, the bad assignments of the glued
  graph are the joins of the parts' bad assignments with disjoint lists at the
  glued vertex, and the split is unique.
- Corollary 2. Bad_q(W) is nonempty exactly for Gallai trees.
- Theorem 3. R_W passes K1-K3 exactly when W is a Gallai tree.
- Theorem 4. On Gallai trees, Bad_q(W) is the set of block colour-set systems.
  The number of excluded leaf colourings is q! times the product of the block
  masses, and q! ((q-1)!)^(k-1) for a tree on k vertices.
- Corollary 5. At d = q, the branch-freezing polynomial is
  (q-1)!/(q-1)^(q-1) p^(q-1). It lies below the diagonal for q >= 3 and is
  the identity for q = 2. In the rainbow colouring, a ball is the only
  extension of its boundary.
- Remark 6. Two star knots sharing a visible vertex fail K2. Hiding that
  vertex leaves no constraint. The union witness network carries a knot.

Controls, each of which must be rejected:
- knot iff tree;
- knot iff bipartite;
- knot iff every block is complete;
- Lemma 1 without a strict vertex;
- a glued vertex is never split.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import random
import sys
from collections import deque
from fractions import Fraction
from itertools import combinations, permutations, product
from math import comb, factorial, prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEAF_CAPS = {2: 12, 3: 9, 4: 7}
BAD_CAP = 120_000


# ------------------------------------------------------------------ graphs

def adjacency(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def connected(n, edges):
    if n <= 1:
        return True
    adj = adjacency(n, edges)
    seen, stack = {0}, [0]
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == n


def blocks(n, edges):
    """Blocks as (sorted vertex list, edge list), by Tarjan's algorithm."""
    adj = [[] for _ in range(n)]
    for i, (a, b) in enumerate(edges):
        adj[a].append((b, i))
        adj[b].append((a, i))
    disc, low, timer, stack, out = {}, {}, [0], [], []

    def dfs(u, pe):
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        for w, i in adj[u]:
            if i == pe:
                continue
            if w not in disc:
                stack.append(i)
                dfs(w, i)
                low[u] = min(low[u], low[w])
                if low[w] >= disc[u]:
                    comp = []
                    while True:
                        e = stack.pop()
                        comp.append(edges[e])
                        if e == i:
                            break
                    out.append((sorted({v for e in comp for v in e}), comp))
            elif disc[w] < disc[u]:
                stack.append(i)
                low[u] = min(low[u], disc[w])

    if n:
        dfs(0, None)
    return out


def block_kind(verts, bedges):
    m, e = len(verts), len(bedges)
    if e == m * (m - 1) // 2:
        return "complete"
    deg = dict.fromkeys(verts, 0)
    for a, b in bedges:
        deg[a] += 1
        deg[b] += 1
    if e == m and all(d == 2 for d in deg.values()):
        return "odd cycle" if m % 2 else "even cycle"
    return "other"


def gallai(n, edges):
    return all(block_kind(v, e) in ("complete", "odd cycle") for v, e in blocks(n, edges))


def bipartite(n, edges):
    adj = adjacency(n, edges)
    side = {0: 0}
    queue = deque([0])
    while queue:
        u = queue.popleft()
        for w in adj[u]:
            if w not in side:
                side[w] = 1 - side[u]
                queue.append(w)
            elif side[w] == side[u]:
                return False
    return True


def canonical(k, edges):
    """Least edge list over the orderings that sort vertices by degree."""
    deg = [0] * k
    for a, b in edges:
        deg[a] += 1
        deg[b] += 1
    groups = {}
    for v in range(k):
        groups.setdefault(deg[v], []).append(v)
    best = None
    for perms in product(*(list(permutations(groups[d])) for d in sorted(groups))):
        pos = {v: i for i, v in enumerate(v for p in perms for v in p)}
        key = tuple(sorted(tuple(sorted((pos[a], pos[b]))) for a, b in edges))
        if best is None or key < best:
            best = key
    return best


def iso_classes(max_k):
    out = []
    for k in range(1, max_k + 1):
        pairs = list(combinations(range(k), 2))
        seen = set()
        for mask in range(1 << len(pairs)):
            edges = [pairs[i] for i in range(len(pairs)) if mask >> i & 1]
            if connected(k, edges):
                key = canonical(k, edges)
                if key not in seen:
                    seen.add(key)
                    out.append((k, list(key)))
    return out


def random_connected(rng, n, p, q):
    """A random spanning tree of maximum degree at most q, plus random edges that keep the bound."""
    deg, edges = [0] * n, set()
    for v in range(1, n):
        u = rng.choice([w for w in range(v) if deg[w] < q])
        edges.add((u, v))
        deg[u] += 1
        deg[v] += 1
    for a, b in combinations(range(n), 2):
        if (a, b) not in edges and deg[a] < q and deg[b] < q and rng.random() < p:
            edges.add((a, b))
            deg[a] += 1
            deg[b] += 1
    return sorted(edges)


def random_gallai(rng, q, max_vertices):
    """Attach complete graphs K_m (m <= q) and odd cycles at vertices with spare degree."""
    edges, n = [], 0

    def add_block(anchor):
        nonlocal n
        cycle = rng.random() < 0.4
        m = rng.choice([3, 5]) if cycle else rng.randint(2, q)
        new = list(range(n, n + m - (anchor is not None)))
        verts = ([anchor] if anchor is not None else []) + new
        n += len(new)
        if cycle:
            edges.extend((verts[i], verts[(i + 1) % m]) for i in range(m))
        else:
            edges.extend(combinations(verts, 2))

    add_block(None)
    for _ in range(12):
        deg = [0] * n
        for a, b in edges:
            deg[a] += 1
            deg[b] += 1
        spare = [v for v in range(n) if deg[v] <= q - 2]
        if not spare or n >= max_vertices:
            break
        saved = (list(edges), n)
        add_block(rng.choice(spare))
        deg = [0] * n
        for a, b in edges:
            deg[a] += 1
            deg[b] += 1
        if max(deg) > q or n > max_vertices:
            edges[:], n = saved
    return n, sorted({tuple(sorted(e)) for e in edges})


# ------------------------------------------------------------------ colouring, relations, bad assignments

def colourable(n, adj, lists):
    order = sorted(range(n), key=lambda v: len(lists[v]))
    colour = [None] * n

    def go(i):
        if i == n:
            return True
        v = order[i]
        for c in lists[v]:
            if all(colour[w] != c for w in adj[v]):
                colour[v] = c
                if go(i + 1):
                    return True
        colour[v] = None
        return False

    return go(0)


def owners_of(n, edges, q):
    deg = [len(a) for a in adjacency(n, edges)]
    return [v for v in range(n) for _ in range(q - deg[v])]


def leaf_relation(n, edges, q):
    adj = adjacency(n, edges)
    owners = owners_of(n, edges, q)
    cache, rel = {}, set()
    for t in product(range(q), repeat=len(owners)):
        lists = [set(range(q)) for _ in range(n)]
        for v, c in zip(owners, t):
            lists[v].discard(c)
        key = tuple(tuple(sorted(s)) for s in lists)
        if key not in cache:
            cache[key] = colourable(n, adj, key)
        if cache[key]:
            rel.add(t)
    return rel, owners


def knot(rel, k, q):
    if not rel or len(rel) == q ** k:
        return False
    return all(len({t[:i] + t[i + 1:] for t in rel}) == q ** (k - 1) for i in range(k))


def projections_full(rel, k, q):
    return all(len({t[:i] + t[i + 1:] for t in rel}) == q ** (k - 1) for i in range(k))


def bad_assignments(n, edges, q):
    adj = adjacency(n, edges)
    choices = [list(combinations(range(q), len(adj[v]))) for v in range(n)]
    if prod(len(c) for c in choices) > BAD_CAP:
        return None
    return {L for L in product(*choices) if not colourable(n, adj, L)}


def block_systems(n, edges, q):
    bl = blocks(n, edges)
    sizes = [len(v) - 1 if block_kind(v, e) == "complete" else 2 for v, e in bl]
    if prod(comb(q, s) for s in sizes) > BAD_CAP:
        return None
    out = set()
    for choice in product(*(combinations(range(q), s) for s in sizes)):
        used = [set() for _ in range(n)]
        ok = True
        for (verts, _), C in zip(bl, choice):
            if any(used[v] & set(C) for v in verts):
                ok = False
                break
            for v in verts:
                used[v] |= set(C)
        if ok:
            out.add(tuple(tuple(sorted(u)) for u in used))
    return out


def block_mass(verts, bedges, q):
    m = len(verts)
    if block_kind(verts, bedges) == "complete":
        return Fraction(factorial(q - m + 1) ** (m - 1), factorial(m - 1))
    return Fraction(factorial(q - 2) ** (m - 1), 2)


def greedy_from(n, adj, lists, root):
    dist = {root: 0}
    queue, order = deque([root]), [root]
    while queue:
        u = queue.popleft()
        for w in adj[u]:
            if w not in dist:
                dist[w] = dist[u] + 1
                queue.append(w)
                order.append(w)
    colour = {}
    for v in reversed(order):
        options = [c for c in sorted(lists[v]) if all(colour.get(w) != c for w in adj[v])]
        if not options:
            return None
        colour[v] = options[0]
    return colour


def lemma3_completion(n, adj, q, owners, t, index):
    """The proof of Lemma 3: colour W - v0 from neighbours of v0, then pick c* and a leaf colour other than c*."""
    v0 = owners[index]
    lists = [set(range(q)) for _ in range(n)]
    for i, (v, c) in enumerate(zip(owners, t)):
        if i != index:
            lists[v].discard(c)
    colour, seen = {}, {v0}
    for u in sorted(adj[v0]):
        if u in seen:
            continue
        order, queue = [u], deque([u])
        seen.add(u)
        while queue:
            a = queue.popleft()
            for b in adj[a]:
                if b not in seen:
                    seen.add(b)
                    queue.append(b)
                    order.append(b)
        for v in reversed(order):
            options = [c for c in sorted(lists[v]) if all(colour.get(w) != c for w in adj[v] if w != v0)]
            if not options:
                return False
            colour[v] = options[0]
    blocked = {colour[w] for w in adj[v0]} | {t[i] for i, v in enumerate(owners) if v == v0 and i != index}
    free = [c for c in range(q) if c not in blocked]
    if not free:
        return False
    colour[v0] = free[0]
    full = list(t)
    full[index] = next(c for c in range(q) if c != free[0])
    final = [set(range(q)) - {full[i] for i, v in enumerate(owners) if v == w} for w in range(n)]
    return all(colour[v] in final[v] for v in range(n)) and all(colour[a] != colour[b] for a in range(n) for b in adj[a])


def glue(n1, e1, x1, n2, e2, x2):
    relabel, nxt = {}, n1
    for v in range(n2):
        if v == x2:
            relabel[v] = x1
        else:
            relabel[v] = nxt
            nxt += 1
    edges = sorted({tuple(sorted(e)) for e in e1} | {tuple(sorted((relabel[a], relabel[b]))) for a, b in e2})
    return nxt, edges, relabel


# ------------------------------------------------------------------ the checks

def run():
    checks, controls, failures = {}, {}, []
    rng = random.Random(20261020)
    classes = iso_classes(6)
    counts = [sum(1 for k, _ in classes if k == j) for j in range(1, 7)]
    checks["graphs_up_to_isomorphism"] = {"counts": counts, "matches_A001349": counts == [1, 1, 2, 6, 21, 112]}
    if counts != [1, 1, 2, 6, 21, 112]:
        failures.append("graph enumeration")

    # Lemma 1
    lemma1 = {"instances": 0, "coloured": 0}
    for _ in range(1500):
        n, q = rng.randint(2, 8), rng.randint(3, 5)
        edges = random_connected(rng, n, 0.45, n)
        adj = adjacency(n, edges)
        deg = [len(a) for a in adj]
        palette, root = max(deg) + 2, rng.randrange(n)
        lists = [set(rng.sample(range(palette), min(palette, deg[v] + (v == root) + rng.choice([0, 0, 1]))))
                 for v in range(n)]
        if any(len(lists[v]) < deg[v] for v in range(n)) or len(lists[root]) <= deg[root]:
            continue
        lemma1["instances"] += 1
        col = greedy_from(n, adj, lists, root)
        lemma1["coloured"] += col is not None and all(col[a] != col[b] for a, b in edges) and all(
            col[v] in lists[v] for v in range(n))
    checks["lemma_1_greedy"] = lemma1
    if not lemma1["instances"] or lemma1["coloured"] != lemma1["instances"]:
        failures.append("Lemma 1")

    # Lemmas 2-4, Corollary 2 and Theorems 3-4 on every class (leaf relations within the caps)
    lem2 = {"networks": 0, "excluded_match": 0}
    lem3 = {"networks": 0, "nonempty_and_projections_full": 0}
    thm3 = {"networks": 0, "gallai": 0, "knots": 0, "agree": 0}
    cor2 = {"graphs": 0, "gallai": 0, "agree": 0, "skipped_by_cap": 0}
    lem4 = {"two_connected": 0, "bad_constant": 0, "nonempty_iff_complete_or_odd_cycle": 0}
    thm4 = {"gallai_trees": 0, "systems_match": 0, "mass_match": 0, "trees": 0, "tree_formula": 0}
    control_tree = control_bip = control_blockgraph = 0
    for q in (2, 3, 4):
        for k, edges in classes:
            adj = adjacency(k, edges)
            deg = [len(a) for a in adj]
            if max(deg) > q:
                continue
            is_g = gallai(k, edges)
            bad = bad_assignments(k, edges, q)
            if bad is None:
                cor2["skipped_by_cap"] += 1
            else:
                cor2["graphs"] += 1
                cor2["gallai"] += is_g
                cor2["agree"] += bool(bad) == is_g
                bl = blocks(k, edges)
                if k >= 2 and len(bl) == 1:
                    lem4["two_connected"] += 1
                    lem4["bad_constant"] += all(len(set(L)) == 1 for L in bad)
                    lem4["nonempty_iff_complete_or_odd_cycle"] += bool(bad) == (
                        block_kind(*bl[0]) in ("complete", "odd cycle"))
                if is_g:
                    systems = block_systems(k, edges, q)
                    thm4["gallai_trees"] += 1
                    thm4["systems_match"] += systems == bad
                    excluded = len(bad) * prod(factorial(q - d) for d in deg)
                    mass = factorial(q) * prod((block_mass(v, e, q) for v, e in bl), start=Fraction(1))
                    thm4["mass_match"] += excluded == mass
                    if len(edges) == k - 1:
                        thm4["trees"] += 1
                        thm4["tree_formula"] += excluded == factorial(q) * factorial(q - 1) ** (k - 1)
            leaves = sum(q - d for d in deg)
            if leaves == 0 or leaves > LEAF_CAPS[q] or bad is None:
                continue
            rel, owners = leaf_relation(k, edges, q)
            excluded = {t for t in product(range(q), repeat=len(owners)) if t not in rel}
            realized = set()
            for t in product(range(q), repeat=len(owners)):
                per = [[c for c, v in zip(t, owners) if v == w] for w in range(k)]
                if all(len(set(p)) == len(p) for p in per):
                    if tuple(tuple(sorted(set(range(q)) - set(p))) for p in per) in bad:
                        realized.add(t)
            lem2["networks"] += 1
            lem2["excluded_match"] += excluded == realized and len(excluded) == len(bad) * prod(
                factorial(q - d) for d in deg)
            lem3["networks"] += 1
            lem3["nonempty_and_projections_full"] += bool(rel) and projections_full(rel, len(owners), q)
            is_knot = knot(rel, len(owners), q)
            thm3["networks"] += 1
            thm3["gallai"] += is_g
            thm3["knots"] += is_knot
            thm3["agree"] += is_knot == is_g
            control_tree += is_knot != (len(edges) == k - 1)
            control_bip += is_knot != bipartite(k, edges)
            control_blockgraph += is_knot != all(block_kind(v, e) == "complete" for v, e in blocks(k, edges))
    checks["lemma_2_exhaustive"] = lem2
    checks["lemma_3_exhaustive"] = lem3
    checks["lemma_4_exhaustive"] = lem4
    checks["corollary_2_exhaustive"] = cor2
    checks["theorem_3_exhaustive"] = thm3
    checks["theorem_4_exhaustive"] = thm4
    for name, row, key, total in (("Lemma 2", lem2, "excluded_match", "networks"),
                                  ("Lemma 3", lem3, "nonempty_and_projections_full", "networks"),
                                  ("Theorem 3", thm3, "agree", "networks"), ("Corollary 2", cor2, "agree", "graphs"),
                                  ("Lemma 4 constant", lem4, "bad_constant", "two_connected"),
                                  ("Lemma 4 kinds", lem4, "nonempty_iff_complete_or_odd_cycle", "two_connected"),
                                  ("Theorem 4 systems", thm4, "systems_match", "gallai_trees"),
                                  ("Theorem 4 mass", thm4, "mass_match", "gallai_trees"),
                                  ("Theorem 4 trees", thm4, "tree_formula", "trees")):
        if not row[total] or row[key] != row[total]:
            failures.append(f"{name} on the exhaustive classes")

    # Lemma 3's construction, Lemma 4 and Theorem 4 on random larger graphs
    lem3_random = {"instances": 0, "completed": 0}
    for _ in range(600):
        q = rng.choice([3, 4, 5])
        n = rng.randint(5, 12)
        edges = random_connected(rng, n, rng.uniform(0.2, 0.5), q)
        owners = owners_of(n, edges, q)
        if not owners:
            continue
        t = [rng.randrange(q) for _ in owners]
        lem3_random["instances"] += 1
        lem3_random["completed"] += lemma3_completion(n, adjacency(n, edges), q, owners, t, rng.randrange(len(owners)))
    checks["lemma_3_construction_random"] = lem3_random
    if not lem3_random["instances"] or lem3_random["completed"] != lem3_random["instances"]:
        failures.append("Lemma 3 construction")

    lem4_random = {"two_connected": 0, "bad_constant": 0, "nonempty_iff_complete_or_odd_cycle": 0}
    for _ in range(400):
        q = rng.choice([3, 4])
        n = rng.randint(7, 8)
        edges = random_connected(rng, n, rng.uniform(0.25, 0.6), q)
        bl = blocks(n, edges)
        if len(bl) != 1:
            continue
        bad = bad_assignments(n, edges, q)
        if bad is None:
            continue
        lem4_random["two_connected"] += 1
        lem4_random["bad_constant"] += all(len(set(L)) == 1 for L in bad)
        lem4_random["nonempty_iff_complete_or_odd_cycle"] += bool(bad) == (
            block_kind(*bl[0]) in ("complete", "odd cycle"))
    bad = bad_assignments(7, [(i, (i + 1) % 7) for i in range(7)], 3)
    lem4_random["two_connected"] += 1
    lem4_random["bad_constant"] += bad is not None and all(len(set(L)) == 1 for L in bad)
    lem4_random["nonempty_iff_complete_or_odd_cycle"] += bad is not None and len(bad) == 3
    checks["lemma_4_random"] = lem4_random
    if lem4_random["two_connected"] <= 1 or not (
            lem4_random["bad_constant"] == lem4_random["nonempty_iff_complete_or_odd_cycle"]
            == lem4_random["two_connected"]):
        failures.append("Lemma 4 on random graphs")

    thm4_random = {"gallai_trees": 0, "systems_match": 0, "mass_match": 0}
    for _ in range(250):
        q = rng.choice([3, 4, 5])
        n, edges = random_gallai(rng, q, 9)
        if not gallai(n, edges):
            failures.append("generator produced a non-Gallai graph")
            continue
        bad = bad_assignments(n, edges, q)
        systems = block_systems(n, edges, q)
        if bad is None or systems is None:
            continue
        deg = [len(a) for a in adjacency(n, edges)]
        thm4_random["gallai_trees"] += 1
        thm4_random["systems_match"] += systems == bad
        mass = factorial(q) * prod((block_mass(v, e, q) for v, e in blocks(n, edges)), start=Fraction(1))
        thm4_random["mass_match"] += len(bad) * prod(factorial(q - d) for d in deg) == mass
    checks["theorem_4_random_gallai_trees"] = thm4_random
    if not thm4_random["gallai_trees"] or not (
            thm4_random["systems_match"] == thm4_random["mass_match"] == thm4_random["gallai_trees"]):
        failures.append("Theorem 4 on random Gallai trees")

    # Theorem 1: the gluing law on random pairs, Gallai or not
    thm1 = {"pairs": 0, "law_holds": 0, "split_unique": 0, "gallai_pairs": 0, "nonempty_glued": 0}
    attempts = 0
    while thm1["pairs"] < 160 and attempts < 4000:
        attempts += 1
        q = rng.choice([3, 4, 5])
        n1, n2 = rng.randint(1, 4), rng.randint(1, 4)
        e1, e2 = random_connected(rng, n1, 0.6, q), random_connected(rng, n2, 0.6, q)
        x1, x2 = rng.randrange(n1), rng.randrange(n2)
        d1, d2 = len(adjacency(n1, e1)[x1]), len(adjacency(n2, e2)[x2])
        if d1 + d2 > q:
            continue
        n, edges, relabel = glue(n1, e1, x1, n2, e2, x2)
        bad, bad1, bad2 = bad_assignments(n, edges, q), bad_assignments(n1, e1, q), bad_assignments(n2, e2, q)
        if bad is None or bad1 is None or bad2 is None:
            continue
        join = set()
        for L1 in bad1:
            for L2 in bad2:
                if set(L1[x1]) & set(L2[x2]):
                    continue
                L = list(L1) + [None] * (n - n1)
                for v in range(n2):
                    L[relabel[v]] = tuple(sorted(set(L1[x1]) | set(L2[x2]))) if v == x2 else L2[v]
                join.add(tuple(L))
        unique = True
        for L in bad:
            splits = 0
            for X1 in combinations(L[x1], d1):
                X2 = tuple(c for c in L[x1] if c not in X1)
                part1 = tuple(X1 if v == x1 else L[v] for v in range(n1))
                part2 = tuple(X2 if v == x2 else L[relabel[v]] for v in range(n2))
                splits += part1 in bad1 and part2 in bad2
            unique &= splits == 1
        thm1["pairs"] += 1
        thm1["law_holds"] += join == bad
        thm1["split_unique"] += unique
        if gallai(n1, e1) and gallai(n2, e2):
            thm1["gallai_pairs"] += 1
            thm1["nonempty_glued"] += bool(bad)
    checks["theorem_1_gluing_law"] = thm1
    if not thm1["pairs"] or not (thm1["law_holds"] == thm1["split_unique"] == thm1["pairs"]) or (
            thm1["nonempty_glued"] != thm1["gallai_pairs"]):
        failures.append("Theorem 1 gluing law")

    # Theorem 3 on random networks beyond six witnesses
    thm3_random = {"gallai_tested": 0, "gallai_knots": 0, "non_gallai_tested": 0, "non_gallai_full": 0}
    for _ in range(300):
        q = rng.choice([3, 4])
        n, edges = random_gallai(rng, q, 9)
        deg = [len(a) for a in adjacency(n, edges)]
        leaves = sum(q - d for d in deg)
        if 0 < leaves <= LEAF_CAPS[q] and n >= 4:
            rel, owners = leaf_relation(n, edges, q)
            thm3_random["gallai_tested"] += 1
            thm3_random["gallai_knots"] += knot(rel, len(owners), q)
        present = set(edges)
        for e in [e for e in combinations(range(n), 2) if e not in present and deg[e[0]] < q and deg[e[1]] < q][:2]:
            new = sorted(edges + [e])
            if gallai(n, new) or not 0 < leaves - 2 <= LEAF_CAPS[q]:
                continue
            rel, owners = leaf_relation(n, new, q)
            thm3_random["non_gallai_tested"] += 1
            thm3_random["non_gallai_full"] += len(rel) == q ** len(owners)
    checks["theorem_3_random_networks"] = thm3_random
    if not (thm3_random["gallai_tested"] and thm3_random["gallai_knots"] == thm3_random["gallai_tested"]
            and thm3_random["non_gallai_tested"]
            and thm3_random["non_gallai_full"] == thm3_random["non_gallai_tested"]):
        failures.append("Theorem 3 on random networks")

    # Corollary 5: the regular tree at d = q
    tree = {}
    for q in range(2, 9):
        m = q - 1
        coeff = Fraction(factorial(m), m ** m)
        points = [Fraction(j, q + 1) for j in range(1, q + 2)]
        identity = all(sum((-1) ** j * comb(m, j) * (1 - j * p / m) ** m for j in range(m + 1)) == coeff * p ** m
                       for p in points)
        tree[str(q)] = {"identity_at_q_plus_1_points": identity, "coefficient": str(coeff),
                        "only_fixed_point_zero": coeff < 1}
    checks["corollary_5_monomial"] = tree
    if not all(row["identity_at_q_plus_1_points"] for row in tree.values()) or not all(
            row["only_fixed_point_zero"] == (int(q) >= 3) for q, row in tree.items()):
        failures.append("Corollary 5 monomial")

    rainbow = {}
    for q, depth in ((3, 3), (4, 2), (5, 2)):
        parent, colour, level, frontier = [None], [0], [0], [0]
        for h in range(depth):
            nxt = []
            for v in frontier:
                cs = list(range(1, q)) + [1] if parent[v] is None else [c for c in range(q) if c != colour[v]]
                for c in cs:
                    parent.append(v)
                    colour.append(c)
                    level.append(h + 1)
                    nxt.append(len(colour) - 1)
            frontier = nxt
        size = len(colour)
        nbrs = [set() for _ in range(size)]
        for v in range(1, size):
            nbrs[v].add(parent[v])
            nbrs[parent[v]].add(v)
        interior = [v for v in range(size) if level[v] < depth]
        fixed = {v: colour[v] for v in range(size) if level[v] == depth}
        found = []

        def extend(i, assign):
            if len(found) > 1:
                return
            if i == len(interior):
                found.append(dict(assign))
                return
            v = interior[i]
            for c in range(q):
                if all(assign.get(w, fixed.get(w)) != c for w in nbrs[v]):
                    assign[v] = c
                    extend(i + 1, assign)
                    del assign[v]

        extend(0, {})
        rainbow[f"q{q}_depth{depth}"] = {
            "proper": all(colour[v] != colour[w] for v in range(size) for w in nbrs[v]),
            "interior_degrees_q": all(len(nbrs[v]) == q for v in interior),
            "extensions_of_boundary": len(found)}
    checks["corollary_5_rainbow_world"] = rainbow
    if not all(r["proper"] and r["interior_degrees_q"] and r["extensions_of_boundary"] == 1 for r in rainbow.values()):
        failures.append("Corollary 5 rainbow world")

    # Remark 6: two star knots sharing a visible vertex u (variable index q - 1)
    hub = {}
    for q in (3, 4):
        k, u = 2 * q - 1, q - 1
        rel = {t for t in product(range(q), repeat=k) if len(set(t[:q])) < q and len(set(t[q - 1:])) < q}
        k2_fails = sum(len({t[:i] + t[i + 1:] for t in rel}) != q ** (k - 1) for i in range(k))
        hidden = {t[:u] + t[u + 1:] for t in rel}
        path_rel, path_owners = leaf_relation(3, [(0, 1), (1, 2)], q)
        hub[str(q)] = {"conjunction_constrained": len(rel) < q ** k, "k2_fails_at": k2_fails,
                       "hiding_u_leaves_full": len(hidden) == q ** (k - 1),
                       "union_witness_is_knot": knot(path_rel, len(path_owners), q)}
    checks["remark_6_hub"] = hub
    if not all(r["conjunction_constrained"] and r["k2_fails_at"] == 2 * int(q) - 2 and r["hiding_u_leaves_full"]
               and r["union_witness_is_knot"] for q, r in hub.items()):
        failures.append("Remark 6 hub")

    # Controls
    controls["knot_iff_tree"] = {"disagreements": control_tree, "rejected": control_tree > 0}
    controls["knot_iff_bipartite"] = {"disagreements": control_bip, "rejected": control_bip > 0}
    controls["knot_iff_every_block_complete"] = {"disagreements": control_blockgraph,
                                                 "rejected": control_blockgraph > 0}
    no_strict = greedy_from(3, adjacency(3, [(0, 1), (1, 2), (0, 2)]), [{0, 1}, {0, 1}, {0, 1}], 0)
    controls["lemma_1_without_strict_vertex"] = {"triangle_with_equal_pairs_coloured": no_strict is not None,
                                                 "rejected": no_strict is None}
    controls["glued_vertex_never_split"] = {"gallai_gluings_with_bad_assignments": thm1["nonempty_glued"],
                                            "rejected": thm1["nonempty_glued"] > 0}
    for name, control in controls.items():
        if not control["rejected"]:
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
