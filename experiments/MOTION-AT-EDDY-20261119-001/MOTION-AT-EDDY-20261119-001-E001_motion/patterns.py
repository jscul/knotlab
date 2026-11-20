"""Exact bounded catalogue and literal transport controls for size-two stages."""

from argparse import ArgumentParser
from collections import Counter, defaultdict, deque
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
from random import Random
from tempfile import NamedTemporaryFile

from motion_stage import (
    HERE, INPUTS, ROOT, STAGES, OVERLAP_WORK_LIMIT, SHORT_CIRCUIT_LIMIT,
    MotionStage, growth_engine, load_case_record, load_marks, load_stage, support_neighbors,
)


OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "patterns.json"
CASES = ("B", "J0", "J1", "J2", "T4", "T8", "C1", "R0", "R1", "R2",
         "B81", "J81", "T81", "R31")
LITERAL_STATE_BITS = 16


def shape_counts(stage):
    touching = defaultdict(list)
    pairs = stage.short_circuits[2]
    for i, pair in enumerate(pairs):
        for v in set().union(*(stage.owners[bit] for bit in pair)):
            touching[v].append(i)
    assert sum(comb(len(ids), 2) for ids in touching.values()) <= OVERLAP_WORK_LIMIT
    composite = {
        pairs[i] | pairs[j] for ids in touching.values() for i, j in combinations(ids, 2)
        if not pairs[i] & pairs[j]
    }
    for support in composite:
        assert stage.allowed_change(support)
    return {
        "simple_by_size": {
            str(k): {"ordinary": sum(not (p & stage.loose) for p in rows),
                     "with_current_loose": sum(bool(p & stage.loose) for p in rows)}
            for k, rows in stage.short_circuits.items()
        },
        "composite_size_four": {"ordinary": sum(not (p & stage.loose) for p in composite),
                                "with_current_loose": sum(bool(p & stage.loose) for p in composite)},
    }


def brute_controls():
    """All allowed rows on small multigraphs and independently built physical steps."""
    fixtures = [
        [(0, 3, 4), (0, 1, 5), (1, 2), (2, 3)],
        [(0, 1, 2, 3), (0, 1, 4), (2, 3, 5)],
        [(0, 1), (2, 3)],
    ]
    rng = Random(20261119)
    for i in range(36):
        n = 2 + i % 4
        rows = [[] for _ in range(n)]
        for bit in range(5 + i % 6):
            for v in rng.sample(range(n), 1 + rng.randrange(2)):
                rows[v].append(bit)
        fixtures.append(rows)
    grades = 0
    shape_checks = 0
    for rows in fixtures:
        stage = MotionStage(rows)
        names = sorted(stage.owners)
        literal = [frozenset(bit for i, bit in enumerate(names) if mask & (1 << i))
                   for mask in range(1 << len(names))]
        allowed = [state for state in literal if all(len(state & set(row)) % 2 == 0 for row in rows)]
        assert all(stage.allowed_change(state) == (state in allowed) for state in literal)
        allowed_set = set(allowed)
        measured_shapes = shape_counts(stage)
        expected_shapes = Counter()
        for small in allowed:
            if not 2 <= len(small) <= 4:
                continue
            seen = {min(small)}
            active = list(seen)
            for a in active:
                fresh = {b for b in small - seen if any(a in row and b in row for row in rows)}
                active.extend(fresh)
                seen |= fresh
            if seen != small:
                continue
            proper = any(frozenset(row) in allowed_set for k in range(1, len(small))
                         for row in combinations(sorted(small), k))
            bucket = "with_current_loose" if small & stage.loose else "ordinary"
            expected_shapes["composite" if proper else str(len(small)), bucket] += 1
            shape_checks += 1
        assert all(measured_shapes["simple_by_size"][k][bucket] == expected_shapes[k, bucket]
                   for k in ("2", "3", "4") for bucket in ("ordinary", "with_current_loose"))
        assert all(measured_shapes["composite_size_four"][bucket] == expected_shapes["composite", bucket]
                   for bucket in ("ordinary", "with_current_loose"))
        # Floyd's recurrence on the direct physical co-holder relation.
        far = len(names) + 1
        distance = {(a, b): 0 if a == b else 1 if any(a in r and b in r for r in rows) else far
                    for a in names for b in names}
        for middle in names:
            for a in names:
                for b in names:
                    distance[a, b] = min(distance[a, b], distance[a, middle] + distance[middle, b])
        for a in names:
            assert stage.distances_from([a]) == {b: distance[a, b] for b in names if distance[a, b] < far}
            for pinned in (False, True):
                replies = [row for row in allowed if a in row and not (pinned and row & (stage.loose - {a}))]
                least = min(map(len, replies), default=None)
                small = [row for row in replies if len(row) == least]
                ends = [max(distance[a, b] for b in row) for row in small]
                observed = stage.minimum_response(a, pinned_loose=pinned)
                assert observed.minimum_size == least and observed.count == len(small)
                assert observed.outside_count == sum(bool(row & stage.loose) for row in small)
                assert observed.least_reach == (min(ends) if ends else None)
                assert observed.greatest_reach == (max(ends) if ends else None)
                if least is not None and least <= 4:
                    assert set(observed.supports) == set(small)
                grades += 1
    stage = MotionStage(fixtures[0])
    assert stage.distances_from([4])[5] == 2
    return {"small_incidence_fixtures": len(fixtures), "target_policy_comparisons": grades,
            "connected_short_changes_independently_classified": shape_checks,
            "exterior_shortcut_control": {"distinct_loose_co_knotted_steps": 2,
                                          "free_shared_minimum_size": 3, "pinned_shared_minimum_size": 4}}


