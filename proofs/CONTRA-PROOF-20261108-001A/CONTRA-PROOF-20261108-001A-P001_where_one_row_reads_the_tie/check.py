#!/usr/bin/env python3
"""Checks for CONTRA-PROOF-20261108-001A: where one row of creation reads the removed line's tie, on random cubic glues.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 16 processes."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import hashlib  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import networkx as nx  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/CONTRA-READ-20261108-001A/CONTRA-READ-20261108-001A-P001_every_row_singles_out_the_contradictory_class"))
import contra_lib as CL  # noqa: E402

TL = CL.TR.engine().TL
# the random glues: (lines and points, random seed, candidates drawn, glues kept), as the long-running run CONTRA-PROOF-R1 drew them
DRAWS = [(8, 2, 3000, 10), (9, 4, 1500, 6), (10, 5, 800, 3)]
STORED = json.loads((HERE / "glues.json").read_text())
GLUES = [CL.Glue(k, {"glue": [tuple(l) for l in g["lines"]], "minimal": []}) for k, g in enumerate(STORED)]
TRISUM = [3, 6, 1, 192, 240, 246, 300]
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:3000], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def random_glue(n, rnd):
    """a connected cubic glue: n points and n lines, each point on three lines, each line on three distinct points"""
    while True:
        stubs = [p for p in range(n) for _ in range(3)]
        rnd.shuffle(stubs)
        lines = [tuple(sorted(stubs[3 * i:3 * i + 3])) for i in range(n)]
        if any(len(set(l)) < 3 for l in lines):
            continue
        G = nx.Graph()
        for i, l in enumerate(lines):
            for p in l:
                G.add_edge(("L", i), ("P", p))
        if nx.is_connected(G):
            return lines


def unsat_of(lines):
    G = CL.Glue(0, {"glue": lines, "minimal": []})
    return [m for m in range(G.N) if len(G.solutions(m)) == 0]


def row_task(job):
    k, a, m = job
    return GLUES[k].row(a, m)


def cut_lines(G):
    """the lines lying in a two-vertex cut of the incidence graph, each with its partner line"""
    out = {}
    for a in range(G.g):
        H = G.G.copy()
        H.remove_node(("L", a))
        arts = [v for v in nx.articulation_points(H) if v[0] == "L"]
        if arts:
            out[a] = arts[0][1]
    return out


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})

    drawn, kept = [], []
    with Pool(16) as pool:
        for n, seed, tries, how in DRAWS:
            rnd = random.Random(seed)
            cands = [random_glue(n, rnd) for _ in range(tries)]
            us = pool.map(unsat_of, cands, chunksize=8)
            with_unsat = [(l, u) for l, u in zip(cands, us) if u]
            drawn.append({"lines": n, "drawn": tries, "with a class without solutions": len(with_unsat)})
            kept += [l for l, u in with_unsat[:how]]
    conn = [nx.node_connectivity(G.G) for G in GLUES]
    one_unsat = [len(unsat_of(list(G.lines))) for G in GLUES]
    check("1 the random glues: drawn again as the run CONTRA-PROOF-R1 drew them (connected cubic glues of 8, 9 and 10 lines, the first 10, "
          "6 and 3 with a class without solutions), they are the stored 19; each has exactly one class without solutions; 8 have an "
          "incidence graph of connectivity 2, 11 of connectivity 3",
          [list(map(list, l)) for l in kept] == [g["lines"] for g in STORED] and all(u == 1 for u in one_unsat)
          and sorted(conn) == [2] * 8 + [3] * 11,
          {"draws": drawn, "connectivity": conn})

    jobs, keys = [], []
    for k, G in enumerate(GLUES):
        for a in range(G.g):
            reps = {}
            for m in range(G.N):
                reps.setdefault(G.restr(a, m), m)
            for r, m in reps.items():
                jobs.append((k, a, m))
                keys.append((k, a))
    with Pool(16) as pool:
        res = pool.map(row_task, jobs, chunksize=16)
    rows = {}
    for (k, a), (row, tied) in zip(keys, res):
        rows.setdefault((k, a), []).append((row, tied))
    fails, alldeg, cuts = {}, True, {}
    for k, G in enumerate(GLUES):
        cuts[k] = cut_lines(G)
        f = []
        for a in range(G.g):
            tied = [row for row, t in rows[(k, a)] if t]
            bad_rows = [row for row, t in rows[(k, a)] if not t and row in tied]
            if bad_rows:
                f.append(a)
                alldeg &= all(all(x is None or not any(x) for x in row) for row in bad_rows + tied)
        fails[k] = f
    exact = all(sorted(fails[k]) == sorted(cuts[k]) for k in range(len(GLUES)))
    check("2 where one row reads the tie: for every glue and line a, one row of creation fails to tell the classes of the glue without a "
          "that tie a's points from those that do not exactly when a lies in a two-vertex cut of the incidence graph (16 lines, on the 8 "
          "glues of connectivity 2), and at those lines nothing creates anywhere in the tied class's row or the rows colliding with it: every "
          "gluing is degenerate or adds no new knot",
          exact and alldeg and sum(len(v) for v in fails.values()) == 16 and all(not fails[k] for k in range(len(GLUES)) if conn[k] == 3),
          {"failing lines per glue": fails, "lines in a two-vertex cut, with the partner line": cuts, "rows computed": len(jobs)})

    sides = []
    for k, G in enumerate(GLUES):
        for a, a2 in cuts[k].items():
            if a < a2:
                H = G.G.copy()
                H.remove_nodes_from([("L", a), ("L", a2)])
                pair = []
                for comp in nx.connected_components(H):
                    ls = [G.lines[v[1]] for v in comp if v[0] == "L"]
                    pts = {v[1] for v in comp if v[0] == "P"}
                    small = len(pts) == 4 and len(ls) == 3 and len(set.intersection(*map(set, ls))) == 1
                    pair.append((len(pts), len(ls), small))
                sides.append(pair)
    check("3 the cuts: each two-vertex cut through a failing line is a pair of lines; each of its two sides has one more point than "
          "lines (counting incidences: the cut lines meet each side in three points together), and one side is always K4^(3) without a "
          "line, three lines on four points through one common point",
          len(sides) == 8 and all(p == l + 1 for pair in sides for p, l, sm in pair) and all(any(sm for p, l, sm in pair) for pair in sides),
          {"sides of each cut (points, lines, K4^(3) without a line)": sides})

    c1 = True
    for k, G in enumerate(GLUES):
        for a in range(G.g):
            once = [i for i, b in enumerate(b for b in range(G.g) if b != a) if len(set(G.lines[a]) & set(G.lines[b])) == 1]
            for row, t in rows[(k, a)]:
                if t:
                    c1 &= all(row[i] is None or not row[i][0] for i in once)
    runs = CL.PL.SW.generate(TRISUM, 0)
    trisum_c1 = {}
    for s in TRISUM:
        G = CL.Glue(s, runs[s])
        pf = G.mask_of(G.minimal)
        loud, tied_all = [], True
        for a in range(G.g):
            row, t = G.row(a, pf)
            once = [i for i, b in enumerate(b for b in range(G.g) if b != a) if len(set(G.lines[a]) & set(G.lines[b])) == 1]
            tied_all &= t
            if any(row[i] is not None and row[i][0] for i in once):
                loud.append(a)
        trisum_c1[str(s)] = {"removed lines where K4^(3) creates at a line meeting them once": loud, "connectivity": nx.node_connectivity(G.G),
                             "tied at every line": tied_all}
    check("4 K4^(3) under the tie is not a general lemma: in the row of every tied class, on the 19 random glues and on six of the seven "
          "trisum glues, the K4^(3) far side creates at no line meeting the removed line in exactly one point; on the 12-line trisum glue "
          "of seed 1 it does, for 8 of its 12 removed lines. All seven trisum glues have incidence graphs of connectivity 3",
          c1 and all(v["tied at every line"] and v["connectivity"] == 3 for v in trisum_c1.values())
          and [s for s, v in trisum_c1.items() if v["removed lines where K4^(3) creates at a line meeting them once"]] == ["1"]
          and len(trisum_c1["1"]["removed lines where K4^(3) creates at a line meeting them once"]) == 8,
          {"trisum glues": trisum_c1})

    c2 = {}
    for k, G in enumerate(GLUES):
        miss = 0
        for a in range(G.g):
            once = [i for i, b in enumerate(b for b in range(G.g) if b != a) if len(set(G.lines[a]) & set(G.lines[b])) == 1]
            tied_null = {tuple(x is None for x in row) for row, t in rows[(k, a)] if t}
            for row, t in rows[(k, a)]:
                if not t and not any(row[i] is not None and row[i][0] for i in once) and tuple(x is None for x in row) in tied_null:
                    miss += 1
        c2[k] = miss
    check("5 that silence plus the degenerate entries is not how a row reads the tie in general: on a glue of connectivity 3 where every "
          "row reads it, some classes without the tie are told apart from the tied one only by other entries",
          any(c2[k] > 0 and conn[k] == 3 and not fails[k] for k in c2), {"classes told apart only by other entries, per glue": c2})

    PY = [tuple(p) for p in TL.PY]
    comp = {k: PY.index(tuple(1 - v for v in p)) for k, p in enumerate(PY)}
    reps3 = sorted({min(k, comp[k]) for k in range(6)})
    singles = []
    for choice in itertools.product([(0,), (1,), (0, 1)], repeat=3):
        m = 0
        for k, xs in zip(reps3, choice):
            for x in xs:
                m |= 1 << (2 * k + x)
                m |= 1 << (2 * comp[k] + (1 - x))
        tied_to_y = any(all(choice[i] == (PY[k][j] ^ c,) for i, k in enumerate(reps3)) for j in range(3) for c in (0, 1))
        singles.append((choice, m, tied_to_y))
    ev = TL.evaluate(1, [m for c, m, t in singles])
    no_k4 = all(not (ev[m][0] and ev[m][1][0]) for c, m, t in singles)
    degenerate_iff_tied = all((not ev[m][0]) == t for c, m, t in singles)
    check("6 the local lemma: over all 27 complement-closed relations on a gluing line's three literals and one further near point, no "
          "single point makes K4^(3) create, and a relation is degenerate exactly when the point is tied to a point of the gluing line, so "
          "points tied to the removed line's points are never witnesses at a line through one of them",
          len(singles) == 27 and no_k4 and degenerate_iff_tied,
          {"relations": 27, "degenerate": sum(1 for c, m, t in singles if not ev[m][0]),
           "creating, per far side (K4^(3), census 6, Fano, census 58)": [sum(1 for c, m, t in singles if ev[m][0] and ev[m][1][i]) for i in range(4)]})

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
