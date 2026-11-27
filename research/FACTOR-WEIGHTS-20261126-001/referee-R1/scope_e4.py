"""Check the two setting rules with one shared fresh distinction on the eleven-rule start.

The old parity rules give x3=1-x2, c=1-x1, s1=1-y1 and s2=1-y2.
The divisor is two exactly when both old setting pairs differ. When x1 differs
from x2, c=x2 and the old rule NAE(c,x2,s1) forces y1=c. The two conditions
can then both be read on (c,x3,s2). When x1 differs from x3, c=x3 and the
old rule NAE(c,x3,s2) forces y2=c. Both conditions can be read on (c,x2,s1).

This check enumerates the original rules without substituting these identities.
The control removes the old rules and leaves the four input distinctions free.
"""

import argparse
import json
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2] / "TWO-COUNTINGS-20261125-001A" / "structures.json"
STRUCTURE = "eleven (start)"


def allows(law, values):
    if law == "nae":
        return min(values) != max(values)
    if law in ("even", "odd"):
        return sum(values) % 2 == int(law == "odd")
    raise ValueError(f"Unrecognised law {law}")


def allowed_start_states(rules):
    names = sorted({name for _, support in rules for name in support})
    for values in product((0, 1), repeat=len(names)):
        state = dict(zip(names, values))
        if all(allows(law, tuple(state[name] for name in support)) for law, support in rules):
            yield state


def completions(left, right):
    return {z for z in (0, 1) if allows("nae", (*left, z)) and allows("nae", (*right, z))}


def setting_result(rules, old_states, first, second):
    left_input = ("x2", "x3")[first]
    right_input = ("y2", "y3")[second]
    support = ("c", "x3", "s2") if first == 0 else ("c", "x2", "s1")
    assert ["nae", list(support)] in rules
    half_weight = {"010", "101"} if second == 0 else {"011", "100"}
    old_by_count = Counter()
    for state in old_states:
        left = state["x1"], state[left_input]
        right = state["y1"], state[right_input]
        choices = completions(left, right)
        old_by_count[len(choices)] += 1
        pattern = "".join(str(state[name]) for name in support)
        local_weight = Fraction(1, 2) if pattern in half_weight else Fraction(1)
        for z in (0, 1):
            divided = Fraction(1, len(choices)) if z in choices else Fraction(0)
            factored = local_weight * allows("nae", (*left, z)) * allows("nae", (*right, z))
            if divided != factored:
                raise AssertionError((first, second, state, z, divided, factored))

    kept = old_by_count[1] + old_by_count[2]
    return {
        "settings": [first, second],
        "old states by number of completions": {str(n): old_by_count[n] for n in range(3)},
        "allowed final states": old_by_count[1] + 2 * old_by_count[2],
        "single old rule carrying the divisor": list(support),
        "patterns with weight 1/2": sorted(half_weight),
        "other patterns before law indicators": "1",
        "renormalisation multiplier for the unit start weights": str(Fraction(1, kept)),
        "comparisons on allowed old states and both fresh values": 2 * len(old_states),
        "mismatches": 0,
    }


def free_input_control():
    table = []
    for x in (0, 1):
        row = []
        for y in (0, 1):
            choices = completions((0, x), (0, y))
            assert 1 in choices
            row.append(Fraction(1, len(choices)))
        table.append(row)
    determinant = table[0][0] * table[1][1] - table[0][1] * table[1][0]
    assert determinant == Fraction(-1, 2)
    return {
        "rules": [["x1", "x2", "z"], ["y1", "y2", "z"]],
        "law": "not-all-equal",
        "fixed": {"x1": 0, "y1": 0, "z": 1},
        "table rows": "x2 = 0, 1",
        "table columns": "y2 = 0, 1",
        "weights from one unit per old state": [[str(value) for value in row] for row in table],
        "determinant": str(determinant),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pilot", action="store_true", help="check the first setting pair")
    args = parser.parse_args()
    rules = json.loads(SOURCE.read_text())[STRUCTURE]
    old_states = list(allowed_start_states(rules))
    settings = [(0, 0)] if args.pilot else list(product((0, 1), repeat=2))
    result = {
        "source": str(SOURCE.relative_to(SOURCE.parents[2])),
        "start": STRUCTURE,
        "allowed start states": len(old_states),
        "start weight unit": "Each allowed start state has weight one before division.",
        "recorded shared-fresh example": [setting_result(rules, old_states, a, b) for a, b in settings],
        "shared-fresh control with otherwise free inputs": free_input_control(),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
