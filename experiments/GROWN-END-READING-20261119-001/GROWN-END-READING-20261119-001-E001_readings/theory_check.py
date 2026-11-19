"""Replay the marked equation-space theorem on three specified starting graphs."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from math import comb
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "theory_check.json"
PREDECESSOR = "EXTEND-ROUND-20261119-001A"
sys.path.insert(0, str(ROOT / "experiments" / PREDECESSOR / (PREDECESSOR + "-E001_extend")))
import extend as law


def start_graph(parts):
    """Complete multipartite graph, with two different loose names at each site."""
    stars = [set() for _ in parts]
    label = 0
    for i, j in combinations(range(len(parts)), 2):
        if parts[i] != parts[j]:
            stars[i].add(label)
            stars[j].add(label)
            label += 1
    for star in stars:
        star.update((label, label + 1))
        label += 2
    return list(map(frozenset, stars))


def minima(stars):
    pairs, triples = {}, {}
    cuts = sorted(law.L.bonds(stars), key=len)
    for cut in cuts:
        k = len(cut)
        for pair in combinations(cut, 2):
            pairs.setdefault(pair, k)
        for triple in combinations(cut, 3):
            triples.setdefault(triple, k)
    return pairs, triples, cuts


def decode(labels, pairs, triples):
    answer = {}
    for (a, b), k in pairs.items():
        names = {a, b}
        for z in labels:
            if z != a and z != b and triples.get(tuple(sorted((a, b, z)))) == k:
                names.add(z)
        if len(names) == k:
            answer[a, b] = frozenset(names)
    return answer


def rank(stars):
    return law.L.rank([sum(1 << x for x in star) for star in stars])


def check(parts):
    n = len(parts)
    start = start_graph(parts)
    current = law.grow1(start)
    owners = law.L.owners(current)
    live, loose, _ = law.reading(current)
    assert len(current) == 2 * n + 1 and len(live) == n + 1
    hub, = (j for j in live if len(current[j] - loose[j]) == n)
    assert len(loose[hub]) == n
    a, b = {}, {}
    for j in live:
        parents = current[j] - loose[j]
        if j != hub:
            assert len(parents) == 1 and len(loose[j]) == 2
        for x in parents:
            i, = (u for u in owners[x] if u < n)
            (a if j == hub else b)[i] = x

    pairs, triples, bonds = minima(current)
    forced = decode(sorted(owners), pairs, triples)
    directed = 0
    q, = {len(s) for s in start}
    for i, j in combinations(range(n), 2):
        for x in start[i] & start[j]:
            for u in (i, j):
                anchor = tuple(sorted((x, a[u])))
                assert pairs[anchor] == q and forced[anchor] == start[u]
                directed += 1
    least_two_b = min(pairs[tuple(sorted((b[i], b[j])))] for i, j in combinations(range(n), 2))
    assert least_two_b >= q
    live_stars = [current[j] for j in live]
    known = rank(live_stars + [cut for cut in bonds if len(cut) <= 3])
    reconstructed = rank(live_stars + list(set(forced.values())))
    assert known == n + 1 and reconstructed == rank(current) == 2 * n + 1
    return {
        "start_junctions": n, "start_ordinary_degree": q - 2,
        "reached_junctions": len(current), "width": len(owners),
        "reached_live_arities": sorted(len(star) for star in live_stars),
        "reached_exhausted_arity": q, "enumerated_bonds": len(bonds),
        "finite_pair_entries": len(pairs), "finite_triple_entries": len(triples),
        "forced_endpoint_stars": n, "specified_anchors_verified": directed,
        "least_bond_through_two_distinct_unary_inputs": least_two_b,
        "rank_live_and_bonds_through_size_three": known,
        "rank_live_and_forced_minimizers": reconstructed,
        "rank_of_physical_equations": rank(current),
    }


def sparse_shore(marked, n):
    """Name (i,j,h) is the incidence of middle vertex (i,j) with i, j, or 'hub'."""
    grouped = defaultdict(set)
    for i, j, end in marked:
        grouped[i, j].add(end)
    if len(grouped) == 1 and len(marked) == 3:
        return set(), set(grouped)

    kept, forbidden = set(), set()
    for mid, ends in grouped.items():
        if len(ends) != 2:
            continue
        if "hub" in ends:
            forbidden.update(ends - {"hub"})
            kept.update(set(mid) - ends)
        else:
            kept.update(ends)
    for mid in grouped:
        if not kept.intersection(mid):
            kept.add(min(set(mid) - forbidden))
    assert not kept & forbidden and len(kept) <= len(marked)
    positive_mids = set()
    for mid, ends in grouped.items():
        if "hub" in ends or not kept.intersection(ends):
            positive_mids.add(mid)
    used = set().union(*grouped)
    helper = next(i for i in range(n) if i not in used)
    positive_mids.update(tuple(sorted((i, helper))) for i in kept)
    return kept | {helper}, positive_mids


def connected_mask(mask, adjacency):
    seen = pending = mask & -mask
    while pending:
        site = pending & -pending
        pending ^= site
        added = adjacency[site.bit_length() - 1] & mask & ~seen
        seen |= added
        pending |= added
    return seen == mask


def static_obstruction():
    n = 21
    analytic_upper_bound = 4 * (n - 1)
    mids = list(combinations(range(n), 2))
    mid_id = {pair: n + j for j, pair in enumerate(mids)}
    hub = n + len(mids)
    adjacency = [0] * (hub + 1)
    incident = [0] * (hub + 1)
    names = {}
    for mid, vertex in mid_id.items():
        for end in (*mid, "hub"):
            u = hub if end == "hub" else end
            label = len(names)
            names[(*mid, end)] = label
            adjacency[u] |= 1 << vertex
            adjacency[vertex] |= 1 << u
            incident[u] |= 1 << label
            incident[vertex] |= 1 << label
    universe = (1 << (hub + 1)) - 1
    assert all(connected_mask(universe ^ (1 << j), adjacency) for j in range(hub + 1))
    # Three marks involve at most six distinct index labels. Every full pattern
    # is an injective relabeling of one of the following, in the unsplit graph.
    sample = [name for name in names if max(name[:2]) < 6]
    counts, largest = {}, {}
    for size in range(1, 4):
        histogram = Counter()
        for marked in combinations(sample, size):
            selected_indices, selected_mids = sparse_shore(marked, n)
            selected = selected_indices | {mid_id[key] for key in selected_mids}
            side = sum(1 << j for j in selected)
            assert connected_mask(side, adjacency) and connected_mask(universe ^ side, adjacency)
            cut = 0
            for j in selected:
                cut ^= incident[j]
            assert all(cut >> names[name] & 1 for name in marked)
            assert len(selected_indices) <= 4 and len(selected_mids) <= 6
            assert cut.bit_count() <= analytic_upper_bound
            histogram[cut.bit_count()] += 1
        counts[str(size)] = sum(histogram.values())
        largest[str(size)] = max(histogram)
    assert largest["3"] == analytic_upper_bound

    # For each i these five paths enter through a different dark middle vertex
    # and leave through a different light one. Verify every used named edge once.
    dark, light, used_edges = set(), set(), set()
    for i in range(n):
        for shift in range(1, 6):
            p = tuple(sorted((i, (i + shift) % n)))
            q = tuple(sorted((i, (i + shift + 5) % n)))
            new = {names[(*p, "hub")], names[(*p, i)], names[(*q, i)], names[(*q, "hub")]}
            assert len(new) == 4 and not new & used_edges
            used_edges.update(new)
            dark.add(p)
            light.add(q)
    assert dark | light == set(mids) and not dark & light
    assert len(used_edges) // 4 == 105
    sigma = {2: 3, 3: 2}
    moved_dark = {tuple(sorted(sigma.get(i, i) for i in mid)) for mid in dark}
    assert moved_dark != dark and moved_dark != light
    assert (0, 1) in dark & moved_dark and (2, 8) in light and (3, 8) in dark

    split_hub = hub + 1
    split_adjacency = adjacency.copy() + [0]
    for mid in light:
        v = mid_id[mid]
        split_adjacency[hub] ^= 1 << v
        split_adjacency[v] ^= 1 << hub
        split_adjacency[split_hub] |= 1 << v
        split_adjacency[v] |= 1 << split_hub
    full = (1 << (split_hub + 1)) - 1
    assert all(connected_mask(full ^ (1 << j), split_adjacency) for j in range(split_hub + 1))
    assert connected_mask(universe ^ (1 << hub), adjacency)
    return {
        "ordinary_indices": n, "middle_vertices": len(mids), "distinctions": len(names),
        "unsplit_vertices": len(adjacency), "split_vertices": len(split_adjacency),
        "unsplit_equation_rank": len(adjacency) - 1, "split_equation_rank": len(split_adjacency) - 1,
        "connected_after_any_vertex_deletion_in_both_graphs": True,
        "literal_mark_sets_checked_on_six_indices": counts,
        "largest_constructed_bond_on_checked_sets": largest,
        "analytic_all_marks_upper_bound": analytic_upper_bound, "edge_disjoint_paths_between_split_hubs": 105,
        "pair_entries_covered_by_proof": comb(len(names), 2),
        "triple_entries_covered_by_proof": comb(len(names), 3),
        "index_transposition": [2, 3], "chosen_fixed_edge": [0, 1, 0],
        "dark_spokes_changed_by_transposition": len(dark ^ moved_dark),
        "nontrivial_pair_flips_in_both_simple_graphs": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    cases = {
        "complete_on_three": [0, 1, 2],
        "complete_on_six": [0, 1, 2, 3, 4, 5],
        "complete_tripartite_two_each": [0, 0, 1, 1, 2, 2],
    }
    result = {name: check(parts) for name, parts in cases.items()}
    result["split_hub_obstruction"] = static_obstruction()
    content = json.dumps(result, indent=2) + "\n"
    if args.check:
        if OUT.read_text() != content:
            raise SystemExit("Saved theorem controls differ from the literal replay.")
    else:
        OUT.write_text(content)
    print("The three reached controls and every static marking pattern pass.")


if __name__ == "__main__":
    main()
