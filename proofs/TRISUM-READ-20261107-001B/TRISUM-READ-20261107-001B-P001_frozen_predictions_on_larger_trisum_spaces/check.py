#!/usr/bin/env python3
"""Checks for TRISUM-READ-20261107-001B: frozen predictions on larger trisum spaces.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 22 processes, and at most 6 for the full-memory enumerator."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import datetime  # noqa: E402
import gzip  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import map_lib as ML  # noqa: E402
TR = ML.TR
A = ML.A

FROZEN = "e15fce8fa9d18a219df2b6fa82eaff9ef96d4d0ff3adb7a9839335bfa0b94d29"   # ticket A's predictions.json, frozen before these maps
EXPECTED = {5: ["P1 loaded lines are a union of native diagonal classes"]}   # space seed -> the frozen statements that fail there,
                                                                              # as scored after all ten maps were computed
RL = TR.load("tr_refine_lib", ROOT / "proofs/REFINE-READ-20261107-001A/REFINE-READ-20261107-001A-P001_pair_refinement_determines_the_atoms"
             / "refine_lib.py")
TR.engine()
T0 = time.time()
OUT = {}
MAPS = json.load(gzip.open(HERE / "maps.json.gz", "rt"))
PROV = json.loads((HERE / "provenance.json").read_text())
WIT = json.loads((HERE / "witnesses.json").read_text())


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def table(d):
    return {str(L): (None if v is None else [int(x) for x in v]) for L, v in d.items()}


def sample_rows(seed, n):
    r = random.Random(seed)
    return sorted({0, *r.sample(range(1, n), 2)})


def lean_task(args):
    seed, M = args
    d = MAPS[str(seed)]
    out, ns = ML.exact_row([tuple(l) for l in d["lines"]], d["points"], M)
    stored = d["rows"][str(M)]
    return seed, M, ns == stored["solutions"] and table(out) == stored["row"]


def full_task(args):
    """the full-memory enumerator: TL.solutions equals lean_solutions as arrays, and tr_lib.exact_row equals the stored row"""
    seed, M = args
    d = MAPS[str(seed)]
    H = [tuple(l) for l in d["lines"]]
    a = TR.engine().TL.solutions(H, [(0, 0, 0)] * len(H), d["points"], skip=M)
    b = ML.lean_solutions(H, [(0, 0, 0)] * len(H), d["points"], skip=M)
    same_arrays = a.shape == b.shape and bool((a == b).all())
    del a, b
    out, ns = TR.exact_row(H, d["points"], M)
    stored = d["rows"][str(M)]
    return seed, M, same_arrays and ns == stored["solutions"] and table(out) == stored["row"]


def is_cut(G, E):
    """E (a set of edges of G) is a coboundary: some 2-colouring of G makes exactly the edges of E bichromatic"""
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


def symmetry_task(seed):
    """the witness permutation is an automorphism of the native map; it moves a loaded line to an unloaded one and fixes every atom
    line; a skeleton automorphism induces it on the skeleton lines and keeps the signing's switching class, not its places"""
    import networkx as nx
    from networkx.algorithms import isomorphism as iso
    d = MAPS[str(seed)]
    H = [tuple(l) for l in d["lines"]]
    n = len(H)
    ex = {int(a): {int(b): (None if v is None else tuple(bool(x) for x in v)) for b, v in r["row"].items()} for a, r in d["rows"].items()}
    w = {int(k): v for k, v in WIT[str(seed)]["permutation"].items()}
    pi = [w.get(a, a) for a in range(n)]
    st = TR.structure(H)
    auto = sorted(pi) == list(range(n)) and all(TR.free(ex[a].get(b)) == TR.free(ex[pi[a]].get(pi[b]))
                                              for a in range(n) for b in range(n) if a != b)
    moved = {a: pi[a] for a in range(n) if pi[a] != a}
    loaded_to_unloaded = any(a in st["loaded"] and pi[a] not in st["loaded"] for a in range(n))
    atoms_fixed = all(pi[a] == a for a in st["atom lines"])
    G = st["G"]
    for v in G:
        G.nodes[v]["k"] = v[0]
    S = {frozenset(A["edge"]) for A in st["atoms"]}
    induced = []
    for m in iso.GraphMatcher(G, G, node_match=lambda a, b: a["k"] == b["k"]).isomorphisms_iter():
        if all(m[("L", l)] == ("L", pi[l]) for l in st["skeleton"]):
            S2 = {frozenset((m[u], m[v])) for u, v in (tuple(e) for e in S)}
            induced.append((is_cut(G, S ^ S2), S2 == S))
    return seed, {"automorphism of the native map": auto, "moved lines": moved, "a loaded line goes to an unloaded one": loaded_to_unloaded,
                  "every atom line fixed": atoms_fixed, "inducing skeleton automorphisms": len(induced),
                  "each keeps the switching class": all(c for c, same in induced), "each moves the atoms' places": all(not same for c, same in induced)}


def census6_task(path_seed):
    """entries where census 6 creates but none of the three order-free far sides does"""
    path, seed = path_seed
    m = json.load(gzip.open(path, "rt"))[str(seed)]
    alone = sum(1 for r in m["rows"].values() for v in r["row"].values() if v is not None and v[1] and not (v[0] or v[2] or v[3]))
    entries = sum(1 for r in m["rows"].values() for v in r["row"].values() if v is not None)
    return seed, alone, entries


