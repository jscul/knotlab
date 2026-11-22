"""Independently check the attempt-denominator marginals and the late NAE guard."""
from collections import defaultdict
from fractions import Fraction
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = "HIDDEN-SENDER-MARKS-20261122-001A"
NEW = HERE.name + "A"


def load(ticket, filename):
    archive, = (ROOT / "artifacts" / ticket).glob("*/" + filename)
    with gzip.open(archive, "rt") as stream:
        return json.load(stream)


def verify():
    old_rows = load(OLD, "supports.json.gz")["projections"]
    old = {(row["law"], row["route"], row["side"]): row["weighted"]
           for row in old_rows if row["target"] == "R"}
    repeated = load(NEW, "joint.json.gz")
    keys = set()
    actual_protocols = {}
    guard_joint = {}
    for trial in repeated["launches"]:
        law, route, side = trial["basis"].split("-")
        schedule, request, operation = (trial[k] for k in ("bands", "request", "class"))
        key = law, route, side, schedule, operation, request
        assert key not in keys
        keys.add(key)
        data = repeated["joint_laws"][trial["joint"]]["joint_P_actual_and_local"]
        counts, statuses = defaultdict(Fraction), defaultdict(set)
        for address, value in data.items():
            actions, word = address.split("|")
            p = Fraction(value)
            assert p > 0
            counts[word] += p
            statuses[word].add(actions)
        assert len(counts) == 8 and sum(counts.values()) == 1
        assert all(possible == next(iter(statuses.values())) for possible in statuses.values())
        # Only the net permutation at the original funding can change any subsequently paid value.
        early_swaps = sum(band == "E" and act == "T" for band, act in zip(schedule, request, strict=True))
        first = old[law, route, side]["swap" if early_swaps % 2 else "idle"]
        assert counts == {w: Fraction(p) for w, p in first.items()}
        actual_protocols[key] = dict(counts)
        if (law, route, side, operation, request) == ("nae", "intact", "00", "pointwise", "TT"):
            if schedule in ("EP", "EB", "EF"):
                # After the first exchange C's fresh triple is freely chosen; undo is legal except on 000.
                # On acceptance its conditional triple is uniform on the seven nonzero words, as with idle.
                for w, p_idle in old[law, route, side]["idle"].items():
                    assert Fraction(data["MM|" + w]) == Fraction(7, 8) * Fraction(p_idle)
                assert sum(Fraction(p) for k, p in data.items() if k.startswith("MU|")) == Fraction(1, 8)
                guard_joint[schedule] = {
                    "two_moves": "7/8", "only_first_moves": "1/8",
                    "two_moves_given_word_000": str(Fraction(data["MM|000"]) / counts["000"]),
                    "two_moves_given_word_111": str(Fraction(data["MM|111"]) / counts["111"]),
                }
            elif "E" not in schedule:
                masses = defaultdict(Fraction)
                for k, p in data.items():
                    masses[k.split("|")[0]] += Fraction(p)
                assert masses == {"MM": Fraction(7, 8), "UU": Fraction(1, 8)}
    score = {}
    for trial in repeated["comparisons"]:
        law, route, side = trial["basis"].split("-")
        schedule, operation = trial["bands"], trial["class"]
        pair = [actual_protocols[law, route, side, schedule, operation, intent] for intent in ("II", "TT")]
        accuracy = sum(max(pair[0][w], pair[1][w]) for w in pair[0]) / 2
        expected = old[law, route, side]["equal_prior_optimal_accuracy"] if schedule.count("E") == 1 else "1/2"
        assert accuracy == Fraction(expected)
        reported = repeated["summaries"][trial["summary"]]
        assert Fraction(reported["gain_from_second_local_sample"]) == 0
        if route == "intact" and side == "00" and operation == "structural":
            score.setdefault(law, {})[schedule] = str(accuracy)
    assert len(keys) == 1920 and len(repeated["comparisons"]) == 480
    return {"all_attempts_with_verified_actual_joint_marginals": len(keys),
            "equal_prior_comparisons": len(repeated["comparisons"]),
            "all_eight_words_share_every_globally_possible_physical_status_within_protocol": True,
            "archived_intact_best_guess_by_original_funding_order": score,
            "pointwise_NAE_after_one_early_exchange_at_archived_reference": guard_joint}


if __name__ == "__main__":
    result = verify()
    (HERE / "joint_check.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
