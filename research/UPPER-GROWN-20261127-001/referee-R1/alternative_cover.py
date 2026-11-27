"""Check which signed lower clauses cover the eight choices below one upper word."""

import argparse
from collections import Counter
from itertools import combinations, islice, permutations, product
import json

from alternative_growth import cnf_check, cnf_with_readings, upper


ORIENTATIONS = tuple(product((0, 1), repeat=3))
SIX_WORDS = tuple("".join(w) for w in product("01", repeat=6))
NAMES = ("A0", "A1", "B0", "B1", "C0", "C1")
CROSS = tuple((i, 2+j, 4+k) for i, j, k in ORIENTATIONS)
EIGHT_WORDS = tuple("".join(map(str, w)) for w in ORIENTATIONS)
ALL = (1 << len(SIX_WORDS)) - 1


def projection(w, places):
    return "".join(w[i] for i in places)


def masks_of(f):
    return {w: sum(1 << i for i, source in enumerate(SIX_WORDS) if f(source) == w) for w in EIGHT_WORDS}


MASKS = {s: masks_of(lambda w: projection(w, s)) for s in combinations(range(6), 3)}
UPPER = masks_of(upper)
UPPER_BITS = [sum(mask for w, mask in UPPER.items() if w[k] == "1") for k in range(3)]


def allows_all_pairs(words):
    return all(len({projection(w, pair) for w in words}) == 4 for pair in combinations(range(3), 2))


def sign_product(assignment):
    for axis in range(3):
        for choice in range(2):
            signs = {assignment[i][axis] for i, src in enumerate(ORIENTATIONS) if src[axis] == choice}
            if len(signs) > 1:
                return False
    return True


def details(assignment, kept, upper_allowed):
    masks = [MASKS[s][w] for s, w in zip(CROSS, assignment)]
    deletes = []
    for j, law in enumerate(masks):
        restored = UPPER["111"] & law
        for i, other in enumerate(masks):
            if i != j:
                restored &= ~other
        assert restored.bit_count() == 1
        deletes.append(SIX_WORDS[restored.bit_length() - 1])
    observed = [w for i, w in enumerate(SIX_WORDS) if (kept >> i) & 1]
    extra = {str(s): [w for w in EIGHT_WORDS if not (kept & m[w])] for s, m in MASKS.items()
             if s not in CROSS and any(not (kept & m[w]) for w in EIGHT_WORDS)}
    mixed = {}
    for s in CROSS:
        counts = []
        for column in range(3):
            groups = {}
            for w in observed:
                groups.setdefault(projection(w, s), set()).add(upper(w)[column])
            counts.append(sum(len(g) == 2 for g in groups.values()))
        assert all(counts)
        mixed[str(s)] = counts
    clauses = [" ".join(("~" if b == "1" else "") + NAMES[j] for j, b in zip(s, w))
               for s, w in zip(CROSS, assignment)]
    _, names = cnf_with_readings()
    for k, out in enumerate("PQR"):
        for x, y in product((0, 1), repeat=2):
            bad = (x, y, int(x != y))
            columns = (NAMES[2*k], NAMES[2*k+1], out)
            clauses.append(" ".join(("~" if v else "") + col for col, v in zip(columns, bad)))
    cnf = "; ".join(clauses)
    return {"forbidden_words_in_000_to_111_transversal_order": assignment,
            "specified_triples": CROSS, "other_nonfull_triples": extra,
            "number_of_six_bit_words": len(observed), "upper_image": upper_allowed,
            "reading_fixes_leaving_both_values_at_each_lower_knot": mixed,
            "six_bit_witness_on_deletion_for_upper_111": deletes,
            "upper_cnf_with_the_six_lower_readings_quantified": cnf,
            "canonical_check": cnf_check(cnf, names)}


def count_patterns(limit):
    counts = Counter()
    missing_tally = Counter()
    witnesses = {}
    previous_tuple = tuple(f"{i ^ j}{j}{k}" for i, j, k in ORIENTATIONS)
    for assignment in islice(permutations(EIGHT_WORDS), limit):
        counts["permutations_read"] += 1
        kept = ALL
        for s, w in zip(CROSS, assignment):
            kept &= ~MASKS[s][w]
        if any(sum(bool(kept & m) for m in MASKS[s].values()) != 7 for s in CROSS):
            continue
        counts["each_specified_triple_forbids_exactly_one_word"] += 1
        upper_allowed = [w for w, m in UPPER.items() if kept & m]
        if not allows_all_pairs(upper_allowed):
            continue
        counts["upper_knot"] += 1
        if sign_product(assignment):
            counts["sign_product_upper_knot"] += 1
            continue
        counts["nonproduct_upper_knot"] += 1
        missing_tally[8 - len(upper_allowed)] += 1
        if all(any(f & kept & reading and f & kept & ~reading for f in MASKS[s].values())
               for s in CROSS for reading in UPPER_BITS):
            counts["nonproduct_upper_knot_unread_at_each_of_eight_lower_knots"] += 1
        if assignment == previous_tuple:
            witnesses["first_sign_at_A_depends_on_B_index"] = details(assignment, kept, upper_allowed)
        if all(kept & m for s in MASKS if s not in CROSS for m in MASKS[s].values()):
            counts["nonproduct_upper_knot_and_no_extra_nonfull_triple"] += 1
            key = f"no_extra_nonfull_triple_upper_words_{len(upper_allowed)}"
            if key not in witnesses:
                witnesses[key] = details(assignment, kept, upper_allowed)
    return {"domain": "Abstract lower relations on six bits. No raw not-all-equal realization is assumed.",
            "normalization": "All three upper agreements are true in the fixed forbidden word.",
            "counts": dict(counts), "nonproduct_upper_knots_by_number_of_missing_upper_words": dict(missing_tally),
            "examples": witnesses}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=40320)
    options = parser.parse_args()
    print(json.dumps(count_patterns(options.limit), indent=2))
