"""Check phase identifiability directly on all rejoining forks in the earlier switch.

This is a coordinator audit of the frozen two-load comparison. For two input
words a fine output o has an off-diagonal bounded by sqrt(p_o q_o). Complete
output effects sum to I. An LP maximizes the signed contrast without assuming
any amplitudes or implementing a knot measurement. Counts are a finite census.
"""
import gzip
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from pathlib import Path

from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parents[2]
PREVIOUS = "SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A"
ARCHIVE = ROOT / "artifacts" / PREVIOUS / (PREVIOUS + "-E001_sign_records") / "archived_events.json.gz"


@lru_cache(maxsize=None)
def sharp_bound(probabilities):
    """Return the maximum plus-versus-minus chance difference on this pool."""
    widths = [math.sqrt(p*q) for p, q, _ in probabilities]
    objective = [-2.0 if selected else 0.0 for _, _, selected in probabilities]
    result = linprog(objective, A_eq=[[1.0] * len(widths)], b_eq=[0.0],
                     bounds=[(-w, w) for w in widths], method="highs")
    assert result.success, result.message
    optimum = -result.fun
    direct = 2 * min(sum(w for w, (_, _, chosen) in zip(widths, probabilities) if chosen == take)
                     for take in (False, True))
    assert math.isclose(optimum, direct, abs_tol=1e-10)
    return round(optimum, 12) or 0.0


def chances(events, target, partition):
    weights = defaultdict(Fraction)
    for event in events:
        dest = event["target"]
        if partition == "arrival":
            output = (dest == target,)
        elif partition == "word":
            output = (dest == target, dest)
        else:
            output = (dest == target, dest, event["event_id"])
        weights[output] += Fraction(event["chance_given_source"])
    assert sum(weights.values()) == 1
    return weights


def audit(trace):
    nodes = {row["id"]: row for row in trace["nodes"]}
    functions = ("arrival", "word", "word_and_event")
    bounds = {part: Counter() for part in functions}
    earliest = None
    examples = {}
    for fork in sorted(nodes.values(), key=lambda n: (n["depth"], n["id"])):
        mids = sorted({e["target"] for e in fork["enabled_events"]})
        for a, b in combinations(mids, 2):
            draws = [nodes[x]["enabled_events"] for x in (a, b)]
            common = {e["target"] for e in draws[0]} & {e["target"] for e in draws[1]}
            for endpoint in sorted(common):
                numbers = []
                for partition in functions:
                    p, q = [chances(events, endpoint, partition) for events in draws]
                    probabilities = tuple(sorted((p[o], q[o], o[0]) for o in p.keys() | q.keys()))
                    cap = sharp_bound(probabilities)
                    numbers.append(cap)
                    bounds[partition][str(cap)] += 1
                assert numbers[0] >= numbers[1] >= numbers[2]
                example = dict(depth=fork["depth"], fork=fork["id"], inputs=[a, b],
                               endpoint=endpoint, bounds=dict(zip(functions, numbers)))
                if earliest is None:
                    earliest = example
                if numbers[0] and not numbers[1]:
                    examples.setdefault("coarse_only", example)
                if numbers[1]:
                    examples.setdefault("current_word_allows_contrast", example)
    return dict(earliest=earliest, examples=examples, tested=sum(bounds["arrival"].values()), bounds=bounds)


if __name__ == "__main__":
    with gzip.open(ARCHIVE, "rt") as stream:
        data = json.load(stream)
    print(json.dumps([audit(arm["traces"]["loaded"]) for arm in data["uniform_switch"]["directions"]],
                     indent=2, sort_keys=True))
