#!/usr/bin/env python3
"""Checks for LOOP-NET-20261108-001A: symmetry cancels returns; a shared ring with more contacts does not.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy and networkx (the repository's .venv). 16 worker processes, a few minutes."""
import hashlib
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import loopnet_lib as L  # noqa: E402

N = L.N
T0 = time.time()
OUT = {}
H = 300


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:400], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def random_network(rng, spaced=None):
    """a random connected ring multigraph (2 to 5 rings, every ring with at least two contacts), a random rotation, random spacing"""
    while True:
        R = rng.randint(2, 5)
        E = rng.randint(R, R + 3)
        edges = [tuple(rng.sample(range(R), 2)) for _ in range(E)]
        deg = [sum(v in e for e in edges) for v in range(R)]
        if min(deg) < 2:
            continue
        seen, todo = {0}, [0]
        while todo:
            v = todo.pop()
            for a, b in edges:
                for x, y in ((a, b), (b, a)):
                    if x == v and y not in seen:
                        seen.add(y)
                        todo.append(y)
        if len(seen) == R:
            break
    rot = {}
    for e, (u, v) in enumerate(edges):
        rot.setdefault(u, []).append(e)
        rot.setdefault(v, []).append(e)
    for v in rot:
        rng.shuffle(rot[v])
    if spaced:
        return L.network(rot, edges, spaced), rot, edges
    sizes, pos = [], {}
    for v in range(R):
        m = len(rot[v])
        gaps = [2] * m
        for _ in range(rng.randint(0, 6)):
            gaps[rng.randrange(m)] += 1
        p = 0
        for e, g in zip(rot[v], gaps):
            pos[(v, e)] = p
            p += g
        sizes.append(p)
    contacts = [(u, pos[(u, e)], v, pos[(v, e)], L.LAW) for e, (u, v) in enumerate(edges)]
    return (tuple(sizes), contacts), rot, edges


def criterion(seed):
    """Theorem 1: D_cc = 1 iff the chain-end witnesses never lapse; otherwise they lapse first at lag val(D_cc - 1) + 1"""
    rng = random.Random(seed)
    (sizes, contacts), rot, edges = random_network(rng)
    D = L.dmatrix(sizes, contacts)
    cells = L.read_cells(sizes, contacts, H)
    ones = 0
    for c in range(len(contacts)):
        lapse = cells[c][0]
        if D[c][c] == L.ONE:
            ones += 1
            if lapse is not None:
                return False, seed, c
        else:
            v = L.valuation(L.radd(D[c][c], L.ONE)) + 1
            if (lapse is None and v <= H) or (lapse is not None and lapse != v):
                return False, seed, c
    return True, len(contacts), ones


def uniform(seed):
    """Theorem 2 (a): in an equally spaced network D_cc = 1 iff every closed-walk count at c is even"""
    rng = random.Random(seed)
    g = rng.choice((2, 3))
    (sizes, contacts), rot, edges = random_network(rng, spaced=g)
    D = L.dmatrix(sizes, contacts)
    odd, _ = L.odd_returns(L.arc_matrix(sizes, contacts))
    ok = all((D[c][c] == L.ONE) == (c not in odd) for c in range(len(contacts)))
    return ok, sum(D[c][c] == L.ONE for c in range(len(contacts))), len(contacts)


def regular(args):
    """Theorem 3 on one regular network: flips at every contact, no odd return, every contact persistent with its witnesses to lag H"""
    name, rot, edges, g, exact = args
    sizes, contacts = L.network(rot, edges, g)
    flips = all(L.flip(rot, edges, e) is not None for e in range(len(edges)))
    odd, _ = L.odd_returns(L.arc_matrix(sizes, contacts))
    cells = L.read_cells(sizes, contacts, H)
    persistent = all(x == (None, None) for x in cells)
    dexact = None
    if exact:
        D = L.dmatrix(sizes, contacts)
        dexact = all(D[c][c] == L.ONE for c in range(len(contacts)))
    return name, g, len(contacts), flips, not odd, persistent, dexact


