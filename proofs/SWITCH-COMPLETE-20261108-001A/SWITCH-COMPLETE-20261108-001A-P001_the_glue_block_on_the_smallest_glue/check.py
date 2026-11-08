#!/usr/bin/env python3
"""Checks for SWITCH-COMPLETE-20261108-001A: the glue block on the smallest trisum glue.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 8 processes."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import collections  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import networkx as nx  # noqa: E402
from networkx.algorithms import isomorphism as iso  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/SWITCH-PROOF-20261108-001A/SWITCH-PROOF-20261108-001A-P001_creation_between_glue_lines_sees_only_the_switching_class"))
import proof_lib as PL  # noqa: E402

TR = PL.TR
TL = TR.engine().TL
FA = PL.SW.FAM.FA
SEED = 3
RUN = PL.SW.generate([SEED], 0)[SEED]
GLUE = [tuple(l) for l in RUN["glue"]]
g = len(GLUE)
n = 1 + max(max(l) for l in GLUE)
G = PL.SW.incidence_of_glue(GLUE)
TREE = nx.minimum_spanning_tree(G)
_key = lambda e: tuple(sorted(e, key=str))  # noqa: E731
OFF = sorted({_key(e) for e in G.edges()} - {_key(e) for e in TREE.edges()}, key=str)
IDX = {frozenset(e): k for k, e in enumerate(OFF)}
FUND = []
for _u, _w in OFF:
    _p = nx.shortest_path(TREE, _u, _w)
    FUND.append({frozenset(e) for e in zip(_p, _p[1:])} | {frozenset((_u, _w))})
N = 1 << len(OFF)
# the two classes that collide across orbits, as signings (incidences (line, point)); found by this computation, checked below
X = [(4, 4), (5, 4), (6, 6), (6, 7), (7, 3)]
Y = [(4, 5), (5, 4), (6, 6), (6, 7), (7, 3)]
T0 = time.time()
OUT = {}
MEMO = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def free(v):
    return None if v is None else (bool(v[0]), bool(v[2]), bool(v[3]))


def signing(mask):
    """the class representative: a sign on each off-tree incidence in the mask"""
    return [([v for v in e if v[0] == "L"][0][1], [v for v in e if v[0] == "P"][0][1]) for k, e in enumerate(OFF) if mask >> k & 1]


def incs(S):
    return {frozenset((("L", i), ("P", p))) for i, p in S}


def mask_of(S):
    """a signing's class: its parity on each fundamental cycle"""
    E = incs(S)
    return sum((len(E & C) & 1) << k for k, C in enumerate(FUND))


def cyc_vec(cyc):
    v = 0
    for u, w in zip(cyc, cyc[1:] + cyc[:1]):
        k = IDX.get(frozenset((u, w)))
        if k is not None:
            v ^= 1 << k
    return v


BASIS = []
for _a in range(g):
    _Ga = G.copy()
    _Ga.remove_node(("L", _a))
    BASIS.append([cyc_vec(c) for c in nx.cycle_basis(_Ga)])


def restr(a, m):
    """the class of the signing on the glue without line a: its parities on a cycle basis of that glue"""
    return tuple(bin(m & v).count("1") & 1 for v in BASIS[a])


def verdict(mm):
    if mm is None:
        return None
    k = (frozenset(mm[0]), frozenset(mm[1]))
    if k not in MEMO:
        MEMO[k] = free(TL.verdict_from_masks(*mm))
    return MEMO[k]


def signed_row(S, a):
    """row a of the signed glue's creation map: remove line a, glue at every other line b"""
    signs = PL.signs_of(GLUE, S)
    AN = TL.solutions(GLUE, signs, n, skip=a)
    return [verdict(TR.fast_masks(AN, list(GLUE[b]), signs[b], [q for q in range(n) if q not in GLUE[b]])) if len(AN) else None
            for b in range(g) if b != a]


def row_task(job):
    a, S = job
    return signed_row(S, a)


def count_task(m):
    return len(TL.solutions(GLUE, PL.signs_of(GLUE, signing(m)), n))


