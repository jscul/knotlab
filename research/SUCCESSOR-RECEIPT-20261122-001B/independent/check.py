"""Recompute the later-source cohort by exact propagation of complete birth words."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCHIVE = ROOT / "artifacts/HIDDEN-SENDER-MARKS-20261122-001A"
PHYSICAL = ROOT / "artifacts/SUCCESSOR-RECEIPT-20261122-001A"
REPEATED = ROOT / "research/REPEATED-SENDS-20261122-001/fixed_holder_replay.json"
GROWTH, = ARCHIVE.glob("*/growth.json.gz")
OLD_WORDS, = ARCHIVE.glob("*/whole_words.json.gz")
FOURTH, = PHYSICAL.glob("*/alternate.json.gz")
WORDS = tuple(product((0, 1), repeat=3))
ACTION = ("I", "T")
TARGETS = ("W", "W0", "action", "W0_and_action")


def load(path):
    data = path.read_bytes()
    return json.loads(decompress(data) if path.suffix == ".gz" else data)


def pairs(row):
    return dict(zip(row["parents"], row["consumed_names"], strict=True))


def recover_births(original, cuts):
    """Validate every paid name against the complete preceding ownership roster."""
    owners = defaultdict(list)
    for holder, holding in enumerate(original):
        for mark in holding:
            owners[mark].append(holder)
    births = {}
    total_holders = len(original)
    for cut in cuts:
        open_marks = {mark for mark, holding in owners.items() if len(holding) == 1}
        paid = set()
        new_owners = {}
        for row in cut["births"]:
            holder = row["holder"]
            assert holder == total_holders
            assert len(pairs(row)) == len(row["parents"])
            for parent, mark in pairs(row).items():
                assert mark in open_marks and mark not in paid and owners[mark] == [parent]
                paid.add(mark)
                new_owners[mark] = [parent, holder]
            fresh = row["fresh_names"]
            assert fresh and len(fresh) + len(row["parents"]) >= 3
            for mark in fresh:
                assert mark not in owners and mark not in new_owners
                new_owners[mark] = [holder]
            births[holder] = row
            total_holders += 1
        assert paid == open_marks
        owners.update(new_owners)
    return births


def select(growth, fourth, births, cuts):
    receiver = growth["physical_holders"]["R"]
    w_marks = births[receiver]["fresh_names"]
    third = {row["holder"]: row for row in cuts[2]["births"]}
    successors = {holder: w_marks.index(pairs(row)[receiver])
                  for holder, row in third.items() if receiver in row["parents"]}
    assert sorted(successors.values()) == list(range(len(w_marks)))
    candidates = []
    for row in fourth["births"]:
        if len(row["parents"]) != 2:
            continue
        for h_id, k_id in (row["parents"], row["parents"][::-1]):
            if h_id in successors and k_id in third and len(third[k_id]["fresh_names"]) > 1:
                candidates.append((k_id in successors, successors[h_id], row["holder"], k_id, h_id))
    _, position, g_id, k_id, h_id = min(candidates)
    h_mark, q_mark = (pairs(births[g_id])[holder] for holder in (h_id, k_id))
    spare = min(set(births[k_id]["fresh_names"]) - {q_mark})
    side, = (mark for parent, mark in pairs(births[h_id]).items() if parent != receiver)
    return {"R": receiver, "W": w_marks, "position": position, "H": h_id,
            "K": k_id, "G": g_id, "h": h_mark, "q": q_mark, "spare": spare,
            "side": side, "eligible_count": len(candidates)}


def lawful(law, word):
    ones = sum(word)
    return ones % 2 == 0 if law == "parity" else 0 < ones < len(word)


@cache
def fresh_words(law, paid, width):
    """Uniformly sample each full word that can extend the actual paid bits."""
    options = tuple(word for word in product((0, 1), repeat=width) if lawful(law, paid + word))
    assert options
    return options


def propagate(law, births, old, original_names, query):
    closure = []
    needed = set(query)
    for holder in sorted(births, reverse=True):
        row = births[holder]
        if needed.intersection(row["fresh_names"]):
            closure.append(row)
            needed.update(row["consumed_names"])
            needed.difference_update(row["fresh_names"])
    assert needed.issubset(original_names)
    rows = list(reversed(closure))
    names_before = sorted(needed)
    old_bits = tuple((old >> name) & 1 for name in names_before)
    states = Counter({old_bits: Fraction(1)})
    largest = len(states)
    for i, row in enumerate(rows):
        live = set(query)
        for future in rows[i + 1:]:
            live.update(future["consumed_names"])
        available = names_before + row["fresh_names"]
        names_after = sorted(live.intersection(available))
        indices = [available.index(mark) for mark in names_after]
        input_indices = [names_before.index(mark) for mark in row["consumed_names"]]
        advanced = Counter()
        for state, mass in states.items():
            paid = tuple(state[index] for index in input_indices)
            options = fresh_words(law, paid, len(row["fresh_names"]))
            for fresh in options:
                extended = state + fresh
                projected = tuple(extended[index] for index in indices)
                advanced[projected] += mass / len(options)
        assert advanced.total() == 1
        largest = max(largest, len(advanced))
        names_before, states = names_after, advanced
    assert names_before == sorted(query)
    return names_before, states, rows, largest


def display(bits):
    return "".join(map(str, bits))


def decision_score(rows, idx, projection):
    tables = defaultdict(Counter)
    for w, action, paid, fresh, mass in rows:
        target = (w, w[0], action, (w[0], action))[idx]
        tables[projection(action, paid, fresh)][target] += mass
    certain = [table for table in tables.values() if len(table) == 1]
    return {"best": sum(max(table.values()) for table in tables.values()),
            "observations": len(tables), "certifying_observations": len(certain),
            "mass_of_certifying_observations": sum(table.total() for table in certain),
            "always_identifies": len(certain) == len(tables)}


def decision(law, joint, fresh_width):
    rows = []
    for (w, h), mass in joint.items():
        for q, action in enumerate(ACTION):
            paid = (h, q)
            words = fresh_words(law, paid, fresh_width)
            rows.extend((w, action, paid, fresh, mass / (2 * len(words))) for fresh in words)
    assert sum(row[-1] for row in rows) == 1
    reads = {"anonymous": lambda paid: sum(paid), "role_addressed": lambda paid: paid}
    directions = {"prior": lambda _a, _p, _f: (), "action_known": lambda a, _p, _f: a}
    scores = {label: {target: decision_score(rows, i, projection)
                      for i, target in enumerate(TARGETS)}
              for label, projection in directions.items()}
    for label, read in reads.items():
        scores[label] = {}
        for i, target in enumerate(TARGETS):
            read_paid = decision_score(rows, i, lambda _a, p, _f: read(p))
            full = decision_score(rows, i, lambda _a, p, f: (read(p), f))
            known_action = decision_score(rows, i, lambda a, p, f: (a, read(p), f))
            assert all(full[key] == read_paid[key] for key in
                       ("best", "mass_of_certifying_observations", "always_identifies"))
            scores[label][target] = {"paid": read_paid, "complete": full,
                                      "complete_with_action_known": known_action}
    for first, second in product(product((0, 1), repeat=2), repeat=2):
        if sum(first) == sum(second):
            assert fresh_words(law, first, fresh_width) == fresh_words(law, second, fresh_width)
    return scores


def law_report(law, growth, words, fourth, prior):
    cuts = growth["cases"]["intact"][law]["cuts"]
    assert len(fourth["births"]) == prior["further_births"] == 964
    births = recover_births(growth["original_stars"], [*cuts, fourth])
    control = select(growth, fourth, births, cuts)
    assert [control[label] for label in ("H", "K", "G", "position", "h", "q", "spare", "side")] == [
        631, 632, 1595, 0, 4381, 4384, 4383, 1748]
    assert control["W"] == [1754, 1755, 1756]
    source_marks = growth["physical_marks"]
    old = int(words["old_words"][f"{law}-00"]["common_before"], 16)
    assert display((old >> name) & 1 for name in growth["original_name_order"]) == growth["common_original_words"][law]
    assert ((old >> source_marks["a"]) & 1, (old >> source_marks["b"]) & 1) == (0, 1)
    assert all(lawful(law, tuple((old >> name) & 1 for name in row)) for row in growth["original_stars"])
    others_h = set(births[control["H"]]["fresh_names"]) - {control["h"]}
    assert {control["q"], control["spare"]}.issubset(births[control["K"]]["fresh_names"])
    zero_marks = {control["side"], *others_h}
    wanted = set(control["W"]) | {control["h"], control["q"], control["spare"]} | zero_marks
    names, states, rows, peak = propagate(law, births, old, set(growth["original_name_order"]), wanted)
    launch_prior = Counter()
    launch_joint = {"ready": Counter(), "ready_and_calibrated": Counter()}
    p_calibration = Fraction(0)
    for state, mass in states.items():
        values = dict(zip(names, state, strict=True))
        w = tuple(values[mark] for mark in control["W"])
        h = values[control["h"]]
        ready = (values[control["q"]], values[control["spare"]]) == (0, 1)
        calibrated = all(values[mark] == 0 for mark in zero_marks)
        launch_prior[w] += mass
        p_calibration += mass * calibrated
        if ready:
            launch_joint["ready"][w, h] += mass
            if calibrated:
                launch_joint["ready_and_calibrated"][w, h] += mass
    assert all(launch_prior[w] == Fraction(prior["diagonal_joint_first_word_and_reread_keep_then_swap"][display(w)][0])
               for w in WORDS)
    report = {"selection": control, "contributing_births": rows, "largest_state_count": peak,
              "W_before_preparation": {display(w): launch_prior[w] for w in WORDS},
              "calibration_without_ready_per_launch": p_calibration, "cohorts": {}}
    for name, joint in launch_joint.items():
        launch_mass = joint.total()
        conditional = {key: mass / launch_mass for key, mass in joint.items()}
        masses_w = {w: sum(joint[w, h] for h in (0, 1)) for w in WORDS}
        report["cohorts"][name] = {
            "probability_per_launch": launch_mass,
            "probability_per_launch_per_action": launch_mass / 2,
            "probability_given_W": {display(w): masses_w[w] / launch_prior[w] for w in WORDS},
            "W_prior": {display(w): masses_w[w] / launch_mass for w in WORDS},
            "W0_prior": {str(bit): sum(m for w, m in masses_w.items() if w[0] == bit) / launch_mass for bit in (0, 1)},
            "W_h_given_cohort": {display(w): [conditional.get((w, h), 0) for h in (0, 1)] for w in WORDS},
            "decisions": decision(law, conditional, len(births[control["G"]]["fresh_names"])),
        }
    ready, calibrated = report["cohorts"].values()
    p_ready = ready["probability_per_launch"]
    p_intersection = calibrated["probability_per_launch"]
    report["selection_checks"] = {
        "P_calibrated_given_ready": p_intersection / p_ready,
        "P_ready_given_calibrated": p_intersection / p_calibration,
        "P_ready_times_P_calibrated": p_ready * p_calibration,
        "P_W0_is_one_ready_vs_both": [ready["W0_prior"]["1"], calibrated["W0_prior"]["1"]],
    }
    if law == "nae":
        assert ready["W0_prior"]["1"] != calibrated["W0_prior"]["1"]
        assert p_intersection != p_ready * p_calibration
        assert len(set(ready["probability_given_W"].values())) > 1
    return report


def build():
    growth = load(GROWTH)
    words = load(OLD_WORDS)
    physical = load(FOURTH)
    archive = load(REPEATED)
    return {"source_sha256": {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest()
                              for path in (GROWTH, OLD_WORDS, FOURTH, REPEATED)},
            "laws": {law: law_report(law, growth, words, physical["courses"][law]["intact"]["fourth"],
                                     archive[law]["intact"]) for law in ("parity", "nae")}}


def compare_main(replay, main, physical):
    """Compare after the independently calculated result has been saved."""
    target_names = dict(zip(TARGETS, ("word", "retained_bit", "second_action", "bit_and_action"), strict=True))
    reads = {"prior": "none", "action_known": "action_only", "anonymous": "anonymous",
             "role_addressed": "addressed"}
    cohorts = {"ready": ("ready_only", "natural"),
               "ready_and_calibrated": ("ready_and_H_calibration", "calibrated")}
    comparisons = Counter()
    for law, result in replay["laws"].items():
        for cohort, (main_name, support_name) in cohorts.items():
            own = result["cohorts"][cohort]
            other = main[law][main_name]
            assert Fraction(own["probability_per_launch"]) == Fraction(other["cohort_probability_per_original_launch"])
            assert own["probability_given_W"] == other["cohort_probability_given_W"]
            comparisons.update({"launch_masses": 1, "W_conditional_launch_masses": len(own["probability_given_W"])})
            support = physical["later_source_controls"][law]["modes"][support_name]
            for w, h_weights in own["W_h_given_cohort"].items():
                assert [h for h, weight in enumerate(h_weights) if Fraction(weight)] == support["paid_h_by_full_W"][w]
                for h, weight in enumerate(h_weights):
                    for q in range(len(ACTION)):
                        key = f"{w}|{h}|{q}"
                        assert Fraction(weight) / 2 == Fraction(other["joint_given_cohort_W_h_action"].get(key, 0))
                        comparisons["joint_W_h_action_cells"] += 1
            for read, main_read in reads.items():
                for target, main_target in target_names.items():
                    score = own["decisions"][read][target]
                    reference = other["scores"][main_read][main_target]
                    if read in ("anonymous", "role_addressed"):
                        score = score["complete"]
                        physical_view = support["G_readings"]["anonymous" if read == "anonymous" else "oriented"]
                        physical_target = dict(zip(TARGETS, ("whole_W", "W_i", "K_action", "W_i_and_K_action"), strict=True))
                        assert score["observations"] == physical_view["complete_local_record_count"]
                        assert score["certifying_observations"] == physical_view["uniquely_identifying_record_count"][physical_target[target]]
                        comparisons["physical_read_support_checks"] += 1
                    assert Fraction(score["best"]) == Fraction(reference["accuracy"])
                    assert Fraction(score["mass_of_certifying_observations"]) == Fraction(reference["mass_of_certifying_outcomes"])
                    comparisons["score_and_certifying_mass_pairs"] += 1
    return comparisons


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--compare-main", action="store_true", help="compare an existing independent result")
    args = parser.parse_args()
    report_path = HERE / "verification.json"
    if args.compare_main:
        main_path = HERE.parent.with_name("SUCCESSOR-RECEIPT-20261122-001") / "later_source_joint.json"
        print(json.dumps(compare_main(load(report_path), load(main_path), load(FOURTH)), sort_keys=True))
    else:
        output = json.dumps(build(), default=str, sort_keys=True, separators=(",", ":"))
        report_path.write_text(output + "\n")
