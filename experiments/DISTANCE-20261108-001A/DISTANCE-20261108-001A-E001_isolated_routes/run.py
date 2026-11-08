"""DISTANCE-20261108-001A-E001: counted length along isolated routes, the frozen test of A40 (see contract.json).

    .venv/bin/python3 -B run.py           the test; writes artifacts/DISTANCE-20261108-001A/DISTANCE-20261108-001A-E001_isolated_routes/
                                          run/result.json
    .venv/bin/python3 -B run.py --pilot   times a network off the roster (a loop of six rings) and prints no verdicts
In each network of the roster (distance_lib.substrates), with every contact g cells apart (g = 2, 3, 4), for L = 1 to 10, three random
shortest routes of L arcs and three random chordless routes of L arcs, each from a ring X holding only its first contact. Every contact
off the route is frozen and the first lag at which the last contact needs X is read at the cell level (rows of M^T).
  (a) affinity: that lag is g L + 1;
  (b) additivity: split at every inner contact c_i, with Y the ring of c_i that the next hop leaves, the first lags of the two halves,
      each isolated on its own, satisfy (t_P - 1) + (t_Q - 1) = t - 1;
  (c) unequal corners: on the square torus of side 5 and the genus-2 network of 16 rings, with consecutive contacts 2 to 5 cells apart
      at random, the first lag is 1 + the cells the route carries influence through (each corner's own cells plus the contact it
      reaches)."""
from __future__ import annotations

import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import distance_lib as D  # noqa: E402

OUT = ROOT / "artifacts" / "DISTANCE-20261108-001A" / "DISTANCE-20261108-001A-E001_isolated_routes" / "run"
SEED = 20261108
GS = (2, 3, 4)
LMAX = 10
PER = 3
UNEQUAL = ("square torus 5", "genus 2, 16 rings of three contacts (GL(2,3))")


def routes_for(rng, out, inn, rc, n, L):
    rings = sorted(rc)
    got = []
    for kind in ("shortest", "chordless"):
        k = 0
        for _ in range(60):
            if k == PER:
                break
            X = rng.choice(rings)
            r = D.shortest_route(rng, out, inn, rc, n, X, L) if kind == "shortest" else D.random_route(rng, out, rc, n, X, L)
            if r is None or not D.valid_route(out, rc, None, r, X):
                continue
            got.append((kind, X, r))
            k += 1
    return got


def measure(sizes, contacts, out, rc, route, X, predicted):
    """(t, splits): the isolated first lag of the whole route and, at each inner contact, (i, t_P, t_Q), or (i, "skip", "skip") when
    c_i's other ring holds a later contact of the route, so that the second half is not a route from it"""
    horizon = 2 * predicted + 8
    t = D.isolated_first_need(sizes, contacts, route, X, horizon)
    splits = []
    for i in range(1, len(route) - 1):
        c = route[i]
        ra, rb = D.rings_of(contacts, c)
        S = D.hop_ring(out, c, route[i + 1])
        Y = rb if S == ra else ra
        if not D.valid_route(out, rc, contacts, route[i:], Y):
            splits.append((i, "skip", "skip"))
            continue
        tp = D.isolated_first_need(sizes, contacts, route[:i + 1], X, horizon)
        tq = D.isolated_first_need(sizes, contacts, route[i:], Y, horizon)
        splits.append((i, tp, tq))
    return t, splits


