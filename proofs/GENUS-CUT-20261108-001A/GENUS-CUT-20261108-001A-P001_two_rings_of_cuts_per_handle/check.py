#!/usr/bin/env python3
"""Checks for GENUS-CUT-20261108-001A: two rings of cuts per handle keep one piece.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy and networkx (the repository's .venv). 16 worker processes, under a minute. Every reading is exact: walk counts and rows of M^T
are followed until the next row lies in the span of the earlier ones (rows of M^T until they repeat for the witnesses); no lag cutoff is
used."""
import hashlib
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import genus_lib as Gl  # noqa: E402

LN, T, N = Gl.LN, Gl.T, Gl.N
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:500], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def networks():
    maps = Gl.gl23_maps()
    out = [("square torus %d" % n, *LN.square_torus(n)) for n in (3, 4, 5, 6, 7, 8)]
    out += [("genus-2 network of 16 rings, three contacts each", *maps[(3, 8)]), ("genus-2 network of 6 rings, eight contacts each", *maps[(8, 3)]),
            ("genus-6 network of 6 rings", *maps[(8, 6)]), ("genus-6 network of 8 rings", *maps[(6, 8)])]
    out += [("double cover of the %d x %d torus, slit %d" % (n, n, k), *Gl.double_torus(n, k)) for n, k in ((3, 1), (4, 2), (5, 2), (6, 1))]
    return out


def pieces_random(args):
    """Theorem 1: after random cuts the pieces read from needs are the pieces of the ring graph without the cut contacts"""
    name, rot, edges, seed = args
    rng = random.Random(seed)
    sizes, contacts = LN.network(rot, edges, 2)
    bad, tried = 0, 0
    for _ in range(12):
        p = rng.choice((0.1, 0.25, 0.4, 0.6))
        cut = [e for e in range(len(edges)) if rng.random() < p]
        tried += 1
        bad += Gl.native_pieces(sizes, contacts, rot, edges, cut)[0] != Gl.graph_pieces(rot, edges, cut)
    return name, tried, bad


def one_piece_iff_injective(args):
    """Theorem 2: for random families of rings of cuts (sums of fundamental dual cycles), one piece exactly when the family's dual cycle
    space injects into homology; tree-cotree systems give 2g rings of cuts and one piece; adding any further ring of cuts separates"""
    name, rot, edges, seed = args
    rng = random.Random(seed)
    sizes, contacts = LN.network(rot, edges, 2)
    fs, g, du = Gl.dual(sizes, contacts)
    bnd = Gl.boundaries(rot, edges)
    ok, top, checked = True, 0, 0
    for _ in range(6):
        Tset, Tstar, X, cyc = Gl.tree_cotree(rot, edges, du, len(fs), rng)
        ok &= len(X) == 2 * g
        C = sorted({e for v in cyc for e in range(len(edges)) if v >> e & 1})
        zc, img = Gl.homology_rank(len(fs), du, C, bnd)
        one = Gl.native_pieces(sizes, contacts, rot, edges, C)[0] == 1
        ok &= one and zc == img == 2 * g
        top = max(top, zc)
        # one more ring of cuts: another tree-cotree system's cycle, or the ring of cuts round one ring
        Tset2, Tstar2, X2, cyc2 = Gl.tree_cotree(rot, edges, du, len(fs), rng)
        for extra in cyc2[:2] + [bnd[rng.randrange(len(bnd))]]:
            C2 = sorted(set(C) | {e for e in range(len(edges)) if extra >> e & 1})
            zc2, img2 = Gl.homology_rank(len(fs), du, C2, bnd)
            pieces = Gl.native_pieces(sizes, contacts, rot, edges, C2)[0]
            checked += 1
            ok &= (pieces == 1) == (zc2 == img2) and pieces == Gl.graph_pieces(rot, edges, C2)
            ok &= zc2 <= 2 * g or pieces > 1
    # random cut sets: one piece iff injective
    for _ in range(10):
        p = rng.choice((0.2, 0.4, 0.6))
        cut = [e for e in range(len(edges)) if rng.random() < p]
        zc, img = Gl.homology_rank(len(fs), du, cut, bnd)
        pieces = Gl.native_pieces(sizes, contacts, rot, edges, cut)[0]
        checked += 1
        ok &= (pieces == 1) == (zc == img) and img <= 2 * g
    return name, g, ok, top, checked


