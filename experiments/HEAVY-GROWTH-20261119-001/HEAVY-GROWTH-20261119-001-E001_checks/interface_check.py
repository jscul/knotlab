"""Check a recurring tip's exact interface and its rooted finite restrictions."""

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path


def children(parents):
    result = defaultdict(set)
    for point, row in enumerate(parents):
        for parent in row:
            result[parent].add(point)
    return result


def maximal_blocks(blocks):
    distinct = {frozenset(block) for block in blocks if len(block) >= 2}
    return {block for block in distinct if not any(block < other for other in distinct)}


def neighbors(points, blocks):
    result = {v: set() for v in points}
    for block in blocks:
        for v in block:
            result[v].update(block - {v})
    return result


def anchored_groups(points, blocks, focus):
    """Enumerate every required group through focus using local maximal cliques."""
    adj = neighbors(points, blocks)
    large = set()

    def visit(clique, available, excluded):
        if not available and not excluded:
            group = frozenset(clique)
            if len(group) >= 3 and not any(group <= block for block in blocks):
                large.add(group)
            return
        pivot = max(available | excluded, key=lambda v: len(available & adj[v]))
        for v in sorted(available - adj[pivot]):
            visit(clique | {v}, available & adj[v], excluded & adj[v])
            available.remove(v)
            excluded.add(v)

    for v in focus:
        visit({v}, adj[v].copy(), set())
    pairs = {frozenset((v, w)) for v in focus for w in adj[v]}
    for group in large:
        for v in focus & group:
            pairs.difference_update(frozenset((v, w)) for w in group if w != v)
    return large | pairs


def wired_realization(parents, opens):
    """Check every site's local parity projection via deletion in the wired graph."""
    n = len(parents)
    labels = sorted({x for row in parents for x in row})
    hubs = {x: n + i for i, x in enumerate(labels)}
    exterior = n + len(hubs)
    pad1, pad2 = exterior + 1, exterior + 2
    adj = [set() for _ in range(exterior + 3)]
    degree = Counter()

    def add(x, y, count=1):
        adj[x].add(y)
        adj[y].add(x)
        degree[x] += count
        degree[y] += count

    for y, row in enumerate(parents):
        add(y, exterior, opens[y])
        for x in row:
            add(y, hubs[x])
    for hub in hubs.values():
        add(hub, pad1)
        add(hub, pad2)
    add(pad1, pad2)
    assert min(degree[v] for v in range(len(adj)) if v != exterior) >= 3
    for removed in range(len(adj)):
        seed = next(v for v in range(len(adj)) if v != removed)
        seen, frontier = {seed}, {seed}
        while frontier:
            frontier = set().union(*(adj[v] for v in frontier)) - seen - {removed}
            seen.update(frontier)
        assert len(seen) == len(adj) - 1


def stationary_boolean(m):
    # Subsets are numbered by their masks. The tip comes last.
    tip = 1 << m
    parents = []
    for mask in range(tip):
        if not mask:
            parents.append([tip, mask])
        else:
            parents.append([mask] + [mask ^ (1 << j) for j in range(m) if mask & (1 << j)])
    parents.append([tip])
    points = set(range(tip + 1))
    blocks = maximal_blocks(children(parents).values())
    actual = anchored_groups(points, blocks, points)
    expected = {frozenset(row) for row in parents if len(row) >= 2}
    assert expected == actual
    demand = Counter(x for group in actual for x in group)
    opens = {x: max(1, 3 - len(row), demand[x]) for x, row in enumerate(parents)}
    assert {x: opens[x] - demand[x] for x in points if opens[x] > demand[x]} == {tip: 1}
    wired_realization(parents, opens)

    remainder = points - {tip, 0}
    ports = {1 << j for j in range(m)}
    reduced_blocks = maximal_blocks(block & remainder for block in blocks)
    interior = anchored_groups(remainder, reduced_blocks, remainder)
    assert interior == {g for g in actual if g <= remainder}
    assert len(interior) + len(ports) == len(remainder)
    reaches = {tip}
    age = 0
    while reaches != points:
        reaches = {v for v, row in enumerate(parents) if reaches.intersection(row)}
        age += 1
        assert age <= m + 1
    assert age == m + 1
    if m == 2:
        assert interior == {frozenset(remainder)}
        assert all(opens[v] - int(v in ports) == 1 for v in remainder)
    return dict(ports=m, total=len(points), heavy=len(remainder),
                ordinary_internal_groups=len(interior), arity_at_least_three=sum(len(g) >= 3 for g in actual),
                maximum_arity=max(map(len, actual)), entire_generation_descends_from_one_tip_at=age,
                physical_projection_checks=len(points) * 2 + 3)


