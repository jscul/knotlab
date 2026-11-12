#!/usr/bin/env python3
"""The census for WHICH-SEQUENCES-20261112-001A (research/WHICH-SEQUENCES-20261112-001/preregistration.md).

    .venv/bin/python3 -B census.py [--write]
PYTHONHASHSEED=0. Bases: one copy of (2, 0, 4) (J1) and the first 12 hits of census_lib.collect_bases. For each base, every law's sums on
every cyclic sequence of two or three knots and whether it counts three at the base's interface. (1) The 16 rules by length (for
sequences of two knots and of three: free, all 0, all 1, all equal): laws at rest, counting among them, enrichment. (2) The null: 1,000
times, each base's counting laws replaced by as many satisfiable laws drawn at random (seed 0), the same rules applied. (3) The base's
symmetries and their orbits on the sequences: the share of counting laws whose sums are constant on every orbit, against the share of all
satisfiable laws."""
import hashlib
import json
import os
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
DEPS = [str((HERE / "census_lib.py").relative_to(ROOT)), "research/WHICH-SEQUENCES-20261112-001/preregistration.md"]
NULL = 1000


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def base_job(item):
    import census_lib as L
    if item == "J1":
        B = L.J.Joined(1)
        name, T = "J1, one copy of (2, 0, 4)", B.ports
    else:
        name, B, T = L.base_of(item)
    rows, counts, seqs = L.law_table(B, list(T))
    pt = [list(t) for t in B.pt]
    syms = L.symmetries(pt, B.real)
    orb = L.orbits(seqs, syms)
    norb = max(orb) + 1 if orb else 0
    cols_by_orbit = [[i for i, o in enumerate(orb) if o == c] for c in range(norb)]

    def orbit_uniform(r):
        return all(len({int(r[i]) for i in cols}) == 1 for cols in cols_by_orbit)
    uni = np.array([orbit_uniform(r) for r in rows])
    rules = {}
    for rule in L.length_rules():
        mask = L.apply_length_rule(rows, seqs, rule)
        rules[" / ".join(rule)] = (int(mask.sum()), int((mask & counts).sum()))
    return {"base": name, "distinctions": B.real, "knots": len(pt), "interface": list(T), "satisfiable laws": int(len(rows)),
            "counting laws": int(counts.sum()), "sequences of two knots": sum(n == 2 for _, n in seqs),
            "sequences of three knots": sum(n == 3 for _, n in seqs), "symmetries": len(syms), "orbits": norb,
            "rules (laws at rest, counting)": rules,
            "share orbit-uniform: counting laws": round(float(uni[counts].mean()), 4) if counts.any() else None,
            "share orbit-uniform: all satisfiable laws": round(float(uni.mean()), 4),
            "_rows": rows, "_counts": counts, "_seqs": [n for _, n in seqs]}


def passes(R, c, R_all, c_all):
    return c >= 1 and R > 0 and (c / R) > (c_all / R_all)


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    import census_lib as L
    with Pool(13) as pool:
        hits = L.collect_bases(pool=pool)
        bases = pool.map(base_job, ["J1"] + hits)
    rule_names = [" / ".join(r) for r in L.length_rules()]
    table, passing = {}, []
    for name in rule_names:
        row = {}
        ok = True
        for b in bases:
            R, c = b["rules (laws at rest, counting)"][name]
            p = passes(R, c, b["satisfiable laws"], b["counting laws"])
            row[b["base"]] = {"laws at rest": R, "counting": c, "expected draws": None if c == 0 else round(R / c, 1),
                              "enrichment": None if R == 0 else round((c / R) / (b["counting laws"] / b["satisfiable laws"]), 3), "passes": p}
            ok &= p
        table[name] = {"passes on every base": ok and name != "free / free", "per base": row}
        if ok and name != "free / free":
            passing.append(name)
    rng = random.Random(0)
    null_hits = 0
    for _ in range(NULL):
        any_rule = False
        fakes = []
        for b in bases:
            n, c = len(b["_rows"]), b["counting laws"]
            idx = rng.sample(range(n), c)
            m = np.zeros(n, dtype=bool)
            m[idx] = True
            fakes.append(m)
        for rule in L.length_rules():
            if rule == ("free", "free"):
                continue
            ok = True
            for b, fake in zip(bases, fakes):
                seqs = [(None, n) for n in b["_seqs"]]
                mask = L.apply_length_rule(b["_rows"], seqs, rule)
                if not passes(int(mask.sum()), int((mask & fake).sum()), len(b["_rows"]), b["counting laws"]):
                    ok = False
                    break
            if ok:
                any_rule = True
                break
        null_hits += any_rule
    out = {"bases": [{k: v for k, v in b.items() if not k.startswith("_") and k != "rules (laws at rest, counting)"} for b in bases],
           "rules by length": table, "rules passing on every base": passing,
           "null: share of 1,000 draws where some rule passes on every base": null_hits / NULL,
           "R1: a native length rule enriches counting on every base beyond chance": bool(passing) and null_hits / NULL < 0.05,
           "seconds": round(time.time() - T0, 1), "dependencies": {p: sha(p) for p in DEPS}}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps({"status": "passed", "checks": {"result": out}}, indent=1, default=str) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k not in ("rules by length",)}, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
