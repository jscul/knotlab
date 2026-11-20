"""Compute minimum physical bond sizes and replay the built parity controls."""

from argparse import ArgumentParser
from collections import Counter, defaultdict, deque
from functools import cache
from itertools import combinations
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "bond_checks.json"
SMALL_KNOT_LIMIT = 16
SMALL_MARK_LIMIT = 12
sys.path.insert(0, str(ROOT / "tools"))
from knotlab import Relation, check_knot


def incidence(stars):
    """Return the physical holders of each distinction and neighbours of each knot."""
    holders = defaultdict(list)
    for j, support in enumerate(stars):
        for d in support:
            holders[d].append(j)
    neighbours = [set() for _ in stars]
    for row in holders.values():
        if len(row) == 2 and row[0] != row[1]:
            a, b = row
            neighbours[a].add(b)
            neighbours[b].add(a)
        elif len(row) != 1:
            raise ValueError("a distinction must have one or two distinct holders")
    return dict(holders), neighbours


def component(neighbours, allowed):
    if not allowed:
        return set()
    seen = {min(allowed)}
    todo = list(seen)
    while todo:
        more = (neighbours[todo.pop()] & allowed) - seen
        seen.update(more)
        todo.extend(more)
    return seen


def loose_bond_tightness(stars, marks):
    """Whether the minimum canonical bond size through these loose marks is |marks|.

    In a connected written presentation the full loose support is the only
    nonempty dual support consisting solely of loose distinctions. At least
    three distinctions are required for a canonical bond.
    """
    stars = tuple(tuple(s) for s in stars)
    holders, neighbours = incidence(stars)
    if not stars or len(component(neighbours, set(range(len(stars))))) != len(stars):
        raise ValueError("loose tightness requires a connected written presentation")
    loose = frozenset(d for d, row in holders.items() if len(row) == 1)
    marks = frozenset(marks)
    if not marks or not marks <= loose:
        raise ValueError("provide a nonempty set of actual loose distinctions")
    return len(marks) >= 3 and marks == loose


def mask(support):
    return sum(1 << d for d in support)


def basis(words):
    result = {}
    for word in words:
        while word:
            p = word.bit_length()
            if p in result:
                word ^= result[p]
            else:
                result[p] = word
                break
    return result


def parity_implied(words, target):
    independent = basis(words)
    while target:
        p = target.bit_length()
        if p not in independent:
            return False
        target ^= independent[p]
    return True


@cache
def canonical_even(arity):
    names = tuple(str(i) for i in range(arity))
    parity = Relation.from_predicate(names, lambda values: sum(values.values()) % 2 == 0)
    return check_knot(parity, names[:-1], names[-1]).is_knot


def check_projections(stars):
    """The actual projection of the whole allowed relation on every written support."""
    words = tuple(map(mask, stars))
    rank = len(basis(words))
    for star, w in zip(stars, words, strict=True):
        if len(star) < 3 or rank - len(basis(other & ~w for other in words)) != 1:
            raise AssertionError(f"the projection on {star} is not a canonical parity knot")
        if len(star) <= 8:
            assert canonical_even(len(star))
    return rank


def row_span(stars):
    span = [0]
    for word in basis(map(mask, stars)).values():
        span.extend(w ^ word for w in tuple(span))
    return span


def span_minimal_supports(stars):
    minimal = []
    for w in sorted(row_span(stars)[1:], key=lambda w: (w.bit_count(), w)):
        if not any((w & kept) == kept for kept in minimal):
            minimal.append(w)
    return [w for w in minimal if w.bit_count() >= 3]


def bits(items):
    return sum(1 << d for d in set(items))


def connected_mask(neighbours, allowed):
    hit = allowed & -allowed
    todo = hit
    unseen = allowed ^ hit
    while todo:
        b = todo & -todo
        todo ^= b
        new = unseen & neighbours[b.bit_length() - 1]
        todo |= new
        unseen ^= new
    return not unseen


def connected_cut_supports(stars):
    """Enumerate physical cut supports. The auxiliary exterior is always outside."""
    holders, neighbours = incidence(stars)
    outer = len(stars)
    neighbours.append(set())
    links = []
    for d, v in holders.items():
        if len(v) == 1:
            neighbours[outer].add(v[0])
            neighbours[v[0]].add(outer)
            v = [v[0], outer]
        links.append((1 << d, 1 << v[0], 1 << v[1]))
    end = 1 << outer
    if not neighbours[outer]:
        end >>= 1
        neighbours.pop()
    neighbour_masks = tuple(map(bits, neighbours))
    full = (end << 1) - 1
    answer = {}
    for side in range(1, end):
        if connected_mask(neighbour_masks, side) and connected_mask(neighbour_masks, full ^ side):
            w = sum(d for d, left, right in links if bool(side & left) != bool(side & right))
            if w.bit_count() >= 3:
                answer[w] = [j for j in range(outer) if side & (1 << j)]
    return answer