def stage_marks(stage, mark, pinned, indices=None):
    reading = stage.minimum_response(mark, pinned_loose=pinned)
    answer = {
        "size": reading.minimum_size, "ties": reading.count,
        "ties_with_current_loose": reading.outside_count,
        "physical_reach": [reading.least_reach, reading.greatest_reach],
        "listed_all_supports": reading.listed_all_supports,
    }
    if indices is not None:
        answer["supports"] = sorted(indices[row] for row in reading.supports)
    return answer


def ordinary_wedges(record, stage, quads):
    """Index every ordinary response by its two original shared distinctions."""
    source = record["stages"]["0"]["stars"]
    neighbors = [dict() for _ in source]
    for d, owners in MotionStage(source).owners.items():
        if len(owners) == 2:
            u, v = owners
            assert v not in neighbors[u]
            neighbors[u][v] = neighbors[v][u] = d
    paths = {}
    offset = {row: i for i, row in enumerate(quads)}
    seen = set()
    age_one = record["stages"]["1"]
    for child, parents in age_one["parent_sets"].items():
        if len(parents) == 1:
            continue
        u, v = parents
        common, = neighbors[u].keys() & neighbors[v].keys()
        key = tuple(sorted((neighbors[u][common], neighbors[v][common])))
        response = frozenset((*key, *(d for _, d in age_one["consumed"][child])))
        assert len(response) == 4 and stage.allowed_change(response) and response in offset
        assert key not in paths
        seen.add(response)
        paths[key] = offset[response]
    assert seen == set(quads)
    assert len(paths) == sum(comb(len(row), 2) for row in neighbors)
    return paths


def display_shift(stage, quads, adjacency, windows, edge_names, landmarks, cyclic):
    pairs = list(zip(edge_names, edge_names[1:]))
    if cyclic:
        pairs.append((edge_names[-1], edge_names[0]))
    ids = [windows[tuple(sorted(pair))] for pair in pairs]
    intervals = list(zip(ids, ids[1:]))
    if cyclic:
        intervals.append((ids[-1], ids[0]))
    for a, b in intervals:
        assert b in adjacency[a] and len(quads[a] & quads[b]) == 1
        change = quads[a] ^ quads[b]
        assert len(change) == 6 and stage.allowed_change(change)
    distance = [stage.distances_from([mark]) for mark in landmarks]
    return {
        "ordered_support_ids": ids,
        "shared_mark_per_step": [next(iter(quads[a] & quads[b])) for a,b in intervals],
        "fixed_landmarks": landmarks,
        "minimum_support_steps_to_landmarks": [
            [min(row[d] for d in quads[i]) for row in distance] for i in ids
        ],
    }


