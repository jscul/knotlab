"""Matched physical relay edits under the two ordinary knot laws."""

from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "mediator.json"
ARCHIVE = ROOT / "experiments/GENERATORS-20261120-001A/GENERATORS-20261120-001A-E001_generators"
sys.path.insert(0, str(ARCHIVE))
import fixtures as ordinary


def source(d, right_open, split=(1, 2), extra=None):
    meetings = [(p, d + 1 + step) for step in range(d)
                for p, amount in zip((step, step + 1), split, strict=True) for _ in range(amount)]
    supplies = [2] * d + [right_open]
    for knot, amount in (extra or {}).items():
        supplies[knot] += amount
    return ordinary.source_from(meetings, supplies + [0] * d)


def add_distinction(rows, at):
    distinction = 1 + max(x for row in rows for x in row)
    edited = tuple((*row, distinction) if k in at else row for k, row in enumerate(rows))
    return edited, {"new_distinction": distinction, "holders": list(at)}


def interval_cells(d, size, right_ray, twig):
    upper = d if right_ray else d - size + 1
    shapes = {(first, first + size - 1, False) for first in range(1 - size, upper + 1)}
    if twig is not None and size >= 2:
        assert right_ray
        shapes.update((first, first + size - 2, True) for first in range(twig - size + 2, twig + 1))
    return shapes


def interval_parents(shape, d, twig):
    left, right, attached = shape
    result = {(left, right, False)} if attached else set()
    for first, last in ((left + 1, right), (left, right - 1)):
        if first <= last and first <= d and last >= 0 and (not attached or first <= twig <= last):
            result.add((first, last, attached))
    return result


@dataclass
class History:
    frames: list
    born: list
    replay: dict


def grow(rows, law, size_limit):
    ordinary.certify_source(rows, law)
    frames, layers = ordinary.trajectory(rows, law, size_limit - 1)
    assert len(frames) == size_limit
    born = [dict()] + [{b.knot: b for b in layer} for layer, _ in layers]
    replay = {tag: ordinary.fixed_map_replay(rows, layers, law, reverse)
              for tag, reverse in (("first_ready", False), ("last_ready", True))}
    return History(frames, born, replay)


def match_intervals(history, d, *, right_ray, twig=None):
    """Match the literal births to independent one-point deletions and extensions."""
    maps = [{(p, p, False): p for p in range(d + 1)}]
    for size, born in enumerate(history.born[1:], 2):
        model = interval_cells(d, size, right_ray, twig)
        forecast = Counter(p for c in interval_cells(d, size + 1, right_ray, twig)
                           for p in interval_parents(c, d, twig))
        actual = {frozenset(b.parents): b for b in born.values()}
        assert len(actual) == len(born)
        mapping = {}
        for c in sorted(model):
            group = frozenset(maps[-1][p] for p in interval_parents(c, d, twig))
            b = actual[group]
            assert forecast[c] == len(b.fresh) >= max(1, 3 - len(group))
            mapping[c] = b.knot
        assert set(mapping.values()) == set(born)
        maps.append(mapping)
    return maps


def live_read(rows):
    _, shared, loose = ordinary.incidence(rows)
    witnesses, graph = ordinary.witnessed_end(shared, loose)
    return loose, witnesses, graph


def original_end_roles(rows, law):
    """Read the two original ends using physical meeting multiplicities."""
    anchors, parents, _, peeled = ordinary.peel(rows, law)
    old = sorted(anchors)
    old_rows = tuple(rows[k] for k in old)
    _, shared, loose = ordinary.incidence(old_rows)
    _, end = ordinary.witnessed_end(shared, loose)
    endpoints = []
    for k in end:
        if end.degree[k] == 1:
            witnesses = set(shared[k]) - loose.keys()
            assert len(witnesses) == 1
            holder = witnesses.pop()
            thickness = len(set(old_rows[holder]) & set(old_rows[k]))
            endpoints.append((thickness, old[k]))
    assert len(endpoints) == 2 and endpoints[0][0] != endpoints[1][0]
    return tuple(k for _, k in sorted(endpoints)), parents, peeled


