#!/usr/bin/env python3
"""Checks for GROW-STOP-20261110-001A: a grown plane that stops reads the fixed torus's distances, scaled by the growth.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
On GROW-CHOOSE-20261109-001A-E001's choose_lib (every born cell a variable) and BIRTH-RULE-20261109-001A-E001's double(). For each run: the
doubling law for k lags from the 3 x 3 tube, then a stop; and the same final torus run from an open first row. For every contact c, every
original ring X and every lag T = 1 .. L after the stop, whether c's value depends on X's first row (the run) or on X's own cells at the
torus's first row (the fixed torus), with and without one contact frozen from the stop on. Check 3 is a computation."""
import copy
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/BIRTH-RULE-20261109-001A/BIRTH-RULE-20261109-001A-E001_birth_rules"))
import run as B  # noqa: E402

C = B.C
T0 = time.time()
OUT = {}
DEPS = {
    "experiments/BIRTH-RULE-20261109-001A/BIRTH-RULE-20261109-001A-E001_birth_rules/run.py":
        "700c9ed85da8852dd0c0d1941031b063c116aa3afe29f22186aeb660df7dd6ce",
    "proofs/DOUBLE-BALANCE-20261109-001A/DOUBLE-BALANCE-20261109-001A-P001_doubling_every_lag_keeps_every_stage_balanced/manifest.json":
        "cc40bc02687e69af79c7c71b66feebc5df67ca24616a4ceb60aa76325860a082",
}
L = 60


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:400], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def freeze(run, c):
    """freeze contact c from now on: its row reads only itself (A38)"""
    run.tube.M = list(run.tube.M)
    run.tube.M[c] = 1 << c


def pattern(run, rings, lags, masks):
    """{(contact, ring): bit string of the lags 1..lags at which the contact depends on the ring's mask}"""
    out = {}
    r = copy.deepcopy(run)
    hist = []
    for _ in range(lags):
        r.step()
        hist.append(list(r.state[:len(r.tube.contacts)]))
    for c in range(len(r.tube.contacts)):
        for R in rings:
            out[(c, R)] = "".join("1" if hist[t][c] & masks[R] else "0" for t in range(lags))
    return out


def grown(n, m, g, k, P):
    run = C.Run2(C.Tube2(list(range(n)), list(range(m)), g))
    t, d = 0, 0
    while d < k:
        if t % P == 0:
            B.double(run, t, "open")
            d += 1
            if d == k:
                break
        run.step()
        t += 1
    return run


def compare(n, m, g, k, P, frozen=None):
    run = grown(n, m, g, k, P)
    original = [(i, j) for i in range(n) for j in range(m)]
    tube = run.tube
    hist_masks = {}
    for v, key in enumerate(run.vkey):
        if key[0] == 'o' and key[1] in original and v < n * m * 4 * g:   # first-row cells of the original rings
            hist_masks[key[1]] = hist_masks.get(key[1], 0) | (1 << v)
    fixed = C.Run2(C.Tube2(tube.cols, tube.rows, g))
    fixed_masks = {R: fixed.ringmask(R) for R in original}
    if frozen is not None:
        freeze(run, frozen)
        freeze(fixed, frozen)
    a = pattern(run, original, L, hist_masks)
    b = pattern(fixed, original, L, fixed_masks)
    diff = sum(1 for key in a if a[key] != b[key])
    return len(a), diff


def main():
    deps = {p: sha(p) for p in DEPS}
    check("0 dependencies bound by hash", all(DEPS[p] == deps[p] for p in DEPS), deps)
    res = {}
    for n, m, g, k in ((3, 3, 2, 1), (3, 3, 2, 2), (3, 3, 2, 3), (3, 4, 2, 2), (3, 3, 3, 1), (3, 3, 3, 2)):
        res["%d x %d, g = %d, k = %d" % (n, m, g, k)] = compare(n, m, g, k, 1)
    check("1 The theorem, doubling every lag: after the stop every contact's dependence on every original ring's first row, lag by lag "
          "for 60 lags, is the fixed torus's", all(d == 0 for p, d in res.values()), res)
    fr = {}
    for n, m, g, k, c in ((3, 3, 2, 2, 0), (3, 3, 2, 2, 17), (3, 3, 3, 2, 5)):
        fr["%d x %d, g = %d, k = %d, contact %d frozen" % (n, m, g, k, c)] = compare(n, m, g, k, 1, frozen=c)
    check("2 The same with a contact frozen from the stop on", all(d == 0 for p, d in fr.values()), fr)
    slow = {}
    for g, P in ((2, 2), (2, 3), (2, 4), (3, 2), (3, 4)):
        slow["g = %d, P = %d, k = 2" % (g, P)] = compare(3, 3, g, 2, P)
    check("3 Computed: slower schedules (k = 2 doublings, then a stop) against the fixed torus: pairs that differ", True, slow)
    result = {"ticket": "GROW-STOP-20261110-001A", "artifact_id": "GROW-STOP-20261110-001A-P001", "checks": OUT, "status": "passed"}
    path = HERE / "result.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        return 0
    old = json.loads(path.read_text())
    same = json.dumps(old["checks"], sort_keys=True, default=str) == json.dumps(json.loads(json.dumps(OUT, default=str)), sort_keys=True)
    print("result.json matches" if same else "result.json differs")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
