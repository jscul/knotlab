"""Ten balanced endpoint tasks. The fitting interface receives only labeled TRAIN rows."""

import json
from collections import Counter
from itertools import permutations, product


POINTS = tuple(product(range(3), repeat=3))
HELD = tuple((x, y, z) for x, y, z in POINTS if z == (x + y + 2) % 3)
TRAIN = tuple(p for p in POINTS if p not in HELD)
RENAMINGS = tuple(permutations(range(3)))
PAIR_EQUAL = "6d18"
TWIN = "f46b"
REMOVED, ADDED = (1, 1, 1), (1, 0, 0)


def index(p):
    x, y, z = p
    return 9*x + 3*y + z


def _bit(mask, p):
    return (mask >> index(p)) & 1


def _matched(x, y, z):
    p = (x, y, z)
    return (x == y and p != REMOVED) or p == ADDED


# Opaque IDs support bookkeeping. Descriptions and predicates are grader-side.
_TASKS = {
    PAIR_EQUAL: ("The first two values agree.", lambda x, y, z: x == y),
    "4caf": ("The first and third values agree.", lambda x, y, z: x == z),
    "a942": ("The last two values agree.", lambda x, y, z: y == z),
    "c10e": ("The third equals the second when the first is zero and equals the first otherwise.",
             lambda x, y, z: z == (y if x == 0 else x)),
    "1ab7": ("The third is zero when the first two agree and takes the remaining label when they differ.",
             lambda x, y, z: z == (0 if x == y else 3-x-y)),
    "e35a": ("The third copies the second when the first two agree and takes the cyclic successor of the second otherwise.",
             lambda x, y, z: z == (y if x == y else (y+1) % 3)),
    "79c2": ("The third copies the first when the second is its cyclic successor and copies the second otherwise.",
             lambda x, y, z: z == (x if y == (x+1) % 3 else y)),
    "528f": ("The third copies the second when the first is zero and takes the cyclic successor of the second otherwise.",
             lambda x, y, z: z == (y if x == 0 else (y+1) % 3)),
    "b037": ("The third counts how many of two tests hold, first value zero and second value one.",
             lambda x, y, z: z == int(x == 0) + int(y == 1)),
    TWIN: ("Start with first-two equality, remove 111 and add 100.", _matched),
}


def panel():
    """Grader specifications. A learner must receive only its selected observation rows."""
    return tuple({"id": key, "mask": sum(1 << index(p) for p in POINTS if _TASKS[key][1](*p))}
                 for key in sorted(_TASKS))


def _apply(program, p):
    # A gate (c,k,t,a) exchanges 0 and a at t when the distinct control c has k.
    # With codes 00,01,10 this is one guarded single-bit flip.
    values = list(p)
    for control, condition, target, color in program:
        if values[control] == condition and values[target] in (0, color):
            values[target] = color - values[target]
    return tuple(values)


def _cycle(x, y, direction):
    # At fixed first two values, these four flips give one 3-cycle on the third.
    # Where either control fails the remaining transposition occurs twice.
    a = (0, x, 2, 1)
    b = (1, y, 2, 2)
    return [b, a, b, a] if direction == 1 else [a, b, a, b]


def _swap_last_two():
    gates = []
    for k in (1, 2):
        a = (1, 0, 2, k)
        b = (2, 0, 1, k)
        gates.extend((a, b, a))
    # Exchange the remaining pair (1,2)/(2,1) along four legal one-bit changes.
    path = [(2, 2, 1, 1), (1, 0, 2, 2), (2, 0, 1, 2), (1, 2, 2, 1)]
    return gates + path + list(reversed(path[:-1]))


def _subtract(control, target):
    return [(control, 1, target, 2), (control, 1, target, 1),
            (control, 2, target, 1), (control, 2, target, 2)]