def check_roles(history, d, law):
    parents = {}
    records = []
    for age, (frame, born) in enumerate(zip(history.frames, history.born, strict=True)):
        parents.update((k, frozenset(b.parents)) for k, b in born.items())
        roles, observed, depth = original_end_roles(frame, law)
        assert roles == (0, d) and observed == parents and depth == age
        changed, inverse = ordinary.rename(frame, 20261120790 + age)
        relabelled, mapped, depth_r = original_end_roles(changed, law)
        assert tuple(inverse[k] for k in relabelled) == roles and depth_r == depth
        assert {inverse[k]: frozenset(inverse[p] for p in row) for k, row in mapped.items()} == parents
        loose, _, graph = live_read(frame)
        loose_r, _, graph_r = live_read(changed)
        profile = sorted(len(loose[k]) for k in graph if graph.degree[k] == 1)
        assert profile == sorted(len(loose_r[k]) for k in graph_r if graph_r.degree[k] == 1)
        assert nx.is_connected(graph)
        records.append(profile)
    return records


def child_offers(history, levels, age, parent):
    id_to_shape = {k: shape for shape, k in levels[age].items()}
    return sorted((tuple(sorted(id_to_shape[p] for p in b.parents)), len(b.fresh))
                  for b in history.born[age + 1].values() if parent in b.parents)


def projected_end(read, mapping, root, radius):
    loose, witnesses, graph = read
    ball = set(nx.single_source_shortest_path_length(graph, root, cutoff=radius))
    shapes = {k: shape for shape, k in mapping.items()}
    return ({shapes[k]: len(loose[k]) for k in ball},
            Counter(frozenset(shapes[k] for k in group & ball)
                    for group in witnesses if len(group & ball) >= 2))


def ancestry(history, d):
    """Grade actual formation, marking the original sources and the launches separately."""
    bit = {0: 1, d: 2}
    originals = bit.copy()
    flags, strict_a, strict_b = {}, set(), set()
    records = []
    for size, level in enumerate(history.born[1:], 2):
        if size == 2:
            for k, b in level.items():
                if b.parents in ((0,), (d,)):
                    flags[k] = bit[b.parents[0]]
            a = {k for k, status in flags.items() if status == 1}
            b = {k for k, status in flags.items() if status == 2}
            assert len(a) == 1 and len(b) <= 1
            direct, pure_and_descendant = [], []
        else:
            a, b = set(), set()
            direct, pure_and_descendant = [], []
            for key, born in level.items():
                operands = set(born.parents)
                flag = 0
                for p in operands:
                    flag |= flags.get(p, 0)
                flags[key] = flag
                if operands <= strict_a:
                    a.add(key)
                if operands <= strict_b:
                    b.add(key)
                if operands & strict_a and operands & strict_b:
                    direct.append(key)
                if operands & strict_a and any(flags.get(p, 0) & 2 for p in operands):
                    pure_and_descendant.append(key)
        new_originals = {}
        for k, born in level.items():
            state = 0
            for p in born.parents:
                state |= originals.get(p, 0)
            new_originals[k] = state
        originals.update(new_originals)
        strict_a, strict_b = a, b
        mixed = {k for k in level if flags.get(k, 0) == 3}
        records.append({"size": size, "mixed": mixed, "passive_both_originals": sum(
            value == 3 for value in new_originals.values()), "pure_a": a, "pure_b": b, "direct": direct,
                        "pure_A_and_B_descendant": pure_and_descendant,
                        "a_inclusive": {k for k in level if flags.get(k, 0) & 1},
                        "b_inclusive": {k for k in level if flags.get(k, 0) & 2}})
    return records, flags


def physical_birth(history, levels, size, cell):
    k = levels[size - 1][cell]
    prior = {v: shape for shape, v in levels[size - 2].items()}
    b = history.born[size - 1][k]
    return {"cell": cell, "knot": k, "parents": b.parents, "parent_cells": [prior[p] for p in b.parents],
            "consumed": b.inputs, "fresh": b.fresh}


