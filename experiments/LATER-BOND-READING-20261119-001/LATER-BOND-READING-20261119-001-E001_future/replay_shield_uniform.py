"""Verify selected uniform shield parameters by literal growth and exact connected cuts."""

import argparse
from collections import defaultdict
from itertools import combinations
import json
from math import comb
import sys

from replay_shield import EXTEND_ROUND, ROOT, actual_growth, follow, optimized_production_round
from verify import Arrangement, connected, indices


class Fixture:
    def __init__(self, anchors, shields, hot, capacity, compact, *, anchor_hot=None, shield_weight=None):
        self.i, self.s, self.l, self.m = anchors, shields, hot, capacity
        self.compact = compact and capacity >= 3
        self.middle_count = 4 + 2 * shields
        self.hubs = (anchors + self.middle_count, anchors + self.middle_count + 1)
        self.outside = self.hubs[-1] + 1
        self.supports = [set() for _ in range(self.outside)]
        self.names = 0
        self.edges = []
        self.physical = {}
        self.arms = {}
        for j in range(self.middle_count):
            p = anchors + j
            for a in range(anchors):
                heavy = hot if anchor_hot is None else anchor_hot
                self.compressed_edge(("anchor", a, j), a, p, heavy if a == 0 and j < 4 else 1)
            red = (j in (0, 1) or 4 <= j < 4 + shields)
            weight = capacity if shield_weight is None else shield_weight
            self.compressed_edge(("spoke", j), self.hubs[int(not red)], p, hot if j < 4 else weight)
            if j >= 4:
                self.edges.append((("branch", j), p, self.outside, capacity, 1))
        for j in range(4, self.middle_count):
            self.arms[j] = self.branch(anchors + j)

    def site(self):
        j = len(self.supports)
        self.supports.append(set())
        return j

    def wire(self, u, v=None):
        x = self.names
        self.names += 1
        self.supports[u].add(x)
        if v is not None:
            self.supports[v].add(x)
        return x

    def loose(self, u, count):
        for _ in range(count):
            self.wire(u)

    def compressed_edge(self, name, a, b, weight):
        self.edges.append((name, a, b, weight, weight))
        self.physical[name] = [self.wire(a, b) for _ in range(weight)]

    def branch(self, pole):
        first = len(self.supports)
        if self.m == 2:
            u, v, s, a, b = [self.site() for _ in range(5)]
            pu, pv = self.wire(pole, u), self.wire(pole, v)
            ua, vb = self.wire(u, a), self.wire(v, b)
            self.wire(u, s)
            self.wire(v, s)
            self.wire(a, b)
            self.loose(s, 2)
            self.loose(a, 1)
            self.loose(b, 1)
            route_plan = [({s, a}, a, (pu, ua)), ({s, b}, b, (pv, vb))]
        else:
            assert self.m >= 3
            r = [self.site() for _ in range(self.m)]
            if self.compact:
                s = self.site()
                u, v = r[1:3]
            else:
                u, v, s = self.site(), self.site(), self.site()
            from_pole = [self.wire(pole, a) for a in r]
            for i, a in enumerate(r[1:], 1):
                if not self.compact:
                    self.wire(u if i == 1 else v, a)
                elif a not in (u, v):
                    self.wire(u if i % 2 else v, a)
                self.loose(a, 2)
            self.wire(u, v)
            self.wire(u, s)
            self.wire(v, s)
            self.loose(r[0], self.m - 1)
            self.loose(s, 1)
            route_plan = [(set(r[1:]) | {s}, r[1], (from_pole[1],)),
                          ({r[0], r[1]}, r[0], (from_pole[0],)),
                          *(({r[0], a}, a, (from_pole[i],)) for i, a in enumerate(r[2:], 2))]
        return {"old_sites": list(range(first, len(self.supports))), "original_route_plan": route_plan}

    def archive_supports(self):
        return Arrangement.parse([sorted(s) for s in self.supports])


def image_key(key):
    j = {0: 2, 2: 0}.get(key[-1], key[-1])
    return (*key[:-1], j)


def current_map(fixture, stage):
    partial = {}
    for key, names in fixture.physical.items():
        partial.update(zip(names, fixture.physical[image_key(key)]))
    mapping = {x: partial.get(x, x) for x in stage.labels}
    assert set(mapping) == set(mapping.values())
    assert all(mapping[x] == x for j in stage.live for x in stage.stars[j])
    columns = defaultdict(set)
    for x, owners in stage.owners.items():
        columns[tuple(owners)].add(x)
    assert {frozenset(group) for group in columns.values()} == {
        frozenset(mapping[x] for x in group) for group in columns.values()}
    return mapping


