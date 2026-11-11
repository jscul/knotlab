#!/usr/bin/env python3
"""Checks for UNDRAWN-LEARN-20261111-001A (research/UNDRAWN-LEARN-20261111-001/preregistration.md).

    .venv/bin/python3 -B check.py --part harness|learn1|learn2|learn3|summary [--write]
PYTHONHASHSEED=0. harness: V, the drawing-free engine's running dissonance equals a fresh count after 20,000 random moves on J1 and J2;
R, the laws (signings modulo flipping a distinction and complementing a knot) that count at J1's interface, and at the undrawn base's,
chosen by the frozen rule; the undrawn base's plain-law map. learn1, learn2, learn3: ten runs each on J1 (seed 9400 + k), J2 (9500 + k)
and the undrawn base U (9600 + k), targets the count of the held inputs, its negation, the count again, budget 8,000,000 steps per
target, each run written to runs_<part>.jsonl as it finishes; caps per run 30, 120 and 30 minutes (over the cap a run is dropped and
counts as not learned). summary: settles L1, L2 and L3."""
import hashlib
import json
import os
import random
import signal
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
LIB = str((HERE / "undrawn_lib.py").relative_to(ROOT))
PREREG = "research/UNDRAWN-LEARN-20261111-001/preregistration.md"
JOIN = "proofs/SHARED-COUNT-20261111-001A/SHARED-COUNT-20261111-001A-P001_counting_through_a_shared_distinction/join_lib.py"
FIVE = "proofs/PARITY-FIVE-20261111-001A/PARITY-FIVE-20261111-001A-P001_parity_of_five_held_points/five_lib.py"
DEPS = [LIB, PREREG, JOIN, FIVE]
RUNS = {"learn1": ("J1", 9400, 1800), "learn2": ("J2", 9500, 7200), "learn3": ("U", 9600, 1800)}
MARKS = {"learn1": "L1: J1 learned and held in at least 8 of 10", "learn2": "L2: J2 learned and held in at least 8 of 10",
         "learn3": "L3: the undrawn base learned and held in at least 8 of 10"}


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def harness():
    import undrawn_lib as U
    out = {}
    for m in (1, 2):
        sp = U.J.Space(m)
        s, x = sp.start()
        E = U.KnotEngine(sp.K, sp.S, s, x)
        rng = random.Random(5)
        for _ in range(20000):
            if rng.random() < 0.5:
                p = rng.randrange(E.n)
                sites = E.sites_of_point[p]
                d, nv, dag = E.delta(sites)
                E.x[p] ^= 1
            else:
                i, k = rng.randrange(E.n), rng.randrange(3)
                sites = [(i, k)]
                d, nv, dag = E.delta(sites)
                E.s[3 * i + k] ^= 1
            E.apply(sites, d, nv, dag)
        G = U.KnotEngine(sp.K, sp.S, E.s, E.x)
        out["V: J%d running dissonance equals a fresh count" % m] = (E.W, E.ag, E.L) == (G.W, G.ag, G.L)
    B1 = U.J.Joined(1)
    out["R: laws counting at J1's interface"] = U.count_laws(B1, B1.ports, B1.real)
    B, T, sets = U.chosen_undrawn()
    out["undrawn base U"] = {"seed": B.seed, "distinctions": B.real, "knots": B.nl, "knots' distinctions": B.pt, "knots per distinction": B.degrees,
                             "interface (three held, one read)": T, "counting sets in any law": sets}
    out["R: laws counting at U's interface"] = U.count_laws(B, T, B.real)
    sp = U.UndrawnSpace(B, T)
    out["U's plain-law map"] = U.F.read_map_k(B, sp.start()[0], T)
    return out


def job(args):
    import undrawn_lib as U
    name, seed, cap = args
    sp = U.space(name)
    k = len(sp.ports) - 1
    targets = [U.F.parity_string(k, 0), U.F.parity_string(k, 1), U.F.parity_string(k, 0)]
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(cap)
    t = time.time()
    try:
        rows = U.run(sp, targets, seed)
        signal.alarm(0)
    except Timeout:
        rows = [{"target": targets[0], "outcome": "dropped (time cap)"}]
    return {"seed": seed, "seconds": round(time.time() - t, 1), "rows": rows}


def verdict(res):
    first = [r["rows"][0]["outcome"] for r in res]
    allo = [x["outcome"] for r in res for x in r["rows"]]
    steps = sorted(r["rows"][0]["steps"] for r in res if r["rows"][0]["outcome"] == "learned, held")
    return {"runs": len(res), "first target outcomes": {o: first.count(o) for o in sorted(set(first))},
            "all targets outcomes": {o: allo.count(o) for o in sorted(set(allo))},
            "learned and held at the first target": first.count("learned, held"),
            "median steps of learned first targets": steps[len(steps) // 2] if steps else None,
            "inexact stops": allo.count("inexact stop"), "seconds per run": [r["seconds"] for r in res], "runs detail": res}


def learn(part, write):
    name, base, cap = RUNS[part]
    path = HERE / ("runs_%s.jsonl" % part)
    if write:
        path.write_text("")
    res = []
    with Pool(10) as pool:
        for r in pool.imap_unordered(job, [(name, base + k, cap) for k in range(10)]):
            res.append(r)
            if write:
                with path.open("a") as f:
                    f.write(json.dumps(r) + "\n")
    return verdict(sorted(res, key=lambda r: r["seed"]))


def summary():
    out = {}
    for part in RUNS:
        p = HERE / ("runs_%s.jsonl" % part)
        res = [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []
        v = verdict(sorted(res, key=lambda r: r["seed"]))
        v.pop("runs detail")
        v["missing runs (part cap)"] = 10 - len(res)
        out[part] = v
        out[MARKS[part]] = v["learned and held at the first target"] >= 8
    out["the faces did real work (L1 or L2 failed)"] = not (out[MARKS["learn1"]] and out[MARKS["learn2"]])
    return out


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    part = sys.argv[sys.argv.index("--part") + 1]
    write = "--write" in sys.argv
    res = harness() if part == "harness" else summary() if part == "summary" else learn(part, write)
    res = json.loads(json.dumps(res, default=str))
    out = {"dependencies": {p: sha(p) for p in DEPS}, "result": res, "seconds": round(time.time() - T0, 1)}
    path = HERE / ("result_%s.json" % part)
    if write:
        path.write_text(json.dumps({"status": "passed", "checks": out}, indent=1) + "\n")
        print("wrote", path, out["seconds"], "s")
        print(json.dumps({k: v for k, v in res.items() if k != "runs detail"}, indent=1)[:3000])
    else:
        old = json.loads(path.read_text())["checks"]["result"]

        def clean(d):
            d = {k: v for k, v in d.items() if k != "seconds per run"}
            if "runs detail" in d:
                d["runs detail"] = [{k: v for k, v in r.items() if k != "seconds"} for r in d["runs detail"]]
            return d
        same = json.dumps(clean(old), sort_keys=True) == json.dumps(clean(res), sort_keys=True)
        print("result reproduced" if same else "result differs")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
