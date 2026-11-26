"""Rebuild the controls, the three-ring cuts and the not-all-equal reads."""

import argparse
from collections import Counter, defaultdict, deque
from contextlib import nullcontext
from dataclasses import dataclass
from itertools import combinations, product
import json
from pathlib import Path
import resource
from time import perf_counter

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ARMS = ("ordinary", "one_fewer", "arity_floor")
CAP = 500


class Start:
    def __init__(self, count):
        self.rows = [[] for _ in range(count)]
        self.next_name = 0

    def knot(self):
        self.rows.append([])
        return len(self.rows) - 1

    def distinction(self, *holders, count=1):
        names = tuple(range(self.next_name, self.next_name + count))
        self.next_name += count
        for k in holders:
            self.rows[k].extend(names)
        return names

    def cycle(self, knots):
        return tuple(self.distinction(a, b)[0] for a, b in zip(knots, knots[1:] + knots[:1]))

    def supports(self):
        return tuple(map(tuple, self.rows))


def ring_start(ring_count, size, attachment, link, edit=""):
    start = Start(ring_count * size)
    rings = [tuple(range(i * size, (i + 1) * size)) for i in range(ring_count)]
    for ring in rings:
        start.cycle(ring)
    carriers = [tuple(d for k in ring for d in start.distinction(k, count=2)) for ring in rings]
    attachment_number = Counter()
    connectors = []
    middles = []
    for i, j in combinations(range(ring_count), 2):
        a, b = start.knot(), start.knot()
        connectors.extend((a, b))
        for r, k in ((i, a), (j, b)):
            p = attachment_number[r]
            places = (2 * p, 2 * p) if attachment == "paired" else (p, p + 2)
            for place in places:
                start.distinction(rings[r][place % size], k)
            attachment_number[r] += 1
        if edit == "links made loose":
            for k in (a, b):
                start.distinction(k, count=2)
        else:
            start.distinction(a, b)
            if link == "double":
                start.distinction(a, b)
            else:
                preceding = a
                for position in range(3):
                    k = start.knot()
                    start.distinction(preceding, k, count=2)
                    preceding = k
                    if position == 1:
                        middles.append(k)
                start.distinction(preceding, b, count=2)
    if edit == "one loose at the middle knot of a detour":
        start.distinction(middles[0])
    if edit == "one loose at a connecting knot":
        start.distinction(connectors[0])
    if edit == "middles joined":
        assert len(middles) == 3
        for a, b in combinations(middles, 2):
            start.distinction(a, b)
        for k in middles:
            start.distinction(k)
    return start.supports(), rings, carriers, tuple(middles)


def two_joining_knots(variant):
    start = Start(14)
    carriers = []
    for i in range(0, 12, 4):
        carriers.append(start.cycle(tuple(range(i, i + 4))))
        for k in (i + 1, i + 3):
            start.distinction(k, count=2)
        start.distinction(i, 12)
        start.distinction(i + 2, 13)
    if variant != "no v":
        start.distinction(12, 13)
    if variant in {"J loose", "J two loose"}:
        start.distinction(12, count=1 if variant == "J loose" else 2)
    return start.supports(), carriers


def owners(rows):
    result = defaultdict(list)
    for k, row in enumerate(rows):
        for d in row:
            result[d].append(k)
    assert all(len(holders) in (1, 2) for holders in result.values())
    return result


def shared_neighbours(rows, ownership):
    result = [set() for _ in rows]
    for holders in ownership.values():
        if len(holders) == 2:
            a, b = holders
            result[a].add(b)
            result[b].add(a)
    return result


def parent_groups(neighbours, live):
    # Two live knots are candidates if they both meet another knot.
    candidate = {k: set() for k in live}
    for meeting in neighbours:
        for a, b in combinations(meeting & live, 2):
            candidate[a].add(b)
            candidate[b].add(a)

    # The no-common-neighbour condition persists when a set gains a member.
    # Thus a maximal valid set is a maximal candidate clique with that condition.
    large = []

    def visit(group, remaining, earlier):
        if not remaining and not earlier:
            if len(group) >= 3 and not set.intersection(*(neighbours[k] for k in group)):
                large.append(tuple(sorted(group)))
            return
        if len(group) + len(remaining) < 3:
            return
        for k in sorted(remaining):
            visit((*group, k), remaining & candidate[k], earlier & candidate[k])
            remaining.remove(k)
            earlier.add(k)

    visit((), {k for k in live if candidate[k]}, set())
    covered = {pair for group in large for pair in combinations(group, 2)}
    pairs = [(a, b) for a, b in combinations(sorted(live), 2) if b in candidate[a] and (a, b) not in covered]
    return sorted(large) + pairs


