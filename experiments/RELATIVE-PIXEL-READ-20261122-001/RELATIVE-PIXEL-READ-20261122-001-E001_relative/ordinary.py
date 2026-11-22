"""Independent exact CART for the two frozen pixel sensors."""

from copy import deepcopy
from fractions import Fraction
from itertools import product
from operator import index


TRAINING_LIMIT = 64
MAX_DEPTH = 3
MEMORY_SCHEMA = "relative-pixel-integer-tree-v1"
IMAGE_SIDE = 8


def _pixels(pixels):
    reader = int if isinstance(pixels, str) else index
    bits = tuple(map(reader, pixels))
    if len(bits) != IMAGE_SIDE ** 2 or any(bit not in (0, 1) for bit in bits):
        raise ValueError("expected a row-major bitmap of 64 bits")
    return bits


def position_features(pixels):
    """Read occupied positions relative to the minimum occupied row and column."""
    occupied = [divmod(offset, IMAGE_SIDE) for offset, bit in enumerate(_pixels(pixels)) if bit]
    features = [0] * (IMAGE_SIDE ** 2)
    if occupied:
        top = min(row for row, _ in occupied)
        left = min(col for _, col in occupied)
        for row, col in occupied:
            features[(row - top) * IMAGE_SIDE + col - left] = 1
    return features


def window_features(pixels):
    """Count all zero-padded two-by-two words in the predecessor's bit order."""
    bits = _pixels(pixels)
    counts = [0] * 16
    for row, col in product(range(-1, IMAGE_SIDE), repeat=2):
        word = 0
        for down, right in ((0, 0), (0, 1), (1, 0), (1, 1)):
            y, x = row + down, col + right
            word *= 2
            if 0 <= y < IMAGE_SIDE and 0 <= x < IMAGE_SIDE:
                word += bits[IMAGE_SIDE * y + x]
        counts[word] += 1
    return counts


_SENSORS = {
    "position": (position_features, 64, 1),
    "window": (window_features, 16, 81),
}


def _majority(rows):
    return int(2 * sum(action for _, action in rows) > len(rows))


def _impurity(rows):
    total = len(rows)
    ones = sum(action for _, action in rows)
    return Fraction(2 * ones * (total - ones), total ** 2)


def _grow(rows, feature_count, depth=0):
    vote = _majority(rows)
    if depth == MAX_DEPTH:
        return {"vote": vote}
    parent_impurity = _impurity(rows)
    if parent_impurity == 0:
        return {"vote": vote}

    best_gain, best = Fraction(0), None
    for feature in range(feature_count):
        observed = sorted({values[feature] for values, _ in rows})
        for threshold in observed[:-1]:
            children = ([], [])
            for sample in rows:
                children[sample[0][feature] > threshold].append(sample)
            weighted = sum(len(child) * _impurity(child) for child in children) / len(rows)
            gain = parent_impurity - weighted
            # Ascending feature and threshold order settles exact positive-gain ties.
            if gain > best_gain:
                best_gain = gain
                best = feature, threshold, children

    if best is None:
        return {"vote": vote}
    feature, threshold, (left, right) = best
    return {"feature": feature, "threshold": threshold,
            "left": _grow(left, feature_count, depth + 1), "right": _grow(right, feature_count, depth + 1)}


def _validate_tree(node, feature_count, max_value, depth=0):
    if not isinstance(node, dict):
        raise ValueError("invalid saved decision tree node")
    if node.keys() == {"vote"} and type(node["vote"]) is int and node["vote"] in (0, 1):
        return
    if depth >= MAX_DEPTH or node.keys() != {"feature", "threshold", "left", "right"}:
        raise ValueError("invalid saved decision tree structure")
    feature, threshold = node["feature"], node["threshold"]
    if (type(feature) is not int or not 0 <= feature < feature_count
            or type(threshold) is not int or not 0 <= threshold < max_value):
        raise ValueError("invalid saved feature or threshold")
    for branch in ("left", "right"):
        _validate_tree(node[branch], feature_count, max_value, depth + 1)


class IntegerTree:
    """Train once from pixels and earned action bits inferred from feedback."""

    def __init__(self, sensor):
        if not isinstance(sensor, str) or sensor not in _SENSORS:
            raise ValueError("unknown pixel sensor")
        self._sensor = sensor
        self._training = []
        self._tree = None

    def predict(self, pixels):
        if self._tree is None:
            return _majority(self._training)
        return self.explain(pixels)["guess"]

    def learn(self, pixels, guess, correct):
        if self._training is None or len(self._training) >= TRAINING_LIMIT:
            raise ValueError("the 64-receipt acquisition is complete")
        if (type(guess) not in (int, bool) or guess not in (0, 1)
                or type(correct) not in (int, bool) or correct not in (0, 1)):
            raise ValueError("guess and correctness must be bits")
        if guess != _majority(self._training):
            raise ValueError("feedback must refer to the current acquisition guess")
        sense, _, _ = _SENSORS[self._sensor]
        self._training.append((sense(pixels), int(guess) ^ int(not correct)))

    def finalize(self):
        if self._training is None or len(self._training) != TRAINING_LIMIT:
            raise ValueError("fitting requires one complete acquisition of 64 receipts")
        _, feature_count, _ = _SENSORS[self._sensor]
        self._tree = _grow(self._training, feature_count)
        self._training = None
        return self.describe()

    def describe(self):
        if self._tree is None:
            raise ValueError("the decision tree has not been fitted")
        return deepcopy(self._tree)

    def explain(self, pixels):
        sense, _, _ = _SENSORS[self._sensor]
        features = sense(pixels)
        path = []
        node = self._tree
        if node is None:
            return {"guess": _majority(self._training), "features": features, "path": path}
        while "vote" not in node:
            feature, threshold = node["feature"], node["threshold"]
            value = features[feature]
            branch = "left" if value <= threshold else "right"
            path.append({"feature": feature, "threshold": threshold, "value": value, "branch": branch})
            node = node[branch]
        return {"guess": node["vote"], "features": features, "path": path}

    def export_memory(self):
        return {"schema": MEMORY_SCHEMA, "sensor": self._sensor, "tree": self.describe()}

    @classmethod
    def from_memory(cls, memory):
        if (not isinstance(memory, dict) or memory.keys() != {"schema", "sensor", "tree"}
                or memory["schema"] != MEMORY_SCHEMA):
            raise ValueError("invalid integer tree memory schema")
        model = cls(memory["sensor"])
        _, feature_count, max_value = _SENSORS[model._sensor]
        _validate_tree(memory["tree"], feature_count, max_value)
        model._tree = deepcopy(memory["tree"])
        model._training = None
        return model
