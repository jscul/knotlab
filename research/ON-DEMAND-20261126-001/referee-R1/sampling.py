"""Reconstruct the frozen draws and count what the region comparisons exercise.

Only the start atlas and generic graph routines are shared. The draws, starting
counts, common-holder map, regions and groups are reconstructed here. Recorded
growth results supply the outcome flags; this script checks their opportunities.
"""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from itertools import combinations, islice, permutations, product
from math import exp
from pathlib import Path
from random import Random
from resource import RUSAGE_SELF, getrusage
from statistics import median
from time import perf_counter
import json

import networkx as nx
from networkx.generators.atlas import graph_atlas_g


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
POPULATIONS = {
    "tree40": (60, 20261201, 8),
    "treeplus25": (60, 20261202, 7),
    "census6": (400, 20261203, 10),
}
H1 = "H1 within t + 1 steps agrees"
SHORTER = "within t steps agrees"
CAPPED = "region growths stopped at the cap, not read"
STAGED = "admitted in three steps"


def pairs(meetings):
    return frozenset(tuple(sorted(meeting)) for meeting in meetings)


def neighbours(n, shared):
    out = [set() for _ in range(n)]
    for a, b in shared:
        out[a].add(b)
        out[b].add(a)
    return tuple(frozenset(group) for group in out)


def map_of(holders, live):
    out = nx.Graph()
    out.add_nodes_from(sorted(live))
    blocks = {block & live for block in holders}
    for block in blocks:
        out.add_edges_from(combinations(sorted(block), 2))
    return out, blocks


def groups_of(graph, blocks):
    joint = {frozenset(group) for group in nx.find_cliques(graph)
             if len(group) >= 3 and not any(set(group) <= block for block in blocks)}
    separate = {frozenset(pair) for pair in graph.edges
                if not any(set(pair) <= group for group in joint)}
    return joint | separate


def holdings_of(shared, loose):
    holdings = [[] for _ in loose]
    for distinction, (a, b) in enumerate(sorted(shared)):
        holdings[a].append(distinction)
        holdings[b].append(distinction)
    unused = len(shared)
    for row, count in zip(holdings, loose, strict=True):
        row.extend(range(unused, unused + count))
        unused += count
    return tuple(map(tuple, holdings))


@cache
def census_six():
    entries = []
    for graph in graph_atlas_g():
        if len(graph) != 6 or not nx.is_connected(graph):
            continue
        shared = pairs(graph.edges)
        symmetries = [order for order in permutations(range(6))
                      if pairs((order[a], order[b]) for a, b in shared) == shared]
        seen = set()
        domains = [range(max(0, 3 - graph.degree(i)), 4) for i in range(6)]
        for loose in product(*domains):
            if loose in seen or not any(loose):
                continue
            seen.update(tuple(loose[i] for i in order) for order in symmetries)
            entries.append((shared, loose))
    assert len(entries) == 82_656
    return entries


@cache
def late_view_sample():
    rest = list(range(len(census_six())))
    for seed, count in ((20261126, 1000), (20261127, 2000)):
        excluded = set(Random(seed).sample(rest, count))
        rest = [i for i in rest if i not in excluded]
    return Random(20261128).sample(rest, 2000)


def tree_start(n, rng, extra):
    word = [rng.randrange(n) for _ in range(n - 2)]
    occurrences = Counter(word)
    remaining = set(range(n))
    shared = set()
    for holder in word:
        leaf = min(i for i in remaining if not occurrences[i])
        shared.add(tuple(sorted((leaf, holder))))
        remaining.remove(leaf)
        occurrences[holder] -= 1
    shared.add(tuple(sorted(remaining)))
    if extra:
        available = [pair for pair in combinations(range(n), 2) if pair not in shared]
        product_of_draws, count = rng.random(), 0
        while product_of_draws > exp(-1):
            count += 1
            product_of_draws *= rng.random()
        shared.update(rng.sample(available, min(count, len(available))))
    holders = neighbours(n, shared)
    graph, blocks = map_of(holders, frozenset(range(n)))
    demand = Counter(knot for group in groups_of(graph, blocks) for knot in group)
    loose = tuple(max(3 - len(holders[i]), demand[i]) for i in range(n))
    return frozenset(shared), loose


