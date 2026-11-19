"""Certify a literal later pair failure using 14 lawful shrinking attachments."""

from collections import Counter, defaultdict
from itertools import combinations
import json
import sys

from networkx import Graph, articulation_points, find_cliques, is_connected

from replay_lifetime import ROOT, EXTEND_ROUND
from verify import Arrangement, connected, round_replay


R, I, S, L, M = 3, 5, 7, 22, 28
MIDS = 4 + 2 * S
H0, H1, OUT = I + MIDS, I + MIDS + 1, -1


class Builder:
    def __init__(self):
        self.rows = [set() for _ in range(I + MIDS + 2)]
        self.width = 0

    def vertex(self):
        j = len(self.rows)
        self.rows.append(set())
        return j

    def distinction(self, a, b=None):
        x = self.width
        self.rows[a].add(x)
        if b is not None:
            self.rows[b].add(x)
        self.width += 1
        return x

    def bundle(self, a, b, count):
        return tuple(self.distinction(a, b) for _ in range(count))


def branch(builder, root):
    """Make M complete groups whose children all join in the second round."""
    a = [builder.vertex() for _ in range(M)]
    b = [builder.vertex() for _ in range(M)]
    common = builder.vertex()
    for parent in a:
        builder.distinction(common, parent)
        builder.bundle(parent, None, M - 1)
    routes = []
    for j, parent in enumerate(b):
        relevant = [site for i, site in enumerate(a) if i != j]
        loose = builder.distinction(parent)
        for k, part in enumerate((relevant[:1], relevant[1:])):
            witness = builder.vertex()
            first = builder.distinction(root, witness)
            second = builder.distinction(witness, parent)
            for site in part:
                builder.distinction(witness, site)
            if not k:
                routes.append((first, second, loose))
    return routes


def source():
    builder = Builder()
    bundle_names = {}
    compressed = []
    for j in range(MIDS):
        mid = I + j
        for i in range(I):
            weight = L if not i and j < 4 else 1
            key = ("anchor", i, j)
            bundle_names[key] = builder.bundle(i, mid, weight)
            compressed.append((key, i, mid, weight))
        color = H0 if j in (0, 1) or 4 <= j < 4 + S else H1
        weight = L if j < 4 else M
        key = ("spoke", j)
        bundle_names[key] = builder.bundle(color, mid, weight)
        compressed.append((key, color, mid, weight))
        if j >= 4:
            compressed.append((("branch", j), OUT, mid, M))
    external = []
    for j in range(4, MIDS):
        first = len(builder.rows)
        routes = branch(builder, I + j)
        external.append({"mid": j, "branch_vertices": list(range(first, len(builder.rows))), "route_prefixes": routes})
    return Arrangement.parse([sorted(row) for row in builder.rows]), bundle_names, compressed, external


def actual_growth(start, grow1):
    stages = [start]
    all_records = []
    for _ in range(2):
        earlier = stages[-1]
        grown = Arrangement.parse([sorted(row) for row in grow1(earlier.stars)])
        stages.append(grown)
        all_records.append(round_replay(earlier, grown))
    for stage in stages:
        ends, _, outside = stage.holder_graph()
        graph = Graph(list(ends.values()))
        assert outside is not None and is_connected(graph) and all(len(row) >= 3 for row in stage.stars)
        assert not set(articulation_points(graph))
    return stages, all_records


def optimized_production_round(stars, law):
    presentation = law.C.S.from_junctions([sorted(support) for support in stars])

    def maximal_groups(live, cap):
        assert cap is None
        active = set(live)
        witnesses = [neighbors & active for neighbors in presentation.nbr]
        graph = Graph()
        graph.add_nodes_from(sorted(active))
        for members in witnesses:
            graph.add_edges_from(combinations(sorted(members), 2))
        valid = [tuple(sorted(c)) for c in find_cliques(graph)
                 if len(c) >= 3 and not any(set(c) <= members for members in witnesses)]
        covered = {pair for c in valid for pair in combinations(c, 2)}
        pairs = sorted(tuple(sorted(pair)) for pair in graph.edges if tuple(sorted(pair)) not in covered)
        return [frozenset(members) for members in [*sorted(valid), *pairs]]

    presentation.groups_among = maximal_groups
    result = presentation.step(law.C.S.gf2(law.C.F.fewest), None)
    assert result is not None and result["new"]
    return [frozenset(s) for s in presentation.bits_of]


