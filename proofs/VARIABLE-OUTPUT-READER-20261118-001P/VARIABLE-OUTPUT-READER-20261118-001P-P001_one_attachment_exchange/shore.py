"""Follow a parent-closed six-shore in the one-spent formation quotient."""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import lru_cache
from itertools import chain, permutations, product
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

PROOFS = Path(__file__).resolve().parents[2]
O_PATH, = (PROOFS / "VARIABLE-OUTPUT-READER-20261118-001O").glob("*/frontier.py")
N_PATH, = (PROOFS / "VARIABLE-OUTPUT-READER-20261118-001N").glob("*/table_tools.py")
sys.path.insert(0, str(N_PATH.parent))
from table_tools import module

O = module(O_PATH, "7fad6370ce65cbd09d457189a9238a69c2e3582e0c41dd024bf344efc2e2e1ed", "one_attachment_one_spent")
sys.path.pop(0)
J, OLD, T = O.J, O.OLD, O.T
ABSENT = -1
CUTOFF = 6
MAX_SHRINKS = 2
MAX_PAID = CUTOFF - 3


@dataclass(frozen=True, slots=True)
class Shore:
    frontier: OLD.Frontier
    inside: int
    colors: int
    high: int
    third_parents: int
    spending_parents: int
    child_inside: bool
    boundary: int

    @property
    def shrinks(self):
        capacity = 7 if self.third_parents == 0 else 10 - self.third_parents
        return capacity - sum(self.frontier.loose)

    @property
    def paid(self):
        return self.boundary - sum(n for i, n in enumerate(self.frontier.loose) if self.inside >> i & 1)


@lru_cache(maxsize=150_000)
def normalize(front, inside, colors, high):
    profiles = []
    for i, n in enumerate(front.loose):
        retired = tuple(sorted(row.bit_count() for row in front.retired if row >> i & 1))
        profiles.append((n, (inside >> i) & 1, (colors >> i) & 1,
                         i == high, front.adjacent[i].bit_count(), retired))
    classes = [tuple(i for i, key in enumerate(profiles) if key == kind)
               for kind in sorted(set(profiles))]
    expanded_orders = product(*(permutations(group) for group in classes))
    ordered = (sum(groups, ()) for groups in expanded_orders)
    result, order = min((front.restrict(order), order) for order in ordered)
    return result, OLD.project(inside, order), OLD.project(colors, order), order.index(high) if high in order else ABSENT, order


def moves(state):
    for parents in OLD.possible_parents(state.frontier):
        if state.spending_parents and state.high in parents:
            continue
        p = len(parents)
        all_inside = all(state.inside >> i & 1 for i in parents)
        if p >= 2 and (p == 2 or state.shrinks < MAX_SHRINKS):
            yield parents, 2, False
            if all_inside:
                yield parents, 2, True
        if state.third_parents == 0 and p <= 2:
            yield parents, 3, False
            if all_inside:
                yield parents, 3, True
        elif state.third_parents and state.high == ABSENT and p == 3 and all_inside:
            yield parents, 3, True


