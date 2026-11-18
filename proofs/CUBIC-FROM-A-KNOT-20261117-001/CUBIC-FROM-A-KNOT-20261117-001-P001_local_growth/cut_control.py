"""Replay growth of the cut boxes and test their eight-bit restriction of the parity boxes.

Coordinates specify the finite control and its predicted cuts. Each move independently
computes its actual allowed states from the ordered betweenness triples alone. The
separate parity projection uses freely chosen output bits and exact binary linear images.
"""

import argparse
import json
from collections import Counter
from itertools import combinations, product


def cut_states(points):
    rows = {(0,) * len(points), (1,) * len(points)}
    for axis in range(3):
        values = [p[axis] for p in points]
        for threshold in range(min(values) + 1, max(values) + 1):
            row = tuple(int(value >= threshold) for value in values)
            rows.update((row, tuple(1 - bit for bit in row)))
    return rows


def extend(points, states, point, knots):
    """Try both new values on every old state. B(a,b,c) says a=c forces b=a."""
    index = {p: i for i, p in enumerate([*points, point])}
    triples = [tuple(index[p] for p in knot) for knot in knots]
    rows = set()
    for old in states:
        for bit in (0, 1):
            row = (*old, bit)
            if all(row[a] != row[c] or row[b] == row[a] for a, b, c in triples):
                rows.add(row)
    return rows


def add_point(points, states, point, knots):
    if point in points:
        raise ValueError(f"Point already present: {point}")
    rows = extend(points, states, point, knots)
    if {row[:-1] for row in rows} != states or rows != cut_states([*points, point]):
        raise ValueError(f"Cut extension disagrees with the replay at {point}")
    if len(rows) == 2 * len(states) or any(
        all(row[i] == row[-1] for row in rows) for i in range(len(points))
    ):
        raise ValueError(f"New distinction is unconstrained or a copy at {point}")
    points.append(point)
    return rows


def grow_layer(points, states, axis, side):
    bounds = [(min(v), max(v)) for v in zip(*points)]
    boundary = bounds[axis][0 if side == -1 else 1]
    layer = [p for p in points if p[axis] == boundary]
    corner = next(p for p in layer if all(v in b for v, b in zip(p, bounds)))
    opposite = tuple(lo + hi - v for v, (lo, hi) in zip(corner, bounds))

    def outward(p):
        return tuple(v + side if i == axis else v for i, v in enumerate(p))

    tip = outward(corner)
    states = add_point(points, states, tip, [(opposite, corner, tip)])
    checked_control = False
    for x in layer:
        if x == corner:
            continue
        point = outward(x)
        knots = [(tip, point, x), (corner, tip, point), (corner, x, point)]
        if not checked_control:
            wrong = [*knots[:2], (x, corner, point)]
            if extend(points, states, point, wrong) == cut_states([*points, point]):
                raise ValueError("A reversed middle role passed the cut control")
            checked_control = True
        states = add_point(points, states, point, knots)
    return states, int(checked_control)


def seed_to_cube():
    a, corner, b = (1, 0, 0), (0, 0, 0), (0, 1, 0)
    points = [a, corner, b]
    states = {r for r in product(range(2), repeat=3) if r[0] != r[2] or r[1] == r[0]}
    if states != cut_states(points):
        raise ValueError("The single betweenness knot disagrees with the starting cut model")
    counts = {3: len(states)}
    fourth = (1, 1, 0)
    states = add_point(points, states, fourth, [(b, fourth, a), (corner, b, fourth), (corner, a, fourth)])
    counts[4] = len(states)
    states, rejected = grow_layer(points, states, 2, 1)
    counts[8] = len(states)
    if set(points) != set(product(range(2), repeat=3)) or counts != {3: 6, 4: 6, 8: 8}:
        raise ValueError("The five moves from the betweenness seed missed the cut cube")
    return points, states, {"states_at_milestones": counts, "single_point_moves": 5,
                            "wrong_middle_controls_rejected": rejected}


def check_box(points, states, side):
    pairs = set(combinations(range(len(points)), 2))
    disagreements = Counter()
    for a, b in pairs:
        if len({(row[a], row[b]) for row in states}) != 4:
            raise ValueError(f"Pair projection is constrained at {a}, {b}")
        count = sum(row[a] != row[b] for row in states)
        steps = sum(abs(x - y) for x, y in zip(points[a], points[b]))
        if count != 2 * steps:
            raise ValueError(f"Disagreement count fails at {a}, {b}")
        disagreements[count] += 1

    # K1 needs a missing triple pattern. All pair projections already passed K2.
    # The nonempty set of cut states gives K3 for every projection.
    witnessed = set()
    for a, b, c in combinations(range(len(points)), 3):
        if len({(row[a], row[b], row[c]) for row in states}) < 8:
            witnessed.update(((a, b), (a, c), (b, c)))
        if witnessed == pairs:
            break
    if witnessed != pairs:
        raise ValueError(f"{len(pairs - witnessed)} pairs lack a triple bond")
    return {
        "side": side, "distinctions": len(points), "allowed_states": len(states),
        "single_point_moves_since_q3": len(points) - 8,
        "bond_distance_counts": {2: len(witnessed)},
        "raw_disagreement_counts": dict(sorted(disagreements.items())),
    }


