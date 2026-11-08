#!/usr/bin/env python3
"""Checks for LATTICE-NET-20261108-001A: odd tori compose everywhere, even tori never reach the antipode; rings of cuts separate when
they bound.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy (the repository's .venv). 16 worker processes, a few minutes. Every reading here is exact: walk counts are followed until the next row
lies in the span of the earlier ones, and rows of M^T until they repeat, so no lag cutoff is used."""
import hashlib
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import lattice_lib as T  # noqa: E402

N = T.N
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:500], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def algebra(n):
    """the contact graph is the convolution h(p) <- v(p - e2), v(p + e1); v(p) <- h(p), h(p - e1 + e2), and two steps h -> h are L"""
    sizes, contacts, rot, edges, ring, hidx, vidx = T.torus(n, 2)
    ins = T.in_sets(sizes, contacts)
    ok = True
    for i in range(n):
        for j in range(n):
            p = (i, j)
            sh = lambda q: ((q[0]) % n, (q[1]) % n)
            ok &= ins[hidx[p]] == (1 << vidx[sh((i, j - 1))]) ^ (1 << vidx[sh((i + 1, j))])
            ok &= ins[vidx[p]] == (1 << hidx[p]) ^ (1 << hidx[sh((i - 1, j + 1))])
    # two steps from h(0) back to h's: the coefficients of L
    union, first, rows, dim = T.reach(ins, hidx[(0, 0)])
    two = rows[2] if len(rows) > 2 else 0
    pts = {q for q, e in hidx.items() if two >> e & 1}
    ok &= pts == {(1 % n, 0), ((-1) % n, 0), (0, 1 % n), (0, (-1) % n)}
    return n, ok


def odd_points(n):
    """odd n: the powers of L reach exactly the origin and the points off both diagonals; L^(2^r - 1) is supported off them"""
    pw, per = T.powers(n)
    U = np.zeros((n, n), dtype=np.uint8)
    for a in pw:
        U |= a
    want = np.array([[1 if (a == 0 and b == 0) or not T.diagonal(n, a, b) else 0 for b in range(n)] for a in range(n)], dtype=np.uint8)
    r = 1
    while pow(2, r, n) != 1:
        r += 1
    P = T.mono(n, [(0, 0)])
    for _ in range(2 ** r - 1 if 2 ** r - 1 < 5000 else 0):
        P = T.mul(T.L(n), P)
    off = np.array([[0 if T.diagonal(n, a, b) else 1 for b in range(n)] for a in range(n)], dtype=np.uint8)
    explicit = 2 ** r - 1 < 5000
    exact_power = (not explicit) or bool((P == off).all())
    return n, bool((U == want).all()), exact_power, r, explicit


def contacts_need_all(n):
    sizes, contacts, rot, edges, ring, hidx, vidx = T.torus(n, 2)
    ins = T.in_sets(sizes, contacts)
    rc = T.ring_contacts(rot, edges, ring)
    todo = range(len(contacts)) if n <= 7 else (hidx[(0, 0)], vidx[(0, 0)])
    return n, all(T.rings_needed(T.reach(ins, c)[0], rc) == set(rc) for c in todo), len(todo)


def even_points(n):
    """even n: every power of L vanishes at the nonzero diagonal points and at (n/2 - 1, n/2); for n a power of two L^(n/2) = 0"""
    pw, per = T.powers(n)
    h = n // 2
    ok = all(not a[(h - 1) % n, h] for a in pw)
    ok &= all(not a[x % n, y % n] for a in pw[1:] for x in range(n) for y in range(n) if T.diagonal(n, x, y) and (x % n, y % n) != (0, 0))
    ok &= all(not a[x % n, y % n] for a in pw[:1] for x in range(n) for y in range(n) if T.diagonal(n, x, y) and (x % n, y % n) != (0, 0))
    nil = None
    if n & (n - 1) == 0:
        P = T.mono(n, [(0, 0)])
        for _ in range(h):
            P = T.mul(T.L(n), P)
        nil = not P.any()
    return n, ok, nil


