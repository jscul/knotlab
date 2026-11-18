"""Audit the four hidden charts, permanent betweenness, and the first round after alignment."""

from collections import Counter
from itertools import combinations
from random import Random
import json

import check_construction as construction
import check_probe as probe
import check_seed as seed


def nearest_graph(rows):
    """Two originals are neighbors iff their betweenness interval has size two."""
    graph = set()
    for a, b in combinations(range(8), 2):
        equal = [row for row in rows if seed.bit(row, a) == seed.bit(row, b)]
        interval = {c for c in range(8) if all(seed.bit(row, a) == seed.bit(row, c)
                                              for row in equal)}
        if len(interval) == 2:
            graph.add((a, b))
    return graph


def translated_seeds():
    rows = seed.seed_rows()[0]
    cuts = [sum(int(bool(v & axis)) << v for v in range(8)) for axis in seed.AXES]
    graphs = set()
    directions = []
    for flip in [0, *cuts]:
        translated = frozenset(row ^ flip for row in rows)
        edges = nearest_graph(translated)
        old = tuple(tuple(seed.bit(row, v) for v in range(8)) for row in sorted(translated))
        table, _ = probe.threshold_two(probe.ProbeProjection(old, probe.PAIRS), probe.WIDTH)
        recovered = probe.recover_cube(table)
        observed = {(a, b) for a, b in combinations(sorted(recovered), 2) if b in recovered[a]}
        assert observed == edges and len(edges) == 12
        displacement = sorted({a ^ b for a, b in edges})
        assert len(displacement) == 3
        directions.append(displacement)
        graphs.add(frozenset(edges))
    assert len(graphs) == 4
    assert {tuple(x) for x in directions} == set(combinations([1, 2, 4, 7], 3))
    return directions


def lasting_betweennesses():
    aligned = construction.load_source("bootstrap_scope_aligned", construction.ALIGNED / "check_aligned.py")
    data = aligned.short_supports(4)
    marked = aligned.mask_of(data.model.mark_bits)
    census = Counter()
    sizes = {s.bit_count() for s in data.mixed}
    assert min(sizes) == 3
    ternary = [support for support in data.mixed if support.bit_count() == 3]
    for support in ternary:
        rows = aligned.projected_rows(data.model, support)
        middles = []
        for middle in range(3):
            left, right = (j for j in range(3) if j != middle)
            if all(seed.bit(row, left) != seed.bit(row, right)
                   or seed.bit(row, middle) == seed.bit(row, left) for row in rows):
                middles.append(middle)
        census[(support & ~marked == 0, len(rows), len(middles))] += 1
    assert census == {(True, 6, 1): 48, (False, 4, 0): 3}
    return {"ternary_projections": 105 * 104 * 103 // 6,
            "full_ternary_projections": 105 * 104 * 103 // 6 - len(ternary),
            "old_only_six_rows_one_middle": 48, "parity_four_rows_no_middle": 3,
            "one_and_two_bit_projections_all_free": True}


