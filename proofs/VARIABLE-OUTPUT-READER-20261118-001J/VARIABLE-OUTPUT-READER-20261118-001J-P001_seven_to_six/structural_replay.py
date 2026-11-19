"""Replay the named six-bit cut, simultaneous legal triples, and nested cuts."""

from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
from pathlib import Path


PROOFS = Path(__file__).resolve().parents[2]
PREDECESSOR = "VARIABLE-OUTPUT-READER-20261118-001C"
CHECKER = PROOFS / PREDECESSOR / f"{PREDECESSOR}-P001_triple_inverse" / "check_gluing.py"
spec = spec_from_file_location("literal_parity", CHECKER)
literal = module_from_spec(spec)
spec.loader.exec_module(literal)

FOLDED = (
    ("a", ("T",), 3), ("b", ("T",), 3), ("u", ("a", "b"), 2),
    ("c", ("T", "u"), 2), ("ab", ("a", "b"), 2), ("ac", ("a", "c"), 2),
    ("bc", ("b", "c"), 2), ("z", ("ab", "ac", "bc"), 2),
)
WIRING = (
    ("E", ("u", "ab"), 2), ("F", ("ac", "bc"), 2),
    ("G", ("z", "E"), 2), ("H", ("z", "F"), 2),
)


def build(actions):
    """Use the least available bit of each parent. Replay every resulting row."""
    names = ["T"]
    rows = [(0, 1, 2)]
    loose = {"T": [0, 1, 2]}
    width = 3
    for name, parents, outputs in actions:
        assert name not in loose
        inputs = [loose[parent].pop(0) for parent in parents]
        loose[name] = list(range(width, width + outputs))
        rows.append(tuple(inputs + loose[name]))
        names.append(name)
        width += outputs
    events = literal.replay(rows)
    for event, (_, parents, outputs) in zip(events[1:], actions, strict=True):
        assert {names[i] for i in event["parents"]} == set(parents)
        assert len(event["fresh"]) == outputs
    return rows, names


def boundary(rows, sites):
    bits = set()
    for i in sites:
        bits.symmetric_difference_update(rows[i])
    return bits


def connected(adjacent, vertices, skip=()):
    unseen = set(vertices)
    todo = [unseen.pop()]
    while todo:
        v = todo.pop()
        for w in adjacent[v] & unseen:
            if (v, w) != skip and (w, v) != skip:
                unseen.remove(w)
                todo.append(w)
    return not unseen


def check_prefix_bond(rows, end, word):
    """Check the exact boundary and both connected shores in the final wired graph."""
    holders, adjacent = literal.incidence(rows)
    outside = len(rows)
    adjacent.append(set())
    for sites in holders.values():
        if len(sites) == 1:
            v, = sites
            adjacent[v].add(outside)
            adjacent[outside].add(v)
    assert boundary(rows, range(end)) == word
    assert connected(adjacent, range(end)) and connected(adjacent, range(end, outside + 1))


def cuts_and_pair_control():
    base, _ = build(FOLDED)
    all_sites = range(len(base))
    width = len(literal.incidence(base)[0])
    word = boundary(base, all_sites)
    before = boundary(base, range(len(base) - 1))
    assert width == 21 and len(before) == 7 and word == {10, 14, 16, 18, 19, 20}
    star_sums = [boundary(base, selection) for n in range(1, len(base) + 1)
                 for selection in combinations(all_sites, n)]
    assert 511 == len(star_sums) and [s for s in star_sums if s <= word] == [word]

    rows, names = build(FOLDED + WIRING)
    holders, _ = literal.incidence(rows)
    assert all(len(holders[bit]) == 2 for bit in word)
    check_prefix_bond(rows, len(base), word)
    pairs = [sorted(word.intersection(rows[names.index(label)])) for label in ("E", "F", "z")]
    assert all(len(pair) == 2 for pair in pairs) and set().union(*pairs) == word
    small_tables = literal.scalar_table(literal.minimal_dual(rows), len(holders))
    values = [literal.delta(small_tables, *pair) + 1 for pair in pairs]
    assert values == [4, 4, 5]
    possible_splits = [triple for triple in combinations(word, 3)
                       if all(len(set(triple).intersection(pair)) != 1 for pair in pairs)]
    assert not possible_splits

    # Change just the cap's output count to give an actual six-place comparator.
    name, parents, _ = FOLDED[-1]
    real, _ = build(FOLDED[:-1] + ((name, parents, 3),))
    inputs, outputs = real[-1][:3], real[-1][3:]
    true_table = literal.scalar_table(literal.minimal_dual(real), len(literal.incidence(real)[0]))
    cross = [1 + literal.delta(true_table, a, b) for a, b in product(inputs, outputs)]
    assert cross == [6] * 9
    return word, {
        "sites_before_and_after_cap": [len(base) - 1, len(base)], "width_after_cap": width,
        "prior_boundary": sorted(before), "six_bit_bond": sorted(word),
        "nonempty_star_sums_checked": len(star_sums), "sites_after_wiring": len(rows),
        "width_after_wiring": len(holders), "all_six_shared": True, "short_pairs": pairs,
        "exact_pair_K": values, "three_plus_three_splits": len(possible_splits),
        "true_six_place_control": {"inputs": inputs, "outputs": outputs, "cross_K": cross},
    }


