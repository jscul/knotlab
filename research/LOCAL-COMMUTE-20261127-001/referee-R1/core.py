"""Independent growth bookkeeping and binary linear algebra for the recount."""

import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import combinations, product
from pathlib import Path

import networkx as nx


ENGINE_DIR = Path(__file__).resolve().parents[2] / "FORBID-EDITS-20261126-001"
sys.path.insert(0, str(ENGINE_DIR))
import forbid


def start_knots(record):
    count, shared, loose = record
    holders = [(a, b) for a, b, copies in shared for _ in range(copies)]
    holders.extend((owner,) for owner, copies in enumerate(loose) for _ in range(copies))
    return tuple(tuple(d for d, owners in enumerate(holders) if k in owners) for k in range(count))


@cache
def read_starts():
    with (ENGINE_DIR / "starts.json").open() as source:
        return tuple(map(start_knots, json.load(source)))


def regenerated_starts():
    return tuple(map(start_knots, forbid.starts()))


class State:
    """Knots and permanent pair decisions through one completed growth round."""

    def __init__(self, knots, previous=None):
        self.knots = tuple(tuple(knot) for knot in knots)
        old_knots = 0 if previous is None else len(previous.knots)
        old_rounds = () if previous is None else previous.knot_round
        self.round = 0 if previous is None else previous.round + 1
        assert self.knots[:old_knots] == (() if previous is None else previous.knots)
        self.knot_round = old_rounds + (self.round,) * (len(self.knots) - old_knots)

        holders = defaultdict(list)
        for knot_id, knot in enumerate(self.knots):
            assert len(knot) == len(set(knot))
            for distinction in knot:
                holders[distinction].append(knot_id)
        self.holders = {d: tuple(ids) for d, ids in holders.items()}
        assert all(1 <= len(ids) <= 2 for ids in self.holders.values())
        self.distinction_round = {d: self.knot_round[ids[0]] for d, ids in self.holders.items()}

        self.decision_counts = Counter()
        self.decision_examples = {}
        newly_eligible = []
        for left, right in combinations(sorted(self.holders), 2):
            left_round = self.distinction_round[left]
            right_round = self.distinction_round[right]
            if max(left_round, right_round) != self.round:
                continue
            left_holders = self.holders[left]
            right_holders = self.holders[right]
            shared_holder = any(knot in right_holders for knot in left_holders)
            twice_held = max(len(left_holders), len(right_holders)) == 2
            category = (
                "same round" if left_round == right_round else "mixed age",
                "held together" if shared_holder else "held apart",
                "one held twice" if twice_held else "both loose",
            )
            self.decision_counts[category] += 1
            self.decision_examples.setdefault(category, (left, right))
            if twice_held and not shared_holder:
                newly_eligible.append((left, right))

        self.new_birth_pairs = tuple(newly_eligible)
        earlier_pairs = () if previous is None else previous.birth_pairs
        self.birth_pairs = tuple(sorted(earlier_pairs + self.new_birth_pairs))

    @property
    def closed(self):
        return all(len(ids) == 2 for ids in self.holders.values())

    @property
    def whole_pairs(self):
        coheld = {pair for knot in self.knots for pair in combinations(sorted(knot), 2)}
        return tuple(pair for pair in combinations(sorted(self.holders), 2) if pair not in coheld)


@dataclass(frozen=True)
class History:
    states: tuple[State, ...]
    births: tuple[tuple[dict, ...], ...]
    end: str
    attempted_round: int
    attempted_knots: int


def history(start, rounds=4, cap=40):
    """A cut records the attempted size and keeps the preceding admitted states."""
    states = [State(start)]
    births = [()]
    while True:
        current = states[-1]
        if current.closed:
            end = "closed"
            break
        later, status, records = forbid.grown(current.knots, "parity", "ordinary")
        if status == "stalled":
            end = "stalled"
            break
        assert status == "funded", status
        if current.round == rounds:
            end = "growing"
            break
        if len(later) > cap:
            return History(tuple(states), tuple(births), "cut", current.round + 1, len(later))
        states.append(State(later, current))
        births.append(tuple(records))
    return History(tuple(states), tuple(births), end, current.round, len(current.knots))


def commutation(state, pairs):
    """One binary row per pair of knots, with its columns in the supplied order."""
    columns = {pair: 1 << index for index, pair in enumerate(pairs)}
    for first, second in combinations(state.knots, 2):
        row = 0
        for left, right in product(first, second):
            row ^= columns.get((left, right) if left < right else (right, left), 0)
        yield row


def first_natural_failure(state, previous=None):
    """Return the first newly tested knot pair failing when every eligible pair fails to commute."""
    earlier_knots = 0 if previous is None else len(previous.knots)
    failing_pairs = set(state.birth_pairs)
    for high in range(earlier_knots, len(state.knots)):
        second = state.knots[high]
        for low in range(high):
            first = state.knots[low]
            failing = sum(
                (left, right) in failing_pairs or (right, left) in failing_pairs
                for left, right in product(first, second)
            )
            if failing % 2:
                return low, high
    return None


def closing_cost(state, pairs, knot_order=None):
    """Charge one interchange per failing pair while sorting the product word."""
    by_low = defaultdict(list)
    for index, (low, high) in enumerate(pairs):
        by_low[low].append((high, 1 << index))
    if knot_order is None:
        knot_order = range(len(state.knots))
    cost = 0
    prefix_parity = set()
    for knot in knot_order:
        for distinction in state.knots[knot]:
            for high, column in by_low.get(distinction, ()):
                if high in prefix_parity:
                    cost ^= column
            prefix_parity.symmetric_difference_update((distinction,))
    assert not prefix_parity, "the product of a closure's checks must omit every distinction"
    return cost


def basis(rows):
    """Echelon basis over GF(2), pivoting on the least set bit."""
    pivots = {}
    for row in rows:
        while row:
            pivot = (row & -row).bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return pivots


def remainder(vector, pivots):
    for pivot in sorted(pivots):
        if vector & (1 << pivot):
            vector ^= pivots[pivot]
    return vector


def indicator(distinctions):
    return sum(1 << d for d in distinctions)


def sharing_graph(state):
    """The literature's graph of knots meeting at twice-held distinctions."""
    graph = nx.Graph()
    graph.add_nodes_from(range(len(state.knots)))
    graph.add_edges_from(ids for ids in state.holders.values() if len(ids) == 2)
    return graph


def three_in_one_block(state, parents):
    return any(len(set(parents) & block) >= 3 for block in nx.biconnected_components(sharing_graph(state)))


def outerplanar(state):
    cone = sharing_graph(state)
    cone.add_edges_from((len(state.knots), knot) for knot in range(len(state.knots)))
    return nx.check_planarity(cone)[0]
