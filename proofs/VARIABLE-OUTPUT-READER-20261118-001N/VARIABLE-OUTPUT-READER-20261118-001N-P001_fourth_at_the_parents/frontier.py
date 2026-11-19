"""Fourth births on the exact six- and seven-loose predecessor frontiers."""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import cache
from itertools import chain, combinations, product
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import table_tools as T


M_PATH = next((T.PROOFS / "VARIABLE-OUTPUT-READER-20261118-001M").glob("*/frontier.py"))
M = T.module(M_PATH, "ccdd73f8689b457bc54d96c2767dd5c628eccb01e372bf50f73952e67f1927f1",
             "fourth_three_output_frontier_predecessor")
K_PATH = next((T.PROOFS / "VARIABLE-OUTPUT-READER-20261118-001K").glob("*/closure.py"))
K = T.module(K_PATH, "79a9d330438f988f094ad364642db6d42a5020f9e5bbab0199d231f357e68240",
             "fourth_three_output_reserved_holder")
J, OLD = M.J, M.OLD
TARGET_LOOSE = (6, 7)
LITERAL_OLD_SITE_LIMIT = 12

WITNESS_PREFIX = (
    (0, 1, 2), (0, 3, 4, 5), (3, 6, 7, 8), (1, 6, 9, 10, 11),
    (4, 9, 12, 13), (7, 12, 14, 15), (14, 10, 16, 17), (2, 16, 18, 19),
    (5, 18, 20, 21), (8, 20, 22, 23), (19, 11, 22, 24, 25), (13, 21, 24, 26, 27),
)


@cache
def legal(front):
    return tuple(OLD.possible_parents(front))


def close_prefixes():
    # The two initial unary births are fixed. Third marks its parent count,
    # or zero while its fresh allocation remains available.
    roots = {(0, J.literal_snapshot(rows)[0]): rows for rows in J.initial_histories()}
    trace = dict.fromkeys(roots)
    depth = dict.fromkeys(roots, 3)
    queue = deque(roots)
    edges = Counter()
    while queue:
        node = queue.popleft()
        third, front = node
        capacity = sum(front.loose)
        assert capacity <= (7 if third == 0 else 10 - third)
        for group in legal(front):
            counts = (2,) if len(group) >= 2 else ()
            if third == 0:
                counts = (*counts, 3)
            for h in counts:
                nxt = (len(group) if h == 3 else third, J.step(front, group, h))
                edges[third] += 1
                if nxt not in trace:
                    trace[nxt] = node, group, h
                    depth[nxt] = depth[node] + 1
                    queue.append(nxt)
    return roots, trace, depth, edges


def literal(node, roots, trace, depth):
    here = node
    moves = []
    while trace[here] is not None:
        previous, inputs, outputs = trace[here]
        moves.append((previous, here, inputs, outputs))
        here = previous
    rows = roots[here]
    for previous, following, group, h in reversed(moves):
        current, site_names, loose = J.literal_snapshot(rows)
        assert current == previous[1]
        assert group in OLD.verify_literal_moves(rows, current, site_names, loose)
        rows = J.advance(rows, tuple(site_names[i] for i in group), h)
        assert J.literal_snapshot(rows)[0] == following[1]
    assert len(rows) == depth[node]
    return rows


def loose_names(front):
    result = []
    cursor = 0
    for count in front.loose:
        result.append(tuple(range(cursor, cursor + count)))
        cursor += count
    return tuple(result)


def fourth_template(front, parents):
    last = len(front.loose)
    now_loose = tuple(count - (i in parents) for i, count in enumerate(front.loose))
    now_adjacent = tuple(row | ((1 << last) if i in parents else 0) for i, row in enumerate(front.adjacent))
    retired = (*front.retired, *(now_adjacent[i] for i, count in enumerate(now_loose) if count == 0))
    keep = (*tuple(i for i, count in enumerate(now_loose) if count), last)
    after = OLD.Frontier((*now_loose, 3), (*now_adjacent, OLD.mask(parents)), retired).restrict(keep)
    newborn = len(after.loose) - 1
    triples = tuple(g for g in OLD.possible_parents(after) if len(g) == 3)
    witness = any((after.adjacent[newborn] & OLD.mask(g)).bit_count() >= 2 for g in triples)
    holder = any(newborn in g for g in triples)
    adjacent = any(after.adjacent[newborn] & OLD.mask(g) for g in triples)
    return keep, triples, (holder, witness, adjacent)