def distances_from_tip(parents):
    ch = children(parents)
    unary = [i for i, row in enumerate(parents) if len(row) == 1]
    assert len(unary) == 1
    tip = unary[0]
    assert len(ch[parents[tip][0]]) == 2
    dist = {tip: 0}
    seen = set()
    frontier = {tip}
    while frontier:
        dist_next = dist[next(iter(frontier))] + 1
        active = {p for v in frontier for p in parents[v]} - seen
        seen.update(active)
        frontier = set().union(*(ch[p] for p in active)) - dist.keys()
        dist.update({v: dist_next for v in frontier})
    assert len(dist) == len(parents)
    return dist, ch


def germ(block_children, members):
    return maximal_blocks(row & members for row in block_children.values())


def physical_map(old_dist, new_dist, new_parents, radius):
    still = {v: {u for u in new_parents[v] if old_dist[u] == d}
             for v, d in new_dist.items() if d <= radius}
    result = {}
    while still:
        single = {v: next(iter(row)) for v, row in still.items() if len(row) == 1}
        assert single and len(set(single.values())) == len(single)
        result.update(single)
        used = set(single.values())
        still = {v: row - used for v, row in still.items() if v not in single}
    assert set(result.values()) == {v for v, d in old_dist.items() if d <= radius}
    return result


def verify_germ(record):
    rows = record["old_vertices_by_position"]
    d = record["distances_by_position"]
    points = set(range(len(rows)))
    focus = {v for v in points if d[v] < 5}
    blocks = {frozenset(x) for x in record["old_maximal_blocks"]}
    tip, = (v for v in points if d[v] == 0)
    adjacency = neighbors(points, blocks)
    found, last = {tip: 0}, {tip}
    for layer in range(1, 6):
        last = set().union(*(adjacency[u] for u in last)) - found.keys()
        found.update({v: layer for v in last})
    assert found == dict(enumerate(d))
    actual = anchored_groups(points, blocks, focus) | {frozenset({tip})}
    # New positions are transported to their corresponding old positions.
    parents = record["new_parents_in_old_positions"]
    assert len(parents) == len(set(map(frozenset, parents))) == len(actual)
    assert {frozenset(row) for row in parents} == actual
    assert maximal_blocks(children(parents).values()) == blocks
    assert parents[tip] == [tip]
    for i, row in enumerate(parents):
        if i != tip:
            assert 1 + min(d[v] for v in row) == d[i]
    return True


