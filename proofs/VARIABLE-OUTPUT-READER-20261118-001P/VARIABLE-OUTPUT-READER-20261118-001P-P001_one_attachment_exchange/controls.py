"""Exact one-attachment comparisons on the live width-31 one-spent family."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys


PROOFS = Path(__file__).resolve().parents[2]
O_ID = "VARIABLE-OUTPUT-READER-20261118-001O"
O_PATH = PROOFS / O_ID / (O_ID + "-P001_one_spent_output")


def load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


O = load("one_exchange_O", O_PATH / "census.py")
T = O.predecessor("table_tools")
N = O.predecessor("inverse_fixtures")


def read_json(name):
    return json.loads((O_PATH / name).read_text())


def names(word):
    return tuple(i for i in range(word.bit_length()) if word & (1 << i))


def bipartition(neighbors, high):
    start = next(i for i in range(len(neighbors)) if i != high)
    colors = {start: 0}
    queue = [start]
    for i in queue:
        for j in sorted(neighbors[i] - {high}):
            color = 1 - colors[i]
            if j not in colors:
                colors[j] = color
                queue.append(j)
            assert colors[j] == color
    assert len(colors) == len(neighbors) - 1
    return colors


@dataclass(slots=True)
class Source:
    rows: tuple
    high: int
    siblings: tuple
    attachments: tuple
    low_owner: dict
    color: dict
    menu: tuple
    spent: int
    third_parents: int
    shrinks: int
    child_outputs_used: int

    @classmethod
    def make(cls, rows):
        rows = tuple(tuple(sorted(row)) for row in rows)
        events = T.replay(rows)
        births = [event for event in events[1:] if len(event["fresh"]) == 3]
        assert len(births) == 4 and len(births[-1]["parents"]) == 3
        high, = (i for i, row in enumerate(rows) if len(row) == 6)
        assert high == births[-1]["site"]
        holders, neighbors = T.incidence(rows)
        siblings = tuple(b for b in births[-1]["fresh"] if len(holders[b]) == 1)
        assert len(siblings) == 2
        spent, = set(births[-1]["fresh"]) - set(siblings)
        child, = set(holders[spent]) - {high}
        attachments = tuple(sorted(set(rows[high]) - set(siblings)))
        low_owner = {b: j for b, users in sorted(holders.items()) if len(ends := set(users) - {high}) == 1
                     for j in ends}
        colors = bipartition(neighbors, high)
        assert len({low_owner[b] for b in attachments}) == 4
        assert len({colors[low_owner[b]] for b in attachments}) == 1
        menu = tuple(T.allowed(rows))
        assert menu
        return cls(rows, high, siblings, attachments, low_owner, colors, menu, spent, len(births[2]["parents"]),
                   sum(len(e["parents"]) == 3 and len(e["fresh"]) == 2 for e in events),
                   sum(len(holders[b]) == 2 for b in events[child]["fresh"]))

    def changed_rows(self, released, added):
        support = tuple(sorted((set(self.rows[self.high]) - {released}) | {added}))
        return self.rows[:self.high] + (support,) + self.rows[self.high + 1:]


def reachable_order(rows):
    """An exact search over incidence prefixes, returning an actual birth order."""
    _, ordinary = T.incidence(rows)
    adjacency = tuple(sum(1 << j for j in ns) for ns in ordinary)
    seed, = (i for i, row in enumerate(rows) if len(row) == 3)
    all_sites = (1 << len(rows)) - 1

    @cache
    def search(selected):
        if selected == all_sites:
            return ()
        for site in names(all_sites ^ selected):
            parents = names(adjacency[site] & selected)
            size = len(parents)
            if not 1 <= size <= 3 or len(rows[site]) - size not in (2, 3):
                continue
            if any(not (adjacency[a] & adjacency[b] & selected) for a, b in combinations(parents, 2)):
                continue
            if size == 3 and adjacency[parents[0]] & adjacency[parents[1]] & adjacency[parents[2]] & selected:
                continue
            suffix = search(selected | (1 << site))
            if suffix is not None:
                return (site, *suffix)
        return None

    tail = search(1 << seed)
    if tail is None:
        return None
    history = tuple(rows[i] for i in (seed, *tail))
    T.replay(history)
    return history


def transpose(width, a, b):
    image = list(range(width))
    image[a], image[b] = b, a
    return tuple(image)


def transport(rows, permutation):
    return tuple(tuple(sorted(permutation[b] for b in row)) for row in rows)


def bond_distance(value):
    return None if value == T.INFINITY else value - 1


def differences(left, right):
    return tuple((a, b, left[a][b], right[a][b]) for a, b in combinations(range(len(left)), 2)
                 if left[a][b] != right[a][b])


def verdict(rows, mark):
    owners, adjacency = T.incidence(rows)
    shared = tuple(b for b in mark if len(owners[b]) != 1)
    if shared:
        return {"verdict": "spent_input", "spent": shared}
    parents = tuple(owners[b][0] for b in mark)
    if len(set(parents)) != 3:
        return {"verdict": "repeated_holder", "holders": parents}
    witnesses = tuple(tuple(sorted(adjacency[a] & adjacency[b])) for a, b in combinations(parents, 2))
    all_three = tuple(sorted(set.intersection(*(adjacency[a] for a in parents))))
    state = "legal" if all(witnesses) and not all_three else "missing_pair_witness" if not all(witnesses) else "common_witness"
    return {"verdict": state, "holders": parents, "pair_witnesses": witnesses, "common_witnesses": all_three}


def measured_comparison(left_rows, right_rows, tables, verify=False):
    left, right = tables
    width = len(left)
    delta = differences(left, right)
    source_menu, rival_menu = set(T.allowed(left_rows)), set(T.allowed(right_rows))
    lost, gained = sorted(source_menu - rival_menu), sorted(rival_menu - source_menu)
    result = {
        "width": width, "pairs": width * (width - 1) // 2,
        "left_history": reachable_order(left_rows), "right_history": reachable_order(right_rows),
        "left_supports": left_rows, "right_supports": right_rows,
        "left_menu": sorted(source_menu), "right_menu": sorted(rival_menu),
        "first_lost": {"mark": lost[0], **verdict(right_rows, lost[0])} if lost else None,
        "first_gained": {"mark": gained[0], **verdict(left_rows, gained[0])} if gained else None,
        "changed_entries": {"D4": sum(min(a, b) <= 5 for _, _, a, b in delta),
                            "D5": sum(min(a, b) <= 6 for _, _, a, b in delta), "exact": len(delta)},
        "differing_exact_pair_entries": [[(a, b), bond_distance(k), bond_distance(j)] for a, b, k, j in delta],
    }
    if verify:
        for rows, table in ((left_rows, left), (right_rows, right)):
            direct = T.parity_minima(rows, (2,))[2]
            assert all(direct.get((a, b), T.INFINITY) == table[a][b] for a, b in combinations(range(width), 2))
        result["two_independent_exact_methods"] = True
    return result


def keep_best(examples, label, key, item):
    if label not in examples or key < examples[label][0]:
        examples[label] = (key, item)


def six_shores(source, added):
    """All size-six shores containing the high site and the new bit's holder."""
    cuts = [0]
    for star in T.masks(source.rows):
        cuts.extend(word ^ star for word in cuts[:])
    required = (1 << source.high) | (1 << source.low_owner[added])
    result = []
    for shore, cut in enumerate(cuts):
        if shore & required == required and cut.bit_count() == 6:
            boundary = names(cut)
            assert added in boundary and set(source.siblings) <= set(boundary)
            result.append({"site_count": shore.bit_count(), "boundary": boundary,
                           "true_attachments_on_boundary": sorted(set(boundary) & set(source.attachments))})
    assert result
    return result


