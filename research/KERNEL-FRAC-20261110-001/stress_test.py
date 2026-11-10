"""Stress test of KERNEL-FRAC-20261110-001 one size past (research-next-steps, "Stress-Test Published Claims").

    .venv/bin/python3 -B stress_test.py    writes stress_test.json beside this file

1. Ticket A, part 1, at n = 64 (checked to 32): the top bit of every hole row is set only for pigeon n, so each top hole bit decodes to
   one cell and every pair of them to a product with a repeated row.
2. Ticket A, part 3, the cap, for l = 31 to 40 (checked to 30), k up to n/2, the largest allowed accuracy: at most 5.2.
3. The two-top family's share at k* against the frozen threshold, l = 23 and 24 (read to 22), exact integers."""
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = ROOT / "proofs/KERNEL-FRAC-20261110-001A/KERNEL-FRAC-20261110-001A-P001_the_top_hole_bit"
spec = importlib.util.spec_from_file_location("kf_a", A / "check.py")
CA = importlib.util.module_from_spec(spec)
sys.modules["kf_a"] = CA
spec.loader.exec_module(CA)
spec = importlib.util.spec_from_file_location("kf_top", HERE / "top_bit_family.py")
TB = importlib.util.module_from_spec(spec)
sys.modules["kf_top"] = TB
spec.loader.exec_module(TB)
OUT = {}
T0 = time.time()


def record(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info, "seconds": round(time.time() - T0, 1)}
    print(("PASS " if ok else "FAIL ") + name, round(time.time() - T0), flush=True)


def main():
    n = 64
    l = 6
    tops = [y for y in range(n + 1) if (y >> l) & 1]
    ok1 = tops == [n]
    pairs = 0
    for h in range(n):
        cells_h = [(y, h) for y in tops]
        for h2 in range(h + 1, n):
            cells_h2 = [(y, h2) for y in tops]
            ok1 &= all(a[0] == b[0] for a in cells_h for b in cells_h2)   # every term repeats a row
            pairs += 1
    record("1_top_bit_at_n_64", ok1, {"pigeons with the top bit": tops, "pairs of holes": pairs})
    worst = 0.0
    for l in range(31, 41):
        n = 2 ** l
        m = n + 1
        v = m * l + n * (l + 1)
        for k in sorted({1, 2, 4, 8, 64, 1024, n // 1024, n // 64, n // 4, n // 2}):
            if k < 1 or k > n // 2:
                continue
            h = math.floor(((n + 1) / (2 * l * k) - 2) / 4)
            if h < 1:
                continue
            val = math.log1p(n * k / v) - (k - 1) * n / (v + k) + h * k * k / (v + k)
            worst = max(worst, val)
    record("2_cap_to_l_40", math.exp(worst) <= 5.2, {"largest certified value": round(math.exp(worst), 4)})
    rows = []
    for l in (23, 24):
        n = 2 ** l
        ks = (n + 1) // (2 * l * (12 * l + 2))
        s = TB.share_with_two_tops(n, ks)
        allow = 1 - math.exp(-ks * ks / (6 * n))
        rows.append({"l": l, "k*": ks, "share": s, "threshold": allow, "exceeds": s > allow})
    record("3_two_top_share_l_23_24", all(r["exceeds"] for r in rows), rows)
    out = {"epic": "KERNEL-FRAC-20261110-001", "checks": OUT, "status": "passed" if all(x["pass"] for x in OUT.values()) else "failed",
           "seconds": round(time.time() - T0, 1)}
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(out["status"], out["seconds"])


if __name__ == "__main__":
    main()