def obstruction(args):
    """Theorem 4 on one figure-eight or chord: at every contact joining a two-contact ring to a ring of three or more, with no
    two-contact face, exactly one closed walk of length 2 returns, and in the equally spaced network the witnesses lapse first at 2g + 1"""
    name, rot, edges, g = args
    sizes, contacts = L.network(rot, edges, g)
    A = L.arc_matrix(sizes, contacts)
    A2 = A.astype(np.int64) @ A.astype(np.int64)
    fs, genus = L.faces(sizes, contacts)
    deg = {v: len(l) for v, l in rot.items()}
    face_two = set()
    for f in fs:
        if len(f) == 2:
            face_two.update(x for R, x, y, l in f)
    cells = L.read_cells(sizes, contacts, H)
    meeting, ok = 0, True
    for e, (u, v) in enumerate(edges):
        if sorted((deg[u], deg[v]))[0] == 2 and max(deg[u], deg[v]) >= 3 and e not in face_two:
            meeting += 1
            ok &= int(A2[e, e]) == 1 and cells[e][0] == 2 * g + 1
    lost = any(x[1] is not None for x in cells)
    return name, g, genus, meeting, ok, lost


def wide(args):
    """computed, not part of a theorem: an equally spaced figure-eight or chord at one spacing. The first lag up to 600 at which some
    contact misses a ring; if there is none and the spacing is at most 9, the rows are followed exactly until they repeat (cap 10^5):
    'every lag', or the first later lag at which some contact misses a ring"""
    name, rot, edges, g = args
    sizes, contacts = L.network(rot, edges, g)
    cells = L.read_cells(sizes, contacts, 600)
    misses = [x[1] for x in cells if x[1] is not None]
    if misses:
        return name, g, min(misses), None
    if g > 9:
        return name, g, None, "persistent to lag 600, not followed"
    rows, Nb, blocks = N.matrix(sizes, (60,) * len(sizes), contacts)
    late = []
    for c, (ra, pa, rb, pb, law) in enumerate(contacts):
        o = N.orbit(rows, 1 << c, 10 ** 5)
        if o is None:
            return name, g, None, "undecided beyond 10^5"
        ma, mb = N.mask(blocks, ra), N.mask(blocks, rb)
        late += [T + 1 for T, x in enumerate(o[0]) if not ((x & ma) and (x & mb))][:1]
    return name, g, None, ("misses a ring first at lag %d" % min(late)) if late else "persistent at every lag"


def full_states(args):
    """the row reading against the full state space, on a small network: lags at which each contact needs each of its rings"""
    name, sizes, contacts, horizon = args
    rules = (60,) * len(sizes)
    for c, (ra, pa, rb, pb, law) in enumerate(contacts):
        for ring in (ra, rb):
            if N.needs(sizes, rules, contacts, c, ring, horizon) != N.needs_full(sizes, rules, contacts, c, ring, horizon):
                return name, False
    return name, True


