#!/usr/bin/env python3
"""Checks for CROSS-WHY-20261110-001B: balance is read on one territory.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
The reduced reading of territory_lib (one fundamental domain of the original lattice's translations, its rings' born cells only) is
compared with a full-state reading on GROW-CHOOSE-20261109-001A-E001's Run2 under BIRTH-RULE-20261109-001A-E001's double(run, t,
"open"), every born cell a variable, and with that experiment's readings(), the balance reading of the doubling census. Rings and
contacts are matched by their positions in the cyclic column and row lists, which both constructions order alike."""
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
import importlib.util  # noqa: E402
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "experiments/BIRTH-RULE-20261109-001A/BIRTH-RULE-20261109-001A-E001_birth_rules"))
_spec = importlib.util.spec_from_file_location(
    "birth_rule_run", ROOT / "experiments/BIRTH-RULE-20261109-001A/BIRTH-RULE-20261109-001A-E001_birth_rules/run.py")
BR = importlib.util.module_from_spec(_spec)
sys.modules["birth_rule_run"] = BR
_spec.loader.exec_module(BR)
import territory_lib as T  # noqa: E402

C = BR.C
T0 = time.time()
OUT = {}
DEPS = {
    "experiments/BIRTH-RULE-20261109-001A/BIRTH-RULE-20261109-001A-E001_birth_rules/run.py":
        "700c9ed85da8852dd0c0d1941031b063c116aa3afe29f22186aeb660df7dd6ce",
    "experiments/GROW-CHOOSE-20261109-001A/GROW-CHOOSE-20261109-001A-E001_dynamics_chosen_growth/choose_lib.py":
        "71e5e8829415d09533a8648fd615cf06b94e767258c383bd8b6624cb510741c4",
    "proofs/DOUBLE-BALANCE-20261109-001A/DOUBLE-BALANCE-20261109-001A-P001_doubling_every_lag_keeps_every_stage_balanced/manifest.json":
        "cc40bc02687e69af79c7c71b66feebc5df67ca24616a4ceb60aa76325860a082",
}
CASES = [(3, [6]), (3, [8]), (3, [12]), (3, [13]), (3, [12, 1]), (3, [12, 3]), (2, [2]), (2, [4]), (2, [5]), (5, [6]), (5, [8])]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:400], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def full_read(run, cap=1000000):
    """every (contact, ring) of the whole network: first lag at which the contact does not bind the ring, through a full cycle"""
    tb = run.tube
    rmask = {R: run.ringmask(R) for R in tb.rings}
    pairs = [(c, tb.rings[r]) for c, (ra, pa, rb, pb, law) in enumerate(tb.contacts) for r in (ra, rb)]
    s = list(run.state)
    fails = {}
    saved, power, lam = list(s), 1, 0
    for t in range(1, cap + 1):
        new = []
        for row in tb.M:
            v, x = 0, row
            while x:
                low = x & -x
                v ^= s[low.bit_length() - 1]
                x ^= low
            new.append(v)
        s = new
        for c, R in pairs:
            if (c, R) not in fails and not (s[c] & rmask[R]):
                fails[(c, R)] = t
        if s == saved:
            return fails, t
        lam += 1
        if lam == power:
            saved, power, lam = list(s), power * 2, 0
    return fails, None


def positions(tb):
    col = {x: i for i, x in enumerate(tb.cols)}
    row = {x: i for i, x in enumerate(tb.rows)}
    ring = lambda R: (col[R[0]], row[R[1]])                      # noqa: E731
    contact = lambda c: (tb.keys[c][1], col[tb.keys[c][2]], row[tb.keys[c][3]])   # noqa: E731
    return ring, contact


def one(g, runs):
    run = C.Run2(C.Tube2([0, 1, 2], [0, 1, 2], g))
    BR.double(run, 0, "open")
    t = 0
    for P in runs:
        for _ in range(P):
            run.step()
            t += 1
        old = BR.double(run, t, "open")
    full, per_full = full_read(run)
    bal_readings, _ = BR.readings(run, old)
    ring, contact = positions(run.tube)
    side = len(run.tube.cols)
    full_pos = {(contact(c), ring(R)): lag for (c, R), lag in full.items()}
    new_failing = sum(1 for (c, R) in full if R not in old)
    nr = T.NRun(g)
    nr.double(0)
    t2 = 0
    for P in runs:
        for _ in range(P):
            nr.step()
            t2 += 1
        nr.double(t2)
    red, per_red = nr.read()
    ring2, contact2 = positions(nr.tube)
    red_pos = {(contact2(c), ring2(R)): lag for (c, R), lag in red.items()}
    k = side // 3
    dom_full = {key: lag for key, lag in full_pos.items() if key[1][0] < k and key[1][1] < k}
    # every failure outside the domain is the translate of one inside it
    def translate(cc, r):
        dx, dy = r[0] - r[0] % k, r[1] - r[1] % k
        return (cc[0], (cc[1] - dx) % side, (cc[2] - dy) % side), (r[0] % k, r[1] % k)
    trans_ok = all(dom_full.get(translate(cc, r)) == lag for (cc, r), lag in full_pos.items())
    return {"side": side, "full failures": len(full), "reduced failures": len(red), "domain failures equal": dom_full == red_pos,
            "outside failures are translates": trans_ok, "balanced (readings)": bal_readings, "balanced (reduced)": not red,
            "periods": [per_full, per_red], "rings born at the stage that fail": new_failing}


def main():
    deps = {p: sha(p) for p in DEPS}
    check("0 dependencies bound by hash", all(DEPS[p] == deps[p] for p in DEPS), deps)
    res = {"g = %d, runs %s" % (g, runs): one(g, runs) for g, runs in CASES}
    ok = all(r["domain failures equal"] and r["outside failures are translates"] and r["balanced (readings)"] == r["balanced (reduced)"]
             for r in res.values())
    check("1 Lemma 1: the reduced reading equals the full-state reading on the domain, every other failure is a translate, and the "
          "balance verdict agrees with BIRTH-RULE's readings()", ok, res)
    check("2 Lemma 2: no ring born at a doubling fails in its stage", all(r["rings born at the stage that fail"] == 0 for r in res.values()),
          {k: r["rings born at the stage that fail"] for k, r in res.items()})
    result = {"ticket": "CROSS-WHY-20261110-001B", "artifact_id": "CROSS-WHY-20261110-001B-P001", "checks": OUT, "status": "passed"}
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