def archive_case(folder, start):
    stages, source_hash = [], {}
    for age in (7, 8):
        path = folder / f"start-{start:02}-age{age:02}.parents.json.gz"
        source_hash[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        with gzip.open(path, "rt") as stream:
            stages.append(json.load(stream))
    old_parents, new_parents = stages
    old_d, old_ch = distances_from_tip(old_parents)
    new_d, new_ch = distances_from_tip(new_parents)
    matching = physical_map(old_d, new_d, new_parents, 5)
    by_old = {old: new for new, old in matching.items()}
    old = sorted(by_old, key=lambda v: (old_d[v], v))
    pos = {v: i for i, v in enumerate(old)}
    old_blocks = germ(old_ch, set(old))
    new_blocks = germ(new_ch, set(matching))
    assert {frozenset(matching[v] for v in block) for block in new_blocks} == old_blocks
    old_ports = [v for v in old if old_d[v] == 2]
    old_companion, = [v for v in old if old_d[v] == 1]
    for port in old_ports:
        assert set(new_parents[by_old[port]]) == {port, old_companion}
    record = dict(start=f"{start:02}", source_sha256=source_hash, ages=[7, 8],
                  old_vertices_by_position=old, new_vertices_by_position=[by_old[v] for v in old],
                  distances_by_position=[old_d[v] for v in old],
                  old_maximal_blocks=sorted(sorted(pos[v] for v in block) for block in old_blocks),
                  new_parents_in_old_positions=[sorted(pos[p] for p in new_parents[by_old[v]]) for v in old],
                  age7_layer_sizes=sorted(Counter(old_d.values()).items()),
                  age8_layer_sizes=sorted(Counter(new_d.values()).items()),
                  heavy_lower_bound_from_age_seven=len(old) - 2)
    assert verify_germ(record)
    return record


def shared_tips():
    # Begin with two reciprocal tips. Every subsequent candidate graph is a path.
    parents = [[0], [0]]
    trace = []
    for age in range(7):
        n = len(parents)
        ch = children(parents)
        blocks = maximal_blocks(ch.values())
        adj = neighbors(range(n), blocks)
        tips = [v for v, row in enumerate(parents) if len(row) == 1]
        assert len(tips) == 2 and all(len(adj[t]) == 1 for t in tips)
        companions = [next(iter(adj[t])) for t in tips]
        port_sets = [adj[b] - {t} for t, b in zip(tips, companions)]
        trace.append(dict(age=age, total=n, light=len(set(tips + companions)),
                          heavy=n - len(set(tips + companions)),
                          distinct_companions=len(set(companions)),
                          outside_port_sets_disjoint=not bool(port_sets[0] & port_sets[1])))
        group = anchored_groups(set(range(n)), blocks, set(range(n)))
        assert all(len(g) == 2 for g in group) and len(group) == n - 1
        assert all(max(1, 3 - len(parents[v]), len(adj[v])) - len(adj[v]) == int(v in tips)
                   for v in range(n))
        parents = [sorted(g) for g in sorted(group, key=lambda s: sorted(s))] + [[t] for t in tips]
    return trace


def single_tip_cycle(m, rounds=4):
    tip, companion = 0, 1
    n = m + 6
    center = n - 1
    cycle = [2, m + 2, m + 3, m + 4]
    blocks = [(tip, companion)] + [(companion, a) for a in range(2, m + 2)]
    blocks.extend((center, v, cycle[(j + 1) % len(cycle)]) for j, v in enumerate(cycle))
    parents = [[] for _ in range(n)]
    for p, block in enumerate(blocks):
        for v in block:
            parents[v].append(p)
    adjacency = neighbors(range(n), map(frozenset, blocks))
    opens = {v: len(adjacency[v]) + int(v == tip) for v in range(n)}
    private = len(blocks)
    for v in range(n):
        if v != tip and len(parents[v]) < 2:
            parents[v].append(private)
            private += 1
    wired_realization(parents, opens)
    trace = []
    for age in range(rounds + 1):
        dist, ch = distances_from_tip(parents)
        assert min(dist[v] for v in cycle) == 2 + age
        ap = germ(ch, set(dist))
        if age >= 1:
            assert sum(d == 2 for d in dist.values()) == m
        trace.append(dict(age=age, heavy=len(parents) - 2, nearest_cycle=min(dist[v] for v in cycle)))
        if age == rounds:
            break
        group = sorted(anchored_groups(set(dist), ap, set(dist)), key=lambda s: sorted(s))
        index = {g: i for i, g in enumerate(group)}
        cycle = [index[frozenset((v, cycle[(j + 1) % len(cycle)]))] for j, v in enumerate(cycle)]
        old_tip = next(v for v, d in dist.items() if d == 0)
        parents = [sorted(g) for g in group] + [[old_tip]]
    return dict(ports=m, trace=trace)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=Path("/var/tmp/hub-sample-20261119"))
    parser.add_argument("--verify", type=Path, help="replay the self-contained radial certificates")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    controls = [stationary_boolean(m) for m in range(7)]
    shared = shared_tips()
    cycles = [single_tip_cycle(m) for m in range(1, 5)]
    if args.verify:
        with args.verify.open() as stream:
            result = json.load(stream)
        assert controls == result["stationary_controls"] and shared == result["shared_tip_control"]
        assert cycles == result["one_tip_cycle_controls"]
        assert all(verify_germ(record) for record in result["radius_five_certificates"])
        print("Verified seven stationary controls, a shared-companion path, four one-tip cycle controls and both radius-five certificates.")
        return
    result = dict(stationary_controls=controls, shared_tip_control=shared, one_tip_cycle_controls=cycles,
                  radius_five_certificates=[archive_case(args.archive, start) for start in (3, 14)])
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    else:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
