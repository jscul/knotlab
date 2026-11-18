"""Solve the finite memoryless game through the first nonroot parity junction."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter
from dataclasses import dataclass
from functools import cache
from itertools import combinations, permutations, product
from pathlib import Path

from networkx import Graph
from networkx.algorithms.isomorphism import GraphMatcher


ROOT = Path(__file__).resolve().parents[3]
SOURCE = (
    ROOT / "proofs/BOOTSTRAP-ALIGNMENT-20261117-001"
    / "BOOTSTRAP-ALIGNMENT-20261117-001-P001_distance_start" / "check_seed.py"
)
SOURCE_SHA256 = "d228eb78ae0c3d976ab59ed20f3e93db115565aeb625f410572e9891570ae3c5"
OLD = tuple(range(8))
PORTS = (8, 9)
UNAVAILABLE = -1
GOAL = -2
MISALIGNED = -3
FAILURES = {UNAVAILABLE, MISALIGNED}
Move = tuple[str, tuple[int, ...]]
Matrix = tuple[tuple[int | None, ...], ...]


@dataclass(frozen=True, order=True)
class Position:
    root: int = -1
    tested: tuple[int, ...] = ()

    @property
    def genuine(self) -> int:
        return 8 if self.root < 0 else 10

    @property
    def width(self) -> int:
        return self.genuine + 2 * bool(self.tested)

    def record(self):
        return {"root": self.root if self.root >= 0 else None, "tested": self.tested}


def cube_symmetries():
    old_maps = {
        tuple(flip ^ sum(((v >> i) & 1) << order[i] for i in range(3)) for v in OLD)
        for flip in OLD
        for order in permutations(range(3))
    }
    assert len(old_maps) == 48
    return tuple(sorted(old + ports for old in old_maps for ports in (PORTS, PORTS[::-1])))


PHYSICAL_SYMMETRIES = cube_symmetries()


def rename(position, perm):
    root = perm[position.root] if position.root >= 0 else -1
    return Position(root, tuple(sorted(perm[bit] for bit in position.tested)))


@cache
def canonical(position):
    return min(rename(position, perm) for perm in PHYSICAL_SYMMETRIES)


def all_positions():
    physical = [
        Position(root, tested)
        for root in (-1, *OLD)
        for tested in ((), *combinations(range(8 if root < 0 else 10), 2))
    ]
    return tuple(sorted({canonical(position) for position in physical})), physical


def load_source():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256
    spec = importlib.util.spec_from_file_location("one_probe_seed_oracle", SOURCE)
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    return source


def actual_rows(position, old_rows, source):
    rows = old_rows
    if position.root >= 0:
        rows = source.parity_extension(rows, 8, (position.root,))
    if not position.tested:
        return rows
    a, b = position.tested
    p, q = position.genuine, position.genuine + 1
    with_probe = frozenset(
        row | (left << p) | (right << q)
        for row in rows
        for left, right in product((0, 1), repeat=2)
        if left != right or (row >> a & 1) == (row >> b & 1) == left
    )
    assert {row & ((1 << p) - 1) for row in with_probe} == rows
    return with_probe


def direct_matrix(rows, width):
    """Independently project every support before selecting minimal obstructions."""
    assert rows
    full = tuple(
        len({row & mask for row in rows}) == 1 << mask.bit_count()
        for mask in range(1 << width)
    )
    table = [[0 if i == j else None for j in range(width)] for i in range(width)]
    for mask, free in enumerate(full):
        if free or mask.bit_count() < 3:
            continue
        bits = tuple(i for i in range(width) if mask >> i & 1)
        if not all(full[mask ^ (1 << i)] for i in bits):
            continue
        for i, j in combinations(bits, 2):
            delta = len(bits) - 1
            current = table[i][j]
            if current is None or delta < current:
                table[i][j] = table[j][i] = delta
    return tuple(map(tuple, table))


def grade_physical_symmetries(positions, physical, rows):
    checked = set()
    for position in positions:
        for perm in PHYSICAL_SYMMETRIES:
            other = rename(position, perm)
            if other in checked:
                continue
            relabel = perm[:position.genuine] + tuple(range(position.genuine, position.width))
            transported = {
                sum(1 << j for i, j in enumerate(relabel) if row >> i & 1)
                for row in rows[position]
            }
            assert transported == rows[other]
            for move in commands(position.width):
                renamed_move = on_labels(move, relabel)
                for replace in (False, True):
                    assert apply(position, move, replace) == apply(other, renamed_move, replace)
            checked.add(other)
    assert checked == set(physical)
    return len(checked)


def disclosed(position, mode):
    endpoints = set(range(position.genuine, position.width))
    return tuple(
        int("endpoints" in mode and bit in endpoints)
        | (2 * int("middles" in mode and bit in position.tested))
        for bit in range(position.width)
    )


def swappable(table, marks, left, right):
    return marks[left] == marks[right] and all(
        table[left][i] == table[right][i]
        for i in range(len(table)) if i not in (left, right)
    )


@dataclass
class Observation:
    table: Matrix
    marks: tuple[int, ...]
    cells: tuple[tuple[int, ...], ...]
    cell_of: dict[int, int]
    quotient: Graph


def make_observation(table, marks):
    cells = []
    remaining = set(range(len(table)))
    while remaining:
        first = min(remaining)
        cell = tuple(
            bit for bit in sorted(remaining)
            if bit == first or swappable(table, marks, first, bit)
        )
        assert all(swappable(table, marks, left, right) for left, right in combinations(cell, 2))
        cells.append(cell)
        remaining.difference_update(cell)
    quotient = Graph()
    for i, cell in enumerate(cells):
        inside = table[cell[0]][cell[-1]] if len(cell) > 1 else 0
        quotient.add_node(i, color=(len(cell), marks[cell[0]], inside))
        assert all(table[left][right] == inside for left, right in combinations(cell, 2))
    for i, j in combinations(range(len(cells)), 2):
        left, right = cells[i], cells[j]
        edge = table[left[0]][right[0]]
        quotient.add_edge(i, j, scalar=edge)
        assert all(table[a][b] == edge for a, b in product(left, right))
    return Observation(
        table, marks, tuple(cells), {bit: i for i, cell in enumerate(cells) for bit in cell}, quotient
    )


def quotient_maps(first, second):
    if len(first.table) != len(second.table):
        return iter(())
    return GraphMatcher(
        first.quotient, second.quotient, node_match=lambda a, b: a == b,
        edge_match=lambda a, b: a == b,
    ).isomorphisms_iter()


def lift(first, second, mapping):
    renamed = {
        left: right
        for i, j in mapping.items()
        for left, right in zip(first.cells[i], second.cells[j], strict=True)
    }
    perm = tuple(renamed[bit] for bit in range(len(first.table)))
    assert len(set(perm)) == len(first.table)
    assert tuple(second.marks[i] for i in perm) == first.marks
    assert tuple(tuple(second.table[i][j] for j in perm) for i in perm) == first.table
    return perm


def commands(width):
    yield "forget", ()
    yield from (("root", (bit,)) for bit in range(width))
    yield from (("probe", pair) for pair in combinations(range(width), 2))
    yield from (("second", pair) for pair in permutations(range(width), 2))


def on_labels(move, perm):
    operation, operands = move
    mapped = tuple(perm[bit] for bit in operands)
    return operation, tuple(sorted(mapped)) if operation == "probe" else mapped


def action_orbits(observation):
    symmetries = tuple(quotient_maps(observation, observation))
    for symmetry in symmetries:
        lift(observation, observation, symmetry)
    remaining = set(commands(len(observation.table)))
    orbits = []
    while remaining:
        move = min(remaining)
        operation, operands = move
        orbit = set()
        for symmetry in symmetries:
            cells = [observation.cells[symmetry[observation.cell_of[bit]]] for bit in operands]
            for choice in product(*cells):
                if len(set(choice)) == len(choice):
                    orbit.add((operation, tuple(sorted(choice)) if operation == "probe" else choice))
        assert move in orbit and orbit <= remaining
        orbits.append(tuple(sorted(orbit)))
        remaining.difference_update(orbit)
    return tuple(orbits)


def observation_partition(positions, tables, mode):
    representatives = []
    orbits = []
    observation_ids = []
    to_position = []
    for row, position in enumerate(positions):
        observation = make_observation(tables[row], disclosed(position, mode))
        for i, (_, prior) in enumerate(representatives):
            mapping = next(quotient_maps(prior, observation), None)
            if mapping is not None:
                break
        else:
            i = len(representatives)
            representatives.append((row, observation))
            orbits.append(action_orbits(observation))
            mapping = {cell: cell for cell in range(len(observation.cells))}
        observation_ids.append(i)
        to_position.append(lift(representatives[i][1], observation, mapping))
    return representatives, orbits, observation_ids, to_position


def apply(position, move, replace):
    operation, operands = move
    if operation == "forget":
        return canonical(Position(position.root)) if position.tested else UNAVAILABLE
    if operation == "probe":
        if (position.tested and not replace) or max(operands) >= position.genuine:
            return UNAVAILABLE
        return canonical(Position(position.root, operands))
    if operation == "root":
        (root,) = operands
        if position.root >= 0 or root >= 8:
            return UNAVAILABLE
        return canonical(Position(root, position.tested))
    assert operation == "second"
    port, old = operands
    if position.root < 0 or port not in (position.root, *PORTS) or old not in OLD or old == position.root:
        return UNAVAILABLE
    return GOAL if (old ^ position.root).bit_count() == 1 else MISALIGNED


def game_edges(positions, orbits, observation_ids, to_position, replace):
    index = {position: i for i, position in enumerate(positions)}
    edges = []
    witnesses = []
    for i, position in enumerate(positions):
        recorded = []
        actual_actions = []
        for orbit in orbits[observation_ids[i]]:
            outcomes = {}
            for move in orbit:
                physical = on_labels(move, to_position[i])
                result = apply(position, physical, replace)
                target = index[result] if isinstance(result, Position) else result
                outcomes.setdefault(target, physical)
            recorded.append(frozenset(outcomes))
            actual_actions.append(outcomes)
        edges.append(tuple(recorded))
        witnesses.append(tuple(actual_actions))
    return edges, witnesses


def full_information_ranks(edges):
    """Optimistically allow selecting the action orbit using the hidden position."""
    ranks = {GOAL: 0}
    while True:
        following = {
            i: min(1 + max(ranks[target] for target in outcomes) for outcomes in choices if outcomes <= ranks.keys())
            for i, choices in enumerate(edges) if i not in ranks
            if any(outcomes <= ranks.keys() for outcomes in choices)
        }
        if not following:
            return ranks
        ranks.update(following)


def smallest_closed_trap(edges, losing, initial):
    requirements = {
        state: {outcomes & losing for outcomes in edges[state] if not outcomes & FAILURES}
        for state in losing
    }
    for size in range(len(losing)):
        for others in combinations(sorted(losing - {initial}), size):
            states = {initial, *others}
            if all(states & required for i in states for required in requirements[i]):
                return states
    raise AssertionError("The optimistic losing complement must contain a closed trap")


def closed_adversary(edges, witnesses, ranks, positions, initial, detailed):
    """Choose one bad outcome per orbit, preferably a legal continuation."""
    losing = set(range(len(positions))) - ranks.keys()
    assert initial in losing
    trap = smallest_closed_trap(edges, losing, initial)
    found, pending = {initial}, [initial]
    policy = {}
    while pending:
        state = pending.pop()
        bad_choices = []
        for i, outcomes in enumerate(edges[state]):
            failure = MISALIGNED if MISALIGNED in outcomes else UNAVAILABLE
            bad = min(outcomes & trap, default=failure)
            assert bad in outcomes and (bad in trap or bad in FAILURES)
            if bad in trap and bad not in found:
                found.add(bad)
                pending.append(bad)
            if detailed and outcomes != {UNAVAILABLE}:
                bad_choices.append({"orbit": i, "physical_move": witnesses[state][i][bad], "outcome": bad})
        if detailed:
            policy[state] = {"position": positions[state].record(), "responses": bad_choices}
    assert found == trap
    result = {
        "initial": initial,
        "reachable_trap_positions": len(found),
        "trap_positions": {i: positions[i].record() for i in sorted(trap)},
    }
    if detailed:
        result["positions_with_responses"] = policy
    return result


def evaluate_policy(initial, choices, edges, observation_ids, optimistic):
    """Evaluate a partial observational policy, using its optimistic bound at holes."""
    open_states = set()
    reached = set()
    visiting = set()
    depths = {GOAL: 0}

    def visit(state):
        if state in depths:
            return depths[state]
        if state in visiting or state not in optimistic:
            raise ValueError("A reachable bad outcome or cycle")
        reached.add(state)
        observation = observation_ids[state]
        if observation not in choices:
            open_states.add(state)
            return optimistic[state]
        visiting.add(state)
        depth = 1 + max(visit(new) for new in edges[state][choices[observation]])
        visiting.remove(state)
        depths[state] = depth
        return depth

    return visit(initial), open_states, reached, depths


def solve_observation_game(initial, edges, observation_ids, optimistic):
    """Search uniform policies on the actually reachable positions, with no fairness."""
    trials = {}
    for limit in range(optimistic[initial], len(edges) + 1):
        attempted = 0

        def choose(policy):
            nonlocal attempted
            attempted += 1
            try:
                bound, missing, reached, depths = evaluate_policy(
                    initial, policy, edges, observation_ids, optimistic
                )
            except ValueError:
                return None
            if bound > limit:
                return None
            if not missing:
                assert bound == limit
                return policy, reached, depths
            state = min(missing)
            obs = observation_ids[state]
            relevant = {i for i in reached if observation_ids[i] == obs}
            for option in range(len(edges[state])):
                if any(not edges[i][option] <= optimistic.keys() for i in relevant):
                    continue
                found = choose({**policy, obs: option})
                if found is not None:
                    return found
            return None

        result = choose({})
        trials[limit] = attempted
        if result is not None:
            return result, trials
    return None, trials


def describe_policy(result, positions, observation_ids, orbits, representatives):
    choices, reached, depths = result
    policy = {}
    for observation, option in choices.items():
        anchor = representatives[observation][0]
        policy[observation] = {
            "representative_position": positions[anchor].record(),
            "move_on_representative": orbits[observation][option][0],
            "permitted_move_choices": len(orbits[observation][option]),
            "reachable_positions": [
                {**positions[i].record(), "remaining_moves": depths[i]}
                for i in sorted(reached) if observation_ids[i] == observation
            ],
        }
    return policy


def grade_mode(positions, tables, mode, replace, initial):
    representatives, orbits, observation_ids, to_position = observation_partition(positions, tables, mode)
    edges, witnesses = game_edges(positions, orbits, observation_ids, to_position, replace)
    optimistic = full_information_ranks(edges)
    record = {
        "observation_classes": len(orbits),
        "observation_class_sizes": sorted(Counter(observation_ids).values()),
        "physical_positions_with_optimistic_win": len(optimistic) - 1,
        "optimistically_winning_positions": {i: positions[i].record() for i in optimistic if i >= 0},
        "syntactic_action_orbits": sum(map(len, orbits)),
    }
    if initial not in optimistic:
        detailed = replace and mode in ((), ("endpoints",))
        record.update(
            guaranteed_safe_second=False,
            closed_adversary=closed_adversary(edges, witnesses, optimistic, positions, initial, detailed),
        )
        return record

    result, trials = solve_observation_game(initial, edges, observation_ids, optimistic)
    record.update(guaranteed_safe_second=result is not None, partial_policies_tested_by_horizon=trials)
    if result is not None:
        record.update(
            minimum_worst_case_moves=result[2][initial],
            winning_policy=describe_policy(result, positions, observation_ids, orbits, representatives),
        )
    return record


def tied_second_control(position, table):
    """One complete scalar-table isometry hides an incorrect permanent choice."""
    neighbor = ("second", (position.root, 1))
    diagonal = ("second", (position.root, 3))
    assert apply(position, neighbor, True) == GOAL
    assert apply(position, diagonal, True) == MISALIGNED
    assert swappable(table, disclosed(position, ("endpoints",)), 1, 3)
    assert not swappable(table, disclosed(position, ("middles",)), 1, 3)
    return {
        "position": position.record(),
        "scalar_table_transposition": [1, 3],
        "safe_move": neighbor,
        "misaligned_move": diagonal,
        "tested_middle_marker_breaks_transposition": True,
    }


def run():
    source = load_source()
    old_rows = source.seed_rows()[0]
    positions, physical = all_positions()
    rows = {state: actual_rows(state, old_rows, source) for state in physical}
    symmetry_checked = grade_physical_symmetries(positions, physical, rows)
    tables = tuple(source.bond_table(rows[state], state.width)[0] for state in positions)
    for table, state in zip(tables, positions, strict=True):
        assert table == direct_matrix(rows[state], state.width)
    assert all(tables[0][a][b] == 2 for a, b in combinations(OLD, 2))
    # The opposite probe has a flat table on ten distinctions with its roles hidden.
    flat = positions.index(canonical(Position(-1, (0, 7))))
    assert all(tables[flat][a][b] == 2 for a, b in combinations(range(10), 2))
    initial = positions.index(Position())
    face = Position(0, (0, 3))
    variants = {}
    for replace in (False, True):
        mechanism = "atomic_replacement" if replace else "erase_before_reprobe"
        variants[mechanism] = {
            title: grade_mode(positions, tables, mode, replace, initial)
            for title, mode in (
                ("anonymous", ()),
                ("endpoints_disclosed", ("endpoints",)),
                ("middles_disclosed", ("middles",)),
                ("both_disclosed", ("endpoints", "middles")),
            )
        }
    return {
        "oracle_sha256": SOURCE_SHA256,
        "full_labeled_physical_positions_checked": symmetry_checked,
        "symmetry_reduced_physical_positions": len(positions),
        "full_scalar_tables_independently_reprojected": len(tables),
        "physical_position_index": {i: state.record() for i, state in enumerate(positions)},
        "terminal_codes": {
            "unavailable_operand_or_operation": UNAVAILABLE,
            "safe_second_junction": GOAL,
            "misaligned_permanent_second_junction": MISALIGNED,
        },
        "matched_second_move_control": tied_second_control(face, tables[positions.index(face)]),
        "variants": variants,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