def mask(names):
    return sum(1 << d for d in names)


def row_space(rows, existing=None):
    basis = {} if existing is None else existing.copy()
    for row in rows:
        row = residue(row, basis)
        if row:
            basis[row.bit_length() - 1] = row
    return basis


def residue(row, basis):
    # Keep nonpivot positions while eliminating every lower pivot too.
    remainder = 0
    while row:
        p = row.bit_length() - 1
        if p in basis:
            row ^= basis[p]
        else:
            remainder |= 1 << p
            row ^= 1 << p
    return remainder


def add_nae(solver, rows, names):
    for row in rows:
        literals = [names[d] for d in row]
        solver.add_clause(literals)
        solver.add_clause([-lit for lit in literals])


@dataclass(frozen=True)
class Birth:
    knot: int
    parents: tuple
    inputs: tuple
    fresh: tuple
    next_demand: int
    ordinary_count: int


def grow(rows, law, arm):
    ownership = owners(rows)
    neighbours = shared_neighbours(rows, ownership)
    available = {k: deque(d for d in row if len(ownership[d]) == 1) for k, row in enumerate(rows)}
    live = {k for k, loose in available.items() if loose}
    if not live:
        return rows, "closed", (), {}
    groups = parent_groups(neighbours, live)
    demand = Counter(k for group in groups for k in group)
    shortages = {k: demand[k] - len(available[k]) for k in sorted(live) if demand[k] > len(available[k])}
    if shortages:
        return rows, "stalled", (), shortages
    groups += [(k,) for k in sorted(live) for _ in range(len(available[k]) - demand[k])]
    inputs = [tuple(available[k].popleft() for k in group) for group in groups]
    assert set(d for group in inputs for d in group) == {d for d, ks in ownership.items() if len(ks) == 1}

    # The count reads demand as if every proposed birth can participate once more.
    forward = [set(near) for near in neighbours] + [set(group) for group in groups]
    new_knots = range(len(rows), len(forward))
    for i, group in zip(new_knots, groups, strict=True):
        for k in group:
            forward[k].add(i)
    next_demand = Counter(k for group in parent_groups(forward, set(new_knots)) for k in group)

    next_name = max(ownership) + 1
    additions = []
    births = []
    names = {d: d + 1 for d in ownership}
    laws = row_space(map(mask, rows)) if law == "parity" else None
    with Solver(name="maplesat") if law == "nae" else nullcontext() as solver:
        if solver is not None:
            add_nae(solver, rows, names)
        for knot, group, consumed in zip(new_knots, groups, inputs, strict=True):
            if solver is None:
                implied = residue(mask(consumed), laws) == 0
            else:
                # Not-all-equal is unchanged by flipping every distinction.
                implied = not solver.solve(assumptions=[names[d] for d in consumed])
            floor = max(0, 3 - len(group))
            ordinary = next_demand[knot] if implied else max(floor, 1, next_demand[knot])
            count = ordinary
            if arm == "one_fewer":
                count = min(ordinary, max(floor, ordinary - 1))
            if arm == "arity_floor":
                count = min(ordinary, floor)
            fresh = tuple(range(next_name, next_name + count))
            next_name += ordinary
            additions.append((*sorted(consumed), *fresh))
            births.append(Birth(knot, group, tuple(sorted(consumed)), fresh, next_demand[knot], ordinary))
    return rows + tuple(additions), "funded", tuple(births), {}


def words(width):
    return tuple(product((0, 1), repeat=width))


def parity_tuples(law_masks, carrier_masks, known_zero=()):
    laws = row_space((*law_masks, *(1 << d for d in known_zero)))
    reduced = [residue(f, laws) for f in carrier_masks]
    equations = []
    for size in range(1, len(reduced) + 1):
        for selected in combinations(range(len(reduced)), size):
            total = 0
            for i in selected:
                total ^= reduced[i]
            if not total:
                equations.append(selected)
    return ["".join(map(str, w)) for w in words(len(reduced)) if all(sum(w[i] for i in eq) % 2 == 0 for eq in equations)]


