"""Rebuild the closed parity presentations from the declared starts and growth rule."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from heapq import heapify, heappop, heappush
from io import StringIO
from itertools import combinations, product
import json
from pathlib import Path
from random import Random

import networkx as nx


ROOT = Path(__file__).resolve().parents[3]
ORIGINAL = ROOT / (
    "artifacts/REVIEW-LEADS-20261123-001A/"
    "REVIEW-LEADS-20261123-001A-E001_operator_test"
)
SOURCES = ROOT / (
    "artifacts/HEAVY-GROWTH-20261119-001/"
    "HEAVY-GROWTH-20261119-001-E001_checks/sources_audit.json"
)
DRAW_SEED = 2026112301


def tree_from_word(word):
    degree = [1] * (len(word) + 2)
    for knot in word:
        degree[knot] += 1
    leaves = [knot for knot, count in enumerate(degree) if count == 1]
    heapify(leaves)
    meetings = []
    for knot in word:
        meetings.append(tuple(sorted((heappop(leaves), knot))))
        degree[knot] -= 1
        if degree[knot] == 1:
            heappush(leaves, knot)
    meetings.append(tuple(sorted(leaves)))
    return sorted(meetings)


def make_holdings(meetings, loose):
    holdings = [[] for _ in loose]
    for distinction, (left, right) in enumerate(meetings):
        holdings[left].append(distinction)
        holdings[right].append(distinction)
    next_distinction = len(meetings)
    for support, count in zip(holdings, loose, strict=True):
        support.extend(range(next_distinction, next_distinction + count))
        next_distinction += count
    return list(map(tuple, holdings))


def fresh_draws():
    random = Random(DRAW_SEED)
    for extras, draw in product(range(4), range(256)):
        knots = random.randint(4, 8)
        word = [random.randrange(knots) for _ in range(knots - 2)]
        spare = [int(random.randrange(4) == 0) for _ in range(knots)]
        tree = tree_from_word(word)
        unused = sorted(set(combinations(range(knots), 2)) - set(tree))
        added = sorted(random.sample(unused, extras))
        meetings = sorted(tree + added)
        degrees = Counter(knot for meeting in meetings for knot in meeting)
        loose = [max(0, 3 - degrees[knot]) + spare[knot] for knot in range(knots)]
        yield {
            "arm": extras, "draw": draw, "prufer": word, "spare": spare,
            "extra_meetings": added, "meetings": meetings, "loose": loose,
        }, make_holdings(meetings, loose)


def recorded_sources():
    """Read the four named constructions and the three archived founder rosters."""
    seven = [(0, 1), (0, 4), (1, 4), (2, 4), (2, 6),
             (3, 4), (3, 5), (5, 6), (0, 1)]
    nine = [(0, 2), (0, 3), (0, 5), (1, 2), (2, 7),
            (3, 8), (4, 5), (4, 8), (5, 6), (6, 7)]
    five = [(0, 1)] * 2 + [(1, 2), (2, 3), (3, 4)] + [(4, 0)] * 3
    directed_meetings = [
        ("v", "r1"), ("r1", "r2"), ("r2", "r3"), ("r3", "v"),
        ("v", "s"), ("t", "v"), ("s", "b0"), ("t", "b0"),
        ("s", "b1"), ("b1", "t"), ("t", "b2"), ("b2", "s"),
    ]
    two_clock_meetings = []
    two_clock_loose = Counter()
    for index, (left, right) in enumerate(directed_meetings):
        witness = f"w{index}"
        two_clock_meetings.extend(((left, witness), (right, witness), (right, witness)))
        two_clock_loose.update((left, right))
    names = sorted({knot for pair in two_clock_meetings for knot in pair})
    indices = {name: index for index, name in enumerate(names)}
    starts = {
        "seven_knot": make_holdings(seven, [3, 0, 3, 3, 3, 2, 2]),
        "nine_knot_drawn": make_holdings(nine, [5, 2, 4, 3, 3, 4, 3, 3, 2]),
        "knots21_two_clocks": make_holdings(
            [(indices[left], indices[right]) for left, right in two_clock_meetings],
            [two_clock_loose[name] for name in names],
        ),
        "five_founder_clock": make_holdings(five, [2] * 5),
    }
    archived = json.loads(SOURCES.read_text())["named_archive_starts"]
    for name in ("start-00", "start-04", "start-13"):
        record = archived[name]
        meetings = record["meetings"]
        degrees = Counter(knot for meeting in meetings for knot in meeting)
        loose = [size - degrees[knot] for knot, size in enumerate(record["sizes"])]
        starts[f"archive_{name}"] = make_holdings(meetings, loose)
    return starts


def holder_index(holdings):
    holders = defaultdict(list)
    for knot, support in enumerate(holdings):
        for distinction in support:
            holders[distinction].append(knot)
    assert all(1 <= len(group) <= 2 and len(set(group)) == len(group)
               for group in holders.values())
    return dict(holders)


def witnessed_end(holdings, holders):
    loose_by_holder = defaultdict(list)
    neighbours = [set() for _ in holdings]
    for distinction, knots in holders.items():
        if len(knots) == 1:
            loose_by_holder[knots[0]].append(distinction)
        else:
            left, right = knots
            neighbours[left].add(right)
            neighbours[right].add(left)
    live = sorted(loose_by_holder)
    local_index = {knot: index for index, knot in enumerate(live)}
    witnessed = [tuple(local_index[knot] for knot in others if knot in local_index)
                 for others in neighbours]
    loose = [sorted(loose_by_holder[knot]) for knot in live]
    return live, loose, witnessed


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def as_mask(group):
    mask = 0
    for knot in group:
        mask |= 1 << knot
    return mask


def pairwise_meetings(size, witnessed):
    adjacency = [0] * size
    witness_masks = {as_mask(group) for group in witnessed if len(group) >= 2}
    large_witnesses = [[] for _ in range(size)]
    for witness in witness_masks:
        for knot in members(witness):
            adjacency[knot] |= witness ^ (1 << knot)
            if witness.bit_count() >= 3:
                large_witnesses[knot].append(witness)
    return adjacency, large_witnesses


def unheld_groups(adjacency, witnesses):
    """A maximal complete group of size at least three, with no common witness."""
    stack = [(0, (1 << len(adjacency)) - 1, 0)]
    while stack:
        included, available, excluded = stack.pop()
        upper = included | available
        if upper.bit_count() < 3:
            continue
        first = (upper & -upper).bit_length() - 1
        if any(upper & witness == upper for witness in witnesses[first]):
            continue
        if not available:
            if not excluded:
                yield included
            continue
        pivot = max(members(available | excluded),
                    key=lambda knot: (adjacency[knot] & available).bit_count())
        for knot in members(available & ~adjacency[pivot]):
            bit = 1 << knot
            stack.append((included | bit, available & adjacency[knot],
                          excluded & adjacency[knot]))
            available ^= bit
            excluded |= bit


class PlannedOverCap(Exception):
    """The number of group births already exceeds the remaining capacity."""


def group_choices(size, witnessed, cap=None):
    adjacency, witnesses = pairwise_meetings(size, witnessed)
    uncovered = adjacency.copy()
    larger_groups = []
    for group in unheld_groups(adjacency, witnesses):
        if cap is not None and len(larger_groups) >= cap:
            raise PlannedOverCap
        knots = tuple(members(group))
        larger_groups.append(knots)
        for knot in knots:
            uncovered[knot] &= ~group
    pair_count = sum(mask.bit_count() for mask in uncovered) // 2
    if cap is not None and len(larger_groups) + pair_count > cap:
        raise PlannedOverCap
    return sorted(larger_groups), uncovered


def group_demands(size, witnessed):
    larger_groups, uncovered = group_choices(size, witnessed)
    demand = Counter(knot for group in larger_groups for knot in group)
    return [demand[knot] + uncovered[knot].bit_count() for knot in range(size)]


def birth_plan(loose, witnessed, capacity):
    try:
        larger_groups, uncovered = group_choices(len(loose), witnessed, cap=capacity)
    except PlannedOverCap:
        return "cap", []
    pairs = [(left, right) for left, mask in enumerate(uncovered)
             for right in members(mask) if left < right]
    parents = larger_groups + pairs
    required = Counter(knot for group in parents for knot in group)
    surplus = [len(available) - required[knot] for knot, available in enumerate(loose)]
    if any(count < 0 for count in surplus):
        return "stall", []
    if len(parents) + sum(surplus) > capacity:
        return "cap", []
    parents.extend((knot,) for knot, count in enumerate(surplus) for _ in range(count))
    if len(parents) == 1:
        return "extend", [(parents[0], 0)]
    rosters = [[] for _ in loose]
    for child, group in enumerate(parents):
        for parent in group:
            rosters[parent].append(child)
    demand = group_demands(len(parents), rosters)
    return "extend", [(group, max(need, 3 - len(group), 1))
                      for group, need in zip(parents, demand, strict=True)]


def history(initial, horizon, cap):
    holdings = initial.copy()
    stages = []
    cohort = []
    for step in range(horizon + 1):
        holders = holder_index(holdings)
        if step == 0:
            meeting_graph = nx.Graph()
            meeting_graph.add_nodes_from(range(len(holdings)))
            meeting_graph.add_edges_from(knots for knots in holders.values() if len(knots) == 2)
            assert nx.is_connected(meeting_graph)
        loose_count = sum(len(knots) == 1 for knots in holders.values())
        stages.append({
            "t": step, "knots": len(holdings), "distinctions": len(holders),
            "loose": loose_count, "links": sum(map(len, holdings)),
            "births": len(cohort),
            "one_parent_births": sum(len(birth["parents"]) == 1 for birth in cohort),
        })
        if loose_count == 0:
            return "closed", stages, holdings
        if step == horizon:
            return "horizon", stages, holdings
        live, loose, witnessed = witnessed_end(holdings, holders)
        outcome, plan = birth_plan(loose, witnessed, cap - len(holdings))
        if outcome != "extend":
            return outcome, stages, holdings
        cohort = []
        next_distinction = len(holders)
        for parents, fresh in plan:
            inputs = tuple(loose[knot].pop() for knot in parents)
            minted = tuple(range(next_distinction, next_distinction + fresh))
            next_distinction += fresh
            cohort.append({"parents": [live[knot] for knot in parents]})
            holdings.append(tuple(sorted(inputs + minted)))


def binary_rank(rows):
    basis = {}
    for row in rows:
        while row:
            high = row.bit_length()
            if high not in basis:
                basis[high] = row
                break
            row ^= basis[high]
    return len(basis)


def check_rotation(meeting_graph, rotation):
    """Read the circular ordering as a rotation system and verify Euler's count."""
    assert all(set(order) == set(meeting_graph[knot])
               for knot, order in enumerate(rotation))
    successor = {(other, knot): (knot, order[(index + 1) % len(order)])
                 for knot, order in enumerate(rotation)
                 for index, other in enumerate(order)}
    assert set(successor) == set(successor.values())
    unseen = set(successor)
    boundary_count = 0
    while unseen:
        first = next(iter(unseen))
        walk = first
        boundary_count += 1
        while walk in unseen:
            unseen.remove(walk)
            walk = successor[walk]
        assert walk == first
    assert len(rotation) - meeting_graph.number_of_edges() + boundary_count == 2
    return boundary_count