def follow(ends, node, route):
    for x in route:
        u, v = ends[x]
        assert node in (u, v)
        node = v if u == node else u
    return node


def branch_certificates(stages, records, external, bundles):
    start, current, following = stages
    after_one, after_two = records
    born_of_taken = {x: j for j, row in enumerate(after_one, len(start.stars)) for x in row["taken"].values()}
    born_next = {x: j for j, row in enumerate(after_two, len(current.stars)) for x in row["taken"].values()}
    ends, _, outside = current.holder_graph()
    traces = []
    for arm in external:
        j = arm["mid"]
        mid = I + j
        current_children = []
        old_routes = []
        tip_names = []
        for x, prefix in zip(bundles["spoke", j], arm["route_prefixes"]):
            p = born_of_taken[prefix[-1]]
            current_children.append(p)
            row = after_one[p - len(start.stars)]
            assert len(row["taken"]) == M and row["demand"] == 1 and not row["implied"]
            (tip,) = row["fresh"]
            tip_names.append(tip)
            hub = next(u for u in ends[x] if u != mid)
            path = (x, *prefix, tip)
            assert follow(ends, hub, path) == outside
            old_routes.append(path)
        assert len(set(current_children)) == M and len({x for route in old_routes for x in route}) == 5 * M
        assert {x for n in current_children for x in current.stars[n] if x in current.loose} == set(tip_names)
        (child,) = {born_next[x] for x in tip_names}
        last = after_two[child - len(current.stars)]
        assert set(last["taken"]) == set(current_children) and last["demand"] == 0 and not last["implied"]
        (fresh,) = last["fresh"]
        traces.append({**arm, "old_terminal_routes": old_routes, "births_round_one": current_children,
                       "birth_round_two": child, "next_sole_loose": fresh})
    assert len(after_one) == len(external) * M and len(after_two) == len(external)
    # Each color has one family of routes on disjoint distinction names, with common endpoints only.
    for hub in (H0, H1):
        paths = [path for arm in traces for path in arm["old_terminal_routes"] if hub in ends[path[0]]]
        assert len(paths) == S * M and len({x for path in paths for x in path}) == 5 * S * M
    return traces


def image_key(key):
    j = {0: 2, 2: 0}.get(key[-1], key[-1])
    return (*key[:-1], j)


def check_folded_projection(compressed):
    folded = [(key, H0 if u in (H0, H1, OUT) else u, mid, weight) for key, u, mid, weight in compressed]
    by_name = {key: (u, mid, weight) for key, u, mid, weight in folded}
    for key, u, mid, weight in folded:
        image = image_key(key)
        assert by_name[image] == (u, I + image[-1], weight)

    # Queries on repeated physical labels in one bundle reduce to a single mark on that bundle.
    count = Counter()
    largest = 0
    certificates = {}
    for k in range(1, R + 1):
        for marks in combinations(folded, k):
            mids = frozenset(mid for _, _, mid, _ in marks)
            touched = {u for _, u, _, _ in marks}
            spare = next(u for u in range(1, I) if u not in touched)
            key = (mids, spare)
            if key not in certificates:
                inner = set(mids) | {spare}
                crossings = {name for name, u, mid, _ in folded if (u in inner) != (mid in inner)}
                cost = sum(weight for name, _, _, weight in folded if name in crossings)
                assert 0 < len(mids) < MIDS
                # Each side has both parts of the complete high–middle incidence pattern.
                assert all(any(u == a and v == mid for _, u, v, _ in folded)
                           for a in range(I) for mid in mids | {next(v for v in range(I, I + MIDS) if v not in mids)})
                assert any(u == H0 and mid not in mids for _, u, mid, _ in folded)
                certificates[key] = crossings, cost
            crossings, cost = certificates[key]
            assert all(name in crossings for name, _, _, _ in marks)
            assert cost <= MIDS + R * (2 * M + I - 2) < S * M
            largest = max(largest, cost)
            count[k] += 1
    return folded, {"bundles": len(folded), "queries_checked": dict(count), "distinct_shores": len(certificates),
                    "largest_constructed_bond": largest, "least_hub_separation_lower_bound": S * M}