def nae_read(rows, carriers):
    # Join the input parities in pairs so each imposed table has three places.
    ownership = owners(rows)
    names = {d: i for i, d in enumerate(sorted(ownership), 1)}
    next_name = len(names) + 1
    roots = []
    result = []
    with Solver(name="maplesat") as solver:
        add_nae(solver, rows, names)
        for carrier in carriers:
            current = deque(names[d] for d in carrier)
            assert current
            while len(current) > 1:
                a, b = current.popleft(), current.popleft()
                for x, y, z in words(3):
                    if x ^ y ^ z:
                        solver.add_clause([(-d if value else d) for d, value in zip((a, b, next_name), (x, y, z))])
                current.append(next_name)
                next_name += 1
            roots.append(current.pop())
        for w in words(len(carriers)):
            assumptions = [root if val else -root for root, val in zip(roots, w)]
            if solver.solve(assumptions=assumptions):
                true = {i for i in solver.get_model() if i > 0}
                assert all(0 < sum(names[d] in true for d in row) < len(row) for row in rows)
                assert tuple(sum(names[d] in true for d in carrier) % 2 for carrier in carriers) == w
                result.append("".join(map(str, w)))

        # One actual one-distinction move that changes a carrier suffices to
        # rule out invariance under either reading. For an incident knot to
        # allow both values of d, its other distinctions must take both values.
        selectors = {}
        for d in {d for carrier in carriers for d in carrier}:
            selectors[d] = next_name
            for k in ownership[d]:
                other = [names[e] for e in rows[k] if e != d]
                solver.add_clause([-next_name, *other])
                solver.add_clause([-next_name, *(-e for e in other)])
            next_name += 1
        changing = []
        for carrier in carriers:
            witness = None
            for d in carrier:
                if solver.solve(assumptions=[selectors[d]]):
                    state = {e for e in solver.get_model() if e > 0}
                    toggled = state ^ {names[d]}
                    for assignment in (state, toggled):
                        assert all(0 < sum(names[e] in assignment for e in row) < len(row) for row in rows)
                    witness = d
                    break
            changing.append(witness)
    return {"tuples": result, "one distinction changes this carrier": changing}


def incidence(rows):
    links = {}
    outside = len(rows)
    adjacency = [[] for _ in range(outside + 1)]
    for d, holders in owners(rows).items():
        a, b = holders if len(holders) == 2 else (holders[0], outside)
        links[d] = (a, b)
        adjacency[a].append((b, d))
        adjacency[b].append((a, d))
    return links, adjacency


def short_cycles(links, adjacency):
    unique = set()
    multiplicity = 0
    for d, (a, b) in links.items():
        levels = {a: 0}
        queue = deque([a])
        while queue:
            k = queue.popleft()
            if b in levels and levels[k] >= levels[b]:
                break
            for j, e in adjacency[k]:
                if e != d and j not in levels:
                    levels[j] = levels[k] + 1
                    queue.append(j)
        if b not in levels:
            continue
        paths = [(b, 1 << d)]
        while paths:
            k, chosen = paths.pop()
            if k == a:
                unique.add(chosen)
                multiplicity += 1
                continue
            for j, e in adjacency[k]:
                if e != d and levels.get(j) == levels[k] - 1:
                    paths.append((j, chosen | (1 << e)))
    return unique, multiplicity


def cycles_through_five(adjacency):
    # Any small change is a disjoint sum of simple cycles, including pairs of
    # distinctions with the same holders. Testing these generators suffices.
    found = set()
    for first in range(len(adjacency)):
        todo = [(first, 0, 1 << first, 0)]
        while todo:
            k, used, visited, length = todo.pop()
            for j, d in adjacency[k]:
                bit = 1 << d
                if used & bit:
                    continue
                if j == first:
                    if length:
                        found.add(used | bit)
                elif j > first and not ((visited >> j) & 1) and length < 4:
                    todo.append((j, used | bit, visited | (1 << j), length + 1))
    return found


