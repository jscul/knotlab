"""Check quadratic signs on four reads, two census counterexamples and the block sign.

For a linear read P on the parity state space S, choose a linear section t of
P(S), and put K = ker P in S. Write q(0) = 0 after removing a global sign.
Let B be the polar form of q, R its radical on K, and split K = R + H. A shift
by r in R cancels all terms over y unless B(t(y), r) = q(r) for every r in R.
These affine equations can be inconsistent. Where they hold, summing over R
gives |R|. On H, the nondegenerate B determines the unique z(y) in H with
B(z(y), h) = B(t(y), h) for every h. Translating by z(y) leaves the common
sum over H times the quadratic sign with exponent q(t(y)) + q(z(y)). The
common sum squared is |H| by summing the characters B(h, u) for u in H.
This proves the claimed form and allows the surviving support to shrink.

For a character on an affine state set, the sum over a pair of reads vanishes
on every value if the character varies along the unread kernel. Otherwise
the absolute sum on each attainable value is the size of that kernel.
When all four squared tables have nonzero totals, they are the pair marginals
of the uniform weighting of the original affine set. A nonconstant character
has zero total under the unsquared reading. A constant character gives the
uniform weighting on its support after normalization.

A value read counting squared weights on a fixed, nonempty support always
has an ordinary joint weighting. On every joint assignment each signed CHSH
expression is +2 or -2, so its weighted average lies between those values.
Restricting the support can change the table.
"""
from argparse import ArgumentParser
from collections import Counter
from ctypes import c_int64
from fractions import Fraction
from itertools import combinations, product
import gzip
import json
from pathlib import Path


STARTS = Path(__file__).resolve().parents[2] / "FORBID-EDITS-20261126-001" / "starts.json"
READ_PAIRS = tuple(product((0, 1), (2, 3)))
WORDS = range(16)


def truth_mask(predicate):
    return sum(1 << word for word in WORDS if predicate(word))


def members(mask):
    return [word for word in WORDS if mask >> word & 1]


def affine_sets():
    """Test every nonempty 16-bit subset for closure under triple XOR."""
    for mask in range(1, 1 << 16):
        if mask.bit_count() not in (1, 2, 4, 8, 16):
            continue
        elements = members(mask)
        origin = elements[0]
        if all(mask >> (origin ^ x ^ y) & 1 for x, y in combinations(elements, 2)):
            yield mask


def all_phases():
    variable = [truth_mask(lambda x: x >> i & 1) for i in range(4)]
    monomial = variable + [a & b for a, b in combinations(variable, 2)]
    phases = [0]
    for term in monomial:
        phases.extend([mask ^ term for mask in phases])
    return phases


def outcome_masks():
    return [
        [truth_mask(lambda w: (w >> s & 1, w >> t & 1) == (a, b))
         for a, b in product(range(2), repeat=2)]
        for s, t in READ_PAIRS
    ]


def integer_tables(support, negative, partitions):
    return [[(support & outcome).bit_count() - 2 * (negative & outcome).bit_count()
             for outcome in pair] for pair in partitions]


def chsh(tables):
    """Return the maximum over signed CHSH orientations after gates G0 through G3."""
    totals = {sum(t) for t in tables}
    if len(totals) != 1 or 0 in totals:
        return None
    z, = totals
    if any(value * z < 0 for t in tables for value in t):
        return None
    (p, q, r, s) = tables
    if ((p[0] + p[1], r[0] + r[1], p[0] + p[2], q[0] + q[2]) !=
            (q[0] + q[1], s[0] + s[1], r[0] + r[2], s[0] + s[2])):
        return None
    e = [t[0] - t[1] - t[2] + t[3] for t in tables]
    return Fraction(max(abs(sum(e) - 2 * v) for v in e), abs(z))


def ties(support):
    return [[i, j, next(iter(values))] for i, j in READ_PAIRS
            if len(values := {(w >> i ^ w >> j) & 1 for w in members(support)}) == 1]