def branch_certificates(fixture, stages, records):
    initial, current, following = stages
    old, next_ = records
    by_parents = {frozenset(row["taken"]): (j, row) for j, row in enumerate(old, len(initial.stars))}
    next_by_parents = {frozenset(row["taken"]): (j, row) for j, row in enumerate(next_, len(current.stars))}
    ends, _, outside = current.holder_graph()
    results = {}
    allocated = set()
    for j, arm in fixture.arms.items():
        pole = fixture.i + j
        new_sites, routes = [], []
        for parents, route_parent, prefix in arm["original_route_plan"]:
            new, step = by_parents[frozenset(parents)]
            assert step["demand"] == 1 and not step["implied"]
            (loose,) = step["fresh"]
            route = (*prefix, step["taken"][route_parent], loose)
            assert follow(ends, pole, route) == outside
            routes.append(route)
            new_sites.append(new)
        assert len(new_sites) == fixture.m and len(set(new_sites)) == fixture.m
        all_names = {x for path in routes for x in path}
        assert len(all_names) == sum(map(len, routes)) and not all_names & allocated
        allocated.update(all_names)
        assert {x for site in new_sites for x in current.stars[site] if x in current.loose} == {p[-1] for p in routes}
        child, step = next_by_parents[frozenset(new_sites)]
        assert step["demand"] == 0 and not step["implied"]
        (next_tip,) = step["fresh"]
        assert {x for site in [*new_sites, child] for x in following.stars[site] if x in following.loose} == {next_tip}
        results[j] = {"old_sites": arm["old_sites"], "children_age_one": new_sites,
                      "children_age_two": [child], "literal_capacity_routes": routes, "second_age_sole_loose": next_tip}
    assert len(old) == len(results) * fixture.m and len(next_) == len(results)
    return results


def connected_shores(fixture):
    stars = [0] * (fixture.outside + 1)
    adjacency = stars.copy()
    for j, (_, u, v, _, _) in enumerate(fixture.edges):
        stars[u] |= 1 << j
        stars[v] |= 1 << j
        adjacency[u] |= 1 << v
        adjacency[v] |= 1 << u
    full = (1 << len(stars)) - 1
    shore = cut = 0
    items = []
    for step in range(1, 1 << fixture.outside):
        changed = step & -step
        shore ^= changed
        cut ^= stars[changed.bit_length() - 1]
        if connected(shore, adjacency) and connected(full ^ shore, adjacency):
            weights = [fixture.edges[j][3:] for j in indices(cut)]
            items.append((cut, shore, sum(a for a, _ in weights), sum(b for _, b in weights)))
    return items


