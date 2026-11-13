#!/usr/bin/env python3
"""Independent finite ray-bond audit, BOND-DEPTH-20261112-001.

Question: reproduce small frozen-validation cases and the two chain controls.
Branch/stage: code_analysis / independent referee validation, sampled finite scope.
Inputs: literal definitions in LIMIT-ONLY's gzipped sample records; recorded
validation.json is a comparison-only input; runs_merged.jsonl also informed
the three supplementary case selections after the initial five agreed.
Forbidden inputs: all producer computational functions (including its DP,
ray_cnf, brute, block_relation, and fixed-point implementation).
Mapping: independently compute the greatest relation fixed point, construct
ray constraints, enumerate their complete finite solution relation, and search
supports in increasing cardinality for a minimal non-shattered support.
Controls: unconstrained relation, direct NAE, a nonminimal NAE superset, and a
chain whose middle rule is removed.
Resource/stop: 8 GiB address-space ceiling; 90 seconds per family; 550 seconds
total; no support-size cutoff. Incomplete cells and mismatches are retained.
Nonclaims: no full census, unbounded-depth theorem, global shortest-bond result,
native emergence claim, or external replication follows from this audit.

Independence: this module imports NO producer code. NumPy evaluates literal
CNF truth tables; PySAT/CaDiCaL checks the returned support and every deletion
through SAT assumptions. The latter SAT backend is shared with the producer,
but it does not determine the exhaustive-search result. No L/run_family/ray_cnf/
brute/block_relation/DP function is imported or called.

Run from the repository root, with bytecode disabled:
  .venv/bin/python -B research/BOND-DEPTH-20261112-001/referee-R1/codex/independent_validation.py
Only this module's adjacent independent_validation.json is written.
"""

import sys

sys.dont_write_bytecode = True

import collections
import glob
import gzip
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import resource
import signal
import time

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_AS)
ceiling = 8 * 1024**3
resource.setrlimit(resource.RLIMIT_AS, (min(ceiling, hard_limit) if hard_limit > 0 else ceiling, hard_limit))

import numpy as np
from pysat.solvers import Solver


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).with_name("independent_validation.json")
RAW = ROOT / "artifacts/LIMIT-ONLY-20261112-001A/LIMIT-ONLY-20261112-001A-E001_limit_only"
PRODUCER = ROOT / "experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py"
RECORDED = ROOT / "artifacts/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds"
SELECTED = (103, 156, 480, 311, 737, 124, 1307, 104)
FAMILY_CAP_SECONDS = 90
TOTAL_CAP_SECONDS = 550
START = time.monotonic()


class BudgetStop(Exception):
    pass


def timeout_handler(signum, frame):
    raise BudgetStop("wall-clock budget reached")


signal.signal(signal.SIGALRM, timeout_handler)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_definition(definition):
    """Independent usual-limit convention: retain pass-through port NAE."""
    k, nlocals, calls = definition
    copied = [(callee, tuple(args)) for callee, args in calls]
    passthrough = any(callee == "SELF" and set(args) == {0, 1, 2} for callee, args in copied)
    if passthrough:
        copied.append(("K", (0, 1, 2)))
    return (k, nlocals, copied), passthrough


def terminal_relation(definition):
    """Greatest fixed point by explicit sets of three-port assignments."""
    k, nlocals, calls = definition
    assert k == 3
    assert all(callee in ("K", "SELF") and len(args) == 3 for callee, args in calls)
    current = frozenset(range(8))
    history = [sorted(current)]
    while True:
        following = set()
        for state in range(1 << (3 + nlocals)):
            for callee, args in calls:
                local = sum(((state >> arg) & 1) << j for j, arg in enumerate(args))
                accepted = local not in (0, 7) if callee == "K" else local in current
                if not accepted:
                    break
            else:
                following.add(state & 7)
        following = frozenset(following)
        assert following <= current, "iteration from the full relation must descend"
        history.append(sorted(following))
        if following == current:
            return current, history
        current = following


