"""Exact last-junction row and menu comparisons on six fixed prefixes."""

from collections import Counter, defaultdict
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
import json


SOURCE = (Path(__file__).resolve().parents[2] / "VARIABLE-OUTPUT-READER-20261118-001G"
          / "VARIABLE-OUTPUT-READER-20261118-001G-P001_two_three_fresh" / "six_check.py")
spec = spec_from_file_location("prefix_literal_checker", SOURCE)
literal = module_from_spec(spec)
spec.loader.exec_module(literal)


SEED = (("0", (0, 1, 2)),)
CUBE = ((0,), (0,), (0,), (1, 2), (1, 3), (2, 3))
LAYER = ((4, 5), (4, 6), (5, 6))
FRONTIER = ((0,), (1,), (0, 2), (1, 3), (2, 4), (3, 5), (0, 6), (5, 7),
            (2, 8), (1, 7, 9), (4, 8, 10), (3, 9, 11), (6, 10, 12))


def attach(history, parents, h):
    holders, adjacency = literal.incidence(history)
    labels = tuple(str(parent) for parent in parents)
    assert literal.legal(labels, adjacency), (parents, h)
    used = tuple(min(bit for bit, users in holders.items() if users == [site]) for site in labels)
    fresh = tuple(range(len(holders), len(holders) + h))
    return (*history, (str(len(history)), (*used, *fresh)))


def grow(history, steps, counts):
    for parents, h in zip(steps, counts, strict=True):
        history = attach(history, parents, h)
    return history


def branch(history, parent):
    first = len(history)
    leaves = tuple(range(first + 1, first + 4))
    steps = ((parent,), (first,), (first,), (first,), *combinations(leaves, 2))
    return grow(history, steps, (3, 2, 2, 2, 2, 2, 2))


def roster():
    core = grow(SEED, CUBE, (2,) * 6)
    mixed = grow(SEED, (*CUBE, (2, 3), (4, 5, 6), (4, 5, 7), (8, 9)),
                 (2, 3, 3, 2, 2, 2, 2, 2, 3, 3))
    four = grow(SEED, FRONTIER, (3,) * 3 + (2,) * 10)
    assert set(bit for bit, users in literal.incidence(four)[0].items() if len(users) == 1) == {27, 29, 30, 31}
    return (("seven_site_core", core), ("layered_six_loose", grow(core, LAYER, (2, 2, 2))),
            ("mixed_sibling_caps", mixed), ("five_loose_frontier", four[:-1]),
            ("two_separate_live_branches", branch(branch(SEED, 0), 0)),
            ("four_frontier_with_live_branch", branch(four, 12)))


def short_equations(history):
    """Walk the literal dual in Gray order, keeping words small enough for the row."""
    stars = tuple(literal.mask(support) for _, support in history)
    current = 0
    short = {0}
    for step in range(1, 1 << len(stars)):
        current ^= stars[(step & -step).bit_length() - 1]
        if current.bit_count() <= 6:
            short.add(current)
    return short


def minimal_words(words, earlier=()):
    accepted = list(earlier)
    for word in sorted(words, key=lambda word: (word.bit_count(), word)):
        if word and not any(word & old == old for old in accepted):
            accepted.append(word)
            yield word


def fresh_row(prefix_width, p, h, short, old_bonds):
    """Only old words of weight ≤6 can contribute to a new bond through h+3."""
    added = literal.mask(range(prefix_width, prefix_width + h))
    operand = literal.mask(p)
    ceiling = h + 3
    pool = {added | (operand ^ old) for old in short if (operand ^ old).bit_count() <= 3}
    row = [ceiling + 1] * (prefix_width + h)
    for bond in minimal_words(pool, old_bonds):
        for bit in literal.bits(bond):
            if bit != prefix_width:
                row[bit] = min(row[bit], bond.bit_count())
    return tuple(value for i, value in enumerate(row) if i != prefix_width)


def verify_row(history, width, prefix_width, h, row):
    _, _, _, _, measured = literal.measure(history, width)
    full = tuple(min(measured[tuple(sorted((prefix_width, i)))][0], h + 4)
                 for i in range(width) if i != prefix_width)
    assert full == row


def image_of_triple(triple, prefix_width, width):
    return tuple(sorted(i if i < prefix_width else width - 1 - (i - prefix_width) for i in triple))


