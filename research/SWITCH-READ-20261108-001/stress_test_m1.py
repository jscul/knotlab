#!/usr/bin/env python3
"""SWITCH-READ-M1, folded in: ticket A's comparison one size past its five pairs.

The nine other alternative placements that HANDLE-COUNT A's generator gives TRISUM-READ's glues (seeds 11, 34, 46, 96, 282 and 288;
56 to 60 points) were mapped exactly in the background (run `sw-maps1`, docs/LONG_RUNNING.md) with TRISUM-READ C's fixed-order
enumerator, as stress_test_m1_map.py does; the maps are stress_test_m1_maps.json.gz. Checks:
  1. each new map's space is the generator's space for its seed and hash seed;
  2. the last row of each new map (removing a line of an atom), recomputed;
  3. the glue block of every new map equals the signed glue's creation map (SWITCH-PROOF's corollary, one size past its 22 placements);
  4. every pair of placements of one glue, 17 pairs on 11 glues: the glue block entry by entry, the whole maps up to isomorphism (the
     glue's lines fixed, or any bijection), and where they differ;
  5. TRISUM-READ's frozen statements P1 to P7 on all 14 alternative placements;
  6. each failing statement explained by a stored symmetry of the native map, as TRISUM-READ B's check 4 explains seed 5's.

    python3 -B research/SWITCH-READ-20261108-001/stress_test_m1.py          compare a fresh run with stress_test_m1.json
    python3 -B research/SWITCH-READ-20261108-001/stress_test_m1.py --write  write stress_test_m1.json
Run from the repository root with its .venv (numpy, networkx). Uses up to 9 processes."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import gzip  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SWA = ROOT / "proofs/SWITCH-READ-20261108-001A/SWITCH-READ-20261108-001A-P001_placements_in_one_switching_class"
SPA = ROOT / "proofs/SWITCH-PROOF-20261108-001A/SWITCH-PROOF-20261108-001A-P001_creation_between_glue_lines_sees_only_the_switching_class"
TRC = ROOT / "proofs/TRISUM-READ-20261107-001C/TRISUM-READ-20261107-001C-P001_one_size_past_four_junctions"
for _p in (SWA, SPA, TRC):
    sys.path.insert(0, str(_p))
import sw_lib as SW  # noqa: E402
import proof_lib as PL  # noqa: E402
import order_lib as OL  # noqa: E402

TR = SW.FAM.TR
TR.engine()
RL = TR.load("m1_refine_lib", ROOT / "proofs/REFINE-READ-20261107-001A/REFINE-READ-20261107-001A-P001_pair_refinement_determines_the_atoms"
             / "refine_lib.py")
PLACE = json.loads((SWA / "placements.json").read_text())
STORED = {**json.load(gzip.open(SW.TRA / "maps.json.gz", "rt")), **json.load(gzip.open(SW.TRB / "maps.json.gz", "rt"))}
ALT = json.load(gzip.open(SWA / "maps.json.gz", "rt"))
NEW = json.load(gzip.open(HERE / "stress_test_m1_maps.json.gz", "rt"))
# found by a search of the native map's automorphisms that take loaded line 8 to unloaded line 9 (VF2 on the coloured complete digraph,
# pair-refinement classes as vertex colours); verified below
WITNESSES = {"11/3": {"1": 3, "3": 1, "8": 9, "9": 8, "10": 11, "11": 10}}
GLUE = {}
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def the_map(seed, hs):
    key = "%d/%d" % (seed, hs)
    return STORED[str(seed)] if hs == PLACE[str(seed)]["stored hash seed"] else ALT.get(key) or NEW[key]


def exact(m):
    return {int(a): {int(b): (None if v is None else tuple(bool(x) for x in v)) for b, v in r["row"].items()} for a, r in m["rows"].items()}


def row_task(key):
    """the last row of a new map (a line of an atom removed), recomputed with the enumerator and point order that made it"""
    m = NEW[key]
    H = [tuple(l) for l in m["lines"]]
    N = 1 + max(max(l) for l in H)
    W, S0, order = OL.fixed_order(H, N)
    M = len(H) - 1
    out, ns = OL.exact_row(H, N, M, order)
    fresh = {str(L): (None if v is None else [int(x) for x in v]) for L, v in out.items()}
    return key, M, fresh == m["rows"][str(M)]["row"] and ns == m["rows"][str(M)]["solutions"]


def glue_block_task(key):
    """the glue block of a new map against the signed glue's creation map, entry by entry"""
    seed = int(key.split("/")[0])
    m = NEW[key]
    glue = GLUE[seed]
    S, ok = PL.signing_of_space([tuple(l) for l in m["lines"]], glue)
    signs = PL.signs_of(glue, S)
    diff = total = 0
    for a in range(len(glue)):
        for b, v in PL.signed_row(glue, signs, a).items():
            total += 1
            diff += SW.free(v) != SW.free(m["rows"][str(a)]["row"][str(b)])
    return key, ok, total, diff


