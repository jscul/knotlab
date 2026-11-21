"""Cross-check the finite tree census using the necessary condition in tree_proof.md.

Only a single spent common holder with three or four leaves can close. Rebuild
those cases with the earlier physical engine. Independently count the mass of
the initial funding test and challenge the condition at one size past the census.
"""
from collections import Counter
from fractions import Fraction
from itertools import product
from math import comb, factorial, prod
from pathlib import Path
import sys

import networkx as nx

ROOT = Path(__file__).resolve().parents[2]
EARLIER = "ERASURE-AND-CLOSING-SIGNS-20261121-001"
ENGINE = "STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B"
sys.path.insert(0, str(ROOT / "research" / EARLIER))
sys.path.insert(0, str(ROOT / "experiments" / ENGINE / (ENGINE + "-E001_pair_growth")))
from independent_checks import closed_components, four_cuts
from explosive_stages import advance


def founder(leaves, extra):
    """One spent holder of all old meetings, followed by its live leaf holders."""
    rows = [tuple(range(leaves))]
    name = leaves
    for leaf in range(leaves):
        loose = 2 + int(leaf < extra)
        rows.append((leaf, *range(name, name + loose)))
        name += loose
    return tuple(rows)


def physical_cases():
    outcomes = {}
    for leaves in (3, 4):
        for extras in range(leaves + 1):
            rows = founder(leaves, extras)
            both = []
            for law in ("parity", "nae"):
                events, whole = four_cuts(rows, law, advance, allow_stall=True)
                assert (len(events) == 1) == whole
                both.append(events[0] if whole else None)
            assert both[1] is None
            outcomes[leaves + 1, extras] = both[0]
    return outcomes


def star_masses(outcomes, extra_chance):
    """One labelled choice of common holder per vertex, then independent extras."""
    p = extra_chance
    per_size = {}
    for size in range(4, 9):
        counts = [Fraction(0), Fraction(0)]
        for extra in range(size):
            event = outcomes.get((size, extra))
            if event is None:
                continue
            chance = (Fraction(size, size ** (size - 2)) * (1 - p)
                      * comb(size - 1, extra) * p ** extra * (1 - p) ** (size - 1 - extra))
            counts[0] += chance
            if event[1]:
                counts[1] += chance
        per_size[size] = tuple(counts)
    return per_size


def tree_symmetries(tree):
    def rooted(vertex, parent):
        parts = [rooted(v, vertex) for v in tree[vertex] if v != parent]
        shape = tuple(sorted(shape for shape, _ in parts))
        order = prod(order for _, order in parts)
        order *= prod(factorial(count) for count in Counter(shape).values())
        return shape, order

    middle = nx.center(tree)
    if len(middle) == 1:
        return rooted(middle[0], None)[1]
    first, second = middle
    a, sa = rooted(first, second)
    b, sb = rooted(second, first)
    return sa * sb * (2 if a == b else 1)


def funding_and_connected_end(size):
    """Count distinct labelled founders by expanding every mask of each plain tree."""
    total = funded = potential = labelled = 0
    for tree in nx.nonisomorphic_trees(size):
        labelings = factorial(size) // tree_symmetries(tree)
        labelled += labelings
        degrees = [tree.degree[i] for i in range(size)]
        end_near = [
            sum(1 << v for w in tree[u] for v in tree[w] if v != u)
            for u in range(size)
        ]
        # The unique intervening knot in a tree prevents duplicate bits here.
        for extra in product((0, 1), repeat=size):
            loose = [max(0, 3 - d) + b for d, b in zip(degrees, extra)]
            mass = labelings * 3 ** (size - sum(extra))
            total += mass
            live = sum(1 << h for h, count in enumerate(loose) if count)
            if any((end_near[h] & live).bit_count() > count
                   for h, count in enumerate(loose) if count):
                continue
            funded += mass
            seen = live & -live
            while True:
                after = seen
                for h in range(size):
                    if seen & (1 << h):
                        after |= end_near[h] & live
                if after == seen:
                    break
                seen = after
            if seen == live:
                assert size in (4, 5) and max(degrees) == size - 1
                center = degrees.index(size - 1)
                assert loose[center] == 0
                assert size == 4 or all(b for h, b in enumerate(extra) if h != center)
                potential += mass
    assert labelled == size ** (size - 2)
    assert total == size ** (size - 2) * 4 ** size
    return total, funded, potential



def one_step_beyond(outcomes):
    """A post-census boundary check for the only still-open eligible founder."""
    rows = founder(3, 3)
    for step in range(1, 6):
        status, rows, births = advance(rows, "parity")
        assert status == "births"
        print("three-extra founder, cut, paid births, fresh, holdings",
              step, len(births), sum(b[1] for b in births), len(rows))
    close = closed_components(rows)
    assert len(close) == 1 and next(iter(close)) == frozenset(range(len(rows)))
    wider = dict(outcomes)
    wider[4, 3] = (5, next(iter(close.values())), len(rows),
                    len({x for row in rows for x in row}))
    totals = star_masses(wider, Fraction(1, 4))
    parity, admitting = (sum(row[j] for row in totals.values()) / 5 for j in (0, 1))
    print("beyond cut four, final case", wider[4, 3], "all-step masses",
          parity, admitting, admitting / parity)



def changed_funding_control(blocks):
    """Each extra interior connector has four loose names. It can pay four calls."""
    graph = nx.Graph()
    for j in range(blocks - 1):
        graph.add_edges_from(((("spent", j), ("connector", j)),
                              (("connector", j), ("spent", j+1))))
    for j in range(blocks):
        needed = 3 - graph.degree(("spent", j))
        for leaf in range(needed):
            graph.add_edge(("spent", j), ("leaf", j, leaf))
    names = {h: [] for h in graph.nodes}
    for x, (a, b) in enumerate(graph.edges):
        names[a].append(x)
        names[b].append(x)
    next_name = len(graph.edges)
    for h, local in names.items():
        supply = {"connector": 4, "leaf": 2, "spent": 0}[h[0]]
        local.extend(range(next_name, next_name + supply))
        next_name += supply
    founder_rows = tuple(map(tuple, names.values()))
    expected = len([h for h in graph if h[0] != "spent"]) - 1
    for law in ("parity", "nae"):
        rows = founder_rows
        for cut in range(1, expected + 1):
            status, rows, _ = advance(rows, law)
            assert status == "births"
            closed = closed_components(rows)
            assert bool(closed) == (law == "parity" and cut == expected)
        if law == "parity":
            assert len(closed) == 1 and all(closed.values())
        print("altered funding, founders, law, cut, closed:", len(graph), law, expected, bool(closed))


def main():
    events = physical_cases()
    for key, event in events.items():
        print("founder size, extra leaves, closure (step, admission, holders, names):", key, event)
    for p in map(Fraction, (0, "1/4", "1/2", 1)):
        rows = star_masses(events, p)
        closure, admitting = (sum(r[j] for r in rows.values()) / 5 for j in (0, 1))
        print("extra probability", p, "per size", rows, "mixed", closure, admitting,
              "conditional", admitting / closure if closure else "undefined")
    for n in range(4, 10):
        print("size, total units, funded, connected funded:", n, *funding_and_connected_end(n))
    one_step_beyond(events)
    for blocks in (2, 3):
        changed_funding_control(blocks)


if __name__ == "__main__":
    main()