def record_match(a, b, short, cutoff):
    p, signature, menu = a
    q, _, other_menu = b
    return {"P": p, "Q": q, "cutoff_K": cutoff,
            "common_row": tuple(min(item, cutoff + 1) for item in signature),
            "same_allowed_states": (literal.mask(p) ^ literal.mask(q)) in short,
            "P_legal_triples": sorted(menu), "Q_legal_triples": sorted(other_menu)}


def full_row_from_swap(prefix, a, b, cutoff):
    difference = sorted(set(a[0]) ^ set(b[0]))
    if len(difference) != 2:
        return False
    x, y = difference
    # A prefix symmetry sends the two successors to one another. Its only
    # two moved row positions have the same known exact value on the first.
    return (a[1][x] == a[1][y] <= cutoff
            and all((x in support) == (y in support) for _, support in prefix))


def examine(prefix, h, short, old_bonds):
    holders, adjacency = literal.incidence(prefix)
    width = len(holders)
    loose = sorted(bit for bit, users in holders.items() if len(users) == 1)
    groups = [group for size in (1, 2, 3) for group in combinations(loose, size)
              if literal.legal(tuple(holders[bit][0] for bit in group), adjacency)]
    entries = []
    independently_measured = 0
    for group in groups:
        row = fresh_row(width, group, h, short, old_bonds)
        successor = (*prefix, (str(len(prefix)), (*group, *range(width, width + h))))
        literal.replay(successor)
        menu = frozenset(literal.direct_triples(*literal.incidence(successor)))
        assert {image_of_triple(triple, width, width + h) for triple in menu} == menu
        if len(prefix) <= 11:
            verify_row(successor, width + h, width, h, row)
            independently_measured += 1
        entries.append((group, row, menu))

    classes = defaultdict(list)
    for entry in entries:
        classes[entry[1]].append(entry)
    matches = [pair for group in classes.values() for pair in combinations(group, 2)]
    for a, b in matches:
        assert len(a[0]) == len(b[0]) and a[2] == b[2], record_match(a, b, short, h + 3)
    positive_matches = [(a, b) for a, b in matches if a[2]]
    fresh_matches = [(a, b) for a, b in positive_matches if any(max(t) >= width for t in a[2])]
    different_spaces = [(a, b) for a, b in positive_matches
                        if (literal.mask(a[0]) ^ literal.mask(b[0])) not in short]
    positive_example = None
    if different_spaces:
        a, b = different_spaces[0]
        positive_example = record_match(a, b, short, h + 3)
        positive_example["full_fresh_row_matches_by_literal_input_swap"] = full_row_from_swap(prefix, a, b, h + 3)

    def coarse(entry):
        return tuple(min(value, h + 3) for value in entry[1])

    def sizes(a, b):
        return "-".join(map(str, sorted((len(a[0]), len(b[0])))))

    pairs = list(combinations(entries, 2))
    smaller = [(a, b) for a, b in pairs if coarse(a) == coarse(b) and a[2] != b[2]]
    return {
        "fresh_count": h,
        "legal_input_counts": dict(sorted(Counter(len(group) for group in groups).items())),
        "literal_comparisons_by_parent_counts": dict(sorted(Counter(sizes(a, b) for a, b in pairs).items())),
        "distinct_rows_through_h_plus_3": len(classes),
        "matching_pairs_by_parent_counts": dict(sorted(Counter(sizes(a, b) for a, b in matches).items())),
        "matching_pairs_with_nonempty_menu": len(positive_matches),
        "matching_pairs_with_nonempty_menu_and_distinct_codes": len(different_spaces),
        "successors_with_fresh_mark_in_a_legal_triple": sum(any(max(t) >= width for t in e[2]) for e in entries),
        "matching_pairs_with_fresh_mark_in_a_legal_triple": len(fresh_matches),
        "capped_h_plus_2_matches_with_opposite_verdict": len(smaller),
        "connected_cut_row_controls": independently_measured,
        "fresh_output_renaming_controls": len(entries),
        "positive_matched_example": positive_example,
        "smaller_horizon_example": record_match(*smaller[0], short, h + 2) if smaller else None,
    }


def main():
    records = []
    for label, prefix in roster():
        literal.replay(prefix)
        holders, adjacency = literal.incidence(prefix)
        old_menu = literal.direct_triples(holders, adjacency)
        assert old_menu
        short = short_equations(prefix)
        old_bonds = tuple(minimal_words(short))
        records.append({"prefix": label, "width": len(holders), "chronological_prefix_checks": prefix,
                        "old_triple_menu": old_menu,
                        "by_fresh_count": [examine(prefix, h, short, old_bonds) for h in (2, 3)]})
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