def exact_named_births(front, p, old_names, fresh):
    # Use one anonymous topology template per parent group and instantiate
    # every choice of loose identity at these holders.
    batches = {}
    for group in legal(front):
        if len(group) != p:
            continue
        keep, triples, roles = fourth_template(front, group)
        extended = (*old_names, fresh)
        for bits in product(*(old_names[i] for i in group)):
            take = set(bits)
            present = tuple(tuple(x for x in extended[i] if x not in take) for i in keep)
            menu = frozenset(tuple(sorted(choice)) for g in triples for choice in product(*(present[i] for i in g)))
            batches[tuple(sorted(take))] = (menu, roles, group)
    return batches


def frontier_screen(depth):
    distribution = defaultdict(Counter)
    witness_widths = {}
    bounded_literal = []
    six_loose_live = set()
    for node, level in depth.items():
        third, front = node
        loose = sum(front.loose)
        if third == 0 or loose not in TARGET_LOOSE:
            continue
        old_names = loose_names(front)
        fresh = tuple(range(loose, loose + 3))
        for p in (1, 2, 3):
            births = exact_named_births(front, p, old_names, fresh)
            stats = distribution[third, loose, p]
            stats["old_frontiers"] += 1
            stats["old_frontiers_permitting_birth"] += bool(births)
            stats["actual_input_sets"] += len(births)
            stats["input_sets_with_live_menu"] += sum(bool(m) for m, _, _ in births.values())
            for flag, category in enumerate(("holder", "pair_witness", "adjacent")):
                count = sum(bits[flag] if flag < 2 else bits[2] and not (bits[0] or bits[1])
                            for _, bits, _ in births.values())
                stats["input_sets_" + category] += count
                if count:
                    witness_widths.setdefault((third, loose, p, category), 2 * level + 7)
            if p != 3:
                continue
            if births and level <= LITERAL_OLD_SITE_LIMIT:
                bounded_literal.append(node)
            hist = Counter(v[0] for v in births.values())
            n = len(births)
            stats["input_set_pairs"] += n * (n - 1) // 2
            stats["pairs_with_distinct_menus"] += n * (n - 1) // 2 - sum(i * (i - 1) // 2 for i in hist.values())
            if loose != 6:
                continue
            if any(menu for menu, _, _ in births.values()):
                six_loose_live.add(node)
            for inputs, (menu, _, holders) in births.items():
                other = tuple(i for i in range(loose) if i not in inputs)
                if inputs < other and other in births:
                    stats["complementary_pairs"] += 1
                    assert births[other][2] == holders
                    assert not menu and not births[other][0]
    report = []
    names = ("old_frontiers", "old_frontiers_permitting_birth", "actual_input_sets", "input_sets_with_live_menu",
             "input_sets_holder", "input_sets_pair_witness", "input_sets_adjacent", "input_set_pairs",
             "pairs_with_distinct_menus", "complementary_pairs")
    for (third, loose, fourth), counts in sorted(distribution.items()):
        report.append({
            "third_parent_count": third, "old_loose": loose, "fourth_parent_count": fourth,
            **{name: counts[name] for name in names},
            "earliest_width_by_role": {role: witness_widths[third, loose, fourth, role]
                                       for role in ("holder", "pair_witness", "adjacent")
                                       if (third, loose, fourth, role) in witness_widths},
        })
    return report, bounded_literal, six_loose_live


def checked_menu(rows):
    physical = T.allowed(rows)
    front, names, loose = J.literal_snapshot(rows)
    inherited = OLD.verify_literal_moves(rows, front, names, loose)
    actual = {tuple(sorted(p)) for group in inherited if len(group) == 3
              for p in product(*(loose[names[i]] for i in group))}
    assert set(physical) == actual
    return physical


def grade_role(rows, cap, menu):
    return {mark: detail for mark, detail in T.roles(rows, cap, menu).items()
            if detail["roles"] != ("adjacent_only",)}


def sample_report(a, b, rows_a, rows_b, mapping, cap, roles):
    assert T.TABLES.disagreement(a, b, mapping) is None
    mark = min(roles)
    image = tuple(sorted(mapping[i] for i in mark))
    assert image in T.allowed(rows_b)
    assert T.transported((rows_a[cap],), mapping).isdisjoint({tuple(sorted(row)) for row in rows_b})
    verify_parity_pairs(rows_a, a)
    verify_parity_pairs(rows_b, b)
    return {"width": len(a), "left": rows_a, "right": rows_b, "left_to_right": mapping,
            "fourth_site_index": cap, "source_mark": mark, "target_mark": image,
            "source_role": roles[mark], "ordinary_isomorphic": T.ordinary_isomorphic(rows_a, rows_b)}


