"""Exact product and reader checks for the four-knot closure under rule R.

Run with --pilot first. It takes prefixes of the same census, settings and
product loops as the full run. Both use one process and integer arithmetic.

For a counting state, let S be the commuting group of signed knot products,
with -I absent. The normalized common-eigenspace projector is proportional
to the sum of S. Orthogonality of the Pauli words under trace therefore
gives moment +1 on S, -1 on -S, and 0 on every other Hermitian Pauli word.
Take Hermitian product settings A0,A1 and B0,B1 with all cross pairs
commuting. Modulo scalar phases, the four labels of Ai Bj sum to zero over
GF(2). If three belong to the labels of S, all four do. In that case,
commutation of A0 B0 with A0 B1 forces B0,B1 to commute, and similarly
A0,A1 commute. The four pair products then multiply to I. Their four
eigenvalue signs have product +1, so a CHSH sum has absolute value 2. With
fewer than three nonzero moments the bound follows from counting the terms.
This includes repeated settings and the identity. It uses the stated
counting projector and product observables with cross-reader compatibility.
"""

import argparse
import json
import resource
from collections import Counter
from itertools import combinations, islice, product
from pathlib import Path
from time import perf_counter


ROOT = Path(__file__).resolve().parents[3]
CENSUS = ROOT / (
    "artifacts/FOUR-READINGS-20261120-001A/"
    "FOUR-READINGS-20261120-001A-E001_signed_rules/census.json"
)
FIXTURE = ((0, 1, 2), (0, 3, 4), (1, 3, 5), (2, 4, 5))
READERS = ((0, 5), (1, 4), (2, 3))
SCORED = {"000": 1, "011": 1, "101": 1, "110": -1}


def mask(indices):
    return sum(1 << i for i in indices)


class HeldValues:
    """Ordered products of involutions, with minus signs from swaps under R."""

    def __init__(self, knots):
        self.knots = tuple(mask(k) for k in knots)
        m = max(self.knots).bit_length()
        self.holders = [frozenset(i for i, k in enumerate(self.knots) if k & 1 << d)
                        for d in range(m)]
        self.anti = [mask(j for j, others in enumerate(self.holders) if hs.isdisjoint(others))
                     for hs in self.holders]

    def swaps(self, left, right, *, reorder_only=False):
        parity = 0
        while left:
            bit = left & -left
            partners = right & self.anti[bit.bit_length() - 1]
            if reorder_only:
                partners &= bit - 1
            parity ^= partners.bit_count() & 1
            left ^= bit
        return parity

    def multiply(self, left, right):
        p, a = left
        q, b = right
        return (p + q + 2 * self.swaps(a, b, reorder_only=True)) % 4, a ^ b

    def ordered_product(self, terms):
        word = (0, 0)
        for term in terms:
            word = self.multiply(word, term)
        return word

    def counting_group(self, signs):
        assert len(signs) == len(self.knots)
        assert all(self.swaps(a, b) == 0 for a, b in combinations(self.knots, 2))
        elements = {0: 0}
        for support, sign in zip(self.knots, signs):
            generator = (0 if sign == 1 else 2, support)
            for old, phase in list(elements.items()):
                p, s = self.multiply((phase, old), generator)
                assert elements.setdefault(s, p) == p
        return elements


def counting_moment(group, operator):
    phase, support = operator
    if support not in group:
        return 0
    difference = (phase - group[support]) % 4
    assert difference in (0, 2)
    return 1 if difference == 0 else -1


def census_pairs(limit):
    data = json.loads(CENSUS.read_bytes())
    checked_types = []
    size_two = []
    readable_size_two = []
    knot_subset_count = 0
    distinct_supports = 0
    for index, entry in islice(enumerate(data), limit):
        knots = [tuple(d for d, hs in enumerate(entry["sharing"]) if k in hs)
                 for k in range(entry["n"])]
        values = HeldValues(knots)
        if any(values.swaps(a, b) for a, b in combinations(values.knots, 2)):
            continue
        checked_types.append(index)
        knot_subset_count += 2 ** len(knots)
        supports = {0}
        for k in values.knots:
            supports |= {s ^ k for s in supports}
        distinct_supports += len(supports)
        for s in sorted(s for s in supports if s.bit_count() == 2):
            d, e = (i for i in range(len(values.holders)) if s & 1 << i)
            size_two.append([index, d, e])
            if not values.holders[d].isdisjoint(values.holders[e]):
                readable_size_two.append([index, d, e])
    return {
        "raw_types_tested": min(limit, len(data)), "commuting_knot_types": checked_types,
        "knot_subsets_including_empty": knot_subset_count, "distinct_supports_summed_over_types": distinct_supports,
        "two_distinction_supports_type_and_pair": size_two,
        "readable_two_distinction_supports_type_and_pair": readable_size_two,
    }


