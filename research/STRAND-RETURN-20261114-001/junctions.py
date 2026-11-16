"""Replay the historical sign conflict and check forgetting on two closed strands."""

import ast
import hashlib
import json
from itertools import product
from pathlib import Path


BITS = (0, 1)
NOTEBOOK = Path("archive/p-vs-np/experiments/36_loop_agents_meta_graph.ipynb")


def historical_clauses():
    """Read the actual clause literals without executing notebook code."""
    raw = (Path(__file__).resolve().parents[2] / NOTEBOOK).read_bytes()
    code = ("".join(cell["source"]) for cell in json.loads(raw)["cells"]
            if cell["cell_type"] == "code")
    fixture, = (cell for cell in code if cell.lstrip().startswith("clauses = ["))
    assignment = ast.parse(fixture).body[0]
    clauses = {}
    for call in assignment.value.elts:
        if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name) or call.func.id != "SignedClause":
            raise ValueError("Expected a SignedClause in the historical example")
        name, weights = map(ast.literal_eval, call.args)
        if name in clauses or set(weights.values()) - {-1, 1}:
            raise ValueError(f"Unexpected historical clause {name}")
        clauses[name] = {variable: int(sign) for variable, sign in weights.items()}
    return clauses, hashlib.sha256(raw).hexdigest()


def historical_cycles(clauses):
    """Recover notebook IDs by its ordering of cycles of at most six incidences."""
    neighbours = {}
    for name, literals in clauses.items():
        clause = "clause:" + name
        neighbours[clause] = ["var:" + variable for variable in literals]
        for variable in neighbours[clause]:
            neighbours.setdefault(variable, []).append(clause)

    cycles = []

    def extend(path):
        start = path[0]
        for node in neighbours[path[-1]]:
            if node == start:
                # The smallest node starts each cycle. Keep one orientation.
                if len(path) >= 4 and path[1] < path[-1]:
                    cycles.append(tuple(path))
            elif len(path) < 6 and node > start and node not in path:
                extend(path + [node])

    for name in clauses:
        extend(["clause:" + name])
    return {f"L{i}": cycle for i, cycle in enumerate(sorted(cycles), 1)}


def historical_replay():
    clauses, digest = historical_clauses()
    catalogue = historical_cycles(clauses)
    loop_clauses = {}
    demands = {}
    for label in ("L1", "L6"):
        cycle = catalogue[label]
        loop_clauses[label] = sorted(node.removeprefix("clause:") for node in cycle[::2])
        demands[label] = {}
        for i in range(1, len(cycle), 2):
            variable = cycle[i].removeprefix("var:")
            previous = clauses[cycle[i - 1].removeprefix("clause:")][variable]
            following = clauses[cycle[(i + 1) % len(cycle)].removeprefix("clause:")][variable]
            if previous == following:
                demands[label][variable] = previous

    shared = demands["L1"].keys() & demands["L6"].keys()
    opposite = sorted(v for v in shared if demands["L1"][v] != demands["L6"][v])
    agreeing = sorted(shared - set(opposite))
    shared_clauses = set(loop_clauses["L1"]) & set(loop_clauses["L6"])
    synergy = len(agreeing) + 0.5 * len(shared_clauses)
    historical_label = "conflict" if opposite else ("attach" if synergy else "independent")

    groups = {name: set(ids) for name, ids in loop_clauses.items()}
    groups["pair"] = groups["L1"] | groups["L6"]
    groups["whole"] = set(clauses)
    held_names = sorted(set().union(*clauses.values()) - {"c"})
    rows = []
    for bits in product(BITS, repeat=len(held_names)):
        held = dict(zip(held_names, bits))
        allowed = {group: [] for group in groups}
        for c in BITS:
            world = {**held, "c": c}
            satisfied = {name for name, literals in clauses.items()
                         if any(world[v] == int(sign > 0) for v, sign in literals.items())}
            for group, clause_names in groups.items():
                if clause_names <= satisfied:
                    allowed[group].append(c)
        if set(allowed["pair"]) != set(allowed["L1"]) & set(allowed["L6"]):
            raise AssertionError(f"Pair and single-loop enumerations disagree at {held}")
        rows.append({"held": held, "allowed_c": allowed})

    example_holdings = (
        {"a": 1, "b": 0, "d": 1, "e": 0, "f": 1},
        {"a": 1, "b": 1, "d": 1, "e": 0, "f": 0},
    )
    examples = [next(row for row in rows if row["held"] == held) for held in example_holdings]
    viable = [row["allowed_c"] for row in rows if row["allowed_c"]["L1"] and row["allowed_c"]["L6"]]
    return {
        "notebook": str(NOTEBOOK), "notebook_sha256": digest, "original_commit": "d92bb3f74",
        "catalogued_cycles": len(catalogue), "loop_clauses": loop_clauses, "literal_demands": demands,
        "historical_sign_rule": {"relation": historical_label, "agreeing_variables": agreeing,
                                 "opposite_variables": opposite, "conflict": len(opposite),
                                 "synergy": synergy, "score": synergy - len(opposite)},
        "outside_assignments": len(rows), "worlds_enumerated": len(rows) * len(BITS),
        "whole_satisfying_worlds_by_c": {str(c): sum(c in row["allowed_c"]["whole"] for row in rows)
                                         for c in BITS},
        "individually_viable_pairs": len(viable),
        "individually_viable_pairs_with_no_shared_value": sum(not values["pair"] for values in viable),
        "examples": examples, "all_outside_assignments": rows,
    }