def antipode_unneeded(n):
    sizes, contacts, rot, edges, ring, hidx, vidx = T.torus(n, 2)
    ins = T.in_sets(sizes, contacts)
    rc = T.ring_contacts(rot, edges, ring)
    need = T.rings_needed(T.reach(ins, hidx[(0, 0)])[0], rc)
    needv = T.rings_needed(T.reach(ins, vidx[(0, 0)])[0], rc)
    return n, ring[(n // 2, n // 2)] not in need, len(rc) - len(need), len(rc) - len(needv)


def when(args):
    """exact, from the eventually periodic rows of M^T: for each contact (all of them, or h(0) and v(0)) and ring, the lags at which
    the contact needs the ring; predicted: needed iff the ring has a contact in the reach, first at g k + 1 (k the least walk length
    with an odd count), and needed in the periodic part whenever needed at all"""
    n, g, allc = args
    sizes, contacts, rot, edges, ring, hidx, vidx = T.torus(n, g)
    ins = T.in_sets(sizes, contacts)
    rc = T.ring_contacts(rot, edges, ring)
    rows, Nb, blocks = N.matrix(sizes, (60,) * len(sizes), contacts)
    todo = range(len(contacts)) if allc else (hidx[(0, 0)], vidx[(0, 0)])
    pairs = 0
    for c in todo:
        union, first, _, _ = T.reach(ins, c)
        seq, T1, p = N.orbit(rows, 1 << c, 10 ** 6)
        for r, cs in rc.items():
            m = N.mask(blocks, r)
            lags = [t + 1 for t, x in enumerate(seq) if x & m]
            ks = [first[d] for d in cs if union >> d & 1]
            if not ks:
                if lags:
                    return n, g, False, (c, r, "needed but unreached")
                continue
            pairs += 1
            if not lags or lags[0] != g * min(ks) + 1 or not any(t >= T1 for t in lags):
                return n, g, False, (c, r, lags[:3], min(ks), T1)
    return n, g, True, pairs


def block_cut(args):
    """cutting the edge boundary of a set R of rings: afterwards no uncut contact with both rings in R needs a ring outside, and none
    with both rings outside needs a ring in R; before the cut (odd n) every inside contact needed some ring outside"""
    n, R = args
    sizes, contacts, rot, edges, ring, hidx, vidx = T.torus(n, 2)
    Ri = {ring[v] for v in R}
    cut = [e for e, (u, w) in enumerate(edges) if (ring[u] in Ri) != (ring[w] in Ri)]
    ins0, ins = T.in_sets(sizes, contacts), T.in_sets(sizes, contacts, cut)
    rc = T.ring_contacts(rot, edges, ring)
    allr = set(rc)
    inside = [e for e, (u, w) in enumerate(edges) if ring[u] in Ri and ring[w] in Ri]
    outside = [e for e, (u, w) in enumerate(edges) if ring[u] not in Ri and ring[w] not in Ri]
    sep = all(T.rings_needed(T.reach(ins, c)[0], rc, cut) <= Ri for c in inside) and \
        all(T.rings_needed(T.reach(ins, c)[0], rc, cut) <= allr - Ri for c in outside)
    pre = all(T.rings_needed(T.reach(ins0, c)[0], rc) & (allr - Ri) for c in inside) and \
        all(T.rings_needed(T.reach(ins0, c)[0], rc) & Ri for c in outside)
    return n, len(R), len(cut), sep, pre


def one_cycle(n):
    """one ring of cuts round the torus (the h contacts between columns n - 1 and 0): h(0, 0) still needs the ring (n - 1, 0) across it,
    through h(n - 2, 0), by exactly one walk of length 2(n - 2) and none shorter; and how many uncut contacts still need every ring"""
    sizes, contacts, rot, edges, ring, hidx, vidx = T.torus(n, 2)
    cut = [hidx[(n - 1, j)] for j in range(n)]
    ins = T.in_sets(sizes, contacts, cut)
    rc = T.ring_contacts(rot, edges, ring)
    union, first, rows, dim = T.reach(ins, hidx[(0, 0)])
    d = hidx[(n - 2, 0)]
    ok = bool(union >> d & 1) and first[d] == 2 * (n - 2) and ring[(n - 1, 0)] in T.rings_needed(union, rc, cut)
    uncut = [e for e in range(len(contacts)) if e not in cut]
    if n <= 7:
        still = sum(T.rings_needed(T.reach(ins, c)[0], rc, cut) == set(rc) for c in uncut)
    else:
        still = None
    return n, ok, still, len(uncut)


def two_cycles(n):
    sizes, contacts, rot, edges, ring, hidx, vidx = T.torus(n, 2)
    h = n // 2
    cut = [hidx[(n - 1, j)] for j in range(n)] + [hidx[(h - 1, j)] for j in range(n)]
    ins = T.in_sets(sizes, contacts, cut)
    rc = T.ring_contacts(rot, edges, ring)
    left = {ring[(i, j)] for i in range(h) for j in range(n)}
    allr = set(rc)
    ok = True
    for e, (u, w) in enumerate(edges):
        if e in cut:
            continue
        side = left if ring[u] in left else allr - left
        ok &= T.rings_needed(T.reach(ins, e)[0], rc, cut) <= side
    return n, ok


def rectangle(nm):
    """computed, not part of a theorem: on the n x m torus, the most rings any contact never needs"""
    n, m = nm
    dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))
    verts = [(i, j) for i in range(n) for j in range(m)]
    edges, eid = [], {}
    for v in verts:
        for d in dirs[:2]:
            w = ((v[0] + d[0]) % n, (v[1] + d[1]) % m)
            eid[(v, d)] = eid[(w, (-d[0], -d[1]))] = len(edges)
            edges.append((v, w))
    rot = {v: [eid[(v, d)] for d in dirs] for v in verts}
    sizes, contacts = T.LN.network(rot, edges, 2)
    ring = {v: i for i, v in enumerate(sorted(rot, key=repr))}
    ins = T.in_sets(sizes, contacts)
    rc = T.ring_contacts(rot, edges, ring)
    return n, m, max(len(rc) - len(T.rings_needed(T.reach(ins, c)[0], rc)) for c in range(len(contacts)))


