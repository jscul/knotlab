"""Exact holder-step and parity controls on constructed wide-family starts."""

import argparse
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from itertools import combinations
import json
from pathlib import Path

import growth


@dataclass(frozen=True)
class Case:
    name: str
    width: int
    rounds: int
    attachments: tuple[tuple[int, int], ...]
    repeated_meetings: bool = False
    literal_rounds: tuple[int, ...] = ()
    odd_control: bool = False


CASES = (
    Case("small", 2, 2, ((0, 2), (2, 2)), literal_rounds=(0, 1)),
    Case("wide_four", 4, 3, ((0, 2), (4, 2))),
    Case("wide_eight", 8, 6, ((0, 2), (8, 2))),
    Case("wide_sixteen", 16, 12, ((0, 2), (16, 2))),
    Case("wide_twenty_four", 24, 18, ((0, 2), (24, 2))),
    Case("deep_birth_routes", 16, 15, ((0, 2), (16, 2)), repeated_meetings=True),
    Case("eight_families", 16, 12, tuple((i, 2) for i in (0, 2, 4, 8, 12, 14, 16))),
    Case("loose_multiplicity", 8, 6, ((0, 4), (8, 3)), odd_control=True),
)


def make_start(case):
    """One B family on b0...b_m, with a separate family per attached knot.

    Each p_i shares with b_i and b_(i+1) and has no loose distinction. Its
    third distinction joins p_(i^1), or repeats its meeting with b_i in the
    repeated-meeting control. Every attachment is a separate live knot.
    """
    width = case.width
    assert width >= 2 and width % 2 == 0
    supports = [[] for _ in range(2 * width + 1 + len(case.attachments))]
    serial = 0

    def add(*knots):
        nonlocal serial
        for knot in knots:
            supports[knot].append(serial)
        serial += 1

    for i in range(width):
        add(i, width + 1 + i)
        add(width + 1 + i, i + 1)
    if case.repeated_meetings:
        for i in range(width):
            add(width + 1 + i, i)
    else:
        for i in range(0, width, 2):
            add(width + 1 + i, width + 2 + i)
    for i in range(width + 1):
        for _ in range(1 if i in (0, width) else 2):
            add(i)
    for index, (attachment, openings) in enumerate(case.attachments, 2 * width + 1):
        add(attachment, index)
        for _ in range(openings):
            add(index)
    families = (tuple(range(width + 1)),) + tuple(
        (i,) for i in range(2 * width + 1, len(supports))
    )
    return tuple(tuple(support) for support in supports), families


def incidences(supports):
    holders = defaultdict(list)
    for knot, support in enumerate(supports):
        assert len(support) == len(set(support))
        for distinction in support:
            holders[distinction].append(knot)
    shared = [[] for _ in supports]
    loose = [[] for _ in supports]
    for distinction, knots in sorted(holders.items()):
        if len(knots) == 1:
            loose[knots[0]].append(distinction)
        else:
            a, b = knots
            shared[a].append((b, distinction))
            shared[b].append((a, distinction))
    return holders, shared, loose


def walk(adjacency, starts, excluded=frozenset()):
    distance = {start: 0 for start in starts}
    previous = {}
    queue = deque(distance)
    while queue:
        at = queue.popleft()
        for nxt, distinction in adjacency[at]:
            if nxt not in distance and nxt not in excluded:
                distance[nxt] = distance[at] + 1
                previous[nxt] = at, distinction
                queue.append(nxt)
    return distance, previous


def route(previous, end):
    knots = [end]
    distinctions = []
    while end in previous:
        end, distinction = previous[end]
        knots.append(end)
        distinctions.append(distinction)
    return {"knots": list(reversed(knots)), "distinctions": list(reversed(distinctions))}


def add_bookkeeping(shared, loose, family_by_knot, family_count):
    n = len(shared)
    augmented = [row[:] for row in shared] + [[] for _ in range(family_count)]
    for knot, distinctions in enumerate(loose):
        if distinctions:
            extra = n + family_by_knot[knot]
            for distinction in distinctions:
                augmented[knot].append((extra, distinction))
                augmented[extra].append((knot, distinction))
    return augmented


