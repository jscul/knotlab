"""Check exactly what two live pair probes can guarantee before the next junction."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path
from random import Random

import z3


ROOT = Path(__file__).resolve().parents[3]
PREDECESSOR = (
    ROOT / "proofs/ONE-PROBE-ALIGNMENT-20261118-001"
    / "ONE-PROBE-ALIGNMENT-20261118-001-P001_serial" / "check_game.py"
)
PREDECESSOR_DIGEST = "63ca47dfc4646aa236b28faedf230589a10ac8b5f55a38c2c2e55e8feabfad8d"
OLD = tuple(range(8))
PORTS = (8, 9)
UNAVAILABLE, GOAL, MISALIGNED = -1, -2, -3
Pair = tuple[int, int]
Move = tuple[str, tuple[int, ...]]


@dataclass(frozen=True, order=True)
class Position:
    rooted: bool
    tests: tuple[Pair, ...]

    @property
    def genuine(self) -> int:
        return 10 if self.rooted else 8

    @property
    def width(self) -> int:
        return self.genuine + 2 * len(self.tests)

    def endpoint_pairs(self) -> tuple[Pair, ...]:
        return tuple((i, i + 1) for i in range(self.genuine, self.width, 2))

    def record(self):
        return {"rooted": self.rooted, "tested": self.tests}


@dataclass(frozen=True)
class Rules:
    instrument_groups: bool = False
    automatic_erase: bool = False
    automatic_replace: bool = False
    create_two_from_idle: bool = False
    filter_endpoint_selection: bool = False
    horizontal: bool = False


def load_predecessor():
    assert hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest() == PREDECESSOR_DIGEST
    spec = importlib.util.spec_from_file_location("one_probe_observation_tools", PREDECESSOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_roster(genuine: int) -> tuple[Pair, ...]:
    return tuple(combinations(range(genuine), 2))


def rename_tests(tests, perm):
    return tuple(sorted(tuple(sorted(perm[i] for i in test)) for test in tests))


class PhysicalGame:
    def __init__(self, inherited):
        self.inherited = inherited
        self.source = inherited.load_source()
        self.seed = self.source.seed_rows()[0]
        syms = inherited.PHYSICAL_SYMMETRIES
        self.symmetries = {False: syms, True: tuple(p for p in syms if p[0] == 0)}
        self.centerings = {i: next(p for p in syms if p[i] == 0) for i in OLD}
        self.raw = tuple(
            Position(rooted, tests)
            for rooted in (False, True)
            for n in range(3)
            for tests in combinations_with_replacement(test_roster(10 if rooted else 8), n)
        )
        self.positions = tuple(sorted({self.canonical(p) for p in self.raw}))
        self.index = {p: i for i, p in enumerate(self.positions)}
        self.start = self.index[Position(False, ())]

    @cache
    def canonical(self, position):
        return min(
            Position(position.rooted, rename_tests(position.tests, perm))
            for perm in self.symmetries[position.rooted]
        )

    def number(self, rooted, tests):
        return self.index[self.canonical(Position(rooted, tuple(sorted(tests))))]

    def permanent_rows(self, position):
        return self.source.parity_extension(self.seed, 8, (0,)) if position.rooted else self.seed

    def rows(self, position):
        permanent = self.permanent_rows(position)
        return self.adjoin_probes(permanent, position.genuine, position.tests)

    @staticmethod
    def adjoin_probes(permanent, width, tests):
        rows = permanent
        for j, (a, b) in enumerate(tests):
            p = width + 2 * j
            rows = frozenset(
                row | (left << p) | (right << (p + 1))
                for row in rows
                for left, right in product((0, 1), repeat=2)
                if left != right or (row >> a & 1) == (row >> b & 1) == left
            )
        assert {row & ((1 << width) - 1) for row in rows} == permanent
        return rows

    def moves(self, position, rules):
        pairs = test_roster(position.genuine)
        if len(position.tests) < 2:
            yield from (("add", pair) for pair in pairs)
        for endpoints in position.endpoint_pairs():
            yield "erase", endpoints
            yield from (("replace", endpoints + pair) for pair in pairs)
        if position.tests and rules.automatic_erase:
            yield "erase_either", ()
            yield "erase_all", ()
        if position.tests and rules.automatic_replace:
            yield from (("replace_either", pair) for pair in pairs)
            yield from (("replace_all", pair) for pair in pairs)
        if rules.create_two_from_idle and not position.tests:
            yield from (
                ("create_two", first + second)
                for first, second in combinations_with_replacement(pairs, 2)
            )
        if position.rooted:
            yield from (("second", (port, b)) for port in (0, *PORTS) for b in OLD[1:])
        else:
            yield from (("root", (r,)) for r in OLD)

    @cache
    def physical_step(self, position, move, horizontal):
        operation, ids = move
        tests = position.tests
        pairs = dict(zip(position.endpoint_pairs(), tests, strict=True))
        if operation == "second":
            port, b = ids
            if not position.rooted or port not in (0, *PORTS) or b not in OLD[1:]:
                return {UNAVAILABLE}
            correct = b.bit_count() == 1 and (not horizontal or port in PORTS)
            return {GOAL if correct else MISALIGNED}
        if operation == "root":
            (root,) = ids
            if position.rooted or root not in OLD:
                return {UNAVAILABLE}
            return {self.number(True, rename_tests(tests, self.centerings[root]))}
        if operation == "add":
            if len(tests) < 2 and max(ids) < position.genuine:
                return {self.number(position.rooted, (*tests, ids))}
            return {UNAVAILABLE}
        if operation in ("create_two", "configure_two"):
            if (operation == "configure_two" or not tests) and max(ids) < position.genuine:
                return {self.number(position.rooted, (ids[:2], ids[2:]))}
            return {UNAVAILABLE}
        if operation in ("erase_all", "replace_all"):
            if tests and (not ids or max(ids) < position.genuine):
                return {self.number(position.rooted, (ids,) if ids else ())}
            return {UNAVAILABLE}
        if operation in ("erase_either", "replace_either"):
            if tests and (not ids or max(ids) < position.genuine):
                return {
                    self.number(position.rooted, tests[:j] + tests[j+1:] + ((ids,) if ids else ()))
                    for j in range(len(tests))
                }
            return {UNAVAILABLE}
        assert operation in ("erase", "replace")
        endpoints, replacement = ids[:2], ids[2:]
        if endpoints not in pairs or (replacement and max(replacement) >= position.genuine):
            return {UNAVAILABLE}
        remaining = list(tests)
        remaining.remove(pairs[endpoints])
        if replacement:
            remaining.append(replacement)
        return {self.number(position.rooted, remaining)}


def normalized_move(operation, ids):
    if operation in ("add", "erase", "replace_either", "replace_all"):
        ids = tuple(sorted(ids))
    elif operation in ("replace", "create_two", "configure_two"):
        pairs = [tuple(sorted(ids[:2])), tuple(sorted(ids[2:]))]
        if operation != "replace":
            pairs.sort()
        ids = pairs[0] + pairs[1]
    return operation, ids


def rename_move(move, perm):
    operation, operands = move
    return normalized_move(operation, tuple(perm[i] for i in operands))


def observation(game, position, table, instrument_groups):
    marks = (0,) * position.width
    if instrument_groups:
        known_pairs = set(position.endpoint_pairs())
        marks = (0,) * position.genuine + (1,) * (position.width - position.genuine)
        table = tuple(
            tuple((value, (min(i, j), max(i, j)) in known_pairs) for j, value in enumerate(line))
            for i, line in enumerate(table)
        )
    return game.inherited.make_observation(table, marks)


def classify_observations(game, tables, instrument_groups):
    inherited = game.inherited
    representatives, classes = [], []
    observation_ids, to_physical = [], []
    for state, (position, table) in enumerate(zip(game.positions, tables, strict=True)):
        actual = observation(game, position, table, instrument_groups)
        for i, known in enumerate(classes):
            isometry = next(inherited.quotient_maps(known, actual), None)
            if isometry is not None:
                break
        else:
            i = len(classes)
            representatives.append(state)
            classes.append(actual)
            isometry = {j: j for j in range(len(actual.cells))}
        observation_ids.append(i)
        to_physical.append(inherited.lift(classes[i], actual, isometry))
    return representatives, classes, observation_ids, to_physical


def move_orbit(move, table, symmetries):
    operation, operands = move
    distinct = tuple(dict.fromkeys(operands))
    orbit = set()
    for symmetry in symmetries:
        cells = [table.cells[symmetry[table.cell_of[bit]]] for bit in distinct]
        for target in product(*cells):
            if len(set(target)) != len(target):
                continue
            lookup = dict(zip(distinct, target, strict=True))
            orbit.add(normalized_move(operation, tuple(lookup[bit] for bit in operands)))
    assert move in orbit
    return orbit


def action_roster(game, classification, rules):
    _, classes, observation_ids, to_physical = classification
    possible = defaultdict(set)
    for i, position in enumerate(game.positions):
        inverse = tuple(to_physical[i].index(j) for j in range(position.width))
        possible[observation_ids[i]].update(rename_move(a, inverse) for a in game.moves(position, rules))
    orbits = {}
    for j, table in enumerate(classes):
        symmetries = tuple(game.inherited.quotient_maps(table, table))
        remaining = possible[j].copy()
        orbits[j] = []
        while remaining:
            first = min(remaining)
            orbit = move_orbit(first, table, symmetries)
            remaining.difference_update(orbit)
            orbits[j].append(tuple(sorted(orbit)))
    return orbits


def transitions(game, classification, orbits, rules):
    _, _, observation_ids, to_physical = classification
    edges = []
    for i, position in enumerate(game.positions):
        available_endpoints = set(position.endpoint_pairs())
        row = []
        for orbit in orbits[observation_ids[i]]:
            outcomes = set()
            for action in orbit:
                move = rename_move(action, to_physical[i])
                if (
                    rules.filter_endpoint_selection and move[0] in ("erase", "replace")
                    and move[1][:2] not in available_endpoints
                ):
                    continue
                outcomes.update(game.physical_step(position, move, rules.horizontal))
            row.append(frozenset(outcomes or {UNAVAILABLE}))
        edges.append(tuple(row))
    return tuple(edges)


def exact_search(game, edges, observation_ids, optimistic):
    """Exhaust every feasible uniform continuation using actual reachable types."""
    nodes = 0

    def visit(policy):
        nonlocal nodes
        nodes += 1
        try:
            _, frontier, reached, _ = game.inherited.evaluate_policy(
                game.start, policy, edges, observation_ids, optimistic
            )
        except ValueError:
            return False
        if not frontier:
            return True
        state = min(frontier)
        obs = observation_ids[state]
        relevant = tuple(i for i in reached if observation_ids[i] == obs)
        return any(
            visit({**policy, obs: choice})
            for choice in range(len(edges[state]))
            if all(edges[i][choice] <= optimistic.keys() for i in relevant)
        )

    return visit({}), nodes


def solve_ranks(game, classification, orbits, edges, optimistic):
    """Encode reachable states by positive integer ranks; every tie must decrease rank."""
    _, classes, observation_ids, _ = classification
    solver = z3.SolverFor("QF_BV")
    solver.set(random_seed=0)
    width = len(game.positions).bit_length()
    rank = [z3.BitVec(f"rank_{i}", width) for i in range(len(game.positions))]
    choice = [z3.BitVec(f"action_{i}", len(orbits[i]).bit_length()) for i in range(len(classes))]
    for i, value in enumerate(choice):
        solver.add(z3.ULT(value, len(orbits[i])))
    solver.add(rank[game.start] != 0)
    for i, before in enumerate(rank):
        solver.add(z3.ULE(before, len(rank)))
        if i not in optimistic:
            solver.add(before == 0)
            continue
        observed = choice[observation_ids[i]]
        for option, outcomes in enumerate(edges[i]):
            selected = z3.And(before != 0, observed == option)
            if outcomes <= optimistic.keys():
                successors = [n for n in sorted(outcomes) if n >= 0]
                solver.add(z3.Implies(selected, z3.And(*(
                    z3.And(rank[n] != 0, z3.ULT(rank[n], before)) for n in successors
                ))))
            else:
                solver.add(z3.Not(selected))
    status = solver.check()
    if status == z3.unsat:
        return None
    assert status == z3.sat
    witness = solver.model()
    policy = {i: witness.eval(value).as_long() for i, value in enumerate(choice)}
    longest, missing, reached, depth = game.inherited.evaluate_policy(
        game.start, policy, edges, observation_ids, optimistic
    )
    assert not missing and longest <= witness.eval(rank[game.start]).as_long()
    return policy, reached, depth


def describe_policy(game, classification, orbits, edges, result):
    representatives, _, observation_ids, _ = classification
    policy, reached, depth = result
    return [
        {
            "physical_position": i,
            "observed_class": obs,
            "representative_for_labels": representatives[obs],
            "action_on_representative": orbits[obs][policy[obs]][0],
            "all_tied_actions_on_representative": len(orbits[obs][policy[obs]]),
            "possible_successors": sorted(edges[i][policy[obs]]),
            "worst_remaining_moves": depth[i],
        }
        for i in sorted(reached, key=lambda i: (-depth[i], i))
        for obs in (observation_ids[i],)
    ]


def reached_commitments(game, classification, orbits, result):
    _, _, observation_ids, to_physical = classification
    policy, reached, _ = result
    for i in sorted(reached):
        obs = observation_ids[i]
        chosen = orbits[obs][policy[obs]]
        if chosen[0][0] == "second":
            for action in chosen:
                _, inputs = rename_move(action, to_physical[i])
                yield game.positions[i], inputs


def check_horizontal_finish(game, classification, orbits, result):
    """Use the marked mate relation for one erase at a time after the commitment."""
    direct = None
    finish_count = 0
    tests_left = Counter()
    for position, (port, original) in reached_commitments(game, classification, orbits, result):
        assert port in PORTS and original.bit_count() == 1
        before = game.permanent_rows(position)
        after = game.source.parity_extension(before, 10, (port, original))
        tests = position.tests
        width = 12
        rows = game.adjoin_probes(after, width, tests)
        # Remake the observation after each erase, independently renaming all labels.
        active = [(width + 2 * j, width + 2 * j + 1) for j in range(len(tests))]
        tests_left[len(active)] += 1
        total_width = width + 2 * len(tests)
        labels = list(range(total_width))
        while active:
            shuffle = labels.copy()
            Random(finish_count + len(labels) + 194).shuffle(shuffle)
            rename = dict(zip(labels, shuffle, strict=True))
            observed_pairs = {
                tuple(sorted((rename[p], rename[q]))): (p, q) for p, q in active
            }
            # Every marked choice is a real probe. Grade the marginal for every tie.
            for named in sorted(observed_pairs):
                p, q = observed_pairs[named]
                keep = ((1 << total_width) - 1) ^ (1 << p) ^ (1 << q)
                remaining = tuple(test for test, pair in zip(tests, active, strict=True) if pair != (p, q))
                target = game.adjoin_probes(after, width, remaining)
                # Pack the surviving labels in their current order after erasure.
                retained = [i for i in labels if keep >> i & 1]
                actual = {
                    sum(((row >> bit) & 1) << i for i, bit in enumerate(retained))
                    for row in rows
                }
                assert actual == target
            # Each tied choice has the same proof. Follow one representative.
            p, q = observed_pairs[min(observed_pairs)]
            retained = [i for i in labels if i not in (p, q)]
            rows = {sum(((row >> bit) & 1) << i for i, bit in enumerate(retained)) for row in rows}
            tests = tuple(test for test, pair in zip(tests, active, strict=True) if pair != (p, q))
            total_width -= 2
            labels = list(range(total_width))
            active = [(width + 2 * j, width + 2 * j + 1) for j in range(len(tests))]
        assert rows == after and {row & 255 for row in after} == game.seed
        # Put the marked original on the first classical axis and its chosen port at 8.
        perm = next(
            p for p in game.symmetries[True] if p[original] == 1 and p[port] == 8
        ) + (10, 11)
        normalized = {
            sum(((row >> i) & 1) << j for i, j in enumerate(perm)) for row in after
        }
        if direct is None:
            direct = game.source.parity_extension(game.permanent_rows(Position(True, ())), 10, (8, 1))
        assert normalized == direct and len(after) == 32
        finish_count += 1
    assert finish_count and direct is not None
    return {
        "legal_horizontal_commitment_ties_checked": finish_count,
        "live_instrument_counts_at_commitment": dict(tests_left),
        "unprobed_width": 12,
        "unprobed_states": len(direct),
        "unprobed_parity_scopes_after_relabelling": ((0, 8, 9), (8, 1, 10, 11)),
        "original_rows": len(game.seed),
    }


def threshold_two(rows, width):
    """Obtain the exact distance-two table by literal projections."""
    table = [[0 if i == j else None for j in range(width)] for i in range(width)]
    assert all(len({row & ((1 << a) | (1 << b)) for row in rows}) == 4
               for a, b in combinations(range(width), 2))
    for triple in combinations(range(width), 3):
        mask = sum(1 << bit for bit in triple)
        if len({row & mask for row in rows}) < 8:
            for a, b in combinations(triple, 2):
                table[a][b] = table[b][a] = 2
    return tuple(map(tuple, table))


def check_physical_reduction(game, relations):
    """Transport whole rows to check the old and port symmetries used in the arena."""
    covered = set()
    for position, rows in zip(game.positions, relations, strict=True):
        for perm in game.symmetries[position.rooted]:
            renamed = [tuple(sorted(perm[i] for i in test)) for test in position.tests]
            order = sorted(range(len(renamed)), key=renamed.__getitem__)
            target = Position(position.rooted, tuple(renamed[i] for i in order))
            if target in covered:
                continue
            probes = tuple(
                position.genuine + 2 * order.index(i) + side
                for i in range(len(renamed)) for side in (0, 1)
            )
            labels = perm[:position.genuine] + probes
            assert set(labels) == set(range(position.width))
            projected = {
                sum(((row >> i) & 1) << j for i, j in enumerate(labels)) for row in rows
            }
            assert projected == game.rows(target)
            covered.add(target)
    assert covered == set(game.raw)
    return len(covered)


def bulk_templates():
    return (
        (Position(False, ()), ("root", (0,)), 6),
        (Position(True, ()), ("add", (1, 8)), 5),
        (Position(True, ((1, 8),)), ("add", (0, 1)), 4),
        (Position(True, ((0, 7), (7, 8))), ("configure_two", (7, 8, 7, 9)), 3),
        (Position(True, ((7, 8), (7, 9))), ("configure_two", (0, 1, 1, 8)), 2),
        (Position(True, ((0, 1), (1, 8))), ("second", (8, 1)), 1),
        (Position(True, ((0, 3), (3, 8))), ("second", (8, 1)), 1),
    )


def direct_bulk_policy(game, d2):
    """Reach the horizontal interface with two label-free bulk reconfigurations."""
    demonstrations = bulk_templates()
    templates = []
    for physical, move, rank in demonstrations:
        table = threshold_two(game.rows(physical), physical.width)
        numbered = game.inherited.make_observation(table, (0,) * physical.width)
        symmetries = tuple(game.inherited.quotient_maps(numbered, numbered))
        sharp = move_orbit(move, numbered, symmetries)
        assert all(next(game.inherited.quotient_maps(known, numbered), None) is None
                   for known, *_ in templates)
        templates.append((numbered, sharp, rank, physical))

    def on_current_matrix(table):
        current = game.inherited.make_observation(table, (0,) * len(table))
        matches = [
            (known, tied, rank, source, isometry)
            for known, tied, rank, source in templates
            if (isometry := next(game.inherited.quotient_maps(known, current), None)) is not None
        ]
        (known, tied, rank, source, isometry), = matches
        transport = game.inherited.lift(known, current, isometry)
        return {rename_move(move, transport) for move in tied}, rank, source

    moves_to_check = {game.start}
    seen = set()
    joins = []
    checkpoints = []
    while moves_to_check:
        current = min(moves_to_check)
        moves_to_check.remove(current)
        if current in seen:
            continue
        seen.add(current)
        position = game.positions[current]
        table = d2[current]
        assert table == threshold_two(game.rows(position), position.width)
        moves, rank, template = on_current_matrix(table)
        shuffled = list(range(position.width))
        Random(343 + current).shuffle(shuffled)
        relabelled = tuple(tuple(table[a][b] for b in shuffled) for a in shuffled)
        shuffled_moves, shuffled_rank, _ = on_current_matrix(relabelled)
        assert shuffled_rank == rank and {rename_move(move, shuffled) for move in shuffled_moves} == moves
        after = set()
        for move in sorted(moves):
            (successor,) = game.physical_step(position, move, True)
            if successor == GOAL:
                joins.append((position, move[1]))
            else:
                assert successor >= 0 and on_current_matrix(d2[successor])[1] < rank
                moves_to_check.add(successor)
            after.add(successor)
        checkpoints.append({
            "position": position.record(), "template": template.record(),
            "action": demonstrations[next(i for i, item in enumerate(demonstrations) if item[0] == template)][1],
            "tied_choices": len(moves), "possible_successors": sorted(after),
        })
    assert len(templates) == 7 and len(checkpoints) == 9 and len(joins) == 3
    # The worst path goes through the opposite and the repeated older middle.
    cleanup, _ = anonymous_cleanup(game, joins)
    return {
        "guaranteed_from_threshold_two_alone": True,
        "maximum_moves_through_horizontal_join": 6,
        "maximum_moves_including_two_individual_erases": 8,
        "checkpoints": checkpoints,
        "clean_interface": cleanup,
    }


def cleanup_move(table):
    """Read the post-commitment phase and identify one whole pair to forget."""
    neighbors = {i: {j for j, delta in enumerate(row) if delta == 2} for i, row in enumerate(table)}
    assert sum(not near for near in neighbors.values()) == 2
    old = {i for i, near in neighbors.items() if len(near) >= 7}
    assert len(old) == 8
    if len(table) == 12:
        return "handoff", ()
    assert len(table) in (14, 16)
    if len(table) == 16:
        erase = {i for i in neighbors.keys() - old if len(neighbors[i] & old) >= 2}
    else:
        erase = {i for i in neighbors.keys() - old if len(neighbors[i]) == 3}
    assert len(erase) == 2 and erase <= neighbors[min(erase)] | {min(erase)}
    return "erase", tuple(sorted(erase))


def anonymous_cleanup(game, joins, observe=threshold_two):
    direct = game.source.parity_extension(game.permanent_rows(Position(True, ())), 10, (8, 1))
    receipts, events = [], []
    for position, (port, other) in joins:
        before = game.permanent_rows(position)
        bare = game.source.parity_extension(before, 10, (port, other))
        probe_specs = position.tests
        rows = game.adjoin_probes(bare, 12, probe_specs)
        while probe_specs:
            width = 12 + 2 * len(probe_specs)
            exact = threshold_two(rows, width)
            roster = list(range(width))
            Random(521 + width + port + other).shuffle(roster)
            renamed = tuple(tuple(exact[i][j] for j in roster) for i in roster)
            assert rename_move(cleanup_move(renamed), roster) == cleanup_move(exact)
            operation, named = cleanup_move(exact)
            assert operation == "erase"
            events.append((observe(rows, width), operation, named))
            index = next(j for j in range(len(probe_specs)) if named == (12 + 2 * j, 13 + 2 * j))
            retain = sorted(set(roster) - set(named))
            rows = {
                sum(((row >> bit) & 1) << i for i, bit in enumerate(retain))
                for row in rows
            }
            probe_specs = probe_specs[:index] + probe_specs[index+1:]
            assert rows == game.adjoin_probes(bare, 12, probe_specs)
        axis = next(p for p in game.symmetries[True] if p[port] == 8 and p[other] == 1) + (10, 11)
        normalized = {
            sum(((row >> a) & 1) << b for a, b in enumerate(axis)) for row in bare
        }
        assert rows == bare and normalized == direct
        assert {row & 255 for row in bare} == game.seed
        receipts.append({"second": (port, other), "tested_before_join": position.tests})
        operation, operands = cleanup_move(threshold_two(bare, 12))
        assert operation == "handoff"
        events.append((observe(bare, 12), operation, operands))
    return {
        "successful_join_ties": receipts,
        "unprobed_width": 12, "unprobed_states": len(direct), "original_rows": len(game.seed),
        "normalized_parity_scopes": ((0, 8, 9), (8, 1, 10, 11)),
    }, tuple(events)


def bulk_observations(full=False):
    """Return (numeric matrix, action, operand IDs) for the checked start and cleanup."""
    game = PhysicalGame(load_predecessor())
    if full:
        observe = lambda rows, width: game.source.bond_table(rows, width)[0]
    else:
        observe = threshold_two
    starts = tuple(
        (observe(game.rows(position), position.width), *move)
        for position, move, _ in bulk_templates()
    )
    joins = (
        (Position(True, ((0, 1), (1, 8))), (8, 1)),
        (Position(True, ((0, 3), (3, 8))), (8, 1)),
        (Position(True, ((0, 3), (3, 8))), (8, 2)),
    )
    _, finishes = anonymous_cleanup(game, joins, observe)
    return starts + finishes


def analyze(game, classification, rules, check_by_search=False):
    orbits = action_roster(game, classification, rules)
    edges = transitions(game, classification, orbits, rules)
    optimistic = game.inherited.full_information_ranks(edges)
    result = solve_ranks(game, classification, orbits, edges, optimistic)
    record = {
        "observations": len(orbits),
        "action_orbits": sum(map(len, orbits.values())),
        "optimistic_winning_physical_types": len(optimistic) - 1,
        "optimistic_start_rank": optimistic.get(game.start),
        "uniform_first_neighbor_guarantee": result is not None,
    }
    if check_by_search:
        alternative, visited = exact_search(game, edges, classification[2], optimistic)
        assert alternative == (result is not None)
        record["exhaustive_uniform_search_nodes"] = visited
    if result is not None:
        record["worst_case_moves_through_commitment"] = result[2][game.start]
        record["reachable_policy"] = describe_policy(game, classification, orbits, edges, result)
        if rules.instrument_groups and rules.horizontal:
            record["individually_erased_horizontal_interface"] = check_horizontal_finish(
                game, classification, orbits, result
            )
    return record


def run():
    inherited = load_predecessor()
    game = PhysicalGame(inherited)
    relations = [game.rows(state) for state in game.positions]
    physically_checked = check_physical_reduction(game, relations)
    tables = tuple(
        game.source.bond_table(rows, state.width)[0]
        for state, rows in zip(game.positions, relations, strict=True)
    )
    classified = {
        marked: classify_observations(game, tables, marked)
        for marked in (False, True)
    }
    d2 = tuple(tuple(tuple(v if v in (0, 2) else None for v in row) for row in t) for t in tables)
    assert d2 == tuple(
        threshold_two(rows, state.width) for state, rows in zip(game.positions, relations, strict=True)
    )
    d2_classes = classify_observations(game, d2, False)
    controls = {
        "individually_addressed": Rules(),
        "automatic_erase_either_or_all": Rules(automatic_erase=True),
        "automatic_replace_either_or_all": Rules(automatic_erase=True, automatic_replace=True),
        "instrument_groups_visible": Rules(instrument_groups=True, horizontal=True),
        "filter_proposed_endpoints_to_actual_pairs": Rules(filter_endpoint_selection=True),
    }
    results = {
        label: analyze(game, classified[rules.instrument_groups], rules, label == "individually_addressed")
        for label, rules in controls.items()
    }
    results["individually_addressed_threshold_two_only"] = analyze(
        game, d2_classes, Rules(), check_by_search=True
    )
    results["simultaneously_configure_two"] = direct_bulk_policy(game, d2)
    results["simultaneously_create_two_only_when_idle"] = analyze(
        game, classified[False], Rules(create_two_from_idle=True), check_by_search=True
    )
    antipode = Position(True, ((0, 7), (7, 8)))
    i = game.index[antipode]
    assert tables[i] == inherited.direct_matrix(relations[i], antipode.width)
    alias = observation(game, antipode, tables[i], False)
    targets = {1, *antipode.endpoint_pairs()[0]}
    assert any(targets <= set(cell) for cell in alias.cells)
    return {
        "predecessor_checker_sha256": PREDECESSOR_DIGEST,
        "solver_version": z3.get_version_string(),
        "unreduced_positions_with_root_normalized": physically_checked,
        "physical_types": len(game.positions),
        "direct_threshold_two_replays": len(d2),
        "physical_index": {str(i): p.record() for i, p in enumerate(game.positions)},
        "terminal_codes": {"unavailable": UNAVAILABLE, "safe_second": GOAL, "misaligned": MISALIGNED},
        "antipodal_erase_alias_control": {"physical_position": i, "full_table_twin_groups": alias.cells},
        "results": results,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