def obstruction(meeting_graph):
    """Find a literal subdivision of one of the two excluded classical patterns."""
    for size in range(meeting_graph.number_of_edges(), 8, -1):
        for kept in combinations(sorted(meeting_graph.edges), size):
            reduced = nx.Graph(kept)
            degrees = sorted(degree for _, degree in reduced.degree if degree != 2)
            if degrees not in ([3] * 6, [4] * 5):
                continue
            while any(degree == 2 for _, degree in reduced.degree):
                knot = next(knot for knot, degree in reduced.degree if degree == 2)
                left, right = reduced[knot]
                if reduced.has_edge(left, right):
                    break
                reduced.remove_node(knot)
                reduced.add_edge(left, right)
            if len(reduced) == 5 and all(degree == 4 for _, degree in reduced.degree):
                return "K5", kept
            if (len(reduced) == 6 and all(degree == 3 for _, degree in reduced.degree)
                    and nx.is_bipartite(reduced)):
                return "K3,3", kept
    raise AssertionError("No subdivision certificate found")


def certificate(meeting_graph):
    planar, embedding = nx.check_planarity(meeting_graph)
    if planar:
        rotation = [list(embedding.neighbors_cw_order(knot)) for knot in meeting_graph]
        return {"rotation": rotation, "boundary_count": check_rotation(meeting_graph, rotation)}
    forbidden, included = obstruction(meeting_graph)
    return {"classical_obstruction": forbidden, "included_meetings": included}