def pair_task(job):
    seed, a, b = job
    g = PLACE[str(seed)]["glue lines"]
    na, ta = SW.table(the_map(seed, a))
    nb, tb = SW.table(the_map(seed, b))
    return "%d: %d vs %d" % (seed, a, b), {
        "lines": na, "glue block differences": len(SW.glue_block_differences(ta, tb, g)),
        "isomorphic with the glue fixed": SW.isomorphic_maps(na, ta, tb, g, True) is not None,
        "isomorphic under some bijection": SW.isomorphic_maps(na, ta, tb, g, False) is not None, **SW.where_they_differ(na, ta, tb, g)}


def statements_task(key):
    seed, hs = map(int, key.split("/"))
    m = the_map(seed, hs)
    r = TR.report([tuple(l) for l in m["lines"]], exact(m), RL)
    return key, [k for k, v in r.items() if k.startswith("P") and v is not True]


def is_cut(G, E):
    col = {}
    for s0 in G:
        if s0 in col:
            continue
        col[s0] = 0
        stack = [s0]
        while stack:
            u = stack.pop()
            for w in G[u]:
                c = col[u] ^ (frozenset((u, w)) in E)
                if w not in col:
                    col[w] = c
                    stack.append(w)
                elif col[w] != c:
                    return False
    return True


def symmetry_task(key):
    """the witness is an automorphism of the native map; it moves a loaded line to an unloaded one and fixes every atom line; each
    automorphism of the skeleton inducing it keeps the signing's switching class and moves its places"""
    from networkx.algorithms import isomorphism as iso
    seed, hs = map(int, key.split("/"))
    m = the_map(seed, hs)
    H = [tuple(l) for l in m["lines"]]
    n = len(H)
    ex = exact(m)
    w = {int(k): v for k, v in WITNESSES[key].items()}
    pi = [w.get(a, a) for a in range(n)]
    st = TR.structure(H)
    auto = sorted(pi) == list(range(n)) and all(TR.free(ex[a].get(b)) == TR.free(ex[pi[a]].get(pi[b]))
                                              for a in range(n) for b in range(n) if a != b)
    G = st["G"]
    for v in G:
        G.nodes[v]["k"] = v[0]
    S = {frozenset(A["edge"]) for A in st["atoms"]}
    induced = []
    for mm in iso.GraphMatcher(G, G, node_match=lambda x, y: x["k"] == y["k"]).isomorphisms_iter():
        if all(mm[("L", l)] == ("L", pi[l]) for l in st["skeleton"]):
            S2 = {frozenset((mm[u], mm[v])) for u, v in (tuple(e) for e in S)}
            induced.append((is_cut(G, S ^ S2), S2 == S))
    return key, {"automorphism of the native map": auto, "moved lines": {a: pi[a] for a in range(n) if pi[a] != a},
                 "a loaded line goes to an unloaded one": any(a in st["loaded"] and pi[a] not in st["loaded"] for a in range(n)),
                 "every atom line fixed": all(pi[a] == a for a in st["atom lines"]), "inducing skeleton automorphisms": len(induced),
                 "each keeps the switching class": all(c for c, same in induced),
                 "each moves the atoms' places": all(not same for c, same in induced)}