def small_bonds(stars):
    stars = tuple(tuple(row) for row in stars)
    if not 0 < len(stars) <= SMALL_KNOT_LIMIT:
        raise ValueError(f"complete small cut enumeration permits at most {SMALL_KNOT_LIMIT} knots")
    holders, neighbours = incidence(stars)
    if len(component(neighbours, set(range(len(stars))))) != len(stars):
        raise ValueError("the small cut checker expects an ordinarily connected presentation")
    physical = connected_cut_supports(stars)
    if len(stars) <= 12:
        assert physical.keys() == set(span_minimal_supports(stars))
    return dict(sorted(physical.items(), key=lambda entry: (entry[0].bit_count(), entry[0])))


def small_bond_table(stars, marks):
    """Exact minimum canonical bond size through every nonempty subset of marks."""
    marks = tuple(sorted(set(marks)))
    if not 0 < len(marks) <= SMALL_MARK_LIMIT:
        raise ValueError(f"the small table permits 1 to {SMALL_MARK_LIMIT} marks")
    stars = tuple(tuple(row) for row in stars)
    holders, _ = incidence(stars)
    if not holders.keys() >= set(marks):
        raise ValueError("all marks must be physical distinctions")
    return table_from_bonds(small_bonds(stars), marks)


def minimum_size(sorted_bonds, marked):
    bond = next((w for w in sorted_bonds if w & marked == marked), None)
    return bond.bit_count() if bond is not None else None


def table_from_bonds(sorted_bonds, marks):
    return {q: minimum_size(sorted_bonds, mask(q))
            for order in range(1, len(marks) + 1) for q in combinations(marks, order)}


def minimum_distinguishing_query(left, right, mark_union):
    """Full comparison certified by the projected supports of actual bonds."""
    marked = mask(mark_union)
    intersections = {b & marked for b in (*left, *right)} - {0}
    if all(minimum_size(left, w) == minimum_size(right, w) for w in intersections):
        return {"equal_everywhere": True, "checked_bond_intersections": len(intersections)}
    for arity in range(1, len(mark_union) + 1):
        first = None
        sizes = [Counter(), Counter()]
        for q in combinations(mark_union, arity):
            l, r = (minimum_size(b, mask(q)) for b in (left, right))
            sizes[0][l] += 1
            sizes[1][r] += 1
            if l != r and first is None:
                first = {"marks": q, "closing_size": l, "extra_size": r}
        if first is not None:
            return {"equal_everywhere": False, "checked_bond_intersections": len(intersections), "first_difference": first,
                    "histograms_at_that_order": [[{"size": n, "count": c} for n, c in h.items()] for h in sizes],
                    "unequal_under_any_renaming_at_that_order": sizes[0] != sizes[1]}
    raise AssertionError("unequal bond intersection evaluations have a distinguishing query")


def exact_small_states(stars, nae=False):
    names = tuple(sorted(incidence(stars)[0]))
    if len(names) > 15:
        raise ValueError("literal assignment enumeration is reserved for at most 15 distinctions")
    locations = dict(zip(names, range(len(names)), strict=True))
    supports = [mask(locations[d] for d in row) for row in stars]
    predicate = (lambda x, w: 0 < (x & w) < w) if nae else (lambda x, w: (x & w).bit_count() % 2 == 0)
    values = tuple(mask(d for i, d in enumerate(names) if (x >> i) & 1)
                   for x in range(1 << len(names)) if all(predicate(x, w) for w in supports))
    return names, values


def nae_bonds(names, states):
    minimal = []
    for size in range(1, len(names) + 1):
        for support in combinations(names, size):
            w = mask(support)
            if not any(w & q == q for q in minimal):
                if len({a & w for a in states}) < (1 << size):
                    minimal.append(w)
    return [w for w in minimal if w.bit_count() >= 3]


def check_explicit_states(stars, states, nae=False):
    assert states
    for s in stars:
        names = tuple(str(d) for d in s)
        rows = frozenset(tuple(bool(a & (1 << d)) for d in s) for a in states)
        p = Relation(names, rows)
        expected = Relation.from_predicate(
            names, lambda v: 0 < sum(v.values()) < len(names) if nae else sum(v.values()) % 2 == 0)
        assert p == expected and check_knot(p, names[:-1], names[-1]).is_knot


