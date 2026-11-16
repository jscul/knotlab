"""Learn one public-example threshold for trying the fold before median search.

A training record contains a prefix of (six-bit input, label) pairs and two
costs in the same unit. median_cost and fold_cost are the complete paired
costs from the respective median and try-one-fold-then-median arms. The
caller meters acquiring those pairs, fitting, and deployment.
"""

from hashlib import sha256
from itertools import islice
import json
from math import fsum, isfinite


PREFIX_LENGTH = 8
MIN_TRAINING_RULES_PER_BRANCH = 4
FEATURE_NAMES = (
    "ones", "minority_labels", "closest_input_errors", "decreasing_pairs",
    "whole_parity_errors",
)


def _public_rows(prefix):
    rows = tuple((x, y) for x, y in islice(prefix, PREFIX_LENGTH))
    for x, y in rows:
        if type(x) is not int or not 0 <= x < 64:
            raise ValueError("a public input must be a six-bit integer")
        if type(y) not in (bool, int) or y not in (0, 1):
            raise ValueError("a public label must be a bit")
    if len({x for x, _ in rows}) != len(rows):
        raise ValueError("the public prefix must use distinct inputs")
    return rows


def _feature(name, rows):
    if name == "ones":
        return sum(y for _, y in rows)
    if name == "minority_labels":
        ones = sum(y for _, y in rows)
        return min(ones, len(rows) - ones)
    if name == "closest_input_errors":
        return min(sum(((x >> bit) & 1) != y for x, y in rows) for bit in range(6))
    if name == "decreasing_pairs":
        # Count ordered input pairs u <= v coordinatewise with labels 1 then 0.
        return sum((u & v) == u for u, a in rows if a for v, b in rows if not b)
    if name == "whole_parity_errors":
        return sum((x.bit_count() & 1) != y for x, y in rows)
    raise ValueError(f"unknown public feature {name!r}")


def features(prefix):
    """Return the five integer counts on the first eight distinct examples."""
    rows = _public_rows(prefix)
    if len(rows) != PREFIX_LENGTH:
        raise ValueError(f"features require {PREFIX_LENGTH} public examples")
    return {name: _feature(name, rows) for name in FEATURE_NAMES}


def _fires(value, rule):
    if rule["op"] == "<=":
        return value <= rule["limit"]
    if rule["op"] == ">=":
        return value >= rule["limit"]
    raise ValueError(f"unknown threshold operator {rule['op']!r}")


def decision(checkpoint, prefix):
    """Return True to try one fold. With a short prefix, use median search."""
    rule = checkpoint["rule"]
    if rule is None:
        return False
    rows = _public_rows(prefix)
    if len(rows) < PREFIX_LENGTH:
        return False
    return _fires(_feature(rule["feature"], rows), rule)


def checkpoint_sha256(checkpoint):
    """Hash canonical JSON of every checkpoint field except the digest itself."""
    payload = {key: value for key, value in checkpoint.items() if key != "sha256"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _cost(record, field):
    value = record[field]
    if type(value) not in (float, int) or value < 0 or (type(value) is float and not isfinite(value)):
        raise ValueError(f"{field} must be a nonnegative finite cost")
    return value


def fit(training_records):
    """Fit a one-threshold policy to total paired cost saved on training rules.

    Each branch needs four training rules. Positive savings win. At tied
    savings the policy with fewer fold attempts wins, then the first named
    feature, lower cut before upper cut, and smaller cutoff. Median search
    wins all zero-gain ties. No distinguishing split also leaves it in force.
    """
    measured = []
    for record in training_records:
        measured.append((features(record["prefix"]), _cost(record, "median_cost"),
                         _cost(record, "fold_cost")))
    total = sum if all(type(c) is int for _, m, f in measured for c in (m, f)) else fsum
    count = len(measured)
    best_rule = None
    best_savings = 0
    best_attempts = 0
    for name in FEATURE_NAMES:
        values = sorted({counts[name] for counts, _, _ in measured})
        # Use the closest observed firing value as the inclusive boundary.
        for op, thresholds in (("<=", values[:-1]), (">=", values[1:])):
            for limit in thresholds:
                rule = {"feature": name, "op": op, "limit": limit}
                gains = [m - f for counts, m, f in measured if _fires(counts[name], rule)]
                if min(len(gains), count - len(gains)) < MIN_TRAINING_RULES_PER_BRANCH:
                    continue
                savings = total(gains)
                if (savings, -len(gains)) > (best_savings, -best_attempts):
                    best_rule, best_savings, best_attempts = rule, savings, len(gains)
    selected_cost = total(
        f if best_rule and _fires(counts[best_rule["feature"]], best_rule) else m
        for counts, m, f in measured
    )
    checkpoint = {
        "schema_version": 1,
        "prefix_length": PREFIX_LENGTH,
        "min_training_rules_per_branch": MIN_TRAINING_RULES_PER_BRANCH,
        "rule": best_rule,
        "training": {
            "rules": count,
            "selected_fold_attempts": best_attempts,
            "selected_cost": selected_cost,
            "savings_vs_always_median": best_savings,
            "always_median_cost": total(m for _, m, _ in measured),
            "always_try_cost": total(f for _, _, f in measured),
            "per_rule_hindsight_min_cost": total(min(m, f) for _, m, f in measured),
        },
    }
    checkpoint["sha256"] = checkpoint_sha256(checkpoint)
    return checkpoint
