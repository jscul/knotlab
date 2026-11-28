"""Measure commuting choices from their cyclic lists of knots."""

from collections import Counter, defaultdict


def steps(cycle):
    return zip(cycle, (*cycle[1:], cycle[0]))


def cross_pair(a, b):
    return (a, b) if a < b else (b, a)


def interleaves(cycle):
    a, c, b, d = cycle
    first, last = cross_pair(a, b)
    return (first < c < last) != (first < d < last)


def occurrences(cycles):
    at = defaultdict(list)
    for index, cycle in enumerate(cycles):
        for a, b in steps(cycle):
            at[cross_pair(a, b)].append((index, a < b))
    return at


def components(adjacent):
    labels = {}
    for start in adjacent:
        if start in labels:
            continue
        labels[start] = start
        pending = [start]
        while pending:
            node = pending.pop()
            for other in adjacent[node]:
                if other not in labels:
                    labels[other] = start
                    pending.append(other)
    return labels


def colourable(adjacent):
    """Every listed pair has an explicit bit required between its ends."""
    colours = {}
    for start in adjacent:
        if start in colours:
            continue
        colours[start] = 0
        pending = [start]
        while pending:
            node = pending.pop()
            for other, required in adjacent[node]:
                colour = colours[node] ^ required
                if other not in colours:
                    colours[other] = colour
                    pending.append(other)
                elif colours[other] != colour:
                    return False
    return True


def crossing_structure(at):
    adjacent = defaultdict(list)
    for a, b in at:
        adjacent[a].append(b)
        adjacent[b].append(a)
    return (
        len(adjacent),
        len(set(components(adjacent).values())),
        colourable({a: [(b, 1) for b in neighbours] for a, neighbours in adjacent.items()}),
    )


def separated_cycles(cycles):
    links = defaultdict(lambda: defaultdict(list))
    for a, b, c, d in cycles:
        for knot, left, right in ((a, d, b), (b, a, c), (c, b, d), (d, c, a)):
            links[knot][left].append(right)
            links[knot][right].append(left)
    labels = {}
    for knot, link in links.items():
        assert all(len(neighbours) == 2 for neighbours in link.values())
        labels[knot] = components(link)
    return [
        tuple((a, labels[a][b]) for a, b in steps(cycle)) for cycle in cycles
    ]


def orientable(at, covered_twice):
    if covered_twice:
        adjacent = defaultdict(list)
        for (i, forward), (j, other_forward) in at.values():
            required = forward == other_forward
            adjacent[i].append((j, required))
            adjacent[j].append((i, required))
        return colourable(adjacent)

    # For each cross pair exactly half its occurrences must list the reference
    # order. The same reversal bit is used for a cycle at every cross pair.
    from pysat.solvers import Minicard

    with Minicard() as solver:
        for items in at.values():
            literals = [-(i + 1) if forward else i + 1 for i, forward in items]
            solver.add_atmost(literals, len(items) // 2)
            solver.add_atmost([-literal for literal in literals], len(items) // 2)
        return solver.solve()


def weak_even(at):
    pivots = {}
    for items in at.values():
        target = (len(items) // 2 - sum(forward for _, forward in items)) % 2
        equation = target | sum(1 << (i + 1) for i, _ in items)
        while equation > 1:
            pivot = equation.bit_length()
            if pivot not in pivots:
                pivots[pivot] = equation
                break
            equation ^= pivots[pivot]
        if equation == 1:
            return False
    return True


def order_count(at, reversed_cycles=0, reversed_pairs=0):
    return sum(
        forward ^ bool(reversed_cycles & (1 << cycle)) ^ bool(reversed_pairs & (1 << pair))
        for pair, items in enumerate(at.values())
        for cycle, forward in items
    ) % 2


def measure_cycles(cycles, *, rngs=()):
    """Measure a choice with one cycle per failing pair, including duplicates."""
    cycles = tuple(tuple(cycle) for cycle in cycles)
    if any(len(cycle) != 4 or len(set(cycle)) != 4 for cycle in cycles):
        raise ValueError("Each failing pair requires four distinct holders")
    at = occurrences(cycles)
    if any(len(items) % 2 for items in at.values()):
        raise ValueError("The choice does not commute")
    coverage = Counter(map(len, at.values()))
    covered_twice = set(coverage) == {2}
    knots, count_components, two_colourable = crossing_structure(at)
    euler = knots - len(at) + len(cycles)
    separated_euler = separated_colour = separated_components = one_cycle = None
    if covered_twice:
        separated = occurrences(separated_cycles(cycles))
        assert len(separated) == len(at)
        assert all(len(items) == 2 for items in separated.values())
        separated_knots, separated_components, separated_colour = crossing_structure(separated)
        separated_euler = separated_knots - len(separated) + len(cycles)
        one_cycle = separated_knots == knots
    return {
        "sign": sum(map(interleaves, cycles)) % 2,
        "max_coverage": max(coverage, default=0),
        "coverage": dict(coverage),
        "covered_twice": covered_twice,
        "one_cycle_per_knot": one_cycle,
        "orientable": orientable(at, covered_twice),
        "weak_even": weak_even(at),
        "two_colourable": two_colourable,
        "euler": euler,
        "separated_euler": separated_euler,
        "separated_two_colourable": separated_colour,
        "components": count_components,
        "separated_components": separated_components,
        "reference_order_count": order_count(at),
        "same_order_parity": (
            sum(items[0][1] == items[1][1] for items in at.values()) % 2
            if covered_twice else None
        ),
        "order_counts": [
            order_count(at, rng.getrandbits(len(cycles)), rng.getrandbits(len(at)))
            for rng in rngs
        ],
    }
