"""Check operational holding projections and exact tree behavior on synthetic inputs."""

from fractions import Fraction
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys

from reader import (
    DEPTH_LIMIT,
    HOLDING_COUNT,
    OPEN_RELATIONS,
    KnotTree,
    _FEATURE_WIDTH,
    _NODE_WIDTH,
    _RECEIPT_WIDTH,
    _TAG_WIDTH,
    _TREE_START,
    _fit_tree,
    _holding,
    features,
)


ROOT = Path(__file__).resolve().parents[3]
OPEN = {"parity": {"000", "011", "101", "110"},
        "nae": {"001", "010", "011", "100", "101", "110"}}
PREPARED = {"parity": {"110", "011"}, "nae": {"110", "001"}}


def bitmap(*occupied):
    return tuple(int((row, col) in occupied) for row in range(8) for col in range(8))


EMPTY = bitmap()
SINGLE = bitmap((3, 2))
MOVED = bitmap((7, 7))


def reject(operation, *inputs):
    try:
        operation(*inputs)
    except ValueError:
        return
    raise AssertionError(f"{operation.__name__} accepted a rejected fixture")


def canonical_check(rows):
    clauses = [" ".join(("~" if bit == "1" else "") + name
                        for bit, name in zip(row, ("mark", "dock", "read"), strict=True))
               for row in map("".join, product("01", repeat=3)) if row not in rows]
    command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", "; ".join(clauses),
               "--loops", "mark", "dock", "--contact", "read", "--json"]
    result = subprocess.run(command, cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT / "tools")),
                            capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def projection(reader, baseline, address, expected):
    observed = set()
    offset = 2 * address
    for word in product((0, 1), repeat=3):
        reader.restore_memory(baseline)
        try:
            reader.prepare_holding(address, word)
        except ValueError:
            assert reader.export_memory() == baseline
        else:
            row = "".join(map(str, word))
            observed.add(row)
            packed = f"{int(row, 2):02x}"
            raw = baseline["words"]
            assert reader.export_memory()["words"] == raw[:offset] + packed + raw[offset + 2:]
    assert observed == expected
    report = canonical_check(observed)
    assert report["is_knot"] and report["minimum_width"] == 3
    return {"address": address, "verdict": report}


def teach(reader, rows):
    for pixels, action in rows:
        guess = reader.predict(pixels)
        reader.learn(pixels, guess, guess == action)


def impurity(rows):
    positive = sum(action for _, action in rows)
    return Fraction(2 * positive * (len(rows) - positive), len(rows) ** 2)


def fraction_tree(rows, depth=0):
    gain, split = Fraction(0), None
    if depth < DEPTH_LIMIT:
        for index in range(len(rows[0][0])):
            for value in sorted({vector[index] for vector, _ in rows})[:-1]:
                left = [row for row in rows if row[0][index] <= value]
                right = [row for row in rows if row[0][index] > value]
                change = impurity(rows) - (len(left) * impurity(left) + len(right) * impurity(right)) / len(rows)
                if change > gain:
                    gain, split = change, (index, value, left, right)
    if split is None:
        return {"vote": int(2 * sum(action for _, action in rows) > len(rows))}
    index, value, left, right = split
    return {"feature": index, "threshold": value,
            "left": fraction_tree(left, depth + 1), "right": fraction_tree(right, depth + 1)}


def shape_depth(tree):
    return 0 if "vote" in tree else 1 + max(shape_depth(tree["left"]), shape_depth(tree["right"]))


def sensor_and_split_checks():
    assert features(EMPTY, "position") == EMPTY
    left = bitmap((0, 2), (2, 0), (3, 3))
    shifted = bitmap((2, 6), (4, 4), (5, 7))
    reflected = bitmap((0, 1), (2, 3), (3, 0))
    assert features(shifted, "position") == features(left, "position") == left
    assert features(reflected, "position") != left
    assert features(SINGLE, "window") == features(MOVED, "window")
    assert features(SINGLE, "window") == tuple(77 if i == 0 else int(i in (1, 2, 4, 8)) for i in range(16))
    reject(features, (0,) * 63, "position")
    reject(features, (2, *EMPTY[1:]), "window")
    reject(features, EMPTY, "missing")

    both_ties = [((0, 0), 0), ((1, 1), 1), ((2, 2), 0)]
    chosen = _fit_tree(both_ties)
    assert chosen == fraction_tree(both_ties) and chosen["feature"] == chosen["threshold"] == 0
    no_gain = [(pair, pair[0] ^ pair[1]) for pair in product((0, 1), repeat=2)]
    assert _fit_tree(no_gain) == fraction_tree(no_gain) == {"vote": 0}
    layered = [((i,), i % 2) for i in range(32)]
    tree = _fit_tree(layered)
    assert tree == fraction_tree(layered) and shape_depth(tree) == DEPTH_LIMIT
    return {"row_column_minima_and_padding": True, "preserved_relative_orientation": True,
            "exact_split_and_threshold_ties": True, "zero_gain_leaf": True, "depth": DEPTH_LIMIT}


