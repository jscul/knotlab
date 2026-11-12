#!/usr/bin/env python3
"""Checks for ODD-FAMILY-20261112-001A (research/ODD-FAMILY-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part scan|verify|counts|explain|summary|referee [--write]
scan: every odd n from 33 to 59 and every prime from 61 to 199, both families. verify: for every set found to make a harmony, every
compatible word enumerated (none may differ from another in one place), least periods, the direct window check, the offsets' gcd.
counts: compatible words of H u 2H (H the fourth roots of 1) at every prime 41 to 199 that is 1 mod 4, capped at 200,000 words.
explain: the frozen tests of section 'One explanation attempt'. summary: F1 to F7. referee: fam_referee.py (fresh code)."""
import hashlib
import json
import os
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("fam_lib.py", "check.py", "fam_referee.py")] + \
       ["proofs/ODD-SEARCH-20261112-001A/ODD-SEARCH-20261112-001A-P001_pattern_sets/odd_lib.py", "research/ODD-FAMILY-20261112-001/preregistration.md"]



def is_prime(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


NS = list(range(33, 60, 2)) + [p for p in range(61, 200, 2) if is_prime(p)]
COUNT_PRIMES = [p for p in range(41, 200) if is_prime(p) and p % 4 == 1]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def scan_job(n):
    import fam_lib as F
    t = time.time()
    rows = F.scan(n)
    made = []
    for r in rows:
        if r["rigid"]:
            r = dict(r)
            r["stabiliser order"] = len(F.stabiliser(r["S"], n))
            r["doubled shape"] = F.doubled_shape(r["S"], n)
            r["steps up to sign"] = F.steps_up_to_sign(r["S"], n)
            made.append(r)
    return {"n": n, "sets": len(rows), "by family": {fam: sum(r["family"] == fam for r in rows) for fam in ("cosets", "doubled steps")},
            "satisfiable": sum(r["satisfiable"] for r in rows), "make a harmony": made, "seconds": round(time.time() - t, 1)}


def verify_job(arg):
    import fam_lib as F
    n, x = arg
    S = tuple(x["S"])
    v = F.rigidity_check(S, n, cap=10**6)
    return {"n": n, "family": x["family"], "S": x["S"], "stabiliser order": x["stabiliser order"], "doubled shape": x["doubled shape"],
            "enumeration": v, "window state breaking the n-repeat": F.window_check(S, n) is not None,
            "offsets gcd": F.offsets_gcd(S, n), "kinds": len(F.kinds(S, n))}


def count_job(p):
    import fam_lib as F
    S = F.h_and_double(p)
    H = next(h for h in F.subgroups_with_minus_one(p) if len(h) == 4)
    return {"p": p, "S": list(S), "count": F.count_orbits(S, p), "words fixed by every fourth root of 1": F.multiplier_invariant(S, p, H)}


def explain():
    import fam_lib as F
    out = {}
    p, S = 61, F.h_and_double(61)
    # X1: two shifts. 11 * 11 = -1 and 6 + 5 * 11 = 61, so x = a + 11 b identifies Z_61 with pairs (a, b) modulo (61, 0) and (-11, 1)
    out["X1 11^2 = -1 mod 61"] = (11 * 11) % 61 == 60
    out["X1 6 + 5*11 = 61"] = 6 + 5 * 11 == 61
    out["X1 S = {±1, ±2} u 11*{±1, ±2}"] = sorted({1, 2, 59, 60} | {(11 * s) % 61 for s in (1, 2, 59, 60)}) == list(S)
    v = F.rigidity_check(S, p)
    words = []
    from pysat.solvers import Solver
    with Solver(name="cadical153", bootstrap_with=F.O.nae_clauses(F.ap_patterns(S, p), p)) as s:
        while s.solve():
            m = s.get_model()
            x = tuple(int(m[i] > 0) for i in range(p))
            words.append(x)
            s.add_clause([-(i + 1) if x[i] else (i + 1) for i in range(p)])
    forbidden = ["000", "111", "01010", "10101"]

    def along(w, step):
        return "".join(str(w[(k * step) % p]) for k in range(p + 4))
    out["X1 every compatible word: along each shift (step 1, step 11) no 000, 111, 01010, 10101"] = all(
        not any(f in along(tuple(w[(r + k) % p] for k in range(p)), st) for f in forbidden) for w in words for r in range(p) for st in (1, 11))
    # X2: the symmetry. Words fixed exactly by x -> 11x and x -> -x; the 61 word's invariance up to a shift
    H = [1, 11, 50, 60]
    out["X2 compatible words"] = len(words)
    out["X2 fixed exactly by every fourth root of 1"] = sum(all(w[(u * x) % p] == w[x] for u in H for x in range(p)) for w in words)
    # X3: the difference-set check (the advisor's): the word fixed by H with fewer ones is 1 at 0 and on 7 cosets? log base 2
    fixed = [w for w in words if all(w[(u * x) % p] == w[x] for u in H for x in range(p))]
    res = []
    for w in fixed:
        ones, m = F.discrete_log_cosets(w, p, 2, H)
        zeros = sorted(set(range(m)) - set(ones))
        for name, D in (("ones", ones), ("zeros", zeros)):
            cnt = F.difference_set(D, m)
            res.append({"word weight": sum(w), "value at 0": w[0], "cosets": name, "D": D, "|D|": len(D),
                        "a difference set (every nonzero difference equally often)": len(set(cnt)) == 1, "difference counts": cnt})
    out["X3"] = res
    # X5: inheritance to 305 = 61 * 5: t with t^2 = -1 mod 305 and t = ±11 mod 61; S' = {±1, ±2, ±t, ±2t} mod 305
    n2 = 305
    ts = sorted(t for t in range(1, n2) if (t * t) % n2 == n2 - 1 and t % 61 in (11, 50))
    lift = []
    for t in ts:
        S2 = tuple(sorted({x % n2 for x in (1, 2, -1, -2, t, 2 * t, -t, -2 * t)}))
        w = fixed[0]
        wl = tuple(w[x % p] for x in range(n2))
        ok = all(not (wl[x] == wl[(x + d) % n2] == wl[(x + 2 * d) % n2]) for x in range(n2) for d in S2)
        pinned = not any(all(not (y[x] == y[(x + d) % n2] == y[(x + 2 * d) % n2]) for x in range(n2) for d in S2)
                         for y in (wl[:i] + (1 - wl[i],) + wl[i + 1:] for i in range(n2)))
        w1, w2 = F.test(S2, n2)
        lift.append({"t": t, "S'": list(S2), "lifted 61 word compatible": ok, "lifted word has no flippable residue": pinned,
                     "S' at 305: a compatible word": w1 is not None, "S' makes a harmony at 305": w1 is not None and w2 is None})
    out["X5 lift to 305"] = lift
    out["61 enumeration"] = v
    return out


def run_part(part):
    if part == "scan":
        with Pool(16) as pool:
            rows = pool.map(scan_job, sorted(NS, reverse=True), chunksize=1)
        return {"rows": sorted(rows, key=lambda r: r["n"])}
    if part == "verify":
        rows = json.loads((HERE / "result_scan.json").read_text())["checks"]["result"]["rows"]
        jobs = [(r["n"], x) for r in rows for x in r["make a harmony"]]
        with Pool(16) as pool:
            return {"sets that make a harmony": pool.map(verify_job, jobs, chunksize=1)}
    if part == "counts":
        with Pool(16) as pool:
            return {"rows": pool.map(count_job, COUNT_PRIMES, chunksize=1)}
    if part == "explain":
        return explain()
    if part == "referee":
        r = subprocess.run([sys.executable, "-B", str(HERE / "fam_referee.py")], capture_output=True, text=True)
        print(r.stdout[-3000:], r.stderr[-3000:])
        return json.loads((HERE / "referee.json").read_text())


def summary():
    import fam_lib as F
    rows = json.loads((HERE / "result_scan.json").read_text())["checks"]["result"]["rows"]
    made = [(r["n"], x) for r in rows for x in r["make a harmony"]]
    ver = json.loads((HERE / "result_verify.json").read_text())["checks"]["result"]["sets that make a harmony"]
    good = [v for v in ver if v["enumeration"] and v["enumeration"]["Hamming-1 pairs"] == 0 and not v["window state breaking the n-repeat"]]
    cnt = json.loads((HERE / "result_counts.json").read_text())["checks"]["result"]["rows"]

    def two_coset_with_double(x, n):
        H = [u for u in F.units(n) if all(((u * s) % n) in set(x["S"]) for s in x["S"])]
        if len(H) != 4 or len(x["S"]) != 8:
            return False
        S = set(x["S"])
        inv2 = pow(2, -1, n)
        return any(S == {(c * h) % n for h in H} | {(c * g * h) % n for h in H} for c in x["S"] for g in (2, inv2))
    made_primes_count = [c["p"] for c in cnt if c["count"] and c["count"]["orbits"] > 0 and c["count"]["orbits with a flippable residue"] == 0]
    return {
        "sets by n": {str(r["n"]): {"sets": r["sets"], "satisfiable": r["satisfiable"], "make a harmony": len(r["make a harmony"])} for r in rows},
        "sets that make a harmony": [{"n": n, "family": x["family"], "S": x["S"], "stabiliser order": x["stabiliser order"]} for n, x in made],
        "verified (enumerated, no two words one place apart, window check, by fam_lib)": len(good), "of": len(ver),
        "F1 none with at most two steps up to sign": all(x["steps up to sign"] > 2 for n, x in made),
        "F2 every one is {±s, ±2s, ±t} or {±s, ±2s, ±t, ±2t}": all(x["doubled shape"] for n, x in made),
        "F3 none whose stabiliser has order >= 6": all(x["stabiliser order"] < 6 for n, x in made),
        "F4 stabiliser of order 4: only H u 2H or H u H/2, up to a multiplier": all(x["stabiliser order"] != 4 or two_coset_with_double(x, n) for n, x in made),
        "F5 counts of H u 2H": {str(c["p"]): c["count"] for c in cnt},
        "F5 primes where H u 2H makes a harmony": made_primes_count,
        "F6 none at the odd n 33 to 59": not any(n <= 59 for n, x in made),
        "F7 one at a prime other than 61": sorted({n for n, x in made if n != 61 and is_prime(n)}),
        "least periods of the states of the harmonies found": sorted({q for v in good for q in v["enumeration"]["minimal periods"]}),
        "unsplit (offsets gcd 1)": sorted({v["n"] for v in good if v["offsets gcd"] == 1}),
    }


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    part = sys.argv[sys.argv.index("--part") + 1]
    write = "--write" in sys.argv
    res = summary() if part == "summary" else run_part(part)
    res = {"dependencies": {p: sha(p) for p in DEPS}, "result": res, "seconds": round(time.time() - T0, 1)}
    path = HERE / ("result_%s.json" % part if part != "summary" else "result.json")
    if write:
        path.write_text(json.dumps({"status": "passed", "checks": res}, indent=1, default=str) + "\n")
        print("wrote", path, round(time.time() - T0, 1), "s")
    else:
        old = json.loads(path.read_text())["checks"]
        same = json.dumps(old["result"], sort_keys=True, default=str) == json.dumps(json.loads(json.dumps(res["result"], default=str)), sort_keys=True)
        print("result reproduced" if same else "result differs")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