def verify_start(shared, loose, supports, repeated_meetings):
    n = len(shared)
    assert all(3 <= len(support) <= 5 for support in supports)
    assert len(walk(shared, [0])[0]) == n
    multiplicities = Counter(
        (a, b) for a, meetings in enumerate(shared) for b, _ in meetings if a < b
    )
    assert max(multiplicities.values()) == (2 if repeated_meetings else 1)
    exterior = add_bookkeeping(shared, loose, dict.fromkeys(range(n), 0), 1)
    for knot, meetings in enumerate(shared):
        reachable, _ = walk(exterior, [n], {knot})
        # Each even word on this knot extends by pairing its selected
        # distinctions' other holders via routes avoiding this knot.
        assert all(neighbor in reachable for neighbor, _ in meetings)


def summary_of_support(support, supports, families_by_knot, loose):
    used = set(support)
    assert len(used) == len(support)
    assert all(len(used.intersection(knot_support)) % 2 == 0 for knot_support in supports)
    family_parity = set()
    loose_counts = {}
    for knot, distinctions in enumerate(loose):
        degree = len(used.intersection(distinctions))
        if degree:
            loose_counts[knot] = degree
            if degree % 2:
                family_parity.symmetric_difference_update({families_by_knot[knot]})
    return family_parity, loose_counts


def weighted_chain(direct):
    costs = [row[:] for row in direct]
    successors = [[b for b in range(len(costs))] for _ in costs]
    for mid in range(len(costs)):
        for a, row in enumerate(costs):
            for b in range(len(costs)):
                cost = row[mid] + costs[mid][b]
                if cost < row[b]:
                    row[b] = cost
                    successors[a][b] = successors[a][mid]
    return costs, successors


def follow_chain(successors, a, b):
    chain = [a]
    while a != b:
        a = successors[a][b]
        chain.append(a)
    return chain


def threshold_partition(costs, scale):
    unseen = set(range(len(costs)))
    partition = []
    while unseen:
        seed = min(unseen)
        cluster = {seed}
        frontier = [seed]
        unseen.remove(seed)
        for at in frontier:
            neighbors = {i for i in unseen if costs[at][i] <= scale}
            cluster.update(neighbors)
            frontier.extend(sorted(neighbors))
            unseen.difference_update(neighbors)
        partition.append(tuple(sorted(cluster)))
    return tuple(partition)


def literal_minima(supports, loose, family_by_knot, family_count):
    """Enumerate every allowed binary change via row reduction and Gray order."""
    n = max(max(support) for support in supports) + 1
    pivot_rows = {}
    for support in supports:
        row = sum(1 << distinction for distinction in support)
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivot_rows:
                pivot_rows[pivot] = row
                break
            row ^= pivot_rows[pivot]
    basis = []
    for distinction in range(n):
        if distinction not in pivot_rows:
            change = 1 << distinction
            for pivot, row in sorted(pivot_rows.items()):
                if (row & change).bit_count() % 2:
                    change ^= 1 << pivot
            basis.append(change)
    family_masks = [0] * family_count
    for knot, distinctions in enumerate(loose):
        if distinctions:
            family_masks[family_by_knot[knot]] |= sum(1 << i for i in distinctions)
    minima = {}
    current = 0
    cells = 1 << len(basis)
    for index in range(cells):
        if index:
            current ^= basis[(index & -index).bit_length() - 1]
        syndrome = sum(1 << i for i, mask in enumerate(family_masks) if (current & mask).bit_count() % 2)
        minima[syndrome] = min(minima.get(syndrome, n + 1), current.bit_count())
    return minima, cells


