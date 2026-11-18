"""Verify the variable identifications and observation boundaries of the three readers."""

from collections import Counter
from functools import cache
import json
from random import Random

import check_block as block
import check_start as start
import check_tail as tail


def capped(matrix, cutoff):
    return tuple(tuple(cutoff + 1 if value is None else min(value, cutoff + 1)
                       for value in row) for row in matrix)


def invariant(matrix, cutoff):
    return tail.observe(capped(matrix, cutoff))[0]


def start_command(operation, operands):
    if operation == "root":
        return "gate", operands[0], ()
    if operation == "second":
        return "gate", operands[1], (operands[0],)
    if operation == "configure_two":
        return "bulk", *sorted((operands[:2], operands[2:]))
    if operation == "erase":
        return "drop", operands
    assert operation == "add"
    return "add", operands


@cache
def early_policy():
    classes = {}
    for matrix, operation, operands in start.bulk_observations(full=False):
        if operation != "handoff":
            short = capped(matrix, 2)
            signature = invariant(short, 2)
            key = block.key_for(short, start_command(operation, operands))
            assert classes.setdefault(signature, key) == key
    return classes


@cache
def late_policy():
    policy = {}
    for points, probes, kind, target, _, _ in tail.trace():
        ids, matrix = tail.current_table(points, probes)
        signature, shades = tail.observe(matrix)
        policy[signature] = kind, tuple(sorted(shades[ids.index(bit)] for bit in target))
    terminal = tail.current_table(frozenset(tail.MODEL.vertices), ())[1]
    return policy, invariant(terminal, 5)


def read_current(matrix):
    """Return every permitted command on these row indices from this table alone."""
    key = early_policy().get(invariant(matrix, 2))
    if key is not None:
        return block.commands_from(capped(matrix, 2), key)
    middle_moves = block.read_actions(capped(matrix, 4))
    if middle_moves:
        return middle_moves
    policy, terminal = late_policy()
    short = capped(matrix, 5)
    if invariant(short, 5) == terminal:
        return {("halt",)}
    kind, choices = tail.read(short, policy)
    operation = {"join": "ordinary", "probe": "add", "erase": "drop"}[kind]
    return {(operation, bits) for bits in choices}


def rename_command(command, names):
    kind, *args = command
    if kind == "gate":
        return kind, names[args[0]], tuple(sorted(names[i] for i in args[1]))
    pairs = [tuple(sorted(names[i] for i in arg)) for arg in args]
    return (kind, *(sorted(pairs) if kind == "bulk" else pairs))


def check_relabeling(matrix, seed):
    choices = read_current(matrix)
    order = list(range(len(matrix)))
    Random(seed).shuffle(order)
    shuffled = tuple(tuple(matrix[i][j] for j in order) for i in order)
    assert {rename_command(move, order) for move in read_current(shuffled)} == choices


def block_wire_identities():
    """Map each block index to its permanent wire in the completed source."""
    sites = ("000", "100", "010", "110", "001", "101", "011", "111")
    wires = [tail.at(site) for site in sites]
    # The first fresh port goes in the indicated direction. At each source
    # its second fresh port goes in the other of the two lateral directions.
    first_axes = (0, 1, 0, 0, 0, 1, 0, 0)
    for i, (site, axis) in enumerate(zip(sites, first_axes, strict=True)):
        wires.extend((tail.at(site, axis), tail.at(site, 1-axis)))
        original, incoming = block.GATES[i]
        assert wires[original] == tail.at(site)
        assert {wires[bit] for bit in incoming} == set(tail.inputs(tail.site(site)))
    return wires