def exact_folded_minimum(folded, marked):
    """Optimize the middles independently for each of the 2**I anchor assignments."""
    answer = float("inf")
    for mask in range(1 << I):
        outside_high_count = 1 + I - mask.bit_count()  # includes the folded hub
        side_cost = [[0, 0] for _ in range(MIDS)]
        required = {}
        for key, u, mid, weight in folded:
            high = (mask >> u) & 1 if u < I else 0
            side_cost[mid - I][1 - high] += weight
            if key in marked:
                m = mid - I
                if m in required and required[m] != 1 - high:
                    break
                required[m] = 1 - high
        else:
            ones = sum(required.values())
            cost = sum(side_cost[m][side] for m, side in required.items())
            differences = []
            for m, (zero, one) in enumerate(side_cost):
                if m not in required:
                    cost += zero
                    differences.append(one - zero)
            differences.sort()
            for k in range(len(differences) + 1):
                selected = k + ones
                if ((mask == 0 and selected == 1) or
                    (mask != 0 and (selected > 0 or mask.bit_count() == 1))):
                    if selected < MIDS or outside_high_count == 1:
                        answer = min(answer, cost)
                if k < len(differences):
                    cost += differences[k]
    return answer if answer < float("inf") else None


def exact_future_minimum(compressed, marked, following, arms):
    weights = [(key, u, mid, 1 if key[0] == "branch" else weight) for key, u, mid, weight in compressed]
    # Use a bit for each compressed holder; OUT is the final bit.
    size = H1 + 2
    outer_id = size - 1
    weights = [(key, outer_id if u == OUT else u, mid, w) for key, u, mid, w in weights]
    neighbors = [0] * size
    for _, u, v, _ in weights:
        neighbors[u] |= 1 << v
        neighbors[v] |= 1 << u
    universe = (1 << size) - 1
    high = [*range(I), H1, outer_id]  # H0 stays outside, fixing the complement choice.
    seed = (1 << 1) | sum(1 << v for key, _, v, _ in weights if key in marked)
    assert connected(seed, neighbors) and connected(universe ^ seed, neighbors)
    best_shore = seed
    best = sum(w for _, u, v, w in weights if (seed >> u ^ seed >> v) & 1)
    visits = 0
    for mask in range(1 << len(high)):
        high_shore = sum(1 << u for i, u in enumerate(high) if mask >> i & 1)
        cost = [[0, 0] for _ in range(MIDS)]
        allowed = [[0, 1] for _ in range(MIDS)]
        for key, u, v, w in weights:
            crossing = 1 - (high_shore >> u & 1)
            cost[v - I][crossing] += w
            if key in marked:
                allowed[v - I] = [side for side in allowed[v - I] if side == crossing]
        if any(not sides for sides in allowed):
            continue
        bound = [0] * (MIDS + 1)
        for j in reversed(range(MIDS)):
            bound[j] = bound[j + 1] + min(cost[j][side] for side in allowed[j])

        def inspect(j, paid, shore):
            nonlocal best, best_shore, visits
            if paid + bound[j] >= best:
                return
            if j == MIDS:
                visits += 1
                if connected(shore, neighbors) and connected(universe ^ shore, neighbors):
                    best, best_shore = paid, shore
                return
            for side in sorted(allowed[j], key=lambda side: cost[j][side]):
                inspect(j + 1, paid + cost[j][side], shore | (side << (I + j)))

        inspect(0, 0, high_shore)

    ends, adjacent, outer = following.holder_graph()
    shore = {j for j in range(outer_id) if best_shore >> j & 1}
    if best_shore >> outer_id & 1:
        shore.add(outer)
    for arm in arms:
        if I + arm["mid"] in shore:
            shore.update([*arm["branch_vertices"], *arm["births_round_one"], arm["birth_round_two"]])
    bitset = sum(1 << j for j in shore)
    assert connected(bitset, adjacent) and connected(((1 << len(adjacent)) - 1) ^ bitset, adjacent)
    cut = sorted(x for x, (u, v) in ends.items() if (u in shore) != (v in shore))
    assert len(cut) == best
    return {"minimum_common_bond_size": best, "attaining_bond": cut, "candidate_shores_examined": visits}