def connected_groups(word):
    actions = list(FOLDED + WIRING)
    older = ("G", "H")
    triples = []
    stages = []
    for i in range(1, 5):
        hub = f"K{i}"
        r, s, t = (f"{letter}{i}" for letter in "rst")
        group = tuple(f"{pair}{i}" for pair in ("rs", "rt", "st"))
        actions.append((hub, older, 3))
        actions.extend((site, (hub,), 3) for site in (r, s, t))
        actions.extend((site, pair, 3) for site, pair in zip(group, ((r, s), (r, t), (s, t))))
        actions.append((f"J{i}", (older[0], r), 2))
        triples.append(group)
        older = group[:2]

        rows, names = build(actions)
        holders, adjacent = literal.incidence(rows)
        check_prefix_bond(rows, len(FOLDED) + 1, word)
        assert all(len(holders[b]) == 2 for b in word)
        assert all(connected(adjacent, set(range(len(rows))) - {v}) for v in range(len(rows)))
        marked = []
        for group in triples:
            sites = [names.index(site) for site in group]
            bits = [min(bit for bit in rows[site] if holders[bit] == [site]) for site in sites]
            certificate = literal.marked_permission(rows, bits)
            assert certificate["legal_triple"]
            marked.append(bits)
        assert len(set().union(*marked)) == 3 * len(marked)
        stages.append({"sites": len(rows), "width": len(holders), "simultaneous_marked_triples": marked,
                       "connected_single_site_deletions": len(rows)})
    return stages


def nested_cuts():
    actions = list(FOLDED + WIRING) + [
        ("k", ("G", "H"), 2), ("l", ("G", "H"), 2),
        ("m", ("E", "k"), 2), ("n", ("F", "k"), 2),
    ]
    older = ("m", "n")
    samples = []
    for i in range(5):
        rows, names = build(actions)
        holders, _ = literal.incidence(rows)
        word = boundary(rows, range(len(rows)))
        pairs = [sorted(b for b in rows[names.index(site)] if len(holders[b]) == 1)
                 for site in ("l", *older)]
        assert all(len(pair) == 2 for pair in pairs) and len(word) == 6
        assert set().union(*pairs) == word and all(len(rows[names.index(site)]) == 4 for site in ("l", *older))
        samples.append({"prefix_sites": len(rows), "width": len(holders), "pairs_at_four_place_stars": pairs})
        children = (f"m{i}", f"n{i}")
        actions.extend((child, older, 2) for child in children)
        older = children
    actions.extend((("x", ("l",), 3), ("y", ("l",), 3), ("xy", ("x", "y"), 2)))
    rows, _ = build(actions)
    holders, adjacent = literal.incidence(rows)
    words = [set().union(*sample["pairs_at_four_place_stars"]) for sample in samples]
    common = set.intersection(*words)
    assert len(common) == 2 and all(x & y == common for x, y in combinations(words, 2))
    for sample, word in zip(samples, words):
        check_prefix_bond(rows, sample["prefix_sites"], word)
    touched = set.union(*words)
    for bit in touched:
        assert len(holders[bit]) == 2 and connected(adjacent, range(len(rows)), tuple(holders[bit]))
    return {"frontiers": samples, "final_sites": len(rows), "final_width": len(holders),
            "each_pair_of_frontiers_intersects_in": sorted(common), "bonds_verified_after_wiring": len(words),
            "distinct_shared_nonbridge_bits_verified": len(touched)}


def main():
    word, initial = cuts_and_pair_control()
    return {"initial_cut": initial, "connected_extensions": connected_groups(word), "nested": nested_cuts()}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