def tensor_word(letters):
    """Action on each three-bit basis word as (destination, exponent of i)."""
    action = []
    for basis in range(8):
        dest, phase = basis, 0
        for j, letter in enumerate(letters):
            bit = 1 << (2 - j)
            value = int(bool(basis & bit))
            if letter in "XY":
                dest ^= bit
            if letter == "Y":
                phase += 1 + 2 * value
            if letter == "Z":
                phase += 2 * value
        action.append((dest, phase % 4))
    return tuple(action)


IDENTITY = tensor_word("III")


def compose(left, right):
    return tuple((left[mid][0], (p + left[mid][1]) % 4) for mid, p in right)


def negative(action):
    return tuple((dest, (phase + 2) % 4) for dest, phase in action)


def state_moment(action):
    """Exact expectation in (|000> + |111>)/sqrt(2)."""
    phases = Counter(p for dest, p in (action[0], action[7]) if dest in (0, 7))
    assert phases[1] == phases[3]
    numerator = phases[0] - phases[2]
    assert numerator % 2 == 0
    return numerator // 2


def fixture(context_limit):
    values = HeldValues(FIXTURE)
    forces = values.ordered_product((0, k) for k in values.knots)
    assert forces == (2, 0)
    group = values.counting_group((1, 1, 1, -1))
    assert len(group) == 8
    operators = [tensor_word(w) for w in ("XII", "IXI", "IIX", "IIY", "IYI", "YII")]
    operators[3] = negative(operators[3])
    for a, b in combinations(range(6), 2):
        commutes = compose(operators[a], operators[b]) == compose(operators[b], operators[a])
        assert commutes == bool(values.holders[a] & values.holders[b])
    projective_actions = set()
    for subset in range(64):
        action = IDENTITY
        for d, operator in enumerate(operators):
            if subset & 1 << d:
                action = compose(action, operator)
        common_phase = action[0][1]
        projective_actions.add(tuple((dest, (p - common_phase) % 4) for dest, p in action))
    assert len(projective_actions) == 64
    correlations, unheld = {}, {}
    probability_counts = Counter()
    for settings in islice(product((0, 1), repeat=3), context_limit):
        chosen = tuple(reader[s] for reader, s in zip(READERS, settings))
        key = "".join(map(str, settings))
        assert all(values.holders[a] & values.holders[b] for a, b in combinations(chosen, 2))
        if not frozenset.intersection(*(values.holders[d] for d in chosen)):
            unheld[key] = list(chosen)
        moments = []
        for subset in range(8):
            ds = [d for j, d in enumerate(chosen) if subset & 1 << j]
            expected = counting_moment(group, values.ordered_product((0, 1 << d) for d in ds))
            action = IDENTITY
            for d in ds:
                action = compose(action, operators[d])
            assert state_moment(action) == expected
            moments.append(expected)
        correlations[key] = moments[7]
        for outcome in range(8):
            # Expand the three commuting outcome projectors. Numerators are over eight.
            numerator = sum((-1) ** ((s & outcome).bit_count() & 1) * mean for s, mean in enumerate(moments))
            probability_counts[numerator] += 1
    scores = Counter()
    for signs in product((1, -1), repeat=6):
        score = 0
        for key, coefficient in SCORED.items():
            term = coefficient
            for reader, setting in zip(READERS, key):
                term *= signs[reader[int(setting)]]
            score += term
        scores[score] += 1
    return {
        "reader_operators": [["XII", "YII"], ["IXI", "IYI"], ["IIX", "-IIY"]],
        "state": "(|000> + |111>)/sqrt(2)", "counting_group_order": len(group),
        "distinct_products_modulo_phase": len(projective_actions), "triple_correlations": correlations,
        "pairwise_coheld_triples_without_one_common_knot": unheld,
        "outcome_counts_by_probability_numerator_over_eight": probability_counts,
        "scored_sum": sum(c * correlations[k] for k, c in SCORED.items()) if len(correlations) == 8 else None,
        "scores_on_64_lists_of_values": scores,
    }


