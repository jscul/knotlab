#!/usr/bin/env python3
"""Checks for PARITY-NEEDS-20261111-001A (research/PARITY-NEEDS-20261111-001/preregistration.md).

    PYTHONPATH=tools .venv/bin/python3 -B check.py --part referee|tori|steered|summary [--write]
PYTHONHASHSEED=0. referee: referee.py's independent check of the 8-point gadget (fresh code, canonical K1-K3). tori: every simple
lattice torus up to 20 points, every class and interface. steered: random knot spaces of n = 8, 10, 12, 14 points steered to genus 1,
2, 3, seeds 0 to 99 for each (n, genus). Each space has a 300-second cap (dropped by rule if over); each part runs as its own process
with a wall-clock cap set by the systemd unit (tori 30 minutes, steered 60 minutes), and a part over its cap is dropped by rule.
summary: the least genus with a non-unate map, the smallest such space at it, and its face count."""
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("needs_lib.py", "referee.py", "gadget.json")] + \
       ["proofs/UNATE-20261111-001A/UNATE-20261111-001A-P001_are_maps_of_held_points_unate/unate_lib.py",
        "research/PARITY-NEEDS-20261111-001/preregistration.md"]
NONUNATE = ("total parity", "partial, non-unate", "total other")


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def torus_job(job):
    import needs_lib as L
    t, N = job
    K = L.SL.KnotSpace(L.SL.torus(*t))
    r = L.read_space(K)
    return {"torus": t, "points": N, "genus": 1, "faces": K.V, "dropped": r is None,
            "kinds": dict(r[0]) if r else None, "first": r[1] if r else None}


def steered_job(job):
    import needs_lib as L
    n, g, seed = job
    built = L.steered(n, g, seed)
    if built is None:
        return {"n": n, "genus": g, "seed": seed, "unreached": True}
    S, K = built
    if not (S.connected() and K.simple()):
        return {"n": n, "genus": g, "seed": seed, "skipped": True}
    assert (2 - K.chi) // 2 == g
    r = L.read_space(K)
    return {"n": n, "genus": g, "seed": seed, "faces": K.V, "dropped": r is None,
            "kinds": dict(r[0]) if r else None, "first": r[1] if r else None}


def run_part(part):
    import needs_lib as L
    if part == "referee":
        out = subprocess.run([sys.executable, "-B", str(HERE / "referee.py")], capture_output=True, text=True,
                             env={**os.environ, "PYTHONPATH": str(ROOT / "tools")})
        return json.loads((HERE / "referee.json").read_text())
    jobs = [(t, N) for t, N in L.tori()] if part == "tori" else [(n, g, s) for n in (8, 10, 12, 14) for g in (1, 2, 3) for s in range(100)]
    with Pool(22) as pool:
        rows = pool.map(torus_job if part == "tori" else steered_job, jobs, chunksize=1)
    return {"rows": rows}


def summary():
    out = {}
    for part in ("referee", "tori", "steered"):
        p = HERE / ("result_%s.json" % part)
        out[part] = json.loads(p.read_text()) if p.exists() else {"dropped by its cap": True}
    rows = [r for part in ("tori", "steered") for r in out[part].get("rows", [])]
    tally = {}
    for r in rows:
        key = "genus %d" % r["genus"]
        t = tally.setdefault(key, Counter())
        t["spaces"] += 1
        for flag in ("unreached", "skipped", "dropped"):
            t[flag] += bool(r.get(flag))
        for k, v in (r.get("kinds") or {}).items():
            t[k] += v
    hits = [r for r in rows if r.get("first") and any(k in r["first"] for k in NONUNATE)]
    least = min((r["genus"] for r in hits), default=None)
    smallest = min((r for r in hits if r["genus"] == least), key=lambda r: (r.get("points", r.get("n")), r.get("seed", 0)), default=None)
    return {"referee passed": out["referee"].get("passed"), "by genus": {k: dict(v) for k, v in sorted(tally.items())},
            "parts dropped by cap": [p for p in ("tori", "steered") if out[p].get("dropped by its cap")],
            "least genus with a non-unate map (searched range)": least, "smallest instance there": smallest,
            "non-unate instances": len(hits)}


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    part = sys.argv[sys.argv.index("--part") + 1]
    write = "--write" in sys.argv
    res = summary() if part == "summary" else run_part(part)
    res = {"dependencies": {p: sha(p) for p in DEPS}, "result": res, "seconds": round(time.time() - T0, 1)}
    path = HERE / ("result_%s.json" % part if part != "summary" else "result.json")
    if write:
        path.write_text(json.dumps({"status": "passed", "checks": res}, indent=1, default=str) + "\n")
        print("wrote", path, round(time.time() - T0, 1), "s")
    else:
        old = json.loads(path.read_text())["checks"]
        same = json.dumps(old["result"], sort_keys=True, default=str) == json.dumps(json.loads(json.dumps(res["result"], default=str)), sort_keys=True)
        print("result reproduced" if same else "result differs")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
