#!/usr/bin/env python3
"""One size past for SHARED-CONTACT-20261108-001's computed claims (research-next-steps, "Stress-Test Published Claims").

    .venv/bin/python3 -B research/SHARED-CONTACT-20261108-001/stress_test.py quick   ticket A's lag-1 criteria one size past
                                                                                 (stress_test_quick.json)
    .venv/bin/python3 -B research/SHARED-CONTACT-20261108-001/stress_test.py nine    ticket C's measurement at 9 + 10 cells
                                                                                 (stress_test_nine.json; long-running, registered in
                                                                                 docs/LONG_RUNNING.md as SHARED-CONTACT-S1)
Reuses ticket A's library and ticket C's run.py (job), with 16 worker processes for the second."""
import json
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/SHARED-CONTACT-20261108-001A/SHARED-CONTACT-20261108-001A-P001_when_a_shared_contact_binds_at_the_first_step"))
sys.path.insert(0, str(ROOT / "proofs/TIME-KNOTS-20261107-001A/TIME-KNOTS-20261107-001A-P001_knots_across_time_are_minimal_decisive_sets"))
sys.path.insert(0, str(ROOT / "experiments/SHARED-CONTACT-20261108-001C/SHARED-CONTACT-20261108-001C-E001_size_trend"))
import shared_contact_lib as S  # noqa: E402
import time_knots_lib as K  # noqa: E402

P = S.P
T0 = time.time()


def quick():
    reps = K.classes()
    rng = random.Random(20261108)
    mism = tested = 0
    m, n = 5, 6
    for ra in reps:
        for rb in rng.sample(reps, 12) + [ra]:
            for g2 in range(16):
                F = P.shared_maps(ra, m, rb, n, g2, 1)[0]
                tested += 1
                mism += S.fast_binds(F, m, n) != S.proposals_bind_at_lag1(ra, rb, g2)
    sb_tested = sb_mism = 0
    m, n = 4, 5
    for _ in range(3000):
        h, ra, rb = rng.randrange(1 << 16), rng.choice(reps), rng.choice(reps)
        F = S.selfblind_maps(ra, m, rb, n, h, 1)[0]
        sb_tested += 1
        sb_mism += S.fast_binds(F, m, n) != S.selfblind_binds_at_lag1(h)
    out = {"Theorem 1 at 5 + 6 cells (every class with itself and 12 random partners, 16 combiners)": {"maps": tested, "mismatches": mism},
           "Theorem 2 at 4 + 5 cells (3,000 random laws and ring rules)": {"maps": sb_tested, "mismatches": sb_mism},
           "seconds": round(time.time() - T0, 1)}
    (HERE / "stress_test_quick.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


def nine():
    import run as C
    reps = K.classes()
    jobs = [("proposals", r, 9, 10, g2) for r in reps for g2 in P.PARITIES]
    jobs += [("self-blind", r, 9, 10, u) for r in reps for u in S.NONCONSTANT_TWO]
    with Pool(16) as pool:
        rows = pool.map(C.job, jobs, chunksize=1)
    rec = [dict(zip(C.COLUMNS, row)) for row in rows]
    out = {"rings": "9 + 10", "configurations": len(rec)}
    for fam in ("proposals", "self-blind"):
        sel = [r for r in rec if r["family"] == fam]
        c = Counter(r["class"] for r in sel)
        out[fam] = {"classes": dict(c), "fraction binding at every lag": round(c["binds at every lag"] / len(sel), 4),
                    "rules with a persistent law": len({r["rule"] for r in sel if r["class"] == "binds at every lag"}),
                    "lag-1 binding as Theorem 1 or 2 says": all(
                        (r["first lag without binding"] != 1) == (fam == "self-blind" or S.proposals_bind_at_lag1(r["rule"], r["rule"], r["law"]))
                        for r in sel)}
    out["seconds"] = round(time.time() - T0, 1)
    (HERE / "stress_test_nine.json").write_text(json.dumps(out, indent=1) + "\n")
    (HERE / "stress_test_nine_rows.json").write_text(json.dumps({"columns": C.COLUMNS, "rows": rows}) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"quick": quick, "nine": nine}[sys.argv[1]]()