def compare_right_open(d, law, split):
    original = source(d, 1, split)
    changed, edit = add_distinction(original, (d,))
    limit = d + 5
    quiet, loaded = (grow(rows, law, limit) for rows in (original, changed))
    q_map = match_intervals(quiet, d, right_ray=False)
    l_map = match_intervals(loaded, d, right_ray=True)
    end_q = check_roles(quiet, d, law)
    end_l = check_roles(loaded, d, law)
    assert end_q == [[1, 2]] * limit and end_l == [[2, 2]] * limit
    q_labels, _ = ancestry(quiet, d)
    l_labels, l_flags = ancestry(loaded, d)
    offers = []
    sizes = []
    for age, (q, l) in enumerate(zip(q_map, l_map, strict=True)):
        m = age + 1
        assert q.keys() <= l.keys() and len(q) == d + 1 and len(l) == d + m
        anchor = (1 - m, 0, False)
        q_view = live_read(quiet.frames[age])
        l_view = live_read(loaded.frames[age])
        for _, witnesses, graph in (q_view, l_view):
            assert len(graph.edges) == len(graph) - 1 and max(dict(graph.degree()).values()) == 2
            assert sum(len(w) >= 2 for w in witnesses) == len(graph.edges)
        assert all(projected_end(q_view, q, q[anchor], r) == projected_end(l_view, l, l[anchor], r)
                   for r in range(d))
        assert projected_end(q_view, q, q[anchor], d) != projected_end(l_view, l, l[anchor], d)
        right = (d, d + m - 1, False)
        assert nx.shortest_path_length(l_view[2], l[anchor], l[right]) == d + age
        if m < limit:
            a_q = child_offers(quiet, q_map, age, q[anchor])
            a_l = child_offers(loaded, l_map, age, l[anchor])
            assert a_q == a_l and sorted((len(g), h) for g, h in a_q) == [(1, 2), (2, 2)]
            offers.append({"parent_size": m, "all_children_through_A": a_q})
        if m == 1:
            continue
        q_mark, l_mark = q_labels[age - 1], l_labels[age - 1]
        assert q_mark["pure_a"] == {q[anchor]} and not q_mark["pure_b"]
        assert l_mark["pure_a"] == {l[anchor]} and l_mark["pure_b"] == {l[right]}
        assert not l_mark["direct"] and not l_mark["pure_A_and_B_descendant"]
        assert set(l[c] for c in l.keys() - q.keys()) == l_mark["b_inclusive"]
        q_a = {c for c in q if q[c] in q_mark["a_inclusive"]}
        l_a = {c for c in l if l[c] in l_mark["a_inclusive"]}
        assert q_a == {c for c in q if c[1] >= 0 and c[0] <= -1}
        assert l_a == {c for c in l if c[1] >= 0 and c[0] <= -1}
        new_a = l_a - q_a
        assert {l[c] for c in new_a} == l_mark["mixed"] and len(new_a) == max(0, m - d - 2)
        assert q_mark["passive_both_originals"] == int(m >= d + 1)
        assert l_mark["passive_both_originals"] == max(0, m - d)
        q_h = quiet.born[age]
        l_h = loaded.born[age]
        changed_a = [c for c in q_a if len(q_h[q[c]].fresh) != len(l_h[l[c]].fresh)]
        assert changed_a == ([(d - m + 1, d, False)] if m >= d + 2 else [])
        assert all(len(q_h[q[c]].fresh) == 1 and len(l_h[l[c]].fresh) == 2 for c in changed_a)
        sizes.append({"size": m, "births": [len(q), len(l)],
                      "fresh": [sum(len(b.fresh) for b in x.values()) for x in (q_h, l_h)],
                      "A_inclusive": [len(q_a), len(l_a)], "new_A_also_B": len(new_a),
                      "both_originals": [q_mark["passive_both_originals"], l_mark["passive_both_originals"]],
                      "A_inclusive_common_price_change": changed_a, "pure_A_co_parent_with_B_descendant": 0,
                      "pure_tips_separation_loaded": d + age})
    joint = physical_birth(loaded, l_map, d + 3, (-1, d + 1, False))
    assert {l_flags.get(p, 0) for p in joint["parents"]} == {1, 2}
    assert set(joint["parent_cells"]) == {(-1, d, False), (0, d + 1, False)}
    return {"sources": [original, changed], "edit": edit, "through_size": limit, "by_size": sizes,
            "A_immediate_children": offers, "root_free_tip_loose_counts": [end_q[0], end_l[0]],
            "launches_at_size_two": {"A_quiet": physical_birth(quiet, q_map, 2, (-1, 0, False)),
                                     "A_loaded": physical_birth(loaded, l_map, 2, (-1, 0, False)),
                                     "B_loaded": physical_birth(loaded, l_map, 2, (d, d + 1, False))},
            "first_mixing_of_originals_only": {"size": d + 1,
                "quiet": physical_birth(quiet, q_map, d + 1, (0, d, False)),
                "loaded": physical_birth(loaded, l_map, d + 1, (0, d, False))},
            "A_end_first_distinguishing_radius": d,
            "first_A_inclusive_price_change": {"size": d + 2,
                "quiet": physical_birth(quiet, q_map, d + 2, (-1, d, False)),
                "loaded": physical_birth(loaded, l_map, d + 2, (-1, d, False))},
            "first_added_A_descendant": {"size": d + 3, "birth": joint},
            "replays": [quiet.replay, loaded.replay]}


