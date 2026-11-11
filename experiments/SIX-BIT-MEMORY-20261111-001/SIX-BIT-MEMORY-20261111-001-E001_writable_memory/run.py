"""Exact finite write/hold/read test for unsigned three-bit constraints.

State strings and port indices follow abcxyz. Roles are always ordered as
(reference, gate, sample, read). Every attempted port is selected with positive
uniform probability; a legal flip is accepted unless its port already matches
a held command. A phase stops on its first state matching all its commands.
The state contains no counter, extra register, or learned update rule.

The scorer enumerates all legal hidden moves. In a finite phase, completion
has probability one exactly when every reachable state can reach a terminal
hit. This does not guarantee completion against adversarial indefinite delay.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
from itertools import combinations, permutations, product
import json
from pathlib import Path
from time import perf_counter


NAMES = "abcxyz"
PORT_COUNT = len(NAMES)
TRIPLES = tuple(combinations(range(PORT_COUNT), 3))
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}
ROLES = tuple(permutations(range(PORT_COUNT), 4))
FIXED_ROLES = tuple(NAMES.index(name) for name in "axby")
ORIGINAL = ("abc", "ayz", "xbz", "xyc")
COMPLEMENTARY = ("xyz", "xbc", "ayc", "abz")


def bit(state: int, port: int) -> int:
    return (state >> (PORT_COUNT - port - 1)) & 1


def words(states) -> list[str]:
    return [format(state, f"0{PORT_COUNT}b") for state in sorted(states)]


def matches(state: int, commands: tuple[tuple[int, int], ...]) -> bool:
    return all(bit(state, port) == value for port, value in commands)


def pattern_indices(rules) -> tuple[int, ...]:
    return tuple(
        sorted(TRIPLE_INDEX[tuple(sorted(NAMES.index(name) for name in rule))] for rule in rules)
    )


def rule_names(pattern) -> list[str]:
    return ["".join(NAMES[port] for port in TRIPLES[index]) for index in pattern]


@dataclass(frozen=True)
class Phase:
    starts: frozenset[int]
    reached: frozenset[int]
    hits: frozenset[int]
    cannot_hit: frozenset[int]

    @property
    def almost_sure(self) -> bool:
        return bool(self.starts) and not self.cannot_hit

    def record(self) -> dict:
        return {
            "starts": words(self.starts),
            "reachable_before_or_at_first_hit": words(self.reached),
            "first_hits": words(self.hits),
            "reachable_states_unable_to_hit": words(self.cannot_hit),
            "almost_sure": self.almost_sure,
            "adversarial_indefinite_delay_possible": bool(self.reached - self.hits),
        }


class Base:
    def __init__(self, pattern):
        self.pattern = tuple(pattern)
        self.states = frozenset(
            state
            for state in range(1 << PORT_COUNT)
            if all(
                len({bit(state, port) for port in TRIPLES[index]}) > 1
                for index in self.pattern
            )
        )
        self.moves = {
            state: tuple(
                (port, state ^ (1 << (PORT_COUNT - port - 1)))
                for port in range(PORT_COUNT)
                if state ^ (1 << (PORT_COUNT - port - 1)) in self.states
            )
            for state in self.states
        }
        self._phases = {}
        self._writes = {}

    def fibre(self, commands: dict[int, int]) -> frozenset[int]:
        ordered = tuple(sorted(commands.items()))
        return frozenset(state for state in self.states if matches(state, ordered))

    def closure(self, starts, held: dict[int, int]) -> frozenset[int]:
        """All hidden legal moves while already matched held ports stay fixed."""
        found = set(starts)
        ordered = tuple(sorted(held.items()))
        assert all(state in self.states and matches(state, ordered) for state in found)
        pending = list(found)
        while pending:
            state = pending.pop()
            for port, target in self.moves[state]:
                if port not in held and target not in found:
                    found.add(target)
                    pending.append(target)
        return frozenset(found)

    def components(self, held: dict[int, int]) -> list[frozenset[int]]:
        remaining = set(self.fibre(held))
        result = []
        while remaining:
            component = self.closure({min(remaining)}, held)
            result.append(component)
            remaining.difference_update(component)
        return result

    def drive(self, starts, commands: dict[int, int]) -> Phase:
        """Stop at first hits; permit all free legal moves before those hits."""
        starts = frozenset(starts)
        ordered = tuple(sorted(commands.items()))
        key = (starts, ordered)
        if key in self._phases:
            return self._phases[key]
        assert starts <= self.states
        reached = set(starts)
        pending = list(starts)
        hits = set()
        reverse = {state: set() for state in starts}
        while pending:
            state = pending.pop()
            if matches(state, ordered):
                hits.add(state)
                continue
            for port, target in self.moves[state]:
                if port in commands and bit(state, port) == commands[port]:
                    continue
                reverse.setdefault(target, set()).add(state)
                if target not in reached:
                    reached.add(target)
                    pending.append(target)
        can_hit = set(hits)
        pending = list(hits)
        while pending:
            state = pending.pop()
            for previous in reverse.get(state, ()):
                if previous not in can_hit:
                    can_hit.add(previous)
                    pending.append(previous)
        phase = Phase(starts, frozenset(reached), frozenset(hits), frozenset(reached - can_hit))
        self._phases[key] = phase
        return phase

    def write(self, reference: int, gate: int, sample: int, value: int, starts=None) -> dict:
        if starts is None:
            starts = self.fibre({reference: 0, gate: 1})
        starts = frozenset(starts)
        key = (reference, gate, sample, value, starts)
        if key in self._writes:
            return self._writes[key]
        opened = self.drive(starts, {reference: 0, gate: 0})
        sampled = self.drive(opened.hits, {reference: 0, gate: 0, sample: value})
        shut = self.drive(sampled.hits, {reference: 0, gate: 1, sample: value})
        retained = self.closure(shut.hits, {reference: 0, gate: 1})
        result = {
            "phases": (opened, sampled, shut),
            "retained": retained,
            "almost_sure": all(phase.almost_sure for phase in (opened, sampled, shut)),
        }
        self._writes[key] = result
        return result

    def successful_roles(self) -> list[dict]:
        success = []
        for reference, gate, sample, read in ROLES:
            results = [self.write(reference, gate, sample, value) for value in (0, 1)]
            if not all(result["almost_sure"] for result in results):
                continue
            readings = [{bit(state, read) for state in result["retained"]} for result in results]
            for inverted in (False, True):
                if all(readings[value] == {value ^ int(inverted)} for value in (0, 1)):
                    success.append(
                        {
                            "ports": "".join(NAMES[port] for port in (reference, gate, sample, read)),
                            "inverted": inverted,
                        }
                    )
        return success


def read_probe(states, read: int) -> dict:
    """A supplied fresh NAE(read, p, q); the uncoupled port is unconstrained."""
    values = sorted({bit(state, read) for state in states})
    queries = [
        "".join(map(str, query))
        for query in product((0, 1), repeat=2)
        if any(len({value, *query}) > 1 for value in values)
    ]
    return {
        "possible_read_values": values,
        "coupled_allowed_queries_pq": queries,
        "coupled_equal_queries": {query: query in queries for query in ("00", "11")},
        "uncoupled_allowed_queries_pq": ["00", "01", "10", "11"],
    }


def witness_report(base: Base, roles=FIXED_ROLES) -> dict:
    reference, gate, sample, read = roles
    starts = base.fibre({reference: 0, gate: 1})
    histories = []
    for value in (0, 1):
        result = base.write(reference, gate, sample, value)
        histories.append(
            {
                "presented_value": value,
                "all_starts_almost_sure": result["almost_sure"],
                "all_possible_states_after_release": words(result["retained"]),
                "all_possible_readouts": sorted({bit(state, read) for state in result["retained"]}),
                "probe": read_probe(result["retained"], read),
                "starts": [
                    {
                        "initial": words({start})[0],
                        "phases": [phase.record() for phase in single["phases"]],
                        "after_release": words(single["retained"]),
                        "readouts": sorted({bit(state, read) for state in single["retained"]}),
                    }
                    for start in sorted(starts)
                    for single in [base.write(reference, gate, sample, value, {start})]
                ],
            }
        )
    return {
        "ports": "".join(NAMES[port] for port in roles),
        "neutral_starts": words(starts),
        "histories": histories,
    }


def base_report(pattern) -> dict:
    base = Base(pattern)
    success = base.successful_roles()
    neutral_fibres = [
        {
            "reference_gate": NAMES[reference] + NAMES[gate],
            "component_sizes": [len(component) for component in components],
            "components": [words(component) for component in components],
        }
        for reference, gate in permutations(range(PORT_COUNT), 2)
        for components in [base.components({reference: 0, gate: 1})]
    ]
    return {
        "rules": rule_names(pattern),
        "legal_states": words(base.states),
        "role_count": len(ROLES),
        "successful_role_count": len(success),
        "successful_roles": success,
        "neutral_fibres": neutral_fibres,
        "fixed_role_witness": witness_report(base),
    }


def original_controls() -> dict:
    base = Base(pattern_indices(ORIGINAL))
    reference, gate, sample, read = FIXED_ROLES
    release = []
    for value in (0, 1):
        retained = base.write(reference, gate, sample, value)["retained"]
        free = base.closure(retained, {})
        one_held = base.closure(retained, {reference: 0})
        release.append(
            {
                "presented_value": value,
                "release_entire_cue": {"states": words(free), "readouts": sorted({bit(s, read) for s in free})},
                "hold_reference_only": {"states": words(one_held), "readouts": sorted({bit(s, read) for s in one_held})},
                "same_complete_preparations_without_writing": words(retained),
            }
        )
    cue_only = []
    for start in sorted(base.fibre({reference: 0, gate: 1})):
        opened = base.drive({start}, {reference: 0, gate: 0})
        shut = base.drive(opened.hits, {reference: 0, gate: 1})
        retained = base.closure(shut.hits, {reference: 0, gate: 1})
        cue_only.append(
            {
                "initial": words({start})[0],
                "almost_sure_open_and_close": opened.almost_sure and shut.almost_sure,
                "states_after_release": words(retained),
                "readouts": sorted({bit(state, read) for state in retained}),
            }
        )
    fibre_summary = []
    for held_count in range(PORT_COUNT):
        counts = Counter()
        for held_ports in combinations(range(PORT_COUNT), held_count):
            for values in product((0, 1), repeat=held_count):
                components = base.components(dict(zip(held_ports, values)))
                if components:
                    counts[tuple(sorted(map(len, components)))] += 1
        fibre_summary.append(
            {
                "held_count": held_count,
                "component_shape_counts": [
                    {"sizes": list(shape), "cases": count} for shape, count in sorted(counts.items())
                ],
            }
        )
    return {"release_controls": release, "cue_only_pulse": cue_only, "all_fixed_cue_fibres": fibre_summary}


def census() -> dict:
    """Cover labeled four-rule patterns by complete permutation orbits."""
    mappings = [
        tuple(TRIPLE_INDEX[tuple(sorted(permutation[p] for p in triple))] for triple in TRIPLES)
        for permutation in permutations(range(PORT_COUNT))
    ]
    remaining = set(combinations(range(len(TRIPLES)), 4))
    labeled_count = len(remaining)
    rows = []
    while remaining:
        representative = min(remaining)
        orbit = {tuple(sorted(mapping[index] for index in representative)) for mapping in mappings}
        assert orbit <= remaining
        base = Base(representative)
        success = base.successful_roles()
        numerator = len(orbit) * len(success)
        assert numerator % len(ROLES) == 0
        # A successful role is transported along each relabeling. The set
        # counts a labeled pattern once even if it has several automorphisms.
        fixed_members = set()
        success_ports = {tuple(NAMES.index(name) for name in row["ports"]) for row in success}
        for permutation, mapping in zip(permutations(range(PORT_COUNT)), mappings):
            if any(tuple(permutation[p] for p in role) == FIXED_ROLES for role in success_ports):
                fixed_members.add(tuple(sorted(mapping[index] for index in representative)))
        fixed_count = numerator // len(ROLES)
        assert len(fixed_members) == fixed_count
        rows.append(
            {
                "rules": rule_names(representative),
                "orbit_size": len(orbit),
                "legal_state_count": len(base.states),
                "active_port_count": len({p for index in representative for p in TRIPLES[index]}),
                "successful_role_count": len(success),
                "successful_roles": success,
                "passing_any_roles": len(orbit) if success else 0,
                "passing_fixed_roles": fixed_count,
                "fixed_role_weight_numerator": numerator,
                "fixed_role_weight_denominator": len(ROLES),
            }
        )
        remaining.difference_update(orbit)
    assert sum(row["orbit_size"] for row in rows) == labeled_count
    return {
        "labeled_pattern_count": labeled_count,
        "orbit_count": len(rows),
        "fixed_roles": "".join(NAMES[p] for p in FIXED_ROLES),
        "passing_any_roles": sum(row["passing_any_roles"] for row in rows),
        "passing_fixed_roles": sum(row["passing_fixed_roles"] for row in rows),
        "successful_pattern_role_pairs": sum(row["fixed_role_weight_numerator"] for row in rows),
        "orbits": rows,
    }


def run() -> dict:
    started = perf_counter()
    original = base_report(pattern_indices(ORIGINAL))
    first_signal_seconds = perf_counter() - started
    complementary = base_report(pattern_indices(COMPLEMENTARY))
    deletions = [
        {"removed_rule": removed, **base_report(pattern_indices(rule for rule in ORIGINAL if rule != removed))}
        for removed in ORIGINAL
    ]
    free = base_report(())
    controls = original_controls()
    model_seconds = perf_counter() - started
    full_census = census()
    result = {
        "schema_version": 1,
        "experiment_id": "SIX-BIT-MEMORY-20261111-001-E001",
        "state_order": NAMES,
        "role_order": ["reference", "gate", "sample", "read"],
        "reference_value": 0,
        "neutral_gate_value": 1,
        "open_gate_value": 0,
        "phase_order": ["open", "hold_sample", "close_while_sampling"],
        "phase_completion": "first hit of all commands; all free legal flips included before the hit",
        "almost_sure_criterion": "every reachable state has a path to a terminal first hit",
        "original": original,
        "complementary": complementary,
        "deletions": deletions,
        "free": free,
        "controls": controls,
        "census": full_census,
        "runtime_seconds": {
            "first_original_report": first_signal_seconds,
            "models_and_controls": model_seconds,
            "census": perf_counter() - started - model_seconds,
            "total": perf_counter() - started,
        },
        "nonclaims": [
            "The sample, command order, completion sensing, uniform attempts and output connection are supplied.",
            "Storing a supplied sample does not adapt an unknown rule or form the meeting pattern.",
            "Probability-one completion does not exclude indefinitely stalling adversarial schedules.",
            "The fixed six-bit census has no infinite or general learning implication.",
        ],
    }
    here = Path(__file__).resolve().parent
    result["contract_sha256"] = hashlib.sha256((here / "contract.json").read_bytes()).hexdigest()
    result["producer_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="-", help="JSON destination; '-' or no option writes to stdout")
    arguments = parser.parse_args()
    result = run()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output == "-":
        print(payload, end="")
    else:
        destination = Path(arguments.output)
        with destination.open("x", encoding="utf-8") as output:
            output.write(payload)


if __name__ == "__main__":
    main()