@dataclass(frozen=True)
class Draw:
    index: int
    stars: tuple
    shared: frozenset
    loose: tuple
    holders: tuple
    live: frozenset
    reader: int
    steps: dict
    horizon: int
    h2_draws: tuple
    admission_order: tuple

    def reach(self, radius):
        return frozenset(knot for knot, steps in self.steps.items() if steps <= radius)


def draws(population):
    count, seed, horizon = POPULATIONS[population]
    rng = Random(seed)
    if population == "census6":
        indices = rng.sample(late_view_sample(), count)
        starts = ((index, *census_six()[index]) for index in indices)
    else:
        n = 40 if population == "tree40" else 25
        starts = ((index, *tree_start(n, rng, population == "treeplus25")) for index in range(count))
    for index, shared, loose in starts:
        holders = neighbours(len(loose), shared)
        live = frozenset(i for i, count in enumerate(loose) if count)
        graph, _ = map_of(holders, live)
        reader = rng.choice(sorted(live))
        steps = dict(nx.single_source_shortest_path_length(graph, reader))
        horizons = [rng.randint(1, horizon) for _ in range(3)]
        extras = tuple((t, frozenset(i for i in sorted(live) if steps.get(i, horizon + 2) > t + 1
                                    and rng.random() < 0.5)) for t in horizons)
        rest = [i for i in sorted(live) if steps.get(i, horizon + 2) > horizons[0] + 1]
        rng.shuffle(rest)
        yield Draw(index, holdings_of(shared, loose), shared, loose, holders, live, reader, steps,
                   horizon, extras, tuple(rest))


def gf2_rank(rows):
    pivot = {}
    for value in rows:
        while value:
            high = value.bit_length()
            if high not in pivot:
                pivot[high] = value
                break
            value ^= pivot[high]
    return len(pivot)


def parity_failures(stars):
    # Every rule has all even assignments on its own, and the all-zero state
    # satisfies the system. The projected codimension is the rank lost by
    # restricting the rule supports to distinctions outside the knot.
    masks = [sum(1 << bit for bit in row) for row in stars]
    rank = gf2_rank(masks)
    failed = []
    for i, mask in enumerate(masks):
        codimension = rank - gf2_rank(other & ~mask for other in masks)
        assert codimension >= 1
        if codimension > 1:
            failed.append({"knot": i, "places": len(stars[i]), "projected codimension": codimension,
                           "projected allowed states": 1 << (len(stars[i]) - codimension)})
    return failed


def keyed_start_identity(draw, buckets):
    graph = nx.Graph()
    graph.add_nodes_from((i, {"loose": count}) for i, count in enumerate(draw.loose))
    graph.add_edges_from(draw.shared)
    key = tuple(sorted((len(block), count) for block, count in zip(draw.holders, draw.loose, strict=True)))
    for previous, index in buckets[key]:
        if nx.is_isomorphic(graph, previous, node_match=lambda a, b: a == b):
            return index
    buckets[key].append((graph, draw.index))
    return draw.index


def grow_first(draw, region):
    graph, blocks = map_of(draw.holders, region)
    groups = groups_of(graph, blocks)
    demand = Counter(knot for group in groups for knot in group)
    short = sorted(knot for knot, cost in demand.items() if cost > draw.loose[knot])
    return groups, demand, short


def held_at_cut(groups, region):
    return [group for group in groups if len(group) >= 3 and group & region and group - region]


def read_archive(name):
    with (STUDY / f"results_{name}.jsonl").open() as source:
        return list(map(json.loads, source))


def scope_tag(region, reader_piece, live):
    if region == live:
        return "all live knots"
    if reader_piece <= region:
        return "proper subset holding whole reader piece"
    return "proper subset cutting reader piece"


