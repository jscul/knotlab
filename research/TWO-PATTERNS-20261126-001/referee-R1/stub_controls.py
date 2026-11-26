"""Exact small controls for the ordinary count, with nothing taken.

A tuple gives each birth's full making. All controls use the same complete
round, the same supplied meeting or bare sharing, and retirement when short.

For the ordinary count a birth gets at least its demand and one fresh loose
distinction. Adding these private distinctions leaves both the roster and its
groups as they were when demand was counted. At its first read every newborn
can therefore pay. It then spends all its loose distinctions. Only originals
can wait under the waiting treatment.

A sufficient condition for the supplied meeting is that every live original
of the side being read, and the first foreign endpoint, can pay at the first
read in both histories. The rest of the far side can be short. In round one
the meeting adds one pair at the site. The groups with an own member agree
after the first foreign endpoint in one start is matched to the other's.

Retain each birth with at least one own parent and its whole parent set.
After the first round an own newborn meets just its own parents. A member
joinable with it has to meet one of those parents. No waiting far original
can do so. When the parent is original the spent meeting separates their
distinctions. When the parent is made it shares only with its own parents
and its children. Thus every such member is a newborn sibling and is
retained. The parent sets specify all adjacencies among these siblings as
well as every common-knot test. Every group containing the own newborn is
determined in this neighborhood, including whether it is maximal or a pair
already contained in a larger group. This gives its demand and its fresh
count. Its partners are newborn and can pay, so all these groups are kept.
Together with its remaining loose distinctions they specify the next set of
births having an own parent and those births' parent sets. Induction gives
identical own births by full making, fresh count, and places at each round.
All three treatments give this conclusion with nothing taken. With a bare
sharing the starts can already differ in their groups with an own member.
"""

import argparse
from collections import Counter, defaultdict
import gzip
from itertools import combinations, combinations_with_replacement
import json
from pathlib import Path
import sys
from time import perf_counter


SINGLE = ([3], [])
PAIR = ([2, 2], [(0, 1)])
PAIR_THREE = ([3, 3], [(0, 1)])
# The last knot is spent. It holds one distinction with each of the first
# three. The first two have one further distinction in common.
FOUR = ([1, 2, 2, 0], [(3, 0), (3, 1), (3, 2), (0, 1)])
SPENT_WITH_THREE_OTHERS = ([2, 2, 2, 0], [(3, 0), (3, 1), (3, 2)])
THREE_SHARING_IN_PAIRS = ([1, 1, 2], [(0, 1), (1, 2), (0, 2)])
RING = ([3] * 5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])
SOURCE = ([3, 0, 3, 3, 3, 2, 2],
          [(0, 1), (0, 1), (0, 4), (1, 4), (2, 4), (2, 6), (3, 4), (3, 5), (5, 6)])
BENCH = {"ring": RING, "two_knot_part": PAIR, "seven_knot_source": SOURCE}


class Start:
    def __init__(self):
        self.places = []
        self.names = []
        self.descent = []
        self.barred = set()
        self.next_distinction = 0

    def knot(self, name, descent):
        self.places.append([])
        self.names.append(name)
        self.descent.append(descent)
        return len(self.places) - 1

    def give(self, *knots):
        for knot in knots:
            self.places[knot].append(self.next_distinction)
        self.next_distinction += 1

    def pattern(self, side, spec):
        loose, pairs = spec
        knots = [self.knot(("start", side, i), frozenset([side]))
                 for i in range(len(loose))]
        for i, j in pairs:
            self.give(knots[i], knots[j])
        for i, count in enumerate(loose):
            for _ in range(count):
                self.give(knots[i])
        return knots