def advance(state, parents, outputs, inside):
    front = state.frontier
    group = OLD.mask(parents)
    p = len(parents)
    boundary = state.boundary + (outputs - p if inside else 0)
    third = p if outputs == 3 and state.third_parents == 0 else state.third_parents
    shrinks = state.shrinks + (p == 3 and outputs == 2)
    assert 0 <= shrinks <= MAX_SHRINKS
    if boundary > CUTOFF + MAX_SHRINKS - shrinks or boundary + (0 if third else 2) < CUTOFF:
        return None, "boundary"
    paid = state.paid + ((group & state.inside).bit_count() if not inside else 0)
    if paid > MAX_PAID:
        return None, "already_spent_crossings"

    new = len(front.loose)
    new_bit = 1 << new
    available = tuple(n - (i in parents) for i, n in enumerate(front.loose))
    adjacent = tuple(row | (new_bit if i in parents else 0) for i, row in enumerate(front.adjacent))
    retired = (*front.retired, *(adjacent[i] for i, n in enumerate(available) if n == 0))
    kept = (*tuple(i for i, n in enumerate(available) if n), new)
    enlarged = OLD.Frontier((*available, outputs), (*adjacent, group), retired)
    new_inside = state.inside | (new_bit if inside else 0)
    parent_color = (state.colors >> parents[0]) & 1
    assert all(((state.colors >> i) & 1) == parent_color for i in parents)
    new_colors = state.colors | (new_bit if not parent_color else 0)
    high = new if outputs == 3 and state.third_parents else state.high
    assert high == ABSENT or high in kept
    marked = kept.index(high) if high in kept else ABSENT
    sub, s, colors, h, _ = normalize(enlarged.restrict(kept), OLD.project(new_inside, kept),
                                     OLD.project(new_colors, kept), marked)
    spend = p if state.high in parents else state.spending_parents
    child_inside = inside if state.high in parents else state.child_inside
    result = Shore(sub, s, colors, h, third, spend, child_inside, boundary)
    assert result.paid == paid and result.shrinks == shrinks
    return result, None


def literal_partition(rows, selected):
    users, graph = T.incidence(rows)
    colors = {0: 0}
    queue = [0]
    for site in queue:
        for neighbor in sorted(graph[site]):
            if neighbor not in colors:
                colors[neighbor] = 1 - colors[site]
                queue.append(neighbor)
            assert colors[site] != colors[neighbor]
    assert len(colors) == len(rows)
    boundary = tuple(sorted(bit for bit, holders in users.items()
                            if sum(i in selected for i in holders) == 1))
    return users, graph, colors, boundary


def snapshot(rows, selected, third=0, high=ABSENT, child=ABSENT, spending=0):
    _, _, colors, cut = literal_partition(rows, selected)
    front, names, slots = J.literal_snapshot(rows)
    inside = OLD.mask(i for i, holder in enumerate(names) if holder in selected)
    color_rows = OLD.mask(i for i, holder in enumerate(names) if colors[holder])
    cap = names.index(high) if high in names else ABSENT
    front, inside, color_rows, cap, order = normalize(front, inside, color_rows, cap)
    return (Shore(front, inside, color_rows, cap, third, spending, child in selected, len(cut)),
            tuple(names[i] for i in order), slots)


def start_records():
    out = {}
    for rows in J.initial_histories():
        events = T.replay(rows)
        for use in product((False, True), repeat=2):
            selected = {0, *(i for i, yes in enumerate(use, 1) if yes)}
            if any(not set(events[i]["parents"]) <= selected for i in selected):
                continue
            state = snapshot(rows, selected)[0]
            if state.boundary + 2 < CUTOFF:
                continue
            out.setdefault(state, (rows, selected))
    return out


def possible_z(state):
    if not state.spending_parents or state.boundary != CUTOFF:
        return ()
    if not O.choices(state.frontier)[1]:
        return ()
    high_color = (state.colors >> state.high) & 1
    return tuple(i for i in range(len(state.frontier.loose))
                 if state.inside >> i & 1 and ((state.colors >> i) & 1) != high_color)


def state_category(s):
    return s.third_parents, s.high != ABSENT, s.spending_parents, s.shrinks