def projection(forms, old_bits, old_rows):
    """Give each parameter above the old bits both values and take its linear image."""
    span = {0}
    for i in range(old_bits, max(form.bit_length() for form in forms)):
        column = sum(((form >> i) & 1) << j for j, form in enumerate(forms))
        if column not in span:
            span = span | {row ^ column for row in span}
    result = set()
    for old in old_rows:
        offset = sum(((form & old).bit_count() % 2) << j for j, form in enumerate(forms))
        result.update(offset ^ row for row in span)
    return result


def parity_bridge(side, marked_points, cut_rows):
    """All states on a down-set have free y,z outputs. Each star fixes its x output."""
    marked = [(v, 2) for v in marked_points]
    forms = {port: 1 << i for i, port in enumerate(marked)}
    next_bit = len(marked)
    stars = {}
    reached = set(marked_points)
    points = sorted(marked_points, key=lambda p: (sum(p), p))
    points += sorted((v for v in product(range(side), repeat=3) if v not in reached),
                     key=lambda p: (sum(p), p))
    for v in points:
        inputs = []
        for axis, value in enumerate(v):
            if value:
                pred = tuple(x - 1 if i == axis else x for i, x in enumerate(v))
                if pred not in stars:
                    raise ValueError("A junction was added ahead of a predecessor")
                inputs.append((pred, axis))
        outputs = [(v, i) for i in range(3)]
        if sum(out in forms for out in outputs) != int(v in reached):
            raise ValueError("The junction did not reuse exactly its old marked output")
        for out in outputs[1:]:
            if out not in forms:
                forms[out] = 1 << next_bit
                next_bit += 1
        value = 0
        for port in [*inputs, *outputs[1:]]:
            value ^= forms[port]
        forms[outputs[0]] = value
        stars[v] = [*inputs, *outputs]
    if next_bit != 2 * side**3 or len(forms) != 3 * side**3:
        raise ValueError("Wrong number of independent parity parameters or ports")

    old = {sum(bit << i for i, bit in enumerate(row)) for row in cut_rows}
    marked_forms = [forms[port] for port in marked]
    free_rows = projection(marked_forms, 0, [0])
    pinned_rows = projection(marked_forms, len(marked), old)
    if free_rows != set(range(256)) or pinned_rows != old:
        raise ValueError("The eight old distinctions have the wrong projection")
    # Each distinguished-direction output uses its own free parameter before pinning.
    position_forms = [forms[(v, 2)] for v in points]
    if (any(form.bit_count() != 1 for form in position_forms)
            or len(set(position_forms)) != len(points)):
        raise ValueError("Hiding the horizontal bits introduced a constraint on positions")
    arities = Counter()
    overlaps = Counter()
    for v, ports in stars.items():
        arity = len(ports)
        local = projection([forms[port] for port in ports], len(marked), old)
        if local != {row for row in range(1 << arity) if row.bit_count() % 2 == 0}:
            raise ValueError(f"The marked restriction changed the even star at {v}")
        arities[arity] += 1
        overlaps[len(set(ports).intersection(marked))] += 1
    # Both constant old rows keep each old bit open but force the two z ports here equal.
    sample = stars[(0, 0, 1)]
    control = projection([forms[port] for port in sample], len(marked), [0, 255])
    if len(control) != 4 or len(sample) != 4:
        raise ValueError("The two-constant control should admit four of eight even tuples")
    return {
        "side": side, "junctions": len(stars), "free_parameters_before_restriction": next_bit,
        "marked_rows_before_restriction": len(free_rows), "marked_rows_after_restriction": len(pinned_rows),
        "free_new_position_bits_after_hiding_other_bits": len(points) - len(marked),
        "full_even_stars_by_arity": dict(sorted(arities.items())),
        "star_counts_by_number_of_old_ports": dict(sorted(overlaps.items())),
        "two_constant_control_at_001": {"even_tuples": 8, "allowed": len(control)},
    }


def run():
    points, states, prefix = seed_to_cube()
    bridges = [parity_bridge(n, points, states) for n in (3, 4)]
    boxes = [check_box(points, states, 2)]
    controls = 0
    for side, moves in [(3, [(0, -1), (2, 1), (1, -1)]),
                        (4, [(1, 1), (0, 1), (2, -1)])]:
        for axis, sign in moves:
            states, rejected = grow_layer(points, states, axis, sign)
            controls += rejected
        if len(points) != side**3:
            raise ValueError(f"Incomplete box of side {side}")
        boxes.append(check_box(points, states, side))
    return {"seed_to_cut_cube": prefix, "boxes": boxes, "wrong_middle_controls_rejected": controls,
            "pinned_parity_boxes": bridges}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="write the result as JSON to stdout")
    args = parser.parse_args()
    result = run()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Betweenness seed to cut cube, states at 3, 4, 8 distinctions: "
              f"{result['seed_to_cut_cube']['states_at_milestones']}")
        for box in result["boxes"]:
            pairs = sum(box["bond_distance_counts"].values())
            print(f"Side {box['side']}: {box['allowed_states']} states, {pairs} pairs at bond distance 2, "
                  f"raw disagreement counts {box['raw_disagreement_counts']}")
        print(f"Rejected {result['wrong_middle_controls_rejected']} reversed-middle controls.")
        for bridge in result["pinned_parity_boxes"]:
            print(f"Parity box of side {bridge['side']}: 256 old rows before restriction, "
                  f"{bridge['marked_rows_after_restriction']} after, {bridge['junctions']} full even stars.")
