"""GROW-NET-20261108-001B-E001: a census of growth steps (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the census; writes artifacts/GROW-NET-20261108-001B/GROW-NET-20261108-001B-E001_growth_steps/run/result.json
    .venv/bin/python3 -B run.py --pilot   times one seed and prints no verdicts
Part 1: from balanced seeds, every way to attach one new ring by m contacts (GROW-NET-20261108-001A's grow_lib.attachments), m = 1 to 3,
and m = 4 on seeds of at most 8 rings; for each, whether every contact keeps even return counts (exact), and whether two corners from
one contact to the same next contact cancel. Part 2: the truncations and rectifications of the five Platonic networks. Equally spaced
contacts throughout, so even return counts are exactly persistence (LOOP-NET-20261108-001A, Theorem 2)."""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/GROW-NET-20261108-001A/GROW-NET-20261108-001A-P001_bands_grow_single_rings_do_not"))
import grow_lib as G  # noqa: E402

LN, Gl = G.LN, G.Gl
OUT = ROOT / "artifacts" / "GROW-NET-20261108-001B" / "GROW-NET-20261108-001B-E001_growth_steps" / "run"


def seeds():
    out = {"loop of %d rings" % r: LN.dihedron(r) for r in range(3, 7)}
    out.update({"two rings sharing %d contacts" % k: LN.hosohedron(k) for k in range(3, 6)})
    out.update({nm: LN.platonic(nm) for nm in ("tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron")})
    out.update({"square torus %d" % n: LN.square_torus(n) for n in (3, 4)})
    out["genus-2 network of 16 rings"] = Gl.gl23_maps()[(3, 8)]
    return out


def degenerate(rot):
    seen = Counter()
    for v, lst in rot.items():
        for i in range(len(lst)):
            seen[(lst[i], lst[(i + 1) % len(lst)])] += 1
    return any(c % 2 == 0 for c in seen.values())


def job(item):
    name, m = item
    rot, edges = seeds()[name]
    tot = good = good_nd = 0
    examples = []
    for new_rot, new_edges in G.attachments(rot, edges, m):
        tot += 1
        if G.balanced(new_rot, len(new_edges)):
            good += 1
            nd = not degenerate(new_rot)
            good_nd += nd
            if len(examples) < 3:
                examples.append({"new ring's contacts on": [repr(new_edges[e][0]) for e in new_rot["new"]], "cancelling corners": not nd})
    return name, m, tot, good, good_nd, examples


def refinements():
    out = {}
    for nm in ("tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"):
        G0 = G.platonic_graph(nm)
        for label, H in (("truncated", G.truncation(G0)), ("rectified", G.rectification(G0))):
            rot, edges = LN.plane_rotation(H)
            out["%s %s" % (label, nm)] = {"rings": H.number_of_nodes(), "contacts": len(edges), "balanced": G.balanced(rot, len(edges)),
                                          "contacts with an odd return count": len(G.odd_contacts(rot, len(edges)))}
    return out


def main():
    t0 = time.time()
    S = seeds()
    items = [(nm, m) for nm in S for m in (1, 2, 3)] + [(nm, 4) for nm, (rot, edges) in S.items() if len(rot) <= 8]
    if "--pilot" in sys.argv:
        job(("tetrahedron", 3))
        print("pilot: tetrahedron, three contacts, in", round(time.time() - t0, 1), "s; jobs:", len(items))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(16) as pool:
        res = pool.map(job, sorted(items, key=lambda x: -x[1]), chunksize=1)
    by = {}
    for name, m, tot, good, good_nd, ex in res:
        by.setdefault(name, {})[str(m)] = {"attachments": tot, "every contact persistent": good, "of these without cancelling corners": good_nd, "examples": ex}
    big = [nm for nm, (rot, edges) in S.items() if len(rot) > 4]
    h1 = all(by[nm][str(m)]["every contact persistent"] == 0 for nm in by for m in ("1", "2")) and \
        all(by[nm][m]["every contact persistent"] == 0 for nm in big for m in by[nm])
    ref = refinements()
    h2 = all((not v["balanced"]) == (k != "rectified tetrahedron") for k, v in ref.items())
    result = {"experiment": "GROW-NET-20261108-001B-E001", "part 1 by seed and contacts": by, "part 2 refinements": ref,
              "H1 (no attachment by 1 or 2 contacts keeps persistence; none by 3 or 4 on a seed of more than 4 rings)": h1,
              "H2 (every truncation and rectification of a Platonic network loses persistence except the rectified tetrahedron)": h2,
              "attachments": sum(r[2] for r in res), "seconds": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "part 1 by seed and contacts"}, indent=1)[:3000])
    for nm in by:
        print(nm, {m: (v["attachments"], v["every contact persistent"], v["of these without cancelling corners"]) for m, v in by[nm].items()})


if __name__ == "__main__":
    main()
