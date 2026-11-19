"""Check the necessary tests for a shortest extra six-bit equation.

Local observations consist of four consecutive degree-four supports, with
two external slots each. A possible sixth bit outside the square stands
for a seed bit. Compatibility is exact for seed-free pairs in the stated
unicyclic source class. All pairs involving a seed bit are left available.
"""

from collections import Counter
from dataclasses import dataclass
from itertools import combinations, permutations, product
import json


SITES = (0, 1, 2, 3)
OPPOSITE_SITES = ((0, 2), (1, 3))
OUTSIDE_SEED_BIT = 12
LABELS = ("01", "12", "23", "30", "0a", "0b", "1a", "1b",
          "2a", "2b", "3a", "3b", "outside_seed")


def ports(site):
    return (4 + 2 * site, 5 + 2 * site)


def bitset(names):
    return sum(1 << bit for bit in names)


def labels(word):
    return tuple(name for bit, name in enumerate(LABELS) if word >> bit & 1)


ENDPOINTS = tuple(
    (bit, (bit + 1) % 4) if bit < 4 else ((bit - 4) // 2,)
    for bit in range(12)
)
STAR = tuple(bitset(bit for bit, holders in enumerate(ENDPOINTS) if i in holders) for i in SITES)
TRANSLATION = [((), 0)]
for site in SITES:
    TRANSLATION.extend(((*sites, site), mask ^ STAR[site]) for sites, mask in tuple(TRANSLATION))


def circle_neighbors(a, b):
    return (a - b) % 4 != 2


CORE_CLOSE = frozenset(
    (a, b) for a, b in combinations(range(12), 2)
    if any(circle_neighbors(i, j) for i in ENDPOINTS[a] for j in ENDPOINTS[b])
)


@dataclass(frozen=True)
class Outside:
    cycle_seed_bits: tuple[int, ...]
    same_nonfour_holder: frozenset[tuple[int, int]]

    def violation(self, word):
        seed = (*self.cycle_seed_bits, OUTSIDE_SEED_BIT)
        if (word & bitset(seed)).bit_count() > 1:
            return {"kind": "shorten_by_seed"}
        seed_free = (bit for bit in range(12) if word >> bit & 1 and bit not in seed)
        for a, b in combinations(seed_free, 2):
            if (a, b) not in CORE_CLOSE and (a, b) not in self.same_nonfour_holder:
                return {"kind": "pair_exceeds_six", "bits": (LABELS[a], LABELS[b])}
        return None

    def describe(self):
        return {
            "cycle_to_seed_slots": tuple(LABELS[i] for i in self.cycle_seed_bits),
            "pairs_with_same_nonfour_holder": tuple((LABELS[a], LABELS[b])
                                                   for a, b in sorted(self.same_nonfour_holder)),
        }


def partial_matchings(first, second):
    for count in range(min(len(first), len(second)) + 1):
        for left in combinations(first, count):
            for right in permutations(second, count):
                yield frozenset(zip(left, right, strict=True))


def models():
    seed_placements = [(), *((bit,) for bit in range(4, 12))]
    seed_placements.extend(pair for a, b in OPPOSITE_SITES for pair in product(ports(a), ports(b)))
    for seed in seed_placements:
        available = tuple(tuple(bit for bit in ports(site) if bit not in seed) for site in SITES)
        groups = [tuple(partial_matchings(available[a], available[b])) for a, b in OPPOSITE_SITES]
        for first, second in product(*groups):
            yield Outside(seed, first | second)


def local_window(word):
    return tuple((sites, word ^ mask) for sites, mask in TRANSLATION)


def first_shortener(window):
    return next(((sites, word) for sites, word in window if word.bit_count() < 6), None)


def tied_failures(window, outside):
    failures = []
    for sites, word in window:
        if word.bit_count() == 6 and (violation := outside.violation(word)) is not None:
            failures.append({"xor_sites": sites, "word": labels(word), **violation})
    return failures


def controls():
    shared = frozenset({(4, 8), (6, 10)})
    source = Outside((), shared)
    with_seed_at_t = Outside((5,), shared)

    # The named predecessor's six-bit false positive. In order around the
    # cycle the sites are t, p, w, q. Slot 0b joins t to the seed.
    old = bitset((0, 2, 4, 6, 8, 10))
    assert with_seed_at_t.violation(old) is None
    xor_sites, shorter = first_shortener(local_window(old))
    assert xor_sites == (1, 2) and shorter.bit_count() == 4

    star_sum = STAR[1] ^ STAR[2]
    assert star_sum.bit_count() == 6 and with_seed_at_t.violation(star_sum) is None
    assert any(word == 0 for _, word in local_window(star_sum))

    tied = bitset((0, 4, 6, 8, 10, OUTSIDE_SEED_BIT))
    tied_window = local_window(tied)
    assert first_shortener(tied_window) is None
    assert source.violation(tied) is None and with_seed_at_t.violation(tied) is None
    pair_fail = next(failure for failure in tied_failures(tied_window, source)
                     if failure["xor_sites"] == (0,))
    seed_fail = next(failure for failure in tied_failures(tied_window, with_seed_at_t)
                     if failure["xor_sites"] == (0, 1, 2, 3))
    assert pair_fail["bits"] == ("0b", "2a") and seed_fail["kind"] == "shorten_by_seed"

    # A deliberately non-simple comparator permits every opposite matching
    # partner simultaneously and must pass the final test on the same word.
    pair_relaxation = Outside((), frozenset(pair for a, b in OPPOSITE_SITES
                                            for pair in product(ports(a), ports(b))))
    assert not tied_failures(tied_window, pair_relaxation)
    return {
        "predecessor_H_six_bit_clique": {
            "outside": with_seed_at_t.describe(), "word": labels(old), "initial_pair_test": True,
            "shortening_xor_sites": xor_sites, "shortened_word": labels(shorter),
        },
        "actual_adjacent_star_sum": {
            "word": labels(star_sum), "initial_pair_test": True,
            "actual_source_equation": True, "minimum_coset_weight_under_local_stars": 0,
        },
        "locally_minimal_six_bit_test": {
            "outside": source.describe(), "word": labels(tied), "initial_pair_test": True,
            "all_four_star_translations_have_6_or_more_bits": True,
            "exclusion_via_opposite_slots": pair_fail, "exclusion_with_cycle_seed_slot_0b": seed_fail,
        },
        "deliberately_non_simple_outside_relation": {
            "outside": pair_relaxation.describe(), "word": labels(tied),
            "passes_even_after_tied_translations": True,
        },
    }


def run():
    universe = Counter()
    locally_minimal = {}
    minimum_weights_by_local_slot_count = {5: Counter(), 6: Counter()}
    for marks in combinations(range(len(LABELS)), 6):
        word = bitset(marks)
        local_count = 6 - (OUTSIDE_SEED_BIT in marks)
        universe[local_count] += 1
        window = local_window(word)
        minimum = min(translation.bit_count() for _, translation in window)
        minimum_weights_by_local_slot_count[local_count][minimum] += 1
        if minimum != 6:
            continue
        assert local_count == 5 and sum(port < 4 for port in marks) == 1
        assert all((word & bitset(ports(site))).bit_count() == 1 for site in SITES)
        locally_minimal[word] = window

    model_list = tuple(models())
    assert len(model_list) == len(set(model_list))
    by_seed_count = {0: Counter(), 1: Counter(), 2: Counter()}
    fields = ("outside_models", "six_subsets", "four_star_minimal_tests", "initial_seed_failure",
              "initial_pair_failure", "initial_tests_passed", "failure_in_tied_seed_test",
              "failure_in_tied_pair_test", "final_survivors")
    for outside in model_list:
        counts = by_seed_count[len(outside.cycle_seed_bits)]
        counts["outside_models"] += 1
        counts["six_subsets"] += sum(universe.values())
        counts["four_star_minimal_tests"] += len(locally_minimal)
        for word, window in locally_minimal.items():
            violation = outside.violation(word)
            if violation is not None:
                tag = "initial_seed_failure" if violation["kind"] == "shorten_by_seed" else "initial_pair_failure"
                counts[tag] += 1
                continue
            counts["initial_tests_passed"] += 1
            reasons = {failure["kind"] for failure in tied_failures(window, outside)}
            counts["failure_in_tied_seed_test"] += "shorten_by_seed" in reasons
            counts["failure_in_tied_pair_test"] += "pair_exceeds_six" in reasons
            counts["final_survivors"] += not reasons
    assert not any(stats["final_survivors"] for stats in by_seed_count.values())
    assert sum(stats["initial_tests_passed"] for stats in by_seed_count.values()) > 0
    return {
        "local_names": LABELS,
        "four_stars": tuple(labels(mask) for mask in STAR),
        "translated_by_site_subsets": tuple(sites for sites, _ in TRANSLATION),
        "six_subsets_by_number_of_cycle_supported_bits": dict(sorted(universe.items())),
        "minimum_four_star_coset_weights_by_number_of_cycle_supported_bits": {
            count: dict(sorted(distribution.items()))
            for count, distribution in minimum_weights_by_local_slot_count.items()
        },
        "locally_minimal_words": len(locally_minimal),
        "counts_by_number_of_cycle_to_seed_ports": {
            seed: {field: counts[field] for field in fields} for seed, counts in by_seed_count.items()
        },
        "totals": {field: sum(counts[field] for counts in by_seed_count.values()) for field in fields},
        "seed_and_pair_failure_counts_can_overlap": True,
        "model_scope": (
            "All opposite-slot partial matchings and all bipartitely possible seed-to-cycle slots. "
            "Every seed-involving pair is allowed. Additional constraints from a lawful exterior "
            "history and from distances above six are omitted."
        ),
        "controls": controls(),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