def verify_block_entry():
    wires = block_wire_identities()
    tests = tuple(tuple(wires.index(bit) for bit in probe)
                  for probe in (tail.PORT_PROBE, tail.FACE_PROBE))
    end_ids = [tail.N + i for i in range(4)]
    present, full = tail.current_table(tail.SITE_BLOCK, (tail.PORT_PROBE, tail.FACE_PROBE))
    order = [present.index(bit) for bit in wires + end_ids]
    transported = tuple(tuple(full[i][j] for j in order) for i in order)
    exact_block = block.table(8, tests, limit=4)
    assert capped(transported, 4) == exact_block
    return {"retained_block_middles": tests,
            "compared_entries": len(wires + end_ids) * (len(wires + end_ids) - 1) // 2,
            "entry_distance_histogram": dict(sorted(Counter(
                exact_block[i][j] for j in range(28) for i in range(j)).items())),
            "larger_distances_pooled_at": 5}


def verify_composition():
    early = start.bulk_observations(full=True)
    inherited = start.load_predecessor()
    # Color and distance descriptions used by the one-piece reader must give
    # precisely the same simultaneous operands as the exact prefix orbit.
    for matrix, operation, operands in early:
        if operation == "handoff":
            continue
        short = capped(matrix, 2)
        observation = inherited.make_observation(short, (0,) * len(short))
        orbit = start.move_orbit((operation, operands), observation,
                                 tuple(inherited.quotient_maps(observation, observation)))
        expected = {start_command(kind, names) for kind, names in orbit}
        assert read_current(matrix) == expected

    startup_signatures = {invariant(matrix, 2) for matrix, op, _ in early if op != "handoff"}
    clean_second = block.table(2)
    handoffs = [matrix for matrix, op, _ in early if op == "handoff"]
    assert handoffs and all(invariant(matrix, 4) == invariant(clean_second, 4)
                            for matrix in handoffs)
    assert invariant(clean_second, 2) not in startup_signatures

    # A rule can recognize its part of the construction on the present matrix.
    # The first reader uses distance two, the block reader distances through
    # four, and the tail distances through five. No phase counter is supplied.
    middle = block.atlas()
    middle_signatures = {invariant(matrix, 4) for matrix, _ in middle}
    assert all(invariant(matrix, 2) not in startup_signatures for matrix, _ in middle)
    assert invariant(clean_second, 4) in middle_signatures
    for _, _, matrix, moves in block.reachable_templates():
        if moves:
            assert read_current(matrix) == moves
    late = []
    for points, probes, kind, target, allowed, _ in tail.trace():
        ids, matrix = tail.current_table(points, probes)
        operation = {"join": "ordinary", "probe": "add", "erase": "drop"}[kind]
        lifted = {tuple(sorted(ids[i] for i in operands))
                  for name, operands in read_current(matrix) if name == operation}
        assert tuple(sorted(target)) in lifted and lifted <= allowed
        late.append(matrix)
    terminal = tail.current_table(frozenset(tail.MODEL.vertices), ())[1]
    for matrix in late + [terminal]:
        assert invariant(matrix, 2) not in startup_signatures
        assert invariant(matrix, 4) not in middle_signatures
    late_signatures = {invariant(matrix, 5) for matrix in late}
    assert len(late_signatures) == len(late) == 33
    assert invariant(terminal, 5) not in late_signatures
    assert len(terminal) == 105
    assert read_current(terminal) == {("halt",)}
    cases = ([matrix for matrix, _, _ in early]
             + [matrix for _, _, matrix, moves in block.reachable_templates() if moves]
             + late + [terminal])
    for i, matrix in enumerate(cases):
        check_relabeling(matrix, 48271 + i)
    return {"seed_and_cleanup_dispatch_classes_at_two": len(startup_signatures),
            "clean_second_join_handoffs": len(handoffs),
            "block_dispatch_classes_at_four": len(middle_signatures),
            "tail_dispatch_classes_at_five": len(late_signatures),
            "cross_phase_dispatch_collisions": 0,
            "independently_renamed_composite_tables": len(cases),
            "entry_identity_transport": verify_block_entry(),
            "terminal_permanent_distinctions": len(terminal)}


if __name__ == "__main__":
    print(json.dumps(verify_composition(), indent=2, sort_keys=True))
