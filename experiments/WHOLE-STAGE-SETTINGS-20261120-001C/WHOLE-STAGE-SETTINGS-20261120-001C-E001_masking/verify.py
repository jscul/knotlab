"""Re-score the two-terminal counts and enacted grants from the physical receipt."""

from collections import Counter
from fractions import Fraction
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ARTIFACT = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name
PAIRS = tuple(product(range(2), repeat=2))
WORDS = tuple(product(range(2), repeat=3))


def named(pair):
    return "".join(str(bit) for bit in pair)


def variation(first, second):
    return sum(abs(first[label] - second[label]) for label in first.keys() | second.keys()) / 2


def distribution(cases, law, command, weight=(1, 1, 1, 1), read="observed"):
    """The command takes the source labels; the score reads the actual ordinary birth ledger."""
    joints = Counter()
    local = [Counter(), Counter()]
    for index, (u, v) in enumerate(PAIRS):
        if not weight[index]:
            continue
        x, y = command(u, v)
        details = cases[named((u, v))]["laws"][law]
        funded = details["trials"][named((x, y))]["ordinary_round"]["status"] == "extend"
        data = details["old_terminal_weights"]
        factor = Fraction(weight[index], sum(weight) * data["old_assignments"])
        for a, row in zip(WORDS, data["counts"], strict=True):
            for b, count in zip(WORDS, row, strict=True):
                gates = (funded, funded)
                if read == "before":
                    gates = (True, True)
                if read == "per_side":
                    gates = (u == x, v == y)
                bits = (a[0] * gates[0], b[0] * gates[1])
                joints[bits] += factor * count
                local[0][u, x, funded, a] += factor * count
                local[1][v, y, funded, b] += factor * count
    assert sum(joints.values()) == 1
    return tuple(joints[outcome] for outcome in PAIRS), local


def check_receipt(receipt, cases, law, weight=(1, 1, 1, 1), read="observed"):
    for (x, y), expected in zip(PAIRS, receipt["contexts"], strict=True):
        actual, _ = distribution(cases, law, lambda u, v: (x, y), weight, read)
        assert list(map(str, actual)) == expected["outputs"]
        assert [p * expected["denominator"] for p in actual] == expected["counts"]


def adaptive(cases, law):
    """Explicit post-freeze access test using only choices among the frozen local edits."""
    report = {}
    for label, address in (("alice_address0", 0), ("alice_address1", 1), ("alice_repairs", None)):
        outputs, observations = [], []
        for message in (0, 1):
            def command(u, v):
                return (u if address is None else address), (v ^ message)

            counts, records = distribution(cases, law, command)
            outputs.append(counts)
            observations.append(records[0])
        tv = variation(*observations)
        bit = abs(sum(outputs[0][2:]) - sum(outputs[1][2:]))
        assert tv == (1 if address is None else Fraction(1, 2))
        assert bit == (Fraction(1, 2) if address is None else Fraction(1, 4))
        report[label] = {"joint_by_message": [list(map(str, cell)) for cell in outputs],
                         "alice_visible_record_TV": str(tv), "alice_outcome_TV": str(bit)}
    return report


def run():
    scores = json.loads((ARTIFACT / "masking.json").read_text())["laws"]
    physical = json.loads((ARTIFACT / "physical.json").read_text())
    report = {"recomputed_from": "ordinary statuses and six-bit physical histograms",
              "adaptive_control_status": "post-freeze diagnostic", "laws": {}}
    for law, results in scores.items():
        sources = physical["modes"]["primary"]
        for kind, rec in results["endpoint_histograms"].items():
            from_incidence = sources[kind]["laws"][law]["old_terminal_weights"]
            assert [n for row in from_incidence["counts"] for n in row] == rec["six_bit_weights"]
            assert rec["total"] == from_incidence["old_assignments"]
        check_receipt(results["primary"], sources, law)
        controls = results["controls"]
        for mode in ("commuting", "identity", "reversed"):
            check_receipt(controls[mode], physical["modes"][mode], law)
        check_receipt(controls["terminal_only"], sources, law, read="before")
        check_receipt(controls["saturated"], physical["saturated"]["types"], law)
        check_receipt(controls["independent_local"], sources, law, read="per_side")
        check_receipt(controls["bob_label_one_three_quarters"], sources, law, (1, 3, 1, 3))
        for i, source in enumerate(PAIRS):
            weight = tuple(int(k == i) for k in range(4))
            check_receipt(controls["fixed_types"][named(source)], sources, law, weight)
        report["laws"][law] = {"prepared_weighting_primary_and_control_tables_reproduced": True,
                               "adaptive_edits": adaptive(sources, law)}
    (ARTIFACT / "verification.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    run()
