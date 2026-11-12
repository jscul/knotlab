#!/usr/bin/env python3
"""Checks for CLAMP-LEARN-20261112-001A (research/CLAMP-LEARN-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part baselines|walk|runs|summary [--write]
PYTHONHASHSEED=0. baselines: on one copy of (2, 0, 4), settings F and GE, targets the count (01101001) and STEER-LEARN's swap target g
(F 0uu01uu1, GE 00001111): the chance per uniform draw among signings at rest, and among those consistent with every positive example
(each example's output allowed); the sturdier probe's walk steps on every law at rest (GE: all 64, once per target). walk: the unchanged
learner taught an impossible map, the map of its law at each of 60 probes, 20 seeds (13000 + k), from the fixed start and from random
starts, both settings. runs: GE, random starts, rules B (unchanged), C (clamped) and CA (contrastive), targets the count and g, 100 seeds
(12000 + k), budget 2,000,000 learning steps, 5 minutes per run, written as each finishes. summary: the marks."""
import hashlib
import json
import math
import os
import random
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
DEPS = [str((HERE / "clamp_lib.py").relative_to(ROOT)), "research/CLAMP-LEARN-20261112-001/preregistration.md",
        "proofs/STEER-LEARN-20261112-001A/STEER-LEARN-20261112-001A-P001_steering_rules/steer_lib.py"]
XOR = "01101001"
G = {"F": "0uu01uu1", "GE": "00001111"}
CAP = 300


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def consistent(m, target):
    return all(a == "u" or a == b for a, b in zip(m, target))


def orbit_maps(m):
    import itertools
    pats = list(itertools.product((0, 1), repeat=3))
    idx = {x: i for i, x in enumerate(pats)}
    sw = {"0": "1", "1": "0", "u": "u", "x": "x"}
    for f in itertools.product((0, 1), repeat=3):
        for o in (0, 1):
            yield "".join((sw if o else {c: c for c in "01ux"})[m[idx[tuple(a ^ b for a, b in zip(x, f))]]] for x in pats)


def cost_job(args):
    import clamp_lib as L
    setting, i, target = args
    law = L.rest_laws(setting)[i]
    return setting, i, target, L.probe_cost(setting, law, target, random.Random(7000 + i))


def baselines():
    import clamp_lib as L
    import audit as A
    out = {}
    jobs = []
    for setting in ("F", "GE"):
        laws = L.rest_laws(setting)
        maps = [L.F.read_map_k(L.J.Joined(1), law, L.J.Joined(1).ports) for law in laws]
        for tg in (XOR, G[setting]):
            draws = [list(orbit_maps(m)) for m in maps]
            pu = sum(sum(x == tg for x in d) / len(d) for d in draws) / len(laws)
            cons = [sum(consistent(x, tg) for x in d) / len(d) for d in draws]
            pr = (sum(sum(x == tg for x in d) / len(d) for d in draws) / len(laws)) / (sum(cons) / len(laws))
            out["%s / %s" % (setting, tg)] = {"laws at rest": len(laws), "p uniform": pu, "blind median uniform": A.blind(pu)[0],
                                             "share consistent with the positive examples": sum(cons) / len(laws), "p restricted": pr,
                                             "blind median restricted": A.blind(pr)[0], "laws consistent (any flip)": sum(c > 0 for c in cons)}
        jobs += [(setting, i, tg) for i in range(len(laws)) for tg in (XOR, G[setting])]
    with Pool(16) as pool:
        costs = pool.map(cost_job, jobs)
    for setting in ("F", "GE"):
        for tg in (XOR, G[setting]):
            c = [x[3] for x in costs if x[0] == setting and x[2] == tg]
            key = "%s / %s" % (setting, tg)
            out[key]["mean probe walk steps per law at rest"] = round(statistics.mean(c), 1)
            b = out[key]
            b["blind median steps uniform"] = b["blind median uniform"] * b["mean probe walk steps per law at rest"]
            b["blind median steps restricted"] = b["blind median restricted"] * b["mean probe walk steps per law at rest"]
    return out


def walk_job(args):
    import clamp_lib as L
    setting, start, seed = args
    return setting, start, seed, L.walk2(setting, seed, 60, start)