def closed_part(holdings, age):
    holders = holder_index(holdings)
    assert all(len(group) == 2 for group in holders.values())
    meetings = Counter(tuple(pair) for pair in holders.values())
    meeting_graph = nx.Graph()
    meeting_graph.add_nodes_from(range(len(holdings)))
    meeting_graph.add_edges_from(meetings)
    assert nx.is_connected(meeting_graph)
    proof = certificate(meeting_graph)
    arities = list(map(len, holdings))
    rows = list(map(as_mask, holdings))
    rank = binary_rank(rows)
    assert rank == len(holdings) - 1
    restrictions = [rank - binary_rank(other_row & ~row for other_row in rows)
                    for row in rows]
    canonical = [places >= 3 and count == 1
                 for places, count in zip(arities, restrictions, strict=True)]
    if age:
        assert binary_rank(rows[:-1]) == rank
    return {
        "age": age, "holdings": holdings, "knots": len(holdings),
        "distinctions": len(holders), "loop_rank": len(holders) - rank,
        "places_in_closing_holding": arities[-1] if age else None,
        "sharing_multiplicities": [(*pair, count) for pair, count in sorted(meetings.items())],
        "ordinary_even_words": 1 << (len(holders) - rank),
        "single_odd_ordinary_words": 0,
        "projection_constraint_counts": restrictions,
        "canonical_parity_knots": canonical,
        "signed_operator_admits_by_arkhipov": "classical_obstruction" in proof,
        "meeting_certificate": proof,
    }


