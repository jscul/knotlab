"""Exact prepared mass and the four accessible cuts of the ordinary devices."""

from dataclasses import dataclass
from functools import cache
from itertools import product
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
BINARY = (0, 1)
TYPES = tuple(product(BINARY, repeat=2))
WORDS = tuple(product(BINARY, repeat=3))
I, P, Q = (0, 1, 2), (1, 0, 2), (0, 2, 1)
PHYSICAL = ROOT / ("artifacts/WHOLE-STAGE-SETTINGS-20261120-001C/"
                   "WHOLE-STAGE-SETTINGS-20261120-001C-E001_masking/physical.json")
CURRENT = ROOT / ("artifacts/LOCAL-EDIT-POLICIES-20261123-001C/"
                  "LOCAL-EDIT-POLICIES-20261123-001C-E001_hidden_demand/kernels.json")


def allowed(values, law):
    total = sum(values)
    return total % 2 == 0 if law == "parity" else 0 < total < len(values)


@cache
def endpoint(law, label):
    """Sum the seven literal supports on one end, with the detector word fixed."""
    bridge = {}
    for c0, c1 in TYPES:
        bridge[c0, c1] = 0
        for link0, link1, first, second in product(BINARY, repeat=4):
            live = (c0, c1)[label], link0, link1, first, second
            spent = (c0, c1)[1 - label], link0, link1
            bridge[c0, c1] += int(allowed(live, law) and allowed(spent, law))
    wire = {}
    for c, w in TYPES:
        wire[c, w] = sum(allowed((d0, d1, room), law) and allowed((d0, d1, w, c), law)
                         for d0, d1, room in WORDS)
    mapped = []
    for terminal in WORDS:
        total = 0
        for w0, w1 in TYPES:
            detector = sum(allowed((w0, w1, *terminal, *room), law) for room in WORDS)
            total += detector * sum(bridge[c0, c1] * wire[c0, w0] * wire[c1, w1] for c0, c1 in TYPES)
        mapped.append(total)
    return tuple(mapped)


def routing(u, v, mode):
    swap_a = P if u else I
    swap_b = (P if mode == "commuting" else Q) if v else I
    steps = [swap_a, swap_b] * 2
    if mode == "identity":
        steps = [I] * 4
    if mode == "reversed":
        steps = [swap_b, swap_a] * 2
    indexes = list(I)
    for step in steps:
        indexes = [step[d] for d in indexes]
    return tuple(indexes)


@cache
def transition(law, steps, permutation=I):
    if law == "parity":
        equal, different = 2 ** steps, 0
    else:
        equal, different = (5 ** steps + 1) // 2, (5 ** steps - 1) // 2
    lookup = (different, equal)
    return tuple(tuple(lookup[a[0] == b[permutation[0]]] * lookup[a[1] == b[permutation[1]]]
                       * lookup[a[2] == b[permutation[2]]] for b in WORDS) for a in WORDS)


@dataclass(frozen=True)
class WeightedState:
    labels: tuple
    detector: tuple
    guard: tuple
    mass: int

    def observes(self, side, mode):
        if mode == "detector":
            return self.detector[side]
        if mode == "guard":
            return self.guard[side]
        if mode == "guard_and_bit":
            return 2 * self.guard[side] + self.first_bit(side)
        if mode == "bit":
            return self.first_bit(side)
        if mode == "type":
            return self.labels[side]
        assert mode == "blind"
        return 0

    def first_bit(self, side):
        return self.detector[side] >> 2


def make_source(law, mode, device, masses=(1, 1, 1, 1)):
    if device == "concealed":
        ends = [endpoint(law, label) for label in BINARY]
        assert ends[0] == ends[1]
    else:
        assert device == "predecessor"
        previous_end = tuple(64 if law == "parity" else 567 if len(set(word)) == 1 else 648 for word in WORDS)
        ends = [previous_end] * 2
    end_to_cut = transition(law, 1)
    records = []
    unweighted = []
    for labels, units in zip(TYPES, masses, strict=True):
        u, v = labels
        middle = transition(law, 6, routing(u, v, mode))
        subtotal = 0
        for d0, d1, z0, z1 in product(range(8), repeat=4):
            w = ends[u][d0] * end_to_cut[d0][z0] * middle[z0][z1] * end_to_cut[z1][d1] * ends[v][d1]
            subtotal += w
            if w and units:
                records.append(WeightedState(labels, (d0, d1), (z0, z1), w * units))
        unweighted.append(subtotal)
    assert len(set(unweighted)) == 1
    return records, unweighted[0], sum(masses) * unweighted[0]


def check_new_kernels(law, records, total):
    published = json.loads(CURRENT.read_text())["laws"][law]["pair_kernels"]
    for left, right in product(("detector", "guard"), repeat=2):
        name = "_".join("terminal" if view == "detector" else view for view in (left, right))
        known = published[name]
        for labels in TYPES:
            observed = [[0] * 8 for _ in range(8)]
            for state in records:
                if state.labels == labels:
                    observed[state.observes(0, left)][state.observes(1, right)] += state.mass
            word = "".join(map(str, labels))
            entry = known[word]
            expected = entry if isinstance(entry, list) else entry["counts"]
            assert observed == expected and sum(map(sum, observed)) == total


def check_old_kernels(law, mode, records, total):
    published = json.loads(PHYSICAL.read_text())["modes"][mode]
    for labels in TYPES:
        observed = [[0] * 8 for _ in range(8)]
        for state in records:
            if state.labels == labels:
                a, b = state.detector
                observed[a][b] += state.mass
        word = "".join(map(str, labels))
        weights = published[word]["laws"][law]["old_terminal_weights"]
        assert observed == weights["counts"] and total == weights["old_assignments"]
