"""Independent literal holdings and complete first grants for the two private-pulse clocks."""

from collections import Counter, defaultdict
from itertools import combinations, product

import networkx as nx


def role(side, position):
    if position in (1, 5, 9, 13):
        return "p" if side == "c" else "h"
    if position in (3, 7):
        return "q" if side == "c" else "k"
    return side + str(position)


def width(side, i, leave):
    if i in (1, 5, 9, 13):
        return (3 if side == "c" else 5, 6, 7, 8, 9, 10, 11, 12)[2 * (1, 5, 9, 13).index(i) + leave]
    if i in (3, 7):
        return (3 if side == "c" else 5, 6, 7, 8)[2 * (3, 7).index(i) + leave]
    return (3 if side == "c" else 5) if leave else 4


def group_list(witness_sets):
    """Compute maximal pairwise-adjacent unheld groups, then all uncovered pairs."""
    graph = nx.Graph()
    for s in witness_sets:
        graph.add_edges_from(combinations(s, 2))
    unheld = [frozenset(g) for g in nx.find_cliques(graph)
              if len(g) >= 3 and not any(set(g) <= w for w in witness_sets)]
    uncovered = [frozenset((a, b)) for a, b in graph.edges()
                 if not any(a in g and b in g for g in unheld)]
    return sorted(unheld + uncovered, key=lambda g: tuple(sorted(g)))


def full_source(mask, triple, switches=(), retag=None, broken=False):
    holdings = defaultdict(set)
    spent = []

    def bundle(owner, slot, size):
        names = {(owner, slot, k) for k in range(size)}
        holdings[owner].update(names)
        return names

    def meet(*parts):
        spent.append(set().union(*parts))

    def outside(edge, a, b, n, m):
        meet(bundle(a, (edge, 0), n), bundle(b, (edge, 1), m))

    for tag, i in product(("c", "u"), range(20)):
        other = ({"c": "u", "u": "c"}[tag] if i in switches else tag)
        j = (i + 1) % 20
        a, b = role(tag, i), role(other, j)
        left = bundle(a, ("leave", tag, i), 3 if i == 8 else width(tag, i, 1))
        right = bundle(b, ("enter", other, j), width(other, j, 0))
        if i != 8:
            meet(left, right)
            continue
        z, w = "z" + other, "w" + other
        meet(left, right, bundle(z, "mask", 1) if mask else set())
        if triple:
            meet(bundle(a, ("third", tag, i), 1), bundle(w, "tail", 2))
            w_right = 2 if (other == "c") != (retag == other) else 3
            meet(bundle(b, ("third", other, j), 1), bundle(w, "head", w_right))
    cycle = ("O", "O1", "O2", "O3")
    for i, a in enumerate(cycle):
        outside(("origin", i), a, cycle[(i + 1) % 4], 1, 2)
    for prefix in ("S", "V"):
        for i in range(7):
            next_prefix = ({"S": "V", "V": "S"}[prefix] if broken and i == 3 else prefix)
            a, b = prefix + str(i), next_prefix + str((i + 1) % 7)
            meet(bundle(a, ("emit", i), 2 if prefix == "S" else 6), bundle(b, ("receive", i), 4))
    for a, b, n, m in (("H", "c0", 1, 11), ("H", "S0", 1, 13), ("c18", "u18", 1, 2),
                       ("O1", "V0", 1, 15), ("O", "H", 1, 17)):
        outside(("attachment", a, b), a, b, n, m)
    witness_sets = [{name[0] for name in w} for w in spent]
    first = group_list(witness_sets)
    counts = Counter(u for g in first for u in g)
    opens = {u: (2 if u.startswith(("w", "z")) else counts[u]) for u in holdings}
    for u, n in opens.items():
        bundle(u, "private", n)
    assert all(len(w) >= 3 for w in spent) and all(len(s) >= 3 for s in holdings.values())
    assert len(set().union(*spent)) == sum(map(len, spent))
    return holdings, spent, witness_sets, opens