def main():
    write = "--write" in sys.argv
    deps = {"LOOP-ANY-20261108-001A manifest": "proofs/LOOP-ANY-20261108-001A/LOOP-ANY-20261108-001A-P001_balance_cancels_the_feedback/manifest.json",
            "net_lib": "proofs/SEPARATE-20261108-001A/SEPARATE-20261108-001A-P001_a_cut_separates_a_cycle_needs_two/net_lib.py"}
    m = json.loads((HERE / "manifest.json").read_text())
    bound = {k: sha(p) for k, p in deps.items()}
    check("0_dependencies_bound", all(m["parent_bindings"].get(p) == bound[k] for k, p in deps.items()), bound)

    with Pool(16) as pool:
        res = pool.map(criterion, range(400))
        bad = [r for r in res if not r[0]]
        check("1_criterion_random_networks", not bad, {"networks": len(res), "contacts": sum(r[1] for r in res),
                                                       "contacts with D_cc = 1": sum(r[2] for r in res), "first failure": bad[:1]})

        fam = []
        for r in range(2, 9):
            fam.append(("loop of %d rings" % r, *L.dihedron(r)))
        for k in range(2, 7):
            fam.append(("two rings sharing %d contacts" % k, *L.hosohedron(k)))
        for nm in ("tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"):
            fam.append((nm, *L.platonic(nm)))
        for n in range(3, 7):
            fam.append(("square torus %d" % n, *L.square_torus(n)))
        for n in range(3, 6):
            fam.append(("triangular torus %d" % n, *L.triangular_torus(n)))
        for n in range(2, 6):
            fam.append(("honeycomb torus %d" % n, *L.honeycomb_torus(n)))
        # surfaces: every corner on one ring and one face; genus 0 for plane rotations, 1 for the tori
        surf = []
        for name, rot, edges in fam:
            sizes, contacts = L.network(rot, edges, 2)
            fs, genus = L.faces(sizes, contacts)
            arcs = L.corners(sizes, contacts)
            once = sorted((R, x) for f in fs for R, x, y, l in f) == sorted((ring, d) for d, e, ring, l in arcs)
            surf.append((name, genus, once))
        check("2_surfaces", all(s[2] for s in surf) and all((s[1] == 1) == ("torus" in s[0]) for s in surf),
              {"networks": len(surf), "genus": {s[0]: s[1] for s in surf}})

        res = pool.map(uniform, range(400))
        check("3_uniform_spaced_returns_even_iff_cancel", all(r[0] for r in res),
              {"networks": len(res), "contacts": sum(r[2] for r in res), "contacts with D_cc = 1": sum(r[1] for r in res)})

        # Theorem 2 (b) and its converse at equal ring sizes: two rings sharing three contacts and the tetrahedron, every planar placement
        sphere = sphere_census()
        check("4_sphere_equal_densities", sphere["agree"] == sphere["networks"] and sphere["balanced"] > 0, sphere)

        jobs = []
        for name, rot, edges in fam:
            for g in (2, 3, 4):
                jobs.append((name, rot, edges, g, len(edges) <= 18 and g <= 3))
        res = pool.map(regular, jobs, chunksize=1)
        bad = [r for r in res if not (r[3] and r[4] and r[5] and r[6] is not False)]
        check("5_regular_networks_persist", not bad, {"networks": len(res), "with exact D": sum(r[6] is not None for r in res),
                                                      "families": sorted({r[0] for r in res}), "failures": bad[:3]})

        jobs = []
        for r1 in range(2, 7):
            for r2 in range(max(r1, 3), 7):
                for order in ("separate", "interleaved"):
                    rot, edges = L.figure_eight(r1, r2, order)
                    for g in (2, 3, 4, 5):
                        jobs.append(("figure-eight %d,%d %s" % (r1, r2, order), rot, edges, g))
        for p in range(1, 5):
            for q in range(p, 5):
                for r in range(q, 5):
                    if (p, q, r) == (1, 1, 1):
                        continue
                    for planar in (True, False):
                        rot, edges = L.theta(p, q, r, planar)
                        for g in (2, 3, 4, 5):
                            jobs.append(("theta %d,%d,%d %s" % (p, q, r, "planar" if planar else "torus"), rot, edges, g))
        res = pool.map(obstruction, jobs, chunksize=4)
        check("6_obstruction_where_loops_meet", all(r[4] and r[3] > 0 for r in res),
              {"networks": len(res), "meeting contacts": sum(r[3] for r in res), "networks losing persistence by lag %d" % H: sum(r[5] for r in res)})
        lost = sum(r[5] for r in res)
        OUT["6_obstruction_where_loops_meet"]["info"]["all lose persistence"] = lost == len(res)

        rot, edges = L.figure_eight(2, 2)
        sizes, contacts = L.network(rot, edges, 2)
        A = L.arc_matrix(sizes, contacts)
        nil = not (np.linalg.matrix_power(A.astype(np.int64), len(contacts)) % 2).any()
        check("7_two_short_loops_degenerate", nil and not L.odd_returns(A)[0], {"arcs mod 2": int(A.sum()), "nilpotent": nil})

        nets = [("figure-eight 3,3 separate", *L.figure_eight(3, 3, "separate")), ("figure-eight 3,3 interleaved", *L.figure_eight(3, 3, "interleaved")),
                ("figure-eight 2,3 separate", *L.figure_eight(2, 3, "separate")), ("figure-eight 4,4 separate", *L.figure_eight(4, 4, "separate")),
                ("chord 1,1,2", *L.theta(1, 1, 2)), ("chord 1,2,2", *L.theta(1, 2, 2)), ("theta 2,2,2", *L.theta(2, 2, 2)), ("chord 1,1,3", *L.theta(1, 1, 3))]
        res = pool.map(wide, [(nm, rot, edges, g) for nm, rot, edges in nets for g in range(2, 17)], chunksize=1)
        lose = {g: all(r[2] is not None for r in res if r[1] == g) for g in range(2, 17)}
        check("9_wide_spacing_computed", all(lose[g] for g in (2, 3, 4, 8, 16)),
              {"spacings at which all eight miss a ring by lag 600": [g for g in lose if lose[g]],
               "outcomes": {"%s at %d" % (r[0], r[1]): ("misses a ring at lag %d" % r[2]) if r[2] is not None else r[3] for r in res}})

        small = []
        for name, (rot, edges) in (("two rings sharing three contacts", L.hosohedron(3)), ("tetrahedron", L.platonic("tetrahedron")),
                                   ("figure-eight 3,3", L.figure_eight(3, 3))):
            sizes, contacts = L.network(rot, edges, 2)
            small.append((name, sizes, contacts, 40))
        res = pool.map(full_states, small)
        check("8_full_state_spaces", all(r[1] for r in res), {r[0]: r[1] for r in res})

    result = {"ticket": "LOOP-NET-20261108-001A", "checks": OUT, "status": "passed", "seconds": round(time.time() - T0, 1)}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path)
    else:
        old = json.loads(path.read_text())
        same = {k: v["pass"] for k, v in old["checks"].items()} == {k: v["pass"] for k, v in OUT.items()}
        print("matches result.json" if same else "DIFFERS from result.json")
        sys.exit(0 if same else 1)


