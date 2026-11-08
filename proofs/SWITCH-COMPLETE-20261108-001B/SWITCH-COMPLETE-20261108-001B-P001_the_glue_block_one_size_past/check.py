#!/usr/bin/env python3
"""Checks for SWITCH-COMPLETE-20261108-001B: the glue block one size past, on the 10-line trisum glue.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 8 processes."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import collections  # noqa: E402
import hashlib  # noqa: E402
import itertools  # noqa: E402
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
RUNS = PL.SW.generate([3, 6, 36], 0)
SEED = 6
GLUE = [tuple(l) for l in RUNS[SEED]["glue"]]
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
# ticket A's pair on the smallest glue, for the census-6 check
GLUE3 = [tuple(l) for l in RUNS[3]["glue"]]
X3 = [(4, 4), (5, 4), (6, 6), (6, 7), (7, 3)]
Y3 = [(4, 5), (5, 4), (6, 6), (6, 7), (7, 3)]
T0 = time.time()
OUT = {}
MEMO = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:3000], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def free(v):
    return None if v is None else (bool(v[0]), bool(v[2]), bool(v[3]))


def signing(mask):
    """the class representative: a sign on each off-tree incidence in the mask"""
    return [([v for v in e if v[0] == "L"][0][1], [v for v in e if v[0] == "P"][0][1]) for k, e in enumerate(OFF) if mask >> k & 1]


def mask_of(S):
    """a signing's class: its parity on each fundamental cycle"""
    E = {frozenset((("L", i), ("P", p))) for i, p in S}
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


def verdict(mm, full=False):
    if mm is None:
        return None
    k = (frozenset(mm[0]), frozenset(mm[1]))
    if k not in MEMO:
        MEMO[k] = tuple(bool(x) for x in TL.verdict_from_masks(*mm))
    return MEMO[k] if full else free(MEMO[k])


def signed_row(glue, S, a):
    """row a of a signed glue's creation map: remove line a, glue at every other line b"""
    nn = 1 + max(max(l) for l in glue)
    signs = PL.signs_of(glue, S)
    AN = TL.solutions(glue, signs, nn, skip=a)
    return [verdict(TR.fast_masks(AN, list(glue[b]), signs[b], [q for q in range(nn) if q not in glue[b]])) if len(AN) else None
            for b in range(len(glue)) if b != a]


def row_task(job):
    a, S = job
    return signed_row(GLUE, S, a)


def count_task(m):
    return len(TL.solutions(GLUE, PL.signs_of(GLUE, signing(m)), n))


def plain_task(job):
    """row a of the plain edge-atom space of a signing, restricted to glue lines, with its own engine"""
    S, a = job
    H = FA.edge_atoms(GLUE, S)
    nn = 1 + max(max(l) for l in H)
    AN = TL.solutions(H, [(0, 0, 0)] * len(H), nn, skip=a)
    return [verdict(TR.fast_masks(AN, list(H[b]), (0, 0, 0), [q for q in range(nn) if q not in H[b]])) for b in range(g) if b != a]


def census6_task(job):
    """row a of a signed glue with all four far sides, census 6 included, under each of the six orders of each gluing line's points:
    for each b the sorted list of the six four-verdict vectors"""
    glue, S, a = job
    nn = 1 + max(max(l) for l in glue)
    signs = PL.signs_of(glue, S)
    AN = TL.solutions(glue, signs, nn, skip=a)
    out = []
    for b in range(len(glue)):
        if b != a:
            vs = []
            for perm in itertools.permutations(range(3)):
                Y = [glue[b][i] for i in perm]
                vs.append(json.dumps(verdict(TR.fast_masks(AN, Y, tuple(signs[b][i] for i in perm), [q for q in range(nn) if q not in Y]),
                                             full=True) if len(AN) else None))
            out.append(sorted(vs))
    return out


def permuted(block, p):
    """the block of s(S) read off the block of S, for a symmetry s acting on lines as p: entry (p a, p b) = entry (a, b)"""
    B, k = {}, 0
    for a in range(g):
        for b in range(g):
            if b != a:
                B[(p[a], p[b])] = block[k]
                k += 1
    return [B[(a, b)] for a in range(g) for b in range(g) if b != a]


