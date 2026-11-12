#!/usr/bin/env python3
"""Checks for LAW-RIGIDITY-20261112-001A, stage 1 (research/LAW-RIGIDITY-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part harness|learnR|learnRS|summary [--write]
PYTHONHASHSEED=0. harness: V, RestEngine's running dissonance equals a fresh count after 20,000 random moves; E, of J1's 512 laws, those
at which R (and the learner with faces) can rest, every face with one agreeing corner possible, that is no even face (a Kasteleyn law),
and those of them that count three. learnR, learnRS: ten runs each on J1, seeds 9700 + k for both (so a run of R and of RS are step for
step the same until the first stop), targets the count, its negation, the count again, budget 8,000,000 steps per target, each run written
to runs_<part>.jsonl as it finishes, 30 minutes per run (over it a run is dropped and counts as not learned). summary: settles M1 and M2."""
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
LIB = str((HERE / "jobs_lib.py").relative_to(ROOT))
PREREG = "research/LAW-RIGIDITY-20261112-001/preregistration.md"
UND = "proofs/UNDRAWN-LEARN-20261111-001A/UNDRAWN-LEARN-20261111-001A-P001_learning_without_a_drawing/undrawn_lib.py"
DEPS = [LIB, PREREG, UND]
RUNS = {"learnR": ("R", 9700, 1800), "learnRS": ("RS", 9700, 1800)}
MARKS = {"learnR": "M1: R learned and held in at least 8 of 10", "learnRS": "M2: RS learned in at least 8 of 10 (held follows)"}


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def harness():
    import jobs_lib as L
    import numpy as np
    sp = L.J.Space(1)
    s, x = sp.start()
    E = L.RestEngine(sp.K, sp.S, s, x)
    rng = random.Random(3)
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
    G = L.RestEngine(sp.K, sp.S, E.s, E.x)
    out = {"V: RestEngine's running dissonance equals a fresh count": (E.W, E.nbad, E.ag) == (G.W, G.nbad, G.ag)}
    B = L.J.Joined(1)
    K0 = B.copies[0]
    X = ((np.arange(1 << B.real)[:, None] >> np.arange(B.real)[None, :]) & 1).astype(np.uint8)
    P = np.array(B.pt)
    rest = count = 0
    for law in L.UL.laws(B):
        if K0.even_faces(law):
            continue
        rest += 1
        S = np.array(law, dtype=np.uint8).reshape(B.nl, 3)
        Lt = X[:, P] ^ S[None, :, :]
        st = X[~((Lt[:, :, 0] == Lt[:, :, 1]) & (Lt[:, :, 1] == Lt[:, :, 2])).any(axis=1)]
        T = B.ports
        par = st[:, T].sum(axis=1) % 2
        if len(st) and (par == par[0]).all() and len({tuple(r) for r in st[:, T[:-1]]}) == 8:
            count += 1
    out["E: laws with no even face (where R and the learner with faces can rest), and of them counting three"] = [rest, count]
    return out


def job(args):
    import jobs_lib as L
    variant, seed, cap = args
    targets = ["01101001", "10010110", "01101001"]
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(cap)
    t = time.time()
    try:
        rows = L.run(variant, targets, seed)
        signal.alarm(0)
    except Timeout:
        rows = [{"target": targets[0], "outcome": "dropped (time cap)"}]
    return {"seed": seed, "seconds": round(time.time() - t, 1), "rows": rows}


def verdict(res, learned_only=False):
    first = [r["rows"][0]["outcome"] for r in res]
    allo = [x["outcome"] for r in res for x in r["rows"]]
    ok = ("learned, held", "learned, not held") if learned_only else ("learned, held",)
    steps = sorted(r["rows"][0]["steps"] for r in res if r["rows"][0]["outcome"] in ok)
    return {"runs": len(res), "first target outcomes": {o: first.count(o) for o in sorted(set(first))},
            "all targets outcomes": {o: allo.count(o) for o in sorted(set(allo))},
            "counted toward the mark": sum(o in ok for o in first),
            "median steps of counted first targets": steps[len(steps) // 2] if steps else None,
            "inexact stops": allo.count("inexact stop"), "seconds per run": [r["seconds"] for r in res], "runs detail": res}


def learn(part, write):
    variant, base, cap = RUNS[part]
    path = HERE / ("runs_%s.jsonl" % part)
    if write:
        path.write_text("")
    res = []
    with Pool(10) as pool:
        for r in pool.imap_unordered(job, [(variant, base + k, cap) for k in range(10)]):
            res.append(r)
            if write:
                with path.open("a") as f:
                    f.write(json.dumps(r) + "\n")
    return verdict(sorted(res, key=lambda r: r["seed"]), part == "learnRS")


def summary():
    out = {}
    for part in RUNS:
        p = HERE / ("runs_%s.jsonl" % part)
        res = [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []
        v = verdict(sorted(res, key=lambda r: r["seed"]), part == "learnRS")
        v.pop("runs detail")
        v["missing runs (part cap)"] = 10 - len(res)
        out[part] = v
        out[MARKS[part]] = v["counted toward the mark"] >= 8
    m1, m2 = out[MARKS["learnR"]], out[MARKS["learnRS"]]
    out["reading"] = ("the rest set alone, with a flat cost of leaving it, is enough" if m1 else
                      "the rest set finds the count; holding it needs the supplied rigid repair" if m2 else
                      "neither the rest set nor a rigid repair, without the graded face term, is enough")
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
