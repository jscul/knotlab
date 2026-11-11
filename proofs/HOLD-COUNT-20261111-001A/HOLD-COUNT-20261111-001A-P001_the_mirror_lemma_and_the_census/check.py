#!/usr/bin/env python3
"""Checks for HOLD-COUNT-20261111-001A (research/HOLD-COUNT-20261111-001/preregistration.md).

    PYTHONPATH=tools .venv/bin/python3 -B check.py --part export|tori|steered|summary|referee [--write]
PYTHONHASHSEED=0. export: every space of the census as plain data (spaces.json) for the referee. tori: every simple lattice torus up to
20 points, every class. steered: the random knot spaces of n = 8, 10, 12, 14 points steered to genus 1, 2, 3, seeds 0 to 99 for each
(PARITY-NEEDS-20261111-001's). Each space has a 300-second cap and each part runs as its own process with a 30-minute wall-clock cap (the
systemd unit); a space or part over its cap is dropped by rule. summary: P0 to P3, the controls and the least space for each count.
referee: hold_referee.py (fresh code) on spaces.json and result.json."""
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
NEEDS = ROOT / "proofs/PARITY-NEEDS-20261111-001A/PARITY-NEEDS-20261111-001A-P001_the_parity_gadget_refereed"
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("hold_lib.py", "hold_referee.py")] + \
       [str((NEEDS / "needs_lib.py").relative_to(ROOT)),
        "proofs/UNATE-20261111-001A/UNATE-20261111-001A-P001_are_maps_of_held_points_unate/unate_lib.py",
        "research/HOLD-COUNT-20261111-001/preregistration.md"]
KINDS = ("parity, no reference", "majority, no reference", "full adder, no reference", "mod 3, no reference", "mod 4, no reference",
         "parity, one reference", "mod 3, one reference", "mod 4, one reference")
STEERED = [(n, g, s) for n in (8, 10, 12, 14) for g in (1, 2, 3) for s in range(100)]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def torus_label(t):
    return "torus %s" % (tuple(t),)


def steered_label(n, g, s):
    return "steered n=%d g=%d seed=%d" % (n, g, s)


def build(job):
    import hold_lib as H
    if job[0] == "torus":
        t = job[1]
        K = H.SL.KnotSpace(H.SL.torus(*t))
        return torus_label(t), K, 1
    n, g, seed = job[1]
    built = H.N.steered(n, g, seed)
    if built is None:
        return steered_label(n, g, seed), None, "unreached"
    S, K = built
    if not (S.connected() and K.simple()):
        return steered_label(n, g, seed), None, "skipped"
    assert (2 - K.chi) // 2 == g
    return steered_label(n, g, seed), K, g


def jobs(part):
    import hold_lib as H
    if part == "tori":
        return [("torus", t) for t, N in H.N.tori()]
    return [("steered", j) for j in STEERED]


def read_job(job):
    import hold_lib as H
    label, K, g = build(job)
    if K is None:
        return {"label": label, g: True}
    r = H.read_space(K)
    row = {"label": label, "points": K.n, "genus": g, "faces": K.V, "dropped": r is None}
    if r is not None:
        tally, first, sizes = r
        row.update({"tally": dict(tally), "first": first, "floor states per class": sizes})
    return row


def export_job(job):
    import hold_lib as H
    label, K, g = build(job)
    return None if K is None else H.export(K, label)


def run_part(part):
    if part == "export":
        with Pool(20) as pool:
            sp = [s for s in pool.map(export_job, jobs("tori") + jobs("steered"), chunksize=4) if s]
        (HERE / "spaces.json").write_text(json.dumps({"spaces": sp}) + "\n")
        return {"spaces": len(sp), "sha256": hashlib.sha256((HERE / "spaces.json").read_bytes()).hexdigest()}
    if part == "referee":
        out = subprocess.run([sys.executable, "-B", str(HERE / "hold_referee.py")], capture_output=True, text=True)
        print(out.stdout, out.stderr)
        return json.loads((HERE / "referee.json").read_text())
    with Pool(20) as pool:
        rows = pool.map(read_job, jobs(part), chunksize=1)
    return {"rows": rows}


def needs_kinds():
    """PARITY-NEEDS-20261111-001's interface counts per space, for control C1"""
    out = {}
    for part in ("tori", "steered"):
        for r in json.loads((NEEDS / ("result_%s.json" % part)).read_text())["checks"]["result"]["rows"]:
            if not r.get("kinds"):
                continue
            lab = torus_label(r["torus"]) if part == "tori" else steered_label(r["n"], r["genus"], r["seed"])
            out[lab] = (r["kinds"].get("total parity", 0), r["kinds"].get("total majority", 0))
    return out


def summary():
    parts = {}
    for part in ("tori", "steered"):
        p = HERE / ("result_%s.json" % part)
        parts[part] = json.loads(p.read_text())["checks"]["result"] if p.exists() else {"dropped by its cap": True}
    rows = [r for part in ("tori", "steered") for r in parts[part].get("rows", [])]
    read = [r for r in rows if "tally" in r]
    flags = Counter(f for r in rows for f in ("unreached", "skipped", "dropped") if r.get(f))
    totals = {k: sum(r["tally"].get(k, 0) for r in read) for k in KINDS}
    spaces_with = {k: sum(1 for r in read if r["tally"].get(k, 0)) for k in KINDS}
    least = {}
    for k in KINDS:
        hits = [r for r in read if r["tally"].get(k, 0)]
        if not hits:
            least[k] = None
            continue
        best = min(hits, key=lambda r: (r["points"], r["genus"], r["faces"], r["label"]))
        least[k] = {"label": best["label"], "points": best["points"], "genus": best["genus"], "faces": best["faces"],
                    "spaces at that size": sorted(r["label"] for r in hits if r["points"] == best["points"]),
                    "first instance": best["first"][k]}
    nk = needs_kinds()
    c1 = [r["label"] for r in read if r["label"] in nk and
          nk[r["label"]] != (r["tally"].get("total parity interfaces (control)", 0), r["tally"].get("total majority interfaces (control)", 0))]
    c1_missing = sorted(set(nk) ^ {r["label"] for r in read})
    c2 = [r["label"] for r in read if r["tally"].get("mod 4, no reference", 0) != r["tally"].get("full adder, no reference", 0)]
    labels = [least[k]["label"] if least[k] else None for k in ("parity, no reference", "full adder, no reference", "mod 3, one reference")]
    return {
        "spaces read": len(read), "unreached, skipped, dropped": dict(flags),
        "parts dropped by cap": [p for p in parts if parts[p].get("dropped by its cap")],
        "instances (triples, or triples and references)": totals, "spaces with an instance": spaces_with, "least": least,
        "P0 no count mod 3 without a reference (proved)": totals["mod 3, no reference"] == 0,
        "P1 a full adder without a reference": totals["full adder, no reference"] > 0,
        "P2 a count mod 3 with one reference": totals["mod 3, one reference"] > 0,
        "P3 least space for P2 larger than 8 points": (least["mod 3, one reference"]["points"] > 8) if least["mod 3, one reference"] else None,
        "measure informative (not all three least spaces the same)": None if None in labels else len(set(labels)) > 1,
        "C1 interface counts equal PARITY-NEEDS's (mismatches, spaces read by only one)": {"mismatch": c1, "only one": c1_missing},
        "C2 mod 4 without a reference equals the full adder (mismatches)": c2,
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
