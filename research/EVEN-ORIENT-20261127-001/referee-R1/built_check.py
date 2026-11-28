"""Rebuild the four starts, their 728-placement family, and the birth obstructions.

Run from the repository root. The archive supplies published rows and its
growth engine for comparison only. The earlier cross-pair referee's
minimal_count and minimal_measure supply the matching search and cycle measurements.
The growth, eligibility, fixture identification and hand checks below are new.
"""

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, permutations, product
import json
from pathlib import Path
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
sys.path.insert(0, str(RESEARCH / "CELL-SIGN-20261127-001/referee-R1"))
from minimal_count import ChoiceCode, bits, minimal_words, relation_support
from minimal_measure import interleaves, measure_cycles


def pair(x, y):
    return (min(x, y), max(x, y))


def failing(left, right):
    return tuple(sorted((pair(*left), pair(*right))))


# Inputs are specified by the two pairs of holders in each failing pair.
A = tuple(failing((u, v), partners) for (u, v), matching in zip(
    ((0, 1), (0, 2), (1, 2)),
    (((3, 4), (5, 6)), ((3, 5), (4, 6)), ((3, 6), (4, 5))), strict=True,
) for partners in matching)
B = tuple(failing((i, i + 3), (offset + (i + 1) % 3, offset + (i + 2) % 3))
          for i in range(3) for offset in (0, 3))
C = tuple(failing(left, right) for left, right in (
    ((5, 1), (3, 4)), ((5, 3), (4, 1)), ((5, 0), (1, 3)),
    ((2, 3), (0, 4)), ((2, 0), (4, 1)), ((2, 4), (1, 0)),
))
KINDS = {"a": A, "b": B, "c": C}


def multiplicities(choice):
    return Counter(holding for cell in choice for holding in cell)


def fixture_starts():
    # Leave out the chosen last knot and turn its values into loose distinctions.
    def remove_last(choice, last):
        counts = multiplicities(choice)
        loose = tuple(counts[pair(k, last)] for k in range(last))
        return Counter({p: k for p, k in counts.items() if last not in p}), loose

    am, al = remove_last(A, 6)
    am[0, 3] += 1  # joins the two parts of the hand-built start
    cm, cl = remove_last(C, 5)
    return {"B1": (multiplicities(B), (1, 1, 1, 0, 0, 0)),
            "B2": (am, al), "B3": (cm, cl),
            "B4": (cm, tuple(k + (i == 4) for i, k in enumerate(cl)))}


def start_rows(meetings, loose_counts):
    rows = [[] for _ in loose_counts]
    next_value = 0
    for (i, j), count in sorted(meetings.items()):
        values = range(next_value, next_value + count)
        rows[i].extend(values)
        rows[j].extend(values)
        next_value += count
    for row, count in zip(rows, loose_counts, strict=True):
        row.extend(range(next_value, next_value + count))
        next_value += count
    return rows


def holder_map(rows):
    holders = defaultdict(list)
    for knot, values in enumerate(rows):
        for value in values:
            holders[value].append(knot)
    return holders


def join_groups(contexts, veto_common=True):
    """Maximal pairwise-compatible sets with empty total intersection, plus uncovered pairs."""
    owners = defaultdict(list)
    for knot, neighbors in contexts.items():
        for shared in neighbors:
            owners[shared].append(knot)
    graph = nx.Graph()
    for knots in owners.values():
        graph.add_edges_from(combinations(knots, 2))
    large = []
    for clique in nx.find_cliques(graph):
        if len(clique) >= 3 and (not veto_common or not set.intersection(*(contexts[i] for i in clique))):
            large.append(tuple(sorted(clique)))
    used = {p for group in large for p in combinations(group, 2)}
    pairs = {pair(i, j) for i, j in graph.edges} - used
    return sorted(large) + sorted(pairs)