if __name__ == "__main__":
    seeds = sorted(int(s) for s in PLACE)
    new_hs = sorted({int(k.split("/")[1]) for k in NEW})
    with Pool(len(new_hs) + 1) as pool:
        runs = dict(zip([0] + new_hs, pool.starmap(SW.generate, [(seeds, h) for h in [0] + new_hs])))
    same = {k: [tuple(l) for l in runs[int(k.split("/")[1])][int(k.split("/")[0])]["lines"]] == [tuple(l) for l in v["lines"]]
            for k, v in NEW.items()}
    expected = sorted("%d/%d" % (s, h) for s in seeds for h in PLACE[str(s)]["placements"]
                      if h != PLACE[str(s)]["stored hash seed"] and h not in PLACE[str(s)]["mapped"])
    check("1 the nine new maps are the placements ticket A lists and has not mapped, and each map's space is the generator's space for "
          "its seed and hash seed, line for line",
          sorted(NEW) == expected and all(same.values()), {"new placements": sorted(NEW), "points": {k: v["points"] for k, v in NEW.items()}})
    GLUE.update({s: [tuple(l) for l in runs[0][s]["glue"]] for s in seeds})

    with Pool(9) as pool:
        rows = pool.map(row_task, sorted(NEW), chunksize=1)
    check("2 the last row of each new map (removing a line of an atom), recomputed with the enumerator and point order that made it",
          all(ok for k, M, ok in rows), {k: M for k, M, ok in rows})

    with Pool(9) as pool:
        red = pool.map(glue_block_task, sorted(NEW), chunksize=1)
    check("3 SWITCH-PROOF's corollary on the nine new placements: the block of glue lines of each native map equals the signed glue's "
          "creation map, entry by entry",
          all(ok and d == 0 for k, ok, t, d in red), {"placements": len(red), "entries": sum(t for k, ok, t, d in red),
                                                      "differing": sum(d for k, ok, t, d in red)})

    jobs = [(s, a, b) for s in seeds for a, b in itertools.combinations(PLACE[str(s)]["placements"], 2)]
    with Pool(9) as pool:
        pairs = dict(pool.map(pair_task, jobs, chunksize=1))
    summary = {"pairs": len(pairs), "glues": len({j[0] for j in jobs}),
               "glue block identical": sum(v["glue block differences"] == 0 for v in pairs.values()),
               "whole maps isomorphic with the glue fixed": sum(v["isomorphic with the glue fixed"] for v in pairs.values()),
               "whole maps isomorphic under some bijection": sum(v["isomorphic under some bijection"] for v in pairs.values()),
               "a glue line's column from atom removals changes": sum(bool(v["glue lines whose column from atom removals changes"])
                                                                      for v in pairs.values()),
               "a glue line's row to atom lines changes": sum(bool(v["glue lines whose row to atom lines changes"]) for v in pairs.values())}
    check("4 every pair of placements of one glue: the glue block is identical, the whole maps are not isomorphic (the glue's lines "
          "fixed, or under any bijection), and the difference comes only from atom removals",
          summary["glue block identical"] == len(pairs) and summary["whole maps isomorphic under some bijection"] == 0
          and summary["a glue line's row to atom lines changes"] == 0 and summary["a glue line's column from atom removals changes"] == len(pairs),
          {"summary": summary, "pairs": pairs})

    alts = sorted("%d/%d" % (s, h) for s in seeds for h in PLACE[str(s)]["placements"] if h != PLACE[str(s)]["stored hash seed"])
    with Pool(9) as pool:
        stmts = dict(pool.map(statements_task, alts, chunksize=1))
    failing = {k: v for k, v in stmts.items() if v}
    check("5 TRISUM-READ's frozen statements P1 to P7 on all 14 alternative placements: they hold except where listed",
          len(stmts) == 14 and sorted(failing) == sorted(WITNESSES), {"placements": len(stmts), "failing": failing})

    sym = dict(symmetry_task(k) for k in sorted(WITNESSES))
    check("6 each failure is a symmetry: a stored permutation of the lines preserves the native map, moves a loaded line to an unloaded "
          "one and fixes every atom line, and the skeleton automorphisms inducing it all keep the switching class and move its places",
          all(v["automorphism of the native map"] and v["a loaded line goes to an unloaded one"] and v["every atom line fixed"]
              and v["inducing skeleton automorphisms"] > 0 and v["each keeps the switching class"] and v["each moves the atoms' places"]
              for v in sym.values()), sym)

    print("ALL OK", round(time.time() - T0, 1), "s")
    text = json.dumps({"stress test": "SWITCH-READ-M1", "epic": "SWITCH-READ-20261108-001", "status": "passed", "checks": OUT},
                      indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "stress_test_m1.json").write_text(text)
    elif not (HERE / "stress_test_m1.json").exists() or json.loads((HERE / "stress_test_m1.json").read_text()) != json.loads(text):
        print("stress_test_m1.json does not match a fresh run; rerun with --write after review")