def renaming_control(stage, quads, adjacency, marks):
    rng = Random(54157)
    order = list(range(len(stage.stars)))
    rng.shuffle(order)
    values = [17 + 3 * i for i in range(len(stage.owners))]
    rng.shuffle(values)
    names = dict(zip(stage.owners, values, strict=True))
    renamed = MotionStage([[names[bit] for bit in stage.stars[v]] for v in order])
    translated = {frozenset(names[d] for d in row) for row in quads}
    assert translated == set(renamed.ordinary_quads())
    new = renamed.ordinary_quads()
    index = {row: i for i, row in enumerate(new)}
    after = support_neighbors(new)
    mapped = [index[frozenset(names[d] for d in row)] for row in quads]
    assert all({mapped[j] for j in ns} == set(after[mapped[i]]) for i, ns in enumerate(adjacency))
    for bit in stage.owners:
        for policy in (False, True):
            first = stage.minimum_response(bit, pinned_loose=policy)
            second = renamed.minimum_response(names[bit], pinned_loose=policy)
            assert stage_marks(stage, bit, policy) == stage_marks(renamed, names[bit], policy)
            assert {frozenset(names[d] for d in row) for row in first.supports} == set(second.supports)
    for mark in marks:
        assert {names[d]: r for d, r in stage.distances_from([mark]).items()} == renamed.distances_from([names[mark]])


def ring_rotation(record, role, quads):
    ring = role["rings"][0]
    named = {u: v for u, v in zip(ring, ring[1:] + ring[:1], strict=True)}
    bits = {a: b for a, b in zip(role["ring_edges"][0], role["ring_edges"][0][1:] + role["ring_edges"][0][:1],
                                strict=True)}
    current = record["stages"]["1"]
    by_parents = {tuple(sorted(row)): int(j) for j, row in current["parent_sets"].items()}
    for j, parents in current["parent_sets"].items():
        child = by_parents[tuple(sorted(named[p] for p in parents))]
        named[int(j)] = child
        take = dict(current["consumed"][str(child)])
        bits.update((d, take[named[p]]) for p, d in current["consumed"][j])
        bits.update(zip(sorted(current["fresh"][j]), sorted(current["fresh"][str(child)]), strict=True))
    stage = MotionStage(current["stars"])
    assert len(set(named.values())) == len(named) == len(stage.stars)
    assert len(set(bits.values())) == len(bits) == len(stage.owners)
    for v, row in enumerate(stage.stars):
        assert {bits[d] for d in row} == set(stage.stars[named[v]])
    assert {frozenset(bits[d] for d in row) for row in quads} == set(quads)
    return {"junction_permutation": sorted(named.items()), "distinction_permutation": sorted(bits.items())}


def row_basis(rows):
    independent = {}
    for value in rows:
        while value:
            p = value.bit_length() - 1
            if p not in independent:
                independent[p] = value
                break
            value ^= independent[p]
    return independent


def kernel(rows, coordinates):
    pivots = row_basis(row & coordinates for row in rows)
    free = coordinates ^ sum(1 << p for p in pivots)
    order = sorted(pivots)
    independent = []
    while free:
        value = free & -free
        free ^= value
        for p in order:
            if (pivots[p] & value).bit_count() % 2:
                value |= 1 << p
        independent.append(value)
    return independent


def span(generators):
    assignments = [0]
    for value in generators:
        assignments.extend([x ^ value for x in assignments])
    return assignments