def task(args):
    name, g = args
    rot, edges = D.substrates()[name]
    sizes, contacts = D.LN.network(rot, edges, g)
    out, inn, rc = D.graph(sizes, contacts)
    n = len(contacts)
    rng = random.Random("%d/%s/%d" % (SEED, name, g))
    rec = {"substrate": name, "g": g, "rings": len(rc), "contacts": n, "parallel arcs": D.parallel_arcs(out),
           "routes": 0, "affine": 0, "splits": 0, "additive": 0, "splits skipped": 0, "lengths without a route": [],
           "failures": []}
    for L in range(1, LMAX + 1):
        rs = routes_for(rng, out, inn, rc, n, L)
        if not rs:
            rec["lengths without a route"].append(L)
        for kind, X, r in rs:
            t, splits = measure(sizes, contacts, out, rc, r, X, g * L + 1)
            rec["routes"] += 1
            if t == g * L + 1:
                rec["affine"] += 1
            else:
                rec["failures"].append({"test": "a", "L": L, "kind": kind, "X": X, "route": r, "t": t})
            for i, tp, tq in splits:
                if tp == "skip":
                    rec["splits skipped"] += 1
                    continue
                rec["splits"] += 1
                if t is not None and tp is not None and tq is not None and (tp - 1) + (tq - 1) == t - 1:
                    rec["additive"] += 1
                else:
                    rec["failures"].append({"test": "b", "L": L, "kind": kind, "X": X, "route": r, "i": i, "t": t, "tP": tp, "tQ": tq})
    return rec


def task_unequal(args):
    name, rep = args
    rot, edges = D.substrates()[name]
    rng = random.Random("%d/unequal/%s/%d" % (SEED, name, rep))
    sizes, contacts = D.network_gaps(rot, edges, rng)
    out, inn, rc = D.graph(sizes, contacts)
    n = len(contacts)
    rec = {"substrate": name, "replicate": rep, "parallel arcs": D.parallel_arcs(out), "routes": 0, "cells read": 0, "failures": []}
    for L in range(1, LMAX + 1):
        for kind, X, r in routes_for(rng, out, inn, rc, n, L):
            want = 1 + sum(D.hop_cells(out, r))
            t = D.isolated_first_need(sizes, contacts, r, X, 2 * want + 8)
            rec["routes"] += 1
            if t == want:
                rec["cells read"] += 1
            else:
                rec["failures"].append({"test": "c", "L": L, "kind": kind, "X": X, "route": r, "t": t, "predicted": want})
    return rec


def pilot():
    t0 = time.time()
    rot, edges = D.LN.dihedron(6)
    for g in GS:
        sizes, contacts = D.LN.network(rot, edges, g)
        out, inn, rc = D.graph(sizes, contacts)
        rng = random.Random(1)
        k = sum(len(routes_for(rng, out, inn, rc, len(contacts), L)) for L in range(1, 6))
        print("pilot: loop of six rings, g = %d: %d routes sampled" % (g, k))
    print("pilot: %.1f s; no verdicts printed" % (time.time() - t0))


def main():
    if "--pilot" in sys.argv:
        pilot()
        return
    t0 = time.time()
    names = list(D.substrates())
    with Pool(16) as pool:
        recs = pool.map(task, [(nm, g) for nm in names for g in GS])
        unequal = pool.map(task_unequal, [(nm, rep) for nm in UNEQUAL for rep in range(4)])
    a = all(r["affine"] == r["routes"] for r in recs)
    b = all(r["additive"] == r["splits"] for r in recs)
    c = all(r["cells read"] == r["routes"] for r in unequal)
    verdict = ("Overturned" if not (a and b) else "Confirmed" if c else "Reworded: counted length in contacts holds on equally spaced "
               "networks only")
    res = {"experiment": "DISTANCE-20261108-001A-E001", "seed": SEED, "g": list(GS), "L max": LMAX, "routes per kind": PER,
           "totals": {"routes": sum(r["routes"] for r in recs), "affine": sum(r["affine"] for r in recs),
                      "splits": sum(r["splits"] for r in recs), "additive": sum(r["additive"] for r in recs),
                      "splits skipped": sum(r["splits skipped"] for r in recs),
                      "unequal routes": sum(r["routes"] for r in unequal), "unequal cells read": sum(r["cells read"] for r in unequal)},
           "pass": {"a affinity": a, "b additivity": b, "c cells": c}, "verdict for A40": verdict,
           "by substrate": recs, "unequal corners": unequal, "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: res[k] for k in ("totals", "pass", "verdict for A40", "seconds")}, indent=1))


if __name__ == "__main__":
    main()