def incidence_typed(glue):
    H = PL.SW.incidence_of_glue(glue)
    for v in H:
        H.nodes[v]["k"] = v[0]
    return H


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})

    degrees = {d for _, d in G.degree()}
    same36 = iso.GraphMatcher(incidence_typed(GLUE), incidence_typed([tuple(l) for l in RUNS[36]["glue"]]),
                              node_match=lambda x, y: x["k"] == y["k"]).is_isomorphic()
    sizes_all = {s: len(RUNS[s]["glue"]) for s in RUNS}
    check("1 the glue one size past: TRISUM-READ's two 10-line glues, seeds 6 and 36, are isomorphic, so there is one; it has 10 lines "
          "and 10 points, and its incidence graph is connected and cubic with cycle rank 11, so its signings fall into 2,048 switching "
          "classes, read off as parities on fundamental cycles",
          g == 10 and n == 10 and degrees == {3} and nx.is_connected(G) and len(OFF) == 11 and same36
          and all(mask_of(signing(m)) == m for m in range(N)),
          {"glue": GLUE, "lines": sizes_all, "seed 36 isomorphic": same36, "classes": N})

    reps = [{} for a in range(g)]
    for m in range(N):
        for a in range(g):
            reps[a].setdefault(restr(a, m), m)
    jobs = [(a, signing(m)) for a in range(g) for m in sorted(reps[a].values())]
    rnd = random.Random(2026110802)
    verts = [("L", i) for i in range(g)] + [("P", p) for p in range(n)]
    direct = []
    for m in rnd.sample(range(N), 16):
        U = {v for v in verts if rnd.random() < 0.5}
        sw = PL.switched(GLUE, signing(m), U)
        for a in range(g):
            direct.append((m, a, signing(m)))
            direct.append((m, a, sw))
    with Pool(8) as pool:
        rows = pool.map(row_task, jobs, chunksize=8)
        drows = pool.map(row_task, [(a, S) for m, a, S in direct], chunksize=4)
        counts = pool.map(count_task, range(N), chunksize=64)
    R = {(a, restr(a, mask_of(S))): r for (a, S), r in zip(jobs, rows)}
    agree = sum(R[(a, restr(a, m))] == r for (m, a, S), r in zip(direct, drows))
    blocks = {m: [x for a in range(g) for x in R[(a, restr(a, m))]] for m in range(N)}
    row_values = [len({json.dumps(R[(a, r)]) for r in reps[a]}) for a in range(g)]
    check("2 the blocks, row by row as in ticket A (the glue without a line has cycle rank 9, 512 classes); recomputed directly from the "
          "representative and from a randomly switched signing of 16 random classes, all 320 rows agree",
          agree == len(direct) and all(len(BASIS[a]) == 9 and len(reps[a]) == 512 for a in range(g)),
          {"rows computed": len(jobs), "rows recomputed directly": len(direct), "agreeing": agree,
           "distinct values of each row (of 512 classes)": row_values})

    keep = list(iso.GraphMatcher(incidence_typed(GLUE), incidence_typed(GLUE), node_match=lambda x, y: x["k"] == y["k"]).isomorphisms_iter())
    lp = lambda s: tuple(s[("L", i)][1] for i in range(g))  # noqa: E731
    act = lambda s, m: mask_of([(s[("L", i)][1], s[("P", p)][1]) for i, p in signing(m)])  # noqa: E731
    equi = all(json.dumps(permuted(blocks[m], lp(s))) == json.dumps(blocks[act(s, m)]) for s in keep for m in range(N))
    orbit = {}
    for m in range(N):
        if m not in orbit:
            o = {act(s, m) for s in keep}
            for x in o:
                orbit[x] = min(o)
    norb = len(set(orbit.values()))
    check("3 the glue's symmetries: 4 automorphisms keep lines and points, acting faithfully on the lines; the blocks are equivariant "
          "under them, and they have 576 orbits on the classes",
          len(keep) == 4 and len({lp(s) for s in keep}) == 4 and equi and norb == 576,
          {"automorphisms keeping lines and points": len(keep), "orbits": norb})

    groups = collections.defaultdict(list)
    for m in range(N):
        groups[json.dumps(blocks[m])].append(m)
    sizes = sorted(collections.Counter(len(v) for v in groups.values()).items())
    coll = [sorted(v) for v in groups.values() if len(v) > 1]
    across = [v for v in coll if len({orbit[m] for m in v}) > 1]
    up_to = len({min(json.dumps(permuted(blocks[m], lp(s))) for s in keep) for m in range(N)})
    empty = [m for m in range(N) if all(x is not None and not any(x) for x in blocks[m])]
    big = max(groups.values(), key=len)
    mixed = sum(1 for v in coll if len({counts[m] for m in v}) > 1)
    check("4 the collisions: 1,526 distinct blocks on the 2,048 classes, and 429 on the 576 orbits up to symmetry; 92 of the 98 groups "
          "of classes sharing a block span several orbits, and 76 mix solution counts; the largest, 190 classes, is exactly the classes "
          "where nothing creates at any entry, from 66 orbits, with 60 to 110 solutions",
          len(groups) == 1526 and up_to == 429 and len(coll) == 98 and len(across) == 92 and sorted(big) == sorted(empty)
          and len(empty) == 190 and mixed == 76 and len({orbit[m] for m in empty}) == 66
          and [min(counts[m] for m in empty), max(counts[m] for m in empty)] == [60, 110],
          {"distinct blocks": len(groups), "blocks up to symmetry": up_to, "group sizes": sizes, "groups across orbits": len(across),
           "groups mixing solution counts": mixed, "classes where nothing creates": len(empty),
           "their orbits": len({orbit[m] for m in empty}), "their solution counts (min, max)": [min(counts[m] for m in empty),
                                                                                                max(counts[m] for m in empty)]})

    pair = min((v for v in across if len(v) == 2), key=lambda v: v)
    P1, P2 = signing(pair[0]), signing(pair[1])
    with Pool(8) as pool:
        px = pool.map(plain_task, [(P1, a) for a in range(g)] + [(P2, a) for a in range(g)], chunksize=1)
    b1 = [x for r in px[:g] for x in r]
    b2 = [x for r in px[g:] for x in r]
    check("5 a cross-orbit pair on its plain spaces: the first pair of classes from two orbits sharing a block has signed glues with "
          "different solution counts, and its two plain edge-atom spaces, with their own engine, have identical blocks of glue lines, "
          "equal to the signed glue's",
          b1 == b2 == blocks[pair[0]] and counts[pair[0]] != counts[pair[1]],
          {"signings": [P1, P2], "solutions": [counts[pair[0]], counts[pair[1]]]})

    jobs6 = [(GLUE3, S, a) for S in (X3, Y3) for a in range(len(GLUE3))] + [(GLUE, S, a) for S in (P1, P2) for a in range(g)]
    with Pool(8) as pool:
        c6 = pool.map(census6_task, jobs6, chunksize=1)
    k3 = len(GLUE3)
    same3 = c6[:k3] == c6[k3:2 * k3]
    same6 = c6[2 * k3:2 * k3 + g] == c6[2 * k3 + g:]
    check("6 census 6 does not separate them: with all four far sides, census 6 under each of the six orders of each gluing line's "
          "points, ticket A's pair on the smallest glue and the pair of check 5 still have identical creation between glue lines",
          same3 and same6, {"smallest glue pair identical": same3, "10-line pair identical": same6})

    pf = mask_of([tuple(x) for x in RUNS[SEED]["minimal"]])
    zero = [m for m in range(N) if counts[m] == 0]
    check("7 the Pfaffian class: the generator's signing lies in the only class whose signed glue has no solution, and no other class "
          "has its block",
          zero == [pf] and len(groups[json.dumps(blocks[pf])]) == 1,
          {"Pfaffian signing": RUNS[SEED]["minimal"], "classes without solutions": len(zero),
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
