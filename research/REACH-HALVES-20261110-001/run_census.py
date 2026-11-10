"""REACH-HALVES-20261110-001B, B2: the full-reach census one size past, every side from 3 to 130.

    python3 -B run_census.py            compiles census.c, runs every side, writes census.json and census_log.txt beside this file

Powers of two run exactly over P = e(2n - 1) steps (e = 4, 8, 16, 16, 32, 32 at 4 to 128, the periods of
FULL-REACH-PROOF-20261108-001 and LINEAR-ROOTS-20261109-001), and census.c checks that A^P is the identity, so the OR of the rows
of A^0, ..., A^P is the exact reach set. Other sides stop as soon as every contact has met every ring (a certificate of full
reach), with a cap of 40,000 steps."""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXE = HERE / "census_bin"
E = {4: 4, 8: 8, 16: 16, 32: 16, 64: 32, 128: 32}


def main():
    subprocess.run(["gcc", "-O3", "-march=native", "-o", str(EXE), str(HERE / "census.c")], check=True)
    out, log = {}, open(HERE / "census_log.txt", "w")
    t0 = time.time()
    for n in range(3, 131):
        t1 = time.time()
        if n in E:
            args = [str(EXE), str(n), "exact", str(E[n] * (2 * n - 1))]
        else:
            args = [str(EXE), str(n), "early", "40000"]
        res = subprocess.run(args, capture_output=True, text=True, check=True).stdout
        rec = {"mode": args[2], "seconds": round(time.time() - t1, 2)}
        m = re.search(r"FULL REACH certified at step (\d+)", res)
        if m:
            rec.update(full_reach=True, certified_at_step=int(m.group(1)))
        else:
            m = re.search(r"after (\d+) steps: contacts (\d+), missing a ring (\d+), missing some contact (\d+)", res)
            rec.update(full_reach=int(m.group(3)) == 0, steps=int(m.group(1)), contacts=int(m.group(2)),
                       missing_a_ring=int(m.group(3)), missing_some_contact=int(m.group(4)))
            rec["period_verified"] = "IS the identity" in res
            rec["contacts_missing_rings"] = re.findall(r"contact \((\d+),(\d+)\) misses (\d+) rings:([^\n]*)", res)
        out[str(n)] = rec
        log.write("n %d %s\n" % (n, json.dumps({k: v for k, v in rec.items() if k != "contacts_missing_rings"})))
        log.flush()
    fails = [int(n) for n, r in out.items() if not r["full_reach"]]
    pred = {}
    for n in (8, 16, 32, 64, 128):
        r = out[str(n)]
        want = sorted((X + 0, X + 1) for X in range(n + 2, 2 * n - 5, 4))
        got = sorted((int(a), int(b)) for a, b, k, _ in r["contacts_missing_rings"] if (int(a) - int(b)) == -1 and int(a) > n)
        pred[str(n)] = {"missing a ring == n - 4": r["missing_a_ring"] == n - 4,
                        "missing some contact == 3n + 20": r["missing_some_contact"] == 3 * n + 20,
                        "each misses exactly three rings": all(int(k) == 3 for _, _, k, _ in r["contacts_missing_rings"]),
                        "the corner-(0,0) failures are (X, X+1), X = n+2, n+6, ..., 2n-6": got == want,
                        "period verified": r["period_verified"]}
    summary = {"sides": [3, 130], "sides failing full reach": fails,
               "prediction (fails exactly at 8, 16, 32, 64, 128)": fails == [8, 16, 32, 64, 128],
               "failing-set predictions at the powers of two": pred, "seconds": round(time.time() - t0, 1), "by side": out}
    (HERE / "census.json").write_text(json.dumps(summary, indent=1) + "\n")
    log.write("done in %.1f s; failing sides %s\n" % (time.time() - t0, fails))
    log.close()


if __name__ == "__main__":
    main()
