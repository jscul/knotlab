"""Check whether a full-table symmetry losing a parity equation survives with legal triples present."""

from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

import check_continuation as continuation


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def eligible_bits_by_parent(supports, gluing):
    holders, _ = gluing.incidence(supports)
    loose = {}
    for bit, parents in sorted(holders.items()):
        if len(parents) == 1:
            loose.setdefault(parents[0], []).append(bit)
    return loose


def extend(source, second_attachments, gluing):
    supports = list(source)
    source_parent_groups = [(7, 8)] * second_attachments + [(8,)] * (3 - second_attachments)
    for parents in (*source_parent_groups, (9, 10), (9, 11), (10, 11)):
        loose = eligible_bits_by_parent(supports, gluing)
        old = [loose[parent][0] for parent in parents]
        first = max(max(star) for star in supports) + 1
        supports.append(tuple([*old, first, first + 1]))
    return tuple(supports)


def verify(source, second_attachments, scout, api, rules, gluing):
    supports = extend(source, second_attachments, gluing)
    history = gluing.replay(supports)
    width = 32
    pairs = list(combinations(range(width), 2))
    bonds = continuation.cut_supports(gluing, supports)
    matrix = continuation.dense(gluing.scalar_table(bonds, width), width)
    separators, differences = continuation.separator_components(matrix, supports)
    assert not differences and not separators

    perm = list(range(width))
    perm[13], perm[14] = perm[14], perm[13]
    changed_pairs = [(a, b, matrix[a][b], matrix[perm[a]][perm[b]]) for a, b in pairs
                     if matrix[a][b] != matrix[perm[a]][perm[b]]]
    lost = tuple(sorted(perm[x] for x in source[-1]))
    dual = scout.parity_span(dict(enumerate(supports)))
    assert scout.mask(source[-1]) in dual and scout.mask(lost) not in dual

    menu = frozenset(action for action in scout.actual_menu(rules, dict(enumerate(supports))) if len(action) == 3)
    assert len(menu) == 8
    group_order, _, generators = api.Quotient.make(matrix).automorphisms()
    for generator in generators:
        assert api.disagreement(matrix, matrix, generator) is None
        assert api.transported(menu, generator) == menu
    # The original and retained tables agree on all labels because the separator list is empty.
    assert len(changed_pairs) == (0, 12, 20)[second_attachments]
    return {
        "width": width, "parent_sets_with_both_7_and_8": second_attachments,
        "history": history, "junction_supports": supports,
        "true_triples": sorted(tuple(sorted(t)) for t in menu),
        "original_and_retained_entries_compared": len(pairs),
        "separating_distinctions": sorted(separators),
        "scalar_automorphism_group_order": group_order,
        "number_of_group_generators_checked": len(generators),
        "menu_changing_generators": 0,
        "transposition": [13, 14], "pairs_changed_by_transposition": changed_pairs,
        "true_parity_equation": source[-1], "image_outside_true_dual": lost,
        "all_self_maps_preserve_triples": True,
    }


def confined_co_parents(holders, adjacent, loose_mark):
    """Certify that a holder's last loose bit cannot belong to a future triple."""
    u, = holders[loose_mark]
    available = {parents[0] for parents in holders.values() if len(parents) == 1}
    if sum(parents == [u] for parents in holders.values()) != 1:
        return False
    pending = available - {u}
    while pending:
        start = pending.pop()
        component = {start}
        queue = [start]
        while queue:
            v = queue.pop()
            other = {z for z in pending if z in adjacent[v] or adjacent[v] & adjacent[z]}
            pending -= other
            component.update(other)
            queue.extend(other)
        candidates = {p for p in component if adjacent[p] & adjacent[u]}
        open_neighbors = adjacent[u] & component
        if open_neighbors:
            if len(open_neighbors) != 1:
                return False
            common, = open_neighbors
            if any(common not in adjacent[p] for p in candidates):
                return False
    return True


def grade_frozen_holders(scout, api, rules, gluing):
    span_data = json.loads((HERE / "span_controls.json").read_text())
    cases = span_data["full_table_rank_one_extension_controls"]["individual_cases"]
    checked = []
    for case in cases:
        if case["reachable_labeled_states"] <= 1:
            continue
        fixture = scout.Fixture((), (3,), ())
        for parents, count in case["source_history"]:
            fixture = fixture.successor(tuple(parents), count)
        supports = tuple(fixture.checks().values())
        assert not any(len(choice) == 3 for choice in scout.actual_menu(rules, fixture.checks()))
        holders, adjacent = gluing.incidence(supports)
        bonds = continuation.cut_supports(gluing, supports)
        matrix = continuation.dense(gluing.scalar_table(bonds, 20), 20)
        dual = scout.parity_span(fixture.checks())
        for perm in api.Quotient.make(matrix).automorphisms()[2]:
            if all(scout.mask(perm[x] for x in star) in dual for star in supports):
                continue
            moved = [x for x in range(20) if perm[x] != x]
            assert len(moved) == 2 and sorted(len(holders[x]) for x in moved) == [1, 2]
            shared, = (x for x in moved if len(holders[x]) == 2)
            loose, = (x for x in moved if len(holders[x]) == 1)
            assert holders[loose][0] in holders[shared]
            checked.append({"source": case["case_id"], "loose": loose, "shared": shared,
                            "ineligible_in_all_continuations_by_component_test":
                                confined_co_parents(holders, adjacent, loose)})
    successes = sum(v["ineligible_in_all_continuations_by_component_test"] for v in checked)
    assert len(checked) == 32 and successes == 18
    return {"state_changing_generators": len(checked), "excluded_at_all_depths": successes,
            "outside_this_sufficient_test": len(checked) - successes, "cases": checked}


def main():
    original = ((0, 1, 2), (0, 3, 5), (1, 4, 7), (2, 6, 8), (3, 4, 9, 11),
                (5, 6, 10, 12), (7, 8, 13, 14), (9, 10, 15, 16), (11, 12, 13, 17, 18, 19))
    populations, api, gluing = (continuation.load(ROOT, *entry) for entry in continuation.SOURCES)
    scout, _, rules = populations.inherited()
    gluing.replay(original)
    report = {
        "continuation_checker_sha256": sha256(Path(continuation.__file__).read_bytes()).hexdigest(),
        "source_supports": original,
        "frozen_holder_certificates": grade_frozen_holders(scout, api, rules, gluing),
        "completions": [verify(original, count, scout, api, rules, gluing) for count in range(3)],
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