def parity_read(rows, carriers):
    laws = tuple(map(mask, rows))
    basis = row_space(laws)
    forms = tuple(map(mask, carriers))
    allowed = parity_tuples(laws, forms)
    links, adjacency = incidence(rows)
    shortest, shortest_through_each = short_cycles(links, adjacency)
    upto_five = cycles_through_five(adjacency)
    local_possible = [len({w[i] for w in allowed}) == 2 for i in range(len(forms))]
    # A class fact is readable by one knot exactly when it is a function of
    # that knot's distinctions on the allowed states. If the fact is invariant,
    # every representative of it is invariant too.
    determined = [False] * len(forms)
    for row in rows:
        known = row_space((1 << d for d in row), basis)
        for i, f in enumerate(forms):
            determined[i] |= residue(f, known) == 0

    def verdict(moves):
        invariant = [not any((f & move).bit_count() % 2 for move in moves) for f in forms]
        return [[kept and free, not (kept and reads)] for kept, free, reads in zip(invariant, local_possible, determined)]

    return {
        "tuples": allowed,
        "carrier sizes": list(map(len, carriers)),
        "shortest": verdict(shortest),
        "through five": verdict(upto_five),
        "determined by one knot": determined,
        "distinct shortest changes": len(shortest),
        "shortest changes counted through each distinction": shortest_through_each,
        "simple changes through size five": len(upto_five),
    }


def trajectory(start, rings, start_carriers, law="parity", arm="ordinary", keep_later_nae=False):
    rows = start
    lineage = {k: i for i, ring in enumerate(rings) for k in ring}
    previous_carriers = None
    for age in range(4):
        births = ()
        if age:
            rows, fate, births, shortages = grow(rows, law, arm)
            if fate != "funded":
                yield {"round": age, "end": fate, "shortages": shortages}, rows, births
                break
        n = len(owners(rows))
        data = {"round": age, "knots": len(rows), "distinctions": n}
        if n <= CAP:
            data["start carriers"] = (parity_read(rows, start_carriers) if law == "parity"
                                      else nae_read(rows, start_carriers))
        else:
            data["start carriers not read"] = True
            if law == "nae" and keep_later_nae:
                data["additional old-carrier check above cap"] = nae_read(rows, start_carriers)
        if previous_carriers and (n <= CAP or (law == "nae" and keep_later_nae)):
            data["new carriers"] = (parity_read(rows, previous_carriers) if law == "parity"
                                    else nae_read(rows, previous_carriers))
        yield data, rows, births
        if n > CAP:
            break
        if births and rings:
            new_carriers = [[] for _ in rings]
            for birth in births:
                descent = {lineage.get(k) for k in birth.parents}
                if len(descent) == 1 and None not in descent:
                    ring = next(iter(descent))
                    lineage[birth.knot] = ring
                    new_carriers[ring].extend(birth.fresh)
            previous_carriers = new_carriers if all(new_carriers) else None


def law_deletion(rows, births, start, carriers, middles):
    masks = tuple(map(mask, rows))
    old_forms = tuple(map(mask, carriers))
    zero_fresh = [b for b in births if not b.fresh]
    middle_births = [b for b in zero_fresh if b.parents == middles]
    assert len(middle_births) == 1, (middles, zero_fresh)
    birth = middle_births[0]
    old_names = owners(start)
    stage_names = owners(rows)
    assert all(len(old_names[d]) == 1 for d in birth.inputs)
    assert all(len(stage_names[d]) == 1 for other in births for d in other.fresh)
    summed_old_laws = 0
    summed_carriers = 0
    for row in masks[:len(start)]:
        summed_old_laws ^= row
    for form in old_forms:
        summed_carriers ^= form
    assert summed_carriers ^ summed_old_laws == mask(birth.inputs)

    before = parity_tuples(masks[:len(start)], old_forms)
    after = parity_tuples(masks, old_forms)
    assert before == ["".join(map(str, w)) for w in words(3)]
    assert after == ["000", "011", "101", "110"]
    freeing = [k for k in range(len(rows)) if parity_tuples(masks[:k] + masks[k + 1:], old_forms) == before]
    assert [k for k in freeing if k >= len(start)] == [birth.knot]
    old_laws = row_space(masks[:len(start)])
    added_rank = len(row_space(residue(mask(b.inputs), old_laws) for b in zero_fresh))
    assert residue(mask(birth.inputs), old_laws) != 0
    local_freedom = sum(parity_tuples(masks, old_forms, known_zero=row) == after for row in rows)
    assert local_freedom == len(rows)
    return {
        "birth on the three middle knots": birth.__dict__,
        "all births with no fresh distinction": [b.__dict__ for b in zero_fresh],
        "independent constraints added on the start's distinctions": added_rank,
        "missing law in the start": True,
        "birth law plus every start law equals sum of carriers": True,
        "joint values deleting only this birth law": parity_tuples(masks[:birth.knot] + masks[birth.knot + 1:], old_forms),
        "freeing start laws, of all start laws": [sum(k < len(start) for k in freeing), len(start)],
        "freeing birth laws, of all birth laws": [1, len(births)],
        "knots whose fixed values retain all four tuples, of all knots": [local_freedom, len(rows)],
        "every proper part free": all(len({w[:i] + w[i + 1:] for w in after}) == 4 for i in range(3)),
    }


