"""Independent CNF/SAT checks for TRUE-BOND's uniformly truncated copy tree.

Identities in the public API are zero based; CNF literals are DIMACS (one based).
Only the boundary relation G is obtained from BD.  Expansion, endpoint choice,
and constrained/minimal tests do not call either bond DP.  In particular a set
is tested by SAT under assignments, never by a projected relation mask.

``count_bonds`` is deliberately bounded.  ``counts`` contains only exhausted
sizes; a partially enumerated size is present only in ``observed_counts``.
``complete`` means the requested size bound was exhausted (or that there are
no qualifying bonds at any size).  With max_size=None the requested bound is
the first least size plus one.  Always check ``through_least_plus_one`` before
using an explicitly size-capped result for the requested validation.
"""

from __future__ import annotations

import importlib.util
import itertools
import math
import resource
import sys
import threading
import time
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from pysat.solvers import Solver


ROOT = Path(__file__).resolve().parents[4]
BD_PATH = (
    ROOT / "experiments/BOND-DEPTH-20261112-001A"
    / "BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py"
)


class TruncationTooLarge(ValueError):
    """The exact expansion would exceed a declared construction ceiling."""


class _Stopped(Exception):
    pass


@lru_cache(maxsize=1)
def _bd():
    spec = importlib.util.spec_from_file_location("true_bond_bd_sat_source", BD_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _definition(defs):
    if len(defs) != 1:
        raise ValueError("SAT validation requires exactly one definition")
    k, own_count, calls = defs[0]
    if k != 3 or not isinstance(own_count, int) or own_count < 0:
        raise ValueError("Expected three ports and a nonnegative own count")
    normalized = []
    for callee, args in calls:
        args = tuple(args)
        if callee not in ("K", "SELF") or len(args) != 3:
            raise ValueError("Only three-argument K and SELF calls are admitted")
        if any(not isinstance(a, int) or a < 0 or a >= 3 + own_count for a in args):
            raise ValueError("Call argument outside the definition's environment")
        normalized.append((callee, args))
    if not any(callee == "SELF" for callee, _ in normalized):
        raise ValueError("The requested ray requires at least one SELF call")
    return own_count, normalized


def _peak_mb():
    # Linux reports KiB, macOS reports bytes.  This is the whole process's
    # high-water mark, including imports and any prior work in this process.
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return peak / (1024 * 1024 if sys.platform == "darwin" else 1024)


def _canonical_clause(literals):
    literals = set(literals)
    if any(-literal in literals for literal in literals):
        return None  # A repeated argument can make a boundary clause tautological.
    return tuple(sorted(literals, key=lambda literal: (abs(literal), literal)))


def build_truncation(defs, s, h, *, max_copies=100_000, max_variables=500_000):
    """Build copies at depths 0,...,D inclusive, D=s+h; bottom SELF calls use G.

    The first SELF child is indexed 0, even if earlier calls are knots.  A
    copy's ``path`` is its sequence of SELF child indices, so C_s has path
    (0,)*s.  Child ports reuse their actual identities, while every copy's own
    identities are fresh.  ``created`` includes the top ports only at C_0.
    Construction ceilings raise TruncationTooLarge; they never shorten a tree.
    """
    if not isinstance(s, int) or s < 0 or not isinstance(h, int) or h < 0:
        raise ValueError("s and h must be nonnegative integers")
    own_count, calls = _definition(defs)
    children_per_copy = sum(callee == "SELF" for callee, _ in calls)
    depth = s + h
    copies_expected = (
        depth + 1 if children_per_copy == 1
        else (children_per_copy ** (depth + 1) - 1) // (children_per_copy - 1)
    )
    variables_expected = 3 + own_count * copies_expected
    if max_copies is not None and copies_expected > max_copies:
        raise TruncationTooLarge(
            f"{copies_expected} copies exceed max_copies={max_copies}"
        )
    if max_variables is not None and variables_expected > max_variables:
        raise TruncationTooLarge(
            f"{variables_expected} identities exceed max_variables={max_variables}"
        )
    _, _, gd = _bd().L.depth_sequence(defs, _bd().L.TOP)
    boundary = tuple(bool(value) for value in gd[0])
    if len(boundary) != 8:
        raise ValueError("Expected an eight-state boundary relation")

    clauses, clause_seen, copies, boundary_calls = [], set(), [], []
    next_variable = 3

    def add_clause(literals):
        clause = _canonical_clause(literals)
        if clause is not None and clause not in clause_seen:
            clause_seen.add(clause)
            clauses.append(list(clause))

    def create_copy(path, ports):
        nonlocal next_variable
        own = list(range(next_variable, next_variable + own_count))
        next_variable += own_count
        record = {
            "path": path, "depth": len(path), "ports": list(ports), "own": own,
            "created": ([0, 1, 2] if not path else []) + own,
            "children": [],
        }
        copies.append(record)
        return record

    create_copy((), [0, 1, 2])
    # Iterating the growing list is a breadth-first traversal, without recursion.
    for record in copies:
        env = record["ports"] + record["own"]
        child_index = 0
        for call_index, (callee, formals) in enumerate(calls):
            args = [env[index] for index in formals]
            if callee == "K":
                add_clause([identity + 1 for identity in args])
                add_clause([-(identity + 1) for identity in args])
                continue
            path = record["path"] + (child_index,)
            if record["depth"] < depth:
                child = create_copy(path, args)
                record["children"].append(child["path"])
            else:
                boundary_calls.append({
                    "parent": record["path"], "call_index": call_index,
                    "child_index": child_index, "args": args,
                })
                # Forbid each disallowed root-port assignment.  This handles
                # repeated actual arguments as well as distinct arguments.
                for state, allowed in enumerate(boundary):
                    if not allowed:
                        add_clause([
                            -(identity + 1) if (state >> bit) & 1 else identity + 1
                            for bit, identity in enumerate(args)
                        ])
            child_index += 1

    by_path = {record["path"]: record for record in copies}
    target = list(by_path[(0,) * s]["own"])
    assert len(copies) == copies_expected and next_variable == variables_expected
    return {
        "clauses": clauses, "n": next_variable, "top": [0, 1, 2],
        "target": target, "s": s, "h": h, "depth": depth,
        "G": list(boundary), "copies": copies, "copy_count": len(copies),
        "boundary_calls": boundary_calls,
        "ray": [(0,) * j for j in range(s + 1)],
        "children_per_copy": children_per_copy,
    }


def _candidate_components(truncation):
    """Return disjoint endpoint-bearing CNF components, excluding unused IDs.

    A CNF is a conjunction of independent components.  A minimal constrained
    set must lie in one component: otherwise its bad assignment already fails
    in a proper component subset.  An unused identity cannot be essential.
    These are exact pruning rules, not assumptions about this family.
    """
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for clause in truncation["clauses"]:
        support = sorted({abs(literal) - 1 for literal in clause})
        if support:
            root = find(support[0])
            for identity in support[1:]:
                parent[find(identity)] = root
    components = defaultdict(list)
    for identity in parent:
        components[find(identity)].append(identity)
    top, target = set(truncation["top"]), set(truncation["target"])
    answer = []
    for members in components.values():
        a, b = sorted(top.intersection(members)), sorted(target.intersection(members))
        if a and b:
            rest = sorted(set(members) - top - target)
            answer.append((a, b, rest))
    return answer


def _component_candidate_count(component, size):
    top, target, rest = component
    total = 0
    for a in range(1, min(len(top), size - 1) + 1):
        for b in range(1, min(len(target), size - a) + 1):
            r = size - a - b
            if r <= len(rest):
                total += math.comb(len(top), a) * math.comb(len(target), b) * math.comb(len(rest), r)
    return total


def _candidates(components, size):
    # Enumerate qualifying sets directly.  Enumerating all n-choose-k sets and
    # then filtering endpoints is needlessly expensive at this tree's sizes.
    for top, target, rest in components:
        for a in range(1, min(len(top), size - 1) + 1):
            for b in range(1, min(len(target), size - a) + 1):
                r = size - a - b
                if r > len(rest):
                    continue
                for first in itertools.combinations(top, a):
                    for last in itertools.combinations(target, b):
                        for middle in itertools.combinations(rest, r):
                            yield tuple(sorted(first + last + middle))


class _SatOracle:
    def __init__(self, solver, deadline, sat_call_limit, cache_limit, complement):
        self.solver, self.deadline = solver, deadline
        self.sat_call_limit, self.cache_limit = sat_call_limit, cache_limit
        self.complement = complement
        self.calls = self.cache_hits = 0
        self.sat_seconds = 0.0
        self.cache = {}
        self.known = defaultdict(set)

    def check_budget(self):
        if self.deadline is not None and time.perf_counter() >= self.deadline:
            raise _Stopped("seconds_limit")
        if self.sat_call_limit is not None and self.calls >= self.sat_call_limit:
            raise _Stopped("sat_call_limit")

    def solve(self, assumptions):
        self.check_budget()
        self.calls += 1
        started = time.perf_counter()
        result = self.solver.solve_limited(assumptions=assumptions, expect_interrupt=True)
        self.sat_seconds += time.perf_counter() - started
        if result is None:
            raise _Stopped("seconds_limit_or_solver_interrupt")
        return result

    def register(self, support):
        support = tuple(sorted(support))
        # Keeping fewer certificates can only reduce pruning, never coverage.
        if len(self.known[len(support)]) < 100_000:
            self.known[len(support)].add(support)

    def contains_proper_constrained_subset(self, variables):
        available = set(variables)
        for size in sorted(self.known):
            if size >= len(variables):
                break
            supports = self.known[size]
            if len(supports) <= math.comb(len(variables), size):
                if any(available.issuperset(support) for support in supports):
                    return True
            elif any(subset in supports for subset in itertools.combinations(variables, size)):
                return True
        return False

    def free(self, variables):
        variables = tuple(variables)
        if variables in self.cache:
            self.cache_hits += 1
            return self.cache[variables]
        # An exact syntactic complement automorphism, when detected, pairs
        # every assignment with its complement.  No relation masks are used.
        assignments = 1 << (len(variables) - int(self.complement and bool(variables)))
        result, core = True, None
        for assignment in range(assignments):
            if self.complement and variables:
                assignment <<= 1  # Fix the first selected identity to zero.
            assumptions = [
                identity + 1 if (assignment >> bit) & 1 else -(identity + 1)
                for bit, identity in enumerate(variables)
            ]
            if not self.solve(assumptions):
                core = tuple(sorted(abs(literal) - 1 for literal in self.solver.get_core()))
                self.register(core)
                result = False
                break
        if self.cache_limit and len(self.cache) >= self.cache_limit:
            self.cache.clear()
        if self.cache_limit:
            self.cache[variables] = result
        return result


def count_bonds(
    defs, s, h, max_size=None, *, candidate_limit=100_000, seconds_limit=30.0,
    sat_call_limit=2_000_000, cache_limit=100_000, solver_name="g3",
    use_complement_symmetry=True, max_copies=100_000, max_variables=500_000,
):
    """Count distinct qualifying bond *sets*, not bad assignments or clauses.

    All surviving candidates are checked by direct SAT assumptions; each
    single deletion must allow every assignment.  Earlier UNSAT cores and
    supports of non-tautological CNF clauses soundly reject nonminimal
    supersets.  Thus even size-pruning certificates need no DP summaries.

    ``candidate_limit`` bounds generated candidates, including pruned ones;
    ``sat_call_limit`` bounds individual SAT calls.  A solver interrupt timer
    enforces the remaining wall budget during SAT (the default g3 supports
    interruption).  Construction is checked separately and never truncated.
    None disables a ceiling.  A cutoff is an incomplete result, never zero.
    """
    if max_size is not None and (not isinstance(max_size, int) or max_size < 0):
        raise ValueError("max_size must be a nonnegative integer or None")
    for name, value in (("candidate_limit", candidate_limit), ("sat_call_limit", sat_call_limit)):
        if value is not None and value < 0:
            raise ValueError(f"{name} must be nonnegative or None")
    if seconds_limit is not None and seconds_limit < 0:
        raise ValueError("seconds_limit must be nonnegative or None")
    started = time.perf_counter()
    deadline = None if seconds_limit is None else started + seconds_limit
    result = {
        "s": s, "h": h, "depth": s + h, "counts": {}, "observed_counts": {},
        "exact_sizes": [], "complete_through": -1, "least": None,
        "complete": False, "through_least_plus_one": False, "status": "incomplete",
        "reason": None, "max_size": max_size, "candidate_limit": candidate_limit,
        "seconds_limit": seconds_limit, "sat_call_limit": sat_call_limit,
        "candidates": 0, "candidates_pruned": 0, "candidates_sat_tested": 0,
        "candidate_totals": {}, "sat_calls": 0, "sat_seconds": 0.0,
        "cache_hits": 0, "solver": solver_name, "sample_bonds": [],
        "memory_measure": "process high-water MiB, including imports/prior work",
    }
    oracle = timer = solver = None
    try:
        truncation = build_truncation(
            defs, s, h, max_copies=max_copies, max_variables=max_variables
        )
        result.update(n=truncation["n"], clauses=len(truncation["clauses"]),
                      copies=truncation["copy_count"], top=truncation["top"],
                      target=truncation["target"])
        if deadline is not None and time.perf_counter() >= deadline:
            raise _Stopped("seconds_limit_during_construction")
        canonical = {tuple(clause) for clause in truncation["clauses"]}
        complement = use_complement_symmetry and all(
            _canonical_clause(-literal for literal in clause) in canonical
            for clause in truncation["clauses"]
        )
        result["complement_symmetry"] = complement
        solver = Solver(name=solver_name, bootstrap_with=truncation["clauses"])
        oracle = _SatOracle(solver, deadline, sat_call_limit, cache_limit, complement)
        if deadline is not None:
            timer = threading.Timer(max(0.0, deadline - time.perf_counter()), solver.interrupt)
            timer.daemon = True
            timer.start()
        alive = oracle.solve([])
        result["base_satisfiable"] = alive
        components = _candidate_components(truncation) if alive else []
        result["candidate_component_sizes"] = [sum(map(len, component)) for component in components]
        no_candidates = not alive or not components
        # If the sole least bond uses every identity, its least+1 count is
        # still required and is exactly zero, so include the structural n+1.
        stop_size = min(max_size, truncation["n"] + 1) if max_size is not None else truncation["n"] + 1
        if no_candidates:
            # This establishes absence at *every* size, even beyond an explicit
            # requested bound.  The empty bond in a dead CNF has no endpoints.
            for size in range(stop_size + 1):
                result["counts"][str(size)] = 0
            result.update(
                complete=True, through_least_plus_one=True, status="complete",
                reason="unsatisfiable_truncation" if not alive else "no_endpoint_component",
                exact_sizes=list(range(stop_size + 1)), complete_through=stop_size,
                all_sizes_zero=True,
            )
            return result
        for clause in truncation["clauses"]:
            oracle.register({abs(literal) - 1 for literal in clause})
        for size in range(stop_size + 1):
            oracle.check_budget()
            total = sum(_component_candidate_count(component, size) for component in components)
            result["candidate_totals"][str(size)] = total
            count = 0
            result["observed_counts"][str(size)] = 0
            for variables in _candidates(components, size):
                oracle.check_budget()
                if candidate_limit is not None and result["candidates"] >= candidate_limit:
                    raise _Stopped("candidate_limit")
                result["candidates"] += 1
                if oracle.contains_proper_constrained_subset(variables):
                    result["candidates_pruned"] += 1
                    continue
                result["candidates_sat_tested"] += 1
                if oracle.free(variables):
                    continue
                # A discovered UNSAT core may itself certify a proper subset.
                if oracle.contains_proper_constrained_subset(variables):
                    result["candidates_pruned"] += 1
                    continue
                if all(oracle.free(variables[:j] + variables[j + 1:]) for j in range(size)):
                    count += 1
                    result["observed_counts"][str(size)] = count
                    # Earlier sizes were exhausted, so even a cutoff partway
                    # through this size cannot change the first observed size.
                    if result["least"] is None:
                        result["least"] = size
                    if len(result["sample_bonds"]) < 20:
                        result["sample_bonds"].append(list(variables))
            result["counts"][str(size)] = count
            result["exact_sizes"].append(size)
            result["complete_through"] = size
            if count and result["least"] is None:
                result["least"] = size
            if max_size is None and result["least"] is not None and size >= result["least"] + 1:
                break
        result.update(complete=True, status="complete", reason="requested_sizes_exhausted")
        result["through_least_plus_one"] = (
            result["least"] is not None and result["complete_through"] >= result["least"] + 1
        ) or result["complete_through"] >= truncation["n"]
    except TruncationTooLarge as error:
        result["reason"] = "construction_limit: " + str(error)
    except _Stopped as error:
        result["reason"] = str(error)
    finally:
        if timer is not None:
            timer.cancel()
            timer.join()
        if oracle is not None:
            result.update(sat_calls=oracle.calls, sat_seconds=oracle.sat_seconds,
                          cache_hits=oracle.cache_hits)
        if solver is not None:
            solver.delete()
        result["seconds"] = time.perf_counter() - started
        result["peak_mb"] = _peak_mb()
    return result


def tiny_fixture_checks():
    """Non-study fixtures with hand-derived counts and independent CNF checks.

    Nothing is written.  They test fresh siblings, inclusive depth, a derived
    four-identity bond, boundary G, exact coverage, and a resource cutoff.
    """
    fixtures = []
    # Two NAE clauses share x.  Projecting x away gives a four-variable
    # constraint: a=b=0,c=y=1 (and its complement) cannot extend.  Each proper
    # subset is free.  The child's own NAE is the other endpoint-bearing bond.
    derived = [(3, 1, [("K", (0, 1, 3)), ("SELF", (3, 2, 1))])]
    exact = count_bonds(derived, 1, 0, candidate_limit=10_000, seconds_limit=5)
    fixtures.append({
        "name": "derived_four_identity_bond", "result": exact,
        "pass": exact["complete"] and exact["through_least_plus_one"]
        and exact["counts"] == {"0": 0, "1": 0, "2": 0, "3": 1, "4": 1},
    })
    all_assignments = count_bonds(
        derived, 1, 0, candidate_limit=10_000, seconds_limit=5,
        use_complement_symmetry=False,
    )
    fixtures.append({
        "name": "complement_optimization_matches_all_assignments",
        "result": all_assignments,
        "pass": all_assignments["complete"] and all_assignments["counts"] == exact["counts"],
    })
    branching = [(3, 1, [
        ("K", (0, 1, 3)), ("SELF", (3, 1, 2)), ("SELF", (3, 1, 2)),
    ])]
    expanded = build_truncation(branching, 1, 1)
    own = [identity for copy in expanded["copies"] for identity in copy["own"]]
    branching_count = count_bonds(branching, 1, 1, candidate_limit=10_000, seconds_limit=5)
    fixtures.append({
        "name": "inclusive_depth_and_fresh_sibling_own_identities",
        "result": branching_count,
        "pass": expanded["copy_count"] == 7 and expanded["n"] == 10
        and len(own) == len(set(own)) == 7 and len(expanded["boundary_calls"]) == 8
        and branching_count["complete"] and branching_count["counts"].get("3") == 3
        # Eliminating shared top identity 1 between the root knot and either
        # grandchild knot also gives one four-identity bond per grandchild.
        and branching_count["counts"].get("4") == 2,
    })
    boundary = [(3, 1, [("K", (0, 1, 2)), ("SELF", (3, 1, 2))])]
    truncation = build_truncation(boundary, 1, 0)
    target = truncation["target"][0]
    with Solver(name="g3", bootstrap_with=truncation["clauses"]) as solver:
        # The target own identity occurs only in the boundary SELF call.
        forbidden = not solver.solve(assumptions=[-2, -3, -(target + 1)])
        allowed = solver.solve(assumptions=[-2, -3, target + 1])
    boundary_count = count_bonds(boundary, 1, 0, candidate_limit=10_000, seconds_limit=5)
    fixtures.append({
        "name": "G_boundary_is_CNF_not_an_extra_copy",
        "result": boundary_count,
        "pass": forbidden and allowed and truncation["copy_count"] == 2
        and truncation["n"] == 5 and sum(truncation["G"]) == 6
        and boundary_count["complete"] and boundary_count["counts"].get("3") == 1,
    })
    cutoff = count_bonds(derived, 1, 0, candidate_limit=0, seconds_limit=5)
    fixtures.append({
        "name": "cutoff_never_reports_partial_size_as_exact", "result": cutoff,
        "pass": not cutoff["complete"] and cutoff["reason"] == "candidate_limit"
        and "2" not in cutoff["counts"] and cutoff["complete_through"] == 1,
    })
    return {"pass": all(fixture["pass"] for fixture in fixtures), "fixtures": fixtures}


if __name__ == "__main__":
    import json
    checked = tiny_fixture_checks()
    print(json.dumps(checked, sort_keys=True))
    sys.exit(0 if checked["pass"] else 1)