def verify_parity_pairs(rows, table):
    assert T.parity_minima(rows, (2,))[2] == {
        (u, v): table[u][v] for u, v in combinations(range(len(table)), 2) if table[u][v] != T.INFINITY
    }


def scan_literally(binary, qualifying, roots, trace, depth):
    stats = Counter()
    earliest = {}
    for node in qualifying:
        old = literal(node, roots, trace, depth)
        front, names, available = J.literal_snapshot(old)
        fresh = tuple(range(T.width(old), T.width(old) + 3))
        symbolic = exact_named_births(front, 3, tuple(tuple(available[i]) for i in names), fresh)
        assert set(symbolic) == set(T.allowed(old))
        ordered = tuple(sorted(symbolic))
        variants = [(*old, (*group, *fresh)) for group in ordered]
        tables = T.all_tables(binary, variants)
        menus = [checked_menu(rows) for rows in variants]
        cap = len(old)
        roles = [grade_role(rows, cap, menu) for rows, menu in zip(variants, menus, strict=True)]
        stats["representative_old_prefixes"] += 1
        stats["named_cap_choices"] += len(variants)
        for i, menu in enumerate(menus):
            assert set(menu) == symbolic[ordered[i]][0]
        for i in range(len(variants)):
            for j in range(i, len(variants)):
                stats["self_cases" if i == j else "cross_pairs"] += 1
                a, b = tables[i], tables[j]
                left, right = variants[i], variants[j]
                mapping = tuple(range(len(a))) if i == j else T.isometry(a, b)
                if mapping is None:
                    continue
                stats["matching_self" if i == j else "matching_cross_pairs"] += 1
                nonisomorphic = not T.ordinary_isomorphic(left, right)
                if nonisomorphic:
                    stats["matches_with_nonisomorphic_ordinary_incidence"] += 1
                    stats["nonisomorphic_matches_with_live_menu"] += bool(menus[i] or menus[j])
                    if "first_nonisomorphic_match" not in earliest:
                        verify_parity_pairs(left, a)
                        verify_parity_pairs(right, b)
                        earliest["first_nonisomorphic_match"] = {
                            "left": left, "right": right, "left_to_right": mapping,
                            "left_legal_triples": tuple(sorted(menus[i])),
                            "right_legal_triples": tuple(sorted(menus[j])),
                        }
                adverse = T.menu_disagreement(a, menus[i], menus[j], mapping)
                if adverse is not None:
                    stats["pairs_with_opposing_menus"] += 1
                    if "first_opposite" not in earliest:
                        assert T.TABLES.disagreement(a, b, adverse) is None
                        verify_parity_pairs(left, a)
                        verify_parity_pairs(right, b)
                        earliest["first_opposite"] = {
                            "left": left, "right": right, "left_to_right": adverse,
                            "source_legal_triples": tuple(sorted(menus[i])), "target_legal_triples": tuple(sorted(menus[j])),
                        }
                    continue
                for u, v, correspond in ((i, j, mapping), (j, i, T.inverse(mapping))):
                    if not roles[u]:
                        continue
                    a, b = tables[u], tables[v]
                    left, right = variants[u], variants[v]
                    off = T.missing_support(a, left[cap], right, correspond)
                    if off is None:
                        continue
                    stats["role_support_moves_with_same_menu"] += 1
                    stats["nonisomorphic_matches_with_a_direct_role_move"] += nonisomorphic
                    key = "first_direct_role_self" if u == v else "first_direct_role_cross"
                    if key not in earliest:
                        earliest[key] = sample_report(a, b, left, right, off, cap, roles[u])
                    break
    stats["pairs_with_opposing_menus"] += 0
    stats["matches_with_nonisomorphic_ordinary_incidence"] += 0
    stats["nonisomorphic_matches_with_live_menu"] += 0
    stats["nonisomorphic_matches_with_a_direct_role_move"] += 0
    return {"old_site_limit": LITERAL_OLD_SITE_LIMIT, "counts": dict(stats), **earliest}


def true_loose_bond(rows):
    users, _ = T.incidence(rows)
    loose = frozenset(bit for bit, owners in users.items() if len(owners) == 1)
    summed = 0
    for scope in T.masks(rows):
        summed ^= scope
    assert summed == sum(1 << bit for bit in loose)
    return loose


