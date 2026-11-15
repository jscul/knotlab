"""Check finite certificates for the simultaneous ternary crossing reader."""

import json
from functools import reduce
from itertools import product
from math import comb
from operator import or_


PAIRS = tuple(product(range(3), repeat=2))
# Each entry pairs a state (a,d) with its designated query (k,t).
CERTIFICATE = (
    ((1, 0), (2, 1)),
    ((2, 2), (0, 2)),
    ((1, 1), (1, 2)),
    ((0, 0), (2, 0)),
    ((1, 2), (0, 1)),
    ((0, 1), (1, 1)),
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def accepts(query, state):
    k, t = query
    a, d = state
    return (a + k * d) % 3 == t


def crosses_to(query, state):
    k, t = query
    a, d = state
    left, right = a, (a + d) % 3
    for _ in range(k):
        left, right = right, (2 * right - left) % 3
    return left == t


def jointly_accepts(query, state):
    return all(accepts(q, s) for q, s in zip(query, state, strict=True))


def bit_members(mask):
    return tuple(i for i in range(mask.bit_length()) if mask & (1 << i))


def profile(states, columns):
    return reduce(or_, (columns[i] for i in states), 0)


def columns_for(words):
    return [
        sum(1 << i for i, query in enumerate(words) if jointly_accepts(query, state))
        for state in words
    ]


def rank_mod_three(rows):
    work = [list(row) for row in rows]
    width = len(work[0])
    rank = 0
    for j in range(width):
        pivot = next((i for i in range(rank, len(work)) if work[i][j]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        # Both nonzero residues in F_3 are their own multiplicative inverses.
        inverse = work[rank][j]
        work[rank] = [(x * inverse) % 3 for x in work[rank]]
        for row in work[rank + 1:]:
            factor = row[j]
            if factor:
                for k in range(j, width):
                    row[k] = (row[k] - factor * work[rank][k]) % 3
        rank += 1
    return rank


def check_base(matrix, columns):
    for i, (k, t) in enumerate(PAIRS):
        for j, (a, d) in enumerate(PAIRS):
            expected = crosses_to((k, t), (a, d))
            require(matrix[i][j] == expected, "crossing disagrees with the indexed test")
            require((1 - (a + k * d - t) ** 2) % 3 == expected, "indicator polynomial")
    profiles = set()
    max_private = 0
    num_max_private = 0
    for mask in range(1 << 9):
        states = bit_members(mask)
        report = profile(states, columns)
        profiles.add(report)
        private = all(profile((j for j in states if j != i), columns) != report for i in states)
        if private:
            if len(states) > max_private:
                max_private = len(states)
                num_max_private = 0
            if len(states) == max_private:
                num_max_private += 1
    require((len(profiles), max_private, num_max_private) == (110, 5, 27),
            "one-pair exhaustive counts")
    five_states = ((0, 0), (0, 1), (0, 2), (1, 0), (2, 1))
    five_queries = ((2, 0), (2, 2), (1, 2), (0, 1), (0, 2))
    for i, query in enumerate(five_queries):
        require([j for j, state in enumerate(five_states) if accepts(query, state)] == [i],
                "five-state certificate")
    return profiles, max_private, num_max_private


def check_certificate():
    states, queries = zip(*CERTIFICATE)
    require(len(set(states)) == len(set(queries)) == 6, "repeated certificate index")
    minor = [[int(accepts(q, s)) for s in states] for q in queries]
    expected = ["100000", "010000", "001000", "011100", "101010", "110001"]
    require(["".join(map(str, row)) for row in minor] == expected, "two-level minor")
    require(rank_mod_three(minor) == 6, "six-state rank certificate")
    return minor


def fixed_level_words(b):
    return [w for w in product(range(6), repeat=b) if sum(i >= 3 for i in w) == b // 2]


def check_restricted_power(b):
    words = fixed_level_words(b)
    states = [tuple(CERTIFICATE[i][0] for i in w) for w in words]
    queries = [tuple(CERTIFICATE[i][1] for i in w) for w in words]
    expected = 3**b * comb(b, b // 2)
    require(len(set(states)) == len(set(queries)) == expected, "power encoding is not injective")
    for i, query in enumerate(queries):
        hits = [j for j, state in enumerate(states) if jointly_accepts(query, state)]
        require(hits == [i], "fixed-level words have an extraneous or missing meeting")
    return states


def compatible_counts_by_level(minor, b):
    """Count possible private-family hits for a query with floor(b/2) high letters."""
    options = [(sum(row[:3]), sum(row[3:])) for row in minor]
    require(set(options[:3]) == {(1, 0)} and set(options[3:]) == {(2, 1)},
            "level choices depend on a different certificate")
    counts = [1]
    for i in range(b):
        low, high = options[3 if i < b // 2 else 0]
        new = [0] * (len(counts) + 1)
        for j, ways in enumerate(counts):
            new[j] += ways * low
            new[j + 1] += ways * high
        counts = new
    return counts


def check_representative(states, columns, rank):
    target = profile(states, columns)
    kept = list(states)
    for i in states:
        reduced = [j for j in kept if j != i]
        if profile(reduced, columns) == target:
            kept = reduced
    require(len(kept) <= rank and profile(kept, columns) == target, "representative bound")
    private_rows = []
    for i in kept:
        private = columns[i] & ~profile((j for j in kept if j != i), columns)
        require(private != 0, "minimal representative has no private query")
        private_rows.append(private & -private)
    require(len(set(private_rows)) == len(kept), "private queries coincide")


def product_report(first, second):
    return sum(second << (9 * i) for i in bit_members(first))


def main():
    local_matrix = [[int(accepts(q, s)) for s in PAIRS] for q in PAIRS]
    rank_one = rank_mod_three(local_matrix)
    require(rank_one == 6, "one-pair ternary rank")
    local_columns = columns_for(list(product(PAIRS, repeat=1)))
    local_profiles, max_private, num_max_private = check_base(local_matrix, local_columns)
    minor = check_certificate()

    words_two = list(product(PAIRS, repeat=2))
    columns_two = columns_for(words_two)
    matrix_two = [[(c >> i) & 1 for c in columns_two] for i in range(len(words_two))]
    rank_two = rank_mod_three(matrix_two)
    require(rank_two == 36, "two-pair ternary rank")
    require(all(sum(row) == 9 for row in matrix_two), "two-pair query has wrong fibre size")

    private_two = check_restricted_power(2)
    private_four = check_restricted_power(4)
    word_index = {w: i for i, w in enumerate(words_two)}
    private_indices = [word_index[w] for w in private_two]
    subsets = {0}
    for i in private_indices:
        subsets |= {report | columns_two[i] for report in subsets}
    require(len(subsets) == 2**18, "private subfamilies give the same joint answer profile")
    controls = [[], range(81), private_indices, [10 * i for i in range(9)], range(0, 81, 2)]
    for states in controls:
        check_representative(states, columns_two, rank_two)

    product_profiles = {product_report(x, y) for x in local_profiles for y in local_profiles}
    require(len(product_profiles) == 1 + 109**2, "two-pair product profile count")
    # Test the product factorization against joint evaluations for every product
    # of two singleton states, then for larger and empty local tables.
    local_tables = [(i,) for i in range(9)] + [(), (0, 3, 8), tuple(range(9))]
    for left, right in product(local_tables, repeat=2):
        state_ids = [9 * i + j for i in left for j in right]
        expected = product_report(profile(left, local_columns), profile(right, local_columns))
        require(profile(state_ids, columns_two) == expected, "Cartesian witness factorization")

    u, v = (0, 0), (1, 0)
    joined, crossed = [(u, u), (v, v)], [(u, v), (v, u)]
    for i in range(2):
        require({s[i] for s in joined} == {s[i] for s in crossed},
                "control has different projections")
    query = ((0, 0), (0, 0))
    require(any(jointly_accepts(query, s) for s in joined), "missing common witness")
    require(not any(jointly_accepts(query, s) for s in crossed), "separate witnesses passed")

    private_eight = 3**8 * comb(8, 4)
    require(compatible_counts_by_level(minor, 8)[4] == 1, "eight-pair query has multiple hits")
    require(private_eight == 459270 and private_eight > max_private**8, "eight-pair gain")
    require((9**8 - 1).bit_length() + 1 == 27, "query-first communication count")
    return {
        "status": "passed",
        "rank_mod_three_b1": rank_one,
        "rank_mod_three_b2": rank_two,
        "profiles_b1": len(local_profiles),
        "minimum_message_bits_b1": (len(local_profiles) - 1).bit_length(),
        "largest_private_family_b1": max_private,
        "largest_private_families_b1": num_max_private,
        "private_states_b2": len(private_two),
        "profiles_of_private_subfamilies_b2": len(subsets),
        "private_states_directly_compared_b4": len(private_four),
        "private_states_b8": private_eight,
        "product_of_local_private_families_b8": max_private**8,
        "representative_controls_b2": len(controls),
        "product_profiles_b2": len(product_profiles),
        "product_minimum_message_bits_b2": (len(product_profiles) - 1).bit_length(),
        "same_projections_have_different_joint_answers": True,
        "query_first_total_bits_b8": (9**8 - 1).bit_length() + 1,
        "explicit_table_bits_b8": 9**8,
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))