def returning_routes(support, holders, shared, loose_counts, family_by_knot):
    """Pair odd knots in the selected shared distinctions and count residue."""
    odd = {knot for knot, count in loose_counts.items() if count % 2}
    unused = {i for i in support if len(holders[i]) == 2}
    segments = []

    def take(at, destinations):
        knots = [at]
        distinctions = []
        while not distinctions or at not in destinations:
            nxt, distinction = next((b, i) for b, i in shared[at] if i in unused)
            unused.remove(distinction)
            distinctions.append(distinction)
            knots.append(nxt)
            at = nxt
        return {"knots": knots, "distinctions": distinctions}

    while odd:
        source = min(odd)
        odd.remove(source)
        segment = take(source, odd)
        target = segment["knots"][-1]
        odd.remove(target)
        segment["families"] = [family_by_knot[source], family_by_knot[target]]
        segments.append(segment)
    residue = []
    while unused:
        source = holders[min(unused)][0]
        residue.append(take(source, {source}))
    return segments, residue


def odd_witness(supports, holders, shared, loose, family_by_knot, start_width, shortest):
    """Add independent parity changes exercising multiplicity and return routes."""
    start_a = 2 * start_width + 1
    selected = set(shortest["distinctions"])
    a_children = [k for k, _ in shared[start_a] if len(loose[k]) == 3]
    chosen, = [k for k in a_children if selected.intersection(loose[k])]
    assert len(a_children) == 4
    selected.update(set(loose[chosen]) - selected)
    returned = [k for k in a_children if k != chosen]
    for knot in returned[:2]:
        inward, = [i for neighbor, i in shared[knot] if neighbor == start_a]
        selected.update((inward, loose[knot][0]))
    selected.update(loose[returned[-1]][:2])
    cycle_knots = (1, start_width + 1, start_width + 2)
    for a, b in combinations(cycle_knots, 2):
        distinction, = [i for neighbor, i in shared[a] if neighbor == b]
        assert distinction not in selected
        selected.add(distinction)
    support = sorted(selected)
    parity, loose_counts = summary_of_support(support, supports, family_by_knot, loose)
    segments, residue = returning_routes(support, holders, shared, loose_counts, family_by_knot)
    assert parity == {1, 2}
    assert loose_counts[chosen] == 3 and loose_counts[returned[-1]] == 2
    assert any(a == b for a, b in (r["families"] for r in segments))
    assert sum(len(r["distinctions"]) for r in residue) == 3
    shared_accounted = [i for trail in segments + residue for i in trail["distinctions"]]
    assert sorted(shared_accounted) == [i for i in support if len(holders[i]) == 2]
    return {
        "selected_distinctions": support,
        "loose_counts_by_knot": loose_counts,
        "odd_families": sorted(parity),
        "paired_knot_routes": segments,
        "closed_residue": residue,
    }


def lemma_audit(shared, start_knots, start_distances, ages, deep_target=None):
    counts = Counter()
    start = set(range(start_knots))
    birth_walks = {}
    for a in range(start_knots):
        reached, _ = walk(shared, [a])
        for b in range(a + 1, start_knots):
            counts["start_pairs"] += 1
            if reached[b] != start_distances[a][b]:
                raise AssertionError((a, b, reached[b], start_distances[a][b]))
        if not any(b not in start for b, _ in shared[a]):
            continue
        # Exclude every other start knot until the final step. A witness
        # here contains births and cannot use the baseline route as padding.
        born_distances, born_previous = walk(shared, [a], start - {a})
        birth_walks[a] = (born_distances, born_previous)
        excursions = {}
        for at, distance in born_distances.items():
            if at not in start:
                for b, _ in shared[at]:
                    if a < b < start_knots:
                        excursions[b] = min(excursions.get(b, len(shared)), distance + 1)
        for b, distance in excursions.items():
            counts["start_pairs_with_birth_excursion"] += 1
            assert distance >= start_distances[a][b]
            if distance == start_distances[a][b]:
                counts["birth_excursion_ties"] += 1

    deep_tie = None
    if deep_target:
        max_age = len(ages) - 1
        to_left, left_previous = birth_walks[0]
        to_right, right_previous = birth_walks[deep_target]
        for born in ages[max_age]:
            if born not in to_left or born not in to_right:
                continue
            if to_left[born] + to_right[born] != start_distances[0][deep_target]:
                continue
            left = route(left_previous, born)
            right = route(right_previous, born)
            knots = left["knots"] + list(reversed(right["knots"][:-1]))
            assert len(knots) == len(set(knots))
            deep_tie = {
                "highest_round": max_age,
                "knots": knots,
                "distinctions": left["distinctions"] + list(reversed(right["distinctions"])),
            }
            break
        assert deep_tie is not None
        counts["specified_highest_birth_ties"] += 1
    return dict(sorted(counts.items())), deep_tie