def grow(meetings, loose_counts, round_limit=10, knot_limit=3000, *, veto_common=True):
    rows = start_rows(meetings, loose_counts)
    dates = [0] * len(rows)
    history = []
    contexts = {i: set() for i in range(len(rows))}
    for i, j in meetings:
        contexts[i].add(j)
        contexts[j].add(i)
    pattern = nx.Graph(contexts)
    assert nx.is_connected(pattern)
    holders = holder_map(rows)
    next_value = len(holders)
    loose = {k: [v for v in row if len(holders[v]) == 1] for k, row in enumerate(rows)}
    while True:
        loose = {k: vs for k, vs in loose.items() if vs}
        if not loose:
            outcome = "grown closed" if history else "initially closed"
            break
        groups = join_groups({i: contexts[i] for i in loose}, veto_common)
        demand = Counter(k for group in groups for k in group)
        short = {i: demand[i] - len(values) for i, values in loose.items() if demand[i] > len(values)}
        if short:
            outcome = "stalled"
            break
        if len(history) == round_limit:
            outcome = "growing"
            break
        # Each unused loose distinction has a one-parent birth of its own.
        parents = groups + [(i,) for i, values in loose.items() for _ in range(len(values) - demand[i])]
        if len(rows) + len(parents) > knot_limit:
            outcome = "cut"
            break
        contexts = {len(rows) + j: set(p) for j, p in enumerate(parents)}
        lookahead = Counter(k for group in join_groups(contexts, veto_common) for k in group)
        unused = {i: iter(values) for i, values in loose.items()}
        total_loose = sum(map(len, loose.values()))
        following, births = {}, []
        for parent_set in parents:
            knot = len(rows)
            taken = sorted(next(unused[i]) for i in parent_set)
            # In a connected holding, eliminating every shared distinction from
            # an old parity sum uses either all knots or none. The sole nonempty
            # implied support on loose distinctions is therefore all of them.
            fresh_count = lookahead[knot]
            if len(taken) != total_loose:
                fresh_count = max(fresh_count, 3 - len(taken), 1)
            fresh = list(range(next_value, next_value + fresh_count))
            next_value += fresh_count
            births.append({"knot": knot, "parents": parent_set, "taken": taken, "fresh": fresh})
            following[knot] = fresh
            rows.append(taken + fresh)
            dates.append(len(history) + 1)
        assert all(next(values, None) is None for values in unused.values())
        loose = following
        history.append(births)
    return {"outcome": outcome, "rounds": len(history), "history": history,
            "last_groups": groups if outcome == "stalled" else None,
            "shortages": short if outcome == "stalled" else None,
            "dates": dates, "rows": rows}


def eligible(rows, dates, whole):
    holders = holder_map(rows)
    candidates = []
    for x, y in combinations(sorted(holders), 2):
        u, v = holders[x]
        w, z = holders[y]
        # The two holding intervals may touch at a round. An eligible birth
        # comparison has one distinction fully held when the other first appears.
        if len({u, v, w, z}) != 4:
            continue
        if whole or dates[v] <= dates[w] or dates[z] <= dates[u]:
            candidates.append((x, y))
    return holders, candidates


def matching_code(holders, candidates, number):
    indices = {p: i for i, p in enumerate(combinations(range(number), 2))}
    checks = [0] * len(indices)
    used = defaultdict(int)
    columns, cycles, used_values = [], [], []
    cost = 0
    for i, (x, y) in enumerate(candidates):
        a, b = holders[x]
        c, d = holders[y]
        cycle = (a, c, b, d)
        col = 0
        for u, v in product((a, b), (c, d)):
            j = indices[pair(u, v)]
            col |= 1 << j
            checks[j] |= 1 << i
        columns.append(col)
        cycles.append(cycle)
        cost |= int(interleaves(cycle)) << i
        used_values.append((1 << x) | (1 << y))
        used[x] |= 1 << i
        used[y] |= 1 << i
    dimension, usable = relation_support(columns)
    disjoint = [usable & ~(used[x] | used[y]) for x, y in candidates]
    return ChoiceCode(cycles, columns, checks, used_values, disjoint, cost, dimension, usable)


@lru_cache(maxsize=None)
def class_key(choice):
    counts = multiplicities(choice)
    knots = sorted({k for holding in counts for k in holding})
    partition = defaultdict(list)
    for knot in knots:
        signature = tuple(sorted(k for p, k in counts.items() if knot in p))
        partition[signature].append(knot)
    ordered = [partition[k] for k in sorted(partition)]
    best = None
    for blocks in product(*(permutations(block) for block in ordered)):
        labels = {k: i for i, k in enumerate(k for block in blocks for k in block)}
        word = tuple(sorted(failing((labels[u], labels[v]), (labels[w], labels[z]))
                            for (u, v), (w, z) in choice))
        if best is None or word < best:
            best = word
    return best


KIND_KEYS = {class_key(tuple(sorted(choice))): name for name, choice in KINDS.items()}
assert len(KIND_KEYS) == 3


def count_rows(counter):
    return [[*key, n] for key, n in sorted(counter.items())]