def walk():
    jobs = [(s, st, 13000 + k) for s in ("F", "GE") for st in ("fixed", "random") for k in range(20)]
    with Pool(20) as pool:
        res = pool.map(walk_job, jobs)
    out = {}
    for setting in ("F", "GE"):
        for st in ("fixed", "random"):
            maps = [m for s, a, _, ms in res if s == setting and a == st for m in ms]
            out["%s / %s start" % (setting, st)] = {"probes": len(maps), "share computing the count": sum(m == XOR for m in maps) / len(maps),
                                                    "share computing g": sum(m == G[setting] for m in maps) / len(maps),
                                                    "first probe": {"count": sum(ms[0] == XOR for s, a, _, ms in res if s == setting and a == st),
                                                                    "g": sum(ms[0] == G[setting] for s, a, _, ms in res if s == setting and a == st)}}
    return out


def run_job(args):
    import clamp_lib as L
    rule, target, seed = args
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(CAP)
    t = time.time()
    try:
        r = L.run2(rule, target, seed)
        signal.alarm(0)
    except Timeout:
        r = {"rule": rule, "target": target, "seed": seed, "found": False, "dropped (time cap)": True}
    r["seconds"] = round(time.time() - t, 1)
    return r


def runs(write):
    jobs = [(rule, tg, 12000 + k) for rule in ("B", "C", "CA") for tg in (XOR, G["GE"]) for k in range(100)]
    path = HERE / "runs.jsonl"
    if write:
        path.write_text("")
    n = 0
    with Pool(20) as pool:
        for r in pool.imap_unordered(run_job, jobs):
            n += 1
            if write:
                with path.open("a") as f:
                    f.write(json.dumps(r) + "\n")
    return {"runs": n}


def med_within(vals, n, bar):
    pr = sorted(vals) + [math.inf] * (n - len(vals))
    return statistics.median(pr), sum(x <= bar for x in pr) / n


def summary():
    base = json.loads((HERE / "result_baselines.json").read_text())["checks"]["result"]
    rows = [json.loads(l) for l in (HERE / "runs.jsonl").read_text().splitlines() if l.strip()]
    out = {}
    bmed = {}
    for tg in (XOR, G["GE"]):
        rr = [r for r in rows if r["rule"] == "B" and r["target"] == tg]
        f = [r["all steps"] for r in rr if r.get("found")]
        bmed[tg] = med_within(f, len(rr), 0)[0]
    for rule in ("B", "C", "CA"):
        for tg in (XOR, G["GE"]):
            b = base["GE / %s" % tg]
            rr = [r for r in rows if r["rule"] == rule and r["target"] == tg]
            found = [r for r in rr if r.get("found")]
            bar_r = b["blind median steps restricted"]
            med, within = med_within([r["all steps"] for r in found], len(rr), bar_r)
            medp, withinp = med_within([r["probes"] for r in found], len(rr), b["blind median restricted"])
            passes = med <= bar_r / 2 and within >= 0.75 and (rule == "B" or med <= bmed[tg] / 2)
            out["%s / %s" % (rule, tg)] = {"runs": len(rr), "found": len(found), "median all steps": med,
                                           "blind median steps uniform": b["blind median steps uniform"],
                                           "blind median steps restricted": bar_r, "B's median all steps": bmed[tg],
                                           "share within the restricted blind median": round(within, 3), "passes": passes,
                                           "median probes": medp, "blind median probes uniform / restricted": [b["blind median uniform"], b["blind median restricted"]],
                                           "share within restricted blind median (probes)": round(withinp, 3)}
    steer = {rule: {"count": out["%s / %s" % (rule, XOR)]["passes"], "g": out["%s / %s" % (rule, G["GE"])]["passes"]} for rule in ("C", "CA")}
    for v in steer.values():
        v["steering shown"] = v["count"] and v["g"]
    out["steering shown"] = steer
    out["any steering"] = any(v["steering shown"] for v in steer.values())
    return out


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    part = sys.argv[sys.argv.index("--part") + 1]
    write = "--write" in sys.argv
    res = {"baselines": baselines, "walk": walk, "summary": summary}.get(part, lambda: runs(write))()
    res = json.loads(json.dumps(res, default=str))
    out = {"dependencies": {p: sha(p) for p in DEPS}, "result": res, "seconds": round(time.time() - T0, 1)}
    if write:
        (HERE / ("result_%s.json" % part)).write_text(json.dumps({"status": "passed", "checks": out}, indent=1) + "\n")
    print(json.dumps(res, indent=1)[:5000])


if __name__ == "__main__":
    main()
