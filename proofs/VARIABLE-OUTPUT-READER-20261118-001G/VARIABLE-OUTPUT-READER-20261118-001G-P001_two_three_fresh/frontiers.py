"""Close the live-holder state space for all-two-fresh growth with small move budgets."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter, deque
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from itertools import combinations, permutations, product
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RULE = (
    ROOT / "proofs/CUBIC-FROM-A-KNOT-20261117-001"
    / "CUBIC-FROM-A-KNOT-20261117-001-P001_local_growth/check.py"
)
RULE_SHA = "038a6845675cbc158e1abd0b55e72addd935c4dee9e6bb8153abe82a543894e8"
MAX_UNARY = 3
MAX_TRIPLE = 2
MIN_SITES = 3
TARGET = 4
START = ((0, 1, 2),)
FRESH_FOR_PARENT_TEST = ("unused-a", "unused-b", "unused-c")


@cache
def original_rule():
    assert sha256(RULE.read_bytes()).hexdigest() == RULE_SHA
    spec = importlib.util.spec_from_file_location("frontier_parent_rule", RULE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def mask(indices):
    return sum(1 << i for i in indices)


def project(bits, order):
    return mask(i for i, former in enumerate(order) if bits >> former & 1)


@dataclass(frozen=True, order=True)
class Frontier:
    loose: tuple[int, ...]
    adjacent: tuple[int, ...]
    retired: tuple[int, ...]

    def restrict(self, order):
        return Frontier(
            tuple(self.loose[j] for j in order),
            tuple(project(self.adjacent[j], order) for j in order),
            tuple(sorted({new for old in self.retired
                          if (new := project(old, order)).bit_count() >= 2})),
        )


@cache
def canonical(frontier):
    """Quotient by every relabeling among live holders of equal loose count."""
    ordered = sorted(range(len(frontier.loose)), key=frontier.loose.__getitem__)
    groups = [tuple(i for i in ordered if frontier.loose[i] == count)
              for count in sorted(set(frontier.loose))]
    return min((frontier.restrict(order), order)
               for groups_in_order in product(*(permutations(group) for group in groups))
               for order in [sum(groups_in_order, ())])


@dataclass(frozen=True, order=True)
class State:
    frontier: Frontier
    unary: int
    triple: int
    sites: int

    def within_budget(self, size):
        return not (size == 1 and self.unary == MAX_UNARY or size == 3 and self.triple == MAX_TRIPLE)

    def record(self):
        return [self.unary, self.triple, self.sites, self.frontier.loose,
                self.frontier.adjacent, self.frontier.retired]


def possible_parents(frontier):
    witnesses = (*frontier.adjacent, *frontier.retired)

    def has_witness(group):
        target = mask(group)
        return any(target & found == target for found in witnesses)

    holders = range(len(frontier.loose))
    for size in (1, 2, 3):
        for parents in combinations(holders, size):
            if all(has_witness(pair) for pair in combinations(parents, 2)):
                if size < 3 or not has_witness(parents):
                    yield parents


def successor(state, parents):
    old = state.frontier
    newest = len(old.loose)
    loose = tuple(count - (i in parents) for i, count in enumerate(old.loose))
    adjacent = tuple(row | ((1 << newest) if i in parents else 0) for i, row in enumerate(old.adjacent))
    retired = (*old.retired, *(adjacent[i] for i, count in enumerate(loose) if count == 0))
    remaining = (*tuple(i for i, count in enumerate(loose) if count), newest)
    updated = Frontier((*loose, 2), (*adjacent, mask(parents)), retired).restrict(remaining)
    return State(canonical(updated)[0], state.unary + (len(parents) == 1),
                 state.triple + (len(parents) == 3), min(MIN_SITES, state.sites + 1))


def snapshot(scopes):
    """Compress a literal incidence independently of the quotient update."""
    rules = original_rule()
    owners, neighbors = rules.incidence(dict(enumerate(scopes)))
    loose = rules.loose_ports(owners)
    live = tuple(sorted(loose))
    names = {j: i for i, j in enumerate(live)}
    rows = {j: mask(names[i] for i in neighbors[j] if i in names) for j in neighbors}
    frontier = Frontier(tuple(len(loose[j]) for j in live), tuple(rows[j] for j in live),
                        tuple(sorted({rows[j] for j in neighbors if j not in names and rows[j].bit_count() >= 2})))
    normal, order = canonical(frontier)
    return normal, tuple(live[i] for i in order), loose


def literal_step(scopes, parents):
    """Replay the names with the original parent rule and exactly two new bits."""
    rules = original_rule()
    checks = dict(enumerate(scopes))
    owners, _ = rules.incidence(checks)
    loose = rules.loose_ports(owners)
    consumed = tuple(min(loose[j]) for j in parents)
    assert rules.legal_local_move(checks, consumed, FRESH_FOR_PARENT_TEST)
    fresh = (len(owners), len(owners) + 1)
    assert not set(fresh) & owners.keys()
    return (*scopes, (*consumed, *fresh)), {"parents": parents, "consumed": consumed, "fresh": fresh}


def verify_literal_moves(scopes, front, live, loose):
    rules = original_rule()
    checks = dict(enumerate(scopes))
    actual = {parents for size in (1, 2, 3) for parents in combinations(range(len(live)), size)
              if rules.legal_local_move(checks, tuple(min(loose[live[i]]) for i in parents), FRESH_FOR_PARENT_TEST)}
    matches = set(possible_parents(front))
    assert actual == matches
    return matches


def construction(history):
    scopes = START
    for parents in history:
        scopes, _ = literal_step(scopes, parents)
    return scopes


def controls():
    # The three children of the now-retired seed share a witness for each pair.
    # The seed is also a common witness for all three and rejects their join.
    fork = ((0,), (0,), (0,))
    star, _, _ = snapshot(construction(fork))
    assert star == Frontier((2, 2, 2), (0, 0, 0), (0b111,))
    parents = set(possible_parents(star))
    assert len([group for group in parents if len(group) == 2]) == 3 and (0, 1, 2) not in parents
    erased = Frontier(star.loose, star.adjacent, ())
    assert all(len(group) == 1 for group in possible_parents(erased))
    # Three pair children use both bits at each old parent. The three
    # retired witnesses now support distinct pairs, and none covers all three.
    three_pairs = (*fork, (1, 2), (1, 3), (2, 3))
    witnesses, _, _ = snapshot(construction(three_pairs))
    assert witnesses == Frontier((2, 2, 2), (0, 0, 0), (0b011, 0b101, 0b110))
    assert (0, 1, 2) in set(possible_parents(witnesses))
    merged = Frontier(witnesses.loose, witnesses.adjacent, (0b111,))
    assert (0, 1, 2) not in set(possible_parents(merged))
    next_scopes, _ = literal_step(construction(three_pairs), (4, 5, 6))
    assert sum(snapshot(next_scopes)[0].loose) == 5
    return {
        "retired_common_witness": {"history": fork, "all_pairs_legal": True, "triple_legal": False,
                                   "erasing_retired_masks_removes_all_pairs": True},
        "retired_distinct_pair_witnesses": {
            "history": three_pairs, "triple_legal": True, "union_of_masks_would_forbid_triple": True,
            "literal_triple_successor_has_five_loose_distinctions": True,
        },
    }


def explore():
    initial = State(snapshot(START)[0], 0, 0, 1)
    queue = deque([initial])
    representatives = {initial: START}
    ancestry = {initial: None}
    transitions = {}
    states_by_budget = Counter()
    widths_by_site_count = Counter()
    shortest = {}
    examined, edges, returning = 0, 0, 0
    while queue:
        state = queue.popleft()
        scopes = representatives[state]
        front, live, loose = snapshot(scopes)
        assert front == state.frontier and state.sites == min(MIN_SITES, len(scopes))
        width = sum(front.loose)
        assert width == 3 + state.unary - state.triple and width <= 6
        states_by_budget[(state.unary, state.triple)] += 1
        widths_by_site_count[(state.sites, width)] += 1
        if width == TARGET:
            shortest.setdefault((state.unary, state.triple, state.sites), state)
        moves = verify_literal_moves(scopes, front, live, loose)
        examined += len(moves)
        next_rows = []
        for parents in sorted(moves):
            if not state.within_budget(len(parents)):
                continue
            nxt = successor(state, parents)
            physical, action = literal_step(scopes, tuple(live[i] for i in parents))
            assert snapshot(physical)[0] == nxt.frontier
            edges += 1
            next_rows.append((parents, nxt))
            if nxt in representatives:
                returning += 1
                continue
            representatives[nxt] = physical
            ancestry[nxt] = state, action
            queue.append(nxt)
        transitions[state] = tuple(next_rows)
    assert set(transitions) == representatives.keys()
    assert all(target in transitions for next_rows in transitions.values() for _, target in next_rows)
    assert edges - returning == len(transitions) - 1

    def history(state):
        steps = []
        while ancestry[state] is not None:
            state, action = ancestry[state]
            steps.append(action)
        return tuple(reversed(steps))

    def witness(state):
        scopes = representatives[state]
        path = history(state)
        assert len(path) + 1 == len(scopes)
        assert construction(step["parents"] for step in path) == scopes
        return {
            "junctions": len(scopes), "unary_joins": state.unary, "three_parent_joins": state.triple,
            "history_after_three_place_seed": path, "junction_supports": scopes,
        }

    by_budget = [
        {"unary_joins": u, "three_parent_joins": t, "reachable_states": states_by_budget[u, t],
         "target_at_three_or_more_junctions": witness(shortest[u, t, MIN_SITES])
         if (u, t, MIN_SITES) in shortest else None}
        for t in range(MAX_TRIPLE + 1) for u in range(MAX_UNARY + 1) if states_by_budget[u, t]
    ]
    canonical_ids = {state: i for i, state in enumerate(sorted(transitions))}
    graph = [[state.record(), [(parents, canonical_ids[target]) for parents, target in transitions[state]]]
             for state in sorted(transitions)]
    digest = sha256(json.dumps(graph, separators=(",", ":")).encode()).hexdigest()
    possible = [state for (u, t, sites), state in shortest.items() if sites == MIN_SITES]
    return {
        "inherited_parent_rule_sha256": RULE_SHA,
        "caps": {"unary": MAX_UNARY, "three_parent": MAX_TRIPLE, "sites_saturated_at": MIN_SITES, "fresh_per_join": 2},
        "target_loose_distinctions": TARGET,
        "possible_target_budgets": [[t + 1, t] for t in range(MAX_TRIPLE + 1)],
        "tested_budgets": by_budget,
        "reachable_states": len(transitions),
        "legal_actions_before_budget_screen": examined,
        "validated_transitions_after_budget_screen": edges,
        "transitions_to_states_already_reached": returning,
        "fixed_point_sha256": digest,
        "states_by_saturated_site_count_and_loose_count": [
            [sites, width, n] for (sites, width), n in sorted(widths_by_site_count.items())
        ],
        "maximum_representative_junction_count": max(map(len, representatives.values())),
        "shortest_target": witness(min(possible, key=lambda state: len(representatives[state]))) if possible else None,
        "four_loose_but_only_two_junctions_control": witness(shortest[1, 0, 2]),
        "matched_controls": controls(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write frontiers.json")
    args = parser.parse_args()
    assert (ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001G/preregistration.md").is_file()
    content = json.dumps(explore(), sort_keys=True, indent=2) + "\n"
    target = HERE / "frontiers.json"
    if args.write:
        target.write_text(content)
    else:
        assert target.read_text() == content
        print("All-two-fresh frontier closure reproduced.")