def load_families():
    """Read source literals in the producer's declared file/record ordering."""
    raw = []
    source_files = sorted(RAW.glob("sample_*.jsonl.gz"))
    for path in source_files:
        with gzip.open(path, "rt") as stream:
            for line in stream:
                record = json.loads(line)
                if record.get("limit_only"):
                    raw.append(record["defs"])
    genuine = []
    for index, definitions in enumerate(raw):
        if len(definitions) != 1:
            continue
        definition, passthrough = canonical_definition(definitions[0])
        relation, history = terminal_relation(definition)
        if relation:
            genuine.append((index, definition, relation, history, passthrough))
    return genuine, raw, source_files


def build_ray(definition, relation, depth):
    """Allocate copies C_0..C_depth and independently encode their rules."""
    k, nlocals, calls = definition
    clauses = []
    knots = []
    next_variable = 3
    ports = (0, 1, 2)
    top = set(ports)
    created_by_copy = []

    def require_relation(actual):
        for forbidden in set(range(8)) - set(relation):
            # A clause is false exactly at the forbidden state of this call.
            clauses.append(tuple(-(v + 1) if (forbidden >> j) & 1 else v + 1 for j, v in enumerate(actual)))

    for level in range(depth + 1):
        own = tuple(range(next_variable, next_variable + nlocals))
        next_variable += nlocals
        actual_environment = tuple(ports) + own
        created_by_copy.append(tuple(top) + own if level == 0 else own)
        next_ports = None
        for callee, arguments in calls:
            actual = tuple(actual_environment[j] for j in arguments)
            if callee == "K":
                clauses.append(tuple(v + 1 for v in actual))
                clauses.append(tuple(-(v + 1) for v in actual))
                knots.append(actual)
            elif next_ports is None:
                assert callee == "SELF"
                next_ports = actual
                if level == depth:
                    require_relation(actual)
            else:
                require_relation(actual)
        assert next_ports is not None
        ports = next_ports
    return clauses, next_variable, top, set(created_by_copy[-1]), knots


def normalize_clauses(clauses):
    result = set()
    for clause in clauses:
        literals = frozenset(clause)
        if any(-lit in literals for lit in literals):
            continue
        result.add(tuple(sorted(literals)))
    return sorted(result)


def complete_relation(clauses, nvariables):
    """Evaluate every state on mentioned variables; free variables factor out."""
    clauses = normalize_clauses(clauses)
    active = sorted({abs(literal) - 1 for clause in clauses for literal in clause})
    lookup = {old: new for new, old in enumerate(active)}
    states = np.arange(1 << len(active), dtype=np.uint64)
    good = np.ones(len(states), dtype=bool)
    for clause in clauses:
        satisfied = np.zeros(len(states), dtype=bool)
        for literal in clause:
            value = ((states >> lookup[abs(literal) - 1]) & 1).astype(bool)
            satisfied |= value if literal > 0 else ~value
        good &= satisfied
    solutions = states[good]
    return clauses, active, lookup, solutions, sorted(set(range(nvariables)) - set(active))


def sat_certificate(clauses, support):
    """K1-K3 on the projected support using separately invoked SAT queries."""
    calls = 0
    with Solver(name="cadical153", bootstrap_with=clauses) as solver:
        alive = solver.solve()
        calls += 1

        def shatters(variables):
            nonlocal calls
            first_missing = None
            for assignment in itertools.product((False, True), repeat=len(variables)):
                assumptions = [(v + 1) if bit else -(v + 1) for v, bit in zip(variables, assignment)]
                calls += 1
                if not solver.solve(assumptions=assumptions):
                    first_missing = [int(bit) for bit in assignment]
                    break
            return first_missing is None, first_missing

        free, missing = shatters(support)
        deletions = []
        for erased in support:
            rest = [v for v in support if v != erased]
            deletion_free, deletion_missing = shatters(rest)
            deletions.append(dict(erased=erased, free=deletion_free, first_missing=deletion_missing))
    return dict(K1_constrained=not free, K2_each_deletion_free=all(r["free"] for r in deletions),
                K3_nonempty=alive, first_missing=missing, deletions=deletions, sat_calls=calls,
                accepted=alive and not free and all(r["free"] for r in deletions))


