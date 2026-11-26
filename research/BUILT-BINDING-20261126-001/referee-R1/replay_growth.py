"""Independent roster and complete-round growth for the birth record replay."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations, count, permutations, product
import json
from pathlib import Path
from random import Random


ROOT = Path(__file__).resolve().parents[3]
CENSUS = ROOT / "research/FORBID-EDITS-20261126-001/starts.json"


def binary_mask(names):
    word = 0
    for distinction in names:
        word |= 1 << distinction
    return word


def remainder(word, basis):
    while word:
        row = basis.get(word.bit_length())
        if row is None:
            break
        word ^= row
    return word


def insert(word, basis):
    word = remainder(word, basis)
    if word:
        basis[word.bit_length()] = word


def elimination(words):
    basis = {}
    for word in words:
        insert(word, basis)
    return basis


def support(number, shared, loose):
    knots = [[] for _ in range(number)]
    next_name = count()
    for first, second, multiplicity in shared:
        for _ in range(multiplicity):
            distinction = next(next_name)
            knots[first].append(distinction)
            knots[second].append(distinction)
    for knot, amount in zip(knots, loose, strict=True):
        knot.extend(next(next_name) for _ in range(amount))
    return tuple(map(tuple, knots))


def connected(number, shared):
    reached = {0}
    while True:
        expanded = reached | {b for a, b, _ in shared if a in reached} | {
            a for a, b, _ in shared if b in reached
        }
        if expanded == reached:
            return len(reached) == number
        reached = expanded


def shared_counts(number, shared):
    places = [0] * number
    for a, b, amount in shared:
        places[a] += amount
        places[b] += amount
    return places


def read_census():
    return json.loads(CENSUS.read_text())


def named_draws(number, accepted, seed, maximum):
    rng = Random(seed)
    pairs = tuple(combinations(range(number), 2))
    while accepted:
        meeting = [pair for pair in pairs if rng.random() < 1 / 3]
        shared = [(*pair, 1 + rng.randrange(2)) for pair in meeting]
        loose = [rng.randrange(3) for _ in range(number)]
        if sum(loose) + sum(item[2] for item in shared) > maximum:
            continue
        if any(q + p < 3 for p, q in zip(loose, shared_counts(number, shared), strict=True)):
            continue
        if connected(number, shared):
            yield support(number, shared, loose)
            accepted -= 1


def verify_census(records):
    """Count labelled cases separately and cover them with disjoint recorded relabellings."""
    results = {}
    for size in (3, 4, 5):
        pairs = tuple(combinations(range(size), 2))
        position = {pair: i for i, pair in enumerate(pairs)}
        limit = len(pairs)
        remaps = []
        for renaming in permutations(range(size)):
            remaps.append((
                [2 * position[tuple(sorted((renaming[a], renaming[b])))] for a, b in pairs],
                [2 * (limit + knot) for knot in renaming],
            ))
        labelled = set()
        unlabelled = 0
        for number, shared, loose in records:
            if number != size:
                continue
            assert all(a < b and amount in (1, 2) for a, b, amount in shared)
            assert all(quantity in (0, 1, 2) for quantity in loose)
            assert len({(a, b) for a, b, _ in shared}) == len(shared)
            assert sum(loose) + sum(amount for _, _, amount in shared) <= 12
            assert connected(size, shared)
            assert all(q + p >= 3 for p, q in zip(loose, shared_counts(size, shared), strict=True))
            nonzero = [(position[a, b], amount) for a, b, amount in shared]
            orbit = {
                sum(amount << shifts[index] for index, amount in nonzero)
                + sum(q << shift for q, shift in zip(loose, loose_shifts, strict=True))
                for shifts, loose_shifts in remaps
            }
            assert labelled.isdisjoint(orbit)
            labelled.update(orbit)
            unlabelled += 1
        expected = 0
        for multiplicities in product(range(3), repeat=limit):
            count_shared = sum(multiplicities)
            if count_shared > 12:
                continue
            shared = [(a, b, m) for (a, b), m in zip(pairs, multiplicities, strict=True) if m]
            if len(shared) < size - 1 or not connected(size, shared):
                continue
            minimum = [max(0, 3 - p) for p in shared_counts(size, shared)]
            if max(minimum) > 2 or sum(minimum) + count_shared > 12:
                continue
            ways = {0: 1}
            for least in minimum:
                next_ways = Counter()
                for previous, amount in ways.items():
                    for loose in range(least, 3):
                        if previous + loose + count_shared <= 12:
                            next_ways[previous + loose] += amount
                ways = next_ways
            expected += sum(ways.values())
        assert expected == len(labelled)
        results[size] = {"labelled": expected, "up to renaming": unlabelled}
    return results


def ring_family(number, size, attachment, link):
    knots = [[] for _ in range(number * size)]
    next_name = count()

    def add(*holders):
        distinction = next(next_name)
        for holder in holders:
            knots[holder].append(distinction)

    for offset in range(0, number * size, size):
        for index in range(size):
            add(offset + index, offset + (index + 1) % size)
    for holder in range(number * size):
        add(holder)
        add(holder)
    port = [0] * number
    for first, second in combinations(range(number), 2):
        left = len(knots)
        right = left + 1
        knots.extend(([], []))
        for ring, connection in ((first, left), (second, right)):
            index = port[ring]
            port[ring] += 1
            options = (index, index + 2) if attachment == "split" else (2 * index, 2 * index)
            for source in options:
                add(ring * size + source % size, connection)
        add(left, right)
        if link == "detour":
            for _ in range(3):
                middle = len(knots)
                knots.append([])
                add(left, middle)
                add(left, middle)
                left = middle
        add(left, right)
        if link == "detour":
            add(left, right)
    return tuple(map(tuple, knots))


def small_built(variant):
    knots = [[] for _ in range(14)]
    next_name = count()

    def add(*holders):
        distinction = next(next_name)
        for holder in holders:
            knots[holder].append(distinction)

    for base in (0, 4, 8):
        for index in range(4):
            add(base + index, base + (index + 1) % 4)
        for holder in (base + 1, base + 3):
            add(holder)
            add(holder)
        add(base, 12)
        add(base + 2, 13)
    if variant != "no v":
        add(12, 13)
    for _ in range({"base": 0, "no v": 0, "J loose": 1, "J two loose": 2}[variant]):
        add(12)
    return tuple(map(tuple, knots))


def items(roster, census):
    if roster == "census":
        for index, row in enumerate(census):
            yield f"census {index}", support(*row)
    elif roster in ("heldout", "sampled"):
        sizes, accepted, seed, maximum, label = {
            "heldout": ((6, 7, 8), 300, 20261206, 18, "held out"),
            "sampled": ((9, 10, 11, 12), 100, 20261212, 30, "sampled"),
        }[roster]
        for size in sizes:
            for index, start in enumerate(named_draws(size, accepted, seed + size, maximum)):
                yield f"{label} {size}-{index}", start
    elif roster == "built":
        for number, size, attachment, link in product(
            (3, 4), (4, 5, 6, 7), ("split", "paired"), ("double", "detour")
        ):
            label = f"{number} rings of {size}, {attachment}, {link}"
            yield label, ring_family(number, size, attachment, link)
    elif roster == "small built":
        for variant in ("base", "no v", "J loose", "J two loose"):
            yield f"built {variant}", small_built(variant)
    else:
        raise ValueError(roster)


def meets_from(incidence, size):
    meeting = [set() for _ in range(size)]
    for holders in incidence.values():
        assert len(holders) in (1, 2)
        if len(holders) == 2:
            first, second = holders
            assert first != second
            meeting[first].add(second)
            meeting[second].add(first)
    return meeting


def incidence_of(stage):
    incidence = defaultdict(list)
    for holder, knot in enumerate(stage):
        for distinction in knot:
            incidence[distinction].append(holder)
    return incidence


def proposals(witnesses):
    """Find maximal complete parent sets with no witness to the entire set."""
    observed = defaultdict(set)
    neighbors = defaultdict(set)
    for index, witnessed in enumerate(witnesses):
        if len(witnessed) < 2:
            continue
        for first in witnessed:
            neighbors[first].update(witnessed - {first})
            observed[first].add(index)

    maximal = []

    def extend(group, available, excluded, common):
        if len(group) + len(available) < 3:
            return
        if any(available <= witnesses[witness] for witness in common):
            return
        if not available:
            if not excluded:
                maximal.append(tuple(sorted(group)))
            return
        pivot = max(available | excluded, key=lambda x: len(available & neighbors[x]))
        for knot in sorted(available - neighbors[pivot]):
            extend(
                group + (knot,), available & neighbors[knot], excluded & neighbors[knot],
                common & observed[knot],
            )
            available.remove(knot)
            excluded.add(knot)

    for first, adjacent in neighbors.items():
        extend((first,), {x for x in adjacent if x > first}, {x for x in adjacent if x < first}, observed[first])
    contained = {pair for group in maximal for pair in combinations(group, 2)}
    pairs = {(a, b) for a, others in neighbors.items() for b in others if a < b}
    return sorted(maximal) + sorted(pairs - contained), pairs


def components(meeting, loose):
    component = {}
    names = {}
    for root in range(len(meeting)):
        if root in component:
            continue
        queue = [root]
        component[root] = root
        all_loose = set()
        for holder in queue:
            all_loose.update(loose.get(holder, ()))
            for other in meeting[holder]:
                if other not in component:
                    component[other] = root
                    queue.append(other)
        names[root] = all_loose
    return component, names


@dataclass(frozen=True)
class Birth:
    parents: tuple
    inputs: tuple
    fresh: tuple
    implied: bool
    takes_all: bool


def implied_nae(stage, inputs):
    # Complementation preserves every condition. An all-zero input witness
    # also certifies that all ones is possible.
    from pysat.solvers import Solver

    clauses = []
    for knot in stage:
        clauses.append([name + 1 for name in knot])
        clauses.append([-name - 1 for name in knot])
    with Solver(bootstrap_with=clauses) as reader:
        for support in inputs:
            if not reader.solve(assumptions=[-name - 1 for name in support]):
                yield True
                continue
            word = set(reader.get_model())
            assert all(-name - 1 in word for name in support)
            assert all(any(literal in word for literal in clause) for clause in clauses)
            yield False


def check_births(births, loose, pairs, component):
    violations = Counter()
    spent = Counter(name for birth in births for name in birth.inputs)
    if spent != Counter(name for support in loose.values() for name in support):
        violations["1: loose not taken once"] += 1
    pair_births = set()
    by_component = Counter(component[birth.parents[0]] for birth in births)
    for birth in births:
        paid_holders = [parent for name in birth.inputs for parent in birth.parents if name in loose[parent]]
        assert tuple(sorted(paid_holders)) == birth.parents
        if len(set(paid_holders)) != len(birth.inputs):
            violations["1: two from one parent"] += 1
        pair_births.update(combinations(birth.parents, 2))
        assert len({component[parent] for parent in birth.parents}) == 1
        if not birth.fresh:
            if by_component[component[birth.parents[0]]] != 1:
                violations["3: zero-fresh birth not alone"] += 1
            if any(len(loose[parent]) != 1 for parent in birth.parents):
                violations["3: zero-fresh parent with more than one loose"] += 1
    if pairs - pair_births:
        violations["2: common neighbour, no common birth"] += len(pairs - pair_births)
    return dict(violations)


def grow(stage, law, arm):
    incidence = incidence_of(stage)
    loose = {}
    for holder, knot in enumerate(stage):
        names = tuple(name for name in knot if len(incidence[name]) == 1)
        if names:
            loose[holder] = names
    if not loose:
        return "closed", stage, [], {}
    meeting = meets_from(incidence, len(stage))
    groups, pairs = proposals([neighbors & loose.keys() for neighbors in meeting])
    usage = Counter(holder for group in groups for holder in group)
    if any(usage[holder] > len(names) for holder, names in loose.items()):
        return "stalled", stage, [], {}
    groups.extend((holder,) for holder, names in loose.items() for _ in range(len(names) - usage[holder]))

    spend = {holder: iter(names) for holder, names in loose.items()}
    inputs = [tuple(next(spend[holder]) for holder in group) for group in groups]
    children = {holder: set() for holder in loose}
    for index, group in enumerate(groups):
        for holder in group:
            children[holder].add(index)
    onward, _ = proposals(tuple(children.values()))
    demand = Counter(knot for group in onward for knot in group)
    component, all_loose = components(meeting, loose)
    if law == "parity":
        laws = elimination(binary_mask(knot) for knot in stage)
        implied = (remainder(binary_mask(names), laws) == 0 for names in inputs)
    else:
        implied = implied_nae(stage, inputs)
    next_name = max(incidence) + 1
    births = []
    for index, (parents, consumed, implied_here) in enumerate(zip(groups, inputs, implied, strict=True)):
        arity_floor = max(0, 3 - len(parents))
        ordinary = demand[index] if implied_here else max(demand[index], arity_floor, 1)
        if arm == "ordinary":
            amount = ordinary
        elif arm == "one_fewer":
            amount = min(ordinary, max(arity_floor, ordinary - 1))
        elif arm == "arity_floor":
            amount = min(ordinary, arity_floor)
        else:
            raise ValueError(arm)
        fresh = tuple(range(next_name, next_name + amount))
        next_name += ordinary
        births.append(Birth(parents, tuple(sorted(consumed)), fresh, implied_here,
                            set(consumed) == all_loose[component[parents[0]]]))
    next_stage = stage + tuple(birth.inputs + birth.fresh for birth in births)
    return "funded", next_stage, births, check_births(births, loose, pairs, component)