def describe_near(items, sources, matrices, measured):
    grouped = defaultdict(list)
    for index, released, added in items:
        grouped[index, added].append(released)
    counts = Counter()
    records = []
    for (index, added), releases in sorted(grouped.items()):
        source, table = sources[index], matrices[index]
        live = tuple(sorted(set(source.low_owner) - set(source.attachments) | set(source.siblings)))
        cuts = six_shores(source, added)
        only_whole = len(cuts) == 1 and cuts[0]["site_count"] == len(source.rows)
        counts["source_and_added_bit_pairs"] += 1
        counts["sole_six_shore_is_whole_source"] += only_whole
        alternatives = []
        for released in releases:
            rival = measured[index, released, added]
            stats = differences(table, rival)
            rows = source.changed_rows(released, added)
            actual = reachable_order(rows)
            same = source.low_owner[released] == source.low_owner[added]
            suffix = "same_holder" if same else "different_holder"
            changed_menu = set(T.allowed(rows)) != set(source.menu)
            counts[suffix + "_lawful"] += actual is not None
            counts[suffix + "_lawful_opposition"] += actual is not None and changed_menu
            alternatives.append({"released": released, "released_was_spent_output": released == source.spent,
                                 "same_holder": same, "lawful": actual is not None,
                                 "candidate_menu_differs": changed_menu, "D4_changed": sum(min(a,b)<=5 for _,_,a,b in stats),
                                 "D5_changed": sum(min(a,b)<=6 for _,_,a,b in stats), "full_changed": len(stats)})
        records.append({"source_index": index, "history": source.rows, "menu": source.menu, "siblings": source.siblings,
                        "attachments": source.attachments, "source_loose": live, "added": added,
                        "low_holder": source.low_owner[added], "low_holder_support": source.rows[source.low_owner[added]],
                        "K_to_each_true_attachment": [(i, table[i][added]) for i in source.attachments],
                        "six_shores": cuts, "comparisons": alternatives})
    return {"counts": dict(counts), "source_and_added_bit_records": records}