def compare_twig(d, law):
    at = d - 1
    plain = source(d, 2)
    decorated, edit = add_distinction(plain, (at,))
    limit = d + 4
    base, extra = (grow(rows, law, limit) for rows in (plain, decorated))
    q_map = match_intervals(base, d, right_ray=True)
    l_map = match_intervals(extra, d, right_ray=True, twig=at)
    assert check_roles(base, d, law) == check_roles(extra, d, law) == [[2, 2]] * limit
    baseline, _ = ancestry(base, d)
    loaded, _ = ancestry(extra, d)
    table = []
    for age, (q, l) in enumerate(zip(q_map, l_map, strict=True)):
        m = age + 1
        assert q.keys() <= l.keys() and len(l) - len(q) == m - 1
        a = (1 - m, 0, False)
        if m < limit:
            assert child_offers(base, q_map, age, q[a]) == child_offers(extra, l_map, age, l[a])
        q_read = live_read(base.frames[age])
        l_read = live_read(extra.frames[age])
        assert all(projected_end(q_read, q, q[a], r) == projected_end(l_read, l, l[a], r)
                   for r in range(at))
        assert projected_end(q_read, q, q[a], at) != projected_end(l_read, l, l[a], at)
        if m == 1:
            continue
        q_m, l_m = baseline[age - 1], loaded[age - 1]
        b = (d, d + age, False)
        assert q_m["pure_a"] == {q[a]} and q_m["pure_b"] == {q[b]}
        assert l_m["pure_a"] == {l[a]} and l_m["pure_b"] == {l[b]}
        assert not l_m["direct"] and not l_m["pure_A_and_B_descendant"]
        count = [len(q_m["mixed"]), len(l_m["mixed"])]
        assert count == [max(0, m - d - 2), max(0, m - d - 2) + max(0, m - d - 3)]
        h_q, h_l = base.born[age], extra.born[age]
        mixed_fresh = [sum(len(h[k].fresh) for k in marked["mixed"])
                       for h, marked in ((h_q, q_m), (h_l, l_m))]
        assert mixed_fresh == [2 * count[0], 3 * count[0] + 2 * (count[1] - count[0])]
        matches = [c for c in q if q[c] in q_m["a_inclusive"] and l[c] in l_m["a_inclusive"]]
        changed = sum(len(h_q[q[c]].fresh) < len(h_l[l[c]].fresh) for c in matches)
        assert changed == max(0, m - at - 1)
        table.append({"size": m, "births": [len(q), len(l)], "both_launches": count,
                      "fresh_on_both_launches": mixed_fresh, "A_inclusive_old_price_increases": changed})
    first = (-1, d + 1, False)
    return {"d": d, "sources": [plain, decorated], "edit": edit, "through_size": limit,
            "by_size": table, "first_A_rooted_candidate_radius": at,
            "first_mixed": [physical_birth(base, q_map, d + 3, first),
                            physical_birth(extra, l_map, d + 3, first)],
            "replays": [base.replay, extra.replay]}


