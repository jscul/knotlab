"""Verify the two-bundle pivot and replay the specified seven-knot examples."""

from collections import Counter, deque
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[3]
LAW = ROOT / "experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots/startlib.py"
spec = spec_from_file_location("reached_pivot_law", LAW)
production = module_from_spec(spec)
spec.loader.exec_module(production)
M, A, B = range(3)
EXACT_VERTEX_CAP = 18


def fans(a, b, bundle=2, spoke=1, loose=2, right_spoke=None):
    """M neighbors A and B. Each side is a fan with the given number of leaves."""
    stars = [[] for _ in range(3 + a + b)]
    meetings = [(M, A, bundle), (M, B, bundle)]
    meetings += [(A, j, spoke) for j in range(3, 3 + a)]
    right_weight = spoke if right_spoke is None else right_spoke
    meetings += [(B, j, right_weight) for j in range(3 + a, len(stars))]
    name = 0
    for u, v, count in meetings:
        for _ in range(count):
            stars[u].append(name)
            stars[v].append(name)
            name += 1
    for j in range(3, len(stars)):
        stars[j].extend(range(name, name + loose))
        name += loose
    assert all(len(star) >= 3 for star in stars)
    return tuple(tuple(star) for star in stars)


def incidence(stars):
    owners = {}
    neighbors = [set() for _ in stars]
    for site, star in enumerate(stars):
        assert len(star) == len(set(star))
        for bit in star:
            owners.setdefault(bit, []).append(site)
    assert set(owners) == set(range(len(owners)))
    for holders in owners.values():
        assert len(holders) in (1, 2)
        if len(holders) == 2:
            u, v = holders
            neighbors[u].add(v)
            neighbors[v].add(u)
    return owners, neighbors


def wired(stars):
    owners, _ = incidence(stars)
    outside = len(stars) if any(len(ends) == 1 for ends in owners.values()) else None
    links = [tuple(owners[b]) if len(owners[b]) == 2 else (owners[b][0], outside) for b in range(len(owners))]
    return links, len(stars) + (outside is not None)


def pivot_cut(stars, m):
    """Return the A-to-B cut minimum after removing M, by integral max flow."""
    links, count = wired(stars)
    assert {i for i, ends in enumerate(links) if M in ends} == set(range(2*m))
    assert all(set(ends) == {M, A if i < m else B} for i, ends in enumerate(links[:2*m]))
    residual = [Counter() for _ in range(count)]
    for u, v in links[2*m:]:
        residual[u][v] += 1
        residual[v][u] += 1
    flow = 0
    while True:
        parents = {A: None}
        queue = deque([A])
        while queue and B not in parents:
            u = queue.popleft()
            for v in sorted(residual[u]):
                if residual[u][v] > 0 and v not in parents:
                    parents[v] = u
                    queue.append(v)
        if B not in parents:
            cut = [i for i, (u, v) in enumerate(links) if i >= 2*m and (u in parents) != (v in parents)]
            assert len(cut) == flow
            return {"lambda": flow, "attaining_side": sorted(parents), "cut": cut}
        v = B
        while v != A:
            u = parents[v]
            residual[u][v] -= 1
            residual[v][u] += 1
            v = u
        flow += 1


def planned_groups(live, adjacency):
    pairs = [pair for pair in combinations(live, 2) if adjacency[pair[0]] & adjacency[pair[1]]]
    pair_set = set(pairs)
    cliques = [frozenset(group) for size in range(3, len(live) + 1) for group in combinations(live, size)
               if all(pair in pair_set for pair in combinations(group, 2))
               and not set.intersection(*(adjacency[j] for j in group))]
    maximal = [group for group in cliques if not any(group < larger for larger in cliques)]
    return maximal + [frozenset(pair) for pair in pairs if not any(set(pair) <= group for group in maximal)]


def validate_round(old, new):
    owners, adjacency = incidence(old)
    after, following = incidence(new)
    assert new[:len(old)] == old
    loose = {bit: ends[0] for bit, ends in owners.items() if len(ends) == 1}
    slots = Counter(loose.values())
    groups = planned_groups(sorted(slots), adjacency)
    planned = Counter(groups)
    uses = Counter(parent for group in groups for parent in group)
    for parent in slots:
        assert slots[parent] >= uses[parent]
        planned[frozenset({parent})] += slots[parent] - uses[parent]
    sites = list(range(len(old), len(new)))
    demand = Counter(j for group in planned_groups(sites, following) for j in group)
    consumed = Counter()
    actual, actions = Counter(), []
    for j in sites:
        takes = tuple(b for b in new[j] if b in owners)
        fresh = tuple(b for b in new[j] if b not in owners)
        parents = frozenset(loose[b] for b in takes)
        assert len(takes) == len(parents) and all(after[b] == [j] for b in fresh)
        implied = set(takes) == loose.keys()
        assert len(fresh) == (demand[j] if implied else max(demand[j], 3 - len(parents), 1))
        actual[parents] += 1
        consumed.update(takes)
        actions.append({"site": j, "parents": sorted(parents), "taken": takes, "fresh": fresh,
                        "k": len(takes), "f": len(fresh), "lookahead_demand": demand[j]})
    assert actual == +planned and consumed == Counter(loose.keys())
    return actions


