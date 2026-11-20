"""Outcome-independent marking and exact scores from marked assignments."""

from collections import deque
from fractions import Fraction
from itertools import combinations, product
from math import comb

from exact_counts import boolean_words, mask


BANDS = ("2", "finite_3_or_more", "no_chain")
ORIGINS = ("old_only", "newborn")
CONTEXTS = tuple(product((0, 1), repeat=2))


def step_neighborhoods(supports):
    nbits = 1 + max(map(max, supports))
    adjacency = [0] * nbits
    for support in supports:
        together = mask(support)
        for bit in support:
            adjacency[bit] |= together
    within_two = [union_from_mask(together, adjacency) for together in adjacency]
    return adjacency, within_two


def union_from_mask(bits, rows):
    out = 0
    while bits:
        bit = bits & -bits
        out |= rows[bit.bit_length() - 1]
        bits ^= bit
    return out


def shortest_steps(left, right, adjacency):
    pending = deque((bit, 0) for bit in left)
    seen = mask(left)
    right = mask(right)
    while pending:
        bit, length = pending.popleft()
        if (1 << bit) & right:
            return length
        fresh = adjacency[bit] & ~seen
        seen |= fresh
        while fresh:
            added = fresh & -fresh
            pending.append((added.bit_length() - 1, length + 1))
            fresh ^= added
    return None


def side_marks(support, width):
    for u, v in combinations(support, 2):
        if width == 2:
            yield u, v
        else:
            for selector in support:
                if selector not in (u, v):
                    yield u, v, selector


def arrangements(allowed, width):
    return comb(allowed.bit_count(), width) * (3 if width == 3 else 1)


def choose_placements(supports, certificates, old_nbits, width, fixed=None):
    """Enumerate frozen support-indexed placements by step bands.

    The lexicographically first support is Alice's, and each side's ordered pair starts
    with the lesser distinction. Changing either order preserves geometric eligibility.
    The third mark in a three-mark reader is the selector.
    """
    adjacency, within_two = step_neighborhoods(supports)
    support_ids = sorted((index for index, row in enumerate(certificates) if row["eligible"]),
                         key=lambda index: (supports[index], index))
    old = (1 << old_nbits) - 1
    slots = {(band, origin): {"band": band, "origin": origin, "eligible": 0, "placement": None}
             for band in BANDS for origin in ORIGINS}
    excluded = {"repeated_mark": 0, "cross_step_one": 0}
    total = 0
    for alice, bob in combinations(support_ids, 2):
        right = supports[bob]
        right_bits = mask(right)
        disconnected = shortest_steps(supports[alice], right, adjacency) is None
        all_right = arrangements(right_bits, width)
        for lhs in side_marks(supports[alice], width):
            left_bits = mask(lhs)
            distinct_right = right_bits & ~left_bits
            step_one = union_from_mask(left_bits, adjacency)
            at_least_two = right_bits & ~step_one
            step_two = union_from_mask(left_bits, within_two)
            at_least_three = right_bits & ~step_two
            total += all_right
            excluded["repeated_mark"] += all_right - arrangements(distinct_right, width)
            excluded["cross_step_one"] += arrangements(distinct_right, width) - arrangements(at_least_two, width)
            bands = (("no_chain", right_bits, 0),) if disconnected else (
                ("2", at_least_two, at_least_three), ("finite_3_or_more", at_least_three, 0))
            for band, allowed, omitted in bands:
                count = arrangements(allowed, width) - arrangements(omitted, width)
                all_left_old = left_bits & old == left_bits
                old_count = (arrangements(allowed & old, width) - arrangements(omitted & old, width)
                             if all_left_old else 0)
                for origin, quantity in (("old_only", old_count), ("newborn", count - old_count)):
                    slot = slots[(band, origin)]
                    slot["eligible"] += quantity
                    if not quantity or slot["placement"] is not None:
                        continue
                    for rhs in side_marks(right, width):
                        right_marks = mask(rhs)
                        if right_marks & ~allowed or not right_marks & ~omitted:
                            continue
                        if (origin == "old_only") != ((left_bits | right_marks) & ~old == 0):
                            continue
                        slot["placement"] = describe_placement(alice, bob, lhs, rhs, adjacency)
                        break

    if fixed is not None:
        alice, bob, lhs, rhs = fixed
        assert set(lhs) <= set(supports[alice]) and set(rhs) <= set(supports[bob])
        assert len(set(lhs + rhs)) == 2 * width
        steps = shortest_steps(lhs, rhs, adjacency)
        assert steps is None or steps >= 2
        band = "no_chain" if steps is None else "2" if steps == 2 else "finite_3_or_more"
        assert slots[(band, "old_only")]["eligible"] and alice in support_ids and bob in support_ids
        slots[(band, "old_only")]["placement"] = describe_placement(alice, bob, lhs, rhs, adjacency)

    assert all(bool(slot["eligible"]) == (slot["placement"] is not None) for slot in slots.values())
    assert total == sum(excluded.values()) + sum(slot["eligible"] for slot in slots.values())
    return {"candidate_count": total, "excluded": excluded, "slots": list(slots.values())}