def oracle_worlds(signs, identified):
    """Check four equal/different requirements on each raw assignment."""
    accepted = []
    nvariables = 2 if identified else 3
    for values in product(BITS, repeat=nvariables):
        h, u = values[:2]
        v = u if identified else values[2]
        links = ((h, u), (u, h), (h, v), (v, h))
        if all(int(first != second) == sign for (first, second), sign in zip(links, signs)):
            accepted.append(values)
    return accepted


def return_relation(outward, backward):
    """Retain both the starting bit and the bit reached before the return."""
    relation = set()
    for h in BITS:
        middle = h ^ outward
        if (middle ^ backward) == h:
            relation.add((h, middle))
    return relation


def junction_panel():
    layouts = {}
    for identified in (False, True):
        variable_order = ["h", "u"] if identified else ["h", "u", "v"]
        cases = []
        for signs in product(BITS, repeat=4):
            left = return_relation(*signs[:2])
            right = return_relation(*signs[2:])
            left_h = {h for h, _ in left}
            right_h = {h for h, _ in right}
            early = left_h & right_h
            kept = {h for h, u in left for k, v in right if h == k and (not identified or u == v)}
            accepted = oracle_worlds(signs, identified)
            oracle = {row[0] for row in accepted}
            if kept != oracle:
                raise AssertionError(f"Joint reduction disagrees with raw worlds at {identified=}, {signs=}")
            cases.append({
                "signs": list(signs), "left_allowed_h": sorted(left_h), "right_allowed_h": sorted(right_h),
                "oracle_worlds": [list(row) for row in accepted], "oracle_allowed_h": sorted(oracle),
                "forget_middle_early": sorted(early), "retain_shared_middle": sorted(kept),
            })
        mismatches = [row for row in cases if row["forget_middle_early"] != row["oracle_allowed_h"]]
        layouts["identified_middles" if identified else "distinct_middles"] = {
            "world_variable_order": variable_order, "systems": len(cases),
            "oracle_assignments_tested": len(cases) * 2**len(variable_order),
            "oracle_assignments_allowed": sum(len(row["oracle_worlds"]) for row in cases),
            "both_strands_individually_viable": sum(bool(row["left_allowed_h"] and row["right_allowed_h"])
                                                    for row in cases),
            "jointly_viable": sum(bool(row["oracle_allowed_h"]) for row in cases),
            "early_forgetting_exact": len(cases) - len(mismatches),
            "retaining_shared_middle_exact": sum(row["retain_shared_middle"] == row["oracle_allowed_h"]
                                                 for row in cases),
            "early_mismatch_signs": [row["signs"] for row in mismatches],
            "cases": cases,
        }
    return {"sign_order": ["h_to_u", "u_to_h", "h_to_v", "v_to_h"],
            "sign_meaning": {"0": "equal", "1": "different"}, "layouts": layouts}


def verify():
    return {"historical": historical_replay(), "junctions": junction_panel()}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
