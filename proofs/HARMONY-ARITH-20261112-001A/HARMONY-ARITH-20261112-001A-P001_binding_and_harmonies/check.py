#!/usr/bin/env python3
"""Checks for HARMONY-ARITH-20261112-001A (research/HARMONY-ARITH-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part harmonies|stitches|summary|referee [--write]
harmonies: every one-shift pattern of one to three knot kinds with span 2 to 10, under the four laws of harm_lib (exact). stitches:
every pair of harmony orbits found at span 2 to 6 under NAE (and, as the control law, under odd parity), with each of the 48 stitch
kinds and 4 overlaps of offsets 0 to 3 (exact). summary: H1 to H3, M, R1, R2 and the controls. referee: harm_referee.py (fresh code)."""
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("harm_lib.py", "harm_referee.py")] + ["research/HARMONY-ARITH-20261112-001/preregistration.md"]
SPANS, STITCH_SPANS = range(2, 11), range(2, 7)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def harmony_job(job):
    import harm_lib as H
    W, law = job
    rows = []
    for S in H.patterns(W):
        c, cycles = H.classify(W, S, law)
        if c == "harmony":
            rows.append({"kinds": S, "offset gcd": H.offset_gcd(S), "periods": sorted(len(w) for w in cycles),
                         "antiperiodic": [H.antiperiodic(w) for w in cycles],
                         "words": ["".join(map(str, H.canon(w))) for w in cycles] if W in STITCH_SPANS else None})
        else:
            rows.append({"kinds": S, "class": c})
    return {"span": W, "law": law, "rows": rows}


def stitch_job(job):
    import harm_lib as H
    law, u, v = job
    U, V = [int(c) for c in u], [int(c) for c in v]
    out = {}
    for bk in H.stitch_kinds():
        g, alive = H.stitched_offsets(U, V, bk, law)
        out["%s %s" % (bk[0], ",".join(map(str, bk[1])))] = alive
    return {"law": law, "u": u, "v": v, "gcd": math.gcd(len(u), len(v)), "surviving": out}


def run_part(part):
    import harm_lib as H
    if part == "harmonies":
        jobs = sorted(((W, law) for W in SPANS for law in H.LAWS), key=lambda j: -j[0])
        with Pool(16) as pool:
            res = pool.map(harmony_job, jobs, chunksize=1)
        return {"cells": sorted(res, key=lambda r: (r["law"], r["span"]))}
    if part == "stitches":
        cells = json.loads((HERE / "result_harmonies.json").read_text())["checks"]["result"]["cells"]
        words = defaultdict(set)
        for c in cells:
            if c["law"] in ("NAE", "odd parity") and c["span"] in STITCH_SPANS:
                for r in c["rows"]:
                    for w in r.get("words") or []:
                        words[c["law"]].add(w)
        jobs = [(law, u, v) for law in ("NAE", "odd parity") for u in sorted(words[law]) for v in sorted(words[law])]
        with Pool(16) as pool:
            res = pool.map(stitch_job, jobs, chunksize=4)
        return {"orbits": {law: sorted(ws) for law, ws in words.items()}, "pairs": res}
    if part == "referee":
        out = subprocess.run([sys.executable, "-B", str(HERE / "harm_referee.py")], capture_output=True, text=True)
        print(out.stdout[-3000:], out.stderr[-3000:])
        return json.loads((HERE / "referee.json").read_text())


def v2(n):
    return (n & -n).bit_length() - 1


def summary():
    cells = json.loads((HERE / "result_harmonies.json").read_text())["checks"]["result"]["cells"]
    B = json.loads((HERE / "result_stitches.json").read_text())["checks"]["result"]
    tally = {}
    for c in cells:
        t = tally.setdefault(c["law"], {})
        h = [r for r in c["rows"] if "periods" in r]
        per = Counter(p for r in h for p in r["periods"])
        t[str(c["span"])] = {"patterns": len(c["rows"]), "harmonies": len(h), "periods": dict(sorted(per.items())),
                             "states antiperiodic": sum(a for r in h for a in r["antiperiodic"]),
                             "states": sum(len(r["periods"]) for r in h),
                             "connected harmonies with a state not antiperiodic": sum(1 for r in h if r["offset gcd"] == 1 and not all(r["antiperiodic"]))}
    late = [str(W) for W in range(7, 11)]
    nae_odd = {W: sum(n for p, n in tally["NAE"][W]["periods"].items() if int(p) % 2) for W in late}
    H1 = all(v == 0 for v in nae_odd.values())
    H2 = all(tally["NAE"][W]["connected harmonies with a state not antiperiodic"] == 0 for W in late)
    H3a = all(any(int(p) % 2 for p in tally["odd parity"][W]["periods"]) for W in late)
    H3b = all(all(int(p) % 3 == 0 for p in tally["exactly one"][W]["periods"]) for W in late)
    # stitches
    pairs = B["pairs"]
    M_fail, M_tested, free_fail = [], 0, []
    by_period = defaultdict(set)
    divides = defaultdict(lambda: True)
    for r in pairs:
        p, q = len(r["u"]), len(r["v"])
        anti = all(r["u"][(i + p // 2) % p] != r["u"][i] for i in range(p)) if p % 2 == 0 else False
        antv = all(r["v"][(i + q // 2) % q] != r["v"][i] for i in range(q)) if q % 2 == 0 else False
        for bk, alive in r["surviving"].items():
            if r["law"] == "NAE" and anti and antv and v2(p) != v2(q):
                M_tested += 1
                if len(alive) % 2:
                    M_fail.append((r["u"], r["v"], bk, alive))
            by_period[(r["law"], bk, p, q)].add(len(alive))
            exists = len(alive) > 0
            reads = (p % q == 0) or (q % p == 0)
            if exists != reads:
                divides[(r["law"], bk)] = False
    R1_words_matter = sorted("%s | %s | %d,%d" % (law, bk, p, q) for (law, bk, p, q), s in by_period.items() if len(s) > 1)
    R1_testable = sum(1 for (law, bk, p, q), s in by_period.items() if law == "NAE")
    R2_readers = sorted("%s | %s" % k for k, ok in divides.items() if ok)
    parity_odd_with_diff_v2 = sum(1 for r in pairs if r["law"] == "odd parity" and v2(len(r["u"])) != v2(len(r["v"]))
                                  for bk, alive in r["surviving"].items() if len(alive) % 2)
    return {
        "harmonies by law and span": tally,
        "H1 NAE harmonies have only even periods at spans 7 to 10": H1, "odd NAE periods by span": nae_odd,
        "H2 connected NAE harmonies are antiperiodic at spans 7 to 10": H2,
        "H3a odd parity has an odd period at every span 7 to 10": H3a,
        "H3b exactly-one periods are multiples of 3 at spans 7 to 10": H3b,
        "orbits stitched": {law: len(ws) for law, ws in B["orbits"].items()},
        "M mirror pairing holds (NAE, antiperiodic, different powers of 2)": not M_fail, "M cases tested": M_tested, "M failures": M_fail[:10],
        "R1 the orbit matters beyond (p, q) (cells with more than one count)": len(R1_words_matter), "R1 examples": R1_words_matter[:10],
        "R2 stitch kinds whose existence is exactly 'one period divides the other'": R2_readers,
        "control: odd parity stitches with different powers of 2 and an odd number of surviving offsets": parity_odd_with_diff_v2,
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
