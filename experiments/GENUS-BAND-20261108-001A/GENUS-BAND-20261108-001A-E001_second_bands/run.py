"""GENUS-BAND-20261108-001A-E001: a census of second bands (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the census; writes artifacts/GENUS-BAND-20261108-001A/GENUS-BAND-20261108-001A-E001_second_bands/run/result.json
    .venv/bin/python3 -B run.py --pilot   times one family on one base and prints no verdicts
Bases: the 20 balanced genus-2 first bands on loops of 5 rings (two loops joined by single rungs; BAND-SURFACE-20261108-001A's band_lib)
and the n x 2 tori, n = 3 to 5 (GROW-NET-20261108-001A's grow_lib). A second band is a new loop of n rings (i, 2), joined column by column:
  S1  every rung (i,0)-(i,1) subdivided by (i,2): (i,0)-(i,2)-(i,1), the old rings keeping their orders; every order of each new ring;
  S2  joined to row r by one rung per column, inserted in every gap; every order of each new ring;
  S3  joined to row r by two rungs per column (a uniform rule: the same gaps and new order at every column; on the 3 x 2 torus every way);
  S5  joined to both rows with the old rungs kept (a uniform rule, and 300,000 uniform random cases).
Balance is exact (return counts followed until the next vector lies in the span of the earlier ones); no lag cutoff."""
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
sys.path.insert(0, str(ROOT / "proofs/BAND-SURFACE-20261108-001A/BAND-SURFACE-20261108-001A-P001_one_band_makes_the_torus"))
import band_lib as B  # noqa: E402

G, LN = B.G, B.LN
OUT = ROOT / "artifacts" / "GENUS-BAND-20261108-001A" / "GENUS-BAND-20261108-001A-E001_second_bands" / "run"
ORD3 = [("E", "W", "r0"), ("E", "r0", "W")]
ORD4 = [("E",) + p for p in itertools.permutations(("W", "down", "up"))]
ORD4D = [("E",) + p for p in itertools.permutations(("W", "r0", "r1"))]


def genus2_bases():
    inc, edges = B.loop_and_band(5, False)
    return [(rot, edges) for rot in B.rotations(inc) if G.balanced(rot, len(edges))]


def twisted_columns(rot, inc, n):
    """a column is twisted when both of its rings list their contacts against the counterclockwise order of the planar prism"""
    out = []
    for i in range(n):
        flips = []
        for r in (0, 1):
            lst = rot[(i, r)]
            base = inc[(i, r)] if i else [inc[(i, r)][1], inc[(i, r)][0], inc[(i, r)][2]]
            flips.append(lst != base and lst != base[1:] + base[:1] and lst != base[2:] + base[:2])
        out.append(flips)
    return out


def subdivide(rot, edges, n, orders):
    edges, rot = list(edges), {v: list(l) for v, l in rot.items()}
    rung = {u[0]: e for e, (u, w) in enumerate(edges) if u[0] == w[0] and {u[1], w[1]} == {0, 1}}
    newE = {}
    for i in range(n):
        newE[i] = len(edges)
        edges.append(((i, 2), ((i + 1) % n, 2)))
    up = {}
    for i in range(n):
        e_old = rung[i]
        edges[e_old] = ((i, 0), (i, 2))
        up[i] = len(edges)
        edges.append(((i, 2), (i, 1)))
        lst = rot[(i, 1)]
        lst[lst.index(e_old)] = up[i]
    for i in range(n):
        items = {"E": newE[i], "W": newE[(i - 1) % n], "down": rung[i], "up": up[i]}
        rot[(i, 2)] = [items[k] for k in orders[i]]
    return rot, edges


def stack(rot, edges, n, row, gaps, orders, gaps2=None):
    edges, rot = list(edges), {v: list(l) for v, l in rot.items()}
    newE = {}
    for i in range(n):
        newE[i] = len(edges)
        edges.append(((i, 2), ((i + 1) % n, 2)))
    rungs = {}
    for i in range(n):
        lst = rot[(i, row)]
        e = len(edges)
        edges.append(((i, row), (i, 2)))
        lst.insert(gaps[i] + 1, e)
        rungs[i] = [e]
        if gaps2 is not None:
            e2 = len(edges)
            edges.append(((i, row), (i, 2)))
            lst.insert((gaps2[i] % len(lst)) + 1, e2)
            rungs[i].append(e2)
    for i in range(n):
        items = {"E": newE[i], "W": newE[(i - 1) % n], "r0": rungs[i][0]}
        if gaps2 is not None:
            items["r1"] = rungs[i][1]
        rot[(i, 2)] = [items[k] for k in orders[i]]
    return rot, edges


def both_rows(rot, edges, n, g0, g1, orders):
    edges, rot = list(edges), {v: list(l) for v, l in rot.items()}
    newE, d, u = {}, {}, {}
    for i in range(n):
        newE[i] = len(edges)
        edges.append(((i, 2), ((i + 1) % n, 2)))
    for i in range(n):
        d[i] = len(edges)
        edges.append(((i, 0), (i, 2)))
        rot[(i, 0)].insert(g0[i] + 1, d[i])
        u[i] = len(edges)
        edges.append(((i, 1), (i, 2)))
        rot[(i, 1)].insert(g1[i] + 1, u[i])
    for i in range(n):
        items = {"E": newE[i], "W": newE[(i - 1) % n], "down": d[i], "up": u[i]}
        rot[(i, 2)] = [items[k] for k in orders[i]]
    return rot, edges


