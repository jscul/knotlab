"""Check the causal ledger against the paid public observation in each matched history."""
from collections import Counter
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_gzip(name):
    with gzip.open(HERE / name, "rt") as handle:
        return json.load(handle)


def verify():
    pairs = read_gzip("history_pairs.json.gz")
    decisions = read_gzip("intervention_rows.json.gz")
    result = {}
    for p, d in zip(pairs, decisions, strict=True):
        law = p["law"]
        cells = result.setdefault(law, {})
        assert [p[k] for k in ("law", "seed", "tape", "variant", "turn")] == [
            d[k] for k in ("law", "seed", "tape", "variant", "turn")
        ]
        assert p["target_holder"] == d["holder"] and d["prefix_eats"] == [
            p[s]["attempt_turns"] for s in ("empty", "full")
        ]
        target, other = p["target_holder"], p["other_paid_holder"]
        assert target != other
        memories = []
        answers = []
        for side in ("empty", "full"):
            e = p[side]
            assert target == e["route"][-1] and (target in e["spent_holders"]) == (side == "empty")
            actual = [i for i in range(len(e["public"])-1) if e["public"][i][4] == 0 and
                      e["public"][i+1][1] > e["public"][i][1]-1]
            assert [i+1 for i in actual] == e["meal_turns"]
            assert e["public"][-1][:-1] == p["current"]
            old = e["public"][actual[-1]][3]
            now = e["public"][-1][3]
            memories.append("101" if old == 1 else "011")
            answers.append(int((old == 1) != (now == 1)))
        assert memories == d["memory"]
        assert d["bits"]["original"] == d["bits"]["sham"] == answers
        assert d["bits"]["swapped"] == answers[::-1]
        correct = answers == [0, 1]
        cert = p["empty"]["verdict"] == "empty" and p["full"]["verdict"] == "full"
        both = all({target, other}.issubset(p[s]["route"]) for s in ("empty", "full"))
        matched_earlier = p["last_meal_same_turn_and_energy"]
        opposite_order = p["visit_orders"] in (["target_first", "other_first"], ["other_first", "target_first"])
        distinct_length = None not in p["return_lengths"] and len(set(p["return_lengths"])) == 2
        for name, condition in (
            ("all", True), ("both_visited", both), ("opposite_visit_order", opposite_order),
            ("different_return_lengths", distinct_length), ("matched_meal_turn_and_energy", matched_earlier),
            ("at_least_two_moves_since_both_last_meals", min(p["moves_since_last_meal"]) >= 2),
            ("queries_above_one_energy", p["current"][1] > 1),
        ):
            if condition:
                c = cells.setdefault(name, Counter())
                c.update(pairs=1, flipped=int(answers[0] != answers[1]), both_stock_correct=int(correct),
                         both_certified=int(cert), certified_correct_flip=int(correct and cert))
    return result


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