class Minimum:
    """Read exact minima from an incidence bitset ordered by connected-cut cost."""

    def __init__(self, bonds, names, age):
        age_column = age + 1
        self.ranked = sorted(bonds, key=lambda cell: cell[age_column])
        packed = [bytearray((len(bonds) + 7) // 8) for _ in names]
        for i, (support, _, _, _) in enumerate(self.ranked):
            byte, position = divmod(i, 8)
            for j in indices(support):
                packed[j][byte] |= 1 << position
        self.members = [int.from_bytes(row, "little") for row in packed]
        self.age_column = age_column

    def mark(self, positions):
        p, *rest = positions
        matching = self.members[p]
        for q in rest:
            matching &= self.members[q]
        if not matching:
            return None, None
        first = (matching & -matching).bit_length() - 1
        record = self.ranked[first]
        return record[self.age_column], record[1]


def literal_minimum_witness(fixture, stage, compressed_shore, arms, age):
    ends, adjacent, outer = stage.holder_graph()
    shore = {j for j in indices(compressed_shore) if j != fixture.outside}
    if compressed_shore >> fixture.outside & 1:
        shore.add(outer)
    for j, arm in arms.items():
        if fixture.i + j in shore:
            shore.update([*arm["old_sites"], *arm["children_age_one"]])
            if age == 2:
                shore.update(arm["children_age_two"])
    flags = sum(1 << j for j in shore)
    assert connected(flags, adjacent) and connected(((1 << len(adjacent)) - 1) ^ flags, adjacent)
    cut = sorted(x for x, (u, v) in ends.items() if (u in shore) != (v in shore))
    return {"literal_shore": sorted(shore), "bond": cut}


def audit(parameters, law, top_order, compact):
    f = Fixture(*parameters, compact)
    start = f.archive_supports()
    stages, steps = actual_growth(start, lambda stars: optimized_production_round(stars, law))
    arms = branch_certificates(f, stages, steps)
    mapping = current_map(f, stages[1])
    keys = [row[0] for row in f.edges]
    position = {key: j for j, key in enumerate(keys)}
    permuted = [position[image_key(key)] for key in keys]
    bonds = connected_shores(f)
    old, new = Minimum(bonds, keys, 1), Minimum(bonds, keys, 2)
    largest = 0
    summary = {}
    first = None
    for order in range(1, top_order + 1):
        examined = different = 0
        max_finite = 0
        for query in combinations(range(len(keys)), order):
            image = tuple(sorted(permuted[j] for j in query))
            if query > image:
                continue
            examined += 1
            source_value, _ = old.mark(query)
            image_value = source_value if image == query else old.mark(image)[0]
            for value in (source_value, image_value):
                if value is not None:
                    max_finite = max(max_finite, value)
            if source_value != image_value:
                different += 1
                if first is None:
                    first = (query, image, source_value, image_value)
        summary[order] = {"all_queries": comb(len(keys), order), "orbits_examined": examined,
                          "difference_orbits": different, "largest_finite_minimum": max_finite}
        if order <= 3:
            largest = max(largest, max_finite)
            assert not different, (parameters, order, first)

    def representative(pos):
        key = keys[pos]
        return arms[key[-1]]["literal_capacity_routes"][0][-1] if key[0] == "branch" else f.physical[key][0]

    quartet = None
    if first is not None:
        q, p, v, w = first
        quartet = {"query": [keys[j] for j in q], "image": [keys[j] for j in p], "sizes": (v, w),
                   "literal_query": [representative(j) for j in q], "literal_image": [representative(j) for j in p]}
        for name, item, desired in [("source", q, v), ("target", p, w)]:
            size, shore = old.mark(item)
            if size is not None:
                witness = literal_minimum_witness(f, stages[1], shore, arms, 1)
                assert len(witness["bond"]) == desired and {representative(j) for j in item} <= set(witness["bond"])
                quartet[name] = witness

    pair = tuple(sorted(position[key] for key in (("spoke", 0), ("spoke", 1))))
    pair_image = tuple(sorted(permuted[k] for k in pair))
    before = [old.mark(q)[0] for q in (pair, pair_image)]
    following = [new.mark(q) for q in (pair, pair_image)]
    assert before[0] == before[1] and following[0][0] != following[1][0]
    assert [mapping[representative(j)] for j in pair] == [representative(permuted[j]) for j in pair]
    next_certificates = []
    for q, (size, shore) in zip((pair, pair_image), following):
        literal = literal_minimum_witness(f, stages[2], shore, arms, 2)
        assert len(literal["bond"]) == size and {representative(j) for j in q} <= set(literal["bond"])
        next_certificates.append(literal)

    return {"parameters": parameters, "compact_branch": f.compact,
            "literal_sizes": [(len(a.stars), len(a.labels)) for a in stages],
            "literal_start": [sorted(row) for row in stages[0].stars],
            "literal_round_additions": [[sorted(row) for row in b.stars[len(a.stars):]] for a, b in zip(stages, stages[1:])],
            "branches": arms, "compressed_names": len(keys), "bond_shores_enumerated": len(bonds),
            "source_hub_separation_bound": f.s * f.m, "largest_current_K_order_at_most_three": largest,
            "readings": summary, "first_quartet_discrepancy": quartet,
            "marked_pair": [representative(j) for j in pair], "image_pair": [representative(j) for j in pair_image],
            "current_K": before, "successor_K": [size for size, _ in following], "literal_bond_certificates": next_certificates}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--params", nargs=4, metavar=("I", "s", "L", "M"), action="append", type=int)
    parser.add_argument("--order", type=int, choices=(3, 4), default=4)
    parser.add_argument("--full-branch", action="store_true")
    options = parser.parse_args()
    sys.path.insert(0, str(ROOT / "experiments" / EXTEND_ROUND))
    import extend as law

    cases = options.params or [[2, 6, 3, 8]]
    print(json.dumps({"cases": [audit(case, law, options.order, not options.full_branch) for case in cases]},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
