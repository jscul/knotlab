"""Fit one anonymous per-question decision rule from terminal rewards.

The four decisions are made together. At evaluation this head materializes
one public packet plan; the 16 alternatives used in training are not tried.
"""

from itertools import combinations


FEATURES = (
    "question_sources",
    "sources_outside_single_source_questions",
    "sources_exclusive_to_question",
    "largest_overlap_with_another_question",
    "distinct_sources_in_menu",
    "sources_outside_smaller_questions",
    "other_questions_with_equal_source_set",
)


def union(sets):
    result = 0
    for cells in sets:
        result |= cells
    return result


def features(supports):
    supports = tuple(supports)
    if len(supports) != 4 or any(type(s) is not int or s < 0 or s > 511 for s in supports):
        raise ValueError("Expected the public traced source sets of four questions")
    singletons = union(s for s in supports if s.bit_count() == 1)
    all_sources = union(supports)
    rows = []
    for port, own in enumerate(supports):
        others = supports[:port] + supports[port + 1:]
        smaller = union(s for s in others if s.bit_count() < own.bit_count())
        rows.append((
            own.bit_count(), (own & ~singletons).bit_count(),
            (own & ~union(others)).bit_count(), max((own & s).bit_count() for s in others),
            all_sources.bit_count(), (own & ~smaller).bit_count(), others.count(own),
        ))
    return rows


def test(row, atom):
    column, threshold = atom
    return row[column] >= threshold


def mask_from_rows(rule, rows):
    op, atoms = rule["op"], rule["tests"]
    if op in ("raw", "computed"):
        return 0 if op == "raw" else 15
    if op not in ("test", "and", "or") or len(atoms) != (1 if op == "test" else 2):
        raise ValueError("Invalid direct decision program")
    result = 0
    for port, row in enumerate(rows):
        values = [test(row, atom) for atom in atoms]
        chosen = any(values) if op == "or" else all(values)
        result |= int(chosen) << port
    return result


def choose_mask(checkpoint, supports):
    if tuple(checkpoint["features"]) != FEATURES:
        raise ValueError("Unknown direct sender feature order")
    return mask_from_rows(checkpoint["rule"], features(supports))


def fit(feature_rows, costs):
    """Costs[menu][mask] holds observed wrong answers and physical width."""
    if not feature_rows or len(feature_rows) != len(costs):
        raise ValueError("Training rows and terminal cost tables must correspond")
    packed = {}
    num_wirings = len(feature_rows)
    all_bits = (1 << (4 * num_wirings)) - 1
    candidate_count = 0

    def consider(signature, op, atoms):
        nonlocal candidate_count
        candidate_count += 1
        key = (len(atoms), op, atoms)
        if signature not in packed or key < packed[signature]:
            packed[signature] = key

    consider(0, "raw", ())
    consider(all_bits, "computed", ())
    tests = {}
    for feature in range(len(FEATURES)):
        for threshold in range(1, 10):
            atom = (feature, threshold)
            signature = sum(int(test(row, atom)) << (4 * i + port)
                            for i, menu in enumerate(feature_rows) for port, row in enumerate(menu))
            consider(signature, "test", (atom,))
            tests[atom] = signature
    for a, b in combinations(tests, 2):
        consider(tests[a] & tests[b], "and", (a, b))
        consider(tests[a] | tests[b], "or", (a, b))

    def score(item):
        signature, syntax = item
        mistakes = width = 0
        for menu, by_mask in enumerate(costs):
            error, size = by_mask[(signature >> (4 * menu)) & 15]
            mistakes += error
            width += size
        return mistakes, width, syntax

    best_signature, best_syntax = min(packed.items(), key=score)
    error, width, _ = score((best_signature, best_syntax))
    _, op, atoms = best_syntax
    rule = {"op": op, "tests": [list(atom) for atom in atoms]}
    assert all(mask_from_rows(rule, rows) == (best_signature >> (4 * i)) & 15
               for i, rows in enumerate(feature_rows))
    return {"features": list(FEATURES), "rule": rule}, {
        "training_wrong_answer_bits": error, "training_total_width": width,
        "training_wirings": num_wirings, "programs_offered": candidate_count,
        "distinct_training_decisions": len(packed),
        "constant_raw": list(map(sum, zip(*(row[0] for row in costs)))),
        "constant_computed": list(map(sum, zip(*(row[15] for row in costs)))),
        "test_time_candidate_packets": 1,
    }
