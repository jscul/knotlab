"""Check the scope of the two-holder claim and bound functions on the archived tables.

For any two allowed words, pick a differing loose distinction. Within its
knot, change its value toward the second word. A parity knot can change one
more differing distinction to restore parity. In a not-all-equal knot this
is needed only when the first change makes the local word constant. If that
second distinction has another holder, repair it there in the same way.
Every change of a local occurrence is toward the chosen target, so this
process ends. It has changed the starting loose distinction and at most one
other visible loose distinction. The reference's eight allowed records fail
this necessary condition on the six loose distinctions.

For the function check, write each nonzero row of the old table M as a
positive integer c_x times a primitive vector R_g, grouped by that vector.
Within a group the present-word counts factor into c_x times the local
birth factor on the first side and R_g(y) times the local birth factor on
the second. Check, with integers, that the normalized mass of each group
is identical for all four setting pairs. When it is, the common group
weighting and these local conditional distributions reproduce the four
complete-record tables. This bounds every two-valued outcome by 2.
"""

import argparse
import json
import math
import time
from collections import Counter
from itertools import product
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = ROOT / "artifacts/REVIEW-LEADS-20261123-001C/REVIEW-LEADS-20261123-001C-E001_present_words"
OLD = list(product(range(2), repeat=3))
WEIGHTS = np.array([[1 + (x[0] != x[1 + a]) for x in OLD] for a in range(2)])


def exchange_fails(allowed, start, target, first):
    different = [i for i, (a, b) in enumerate(zip(start, target)) if a != b]
    assert first in different
    for other in different:
        revised = list(start)
        for index in {first, other}:
            revised[index] = target[index]
        if tuple(revised) in allowed:
            return False
    return True


def support_checks():
    counts = {}
    for width in (3, 4):
        words = list(product(range(2), repeat=width))
        for name, rule in (
            ("even", lambda w: sum(w) % 2 == 0),
            ("odd", lambda w: sum(w) % 2 == 1),
            ("not_all_equal", lambda w: len(set(w)) > 1),
        ):
            allowed = {w for w in words if rule(w)}
            checks = 0
            for start, target in product(allowed, repeat=2):
                for i in range(width):
                    if start[i] != target[i]:
                        assert not exchange_fails(allowed, start, target, i)
                        checks += 1
            counts[f"{name}_{width}"] = checks

    recorded = json.loads((ARCHIVE / "reference_final.json").read_text())["M"]
    support = {x + y for ix, x in enumerate(OLD) for iy, y in enumerate(OLD) if recorded[ix][iy]}
    start = (0, 0, 1, 0, 0, 1)
    target = (0, 1, 0, 0, 1, 0)
    assert start in support and target in support
    assert exchange_fails(support, start, target, 4)
    return {
        "local_differing_place_checks": counts,
        "reference_allowed_old_pairs": len(support),
        "allowed_old_pairs": ["001,001", "010,010"],
        "required_change": "Bob's middle distinction",
        "remaining_candidate_absent": (0, 0, 1, 0, 1, 0) not in support,
    }


def proportional(v, w):
    return bool((v * sum(w) == w * sum(v)).all())


def has_common_group_weighting(matrix):
    """Check equality of all four group marginals with exact cross products."""
    counts = {}
    for i, row in enumerate(matrix):
        scale = math.gcd(*map(int, row))
        if not scale:
            continue
        profile = tuple(row // scale)
        a, b = counts.get(profile, (0, 0))
        counts[profile] = (a + int(WEIGHTS[0, i]) * scale, b + int(WEIGHTS[1, i]) * scale)
    group_masses = []
    for profile, own_weights in counts.items():
        far_weights = WEIGHTS @ profile
        group_masses.append(
            [own_weights[a] * int(far_weights[b]) for a, b in product(range(2), repeat=2)]
        )
    totals = list(map(sum, zip(*group_masses)))
    return all(
        all(mass * totals[0] == masses[0] * total for mass, total in zip(masses, totals))
        for masses in group_masses
    )


def assess_archive(limit):
    with np.load(ARCHIVE / "extras_c2_tables.npz") as source:
        records = source["M"]
        from_smaller_census = source["in_census"]
    counts = Counter()
    unresolved = []
    for idx, matrix in enumerate(records[:limit]):
        matrix = matrix.astype(np.int64)
        assert all(proportional(m @ WEIGHTS[0], m @ WEIGHTS[1]) for m in (matrix, matrix.T))
        left, right = [has_common_group_weighting(m) for m in (matrix, matrix.T)]
        if left and right:
            counts["either_observer"] += 1
        elif left:
            counts["first_observer_only"] += 1
        elif right:
            counts["second_observer_only"] += 1
        else:
            unresolved.append(idx)
    reference = np.asarray(json.loads((ARCHIVE / "reference_final.json").read_text())["M"])
    ref_checks = [has_common_group_weighting(m) for m in (reference, reference.T)]
    assert not any(ref_checks)
    return {
        "archive_tables": len(records),
        "tables_checked": len(records[:limit]),
        "distinct_tables_checked": len({m.tobytes() for m in records[:limit]}),
        "in_smaller_census": int(from_smaller_census[:limit].sum()),
        "local_explanation_counts": counts,
        "unresolved_indices": unresolved,
        "reference_control_has_common_group_weighting": ref_checks,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    started = time.process_time()
    output = {"support_exchange": support_checks(), "two_shared_distinctions": assess_archive(args.limit)}
    output["cpu_seconds_inside_check"] = round(time.process_time() - started, 3)
    print(json.dumps(output, indent=2))
