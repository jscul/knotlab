"""PLAIN-TIME-20261108-001A-E001: when the plain first need is on time, a census of regular maps (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the census; writes artifacts/PLAIN-TIME-20261108-001A/PLAIN-TIME-20261108-001A-E001_map_census/
                                          run/result.json
    .venv/bin/python3 -B run.py --pilot   checks the construction on small maps off the census's verdicts (A4, S4, tori of index at
                                          most 13, loops and two rings sharing contacts, up to 8) and times one group; prints no verdict
Every map is a network of equally spaced rule-60 rings with law (12, 12) contacts. For one target contact (every contact is alike under
the map's rotations), the directed distance and the number of shortest routes from every contact, the least odd walk length (exact),
and the verdict for every ring: on time when an odd number of shortest routes arrive from one of its contacts at its distance."""
from __future__ import annotations

import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import plain_lib as P  # noqa: E402

OUT = ROOT / "artifacts" / "PLAIN-TIME-20261108-001A" / "PLAIN-TIME-20261108-001A-E001_map_census" / "run"
GROUPS = (["A 4", "S 4", "SL(2,p) 3", "GL(2,p) 3", "PSL(2,p) 5", "PGL(2,p) 5", "SL(2,p) 5", "S 5", "PSL(2,p) 7", "PGL(2,p) 7",
           "SL(2,p) 7", "A 6", "GL(2,p) 5", "S 6", "PSL(2,p) 11", "PGL(2,p) 11", "PSL(2,p) 13", "PGL(2,p) 13", "PSL(2,p) 17", "A 7",
           "PSL(2,p) 19", "PSL(2,p) 23", "PSL(2,p) 29"] + ["D %d" % n for n in range(3, 31)])
TORI = {"square": 400, "triangular": 300, "honeycomb": 200}
LOOPS = range(2, 61)


def genus(rings, contacts, faces):
    return (2 - (rings - contacts + faces)) // 2


def group_rows(name):
    G, gens = P.group(name)
    rows, seen = [], {}
    for x, y in P.generating_pairs(G, gens):
        n, out, rc, target, m, f = P.group_map(G, x, y)
        v = P.verdicts(n, out, rc, target)
        row = {"family": "group", "name": name, "order": len(G), "m": m, "f": f,
               "genus": genus(len(rc), n, len(G) // f), "rings": len(rc), "contacts": n, **v}
        key = json.dumps(row, sort_keys=True)
        if key in seen:
            rows[seen[key]]["maps"] += 1
        else:
            seen[key] = len(rows)
            row["maps"] = 1
            rows.append(row)
    return rows


def network_row(family, name, rot, edges, m, f, targets=(0,)):
    sizes, contacts = P.LN.network(rot, edges, 2)
    n, out, rc = P.network_map(sizes, contacts)
    fs, g = P.LN.faces(sizes, contacts)
    vs = [P.verdicts(n, out, rc, t) for t in targets]
    row = {"family": family, "name": name, "m": m, "f": f, "genus": g, "rings": len(rc), "contacts": n, **vs[0]}
    return row, all(json.dumps(v, sort_keys=True) == json.dumps(vs[0], sort_keys=True) for v in vs)


def torus_row(args):
    kind, b, c = args
    rot, edges = P.lattice_torus(kind, b, c)
    m, f = {"square": (4, 4), "triangular": (6, 3), "honeycomb": (3, 6)}[kind]
    return network_row("torus", "%s (%d,%d)" % (kind, b, c), rot, edges, m, f)[0]


def loop_rows(k):
    a = network_row("loop", "loop of %d rings" % k, *P.LN.dihedron(k), 2, k)[0]
    b = network_row("loop", "two rings sharing %d contacts" % k, *P.LN.hosohedron(k), k, 2)[0]
    return [a, b]


def pilot():
    t0 = time.time()
    # the group construction against distance_lib.regular_map and loopnet_lib (the repository's contact graph), on A4 and S4
    for name in ("A 4", "S 4"):
        G, gens = P.group(name)
        for x, y in P.generating_pairs(G, gens):
            n, out, rc, target, m, f = P.group_map(G, x, y)
            v1 = P.verdicts(n, out, rc, target)
            rot, edges = P.D.regular_map(G, P.mul, tuple(range(len(G[0]))), x, y)
            row, same = network_row("check", name, rot, edges, m, f, targets=range(n))
            assert same, ("not transitive", name)
            for k in ("diameter", "rings late", "rings never", "contacts late", "contacts never", "largest count"):
                assert row[k] == v1[k], (name, k, row[k], v1[k])
    # every target alike on small tori, loops and two rings sharing contacts
    for kind in TORI:
        for b, c, N in P.torus_shapes(kind, 13):
            rot, edges = P.lattice_torus(kind, b, c)
            m, f = {"square": (4, 4), "triangular": (6, 3), "honeycomb": (3, 6)}[kind]
            nc = len(edges)
            row, same = network_row("check", kind, rot, edges, m, f, targets=range(nc))
            assert same, ("not transitive", kind, b, c)
            assert row["genus"] == 1 and row["cone mismatches"] == 0
    for k in range(2, 9):
        for rot, edges in (P.LN.dihedron(k), P.LN.hosohedron(k)):
            row, same = network_row("check", "loop", rot, edges, 2, k, targets=range(len(edges)))
            assert same
    t1 = time.time()
    G, gens = P.group("PSL(2,p) 13")
    k = sum(1 for _ in P.generating_pairs(G, gens))
    print("pilot: construction checks passed in %.1f s; PSL(2,13) has %d maps up to the centraliser, enumerated in %.1f s; no verdicts"
          % (t1 - t0, k, time.time() - t1))


def main():
    if "--pilot" in sys.argv:
        pilot()
        return
    t0 = time.time()
    tori = [(kind, b, c) for kind, nmax in TORI.items() for b, c, N in P.torus_shapes(kind, nmax)]
    with Pool(16) as pool:
        groups = pool.map(group_rows, GROUPS, chunksize=1)
        trs = pool.map(torus_row, tori, chunksize=4)
        lps = pool.map(loop_rows, LOOPS)
    rows = [r for g in groups for r in g] + trs + [r for pair in lps for r in pair]
    for r in rows:
        r["kind"] = ("sphere" if r["genus"] == 0 else "torus" if r["genus"] == 1 else "higher genus")
        r["on time"] = r["rings late"] == 0 and r["rings never"] == 0
        r["unique routes to the diameter"] = r["shortest pair of equal routes"] is None
    summary = {}
    for r in rows:
        key = "%s, genus %s" % (r["family"], "0" if r["genus"] == 0 else "1" if r["genus"] == 1 else ">= 2")
        s = summary.setdefault(key, {"maps": 0, "on time": 0})
        s["maps"] += 1
        s["on time"] += r["on time"]
    h1 = [r["name"] for r in rows if r["on time"] != r["unique routes to the diameter"]]
    late_hyper = [(r["name"], r["m"], r["f"], r["genus"]) for r in rows if r["genus"] >= 2 and not r["on time"]]
    tori_on = sorted((r["name"], r["rings"]) for r in rows if r["family"] == "torus" and r["on time"])
    res = {"experiment": "PLAIN-TIME-20261108-001A-E001", "rows": rows, "summary": summary,
           "H1 (on time exactly when shortest routes are unique to the diameter): counterexamples": h1,
           "H2 (every map of genus 0 or at least 2 on time): late maps of genus at least 2": late_hyper,
           "H2: tori on time": tori_on,
           "cone mismatches": sum(r["cone mismatches"] for r in rows), "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1)[:6000])


if __name__ == "__main__":
    main()