def plain_task(job):
    """row a of the plain edge-atom space of a signing, restricted to glue lines, with its own engine"""
    S, a = job
    H = FA.edge_atoms(GLUE, S)
    nn = 1 + max(max(l) for l in H)
    AN = TL.solutions(H, [(0, 0, 0)] * len(H), nn, skip=a)
    return [verdict(TR.fast_masks(AN, list(H[b]), (0, 0, 0), [q for q in range(nn) if q not in H[b]])) for b in range(g) if b != a]


def plain_count(S):
    H = FA.edge_atoms(GLUE, S)
    nn = 1 + max(max(l) for l in H)
    return len(H), len(TL.solutions(H, [(0, 0, 0)] * len(H), nn))


def permuted(block, p):
    """the block of s(S) read off the block of S, for a symmetry s acting on lines as p: entry (p a, p b) = entry (a, b)"""
    B, k = {}, 0
    for a in range(g):
        for b in range(g):
            if b != a:
                B[(p[a], p[b])] = block[k]
                k += 1
    return [B[(a, b)] for a in range(g) for b in range(g) if b != a]


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})

    degrees = {d for _, d in G.degree()}
    reps_ok = all(mask_of(signing(m)) == m for m in range(N))
    check("1 the glue: TRISUM-READ's seed 3 from HANDLE-COUNT A's generator has 8 lines and 8 points, its incidence graph is connected "
          "and cubic with cycle rank 9, so its signings fall into 512 switching classes; a class is read off as its parities on the "
          "fundamental cycles of a spanning tree, and the representative with signs only off the tree has the given parities",
          g == 8 and n == 8 and degrees == {3} and nx.is_connected(G) and len(OFF) == 9 and reps_ok,
          {"glue": GLUE, "off-tree incidences": [[e[0][1], e[1][1]] for e in OFF], "classes": N})

    reps = [{} for a in range(g)]
    for m in range(N):
        for a in range(g):
            reps[a].setdefault(restr(a, m), m)
    jobs = [(a, signing(m)) for a in range(g) for m in sorted(reps[a].values())]
    rnd = random.Random(2026110801)
    verts = [("L", i) for i in range(g)] + [("P", p) for p in range(n)]
    direct = []
    for m in rnd.sample(range(N), 16):
        U = {v for v in verts if rnd.random() < 0.5}
        sw = PL.switched(GLUE, signing(m), U)
        for a in range(g):
            direct.append((m, a, "representative", signing(m)))
            direct.append((m, a, "switched", sw))
    with Pool(8) as pool:
        rows = pool.map(row_task, jobs, chunksize=4)
        drows = pool.map(row_task, [(a, S) for m, a, kind, S in direct], chunksize=4)
        counts = pool.map(count_task, range(N), chunksize=32)
    R = {(a, restr(a, mask_of(S))): r for (a, S), r in zip(jobs, rows)}
    agree = sum(R[(a, restr(a, m))] == r for (m, a, kind, S), r in zip(direct, drows))
    dims = [len(BASIS[a]) for a in range(g)]
    blocks = {m: [x for a in range(g) for x in R[(a, restr(a, m))]] for m in range(N)}
    row_values = [len({json.dumps(R[(a, r)]) for r in reps[a]}) for a in range(g)]
    check("2 the blocks: by SWITCH-PROOF's theorem on the glue without line a, row a depends only on the signing's class there, so each "
          "row is computed once per such class (the glue without a line has cycle rank 7, 128 classes); recomputed directly from the "
          "representative and from a randomly switched signing of 16 random classes, all 256 rows agree",
          agree == len(direct) and set(dims) == {7} and all(len(reps[a]) == 128 for a in range(g))
          and row_values == [55, 57, 55, 57, 55, 55, 55, 55],
          {"rows computed": len(jobs), "rows recomputed directly": len(direct), "agreeing": agree,
           "distinct values of each row (of 128 classes)": row_values})

    auts = list(iso.GraphMatcher(G, G).isomorphisms_iter())
    keep = [s for s in auts if s[("L", 0)][0] == "L"]
    swap = [s for s in auts if s[("L", 0)][0] == "P"]
    lp = lambda s: tuple(s[("L", i)][1] for i in range(g))  # noqa: E731
    act = lambda s, m: mask_of([(s[("L", i)][1], s[("P", p)][1]) for i, p in signing(m)])  # noqa: E731
    equi = all(json.dumps(permuted(blocks[m], lp(s))) == json.dumps(blocks[act(s, m)]) for s in keep for m in range(N))
    orbit = {}
    for m in range(N):
        if m not in orbit:
            o = {act(s, m) for s in keep}
            for x in o:
                orbit[x] = min(o)
    orbits = collections.Counter(orbit.values())
    check("3 the glue's symmetries: its incidence graph has 48 automorphisms, 24 keeping lines and points and acting faithfully on the "
          "lines, 24 exchanging them; the blocks are equivariant under the first 24, which have 42 orbits on the classes",
          len(auts) == 48 and len(keep) == 24 and len({lp(s) for s in keep}) == 24 and len(swap) == 24 and equi and len(orbits) == 42,
          {"automorphisms": len(auts), "keeping lines": len(keep), "exchanging lines and points": len(swap), "orbits": len(orbits),
           "orbit sizes": sorted(collections.Counter(orbits.values()).items())})

    groups = collections.defaultdict(list)
    for m in range(N):
        groups[json.dumps(blocks[m])].append(m)
    sizes = sorted(collections.Counter(len(v) for v in groups.values()).items())
    across = [sorted(v) for v in groups.values() if len({orbit[m] for m in v}) > 1]
    up_to = len({min(json.dumps(permuted(blocks[m], lp(s))) for s in keep) for m in range(N)})
    mx, my = mask_of(X), mask_of(Y)
    ox = sorted(m for m in range(N) if orbit[m] == orbit[mx])
    oy = sorted(m for m in range(N) if orbit[m] == orbit[my])
    dual = lambda s, m: mask_of([(s[("P", p)][1], s[("L", i)][1]) for i, p in signing(m)])  # noqa: E731
    no_dual = not any(orbit[dual(s, mx)] == orbit[my] for s in swap)
    check("4 the collisions: 448 distinct blocks on the 512 classes; every collision lies inside one orbit except one, which is the "
          "union of the two orbits of the signings X = {(4,4),(5,4),(6,6),(6,7),(7,3)} and Y = {(4,5),(5,4),(6,6),(6,7),(7,3)}, six "
          "classes each, whose signed glues have 40 and 34 solutions; so the blocks take 41 values on the 42 orbits; no automorphism "
          "of the incidence graph, those exchanging lines and points included, takes one orbit to the other",
          len(groups) == 448 and sizes == [(1, 395), (2, 51), (3, 1), (12, 1)] and len(across) == 1 and sorted(across[0]) == sorted(ox + oy) and len(ox) == len(oy) == 6
          and counts[mx] == 40 and counts[my] == 34 and up_to == 41 and no_dual and blocks[mx] == blocks[my],
          {"distinct blocks": len(groups), "group sizes": sizes, "groups across orbits": across, "blocks up to symmetry": up_to,
           "solutions": {"X": counts[mx], "Y": counts[my]}, "entries of the shared block": sorted(collections.Counter(
               json.dumps(x) for x in blocks[mx]).items())})

    with Pool(8) as pool:
        px = pool.map(plain_task, [(X, a) for a in range(g)] + [(Y, a) for a in range(g)], chunksize=1)
        pc = pool.map(plain_count, [X, Y])
    bx = [x for r in px[:g] for x in r]
    by = [x for r in px[g:] for x in r]
    check("5 on the plain spaces themselves: the edge-atom spaces of X and Y (43 points each), with their own engine, have identical "
          "blocks of glue lines, equal to the signed glue's; their solution counts are 5^5 x 40 and 5^5 x 34",
          bx == by == blocks[mx] and pc == [(43, 5 ** 5 * 40), (43, 5 ** 5 * 34)], {"lines and solutions": pc})

    pf = mask_of([tuple(x) for x in RUN["minimal"]])
    zero = [m for m in range(N) if counts[m] == 0]
    check("6 the Pfaffian class: the generator's signing lies in the only class whose signed glue has no solution, and no other class "
          "has its block",
          zero == [pf] and len(groups[json.dumps(blocks[pf])]) == 1,
          {"Pfaffian signing": RUN["minimal"], "classes without solutions": len(zero),
           "its block": sorted(collections.Counter(json.dumps(x) for x in blocks[pf]).items())})

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
              "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
