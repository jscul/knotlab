"""Compare named triple menus immediately after the exceptional birth."""

from collections import Counter, defaultdict, deque
from itertools import chain, combinations, product
import json

from closure import J, OLD, RULE, NOT_YET, State, actual_triples, original_control


def examine():
    representatives = {J.literal_snapshot(rows)[0]: rows for rows in J.initial_histories()}
    queue = deque(representatives)
    arcs = {}
    counts = defaultdict(Counter)
    adverse_prefixes = []
    while queue:
        front = queue.popleft()
        rows = representatives[front]
        same, sites, loose = J.literal_snapshot(rows)
        assert same == front
        allowed = OLD.verify_literal_moves(rows, front, sites, loose)
        slots = sum(front.loose)
        width = 1 + max(chain.from_iterable(rows))
        fresh = (width, width + 1, width + 2)
        menus = {}
        links = []
        support = dict(enumerate(rows))
        for parents in sorted(allowed):
            if len(parents) == 3:
                for inputs in product(*(loose[sites[i]] for i in parents)):
                    assert RULE.legal_local_move(support, inputs, OLD.FRESH_FOR_PARENT_TEST)
                    marked = tuple(sorted(inputs))
                    after = (*rows, (*marked, *fresh))
                    possible = frozenset(actual_triples(after))
                    assert marked not in possible
                    menus[marked] = possible
            if len(parents) < 2:
                continue
            following = J.step(front, parents, 2)
            replayed = J.advance(rows, tuple(sites[i] for i in parents), 2)
            assert J.literal_snapshot(replayed)[0] == following
            if following not in representatives:
                representatives[following] = replayed
                queue.append(following)
            links.append((parents, 2, State(NOT_YET, following)))
        arcs[State(NOT_YET, front)] = tuple(links)
        number = counts[slots]
        number.update(frontiers=1, frontiers_with_an_exceptional_birth=bool(menus),
                      named_input_sets=len(menus), named_input_sets_with_live_new_menu=sum(map(bool, menus.values())))
        differences = []
        for first, second in combinations(sorted(menus), 2):
            number["pairs"] += 1
            if menus[first] == menus[second]:
                continue
            number["different_menus"] += 1
            differences.append({
                "left_input": first, "right_input": second,
                "left_only_legal": tuple(sorted(menus[first] - menus[second])),
                "right_only_legal": tuple(sorted(menus[second] - menus[first])),
            })
        if differences:
            adverse_prefixes.append({
                "loose_bits_at_old_prefix": slots, "prefix_width": width, "old_supports": rows,
                "same_fresh_names": fresh, "adverse_input_pairs": differences,
            })
    assert counts[6]["named_input_sets"] and counts[6]["named_input_sets_with_live_new_menu"] == 0
    assert counts[7]["different_menus"] > 0
    return {
        "archived_predecessor_fixed_point": original_control(arcs),
        "by_number_of_old_loose_bits": {
            slots: {label: result[label] for label in (
                "frontiers", "frontiers_with_an_exceptional_birth", "named_input_sets",
                "named_input_sets_with_live_new_menu", "pairs", "different_menus",
            )}
            for slots, result in sorted(counts.items())
        },
        "prefixes_with_a_named_menu_disagreement": adverse_prefixes,
    }


if __name__ == "__main__":
    print(json.dumps(examine(), indent=2))