def round_after_alignment():
    """Probe the y-translated seed and apply a decoded complete round on its actual bits."""
    old_ids = tuple(range(8))
    old_rows = tuple(tuple(value ^ point[1] for value, point in zip(row, probe.POSITIONS, strict=True))
                     for row in probe.literal_rows())
    graph, _ = probe.threshold_two(probe.ProbeProjection(old_rows, probe.PAIRS), probe.WIDTH)
    adjacency = probe.recover_cube(graph)
    frame_index = 37
    chart = construction.cube_frames(adjacency)[frame_index]
    assert construction.cut_rows_in_chart(chart, old_ids) == set(old_rows)
    old_at = {point: bit for bit, point in chart.items()}

    growth = construction.load_source("bootstrap_scope_growth", construction.GROWTH / "check.py")
    aligned = construction.load_source("bootstrap_scope_aligned", construction.ALIGNED / "check_aligned.py")
    reader = construction.load_source("bootstrap_scope_reader", construction.ALIGNED / "read_frontier.py")
    target = construction.locally_generated_target(growth)
    moves = construction.compile_alignment(adjacency, chart, target)
    checks, _ = construction.audit_replay(moves, old_ids, old_rows, growth, target)
    stage = aligned.short_supports(4)
    physical = construction.bind_aligned_model(moves, checks, old_ids, old_rows, stage.model, aligned)
    names = list(physical)
    permutation_seed = 1597
    Random(permutation_seed).shuffle(names)
    indices = {bit: i for i, bit in enumerate(names)}
    supports = {sum(1 << indices[physical[i]] for i in aligned.bits(mask)) for mask in stage.mixed}
    decoded = reader.read_frontier(reader.sparse_rows(len(names), supports))
    available = {group: list(group) for group in decoded["triplets"]}
    groups = decoded["groups"]
    assert Counter(map(len, groups)) == {1: 3, 2: 12, 3: 6}

    # The reader chooses each join above. The independent I5 model grades its
    # parent set and supplies a coordinate name only after the move is legal.
    next_stage = aligned.short_supports(5)
    arrivals = {}
    for point in next_stage.model.vertices:
        if sum(point) == 5:
            parents = frozenset(point[:i] + (v - 1,) + point[i + 1:]
                                for i, v in enumerate(point) if v)
            arrivals[parents] = point
    assert len(arrivals) == len(groups) == 21
    owners, _ = growth.incidence(checks)
    fresh_at = {}
    for number, group in enumerate(reversed(groups)):
        inputs = tuple(names[available[parent].pop()] for parent in group)
        fresh = tuple(f"after-alignment-{number}-{i}" for i in range(3))
        assert growth.legal_local_move(checks, inputs, fresh)
        point = arrivals.pop(frozenset(owners[bit][0] for bit in inputs))
        checks[point] = inputs + fresh
        fresh_at[point] = fresh
    assert not arrivals and not any(available.values())

    # Bind every resulting incidence: internal wires have a unique pair of
    # holders; the only loose wires are the three fresh outputs of each arrival.
    model = next_stage.model
    assert set(checks) == set(model.vertices)
    labels = []
    for point, axis in model.wires:
        neighbor = point[:axis] + (point[axis] + 1,) + point[axis + 1:]
        if neighbor in checks:
            bit, = set(checks[point]) & set(checks[neighbor])
        else:
            bit = fresh_at[point][axis]
        labels.append(bit)
    assert len(labels) == len(set(labels)) == 168 and set(physical) <= set(labels)
    for point, star in zip(model.vertices, model.stars, strict=True):
        assert {labels[i] for i in aligned.bits(star)} == set(checks[point])
    for i in model.mark_bits:
        assert labels[i] == old_at[model.wires[i][0]]

    index = {bit: i for i, bit in enumerate(labels)}
    equations = growth.encode(checks, index)
    rank = growth.binary_rank(equations)
    assert rank == len(checks) == 56
    assert not growth.projected_equations(equations, sum(1 << index[bit] for bit in old_ids))
    state_count = len(old_rows) << (len(labels) - rank - len(old_ids))
    assert state_count == 2 ** 107

    following = reader.read_frontier(reader.sparse_rows(len(labels), next_stage.mixed))
    loose = growth.loose_ports(growth.incidence(checks)[0])
    prescribed, _ = growth.parent_groups(checks)
    expected = {tuple(sorted(tuple(sorted(index[bit] for bit in loose[p])) for p in group))
                for group in prescribed}
    assert len(expected) == len(prescribed) and tuple(sorted(expected)) == following["groups"]
    counts = dict(sorted(Counter(map(len, following["groups"])).items()))
    assert counts == {1: 3, 2: 15, 3: 10}
    return {"seed_translation": "y", "frame_index": frame_index, "old_origin_id": old_at[(0, 0, 0)],
            "I4_table_permutation_seed": permutation_seed, "executed_I4_joins": len(groups),
            "I4_bits_retained": len(physical), "I5_bits": len(labels), "I5_junctions": len(checks),
            "original_ids_at_their_exact_outputs": len(model.mark_bits),
            "original_rows_preserved": len(old_rows), "I5_states": state_count,
            "I5_next_groups_by_parent_count": counts}


if __name__ == "__main__":
    print(json.dumps({"old_neighbor_displacements_after_flip_0_x_y_z": translated_seeds(),
                      "persistent_betweenness_at_I4": lasting_betweennesses(),
                      "one_round_after_alignment": round_after_alignment()},
                     indent=2, sort_keys=True))
