"""Primal enumeration of policy contrasts and independent raw witness replay."""

from collections import Counter
from fractions import Fraction
import gzip
from itertools import product
import json
from pathlib import Path

import numpy as np

from kernels import make_source


HERE = Path(__file__).resolve().parent
ARTIFACT = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name / "exact_policies.json.gz"
width = {"blind": 1, "bit": 2, "type": 2, "detector": 8, "guard": 8}


def q(pair):
    return Fraction(*pair)


def direct_hist(states, sender, before_sender, before_receiver, receive, st, rt):
    """Score all trials by their actual post-flag records rather than by a signed event."""
    receiver = 1 - sender
    counted = {"gain": Counter(), "published_bit": Counter(), "old_bit_and_gain": Counter(),
               "view_and_gain": Counter(), "old_bit": Counter(), "joint_outcomes": Counter(), "sender_action_counts": Counter()}
    for row in states:
        p = st[row.observes(sender, before_sender)]
        t = rt[row.observes(receiver, before_receiver)]
        f = p == row.labels[sender] and t == row.labels[receiver]
        b = row.first_bit(receiver)
        counted["gain"][int(f)] += row.mass
        counted["published_bit"][b if f else 0] += row.mass
        counted["old_bit_and_gain"][2 * b + int(f)] += row.mass
        counted["view_and_gain"][2 * row.observes(receiver, receive) + int(f)] += row.mass
        counted["old_bit"][b] += row.mass
        raw = 2 * row.first_bit(0) + row.first_bit(1) if f else 0
        counted["joint_outcomes"][raw] += row.mass
        counted["sender_action_counts"][p] += row.mass
    sizes = {"gain": 2, "published_bit": 2, "old_bit_and_gain": 4, "view_and_gain": 2 * width[receive],
             "old_bit": 2, "joint_outcomes": 4, "sender_action_counts": 3}
    return {name: [row[i] for i in range(sizes[name])] for name, row in counted.items()}


def check_witness(states, source, side, views, counts, tested):
    a, b, post = views
    receiver = counts["receiver_actions"]
    prior = counts["sender_actions_by_message"]
    first, second = (direct_hist(states, side, a, b, post, action, receiver) for action in prior)
    assert [first, second] == counts["counts_by_message"]
    assert counts["denominator_each_message"] == source["common_denominator"]
    for name, ratio in counts["TV"].items():
        tv = Fraction(sum(abs(x - y) for x, y in zip(first[name], second[name], strict=True)), 2 * source["common_denominator"])
        assert q(ratio) == tv
    tested["independent_witnesses"] += 1


def brute_optimum(states, sender, sender_view, receiver_view, record, readout, menu):
    """Enumerate material sender differences, avoiding the signed-event maximization."""
    receiver = 1 - sender
    ns, nr = width[sender_view], width[receiver_view]
    length = width[record] if readout == "view_and_gain" else 2 if readout == "old_bit_and_gain" else 1
    by_action = [[[Counter() for _ in range(length)] for _ in range(menu)] for _ in range(nr)]
    for row in states:
        t = row.first_bit(receiver)
        if readout == "published_bit" and t != 1:
            continue
        o = row.observes(receiver, record) if readout == "view_and_gain" else t if readout == "old_bit_and_gain" else 0
        ri = row.observes(receiver, receiver_view)
        by_action[ri][row.labels[receiver]][o][(row.observes(sender, sender_view), row.labels[sender])] += row.mass
    # Every sender contrast is a difference of two unit vectors at each observed word.
    # Equal actions give zero, in the convex hull of the opposing contrasts.
    local_differences = []
    for a, b in product(range(menu), repeat=2):
        if a != b:
            local_differences.append(tuple(int(i == a) - int(i == b) for i in range(menu)))
    differences = np.asarray([sum(item, ()) for item in product(local_differences, repeat=ns)], dtype=object)
    # One row per sender contrast, one column per output bin. Compute the observed
    # probability changes for each choice of the receiver's own control table.
    replay = np.empty((nr, menu, len(differences), length), dtype=object)
    for obs, action in product(range(nr), range(menu)):
        counts = [[by_action[obs][action][o][s, t] for s, t in product(range(ns), range(menu))] for o in range(length)]
        replay[obs, action] = differences @ np.asarray(counts, dtype=object).T
    result = {}
    for action in range(menu):
        result[f"fixed_{action}"] = int(np.abs(replay[:, action].sum(axis=0)).sum(axis=1).max())
    best = 0
    for receiver in product(range(menu), repeat=nr):
        score = int(np.abs(replay[np.arange(nr), receiver].sum(axis=0)).sum(axis=1).max())
        best = max(best, score)
    result["adaptive"] = best
    return result


