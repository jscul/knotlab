#!/usr/bin/env python3
"""Checks for EVEN-PERIOD-20261112-001A (research/EVEN-PERIOD-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part census|control|summary|referee [--write]
census: every Lyndon word of odd length p = 3 .. 29 (one per orbit of minimal period p): its certificate class (lemma 3), and for
every word u that is not its own certificate, the certificate c and residue found by SAT. control: the 11 orbit words of
not-all-equal harmonies found by HARMONY-ARITH-20261112-001 at spans 2 to 6 must have NO certificate (lemma 3's consequence).
summary: E1, E2 and the control. referee: even_referee.py (fresh code)."""
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("even_lib.py", "even_referee.py")] + ["research/EVEN-PERIOD-20261112-001/preregistration.md"]
HARM = ROOT / "proofs/HARMONY-ARITH-20261112-001A/HARMONY-ARITH-20261112-001A-P001_binding_and_harmonies/result_stitches.json"
PERIODS = list(range(3, 30, 2))


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def census_job(p):
    import even_lib as E
    t = time.time()
    tally, others, none = Counter(), [], []
    for u in E.words(p):
        k, cert, nG = E.certify(u)
        tally[k] += 1
        if k == "other":
            others.append({"u": "".join(map(str, u)), "c": "".join(map(str, cert[0])), "residue": cert[1], "pairs": nG})
        elif k == "none":
            none.append("".join(map(str, u)))
    return {"p": p, "tally": dict(tally), "certified by another word": others, "no certificate": none, "seconds": round(time.time() - t, 1)}


def run_part(part):
    import even_lib as E
    import numpy as np
    if part == "census":
        with Pool(len(PERIODS)) as pool:
            rows = pool.map(census_job, sorted(PERIODS, reverse=True), chunksize=1)
        return {"rows": sorted(rows, key=lambda r: r["p"])}
    if part == "control":
        words = json.loads(HARM.read_text())["checks"]["result"]["orbits"]["NAE"]
        out = []
        for w in words:
            k, cert, nG = E.certify(np.array([int(x) for x in w], dtype=np.int8))
            out.append({"word": w, "period": len(w), "class": k, "certificate": None if cert is None else str(cert)})
        return {"harmony words": out}
    if part == "referee":
        r = subprocess.run([sys.executable, "-B", str(HERE / "even_referee.py")], capture_output=True, text=True)
        print(r.stdout[-3000:], r.stderr[-3000:])
        return json.loads((HERE / "referee.json").read_text())


def summary():
    rows = json.loads((HERE / "result_census.json").read_text())["checks"]["result"]["rows"]
    ctrl = json.loads((HERE / "result_control.json").read_text())["checks"]["result"]["harmony words"]
    frozen = [r for r in rows if r["p"] >= 21]
    return {
        "words by period": {str(r["p"]): r["tally"] for r in rows},
        "E1 every odd-period word of period 21 to 29 has a certificate": all(not r["no certificate"] for r in frozen),
        "E2 replay: every odd-period word of period 3 to 19 has a certificate": all(not r["no certificate"] for r in rows if r["p"] <= 19),
        "words with no certificate": {str(r["p"]): r["no certificate"] for r in rows if r["no certificate"]},
        "words certified by another word, by period": {str(r["p"]): len(r["certified by another word"]) for r in rows},
        "control: no harmony word has a certificate": all(c["class"] in ("none",) for c in ctrl),
        "control classes": Counter(c["class"] for c in ctrl),
        "seconds by period": {str(r["p"]): r["seconds"] for r in rows},
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