def joined(a, b, join, site_a=0, site_b=0, mark=None, stub_extra=0, order="AB", steps=1):
    state = Start()
    patterns = {"A": a, "B": b}
    knots = {}
    for side in order:
        knots[side] = state.pattern(side, patterns[side] or ([0], []))
    left, right = knots["A"][site_a], knots["B"][site_b]
    links = [state.knot(("start", "link", i), frozenset(["link"])) for i in range(steps - 1)]
    path = [left, *links, right]
    for i, (first, second) in enumerate(zip(path, path[1:])):
        if join == "meeting":
            spent = state.knot(("start", "spent", i), frozenset(["spent"]))
            state.give(first, spent)
            state.give(second, spent)
            state.give(second, spent)
            state.give(first)
            state.give(second)
        else:
            assert join == "share"
            state.give(first, second)
    if join == "share":
        for link in links:
            state.give(link)
    for side, end in (("A", left), ("B", right)):
        if patterns[side] is None:
            while len(state.places[end]) < 3:
                state.give(end)
            for _ in range(stub_extra):
                state.give(end)
    if mark is not None:
        side, index = mark
        state.give(knots[side][index])
    return state


def holders(state):
    by_distinction = defaultdict(set)
    for knot, places in enumerate(state.places):
        for distinction in places:
            by_distinction[distinction].add(knot)
    return by_distinction


def groups(state, active, held):
    met = set()
    for common, places in enumerate(state.places):
        meets = set().union(*(held[d] for d in places)) if places else set()
        members = (meets - {common}) & active
        if len(members) >= 2:
            met.add(frozenset(members))
    partners = {i: set() for i in active}
    pairs = set()
    for members in met:
        for i, j in combinations(sorted(members), 2):
            pairs.add((i, j))
            partners[i].add(j)
            partners[j].add(i)

    # Enumerate maximal pairwise-joinable sets, retaining the unheld sets
    # of at least three. The remaining pairs themselves are groups.
    big = set()

    def extend(chosen, add, excluded):
        if not add and not excluded:
            if len(chosen) >= 3 and all(not chosen <= m for m in met):
                big.add(tuple(sorted(chosen)))
            return
        pivot = max(add | excluded, key=lambda u: len(add & partners[u]))
        for u in sorted(add - partners[pivot]):
            extend(chosen | {u}, add & partners[u], excluded & partners[u])
            add.remove(u)
            excluded.add(u)

    extend(set(), set(active), set())
    for group in big:
        pairs.difference_update(combinations(group, 2))
    return sorted(big | pairs)


def opening(state):
    held = holders(state)
    loose = {}
    for u, places in enumerate(state.places):
        free = sorted(d for d in places if len(held[d]) == 1 and d not in state.barred)
        if free:
            loose[u] = free
    offered = groups(state, set(loose), held)
    owing = Counter(u for group in offered for u in group)
    short = {u for u, available in loose.items() if len(available) < owing[u]}
    return loose, offered, owing, short


def one_round(state):
    loose, offered, _, short = opening(state)
    kept = [group for group in offered if short.isdisjoint(group)]
    records = [("join", group) for group in kept]
    paid = Counter(u for group in kept for u in group)
    for u, available in loose.items():
        if u in short:
            state.barred.update(available)
        else:
            records.extend(("offshoot", (u,)) for _ in range(len(available) - paid[u]))

    children = []
    ordinal = Counter()
    next_loose = {p: iter(v) for p, v in loose.items()}
    for kind, parents in records:
        making = (kind, tuple(sorted(state.names[p] for p in parents)))
        name = (*making, ordinal[making])
        ordinal[making] += 1
        flags = frozenset().union(*(state.descent[p] for p in parents))
        child = state.knot(name, flags)
        state.places[child].extend(next(next_loose[p]) for p in parents)
        children.append(child)
    demand = Counter(u for group in groups(state, set(children), holders(state)) for u in group)
    by_side = {"A": [], "B": []}
    numeric = {"A": [], "B": []}
    for child, (kind, parents) in zip(children, records):
        fresh = max(1, 3 - len(parents), demand[child])
        for _ in range(fresh):
            state.give(child)
        side = state.descent[child]
        if side == {"A"} or side == {"B"}:
            tag, = side
            places = len(state.places[child])
            by_side[tag].append((state.names[child], fresh, places))
            numeric[tag].append((kind, len(parents), fresh, places))
    return {
        "own": {side: sorted(rows) for side, rows in by_side.items()},
        "numeric": {side: sorted(rows) for side, rows in numeric.items()},
        "short": [state.names[u] for u in sorted(short)],
        "groups": [(tuple(state.names[u] for u in group), short.isdisjoint(group))
                   for group in offered],
    }