def least_bond(clauses, nvariables, top, last, deadline):
    clauses, active, lookup, solutions, ignored = complete_relation(clauses, nvariables)
    record = dict(nvariables=nvariables, active_variables=active, ignored_free_variables=ignored,
                  assignments_evaluated=1 << len(active), active_solutions=len(solutions),
                  clauses=len(clauses), sizes_fully_completed=[], supports_seen=0,
                  supports_evaluated=0, supersets_of_known_bonds_skipped=0,
                  search_max_support_size=len(active), support_size_cutoff=None)
    if not len(solutions):
        return dict(record, status="dead", L=None)
    topmask = sum(1 << lookup[v] for v in top if v in lookup)
    lastmask = sum(1 << lookup[v] for v in last if v in lookup)
    if not topmask or not lastmask:
        return dict(record, status="exact_no_ray_bond", L=None,
                    reason="every eligible endpoint on at least one side is unconstrained")
    known_bonds = []
    free_cache = {0: True}

    def free(mask):
        if mask not in free_cache:
            free_cache[mask] = len(np.unique(solutions & np.uint64(mask))) == (1 << mask.bit_count())
        return free_cache[mask]

    for size in range(1, len(active) + 1):
        for positions in itertools.combinations(range(len(active)), size):
            record["supports_seen"] += 1
            if record["supports_seen"] % 128 == 0 and time.monotonic() > deadline:
                raise BudgetStop("per-family or total deadline reached in exhaustive support search")
            mask = sum(1 << j for j in positions)
            if any(mask & bond == bond for bond in known_bonds):
                record["supersets_of_known_bonds_skipped"] += 1
                continue
            record["supports_evaluated"] += 1
            if free(mask):
                continue
            # A minimal non-shattered subset exists in every non-shattered
            # support; all smaller supports have already been covered.
            assert all(free(mask ^ (1 << j)) for j in positions)
            known_bonds.append(mask)
            if mask & topmask and mask & lastmask:
                support = [active[j] for j in positions]
                certificate = sat_certificate(clauses, support)
                return dict(record, status="exact", L=size, witness=support,
                            certificate=certificate, known_bonds_found=len(known_bonds),
                            all_smaller_supports_covered=True)
        record["sizes_fully_completed"].append(size)
    return dict(record, status="exact_no_ray_bond", L=None, known_bonds_found=len(known_bonds),
                all_support_sizes_covered=True)


def min_steps(knots, top, last):
    """Minimum number of co-knotted pairs, for the finite chain controls."""
    adjacent = collections.defaultdict(set)
    for triple in knots:
        for v in triple:
            adjacent[v].update(set(triple) - {v})
    queue = collections.deque((v, 0) for v in top)
    seen = set(top)
    while queue:
        variable, steps = queue.popleft()
        if variable in last:
            return steps
        for other in adjacent[variable] - seen:
            seen.add(other)
            queue.append((other, steps + 1))
    return None


def recorded_value(row, depth):
    values = list(row["L"])
    rate = row.get("rate")
    if len(values) < depth and rate:
        while len(values) < depth:
            predecessor = values[len(values) - rate["period"]]
            values.append(predecessor + rate["gain"] if predecessor < 10**9 else predecessor)
    if len(values) < depth:
        return None
    return values[depth - 1] if values[depth - 1] < 10**9 else None


