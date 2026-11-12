#!/usr/bin/env python3
"""Checks for LINE-LOCK-20261112-001A (research/LINE-LOCK-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part census|summary [--write]
census: every orbit of the 66 harmonies of span <= 8 (every period) and the 7 odd step sets: increments, cyclic subgroups and cosets
inside them (classified at each odd prime), F4 blocks, free pairs, genuine cosets a lag can give; per harmony, a free site on the
integers. summary: the frozen items. Referee: the background referee thread (referee pending)."""
import hashlib
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("line_lib.py", "check.py")] + \
       ["proofs/BASES-WITHIN-20261112-001A/BASES-WITHIN-20261112-001A-P001_inner_series/nest_lib.py",
        "proofs/ODD-FAMILY-20261112-001A/ODD-FAMILY-20261112-001A-P001_symmetric_steps/fam_lib.py",
        "research/LINE-LOCK-20261112-001/preregistration.md"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def job(h):
    import line_lib as L
    t = time.time()
    orbs = L.summarise(h)
    return {"harmony": h["name"], "source": h["source"], "P": h["P"], "states": len(h["states"]), "kinds": len(h["kinds"]),
            "free site": L.free_site(h), "orbits": orbs, "seconds": round(time.time() - t, 1)}


def run_part(part):
    import line_lib as L
    hs = L.census_harmonies() + L.odd_harmonies()
    hs.sort(key=lambda h: -h["P"])
    with Pool(8) as pool:
        rows = pool.map(job, hs, chunksize=1)
    return {"rows": sorted(rows, key=lambda r: (r["P"], r["harmony"]))}


def summary():
    rows = json.loads((HERE / "result_census.json").read_text())["checks"]["result"]["rows"]
    orbs = [(r["harmony"], o) for r in rows for o in r["orbits"]]
    return {
        "harmonies": len(rows), "orbits": len(orbs),
        "premise: harmonies with a free site": [r["harmony"] for r in rows if r["free site"]],
        "theorem: genuine subgroups found": [[h, o["orbit period"], g] for h, o in orbs for g in o["genuine subgroups"]],
        "theorem: F4 blocks found": [[h, o["orbit period"], o["F4 blocks"]] for h, o in orbs if o["F4 blocks"]],
        "theorem: free pairs found": [[h, o["orbit period"], o["free pairs"]] for h, o in orbs if o["free pairs"]],
        "cyclic subgroups inside (all degenerate)": sum(o["cyclic subgroups inside"] for _, o in orbs),
        "cosets inside": sum(o["cosets inside"] for _, o in orbs),
        "genuine cosets": [[h, o["orbit period"], c] for h, o in orbs for c in o["genuine cosets"]],
        "genuine cosets a lag can give": [[h, o["orbit period"], c] for h, o in orbs for c in o["genuine cosets a lag can give"]],
        "orbits whose period has an odd prime factor": sum(1 for _, o in orbs if any(o["orbit period"] % q == 0 for q in range(3, o["orbit period"] + 1, 2))),
    }


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    part = sys.argv[sys.argv.index("--part") + 1]
    res = summary() if part == "summary" else run_part(part)
    res = {"dependencies": {p: sha(p) for p in DEPS}, "result": res, "seconds": round(time.time() - T0, 1)}
    path = HERE / ("result_%s.json" % part if part != "summary" else "result.json")
    if "--write" in sys.argv:
        path.write_text(json.dumps({"status": "passed", "checks": res}, indent=1, default=str) + "\n")
        print("wrote", path, round(time.time() - T0, 1), "s")


if __name__ == "__main__":
    main()
