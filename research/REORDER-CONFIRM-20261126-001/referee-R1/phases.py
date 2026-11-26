"""Independent pair-rule and phase checks for the single listed parity knot.

Run from the repository root with the command recorded in phases.json.
The optional pilot uses twelve spaced listings or all listings if fewer.
Only the comparison at the end reads the original receipt.
"""

import argparse
import json
import math
import resource
import time
from collections import Counter
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path


HERE = Path(__file__).resolve().parent
TICKET = HERE.parent.name
ROOT = HERE.parents[2]
RECEIPT = ROOT / "artifacts" / TICKET / (TICKET + "-E001_schedules") / "results.json"
RULES = tuple(product((1, -1), repeat=3))
FERMION = (1, 1, -1)
HOLES = (-1, 1, 1)
FLAT = (1, 1, 1)


def reader_bits(n):
    return tuple(1 << (n - i - 1) for i in range(n))


def even_words(n):
    return tuple(x for x in range(1 << n) if x.bit_count() % 2 == 0)


def adjacent_reordering(order):
    """Actually move the requested readers to their new places, one at a time."""
    readers = sorted(order)
    swaps = []
    for place, reader in enumerate(order):
        current = readers.index(reader)
        while current > place:
            previous = readers[current - 1]
            swaps.append((previous, reader))
            readers[current - 1], readers[current] = reader, previous
            current -= 1
    return swaps


def swap_counts(words, n, swaps):
    bits = reader_bits(n)
    kinds = []
    for x in words:
        counts = [0, 0, 0]
        for i, j in swaps:
            count = int(bool(x & bits[i])) + int(bool(x & bits[j]))
            counts[count] += 1
        kinds.append(counts)
    return kinds


def settings(words):
    position = {x: j for j, x in enumerate(words)}
    return {
        t: [(position[x ^ t], 12 * ((x & ~t).bit_count() % 2)) for x in words]
        for t in words
    }


def noncharacter(signs):
    return any(signs[t ^ u] != signs[t] * signs[u] for t in signs for u in signs)


def carrying(angles, read):
    """Angles are integer multiples of pi/12. Extremality is tested exactly."""
    signs = {}
    for t, translated in read.items():
        image0, z0 = translated[0]
        reference = (angles[0] - angles[image0] + z0) % 24
        if reference not in (0, 12):
            return False
        for index, (image, z) in enumerate(translated):
            if (angles[index] - angles[image] + z) % 24 != reference:
                return False
        signs[t] = 1 if reference == 0 else -1
    return noncharacter(signs)


def real_readout(angles, read):
    """Unnormalised correlations of a real sign state."""
    return {
        t: sum(
            1 if (angles[i] - angles[j] + z) % 24 == 0 else -1
            for i, (j, z) in enumerate(row)
        )
        for t, row in read.items()
    }


def rule_angles(counts, rule):
    return [
        12 * (sum(k for k, sign in zip(kinds, rule) if sign == -1) % 2)
        for kinds in counts
    ]


def label(order):
    return "".join(chr(97 + j) for j in order)


def rule_key(rule):
    return "c00={},c01={},c11={}".format(*rule)


