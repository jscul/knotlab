"""Extract the shortest live two-shrink controls from the O formation closure."""

from collections import Counter
from functools import cache
from itertools import chain
import json

import census
import frontier as F


def formation():
    prior = F.N.close_prefixes()
    roots, _ = F.all_starts(prior)
    result = F.closure(roots)

    @cache
    def depth(node):
        if node in result["roots"]:
            old, _ = result["roots"][node]
            return prior[2][old] + 1
        return depth(result["linked"][node][0]) + 1

    tally = Counter()
    shortest = {}
    for node in chain(result["roots"], result["linked"]):
        third, spend, state = node
        if third not in (1, 2) or spend != 2:
            continue
        shrinks = 10 - third - sum(state.frontier.loose)
        if shrinks < 2:
            continue
        roles = F.menu_roles(state)
        if not roles:
            continue
        child = state.child
        used = 2 if child == F.OTHER else 2 - state.frontier.loose[child]
        holds = bool(roles["fourth_holder"])
        key = third, shrinks, used, holds
        tally[key] += 1
        if key not in shortest or depth(node) < depth(shortest[key]):
            shortest[key] = node

    cases = []
    for (third, shrinks, used, holds), node in sorted(shortest.items()):
        if not used:
            continue
        previous, move = result["linked"][node]
        rows, fourth, child = F.replay(F.Sample(previous, move, depth(node), ()), result, prior)
        description = F.describe(rows, fourth, child)
        assert len(description["shrinking_sites"]) == shrinks
        assert len(description["spent_spending_child_outputs"]) == used
        assert (child not in description["shrinking_sites"]) and description["current"]
        events = F.T.replay(rows)
        assert len(events[child]["consumes"]) == len(events[child]["fresh"]) == 2
        loose_siblings = tuple(bit for bit in events[fourth]["fresh"] if bit != description["spent_fourth_bit"])
        direct = tuple(mark for mark in description["current"] if set(mark).intersection(loose_siblings))
        assert bool(direct) == holds
        cases.append({
            "third_parents": third, "shrinks": shrinks, "child_outputs_used": used,
            "fourth_siblings": loose_siblings, "marks_using_fourth_sibling": direct, **description,
        })
    assert sum(tally.values()) == sum(
        stats["union"] for (third, p, shrinks), stats in result["distinct_positive"].items()
        if third in (1, 2) and p == 2 and shrinks >= 2)
    return {
        "exact_positive_formation_counts": [
            {"third_parents": t, "shrinks": s, "child_outputs_used": c, "fourth_holds_a_mark": h, "states": count}
            for (t, s, c, h), count in sorted(tally.items())
        ],
        "shortest_named_cases_with_a_spent_child_output": cases,
    }


def scalar_certificate(case):
    n = census.N
    inverse = census.predecessor("inverse_fixtures")
    rows = case["junction_supports"]
    source = n.two_method_record(n.old.previous.named(rows))
    width, sites = source.fixture.width, source.fixture.sites
    table = census.record_table(source)
    x, y = case["fourth_siblings"]

    def get(i, j):
        return table[tuple(sorted((i, j)))]

    row_minima = tuple(min(get(s, i) for i in range(width) if s != i) for s in (x, y))
    assert row_minima == (6, 6)
    assert all(get(x, i) == get(y, i) for i in range(width) if i not in (x, y))
    size_six = tuple(i for i in range(width) if i == x or get(x, i) == 6)
    rank = n.rank_certificate(source)
    assert rank["short_rank_checks"][-1]["forces_every_matching_rival_equation_space"]

    def expected(renaming):
        def image(group):
            return tuple(sorted(renaming[b] for b in group))

        return {"supports": sorted(image(row) for row in rows),
                "menu": tuple(sorted(image(mark) for mark in case["current"]))}

    readout = inverse.read(table, width, sites)
    goal = expected(tuple(range(width)))
    assert readout["through_D5"] == readout["exact"] == [goal]
    rename = tuple((3 * i + 7) % width for i in range(width))
    assert len(set(rename)) == width
    renamed_table = {tuple(sorted((rename[i], rename[j]))): k for (i, j), k in table.items()}
    renamed = inverse.read(renamed_table, width, sites)
    assert renamed["through_D5"] == renamed["exact"] == [expected(rename)]
    mark = next(iter(case["marks_using_fourth_sibling"]))
    literal = n.mark_status(source, mark)
    assert literal["verdict"] == "legal"
    return {
        "width": width, "checked_pair_entries": len(table),
        "K_upper_triangle_hex": bytes(table.values()).hex(),
        "sibling_row_minima_K": row_minima, "closed_neighborhood_S": size_six, "S_cardinality": len(size_six),
        "meets_one_spent_image_lower_bound_11": len(size_six) >= 11,
        "chosen_mark": mark, "chosen_mark_literal_grading": literal,
        "rank_certificate": rank, "physical_rivals": readout, "simultaneous_check_renaming": rename,
    }


def run():
    evidence = formation()
    fixtures = evidence["shortest_named_cases_with_a_spent_child_output"]
    selected = min((i for i, row in enumerate(fixtures) if row["marks_using_fourth_sibling"]),
                   key=lambda i: (-fixtures[i]["child_outputs_used"], fixtures[i]["width"]))
    return {**evidence, "selected_fixture_index": selected, "selected_scalar_certificate": scalar_certificate(fixtures[selected])}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