def report_task(seed):
    d = MAPS[str(seed)]
    H = [tuple(l) for l in d["lines"]]
    ex = {int(a): {int(b): (None if v is None else tuple(bool(x) for x in v)) for b, v in r["row"].items()} for a, r in d["rows"].items()}
    return seed, TR.report(H, ex, RL)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; ticket A Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})

    pr = (A / "predictions.json").read_bytes()
    fr = json.loads(pr)
    tests = fr["spaces"]["test"]
    frozen_at = datetime.datetime.fromisoformat(fr["frozen at"])
    complete = {str(r["seed"]): sorted(MAPS[str(r["seed"])]["rows"], key=int) == [str(M) for M in range(r["lines"])]
                and all(len(v["row"]) == r["lines"] - 1 for v in MAPS[str(r["seed"])]["rows"].values()) for r in tests}
    hashes = {str(r["seed"]): hashlib.sha256(json.dumps(MAPS[str(r["seed"])]["lines"]).encode()).hexdigest() == r["lines sha256"]
              for r in tests}
    after = {k: datetime.datetime.fromisoformat(v["finished"]) > frozen_at for k, v in PROV["maps"].items()}
    check("1 the freeze: ticket A's predictions.json is the frozen file and names tr_lib.py by hash; the stored maps are complete maps of "
          "exactly its ten test spaces (lines bound by hash), each recorded as finished after the freeze",
          hashlib.sha256(pr).hexdigest() == FROZEN
          and fr["library sha256 (tr_lib.py)"] == hashlib.sha256((A / "tr_lib.py").read_bytes()).hexdigest()
          and sorted(MAPS, key=int) == sorted((str(r["seed"]) for r in tests), key=int) and all(complete.values()) and all(hashes.values())
          and sorted(PROV["maps"], key=int) == sorted(MAPS, key=int) and all(after.values()),
          {"frozen at": fr["frozen at"], "maps": len(MAPS), "rows": sum(len(m["rows"]) for m in MAPS.values()),
           "finished": {k: v["finished"] for k, v in sorted(PROV["maps"].items(), key=lambda kv: int(kv[0]))},
           "engines": {k: v["engine"] for k, v in sorted(PROV["maps"].items(), key=lambda kv: int(kv[0]))}})

    jobs = [(r["seed"], M) for r in tests for M in sample_rows(r["seed"], r["lines"])]
    with Pool(22) as pool:
        lean = pool.map(lean_task, jobs, chunksize=1)
    with Pool(6) as pool:
        full = pool.map(full_task, jobs, chunksize=1)
    counts = {str(s): sorted({v["solutions"] for v in MAPS[str(s)]["rows"].values()}) for s in sorted(map(int, MAPS))}
    check("2 the engines agree: three rows of every test space (row 0 and two seeded at random) recomputed by the lean enumerator and by "
          "CHAIN-TRANSFER A's enumerator through tr_lib equal the stored rows, and the two enumerators return the same solution arrays",
          all(x[2] for x in lean) and all(x[2] for x in full) and len(lean) == len(full) == 30,
          {"rows": len(jobs), "lean equal": sum(x[2] for x in lean), "full equal": sum(x[2] for x in full),
           "solutions per row, by space": counts})

    with Pool(10) as pool:
        reps = dict(pool.map(report_task, [r["seed"] for r in tests]))
    preds = [k for k in next(iter(reps.values())) if k.startswith("P")]
    fails = {str(s): [k for k in preds if r[k] is not True] for s, r in reps.items()}
    check("3 the frozen statements on the ten test spaces: the outcomes are as reported (" +
          ("every one of P1 to P7 holds in every space" if not EXPECTED else "failures listed in EXPECTED") + ")",
          {s: f for s, f in fails.items() if f} == {str(k): v for k, v in EXPECTED.items()},
          {"by space": {str(s): {k: v for k, v in r.items() if not k.startswith("P")} for s, r in sorted(reps.items())},
           "failing": {s: f for s, f in fails.items() if f}})

    with Pool(len(WIT)) as pool:
        sym = dict(pool.map(symmetry_task, sorted(map(int, WIT))))
    check("4 the failure is a symmetry: in every space where a frozen statement fails, a stored permutation of the lines preserves the "
          "order-free vector of every ordered pair, exchanges a loaded line with an unloaded one and fixes every atom line; the skeleton "
          "automorphisms inducing it all keep the switching class of the signing (the incidences that carry atoms) and move its places",
          sorted(map(int, WIT)) == sorted(EXPECTED) and all(v["automorphism of the native map"] and v["a loaded line goes to an unloaded one"]
                                                           and v["every atom line fixed"] and v["inducing skeleton automorphisms"] > 0
                                                           and v["each keeps the switching class"] and v["each moves the atoms' places"]
                                                           for v in sym.values()),
          {str(k): v for k, v in sym.items()})

    a_maps = A / "maps.json.gz"
    jobs = [(str(a_maps), int(k)) for k in json.load(gzip.open(a_maps, "rt"))] + [(str(HERE / "maps.json.gz"), int(k)) for k in MAPS]
    with Pool(17) as pool:
        c6 = pool.map(census6_task, jobs)
    check("5 yes/no creation is native: on all 17 maps (ticket A's seven and these ten) census 6 never creates where none of K4^(3), the "
          "Fano plane and census 58 does, so whether creation occurs equals creation by the three order-free far sides",
          len(c6) == 17 and all(alone == 0 for s_, alone, e in c6),
          {"maps": len(c6), "non-degenerate entries": sum(e for s_, a_, e in c6), "census 6 alone": sum(a_ for s_, a_, e in c6)})

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