def grade_many(sources, matrices, binary):
    counts = {label: Counter() for label in ("same_holder", "different_holder")}
    f_profile = defaultdict(Counter)
    local_profiles = defaultdict(Counter)
    by_source = defaultdict(Counter)
    same_maps = Counter()
    for_measurement, sibling_close, examples = [], [], {}
    eligible_different = []
    max_siblings = 0
    for index, (source, table) in enumerate(zip(sources, matrices, strict=True)):
        a, b = source.siblings
        assert table[a][b] == 6 and all(table[a][i] == table[b][i] >= 6 for i in range(len(table)) if i not in (a, b))
        profile = by_source[source.third_parents, source.shrinks, source.child_outputs_used]
        profile["sources"] += 1
        max_siblings = max(max_siblings, sum(d == 6 for d in table[a]) + 1)
        for released in source.attachments:
            retained = tuple(i for i in source.attachments if i != released)
            old_holder = source.low_owner[released]
            for added, holder in source.low_owner.items():
                if added in source.attachments:
                    continue
                label = "same_holder" if holder == old_holder else "different_holder"
                stats = counts[label]
                stats["offered"] += 1
                item = index, released, added
                if label == "same_holder":
                    # This is literally the source under a transposition that fixes all low supports.
                    moved = [min(table[released][i], table[added][i]) for i in range(len(table))
                             if i not in (released, added) and table[released][i] != table[added][i]]
                    menu_changes = any(added in mark for mark in source.menu)
                    if menu_changes:
                        same_maps["opposing_menu_under_identity"] += 1
                    for name, matches in (("exact", not moved), ("D5", not any(v <= 6 for v in moved)),
                                          ("D4", not any(v <= 5 for v in moved))):
                        if matches:
                            same_maps[name + "_entrywise_equal"] += 1
                            same_maps[name + "_opposing_menu"] += menu_changes
                            if name == "D4" and menu_changes:
                                keep_best(examples, "same_holder_D4_opposition", (index, released, added), item)
                if holder in {source.low_owner[i] for i in retained}:
                    continue
                stats["four_distinct_holders"] += 1
                if source.color[holder] != source.color[old_holder]:
                    continue
                stats["one_color"] += 1
                f = table[a][added]
                other = tuple(sorted(table[i][added] for i in retained))
                f_profile[label][f] += 1
                if f == 6:
                    stats["both_siblings_close"] += 1
                    local_profiles[label][other] += 1
                    profile[label + "_both_siblings_close"] += 1
                    sibling_close.append(item)
                missing = (f > 6) + sum(k > 6 for k in other)
                key = (missing, max((f, *other)), sum((f, *other)), index, released, added)
                keep_best(examples, label + "_closest_local_readings",
                          key, item)
                if label == "different_holder":
                    eligible_different.append((key, item))
                if missing:
                    continue
                stats["all_three_retained_close"] += 1
                profile[label + "_local_survivors"] += 1
                for_measurement.append(item)

    if len(matrices) > 1:
        # Among the closest candidates, look for a literal alternative birth order.
        # This diagnostic does not enter the exhaustive local exclusions.
        for key, item in sorted(eligible_different)[:128]:
            index, released, added = item
            source = sources[index]
            rows = source.changed_rows(released, added)
            if set(T.allowed(rows)) != set(source.menu) and reachable_order(rows):
                examples["different_holder_reachable_opposition_control"] = (key, item)
                break
    selected = dict.fromkeys((*sibling_close, *(item for _, item in examples.values())))
    distinct_rows = [sources[i].changed_rows(a, b) for i, a, b in selected]
    measured = dict(zip(selected, T.all_tables(binary, distinct_rows), strict=True))
    reports = []
    for item in for_measurement:
        index, released, added = item
        source, table, rival = sources[index], matrices[index], measured[item]
        rows = source.changed_rows(released, added)
        label = "same_holder" if source.low_owner[released] == source.low_owner[added] else "different_holder"
        exact = table == rival
        clipped = not any(min(a, b) <= 6 for _, _, a, b in differences(table, rival))
        actual = reachable_order(rows)
        after_menu = set(T.allowed(rows))
        stats = counts[label]
        stats["D5_full_matrix_matches"] += clipped
        stats["exact_full_matrix_matches"] += exact
        stats["lawful_local_survivors"] += actual is not None
        stats["local_menus_differ"] += set(source.menu) != after_menu
        stats["lawful_local_menus_differ"] += actual is not None and set(source.menu) != after_menu
        stats["reachable_D5_matches"] += clipped and actual is not None
        stats["reachable_exact_matches"] += exact and actual is not None
        stats["reachable_D5_opposition"] += clipped and actual is not None and set(source.menu) != after_menu
        stats["reachable_exact_opposition"] += exact and actual is not None and set(source.menu) != after_menu
        if exact or len(reports) < 8:
            reports.append({"candidate": item, "comparison": measured_comparison(source.rows, rows, (table, rival), verify=True)})

    controls = {}
    for label, (_, item) in sorted(examples.items()):
        index, released, added = item
        source = sources[index]
        controls[label] = {"candidate": item,
                           "K_to_siblings": tuple(matrices[index][a][added] for a in source.siblings),
                           "retained_K": [(i, matrices[index][i][added]) for i in source.attachments if i != released],
                           "comparison": measured_comparison(source.rows, source.changed_rows(released, added),
                                                             (matrices[index], measured[item]), verify=True)}
    for stats in counts.values():
        for name in ("offered", "four_distinct_holders", "one_color", "both_siblings_close", "all_three_retained_close",
                     "D5_full_matrix_matches", "exact_full_matrix_matches", "reachable_D5_matches", "reachable_exact_matches"):
            stats.setdefault(name, 0)
    for cutoff in ("D4", "D5", "exact"):
        same_maps.setdefault(cutoff + "_entrywise_equal", 0)
        same_maps.setdefault(cutoff + "_opposing_menu", 0)
    return {
        "necessary_tests_in_order": ["offered", "four_distinct_holders", "one_color", "both_siblings_close",
                                     "all_three_retained_close"],
        "counts": {key: dict(value) for key, value in counts.items()},
        "K_to_added_bit_from_siblings_after_color_test": {key: sorted(value.items()) for key, value in sorted(f_profile.items())},
        "retained_K_multisets_after_sibling_test": {key: sorted(value.items()) for key, value in sorted(local_profiles.items())},
        "maximum_closed_D5_sibling_row_size": max_siblings,
        "by_source_third_parents_shrinks_child_outputs_used": [{"profile": key, **value} for key, value in sorted(by_source.items())],
        "same_holder_exact_transposition_check_before_any_distance_filters": dict(same_maps),
        "every_exchange_with_two_close_siblings": describe_near(sibling_close, sources, matrices, measured),
        "local_survivors_examples": reports, "closest_named_tests": controls,
    }


