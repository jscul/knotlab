#!/usr/bin/env python3
"""Run ROUND-READ-20261110-001A-E001 (frozen contract beside this file): does growth round the reading?

    .venv/bin/python3 -B run.py
On round_lib beside this file (checked in part C against METRIC-GROW-20261110-001A-E001's metric_lib). Writes
artifacts/ROUND-READ-20261110-001A/ROUND-READ-20261110-001A-E001_does_growth_round_the_reading/run/result.json."""
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "experiments/METRIC-GROW-20261110-001A/METRIC-GROW-20261110-001A-E001_time_length_while_growing"))
import metric_lib as M  # noqa: E402
import round_lib as RL  # noqa: E402

OUT = ROOT / "artifacts/ROUND-READ-20261110-001A/ROUND-READ-20261110-001A-E001_does_growth_round_the_reading/run"
READINGS = ("T", "T1", "L", "L1")


def window(n, g):
    return 4 * g * 2 * (n // 2) + 9 * g + 2      # conformal time by which Theorem 2 has every ring reached


def families():
    jobs = []
    for n, g in ((13, 3), (21, 3), (41, 3), (13, 2), (13, 5)):
        W = window(n, g)
        jobs.append((n, g, [W], "baseline"))
        for P1 in (2, 4, 8, 12, 16, 20, 24, 28, 32, 40, 48, 56):
            jobs.append((n, g, [P1, math.ceil(2 * (W - P1))], "two runs"))
        if n <= 21:
            for P in (8, 12, 16, 24, 32, 48):
                for m in (2, 3):
                    done = sum(P * 2.0 ** -j for j in range(m))
                    jobs.append((n, g, [P] * m + [math.ceil(2 ** m * (W - done))], "pauses then a long run"))
    return jobs


def lsq_slope(pts):
    if len(pts) < 3:
        return None
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den


def one(job):
    n, g, runs, kind = job
    t0 = time.time()
    first, D, t_end = RL.readings(n, g, runs)
    phi = RL.conformal(D)
    out = {"n": n, "g": g, "runs": runs, "kind": kind, "doublings": D, "conformal length": phi(t_end)}
    lab = lambda x, y: (x % n, y % n)   # noqa: E731
    for key in READINGS:
        lag = first[key]
        gaps = []
        for d in range(2, n // 2 + 1, 2):
            m = d // 2
            diag = [lag[lab(sx * m, sy * m)] for sx in (1, -1) for sy in (1, -1) if lab(sx * m, sy * m) in lag]
            axis = [lag[lab(*v)] for v in ((d, 0), (-d, 0), (0, d), (0, -d)) if lab(*v) in lag]
            if diag and axis:
                gaps.append((d, phi(min(diag)) - phi(min(axis))))
        out[key] = {"gaps": gaps, "slope": lsq_slope(gaps), "heard": len(lag)}
    out["plain holes (T reached, L never)"] = sum(1 for Y in first["T"] if Y not in first["L"])
    out["plain holes (T1 reached, L1 never)"] = sum(1 for Y in first["T1"] if Y not in first["L1"])
    out["seconds"] = round(time.time() - t0, 1)
    return out


def check_c(job):
    n, g, runs = job
    f, D, t = RL.readings(n, g, runs)
    r = M.run_schedule(n, g, runs, read_balance=False)
    return all(f[k] == r[k] for k in ("T", "T1", "L"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    cases = [(5, 3, [12, 28]), (5, 3, [28, 1]), (5, 3, [35, 1]), (3, 3, [12, 1]), (5, 2, [8, 20]), (5, 5, [20, 40]), (7, 3, [40, 8])]
    with Pool(6) as pool:
        agree = pool.map(check_c, cases, chunksize=1)
        print("C", sum(agree), "of", len(cases), flush=True)
        rows = list(pool.imap(one, families(), chunksize=1))
    summary = {}
    for n, g in ((13, 3), (21, 3), (41, 3), (13, 2), (13, 5)):
        sub = [r for r in rows if r["n"] == n and r["g"] == g]
        s = {"schedules": len(sub)}
        for key in READINGS:
            gaps = [gp for r in sub for d, gp in r[key]["gaps"]]
            slopes = [r[key]["slope"] for r in sub if r[key]["slope"] is not None]
            s[key] = {"gap range": [min(gaps, default=None), max(gaps, default=None)],
                      "slope range": [min(slopes, default=None), max(slopes, default=None)],
                      "schedules with slope <= -g/2": sum(1 for x in slopes if x <= -0.5 * g),
                      "schedules with slope >= g/2": sum(1 for x in slopes if x >= 0.5 * g)}
        base = [r for r in sub if r["kind"] == "baseline"]
        s["baseline slopes"] = {key: base[0][key]["slope"] for key in READINGS} if base else None
        s["plain holes"] = [sum(r["plain holes (T reached, L never)"] for r in sub), sum(r["plain holes (T1 reached, L1 never)"] for r in sub)]
        summary["%d x %d, g = %d" % (n, n, g)] = s
    result = {"experiment_id": "ROUND-READ-20261110-001A-E001", "code agreement (C)": [sum(agree), len(cases)], "summary": summary,
              "rows": rows, "seconds": round(time.time() - t0)}
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(summary, indent=1), round(time.time() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
