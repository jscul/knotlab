#!/usr/bin/env python3
"""Checks for GROW-HORIZON-20261109-001A: while it doubles every lag, no ring hears another.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, a few minutes. Exact: every cell's dependence on the original rings' own first-row cells is followed lag by lag (horizon_lib),
to the lags stated. Checks 2 and 3 are computations, not theorems."""
import hashlib
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import horizon_lib as H  # noqa: E402

T0 = time.time()
OUT = {}
DEPS = {
    "proofs/SEPARATE-20261108-001A/SEPARATE-20261108-001A-P001_a_cut_separates_a_cycle_needs_two/net_lib.py":
        "e75467f9d6df5f0fe7c8311e4801fabfaa8b4a4a74b3a4e2ff26c1cab9d26351",
    "research/GROW-HORIZON-20261109-001/preregistration.md":
        "9adf9e88a5b1a5039a10dddb99e57162a2f520d0b8cd96d659b0e1561efbfa92",
}
MAX_RINGS = 9216


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:500], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def contact_rings_only(run):
    """every contact depends only on the original cells of the original rings it lies on, if it lies on any"""
    net = run.net
    for c, (ra, pa, rb, pb, law) in enumerate(net.contacts):
        allowed = run.ringbits.get(net.rings[ra], 0) | run.ringbits.get(net.rings[rb], 0)
        if run.state[c] & ~allowed:
            return False
    return True


def every_lag(n, m, g, lags):
    run = H.Run(n, m, g)
    rows = []
    for t in range(lags + 1):
        if len(run.net.rings) * 4 <= MAX_RINGS:
            run.double()
            doubled = True
        else:
            doubled = False
        rows.append((t, len(run.net.cols), len(run.net.rows), doubled, run.own_cells_hearing_others(), contact_rings_only(run)))
        run.step()
        rows[-1] = rows[-1] + (run.own_cells_hearing_others(), contact_rings_only(run),
                               str(run.reach((Fraction(0), Fraction(0)))[0]))
        if not doubled:
            break
    return rows


def every_p(P, n, m, g):
    """doubling every P lags while the network has at most MAX_RINGS / 4 rings: the reach of ring (0, 0) at the last lag before each
    doubling, its largest reach over every lag read, and the original rings that ever hear it (one of their own cells depending on its
    first row), with their taxicab distances"""
    run = H.Run(n, m, g)
    X = (Fraction(0), Fraction(0))
    before, t, most, ever = [], 0, Fraction(0), set()
    while True:
        if t % P == 0:
            if len(run.net.rings) * 4 > MAX_RINGS:
                break
            if t > 0:
                r, cnt = run.reach(X)
                before.append({"lag": t - 1, "side": len(run.net.cols), "reach": str(r), "contacts needing it": cnt})
            run.double()
        run.step()
        t += 1
        r, cnt = run.reach(X)
        if r is not None and r > most:
            most = r
        ever |= H.heard(run, X)
    return {"lags read": t, "before each doubling": before, "largest reach": str(most),
            "original rings that ever hear it": sorted(str(H.taxicab(Y, X, run.net.period)) for Y in ever)}


def static(n, m, g, lags):
    run = H.Run(n, m, g)
    X = (Fraction(0), Fraction(0))
    best = Fraction(0)
    for t in range(lags):
        run.step()
        r, c = run.reach(X)
        if r is not None and r > best:
            best = r
    return str(best)


def main():
    deps = {p: sha(p) for p in DEPS}
    check("0 dependencies bound by hash", all(DEPS[p] == deps[p] for p in DEPS), deps)
    res = {}
    for n, m, g in ((3, 3, 2), (4, 4, 2), (3, 4, 2), (3, 3, 3)):
        res["%d x %d, g = %d" % (n, m, g)] = every_lag(n, m, g, 8)
    ok = all(r[4] == 0 and r[5] and r[6] == 0 and r[7] for rows in res.values() for r in rows if r[3])
    check("1 The theorem: doubling at every lag, from 3 x 3, 4 x 4, 3 x 4 at g = 2 and 3 x 3 at g = 3 to 96 x 96 rings or fewer: at every "
          "doubling lag and the lag after, no own cell depends on another ring's original cells and every contact only on the original "
          "rings it lies on", ok,
          {k: [(r[0], "%d x %d" % (r[1], r[2]), r[4], r[6], r[8]) for r in rows] for k, rows in res.items()})
    hz = {}
    for n in (3, 5):
        for P in (2, 3, 4, 6, 8):
            hz["%d x %d, P = %d" % (n, n, P)] = every_p(P, n, n, 2)
    check("2 Computed: doubling every P lags from 3 x 3 and 5 x 5 at g = 2 (to 96 x 96 rings or fewer), the reach of an original ring "
          "and the original rings that ever hear it", all(len(v["before each doubling"]) >= 3 for v in hz.values()), hz)
    ctl = {"%d x %d" % (n, m): static(n, m, 2, 40) for n, m in ((3, 3), (4, 4), (5, 5))}
    check("3 Control: without growth the reach of ring (0, 0) within 40 lags", True, ctl)
    result = {"ticket": "GROW-HORIZON-20261109-001A", "artifact_id": "GROW-HORIZON-20261109-001A-P001", "checks": OUT, "status": "passed"}
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