def measurements(rows, dates, whole, include_words=False):
    holders, candidates = eligible(rows, dates, whole)
    code = matching_code(holders, candidates, len(rows))
    # Strictness limits every choice to half the number of available values.
    words = minimal_words(code, len(holders) // 2)
    tally, features = Counter(), Counter()
    cases = []
    for word in words:
        selected = [candidates[i] for i in bits(word)]
        cycles = [code.cycles[i] for i in bits(word)]
        details = measure_cycles(cycles)
        tally[len(cycles), "odd" if details["sign"] else "even", details["orientable"]] += 1
        if details["sign"] or details["orientable"]:
            continue
        holding = tuple(sorted(failing((a, b), (c, d)) for a, c, b, d in cycles))
        kind = KIND_KEYS.get(class_key(holding), "other") if len(selected) == 6 else "other"
        values = {x for p in selected for x in p}
        used = {k for x in values for k in holders[x]}
        with_newborn = sum(dates[holders[x][1]] > 0 for x in values)
        fresh_at_birth = sum(dates[holders[x][0]] > 0 for x in values)
        on_start = sum(dates[k] == 0 for k in used)
        doubled = sum(n >= 2 for n in multiplicities(holding).values())
        features[len(cycles), kind, details["max_coverage"], details["separated_euler"],
                 doubled, on_start, len(used) - on_start, with_newborn, fresh_at_birth] += 1
        if include_words:
            cases.append([kind, selected])
    return {"candidate_pairs": len(candidates), "minimal_choices": len(words), "tally": count_rows(tally),
            "nonorientable_even": count_rows(features), **({"choice_labels": cases} if include_words else {})}


def serial_start(meetings, loose):
    return [len(loose), [[u, v, n] for (u, v), n in sorted(meetings.items())], list(loose)]


def census_index(meetings, loose, census):
    n = len(loose)
    if n > 5:
        return None
    best = None
    for relabel in permutations(range(n)):
        holding = sorted([*pair(relabel[i], relabel[j]), k] for (i, j), k in meetings.items())
        counts = [loose[relabel.index(i)] for i in range(n)]
        candidate = [n, holding, counts]
        if best is None or candidate < best:
            best = candidate
    return census.index(best) if best in census else None


def holding_summary(meetings, loose, state):
    return {"start": serial_start(meetings, loose), "start_distinctions": sum(meetings.values()) + sum(loose),
            "outcome": state["outcome"], "rounds": state["rounds"], "last_knot_count": len(state["rows"])}


def doubled_check(rows, dates):
    counts = Counter(tuple(knots) for knots in holder_map(rows).values())
    assert all(len(p) == 2 for p in counts)
    assert all(all(dates[i] == 0 for i in p) for p, count in counts.items() if count > 1)
    assert all((dates[i] == dates[j] == 0) or abs(dates[i] - dates[j]) == 1 for i, j in counts)


def individual(meetings, loose, census):
    state = grow(meetings, loose)
    result = holding_summary(meetings, loose, state)
    result.update({"start_rows": start_rows(meetings, loose), "census_index": census_index(meetings, loose, census),
                   "births_by_round": state["history"], "last_groups_on_stall": state["last_groups"],
                   "shortages_on_stall": state["shortages"]})
    if state["outcome"] == "grown closed":
        doubled_check(state["rows"], state["dates"])
        result["closure_rows"] = state["rows"]
        for whole, arm in enumerate(("birth", "whole")):
            result[arm] = measurements(state["rows"], state["dates"], bool(whole), include_words=True)
    return result


def classify_assignment(holding, newborns):
    """With 12 start distinctions every member of a first-round group must supply a choice value."""
    neighbors = defaultdict(set)
    for u, v in holding:
        neighbors[u].add(v)
        neighbors[v].add(u)
    starts = set(neighbors) - set(newborns)
    parent_sets = {v: neighbors[v] for v in newborns}
    if any(target & set(newborns) for target in parent_sets.values()):
        return {"reason": "two first-round knots would have to meet"}
    shared = {v: sorted(k for k in starts if ps <= neighbors[k]) for v, ps in parent_sets.items()}
    groups = join_groups({k: neighbors[k] & starts for k in starts if any(k in ps for ps in parent_sets.values())})
    desired = Counter(tuple(sorted(ps)) for ps in parent_sets.values())
    if any(shared.values()):
        reason = "one start knot meets all the requested parents"
    elif len(desired) < len(parent_sets):
        reason = "two births request the same multi-parent group"
    elif any(tuple(group) not in groups for group in desired):
        reason = "the requested group is absent"
    else:
        reason = "group present"
    return {"reason": reason, "start_knots": sorted(starts), "parents": [list(p) for p in desired.elements()],
            "common_start_neighbors": shared, "available_groups": groups}


def orientation_cover(cycles):
    # Put the two cyclic orders over each failing pair. Glue copies at a cross
    # pair only when their traversals are opposite. Keep both ends' knot names.
    appearances = defaultdict(list)
    for i, cycle in enumerate(cycles):
        for u, v in zip(cycle, cycle[1:] + cycle[:1]):
            appearances[pair(u, v)].append((i, u < v))
    identifications = nx.Graph()
    for (u, v), ((i, order), (j, other)) in appearances.items():
        for sheet in (0, 1):
            for k in (u, v):
                identifications.add_edge((i, sheet, k), (j, sheet ^ (order == other), k))
    parts = {}
    flip = {}
    for number, nodes in enumerate(nx.connected_components(identifications)):
        for node in nodes:
            parts[node] = number
    for (i, sheet, k), number in parts.items():
        target = parts[i, 1 - sheet, k]
        assert flip.setdefault(number, target) == target and target != number
    lifted = [tuple(parts[i, sheet, k] for k in cycle) for i, cycle in enumerate(cycles) for sheet in (0, 1)]
    data = measure_cycles(lifted)
    meet = nx.Graph()
    for cycle in lifted:
        meet.add_edges_from(zip(cycle, cycle[1:] + cycle[:1]))
    assert nx.is_connected(meet) and data["orientable"] and data["covered_twice"]
    colours = nx.bipartite.color(meet)
    changes = {colours[k] != colours[other] for k, other in flip.items()}
    assert len(changes) == 1
    return {"knots": len(meet), "cross_pairs": meet.number_of_edges(), "failing_pairs": len(lifted),
            "euler": data["euler"], "connected": True, "orientable": True, "two_colourable": True,
            "exchange_of_copies_switches_colours": changes.pop()}


def five_knot_check():
    # With ten cross pairs and five failing pairs, every knot is left out
    # once. Assign one of three pairings of the other four to each missing knot.
    choices = []
    for missing in range(5):
        a, b, c, d = [i for i in range(5) if i != missing]
        choices.append((failing((a, b), (c, d)), failing((a, c), (b, d)), failing((a, d), (b, c))))
    checked = []
    for collection in product(*choices):
        if len(multiplicities(collection)) != 10:
            continue
        cycles = [(a, c, b, d) for (a, b), (c, d) in collection]
        data = measure_cycles(cycles)
        assert data["covered_twice"] and data["orientable"] and not data["sign"] and data["one_cycle_per_knot"]
        checked.append(tuple(sorted(collection)))
    return {"assignments": 3**5, "fully_covered": len(checked), "orientable": len(checked),
            "relabeling_classes": len({class_key(choice) for choice in checked}), "example": checked[0]}


def hand_checks():
    witnesses = {}
    for name, choice in KINDS.items():
        holding = multiplicities(choice)
        cycles = [(a, c, b, d) for (a, b), (c, d) in choice]
        data = measure_cycles(cycles)
        cross = Counter(pair(u, v) for (a, b), (c, d) in choice for u, v in product((a, b), (c, d)))
        neighbors = {i: {v if i == u else u for u, v in holding if i == u or i == v}
                     for p in holding for i in p}
        linked = nx.Graph()
        linked.add_nodes_from(range(len(choice)))
        appearances = defaultdict(list)
        for i, (p, q) in enumerate(choice):
            for u, v in product(p, q):
                appearances[pair(u, v)].append(i)
        linked.add_edges_from(appearances.values())
        assert nx.is_connected(linked) and set(cross.values()) == {2}
        assert not data["orientable"] and not data["sign"] and data["one_cycle_per_knot"]
        doubled = sorted(p for p, k in holding.items() if k > 1)
        on_doubled = {k for p in doubled for k in p}
        witnesses[name] = {"failing_holder_pairs": choice, "knots": len(neighbors), "cross_pairs": len(cross),
                           "sign": data["sign"], "orientable": data["orientable"],
                           "separated_euler": data["separated_euler"], "doubled_meetings": doubled,
                           "partners": {k: sorted(vs) for k, vs in sorted(neighbors.items())},
                           "common_knots_at_nondoubled": {k: sorted(j for j in neighbors if j != k and ns <= neighbors[j])
                                                          for k, ns in neighbors.items() if k not in on_doubled},
                           "orientation_double_cover": orientation_cover(cycles)}
    # An initial knot meets a newborn only in round one. Among newborns,
    # meetings have opposite round parity. In a pairwise-meeting set of four,
    # at least three must be start knots: at most two newborns if all are new
    # (indeed no triple), and no two newborns can both meet a start and each other.
    dates = range(5)
    possible = [label for label in product(dates, repeat=4)
                if all((x == y == 0) or abs(x - y) == 1 for x, y in combinations(label, 2))]
    assert min(label.count(0) for label in possible) == 3
    witnesses["a"]["four_pairwise_meeting_knots_possible_rounds_0_through_4"] = possible
    # Each knot off (c)'s doubled meeting shares a choice value with 1 or 4,
    # so every one of its non-start knots has date one. Twelve distinct choice
    # values must all be there at the start; with that budget no other parent fits.
    hc = multiplicities(C)
    c_checks = []
    for size in range(1, 5):
        for born in combinations((0, 2, 3, 5), size):
            case = classify_assignment(hc, born)
            assert case["reason"] != "group present"
            c_checks.append({"nonstart_knots": born, **case})
    witnesses["c"]["all_nonempty_subsets_of_four_possible_first_round_knots"] = c_checks
    witnesses["five_knots_five_pairs_euler_zero"] = five_knot_check()
    return witnesses


def archive_comparison(archive, built, family):
    differences = []

    def check(key, field, left, right):
        if left != right:
            differences.append({"case": key, "field": field, "independent": left, "archive": right})

    def compare_growth(key, row, old):
        for field in ("outcome", "rounds"):
            check(key, field, row[field], old[field])
        if row["outcome"] == "grown closed":
            check(key, "closure_knots", row["last_knot_count"], old["knots"])
            new = row["birth"]
            for left, right in (("candidate_pairs", "candidates"), ("minimal_choices", "words"), ("tally", "tally")):
                check(key, left, new[left], old["birth"][right])

    for key, old in archive["B"].items():
        row = built[key]
        compare_growth(key, row, old)
        check(key, "input", row["start"], old["start"])
        check(key, "census_index", row["census_index"], old["census start"])
        birth_rows = [[r, b["knot"], list(b["parents"])] for r, births in enumerate(row["births_by_round"], start=1)
                      for b in births]
        check(key, "births", birth_rows, old["births"])
        if "birth" in row:
            labels = sorted([kind, sorted([list(p) for p in pairs])] for kind, pairs in row["birth"]["choice_labels"])
            published = sorted([f["kind"], sorted(f["failing pairs"])] for f in old["non-orientable even"])
            check(key, "all_nonorientable_even_choice_labels", labels, published)
    for row, old in zip(family, archive["B1 family"], strict=True):
        key = list(row["loose"])
        check(key, "loose", key, old["loose"])
        compare_growth(key, row, old)
        if row["outcome"] == "grown closed":
            found = row["birth"]["nonorientable_even"]
            check(key, "nonorientable_even", sum(f[-1] for f in found), old["non-orientable even"])
            check(key, "holds_b", any(f[1] == "b" for f in found), old["kind (b)"])
    return differences


def compare_funded_rounds(start, state, engine, totals):
    current = engine.supports_of(start)
    n = len(current)
    assert current == tuple(tuple(row) for row in state["rows"][:n])
    totals["starts"] += 1
    for expected in state["history"]:
        following, status, actual = engine.grown(current, "parity", "ordinary")
        assert status == "funded" and len(expected) == len(actual)
        for own, other in zip(expected, actual, strict=True):
            assert (own["knot"], own["parents"], own["taken"], own["fresh"]) == (
                other["knot"], tuple(other["parents"]), list(other["inputs"]), list(other["fresh"]))
        assert following == tuple(tuple(row) for row in state["rows"][:len(following)])
        current = following
        totals["funded_rounds"] += 1
        totals["births_with_holders_and_fresh_distinctions"] += len(actual)
    if state["outcome"] == "grown closed":
        assert all(len(h) == 2 for h in holder_map(current).values())
    else:
        following, status, _ = engine.grown(current, "parity", "ordinary")
        assert ((state["outcome"] == "stalled" and status == "stalled") or
                (state["outcome"] == "growing" and status == "funded" and state["rounds"] == 10) or
                (state["outcome"] == "cut" and status == "funded" and len(following) > 3000))


def main(pilot):
    sys.path.insert(0, str(RESEARCH / "FORBID-EDITS-20261126-001"))
    import forbid  # used only to compare the independent growth histories

    census = json.loads((RESEARCH / "FORBID-EDITS-20261126-001/starts.json").read_text())
    starts = fixture_starts()
    built = {name: individual(m, loose, census) for name, (m, loose) in starts.items()}
    replay = Counter()
    for m, loose in starts.values():
        compare_funded_rounds(serial_start(m, loose), grow(m, loose), forbid, replay)
    c_holding, c_loose = starts["B3"]
    additions = []
    for i in range(len(c_loose)):
        loose = tuple(n + (j == i) for j, n in enumerate(c_loose))
        state = grow(c_holding, loose)
        additions.append({"extra_loose_at": i, "outcome": state["outcome"], "rounds": state["rounds"],
                          "first_births": state["history"][:1], "last_groups_on_stall": state["last_groups"],
                          "shortages_on_stall": state["shortages"]})
    no_veto = grow(c_holding, c_loose, veto_common=False)
    assert no_veto["outcome"] == "grown closed"
    intervention = {"change": "Remove the common-knot veto on groups of at least three. Keep the 12-distinction start and all other rules fixed.",
                    "outcome": no_veto["outcome"], "rounds": no_veto["rounds"], "births_by_round": no_veto["history"],
                    "birth": measurements(no_veto["rows"], no_veto["dates"], False, include_words=True)}
    assert any(f[1] == "c" for f in intervention["birth"]["nonorientable_even"])
    base = starts["B1"][0]
    family = []
    tally = {arm: Counter() for arm in ("birth", "whole")}
    details = {arm: Counter() for arm in tally}
    for loose in product(range(3), repeat=6):
        if not any(loose):
            continue
        if pilot and len(family) >= pilot:
            break
        state = grow(base, loose)
        compare_funded_rounds(serial_start(base, loose), state, forbid, replay)
        row = {"loose": loose, "outcome": state["outcome"], "rounds": state["rounds"], "last_knot_count": len(state["rows"])}
        if row["outcome"] == "grown closed":
            doubled_check(state["rows"], state["dates"])
            for arm in tally:
                counts = measurements(state["rows"], state["dates"], arm == "whole")
                row[arm] = counts
                tally[arm].update({tuple(r[:-1]): r[-1] for r in counts["tally"]})
                details[arm].update({tuple(r[:-1]): r[-1] for r in counts["nonorientable_even"]})
        family.append(row)
    summary = {"placements": len(family),
               "outcomes_by_round": count_rows(Counter((r["outcome"], r["rounds"]) for r in family)),
               "closures_by_knots_and_round": count_rows(Counter((r["last_knot_count"], r["rounds"]) for r in family
                                                                 if r["outcome"] == "grown closed")),
               "choices": {arm: count_rows(counts) for arm, counts in tally.items()},
               "nonorientable_even": {arm: count_rows(counts) for arm, counts in details.items()}}
    hand = hand_checks()
    if pilot:
        print(json.dumps(summary))
        return
    archive = json.loads((STUDY / "built.json").read_text())
    diff = archive_comparison(archive, built, family)
    output = {"weighting": "One per specified start or labelled placement. Within each closure, one per labelled minimal strict choice; birth and whole are separate readings of that closure.",
              "nonorientable_even_columns": ["failing_pairs", "six_pair_kind", "maximum_coverage", "separated_euler",
                                             "doubled_meetings", "start_knots", "nonstart_knots", "newborn_held_values",
                                             "values_first_introduced_after_start", "labelled_count"],
              "choice_tally_columns": ["failing_pairs", "sign", "orientable", "labelled_count"],
              "B1_to_B4": built, "B3_one_distinction_additions": additions, "B3_without_the_common_knot_veto": intervention,
              "hand_witnesses": hand,
              "family_summary": summary, "published_row_disagreements": diff,
              "archived_engine_comparison_four_fixtures_and_family": replay, "family_rows": family}
    # Keep every placement addressable and the summary readable. Each family
    # member has one physical line, including its closure counts when present.
    family_section = output.pop("family_rows")
    brief = json.dumps(output, indent=2)
    body = brief[:-2] + ',\n  "family_rows": [\n' + ',\n'.join('    ' + json.dumps(r, separators=(",", ":"))
                                                               for r in family_section) + '\n  ]\n}\n'
    (HERE / "built_counts.json").write_text(body)
    print(json.dumps(summary, indent=1))
    print("Published row discrepancies", len(diff))
    assert not diff


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", type=int, help="run this prefix of placements and print counts without writing")
    main(parser.parse_args().pilot)