def round_trip(law, sensor):
    reader = KnotTree(law, sensor)
    neutral = reader.export_memory()
    reject(reader.finalize)
    reject(reader.learn, EMPTY, 1, False)
    assert reader.export_memory() == neutral
    cases = [(EMPTY, 0), (SINGLE, 1)] * 32
    teach(reader, cases[:17])
    prefix = reader.export_memory()
    assert prefix != neutral
    reject(reader.finalize)
    receiver = KnotTree.from_memory(json.loads(json.dumps(prefix)))
    assert receiver.export_memory() == prefix and receiver.predict(MOVED) == 0
    teach(receiver, cases[17:])
    receipt_words = receiver.export_memory()
    reject(receiver.learn, EMPTY, 0, True)
    expected = fraction_tree([(features(pixels, sensor), action) for pixels, action in cases])
    assert receiver.finalize() == receiver.describe() == expected
    deployed = receiver.export_memory()
    assert deployed["words"][2:2 * _TREE_START] == neutral["words"][2:2 * _TREE_START]
    assert receiver.export_memory() == deployed
    reject(receiver.learn, EMPTY, 0, True)
    reject(receiver.finalize)

    assert receiver.predict(EMPTY) == 0 and receiver.predict(MOVED) == 1
    readout = receiver.explain(MOVED)
    assert readout["path"] == [{"feature": expected["feature"], "threshold": expected["threshold"],
                               "value": readout["features"][expected["feature"]],
                               "branch": "right" if sensor == "position" else "left"}]
    opposite = KnotTree(law, sensor)
    teach(opposite, [(pixels, 1 - action) for pixels, action in cases])
    opposite.finalize()
    receiver.restore_memory(opposite.export_memory())
    assert receiver.predict(EMPTY) == 1 and receiver.predict(MOVED) == 0
    assert receiver.clear_memory() == opposite.export_memory()
    assert receiver.export_memory() == neutral and receiver.predict(MOVED) == 0
    receiver.restore_memory(deployed)
    assert receiver.describe() == expected and receiver.explain(MOVED) == readout

    reject(receiver.restore_memory, {**deployed, "sensor": "window" if sensor == "position" else "position"})
    raw = deployed["words"]
    root_start = 2 * _TREE_START
    reject(receiver.restore_memory, {**deployed, "words": "ff" + raw[2:]})
    reject(receiver.restore_memory, {**deployed, "words": raw[:root_start] + "0606" + raw[root_start + 4:]})
    unreachable = 2 * (_TREE_START + 3 * _NODE_WIDTH)
    reject(receiver.restore_memory, {**deployed,
                                     "words": raw[:unreachable] + raw[:2] + raw[unreachable + 2:]})
    unprepared = min(OPEN[law] - PREPARED[law])
    receiver.prepare_holding(_TREE_START, tuple(map(int, unprepared)))
    reject(receiver.predict, MOVED)
    receiver.restore_memory(deployed)
    return receiver, receipt_words, deployed


def full_depth_round_trip(law):
    cases = [(tuple(int(index < extent) for index in range(64)), extent % 2) for extent in range(32)] * 2
    reader = KnotTree(law, "position")
    teach(reader, cases)
    fitted = reader.finalize()
    assert fitted == fraction_tree([(features(pixels, "position"), action) for pixels, action in cases])
    assert shape_depth(fitted) == DEPTH_LIMIT
    placed = KnotTree.from_memory(reader.export_memory())
    readings = [reader.explain(pixels) for pixels, _ in cases[:32]]
    assert readings == [placed.explain(pixels) for pixels, _ in cases[:32]]
    assert max(len(reading["path"]) for reading in readings) == DEPTH_LIMIT


def checked_laws():
    full_rows = {"".join(row) for row in product("01", repeat=3)}
    free = canonical_check(full_rows)
    assert not free["binding"] and not free["is_knot"]
    free_relation = frozenset(tuple(map(int, row)) for row in full_rows)
    results = {}
    for law in OPEN_RELATIONS:
        for row in PREPARED[law]:
            mark, dock, read = map(int, row)
            assert _holding._admit_word(law, mark, dock) == (mark, dock, read)
            reject(_holding._complete_read, free_relation, mark, dock)
        prepared = canonical_check(PREPARED[law])
        assert not prepared["loss_on_erasure"] and not prepared["is_knot"]
        _, position_receipts, _ = round_trip(law, "position")
        reader, window_receipts, deployed = round_trip(law, "window")
        full_depth_round_trip(law)
        assert window_receipts["words"] == position_receipts["words"]
        expected = OPEN[law]
        occupied_pixel = 1 + _RECEIPT_WIDTH + 2 + 3 * 8 + 2
        results[law] = {"received_bitmap": projection(reader, window_receipts, occupied_pixel, expected),
                        "learned_tag": projection(reader, deployed, _TREE_START, expected),
                        "learned_feature": projection(reader, deployed, _TREE_START + _TAG_WIDTH, expected),
                        "learned_threshold": projection(reader, deployed,
                                                        _TREE_START + _TAG_WIDTH + _FEATURE_WIDTH, expected),
                        "prepared_only": prepared, "same_raw_receipts_both_sensors": True,
                        "fit_swap_clear_restore": True, "shape_rejections": True,
                        "full_depth_round_trip": True}
    return {"laws": results, "unconstrained_negative": free}


if __name__ == "__main__":
    print(json.dumps({**checked_laws(), "holding_count": HOLDING_COUNT,
                      "synthetic_checks": sensor_and_split_checks()}, indent=2, sort_keys=True))
