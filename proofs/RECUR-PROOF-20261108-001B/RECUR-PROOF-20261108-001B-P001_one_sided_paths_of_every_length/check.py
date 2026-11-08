#!/usr/bin/env python3
"""Checks for RECUR-PROOF-20261108-001B: one-sided additive paths of every length.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy (the repository's .venv). 16 worker processes, a few minutes."""
import hashlib
import importlib.util
import itertools
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E2 = ROOT / "experiments/RECUR-PATH-20261108-001A/RECUR-PATH-20261108-001A-E002_recurring_lags_fixed"
sys.path.insert(0, str(E2))
spec = importlib.util.spec_from_file_location("recur_run", E2 / "run.py")
RUN = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RUN)
R, PL = RUN.R, RUN.PL
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:400], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def odd(n, k):
    return n >= 0 and (n & k) == k


def path(rules, s, ks):
    side = lambda r: 10 if r == 60 else 12
    n = len(rules)
    laws = (("self-blind", side(rules[0]), side(rules[1])),) + tuple(("self-blind", 6, side(rules[i])) for i in range(2, n))
    return tuple(rules), (s,) * n, list(ks), laws


def predict(args):
    rules, s, ks = args
    p = path(rules, s, ks)
    n = len(rules)
    e = sum((k if r == 60 else s - k) - 1 for k, r in zip(ks, rules[1:-1]))
    rows, N, blocks = PL.linear_matrix(*p)
    msk = [PL.mask(blocks, f"R{i}") for i in range(n)]
    orbs = [R.orbit(rows, 1 << c, 10 ** 6) for c in range(n - 1)]
    H = max(o[1] + o[2] for o in orbs) + 64
    bad = 0
    for T in range(1, H):
        rw = [R.row_at(o, T) for o in orbs]
        pers = all(rw[c] & msk[c] and rw[c] & msk[c + 1] for c in range(n - 1))
        bad += (not pers) or (not rw[-1] & msk[-1]) or (bool(rw[-1] & msk[0]) != odd(T - (n - 1), e))
    return bad, H - 1


def full(args):
    rules, s, ks = args
    return RUN.brute(*path(rules, s, ks))


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"] if q.endswith("manifest.json")}
    check("0 dependency artifacts bound by hash; upstream statuses", not bad and all(s_ == "Proved" for s_ in status.values()),
          {"mismatched": bad, "statuses": status})
    jobs = [((60,) * n, s, ks) for n in range(3, 11) for s in range(4, 17) for ks in itertools.product((2, s - 2), repeat=n - 2)]
    with Pool(16) as pool:
        res = pool.map(predict, jobs, chunksize=8)
    check("1 the theorem's predictions at every lag through the eventual cycle, rule 60 everywhere, n = 3 to 10, sizes 4 to 16, every choice "
          "of positions", sum(b for b, l in res) == 0, {"paths": len(jobs), "lags": sum(l for b, l in res), "mismatches": sum(b for b, l in res)})
    rng = random.Random(20261108)
    jobs = []
    for _ in range(400):
        n, s = rng.randint(3, 8), rng.randint(4, 14)
        jobs.append((tuple(rng.choice((60, 102)) for _ in range(n)), s, [rng.choice((2, s - 2)) for _ in range(n - 2)]))
    with Pool(16) as pool:
        res = pool.map(predict, jobs, chunksize=4)
    check("2 the same on 400 random paths with rule 60 or 102 on each ring, n = 3 to 8, against the mirrored positions",
          sum(b for b, l in res) == 0, {"paths": len(jobs), "lags": sum(l for b, l in res), "mismatches": sum(b for b, l in res)})
    jobs = [((60, 60, 60), s, [k]) for s in (4, 5) for k in (2, s - 2)] + [((60,) * 5, 4, [2, 2, 2])]
    with Pool(8) as pool:
        fs = pool.map(full, jobs)
    check("3 full state spaces: n = 3 at sizes 4 and 5, n = 5 at size 4: every lag no, recurring with every contact persistent yes",
          all(b is not None and b[0] is False and b[1] is True for b in fs), {"paths": len(jobs), "readings": fs})
    res = {"status": "passed", "checks": OUT, "seconds": round(time.time() - T0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
        print("wrote result.json")
    else:
        old = json.loads((HERE / "result.json").read_text())
        same = {k: v["info"] for k, v in old["checks"].items()} == json.loads(json.dumps({k: v["info"] for k, v in OUT.items()}, default=str))
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