def sphere_census():
    """two rings of equal size sharing three contacts (sizes 6 to 12) and the tetrahedron of equal rings (sizes 6 to 8), every planar
    placement: D_cc = 1 at every contact iff every face has the same size"""
    import itertools
    out = {"networks": 0, "agree": 0, "balanced": 0}
    for (rot0, edges), srange in ((L.hosohedron(3), range(6, 13)), (L.platonic("tetrahedron"), range(6, 9))):
        verts = sorted(rot0)
        for s in srange:
            per = []
            for v in verts:
                m = len(rot0[v])
                comps = [c for c in itertools.product(range(2, s), repeat=m) if sum(c) == s]
                per.append([(v, gaps) for gaps in comps])
            for choice in itertools.product(*per):
                pos = {}
                for v, gaps in choice:
                    p = 0
                    for e, gg in zip(rot0[v], gaps):
                        pos[(v, e)] = p
                        p += gg
                sizes = tuple(s for _ in verts)
                contacts = [(verts.index(u), pos[(u, e)], verts.index(v), pos[(v, e)], L.LAW) for e, (u, v) in enumerate(edges)]
                fs, genus = L.faces(sizes, contacts)
                assert genus == 0
                equal = len({(len(f), sum(c[3] for c in f)) for f in fs}) == 1
                D = L.dmatrix(sizes, contacts)
                ones = all(D[c][c] == L.ONE for c in range(len(contacts)))
                out["networks"] += 1
                out["agree"] += ones == equal
                out["balanced"] += ones
    return out


if __name__ == "__main__":
    main()