def describe_placement(alice, bob, lhs, rhs, adjacency):
    return {"supports": [alice, bob], "alice": lhs, "bob": rhs,
            "cross_steps": shortest_steps(lhs, rhs, adjacency)}


def ratio(value):
    return None if value is None else [value.numerator, value.denominator]


def total_variation(counts, baseline):
    den, base_den = sum(counts), sum(baseline)
    if not den or not base_den:
        return None
    return Fraction(sum(abs(value * base_den - other * den)
                        for value, other in zip(counts, baseline, strict=True)), 2 * den * base_den)


def product_of_marginals(counts, width):
    columns = [sum(counts[col::width]) for col in range(width)]
    rows = [sum(counts[row * width:(row + 1) * width]) for row in range(width)]
    return [a * b for a, b in product(rows, columns)]


def score(weighted_counts, width):
    words = [tuple(map(int, word)) for word in boolean_words(2 * width)]
    full_pairs = pair_counts(words, weighted_counts, width)
    arms = {"external": {}}
    if width == 3:
        arms["embodied"] = {}
    for arm in arms:
        contexts = []
        for x, y in CONTEXTS:
            if arm == "embodied":
                counts = [count if (word[2], word[5]) == (x, y) else 0
                          for word, count in zip(words, weighted_counts, strict=True)]
            else:
                counts = weighted_counts
            pairs = pair_counts(words, counts, width)
            table = context_counts(pairs, x, y)
            table["mass"] = ratio(Fraction(sum(counts), sum(weighted_counts))) if arm == "embodied" else [1, 4]
            table["all_marks_tv_from_common"] = ratio(total_variation(counts, weighted_counts))
            table["joint_pairs_tv_from_common"] = ratio(total_variation(pairs, full_pairs))
            contexts.append(table)
        arms[arm] = context_scores(contexts)
    return arms


def pair_counts(words, counts, width):
    output = [0] * 16
    for word, count in zip(words, counts, strict=True):
        at = 8 * word[0] + 4 * word[1] + 2 * word[width] + word[width + 1]
        output[at] += count
    return output


def context_counts(pairs, x, y):
    outputs = {"I": [0] * 4, "II": [0] * 4}
    pair_marginals = ([0] * 4, [0] * 4)
    for word, count in enumerate(pairs):
        a, b = divmod(word, 4)
        pair_marginals[0][a] += count
        pair_marginals[1][b] += count
        outputs["I"][2 * ((a >> (1 - x)) & 1) + ((b >> (1 - y)) & 1)] += count
        outputs["II"][2 * int(a == 3 * x) + int(b == 3 * y)] += count
    total = sum(pairs)
    result = {"settings": [x, y], "weight": total, "pair_joint": pairs, "pair_marginals": pair_marginals,
              "joint_pairs_tv_from_product": ratio(total_variation(pairs, product_of_marginals(pairs, 4)))}
    for reading, cells in outputs.items():
        e = Fraction(cells[0] + cells[3] - cells[1] - cells[2], total) if total else None
        result[reading] = {"joint": cells, "correlation": ratio(e),
                           "outcome_marginals": ([cells[0] + cells[1], cells[2] + cells[3]],
                                                 [cells[0] + cells[2], cells[1] + cells[3]]),
                           "joint_tv_from_product": ratio(total_variation(cells, product_of_marginals(cells, 2)))}
    return result


def remote_changes(contexts, marginal):
    pairs = ((0, 1), (2, 3)), ((0, 2), (1, 3))
    return [[ratio(total_variation(marginal(contexts[i])[side], marginal(contexts[j])[side]))
             for i, j in comparisons] for side, comparisons in enumerate(pairs)]


def context_scores(contexts):
    result = {"contexts": contexts,
              "pair_marginal_remote_tv": remote_changes(contexts, lambda row: row["pair_marginals"])}
    for reading in ("I", "II"):
        encoded = [row[reading]["correlation"] for row in contexts]
        signs = [settings for settings in product((1, -1), repeat=4) if settings.count(-1) % 2]
        if all(value is not None for value in encoded):
            ev = [Fraction(*value) for value in encoded]
            signed = ev[0] + ev[1] + ev[2] - ev[3]
            all_scores = [sum((value * sign for value, sign in zip(ev, pattern, strict=True)), Fraction())
                          for pattern in signs]
            maximum = max(all_scores)
        else:
            signed = maximum = None
            all_scores = [None] * len(signs)
        result[reading] = {"signed_s": ratio(signed), "maximum": ratio(maximum),
                           "chsh_sign_scores": [{"signs": pattern, "value": ratio(value)}
                                                for pattern, value in zip(signs, all_scores, strict=True)],
                           "outcome_marginal_remote_tv": remote_changes(
                               contexts, lambda row: row[reading]["outcome_marginals"])}
    return result