def projected_values(states, marks):
    return sorted({tuple(int(bool(a & (1 << d))) for d in marks) for a in states})


def nae_lifts(old, stage, states):
    previous_names = set(incidence(old)[0])
    fresh = tuple(sorted(set(incidence(stage)[0]) - previous_names))
    new = tuple(map(mask, stage[len(old):]))
    assignments = [mask(d for i, d in enumerate(fresh) if (x >> i) & 1) for x in range(1 << len(fresh))]
    result = []
    for a in states:
        before = len(result)
        for f in assignments:
            x = a | f
            if all(0 < (x & w) < w for w in new):
                result.append(x)
        assert len(result) > before
    check_explicit_states(stage, result, nae=True)
    return result


def steps_from(graph, start):
    distance = {start: 0}
    queue = deque([start])
    while queue:
        u = queue.popleft()
        for v in graph[u] - distance.keys():
            distance[v] = distance[u] + 1
            queue.append(v)
    return distance


def ordinary_readings(stars, marks):
    holders, neighbours = incidence(stars)
    live = {row[0] for row in holders.values() if len(row) == 1}
    current = {v: {u for u in live - {v} if neighbours[u] & neighbours[v]} for v in live}
    rows = []
    for a, b in combinations(marks, 2):
        [u], [v] = holders[a], holders[b]
        step = steps_from(neighbours, u)[v]
        rows.append({"marks": [a, b], "end_steps": steps_from(current, u).get(v),
                     "ordinary_holder_steps": step, "ordinary_distinction_steps": step + 1})
    return rows


def unchanged_on_renaming(stars, marks, expected):
    names = sorted(incidence(stars)[0])
    recode = dict(zip(names, (3 * i + 19 for i in reversed(range(len(names)))), strict=True))
    moved = tuple(tuple(recode[d] for d in reversed(row)) for row in reversed(stars))
    actual = small_bond_table(moved, (recode[d] for d in marks))
    return all(actual[tuple(sorted(recode[d] for d in q))] == n for q, n in expected.items())


def candidate_groups(live, witnesses):
    live = tuple(sorted(live))
    witnessed = {frozenset(q) for q in witnesses if len(q) >= 2}
    pairs = {frozenset(pair) for q in witnessed for pair in combinations(q, 2)}
    groups = []
    for arity in range(len(live), 2, -1):
        for row in combinations(live, arity):
            q = frozenset(row)
            if all(frozenset(p) in pairs for p in combinations(row, 2)) and not any(
                    q <= other for other in (*witnessed, *groups)):
                groups.append(q)
    return tuple(tuple(sorted(q)) for q in groups + sorted(
        (q for q in pairs if not any(q <= g for g in groups)), key=sorted))


def replay_round(stars, first_fresh=None, nae_states=None):
    """Independent literal complete-round replay on a small built front."""
    holders, neighbours = incidence(stars)
    loose = defaultdict(list)
    for d, row in holders.items():
        if len(row) == 1:
            loose[row[0]].append(d)
    live = set(loose)
    groups = candidate_groups(live, [live & row for row in neighbours])
    funding = Counter(x for row in groups for x in row)
    shortages = [[j, len(loose[j]), funding[j]] for j in sorted(live) if len(loose[j]) < funding[j]]
    if shortages:
        return stars, {"status": "stalled", "groups": groups, "shortages": shortages, "births": []}
    if not live:
        return stars, {"status": "closed", "births": []}
    roster = groups + tuple((j,) for j in sorted(live) for _ in range(len(loose[j]) - funding[j]))
    by_parent = [{i for i, row in enumerate(roster) if j in row} for j in live]
    demand = Counter(i for row in candidate_groups(range(len(roster)), by_parent) for i in row)
    allocated = {j: iter(sorted(ds)) for j, ds in loose.items()}
    next_name = max(holders) + 1 if first_fresh is None else first_fresh
    assert next_name > max(holders)
    words = tuple(map(mask, stars))
    births = []
    for i, row in enumerate(roster):
        spent = tuple(next(allocated[j]) for j in row)
        marked = mask(spent)
        if nae_states is None:
            implied = parity_implied(words, marked)
        else:
            implied = all(0 < (a & marked) < marked for a in nae_states)
        count = 0 if implied else max(1, 3 - len(row), demand[i])
        assert not implied or (len(roster) == 1 and demand[i] == 0)
        fresh = tuple(range(next_name, next_name + count))
        births.append({"parents": row, "spent": spent, "fresh": fresh, "demand": demand[i], "implied": implied})
        next_name += count
    child = stars + tuple(x["spent"] + x["fresh"] for x in births)
    return child, {"status": "open" if any(x["fresh"] for x in births) else "closed", "births": births}