def explore():
    sources = start_records()
    distance = dict.fromkeys(sources, 3)
    predecessors = dict.fromkeys(sources)
    queue = deque(sources)
    counts, edges, rejected, observations = Counter(), Counter(), Counter(), Counter()
    survivors = []
    while queue:
        state = queue.popleft()
        cat = state_category(state)
        counts[cat] += 1
        if state.spending_parents and state.boundary == CUTOFF and O.choices(state.frontier)[1]:
            observations[(*cat, "live_six_shore")] += 1
        zs = possible_z(state)
        if zs:
            survivors.append(state)
        for kind, test in (
            ("any", bool(zs)),
            ("different_small_holder", any(not (state.frontier.adjacent[state.high] >> v & 1) for v in zs)),
            ("sibling_at_true_small_holder", any(state.frontier.adjacent[state.high] >> v & 1 for v in zs)),
            ("whole_ordinary_shore", bool(zs) and state.paid == 0),
            ("proper_ordinary_shore", bool(zs) and state.paid > 0),
            ("spending_child_inside", bool(zs) and state.child_inside),
            ("spending_child_outside", bool(zs) and not state.child_inside),
        ):
            if test:
                key = (*cat, kind)
                observations[key] += 1
        for parents, h, selected in moves(state):
            nxt, why = advance(state, parents, h, selected)
            if nxt is None:
                rejected[why] += 1
                continue
            edges[cat] += 1
            if nxt not in distance:
                distance[nxt] = distance[state] + 1
                predecessors[nxt] = state, parents, h, selected
                queue.append(nxt)
    return sources, distance, predecessors, counts, edges, rejected, observations, survivors


def literal_path(target, sources, distance, predecessors):
    path = []
    here = target
    while predecessors[here] is not None:
        prev, parents, outputs, inside = predecessors[here]
        path.append((prev, here, parents, outputs, inside))
        here = prev
    rows, start = sources[here]
    selected = set(start)
    high, child = ABSENT, ABSENT
    for before, after, parents, outputs, inside in reversed(path):
        got, names, slots = snapshot(rows, selected, before.third_parents, high, child, before.spending_parents)
        assert got == before
        assert parents in OLD.verify_literal_moves(rows, before.frontier, names, slots)
        if outputs == 3 and before.third_parents:
            high = len(rows)
        elif before.high in parents:
            assert child == ABSENT
            child = len(rows)
        if inside:
            selected.add(len(rows))
        rows = J.advance(rows, tuple(names[i] for i in parents), outputs)
        assert snapshot(rows, selected, after.third_parents, high, child, after.spending_parents)[0] == after
    assert len(rows) == distance[target]
    users, graph, colors, boundary = literal_partition(rows, selected)
    zs = tuple(sorted(b for b, holders in users.items()
                      if len(holders) == 1 and holders[0] in selected and colors[holders[0]] != colors[high]))
    events = T.replay(rows)
    assert all(set(events[i]["parents"]) <= selected for i in selected)
    assert len(boundary) == CUTOFF and high in selected and child != ABSENT
    fourth_loose = tuple(b for b in events[high]["fresh"] if len(users[b]) == 1)
    assert len(fourth_loose) == 2 and set(fourth_loose) <= set(boundary)
    assert zs and set(zs) <= set(boundary)
    shared = tuple(b for b in boundary if len(users[b]) == 2)
    assert target.paid == len(shared) and (not shared) == (len(selected) == len(rows))
    menu = O.N.checked_menu(rows)
    assert menu
    return {
        "width": T.width(rows), "junction_supports": rows, "ordinary_shore": sorted(selected),
        "fourth_site": high, "spending_child": child, "boundary": boundary,
        "fourth_loose": fourth_loose, "proposed_z": zs, "shared_boundary_bits": shared,
        "spending_child_loose_outputs": tuple(b for b in events[child]["fresh"] if len(users[b]) == 1),
        "already_adjacent_to_H": tuple(z for z in zs if users[z][0] in graph[high]),
        "current_menu": sorted(menu),
    }


