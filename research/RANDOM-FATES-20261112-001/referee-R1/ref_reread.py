#!/usr/bin/env python3
"""Referee RANDOM-FATES-R1: re-read the census's bases (regenerated from their seeds by ref_fates.py) with the referee's own reader.

    python3 -B ref_reread.py --part u|g|gk|cores [--workers 8]

u:     uniform bases (read runs 5 to 14 at every size; the full set proved too slow on the shared machine) at every read point: exact tie classes against the record; at P1's points
       f0.5 and f0.75 the least bond of every recorded pair. Sizes 2 to 4 over every distinction; size 5
       over every distinction at n <= 100, else over the uncapped lens of steps(u, w) + steps(w, v) <= d + 2.
g:     the living bases at the horizon read for P6, P7 and C2 (X0.1, X0.2, Og0.0, Og0.05, Og0.1, L4_0.5, L4_0.7, T): ties, and
       the least bond of every recorded pair; sizes 2 and 3 over every distinction, size 4 over the uncapped lens with d + 2,
       size 5 over the uncapped lens with d + 1 (the census: 40 nearest of the d + 1 lens for both, beyond 600 distinctions).
gk:    the bases before the end of every growth that ended and was read (X, O, newest-five and -six): exact tie classes.
cores: minimal contradictions by the referee's own deletion (Glucose 4, deletion in reverse order of arrival), for every U50
       and U100 run, U200 runs 0 to 49, and every ending of X, O and newest-five and -six growth.
Each base is written to result_<part>.jsonl as it finishes; a rerun skips bases already written."""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import ref_fates as F
from pysat.solvers import Glucose4

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A = ROOT / "artifacts/RANDOM-FATES-20261112-001A/RANDOM-FATES-20261112-001A-E001_fates_census"
FULL_U = ("f0.5", "f0.75", "f0.9", "k1", "k10", "k50")
ALL_U = FULL_U + ("k2", "k3", "k5", "k20")
BONDS_U = ("f0.5", "f0.75")                     # least bonds re-read at P1's registered points; ties at every point
G_END = ("X0.1", "X0.2", "Og0.0", "Og0.05", "Og0.1", "L4_0.5", "L4_0.7", "T")
G_K = ("k1", "k2", "k3", "k5", "k10", "k20", "k50")


def records():
    return {(r["label"], r["run"]): r for r in map(json.loads, open(A / "runs.jsonl"))}


def base_of(lab, run, point, knots):
    M = len(knots)
    if point == "end":
        return knots
    if point.startswith("f"):
        return knots[:int(round(float(point[1:]) * M))]
    return knots[:M - int(point[1:])]