def tally(networks):
    tot, kept = 0, Counter()
    for rot, edges in networks:
        tot += 1
        if G.balanced(rot, len(edges)):
            sizes, contacts = LN.network(rot, edges, 2)
            kept[LN.faces(sizes, contacts)[1]] += 1
    return tot, kept


def job(name):
    bases = genus2_bases()
    n = 5
    if name == "S1 on genus 2":
        return name, tally(subdivide(r, e, n, o) for r, e in bases for o in itertools.product(ORD4, repeat=n))
    if name == "S2 on genus 2":
        return name, tally(stack(r, e, n, row, g, o) for r, e in bases for row in (0, 1)
                           for g in itertools.product(range(3), repeat=n) for o in itertools.product(ORD3, repeat=n))
    if name == "S3 uniform on genus 2":
        return name, tally(stack(r, e, n, row, [a] * n, [o] * n, [b] * n) for r, e in bases for row in (0, 1)
                           for a in range(3) for b in range(4) for o in ORD4D)
    if name == "S5 uniform on genus 2":
        return name, tally(both_rows(r, e, n, [a] * n, [b] * n, [o] * n) for r, e in bases for a in range(3) for b in range(3) for o in ORD4)
    if name == "S5 sample on genus 2":
        rng = random.Random(1)

        def gen():
            for _ in range(300000):
                r, e = bases[rng.randrange(len(bases))]
                yield both_rows(r, e, n, [rng.randrange(3) for _ in range(n)], [rng.randrange(3) for _ in range(n)], [rng.choice(ORD4) for _ in range(n)])
        return name, tally(gen())
    kind, nn = name.rsplit(" ", 1)
    nn = int(nn)
    rot, edges = G.rect_torus(nn, 2)
    if kind == "S1 on the torus n x 2, n =":
        return name, tally(subdivide(rot, edges, nn, o) for o in itertools.product(ORD4, repeat=nn))
    if kind == "S2 on the torus n x 2, n =":
        return name, tally(stack(rot, edges, nn, 0, g, o) for g in itertools.product(range(4), repeat=nn) for o in itertools.product(ORD3, repeat=nn))
    if kind == "S3 on the torus n x 2, n =":
        if nn == 3:
            return name, tally(stack(rot, edges, nn, 0, list(g), list(o), list(g2)) for g in itertools.product(range(4), repeat=3)
                               for g2 in itertools.product(range(5), repeat=3) for o in itertools.product(ORD4D, repeat=3))
        rng = random.Random(2)
        uni = list(stack(rot, edges, nn, 0, [a] * nn, [o] * nn, [b] * nn) for a in range(4) for b in range(5) for o in ORD4D)
        samp = (stack(rot, edges, nn, 0, [rng.randrange(4) for _ in range(nn)], [rng.choice(ORD4D) for _ in range(nn)],
                      [rng.randrange(5) for _ in range(nn)]) for _ in range(100000))
        return name, tally(itertools.chain(uni, samp))


def main():
    t0 = time.time()
    names = ["S1 on genus 2", "S2 on genus 2", "S3 uniform on genus 2", "S5 uniform on genus 2", "S5 sample on genus 2"]
    names += ["%s %d" % (k, nn) for k in ("S1 on the torus n x 2, n =", "S2 on the torus n x 2, n =", "S3 on the torus n x 2, n =") for nn in (3, 4, 5)]
    if "--pilot" in sys.argv:
        job("S5 uniform on genus 2")
        print("pilot in", round(time.time() - t0, 1), "s; families:", len(names))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    bases = genus2_bases()
    inc, _ = B.loop_and_band(5, False)
    twists = sorted(sum(all(f) for f in twisted_columns(r, inc, 5)) for r, e in bases)
    with Pool(12) as pool:
        res = dict(pool.map(job, names, chunksize=1))
    fams = {k: {"second bands": v[0], "balanced, by genus": dict(v[1])} for k, v in res.items()}
    g2 = [k for k in fams if "genus 2" in k]
    tor = [k for k in fams if "torus" in k]
    result = {"experiment": "GENUS-BAND-20261108-001A-E001", "genus-2 bases": len(bases),
              "twisted columns per base (both rings reversed)": dict(sorted((t, twists.count(t)) for t in set(twists))),
              "families": fams,
              "H1 (no second band in the families keeps a genus-2 base balanced)": all(not fams[k]["balanced, by genus"] for k in g2),
              "H2 (on the n x 2 tori the balanced second bands in the families all have genus 1)": all(set(fams[k]["balanced, by genus"]) <= {1} for k in tor),
              "second bands": sum(v["second bands"] for v in fams.values()), "seconds": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1)[:4000])


if __name__ == "__main__":
    main()