def product_chsh(pair_limit):
    words = ["".join(t) for t in product("IXYZ", repeat=3) if t != ("I", "I", "I")]
    actions = [tensor_word(w) for w in words]
    # Each local Z is XY up to a factor of i. An even number of local Zs
    # makes the unphased product Hermitian. No local Z means that the
    # primitive factors themselves form a read set.
    literal = {i for i, w in enumerate(words) if w.count("Z") % 2 == 0}
    read_sets = {i for i, w in enumerate(words) if "Z" not in w}
    cor = {}
    signs_fixed = {IDENTITY}
    # These are the three older knot operators. The fourth is their product after signing.
    for generator in (tensor_word("XXX"), negative(tensor_word("XYY")), negative(tensor_word("YXY"))):
        signs_fixed |= {compose(generator, old) for old in signs_fixed}
    assert len(signs_fixed) == 8
    assert negative(tensor_word("YYX")) in signs_fixed
    for a, ma in enumerate(actions):
        for b in range(a, len(words)):
            mb = actions[b]
            ab, ba = compose(ma, mb), compose(mb, ma)
            if ab != ba:
                assert ab == negative(ba)
                continue
            mean = state_moment(ab)
            assert mean == int(ab in signs_fixed) - int(negative(ab) in signs_fixed)
            cor[a, b] = cor[b, a] = mean
    counts, absolute_values, disjoint, both_anti = Counter(), Counter(), Counter(), Counter()
    literal_counts, read_set_counts = Counter(), Counter()
    n_alice = 0
    for a, aa in islice(combinations(range(len(words)), 2), pair_limit):
        n_alice += 1
        common = [b for b in range(len(words)) if (a, b) in cor and (aa, b) in cor]
        assert len(common) == 15
        for b, bb in combinations(common, 2):
            e = (cor[a, b], cor[a, bb], cor[aa, b], cor[aa, bb])
            nz = sum(x != 0 for x in e)
            # Relabelling signs and the two settings covers every odd coefficient pattern.
            total = sum(e)
            best = max(abs(total - 2 * x) for x in e)
            counts[nz] += 1
            absolute_values[best] += 1
            four = {a, aa, b, bb}
            if len(four) == 4:
                disjoint[best] += 1
            if four <= literal:
                literal_counts[best] += 1
            if four <= read_sets:
                read_set_counts[best] += 1
            incompatible = (a, aa) not in cor or (b, bb) not in cor
            if (a, aa) not in cor and (b, bb) not in cor:
                both_anti[best] += 1
            assert nz != 3 and (not incompatible or nz <= 2)
            if nz == 4:
                assert e[0] * e[1] * e[2] * e[3] == 1
            assert best <= 2
    # All four settings use only primitive factors readable together within
    # each setting. The two choices of each reader are incompatible.
    fixed = ("XII", "YII", "IXX", "IYX")
    a, aa, b, bb = map(words.index, fixed)
    assert (a, aa) not in cor and (b, bb) not in cor
    fixed_correlations = (cor[a, b], cor[a, bb], cor[aa, b], cor[aa, bb])
    assert fixed_correlations == (1, 0, 0, -1)
    return {
        "nonidentity_words_modulo_sign": len(words), "distinct_A_pairs": n_alice,
        "distinct_B_pairs_per_A_pair": 105, "compatible_setting_quadruples": sum(counts.values()),
        "quadruples_by_number_of_nonzero_moments": counts, "best_absolute_CHSH_frequencies": absolute_values,
        "best_absolute_CHSH_all_four_settings_distinct": disjoint,
        "best_absolute_CHSH_both_readers_locally_incompatible": both_anti,
        "literal_Hermitian_words_without_phase_adjustment": len(literal),
        "best_absolute_CHSH_literal_Hermitian_words": literal_counts,
        "words_whose_primitive_factors_are_a_read_set": len(read_sets),
        "best_absolute_CHSH_products_from_primitive_read_sets": read_set_counts,
        "attaining_settings_A0_A1_B0_B1": fixed, "attaining_moments_00_01_10_11": fixed_correlations,
    }