def check_named_pairs(records):
    if not records:
        return []
    with TemporaryDirectory(prefix="one-attachment-shore-measurement-") as tmp:
        binary = T.compiler(Path(tmp) / "table")
        tables = T.all_tables(binary, [record["junction_supports"] for record in records])
    results = []
    for record, table in zip(records, tables, strict=True):
        rows = record["junction_supports"]
        O.N.verify_parity_pairs(rows, table)
        users, _, colors, _ = literal_partition(rows, record["ordinary_shore"])
        h = record["fourth_site"]
        f, g = record["fourth_loose"]
        a = tuple(sorted(set(rows[h]) - {f, g}))
        small_holder = {i: next(u for u in users[i] if u != h) for i in a}
        grades = []
        for z in record["proposed_z"]:
            assert table[f][z] == table[g][z] == CUTOFF
            compatible = tuple(i for i in a if small_holder[i] != users[z][0] and table[z][i] <= CUTOFF)
            possible = tuple(i for i in a if set(a) - {i} <= set(compatible) and i not in record["shared_boundary_bits"])
            grades.append({"candidate": z, "K_to_true_attachments": tuple(table[z][i] for i in a),
                           "compatible_retained_attachments": compatible,
                           "possible_removals_under_necessary_tests": possible})
        other_loose = sum(1 << b for b, ends in users.items() if len(ends) == 1 and colors[ends[0]] != colors[h])
        cuts = [0]
        for scope in T.masks(rows):
            cuts.extend([word ^ scope for word in cuts])
        qualifying = [
            tuple(i for i in range(len(rows)) if subset >> i & 1)
            for subset, cut in enumerate(cuts)
            if subset >> h & 1 and cut.bit_count() == CUTOFF and cut & other_loose
        ]
        assert tuple(record["ordinary_shore"]) in qualifying
        results.append({"true_attachments": a, "named_pair_controls": grades,
                        "directly_enumerated_qualifying_shores": qualifying})
    return results


def child_projections(survivors):
    # Forget the color and shore tags and compare with the exact O quotient
    # which carries the named child. An actual history must have both views.
    if not survivors:
        return []
    prior = O.N.close_prefixes()
    starters, _ = O.all_starts(prior)
    result = O.closure(starters)
    alternatives = defaultdict(list)
    for third, arity, state in chain(result["roots"], result["linked"]):
        shrinks = 10 - third - sum(state.frontier.loose)
        if arity and O.menu_roles(state):
            alternatives[third, arity, shrinks].append(state)
    data = []
    for state in survivors:
        query = state.third_parents, state.spending_parents, state.shrinks
        counts = set()
        z = possible_z(state)
        for other in alternatives[query]:
            if len(other.frontier.loose) != len(state.frontier.loose):
                continue
            for order in permutations(range(len(other.frontier.loose))):
                if order[state.high] != other.fourth or other.frontier.restrict(order) != state.frontier:
                    continue
                child_live = order.index(other.child) if other.child in order else ABSENT
                loose_at_child = state.frontier.loose[child_live] if child_live != ABSENT else 0
                counts.add((loose_at_child, sum(state.frontier.loose[i] for i in z if i == child_live),
                            sum(state.frontier.loose[i] for i in z if i != child_live)))
        assert counts
        data.append([
            {"child_loose_outputs": c, "candidate_z_at_child": at, "candidate_z_elsewhere": elsewhere}
            for c, at, elsewhere in sorted(counts)
        ])
    return data


def main():
    sources, depth, traces, counts, edges, rejected, seen, survivors = explore()
    records = [literal_path(state, sources, depth, traces) for state in survivors]
    pair_control = check_named_pairs(records)
    child_controls = child_projections(survivors)
    out = {
        "maximum_shrinks": MAX_SHRINKS, "maximum_spent_crossings": MAX_PAID,
        "seeded_shore_forms": len(sources), "closed_states": len(depth), "closed_transitions": sum(edges.values()),
        "by_formation_stage": [
            {"third_parents": a, "after_fourth": b, "spending_parents": c, "shrinks": d,
             "states": count, "transitions": edges[a, b, c, d]}
            for (a, b, c, d), count in sorted(counts.items())
        ],
        "rejected_projected_transitions": dict(sorted(rejected.items())),
        "observations": [
            {"third_parents": a, "after_fourth": b, "spending_parents": c, "shrinks": d, "case": k, "states": count}
            for (a, b, c, d, k), count in sorted(seen.items())
        ],
        "shortest_named_representative_per_surviving_state": [
            {"paid_crossings": state.paid, "child_inside": state.child_inside,
             "bipartition_of_fourth": (state.colors >> state.high) & 1,
             "child_occupancy_from_uncolored_projection": control, **record, **graded}
            for state, record, graded, control in zip(survivors, records, pair_control, child_controls, strict=True)
        ],
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