def projected_laws(rows, keep):
    kept_names = mask(keep)
    outside_basis = {}
    inside = []
    for row in rows:
        equation = mask(row)
        while outside := equation & ~kept_names:
            pivot = outside.bit_length() - 1
            if pivot not in outside_basis:
                outside_basis[pivot] = equation
                break
            equation ^= outside_basis[pivot]
        else:
            inside.append(equation)
    return row_space(inside)


def fixed_names(basis, names):
    return {d for d in names if residue(1 << d, basis) == 0}


def extend_arity_floor(member):
    start, _, carriers, _ = ring_start(*member, "middles joined")
    start_names = owners(start)
    carrier_forms = tuple(map(mask, carriers))
    original_laws = row_space(map(mask, start))
    previous_projection = original_laws
    previous_start_fixed = fixed_names(original_laws, start_names)
    result = []
    rows = start
    last_births = {}
    for age in range(1, 7):
        previous_knots = rows
        rows, status, births, shortages = grow(rows, "parity", "arity_floor")
        if status != "funded":
            blockers = []
            for k, shortage in shortages.items():
                birth = last_births[k]
                blockers.append({
                    "knot": k,
                    "birth parents": list(birth.parents),
                    "loose distinctions held": len(birth.fresh),
                    "loose distinctions required": len(birth.fresh) + shortage,
                })
            result.append({"round": age, "end": status, "blocking knots": blockers})
            break
        stages = tuple(map(mask, rows))
        previous_names = owners(previous_knots)
        previous_laws = row_space(map(mask, previous_knots))
        retained_previous = projected_laws(rows, previous_names)
        retained_start = projected_laws(rows, start_names)
        start_fixed = fixed_names(retained_start, start_names)
        added_previous = len(retained_previous) - len(previous_laws)
        zero_fresh = [b for b in births if not b.fresh]
        local_equations = row_space(residue(mask(b.inputs), previous_laws) for b in zero_fresh)
        assert added_previous == len(local_equations)

        result.append({
            "round": age,
            "knots": len(rows),
            "distinctions": len(owners(rows)),
            "births": len(births),
            "births with no fresh distinction": len(zero_fresh),
            "new independent constraints on previous distinctions": added_previous,
            "new independent constraints on start distinctions": len(retained_start) - len(previous_projection),
            "independent constraints on start distinctions added since round 0": len(retained_start) - len(original_laws),
            "newly fixed previous distinctions": sorted(fixed_names(retained_previous, previous_names) - fixed_names(previous_laws, previous_names)),
            "newly fixed start distinctions": sorted(start_fixed - previous_start_fixed),
            "start carrier tuples": parity_tuples(stages, carrier_forms),
        })
        previous_projection = retained_start
        previous_start_fixed = start_fixed
        last_births = {birth.knot: birth for birth in births}
    return result


def archive(name):
    with (STUDY / name).open() as stream:
        return [json.loads(line) for line in stream]


def compare_read(actual, expected):
    assert (len(actual["tuples"]), len(actual["tuples"][0])) == (expected["tuples"], expected["of"].bit_length() - 1)
    if "carrier sizes" in actual:
        assert actual["carrier sizes"] == expected["carriers"]
        assert actual["shortest"] == expected["SHORT"]
        assert actual["through five"] == expected["UPTO5"]
    if "law deletion" in actual:
        raw = expected["laws whose removal frees every tuple"]
        assert actual["law deletion"]["freeing start laws, of all start laws"] == [raw["start knots"], raw["of start / born"][0]]
        assert actual["law deletion"]["freeing birth laws, of all birth laws"] == [raw["born knots"], raw["of start / born"][1]]


