"""Recount the registered orders from the finished assignments and rule prefixes."""

import argparse
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
import json
from math import lcm
from pathlib import Path
import random

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REGISTRATION = ROOT / "research/TWO-COUNTINGS-20261125-001A"
RECORDED = (
    ROOT / "artifacts/TWO-COUNTINGS-20261125-001A"
    / "TWO-COUNTINGS-20261125-001A-E001_two_countings/part6_orders.json"
)
PAIRS = tuple(product(range(2), repeat=2))
RECORDS = (("x1", "x2", "x3", "za"), ("y1", "y2", "y3", "zb"))
OPTIONS = (("x2", "x3"), ("y2", "y3"))
ORDINARY_STARTS = {
    "eleven_registered_400": "eleven (start)",
    "eleven_new_400": "eleven (start)",
    "smallest_gain_400": "smallest gain: part + rule-Q round 1",
}


def rule_satisfied(states, law, mask):
    values = states & mask
    if law == "nae":
        return (values != 0) & (values != mask)
    assert law in ("even", "odd")
    parity = np.zeros_like(states)
    while mask:
        bit = mask & -mask
        parity ^= (values & bit) != 0
        mask ^= bit
    return parity == int(law == "odd")


@dataclass
class WeightedRecords:
    table: np.ndarray
    kept: Fraction
    loss_positions: tuple