def witness_pair(stages, traces, bundles):
    current, following = stages[1:]
    partial = {}
    for key, names in bundles.items():
        partial.update(zip(names, bundles[image_key(key)]))
    phi = {x: partial.get(x, x) for x in current.labels}
    assert set(phi.values()) == set(phi)
    assert all(phi[x] == x for j in current.live for x in current.stars[j])
    columns = defaultdict(set)
    for x, holders in current.owners.items():
        columns[tuple(holders)].add(x)
    old_partition = {frozenset(names) for names in columns.values()}
    assert {frozenset(phi[x] for x in names) for names in old_partition} == old_partition

    ends, adjacent, _ = following.holder_graph()
    inside = {H0}
    for arm in traces:
        j = arm["mid"]
        if j < 4 + S:
            inside.update([I + j, *arm["branch_vertices"], *arm["births_round_one"], arm["birth_round_two"]])
    side = sum(1 << j for j in inside)
    assert connected(side, adjacent) and connected(((1 << len(adjacent)) - 1) ^ side, adjacent)
    cut = sorted(x for x, (u, v) in ends.items() if (u in inside) != (v in inside))
    red = [("spoke", 0), ("spoke", 1), ("anchor", 0, 1), ("anchor", 0, 0)]
    blue = [("spoke", 2), ("spoke", 3), ("anchor", 0, 3), ("anchor", 0, 2)]
    cycles = [[bundles[key][0] for key in keys] for keys in (red, blue)]
    assert follow(ends, I, cycles[0]) == I and follow(ends, I + 2, cycles[1]) == I + 2
    assert all(len(bundles[key]) == L for key in red + blue) and not set(red) & set(blue)
    for key in red + blue:
        assert len({tuple(sorted(ends[x])) for x in bundles[key]}) == 1
    a, b = cycles[0][:2]
    assert (phi[a], phi[b]) == (cycles[1][0], b) and {a, b} <= set(cut)
    assert len(cut) == 2 * L + S * (I + 1) < 4 * L
    allowed = set(cycles[0])
    old_row_image = {phi[x] for x in current.stars[H0]}
    assert all(len(row & allowed) % 2 == 0 for row in current.stars) and len(old_row_image & allowed) == 1
    return {"marked_pair": (a, b), "image_pair": (phi[a], phi[b]), "next_bond_upper_bound": len(cut),
            "next_image_minimum_lower_bound": 4 * L, "successor_bond": cut, "successor_inside": sorted(inside),
            "lower_bound_cycles": cycles, "allowed_difference_violating_image": cycles[0],
            "changed_names": sorted((x, y) for x, y in phi.items() if x != y),
            "all_live_distinctions_fixed": True, "all_pair_flip_bits_preserved": True}


def main():
    sys.path.insert(0, str(ROOT / "experiments" / EXTEND_ROUND))
    import extend as law

    start, bundles, compressed, arms = source()
    stages, records = actual_growth(start, lambda stars: optimized_production_round(stars, law))
    traces = branch_certificates(stages, records, arms, bundles)
    folded, projection = check_folded_projection(compressed)
    pair = {("spoke", 0), ("spoke", 1)}
    probe = ("branch", 4)
    for label, marks in [("pair", pair), ("pair_with_fixed_branch_mark", pair | {probe})]:
        measured = exact_folded_minimum(folded, marks)
        assert measured == exact_folded_minimum(folded, {image_key(key) for key in marks}) and measured < S * M
        projection[label] = {"size_at_source_and_image": measured, "marks": sorted(marks)}
    projection["pair_with_fixed_branch_mark"]["literal_loose_name_of_cost_M"] = traces[0]["old_terminal_routes"][0][-1]
    future = witness_pair(stages, traces, bundles)
    future["exact_source"] = exact_future_minimum(compressed, pair, stages[-1], traces)
    future["exact_image"] = exact_future_minimum(compressed, {image_key(key) for key in pair}, stages[-1], traces)
    result = {"parameters": dict(mark_order=R, anchors=I, shields_of_each_color=S, hot_weight=L, shield_weight=M),
              "sizes": [(len(stage.stars), len(stage.labels)) for stage in stages],
              "literal_start": [sorted(s) for s in start.stars],
              "literal_round_additions": [[sorted(row) for row in b.stars[len(a.stars):]] for a, b in zip(stages, stages[1:])],
              "branch_certificates": traces, "folded_reading_certificates": projection,
              "future_pair_witness": future}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