def compare(case, start_groups, new_carriers=None):
    computed = {r["round"]: r for r in case["rounds"]}
    assert len(computed) == len(start_groups["rounds"])
    for expected in start_groups["rounds"]:
        actual = computed[expected["round"]]
        if "end" in expected:
            fate = "not read" if "start carriers not read" in actual else actual["end"]
            assert fate == expected["end"]
        else:
            compare_read(actual["start carriers"], expected)
    if new_carriers is None:
        return
    assert len(computed) - 1 == len(new_carriers["rounds"])
    for expected in new_carriers["rounds"]:
        age = expected["round"]
        actual = computed[age]
        if "end" in expected:
            assert actual["end"] == expected["end"]
        else:
            assert actual["distinctions"] == expected["distinctions"]
            expected_new = expected.get(f"carriers born in round {age - 1}")
            assert (expected_new is not None) == ("new carriers" in actual), (new_carriers["family"], age, actual)
            if expected_new is not None:
                compare_read(actual["new carriers"], expected_new)


def run_case(start, rings, carriers, law, arm="ordinary", middles=()):
    results = []
    parity_stage = start
    for data, rows, births in trajectory(start, rings, carriers, law, arm, keep_later_nae=True):
        if middles and arm != "ordinary" and data["round"] == 1:
            data["start carriers"]["law deletion"] = law_deletion(rows, births, start, carriers, middles)
        if law == "nae" and data["round"]:
            parity_stage, parity_fate, _, _ = grow(parity_stage, "parity", arm)
            data["same growth as under parity"] = (rows, data.get("end", "funded")) == (parity_stage, parity_fate)
        results.append(data)
    return {"start knots": len(start), "start distinctions": len(owners(start)), "rounds": results}


def select_archive(name):
    result = {}
    for line in archive(name):
        for section in ("start groups", "new carriers"):
            if section in line:
                r = line[section]
                result[r["family"], r["arm"], section] = r
    return result


def recount_cut_premises(arm):
    records = archive(f"frozen_premises_census_{arm}.jsonl")
    total = records.pop()
    funded = [row for record in records for row in record["rounds"] if "premises broken" in row]
    first = "3: zero-fresh birth not alone"
    second = "3: zero-fresh parent with more than one loose"
    tally = Counter()
    failing_rounds = Counter()
    span = Counter()
    for row in funded:
        flags = row["premises broken"]
        tally.update(flags)
        failing_rounds.update(flags.keys())
        failing_rounds["either part of premise 3"] += int(first in flags or second in flags)
        if "span" in row:
            r = row["span"]
            span["stages"] += 1
            span["equal"] += int(r["dim Z_new"] == r["rank of pairs and loops of four"] and r["inside Z_new"])
    assert {"rounds read": len(funded), **tally} == total["premises"]
    assert dict(span) == total["span"]
    return {
        "census starts": len(records),
        "funded rounds": len(funded),
        "funded rounds per round": dict(sorted(Counter(row["round"] for row in funded).items())),
        "starts with no funded round": sum(not any("premises broken" in row for row in r["rounds"]) for r in records),
        "birth-level violations": dict(tally),
        "distinct failing rounds by premise": dict(failing_rounds),
        "distinct starts with any failing round": sum(any(row.get("premises broken") for row in r["rounds"]) for r in records),
        "span": dict(span),
    }