def _feasibility_witness(key, mask):
    if key in ("4caf", "a942"):
        return _subtract(0 if key == "4caf" else 1, 2)
    if key in (PAIR_EQUAL, TWIN):
        # Subtract the first value from the second, then put the result in the flag.
        program = _subtract(0, 1) + _swap_last_two()
        if key == TWIN:
            # Conjugate one 3-cycle so that 100 moves to 111 and 111 to 102.
            change = (2, 1, 1, 1)
            program = [change] + _cycle(1, 0, 1) + [change] + program
        return program
    program = []
    for x, y in product(range(3), repeat=2):
        required, = (z for z in range(3) if _bit(mask, (x, y, z)))
        if required:
            program.extend(_cycle(x, y, -1 if required == 1 else 1))
    return program


def _orbit_counts():
    remaining = set(POINTS)
    sizes = []
    while remaining:
        p = min(remaining)
        orbit = {tuple(g[v] for v in p) for g in RENAMINGS}
        remaining -= orbit
        sizes.append(len(orbit))
    return sorted(sizes)


def audit():
    """Evaluation-only controls, computed independently of the selector and of any prior fit."""
    rows = []
    masks = {case["id"]: case["mask"] for case in panel()}
    if len(set(masks.values())) != len(masks):
        raise AssertionError("Duplicate full truth tables")
    for key, mask in masks.items():
        program = _feasibility_witness(key, mask)
        output = [_apply(program, p) for p in POINTS]
        witness_mask = sum(1 << i for i, result in enumerate(output) if result[2] == 0)
        if witness_mask != mask or len(set(output)) != len(POINTS) or mask.bit_count() != 9:
            raise AssertionError(f"Raw-gate feasibility failed for {key}")
        stabilizer = []
        training_violations = []
        for g in RENAMINGS:
            image = {p: tuple(g[v] for v in p) for p in POINTS}
            if all(_bit(mask, p) == _bit(mask, image[p]) for p in POINTS):
                stabilizer.append(g)
            training_violations.append(sum(_bit(mask, p) != _bit(mask, image[p])
                                           for p in TRAIN if image[p] in TRAIN))
        changes = [sum(_bit(mask, p) != _bit(mask, p[:i] + (a,) + p[i+1:])
                       for p in POINTS for a in range(3)) for i in range(3)]
        rows.append({
            "id": key, "definition": _TASKS[key][0], "positive": mask.bit_count(),
            "training_positive": sum(_bit(mask, p) for p in TRAIN),
            "held_positive": sum(_bit(mask, p) for p in HELD),
            "full_stabilizer": stabilizer, "stabilizer_order": len(stabilizer),
            "training_violations_in_renaming_order": training_violations,
            "essential_inputs": [axis for axis, count in zip(("x", "y", "z"), changes) if count],
            "directed_changes_by_input": changes, "primitive_witness": program,
            "witness_flips": len(program), "distinct_witness_outputs": len(set(output)),
        })
    twins = masks[PAIR_EQUAL] ^ masks[TWIN]
    disagreements = [p for p in POINTS if _bit(twins, p)]
    if set(disagreements) != {REMOVED, ADDED} or not set(disagreements) <= set(HELD):
        raise AssertionError("Matched targets must disagree only on the two reserved rows")
    return {
        "point_mask_index": "9*x+3*y+z", "renaming_order": RENAMINGS,
        "cyclic_successor": [1, 2, 0], "global_orbit_sizes": _orbit_counts(),
        "train": TRAIN, "held": HELD, "tasks": rows,
        "stabilizer_order_counts": dict(sorted(Counter(r["stabilizer_order"] for r in rows).items())),
        "witness_gate_fields": ["control_register", "control_value", "target_register", "swap_zero_with"],
        "twin": {"invariant_id": PAIR_EQUAL, "sensitive_id": TWIN,
                 "same_ordered_observations": all(not _bit(twins, p) for p in TRAIN),
                 "held_disagreements": disagreements,
                 "paired_max_correct_from_identical_predictions": 2*len(HELD)-len(disagreements)},
    }


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