def two_product_table(values, group, u, v):
    assert values.swaps(u, v) == 0
    terms = (0, u), (0, v), values.multiply((0, u), (0, v))
    eu, ev, euv = (counting_moment(group, term) for term in terms)
    return [1 + a * eu + b * ev + a * b * euv for a, b in product((1, -1), repeat=2)]


def closing_sign(values, knot_masks):
    phase, support = values.ordered_product((0, k) for k in knot_masks)
    assert support == 0 and phase in (0, 2)
    return 1 if phase == 0 else -1


def disjoint_products(setting_limit):
    # Two separate closed components, each with five knots that share one distinction per pair.
    pairs = list(combinations(range(5), 2))
    knots = [[offset + d for d, hs in enumerate(pairs) if k in hs]
             for offset in (0, 10) for k in range(5)]
    values = HeldValues(knots)
    signs = [1] * 10
    signs[4] = closing_sign(values, values.knots[:5])
    signs[9] = closing_sign(values, values.knots[5:])
    group = values.counting_group(signs)
    assert all(len(hs) == 2 for hs in values.holders)
    assert all(a & b == 0 for a, b in product(values.knots[:5], values.knots[5:]))
    assert all(values.swaps(1 << a, 1 << b) == 1 for a, b in product(range(10), range(10, 20)))
    first = ((0, 1), (0, 2))
    second = ((10, 11), (10, 12))
    tables = [two_product_table(values, group, mask(u), mask(v))
              for u, v in islice(product(first, second), setting_limit)]
    assert all(t == [1, 1, 1, 1] for t in tables)
    return {
        "knots": knots, "knot_signs": signs, "reader_product_supports": [first, second],
        "cross_primitive_anticommuting_pairs": 100, "cross_product_commuting_pairs": len(tables),
        "outcome_numerators_over_four_order_pp_pm_mp_mm": tables,
    }


def connected_products():
    # Nine distinctions e_ij. The six knots are the three rows and three columns.
    knots = [list(range(i, i + 3)) for i in (0, 3, 6)] + [list(range(j, 9, 3)) for j in range(3)]
    values = HeldValues(knots)
    signs = [1] * 5 + [closing_sign(values, values.knots)]
    group = values.counting_group(signs)
    first, second = (0, 1), (5, 8)
    assert all(values.holders[a].isdisjoint(values.holders[b]) for a, b in product(first, second))
    assert all(values.swaps(1 << a, 1 << b) == 1 for a, b in product(first, second))
    u, v = mask(first), mask(second)
    assert values.multiply((0, u), (0, v)) == values.multiply((0, values.knots[0]), (0, values.knots[5]))
    table = two_product_table(values, group, u, v)
    assert table == [0, 2, 2, 0]
    return {
        "knots": knots, "knot_signs": signs, "product_supports": [first, second],
        "cross_primitive_anticommuting_pairs": 4, "joint_product_mean": -1,
        "outcome_numerators_over_four_order_pp_pm_mp_mm": table,
    }


def main():
    cap = 2 * 1024 ** 3
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    jobs = [
        ("census_pair_supports", census_pairs, (4 if args.pilot else 173,)),
        ("four_knot_closure", fixture, (1 if args.pilot else 8,)),
        ("product_CHSH", product_chsh, (12 if args.pilot else 1953,)),
        ("disjoint_closed_components", disjoint_products, (1 if args.pilot else 4,)),
        ("connected_six_knots", connected_products, ()),
    ]
    data = {"pilot_prefix": args.pilot, "elapsed_seconds": {}}
    for name, run, arguments in jobs:
        start = perf_counter()
        data[name] = run(*arguments)
        data["elapsed_seconds"][name] = round(perf_counter() - start, 6)
    data["peak_resident_KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