def previous_funding_controls(pilot):
    rows, rings, carriers, _ = ring_start(3, 5, "split", "detour")
    ring_knots = {k for ring in rings for k in ring}
    connecting_knots = sorted(set(range(len(rows))) - ring_knots)
    holdings = owners(rows)
    nearest = shared_neighbours(rows, holdings)
    loose = [sum(len(holdings[d]) == 1 for d in row) for row in rows]
    names = ("one added, previous funding kept", "meet the demand", "meet demand plus one")
    carrier_forms = tuple(map(mask, carriers))
    counts = Counter()
    finishes = Counter()
    cache = {}
    for size in (1, 2):
        for selected in combinations(connecting_knots, size):
            if pilot and selected not in {(15,), (17,), (15, 16), (17, 25)}:
                continue
            live = ring_knots | set(selected)
            demand = Counter(k for g in parent_groups(nearest, live) for k in g)
            for name in names:
                d = max(holdings) + 1
                adjusted_rows = []
                for k, row in enumerate(rows):
                    amount = 0
                    if name == names[0]:
                        amount = int(k in selected)
                    elif k in live:
                        amount = max(0, max(1, demand[k]) - loose[k]) + int(name == names[2] and k in selected)
                    adjusted_rows.append((*row, *range(d, d + amount)))
                    d += amount
                start = tuple(adjusted_rows)
                if start not in cache:
                    results = {}
                    for arm in ARMS:
                        stage = start
                        records = []
                        reason = "studied through round 3"
                        for age in range(4):
                            if age:
                                stage, status, _, _ = grow(stage, "parity", arm)
                                if status != "funded":
                                    reason = f"{status} at round {age}"
                                    break
                            if len(owners(stage)) > 512:
                                reason = f"over 512 distinctions at round {age}, not read"
                                break
                            records.append(len(parity_tuples(map(mask, stage), carrier_forms)))
                        results[arm] = records, reason
                    cache[start] = results
                for arm, (readings, reason) in cache[start].items():
                    finishes[name, size, arm, reason] += 1
                    for age, count in enumerate(readings):
                        counts[name, size, arm, age, "settings with this stage"] += 1
                        counts[name, size, arm, age, "original three values freely vary"] += int(count == 8)
    if not pilot:
        earlier_file = STUDY.parent / "BINDING-20261126-001" / "referee-R1" / "cuts_changes.json"
        earlier = json.loads(earlier_file.read_text())
        assert len(cache) == earlier["distinct modified starts"]
        expected = {}
        for r in earlier["tables"]:
            key = (r["funding"], r["number of selected connecting knots"], r["growth law"], r["round"])
            for field in ("settings with this stage", "original three values freely vary"):
                expected[*key, field] = r[field]
        assert dict(counts) == expected
        expected = {}
        for r in earlier["finishes"]:
            key = (r["funding"], r["number of selected connecting knots"], r["growth law"], r["finish"])
            expected[key] = r["settings"]
        assert dict(finishes) == expected
    return {
        "settings": sum(finishes.values()) // len(ARMS),
        "distinct starts": len(cache),
        "stage reads by arm": {arm: sum(value for (_, _, a, _, field), value in counts.items()
                                          if a == arm and field == "settings with this stage") for arm in ARMS},
        "all eight tuples by arm": {arm: sum(value for (_, _, a, _, field), value in counts.items()
                                              if a == arm and field == "original three values freely vary") for arm in ARMS},
    }


def case_counts(cases):
    out = Counter()
    for case in cases:
        out["trajectories"] += 1
        for stage in case["rounds"]:
            if "end" in stage:
                out[f"{stage['end']} at round {stage['round']}"] += 1
                continue
            age = stage["round"]
            if stage.get("same growth as under parity"):
                out["funded rounds matching parity growth"] += 1
            for carrier_kind in ("start carriers", "new carriers"):
                if carrier_kind in stage:
                    read = stage[carrier_kind]
                    tuples = read["tuples"]
                    out[f"{carrier_kind} read at round {age}"] += 1
                    if len(tuples) == 2 ** len(tuples[0]):
                        out[f"{carrier_kind} free at round {age}"] += 1
                    if "one distinction changes this carrier" in read:
                        changes = read["one distinction changes this carrier"]
                        out[f"{carrier_kind} individual parities"] += len(changes)
                        out[f"{carrier_kind} individual parities changed by one distinction"] += sum(d is not None for d in changes)
                if carrier_kind + " not read" in stage:
                    out[f"{carrier_kind} not read at round {age}"] += 1
    return dict(sorted(out.items()))