def census_roster():
    target = 13
    layer = tuple(O.Tagged(shape) for shape in O.old.starters())
    stages = []
    sources = []
    for sites in range(4, target + 1):
        layer = O.next_layer(layer, target)
        classes = O.physical_classes(layer)
        if sites == 12:
            assert len(classes) == 2854
        if sites < 9:
            continue
        counts = Counter(physical=len(classes))
        for members in classes:
            shape = members[0][0].shape
            if not any(shape.groups((3,))):
                continue
            counts["live"] += 1
            if sum(edge.bit_count() + l == 6 for edge, l in zip(shape.neighbors, shape.loose, strict=True)) != 1:
                counts["live_with_second_high"] += 1
                continue
            counts["live_sole_high"] += 1
            if sites == target:
                sources.append(Source.make(row for _, row in shape.history()))
        stages.append({"width": 2 * sites + 5, **counts})
    assert stages[-2]["live"] == 895 and len(sources) == stages[-1]["live_sole_high"]
    return stages, sources


def literal_controls(binary):
    o_named = read_json("controls.json")
    residual = read_json("residual.json")
    prepared = residual["shortest_named_cases_with_a_spent_child_output"]
    chosen = prepared[residual["selected_fixture_index"]]
    one = next(case for case in prepared if case["width"] == 31 and case["child_outputs_used"] == 1)
    o_census = read_json("census.json")["comparison_examples"]["D4"]
    left23 = tuple(tuple(row) for row in o_census["source_replay"]["supports"])
    right23 = transport(left23, o_census["permutation"])
    assert left23[:-2] == right23[:-2] and sum(a != b for a, b in zip(left23, right23, strict=True)) == 1
    matched = {
        "O23_sharp_one_exchange": (left23, right23),
        "N31_equal_exact_unspent": (N.LIVE, N.OTHER),
        "N31_same_spending_child_gives_width33": ((*N.LIVE, (17,28,31,32)), (*N.OTHER, (17,28,31,32))),
    }
    results = {key: measured_comparison(left, right, T.all_tables(binary, (left, right)), verify=True)
               for key, (left, right) in matched.items()}
    a, b, c = results.values()
    assert a["left_history"] and a["right_history"] and a["first_lost"]
    assert a["changed_entries"] == {"D4": 0, "D5": 10, "exact": 16}
    assert b["left_history"] and b["right_history"] and b["changed_entries"]["exact"] == 0
    assert b["left_menu"] == b["right_menu"] == [(17,25,28), (17,25,29), (17,25,30)]
    state = {24,25,27}
    assert all(len(state.intersection(row)) % 2 == 0 for row in N.LIVE)
    assert any(len(state.intersection(row)) % 2 for row in N.OTHER)
    b["allowed_on_left_only_at_ones"] = sorted(state)
    assert c["left_history"] and c["right_history"] and not (c["left_menu"] or c["right_menu"])
    assert c["changed_entries"] == {"D4": 0, "D5": 4, "exact": 4}

    rows25 = o_named["fourth_holds_surviving_mark"]["history"]
    samples = {"O25_live_sibling_still_holds": rows25,
               "O31_two_shrinks_both_child_outputs_used": chosen["junction_supports"],
               "O31_two_shrinks_one_child_output_used": one["junction_supports"]}
    for label, rows in samples.items():
        source = Source.make(rows)
        table, = T.all_tables(binary, (source.rows,))
        grade = grade_many([source], [table], binary)
        direct = T.parity_minima(source.rows, (2,))[2]
        assert all(table[a][b] == k for (a, b), k in direct.items()) and len(direct) == len(table) * (len(table) - 1) // 2
        results[label] = {"history": source.rows, "menu": source.menu, "high": source.high,
                          "siblings": source.siblings, "all_swaps": grade}
    return results


def run(binary):
    named = literal_controls(binary)
    print("Named controls passed; enumerating live width-31 sources.", file=sys.stderr, flush=True)
    roster, sources = census_roster()
    print(f"Measuring {len(sources)} live width-31 sources with one six-place site.", file=sys.stderr, flush=True)
    rows = [source.rows for source in sources]
    matrices = T.all_tables(binary, rows)
    return {"freeze": "59c7215e0", "complete_width_31_roster": roster, "named_controls": named,
            "width_31_one_exchange": grade_many(sources, matrices, binary)}


if __name__ == "__main__":
    with TemporaryDirectory(prefix="one-attachment-exchange-") as scratch:
        binary = T.compiler(Path(scratch) / "bonds")
        result = run(binary)
    print(json.dumps(result, indent=2))
