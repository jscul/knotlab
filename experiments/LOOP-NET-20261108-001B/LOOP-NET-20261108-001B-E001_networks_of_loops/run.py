"""LOOP-NET-20261108-001B-E001: a census of networks of loops (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the census; writes artifacts/LOOP-NET-20261108-001B/LOOP-NET-20261108-001B-E001_networks_of_loops/
                                          run/result.json and networks.json
    .venv/bin/python3 -B run.py --pilot   times a sample and prints no verdicts
Part 1: plane ring graphs of 2 to 7 rings (networkx's atlas: simple, connected, every ring with at least two contacts, planar), each with
networkx's plane rotation and equally spaced contacts: whether every count of returns to every contact is even, and whether every
contact has an edge-reversing symmetry (LOOP-NET-20261108-001A's flip). Part 2: figure-eights and chords of rule-60 rings all of the
same size s = 5 to 9, law (12, 12), every cyclic order of the contacts on rings with three or more and every spacing: whether some pair
of corners from one contact to the next has equal length (degenerate), whether D_cc = 1 at every contact (exact), and the first lag up to
300 at which some contact misses one of its rings. Library: LOOP-NET-20261108-001A's loopnet_lib."""
from __future__ import annotations

import itertools
import json
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/LOOP-NET-20261108-001A/LOOP-NET-20261108-001A-P001_symmetry_cancels_returns"))
import loopnet_lib as L  # noqa: E402

OUT = ROOT / "artifacts" / "LOOP-NET-20261108-001B" / "LOOP-NET-20261108-001B-E001_networks_of_loops" / "run"
H = 300
GRAPHS = {"figure-eight 2,2": L.figure_eight(2, 2), "figure-eight 2,3": L.figure_eight(2, 3), "figure-eight 3,3": L.figure_eight(3, 3),
          "chord 1,1,2": L.theta(1, 1, 2), "chord 1,2,2": L.theta(1, 2, 2), "theta 2,2,2": L.theta(2, 2, 2)}
SIZES = range(5, 10)


def gaps_of(s, m):
    """every m gaps of at least two cells summing to s"""
    if m == 1:
        if s >= 2:
            yield (s,)
        return
    for g in range(2, s - 2 * (m - 1) + 1):
        for rest in gaps_of(s - g, m - 1):
            yield (g,) + rest


def placements(rot, edges, s):
    """every cyclic order of each ring's contacts (first contact fixed) and every spacing with gaps >= 2"""
    verts = sorted(rot, key=repr)
    per = []
    for v in verts:
        first, rest = rot[v][0], rot[v][1:]
        opts = []
        for perm in itertools.permutations(rest):
            order = (first,) + perm
            for gaps in gaps_of(s, len(order)):
                pos, p = {}, 0
                for e, g in zip(order, gaps):
                    pos[e] = p
                    p += g
                opts.append(pos)
        per.append(opts)
    idx = {v: i for i, v in enumerate(verts)}
    for choice in itertools.product(*per):
        yield (s,) * len(verts), [(idx[u], choice[idx[u]][e], idx[v], choice[idx[v]][e], L.LAW) for e, (u, v) in enumerate(edges)]


def judge(sizes, contacts):
    arcs = L.corners(sizes, contacts)
    par = Counter((d, e, l) for d, e, ring, l in arcs)
    degenerate = any(v % 2 == 0 for v in par.values())
    D = L.dmatrix(sizes, contacts)
    ones = sum(D[c][c] == L.ONE for c in range(len(contacts)))
    fs, genus = L.faces(sizes, contacts)
    cells = L.read_cells(sizes, contacts, H)
    misses = [x[1] for x in cells if x[1] is not None]
    return genus, degenerate, ones, len(contacts), (min(misses) if misses else None)


