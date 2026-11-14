"""Fresh rigidity tests. Only earlier referee pattern reconstruction is reused.

Fix X_0=0, exclude the full parity assignment, then certify UNSAT with DRUP.
Complement symmetry lifts this to exactly parity and its complement.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[4]
EARLIER = ROOT / "research/ADDR-KNOTS-20261113-001/referee-R1/codex"
sys.path.insert(0, str(EARLIER))
from fresh_patterns import pattern, cnf, verify_assignment
from pysat.solvers import Cadical195, Glucose4

OUT = pathlib.Path(__file__).resolve().parent / "rigidity"
KEY = [3, [1, 0, 1], [0, 2, 2], [2, 1, 1], [[0, 8, 10], [1, 8, 12], [1, 9, 10]]]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_cnf(path, nvars, clauses):
    with path.open("w") as f:
        f.write(f"p cnf {nvars} {len(clauses)}\n")
        for c in clauses:
            f.write(" ".join(map(str, c)) + " 0\n")


def solve_one(n, budget, solver_name):
    start = time.monotonic()
    triples = pattern(KEY, n)
    values = [x.bit_count() & 1 for x in range(1 << n)]
    removed = [t for t in triples if len({values[x] for x in t}) == 1]
    remaining = [t for t in triples if t not in removed]
    assert len(removed) == 2 and verify_assignment(remaining, values)
    # All addresses are included, so this also detects any free variable.
    blocking = [-(x + 1) if b else x + 1 for x, b in enumerate(values)]
    clauses = cnf(remaining) + [[-1], blocking]
    base = OUT / f"reduced-L{n:02d}"
    cnf_path = base.with_suffix(".cnf")
    write_cnf(cnf_path, 1 << n, clauses)
    scratch = OUT / "scratch"
    scratch.mkdir(exist_ok=True)
    tempfile.tempdir = str(scratch)
    solver_cls = Cadical195 if solver_name == "cadical195" else Glucose4
    solver = solver_cls(bootstrap_with=clauses, with_proof=True)
    solver.conf_budget(budget)
    result = solver.solve_limited()
    record = {
        "level": n, "solver": solver_name, "conflict_budget": budget,
        "knots_original": len(triples), "knots_reduced": len(remaining),
        "removed": removed, "parity_model_valid": True,
        "anchor": [-1], "blocking_clause_length": len(blocking),
        "cnf": str(cnf_path.relative_to(OUT.parent)), "cnf_sha256": sha(cnf_path),
        "sat_second_state": result, "stats": solver.accum_stats(),
    }
    if result is False:
        if solver_name == "cadical195":
            # Its C trace stream otherwise can retain the final proof buffer.
            import ctypes
            assert ctypes.CDLL(None).fflush(None) == 0
        proof = solver.get_proof()
        assert proof and any(line.strip() == "0" for line in proof), "Proof capture has no empty clause"
        proof_path = base.with_suffix(".drup.gz")
        with gzip.open(proof_path, "wt") as f:
            for line in proof:
                f.write(line + "\n")
        record.update(proof=str(proof_path.relative_to(OUT.parent)),
                      proof_sha256=sha(proof_path), proof_lines=len(proof),
                      independent_proof_check="pending")
    elif result is True:
        raw = solver.get_model()
        alternate = [False] * (1 << n)
        for lit in raw:
            if abs(lit) <= len(alternate): alternate[abs(lit)-1] = lit > 0
        assert alternate[0] == 0 and alternate != values
        assert verify_assignment(remaining, alternate)
        record.update(alternative="".join("1" if v else "0" for v in alternate),
                      alternative_checked_all_knots=True,
                      alternative_original_model=verify_assignment(triples, alternate))
    solver.delete()
    scratch.rmdir()  # Anonymous proof streams have been closed.
    record["seconds"] = time.monotonic() - start
    base.with_suffix(".json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({k: v for k, v in record.items() if k not in ["alternative"]}), flush=True)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--levels", type=int, nargs="+", default=[4, 6, 8, 10, 12])
    parser.add_argument("--budget", type=int, default=2000000)
    parser.add_argument("--solver", choices=["cadical195", "glucose4"], default="glucose4")
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    results = [solve_one(n, args.budget, args.solver) for n in args.levels]
    (OUT / "solve_results.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
