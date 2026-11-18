"""Exact states-only growth after knot erasure for the two STATE-RULES starts."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import time
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

import networkx as nx

Rows = tuple[int, ...]
Scope = tuple[int, int, int]
Forces = tuple[int, int]
Law = Counter[int]

STARTS = {
    "fan6": ((0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5)),
    "nonfan6": ((1, 2, 3), (1, 3, 4), (4, 1, 0), (0, 4, 5)),
}
START_NAMES = tuple(STARTS)
COMMON_PATTERNS = ((0, 1), (1, 0), (1, 1))
SIGNED_PATTERNS = ((0, 0), *COMMON_PATTERNS)
SOURCE = (
    Path(__file__).resolve().parents[3] / "experiments" / "STATE-RULES-20261117-001B"
    / "STATE-RULES-20261117-001B-E001_rules" / "rules.py"
)
SOURCE_DIGEST = "d1ee374ca2c6784bdbad72c32878d7c6a3c98c60a28da73f34f14f76c8d10172"


def seed_rows(width: int, knots: tuple[Scope, ...]) -> Rows:
    return tuple(
        row for row in range(1 << width)
        if all(
            ((row >> left) ^ (row >> right)) & 1
            or not (((row >> left) ^ (row >> middle)) & 1)
            for left, middle, right in knots
        )
    )


def state_columns(rows: Rows, width: int) -> tuple[Forces, ...]:
    full = (1 << len(rows)) - 1
    columns = [sum(((row >> bit) & 1) << index for index, row in enumerate(rows))
               for bit in range(width)]
    return tuple((full ^ column, column) for column in columns)


def candidates(columns: tuple[Forces, ...], pairs, signed: bool):
    """For each forbidden pair use its old values when the new value is zero."""
    patterns = SIGNED_PATTERNS if signed else COMMON_PATTERNS
    for left, right in pairs:
        for left_value, right_value in patterns:
            yield (
                columns[left][1 - left_value] & columns[right][1 - right_value],
                columns[left][left_value] & columns[right][right_value],
            ), (left, right, len(columns))


def irredundant_joins(forces: tuple[Forces, ...]):
    for i, (a0, a1) in enumerate(forces):
        yield (a0, a1), (i,)
        for j in range(i + 1, len(forces)):
            b0, b1 = forces[j]
            pair = pair0, pair1 = a0 | b0, a1 | b1
            if pair0 & pair1 or pair in (forces[i], forces[j]):
                continue
            yield pair, (i, j)
            for k in range(j + 1, len(forces)):
                c0, c1 = forces[k]
                triple = triple0, triple1 = pair0 | c0, pair1 | c1
                if triple0 & triple1:
                    continue
                if triple not in (pair, (a0 | c0, a1 | c1), (b0 | c0, b1 | c1)):
                    yield triple, (i, j, k)


def untied(forces: Forces, copies: set[Forces]) -> bool:
    zero, one = forces
    return bool(zero | one) and not zero & one and forces not in copies


def extend(representatives: Rows, width: int, forces: Forces) -> Rows:
    zero, one = forces
    new_bit = 1 << width
    complement = (new_bit << 1) - 1
    out = []
    for index, row in enumerate(representatives):
        if not (one >> index) & 1:
            out.extend((row, row ^ complement))
        if not (zero >> index) & 1:
            with_new = row | new_bit
            out.extend((with_new, with_new ^ complement))
    return tuple(sorted(out))


def cheapest(rows: Rows, width: int, signed: bool, local: tuple[Scope, ...] | None = None):
    """The retained-knot rule counts knot sets. The erased rule counts relations."""
    # A local constraint forces opposite new values on complementary old rows.
    # One representative per pair suffices. Conflicting forces kill an old row.
    representatives = rows[:len(rows) // 2]
    complement = (1 << width) - 1
    assert tuple(row ^ complement for row in representatives) == rows[len(representatives):][::-1]
    columns = state_columns(representatives, width)
    copies = set(columns)
    if signed:
        copies.update((one, zero) for zero, one in columns)

    old_pairs = (
        combinations(range(width), 2) if local is None
        else sorted({pair for knot in local for pair in combinations(sorted(knot), 2)})
    )
    options = tuple(candidates(columns, old_pairs, signed))
    forces = tuple(mask for mask, _ in options)
    if local is None:
        forces = tuple(dict.fromkeys(forces))

    most_forced = -1
    best = []
    for force, indexes in irredundant_joins(forces):
        forced_count = (force[0] | force[1]).bit_count()
        if forced_count < most_forced or not untied(force, copies):
            continue
        if forced_count > most_forced:
            most_forced, best = forced_count, []
        best.append((force, indexes))

    if local is None:
        distinct = sorted({force for force, _ in best})
        return [(extend(representatives, width, force), ()) for force in distinct]
    return [
        (extend(representatives, width, force), tuple(options[index][1] for index in indexes))
        for force, indexes in best
    ]


def recode(rows: Rows, permutation: tuple[int, ...], flips: int = 0) -> Rows:
    return tuple(sorted(
        sum(((row >> source) & 1) << target for source, target in enumerate(permutation))
        ^ flips for row in rows
    ))


class StateClasses:
    """Classify whole relations, using pair disagreements only to limit the search."""

    def __init__(self, signed: bool):
        self.signed = signed
        self.representatives = []
        self._seen = {}
        self._buckets = defaultdict(list)

    def intern(self, rows: Rows, width: int) -> int:
        cache_key = width, rows
        if cache_key in self._seen:
            return self._seen[cache_key]

        columns = state_columns(rows, width)
        weights = {}
        incidents = [[] for _ in range(width)]
        for left, right in combinations(range(width), 2):
            count = (columns[left][1] ^ columns[right][1]).bit_count()
            weight = abs(len(rows) - 2 * count) if self.signed else count
            weights[left, right] = weight
            incidents[left].append(weight)
            incidents[right].append(weight)
        signatures = tuple(tuple(sorted(incident)) for incident in incidents)
        bucket = self._buckets[width, len(rows), tuple(sorted(signatures))]

        graph = nx.Graph()
        graph.add_nodes_from((coordinate, {"signature": signature})
                             for coordinate, signature in enumerate(signatures))
        graph.add_weighted_edges_from((left, right, w) for (left, right), w in weights.items())
        for class_id, reference, reference_set in bucket:
            matcher = nx.algorithms.isomorphism.GraphMatcher(
                graph, reference, node_match=lambda a, b: a == b, edge_match=lambda a, b: a == b
            )
            for order in matcher.isomorphisms_iter():
                moved = recode(rows, tuple(order[bit] for bit in range(width)))
                if self.signed:
                    # Any successful flip mask sends one fixed row to an allowed
                    # target row. One target per complement pair suffices.
                    target_rows = self.representatives[class_id]
                    masks = (moved[0] ^ target for target in target_rows[:len(target_rows) // 2])
                    equal = any(all(row ^ mask in reference_set for row in moved) for mask in masks)
                else:
                    equal = moved == self.representatives[class_id]
                if equal:
                    self._seen[cache_key] = class_id
                    return class_id

        class_id = len(self.representatives)
        # Only the anonymous table remains. A representative carries no mark
        # for any distinguished coordinate or record of the incoming move.
        self.representatives.append(rows)
        self._seen[cache_key] = class_id
        bucket.append((class_id, graph, frozenset(rows)))
        return class_id


def precut() -> tuple[dict, dict]:
    outcomes = {7: {}, 8: {}}
    branches = {}
    for start, knots in STARTS.items():
        rows = seed_rows(6, knots)
        assert len(rows) == 12
        first = cheapest(rows, 6, False, knots)
        assert len(first) == 4
        cut_seven, cut_eight, counts = [], [], []
        for after_one, added in first:
            second = cheapest(after_one, 7, False, knots + added)
            assert second
            cut_seven.append((after_one, Fraction(1, len(first))))
            cut_eight.extend((after_two, Fraction(1, len(first) * len(second)))
                             for after_two, _ in second)
            counts.append(len(second))
        assert len(cut_eight) == 24
        outcomes[7][start] = cut_seven
        outcomes[8][start] = cut_eight
        branches[start] = {"first_moves": len(first), "second_moves_per_first": sorted(counts)}
    return outcomes, branches


def mixture(outcomes: dict, width: int, classes: StateClasses) -> tuple[Law, Law]:
    distributions = tuple(Counter() for _ in START_NAMES)
    for name, dist in zip(START_NAMES, distributions):
        for rows, probability in outcomes[name]:
            dist[classes.intern(rows, width)] += probability
    return distributions


def hamming_histogram(rows: Rows, width: int) -> tuple[int, ...]:
    counts = Counter((left ^ right).bit_count() for left, right in combinations(rows, 2))
    return tuple(counts[index] for index in range(width + 1))


def variation(left: Counter, right: Counter) -> Fraction:
    return Fraction(sum(abs(left[key] - right[key]) for key in left.keys() | right.keys()), 2)


def describe_layer(width: int, laws: tuple[Law, Law], stopped: tuple[Fraction, Fraction],
                   classes: StateClasses, *, retain_rows: bool = True) -> dict:
    left, right = laws
    keys = sorted(left.keys() | right.keys(), key=classes.representatives.__getitem__)
    norms = [sum(law.values()) + stall for law, stall in zip(laws, stopped)]
    assert norms == [1, 1]
    tv = variation(left, right) + abs(stopped[0] - stopped[1]) / 2
    histograms = (Counter(), Counter())
    class_records = []
    for key in keys:
        rows = classes.representatives[key]
        histogram = hamming_histogram(rows, width)
        for law, coarse in zip(laws, histograms):
            coarse[histogram] += law[key]
        if retain_rows:
            class_records.append({
                "rows": rows,
                "fan6_probability": str(left[key]),
                "nonfan6_probability": str(right[key]),
            })
    histogram_tv = variation(*histograms) + abs(stopped[0] - stopped[1]) / 2
    assert histogram_tv <= tv
    record = {
        "width": width,
        "classes_per_start": [len(left), len(right)],
        "union_classes": len(keys),
        "shared_classes": len(left.keys() & right.keys()),
        "probability_sums": list(map(str, norms)),
        "stalled_probability": list(map(str, stopped)),
        "total_variation": str(tv),
        "recognition": str((1 + tv) / 2),
        "hamming_histogram_total_variation": str(histogram_tv),
        "hamming_histogram_recognition": str((1 + histogram_tv) / 2),
    }
    if retain_rows:
        record["class_records"] = class_records
    return record


def relabel_check(rows: Rows, width: int, signed: bool, extensions: list[Rows]) -> dict:
    reversal = tuple(reversed(range(width)))
    old_flip = 0b101010101 & ((1 << width) - 1) if signed else 0
    moved = recode(rows, reversal, old_flip)
    actual = {target for target, _ in cheapest(moved, width, signed)}
    new_flip = old_flip | (1 << width) if signed else 0
    expected = {recode(target, (*reversal, width), new_flip) for target in extensions}
    assert actual == expected
    return {"width": width, "checked_extensions": len(expected), "passes": True}


def propagate(outcomes: dict, cut: int, signed: bool) -> dict:
    classes = StateClasses(signed)
    laws = mixture(outcomes, cut, classes)
    stopped = [Fraction(), Fraction()]
    layers = [describe_layer(cut, laws, tuple(stopped), classes)]
    checks = []
    for width in range(cut, 10):
        t0 = time.perf_counter()
        next_laws = (Counter(), Counter())
        active_keys = sorted(laws[0].keys() | laws[1].keys())
        for index, class_id in enumerate(active_keys):
            rows = classes.representatives[class_id]
            extensions = [target for target, _ in cheapest(rows, width, signed)]
            if index == 0:
                checks.append(relabel_check(rows, width, signed, extensions))
            if not extensions:
                for start_index, law in enumerate(laws):
                    stopped[start_index] += law[class_id]
                continue
            multiplicities = Counter(classes.intern(target, width + 1) for target in extensions)
            for target, count in multiplicities.items():
                probability = Fraction(count, len(extensions))
                for prior, posterior in zip(laws, next_laws):
                    if class_id in prior:
                        posterior[target] += prior[class_id] * probability
        laws = next_laws
        layer = describe_layer(width + 1, laws, tuple(stopped), classes)
        assert Fraction(layer["total_variation"]) <= Fraction(layers[-1]["total_variation"])
        layer["transition_seconds"] = round(time.perf_counter() - t0, 6)
        layers.append(layer)
    return {"layers": layers, "relabel_checks": checks}


def controls() -> dict:
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_DIGEST
    spec = importlib.util.spec_from_file_location("frozen_state_rules", SOURCE)
    frozen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(frozen)
    compared = []
    for width in (3, 4, 5):
        rows = seed_rows(width, tuple((0, mid, mid + 1) for mid in range(1, width - 1)))
        known = frozen.extensions(list(rows), width, 3)
        best = min(zero.bit_count() + one.bit_count() for zero, one in known)
        expected = {tuple(frozen.apply(list(rows), width, zero, one)) for zero, one in known
                    if zero.bit_count() + one.bit_count() == best}
        actual = {target for target, _ in cheapest(rows, width, False)}
        assert actual == expected
        compared.append({"width": width, "checked_extensions": len(expected)})

    columns = set(state_columns((0, 1), 2))
    signed_copies = columns | {(one, zero) for zero, one in columns}
    assert not untied((0, 0), signed_copies)
    assert not untied((1, 1), signed_copies)
    assert untied((0, 3), columns) and not untied((0, 3), signed_copies)
    assert not untied((3, 0), signed_copies)
    rows = seed_rows(3, ((0, 1, 2),))
    extensions = [target for target, _ in cheapest(rows, 3, True)]
    assert set(SIGNED_PATTERNS) == {
        (u ^ flip_u ^ flip_p, v ^ flip_v ^ flip_p)
        for u, v in COMMON_PATTERNS for flip_u, flip_v, flip_p in product((0, 1), repeat=3)
    }
    nonconstant_orientation = recode(rows, (0, 1, 2), 2)
    assert 0 not in nonconstant_orientation and 7 not in nonconstant_orientation
    assert cheapest(nonconstant_orientation, 3, True)
    return {
        "frozen_common_rule_agreement": compared,
        "rejects_free_killed_and_copy": True,
        "signed_rejects_complementary_copy": True,
        "signed_requires_no_constant_rows": True,
        "signed_atom_orbit": SIGNED_PATTERNS,
        "synthetic_signed_relabel_check": relabel_check(rows, 3, True, extensions),
    }


def run() -> dict:
    started = time.perf_counter()
    control_results = controls()
    outcomes, branches = precut()
    baselines = {}
    baseline_accuracies = {(7, False): "7/8", (7, True): "1/2",
                           (8, False): "249/280", (8, True): "26/35"}
    for (width, signed), expected in baseline_accuracies.items():
        classes = StateClasses(signed)
        laws = mixture(outcomes[width], width, classes)
        layer = describe_layer(width, laws, (Fraction(), Fraction()), classes)
        assert layer["recognition"] == expected
        if width == 7 and signed:
            assert laws[0] == laws[1]
        baselines[f"{width}_{'independent' if signed else 'common'}"] = layer

    common_seven = propagate(outcomes[7], 7, False)
    independent_eight = propagate(outcomes[8], 8, True)
    return {
        "start_names": START_NAMES,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "controls": control_results,
        "precut_branch_counts": branches,
        "cut_baselines": baselines,
        "seven_common": common_seven,
        "seven_independent": {
            "method": "Identical cut laws and the same equivariant transition",
            "derived_recognition": {width: "1/2" for width in (8, 9, 10)},
            "derived_total_variation": {width: "0" for width in (8, 9, 10)},
        },
        "eight_independent": independent_eight,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="Run only synthetic controls")
    parser.add_argument("--output", type=Path, help="Write the JSON result to this path")
    args = parser.parse_args()
    result = controls() if args.smoke else run()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