def tie_summary(B):
    cl = B.ties()
    sizes = sorted((len(c) for c in cl), reverse=True)
    return {"classes": len(cl), "largest_class": sizes[0] if sizes else 1, "tied_pairs": sum(s * (s - 1) // 2 for s in sizes),
            "n_used": len(B.used)}


def read_job(item):
    lab, run, point, rec_read, do_bonds = item
    t0 = time.time()
    knots, dead = F.grow(lab, run)
    n = int(lab[1:]) if lab.startswith("U") else max(v for t in knots for v in t) + 1
    base = base_of(lab, run, point, knots)
    B = F.Base(n, base, seed=F.seed_of(lab, run, point, "referee"))
    out = {"label": lab, "run": run, "point": point, "knots": len(base)}
    if not B.ok:
        out["state"] = False
        B.close()
        return out
    out["state"] = True
    out.update(tie_summary(B))
    out["record"] = {k: rec_read.get(k) for k in ("classes", "largest_class", "tied_pairs", "n_used")}
    out["ties agree"] = all(out[k] == rec_read.get(k) for k in ("classes", "largest_class", "tied_pairs", "n_used"))
    if do_bonds and "bond_profile" in rec_read:
        nb = F.neighbours(n, base)
        pairs = []
        for d, lst in rec_read["bond_profile"].items():
            d = int(d)
            for (u, v, size, kind) in lst:
                if lab.startswith("U"):
                    pool4 = B.used
                    pool5 = B.used if n <= 100 else F.lens(nb, u, v, d, 2)
                else:
                    pool4 = F.lens(nb, u, v, d, 2)
                    pool5 = F.lens(nb, u, v, d, 1)
                mine = B.least_bond(u, v, pool4, pool5)
                # is the census's own bond size reachable? (only meaningful when it found one)
                pairs.append({"d": d, "u": u, "v": v, "census": size, "census kind": kind, "referee": mine,
                              "pool4": len(pool4), "pool5": len(pool5)})
        out["pairs"] = pairs
    B.close()
    out["seconds"] = round(time.time() - t0, 1)
    return out


def core_job(item):
    lab, run = item
    t0 = time.time()
    knots, dead = F.grow(lab, run)
    if not dead:
        return {"label": lab, "run": run, "dead": False}
    sel_base = max(v for t in knots for v in t) + 2
    sel = [sel_base + i for i in range(len(knots))]
    with Glucose4() as s:
        for i, t in enumerate(knots):
            for c in F.nae_clauses(t):
                s.add_clause(c + [-sel[i]])
        assert not s.solve(assumptions=sel)
        keep = sorted(set(s.get_core()), reverse=True)        # newest first
        i = 0
        while i < len(keep):
            trial = keep[:i] + keep[i + 1:]
            if not s.solve(assumptions=trial):
                core = set(s.get_core())
                keep = [x for x in trial if x in core]
            else:
                i += 1
        # minimality check: every proper subset by one removal allows a state
        minimal = all(s.solve(assumptions=keep[:j] + keep[j + 1:]) for j in range(len(keep)))
    core = [knots[x - sel_base] for x in keep]
    cv = sorted({v for t in core for v in t})
    return {"label": lab, "run": run, "dead": True, "death_knot": len(knots), "core_knots": len(core),
            "core_distinctions": len(cv), "core_index_span": cv[-1] - cv[0], "core_has_killer": knots[-1] in core,
            "minimal": minimal, "seconds": round(time.time() - t0, 1)}


def items(part, recs):
    out = []
    if part == "u":
        for n in (50, 100, 200, 300):
            for run in range(5, 15):           # ten read runs per size (U300's first read run is 5)
                r = recs[(f"U{n}", run)]
                for p in ALL_U:
                    if p in r["reads"]:
                        out.append((f"U{n}", run, p, r["reads"][p], p in BONDS_U))
    elif part == "g":
        for lab in G_END:
            for run in range(30):
                r = recs.get((lab, run))
                if r and "reads" in r and "end" in r["reads"]:
                    out.append((lab, run, "end", r["reads"]["end"], True))
    elif part == "gk":
        for (lab, run), r in sorted(recs.items()):
            if lab.startswith(("X", "Og", "Ol", "L5", "L6")) and r["dead"] and "reads" in r:
                for p in G_K:
                    if p in r["reads"]:
                        out.append((lab, run, p, r["reads"][p], False))
    elif part == "cores":
        for (lab, run), r in sorted(recs.items()):
            if lab in ("U50", "U100") or (lab == "U200" and run < 50) or (lab.startswith(("X", "Og", "Ol", "L5", "L6")) and r["dead"]):
                out.append((lab, run))
    return out


def main():
    part = sys.argv[sys.argv.index("--part") + 1]
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8
    recs = records()
    path = HERE / f"result_{part}.jsonl"
    done = set()
    if path.exists():
        for l in open(path):
            x = json.loads(l)
            done.add((x["label"], x["run"], x.get("point")))
    its = [it for it in items(part, recs) if (it[0], it[1], it[2] if part != "cores" else None) not in done]
    if part == "u":
        # P1's bond points first (every size), then the tie points from the smallest size up (n = 300's are the slowest)
        its.sort(key=lambda it: (not it[4], int(it[0][1:]), it[1]))
    elif part == "cores":
        # smallest first: U50 and U100 (P3 at n = 100) before U200
        its.sort(key=lambda it: (int(it[0][1:]) if it[0].startswith("U") else 0, it[1]))
    else:
        its.sort(key=lambda it: -(int(it[0][1:]) if it[0].startswith("U") else 2000))
    fn = core_job if part == "cores" else read_job
    t0 = time.time()
    with Pool(workers) as pool, open(path, "a") as f:
        for i, rec in enumerate(pool.imap_unordered(fn, its, chunksize=1)):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            if (i + 1) % 50 == 0:
                print(f"{i + 1}/{len(its)} {time.time() - t0:.0f} s", flush=True)
    print("done", part, round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