def cells_cut(args):
    """the cut readings at cell level (rows of M^T with the cut contacts frozen, exact): a block on the 5 x 5 torus and one or two rings
    of cuts round it, every contact against every ring"""
    name, n, g, cutspec = args
    sizes, contacts, rot, edges, ring, hidx, vidx = T.torus(n, g)
    if cutspec == "block":
        R = {ring[(i, j)] for i in range(2) for j in range(2)}
        cut = [e for e, (u, w) in enumerate(edges) if (ring[u] in R) != (ring[w] in R)]
    elif cutspec == "one":
        cut = [hidx[(n - 1, j)] for j in range(n)]
    else:
        cut = [hidx[(n - 1, j)] for j in range(n)] + [hidx[(n // 2 - 1, j)] for j in range(n)]
    ins = T.in_sets(sizes, contacts, cut)
    rc = T.ring_contacts(rot, edges, ring)
    rows, Nb, blocks = N.matrix(sizes, (60,) * len(sizes), contacts, cut=tuple(cut))
    for c in range(len(contacts)):
        if c in cut:
            continue
        want = T.rings_needed(T.reach(ins, c)[0], rc, cut)
        seq, T1, p = N.orbit(rows, 1 << c, 10 ** 6)
        got = {r for r in rc if any(x & N.mask(blocks, r) for x in seq)}
        if got != want:
            return name, False, c
    return name, True, len(contacts) - len(cut)


def main():
    write = "--write" in sys.argv
    deps = {"LOOP-NET-20261108-001A manifest": "proofs/LOOP-NET-20261108-001A/LOOP-NET-20261108-001A-P001_symmetry_cancels_returns/manifest.json",
            "loopnet_lib": "proofs/LOOP-NET-20261108-001A/LOOP-NET-20261108-001A-P001_symmetry_cancels_returns/loopnet_lib.py"}
    m = json.loads((HERE / "manifest.json").read_text())
    bound = {k: sha(p) for k, p in deps.items()}
    check("0_dependencies_bound", all(m["parent_bindings"].get(p) == bound[k] for k, p in deps.items()), bound)
    with Pool(16) as pool:
        res = pool.map(algebra, range(3, 9))
        check("1_contact_graph_is_the_convolution", all(r[1] for r in res), {"sides": [r[0] for r in res]})
        res = pool.map(odd_points, range(3, 23, 2))
        check("2_odd_tori_powers_of_L", all(r[1] and r[2] for r in res), {"sides": [r[0] for r in res], "orders of 2": {r[0]: r[3] for r in res},
                                                                        "L^(2^r - 1) computed explicitly at": [r[0] for r in res if r[4]]})
        res = pool.map(contacts_need_all, range(3, 14, 2))
        check("3_odd_tori_every_contact_needs_every_ring", all(r[1] for r in res), {"sides and contacts checked": {r[0]: r[2] for r in res}})
        res = pool.map(even_points, range(4, 22, 2))
        check("4_even_tori_powers_of_L", all(r[1] for r in res) and all(r[2] in (None, True) for r in res),
              {"sides": [r[0] for r in res], "L^(n/2) = 0 at": [r[0] for r in res if r[2]]})
        res = pool.map(antipode_unneeded, range(4, 17, 2))
        check("5_even_tori_antipode_never_needed", all(r[1] for r in res),
              {"rings never needed by h(0) and by v(0)": {r[0]: (r[2], r[3]) for r in res}})
        jobs = [(3, 2, True), (3, 3, True), (4, 2, True), (4, 3, True), (5, 2, False), (5, 3, False), (6, 2, False), (7, 2, False), (8, 2, False)]
        res = pool.map(when, jobs, chunksize=1)
        check("6_when_cell_level_exact", all(r[2] for r in res), {"(side, spacing): contact-ring pairs": {"%d,%d" % (r[0], r[1]): r[3] for r in res}})
        blocks = []
        for n in range(3, 10):
            for k in range(2, n - 1):
                blocks.append((n, [(i, j) for i in range(k) for j in range(k)]))
            if n >= 5:
                blocks.append((n, [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)]))
                blocks.append((n, [(0, 0), (1, 1), (2, 2)]))
        res = pool.map(block_cut, blocks, chunksize=1)
        check("7_bounding_rings_of_cuts_separate", all(r[3] for r in res),
              {"cuts": len(res), "with every inside and outside contact reaching across before the cut": sum(r[4] for r in res),
               "pre-reach on every odd torus": all(r[4] for r in res if r[0] % 2 == 1)})
        res = pool.map(one_cycle, range(3, 13))
        check("8_one_ring_of_cuts_round_the_torus_does_not_separate", all(r[1] for r in res),
              {"sides": [r[0] for r in res], "uncut contacts still needing every ring": {r[0]: "%s of %d" % (r[2], r[3]) for r in res if r[2] is not None}})
        res = pool.map(two_cycles, range(4, 11))
        check("9_two_rings_of_cuts_round_the_torus_separate", all(r[1] for r in res), {"sides": [r[0] for r in res]})
        res = pool.map(cells_cut, [("block 2x2 on 5x5", 5, 2, "block"), ("one ring of cuts on 5x5", 5, 2, "one"), ("two rings of cuts on 6x6", 6, 2, "two"),
                                   ("block 2x2 on 4x4", 4, 2, "block")], chunksize=1)
        check("10_cuts_at_cell_level_exact", all(r[1] for r in res), {r[0]: r[2] for r in res})
        res = pool.map(rectangle, [(n, m) for n in range(3, 11) for m in range(n, 13)], chunksize=1)
        check("11_rectangular_tori_computed", all(r[2] == 0 for r in res if r[0] % 2 or r[1] % 2),
              {"tori with a ring some contact never needs": {"%d x %d" % (r[0], r[1]): r[2] for r in res if r[2]},
               "tori checked": len(res)})
    result = {"ticket": "LATTICE-NET-20261108-001A", "checks": OUT, "status": "passed", "seconds": round(time.time() - T0, 1)}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path)
    else:
        old = json.loads(path.read_text())
        same = {k: v["pass"] for k, v in old["checks"].items()} == {k: v["pass"] for k, v in OUT.items()}
        print("matches result.json" if same else "DIFFERS from result.json")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