def verify_explicit_witnesses(states, source, count):
    for mode, views in (("old_bit_vs_opposite", ("bit", "blind", "guard")),
                        ("constant_receiver_record_controls", ("blind", "blind", "guard"))):
        for side, name in enumerate(("alice_to_bob", "bob_to_alice")):
            for receipt in source[mode][name].values():
                check_witness(states, source, side, views, receipt, count)
    for block in ("optimum", "withhold", "readiness_revealed"):
        for analysis in source.get(block, []):
            side = int(analysis["sender"] == "bob")
            for reading, sender_paths in analysis["optima"].items():
                for sender_path, found in sender_paths.items():
                    before = analysis["sender_before"] if sender_path == "locally_informed_sender" else "blind"
                    views = before, analysis["receiver_before"], analysis["receiver_record"]
                    for detail in found.values():
                        assert detail["maximum"] == detail["attainment"]["TV"][reading]
                        # The producer re-scores all optima; this path replays all
                        # attained nonzero fixed/adaptive witnesses in the main views.
                        if views[0] == views[1] == views[2] and q(detail["maximum"]):
                            check_witness(states, source, side, views, detail["attainment"], count)
    for side, direction in enumerate(("alice_to_bob", "bob_to_alice")):
        if "full_policy_old_bit_and_gain" in source:
            receipt = source["full_policy_old_bit_and_gain"][direction]
            check_witness(states, source, side, ("guard", "guard_and_bit", "guard"), receipt["attainment"], count)
            check_witness(states, source, side, ("bit", "blind", "guard"), source["single_class_edit"][direction], count)
    for view, records in source.get("conditioned_type_counts", {}).items():
        direct = Counter()
        for row in states:
            key = row.observes(0, view), row.observes(1, view), row.labels
            direct[key] += row.mass
        for row in records:
            a, b = row["old_records"]
            expected = [direct[a, b, label] for label in product((0, 1), repeat=2)]
            assert row["type_counts_00_01_10_11"] == expected
            assert row["conditional_denominator"] == sum(expected)
            count["conditioned_type_rows"] += 1


def verify_maxima(states, source, checked):
    for block in ("optimum", "withhold"):
        for analysis in source.get(block, []):
            modes = analysis["sender_before"], analysis["receiver_before"], analysis["receiver_record"]
            if len(set(modes)) != 1 or block == "withhold" and modes[0] not in ("blind", "bit"):
                continue
            side = int(analysis["sender"] == "bob")
            menu = len(analysis["menu"])
            for reading, result in analysis["optima"].items():
                references = result["locally_informed_sender"]
                direct = brute_optimum(states, side, *modes, reading, menu)
                for policy, score in direct.items():
                    assert q(references[policy]["maximum"]) == Fraction(score, source["common_denominator"])
                    checked["primal_optima"] += 1


def check_neighbor_relation(source, checked):
    signed = [q(value) for value in source["constant_addresses"]["E"]]
    for direction, pairs in (("bob_to_alice", ((0, 1), (2, 3))), ("alice_to_bob", ((0, 2), (1, 3)))):
        for setting, (a, b) in enumerate(pairs):
            row = source["old_bit_vs_opposite"][direction][str(setting)]["TV"]
            assert q(row["gain"]) == 0
            assert q(row["published_bit"]) == abs(signed[a] - signed[b]) / 2
            assert q(row["old_bit_and_gain"]) == abs(signed[a] - signed[b])
            checked["adjacent_identity_checks"] += 1


def main():
    records = json.loads(gzip.decompress(ARTIFACT.read_bytes()))
    checked = Counter()
    for source in records["cases"]:
        weights = tuple(source["type_mass_units"])
        states, one, mass = make_source(source["law"], source["routing"], source["device"], weights)
        assert one == source["prepared_states_per_type"] and mass == source["common_denominator"]
        verify_explicit_witnesses(states, source, checked)
        if weights == (1, 1, 1, 1):
            check_neighbor_relation(source, checked)
        if source["device"] == "concealed" and source["routing"] == "primary" and weights == (1, 1, 1, 1):
            verify_maxima(states, source, checked)
    print(json.dumps(dict(checked)))


if __name__ == "__main__":
    main()
