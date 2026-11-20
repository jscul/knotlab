"""Exact built-fixture checks for the two ordinary growth laws."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import combinations
import json
from pathlib import Path
import random
import sys

import networkx as nx
from pysat.solvers import Minisat22


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "fixtures.json"
WORLD = ROOT / "experiments/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A/"
                       "ORDINARY-DYNAMICS-20261120-001A-E001_ordinary"))
from end_operator import from_stars, step
from knotlab.knots import check_knot
from knotlab.relations import Relation


@dataclass(frozen=True)
class Birth:
    knot: int
    parents: tuple
    inputs: tuple
    fresh: tuple

    @property
    def support(self):
        return self.inputs + self.fresh


def incidence(stars):
    owners = defaultdict(list)
    ordinary = nx.Graph()
    ordinary.add_nodes_from(range(len(stars)))
    loose = defaultdict(list)
    for knot, support in enumerate(stars):
        for distinction in support:
            owners[distinction].append(knot)
    for distinction, holders in owners.items():
        assert len(holders) in (1, 2) and len(holders) == len(set(holders))
        if len(holders) == 1:
            loose[holders[0]].append(distinction)
        else:
            ordinary.add_edge(*holders)
    return owners, ordinary, {knot: sorted(bits) for knot, bits in loose.items()}


def witnessed_end(ordinary, loose):
    """The weaker reader receives just live knots and their witness sets."""
    blocks = [frozenset(set(ordinary[knot]) & loose.keys()) for knot in ordinary]
    graph = nx.Graph()
    graph.add_nodes_from(loose)
    graph.add_edges_from(pair for block in blocks for pair in combinations(sorted(block), 2))
    return blocks, graph


def multi_groups(blocks, graph):
    big = sorted(tuple(sorted(group)) for group in nx.find_cliques(graph)
                 if len(group) >= 3 and not any(set(group) <= block for block in blocks))
    used = {pair for group in big for pair in combinations(group, 2)}
    pairs = {tuple(sorted(pair)) for pair in graph.edges}
    return tuple(big + sorted(pairs - used))


def literal_turn(stars, law):
    """Generate independently from ordinary incidences, checking the archived operator."""
    owners, graph, loose = incidence(stars)
    old_end = from_stars(stars)
    assert old_end.opens == {k: len(row) for k, row in loose.items()}
    actual = step(old_end, law, max_births=1024)
    if not loose:
        assert actual.status == "closed"
        return actual.status, (), ()

    blocks, end = witnessed_end(graph, loose)
    multi = multi_groups(blocks, end)
    spent = Counter(knot for group in multi for knot in group)
    assert all(spent[knot] <= len(bits) for knot, bits in loose.items())
    parents = multi + tuple((knot,) for knot in sorted(loose)
                            for _ in range(len(loose[knot]) - spent[knot]))
    siblings = defaultdict(set)
    next_graph = nx.Graph()
    next_graph.add_nodes_from(range(len(parents)))
    for i, group in enumerate(parents):
        for parent in group:
            siblings[parent].add(i)
    next_graph.add_edges_from(pair for siblings_of_parent in siblings.values()
                              for pair in combinations(sorted(siblings_of_parent), 2))
    demand = Counter(child for group in multi_groups(tuple(siblings.values()), next_graph)
                     for child in group)
    implied = law == "parity" and len(parents) == 1
    fresh = tuple(0 if implied else max(1, 3 - len(group), demand[i])
                  for i, group in enumerate(parents))
    assert actual.status == "extend" and actual.parents == parents and actual.fresh == fresh
    assert actual.demand == tuple(demand[i] for i in range(len(parents))) and actual.implied == implied

    queue = {knot: iter(bits) for knot, bits in loose.items()}
    top = max(owners) + 1
    births = []
    for i, (group, count) in enumerate(zip(parents, fresh, strict=True)):
        births.append(Birth(len(stars) + i, group, tuple(next(queue[knot]) for knot in group),
                            tuple(range(top, top + count))))
        top += count
    assert all(next(bits, None) is None for bits in queue.values())
    return "extend", tuple(births), multi


def trajectory(source, law, horizon):
    frames = [source]
    layers = []
    for _ in range(horizon):
        status, births, multi = literal_turn(frames[-1], law)
        if status == "closed":
            break
        layers.append((births, multi))
        frames.append(frames[-1] + tuple(birth.support for birth in births))
    return frames, layers


def source_from(meetings, opens):
    stars = [[] for _ in opens]
    for d, (left, right) in enumerate(meetings):
        stars[left].append(d)
        stars[right].append(d)
    top = len(meetings)
    for row, count in zip(stars, opens, strict=True):
        row.extend(range(top, top + count))
        top += count
    return tuple(map(tuple, stars))


def archived_case(spec):
    degree = Counter(knot for pair in spec["meetings"] for knot in pair)
    return source_from(spec["meetings"], [a - degree[k] for k, a in enumerate(spec["sizes"])])


def solo_on_background(two, keep):
    """Remove one exclusive ring, preserving the funded spare at each surviving holder."""
    owners, ordinary, loose = incidence(archived_case(two))
    assert all(len(p) <= 2 for p in owners.values())
    blocks, graph = witnessed_end(ordinary, loose)
    groups = multi_groups(blocks, graph)
    assert all(len(group) == 2 for group in groups)
    used = Counter(knot for pair in groups for knot in pair)
    retain = sorted(set(two["roles"]["background"]) | set(two["roles"]["rings"][keep]))
    names = {old: new for new, old in enumerate(retain)}
    meetings = [(names[u], names[v]) for u, v in two["meetings"] if u in names and v in names]
    restricted = nx.Graph(meetings)
    restricted.add_nodes_from(names.values())
    demand = [sum(restricted.degree[w] - 1 for w in restricted[v]) for v in range(len(retain))]
    opens = [demand[i] + len(loose[old]) - used[old] for i, old in enumerate(retain)]
    source = source_from(meetings, opens)
    return source, tuple(names[v] for v in two["roles"]["rings"][keep]), tuple(retain)


def mask(bits):
    return sum(1 << bit for bit in bits)


def parity_words(stars, scope):
    """Eliminate distinctions outside the scope before evaluating projected words."""
    keep = mask(scope)
    pivots, equations = {}, []
    for row in stars:
        word = mask(row)
        while word & ~keep:
            pivot = (word & ~keep).bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = word
                break
            word ^= pivots[pivot]
        else:
            if word:
                equations.append(mask(i for i, d in enumerate(scope) if word >> d & 1))
    return tuple(w for w in range(1 << len(scope))
                 if all((w & row).bit_count() % 2 == 0 for row in equations))


def nae_add(solver, row):
    solver.add_clause([d + 1 for d in row])
    solver.add_clause([-d - 1 for d in row])


def nae_words(solver, scope):
    return tuple(w for w in range(1 << len(scope))
                 if solver.solve(assumptions=[(d + 1) if w >> i & 1 else (-d - 1)
                                              for i, d in enumerate(scope)]))


@cache
def expected_words(law, size):
    end = (1 << size) - 1
    if law == "parity":
        return tuple(w for w in range(end + 1) if w.bit_count() % 2 == 0)
    return tuple(range(1, end))


@cache
def canonical_relation(law, size):
    # Only the named small types need the slower canonical implementation.
    if size <= 5:
        names = tuple(map(str, range(size)))
        rows = frozenset(tuple(bool(w >> i & 1) for i in range(size))
                         for w in expected_words(law, size))
        assert check_knot(Relation(names, rows), names[:-1], names[-1]).is_knot
    assert size >= 3


def certify_source(stars, law):
    assert len(stars) == len(set(map(frozenset, stars)))
    _, graph, _ = incidence(stars)
    assert nx.is_connected(graph)
    with Minisat22() as solver:
        if law == "nae":
            for row in stars:
                nae_add(solver, row)
        for row in stars:
            words = parity_words(stars, row) if law == "parity" else nae_words(solver, row)
            assert words == expected_words(law, len(row))
            canonical_relation(law, len(row))


def fixed_map_replay(source, layers, law, later_first):
    """Materialize two parent-closed orders of the supplied whole-layer plan."""
    remaining = {b.knot: (age, b) for age, (layer, _) in enumerate(layers, 1) for b in layer}
    sources = {b.knot: b for _, b in remaining.values()}
    holds, _, _ = incidence(source)
    old_rows = dict(enumerate(source))
    for birth in sources.values():
        assert all(parent in sources or parent in old_rows for parent in birth.parents)
    age_sequence = []
    all_input_projections = Counter()
    covering_events = []
    with Minisat22() as solver:
        if law == "nae":
            for row in source:
                nae_add(solver, row)
        while remaining:
            eligible = (k for k, (_, b) in remaining.items() if all(p in old_rows for p in b.parents))
            k = (max if later_first else min)(eligible)
            age, birth = remaining.pop(k)
            age_sequence.append(age)
            assert len(birth.support) >= 3 and len(set(birth.support)) == len(birth.support)
            assert all(holds[d] == [p] for p, d in zip(birth.parents, birth.inputs, strict=True))
            assert all(d not in holds for d in birth.fresh)
            all_loose = {d for d, at in holds.items() if len(at) == 1}
            pinned_all = all_loose == set(birth.inputs)
            wants = tuple(range(1 << len(birth.inputs)))
            if law == "parity":
                # The accumulated ordinary graph is connected. Summing its checks
                # gives precisely one constraint on the loose distinctions.
                if pinned_all:
                    wants = expected_words(law, len(birth.inputs))
                assert bool(birth.fresh) == (not pinned_all)
                if len(source) <= 8 and len(old_rows) <= 48:
                    assert parity_words(tuple(old_rows.values()), birth.inputs) == wants
            else:
                assert birth.fresh
                assert nae_words(solver, birth.inputs) == wants
                nae_add(solver, birth.support)
            if pinned_all:
                covering_events.append({"age": age, "input_scope": birth.inputs,
                                        "parent_count": len(birth.parents), "arity": len(birth.support),
                                        "input_projected_words": wants, "fresh": len(birth.fresh)})
            canonical_relation(law, len(birth.support))
            for d in birth.support:
                holds[d].append(k)
            old_rows[k] = birth.support
            all_input_projections[len(birth.inputs)] += 1
    assert all(old_rows[k] == b.support for k, b in sources.items())
    return {"births": len(age_sequence),
            "earlier_age_after_later": sum(b < a for a, b in zip(age_sequence, age_sequence[1:])),
            "supply_covering_events": covering_events,
            "input_arity_checks": sorted(all_input_projections.items())}


def induced_cycles(graph, length):
    """Count each cyclic set once, with reversal and rotation forgotten."""
    result = set()

    def extend(path):
        at = path[-1]
        for end in graph[at]:
            if end <= path[0] or end in path:
                continue
            if any(graph.has_edge(end, p) for p in path[1:-1]):
                continue
            if len(path) == length - 1:
                if graph.has_edge(end, path[0]):
                    result.add(frozenset((*path, end)))
            elif not graph.has_edge(end, path[0]) or len(path) == 1:
                extend((*path, end))

    for first in graph:
        extend((first,))
    return result


def read_end(stars, lengths):
    _, ordinary, loose = incidence(stars)
    _, graph = witnessed_end(ordinary, loose)
    return {
        "parts": {frozenset(row) for row in nx.connected_components(graph)},
        "tips": {knot for knot in graph if graph.degree[knot] == 1 and len(loose[knot]) == 2},
        "cycles": set().union(*(induced_cycles(graph, length) for length in lengths)),
    }


def peel(stars, law):
    """Read a fully delivered continuing frame without source marks or birth dates."""
    names = tuple(range(len(stars)))
    parents = {}
    depths = 0
    while True:
        _, graph, loose = incidence(stars)
        old = tuple(k for k in graph if k not in loose)
        remaining = graph.subgraph(old)
        if not old or not loose or not nx.is_connected(remaining):
            break
        if any(any(w in loose for w in graph[k]) for k in loose):
            break
        prior = tuple(stars[k] for k in old)
        prior_bits, _, earlier_loose = incidence(prior)
        actual = step(from_stars(prior), law, max_births=1024)
        if actual.status != "extend" or not all(actual.fresh):
            break
        obligations = Counter(zip(actual.parents, actual.fresh, strict=True))
        removed = {}
        consumed = []
        for k in loose:
            inputs = [d for d in stars[k] if d in prior_bits]
            if any(len(prior_bits[d]) != 1 for d in inputs):
                break
            group = tuple(sorted(prior_bits[d][0] for d in inputs))
            if len(set(group)) != len(group):
                break
            obligations[group, len(loose[k])] -= 1
            removed[names[k]] = frozenset(names[old[p]] for p in group)
            consumed.extend(inputs)
        else:
            if not any(obligations.values()) and sorted(consumed) == sorted(
                    d for bits in earlier_loose.values() for d in bits):
                parents.update(removed)
                names = tuple(names[k] for k in old)
                stars = prior
                depths += 1
                continue
        break
    _, graph, _ = incidence(stars)
    rings = {frozenset(names[v] for v in block) for block in nx.biconnected_components(graph)
             if len(block) >= 5 and all(graph.subgraph(block).degree(v) == 2 for v in block)}
    return frozenset(names), parents, rings, depths


def rename(stars, seed):
    rng = random.Random(seed)
    names = list(range(len(stars)))
    bits = sorted({d for row in stars for d in row})
    other_bits = rng.sample(range(len(bits) + 100, (len(bits) + 100) * 4), len(bits))
    rng.shuffle(names)
    mapped = dict(zip(bits, other_bits, strict=True))
    renamed = [tuple(rng.sample(row, len(row))) if row else ()
               for k in names for row in [tuple(mapped[d] for d in stars[k])]]
    return tuple(renamed), names


def transport_sets(groups, mapping):
    return {frozenset(mapping[k] for k in row) for row in groups}


def read_ring_families(stars, rings, recovered_parents):
    """At the present end, retain a ring family by requiring every parent."""
    _, _, loose = incidence(stars)

    @cache
    def belongs(knot, ring):
        if knot not in recovered_parents:
            return knot in ring
        return all(belongs(p, ring) for p in recovered_parents[knot])

    return {ring: frozenset(k for k in loose if belongs(k, ring)) for ring in rings}


def check_readers(frame, law, families, oracle_parents, want_depth, cycle_lengths, seed):
    root, parents, read_rings, depth = peel(frame, law)
    assert depth == want_depth and oracle_parents.items() <= parents.items() and read_rings == families.keys()
    assert read_ring_families(frame, read_rings, parents) == families
    end = read_end(frame, cycle_lengths)
    renamed, names = rename(frame, seed)
    root1, parents1, rings1, depth1 = peel(renamed, law)
    assert root == frozenset(names[k] for k in root1) and depth == depth1
    assert parents == {names[k]: frozenset(names[p] for p in row) for k, row in parents1.items()}
    assert read_rings == transport_sets(rings1, names)
    reassigned = {frozenset(names[k] for k in ring): frozenset(names[k] for k in cohort)
                  for ring, cohort in read_ring_families(renamed, rings1, parents1).items()}
    assert reassigned == families
    end1 = read_end(renamed, cycle_lengths)
    assert end["parts"] == transport_sets(end1["parts"], names)
    assert end["cycles"] == transport_sets(end1["cycles"], names)
    assert end["tips"] == {names[k] for k in end1["tips"]}
    return end


def checked_parts(frame, births, new_parts):
    """Check the entire physical component correspondence, including all witnesses."""
    _, graph, loose = incidence(frame)
    _, end = witnessed_end(graph, loose)
    parts = {frozenset(component) for component in nx.connected_components(end)}
    home = {p: part for part in parts for p in part}
    children = defaultdict(set)
    image = defaultdict(set)
    for b in births:
        old_parts = {home[p] for p in b.parents}
        assert len(old_parts) == 1
        for p in b.parents:
            children[p].add(b.knot)
        image[old_parts.pop()].add(b.knot)
    assert children.keys() == home.keys()
    assert all(children[u] & children[v] for u, v in end.edges)
    if new_parts:
        assert set(map(frozenset, image.values())) == new_parts
    else:
        assert len(births) == 1 and not births[0].fresh


def small_panel(source, law, horizon, rings=(), *, cycle_lengths=(), earlier_valid_frames=0):
    certify_source(source, law)
    frames, layers = trajectory(source, law, horizon)
    parents = {}
    source_origins = {knot: {knot} for knot in range(len(source))}
    spines = tuple(rings)
    rows = []
    for age, frame in enumerate(frames):
        births, multi = layers[age - 1] if age else ((), ())
        for birth in births:
            parents[birth.knot] = frozenset(birth.parents)
            source_origins[birth.knot] = set().union(*(source_origins[p] for p in birth.parents))
        _, _, loose = incidence(frame)
        families = {ring: frozenset(k for k in loose if source_origins[k] <= ring) for ring in rings}
        if age:
            spines = tuple(frozenset(b.knot for b in births if len(b.parents) == 2 and set(b.parents) <= old)
                           for old in spines)
        if loose:
            depth = age + earlier_valid_frames
            end = check_readers(frame, law, families, parents, depth, cycle_lengths, 2026112080 + age)
        else:
            depth = None
            end = read_end(frame, cycle_lengths)
            assert not any(end.values())
        if age:
            checked_parts(frames[age - 1], births, end["parts"])
        assert all(spine in end["cycles"] for spine in spines)
        rows.append({"age": age, "knots": len(frame), "distinctions": len({d for row in frame for d in row}),
                     "born": len(births), "fresh": sum(len(b.fresh) for b in births),
                     "proposed_previous_multi": len(multi), "part_sizes": sorted(map(len, end["parts"])),
                     "cyclic_sets": len(end["cycles"]), "tips": sorted(end["tips"]), "peeled_frames": depth,
                     "current_ring_family_sizes": sorted(map(len, families.values())),
                     "ring_core_cyclic_sets": len(spines),
                     "closed": not loose})
    replay = {tag: fixed_map_replay(source, layers, law, order)
              for tag, order in (("earliest_ready", False), ("latest_ready", True))}
    return {"source": source, "stages": rows, "replay": replay}, frames, layers


def clusters(period, spare_phase, size):
    """Connected sets on the unrolled ring, modulo full turns.

    A retained set has a nonempty straight run, plus some of the optional
    terminal points hanging from positions in that run.
    """
    return {(start, length, pendants) for start in range(period) for length in range(1, size + 1)
            for pendants in combinations([i for i in range(length)
                                          if (start + i) % period == spare_phase], size - length)}


def deletions(cluster, period):
    start, length, pendants = cluster
    parents = {(start, length, tuple(p for p in pendants if p != dropped)) for dropped in pendants}
    if length > 1 and 0 not in pendants:
        parents.add(((start + 1) % period, length - 1, tuple(p - 1 for p in pendants)))
    if length > 1 and length - 1 not in pendants:
        parents.add((start, length - 1, pendants))
    return parents


def independent_ring_map(source, layers):
    _, graph, loose = incidence(source)
    _, end = witnessed_end(graph, loose)
    cycle = [min(end), min(end[min(end)])]
    while len(cycle) < len(end):
        cycle.append(next(iter(set(end[cycle[-1]]) - {cycle[-2]})))
    assert len(set(cycle)) == len(end) and end.has_edge(cycle[-1], cycle[0])
    spare = [i for i, v in enumerate(cycle) if len(loose[v]) == 3]
    assert len(spare) <= 1
    phase = spare[0] if spare else None
    p = len(cycle)
    naming = {(i, 1, ()): v for i, v in enumerate(cycle)}
    counts = [p]
    verified_rosters = 0
    for size, (births, _) in enumerate(layers, 2):
        by_parents = {frozenset(b.parents): b for b in births}
        assert len(by_parents) == len(births)
        this_layer = clusters(p, phase, size)
        following = Counter(ancestor for child in clusters(p, phase, size + 1)
                            for ancestor in deletions(child, p))
        comes_from = {}
        for child in sorted(this_layer):
            parent_set = frozenset(naming[anc] for anc in deletions(child, p))
            b = by_parents[parent_set]
            assert len(b.fresh) == following[child]
            comes_from[child] = b.knot
        assert set(comes_from.values()) == {b.knot for b in births}
        counts.append(len(comes_from))
        naming = comes_from
        verified_rosters += len(comes_from)
    return {"canonical_cohort_sizes": counts, "births_checked_by_all_deletions_and_fresh": verified_rosters}


def bare_run_control(source, layers):
    _, graph, loose = incidence(source)
    _, end = witnessed_end(graph, loose)
    sequences = set()
    for v in end:
        for w in end[v]:
            run = [v, w]
            sequences.add(frozenset({v}))
            while len(run) < len(end):
                sequences.add(frozenset(run))
                run.append(next(iter(set(end[run[-1]]) - {run[-2]})))
    summaries = {}
    for run in sequences:
        strict, inclusive = set(run), set(run)
        records = [[len(run), len(run)]]
        for depth, (births, _) in enumerate(layers, 1):
            strict = {b.knot for b in births if set(b.parents) <= strict}
            inclusive = {b.knot for b in births if set(b.parents) & inclusive}
            counts = [len(strict), len(inclusive)]
            assert counts == [max(len(run) - depth, 0), min(len(end), len(run) + depth)]
            records.append(counts)
        assert summaries.setdefault(len(run), records) == records
    return {"proper_run_sets": len(sequences), "all_and_any_counts_by_initial_run_length": summaries}


def relay_tips(source, layers, sizes):
    active = read_end(source, ())
    assert len(active["parts"]) == 1 and len(active["tips"]) == 2
    tips = active["tips"]
    seen = []
    for age, (births, _) in enumerate(layers, 1):
        actual = {b.knot for b in births if len(b.parents) == 1 and b.parents[0] in tips}
        assert len(actual) == 2 and actual == set(sizes[age]["tips"])
        assert all(len(b.fresh) == 2 for b in births if b.knot in actual)
        assert sizes[age]["part_sizes"] == [age + 2]
        seen.append(sorted(actual))
        tips = actual
    _, graph, loose = incidence(source)
    _, end = witnessed_end(graph, loose)
    end.remove_edges_from(list(end.edges))
    erased_tips = [v for v in end if end.degree(v) == 1 and len(loose[v]) == 2]
    assert not erased_tips
    return {"unary_tips": seen, "tips_after_witness_erasure": erased_tips}


def earlier_births(source, layers, marked):
    """Evaluator: follow distinct original marks through verified physical parents."""
    marked = frozenset(marked)
    colors = [{v} for v in range(len(source))]
    all_nodes = [dict(enumerate(colors))]
    for births, _ in layers:
        layer = {}
        for birth in births:
            ancestry = set().union(*(colors[p] for p in birth.parents))
            assert len(colors) == birth.knot
            colors.append(ancestry)
            layer[birth.knot] = ancestry
        all_nodes.append(layer)
    pure = [{k for k, ancestors in layer.items() if ancestors <= marked} for layer in all_nodes]
    return colors, all_nodes, pure


def paired_pure(target_source, target_layers, marked, isolated, isolated_layers, isolated_mark):
    _, _, pure = earlier_births(target_source, target_layers, marked)
    _, _, solo = earlier_births(isolated, isolated_layers, isolated_mark)
    # Archived rings list the five physical knots cyclically, with the spare in
    # the same corresponding place. The marks are supplied only to this grader.
    match = dict(zip(isolated_mark, marked, strict=True))
    bins = []
    for age, ((target, _), (sham, _)) in enumerate(zip(target_layers, isolated_layers), 1):
        left = [b for b in target if b.knot in pure[age]]
        right = [b for b in sham if b.knot in solo[age]]
        keep = {frozenset(b.parents): b for b in left}
        assert len(keep) == len(left) == len(right)
        tally = Counter()
        next_match = {}
        for b in right:
            key = frozenset(match[p] for p in b.parents)
            observed = keep[key]
            next_match[b.knot] = observed.knot
            tally[len(observed.fresh), len(b.fresh)] += 1
        assert set(next_match.values()) == pure[age]
        match = next_match
        bins.append({"age": age, "identical_pure_parent_roster": len(left),
                     "fresh_target_vs_solo": [[x, y, count] for (x, y), count in sorted(tally.items())]})
    return bins


def pair_ring_meeting(source, layers, marked, background):
    colors, all_nodes, _ = earlier_births(source, layers, frozenset())
    left, right = map(frozenset, marked)
    assert not left & right
    exclusive_left, exclusive_right = left - set(background), right - set(background)

    def ring_words(ancestry):
        return (bool(ancestry & exclusive_left), bool(ancestry & exclusive_right))

    def explanation(birth):
        return {"knot": birth.knot, "parents": birth.parents, "spent": birth.inputs, "fresh": birth.fresh,
                "parent_source_supports": [sorted(colors[p]) for p in birth.parents],
                "parent_wholly_within_one_ring": [colors[p] <= left or colors[p] <= right
                                                   for p in birth.parents]}

    counts, first, ancestry_only = [], None, None
    for age, (layer, _) in enumerate(layers, 1):
        mixed = [b for b in layer if ring_words(all_nodes[age][b.knot]) == (True, True)]
        opposed = [b for b in mixed if {ring_words(colors[p]) for p in b.parents} >=
                   {(True, False), (False, True)}]
        pure_parent_pairs = [b.knot for b in layer if any(colors[p] <= left for p in b.parents) and
                             any(colors[p] <= right for p in b.parents)]
        assert not pure_parent_pairs
        counts.append({"age": age, "both_exclusive_origins": len(mixed),
                       "fresh_in_mixed_births": sum(len(b.fresh) for b in mixed),
                       "births_joining_two_wholly_pure_parents": len(pure_parent_pairs),
                       "joint_with_opposing_unmixed_parents": len(opposed)})
        if mixed and first is None:
            assert mixed == opposed and all(ring_words(colors[p]) != (True, True)
                                            for b in mixed for p in b.parents)
            first = {"age": age, "cluster_size": age + 1, "earliest_births": [explanation(b) for b in mixed]}
        if len(opposed) < len(mixed) and ancestry_only is None:
            false_meeting = next(b for b in mixed if b not in opposed)
            assert any(ring_words(colors[p]) == (True, True) for p in false_meeting.parents)
            ancestry_only = {"age": age, "example": explanation(false_meeting)}
    return {"by_age": counts, "first": first, "ancestry_only_control": ancestry_only}


def withhold_other_births(source, layers, marks, law):
    _, all_nodes, _ = earlier_births(source, layers, ())
    ring_sets = list(map(frozenset, marks))
    retained = [(tuple(b for b in layer if any(all_nodes[age][b.knot] <= ring for ring in ring_sets)), ())
                for age, (layer, _) in enumerate(layers, 1)]
    return {tag: fixed_map_replay(source, retained, law, order)
            for tag, order in (("earliest_ready", False), ("latest_ready", True))}


def matched_small(law):
    before = ((0, 1, 2), (0, 3, 4))
    coupled = (*before, (3, 5, 6))
    strict = (before[0], (*before[1], 5), (5, 6, 7))
    result = {}
    for name, source in (("two_knots", before), ("three_knots", coupled), ("preserve_old_loose", strict)):
        result[name], _, layers = small_panel(source, law, 5)
        births, multi = layers[0]
        _, graph, loose = incidence(source)
        _, end = witnessed_end(graph, loose)
        assert loose[0] == [1, 2]
        actual = [b for b in births if b.parents == (0,)]
        witness = sorted(set(graph[0]) & set(graph[2])) if len(source) == 3 else []
        assert len(actual) == (2 if not witness else 1)
        assert multi == (((0, 2),) if witness else ())
        assert not witness or not graph.has_edge(0, 2)
        ablated = nx.empty_graph(list(loose))
        assert not multi_groups((), ablated)
        paired_knot = len(source) - 1
        assert len(loose[0]) == len(loose[paired_knot]) == 2
        first = {"pure_A": [{"input": b.inputs[0], "fresh": b.fresh} for b in actual],
                 "multi": list(multi), "actual_shared_witness": witness,
                 "marked_pair": [0, paired_knot], "marked_pair_loose_counts": [len(loose[0]), len(loose[paired_knot])],
                 "marked_pair_ordinary_meeting": graph.has_edge(0, paired_knot),
                 "marked_pair_common_holder": end.has_edge(0, paired_knot),
                 "multi_under_loose_only": [], "all_first_births": [vars(b) for b in births]}
        result[name]["first"] = first
    return result


def full_panel(law, cases):
    result = {"near_competition": matched_small(law)}
    terminal = source_from([(0, 1), (0, 2), (0, 3)], [0, 2, 2, 2])
    result["terminal_star"], _, _ = small_panel(terminal, law, 5, earlier_valid_frames=1)
    supply_covering = result["terminal_star"]["replay"]["earliest_ready"]["supply_covering_events"][0]
    assert supply_covering["parent_count"] == 3
    assert supply_covering["fresh"] == (0 if law == "parity" else 1)
    relay = source_from([(0, 2), (0, 2), (1, 2)], [2, 2, 0])
    result["two_relay_tips"], _, relay_layer = small_panel(relay, law, 8)
    result["two_relay_tips"].update(relay_tips(relay, relay_layer, result["two_relay_tips"]["stages"]))

    ring_types = {"bare5": (archived_case(cases["R0"]), 5),
                  "bare7": (source_from([(i, (i + 1) % 7) for i in range(7)], [2] * 7), 7),
                  "spare5": (archived_case(cases["R1"]), 5)}
    r1_layers = None
    for name, (source, period) in ring_types.items():
        result[name], frames, layers = small_panel(source, law, 8, [frozenset(range(period))],
                                                    cycle_lengths=(period,))
        result[name]["independent_map"] = independent_ring_map(source, layers)
        assert all(x["cyclic_sets"] >= 1 for x in result[name]["stages"])
        if name == "spare5":
            r1_layers = layers
        else:
            assert all(x["part_sizes"] == [period] and x["cyclic_sets"] == 1 for x in result[name]["stages"])
            result[name]["strict_vs_any"] = bare_run_control(frames[0], layers)

    r1 = ring_types["spare5"][0]
    base_mark = tuple(cases["R1"]["roles"]["rings"][0])
    double_rings = {}
    for name, bound in (("T4", 5), ("T8", 6)):
        spec = cases[name]
        source = archived_case(spec)
        marked = [tuple(row) for row in spec["roles"]["rings"]]
        result[name], _, layers = small_panel(source, law, bound, list(map(frozenset, marked)), cycle_lengths=(5,))
        double_rings[name] = (source, layers, marked)
        meeting = pair_ring_meeting(source, layers, marked, spec["roles"]["background"])
        assert meeting["first"]["age"] == (3 if name == "T4" else 5)
        assert len(meeting["first"]["earliest_births"]) == 4
        result[name]["meeting"] = meeting
        result[name]["keep_only_both_pure_families_in_fixed_map"] = withhold_other_births(source, layers, marked, law)
        result[name]["pure_vs_isolated_ring"] = [paired_pure(source, layers, ring, r1, r1_layers, base_mark)
                                                for ring in marked]
        one_at_a_time, including_background, matched_replays = [], [], []
        for which in (0, 1):
            solo, solo_mark, retained = solo_on_background(spec, which)
            if which == 0:
                assert solo == archived_case(cases["J1"])
            certify_source(solo, law)
            _, solo_layers = trajectory(solo, law, bound)
            matched_replays.append(fixed_map_replay(solo, solo_layers, law, later_first=False))
            assert len(solo_mark) == 5
            one_at_a_time.append(paired_pure(source, layers, marked[which], solo, solo_layers, solo_mark))
            including_background.append(paired_pure(source, layers, retained, solo, solo_layers,
                                                     tuple(range(len(retained)))))
        result[name]["pure_vs_matched_one_ring_on_background"] = one_at_a_time
        result[name]["all_births_avoiding_other_ring_vs_matched_one_ring"] = including_background
        result[name]["matched_one_ring_lawfulness_replays"] = matched_replays
    left, right = double_rings["T4"], double_rings["T8"]
    result["T4_vs_T8_matched_pure"] = [paired_pure(*left[:2], lmark, *right[:2], rmark)
                                      for lmark, rmark in zip(left[2], right[2], strict=True)]
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    cases = {case["id"]: case for case in json.loads((WORLD / "inputs.json").read_text())["cases"]}
    data = {"design": "140ecfc789f6bb2d6d5e5282de8c319b2929ceed",
            "lawful_at_source_and_all_completed_births": True,
            "laws": {law: full_panel(law, cases) for law in ("parity", "nae")}}
    args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
