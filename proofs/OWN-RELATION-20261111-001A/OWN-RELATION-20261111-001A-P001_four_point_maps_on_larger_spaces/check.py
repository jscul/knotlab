#!/usr/bin/env python3
"""Checks for OWN-RELATION-20261111-001A (research/OWN-RELATION-20261111-001/preregistration.md).

    PYTHONPATH=tools .venv/bin/python3 -B check.py --part control|census|export|summary|referee [--write]
PYTHONHASHSEED=0. control: the positive control (synthetic floor states realising each of A, B, C, D). census: random knot spaces of
n = 16, 18, 20 points steered to genus 2, 3, 4, seeds 0 to 99 for each (n, genus), every class; each space capped at 1,200 s, the part
at 3 hours by its systemd unit. export: the referee's sample (every tenth space read, by label) and every space with a C or D instance,
rebuilt as plain data. summary: P1, P2, the controls and the failure criterion. referee: own_referee.py (fresh code)."""
import hashlib
import json
import os
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("own_lib.py", "own_referee.py")] + \
       ["proofs/PARITY-NEEDS-20261111-001A/PARITY-NEEDS-20261111-001A-P001_the_parity_gadget_refereed/needs_lib.py",
        "proofs/UNATE-20261111-001A/UNATE-20261111-001A-P001_are_maps_of_held_points_unate/unate_lib.py",
        "research/OWN-RELATION-20261111-001/preregistration.md"]
JOBS = [(n, g, s) for n in (16, 18, 20) for g in (2, 3, 4) for s in range(100)]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def label(n, g, s):
    return "steered n=%d g=%d seed=%d" % (n, g, s)


def build(job):
    import own_lib as O
    n, g, s = job
    built = O.N.steered(n, g, s)
    if built is None:
        return None, "unreached"
    S, K = built
    if not (S.connected() and K.simple()):
        return None, "skipped"
    assert (2 - K.chi) // 2 == g
    return K, None


def census_job(job):
    import own_lib as O
    n, g, s = job
    K, why = build(job)
    if K is None:
        return {"label": label(n, g, s), "n": n, "genus": g, why: True}
    t = time.time()
    r = O.read_space(K)
    row = {"label": label(n, g, s), "n": n, "genus": g, "faces": K.V, "dropped": r is None, "seconds": round(time.time() - t, 1)}
    if r is not None:
        row["tally"], row["first"] = dict(r[0]), r[1]
    return row


def export_job(job):
    import own_lib as O
    K, why = build(job)
    return O.export(K, label(*job))


def read_rows():
    return json.loads((HERE / "result_census.json").read_text())["checks"]["result"]["rows"]


def run_part(part):
    import own_lib as O
    if part == "control":
        return O.positive_control()
    if part == "census":
        order = sorted(JOBS, key=lambda j: (-j[0] * j[1], j))   # largest first, so the long jobs do not trail
        with Pool(20) as pool:
            rows = pool.map(census_job, order, chunksize=1)
        return {"rows": sorted(rows, key=lambda r: (r["n"], r["genus"], r["label"]))}
    if part == "export":
        rows = [r for r in read_rows() if "tally" in r]
        labels = sorted(r["label"] for r in rows)
        pick = set(labels[::10]) | {r["label"] for r in rows if any(r["tally"].get(k) for k in "CD")}
        jobs = [(r["n"], r["genus"], int(r["label"].split("seed=")[1])) for r in rows if r["label"] in pick]
        with Pool(20) as pool:
            sp = pool.map(export_job, jobs, chunksize=1)
        (HERE / "spaces.json").write_text(json.dumps({"spaces": sp}) + "\n")
        return {"spaces": len(sp), "sha256": hashlib.sha256((HERE / "spaces.json").read_bytes()).hexdigest()}
    if part == "referee":
        out = subprocess.run([sys.executable, "-B", str(HERE / "own_referee.py")], capture_output=True, text=True)
        print(out.stdout, out.stderr)
        return json.loads((HERE / "referee.json").read_text())


def summary():
    rows = read_rows()
    read = [r for r in rows if "tally" in r]
    reached = [r for r in rows if not r.get("unreached") and not r.get("skipped")]
    dropped = [r["label"] for r in rows if r.get("dropped")]
    tot = {k: sum(r["tally"].get(k, 0) for r in read) for k in ("A", "B", "C", "D", "1 inputs", "3 inputs", "free four-point sets")}
    by = {}
    for r in read:
        key = "n=%d g=%d" % (r["n"], r["genus"])
        b = by.setdefault(key, {"spaces": 0, "A": 0, "B": 0, "C": 0, "D": 0, "spaces with B": 0})
        b["spaces"] += 1
        for k in "ABCD":
            b[k] += r["tally"].get(k, 0)
        b["spaces with B"] += bool(r["tally"].get("B"))
    hits = sorted((r for r in read if any(r["tally"].get(k) for k in "CD")), key=lambda r: (r["n"], r["genus"], r["label"]))
    b_per = {n: by.get("n=%d g=3" % n, {}).get("B", 0) / max(1, by.get("n=%d g=3" % n, {}).get("spaces", 0)) for n in (16, 18, 20)}
    control = json.loads((HERE / "result_control.json").read_text())["checks"]["result"]
    return {
        "jobs": len(rows), "reached": len(reached), "read": len(read), "dropped": dropped,
        "inconclusive (more than 10% of reached spaces dropped)": len(dropped) > 0.1 * max(1, len(reached)),
        "positive control passed": all(v["ok"] for v in control.values()),
        "totals": tot, "by size and genus": by,
        "P1 neither C nor D occurs": not hits,
        "instances of C or D": [{"label": r["label"], "first": {k: r["first"][k] for k in "CD" if k in r["first"]}} for r in hits],
        "P2 B per space at genus 3 grows with n (16 < 18 < 20)": b_per[16] < b_per[18] < b_per[20], "B per space at genus 3": b_per,
    }


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