def evidence(state, depth):
    return [one_round(state) for _ in range(depth)]


def one_comparison(first, second, depth, side="A"):
    left, right = evidence(first, depth), evidence(second, depth)
    equal = [a["own"][side] == b["own"][side] for a, b in zip(left, right)]
    numeric_equal = [a["numeric"][side] == b["numeric"][side] for a, b in zip(left, right)]
    counts = [[len(a["own"][side]), len(b["own"][side])] for a, b in zip(left, right)]
    return {
        "rounds": depth,
        "own_births_by_round_first_and_second": counts,
        "exact_named_births_equal_by_round": equal,
        "numeric_multisets_equal_by_round": numeric_equal,
        "short_counts_by_round_first_and_second":
            [[len(a["short"]), len(b["short"])] for a, b in zip(left, right)],
        "first_round": {
            name: {"short": rows[0]["short"], "groups_and_whether_kept": rows[0]["groups"],
                   "own_births_as_full_name_fresh_and_places": rows[0]["own"][side]}
            for name, rows in (("first", left), ("second", right))
        },
    }


def bare_no_short():
    res = one_comparison(joined(SINGLE, PAIR, "share"), joined(SINGLE, None, "share"), 3)
    assert res["own_births_by_round_first_and_second"][0] == [2, 3]
    assert res["short_counts_by_round_first_and_second"] == [[0, 0]] * 3
    return res


def bare_mark_no_short():
    res = one_comparison(joined(SINGLE, SPENT_WITH_THREE_OTHERS, "share"),
                         joined(SINGLE, SPENT_WITH_THREE_OTHERS, "share", mark=("B", 3)), 3)
    assert res["own_births_by_round_first_and_second"][0] == [3, 2]
    assert res["short_counts_by_round_first_and_second"] == [[0, 0]] * 3
    return res


def short_site():
    res = one_comparison(joined(SINGLE, FOUR, "meeting"), joined(SINGLE, None, "meeting"), 3)
    assert res["own_births_by_round_first_and_second"][0] == [4, 3]
    assert res["short_counts_by_round_first_and_second"] == [[1, 0], [0, 0], [0, 0]]
    return res


def mark_short_site():
    res = one_comparison(joined(SINGLE, FOUR, "meeting"),
                         joined(SINGLE, FOUR, "meeting", mark=("B", 0)), 3)
    assert res["own_births_by_round_first_and_second"][0] == [4, 3]
    assert res["short_counts_by_round_first_and_second"] == [[1, 0], [0, 0], [0, 0]]
    return res


def short_away_from_site():
    res = one_comparison(joined(SINGLE, FOUR, "meeting", site_b=2), joined(SINGLE, None, "meeting"), 4)
    assert all(res["exact_named_births_equal_by_round"])
    assert res["short_counts_by_round_first_and_second"] == [[1, 0]] + [[0, 0]] * 3
    return res


def other_stub():
    res = one_comparison(joined(PAIR, None, "meeting"), joined(PAIR, None, "meeting", stub_extra=2), 4)
    assert all(res["exact_named_births_equal_by_round"])
    assert res["short_counts_by_round_first_and_second"] == [[0, 0]] * 4
    return res


def numeric_ambiguity():
    res = one_comparison(joined(PAIR_THREE, None, "meeting", site_a=0),
                         joined(PAIR_THREE, None, "meeting", site_a=1), 1)
    assert res["numeric_multisets_equal_by_round"] == [True]
    assert res["exact_named_births_equal_by_round"] == [False]
    assert res["own_births_by_round_first_and_second"] == [[6, 6]]
    return res