def named_control(binary):
    old = WITNESS_PREFIX
    events = T.replay(old)
    assert tuple(len(step["consumes"]) for step in events[1:] if len(step["fresh"]) == 3) == (1, 1, 2)
    p, q, fresh = (15, 23, 26), (15, 23, 27), (28, 29, 30)
    left, right = (*old, (*p, *fresh)), (*old, (*q, *fresh))
    assert p in checked_menu(old) and q in checked_menu(old)
    assert T.replay(left)[-1]["parents"] == T.replay(right)[-1]["parents"]
    tables = T.all_tables(binary, (left, right))
    assert tables[0] == tables[1]
    measurements = [T.parity_minima(rows) for rows in (left, right)]
    for table, preview in zip(tables, measurements, strict=True):
        assert preview[2] == {(i, j): table[i][j] for i, j in combinations(range(31), 2)}
    mark = (17, 25, 28)
    menus = checked_menu(left), checked_menu(right)
    assert set(menus[0]) == set(menus[1]) and mark in menus[0]
    assert len(menus[0]) == 3 and T.two_connected(left) and T.two_connected(right)
    directed_roles = [T.roles(rows, len(old), menu)[mark] for rows, menu in zip((left, right), menus, strict=True)]
    assert all("holder" in grade["roles"] for grade in directed_roles)
    reported = (24, 25, 27)
    assert all(len(set(row) & set(reported)) % 2 == 0 for row in left)
    assert [i for i, row in enumerate(right) if len(set(row) & set(reported)) % 2] == [len(old)]
    probes = [{g: m[3].get(g) for g in ((15, 26, 28), mark)} for m in measurements]
    witness = {
        "width": 31, "old_prefix": old, "old_whole_shore_bond": sorted(true_loose_bond(old)),
        "left_fourth_support": left[-1], "right_fourth_support": right[-1],
        "correspondence": tuple(range(31)), "marked_legal_triple": mark,
        "left_and_right_roles": directed_roles,
        "legal_triples_both": tuple(sorted(menus[0])),
        "ordinary_sites_in_one_two_connected_graph_on_each_side": True,
        "full_pair_entries_verified": 465, "full_K_upper_triangle_hex": T.table_upper(tables[0]).hex(),
        "one_bits_in_left_but_not_right": reported,
        "joint_bond_minimum_control": [
            {"three_distinctions": g, "left_K3": probes[0][g], "right_K3": probes[1][g]}
            for g in ((15, 26, 28), mark)
        ],
        "number_of_joint_entries_differing": sum(a != b for a, b in (
            (measurements[0][3].get(g), measurements[1][3].get(g)) for g in combinations(range(31), 3)
        )),
    }
    return witness, left, right


def continuation_controls(binary, left, right):
    level = [(left, right, ())]
    report = []
    swap = tuple(27 if i == 26 else 26 if i == 27 else i for i in range(35))
    for _ in range(2):
        upcoming = []
        for a, b, path in level:
            shared = sorted(T.allowed(a, (2, 3)).keys() & T.allowed(b, (2, 3)).keys())
            w = T.width(a)
            for group in shared:
                support = (*group, w, w + 1)
                upcoming.append(((*a, support), (*b, support), (*path, group)))
        measured = T.all_tables(binary, [rows for a, b, _ in upcoming for rows in (a, b)])
        for i, (a, b, path) in enumerate(upcoming):
            ta, tb = measured[2 * i:2 * i + 2]
            assert T.TABLES.disagreement(ta, tb, swap[:len(ta)]) is None
            menu_a, menu_b = checked_menu(a), checked_menu(b)
            differences = sum(ta[x][y] != tb[x][y] for x, y in combinations(range(len(ta)), 2))
            report.append({
                "joined_input_sets_in_order": path, "width": len(ta), "changed_named_entries": differences,
                "some_fourth_output_consumed": bool(set(chain.from_iterable(path)) & {28, 29, 30}),
                "left_triples": tuple(sorted(menu_a)), "right_triples": tuple(sorted(menu_b)),
                "left_fourth_direct_role": bool(grade_role(a, 12, menu_a)),
                "right_fourth_direct_role": bool(grade_role(b, 12, menu_b)),
            })
        level = upcoming
    return report