def cut(witnesses, opens):
    groups = group_list(witnesses)
    demand = Counter(u for g in groups for u in g)
    if any(demand[u] > h for u, h in opens.items()):
        return None
    parents = groups + [frozenset({u}) for u, h in opens.items() for _ in range(h - demand[u])]
    child_sets = [{i for i, g in enumerate(parents) if u in g} for u in opens]
    next_groups = group_list(child_sets)
    next_demand = Counter(c for g in next_groups for c in g)
    assert len(parents) > 1
    fresh = {i: max(1, 3 - len(g), next_demand[i]) for i, g in enumerate(parents)}
    return parents, child_sets, fresh


def visible_spent(holdings, spent, occupied):
    names = set().union(*(holdings[v] for v in occupied))
    return {frozenset(w) for w in spent if w <= names}


def complete_source(holdings, spent, given, law):
    """Construct an extension when disjoint spent factors and private bits permit one."""
    values = dict(given)

    def extend(row):
        free = sorted(row - values.keys(), key=repr)
        for name in free[:-1]:
            values[name] = 0
        if free:
            ones = sum(values.get(name, 0) for name in row)
            values[free[-1]] = ones % 2 if law == "parity" else int(ones == 0)
        ones = sum(values[name] for name in row)
        return ones % 2 == 0 if law == "parity" else 0 < ones < len(row)

    for row in list(spent) + list(holdings.values()):
        if not extend(row):
            return None
    return values


def main():
    earlier = {"O", "H", "p", "q", "c0", "c2", "c4", "c6", "c8"} | {"S" + str(i) for i in range(7)}
    for mask, triple in product((False, True), repeat=2):
        arms = {}
        for near in (False, True):
            old = full_source(mask, triple, (8, 10) if near else ())
            holdings, spent, witnesses, opens = old
            first, child_sets, fresh = cut(witnesses, opens)
            second, grandchildren, next_fresh = cut(child_sets, fresh)
            b = "h" if near else "p"
            local = frozenset(("c8", b, ("wu" if near else "wc"))) if triple else frozenset(("c8", b))
            assert local in first
            if mask:
                z = "zu" if near else "zc"
                az, bz = frozenset(("c8", z)), frozenset((b, z))
                assert az in first and bz in first
                if triple:
                    assert frozenset(map(first.index, (local, az, bz))) in second
                    third, _, third_grants = cut(grandchildren, next_fresh)
                    assert (len(third), sum(third_grants.values())) == (440, 3847)
            arms[near] = old
            print("mask", mask, "third", triple, "near", near, "living", len(opens),
                  "first", len(first), "second", len(second), "total grants", sum(fresh.values()), sum(next_fresh.values()))
        h, w, _, supply = arms[False]
        hh, ww, _, ss = arms[True]
        assert supply == ss and h == hh
        assert (visible_spent(h, w, earlier) == visible_spent(hh, ww, earlier)) == mask
        assert {frozenset(g) for g in w} != {frozenset(g) for g in ww}
        if mask and triple:
            # The actual a,b,z witness is hidden from the historical twelve
            # a,b names. The missing z bit completes any prescribed values.
            joint = next(wit for wit in w if {name[0] for name in wit} == {"c8", "p", "zc"})
            ab = {name for name in joint if name[0] in {"p", "c8"}}
            assert (len(ab), len(joint)) == (12, 13)
            for law in ("parity", "not-all-equal"):
                illegal = dict.fromkeys(joint, 0)
                if law == "parity":
                    illegal[min(ab, key=repr)] = 1
                partial = {name: illegal[name] for name in ab}
                assert complete_source(h, w, partial, law) is not None
                assert complete_source(hh, ww, partial, law) is not None
                assert complete_source(h, w, illegal, law) is None
                assert complete_source(hh, ww, illegal, law) is not None
            assert visible_spent(h, w, earlier | {"zc", "wc"}) != visible_spent(hh, ww, earlier | {"zc", "wc"})
            for side, near in (("c", False), ("u", True)):
                tagged = full_source(mask, triple, (8, 10) if near else (), retag=side)
                assert tagged[2:] == arms[near][2:]
            low = dict(supply)
            low["p"] -= 1
            assert cut(arms[False][2], low) is None


if __name__ == "__main__":
    main()
