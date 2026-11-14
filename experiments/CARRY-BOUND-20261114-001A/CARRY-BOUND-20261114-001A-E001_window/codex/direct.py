"""Finite full-pattern direct bond search for the frozen post-path sample.

The previous independent referee's DirectSearch is reused read-only.  CNF
construction and covered-target selection use brute.py, not window code.
Each result concerns one absolute depth, all covered S copies there, and
members anywhere in the explicit pattern through depth s+2 with usual-limit
relations at the frontier.  It is a finite-reading upper bound only.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "research/FREE-TARGET-20261114-001/referee-R1/codex/direct_bonds.py"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import brute

DEFAULT_SECONDS = 480.0
DEFAULT_SEEDS = 30
MAX_SIZE = 6


def _search_module():
    name = "carry_readonly_direct_referee"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, SOURCE)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load independent direct search: {SOURCE}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _key(row):
    if isinstance(row, str):
        return row
    if isinstance(row, dict) and isinstance(row.get("key"), str):
        return row["key"]
    raw = row["defs"] if isinstance(row, dict) and "defs" in row else row
    return json.dumps(raw, separators=(",", ":"), ensure_ascii=True)


def run_case(row, s, *, seconds=DEFAULT_SECONDS, seeds=DEFAULT_SEEDS,
             max_variables=15_000, max_clauses=100_000, max_copies=25_000):
    """Return the least eligible finite-reading bond through size 6, or cap.

    Completed exclusion of sizes 2..6 is reported as the literal ``'> 6'``.
    Timeouts, construction caps and unresolved input conventions have a null
    minimum, and are never reported as completed exclusions or as growth.
    """
    s = int(s)
    if s not in range(1, 7):
        raise ValueError("frozen direct depths are exactly 1 through 6")
    if seconds <= 0 or seeds < 0:
        raise ValueError("seconds must be positive and seeds nonnegative")
    started = time.monotonic()
    key = _key(row)
    caps = {"search_seconds": float(seconds), "max_size": MAX_SIZE,
            "max_variables": int(max_variables), "max_clauses": int(max_clauses),
            "max_copies": int(max_copies), "seeds": int(seeds)}
    result = {"key": key, "key_sha256": hashlib.sha256(key.encode()).hexdigest(),
        "s": s, "cutoff_depth": s + 2, "blocks_through_cutoff_inclusive": True,
        "members": "all unfolded distinctions", "targets_rule": "all covered S copies at absolute depth s",
        "minimum": None, "checked_max_size": MAX_SIZE, "limits": caps,
        "evidence_scope": "finite reading; upper bounds only; no growth conclusion",
        "search_source": str(SOURCE.relative_to(ROOT)),
        "search_source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
    search = None
    try:
        family = brute.prepare_family(row)
        result.update(S=family.S, main=family.main, usual_limit_alive=family.alive,
                      main_equals_S=family.main == family.S)
        if not family.alive:
            result["status"] = "not_living"
            return result
        pattern = brute.unfold_pattern(family, s + 2, target_depth=s,
                                      max_variables=max_variables, max_clauses=max_clauses,
                                      max_copies=max_copies)
        clauses, n = pattern["clauses"], pattern["n"]
        roots, targets = set(pattern["roots"]), set(pattern["targets"])
        target_copies = [copy for copy in pattern["copies"]
                         if copy["covered"] and copy["depth"] == s]
        result.update(variables=n, clauses=len(clauses), copies=len(pattern["copies"]),
                      root_ports=len(roots), targets=len(targets),
                      target_copies=len(target_copies),
                      target_definitions=sorted({pattern["origin"][v]["definition"] for v in targets}),
                      limit_relations={str(i): [state for state, allowed in enumerate(g) if allowed]
                                       for i, g in sorted(family.limits.items())})
        if not targets:
            result["status"] = "no_covered_target"
            return result
        direct = _search_module()
        search = direct.DirectSearch(clauses, n, roots, targets, seconds=float(seconds),
                                     preferred_pools=[roots | targets])
        answer = search.run(max_size=MAX_SIZE, seeds=int(seeds))
        result.update(answer)
        if answer["minimum"] is None:
            if any(not entry.get("exhausted") for entry in answer["by_size"]):
                raise AssertionError("completed exclusion contains an unexhausted lower size")
            result.update(status="sizes_through_6_excluded", minimum="> 6")
        else:
            witness = tuple(answer["witness"])
            check = brute.bond_check_cnf(clauses, n, witness, max_rows=1 << MAX_SIZE,
                                         backend="glucose42")
            result["verification"] = check
            result["witness_detail"] = [{"variable": v, "is_top_port": v in roots,
                "is_target": v in targets, "origin": pattern["origin"].get(v, {"top_port": v})}
                for v in witness]
            if not check["is_bond"] or not roots.intersection(witness) or not targets.intersection(witness):
                result.update(status="verification_failed", minimum=None)
            else:
                result["status"] = "exact_minimum"
        return result
    except brute.ComputationAmbiguity as exc:
        result.update(status="not_computed", reason=str(exc), minimum=None)
        return result
    except brute.CalculationCap as exc:
        result.update(status="cap", cap=exc.record(), minimum=None)
        return result
    except Exception as exc:
        # The read-only search module's own deadline is a reported cap.  A
        # runner-level timeout remains the shared runner's timeout result.
        if search is None or not isinstance(exc, _search_module().SearchTimeout):
            raise
        result.update(status="timeout", minimum=None,
                      reason="direct search deadline", completed_lower_sizes=list(search.by_size))
        result["proved_lower_bound"] = max([entry["size"] + 1 for entry in search.by_size
                                            if entry.get("exhausted")] + [2])
        return result
    finally:
        if search is not None:
            result.update(sat_queries=search.queries, iterations=search.iterations,
                          models=len(search.models), excluded_nonfaces=len(search.forbidden))
            search.close()
        result.update(seconds=time.monotonic() - started,
                      peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key", required=True, help="canonical raw family JSON key")
    parser.add_argument("--depth", type=int, required=True, choices=range(1, 7))
    parser.add_argument("--seconds", type=float, default=DEFAULT_SECONDS)
    parser.add_argument("--seeds", type=int, default=DEFAULT_SEEDS)
    parser.add_argument("--max-variables", type=int, default=15_000)
    parser.add_argument("--max-clauses", type=int, default=100_000)
    parser.add_argument("--max-copies", type=int, default=25_000)
    args = parser.parse_args()
    result = run_case({"key": args.key}, args.depth, seconds=args.seconds, seeds=args.seeds,
                      max_variables=args.max_variables, max_clauses=args.max_clauses,
                      max_copies=args.max_copies)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
