"""Replay the frozen composition holdouts with both original path-end readings."""

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
PRIOR = "MOTION-AT-EDDY-20261119-001"
FAMILY = PRIOR + "-E001_motion"
EXPERIMENT = ROOT / "experiments" / PRIOR / FAMILY
RECEIPT = ROOT / "artifacts" / PRIOR / FAMILY / "composed_motion.json"
sys.path.insert(0, str(EXPERIMENT))
from b_updates import holder_steps
from composed_motion import PHASES, PairedReader, bits, co_knotted_pairs, growth_engine


def replay_launch(reader, path, old_positions, slots, rulers, start, direction, seams):
    def placed(anchor, phase):
        return tuple(anchor + direction * offset for offset in PHASES[phase])

    initial = placed(start, 0)
    if any(slots.get(i) is None for i in range(min(initial), max(initial) + 1)):
        return None
    state = reader.encode(slots[i] for i in initial)
    readings = []
    occupied_across = set()
    event = 0
    while True:
        shifts, phase = divmod(event, 4)
        anchor = start + direction * shifts
        centres = placed(anchor, phase)
        assert state == reader.encode(slots[i] for i in centres)
        footprint = {v for e in bits(state) for v in reader.stage.owners[e]}
        old_footprint = [old_positions[v] for v in footprint if v in old_positions]
        occupied_across.update(seam for seam in seams if min(old_footprint) < seam < max(old_footprint))
        if phase == 0:
            assert state.bit_count() == 10
            anchor_steps = [ruler[path[anchor]] for ruler in rulers]
            support_steps = [min(ruler[v] for v in footprint) for ruler in rulers]
            readings.append([event, anchor, *anchor_steps, *support_steps])
        following = reader.next_state(state)
        if following is None:
            break
        state = following
        event += 1
        if event > 4 * len(path) + 4:
            raise ValueError("replay exceeded the predecessor's event bound")
    delta = [direction, -direction] * 2
    assert all([later[i] - earlier[i] for i in range(2, 6)] == delta
               for earlier, later in zip(readings, readings[1:]))
    anchors = [row[1] for row in readings]
    return {
        "start": start, "direction": direction, "events": event,
        "completed_shifts": len(readings) - 1, "last_full_anchor": anchors[-1],
        "crossed": [seam for seam in seams if min(anchors) < seam < max(anchors)],
        "seams_straddled_by_a_literal_footprint_at_any_phase": sorted(occupied_across),
        "phase_a": readings,
    }


def replay_case(spec, old):
    growth = growth_engine()
    export = growth.grow_case(spec, 1, {"junctions": 2048, "distinctions": 8192})
    assert export["qualification"]["canonical"] and export["qualification"]["DOUBLE_IDENT"]["in_class"]
    stars = export["stages"]["1"]["stars"]
    reader = PairedReader(co_knotted_pairs(stars))
    recovered = {frozenset(row): i for i, row in enumerate(reader.rule.stars)}
    path = [recovered[frozenset(stars[v])] for v in spec["roles"]["background"]]
    assert len(path) == 85 and len(set(path)) == 85
    rulers = [holder_steps(reader.stage, path[i]) for i in (0, len(path) - 1)]
    assert all(len(ruler) == len(stars) for ruler in rulers)
    assert [rulers[0][v] for v in path] == list(range(len(path)))
    assert [rulers[1][v] for v in path] == list(reversed(range(len(path))))
    slots = {i: reader.sites.get(frozenset(path[i - 1:i + 2])) for i in range(1, len(path) - 1)}
    old_positions = {v: i for i, v in enumerate(path)}
    seams = spec["roles"]["seams"]
    launches = []
    for direction in (1, -1):
        for start in slots:
            row = replay_launch(reader, path, old_positions, slots, rulers, start, direction, seams)
            if row is not None:
                launches.append(row)
    reader.next_state.cache_clear()

    def earlier_fields(row):
        return {k: row[k] for k in ("start", "direction", "events", "completed_shifts", "last_full_anchor", "crossed")}

    orientations = Counter(row["direction"] for row in launches)
    earlier_crossings = Counter(",".join(map(str, row["crossed"])) or "none" for row in launches)
    outermost = [row for row in launches if row["start"] in (1, len(path) - 2)]
    assert old["launches"] == {"positive": orientations[1], "negative": orientations[-1]}
    assert old["crossed_by_full_anchor"] == earlier_crossings
    assert old["outermost_launches"] == [earlier_fields(row) for row in outermost]
    assert old["longest"] == earlier_fields(max(launches, key=lambda row: row["events"]))
    assert old["at_least_two_shifts"] == sum(row["completed_shifts"] >= 2 for row in launches)
    return {
        "launches_positive_negative": [orientations[1], orientations[-1]],
        "phase_a_readings": sum(len(row["phase_a"]) for row in launches),
        "unit_translations_with_both_endpoint_readings": sum(row["completed_shifts"] for row in launches),
        "launches_with_at_least_two_translations": old["at_least_two_shifts"],
        "unreachable_landmarks": 0,
        "outermost_summary": [
            earlier_fields(row) | {"first_phase_a": row["phase_a"][0], "last_phase_a": row["phase_a"][-1]}
            for row in outermost
        ],
        "seams_straddled_in_any_literal_phase": sorted({
            seam for row in launches for seam in row["seams_straddled_by_a_literal_footprint_at_any_phase"]
        }),
        "earlier_launch_and_crossing_summary_reproduced": True,
        "launches": launches,
    }


def main():
    inputs = (EXPERIMENT / "holdout.json").read_bytes()
    old = RECEIPT.read_bytes()
    receipt = json.loads(old)
    result = {spec["id"]: replay_case(spec, receipt[spec["id"]]) for spec in json.loads(inputs)["cases"]}
    print(json.dumps({
        "measurement": "supplemental replay of the already frozen size-two holdout launches",
        "holdout_input_sha256": sha256(inputs).hexdigest(),
        "predecessor_receipt_sha256": sha256(old).hexdigest(),
        "landmarks_in_order": ["b0", "b84"],
        "ruler": ("shortest knot-to-knot steps across literal distinctions with two holders on the "
                  "entire fixed stage, with one step per shared distinction and no auxiliary exterior"),
        "anchor": "the trailing phase-A response centre in that launch's direction",
        "occupied_support": "minimum from an endpoint to any holder of any occupied physical distinction",
        "phase_a_columns": ["elementary_event", "anchor_source_position", "anchor_steps_from_b0",
                            "anchor_steps_from_b84", "occupied_support_steps_from_b0",
                            "occupied_support_steps_from_b84"],
        "cases": result,
    }, indent=2))


if __name__ == "__main__":
    main()
