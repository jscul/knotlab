#!/usr/bin/env python3
"""Checks for NATIVE-GRADE-20261112-001A (research/NATIVE-GRADE-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part harness|learnJ1|learnU|summary [--write]
PYTHONHASHSEED=0. harness: V, GradeEngine's running dissonance equals a fresh count after 20,000 random moves (J1, U); E, on J1, U and the
next two bases of UNDRAWN-LEARN's frozen search, the laws at rest under "all shortest sums equal" (and under "all 0", "all 1"), how many
count three, and how many places lie on no, one, or two or more shortest sequences. learnJ1, learnU: ten runs each (seeds 10000 + k),
targets the count, its negation, the count again, budget 8,000,000 steps per target, the free repair, 30 minutes per run, each run written
to runs_<part>.jsonl as it finishes. summary: settles the marks and compares first-target probes with drawing laws at rest at random."""
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
LIB = str((HERE / "grade_lib.py").relative_to(ROOT))
PREREG = "research/NATIVE-GRADE-20261112-001/preregistration.md"
NAT = "proofs/LAW-RIGIDITY-20261112-001B/LAW-RIGIDITY-20261112-001B-P001_a_native_rest_set/native_lib.py"
DEPS = [LIB, PREREG, NAT]
RUNS = {"learnJ1": ("J1", 10000, 1800), "learnU": ("U", 10000, 1800)}
REST = {"learnJ1": (64, 4), "learnU": (2, 1)}


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def counts(B, law, T, X, P):
    import numpy as np
    S = np.array(law, dtype=np.uint8).reshape(len(B.pt), 3)
    Lt = X[:, P] ^ S[None, :, :]
    st = X[~((Lt[:, :, 0] == Lt[:, :, 1]) & (Lt[:, :, 1] == Lt[:, :, 2])).any(axis=1)]
    if not len(st):
        return False
    par = st[:, T].sum(axis=1) % 2
    return bool((par == par[0]).all() and len({tuple(r) for r in st[:, T[:-1]]}) == 2 ** (len(T) - 1))


def harness():
    import grade_lib as G
    import numpy as np
    out = {}
    for name in ("J1", "U"):
        sp = G.N.space(name)
        s, x = sp.start()
        E = G.GradeEngine(sp.K, sp.S, s, x)
        rng = random.Random(6)
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
        H = G.GradeEngine(sp.K, sp.S, E.s, E.x)
        out["V: %s" % name] = (E.W, E.n1, E.par) == (H.W, H.n1, H.par)
    bases = [("J1", G.J.Joined(1), None)]
    B, T, _ = G.UL.chosen_undrawn()
    bases.append(("U", B, T))
    for n, m in [(7, 9), (8, 10)]:
        r = G.UL.find_undrawn(100, n, m)
        bases.append(("U(%d, %d) seed %d" % (n, m, r[0].seed), r[0], r[1]))
    for name, B, T in bases:
        T = T if T is not None else B.ports
        pt = [list(t) for t in B.pt]
        length, seqs = G.N.shortest_sequences(pt)
        X = ((np.arange(1 << B.real)[:, None] >> np.arange(B.real)[None, :]) & 1).astype(np.uint8)
        P = np.array(B.pt)
        tally = {"all equal": [0, 0], "all 0": [0, 0], "all 1": [0, 0]}
        total = counting = 0
        for law in G.UL.laws(B):
            total += 1
            c = counts(B, law, T, X, P)
            counting += c
            sums = {sum(law[3 * k + pt[k].index(d)] for (k, d) in seq) % 2 for seq in seqs}
            for key, ok in (("all equal", len(sums) == 1), ("all 0", sums == {0}), ("all 1", sums == {1})):
                if ok:
                    tally[key][0] += 1
                    tally[key][1] += c
        cover = [sum((k, d) in seq for seq in seqs) for k in range(len(pt)) for d in pt[k]]
        out["E: %s" % name] = {"distinctions": B.real, "knots": len(pt), "laws": total, "counting laws": counting,
                               "shortest sequences": [length, len(seqs)], "laws at rest, counting among them": tally,
                               "places on 0, 1, 2+ shortest sequences": [sum(c == 0 for c in cover), sum(c == 1 for c in cover),
                                                                        sum(c >= 2 for c in cover)]}
    return out


def job(args):
    import grade_lib as G
    name, seed, cap = args
    targets = ["01101001", "10010110", "01101001"]
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(cap)
    t = time.time()
    try:
        rows = G.run(name, targets, seed)
        signal.alarm(0)
    except Timeout:
        rows = [{"target": targets[0], "outcome": "dropped (time cap)"}]
    return {"seed": seed, "seconds": round(time.time() - t, 1), "rows": rows}


def verdict(res):
    first = [r["rows"][0]["outcome"] for r in res]
    allo = [x["outcome"] for r in res for x in r["rows"]]
    found = sum(o in ("learned, held", "learned, not held") for o in first)
    probes = sorted(r["rows"][0]["probes"] for r in res if r["rows"][0].get("probes") is not None and r["rows"][0]["outcome"] != "dropped (time cap)")
    return {"runs": len(res), "first target outcomes": {o: first.count(o) for o in sorted(set(first))},
            "all targets outcomes": {o: allo.count(o) for o in sorted(set(allo))}, "found at the first target": found,
            "learned and held at the first target": first.count("learned, held"),
            "first-target probes": probes, "inexact stops": allo.count("inexact stop"),
            "seconds per run": [r["seconds"] for r in res], "runs detail": res}


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
        rest, cnt = REST[part]
        v["laws at rest per counting law (random draws expected)"] = rest / cnt
        held, found = v["learned and held at the first target"], v["found at the first target"]
        v["P: learned and held in at least 8 of 10"] = held >= 8
        v["reading"] = "holds" if held >= 8 else ("still drifts" if found >= 8 else "not found")
        out[part] = v
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
        print(json.dumps({k: v for k, v in res.items() if k != "runs detail"}, indent=1)[:4000])
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
