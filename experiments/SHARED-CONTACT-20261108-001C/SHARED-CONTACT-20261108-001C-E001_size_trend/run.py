"""SHARED-CONTACT-20261108-001C-E001: persistence of shared contacts as the rings grow (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the measurement; writes artifacts/SHARED-CONTACT-20261108-001C/
                                          SHARED-CONTACT-20261108-001C-E001_size_trend/run/rows.json and result.json
    .venv/bin/python3 -B run.py --pilot   times the largest size on a few configurations and prints no verdicts
The T-step maps are told apart by 16-byte digests, and a repeated digest is confirmed by recomputing the earlier map, so every
verdict reported as decided is exact."""
from __future__ import annotations

import hashlib
import json
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/SHARED-CONTACT-20261108-001A/SHARED-CONTACT-20261108-001A-P001_when_a_shared_contact_binds_at_the_first_step"))
sys.path.insert(0, str(ROOT / "proofs/TIME-KNOTS-20261107-001A/TIME-KNOTS-20261107-001A-P001_knots_across_time_are_minimal_decisive_sets"))
import shared_contact_lib as S  # noqa: E402
import time_knots_lib as K  # noqa: E402

P = S.P
OUT = ROOT / "artifacts" / "SHARED-CONTACT-20261108-001C" / "SHARED-CONTACT-20261108-001C-E001_size_trend" / "run"
SIZES = tuple((m, m + 1) for m in range(3, 9))
CAP = 4096
COLUMNS = ["family", "rule", "m", "n", "law", "class", "first lag without binding", "repeat from", "period", "lags computed"]


def lags_hashed(nxt, test, cap):
    cur = np.arange(len(nxt), dtype=np.int64)
    seen = {}
    verdicts = []
    for T in range(1, cap + 1):
        cur = nxt[cur]
        key = hashlib.blake2b(cur.tobytes(), digest_size=16).digest()
        if key in seen:
            T1 = seen[key]
            back = np.arange(len(nxt), dtype=np.int64)
            for _ in range(T1):
                back = nxt[back]
            if (back == cur).all():
                return verdicts, T1, T - T1
            raise RuntimeError("digest collision")
        seen[key] = T
        verdicts.append(test((cur & 1).astype(np.uint8)))
    return verdicts, None, None


def job(args):
    family, r, m, n, law = args
    if family == "proposals":
        nxt = P.shared_state_maps(r, m, r, n, law)
    else:
        nxt = S.selfblind_state_map(r, m, r, n, S.parity_table(law, law))
    verdicts, T1, period = lags_hashed(nxt, lambda F: S.fast_binds(F, m, n), CAP)
    first_fail = next((T for T, ok in enumerate(verdicts, 1) if not ok), None)
    return [family, r, m, n, law, S.classify(verdicts, T1, period), first_fail, T1, period, len(verdicts)]


def main():
    t0 = time.time()
    reps = K.classes()
    if "--pilot" in sys.argv:
        for args in (("proposals", 30, 8, 9, 6), ("self-blind", 110, 8, 9, 6), ("self-blind", 184, 8, 9, 8), ("proposals", 90, 8, 9, 9)):
            s = time.time()
            row = job(args)
            print("pilot", args, "lags computed", row[-1], "seconds", round(time.time() - s, 2))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [("proposals", r, m, n, g2) for (m, n) in SIZES for r in reps for g2 in P.PARITIES]
    jobs += [("self-blind", r, m, n, u) for (m, n) in SIZES for r in reps for u in S.NONCONSTANT_TWO]
    jobs.sort(key=lambda j: -j[2])                        # the largest sizes first, for the pool's balance
    with Pool(16) as pool:
        rows = pool.map(job, jobs, chunksize=1)
    rec = [dict(zip(COLUMNS, row)) for row in rows]
    # control: the sizes shared with PROCESS-CONTACT-20261108-001B and SHARED-CONTACT-20261108-001B give the same classes
    prev_prop = json.loads((ROOT / "artifacts/PROCESS-CONTACT-20261108-001B/PROCESS-CONTACT-20261108-001B-E001_figure_eight_census/run/rows.json").read_text())
    pp = {(r["rule_a"], r["m"], r["n"], r["combiner"]): r["class"] for r in prev_prop if r["kind"] == "alike"}
    prev_sb = json.loads((ROOT / "artifacts/SHARED-CONTACT-20261108-001B/SHARED-CONTACT-20261108-001B-E001_self_blind_census/run/rows.json").read_text())
    cols = prev_sb["columns"]
    ps = {(row[0], row[1], row[2], row[3]): row[5] for row in prev_sb["rows"] if row[3] == row[4]}
    agree = []
    for r in rec:
        key = (r["rule"], r["m"], r["n"], r["law"])
        if r["family"] == "proposals" and key in pp and r["class"] != "undecided":
            agree.append(pp[key] == r["class"])
        if r["family"] == "self-blind" and key in ps and r["class"] != "undecided" and ps[key] != "undecided":
            agree.append(ps[key] == r["class"])
    controls = {"configurations shared with the two earlier censuses get the same class": bool(agree) and all(agree),
                "every self-blind configuration binds at lag 1 (Theorem 2)": all(r["first lag without binding"] != 1 for r in rec
                                                                                  if r["family"] == "self-blind")}
    trend = {}
    for fam in ("proposals", "self-blind"):
        trend[fam] = {}
        for (m, n) in SIZES:
            sel = [r for r in rec if r["family"] == fam and (r["m"], r["n"]) == (m, n)]
            c = Counter(r["class"] for r in sel)
            trend[fam][f"{m} + {n}"] = {"configurations": len(sel), "binds at every lag": c["binds at every lag"],
                                        "fraction": round(c["binds at every lag"] / len(sel), 4), "undecided": c["undecided"],
                                        "rules with a persistent law": len({r["rule"] for r in sel if r["class"] == "binds at every lag"})}
    frozen = {51, 204}
    trend_unfrozen = {fam: {k: round(sum(1 for r in rec if r["family"] == fam and f"{r['m']} + {r['n']}" == k and r["rule"] not in frozen
                                         and r["class"] == "binds at every lag")
                                     / max(1, sum(1 for r in rec if r["family"] == fam and f"{r['m']} + {r['n']}" == k and r["rule"] not in frozen)), 4)
                            for k in trend[fam]} for fam in trend}
    persistent_rules = {fam: {k: sorted({r["rule"] for r in rec if r["family"] == fam and f"{r['m']} + {r['n']}" == k
                                         and r["class"] == "binds at every lag"}) for k in trend[fam]} for fam in trend}
    every_size = {fam: sorted(set.intersection(*[set(v) for v in persistent_rules[fam].values()])) for fam in trend}
    result = {"experiment": "SHARED-CONTACT-20261108-001C-E001", "configurations": len(rec), "controls": controls,
              "controls_ok": all(controls.values()), "trend": trend,
              "fraction binding at every lag without the frozen rings (rules 51 and 204)": trend_unfrozen,
              "rules with a persistent law at every size": every_size, "persistent rules by size": persistent_rules,
              "seconds": round(time.time() - t0, 1)}
    (OUT / "rows.json").write_text(json.dumps({"columns": COLUMNS, "rows": rows}) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "persistent rules by size"}, indent=1)[:6000])


if __name__ == "__main__":
    main()
