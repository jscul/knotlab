#!/usr/bin/env python3
"""Referee PARITY-SURVIVE-R1, with the referee's own code (PARITY-MIX-R1's ref_parity.py and ref_parity_fast.py; no import of
survive_lib.py, check.py, parity_lib.py or shift_lib.py):
  classlevel  every placement of 3 x 3 and 4 x 4 (one check per translation class, weighted by its size; both checks are the same under
              translation), for the 8 harmonies: survival (the lighter encoding) and class-level survival (one class per copy, the
              stitch's class triples at stitch cells, flip-blind class triples at parity cells, by support clauses); B1's lifting
              obstructions are the placements that survive at class level only; also B2's isolated parity cells among survivors;
  scale       the frozen Bernoulli samples regenerated (random.Random("PARITY-SURVIVE|i|n|rho|s"), each cell parity with probability
              rho, i the census's harmony index), n = 3 to 9, rho in 1/8 .. 7/8, 100 each: survival and class-level survival, the
              missing cell (the seven-orbit harmony at 9 x 9) included.

    python3 -B ref_survive.py classlevel|scale      (writes result_classlevel.json / result_scale.jsonl)"""
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research" / "PARITY-MIX-20261112-001" / "referee-R1"))
import ref_parity as RP  # noqa: E402
import ref_parity_fast as F  # noqa: E402
import ref_gac as G  # noqa: E402

LEMMA = ROOT / "proofs" / "PARITY-SURVIVE-20261112-001A" / "PARITY-SURVIVE-20261112-001A-P001_which_survive" / "result_lemma.json"
RHOS = (0.125, 0.25, 0.5, 0.75, 0.875)


def eight():
    names = {RP.setup(h)["name"]: h for h in RP.hs()}
    lem = json.loads(LEMMA.read_text())["checks"]["result"]["rows"]
    return [(r["i"], r["harmony"], names[r["harmony"]]) for r in lem if r["flip-blind triples"] > 0]


def survives(st, n, K):
    with Solver(name="cadical153", bootstrap_with=F.light_cnf(st, n, K)) as s:
        return s.solve()


def class_level(st, n, K, rels):
    nae, par = rels
    C = len(st["reps"])
    var = lambda x, a: x * C + a + 1
    cl = []
    for x in range(n * n):
        cl.append([var(x, a) for a in range(C)])
        for a in range(C):
            for b in range(a + 1, C):
                cl.append([-var(x, a), -var(x, b)])
    v = lambda r, c: (r % n) * n + (c % n)
    for r in range(n):
        for c in range(n):
            x, y, z = v(r, c), v(r, c + 1), v(r + 1, c)
            allowed = par if r * n + c in K else nae
            sup = {}
            for a, b, d in allowed:
                sup.setdefault((a, b), []).append(d)
            for a in range(C):
                for b in range(C):
                    cl.append([-var(x, a), -var(y, b)] + [var(z, d) for d in sup.get((a, b), [])])
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        return s.solve()


def isolated(n, K):
    v = lambda r, c: (r % n) * n + (c % n)
    knot = {r * n + c: {v(r, c), v(r, c + 1), v(r + 1, c)} for r in range(n) for c in range(n)}
    return any(not any(d in K for d in knot if d != c and knot[d] & knot[c]) for c in K)


def classlevel_job(arg):
    i, name, h = arg
    st = RP.setup(h)
    rels = G.class_relations(st)
    out = {"i": i, "harmony": name}
    for n in (3, 4):
        t = {"placements": 0, "survive": 0, "class level": 0, "class level only": 0, "state but not class level": 0,
             "mixed survivors with an isolated parity cell": 0, "examples of class level only": []}
        for orb in RP.classes(n, n):
            K, w = orb[0], len(orb)
            s = survives(st, n, K)
            c = class_level(st, n, K, rels)
            t["placements"] += w
            t["survive"] += w * s
            t["class level"] += w * c
            t["class level only"] += w * (c and not s)
            t["state but not class level"] += w * (s and not c)
            if s and 0 < len(K) < n * n and isolated(n, K):
                t["mixed survivors with an isolated parity cell"] += w
            if c and not s and len(t["examples of class level only"]) < 5:
                t["examples of class level only"].append(sorted(K))
        out[f"{n} x {n}"] = t
    return out


def scale_job(arg):
    i, name, h, n = arg
    st = RP.setup(h)
    rels = G.class_relations(st)
    rows = []
    for rho in RHOS:
        for s in range(100):
            rng = random.Random("PARITY-SURVIVE|%d|%d|%s|%d" % (i, n, rho, s))
            K = frozenset(c for c in range(n * n) if rng.random() < rho)
            sv = survives(st, n, K)
            rows.append({"rho": rho, "sample": s, "k": len(K), "state": sv, "class level": class_level(st, n, K, rels),
                         "isolated parity cell": isolated(n, K) if sv else None, **({"cells": sorted(K)} if sv and 0 < len(K) < n * n else {})})
    return {"i": i, "harmony": name, "n": n, "rows": rows}


def main():
    part = sys.argv[1]
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    t0 = time.time()
    H = eight()
    if part == "classlevel":
        with Pool(workers) as pool:
            res = pool.map(classlevel_job, H, chunksize=1)
        tot = {}
        for r in res:
            for n in ("3 x 3", "4 x 4"):
                for k, v in r[n].items():
                    if isinstance(v, int):
                        tot[k] = tot.get(k, 0) + v
        (HERE / "result_classlevel.json").write_text(json.dumps({"totals over 3 x 3 and 4 x 4": tot, "rows": res}, indent=1) + "\n")
        print(json.dumps(tot, indent=1), round(time.time() - t0), "s")
        return
    path = HERE / "result_scale.jsonl"
    done = set()
    if path.exists():
        done = {(json.loads(l)["i"], json.loads(l)["n"]) for l in path.read_text().splitlines()}
    args = [(i, name, h, n) for n in range(9, 2, -1) for i, name, h in H if (i, n) not in done]
    with Pool(workers) as pool:
        for res in pool.imap_unordered(scale_job, args):
            with open(path, "a") as fh:
                fh.write(json.dumps(res) + "\n")
            print(res["harmony"][:30], res["n"], sum(r["state"] and 0 < r["k"] < res["n"] ** 2 for r in res["rows"]), round(time.time() - t0), "s", flush=True)
    print("done", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