def four_read_census(sets):
    phases = all_phases()
    partitions = outcome_masks()
    size_count = Counter()
    hit_counts = {r: Counter() for r in ("R1", "R2")}
    distinct_hits = Counter()
    hit_relations = Counter()
    best = {"R1": 0, "R2": 0}
    best_affine = best.copy()
    for support in sets:
        size_count[support.bit_count()] += 1
        # Signs differing globally have identical probabilities under both readings.
        def restriction(mask):
            negative = support & mask
            return min(negative, support ^ negative)

        multiplicity = Counter(restriction(q) for q in phases)
        linear = {restriction(q) for q in phases[:16]}
        for negative, count in multiplicity.items():
            tables = integer_tables(support, negative, partitions)
            scores = {"R1": chsh(tables), "R2": chsh([[x*x for x in t] for t in tables])}
            hits = []
            for reading, score in scores.items():
                if score is None:
                    continue
                best[reading] = max(best[reading], score)
                if negative in linear:
                    best_affine[reading] = max(best_affine[reading], score)
                if score > 2:
                    key = f"support {support.bit_count()}, cross ties {len(ties(support))}, CHSH {score}"
                    hit_counts[reading][key] += count
                    distinct_hits[reading] += 1
                    hits.append(reading)
            if hits:
                hit_relations[" and ".join(hits)] += count

    return {
        "scope": "All four-read affine sets and 1024 ambient polynomials per set, up to global sign",
        "nonempty_affine_sets_by_size": dict(sorted(size_count.items())),
        "polynomial_and_support_presentations": sum(size_count.values()) * len(phases),
        "largest_CHSH": {r: str(v) for r, v in best.items()},
        "largest_for_sign_affine_on_its_own_support": {r: str(v) for r, v in best_affine.items()},
        "hits_counting_ambient_polynomials": hit_counts,
        "distinct_hitting_weightings_on_their_own_support_up_to_global_sign": distinct_hits,
        "same_presentations_by_reading": hit_relations,
    }


def knot_rows(start):
    n, sharing, loose = start
    rows = [[] for _ in range(n)]
    next_bit = 0
    for i, j, number in sharing:
        for _ in range(number):
            rows[i].append(next_bit)
            rows[j].append(next_bit)
            next_bit += 1
    for row, number in zip(rows, loose):
        row.extend(range(next_bit, next_bit + number))
        next_bit += number
    return rows


def lift_pairs(rows, swap, maximal):
    by_holders = {}
    distinctions = sorted({d for row in rows for d in row})
    for d in distinctions:
        group = tuple(i for i, row in enumerate(rows) if d in row)
        by_holders.setdefault(group, []).append(d)
    pairs = []
    for group, bits in by_holders.items():
        image = tuple(sorted(swap[i] for i in group))
        if image < group:
            pairs.extend(zip(bits, by_holders[image]))
        if maximal and image == group:
            pairs.extend(zip(bits[::2], bits[1::2]))
    return [sorted(pair) for pair in pairs]


def allowed(rows):
    masks = [sum(1 << d for d in row) for row in rows]
    for state in range(1 << max(m.bit_length() for m in masks)):
        if all((state & m).bit_count() % 2 == 0 for m in masks):
            yield state


def projected_sums(words, sums):
    return [[sum(sums[w] for w in words if (w >> s & 1, w >> t & 1) == (a, b))
             for a, b in product(range(2), repeat=2)] for s, t in READ_PAIRS]


def support_witness(start, reads, swap):
    rows = knot_rows(start)
    pairs = lift_pairs(rows, swap, False)
    unsigned, signed, restricted = ([0] * 16 for _ in range(3))
    for state in allowed(rows):
        word = sum((state >> d & 1) << i for i, d in enumerate(reads))
        sign = (-1) ** sum((state >> i) & (state >> j) & 1 for i, j in pairs)
        unsigned[word] += 1
        signed[word] += sign
        if all((state >> i ^ state >> j) & 1 == 0 for i, j in pairs):
            restricted[word] += sign ** 2
    support = truth_mask(lambda w: signed[w] != 0)
    allowed_support = truth_mask(lambda w: unsigned[w] != 0)
    raw = projected_sums(WORDS, signed)
    ordinary = projected_sums(WORDS, unsigned)
    kept = projected_sums(WORDS, restricted)
    return {
        "pattern": "Four knots with two loose distinctions each, shared once at 0–1, 0–2 and 1–3",
        "census_index": 89, "round": 0, "knots": rows, "swap": swap, "minimal_lift_pairs": pairs,
        "weight": "Minus one for an odd number of swapped pairs both holding one; plus one otherwise",
        "reader_distinctions": [reads[:2], reads[2:]], "word_encoding": "least significant bit is first read",
        "all_four_read_completion_counts": unsigned, "all_four_read_signed_sums": signed,
        "cross_ties_on_allowed_reads": ties(allowed_support),
        "cross_ties_on_noncancelling_reads": ties(support),
        "cross_tie_encoding": "[position of first read, position of second read, their XOR]",
        "R1_signed_pair_sums": raw, "R1_CHSH": str(chsh(raw)),
        "R2_CHSH": str(chsh([[x*x for x in t] for t in raw])),
        "A6_unsigned_pair_counts": ordinary, "A6_unsigned_CHSH": str(chsh(ordinary)),
        "A6_unsigned_pair_counts_after_restricting_to_kept_states": kept,
        "A6_restricted_CHSH": str(chsh(kept)),
    }