def compare_stage(case, t, supports, family_by_knot, families, start_distances, family_start, ages):
    holders, shared, loose = incidences(supports)
    m = len(families)
    n = len(supports)
    live = tuple(
        tuple(k for k, names in enumerate(loose) if names and family_by_knot[k] == f)
        for f in range(m)
    )
    assert all(live)
    if t:
        assert {k for group in live for k in group} == set(ages[t])
    if t <= case.width:
        assert len(live[0]) == case.width + 1 - t
    start_knots = len(start_distances)
    audit, deep_tie = lemma_audit(
        shared, start_knots, start_distances, ages, t if case.repeated_meetings and t else None
    )
    augmented = add_bookkeeping(shared, loose, family_by_knot, m)
    direct = [[distance + 2 * t + 2 if a != b else 0 for b, distance in enumerate(row)]
              for a, row in enumerate(family_start)]
    predicted, successors = weighted_chain(direct)
    pair = [[0] * m for _ in range(m)]
    strict_witnesses = []
    counts = Counter(audit)
    for a in range(m):
        distances, previous = walk(augmented, [n + a])
        raw_shared, _ = walk(shared, live[a])
        for b in range(a + 1, m):
            raw = distances[n + b]
            pair[a][b] = pair[b][a] = raw
            assert min(raw_shared[knot] for knot in live[b]) + 2 == direct[a][b]
            assert raw == predicted[a][b]
            counts["pairs"] += 1
            if raw < direct[a][b]:
                counts["strict_pairs"] += 1
                change = route(previous, n + b)
                parity, _ = summary_of_support(change["distinctions"], supports, family_by_knot, loose)
                assert parity == {a, b}
                strict_witnesses.append({
                    "families": [a, b],
                    "direct_cost": direct[a][b],
                    "pair_cost": raw,
                    "predicted_chain": follow_chain(successors, a, b),
                    "actual_bookkeeping_visits": [k - n for k in change["knots"] if k >= n],
                    "actual_change": change,
                })

    literal = None
    if t in case.literal_rounds:
        literal, counts["literal_allowed_changes"] = literal_minima(supports, loose, family_by_knot, m)
        assert len(literal) == 1 << (m - 1)
        for a, b in combinations(range(m), 2):
            assert literal[(1 << a) | (1 << b)] == pair[a][b]

    set_costs = []
    for mask in range(1, 1 << (m - 1)):
        chosen = [f for f in range(m) if mask & (1 << f)]
        complement = [f for f in range(m) if not mask & (1 << f)]
        crossing, _ = walk(shared, [k for f in chosen for k in live[f]])
        raw = min(crossing[k] for f in complement for k in live[f]) + 2
        assert raw == min(pair[a][b] for a in chosen for b in complement)
        assert raw == min(direct[a][b] for a in chosen for b in complement)
        if literal is not None:
            assert raw == min(cost for syndrome, cost in literal.items()
                              if (syndrome & mask).bit_count() % 2)
        set_costs.append(raw)
        counts["family_splits"] += 1

    scales = []
    for scale in range(max(max(row) for row in direct) + 1):
        clusters = threshold_partition(direct, scale)
        actual_clusters = threshold_partition(pair, scale)
        cluster_masks = [sum(1 << f for f in cluster) for cluster in clusters]
        for mask, cost in enumerate(set_costs, 1):
            separates_a_cluster = any(0 < (mask & cluster) < cluster for cluster in cluster_masks)
            assert (cost <= scale) == separates_a_cluster
        frozen_splits = sum(cost > scale for cost in set_costs)
        assert actual_clusters == clusters
        assert frozen_splits == (1 << (len(clusters) - 1)) - 1
        if not scales or scales[-1][1] != len(clusters) - 1:
            scales.append([scale, len(clusters) - 1])
        counts["thresholds"] += 1

    odd = None
    if t == 1 and case.odd_control:
        _, paths = walk(augmented, [n + 1])
        odd = odd_witness(supports, holders, shared, loose, family_by_knot, case.width, route(paths, n + 2))

    return {
        "round": t,
        "knots": n,
        "distinctions": len(holders),
        "live_knots_by_family": [len(group) for group in live],
        "set_cost_histogram": Counter(set_costs),
        "class_fact_dimension_changes": scales,
        "counts": dict(sorted(counts.items())),
    }, strict_witnesses, deep_tie, odd