class Finished:
    def __init__(self, rules):
        self.rules = rules
        names = sorted({name for _, places in rules for name in places})
        self.name_bit = {name: 1 << i for i, name in enumerate(names)}
        self.width = len(names)
        self.masks = [sum(self.name_bit[name] for name in places) for _, places in rules]
        assignments = np.arange(1 << self.width, dtype=np.int64)
        relations = [
            rule_satisfied(assignments, law, mask)
            for (law, _), mask in zip(rules, self.masks, strict=True)
        ]
        allowed = np.logical_and.reduce(relations)
        self.states = assignments[allowed]
        self.rule_sets = [
            int.from_bytes(np.packbits(relation, bitorder="little").tobytes(), "little")
            for relation in relations
        ]
        self.prefix_sets = {0: (1 << assignments.size) - 1}
        codes = []
        for record in RECORDS:
            code = np.zeros_like(self.states)
            for i, name in enumerate(record):
                code |= ((self.states & self.name_bit[name]) != 0).astype(np.int64) << i
            codes.append(code)
        self.record_cells = 16 * codes[0] + codes[1]

    def completions(self, law, fresh, old):
        if not fresh:
            # Every finished assignment has already passed this rule.
            return 1, 1
        if law != "nae":
            return 1 << (fresh - 1), 1 << (fresh - 1)
        if not old:
            count = (1 << fresh) - 2
            return count, count
        count = 1 << fresh
        if old.bit_count() == 1:
            return count - 1, count - 1
        return count, count - 1

    def history(self, order, mixed_at):
        width_mask = 0
        rule_prefix = 0
        possible = self.prefix_sets[0]
        factors = np.ones(self.states.size, dtype=np.int64)
        scale = 1
        mixed_factors = np.ones_like(factors)
        mixed_scale = 1
        mixed_start_count = 0
        loss_positions = []
        for position, index in enumerate(order):
            rule_set = self.rule_sets[index]
            mask = self.masks[index]
            law = self.rules[index][0]
            fresh = (mask & ~width_mask).bit_count()
            old = mask & width_mask
            if not fresh and possible & ~rule_set:
                loss_positions.append(position)
            common, monochrome = self.completions(law, fresh, old)
            new_scale = lcm(common, monochrome)
            if common == monochrome:
                factor = 1
            else:
                old_values = self.states & old
                same = (old_values == 0) | (old_values == old)
                factor = np.where(same, new_scale // monochrome, new_scale // common)
            scale *= new_scale
            factors *= factor
            if position > mixed_at:
                mixed_scale *= new_scale
                mixed_factors *= factor
            width_mask |= mask
            rule_prefix |= 1 << index
            if rule_prefix not in self.prefix_sets:
                self.prefix_sets[rule_prefix] = possible & rule_set
            possible = self.prefix_sets[rule_prefix]
            if position == mixed_at:
                mixed_start_count = possible.bit_count() >> (self.width - width_mask.bit_count())

        def weighted_records(numerators, denominator, positions):
            assert 0 < denominator < 2**62
            table = np.zeros(256, dtype=np.int64)
            np.add.at(table, self.record_cells, numerators)
            kept = Fraction(int(table.sum()), denominator)
            assert 0 < kept <= 1
            assert (kept < 1) == bool(positions)
            return WeightedRecords(table.reshape(16, 16), kept, tuple(positions))

        return (
            weighted_records(factors, scale, loss_positions),
            weighted_records(mixed_factors, mixed_scale * mixed_start_count,
                             [position for position in loss_positions if position > mixed_at]),
        )


def total_variation(left, right, denominator):
    return Fraction(int(np.abs(left - right).sum()), 2 * denominator)


def signs(width):
    encodings = np.arange(1 << width, dtype=np.int64)[:, None]
    return 1 - 2 * ((encodings >> np.arange(width)) & 1)


PARITIES = np.array([
    [(-1) ** (mask & code).bit_count() for code in range(16)]
    for mask in range(1, 16)
], dtype=np.int64)


def best_all(tables):
    # For unrestricted signed outcomes, flipping one observer's outcomes for
    # an entire setting moves a minus sign without changing the optimum.
    a_support = tuple(np.flatnonzero(sum(tables[a, b].sum(axis=1) for b in range(2)))
                      for a in range(2))
    b_support = tuple(np.flatnonzero(sum(tables[a, b].sum(axis=0) for a in range(2)))
                      for b in range(2))
    if sum(map(len, a_support)) > sum(map(len, b_support)):
        tables = {(a, b): tables[b, a].T for a, b in PAIRS}
        a_support = b_support
    left = signs(len(a_support[0]))
    # Fix one overall sign, since both signs of the response are available.
    right = signs(len(a_support[1]))[::2]
    left_by_b = [left @ tables[0, b][a_support[0]] for b in range(2)]
    right_by_b = [right @ tables[1, b][a_support[1]] for b in range(2)]
    best = 0
    for start in range(0, len(left), 16):
        score = np.abs(left_by_b[0][start:start + 16, None] + right_by_b[0]).sum(axis=2)
        score += np.abs(left_by_b[1][start:start + 16, None] - right_by_b[1]).sum(axis=2)
        best = max(best, int(score.max()))
    return best


def best_parities(tables):
    correlations = {pair: PARITIES @ tables[pair] @ PARITIES.T for pair in PAIRS}
    signed, absolute = None, 0
    for negative in PAIRS:
        side = [
            ((-1 if negative == (0, b) else 1) * correlations[0, b])[:, None, :]
            + ((-1 if negative == (1, b) else 1) * correlations[1, b])[None, :, :]
            for b in range(2)
        ]
        high = int((side[0].max(axis=2) + side[1].max(axis=2)).max())
        low = int((side[0].min(axis=2) + side[1].min(axis=2)).min())
        signed = max(signed, high) if signed is not None else high
        absolute = max(absolute, high, -low)
    return signed, absolute


def score(histories):
    totals = {pair: int(history.table.sum()) for pair, history in histories.items()}
    denom = lcm(*totals.values())
    assert denom < 2**61
    tables = {pair: history.table * (denom // totals[pair]) for pair, history in histories.items()}
    first = max(total_variation(tables[a, 0].sum(axis=1), tables[a, 1].sum(axis=1), denom)
                for a in range(2))
    second = max(total_variation(tables[0, b].sum(axis=0), tables[1, b].sum(axis=0), denom)
                 for b in range(2))
    signed, absolute = best_parities(tables)
    return {
        "score_all": str(Fraction(best_all(tables), denom)),
        "score_parity": str(Fraction(signed, denom)),
        "score_parity_abs": str(Fraction(absolute, denom)),
        "change_first": str(first),
        "change_second": str(second),
        "hidden": first == second == 0,
        "weight lost": {str(pair): str(1 - history.kept) for pair, history in histories.items()},
        "weight loss positions": {str(pair): history.loss_positions for pair, history in histories.items()},
        "weight lost equally across the setting pairs": len({h.kept for h in histories.values()}) == 1,
        "any weight lost": any(h.kept < 1 for h in histories.values()),
    }


def order_class(order, base_rules):
    held = set()
    meets = []
    for index in order:
        if index < len(base_rules):
            held.update(base_rules[index][1])
            continue
        side = index - len(base_rules)
        older = RECORDS[side][:1]
        options = OPTIONS[side]
        common = {older[0], RECORDS[side][-1]}
        meets.append((side, {*older, *options} <= held and RECORDS[side][-1] not in held))
        held.update(common)
    return dict(zip(("first setting knot", "second setting knot"), (v for _, v in sorted(meets))))


def check_by_forward_enumeration(end, order, mixed_at, histories):
    whole = {0: Fraction(1)}
    mixed = None
    held = 0
    for position, index in enumerate(order):
        law, names = end.rules[index]
        places = [end.name_bit[name] for name in names]
        new = [bit for bit in places if not (held & bit)]
        assignments = [sum(subset) for subset in product(*((0, bit) for bit in new))]
        next_whole = {}
        next_mixed = {}
        for old, weight in whole.items():
            allowed = []
            for padding in assignments:
                state = old | padding
                ones = sum(bool(state & bit) for bit in places)
                retains = 0 < ones < len(places) if law == "nae" else ones % 2 == int(law == "odd")
                if retains:
                    allowed.append(state)
            for state in allowed:
                next_whole[state] = weight / len(allowed)
                if mixed is not None:
                    next_mixed[state] = mixed[old] / len(allowed)
        whole = next_whole
        if position == mixed_at:
            mixed = dict.fromkeys(whole, Fraction(1, len(whole)))
        elif mixed is not None:
            mixed = next_mixed
        held |= sum(places)

    for weights, backward in zip((whole, mixed), histories, strict=True):
        direct = Counter()
        for state, weight in weights.items():
            records = [
                sum(1 << i for i, name in enumerate(record) if state & end.name_bit[name])
                for record in RECORDS
            ]
            direct[tuple(records)] += weight
        kept = sum(direct.values())
        assert kept == backward.kept
        cells = int(backward.table.sum())
        for ab in product(range(16), repeat=2):
            assert direct[ab] / kept == Fraction(int(backward.table[ab]), cells)


def summarize(rows):
    in_class = [row for row in rows if row["in class"]]
    outside = [row for row in rows if not row["in class"]]
    finish = lambda row: (Fraction(row["score_all"]), row["hidden"])
    hidden_baseline = lambda row: finish(row) == (2, True)
    above = lambda row: finish(row)[0] > 2
    hidden_outside = [row for row in outside if row["hidden"] and above(row)]
    maximum = max((finish(row)[0] for row in hidden_outside), default=None)
    largest = max((finish(row)[0] for row in outside), default=None)
    mixed_counts = Counter(
        (row["mixed from after first setting"]["score_all"], row["mixed from after first setting"]["hidden"])
        for row in rows
    )
    return {
        "orders": len(rows),
        "in the class": len(in_class),
        "in the class: at 2 and hidden": sum(map(hidden_baseline, in_class)),
        "in the class: losing weight at some rule": sum(row["any weight lost"] for row in in_class),
        "in the class: equal weight loss across the four setting pairs": sum(
            row["weight lost equally across the setting pairs"] for row in in_class
        ),
        "in the class: no loss, indices": [row["index"] for row in in_class if not row["any weight lost"]],
        "outside: at 2, hidden": sum(map(hidden_baseline, outside)),
        "outside: above 2, hidden": len(hidden_outside),
        "outside: above 2, not hidden": sum(above(row) and not row["hidden"] for row in outside),
        "outside: largest score": str(largest) if largest is not None else None,
        "outside: largest score, indices": [row["index"] for row in outside if finish(row)[0] == largest],
        "outside: largest hidden score": str(maximum) if maximum is not None else None,
        "outside: largest hidden score, indices": [
            row["index"] for row in hidden_outside if finish(row)[0] == maximum
        ],
        "outside: above 2, hidden, equal loss": [
            row["index"] for row in hidden_outside if row["weight lost equally across the setting pairs"]
        ],
        "in the class: above 2 from the mixed stage": [
            row["index"] for row in in_class
            if Fraction(row["mixed from after first setting"]["score_all"]) > 2
        ],
        "mixed scores and hidden, counts": {str(key): value for key, value in mixed_counts.items()},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="check this many orders from each list")
    parser.add_argument("--output", type=Path, default=HERE / "orders.json")
    args = parser.parse_args()
    structures = json.loads((REGISTRATION / "structures.json").read_text())
    order_lists = json.loads((REGISTRATION / "construction_orders.json").read_text())
    recorded = {
        (row["list"], row["index"]): row for row in json.loads(RECORDED.read_text())["rows"]
    }
    summaries = {}
    rows = []
    disagreements = []
    forward_controls = []
    for list_name, structure in ORDINARY_STARTS.items():
        base_rules = structures[structure]
        supplied = order_lists[list_name]
        cases = supplied["orders"][:args.limit]
        rand = random.Random(supplied["seed"])
        finished = {
            (a, b): Finished(base_rules + [
                ["nae", ["x1", OPTIONS[0][a], "za"]],
                ["nae", ["y1", OPTIONS[1][b], "zb"]],
            ])
            for a, b in PAIRS
        }
        list_rows = []
        for index, order in enumerate(cases):
            regenerated = list(range(len(base_rules) + 2))
            rand.shuffle(regenerated)
            assert order == regenerated
            mixed_at = min(order.index(len(base_rules) + side) for side in range(2))
            histories = {pair: end.history(order, mixed_at) for pair, end in finished.items()}
            if index in (0, 11) or (list_name == "smallest_gain_400" and index == 279):
                for pair, end in finished.items():
                    check_by_forward_enumeration(end, order, mixed_at, histories[pair])
                forward_controls.append([list_name, index])
            classification = order_class(order, base_rules)
            row = {"list": list_name, "index": index, "order": order,
                   "in class": all(classification.values()), "class detail": classification}
            row.update(score({pair: history[0] for pair, history in histories.items()}))
            if row["in class"]:
                row["verdict"] = ("in the class, at 2, hidden" if row["score_all"] == "2" and row["hidden"]
                                  else "in the class, P4 fails")
            else:
                row["verdict"] = "outside the class"
            for key, value in row.items():
                if key in recorded[list_name, index] and value != recorded[list_name, index][key]:
                    disagreements.append([list_name, index, key, value, recorded[list_name, index][key]])
            row["mixed first setting"] = "first observer" if order[mixed_at] == len(base_rules) else "second observer"
            row["mixed from after first setting"] = score({pair: history[1] for pair, history in histories.items()})
            list_rows.append(row)
        summaries[list_name] = summarize(list_rows)
        rows.extend(list_rows)

    result = {
        "comparison": "Exact probabilities after renormalising each history's surviving weight.",
        "mixed": "Exploratory. Starts just after the first setting rule. That stage is common only to pairs sharing that setting.",
        "indices": "Zero-based within a list or order.",
        "orders checked also by forward enumeration": forward_controls,
        "P4 holds on orders checked": all(not r["in class"] or (r["score_all"] == "2" and r["hidden"]) for r in rows),
        "disagreements with recorded rows": disagreements,
        "summary": summaries,
        "rows": rows,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"{len(rows)} orders, {len(disagreements)} differences from recorded rows")
    if disagreements:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