def exceptional_projection(holdings):
    row_masks = list(map(as_mask, holdings))
    predecessor, closing = row_masks[:-1], row_masks[-1]
    words = [word for word in range(1 << len(holder_index(holdings)))
             if all((word & mask).bit_count() % 2 == 0 for mask in predecessor)]
    return {
        "predecessor_words": len(words),
        "ordinary_even_words": sum((word & closing).bit_count() % 2 == 0 for word in words),
        "single_odd_at_closing_ordinary_words": sum(
            (word & closing).bit_count() % 2 == 1 for word in words),
        "predecessor_projection_on_closing_distinctions": sorted({
            "".join(str((word >> distinction) & 1) for distinction in holdings[-1])
            for word in words
        }),
    }


def projected_knot_checks(parts):
    """Enumerate ordinary words and submit the projected relations to the canonical checker."""
    from knotlab.cli import main as knotlab_check

    checked = []
    for part in parts:
        is_exceptional = part["signed_operator_admits_by_arkhipov"]
        full_arity = all(len(support) >= 3 for support in part["holdings"])
        if not is_exceptional and not (full_arity and not all(part["canonical_parity_knots"])):
            continue
        rows = list(map(as_mask, part["holdings"]))
        allowed = [word for word in range(1 << part["distinctions"])
                   if all((word & mask).bit_count() % 2 == 0 for mask in rows)]
        assert len(allowed) == part["ordinary_even_words"]
        for index, (support, expected) in enumerate(zip(
                part["holdings"], part["canonical_parity_knots"], strict=True)):
            if expected and not is_exceptional:
                continue
            projected_words = {tuple((word >> distinction) & 1 for distinction in support)
                               for word in allowed}
            labels = [f"d{distinction}" for distinction in support]
            cnf = "; ".join(
                " ".join("~" + label if value else label
                         for label, value in zip(labels, word, strict=True))
                for word in product(range(2), repeat=len(support)) if word not in projected_words
            )
            output = StringIO()
            with redirect_stdout(output):
                status = knotlab_check([
                    "check", "--cnf", cnf, "--loops", *labels[:-1], "--contact", labels[-1], "--json",
                ])
            verdict = json.loads(output.getvalue())
            assert status == 0 and verdict["is_knot"] == expected
            checked.append({"start": part["start"], "holding_index": index, "verdict": verdict})
    return checked


