#!/usr/bin/env python3
"""Checks for COUNT-NOTE-20261107-001B: the sphere's count has a unary Sherali-Adams refutation of degree 3.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv. Single process; under a minute. The solver record in solvers/ is read, not rerun: rerunning it
needs the packages exact and pycryptosat, which the repository's .venv does not carry (see solvers/README.md)."""
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import sa_lib as S  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:400], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # 1. the certificate, for k = 2..8
    rows, ok1 = {}, True
    for k in range(2, 9):
        terms, info = S.certificate(k)
        pos = {frozenset(J.items()) for c, J in terms if c > 0}
        info["coefficients"] = sorted({c for c, J in terms})
        info["literals per term"] = sorted({len(J) for c, J in terms})
        info["positive terms are exactly the clauses' falsifying conjunctions"] = pos == S.falsifiers(k) and \
            sum(c > 0 for c, J in terms) == len(pos)
        info["terms"] = len(terms)
        ok1 &= all(v for key, v in info.items() if isinstance(v, bool)) and info["coefficients"] == [-1, 1] and \
            info["literals per term"] == [3] and info["faces minus lines"] == 2
        rows["k=%d" % k] = info
    check("1 the certificate: sum over lines of the two clause falsifiers minus sum over three-point faces of two complementary "
          "conjunctions is the constant polynomial 1, exactly, for K_2..K_8; coefficients +1 and -1; three literals per term", ok1, rows)

    # 2. brute force on K_2: the identity at every assignment
    terms, info = S.certificate(2)
    n = info["points"]
    worst, ok2 = None, True
    for bits in itertools.product((0, 1), repeat=n):
        val = sum(c for c, J in terms if all(bits[p] == v for p, v in J.items()))
        ok2 &= val == 1
        if not ok2:
            worst = bits
            break
    check("2 brute force on K_2 (2^16 assignments): violated clauses minus monochromatic three-point faces is 1 at every assignment",
          ok2, {"assignments": 2 ** n, "first failure": worst})

    # 3. the solver record (read, not rerun)
    rec = json.loads((HERE / "solvers" / "solver_runs.json").read_text())
    table, ok3 = {}, True
    for solver, runs in rec["runs"].items():
        ks = sorted(int(k) for k in runs)
        ok3 &= all(runs[str(k)]["result"] in ("UNSAT", "TIMEOUT") for k in ks)
        solved = [k for k in ks if runs[str(k)]["result"] == "UNSAT"]
        table[solver] = {"largest k refuted within the limit": max(solved), "first k not refuted": min([k for k in ks if k not in solved], default=None),
                         "conflicts by k": {k: runs[str(k)].get("conflicts") for k in ks},
                         "seconds by k": {k: runs[str(k)]["seconds"] for k in ks}}
    check("3 solver record (experiment, read from solvers/solver_runs.json): no solver refutes beyond small k within its limit", ok3,
          {"limits": rec["limits"], "table": table})

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
              "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        sys.exit(1)
