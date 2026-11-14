"""Fresh exact L=2/L=3 checks on the parent's frozen bounded sample.

The old support and forbidden values are upper-bound candidates only. A fresh
NAE CNF and independent SAT queries validate them and every maximal proper
projection. Exhaustive cross-level pair projections establish the lower bound
for L=3. This program imports no study producer or study search implementation.
"""

from __future__ import annotations

import gzip
import hashlib
import itertools
import json
import resource
import sys
import time
from pathlib import Path

resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
REF = OUT.parent
sys.path.insert(0, str(REF))

from fresh_pattern import build
from fresh_search import levels
from pysat.solvers import Solver

START = time.monotonic()
QUERY_SECONDS = 60
N = 9
NVARS = (1 << (N + 1)) - 1


class QueryLimit(Exception):
    pass


class CheckedSolver:
    def __init__(self, clauses, nvars):
        self.solver = Solver(name="glucose4", bootstrap_with=clauses)
        self.clauses = clauses
        self.nvars = nvars
        self.calls = 0
        self.slices = 0
        self.models = {}
        self.states = []
        self.unsat_assumptions = []

    def solve(self, assumptions=()):
        self.calls += 1
        end = time.monotonic() + QUERY_SECONDS
        while True:
            self.solver.conf_budget(20_000)
            answer = self.solver.solve_limited(assumptions=list(assumptions))
            self.slices += 1
            if answer is not None:
                break
            if time.monotonic() >= end:
                raise QueryLimit("SAT conflict-slice deadline")
        if not answer:
            self.unsat_assumptions.append(list(assumptions))
            return False, None
        model = sum(1 << (literal - 1) for literal in self.solver.get_model() if 0 < literal <= self.nvars)
        assert all(bool(model >> (abs(literal) - 1) & 1) == (literal > 0) for literal in assumptions)
        if model not in self.models:
            assert all(any(bool(model >> (abs(literal) - 1) & 1) == (literal > 0) for literal in clause)
                       for clause in self.clauses), "SAT model fails the independently built formula"
            self.models[model] = len(self.states)
            self.states.append(model.to_bytes((self.nvars + 7) // 8, "little").hex())
        return True, self.models[model]

    def close(self):
        self.solver.delete()


def literals(support, values):
    return [(variable + 1) if value else -(variable + 1) for variable, value in zip(support, values)]


def check_support(solver, support, forbidden):
    forbidden_extends, _ = solver.solve(literals(support, forbidden))
    maximal = []
    for dropped in support:
        subset = [variable for variable in support if variable != dropped]
        states = []
        for values in itertools.product((0, 1), repeat=len(subset)):
            satisfiable, state = solver.solve(literals(subset, values))
            states.append({"values": values, "satisfiable": satisfiable, "state_index": state})
        maximal.append({"support": subset, "assignments": states})
    return {
        "support": support, "forbidden_assignment": forbidden,
        "forbidden_is_nonextendible": not forbidden_extends,
        "all_maximal_projections_full": all(state["satisfiable"] for item in maximal for state in item["assignments"]),
        "maximal_projections": maximal,
    }


def pair_lower_bound(solver, A, B):
    counterexamples = []
    rows = []
    for a in A:
        for b in B:
            states = []
            # NAE complement symmetry supplies 11 and 10 from these states.
            for values in ((0, 0), (0, 1)):
                satisfiable, state = solver.solve(literals([a, b], values))
                states.append(state)
                if not satisfiable:
                    counterexamples.append({"support": [a, b], "forbidden_assignment": values})
            rows.append({"a": a, "b": b, "state_indices_for_00_01": states})
    return {
        "pairs": len(A) * len(B), "queried_assignments": 2 * len(A) * len(B),
        "complement_symmetry": "NAE CNF invariant under global value complement; checked models for00/01 supply11/10",
        "all_cross_pairs_full": not counterexamples,
        "counterexamples": counterexamples, "pair_state_indices": rows,
    }


def controls():
    solver = CheckedSolver([[1, 2, 3], [-1, -2, -3]], 3)
    try:
        plain = check_support(solver, [0, 1, 2], [0, 0, 0])
        lower = pair_lower_bound(solver, [0], [1])
        assert plain["forbidden_is_nonextendible"] and plain["all_maximal_projections_full"] and lower["all_cross_pairs_full"]
    finally:
        solver.close()
    solver = CheckedSolver([], 3)
    try:
        free = check_support(solver, [0, 1, 2], [0, 0, 0])
        assert not free["forbidden_is_nonextendible"]
    finally:
        solver.close()
    solver = CheckedSolver([[-1, 2], [1, -2]], 3)
    try:
        bad_minimum = check_support(solver, [0, 1, 2], [0, 1, 0])
        lower = pair_lower_bound(solver, [0], [1])
        assert not bad_minimum["all_maximal_projections_full"] and not lower["all_cross_pairs_full"]
    finally:
        solver.close()
    return {"plain_NAE_triple_L3": True, "free_support_rejected": True, "nonminimal_upper_and_false_pair_lower_rejected": True}


plan_path = REF / "sample_plan.json"
plan = json.loads(plan_path.read_text())
selected = [item for item in plan["sample"] if item["stratum"] in ("direct3", "direct2", "Q3_targeted")]
raw = {}
artifact = ROOT / "artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/results.jsonl.gz"
with gzip.open(artifact, "rt") as handle:
    for line in handle:
        item = json.loads(line)
        if item["case"] in {sample["case"] for sample in selected}:
            raw[item["case"]] = item["result"]

result = {
    "method": "fresh Glucose4 NAE SAT; all cross-level pairs for L3; old candidates supply upper bounds only",
    "N": N, "k0": 3, "processes": 1, "memory_GiB": 2,
    "query_seconds": QUERY_SECONDS,
    "sample_plan_sha256": hashlib.sha256(plan_path.read_bytes()).hexdigest(),
    "source_hashes": {name: hashlib.sha256((REF / name).read_bytes()).hexdigest() for name in ("fresh_pattern.py", "fresh_search.py")},
    "controls": controls(), "cases": [],
    "limitations": [
        "Only listed finite keys at N9 were checked; no class-wide theorem or full-census search validation follows.",
        "UNSAT query answers use an independent solver; this audit does not emit LRAT proofs.",
        "For reported L4 in Q3_targeted, upper-support validity is checked but pair exhaustion is only lower>=3, not exact4.",
    ],
}

progress = OUT / "direct_pair_progress.jsonl"
with progress.open("w") as log:
    for item in selected:
        start = time.monotonic()
        record = raw[item["case"]]
        assert record["key"] == item["key"]
        knots = build(item["key"], N)
        clauses = []
        for knot in knots:
            clauses.append([v + 1 for v in knot])
            clauses.append([-(v + 1) for v in knot])
        solver = CheckedSolver(clauses, NVARS)
        case_result = {"case": item["case"], "stratum": item["stratum"], "key": item["key"], "knots": len(knots), "queries": []}
        try:
            alive, state = solver.solve()
            case_result["alive"] = alive
            case_result["alive_state_index"] = state
            assert alive
            for gap, entry in enumerate(record["levels"], 1):
                A, B = levels(3, gap)
                original = entry["anywhere"]
                candidate = check_support(solver, original["bond"], original["forbidden_assignment"])
                query = {"s": gap, "reported_L": entry["L_N"], "candidate": candidate,
                         "candidate_meets_levels": bool(set(original["bond"]) & set(A)) and bool(set(original["bond"]) & set(B))}
                if entry["L_N"] >= 3:
                    query["pair_lower_bound"] = pair_lower_bound(solver, A, B)
                    query["lower_bound"] = 3 if query["pair_lower_bound"]["all_cross_pairs_full"] else 2
                else:
                    # A two-member candidate containing both disjoint levels is
                    # automatically smallest once its singleton projections are full.
                    query["lower_bound"] = 2
                query["upper_bound"] = len(original["bond"]) if candidate["forbidden_is_nonextendible"] and candidate["all_maximal_projections_full"] else None
                query["exact"] = query["upper_bound"] == query["lower_bound"] and query["candidate_meets_levels"]
                query["target_candidate"] = check_support(solver, entry["target_restricted"]["bond"], entry["target_restricted"]["forbidden_assignment"])
                target_bond = entry["target_restricted"]["bond"]
                query["target_candidate_within_target"] = all((v + 1).bit_length() - 1 <= 3 + gap for v in target_bond)
                case_result["queries"].append(query)
            case_result["exact_profile"] = [query["upper_bound"] for query in case_result["queries"]] if all(query["exact"] for query in case_result["queries"]) else None
            case_result["status"] = "ok"
        except QueryLimit as error:
            case_result["status"] = "undecided"
            case_result["reason"] = str(error)
        finally:
            case_result["SAT_queries"] = solver.calls
            case_result["SAT_conflict_slices"] = solver.slices
            case_result["checked_distinct_models"] = len(solver.states)
            case_result["seconds"] = time.monotonic() - start
            states_path = OUT / f"direct_states_{item['case']}.json.gz"
            with gzip.open(states_path, "wt") as handle:
                json.dump({"encoding": "little-endian hex bitv=idv", "states": solver.states, "unsat_assumptions": solver.unsat_assumptions}, handle)
            case_result["states_file"] = states_path.name
            solver.close()
        result["cases"].append(case_result)
        log.write(json.dumps({key: value for key, value in case_result.items() if key != "queries"}) + "\n")
        log.flush()
        print(json.dumps({"case": item["case"], "stratum": item["stratum"], "exact_profile": case_result.get("exact_profile"), "seconds": case_result["seconds"], "queries": case_result["SAT_queries"]}), flush=True)

result["seconds"] = time.monotonic() - START
result["peak_rss_MB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
result["exact_query_count"] = sum(query["exact"] for case in result["cases"] for query in case["queries"])
result["query_count"] = sum(len(case["queries"]) for case in result["cases"])
(OUT / "direct_pair_audit.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps({"exact_queries": result["exact_query_count"], "queries": result["query_count"], "seconds": result["seconds"], "peak_rss_MB": result["peak_rss_MB"]}), flush=True)
