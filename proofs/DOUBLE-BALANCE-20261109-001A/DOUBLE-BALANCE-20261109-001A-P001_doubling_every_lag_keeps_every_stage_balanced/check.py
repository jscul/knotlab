#!/usr/bin/env python3
"""Checks for DOUBLE-BALANCE-20261109-001A: doubling every lag keeps every stage balanced; slower doubling does not.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, a few minutes. On GROW-CHOOSE-20261109-001A-E001's choose_lib (every born cell a variable, persistence read through a full
cycle of the state, Brent's method), validated against actual bits by GROW-ALL-20261109-001's validate.py. Check 3 is a computation."""
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/GROW-CHOOSE-20261109-001A/GROW-CHOOSE-20261109-001A-E001_dynamics_chosen_growth"))
import choose_lib as C  # noqa: E402

T0 = time.time()
OUT = {}
DEPS = {
    "experiments/GROW-CHOOSE-20261109-001A/GROW-CHOOSE-20261109-001A-E001_dynamics_chosen_growth/choose_lib.py":
        "71e5e8829415d09533a8648fd615cf06b94e767258c383bd8b6624cb510741c4",
    "research/GROW-ALL-20261109-001/validate.py":
        "2f66e504c2c146b8d1837ab08f47ecbbb0d19eea871e71dbac6708d8aacfbaf4",
    "proofs/GROW-HORIZON-20261109-001A/GROW-HORIZON-20261109-001A-P001_while_it_doubles_every_lag_no_ring_hears_another/manifest.json":
        "cf2c6a0245a6367f3bd57fa5460dd01db2b2e2d3aa563255d65fd7007af907f0",
}
MAX_RINGS = 2400


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:500], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def double(run, t):
    cuts = [('row', x) for x in run.tube.rows] + [('col', x) for x in run.tube.cols]
    for k, (kind, x) in enumerate(cuts):
        run.insert(kind, x, ('b', t, k), 'fresh')


def rank(vecs):
    basis = {}
    r = 0
    for v in vecs:
        while v:
            h = v.bit_length() - 1
            if h not in basis:
                basis[h] = v
                r += 1
                break
            v ^= basis[h]
    return r


def hypothesis(run):
    """the lemma's hypothesis at this lag, for every ring X: no cell outside X's own cells holds one of X's born own cells, and the parts
    of X's own cells over X's born own cells are linearly independent; returns the number of rings failing it"""
    born = {}
    for v, k in enumerate(run.vkey):
        if k[0] == 'o':
            born.setdefault(k[1], 0)
            born[k[1]] |= 1 << v
    own = {}
    for b, k in enumerate(run.tube.keys):
        if k[0] == 'o':
            own.setdefault(k[1], []).append(b)
    fails = 0
    for X, mask in born.items():
        mine = set(own.get(X, []))
        outside = any(run.state[b] & mask for b in range(len(run.state)) if b not in mine)
        parts = [run.state[b] & mask for b in own.get(X, [])]
        if outside or rank(parts) < len(parts):
            fails += 1
    return fails


def schedule(n, m, g, P, max_rings=MAX_RINGS):
    run = C.Run2(C.Tube2(list(range(n)), list(range(m)), g))
    t, rows = 0, []
    while len(run.tube.rings) * 4 <= max_rings or t % P:
        if t % P == 0:
            double(run, t)
            rows.append({"lag": t, "side": [len(run.tube.cols), len(run.tube.rows)], "rings failing the hypothesis": hypothesis(run),
                         "stage balanced": C.persists(run, 300000)})
            print(n, m, g, P, rows[-1], round(time.time() - T0, 1), flush=True)
        run.step()
        t += 1
    return rows


def main():
    deps = {p: sha(p) for p in DEPS}
    check("0 dependencies bound by hash", all(DEPS[p] == deps[p] for p in DEPS), deps)
    every = {"%d x %d, g = %d" % (n, m, g): schedule(n, m, g, 1, cap) for n, m, g, cap in ((3, 3, 2, MAX_RINGS), (3, 4, 2, MAX_RINGS), (3, 3, 3, 600))}
    check("1 The lemma's hypothesis holds at every doubling lag of doubling every lag (3 x 3 to 48 x 48 and 3 x 4 to 24 x 32 at g = 2, 3 x 3 "
          "to 24 x 24 at g = 3), as the theorem says", all(r["rings failing the hypothesis"] == 0 for v in every.values() for r in v), every)
    check("2 The theorem's conclusion: every one of those stages balanced, read through a full cycle",
          all(r["stage balanced"] is True for v in every.values() for r in v), {k: [r["stage balanced"] for r in v] for k, v in every.items()})
    slow = {"P = %d" % P: schedule(3, 3, 2, P) for P in (2, 3, 4, 6, 8)}
    check("3 Computed: doubling every P lags from 3 x 3 at g = 2 to 48 x 48; isolation and balance at each doubling lag", True, slow)
    result = {"ticket": "DOUBLE-BALANCE-20261109-001A", "artifact_id": "DOUBLE-BALANCE-20261109-001A-P001", "checks": OUT, "status": "passed"}
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