def grow(start, rounds):
    P = production.from_junctions([list(row) for row in start])
    stages, actions = [start], []
    for _ in range(rounds):
        result = P.step(production.gf2(production.F.fewest), None)
        assert result and result["new"] > 0 and P.implied_mismatch == 0
        new = tuple(tuple(sorted(star)) for star in P.bits_of)
        actions.append(validate_round(stages[-1], new))
        stages.append(new)
    return stages, actions


def full_table(stars):
    """Independent exact minima across all cuts with both shores connected."""
    links, count = wired(stars)
    assert count <= EXACT_VERTEX_CAP
    neighbors = [0] * count
    words = [0] * count
    for i, (u, v) in enumerate(links):
        neighbors[u] |= 1 << v
        neighbors[v] |= 1 << u
        words[u] |= 1 << i
        words[v] |= 1 << i

    def connected(inside):
        pending = reached = inside & -inside
        while pending:
            v = pending & -pending
            more = neighbors[v.bit_length()-1] & inside & ~reached
            reached |= more
            pending = (pending ^ v) | more
        return inside == reached

    all_sites = (1 << count) - 1
    assert connected(all_sites)
    cuts = [0]
    for word in words[1:]:
        cuts += [previous ^ word for previous in cuts]
    width = len(links)
    minima = [[None] * width for _ in links]
    for i in range(1, len(cuts)):
        side = i << 1
        if not connected(side) or not connected(all_sites ^ side):
            continue
        cut = cuts[i]
        size = cut.bit_count()
        bits = []
        while cut:
            low = cut & -cut
            bits.append(low.bit_length() - 1)
            cut ^= low
        for a, b in combinations(bits, 2):
            if minima[a][b] is None or size < minima[a][b]:
                minima[a][b] = minima[b][a] = size
    return minima


def discrepancies(matrix, a, b):
    image = list(range(len(matrix)))
    image[a], image[b] = b, a
    return [(x, y) for x, y in combinations(range(len(matrix)), 2)
            if matrix[x][y] != matrix[image[x]][image[y]]]


def measure(label, start, m, growth_rounds):
    stages, actions = grow(start, growth_rounds)
    cuts = [pivot_cut(stage, m) for stage in stages]
    current, next_stage = stages[-2:]
    table, after = full_table(current), full_table(next_stage)
    old_diff, new_diff = discrepancies(table, 0, m), discrepancies(after, 0, m)
    assert not discrepancies(after, 0, 1)
    owners, neighbors = incidence(current)
    loose = {b for b, ends in owners.items() if len(ends) == 1}
    live = {owners[b][0] for b in loose}
    assert not {M,A,B} & live
    assert all(len(owners[bit]) == 2 for bit in (0, 1, m))
    old_k = table[0][1], table[m][1]
    new_k = after[0][1], after[m][1]
    for (k, k_cross), cut in zip((old_k, new_k), cuts[-2:], strict=True):
        flow = cut["lambda"]
        assert (k, k_cross) == ((min(2*m, m+flow), 2*m) if flow else (m, None))
    assert bool(old_diff) == (cuts[-2]["lambda"] < m)
    assert bool(new_diff) == (cuts[-1]["lambda"] < m)
    assert all(len({0,1} & set(row)) % 2 == 0 for row in current)
    assert any(len({m,1} & set(row)) % 2 for row in current)
    return {"example": label, "start_junctions": len(start), "m": m, "age_of_current": growth_rounds-1,
            "stages": stages, "production_rounds_checked_by_subsets": actions, "pivot_cuts": cuts,
            "swap": [0,m], "old_pair": [0,1], "image_pair": [1,m],
            "old_D": tuple(k-1 if k is not None else None for k in old_k),
            "next_D": tuple(k-1 if k is not None else None for k in new_k),
            "pair_counts_current_and_next": [len(table)*(len(table)-1)//2, len(after)*(len(after)-1)//2],
            "full_table_disagreements_current_and_next": [len(old_diff), len(new_diff)],
            "next_disagreements_all_named": new_diff,
            "reading_fixed": {"live": sorted(live), "loose_bits": sorted(loose),
                              "live_neighbor_sets": sorted({tuple(sorted(row & live)) for row in neighbors})},
            "allowed_flips_to_forbidden": [[0,1], [1,m]],
            "within_bundle_transposition_extends": True,
            "all_extensions_refuted_at_two_previously_shared_bits": not old_diff and new_k[0] != new_k[1]}


def run():
    reached = measure("three_left_leaves_one_right_double_spoke", fans(3, 1, right_spoke=2), 2, 2)
    static = measure("static_detector_control", fans(2, 2, spoke=2, loose=1), 2, 1)
    rejected = measure("single_right_spoke_rejects_current_symmetry", fans(3, 1), 2, 2)
    assert reached["age_of_current"] == 1 and reached["all_extensions_refuted_at_two_previously_shared_bits"]
    assert static["age_of_current"] == 0 and static["all_extensions_refuted_at_two_previously_shared_bits"]
    assert rejected["full_table_disagreements_current_and_next"][0] > 0
    return {"freeze": "a254c8c57", "exact_vertex_cap": EXACT_VERTEX_CAP, "named_cases": [reached, static, rejected],
            "start_law_sha256": sha256(LAW.read_bytes()).hexdigest(),
            "round_law_sha256": sha256(Path(production.F.__file__).read_bytes()).hexdigest(),
            "further_template_enumeration_stopped_at_certified_obstruction": True}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