def check_case(case, pilot):
    supports, families = make_start(case)
    actual_families = growth.families(supports)
    assert {frozenset(group) for group in families} == {frozenset(group) for group in actual_families}
    _, shared, loose = incidences(supports)
    verify_start(shared, loose, supports, case.repeated_meetings)
    start_distances = [walk(shared, [knot])[0] for knot in range(len(supports))]
    family_start = [
        [min(start_distances[a][b] for a in left for b in right) for right in families]
        for left in families
    ]
    family_by_knot = {knot: f for f, group in enumerate(families) for knot in group}
    ages = [tuple(range(len(supports)))]
    results = []
    first_strict = last_strict = last_deep_tie = odd = None
    counts = Counter()
    through = min(case.rounds, 1) if pilot and case.name != "small" else case.rounds
    for t, stage, status, births in growth.stages(supports, rounds=through, cap=4000):
        assert status == "stage", (case.name, t, status)
        if t:
            for birth in births:
                parent_labels = {family_by_knot[k] for k in birth.parents}
                assert len(parent_labels) == 1
                family_by_knot[birth.knot], = parent_labels
            ages.append(tuple(birth.knot for birth in births))
        row, strict, deep_tie, odd_at_stage = compare_stage(
            case, t, stage, family_by_knot, families, start_distances, family_start, ages
        )
        results.append(row)
        counts.update(row["counts"])
        if strict:
            most_separated = max(strict, key=lambda x: x["direct_cost"] - x["pair_cost"])
            witness = {"round": t, **most_separated}
            if first_strict is None:
                first_strict = witness
            last_strict = {**witness, "knot_supports": stage}
        if deep_tie:
            _, previous = walk(shared, [0])
            last_deep_tie = {
                **deep_tie,
                "start_route": route(previous, t),
                "knot_supports_on_route": {k: stage[k] for k in deep_tie["knots"]},
            }
        if odd_at_stage:
            odd = {**odd_at_stage, "round": t, "knot_supports": stage}
    assert len(results) == through + 1
    return {
        "name": case.name,
        "width": case.width,
        "attachment_knots_and_loose_counts": case.attachments,
        "repeated_meetings": case.repeated_meetings,
        "start_supports": supports,
        "start_families": families,
        "family_start_holder_steps": family_start,
        "stages": results,
        "counts": dict(sorted(counts.items())),
        "first_strict_pair": first_strict,
        "latest_strict_pair": last_strict,
        "latest_highest_birth_tie": last_deep_tie,
        "odd_knot_control": odd,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = [check_case(case, args.pilot) for case in CASES]
    by_round = defaultdict(Counter)
    for case in cases:
        for stage in case["stages"]:
            by_round[stage["round"]].update(stage["counts"])
    rendered = json.dumps({
        "pilot": args.pilot,
        "weighting": "One count per stated constructed start and reached round, with no population sampling.",
        "families": "Family 0 contains the b knots. Separate families follow attachment order.",
        "family_splits": "One count per nontrivial split up to complement.",
        "thresholds": "All integer scales from zero through the largest direct cost on each stage.",
        "lemma_2": "All distinct pairs of start knots, comparing raw holder steps with loose distinctions removed.",
        "birth_excursions": "Holder-step routes with at least one birth and no start knot in the interior.",
        "counts_by_round": {t: dict(sorted(counts.items())) for t, counts in sorted(by_round.items())},
        "cases": cases,
    }, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