def main():
    recorded_validation = json.loads((RECORDED / "validation.json").read_text())
    recorded_rows = {row["idx"]: row for row in map(json.loads, (RECORDED / "runs_merged.jsonl").read_text().splitlines())}
    genuine, raw, source_files = load_families()
    sampled = random.Random(7).sample(genuine, 40)
    sample_order = {entry[0]: order for order, entry in enumerate(sampled)}
    available = {entry[0]: entry for entry in genuine}
    assert len(genuine) == 664
    assert all(index in sample_order for index in SELECTED)
    result = dict(
        scope_kind="epic", scope_id="BOND-DEPTH-20261112-001",
        kind="independent finite referee computation", validation_independence="V2",
        evidence_class="exact finite computation; independent AI-subagent implementation within the same task",
        external_replication=False, producer_imports=[],
        dependencies_used=dict(raw_literal_definitions=True, recorded_validation="comparison only",
                               recorded_census="comparison and supplementary case selection only", numpy="truth-table operations",
                               pysat_cadical153="witness and deletion SAT checks; backend shared with producer"),
        budget=dict(per_family_seconds=FAMILY_CAP_SECONDS, total_seconds=TOTAL_CAP_SECONDS,
                    address_space_bytes=ceiling, support_size_cap=None),
        contract=dict(sample_rule="selected fixed IDs from independently reconstructed random.Random(7).sample(genuine,40)",
                      selected_ids=list(SELECTED), depths=[1, 2, 3], chain_depths=list(range(1, 7)),
                      selection_reason="initial five small cases; then three supplementary small cases chosen to cover varied recorded prefixes",
                      selection_history=[dict(phase="initial", ids=[103, 156, 480, 311, 737],
                                              reason="small cases and 737's nontrivial terminal relation"),
                                         dict(phase="supplementary", ids=[124, 1307, 104],
                                              reason="initial cases all flat through depth 3; recorded prefixes add 3,4,4; 3,4,5; and 3,2,2")],
                      exhaustive_rule="all smaller supports covered; supersets of known bonds excluded by minimality",
                      primary_observable="least cardinality of a minimal non-shattered support meeting top and last locals"),
        provenance=dict(command=".venv/bin/python -B " + str(Path(__file__).relative_to(ROOT)),
                        python=sys.version, numpy=np.__version__, thread_id=os.environ.get("CODEX_THREAD_ID"),
                        producer_sha256=digest(PRODUCER), script_sha256=digest(__file__),
                        validation_sha256=digest(RECORDED / "validation.json"),
                        merged_census_sha256=digest(RECORDED / "runs_merged.jsonl"),
                        raw_files=[dict(path=str(p.relative_to(ROOT)), sha256=digest(p)) for p in source_files]),
        source_counts=dict(limit_only_families=len(raw), one_definition_genuine=len(genuine)),
        recorded_validation=recorded_validation,
        recorded_validation_limitation="aggregate 120/120 and chains only; individual validation values were not retained",
        reconstructed_40_sample_ids=[entry[0] for entry in sampled], cases=[], controls=[], chains=[], mismatches=[], incomplete=[])

    def process(label, definition, relation, depths, expectation=None):
        begun = time.monotonic()
        deadline = min(begun + FAMILY_CAP_SECONDS, START + TOTAL_CAP_SECONDS)
        signal.setitimer(signal.ITIMER_REAL, max(0.01, deadline - time.monotonic()))
        cells = []
        for depth in depths:
            t0 = time.monotonic()
            try:
                clauses, nvariables, top, last, knots = build_ray(definition, relation, depth)
                cell = least_bond(clauses, nvariables, top, last, deadline)
                cell.update(depth=depth, seconds=round(time.monotonic() - t0, 6))
                if expectation is not None:
                    expected = expectation(depth)
                    cell["expected_L"] = expected
                    cell["matches_expected"] = cell["L"] == expected and cell["status"] in ("exact", "exact_no_ray_bond")
                    if not cell["matches_expected"]:
                        result["mismatches"].append(dict(label=label, depth=depth, observed=cell["L"], expected=expected))
                if isinstance(label, str) and label.startswith("chain"):
                    cell["steps_apart"] = min_steps(knots, top, last)
                    cell["matches_steps_plus_two"] = cell["L"] == cell["steps_apart"] + 2
                cells.append(cell)
                print(json.dumps(dict(label=label, depth=depth, L=cell["L"], status=cell["status"], seconds=cell["seconds"])), flush=True)
            except BudgetStop as error:
                incomplete = dict(label=label, depth=depth, reason=str(error),
                                  unattempted_depths=[s for s in depths if s > depth])
                cells.append(dict(depth=depth, status="incomplete", reason=str(error)))
                result["incomplete"].append(incomplete)
                break
        signal.setitimer(signal.ITIMER_REAL, 0)
        return cells, round(time.monotonic() - begun, 6)

    for index in SELECTED:
        _, definition, relation, history, passthrough = available[index]
        cells, seconds = process(index, definition, relation, [1, 2, 3],
                                 lambda depth, row=recorded_rows[index]: recorded_value(row, depth))
        result["cases"].append(dict(idx=index, seeded_validation_sample_order=sample_order[index],
                                    definition=definition, terminal_relation=sorted(relation),
                                    fixedpoint_history=history, usual_passthrough_added=passthrough,
                                    recorded_census=recorded_rows[index], cells=cells, seconds=seconds))

    # Small controls exercise the same exact search and SAT certificate.
    for label, clauses, nvariables, top, last, expected in (
        ("unconstrained", [], 4, {0}, {3}, None),
        ("direct_NAE", [(1, 2, 3), (-1, -2, -3)], 3, {0}, {2}, 3),
        ("broken_chain_middle_rule_removed", [(1, 2, 3), (-1, -2, -3), (5, 6, 7), (-5, -6, -7)],
         7, {0, 1}, {5, 6}, None),
    ):
        cell = least_bond(clauses, nvariables, top, last, time.monotonic() + 20)
        cell.update(label=label, expected_L=expected, matches_expected=cell["L"] == expected)
        result["controls"].append(cell)
        if not cell["matches_expected"]:
            result["mismatches"].append(dict(label=label, observed=cell["L"], expected=expected))
    bad = sat_certificate([(1, 2, 3), (-1, -2, -3)], [0, 1, 2, 3])
    result["controls"].append(dict(label="reject_nonminimal_NAE_superset", certificate=bad,
                                   matches_expected=not bad["accepted"] and not bad["K2_each_deletion_free"]))

    chain_definitions = [
        (3, 3, [("K", (0, 1, 3)), ("SELF", (3, 4, 5))]),
        (3, 2, [("K", (0, 3, 4)), ("SELF", (4, 1, 3))]),
    ]
    for number, definition in enumerate(chain_definitions):
        relation, history = terminal_relation(definition)
        cells, seconds = process("chain_" + str(number + 1), definition, relation, list(range(1, 7)),
                                 lambda depth, number=number: recorded_validation["chains"][number][depth - 1])
        result["chains"].append(dict(definition=definition, terminal_relation=sorted(relation),
                                     fixedpoint_history=history, cells=cells, seconds=seconds))

    all_cells = [cell for family in result["cases"] + result["chains"] for cell in family["cells"]]
    exact = [cell for cell in all_cells if cell["status"] == "exact"]
    result["summary"] = dict(
        completed_finite_cells=sum(cell["status"] in ("exact", "exact_no_ray_bond") for cell in all_cells),
        selected_family_cells=sum(len(case["cells"]) for case in result["cases"]),
        chain_cells=sum(len(case["cells"]) for case in result["chains"]),
        mismatches=len(result["mismatches"]), incomplete=len(result["incomplete"]),
        all_controls_pass=all(control["matches_expected"] for control in result["controls"]),
        all_returned_witnesses_sat_verified=all(cell["certificate"]["accepted"] for cell in exact),
        elapsed_seconds=round(time.monotonic() - START, 6),
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        conclusion="finite sampled validation only; no asymptotic or full-census conclusion")
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["summary"], indent=2), flush=True)
    return 0 if (not result["mismatches"] and not result["incomplete"]
                 and result["summary"]["all_controls_pass"]
                 and result["summary"]["all_returned_witnesses_sat_verified"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