def torus_both_ways(n):
    """cut a meridian and a longitude of the n x n torus: one piece; with a second meridian, two pieces; and (computed) how many uncut
    contacts still need every ring"""
    sizes, contacts, rot, edges, ring, hidx, vidx = T.torus(n, 2)
    cut = [hidx[(n - 1, j)] for j in range(n)] + [vidx[(i, n - 1)] for i in range(n)]
    p1, full, unc = Gl.native_pieces(sizes, contacts, rot, edges, cut)
    cut2 = cut + [hidx[(n // 2 - 1, j)] for j in range(n)]
    p2 = Gl.native_pieces(sizes, contacts, rot, edges, cut2)[0]
    return n, p1, p2, full, unc


def genus2_persistence():
    """the genus-2 networks from GL(2,3): a flip at every contact, every return count even (so every contact persists at every lag at
    every size by LOOP-NET-20261108-001A, Theorem 3), and every contact needs every ring"""
    out = {}
    for key, name in (((3, 8), "16 rings, three contacts each"), ((8, 3), "6 rings, eight contacts each")):
        rot, edges = Gl.gl23_maps()[key]
        sizes, contacts = LN.network(rot, edges, 2)
        fs, g, du = Gl.dual(sizes, contacts)
        flips = all(LN.flip(rot, edges, e) is not None for e in range(len(edges)))
        odd, _ = LN.odd_returns(LN.arc_matrix(sizes, contacts))
        p, full, unc = Gl.native_pieces(sizes, contacts, rot, edges, [])
        rings, Nb, blocks = N.layout(sizes, contacts)
        rows = N.matrix(sizes, (60,) * len(sizes), contacts)[0]
        witnesses = True
        for c0, (ra, pa, rb, pb, law) in enumerate(contacts):
            seq, T1, p = N.orbit(rows, 1 << c0, 10 ** 6)
            wa, wb = rings[ra][pa - 1], rings[rb][pb - 1]
            witnesses &= all(x >> wa & 1 and x >> wb & 1 for x in seq)
        out[name] = {"genus": g, "faces": len(fs), "flips at every contact": flips, "contacts with an odd return count": len(odd),
                     "contacts needing every ring": "%d of %d" % (full, unc), "witnesses hold at every lag (exact)": witnesses}
    return out


def cells_exact(args):
    """the walk-count reading of needs against the rows of M^T (exact, by their span), with cuts"""
    name, rot, edges, cutspec = args
    sizes, contacts = LN.network(rot, edges, 2)
    ring = Gl.ring_index(rot)
    if cutspec == "both ways":
        n = int(round((len(rot)) ** 0.5))
        _, _, _, _, _, hidx, vidx = T.torus(n, 2)
        cut = [hidx[(n - 1, j)] for j in range(n)] + [vidx[(i, n - 1)] for i in range(n)]
    else:
        fs, g, du = Gl.dual(sizes, contacts)
        Tset, Tstar, X, cyc = Gl.tree_cotree(rot, edges, du, len(fs), random.Random(5))
        cut = sorted({e for v in cyc for e in range(len(edges)) if v >> e & 1})
    ins = T.in_sets(sizes, contacts, cut)
    rc = T.ring_contacts(rot, edges, ring)
    rows, Nb, blocks = N.matrix(sizes, (60,) * len(sizes), contacts, cut=tuple(cut))
    for c in range(len(contacts)):
        if c in cut:
            continue
        want = T.rings_needed(T.reach(ins, c)[0], rc, cut)
        union = cell_union(rows, 1 << c)
        got = {r for r in rc if union & N.mask(blocks, r)}
        if got != want:
            return name, False
    return name, True


def cell_union(rows, start):
    """every cell a contact's value ever depends on: the rows of M^T at lags 1, 2, ... until the next lies in the span of the earlier
    ones, after which every row is a sum of these (exact, no lag cutoff)"""
    row, union, basis = start, 0, {}
    while True:
        nxt, y = 0, row
        while y:
            low = y & -y
            nxt ^= rows[low.bit_length() - 1]
            y ^= low
        row, x = nxt, nxt
        while x:
            top = x.bit_length() - 1
            if top not in basis:
                break
            x ^= basis[top]
        if not x:
            return union
        basis[x.bit_length() - 1] = x
        union |= row


def main():
    write = "--write" in sys.argv
    deps = {"LATTICE-NET-20261108-001A manifest": "proofs/LATTICE-NET-20261108-001A/LATTICE-NET-20261108-001A-P001_odd_tori_compose_rings_of_cuts_separate/manifest.json",
            "lattice_lib": "proofs/LATTICE-NET-20261108-001A/LATTICE-NET-20261108-001A-P001_odd_tori_compose_rings_of_cuts_separate/lattice_lib.py"}
    m = json.loads((HERE / "manifest.json").read_text())
    bound = {k: sha(p) for k, p in deps.items()}
    check("0_dependencies_bound", all(m["parent_bindings"].get(p) == bound[k] for k, p in deps.items()), bound)
    nets = networks()
    genera = {}
    for name, rot, edges in nets:
        sizes, contacts = LN.network(rot, edges, 2)
        genera[name] = Gl.dual(sizes, contacts)[1]
    check("1_networks_and_their_surfaces", genera["genus-2 network of 16 rings, three contacts each"] == 2 and all(
        genera[n] == 2 for n in genera if n.startswith("double cover")) and all(genera[n] == 1 for n in genera if n.startswith("square")), genera)
    with Pool(16) as pool:
        res = pool.map(pieces_random, [(n, r, e, s) for n, r, e in nets for s in range(3)], chunksize=1)
        check("2_native_pieces_are_the_cut_surface_pieces", all(r[2] == 0 for r in res), {"cut sets": sum(r[1] for r in res), "mismatches": sum(r[2] for r in res)})
        res = pool.map(one_piece_iff_injective, [(n, r, e, s) for n, r, e in nets for s in range(2)], chunksize=1)
        check("3_two_rings_of_cuts_per_handle", all(r[2] for r in res),
              {"most rings of cuts keeping one piece, by genus": sorted({(r[1], r[3]) for r in res}), "families checked": sum(r[4] for r in res)})
        res = pool.map(torus_both_ways, range(3, 18))
        check("4_torus_cut_both_ways", all(r[1] == 1 and r[2] == 2 for r in res),
              {"uncut contacts still needing every ring (computed)": {r[0]: "%d of %d" % (r[3], r[4]) for r in res}})
        OUT["4_torus_cut_both_ways"]["info"]["sides where some uncut contact misses a ring"] = [r[0] for r in res if r[3] < r[4]]
        res = pool.map(cells_exact, [("5 x 5 torus cut both ways", *LN.square_torus(5), "both ways"), ("8 x 8 torus cut both ways", *LN.square_torus(8), "both ways"),
                                     ("16-ring genus-2 network, tree-cotree cuts", *Gl.gl23_maps()[(3, 8)], "tree-cotree"),
                                     ("double cover of the 4 x 4 torus, tree-cotree cuts", *Gl.double_torus(4, 2), "tree-cotree")], chunksize=1)
        check("6_cells_exact", all(r[1] for r in res), {r[0]: r[1] for r in res})
    g2 = genus2_persistence()
    check("5_genus_2_networks_persist", all(v["flips at every contact"] and v["contacts with an odd return count"] == 0 and v["witnesses hold at every lag (exact)"]
                                            for v in g2.values()), g2)
    result = {"ticket": "GENUS-CUT-20261108-001A", "checks": OUT, "status": "passed", "seconds": round(time.time() - T0, 1)}
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