def occupancy_report(stage, quads, source_shared):
    names = {bit: 1 << i for i, bit in enumerate(stage.owners)}
    equation = [sum(names[d] for d in row) for row in stage.stars]
    old = sum(names[d] for d in source_shared)
    occupied = [sum(names[d] for d in row) for row in quads]
    private = []
    for row in quads:
        a, b = sorted(row - source_shared)
        youngest, = set(stage.owners[a]) & set(stage.owners[b])
        assert set(stage.stars[youngest]) - stage.loose == {a, b}
        private.append((names[a], names[b]))
    assert all(len(pair) == 2 for pair in private)
    assert len(set(d for pair in private for d in pair)) == 2 * len(quads)
    assert all((a | b) & pulse == a | b
               for (a, b), pulse in zip(private, occupied, strict=True))
    assert all(sum(bool(a & pulse) for pulse in occupied) == 1 and
               sum(bool(b & pulse) for pulse in occupied) == 1 for a, b in private)

    def relative(value, reference=0):
        difference = value ^ reference
        mask = reconstructed = 0
        for i, ((a, b), pulse) in enumerate(zip(private, occupied, strict=True)):
            assert bool(difference & a) == bool(difference & b)
            if difference & a:
                mask |= 1 << i
                reconstructed ^= pulse
        return mask, reconstructed

    all_bits = sum(names.values())
    closed = all_bits ^ sum(names[d] for d in stage.loose)
    closed_basis = kernel(equation, closed)
    old_basis = kernel(equation, old)
    dim_free = len(names) - len(row_basis(equation))
    assert len(row_basis(occupied + old_basis)) == len(occupied) + len(old_basis) == len(closed_basis)
    assert all((value & row).bit_count() % 2 == 0 for row in equation for value in occupied)
    # An independent recoding of values by a codeword transports the reference too.
    shift = occupied[0]
    assert relative(shift, 0) == relative(0, shift) == (1, shift)
    assert relative(shift)[0] != relative(0)[0]

    small_weight = {0: {0: 1}, 1: {4: len(quads)}}
    small_weight[2] = Counter((x ^ y).bit_count() for x, y in combinations(occupied, 2))
    small_weight[3] = Counter((x ^ y ^ z).bit_count() for x, y, z in combinations(occupied, 3))
    literal = {}
    for label, dimension, basis in (("closed", len(closed_basis), closed_basis),
                                    ("free", dim_free, None)):
        if dimension > LITERAL_STATE_BITS:
            continue
        assignments = span(basis if basis is not None else kernel(equation, all_bits))
        assert len(assignments) == len(set(assignments)) == 1 << dimension
        assert all(not any((x & row).bit_count() % 2 for row in equation) for x in assignments)
        literal[label] = {"all_allowed_states": len(assignments),
                          "weight_histogram": Counter(x.bit_count() for x in assignments)}
        if label == "closed":
            fibers = Counter()
            for x in assignments:
                locations, reconstructed = relative(x)
                rest = x ^ reconstructed
                assert rest & ~old == 0
                fibers[locations] += 1
            assert len(fibers) == 1 << len(occupied)
            assert set(fibers.values()) == {1 << len(old_basis)}
            literal[label]["occupancy_fibers"] = len(fibers)
            literal[label]["allowed_states_per_occupancy"] = 1 << len(old_basis)

    minimum_free = stage.short_circuits[2][0]
    minimum_closed = quads[0]
    assert all(row & stage.loose for k in (2, 3) for row in stage.short_circuits[k])
    residue = [bit for bit, value in names.items() if old_basis and value & old_basis[0]]
    return {
        "ordinary_occupancy_dimension": len(occupied), "closed_dimension": len(closed_basis),
        "free_dimension": dim_free, "old_cycle_dimension": len(old_basis),
        "ordinary_occupancy_states": 1 << len(occupied),
        "closed_allowed_states": 1 << len(closed_basis), "free_allowed_states": 1 << dim_free,
        "closed_states_per_occupancy": 1 << len(old_basis),
        "one_old_cycle_at_zero_occupancy": residue,
        "physical_weight_by_occupied_slots_through_three": small_weight,
        "complete_literal_state_replays": literal,
        "minimum_free": {"size": len(minimum_free), "support": sorted(minimum_free)},
        "minimum_closed": {"size": len(minimum_closed), "support": sorted(minimum_closed)},
        "reference_control": {
            "same_relative_occupancy_when_state_and_reference_recoded": True,
            "allowed_value_swap_changing_raw_zero_occupancy": sorted(minimum_closed),
        },
    }


def published_pulse_one_size_past():
    prior_file = STAGES.with_name("adjacent_changes.json")
    prior = json.loads(prior_file.read_text())
    last_size = max(prior["physical_cluster_sizes_checked"])
    assert last_size == 7 and prior["case"] == "J1"
    archived = load_case_record("J1")
    # The first omitted layer had an exact size forecast in EDDY-WORLD.
    cap = {"junctions": 2048, "distinctions": 12_000}
    extension = growth_engine().grow_case(archived["input"], last_size, cap)
    assert all(after == extension["stages"][age] for age, after in archived["stages"].items())
    new = extension["stages"][str(last_size)]
    stage = MotionStage(new["stars"])
    assert (new["junction_count"], new["distinction_count"]) == (1784, 10767)
    for support in prior["four_distinction_states"] + prior["successive_state_changes"]:
        assert stage.allowed_change(support) and not set(support) & stage.loose
    physical_neighbors = [set(row) - {stage.outside} for row in stage.bundles[:-1]]

    def holder_steps(mark):
        distances = {mark: 0}
        pending = deque([mark])
        while pending:
            u = pending.popleft()
            for v in physical_neighbors[u] - distances.keys():
                distances[v] = distances[u] + 1
                pending.append(v)
        return distances

    centers = [holder_steps(mark) for mark in (0, 16)]
    measured = [[min(center[v] for d in support for v in stage.owners[d]) for center in centers]
                for support in prior["four_distinction_states"]]
    assert measured == prior["junction_steps_to_landmarks"]
    result = {"case": "J1", "prior_last_size": last_size, "one_size_past": last_size + 1,
              "caps": cap, "junctions": new["junction_count"], "distinctions": new["distinction_count"],
              "three_allowed_supports": prior["four_distinction_states"],
              "two_allowed_six_distinction_changes": prior["successive_state_changes"],
              "holder_steps_to_fixed_source_ends": measured}
    return result