def job2(item):
    name, s = item
    rot, edges = GRAPHS[name]
    counts, keep = Counter(), []
    for sizes, contacts in placements(rot, edges, s):
        genus, degenerate, ones, n, miss = judge(sizes, contacts)
        all_one = ones == n
        persist = miss is None
        counts[("genus %d" % genus, "degenerate" if degenerate else "not degenerate",
                "every return cancels" if all_one else "some return survives", "persistent to %d" % H if persist else "misses a ring")] += 1
        if (all_one and not degenerate) or persist:
            keep.append([name, s, [list(c[:4]) for c in contacts], genus, degenerate, ones, persist])
    return name, s, counts, keep


def job1(Gr):
    import networkx as nx
    rot, edges = L.plane_rotation(Gr)
    sizes, contacts = L.network(rot, edges, 2)
    odd, _ = L.odd_returns(L.arc_matrix(sizes, contacts))
    flips = all(L.flip(rot, edges, e) is not None for e in range(len(edges)))
    return Gr.number_of_nodes(), Gr.number_of_edges(), sorted(d for _, d in Gr.degree()), not odd, flips, sorted(nx.edges(Gr))


def atlas():
    import networkx as nx
    from networkx.generators.atlas import graph_atlas_g
    return [G for G in graph_atlas_g() if G.number_of_nodes() >= 2 and nx.is_connected(G) and min(d for _, d in G.degree()) >= 2
            and nx.check_planarity(G)[0]]


def main():
    t0 = time.time()
    items = sorted([(n, s) for n in GRAPHS for s in SIZES], key=lambda x: -x[1])
    if "--pilot" in sys.argv:
        rng = random.Random(5)
        n = 0
        total = 0
        for name, s in items:
            pl = list(placements(*GRAPHS[name], s))
            total += len(pl)
            for sizes, contacts in rng.sample(pl, min(20, len(pl))):
                judge(sizes, contacts)
                n += 1
        print("pilot:", n, "networks in", round(time.time() - t0, 1), "s; part 2 networks:", total, "; part 1 graphs:", len(atlas()))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(16) as pool:
        res1 = pool.map(job1, atlas(), chunksize=4)
        res2 = pool.map(job2, items, chunksize=1)
    p1 = {"plane ring graphs": len(res1), "every return count even": sum(r[3] for r in res1),
          "a flip at every contact": sum(r[4] for r in res1),
          "flip at every contact but some return count odd (H2 predicts none)": sum(r[4] and not r[3] for r in res1),
          "even without a flip at every contact": [{"rings": r[0], "contacts": r[1], "contacts per ring": r[2], "edges": r[5]} for r in res1 if r[3] and not r[4]],
          "even with a flip at every contact": [{"rings": r[0], "contacts": r[1], "contacts per ring": r[2]} for r in res1 if r[3] and r[4]]}
    total, by, keep = Counter(), {}, []
    for name, s, counts, kp in res2:
        total.update(counts)
        by[f"{name}, rings of {s} cells"] = {" / ".join(k): v for k, v in counts.items()}
        keep.extend(kp)
    nondeg_cancel = sum(v for k, v in total.items() if k[1] == "not degenerate" and k[2] == "every return cancels")
    result = {"experiment": "LOOP-NET-20261108-001B-E001", "part 1": p1,
              "part 2 networks": sum(total.values()),
              "part 2 totals": {" / ".join(k): v for k, v in sorted(total.items())},
              "H1 (no placement without a cancelled corner pair cancels every return)": nondeg_cancel == 0,
              "H2 (every plane graph with a flip at every contact has every return count even)": p1["flip at every contact but some return count odd (H2 predicts none)"] == 0,
              "part 2 by graph and size": by, "seconds": round(time.time() - t0, 1)}
    (OUT / "networks.json").write_text(json.dumps({"columns": ["graph", "size", "contacts (ring a, pos a, ring b, pos b)", "genus", "degenerate",
                                                               "contacts with D_cc = 1", "persistent to 300"], "rows": keep}) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("part 2 by graph and size",)}, indent=1)[:4000])


if __name__ == "__main__":
    main()