def run(pilot):
    control_archive = select_archive("frozen_controls.jsonl")
    cut_archive = select_archive("frozen_cuts.jsonl")
    nae_archive = select_archive("frozen_nae.jsonl")
    control_cases = {}
    cut_cases = {}
    nae_cases = {}
    control_cache = {}
    pilot_members = {(3, 4, "split", "double"), (3, 5, "split", "detour"), (3, 6, "split", "detour"), (4, 6, "paired", "detour")}
    reading = ("one loose at the middle knot of a detour", "one loose at a connecting knot", "links made loose")
    for member in product((3, 4), (4, 5, 6, 7), ("split", "paired"), ("double", "detour")):
        r, n, attachment, link = member
        if pilot and member not in pilot_members:
            continue
        name = f"{r} rings of {n}, {attachment}, {link}"
        for edit in (reading[0 if link == "detour" else 1], reading[2]):
            label = f"{name} + {edit}"
            start, rings, carriers, _ = ring_start(*member, edit)
            if start not in control_cache:
                control_cache[start] = run_case(start, rings, carriers, "parity")
            case = control_cache[start]
            compare(case, control_archive[label, "ordinary", "start groups"], control_archive[label, "ordinary", "new carriers"])
            control_cases[label] = case
        if r == 3 and link == "detour":
            label = name + ", middles joined"
            cut_cases[label] = {}
            start, rings, carriers, middles = ring_start(*member, "middles joined")
            for arm in ARMS:
                case = run_case(start, rings, carriers, "parity", arm, middles)
                compare(case, cut_archive[label, arm, "start groups"])
                cut_cases[label][arm] = case
        start, rings, carriers, _ = ring_start(*member)
        case = run_case(start, rings, carriers, "nae")
        compare(case, nae_archive[name, "ordinary", "start groups"], nae_archive[name, "ordinary", "new carriers"])
        nae_cases[name] = case

    prior_cut = archive("repro_cuts.jsonl")
    prior_case = cut_cases["3 rings of 5, split, detour, middles joined"]
    for old in prior_cut:
        case = prior_case[old["arm"]]
        assert old["knots"] == case["start knots"] == 30
        compare(case, old)
        for actual, earlier in zip(case["rounds"], old["rounds"], strict=True):
            if "births with no fresh distinction" in earlier:
                certificate = actual["start carriers"].get("law deletion")
                zero_fresh = []
                if certificate:
                    zero_fresh = [[list(b["parents"]), len(b["inputs"])] for b in certificate["all births with no fresh distinction"]]
                assert earlier["births with no fresh distinction"] == zero_fresh

    prior_controls = {}
    for variant in ("no v", "J loose", "J two loose"):
        start, carriers = two_joining_knots(variant)
        prior_controls[variant] = run_case(start, [], carriers, "parity")
    for old in archive("built_controls_explore.jsonl"):
        case = prior_controls[old["variant"]]
        assert len(case["rounds"]) == len(old["rounds"])
        for new, earlier in zip(case["rounds"], old["rounds"], strict=True):
            assert new["round"] == earlier["round"]
            if "end" in earlier:
                assert new["end"] == earlier["end"]
            else:
                projection = new["start carriers"]
                assert len(projection["tuples"]) == earlier["tuples of the ring facts"]
                for new_key, old_key in (("shortest", "SHORT"), ("through five", "UPTO5")):
                    flags = [[f["label"], f["read by no single knot"]] for f in earlier[old_key]["ring facts"]]
                    assert projection[new_key] == flags

    extensions = {
        f"3 rings of 6, {a}, detour, middles joined": extend_arity_floor((3, 6, a, "detour"))
        for a in (("split",) if pilot else ("split", "paired"))
    }

    return {
        "control counts": {edit: case_counts(case for name, case in control_cases.items() if name.endswith(edit)) for edit in reading},
        "distinct control starts": len(control_cache),
        "cut counts": {arm: case_counts(c[arm] for c in cut_cases.values()) for arm in ARMS},
        "not-all-equal counts": case_counts(nae_cases.values()),
        "control trajectories": control_cases,
        "cut trajectories": cut_cases,
        "not-all-equal trajectories": nae_cases,
        "before-freeze controls on the 14-knot start": prior_controls,
        "before-freeze cut trajectories matched": len(prior_cut),
        "earlier funding controls on the 30-knot start": previous_funding_controls(pilot),
        "cut premise archive recount": {arm: recount_cut_premises(arm) for arm in ARMS[1:]},
        "later arity-floor rounds": extensions,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    ceiling = 5 * 1024 ** 3 // 2
    resource.setrlimit(resource.RLIMIT_AS, (ceiling, ceiling))
    started = perf_counter()
    result = run(args.pilot)
    result["elapsed seconds"] = round(perf_counter() - started, 3)
    result["peak resident KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    shown = {k: v for k, v in result.items() if "trajectories" not in k and "14-knot" not in k and k != "later arity-floor rounds"}
    print(json.dumps(shown, indent=2))
    if not args.pilot:
        (HERE / "cut_counts.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