def flip_witness(starts):
    pattern = [3, [[0, 1, 2], [0, 2, 2]], [2, 2, 2]]
    rows = knot_rows(pattern)
    swap = [0, 2, 1]
    pairs = lift_pairs(rows, swap, True)
    moved = {d for pair in pairs for d in pair}
    states = list(allowed(rows))
    return {
        "pattern": "Three knots with two loose distinctions each, each outside knot sharing two with the middle",
        "census_index": starts.index(pattern), "knots": rows, "swap": swap,
        "maximal_lift_pairs": pairs, "total_distinctions": len(set.union(*map(set, rows))),
        "moved_distinctions": len(moved), "moved_counts_per_knot": [len(set(row) & moved) for row in rows],
        "allowed_states": len(states),
        "flipped_on_moved_states": sum(all((x >> a ^ x >> b) & 1 for a, b in pairs) for x in states),
        "reason": "A flipped assignment has three ones on the fixed middle knot, one from each of its three swapped pairs.",
    }


def squared_character():
    # The common bit distinguishes the two words, so their signed total is zero.
    tables = integer_tables((1 << 0) | (1 << 15), 1 << 15, outcome_masks())
    squared = [[x*x for x in t] for t in tables]
    return {"support": ["0000", "1111"], "weights": [1, -1], "R1_total": sum(tables[0]),
            "R2_pair_tables_before_normalization": squared, "R2_CHSH": str(chsh(squared))}


def fixed_width_boundary(pilot):
    """Compare the four-term score in exact and signed 64-bit arithmetic."""
    amplitude = 1 << 30
    e = [-2 * amplitude ** 2] + [2 * amplitude ** 2] * 3
    exact = [abs(sum(e) - 2 * v) for v in e]
    narrow = [c_int64(abs(c_int64(sum(e) - 2 * v).value)).value for v in e]
    score_denominator = 2 * amplitude ** 2
    here = Path(__file__).resolve().parents[1]
    # The stored normalizers are used only to locate the numerical boundary.
    coverage = {}
    for name in ("census_results.jsonl.gz", "named_rings.jsonl", "named_lone.jsonl", "named_partnered.jsonl"):
        opener = gzip.open if name.endswith(".gz") else open
        records = rows = at_boundary = maximum = 0
        with opener(here / name, "rt") as stream:
            for line in stream:
                records += 1
                item = json.loads(line)
                stages = item["result"]["rows"] if "result" in item else [item]
                for stage in stages:
                    if stage["law"] != "parity" or not isinstance(stage["classes"], list):
                        continue
                    for action in stage["classes"]:
                        for weight, result in action["weightings"].items():
                            if weight not in ("W1", "W1c", "W2"):
                                continue
                            rows += 1
                            total = abs(result["Z"])
                            maximum = max(maximum, total)
                            at_boundary += total == 2 * amplitude
                if pilot:
                    break
        coverage[name] = {"records": records, "weighting_rows": rows, "maximum_absolute_total": maximum,
                          "absolute_total_equal_to_twice_the_cell_amplitude": at_boundary}
    return {"largest_raw_cell": amplitude, "squared_normalizer": score_denominator,
            "exact_numerators": exact, "signed_64_bit_numerators": narrow,
            "exact_CHSH": str(Fraction(max(exact), score_denominator)),
            "signed_64_bit_CHSH": str(Fraction(max(narrow), score_denominator)),
            "stored_normalizers_read_for_scope_check": coverage}


