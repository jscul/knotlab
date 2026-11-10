"""WIDE-LEFT-20261110-001B-E001, finished after run.py was stopped (see contract.json; run.py is unchanged).

    .venv/bin/python3 -B finish.py    reads run.py's progress.txt, writes result.json

run.py finished Q1 at all three entries and Q2 at (4, 1) and (8, 1), then was stopped in Q2 at (16, 2): checking every top monomial of
U_0 (5,925) against every monomial (5,926) would take about 39 hours. Here Q2 at (16, 2) checks 60 top monomials drawn with a fixed seed
(30 of degree 2, 30 of degree 1) against every monomial of U_0, with run.py's own functions; Q3 is run.py's, unchanged. Q4 as frozen
sums e_k term by term, which for l above about 32 (k up to 10^17) does not finish; here it is summed term by term for l <= 32 and
bounded beyond by the sequential product of WIDE-LEFT-20261110-001A's Lemma 3 (a lower bound, so the check is conservative)."""
import importlib.util
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("wide_run", HERE / "run.py")
R = importlib.util.module_from_spec(spec)
sys.modules["wide_run"] = R
spec.loader.exec_module(R)


def q2_sample(W, E, P, hs, ps, k, count, seed):
    pigeons = [x for x in range(W.m) if x not in P]
    holes = [h for h in range(W.n) if h not in E]
    mons = W.monomials(pigeons, holes, k)
    rng = random.Random(seed)
    tops = rng.sample([M for M in mons if len(M) == 2], count // 2) + rng.sample([M for M in mons if len(M) == 1], count // 2)
    ok = True
    for M0 in tops:
        hstars, pstars = [list(s) for s in hs], [list(s) for s in ps]
        coords, hi, pi = [], 0, 0
        for (kind, r, b) in M0:
            if kind == "f":
                s = hstars[hi]; hi += 1
                coords.append(("f", r, b, (s[0], s[0] ^ (1 << b))))
            else:
                s = pstars[pi]; pi += 1
                park = hstars[hi][0]; hi += 1
                coords.append(("g", r, b, (s[0], s[0] ^ (1 << b)), park))
        for M in mons:
            if len(M) > len(M0):
                continue
            ok &= R.cube_value(W, M, coords) == ({frozenset(): 1} if M == M0 else {})
    return ok, len(tops)


def q4():
    import math
    rows = []
    for l in range(20, 61):
        n = 2 ** l
        k = n // (64 * l ** 3)
        h = math.floor(((n + 1) / (2 * l * k) - 2) / 4)
        v = 2 * n * l + n * (l + 1)
        if l <= 32:
            lr = R.log_ek(2 * n - k * (l + 2), l, n - 2 * k * (l + 1), l + 1, k) - R.log_binom(v + k, k)
        else:
            s = k * (l + 2) * l + 2 * k * (l + 1) ** 2
            lr = -(2 * k * s + (l + 2) * k * (k - 1) + 2 * k) / v
        val = lr + h * k * k / (v + k)
        rows.append({"l": l, "k": k, "h": h, "D >= 2h + l + 1": 4 * h + 1 >= 2 * h + l + 1, "log bound": val, "ratio to n / l^5": val / (n / l ** 5),
                     "summed": "term by term" if l <= 32 else "sequential lower bound"})
    return rows


def main():
    t0 = time.time()
    log = open(R.OUT / "progress.txt", "a")
    res = {"experiment": "WIDE-LEFT-20261110-001B-E001", "Q1": [], "Q2": [], "Q3": []}
    for line in open(R.OUT / "progress.txt"):
        if line.startswith("Q1 "):
            res["Q1"].append(json.loads(line[3:line.rindex("}") + 1]))
        elif line.startswith("Q2 ") and "sampled" not in line:
            parts = line.split()
            res["Q2"].append({"n": int(parts[1]), "k": int(parts[2]), "cubes": int(parts[4]), "identities hold": parts[3] == "True"})
    r, W, E, P, hs, ps = R.q1(16, 2)
    ok, cnt = q2_sample(W, E, P, hs, ps, 2, 60, 20261110)
    res["Q2"].append({"n": 16, "k": 2, "cubes": cnt, "sampled": "60 top monomials of 5,925, seed 20261110", "identities hold": ok})
    print("Q2 16 2 sampled", ok, cnt, round(time.time() - t0), file=log, flush=True)
    for n, k in ((4, 2), (8, 2)):
        q = R.q3(n, k)
        res["Q3"].append(q)
        print("Q3", json.dumps(q), round(time.time() - t0), file=log, flush=True)
    res["Q4"] = q4()
    res["Q1 holds"] = all(x["dim U_0 ∩ K_k"] == 0 for x in res["Q1"]) and len(res["Q1"]) == 3
    res["Q2 holds"] = all(x["identities hold"] for x in res["Q2"])
    res["Q3 below LP_{n+1}'s 0.73 and 0.49"] = res["Q3"][0]["fraction"] < 0.73 and res["Q3"][1]["fraction"] < 0.49
    res["Q4 positive from some l on, ratio bounded below"] = {
        "first l with a positive bound": next((x["l"] for x in res["Q4"] if x["log bound"] > 0), None),
        "smallest ratio over l >= 40": round(min(x["ratio to n / l^5"] for x in res["Q4"] if x["l"] >= 40), 6)}
    res["finished by"] = "finish.py after run.py was stopped in Q2 at (16, 2); Q2 there sampled"
    res["seconds"] = round(time.time() - t0, 1)
    (R.OUT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "Q4"}, indent=1))


if __name__ == "__main__":
    main()
