"""Exact fourth-addition laws after projecting the preceding three additions."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from itertools import combinations, permutations
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[3]
PREVIOUS = "FRESH-THREE-20261117-001"
PREVIOUS_FAMILY = PREVIOUS + "-E001_projection"
RULE_SOURCE = ROOT / "experiments" / PREVIOUS / PREVIOUS_FAMILY / "measure.py"
RULE_DIGEST = "3eac5f38800d98c6d0968257580b80b167ac522d7a5e990c4f80f015fc036f1e"
RESULT_SOURCE = ROOT / "artifacts" / PREVIOUS / PREVIOUS_FAMILY / "results.json"
RESULT_DIGEST = "2ad9a1f8824ef5649a6a1e6ed9cbf485d77b2125c77a3f8cb3eccd2737235d7f"
STARTS = ("fan6", "nonfan6")
FULL = 63
PARITY_CODE = sum(1 << word for word in range(8) if word.bit_count() % 2 == 0)


@dataclass(frozen=True)
class Observation:
    words: tuple[int, ...]
    triple_sizes: tuple[int, ...]
    all_pairs_free: bool

    @property
    def k(self) -> int:
        return self.triple_sizes[:3].count(6)


@dataclass(frozen=True)
class Context:
    cut: int
    columns: tuple[int, ...]
    fresh: tuple[int, ...]
    weight: Fraction
    choice_count: int
    marked: Counter
    unmarked: Counter
    k: Counter
    row_sizes: Counter

    def ref(self) -> dict:
        return {"cut_class": self.cut, "fresh_words": column_words(self.fresh)}


def column_words(columns: tuple[int, ...]) -> list[str]:
    return [f"{word:06b}" for word in columns]


def normalize(word: int, full: int) -> int:
    return min(word, word ^ full)


def verified_read(path: Path, digest: str) -> bytes:
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError(f"Frozen input digest changed: {path}")
    return data


def previous_rule():
    verified_read(RULE_SOURCE, RULE_DIGEST)
    spec = importlib.util.spec_from_file_location("fresh_three_growth", RULE_SOURCE)
    previous = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(previous)
    return previous


def permute(word: int, order: tuple[int, ...]) -> int:
    return sum(((word >> source) & 1) << dest for source, dest in enumerate(order))


def recoding_maps(width: int, marked: bool) -> tuple[tuple[int, ...], ...]:
    orders = (
        ((*order, width - 1) for order in permutations(range(width - 1)))
        if marked else permutations(range(width))
    )
    half = 1 << (width - 1)
    return tuple(
        tuple(normalize(permute(word, order) ^ flip, (half << 1) - 1) for word in range(half))
        for order in orders for flip in range(half)
    )


def recoded_support(code: int, mapping: tuple[int, ...]) -> int:
    return sum(1 << mapped for bit, mapped in enumerate(mapping) if (code >> bit) & 1)


def canonical_lookup(marked: bool) -> tuple[int, ...]:
    mappings = recoding_maps(4, marked)
    classes = [-1] * 256
    for code, previous_class in enumerate(classes):
        if previous_class == -1:
            for mapping in mappings:
                image = recoded_support(code, mapping)
                assert classes[image] in (-1, code)
                classes[image] = code
    return tuple(classes)


def project_word(word: int, kept: tuple[int, ...]) -> int:
    return sum(((word >> source) & 1) << dest for dest, source in enumerate(kept))


def row_words(columns: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        sum(((column >> row) & 1) << bit for bit, column in enumerate(columns))
        for row in range(6)
    )


def describe_support(code: int) -> Observation:
    words = tuple(sorted(word for word in range(16) if code & (1 << normalize(word, 15))))
    triple_sizes = tuple(
        len({project_word(word, kept) for word in words})
        for drop in range(4) for kept in [tuple(bit for bit in range(4) if bit != drop)]
    )
    all_pairs_free = all(
        {project_word(word, kept) for word in words} == set(range(4))
        for kept in combinations(range(4), 2)
    )
    return Observation(words, triple_sizes, all_pairs_free)


@cache
def four_support(fresh: tuple[int, ...], added: int) -> int:
    return sum(1 << word for word in {normalize(word, 15) for word in row_words((*fresh, added))})


def normalized_choices(previous, current: tuple[int, ...]) -> tuple[int, ...]:
    literal = previous.literal_extensions(current, FULL)
    if not literal:
        raise RuntimeError(
            f"No zero-cost option at width {len(current)} for columns {current}. "
            "Check the full minimization before drawing any conclusion."
        )
    quotient = Counter(normalize(column, FULL) for column in literal)
    assert len(literal) == len(set(literal)) and set(quotient.values()) == {2}
    assert not set(quotient).intersection(current)
    return tuple(sorted(quotient))


def replay_prefix(previous, root: tuple[int, ...], stages: list[dict]) -> dict:
    law = {root: Fraction(1)}
    histories = {root: 1}
    for stage in stages:
        assert stage["width_before"] == len(next(iter(law)))
        successor_law = Counter()
        successor_histories = Counter()
        branches = Counter()
        for current, probability in law.items():
            choices = normalized_choices(previous, current)
            branches[2 * len(choices)] += 1
            contribution = probability / len(choices)
            for added in choices:
                successor = tuple(sorted((*current, added)))
                successor_law[successor] += contribution
                successor_histories[successor] += 2 * histories[current]
        assert len(law) == stage["reachable_nodes_with_zero_cost_extension"]
        assert len(successor_law) == stage["distinct_column_sets_after"]
        assert sum(successor_histories.values()) == stage["literal_histories_after"]
        assert dict(branches) == {int(key): value for key, value in stage["literal_branch_count_histogram"].items()}
        assert sum(successor_law.values()) == 1 and stage["stalled_probability"] == "0"
        law, histories = successor_law, successor_histories
    return law


def classify_context(previous, cut: int, original: tuple[int, ...], current: tuple[int, ...],
                     weight: Fraction, lookups: tuple[tuple[int, ...], ...],
                     descriptions: tuple[Observation, ...]) -> tuple[int, Context]:
    fresh = tuple(column for column in current if column not in original)
    assert len(current) == 11 and len(fresh) == 3
    size = previous.observed_class(fresh, FULL)
    choices = normalized_choices(previous, current)
    marked, unmarked, k, row_sizes = (Counter() for _ in range(4))
    determined = []
    for added in choices:
        code = four_support(fresh, added)
        obs = descriptions[code]
        assert obs.all_pairs_free and set(obs.triple_sizes) <= {6, 8}
        assert obs.triple_sizes[3] == size
        tagged, anonymous = lookups[0][code], lookups[1][code]
        assert descriptions[tagged].k == obs.k and descriptions[tagged].triple_sizes[3] == size
        assert sorted(descriptions[anonymous].triple_sizes) == sorted(obs.triple_sizes)
        marked[tagged] += 1
        unmarked[anonymous] += 1
        k[obs.k] += 1
        row_sizes[len(obs.words)] += 1
        if len(obs.words) == size:
            determined.append(added)
    assert all(sum(counts.values()) == len(choices) for counts in (marked, unmarked, k, row_sizes))
    if size == 6:
        xor = normalize(fresh[0] ^ fresh[1] ^ fresh[2], FULL)
        assert determined == ([xor] if xor not in current else [])
    return size, Context(cut, current, fresh, weight, len(choices), marked, unmarked, k, row_sizes)


def recoded_context_control(previous, context: Context, size: int, lookups, descriptions) -> dict:
    width = len(context.columns)
    order = tuple(reversed(range(width)))
    flip = 0b10110101100
    mask = (1 << width) - 1
    moved = {permute(word, order) ^ flip for word in row_words(context.columns)}
    rows = tuple(sorted(moved | {word ^ mask for word in moved}))
    current, full = previous.cut_columns(rows, width)
    assert full == FULL
    fresh = {
        normalize(sum(((row >> target) & 1) << index for index, row in enumerate(rows[:6])), FULL)
        for position, target in enumerate(order) if context.columns[position] in context.fresh
    }
    original = tuple(column for column in current if column not in fresh)
    after_size, after = classify_context(
        previous, context.cut, original, current, context.weight, lookups, descriptions
    )
    assert after_size == size
    assert after.choice_count == context.choice_count
    assert (after.marked, after.unmarked, after.k, after.row_sizes) == (
        context.marked, context.unmarked, context.k, context.row_sizes,
    )
    return {
        **context.ref(),
        "triple_support_size": size,
        "matched_literal_options": 2 * context.choice_count,
        "full_conditional_laws_equal": True,
    }


def extrema(items: list[tuple[Fraction, Context]]) -> dict:
    low, low_context = min(items, key=lambda item: item[0])
    high, high_context = max(items, key=lambda item: item[0])
    return {
        "min": str(low), "at_min": low_context.ref(),
        "max": str(high), "at_max": high_context.ref(),
    }


def describe_channel(contexts: list[Context], channel: str, observations: tuple[Observation, ...]) -> dict:
    laws = set()
    supports = set()
    occurrence = Counter()
    extrema_by_class = {}
    for context in contexts:
        counts = getattr(context, channel)
        law = tuple(sorted((code, Fraction(count, context.choice_count)) for code, count in counts.items()))
        laws.add(law)
        supports.add(tuple(code for code, _ in law))
        for code, probability in law:
            point = probability, context
            occurrence[code] += 1
            if code not in extrema_by_class:
                extrema_by_class[code] = [point, point]
            else:
                ends = extrema_by_class[code]
                if probability < ends[0][0]:
                    ends[0] = point
                if probability > ends[1][0]:
                    ends[1] = point
    classes = []
    for code, items in sorted(extrema_by_class.items()):
        if occurrence[code] < len(contexts):
            absent = next(context for context in contexts if code not in getattr(context, channel))
            items.append((Fraction(), absent))
        desc = observations[code]
        classes.append({
            "canonical_support_code": code,
            "allowed_words": desc.words,
            "contexts_where_possible": occurrence[code],
            "conditional_probability_range": extrema(items),
        })
    return {
        "distinct_possible_outcome_sets": len(supports),
        "all_possible_outcome_sets_equal": len(supports) == 1,
        "distinct_conditional_laws": len(laws),
        "all_conditional_laws_equal": len(laws) == 1,
        "possible_outcome_count_range": [min(map(len, supports)), max(map(len, supports))],
        "observed_classes": classes,
    }


def event_counts(context: Context, size: int) -> dict[str, int]:
    return {
        "determined_by_three": context.row_sizes[size],
        "all_twelve_rows": context.row_sizes[12],
        "four_place_parity": context.unmarked[PARITY_CODE],
        "k_at_least_one": context.choice_count - context.k[0],
        **{f"k_{index}": context.k[index] for index in range(4)},
    }


def describe_events(contexts: list[Context], size: int) -> dict:
    by_event = defaultdict(list)
    possible = Counter()
    for context in contexts:
        for label, count in event_counts(context, size).items():
            by_event[label].append((Fraction(count, context.choice_count), context))
            possible[label] += count > 0
    return {
        label: {
            "contexts_where_possible": possible[label],
            "contexts_where_impossible": len(contexts) - possible[label],
            "conditional_probability_range": extrema(points),
        }
        for label, points in by_event.items()
    }


@cache
def multiplicities(fresh: tuple[int, ...]) -> tuple[int, ...]:
    counts = Counter(normalize(word, 7) for word in row_words(fresh))
    # Three-coordinate recodings induce every permutation of the four antipodal pairs.
    return tuple(sorted(counts[index] for index in range(4)))


def contrast(contexts: list[Context], counts: Callable[[Context], int],
             matching: Callable[[Context], tuple], availability: bool) -> tuple | None:
    groups = defaultdict(dict)
    for context in contexts:
        count = counts(context)
        value = bool(count) if availability else Fraction(count, context.choice_count)
        groups[matching(context)].setdefault(value, {}).setdefault(context.cut, context)
    for group in groups.values():
        for left, right in combinations(sorted(group), 2):
            for cut, a in group[left].items():
                for other, b in group[right].items():
                    if cut != other:
                        return a, b
    return None


def witness_path(context: Context, previous) -> dict:
    root = tuple(column for column in context.columns if column not in context.fresh)
    for order in permutations(context.fresh):
        current = root
        probabilities = []
        for word in order:
            literal = previous.literal_extensions(current, FULL)
            if word not in literal:
                break
            probabilities.append(len(literal))
            current = tuple(sorted((*current, word)))
        if current == context.columns:
            probability = Fraction(1)
            for branch_count in probabilities:
                probability /= branch_count
            return {
                "successive_new_words": column_words(order),
                "literal_branch_counts": probabilities,
                "literal_path_probability_given_cut_class": str(probability),
            }
    raise AssertionError("The witness has no replayable path from its cut class")


def full_context(context: Context, size: int, previous, descriptions: tuple[Observation, ...]) -> dict:
    literal = previous.literal_extensions(context.columns, FULL)
    normalized = tuple(sorted({normalize(word, FULL) for word in literal}))
    assert len(normalized) == context.choice_count and len(literal) == 2 * context.choice_count
    xor = normalize(context.fresh[0] ^ context.fresh[1] ^ context.fresh[2], FULL)
    report = {
        **context.ref(),
        "all_current_words": column_words(context.columns),
        "fresh_assignment_multiplicities_by_complement_pair": multiplicities(context.fresh),
        "probability_given_cut_class": str(context.weight),
        "reachable_path": witness_path(context, previous),
        "literal_option_words": column_words(literal),
        "normalized_option_words": column_words(normalized),
        "literal_option_count": len(literal),
        "normalized_option_count": context.choice_count,
        "normalized_counts_by_k": dict(context.k),
        "normalized_counts_by_row_count": dict(context.row_sizes),
        "normalized_event_counts": event_counts(context, size),
    }
    if size == 6:
        report["normalized_xor_word"] = column_words((xor,))[0]
        report["xor_word_already_used"] = xor in context.columns
    for channel in ("marked", "unmarked"):
        report[f"{channel}_transition_counts"] = [
            {
                "canonical_support_code": code,
                "allowed_words": descriptions[code].words,
                "normalized_option_count": count,
                "literal_option_count": 2 * count,
            }
            for code, count in sorted(getattr(context, channel).items())
        ]
    return report


def select_witness(contexts: list[Context], size: int, previous,
                   descriptions: tuple[Observation, ...]) -> dict | None:
    event_order = (
        ("determined_by_three", "all_twelve_rows", "k_at_least_one", "k_0", "k_1", "k_2", "k_3")
        if size == 6 else
        ("four_place_parity", "all_twelve_rows", "determined_by_three",
         "k_at_least_one", "k_0", "k_1", "k_2", "k_3")
    )
    match_levels = (
        ("same_fresh_words", lambda context: context.fresh),
        ("same_projection_with_multiplicity", lambda context: multiplicities(context.fresh)),
        ("same_projected_class", lambda context: (size,)),
    )
    events = [(label, lambda context, event=label: event_counts(context, size)[event])
              for label in event_order]
    events.extend(
        (f"anonymous_four_support_{code}", lambda context, key=code: context.unmarked[key])
        for code in sorted({code for context in contexts for code in context.unmarked})
    )
    for availability in (True, False):
        for event, event_function in events:
            for match_label, match_function in match_levels:
                pair = contrast(contexts, event_function, match_function, availability)
                if pair is not None:
                    return {
                        "event": event,
                        "match": match_label,
                        "availability_versus_impossibility": availability,
                        "conditional_probabilities": [
                            str(Fraction(event_function(context), context.choice_count))
                            for context in pair
                        ],
                        "contexts": [
                            full_context(context, size, previous, descriptions) for context in pair
                        ],
                    }
    return None


def pooled(laws: dict[str, Counter]) -> dict:
    equal_prior = (laws["fan6"] + laws["nonfan6"])
    mass = equal_prior["mass"]
    assert mass

    def conditional(law: Counter) -> dict:
        assert sum(law[f"k_{k}"] for k in range(4)) == law["mass"]
        return {
            "observed_type_probability": str(law["mass"]),
            "k_distribution": {k: str(law[f"k_{k}"] / law["mass"]) for k in range(4)},
            "k_at_least_one": str(law["k_at_least_one"] / law["mass"]),
            "determined_by_three": str(law["determined_by_three"] / law["mass"]),
            "four_place_parity": str(law["four_place_parity"] / law["mass"]),
        }

    mixture = conditional(equal_prior)
    mixture["observed_type_probability"] = str(mass / 2)
    return {
        "equal_prior_mixture": mixture,
        "by_start": {start: conditional(law) for start, law in laws.items()},
    }


def controls(lookups: tuple[tuple[int, ...], ...], descriptions: tuple[Observation, ...]) -> dict:
    for marked, lookup in zip((True, False), lookups):
        mappings = recoding_maps(4, marked)
        for code, canonical in enumerate(lookup):
            images = {recoded_support(code, mapping) for mapping in mappings}
            assert canonical == min(images)
            desc = descriptions[code]
            assert all(len(descriptions[image].words) == len(desc.words) for image in images)
            if marked:
                assert all(descriptions[image].k == desc.k for image in images)
                assert all(descriptions[image].triple_sizes[3] == desc.triple_sizes[3] for image in images)
    assert len(set(recoding_maps(3, False))) == 24
    assert all(lookup[PARITY_CODE] == PARITY_CODE for lookup in lookups)
    parity = descriptions[PARITY_CODE]
    assert len(parity.words) == 8 and parity.triple_sizes == (8,) * 4
    fresh = (0, 3, 5)
    for added in (9, 17, 33):
        state_set = set(row_words((*fresh, added)))
        state_set |= {word ^ 15 for word in state_set}
        code = four_support(fresh, added)
        assert state_set == set(descriptions[code].words)
        opposite = four_support(fresh, added ^ FULL)
        assert all(lookup[code] == lookup[opposite] for lookup in lookups)
    return {
        "complement_closed_supports_checked": 256,
        "marked_class_count_over_all_supports": len(set(lookups[0])),
        "unmarked_class_count_over_all_supports": len(set(lookups[1])),
        "synthetic_literal_flip_twins_agree": True,
    }


def run(previous, lookups, descriptions, control_result) -> dict:
    started = time.perf_counter()
    recorded = json.loads(verified_read(RESULT_SOURCE, RESULT_DIGEST))
    erase = json.loads(verified_read(previous.CUT_SOURCE, previous.CUT_DIGEST))
    cut, = (layer for layer in erase["eight_independent"]["layers"] if layer["width"] == 8)
    all_contexts = {6: [], 8: []}
    laws = {size: {start: Counter() for start in STARTS} for size in all_contexts}
    cut_summaries = []
    assert len(recorded["per_cut_class"]) == len(cut["class_records"]) == 13
    for previous_cut, source in zip(recorded["per_cut_class"], cut["class_records"]):
        index = previous_cut["cut_class"]
        rows = tuple(source["rows"])
        assert list(rows) == previous_cut["cut_rows"]
        masses = {start: Fraction(source[f"{start}_probability"]) for start in STARTS}
        assert all(str(masses[start]) == previous_cut["cut_probabilities"][start] for start in STARTS)
        original, full = previous.cut_columns(rows, 8)
        assert full == FULL
        endpoints = replay_prefix(previous, original, previous_cut["stages"])
        type_masses = Counter()
        for current, weight in endpoints.items():
            size, context = classify_context(previous, index, original, current, weight, lookups, descriptions)
            all_contexts[size].append(context)
            type_masses[size] += weight
            events = event_counts(context, size)
            for start, mass in masses.items():
                context_mass = weight * mass
                accumulator = laws[size][start]
                accumulator["mass"] += context_mass
                for label, count in events.items():
                    accumulator[label] += context_mass * Fraction(count, context.choice_count)
        assert all(str(type_masses[size]) == previous_cut["projection_probabilities"][str(size)] for size in (6, 8))
        cut_summaries.append({
            "cut_class": index, "cut_rows": rows, "cut_column_words": column_words(original),
            "cut_probabilities": previous_cut["cut_probabilities"],
            "width_eleven_endpoints": len(endpoints),
            "width_eleven_probability_sum": str(sum(endpoints.values())),
            "triple_type_probabilities": {size: str(type_masses[size]) for size in (6, 8)},
        })
    assert sum(map(len, all_contexts.values())) == 22475
    for start in STARTS:
        assert sum(laws[size][start]["mass"] for size in (6, 8)) == 1
        for size in (6, 8):
            assert str(laws[size][start]["mass"]) == recorded["by_start"][start]["projection_probabilities"][str(size)]
    by_type = {}
    for size, contexts in all_contexts.items():
        by_type[size] = {
            "context_count": len(contexts),
            "marked": describe_channel(contexts, "marked", descriptions),
            "unmarked": describe_channel(contexts, "unmarked", descriptions),
            "events": describe_events(contexts, size),
            "pooled": pooled(laws[size]),
            "witness": select_witness(contexts, size, previous, descriptions),
        }
    recoded_cases = [
        recoded_context_control(previous, contexts[0], size, lookups, descriptions)
        for size, contexts in all_contexts.items()
    ]
    return {
        "fresh_three_results_sha256": RESULT_DIGEST,
        "fresh_three_transition_sha256": RULE_DIGEST,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "controls": {**control_result, "recoded_full_contexts": recoded_cases},
        "cut_classes": cut_summaries,
        "width_eleven_context_count": sum(map(len, all_contexts.values())),
        "width_eleven_literal_branch_histogram": dict(Counter(
            2 * context.choice_count for contexts in all_contexts.values() for context in contexts
        )),
        "width_eleven_total_literal_extensions": sum(
            2 * context.choice_count for contexts in all_contexts.values() for context in contexts
        ),
        "all_width_eleven_contexts_have_zero_cost_extension": True,
        "all_flip_twins_equal_weight": True,
        "all_four_pair_shadows_free": True,
        "stalled_probability": "0",
        "six_row_xor_criterion_holds_in_all_contexts": True,
        "by_triple_support_size": by_type,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="Run only finite synthetic controls")
    parser.add_argument("--output", type=Path, help="Write JSON to this path")
    args = parser.parse_args()
    lookups = canonical_lookup(True), canonical_lookup(False)
    descriptions = tuple(describe_support(code) for code in range(256))
    control_result = controls(lookups, descriptions)
    result = control_result if args.smoke else run(previous_rule(), lookups, descriptions, control_result)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