def audit_h1(draw, law, row, graph, large_groups, first, counts):
    rounds = row["rounds read"]
    recorded = {int(t): agree for t, agree in row[H1].items()}
    shorter = {int(t): agree for t, agree in row[SHORTER].items()}
    capped = {t for alleged, t in row.get(CAPPED, ()) if alleged == "H1"}
    assert set(recorded) | capped == set(range(1, rounds + 1))
    assert not set(recorded) & capped and set(shorter) <= set(recorded)
    piece = frozenset(draw.steps)
    pair_groups = {group for group in first(draw.live)[0] if len(group) == 2}
    cases, misses = {}, []
    for t, match in recorded.items():
        smaller, base = draw.reach(t), draw.reach(t + 1)
        cut_smaller, cut_base = held_at_cut(large_groups, smaller), held_at_cut(large_groups, base)
        outcome = "agree" if match else "differ"
        counts["H1 by region"][f"{scope_tag(base, piece, draw.live)}: {outcome}"] += 1
        counts["H1 by round"][t] += 1
        counts["groups of three or more cut at t + 1"][f"{bool(cut_base)}: {outcome}"] += 1
        if first(base)[2]:
            counts["H1 initial shortage from restriction"][outcome] += 1
        cases[t, base] = match
        if t not in shorter:
            continue
        shorter_result = "agree" if shorter[t] else "differ"
        counts["groups of three or more cut at t"][f"{bool(cut_smaller)}: {shorter_result}"] += 1
        counts["by shorter region"][f"{scope_tag(smaller, piece, draw.live)}: {shorter_result}"] += 1
        shared_candidates = [(group, knot, group & smaller & graph[knot].keys())
                             for group in large_groups for knot in draw.live - smaller]
        shared_candidates = [(group, knot, retained) for group, knot, retained in shared_candidates if len(retained) >= 2]
        counts["outside candidate meeting two retained members of a large group"][
            f"{bool(shared_candidates)}: {shorter_result}"] += 1
        two_pairs = any(sum(frozenset((knot, member)) in pair_groups for member in retained) >= 2
                        for group, knot, retained in shared_candidates)
        counts["outside knot in two pair groups with retained members of a large group"][
            f"{two_pairs}: {shorter_result}"] += 1
        if first(smaller)[2]:
            counts["initial shortage from shorter restriction"][shorter_result] += 1
        if shorter[t] or not match:
            continue
        cut = [{"members": sorted(group), "kept": sorted(group & smaller), "omitted": sorted(group - smaller),
                "full group is present at t plus one": group <= base}
               for group in sorted(cut_smaller, key=sorted)]
        full_demand = first(draw.live)[1]
        small_groups, small_demand, short = first(smaller)
        miss = {"index": draw.index, "reader": draw.reader, "round": t, "within t": sorted(smaller),
                "within t plus one": sorted(base), "large groups cut at t": cut,
                "large groups still cut at t plus one": sorted(map(sorted, cut_base)),
                "groups made only in the shorter restriction": sorted(map(sorted, small_groups - first(draw.live)[0])),
                "round-one demand changes within t": [[k, full_demand[k], small_demand[k]] for k in sorted(smaller)
                                                       if full_demand[k] != small_demand[k]],
                "round-one shortages in shorter restriction": short,
                "outside common-candidate witnesses": [[sorted(group), knot, sorted(retained)]
                                                        for group, knot, retained in shared_candidates],
                "extra shared distinctions beyond a tree": len(draw.shared) - len(draw.loose) + 1}
        if t == 1 and law == "nae":
            readings = {label: one_round_views(draw, region) for label, region in (
                ("shorter region", smaller), ("predicted region", base), ("full", draw.live))}
            assert readings["shorter region"] != readings["full"] and readings["predicted region"] == readings["full"]
            parents = [Counter(tuple(parent_set) for parent_set, _ in read["reader birth descriptions"])
                       for read in readings.values()]
            counts["H1 first-round shorter misses independently replayed"][
                "same reader birth parents" if parents[0] == parents[2] else "different reader birth parents"] += 1
            miss["independent not-all-equal round-one readings"] = readings
        misses.append(miss)
    counts["H1 distinct region initializations"]["start and region"] += len({region for _, region in cases})
    return cases, misses


