"""Independent exact tree objective and state encoding for the pixel audit."""

from collections import Counter
from fractions import Fraction
from pathlib import Path
import sys


GROUP_AUDIT = Path(__file__).resolve().parents[2] / "LEARNED-PATCH-GROUPS-20261122-001/audit"
sys.path.insert(0, str(GROUP_AUDIT))
from panel_census import digest, equivalent, loads, read_jsonl, require
from pixel_counts import counts as window_counts
from replay import hash_memory, write_value
sys.path.pop(0)


TRAINING_LIMIT = 64
TREE_BASE = 1 + TRAINING_LIMIT * 66
TREE_HOLDINGS = TREE_BASE + 15 * 15
PREPARED = {"parity": (6, 3), "nae": (6, 1)}


def relative_pixels(raw):
    require(type(raw) is str and len(raw) == 64 and set(raw) <= {"0", "1"}, "Malformed bitmap")
    light = [i for i, bit in enumerate(raw) if bit == "1"]
    if not light:
        return (0,) * 64
    row = light[0] // 8
    col = min(index % 8 for index in light)
    pivot = 8 * row + col
    occupied = {index - pivot for index in light}
    return tuple(int(index in occupied) for index in range(64))


def sensor_view(name, raw):
    if name == "position":
        return relative_pixels(raw)
    if name in ("window_tree", "window_group"):
        return window_counts(raw)
    raise ValueError(f"Unknown sense {name}")


def impurity(samples):
    """Weighted binary Gini loss without the common factor two / total samples."""
    zeroes, ones = samples
    return Fraction(zeroes * ones, zeroes + ones)


def ranked_splits(panel):
    label_counts = Counter(label for _, label in panel)
    ranking = []
    for category in range(len(panel[0][0])):
        by_value = {}
        for features, label in panel:
            by_value.setdefault(features[category], Counter())[label] += 1
        left_label = Counter()
        thresholds = sorted(by_value)
        for upper in thresholds[:-1]:
            left_label.update(by_value[upper])
            right = (label_counts[0] - left_label[0], label_counts[1] - left_label[1])
            joint = impurity((left_label[0], left_label[1])) + impurity(right)
            ranking.append((joint, category, upper))
    return sorted(ranking)


def fit_tree(rows, targets, *, depth_limit=3):
    inputs = tuple(zip(rows, targets, strict=True))
    require(bool(inputs), "Need positive synthetic or released training support")
    def fit(panel, depth):
        label_counts = Counter(label for _, label in panel)
        majority = {"vote": int(label_counts[1] > label_counts[0])}
        baseline = impurity((label_counts[0], label_counts[1]))
        if depth >= depth_limit or baseline == 0:
            return majority
        eligible = ranked_splits(panel)
        if not eligible or eligible[0][0] >= baseline:
            return majority
        _, category, threshold = eligible[0]
        sides = ([row for row in panel if row[0][category] <= threshold],
                 [row for row in panel if row[0][category] > threshold])
        return {"feature": category, "threshold": threshold, "left": fit(sides[0], depth + 1), "right": fit(sides[1], depth + 1)}

    return fit(inputs, 0)


def route(tree, feature):
    path = []
    index = 0
    while "vote" not in tree:
        dimension, margin = tree["feature"], tree["threshold"]
        value = feature[dimension]
        side = "left" if value <= margin else "right"
        path.append((index, dimension, margin, value, side))
        tree = tree[side]
        index = index * 2 + (1 if side == "left" else 2)
    return tree["vote"], index, path


def tree_memory(law, sensor, binary):
    encoded = bytes(binary).translate(bytes.maketrans(b"\x00\x01", bytes(PREPARED[law]))).hex()
    return {"schema": "pixel-knot-tree-v1", "law": law, "sensor": sensor, "training_limit": TRAINING_LIMIT, "words": encoded}


def tree_prefix(raw_images, actions, sensor):
    held = bytearray(TREE_HOLDINGS)
    receipts = Counter()
    before = {law: hash_memory(tree_memory(law, sensor, held)) for law in PREPARED}
    for index, (raw, target) in enumerate(zip(raw_images, actions, strict=True)):
        guess = int(receipts[1] > receipts[0])
        correct = guess == target
        earned = guess ^ int(not correct)
        cursor = 1 + 66 * index
        held[cursor:cursor + 66] = bytes([1, earned, *map(int, raw)])
        receipts[earned] += 1
        after = {law: hash_memory(tree_memory(law, sensor, held)) for law in PREPARED}
        yield guess, correct, before, after
        before = after


def tree_archive(model, law, sensor):
    binary = bytearray(TREE_HOLDINGS)
    binary[0] = 1

    def populate(node, i):
        cursor = TREE_BASE + 15 * i
        if "vote" in node:
            write_value(binary, cursor, 2, 1 + node["vote"])
            return
        write_value(binary, cursor, 2, 3)
        write_value(binary, cursor + 2, 6, node["feature"])
        write_value(binary, cursor + 8, 7, node["threshold"])
        populate(node["left"], 2 * i + 1)
        populate(node["right"], 2 * i + 2)

    populate(model, 0)
    return tree_memory(law, sensor, binary)