def block_sign(start):
    """Attach the same three parity knots to each side of a known block-sign hit.

    In each four-read fiber the two side parities are uniform on an affine
    subset of two-bit words. If either parity varies in any fiber, each
    nonempty fiber has at least two such words. At most half are 11, the
    only negative word, so every fiber sum is nonnegative. A negative entry
    therefore requires both side parities to factor through the four reads.

    Each old attachment knot receives two distinctions c, d. New knots hold
    (c,u,v), (d,w,z) and (u,v,w,z). Summing all three parity rows gives
    c+d=0, so the old law is unchanged on every state. Summing the first two
    rows gives even parity on the six new distinctions. Repeating the same
    attachment on both sides preserves the swap, the block sign, and the four
    read marginals after normalization. Reachability by ordinary growth is
    a separate question.
    """
    rows = knot_rows(start)
    reads = [6, 8, 7, 9]
    old_states = list(allowed(rows))
    gadget = list(allowed([[0, 2, 3], [1, 4, 5], [2, 3, 4, 5]]))
    assert all((x >> 1 ^ x) & 1 == 0 for x in gadget)
    assert all(x.bit_count() % 2 == 0 for x in gadget)
    original = [0] * 16
    enlarged = [0] * 16
    for x in old_states:
        word = sum((x >> d & 1) << i for i, d in enumerate(reads))
        a, b = ((word & 3).bit_count() % 2, (word >> 2).bit_count() % 2)
        original[word] += (-1) ** (a * b)
        for left, right in product(gadget, repeat=2):
            new_a = (a + left.bit_count()) % 2
            new_b = (b + right.bit_count()) % 2
            enlarged[word] += (-1) ** (new_a * new_b)
    assert enlarged == [len(gadget) ** 2 * v for v in original]
    t0, t1 = (projected_sums(WORDS, counts) for counts in (original, enlarged))
    return {
        "source": "Five-knot census arrangement at index 3097, before growth; swap 1 with 2 and 3 with 4",
        "reader_distinctions": [reads[:2], reads[2:]],
        "comparison": "The same three-knot attachment on one knot of each exchanged side; a constructed parity pattern",
        "per_side_distinctions_before_and_after": [2, 8],
        "side_distinctions_after_t_copies_per_side": "2 + 6t",
        "number_of_allowed_assignments_for_one_attachment": len(gadget),
        "all_six_added_distinctions_open": all({x >> j & 1 for x in gadget} == {0, 1} for j in range(6)),
        "unsigned_state_counts_before_and_after": [len(old_states), len(old_states) * len(gadget) ** 2],
        "R1_signed_pair_sums_before_and_after": [t0, t1],
        "R1_CHSH_before_and_after": [str(chsh(t0)), str(chsh(t1))],
        "R2_CHSH_before_and_after": [str(chsh([[v*v for v in t] for t in ts])) for ts in (t0, t1)],
        "scope": "The algebra of the block sign supplies no size bound. Ordinary-growth reachability was not tested.",
    }


def main():
    arg = ArgumentParser()
    arg.add_argument("--pilot", action="store_true", help="Use one affine set of each size at the same settings")
    args = arg.parse_args()
    sets = list(affine_sets())
    if args.pilot:
        sets = [next(mask for mask in sets if mask.bit_count() == size) for size in (1, 2, 4, 8, 16)]
    starts = json.loads(STARTS.read_text())
    census = four_read_census(sets)
    tie = support_witness(starts[89], [3, 4, 5, 9], [1, 0, 3, 2])
    flip = flip_witness(starts)
    block = block_sign(starts[3097])
    numeric = fixed_width_boundary(args.pilot)
    assert tie["R1_CHSH"] == tie["R2_CHSH"] == "4"
    assert not tie["cross_ties_on_allowed_reads"] and tie["cross_ties_on_noncancelling_reads"]
    assert all(c > 0 for c in tie["all_four_read_completion_counts"])
    assert flip["total_distinctions"] == flip["moved_distinctions"] and flip["flipped_on_moved_states"] == 0
    assert block["R1_CHSH_before_and_after"] == block["R2_CHSH_before_and_after"] == ["4", "4"]
    assert numeric["exact_CHSH"] == "4" and numeric["signed_64_bit_CHSH"] == "0"
    if not args.pilot:
        assert sum(census["nonempty_affine_sets_by_size"].values()) == 307
    print(json.dumps({"four_read_census": census, "ordinary_and_signed_support": tie,
                      "necessary_evenness": flip, "nonconstant_character": squared_character(),
                      "size_of_sides_for_block_sign": block, "wide_integer_control": numeric}, indent=2))


if __name__ == "__main__":
    main()