def measure(case):
    rec = load_case_record(case)
    stage = load_stage(case)
    marks = load_marks(case)
    assert rec["qualification"]["canonical"] and rec["qualification"]["DOUBLE_IDENT"]["in_class"]
    quads = stage.ordinary_quads()
    assert quads == stage.ordinary_quads(pinned_loose=True)
    assert all(stage.minimum_response(d, pinned_loose=policy).minimum_size == 4
               for row in quads for d in row for policy in (False, True))
    adjacency = support_neighbors(quads)
    windows = ordinary_wedges(rec, stage, quads)
    assert all((j in adjacency[i]) == (len(a & b) == 1)
               for (i, a), (j, b) in combinations(enumerate(quads), 2))
    limits = shape_counts(stage)
    least = {row for d in stage.owners for policy in (False, True)
             for row in stage.minimum_response(d, pinned_loose=policy).supports}
    listed = sorted(least, key=lambda row: (len(row), sorted(row)))
    indices = {row: i for i, row in enumerate(listed)}
    outcomes = []
    for d in stage.owners:
        population = ("original_shared" if d in marks["source_shared"] else
                      "original_loose_consumed" if d in marks["source_loose"] else "current_loose")
        if population == "current_loose":
            assert d in stage.loose
        outcomes.append({"mark": d, "population": population, "free": stage_marks(stage, d, False, indices),
                         "pinned": stage_marks(stage, d, True, indices)})
    grades = {}
    if marks["anchors"]:
        grades["path"] = display_shift(stage, quads, adjacency, windows, marks["anchors"],
                                       marks["path_landmarks"], cyclic=False)
        values = grades["path"]["minimum_support_steps_to_landmarks"]
        assert values == [[i, len(values) - i - 1] for i in range(len(values))]
    grades["rings"] = [display_shift(stage, quads, adjacency, windows, edges, landmarks, cyclic=True)
                       for edges, landmarks in zip(marks["ring_edges"], marks["ring_landmarks"], strict=True)]
    landmarks = [*marks["path_landmarks"], *(d for row in marks["ring_landmarks"] for d in row)]
    renaming_control(stage, quads, adjacency, landmarks)
    if case in ("R0", "R31"):
        grades["bare_ring_rotation"] = ring_rotation(rec, marks, quads)
    summary = defaultdict(Counter)
    for row in outcomes:
        for policy in ("free", "pinned"):
            size = row[policy]["size"]
            summary[row["population"] + "/" + policy][str(size) if size is not None else "infinity"] += 1
    return {
        "age": 1, "junctions": len(stage.stars), "distinctions": len(stage.owners),
        "stage_support_sha256": sha256(json.dumps(stage.stars).encode()).hexdigest(),
        "short_connected_shapes": limits, "ordinary_quads": list(map(sorted, quads)),
        "ordinary_quad_neighbors": adjacency,
        "ordinary_quad_overlap_edges": sum(map(len, adjacency)) // 2,
        "all_quads_minimum_for_each_mark_both_policies": True,
        "literal_short_minimum_supports": list(map(sorted, listed)), "target_profiles": outcomes,
        "summary": dict(summary), "translation_controls": grades, "full_renaming_check": True,
        "occupancy": occupancy_report(stage, quads, marks["source_shared"]),
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    controls = brute_controls()
    if args.controls_only:
        print(json.dumps(controls, indent=2))
        return
    records = {
        "archived_stage_sha256": sha256(STAGES.read_bytes()).hexdigest(),
        "frozen_inputs_sha256": sha256(INPUTS.read_bytes()).hexdigest(),
        "per_cardinality_catalogue_limit": SHORT_CIRCUIT_LIMIT,
        "overlap_work_limit": OVERLAP_WORK_LIMIT,
        "literal_state_dimension_limit": LITERAL_STATE_BITS,
        "controls": controls, "cases": {case: measure(case) for case in CASES},
        "published_pulse_one_size_past": published_pulse_one_size_past(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", dir=args.output.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            json.dump(records, stream, separators=(",", ":"))
            print(file=stream)
            stream.flush()
            temporary.replace(args.output)
        finally:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