def four_knot_sources():
    base = ((0, 1, 2), (0, 3, 4), (1, 5, 6), (2, 7, 8))
    extra = ((0, 1, 2, 9), *base[1:])
    underfunded = ((0, 1, 2, 4), *base[1:])
    restored = (underfunded[0], (0, 3, 4, 9), *base[2:])
    return base, extra, underfunded, restored


def four_knot_controls():
    base, extra, underfunded, restored = four_knot_sources()
    stages = []
    search_tables = []
    for name, stars in (("closing", base), ("extra", extra)):
        reached, first = replay_round(stars, first_fresh=16)
        successor, second = replay_round(reached)
        assert len(first["births"]) == (3 if name == "closing" else 4)
        parents = range(len(stars), len(stars) + 3)
        marks = tuple(r["fresh"][0] for r in first["births"][:3])
        assert len(marks) == 3 and second["births"][0]["spent"] == marks
        assert len(second["births"][0]["fresh"]) == (name == "extra")
        parent_mark_union = tuple(sorted(d for j in parents for d in reached[j]))
        assert len(set(parent_mark_union)) == 9
        table = small_bond_table(reached, parent_mark_union)
        assert unchanged_on_renaming(reached, parent_mark_union, table)
        assert loose_bond_tightness(reached, marks) == (name == "closing")
        assert table[marks] == (3 if name == "closing" else 4)
        parity_rows = [exact_small_states(q)[1] for q in (stars, reached)]
        for stage, values in zip((stars, reached), parity_rows, strict=True):
            check_explicit_states(stage, values)
        nae_source = exact_small_states(stars, nae=True)[1]
        check_explicit_states(stars, nae_source, nae=True)
        nae_reached, _ = replay_round(stars, first_fresh=16, nae_states=nae_source)
        assert nae_reached == reached
        names, nae_states = exact_small_states(reached, nae=True)
        check_explicit_states(reached, nae_states, nae=True)
        nae_next, nae_step = replay_round(reached, nae_states=nae_states)
        assert len(nae_step["births"][0]["fresh"]) == 1
        nae_table = table_from_bonds(nae_bonds(names, nae_states), marks)
        old_nae_projection = projected_values(nae_states, marks)
        assert len(old_nae_projection) == 8
        nae_next_states = nae_lifts(reached, nae_next, nae_states)
        search_tables.append(table)
        stages.append({"case": name, "source": stars, "reached": reached, "successor": successor,
                       "first": first, "second": second, "projection_ranks": list(map(check_projections, (stars, reached, successor))),
                       "marked_loose_inputs": marks, "parent_support_union": parent_mark_union,
                       "loose_input_minima": [{"marks": q, "size": b} for q, b in table.items() if set(q) <= set(marks)],
                       "ordinary_readings": ordinary_readings(reached, marks), "renaming_of_511_queries": True,
                       "literal_parity_reached_input_assignments": projected_values(parity_rows[1], marks),
                       "not_all_equal": {"literal_input_assignments": old_nae_projection,
                                         "state_counts_by_age": [len(nae_source), len(nae_states), len(nae_next_states)],
                                         "loose_input_minima": [{"marks": q, "size": b} for q, b in nae_table.items()],
                                         "all_earlier_rows_extend": True, "next": nae_step}})
    left, right = search_tables
    assert left.keys() == right.keys()
    by_order = [{"order": k, "queries": n, "changed": sum(left[q] != right[q] for q in left if len(q) == k)}
                for k, n in sorted(Counter(map(len, left)).items())]
    failed, poor = replay_round(underfunded)
    renewed, funded = replay_round(restored)
    assert failed == underfunded and poor["status"] == "stalled" and len(poor["shortages"]) == 1
    assert funded["status"] == "open" and len(funded["births"]) == 3
    return {"paired_examples": stages,
            "parent_support_queries_by_order": by_order,
            "parent_support_table": [{"marks": q, "closing_size": left[q], "extra_size": right[q]} for q in left],
            "funding_control": {"underfunded": underfunded, "restored": restored, "refused": poor, "funded": funded,
                                "projection_ranks": list(map(check_projections, (underfunded, restored, renewed)))}}