def audit_h2(draw, row, graph, first, h1_cases, counts):
    # There are three independently drawn subsets. The remaining three
    # checks are a single nested sequence at the first drawn horizon.
    front_round = draw.h2_draws[0][0]
    front = draw.reach(front_round + 1)
    half = front | frozenset(draw.admission_order[:len(draw.admission_order) // 2])
    expected = [(f"coin draw {i}", t, draw.reach(t + 1) | added, len(added))
                for i, (t, added) in enumerate(draw.h2_draws, 1)]
    rounds = row["rounds read"]
    cap = Counter((test, t) for test, t in row.get(CAPPED, ()) if test != "H1")
    read = iter(row["H2"])
    checks = []
    for kind, t, region, added in expected:
        if t > rounds:
            counts["unread comparisons"]["coin draw beyond full growth cap"] += 1
        elif cap["H2", t]:
            cap["H2", t] -= 1
            counts["unread comparisons"]["coin region hit cap"] += 1
        else:
            saved_t, number_added, match = next(read)
            assert (t, added) == (saved_t, number_added), (draw.index, t, added, saved_t, number_added)
            checks.append((kind, t, region, match))
    if front_round > rounds:
        counts["unread comparisons"]["staged region beyond full growth cap"] += 3
    else:
        saved_t, status, flags = next(read)
        assert (saved_t, status) == (front_round, STAGED)
        flags = iter(flags)
        for label, region in (("first stage", front), ("middle stage", half), ("last stage", draw.live)):
            if cap["H2 admitted", front_round]:
                cap["H2 admitted", front_round] -= 1
                counts["unread comparisons"]["staged region hit cap"] += 1
            else:
                checks.append((label, front_round, region, next(flags)))
        assert next(flags, None) is None
    assert next(read, None) is None and not +cap

    unique, distinct_regions, unique_coin_proper = {}, set(), set()
    unique_coin_piece, unique_coin_changed_component = set(), set()
    complete_piece = frozenset(draw.steps)
    for label, t, region, match in checks:
        base = draw.reach(t + 1)
        extras = region - base
        outcome = "agree" if match else "differ"
        key = t, region
        component = frozenset(nx.node_connected_component(graph.subgraph(region), draw.reader))
        assert base <= component <= complete_piece
        counts["all comparisons"][outcome] += 1
        counts["H2 by region"][f"{scope_tag(region, complete_piece, draw.live)}: {outcome}"] += 1
        counts["by kind"][f"{label}: {outcome}"] += 1
        counts["by comparison to the minimum region"][f"{'strict addition' if extras else 'same region'}: {outcome}"] += 1
        if extras & complete_piece:
            counts["reader change"][f"added a knot in the full reader piece: {outcome}"] += 1
        if component != base:
            counts["reader change"][f"enlarged the reader piece in the restriction: {outcome}"] += 1
        if first(region)[2]:
            counts["H2 initial shortage from restriction"][outcome] += 1
        if key in h1_cases:
            assert h1_cases[key] == match
            counts["repeated comparisons"]["same start, round and region as H1"] += 1
        if key in unique:
            assert unique[key] == match
        else:
            unique[key] = match
        distinct_regions.add(region)

        if label.startswith("coin"):
            counts["coin draws by horizon"][t] += 1
            counts["coin draws by count eligible for addition"][len(draw.live - base)] += 1
            counts["coin draws by actual number added"][len(extras)] += 1
            if base < region:
                counts["coin strict additions"][outcome] += 1
                if region < draw.live:
                    counts["coin strict additions"][f"proper region: {outcome}"] += 1
                    unique_coin_proper.add(key)
                if extras & complete_piece:
                    counts["coin strict additions"][f"adds to reader's full piece: {outcome}"] += 1
                    unique_coin_piece.add(key)
                if component != base:
                    counts["coin strict additions"][f"enlarges restricted reader piece: {outcome}"] += 1
                    unique_coin_changed_component.add(key)
        if label == "middle stage":
            counts["middle stages"][outcome] += 1
            if base < region < draw.live:
                counts["middle stages"][f"distinct proper addition: {outcome}"] += 1
            if base < component:
                counts["middle stages"][f"enlarges restricted reader piece: {outcome}"] += 1
                if component < complete_piece:
                    counts["middle stages"][f"enlarges restricted reader piece but leaves part out: {outcome}"] += 1
            if not (base < region < draw.live):
                counts["middle stages"]["repeats first or full region"] += 1

    for label, comparison in (("read checks beyond unique start, round and region", len(checks) - len(unique)),
                              ("read checks beyond unique start and region", len(checks) - len(distinct_regions)),
                              ("unique start, round and region combinations", len(unique)),
                              ("unique start and region initializations", len(distinct_regions))):
        counts["repeated comparisons"][label] += comparison
    counts["coin strict additions"]["distinct start, round and proper region"] += len(unique_coin_proper)
    counts["coin strict additions"]["distinct start, round and region adding to reader's full piece"] += len(unique_coin_piece)
    counts["coin strict additions"]["distinct start, round and region enlarging restricted reader piece"] += len(unique_coin_changed_component)
    counts["repeated comparisons"]["unique start, round and region combinations absent from H1"] += len(unique.keys() - h1_cases.keys())
    return checks


def comparable_archive_row(row):
    comparable = {name: value for name, value in row.items() if name != "seconds"}
    comparable["laws"] = {
        law: {name: value for name, value in check.items() if name != CAPPED or value}
        for law, check in row["laws"].items()
    }
    return comparable


def shortage_attribution(draw, shortages, first):
    first_short = next(((r, set(first(draw.reach(r))[2])) for r in range(max(draw.steps.values()) + 1)
                        if first(draw.reach(r))[2]), None)
    if first_short is None:
        assert not (set(shortages) & draw.steps.keys())
        return None, "all original shortages beyond reader piece", ()
    r, short = first_short
    original = set(shortages)
    if short <= original:
        attribution = "only original short knots"
    elif short & original:
        attribution = "both original and newly short knots"
    else:
        attribution = "only newly short knots"
    return r, attribution, tuple(sorted(short))


def audit_population(population, pilot):
    raw = read_archive(population)
    _, _, horizon = POPULATIONS[population]
    old_prefix = read_archive("treeplus25_first_run") if population == "treeplus25" else []
    buckets = defaultdict(list)
    weights, shape = defaultdict(Counter), Counter()
    results = {law: defaultdict(Counter) for law in ("nae", "parity")}
    starts = {"extra shared distinctions beyond a tree": {}, "no growth result": []}
    retained_checks = {"H1": Counter(), "H2": Counter()}
    parity_exclusions, repeated, cut_reports, failures, shortage_examples = [], [], [], [], []
    shares_by_extra = defaultdict(list)
    all_indices = []
    for ordinal, (draw, rec) in enumerate(islice(zip(draws(population), raw, strict=True), pilot)):
        assert (population, draw.index, draw.reader) == (rec["population"], rec["index"], rec["reader"])
        shape["readers checked"] += 1
        all_indices.append(draw.index)
        excess = len(draw.shared) - len(draw.loose) + 1
        if ordinal < len(old_prefix):
            assert comparable_archive_row(old_prefix[ordinal]) == comparable_archive_row(rec), draw.index
            shape["complete prefix records reproduced by guarded rerun"] += 1
        shape["starts with a cycle" if excess else "starts with no cycle"] += 1
        starts["extra shared distinctions beyond a tree"][draw.index] = excess
        identity = keyed_start_identity(draw, buckets)
        if identity != draw.index:
            repeated.append([identity, draw.index])
        fails_k2 = parity_failures(draw.stars)
        if fails_k2:
            parity_exclusions.append({"index": draw.index, "reader": draw.reader,
                                      "starting rules failing K2": fails_k2})
        if "not read" in rec:
            starts["no growth result"].append({"index": draw.index, "reader": draw.reader,
                                             "reason": rec["not read"], "cycle surplus": excess})
            continue
        assert (len(draw.live), len(draw.steps), max(draw.steps.values())) == (
            rec["live"], rec["live in the reader piece"], rec["eccentricity"]), draw.index
        shape["complete map geometry matched"] += 1
        graph, _ = map_of(draw.holders, draw.live)
        piece = frozenset(draw.steps)
        assert piece == frozenset(nx.node_connected_component(graph, draw.reader))
        first = cache(lambda region: grow_first(draw, region))
        groups, _, shortages = first(draw.live)
        large_groups = {group for group in groups if len(group) >= 3}
        shape["starts with groups of three or more"] += bool(large_groups)
        shape["starts with groups of three or more in the reader piece"] += any(group <= piece for group in large_groups)
        shape["starts with two groups of three or more meeting"] += any(a & b for a, b in combinations(large_groups, 2))
        for law, row in rec["laws"].items():
            counts = results[law]
            end, rounds = row["end"], row["rounds read"]
            assert (end == "stall") == bool(shortages), (population, draw.index, law, shortages)
            counts["end of full growth"][end] += 1
            if end == "cap":
                counts["unread horizons"]["beyond full-growth cap"] += horizon - rounds
                counts["full-growth cap after horizon"][rounds] += 1
                assert 0 <= rounds < horizon
            else:
                assert rounds == horizon
            if shortages:
                least, attribution, regional_short = shortage_attribution(draw, shortages, first)
                assert least == row["least steps whose knots stall"], (population, draw.index, least)
                counts["least map steps to a regional shortage"]["none" if least is None else str(least)] += 1
                counts["first regional shortage attribution"][attribution] += 1
                if any(knot not in piece for knot in shortages):
                    counts["first regional shortage attribution"]["at least one original shortage beyond reader piece"] += 1
                if law == "nae" and attribution != "only original short knots":
                    shortage_examples.append({"index": draw.index, "reader": draw.reader,
                                              "reader piece": sorted(piece), "full short knots": shortages,
                                              "first regional shortage found within map steps": least,
                                              "short knots in that region": regional_short})
                continue
            if large_groups:
                counts["non-stalling start exposure"]["large group"] += 1
                if any(group <= piece for group in large_groups):
                    counts["non-stalling start exposure"]["large group in reader piece"] += 1
                if any(a & b for a, b in combinations(large_groups, 2)):
                    counts["non-stalling start exposure"]["two large groups meeting"] += 1
            h1_cases, shorter_only = audit_h1(draw, law, row, graph, large_groups, first, counts)
            h2_cases = audit_h2(draw, row, graph, first, h1_cases, counts)
            for t, match in row[H1].items():
                if law == "parity" and not fails_k2:
                    retained_checks["H1"]["agree" if match else "differ"] += 1
            for label, t, region, match in h2_cases:
                if law == "parity" and not fails_k2:
                    retained_checks["H2"]["agree" if match else "differ"] += 1
                if not match:
                    failures.append({"index": draw.index, "reader": draw.reader, "law": law, "comparison": label,
                                     "round": t, "region": sorted(region), "K2 at the start": not bool(fails_k2)})
            if law != "nae":
                continue
            cut_reports.extend(shorter_only)
            weights["successful tree weighting or cycle-surplus group"][f"surplus {excess}, starts"] += 1
            weights["successful tree weighting or cycle-surplus group"][f"surplus {excess}, H1 checked"] += len(h1_cases)
            weights["successful tree weighting or cycle-surplus group"][f"surplus {excess}, H2 checked"] += len(h2_cases)
            weights["successful tree weighting or cycle-surplus group"][f"surplus {excess}, shorter miss"] += len(shorter_only)
            needed, total = row["births needed, of all births, through round t"][str(rounds)]
            shares_by_extra["with a cycle" if excess else "no cycle"].append(needed / total)
    return {
        "draw identity and structure": shape,
        "all start indices in recorded order": all_indices,
        "draw index sequence SHA-256": sha256(json.dumps(all_indices).encode()).hexdigest(),
        "distinct start identities up to renaming": sum(map(len, buckets.values())),
        "repeated start identities up to renaming": repeated,
        "start draw details": starts,
        "counts by law": results,
        "not-all-equal extra-line weights": weights,
        "recorded not-all-equal birth shares by cycle membership": {
            group: {"starts": len(shares), "median": median(shares), "least": min(shares)}
            for group, shares in shares_by_extra.items()
        },
        "not-all-equal t-step misses fixed by t plus one": cut_reports,
        "not-all-equal shortage examples": shortage_examples,
        "H2 comparison misses": failures,
        "parity exclusions by K2 at the start": parity_exclusions,
        "parity checks on starts passing K1–K3 for each starting rule": retained_checks,
    }


def one_round_views(draw, region):
    groups, demand, short = grow_first(draw, region)
    if short:
        return {"shortages": short, "reader birth descriptions": []}
    parents = list(sorted(groups, key=sorted))
    for knot in sorted(region):
        parents.extend([frozenset((knot,))] * (draw.loose[knot] - demand[knot]))
    sibling_blocks = tuple(frozenset(i for i, parent_set in enumerate(parents) if knot in parent_set)
                           for knot in sorted(region))
    next_map, blocks = map_of(sibling_blocks, frozenset(range(len(parents))))
    next_demand = Counter(i for group in groups_of(next_map, blocks) for i in group)
    descriptions = [[sorted(together), max(next_demand[i], 3 - len(together), 1)]
                    for i, together in enumerate(parents) if draw.reader in together]
    return {"shortages": [], "reader birth descriptions": descriptions}


def not_all_equal_projections(stars):
    masks = [sum(1 << d for d in support) for support in stars]
    projections = [set() for support in stars]
    for state in range(1 << max(masks).bit_length()):
        if all(state & mask not in (0, mask) for mask in masks):
            for projection, mask in zip(projections, masks, strict=True):
                projection.add(state & mask)
    sizes = [len(projection) for projection in projections]
    # The two constant states are excluded by the rule. If all other states
    # appear in its projection, forgetting any distinction frees the rest.
    assert sizes == [(1 << len(support)) - 2 for support in stars]
    return sizes


def second_hypothesis_witness():
    # The reader's piece is unchanged. A partial admission in a different
    # piece can introduce a round-one shortage, which stalls the whole region.
    names = "abcdhxyz"
    shared = pairs(tuple(names.index(knot) for knot in meeting)
                   for meeting in ("ha", "hb", "hc", "ax", "dx", "by", "dy", "cz", "dz"))
    loose = (1, 1, 1, 1, 0, 2, 2, 2)
    holders = neighbours(len(loose), shared)
    live = frozenset(i for i, count in enumerate(loose) if count)
    graph, _ = map_of(holders, live)
    reader = names.index("x")
    steps = dict(nx.single_source_shortest_path_length(graph, reader))
    stars = holdings_of(shared, loose)
    draw = Draw(-1, stars, shared, loose, holders, live, reader, steps, 1, (), ())
    through_two = draw.reach(2)
    more = live - {names.index("d")}
    base_read, middle_read, full_read = (one_round_views(draw, region) for region in (through_two, more, live))
    assert through_two < more < live and base_read == full_read
    assert base_read["reader birth descriptions"] and middle_read["shortages"] == [0, 1, 2]

    def describe(region):
        groups, demand, short = grow_first(draw, region)
        return {"kept knots": [names[i] for i in sorted(region)],
                "round-one groups": [[names[i] for i in group] for group in sorted(map(sorted, groups))],
                "demand and loose counts": {names[i]: [demand[i], loose[i]] for i in sorted(region)},
                "short knots": [names[i] for i in short],
                "reader birth parents and fresh counts": [[[names[i] for i in parents], fresh]
                                                           for parents, fresh in one_round_views(draw, region)["reader birth descriptions"]]}

    return {"law": "not-all-equal", "round": 1, "reader": "x", "start knots by number": names,
            "starting rule supports": stars, "shared distinctions by holders": [[names[a], names[b]] for a, b in sorted(shared)],
            "projected states at each starting rule (passes K1–K3)": not_all_equal_projections(stars),
            "full": describe(live), "within two steps of the map": describe(through_two),
            "strict partial admission": describe(more)}


def main(pilot):
    begun = perf_counter()
    summaries = {name: audit_population(name, pilot) for name in POPULATIONS}
    return {
        "scope": "timing pilot on each population prefix" if pilot is not None else "all frozen starts and recorded comparisons",
        "independence": "Starting counts, random draws and common-holder map independently implemented from the design. The graph atlas provides the historical census order and generic graph routines. Growth outcomes and cap eligibility are read from the archives. Round-one shortages are recomputed directly.",
        "region classifications": "A proper subset cutting the reader's piece omits a knot reachable in the full map. A restricted reader piece is recomputed in that region, so adding a knot in the full piece need not enlarge the restricted one.",
        "H2 weights": {"coin comparisons": "Three independent rounds uniform on 1 through the target. With m eligible knots at the drawn round, each exact additional subset has weight 1/2^m before eligibility exclusions.",
                       "staged comparison": "One fresh growth per region at the first coin round, starting with the minimum region. The middle region adds the first floor(m/2) names of one uniformly shuffled order. Every subset of that size has equal weight. The final region is the whole start.",
                       "eligibility": "Starts without a saved growth, starts stalling at round one, horizons after a full-growth cap, and regions hitting a region cap are excluded where applicable."},
        "populations": summaries,
        "strict-superset counterexample": second_hypothesis_witness(),
        "seconds": round(perf_counter() - begun, 3),
        "peak resident KiB": getrusage(RUSAGE_SELF).ru_maxrss,
    }


if __name__ == "__main__":
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("--pilot", type=int, metavar="STARTS", help="use a prefix of each population")
    args = cli.parse_args()
    summary = main(args.pilot)
    name = "sampling_pilot.json" if args.pilot is not None else "sampling.json"
    (HERE / name).write_text(json.dumps(summary, indent=2) + "\n")
    print(name, summary["seconds"], "seconds", summary["peak resident KiB"], "KiB")