def numeric_ambiguity_in_census():
    res = one_comparison(joined(PAIR, THREE_SHARING_IN_PAIRS, "share"),
                         joined(PAIR, None, "share"), 1)
    assert res["exact_named_births_equal_by_round"] == [False]
    assert res["numeric_multisets_equal_by_round"] == [True]
    assert res["own_births_by_round_first_and_second"] == [[3, 3]]
    raw = Path(__file__).resolve().parent.parent / "census" / "census_runs.jsonl.gz"
    with gzip.open(raw, "rt") as lines:
        row = next(r for r in map(json.loads, lines)
                   if r.get("A") == "g3:22@0" and r.get("B") == "g7:112@0"
                   and r.get("join") == "share" and r.get("law") == ["ORD", "CANCEL-RETIRE"])
    recorded = (row["short"][0], row["reads"]["A"]["own births"][0], row["reads"]["A"]["stub"])
    assert recorded == (2, 3, 1)
    res["recorded_census_row"] = {
        "two_knot_part": row["A"], "three_knots_sharing_in_pairs": row["B"],
        "round_one_short": recorded[0], "round_one_own_births": recorded[1],
        "first_difference_from_stub": recorded[2],
    }
    return res


def renumbered():
    res = one_comparison(joined(FOUR, PAIR, "meeting"),
                         joined(FOUR, PAIR, "meeting", order="BA"), 3, side="B")
    assert all(res["exact_named_births_equal_by_round"])
    return res


def bench_mark_funding(pairs=None):
    if pairs is None:
        pairs = combinations_with_replacement(BENCH, 2)
    unmarked = Counter()
    marked = Counter()
    marked_short = []
    for first, second in pairs:
        a, b = BENCH[first], BENCH[second]
        for steps in (1, 2, 3):
            start = joined(a, b, "meeting", steps=steps)
            _, _, _, short = opening(start)
            unmarked[len(short)] += 1
            for side, size in (("A", len(a[0])), ("B", len(b[0]))):
                for index in range(size):
                    start = joined(a, b, "meeting", steps=steps, mark=(side, index))
                    loose, _, owing, short = opening(start)
                    marked[len(short)] += 1
                    if short:
                        who = [(start.names[u], len(loose[u]), owing[u]) for u in sorted(short)]
                        assert all(name[1] == side for name, _, _ in who)
                        assert all(name[:2] != ("start", "link") and name[2] != 0
                                   for name, _, _ in who)
                        assert [(name[2], h, cost) for name, h, cost in who] == [
                            (1, 1, 3), (2, 3, 4), (3, 3, 4)]
                        marked_short.append({"patterns": [first, second], "steps": steps,
                                             "mark": [side, index], "short_name_loose_owing": who})
    return {
        "unmarked_starts_by_number_of_short_members": dict(sorted(unmarked.items())),
        "marks_by_number_of_short_members": dict(sorted(marked.items())),
        "marked_starts_with_a_short_member": marked_short,
        "treatment_scope": "Opening precedes the short-knot treatment and agrees for all three.",
    }


CONTROLS = {
    "bare_sharing_two_knot_part_vs_stub": bare_no_short,
    "bare_sharing_mark_activates_a_previously_spent_knot": bare_mark_no_short,
    "meeting_short_starting_site_vs_stub": short_site,
    "mark_which_funds_the_short_starting_site": mark_short_site,
    "meeting_short_start_away_from_the_site_vs_stub": short_away_from_site,
    "meeting_stub_vs_same_stub_with_two_more_loose_distinctions": other_stub,
    "swap_the_sites_of_a_two_knot_part_with_three_loose_at_each": numeric_ambiguity,
    "same_site_and_numeric_births_different_parent_in_the_census": numeric_ambiguity_in_census,
    "change_global_knot_numbering_keep_the_role_local_names": renumbered,
    "initial_funding_for_each_ordinary_paid_bench_mark": bench_mark_funding,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=CONTROLS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = [args.case] if args.case else CONTROLS
    before = perf_counter()
    out = {
        "law": "ordinary count, nothing taken, short knots retire, complete rounds",
        "start_specs_loose_counts_and_shared_pairs": {
            "single": SINGLE, "two_knot_part": PAIR, "four_knot_part": FOUR,
            "two_knot_part_with_three_loose_at_each": PAIR_THREE,
            "a_spent_knot_sharing_once_with_each_of_three_others": SPENT_WITH_THREE_OTHERS,
            "three_knots_sharing_in_pairs": THREE_SHARING_IN_PAIRS,
        },
        "controls": {name: CONTROLS[name]() for name in cases},
    }
    payload = json.dumps(out, indent=2) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.write_text(payload)
    print(f"{len(out['controls'])} controls in {perf_counter() - before:.4f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