def two_common_holders(p, extra):
    h1, h2, other = 0, 1, 2
    parents = tuple(range(3, p + 3))
    main, (v, w) = parents[:-2], parents[-2:]
    stars = [[] for _ in range(p + 3)]
    meetings = [(h, j) for h in (h1, h2) for j in main]
    meetings += [(h1, v), (h2, w), (other, v), (other, v), (other, w), (other, w)]
    if p == 3:
        # The ternary instance needs both common holders to have at least three places.
        meetings += [(h1, main[0]), (h2, main[0])]
    for d, (u, j) in enumerate(meetings):
        stars[u].append(d)
        stars[j].append(d)
    names = tuple(range(len(meetings), len(meetings) + p))
    for j, d in zip(parents, names, strict=True):
        stars[j].append(d)
    if extra:
        stars[other].append(names[-1] + 1)
    return tuple(map(tuple, stars)), parents, names


def same_selected_deck(p):
    left, parents, names = two_common_holders(p, extra=False)
    right, _, _ = two_common_holders(p, extra=True)
    selected = names[:-2]
    full_parent_marks = tuple(sorted({d for j in parents for d in left[j]}))
    bonds = [small_bonds(stars) for stars in (left, right)]
    l, r = (table_from_bonds(b, names) for b in bonds)
    assert all(l[q] == r[q] == (3 if len(q) == 1 else p) for q in l if set(q) <= set(selected))
    assert all(l[q] == p and r[q] > p for q in l if len(q) == p - 1)
    assert unchanged_on_renaming(left, names, l) and unchanged_on_renaming(right, names, r)
    replay = []
    for extra, stars in enumerate((left, right)):
        next_stars, report = replay_round(stars)
        birth = report["births"][0]
        assert birth["parents"] == parents and birth["spent"] == names
        assert len(birth["fresh"]) == extra and birth["implied"] == (not extra)
        assert loose_bond_tightness(stars, names) == (not extra)
        replay.append({"source": stars, "growth": report, "successor": next_stars,
                       "projection_ranks": [check_projections(s) for s in (stars, next_stars)]})
    return {"input_arity": p, "marks": names, "restricted_main_marks": selected, "ternary_arity_padding": p == 3,
            "full_input_minima": [{"marks": q, "closing_size": l[q], "extra_size": r[q]} for q in l],
            "entire_restricted_deck_matches": True, "all_mark_recodings_checked": True,
            "full_parent_supports": full_parent_marks,
            "full_parent_comparison": minimum_distinguishing_query(*bonds, full_parent_marks), "replays": replay}


def binary_exception():
    left = ((0, 1, 2, 3), (0, 1, 4), (2, 3, 5))
    right = ((*left[0], 6), *left[1:])
    names = (4, 5)
    marks = [small_bond_table(s, names) for s in (left, right)]
    assert [m[names] for m in marks] == [None, 3]
    assert all(m[(4,)] == m[(5,)] == 3 for m in marks)
    replay = []
    for extra, stars in enumerate((left, right)):
        grown, report = replay_round(stars)
        check_projections(stars)
        rows = projected_values(exact_small_states(stars)[1], names)
        assert len(rows) == 2 + 2 * extra
        first = report["births"][0]
        assert first["parents"] == (1, 2) and first["implied"] == (not extra)
        add_one_under_floor = [(*row, row[0] ^ row[1]) for row in rows]
        if not extra:
            assert len(first["fresh"]) == 0 and report["status"] == "closed" and set(grown[-1]) == set(names)
            assert {row[-1] for row in add_one_under_floor} == {0}
        replay.append({"source": stars, "next": report, "literal_input_assignments": rows,
                       "literal_projection_if_forcing_one_output": add_one_under_floor})
    return {"marks": names, "minimum_bond_sizes": [{"marks": q, "closing_size": marks[0][q], "extra_size": marks[1][q]}
                                                     for q in marks[0]],
            "replays": replay, "closed_binary_support_is_subternary": True}


def min_cut_control():
    stars = ((0, 1, 4), (0, 1, 2, 3, 6, 7, 8, 9, 10), (2, 3, 5))
    marks = (4, 5)
    query = mask(marks)
    arbitrary = min(w.bit_count() for w in row_span(stars) if w & query == query)
    bond_size = small_bond_table(stars, marks)[marks]
    assert (arbitrary, bond_size) == (6, 7)
    return {"stars": stars, "marks": marks, "projection_rank": check_projections(stars),
            "smaller_disconnected_cut_support": (0, 1, 2, 3, 4, 5),
            "arbitrary_cut_size": arbitrary, "connected_shores_bond_size": bond_size}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    result = {"units": "size of smallest canonical bond containing all marks; null means absent",
              "four_knot_controls": four_knot_controls(), "binary_exception": binary_exception(),
              "same_restricted_deck": [same_selected_deck(p) for p in (3, 4, 5, 6)],
              "min_cut_control": min_cut_control()}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