def compare_null(d, law):
    first = source(d, 2)
    second, edit = add_distinction(first, (d - 2, d))
    limit = d + 4
    q, l = (grow(rows, law, limit) for rows in (first, second))
    base_levels, edited_levels = (match_intervals(history, d, right_ray=True) for history in (q, l))
    assert check_roles(q, d, law) == check_roles(l, d, law)
    counts = []
    for t, (q_names, l_names) in enumerate(zip(base_levels, edited_levels, strict=True)):
        shape = (-t, 0, False)
        q_read, l_read = live_read(q.frames[t]), live_read(l.frames[t])
        assert projected_end(q_read, q_names, q_names[shape], len(q_names)) == projected_end(
            l_read, l_names, l_names[shape], len(l_names))
        q_plan = [(b.parents, len(b.fresh)) for b in q.born[t].values()]
        l_plan = [(b.parents, len(b.fresh)) for b in l.born[t].values()]
        assert q_plan == l_plan
        counts.append(len(q_plan))
    return {"d": d, "sources": [first, second], "edit": edit, "through_size": limit,
            "equal_whole_end_witnesses_and_birth_plan_each_size": True, "birth_counts": counts,
            "replays": [q.replay, l.replay]}


def compare_shortcut(law):
    d = 8
    first = source(d, 2, extra={2: 1, 3: 1, 6: 2})
    second, edit = add_distinction(first, (d + 1 + 2, 6))
    q_open, _, q_g = live_read(first)
    l_open, _, l_g = live_read(second)
    assert q_open == l_open and len(q_g.edges) + 2 == len(l_g.edges)
    traces = []
    for rows, limit in ((first, d + 4), (second, 9)):
        history = grow(rows, law, limit)
        # The extra shared distinction does not move either original tip.
        profiles = check_roles(history, d, law)
        assert all(profile == [2, 2] for profile in profiles)
        scores, flags = ancestry(history, d)
        first_joint = None
        a, b_tip = 0, d
        metrics = []
        for age, marked in enumerate(scores, 1):
            knots = history.born[age]
            budget = sorted((len(b.parents), len(b.fresh)) for b in knots.values() if a in b.parents)
            budget_b = sorted((len(b.parents), len(b.fresh)) for b in knots.values() if b_tip in b.parents)
            assert budget == budget_b == [(1, 2), (2, 2)]
            assert len(marked["pure_a"]) == len(marked["pure_b"]) == 1
            a, = marked["pure_a"]
            b_tip, = marked["pure_b"]
            assert not marked["direct"] and not marked["pure_A_and_B_descendant"]
            if first_joint is None and marked["mixed"]:
                roster = []
                for key in sorted(marked["mixed"]):
                    b = knots[key]
                    assert {flags.get(p, 0) for p in b.parents} >= {1, 2}
                    roster.append({"knot": key, "parents": b.parents, "parent_launch_flags": [flags.get(p, 0)
                                   for p in b.parents], "consumed": b.inputs, "fresh": b.fresh})
                first_joint = {"size": age + 1, "roster": roster}
            metrics.append({"size": age + 1, "births": len(knots), "fresh": sum(len(b.fresh) for b in knots.values()),
                            "launches_both": len(marked["mixed"]), "A_child_budgets": budget,
                            "B_child_budgets": budget_b})
        traces.append({"through_size": limit, "metrics": metrics, "first_joint": first_joint,
                       "replays": history.replay})
    assert [t["first_joint"]["size"] for t in traces] == [11, 8]
    return {"d": d, "sources": [first, second], "edit": edit,
            "original_end_step_separation": [nx.shortest_path_length(g, 0, d) for g in (q_g, l_g)],
            "unchanged_original_loose_distinctions": True, "comparison": traces}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    readings = {}
    for law in ("parity", "nae"):
        readings[law] = {"right_supply": {str(d): compare_right_open(d, law, (1, 2)) for d in (2, 3, 5, 8)},
                         "thicker_witnesses_2_and_3": compare_right_open(3, law, (2, 3)),
                         "near_right_spare": compare_twig(5, law), "live_live_null": compare_null(3, law),
                         "extra_witness_meeting": compare_shortcut(law)}
    data = {"design": "fe65cd3c28cb4e00909e92f83597cd85cb1aebf6",
            "both_laws": readings, "complete_funded_layers": True, "identified_fixed_map_replay": True}
    args.out.write_text(json.dumps(data, sort_keys=True, indent=2) + "\n")


if __name__ == "__main__":
    main()