def listings(n, pilot):
    orders = list(permutations(range(n)))
    if pilot and len(orders) > 12:
        return [orders[index * (len(orders) - 1) // 11] for index in range(12)]
    return orders


def sweep(n, pilot):
    words = even_words(n)
    read = settings(words)
    bits = reader_bits(n)
    selected = listings(n, pilot)
    carrying_rules = {rule: set() for rule in RULES}
    relative_state_differences = Counter()
    phase_orders = {k: set() for k in range(24)}
    for order in selected:
        swaps = adjacent_reordering(order)
        counts = swap_counts(words, n, swaps)
        fermion = rule_angles(counts, FERMION)
        degrees = Counter(j for pair in swaps for j in pair)
        odds = sum(bits[j] for j in range(n) if degrees[j] % 2)
        for rule in RULES:
            angles = rule_angles(counts, rule)
            if carrying(angles, read):
                carrying_rules[rule].add(order)
            a = int(rule[0] == -1)
            b = int(rule[0] != rule[1])
            g = int(rule[0] != rule[2])
            reduced = []
            for x, actual, occupied in zip(words, angles, fermion):
                flip = b * ((x & odds).bit_count() % 2)
                expected = (12 * (a * len(swaps) + flip) + g * occupied) % 24
                assert actual == expected
                reduced.append((actual - angles[0] - g * occupied) % 24)
            relative_state_differences[rule] += any(reduced)
        occupied_counts = [c[2] for c in counts]
        for k in range(24):
            if carrying([(k * value) % 24 for value in occupied_counts], read):
                phase_orders[k].add(order)

    fermion_set = carrying_rules[FERMION]
    reversal = tuple(reversed(range(n)))
    expected = {reversal[k:] + reversal[:k] for k in range(n)} & set(selected)
    assert fermion_set == expected
    for rule in RULES:
        assert carrying_rules[rule] == (fermion_set if rule[0] != rule[2] else set())
    assert phase_orders[12] == fermion_set
    assert all(not orders for k, orders in phase_orders.items() if k != 12)
    return {
        "listings": len(selected),
        "nonidentity_listings": sum(order != tuple(range(n)) for order in selected),
        "fermion_carrying_listings": sorted(map(label, fermion_set)),
        "rules": {rule_key(rule): len(carrying_rules[rule]) for rule in RULES},
        "relative_state_differs_from_its_fermion_or_flat_representative": {
            rule_key(rule): relative_state_differences[rule] for rule in RULES
        },
        "phase_carrying_counts_by_k": {str(k): len(v) for k, v in phase_orders.items()},
        "rule_cases": 8 * len(selected),
        "rule_carrying_cases": sum(map(len, carrying_rules.values())),
        "phase_cases": 24 * len(selected),
        "phase_carrying_cases": sum(map(len, phase_orders.values())),
    }


def difference_example():
    words = even_words(3)
    read = settings(words)
    counts = swap_counts(words, 3, adjacent_reordering((1, 0, 2)))
    output = {"listing": "bac", "words": [format(x, "03b") for x in words]}
    for name, rule in (("both_hold_zero", HOLES), ("both_hold_one", FERMION)):
        angles = rule_angles(counts, rule)
        values = real_readout(angles, read)
        output[name] = {
            "amplitudes": [1 if a == 0 else -1 for a in angles],
            "correlations_ZZZ_ZXX_XZX_XXZ": [values[t] // 4 for t in words],
        }
    assert output["both_hold_zero"]["correlations_ZZZ_ZXX_XZX_XXZ"] == [1, -1, -1, -1]
    assert output["both_hold_one"]["correlations_ZZZ_ZXX_XZX_XXZ"] == [1, 1, 1, -1]
    marginal = {}
    for name, rule in (("mixed_holdings", (1, -1, 1)), ("flat_rule", FLAT)):
        angles = rule_angles(counts, rule)
        ac = 0b101
        values = [1 if (angles[i] - angles[j]) % 24 == 0 else -1 for i, (j, _) in enumerate(read[ac])]
        marginal[name] = sum(values) // 4
    assert marginal == {"mixed_holdings": -1, "flat_rule": 1}
    output["two_reader_XaXc_marginal_with_b_ignored"] = marginal
    return output


def reversal_score():
    words = even_words(3)
    bits = reader_bits(3)
    read = settings(words)
    counts = [row[2] for row in swap_counts(words, 3, adjacent_reordering((2, 1, 0)))]
    # Pairing a word with its flipped word cancels the sine. The other two
    # coefficients of the numerator multiply 1 and cos(theta) respectively.
    coefficients = {}
    for t, translated in read.items():
        coeff = [0, 0]
        sine = 0
        for i, (j, z) in enumerate(translated):
            exponent = counts[i] - counts[j]
            sign = -1 if z else 1
            coeff[abs(exponent)] += sign
            sine += sign * exponent
        assert sine == 0
        coefficients[t] = tuple(coeff)
    assert coefficients == {0: (4, 0), 3: (-2, 2), 5: (-2, 2), 6: (-2, 2)}
    # Relabel either outcome of either setting at each of the three readers.
    possible = set()
    for signs in product((-1, 1), repeat=6):
        coeff = [0, 0]
        for t in words:
            factor = 1 if t == 0 else -1
            for i, bit in enumerate(bits):
                factor *= signs[2 * i + int(bool(t & bit))]
            for j in range(2):
                coeff[j] += factor * coefficients[t][j]
        possible.add(tuple(coeff))

    def best(cosine):
        return max((a + b * cosine) / 4 for a, b in possible)

    scores = {}
    for k in range(24):
        cosine = math.cos(k * math.pi / 12)
        scores[str(k)] = round(best(cosine), 12)
    threshold = {}
    for cosine in (Fraction(1, 4), Fraction(1, 3), Fraction(1, 2)):
        value = best(cosine)
        assert value == 1 + 3 * (1 - cosine) / 2
        threshold[str(cosine)] = str(value)
    return {
        "correlation_numerators_over_four_constant_and_cosine": {
            format(t, "03b"): values for t, values in coefficients.items()
        },
        "outcome_label_assignments": 64,
        "distinct_score_numerators_constant_and_cosine": sorted(possible),
        "by_k": scores,
        "grid_k_above_two": [int(k) for k, value in scores.items() if value > 2],
        "off_grid_exact_score_by_cosine": threshold,
        "all_angles": "The three mixed correlations are (cos(theta)-1)/2, all nonpositive. The displayed Mermin signs attain the sum of the four absolute values. This gives 1+3(1-cos(theta))/2 at every angle, with equality to 2 at cos(theta)=1/3.",
    }


def local_adjustment(n):
    words = even_words(n)
    bits = reader_bits(n)
    read = settings(words)
    # A local diagonal adjustment reproducing real signs must have local
    # factors that are all real units or all imaginary units. Every pair of
    # occupied readers is an allowed word, and each of its factors is +/-1.
    local_states = set()
    for common in (0, 1):
        for z in product((0, 2), repeat=n):
            local = []
            for w in words:
                exponent = sum(common + d for bit, d in zip(bits, z) if w & bit) % 4
                assert exponent in (0, 2)
                local.append(exponent // 2)
            local_states.add(tuple(local))
    squared = [math.comb(x.bit_count(), 2) % 2 for x in words]
    assert all(2 * r % 4 == x.bit_count() % 4 for x, r in zip(words, squared))
    category = Counter()
    compared = 0
    for signs_tail in product((0, 1), repeat=len(words) - 1):
        q = (0,) + signs_tail
        angles = [12 * bit for bit in q]
        conjugated = [12 * (a ^ b) for a, b in zip(q, squared)]
        cx = real_readout(angles, read)
        cx_after = real_readout(conjugated, read)
        cy = {}
        for t, pairs in read.items():
            value = 0
            for index, (j, _) in enumerate(pairs):
                x = words[index]
                # Each Y contributes i*(-1)^x, each remaining Z contributes
                # (-1)^x. This reads the complex setting directly.
                exponent = (
                    t.bit_count() + 2 * (x & t).bit_count()
                    + 2 * (x & ~t).bit_count() + 2 * (q[index] + q[j])
                ) % 4
                assert exponent in (0, 2)
                value += 1 if exponent == 0 else -1
            cy[t] = value
            assert value == cx_after[t]
            compared += 1

        def sharp(values):
            return all(abs(v) == len(words) for v in values.values()) and noncharacter(
                {t: v // len(words) for t, v in values.items()}
            )

        category[(sharp(cx), sharp(cy))] += 1
        assert (q in local_states) == (sharp(cx) or sharp(cy))
    return {
        "real_sign_functions_with_blank_positive": 2 ** (len(words) - 1),
        "functions_removable_by_local_diagonal_units": len(local_states),
        "carrying_only_real": category[(True, False)],
        "carrying_only_complex": category[(False, True)],
        "carrying_neither": category[(False, False)],
        "carrying_both": category[(True, True)],
        "complex_correlations_equal_to_reversal_adjusted_real_correlations": compared,
    }


def normalization_and_mixed_readers():
    words = even_words(3)
    read = settings(words)
    q = {x: 1 ^ (math.comb(x.bit_count(), 2) % 2) for x in words}
    assert carrying([12 * q[x] for x in words], read)
    for x, t in product(words, repeat=2):
        dot = (x & t).bit_count() % 2
        assert q[x ^ t] ^ q[x] ^ q[t] != dot
        assert q[x ^ t] ^ q[x] ^ q[t] ^ q[0] == dot
    # With a single Y (at a), every word's term for Y_a X_b Z_c is
    # purely imaginary. Pairing a word with its flip gives opposite terms.
    imag = sum((-1) ** (int(bool(x & 0b100)) + int(bool(x & 0b001))) for x in words)
    assert imag == 0
    return {
        "real_state_with_negative_blank": [(-1) ** q[x] for x in words],
        "carrying": True,
        "uncorrected_polar_mismatches_over_16_pairs": 16,
        "polar_with_constant_included_mismatches": 0,
        "one_complex_reader_on_unsigned_ternary_YaXbZc": 0,
        "general_reason": "For an arbitrary real Boolean sign q, sharpness at every even t gives q(x+t)+q(x)+q(t)+q(0)=x dot t modulo two. Add q(0) or stipulate a positive blank. A mix of X and Y reader types has an even two-reader flip containing one Y. Its expectation vanishes in every real state.",
    }


def minor_coefficients(matrix, rows, columns):
    """Exact determinant at a primitive eighth root, represented in 1,z,z²,z³."""
    coeff = [0] * 4
    for p in permutations(range(len(columns))):
        entries = [matrix[row][columns[j]] for row, j in zip(rows, p)]
        if any(value is None for value in entries):
            continue
        inv = sum(i > j for i, j in combinations(p, 2))
        exponent = sum(entries) % 8
        coeff[exponent % 4] += (-1) ** (inv + exponent // 4)
    return coeff


def partition_rank(amplitude, left, right):
    # An exponent stands for a power of exp(i*pi/4). None is zero amplitude.
    matrix = [[None] * 4 for _ in range(4)]
    bits = reader_bits(4)
    for x, value in amplitude.items():
        row = 2 * int(bool(x & bits[left[0]])) + int(bool(x & bits[left[1]]))
        col = 2 * int(bool(x & bits[right[0]])) + int(bool(x & bits[right[1]]))
        matrix[row][col] = value
    for k in range(4, 0, -1):
        groups = list(combinations(range(4), k))
        for rows, cols in product(groups, repeat=2):
            minor = minor_coefficients(matrix, rows, cols)
            if any(minor):
                return {"rank": k, "rows": rows, "columns": cols, "minor": minor}
    return {"rank": 0}


def general_phase_witnesses():
    words = even_words(4)
    bits = reader_bits(4)
    flat = dict.fromkeys(words, 0)
    one_swap = {x: 4 * int(bool(x & bits[0]) and bool(x & bits[1])) for x in words}
    reversed_phase = {x: math.comb(x.bit_count(), 2) % 8 for x in words}
    single = [partition_rank(amplitudes, (0, 2), (1, 3)) for amplitudes in (flat, one_swap)]
    reversal = [partition_rank(amplitudes, (0, 1), (2, 3)) for amplitudes in (flat, reversed_phase)]
    assert [r["rank"] for r in single] == [2, 4]
    assert [r["rank"] for r in reversal] == [2, 3]
    return {
        "one_swapped_pair_at_s_minus_one": {
            "listing": "bacd", "sign": "(-1)^(x_a*x_b)", "partition": "ac|bd",
            "flat_then_swapped_ranks_and_nonzero_minors": single,
        },
        "reversal_at_s_exp_i_pi_over_four": {
            "listing": "dcba", "partition": "ab|cd",
            "flat_then_reversed_ranks_and_nonzero_minors": reversal,
        },
        "minor_basis": ["1", "exp(i*pi/4)", "i", "exp(3*i*pi/4)"],
        "reversal_for_general_s": "For n=3 the only weights are 0 and 2, so diag(1,sqrt(s)) on each reader gives the reversal amplitude. At n>=4 the determinant on 00 and 11 in both parts is s^6-s^2, and a separate odd-odd block is nonzero. A rank of at least three when s^4!=1 excludes local-unitary equivalence to the unsigned state, of rank two. When s^4=1 the same product works for all even weights since C(2m,2)-m=2m(m-1) is a multiple of four.",
    }


def compare(out):
    with RECEIPT.open() as stream:
        receipt = json.load(stream)["P6"]
    for n in range(3, 7):
        key = f"n{n}"
        actual = out["sweep"][key]
        assert actual["rules"] == receipt[key]["rules"]
        assert len(actual["fermion_carrying_listings"]) == receipt[key]["fermion_rule_carrying"]
        reported = receipt["phase_family"][key]["theta_k_pi_over_12_with_carrying_listings"]
        assert {k: v for k, v in actual["phase_carrying_counts_by_k"].items() if v} == reported
    assert out["reversal_score"]["by_k"] == receipt["reversal_best_mermin_n3"]["by_k"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.pilot and args.output:
        parser.error("the pilot reports to standard output")
    _, hard_limit = resource.getrlimit(resource.RLIMIT_AS)
    cap = 2 * 1024**3
    if hard_limit != resource.RLIM_INFINITY:
        cap = min(cap, hard_limit)
    resource.setrlimit(resource.RLIMIT_AS, (cap, hard_limit))
    sizes = {}
    timing = {}
    for n in range(3, 7):
        start = time.perf_counter()
        sizes[f"n{n}"] = sweep(n, args.pilot)
        timing[f"n{n}"] = round(time.perf_counter() - start, 6)
    start = time.perf_counter()
    out = {
        "sweep": sizes,
        "unequal_fixed_labels": difference_example(),
        "reversal_score": reversal_score(),
        "local_adjustment": {f"n{n}": local_adjustment(n) for n in (3, 4)},
        "global_sign_and_mixed_reader_checks": normalization_and_mixed_readers(),
        "local_unitary_obstructions": general_phase_witnesses(),
        "continuous_phase": "For an even flip t, the vacuum contribution to the expectation has phase conjugate(a(t))*a(0). Sharpness of a Hermitian flip requires all summands to have the same real unit sign. For any inverted pair ij, t with just i and j occupied gives a(t)=s. Thus sharpness requires s=+1 or -1. Without inversions and at s=+1 the state is flat and a two-reader flip has expectation zero for n>=3. Full reversal at s=-1 attains the contradiction.",
        "local_adjustment_identity": "On every even old word of weight k, (-1)^C(k,2)=i^k. Multiplication by this specific sign exchanges real and complex flip correlations for any amplitude on the even words. For a general normalised real sign g, the weights of two occupied readers require local phase factors z_i z_j in {+1,-1}. For n>=3 all z_i are real signs or all are imaginary units. Hence a product exists exactly when g is a product of real single-reader signs, possibly times the reversal sign. For a crossing-pair sign these are respectively a cut and all pairs except a cut.",
        "rule_equivalence": "A symmetric pair rule is (-1)^(a+b(u+v)+g*u*v), with g=1 iff c00*c11=-1. On a listing its factor is a global sign (-1)^(a*number_of_swaps), a product of reader signs at the odd-degree readers if b=1, and the fermion factor if g=1. The global and reader factors may both occur.",
        "independent_method": "Adjacent moves of named readers; exact integers modulo 24 for interference of root-of-unity phases; all 64 local outcome choices for the reversal score. Only the 24 rounded score comparisons use floating-point cosines. Carrying requires sharpness at every even flip and a noncharacter.",
        "evidence_limit": "One listed parity knot with equal magnitudes, symmetric holding-dependent signs and fixed Z/X readings. The receipt stores counts per rule and only the nonempty angle totals. The identities for continuous angles and the local-unitary counterexamples are separate algebraic checks.",
        "rerun": ".venv/bin/python -B research/REORDER-CONFIRM-20261126-001/referee-R1/phases.py --output research/REORDER-CONFIRM-20261126-001/referee-R1/phases.json",
    }
    timing["score_and_witnesses"] = round(time.perf_counter() - start, 6)
    if args.pilot:
        print(json.dumps({"pilot_listings": {n: d["listings"] for n, d in sizes.items()}, "seconds": timing}))
        return
    compare(out)
    out["receipt_comparison"] = {
        "rule_totals": 32, "fermion_totals": 4, "phase_size_angle_totals": 96,
        "rounded_reversal_scores": 24, "mismatches": 0,
    }
    if args.output:
        args.output.write_text(json.dumps(out, indent=2) + "\n")
    else:
        print(json.dumps(out, indent=2))
    print(json.dumps({"seconds": timing, "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))


if __name__ == "__main__":
    main()