def reserved_spare_control(binary, left, right):
    # K's marked holder is carried through every 2-output transition.
    # Its tag for the number of shrinks before a 3-output birth is fixed here.
    holder = 11
    source_spare, target_spare = 27, 26
    assert set(checked_menu(left)) == set(checked_menu(right)) and checked_menu(left)
    initial = K.snapshot(left, 0, holder)[0]
    assert initial == K.snapshot(right, 0, holder)[0]
    cases = {initial: (left, right)}
    queue = deque([initial])
    receipt = {}
    counts, transitions = Counter(), Counter()
    earliest = None
    while queue:
        state = queue.popleft()
        a, b = cases[state]
        again, names, slots = K.snapshot(a, 0, holder)
        paired, names_b, slots_b = K.snapshot(b, 0, holder)
        marked = state.high_holder
        assert again == paired == state and names == names_b and names[marked] == holder
        assert tuple(slots[holder]) == (source_spare,) and tuple(slots_b[holder]) == (target_spare,)
        actual = OLD.verify_literal_moves(a, state.frontier, names, slots)
        assert actual == OLD.verify_literal_moves(b, state.frontier, names_b, slots_b)

        counts[state.loose] += 1
        menu_a, menu_b = checked_menu(a), checked_menu(b)
        marked_triples = {p for p in menu_a if source_spare in p}
        assert bool(marked_triples) == any(len(g) == 3 and marked in g for g in actual)
        if marked_triples and earliest is None:
            first, second = T.all_tables(binary, (a, b))
            for rows, table in zip((a, b), (first, second), strict=True):
                verify_parity_pairs(rows, table)
            earliest = {
                "left": a, "right": b, "width": T.width(a), "left_legal_triple_using_spare": min(marked_triples),
                "named_tables_equal": first == second,
            }
        if not marked_triples:
            assert not any(target_spare in p for p in menu_b)
            assert set(menu_a) == set(menu_b)

        following = []
        for parents in sorted(actual):
            if len(parents) < 2 or marked in parents:
                continue
            nxt = K.turn(state, parents, 2)
            physical = tuple(names[i] for i in parents)
            aa, bb = J.advance(a, physical, 2), J.advance(b, physical, 2)
            assert aa[-1] == bb[-1]
            assert K.snapshot(aa, 0, holder)[0] == K.snapshot(bb, 0, holder)[0] == nxt
            following.append((parents, nxt))
            transitions[len(parents)] += 1
            if nxt not in cases:
                cases[nxt] = aa, bb
                queue.append(nxt)
        receipt[state] = following
    index = {state: i for i, state in enumerate(sorted(receipt))}
    return {
        "holder": holder, "reserved_spares_left_and_right": (source_spare, target_spare),
        "states_by_loose_count": dict(sorted(counts.items())),
        "transitions_by_parent_count": dict(sorted(transitions.items())),
        "first_legal_triple_using_reserved_holder": earliest,
        "closed_graph": [
            {"loose_counts": state.frontier.loose, "adjacency_masks": state.frontier.adjacent,
             "retired_neighborhood_masks": state.frontier.retired, "marked_holder_index": state.high_holder,
             "next": [(parents, index[following]) for parents, following in receipt[state]]}
            for state in sorted(receipt)
        ],
        "initial_record_index": index[initial],
    }


def run(binary):
    roots, trace, depth, edges = close_prefixes()
    abstract, qualifying, six_loose_live = frontier_screen(depth)
    witness, a, b = named_control(binary)
    earliest = min(row["earliest_width_by_role"][kind] for row in abstract
                   if row["old_loose"] == 6 and row["fourth_parent_count"] == 3
                   for kind in ("holder", "pair_witness") if kind in row["earliest_width_by_role"])
    assert earliest == witness["width"]
    front, names, available = J.literal_snapshot(WITNESS_PREFIX)
    assert six_loose_live == {(2, front)} and sorted(front.loose) == [1, 1, 1, 1, 2]
    actual_old = tuple(tuple(available[i]) for i in names)
    choices = exact_named_births(front, 3, actual_old, a[-1][3:])
    live_choices = sorted(inputs for inputs, (menu, _, _) in choices.items() if menu)
    assert live_choices == [a[-1][:3], b[-1][:3]]
    return {
        "closed_frontiers_by_third_parent_count": dict(sorted(Counter(n for n, _ in depth).items())),
        "closed_transitions_by_third_parent_count": dict(sorted(edges.items())),
        "abstract_fourth_births": abstract, "minimum_width_for_direct_role_in_fourth_three_on_six": earliest,
        "only_six_loose_frontier_with_a_live_ternary_fourth": {
            "third_parent_count": 2, "loose_bits_by_holder_in_witness": actual_old,
            "adjacency_masks": front.adjacent, "retired_neighborhood_masks": front.retired,
            "live_choices_in_witness": live_choices,
            "minimum_old_sites": depth[2, front],
        },
        "literal_same_prefix_scan": scan_literally(binary, qualifying, roots, trace, depth),
        "width_31_direct_role": witness, "two_steps_from_width_31_on_common_named_moves": continuation_controls(binary, a, b),
        "reserved_holder_suffix_closure": reserved_spare_control(binary, a, b),
    }


if __name__ == "__main__":
    with TemporaryDirectory(prefix="fourth-at-the-parents-") as work:
        measure = T.compiler(Path(work) / "bond_table")
        print(json.dumps(run(measure), indent=2))
