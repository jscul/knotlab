"""Average every equally preferred action, for exactly the recorded three Q tables."""

import json
import sys
from fractions import Fraction
from functools import cache
from itertools import product
from pathlib import Path


TICKET = "LOCAL-RULE-ACTIONS-20261114-001"
FAMILY = TICKET + "-E001_local_policy"
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / TICKET / FAMILY))
from job import Config, train


def exact_rates(table, availability):
    """Independent state transitions for the already checked signed parity family."""
    @cache
    def success(signs, target, budget):
        can_fuse = budget > 0 and len(signs) >= 2
        legal = ("keep", "flip", "fuse:0") if can_fuse else ("keep", "flip")
        key = (target, int(budget > 0) if availability else budget,
               signs[:2], len(signs) <= 2, legal)
        values = table.get(key, {})
        best = max(values.get(action, 0.0) for action in legal)
        tied = [a for a in legal if abs(values.get(a, 0.0) - best) <= 1e-12]
        total = Fraction(0)
        for action in tied:
            if action == "fuse:0":
                reduced = (signs[0] ^ signs[1],) + signs[2:]
                total += success(reduced, target, budget - 1)
            else:
                total += ((sum(signs) + (action == "flip")) % 2 == target)
        return total / len(tied)

    rates = {}
    for n in (3, 4, 5):
        for budget in sorted({1, n - 2}):
            scores = [success(signs, target, budget)
                      for signs in product((0, 1), repeat=n) for target in (0, 1)]
            rates[n, budget] = sum(scores, Fraction(0)) / len(scores)
    return rates


def main():
    result_file = ROOT / "artifacts" / TICKET / FAMILY / "results.jsonl"
    rows = [json.loads(line) for line in result_file.read_text().splitlines()]
    result = next(row["result"] for row in rows if row["case"] == "sight-1-action-1")
    for trial in result["trials"]:
        q, fit = train(Config(), trial["seed"])
        if fit["trained_q_sha256"] != trial["training"]["trained_q_sha256"]:
            raise ValueError("Original fitted table did not reproduce")
        if len(q.q) != 16:
            raise ValueError("Unexpected number of local states during fitting")
        for key, values in q.q.items():
            target, remaining, signs, end_in_view, legal = key
            wanted = "fuse:0"
            if end_in_view:
                wanted = "keep" if sum(signs) % 2 == target else "flip"
            if len(signs) != 2 or bool(remaining) == end_in_view:
                raise ValueError(("Unexpected local state", key))
            if any(values.get(wanted, 0.0) - values.get(other, 0.0) <= 1e-12
                   for other in legal if other != wanted):
                raise ValueError(("Ambiguous fitted action", key, wanted, values))
        counted = exact_rates(q.q, availability=False)
        available = exact_rates(q.q, availability=True)
        for (length, budget), a in counted.items():
            b = available[length, budget]
            expected = Fraction(1, 2) if budget < length - 2 else (
                Fraction(1, 2) + Fraction(1, 2 * 3 ** (length - 3)))
            if a != expected or b != (Fraction(1, 2) if budget < length - 2 else 1):
                raise ValueError((trial["seed"], length, budget, a, b))
            print(f"seed {trial['seed']}, rules {length}, fold budget {budget}: "
                  f"exact count {a}, availability {b}")


if __name__ == "__main__":
    main()
