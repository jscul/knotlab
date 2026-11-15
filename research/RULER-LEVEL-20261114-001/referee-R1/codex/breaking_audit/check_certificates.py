"""Separate retained-model and DRUP certificate check for the five cases."""
from __future__ import annotations

import hashlib
import itertools as it
import json
import resource
import time
from pathlib import Path

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent


def clauses(knots):
    return [c for row in knots for c in ([v+1 for v in row], [-v-1 for v in row])]


def rup(active, candidate):
    """Hint-free unit propagation of active clauses under not(candidate)."""
    assignment = {}
    for lit in candidate:
        v, bit = abs(lit), int(lit < 0)
        if v in assignment and assignment[v] != bit:
            return True
        assignment[v] = bit
    while True:
        changed = False
        for clause in active:
            unset = []
            satisfied = False
            for lit in clause:
                bit = assignment.get(abs(lit))
                if bit is None:
                    unset.append(lit)
                elif bit == int(lit > 0):
                    satisfied = True
                    break
            if satisfied:
                continue
            if not unset:
                return True
            if len(unset) == 1:
                lit = unset[0]
                assignment[abs(lit)] = int(lit > 0)
                changed = True
        if not changed:
            return False


def check_proof(initial, lines):
    active = {frozenset(c) for c in initial}
    additions = deletions = 0
    empty = False
    for line in lines:
        tokens = line.strip().split()
        if not tokens or tokens[0] == "c":
            continue
        delete = tokens[0] == "d"
        literals = list(map(int, tokens[1:] if delete else tokens))
        if not literals or literals[-1] != 0 or 0 in literals[:-1]:
            return False, {"reason": "bad proof syntax"}
        clause = frozenset(literals[:-1])
        if delete:
            # Retaining an original/proved clause after a deletion is sound:
            # it remains an implicate of the original input. This also avoids
            # conflating duplicate clause instances when a solver deletes one.
            deletions += 1
        else:
            if not rup(active, clause):
                return False, {"reason": "addition is not RUP", "clause": list(clause)}
            active.add(clause)
            additions += 1
            if not clause:
                empty = True
    return empty, {"additions": additions, "deletions": deletions,
                   "derived_empty_clause": empty}


def main():
    resource.setrlimit(resource.RLIMIT_AS, (2300*1024**2, 2300*1024**2))
    started = time.perf_counter()
    results = []
    model_count = 0
    for source in sorted(HERE.glob("case_*.json")):
        record = json.loads(source.read_text())
        base = clauses(record["knots"])
        assert not check_proof(base, ["0"])[0], "bogus contradiction accepted"
        for level in record["levels"]:
            cert = level["certificate"]
            support, bits = cert["support"], cert["forbidden_assignment"]
            assert len(support) == level["L"]
            assert set(support) & set(level["A"]) and set(support) & set(level["B"])
            expected = {(removed, tuple(x for x in support if x != removed), bits)
                        for removed in support
                        for bits in it.product((0, 1), repeat=len(support)-1)}
            actual = set()
            for row in cert["maximal_proper_projection_models"]:
                values = row["model"]
                assert len(values) == 127 and set(values) <= {0, 1}
                assert all(len({values[v] for v in knot}) == 2 for knot in record["knots"])
                assert all(values[v] == b for v, b in zip(row["support"], row["assignment"]))
                actual.add((row["removed"], tuple(row["support"]), tuple(row["assignment"])))
                corrupted = list(values)
                for v in record["knots"][0]:
                    corrupted[v] = 0
                assert any(len({corrupted[v] for v in knot}) != 2 for knot in record["knots"])
                model_count += 1
            assert actual == expected
            units = [[v+1 if b else -v-1] for v, b in zip(support, bits)]
            initial = base + units
            with Solver(name="glucose4", bootstrap_with=initial, with_proof=True) as solver:
                assert not solver.solve()
                proof = solver.get_proof()
            # Glucose emits no proof when adding the input units already
            # detects a contradiction. An explicit RUP empty clause suffices.
            if not proof and rup({frozenset(c) for c in initial}, frozenset()):
                proof = ["0"]
            accepted, stats = check_proof(initial, proof)
            assert accepted, (record["case"], level["s"], stats)
            target = HERE / f"case_{record['case']}_s{level['s']}.drup"
            target.write_text("\n".join(proof)+"\n")
            # A truncated proof lacking an empty clause must not certify UNSAT.
            without_empty = [line for line in proof if line.strip() != "0"]
            assert not check_proof(initial, without_empty)[0]
            results.append({"case": record["case"], "s": level["s"], "L": level["L"],
                            "support": support, "forbidden_assignment": bits,
                            "proper_assignment_models": len(actual), "all_models_checked": True,
                            "drup_path": target.name,
                            "drup_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                            "rup_proof_checked": True, "proof_stats": stats})
    output = {"bond_certificates": results, "models_checked": model_count,
              "all_passed": True, "bogus_empty_clause_rejected_for_each_alive_base": True,
              "empty_clause_erasure_rejected_for_each_proof": True,
              "corrupted_model_rejected_for_each_retained_model": True,
              "seconds": time.perf_counter()-started,
              "max_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "algorithm": "independent direct model evaluation plus hint-free RUP checking of Glucose4 DRUP"}
    (HERE / "certificate_audit.json").write_text(json.dumps(output, indent=2)+"\n")
    print(json.dumps({"bonds": len(results), "models": model_count, "all_passed": True,
                      "seconds": output["seconds"]}), flush=True)


if __name__ == "__main__":
    main()
