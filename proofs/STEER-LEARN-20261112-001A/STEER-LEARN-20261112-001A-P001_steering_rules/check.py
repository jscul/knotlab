#!/usr/bin/env python3
"""Checks for STEER-LEARN-20261112-001A (research/STEER-LEARN-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part harness|runs|summary [--write]
PYTHONHASHSEED=0. harness: for settings F and GE on one copy of (2, 0, 4), the laws at rest, the exact chance per blind draw of the count
(XOR, 01101001) and of the swap target g (the map other than XOR and its negation whose chance is closest to XOR's, ties by sorted order),
and the blind medians. runs: rules B, P, M and A, both settings, targets XOR and g, 100 seeds each (11000 + k), to the first stop, budget
2,000,000 steps, 5 minutes per run; each run written to runs.jsonl as it finishes. summary: the marks."""
import hashlib
import json
import math
import os
import signal
import statistics
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "proofs/SEARCH-AUDIT-20261112-001A/SEARCH-AUDIT-20261112-001A-P001_learning_against_blind_search"))
T0 = time.time()
DEPS = [str((HERE / "steer_lib.py").relative_to(ROOT)), "research/STEER-LEARN-20261112-001/preregistration.md",
        "proofs/SEARCH-AUDIT-20261112-001A/SEARCH-AUDIT-20261112-001A-P001_learning_against_blind_search/audit.py"]
XOR = "01101001"
RULES, SETTINGS, SEEDS, CAP = ("B", "P", "M", "A"), ("F", "GE"), 100, 300


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def rest_maps(setting):
    """the map at the interface of every law (F: class) at rest, one signing each"""
    import steer_lib as S
    B = S.J.Joined(1)
    K0 = B.copies[0]
    pt = [list(t) for t in B.pt]
    _, seqs = S.N.shortest_sequences(pt)
    out = []
    for law in S.UL.laws(B):
        if setting == "F":
            if K0.even_faces(law):
                continue
        else:
            sums = {sum(law[3 * k + pt[k].index(d)] for (k, d) in sq) % 2 for sq in seqs}
            if len(sums) != 1:
                continue
        from pysat.solvers import Solver
        with Solver(name="cadical153", bootstrap_with=B.clauses(law)) as so:
            if not so.solve():
                continue
        out.append((law, S.F.read_map_k(B, law, B.ports)))
    return out


def harness():
    import audit as A
    out = {}
    for setting in SETTINGS:
        maps = rest_maps(setting)
        cands = set()
        for _, m in maps:
            for t in _orbit(m):
                cands.add(t)
        p = {t: sum(A.flips_share(m, t) for _, m in maps) / len(maps) for t in sorted(cands)}
        pxor = p[XOR]
        others = [t for t in sorted(cands) if t not in (XOR, "10010110") and "x" not in t]
        g = min(others, key=lambda t: (abs(p[t] - pxor), t))
        out[setting] = {"laws at rest": len(maps), "p(XOR)": pxor, "blind median XOR": A.blind(pxor)[0], "g": g, "p(g)": p[g],
                        "blind median g": A.blind(p[g])[0]}
    return out


def _orbit(m):
    import itertools
    pats = list(itertools.product((0, 1), repeat=3))
    idx = {x: i for i, x in enumerate(pats)}
    sw = {"0": "1", "1": "0", "u": "u", "x": "x"}
    out = set()
    for f in itertools.product((0, 1), repeat=3):
        for o in (0, 1):
            out.add("".join((sw if o else {c: c for c in "01ux"})[m[idx[tuple(a ^ b for a, b in zip(x, f))]]] for x in pats))
    return out


def job(args):
    import steer_lib as S
    setting, rule, target, seed, xor_set = args
    xor_law = None
    if xor_set:
        B = S.J.Joined(1)
        xor_law = lambda s: S.F.read_map_k(B, s, B.ports) == XOR
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(CAP)
    t = time.time()
    try:
        r = S.run(setting, rule, target, seed, xor_law=xor_law)
        signal.alarm(0)
    except Timeout:
        r = {"setting": setting, "rule": rule, "target": target, "seed": seed, "found": False, "dropped (time cap)": True}
    r["seconds"] = round(time.time() - t, 1)
    return r


def runs(write):
    h = json.loads((HERE / "result_harness.json").read_text())["checks"]["result"]
    jobs = []
    for setting in SETTINGS:
        for rule in RULES:
            for target in (XOR, h[setting]["g"]):
                for k in range(SEEDS):
                    jobs.append((setting, rule, target, 11000 + k, target != XOR))
    path = HERE / "runs.jsonl"
    if write:
        path.write_text("")
    n = 0
    with Pool(20) as pool:
        for r in pool.imap_unordered(job, jobs):
            n += 1
            if write:
                with path.open("a") as f:
                    f.write(json.dumps(r) + "\n")
    return {"runs": n}


def mark(charged, n, bmed):
    pr = sorted(charged) + [math.inf] * (n - len(charged))
    med = statistics.median(pr)
    within = sum(x <= bmed for x in pr) / n
    return med, within, (med <= bmed / 2 and within >= 0.75)


def summary():
    h = json.loads((HERE / "result_harness.json").read_text())["checks"]["result"]
    rows = [json.loads(l) for l in (HERE / "runs.jsonl").read_text().splitlines() if l.strip()]
    out = {}
    for setting in SETTINGS:
        for rule in RULES:
            for target, bkey in ((XOR, "blind median XOR"), (h[setting]["g"], "blind median g")):
                rr = [r for r in rows if r["setting"] == setting and r["rule"] == rule and r["target"] == target]
                found = [r for r in rr if r.get("found")]
                bmed = h[setting][bkey]
                med_c, within_c, ok_c = mark([r["charged probes"] for r in found], len(rr), bmed)
                med_w, within_w, ok_w = mark([r["world probes"] for r in found], len(rr), bmed)
                key = "%s / %s / %s" % (setting, rule, "XOR" if target == XOR else "g = " + target)
                out[key] = {"runs": len(rr), "found": len(found), "blind median": bmed,
                            "median charged probes": med_c, "share within the blind median (charged)": round(within_c, 3), "passes (charged)": ok_c,
                            "median world probes": med_w, "share within the blind median (world)": round(within_w, 3),
                            "median candidate checks": statistics.median([r["candidate checks"] for r in found]) if found else None,
                            "XOR seen before the stop (swap runs)": sum(1 for r in rr if r.get("xor seen at probe")) if target != XOR else None}
    steer = {}
    for setting in SETTINGS:
        for rule in RULES:
            a = out["%s / %s / XOR" % (setting, rule)]["passes (charged)"]
            b = out["%s / %s / g = %s" % (setting, rule, h[setting]["g"])]["passes (charged)"]
            steer["%s / %s" % (setting, rule)] = {"XOR": a, "g": b, "steering shown": a and b}
    out["S: steering shown (passes on XOR and on g, charged)"] = steer
    out["any rule steers"] = any(v["steering shown"] for v in steer.values())
    return out


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    part = sys.argv[sys.argv.index("--part") + 1]
    write = "--write" in sys.argv
    res = {"harness": harness, "summary": summary}.get(part, lambda: runs(write))()
    res = json.loads(json.dumps(res, default=str))
    out = {"dependencies": {p: sha(p) for p in DEPS}, "result": res, "seconds": round(time.time() - T0, 1)}
    if write:
        (HERE / ("result_%s.json" % part)).write_text(json.dumps({"status": "passed", "checks": out}, indent=1) + "\n")
    print(json.dumps(res, indent=1)[:5000])


if __name__ == "__main__":
    main()
