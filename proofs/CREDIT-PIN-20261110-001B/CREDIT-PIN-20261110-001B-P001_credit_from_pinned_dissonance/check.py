#!/usr/bin/env python3
"""Checks for CREDIT-PIN-20261110-001B: credit from pinned dissonance (research/CREDIT-PIN-20261110-001/preregistration.md, ticket B).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. The credit learner (credit_lib.py) at every interface of S3 and S4 (learner seed 3000 + k, the same k as ticket A)
and of S5 (seed 5000 + k), targets 1uu0, u10u, uuuu, 0uu1, 0001; each cooling recorded with the atoms acting at that moment (read by SAT
afterwards). Marks C2, M (against ticket A's result.json), A, and C2 on S5. Interfaces run in parallel."""
import hashlib
import json
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
OUT = {}
FA = "proofs/CREDIT-PIN-20261110-001A/CREDIT-PIN-20261110-001A-P001_the_fixed_learner"
DEPS = [str((HERE / "credit_lib.py").relative_to(ROOT)), FA + "/fix_lib.py", FA + "/result.json", "research/CREDIT-PIN-20261110-001/preregistration.md"]
SPACES = ["S1 single K_3 thin", "S2 single K_3 Fano", "S3 two-level K_3 thin", "S4 two-level K_3 Fano"]
S5 = "S5 two-level K_3 thin, three composites"
TARGETS = ["1uu0", "u10u", "uuuu", "0uu1", "0001"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def run(job):
    import credit_lib as C
    name, iname, ports, seed = job
    sp = C.W.Space(name)
    leaf_lines = {j: set(sp.atoms[j][1]) for j in sp.atoms}
    comps = sorted({q[:1] for q in sp.leaves if len(q) > 1})
    comp_lines = {t: set(sp.O.group_parts(sp.K, t)[0]) for t in comps}
    comp_leaves = {t: [j for j, q in enumerate(sp.leaves) if q[:1] == t] for t in comps}
    events = []
    orig = C.cooled_lines

    def recorded(E, nb, rng, tau, att, interface):
        cool = orig(E, nb, rng, tau, att, interface)
        act = set(sp.acting(E.s))
        on = set().union(*([leaf_lines[j] for j in act] or [set()]))
        for t in comps:
            if all(j in act for j in comp_leaves[t]):
                on |= comp_lines[t]
        events.append((len(cool), len(cool & on)))
        return cool
    C.cooled_lines = recorded
    rows = C.F.run_interface(sp, ports, TARGETS, seed, params=C.PARAMS, learner=C.learn)
    return name, iname, rows, events


def summary(rows):
    def kind(key):
        return "composite" if "/ composite" in key else "leaf"
    writes = [(kind(k), r) for k, rr in rows.items() for r in rr if r["target"] != "0001"]
    oc = {g: dict(Counter(r["outcome"] for kk, r in writes if kk == g)) for g in ("leaf", "composite")}
    held = {g: sum(1 for kk, r in writes if kk == g and r["outcome"] == "learned, held") for g in ("leaf", "composite")}
    inexact = sum(1 for kk, r in writes if r["outcome"] == "inexact stop") + sum(1 for k, rr in rows.items() for r in rr if r["target"] == "0001" and r["stopped"])
    ctrl_stops = sum(1 for k, rr in rows.items() for r in rr if r["target"] == "0001" and r["stopped"])
    return oc, held, inexact, ctrl_stops


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    import credit_lib as C
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    jobs, k = [], 0
    for name in SPACES:
        sp = C.W.Space(name)
        for iname, ports in C.I.interfaces(sp):
            if name in SPACES[2:]:
                jobs.append((name, iname, ports, 3000 + k))
            k += 1
    sp5 = C.W.Space(S5)
    for k5, (iname, ports) in enumerate(C.I.interfaces(sp5)):
        jobs.append((S5, iname, ports, 5000 + k5))
    with Pool(len(jobs)) as pool:
        res = pool.map(run, jobs)
    rows = {"%s / %s" % (n, i): r for n, i, r, _ in res}
    events = {"%s / %s" % (n, i): e for n, i, _, e in res}
    test = {k: v for k, v in rows.items() if not k.startswith("S5")}
    five = {k: v for k, v in rows.items() if k.startswith("S5")}
    oc, held, inexact, ctrl = summary(test)
    prev = json.loads((ROOT / FA / "result.json").read_text())["checks"]["rows"]
    prev = {k: v for k, v in prev.items() if k.startswith("S3") or k.startswith("S4")}
    poc, pheld, pinexact, _ = summary(prev)
    ev = [e for k, v in events.items() if not k.startswith("S5") for e in v]
    cooled, on = sum(a for a, b in ev), sum(b for a, b in ev)
    check("1 the credit learner at the interfaces of S3 and S4 (computed, frozen)", True, {
        "outcomes": oc, "learned and held": held,
        "C2: composites at least 90% (15 of 16)": held["composite"] >= 15,
        "ticket A's fixed learner, same interfaces and seeds": {"outcomes": poc, "learned and held": pheld, "inexact stops": pinexact},
        "M: pinned dissonance misleads": (held["leaf"] + held["composite"] < pheld["leaf"] + pheld["composite"]) or inexact > pinexact,
        "inexact stops": inexact, "A: 0001 never stopped": ctrl == 0,
        "coolings": len(ev), "cooled lines (summed over coolings)": cooled, "of them in an atom acting at that moment": on,
        "share on target": round(on / cooled, 3) if cooled else None})
    oc5, held5, inexact5, ctrl5 = summary(five)
    ev5 = [e for k, v in events.items() if k.startswith("S5") for e in v]
    c5, o5 = sum(a for a, b in ev5), sum(b for a, b in ev5)
    check("2 one size past: S5 (computed, frozen)", True, {
        "outcomes": oc5, "learned and held": held5, "C2 on S5 (11 of 12)": held5["composite"] >= 11, "inexact stops": inexact5,
        "A: 0001 never stopped": ctrl5 == 0, "share of cooled lines on target": round(o5 / c5, 3) if c5 else None})
    OUT["rows"] = rows
    OUT["events"] = events
    OUT["seconds"] = round(time.time() - T0, 1)
    res_path = HERE / "result.json"
    if write:
        res_path.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res_path)
    else:
        old = json.loads(res_path.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [k for k in OUT if k != "seconds" and json.dumps(old.get(k), sort_keys=True) != json.dumps(fresh[k], sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
