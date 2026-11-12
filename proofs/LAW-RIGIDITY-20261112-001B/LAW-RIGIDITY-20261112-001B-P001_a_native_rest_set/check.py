#!/usr/bin/env python3
"""Checks for LAW-RIGIDITY-20261112-001B, stage 2 (research/LAW-RIGIDITY-20261112-001/preregistration.md, addendum).

    .venv/bin/python3 -B check.py --part harness|learnN0U|learnN1J1|summary [--write]
PYTHONHASHSEED=0. harness: V, NativeEngine's running dissonance equals a fresh count after 20,000 random moves (both rules, both bases);
E, for each rule (every shortest sum 0, or every shortest sum 1) and base (J1, U), the laws it lets the learner rest at and how many of them
count three at the base's interface. learnN0U and learnN1J1: ten runs each (seeds 9900 + k), targets the count, its negation, the count
again, budget 8,000,000 steps per target, 30 minutes per run, each run written to runs_<part>.jsonl as it finishes. The other two pairs
(N0 on J1, N1 on U) are settled by E and not run. summary: settles the marks."""
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
LIB = str((HERE / "native_lib.py").relative_to(ROOT))
PREREG = "research/LAW-RIGIDITY-20261112-001/preregistration.md"
JOBS = "proofs/LAW-RIGIDITY-20261112-001A/LAW-RIGIDITY-20261112-001A-P001_the_two_jobs_apart/jobs_lib.py"
DEPS = [LIB, PREREG, JOBS]
RUNS = {"learnN0U": ("U", 0, 9900, 1800), "learnN1J1": ("J1", 1, 9900, 1800)}
MARKS = {"learnN0U": "N0 on U: learned in at least 8 of 10", "learnN1J1": "N1 on J1: learned in at least 8 of 10"}


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def harness():
    import native_lib as N
    import numpy as np
    out = {}
    for name in ("J1", "U"):
        sp = N.space(name)
        for want in (0, 1):
            s, x = sp.start()
            E = N.NativeEngine(sp.K, sp.S, s, x, want)
            rng = random.Random(4)
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
            G = N.NativeEngine(sp.K, sp.S, E.s, E.x, want)
            out["V: %s, rule N%d" % (name, want)] = (E.W, E.nwrong, E.par) == (G.W, G.nwrong, G.par)
        B = sp.K
        pt = [list(t) for t in B.pt]
        length, seqs = N.shortest_sequences(pt)
        X = ((np.arange(1 << B.real)[:, None] >> np.arange(B.real)[None, :]) & 1).astype(np.uint8)
        P = np.array(B.pt)
        T = sp.ports
        rows = {0: [0, 0], 1: [0, 0]}
        for law in N.UL.laws(B):
            sums = [sum(law[3 * k + pt[k].index(d)] for (k, d) in seq) % 2 for seq in seqs]
            for want in (0, 1):
                if all(v == want for v in sums):
                    rows[want][0] += 1
                    S = np.array(law, dtype=np.uint8).reshape(len(B.pt), 3)
                    Lt = X[:, P] ^ S[None, :, :]
                    st = X[~((Lt[:, :, 0] == Lt[:, :, 1]) & (Lt[:, :, 1] == Lt[:, :, 2])).any(axis=1)]
                    par = st[:, T].sum(axis=1) % 2
                    if len(st) and (par == par[0]).all() and len({tuple(r) for r in st[:, T[:-1]]}) == 8:
                        rows[want][1] += 1
        out["E: %s, shortest sequences" % name] = {"length (knots)": length, "count": len(seqs)}
        for want in (0, 1):
            out["E: %s, rule N%d: laws at rest, and of them counting" % (name, want)] = rows[want]
    return out


def job(args):
    import native_lib as N
    name, want, seed, cap = args
    targets = ["01101001", "10010110", "01101001"]
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(cap)
    t = time.time()
    try:
        rows = N.run(name, want, targets, seed)
        signal.alarm(0)
    except Timeout:
        rows = [{"target": targets[0], "outcome": "dropped (time cap)"}]
    return {"seed": seed, "seconds": round(time.time() - t, 1), "rows": rows}


def verdict(res):
    first = [r["rows"][0]["outcome"] for r in res]
    allo = [x["outcome"] for r in res for x in r["rows"]]
    ok = ("learned, held", "learned, not held")
    steps = sorted(r["rows"][0]["steps"] for r in res if r["rows"][0]["outcome"] in ok)
    return {"runs": len(res), "first target outcomes": {o: first.count(o) for o in sorted(set(first))},
            "all targets outcomes": {o: allo.count(o) for o in sorted(set(allo))}, "counted toward the mark": sum(o in ok for o in first),
            "median steps of counted first targets": steps[len(steps) // 2] if steps else None,
            "inexact stops": allo.count("inexact stop"), "seconds per run": [r["seconds"] for r in res], "runs detail": res}


def learn(part, write):
    name, want, base, cap = RUNS[part]
    path = HERE / ("runs_%s.jsonl" % part)
    if write:
        path.write_text("")
    res = []
    with Pool(10) as pool:
        for r in pool.imap_unordered(job, [(name, want, base + k, cap) for k in range(10)]):
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
        out[MARKS[part]] = v["counted toward the mark"] >= 8
    out["one rule learned on both bases"] = False
    out["why"] = "settled by E: N0 lets J1 rest at no counting law, N1 lets U rest at no law at all"
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