def brute_proposals(size, witnessed):
    """All subsets, used only for the small proposal controls."""
    pairs = {pair for group in witnessed for pair in combinations(sorted(group), 2)}
    candidates = [set(group) for count in range(3, size + 1)
                  for group in combinations(range(size), count)
                  if all(pair in pairs for pair in combinations(group, 2))
                  and all(not set(group).issubset(witness) for witness in witnessed)]
    larger = [group for group in candidates
              if not any(group < other for other in candidates)]
    remaining = [pair for pair in pairs if not any(set(pair) <= group for group in larger)]
    return sorted(tuple(sorted(group)) for group in larger), sorted(remaining)


def controls():
    random = Random(82641)
    separate_triple = [(0, 1), (1, 2), (0, 2)]
    witnessed_triple = [(0, 1, 2)]
    assert brute_proposals(3, separate_triple) == ([(0, 1, 2)], [])
    assert brute_proposals(3, witnessed_triple) == ([], separate_triple[:1] + [(0, 2), (1, 2)])
    cases = [(3, separate_triple), (3, witnessed_triple)]
    for _ in range(96):
        size = random.randint(4, 8)
        witnessed = [random.sample(range(size), random.randint(2, size)) for _ in range(size)]
        cases.append((size, witnessed))
    for size, witnessed in cases:
        groups, uncovered = group_choices(size, witnessed)
        pairs = [(left, right) for left, mask in enumerate(uncovered)
                 for right in members(mask) if left < right]
        assert (groups, pairs) == brute_proposals(size, witnessed)
    return len(cases)


def original_rows(paths, keys):
    groups = defaultdict(list)
    for path in paths:
        with path.open() as stream:
            for line in stream:
                row = json.loads(line)
                if row["law"] == "parity":
                    groups[tuple(row[key] for key in keys)].append(row)
    return groups


def compare_archive(start, outcome, stages, closed, records, fields):
    archive_stages = [row for row in records if row["kind"] == "stage"]
    archive_parts = [row for row in records if row["kind"] == "closed_part"]
    summaries = [row for row in records if row["kind"] == "history"]
    archive_summary, = summaries
    assert archive_summary["outcome"] == outcome, (start, outcome, archive_summary)
    assert len(archive_stages) == len(stages), start
    for rebuilt, archived in zip(stages, archive_stages, strict=True):
        assert all(archived[key] == value for key, value in rebuilt.items()), (
            start, rebuilt, archived)
    for rebuilt_field, archived_field in fields:
        # The archive records the sampled start, before any birth, only for fresh draws.
        value = json.loads(json.dumps(start[rebuilt_field]))
        assert value == archive_summary[archived_field], (start, rebuilt_field)
    assert len(archive_parts) == int(closed is not None), start
    if closed is not None:
        archived, = archive_parts
        assert closed["age"] == archived["t"], start
        assert closed["holdings"] == list(map(tuple, archived["stars"])), start
        assert closed["knots"] == archived["knots"], start
        assert closed["distinctions"] == archived["distinctions"], start
        assert closed["loop_rank"] == archived["loop_rank"], start
        assert closed["signed_operator_admits_by_arkhipov"] == archived["admits"], start
        assert closed["signed_operator_admits_by_arkhipov"] == (archived["T"] == "fail"), start


