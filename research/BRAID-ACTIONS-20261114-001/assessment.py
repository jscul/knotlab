"""Score a saved frozen policy, including real packets and new downstream wirings."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
TICKET = "BRAID-ACTIONS-20261114-001"
FAMILY = TICKET + "-E001_atomic_policy"
sys.path.insert(0, str(ROOT / "experiments" / TICKET / FAMILY))
import actions
import reader


def challenges(forward):
    menus = {}

    def add(name, menu):
        menus.setdefault(tuple(menu), []).append(name)

    for i, menu in enumerate(reader.training_menus()):
        add(f"training_{i}", menu)
    for port in reader.PORTS:
        add("one_reader", reader.cycle([port]))
        for other in reader.PORTS:
            if other != port:
                add("alternating_two_readers", reader.cycle((port, other)))
    order = (4, 0, 8, 3, 5, 2, 7, 6, 1)
    for phase in range(2):
        cells = [(phase, *reader.POINTS[i]) for i in order]
        for k in range(1, 10):
            add(f"ladder_{phase}_{k}", reader.cycle(cells[:k]))
        add(f"full_reversed_socket_order_{phase}", tuple(reversed(cells)))
    for old, current in zip(reader.POINTS, forward):
        add("alias_across_frames", reader.cycle(((1, *old), (0, *current))))
    add("stop_or_undo_row_zero", reader.cycle(((0, 0, -1), (1, 0, -1))))
    add("row_and_three_cells", reader.cycle(((0, 0, -1), (0, 0, 0), (0, 0, 1), (0, 0, 2))))
    add("six_row_reads", reader.cycle(tuple((phase, r, -1) for phase in (0, 1) for r in range(3))))
    return menus


def results_by_menu(checkpoint, *, executed_moves=None):
    forward, undo = reader.frame_values(checkpoint["moves"]) if executed_moves is None else executed_moves
    panels = challenges(forward)
    trained = set(reader.training_menus())
    reach = {p: reader.reach(p, undo) for p in reader.PORTS}
    expected = {p: reader.truth_column(reader.original_query(p, forward)) for p in reader.PORTS}
    columns = reader.crossed_columns(forward)
    predicted = {m: reader.scan_columns(checkpoint["reader"]["aggregate"], columns, m)
                 for m in set(reach.values())}
    allowed = reader.allocator(checkpoint["reader"]["reuse"])
    # Every payload below is materialized. The decoder consumes it via the
    # public bindings, identical for all 512 relations with this wiring.
    wire_bits = {m: tuple((out >> w) & 1 for w in range(512)) for m, out in predicted.items()}
    want_bits = {p: tuple((values >> w) & 1 for w in range(512)) for p, values in expected.items()}
    tallies = {name: Counter() for name in ("train_menu_even", "train_menu_odd", "held_menu_even", "held_menu_odd")}
    by_width = Counter()
    rows = []
    for menu, tags in panels.items():
        reps, binding = reader.allocation(tuple(reach[port] for port in menu), allowed)
        outputs = [wire_bits[r] for r in reps]
        truths = [want_bits[p] for p in menu]
        answer_classes, packet_classes = set(), set()
        error = None
        packet_hash = sha256()
        counts = [0, 0]
        for world in range(512):
            payload = tuple(col[world] for col in outputs)
            actual = tuple(payload[slot] for slot in binding)
            wanted = tuple(col[world] for col in truths)
            score = sum(a == b for a, b in zip(actual, wanted))
            counts[world.bit_count() % 2] += score
            if score < 9 and error is None:
                error = {"world": world, "payload": payload, "actual": actual, "wanted": wanted}
            packet_hash.update(bytes(payload))
            answer_classes.add(wanted)
            packet_classes.add(payload)
        min_bits = (len(answer_classes) - 1).bit_length()
        by_width[len(reps), min_bits] += 1
        for parity, correct in zip(("even", "odd"), counts):
            key = ("train_menu_" if menu in trained else "held_menu_") + parity
            tallies[key].update(queries=256 * 9, correct=correct, packets=256, payload_bits=256 * len(reps))
        rows.append({"wiring": menu, "tags": tags, "training_wiring": menu in trained,
                     "width": len(reps), "minimum": min_bits, "packet_classes": len(packet_classes),
                     "answer_classes": len(answer_classes), "correct": sum(counts), "queries": 512 * 9,
                     "first_error": error, "packet_stream_sha256": packet_hash.hexdigest()})
    return {"menus": len(rows), "queries": sum(row["queries"] for row in rows),
            "correct": sum(row["correct"] for row in rows), "strata": tallies,
            "widths": [{"sent": a, "minimum": b, "menus": count} for (a, b), count in sorted(by_width.items())],
            "rows": rows}


def changed_pair_probes(checkpoint):
    probe = reader.cycle(((1, 0, 0),))
    rewired = reader.cycle(((1, 1, 1),))
    complete = tuple((1, *pair) for pair in reader.POINTS)
    rows = []
    for original in (511 ^ 1, 511 ^ 16):
        current = reader.cross_relation(checkpoint["moves"], original)
        result = {}
        for name, menu in (("first_attachment", probe), ("rewired_attachment", rewired),
                           ("whole_pairing", complete)):
            plan = reader.public_plan(checkpoint, menu)
            packet = reader.send(checkpoint, current, plan)
            result[name] = {"physical_packet": packet,
                            "answer": [reader.receive(checkpoint, menu, packet, i) for i in range(9)]}
        rows.append({"original": original, "current": current,
                     "current_marginals": [sorted({p[i] for j, p in enumerate(reader.POINTS)
                                                    if current & (1 << j)}) for i in range(2)],
                     "reads": result})
    matched = Counter()
    old_plan = reader.public_plan(checkpoint, probe)
    new_plan = reader.public_plan(checkpoint, rewired)
    for original in range(512):
        current = reader.cross_relation(checkpoint["moves"], original)
        expected_a, expected_b = bool(original & 1), bool(original & 16)
        packet_a = reader.send(checkpoint, current, old_plan)
        packet_b = reader.send(checkpoint, current, new_plan)
        if expected_a != expected_b:
            matched["required_change"] += 1
            matched["rewired_correct"] += packet_b[new_plan[1][0]] == expected_b
            matched["stale_correct"] += packet_a[old_plan[1][0]] == expected_b
            matched["actual_changed"] += packet_b[new_plan[1][0]] != packet_a[old_plan[1][0]]
    # Make the measured reader actually cross a moved cell, including cases
    # where separately inspecting either strand reports all three values.
    forward, _ = reader.frame_values(checkpoint["moves"])
    source = next(p for p, q in zip(reader.POINTS, forward) if q != p)
    target = forward[reader.index(source)]
    changed_frame = []
    for missing in (source, target):
        original = 511 ^ (1 << reader.index(missing))
        current = reader.cross_relation(checkpoint["moves"], original)
        readings = []
        for phases in ((0,), (1,), (0, 1)):
            menu = reader.cycle(tuple((phase, *target) for phase in phases))
            payload = reader.send(checkpoint, current, reader.public_plan(checkpoint, menu))
            readings.append({"phases": phases, "packet": payload,
                             "decoded": [reader.receive(checkpoint, menu, payload, i)
                                         for i in range(len(phases))]})
        changed_frame.append({"missing_original": missing, "missing_current": forward[reader.index(missing)],
                              "current_marginals": [sorted({p[i] for j, p in enumerate(reader.POINTS)
                                                            if current & (1 << j)}) for i in range(2)],
                              "read_pins": target, "readings": readings})
    return {"same_marginal_witnesses": rows, "matched_fixed_worlds": matched,
            "moved_cell_frame_rewire": changed_frame,
            "full_relation_one_slot_exact_identifications_upper_bound": 2}


def four_strands(checkpoint):
    forward, undo = reader.frame_values(checkpoint["moves"])

    def act(state, wiring, table):
        a, b = wiring
        result = list(state)
        result[a], result[b] = table[reader.index((state[a], state[b]))]
        return tuple(result)

    labels = range(4)
    words = list(product(tuple(permutations(labels, 2)), repeat=2))
    words.append(((0, 2), (3, 1), (1, 2), (2, 0), (1, 3), (0, 1), (2, 3)))
    counts = Counter()
    witnesses = []
    for start in product(range(3), repeat=4):
        if not witnesses and act(start, (0, 1), forward) != act(start, (0, 2), forward):
            witnesses.append({"start": start, "AB": act(start, (0, 1), forward),
                              "AC": act(start, (0, 2), forward)})
        for word in words:
            state = start
            for pair in word:
                state = act(state, pair, forward)
            for pair in reversed(word):
                state = act(state, pair, undo)
            counts["round_trips"] += 1
            counts["restored"] += state == start
        for a, b, c in permutations(labels, 3):
            left = right = start
            for pair in ((a, b), (b, c), (a, b)):
                left = act(left, pair, forward)
            for pair in ((b, c), (a, b), (b, c)):
                right = act(right, pair, forward)
            counts["braid_triples"] += 1
            counts["braid_agreements"] += left == right
    return {"counts": counts, "rewiring_example": witnesses, "word_lengths": [2, 7]}


def simplicity_control():
    """Count all maps satisfying the other structural constraints, after fitting."""
    # A permutation of three symbols fixing a specified one has two choices.
    # This leaves 2^3 independent choices per output coordinate.
    points = reader.POINTS
    predicates, _ = actions.enumerate_predicates()
    counts = {}
    for flags in product((False, True), repeat=6):
        table = []
        for x, y in points:
            remaining = 3 - x - y
            first = remaining if flags[x] and y != x else y
            second = remaining if flags[3 + y] and x != y else x
            table.append((first, second))
        if len(set(table)) != 9 or not any(flags):
            continue
        if all(table[reader.index(dest)] == point for point, dest in zip(points, table)):
            continue
        cost = sum(predicates[sum(1 << i for i, pair in enumerate(table) if pair[coord] == value)].gates
                   for coord in range(2) for value in range(3))

        def compose(triple, order):
            state = list(triple)
            for i in order:
                state[i:i+2] = table[reader.index(state[i:i+2])]
            return state

        agrees = all(compose(t, (0, 1, 0)) == compose(t, (1, 0, 1))
                     for t in product(range(3), repeat=3))
        tally = counts.setdefault(cost, {"candidates": 0, "full_braids": 0})
        tally["candidates"] += 1
        tally["full_braids"] += agrees
    return {"diagonal_and_fiber_type_only": 64, "by_total_gate_count": counts,
            "tested_after_checkpoint_freeze": True}


def audit(checkpoint, frozen_training):
    saved = actions.canonical_sha256(checkpoint)
    move_result = dict(frozen_training, checkpoint=checkpoint["moves"])
    action_findings = actions.assess_fitted(move_result)
    result = {"checkpoint_sha256": saved, "actions": action_findings,
              "wiring": results_by_menu(checkpoint), "pairing": changed_pair_probes(checkpoint),
              "four_strands": four_strands(checkpoint), "simplicity_control": simplicity_control()}
    if actions.canonical_sha256(checkpoint) != saved:
        raise RuntimeError("evaluation changed the policy")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "artifacts" / TICKET / FAMILY)
    args = parser.parse_args()
    checkpoint = json.loads((args.out / "checkpoint.json").read_text())
    raw = json.loads((args.out / "results.jsonl").read_text())["result"]
    if raw["checkpoint_sha256"] != actions.canonical_sha256(checkpoint):
        raise ValueError("checkpoint does not match the fit")
    print(json.dumps(audit(checkpoint, raw["move_training"]), separators=(",", ":")))