def meeting_type_multiplicities(parts):
    representatives = []
    for part in parts:
        current = nx.Graph()
        current.add_weighted_edges_from(part["sharing_multiplicities"])
        same_weight = nx.algorithms.isomorphism.numerical_edge_match("weight", 1)
        for group, earlier in representatives:
            if nx.is_isomorphic(current, earlier, edge_match=same_weight):
                break
        else:
            group = {"members": [], "representative": part["start"]}
            representatives.append((group, current))
        group["members"].append(part["start"])
    return [{"multiplicity": len(group["members"]), **group} for group, _ in representatives]


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument("--recorded", action="store_true")
    parser.add_argument("--source", action="append")
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--sample-size", type=int)
    parser.add_argument("--sample-seed", type=int)
    parser.add_argument("--check-projections", action="store_true",
                        help="Verify the decisive projections with PYTHONPATH=tools")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not (args.fresh or args.recorded):
        parser.error("Choose --fresh, --recorded, or both")
    if (args.sample_size is None) != (args.sample_seed is None):
        parser.error("--sample-size and --sample-seed must be supplied together")
    cases = []
    fresh_archive = {}
    recorded_archive = {}
    if args.fresh:
        choices = list(fresh_draws())
        if args.pilot:
            projection_controls = {(1, 78), (3, 215)}
            choices = [(start, holdings) for start, holdings in choices
                       if start["draw"] < 8 or (start["arm"], start["draw"]) in projection_controls]
        if args.sample_size is not None:
            indices = sorted(Random(args.sample_seed).sample(range(len(choices)), args.sample_size))
            choices = [choices[index] for index in indices]
        cases.extend((start, holdings, 12, 5000) for start, holdings in choices)
        fresh_archive = original_rows(sorted(ORIGINAL.glob("p3_parity_*.jsonl")), ("arm", "draw"))
    if args.recorded:
        recorded = recorded_sources()
        names = args.source or (["five_founder_clock"] if args.pilot else sorted(recorded))
        cases.extend(({"source": name}, recorded[name], 16, 20000) for name in names)
        recorded_archive = original_rows([ORIGINAL / f"p2_{name}.jsonl" for name in names], ("source",))
    ordinary_controls = controls()
    parts = []
    outcomes = Counter()
    recorded_details = []
    stage_count = 0
    for start, holdings, horizon, cap in cases:
        outcome, stages, grown = history(holdings, horizon, cap)
        part = closed_part(grown, stages[-1]["t"]) if outcome == "closed" else None
        if "arm" in start:
            records = fresh_archive[(start["arm"], start["draw"])]
            fields = (("loose", "opens"), ("meetings", "meetings"),
                      ("extra_meetings", "extra_meetings"))
        else:
            records = recorded_archive[(start["source"],)]
            fields = ()
            recorded_details.append({"start": start, "outcome": outcome, "stages": stages})
        compare_archive(start, outcome, stages, part, records, fields)
        stage_count += len(stages)
        outcomes[outcome] += 1
        if part is not None:
            part["start"] = start
            parts.append(part)
            if part["signed_operator_admits_by_arkhipov"]:
                part["stages"] = stages
                part["founding_holdings"] = holdings
                part["ordinary_word_enumeration"] = exceptional_projection(grown)
                predecessor = grown[:-1]
                prior_meetings = nx.Graph()
                prior_meetings.add_nodes_from(range(len(predecessor)))
                prior_meetings.add_edges_from(tuple(knots) for knots in holder_index(predecessor).values()
                                             if len(knots) == 2)
                part["predecessor_meeting_certificate"] = certificate(prior_meetings)
    grouping = meeting_type_multiplicities(parts)
    canonical = [part for part in parts if all(part["canonical_parity_knots"])]
    summary = {
        "classification_source": "https://arxiv.org/abs/1209.3819",
        "sampling_seed": DRAW_SEED,
        "additional_sample_seed": args.sample_seed,
        "pilot": args.pilot,
        "fresh_draws_run": sum("arm" in start for start, _, _, _ in cases),
        "recorded_sources_run": len(recorded_details),
        "reconstructed_stages": stage_count,
        "matching_archived_outcomes_and_stage_counts": len(cases),
        "small_proposal_controls": ordinary_controls,
        "outcomes": outcomes,
        "closure_count": len(parts),
        "signed_operator_admits": sum(part["signed_operator_admits_by_arkhipov"] for part in parts),
        "closure_count_by_age": Counter(part["age"] for part in parts),
        "closing_holding_count_by_places": Counter(
            part["places_in_closing_holding"] for part in parts if part["age"]),
        "all_holdings_are_canonical_knots": len(canonical),
        "all_holdings_are_canonical_knots_by_age": Counter(part["age"] for part in canonical),
        "largest_sharing_multiplicity": max(
            (count for part in parts for _, _, count in part["sharing_multiplicities"]), default=0),
        "closed_presentation_counts_by_knots_and_distinctions": [
            [knots, distinctions, count] for (knots, distinctions), count in sorted(Counter(
                (part["knots"], part["distinctions"]) for part in parts).items())
        ],
        "distinct_literal_holdings": len({tuple(part["holdings"]) for part in parts}),
        "distinct_meeting_types": len(grouping),
        "meeting_type_counts_by_multiplicity": Counter(group["multiplicity"] for group in grouping),
    }
    result = {
        "summary": summary, "recorded_sources": recorded_details,
        "meeting_type_multiplicities": grouping, "closed_presentations": parts,
    }
    if args.check_projections:
        result["canonical_projection_checks"] = projected_knot_checks(parts)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
