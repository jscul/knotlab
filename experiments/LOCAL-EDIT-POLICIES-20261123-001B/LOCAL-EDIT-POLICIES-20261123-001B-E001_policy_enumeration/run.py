"""Compute exact address-policy tables for the frozen concealed-demand source."""

from argparse import ArgumentParser
import gzip
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import time

from kernels import CURRENT, PHYSICAL, ROOT, check_new_kernels, check_old_kernels, make_source
from policies import ADDRESSES, READINGS, adaptive_on_cut_and_bit, optimum, standard_table, witness


HERE = Path(__file__).resolve().parent
DESIGN = ROOT / "research/LOCAL-EDIT-POLICIES-20261123-001/preregistration.md"
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
LAWS = ("parity", "nae")
PRIMARY_VIEWS = ("blind", "bit", "detector", "guard")
PRIMARY_INTERFACES = tuple((view, view, view) for view in PRIMARY_VIEWS) + (
    ("bit", "detector", "detector"), ("detector", "bit", "detector"),
    ("detector", "blind", "detector"), ("guard", "blind", "guard"),
    ("bit", "guard", "guard"), ("blind", "guard", "guard"),
    ("detector", "guard", "guard"), ("guard", "detector", "detector"),
)


def messages_by_old_bit(states, denominator):
    return {name: {str(action): witness(states, denominator, side, "bit", "blind", "guard", (action,), [(0, 1), (1, 0)])
                   for action in ADDRESSES} for side, name in enumerate(("alice_to_bob", "bob_to_alice"))}


def constant_record_variation(states, denominator):
    return {name: {str(action): witness(states, denominator, side, "blind", "blind", "guard", (action,), [(0,), (1,)])
                   for action in ADDRESSES} for side, name in enumerate(("alice_to_bob", "bob_to_alice"))}


def conditional_counts(states, view):
    """Store all type counts at each supported pair of pre-edit records."""
    supported = {}
    for state in states:
        pair = tuple(state.observes(side, view) for side in (0, 1))
        counts = supported.setdefault(pair, [0, 0, 0, 0])
        counts[2 * state.labels[0] + state.labels[1]] += state.mass
    return [{"old_records": pair, "type_counts_00_01_10_11": counts, "conditional_denominator": sum(counts)}
            for pair, counts in sorted(supported.items())]


def optimize_interfaces(states, denominator, interfaces, menus):
    records = []
    cache = {}

    def score(side, sender_view, receiver_view, receiver_record, reading, menu):
        key = side, sender_view, receiver_view, receiver_record, reading, menu
        if key not in cache:
            cache[key] = optimum(states, denominator, *key, sender_constant=False)
        return cache[key]

    for side, (sender_view, receiver_view, receiver_record), actions in product((0, 1), interfaces, menus):
        entry = {"sender": "alice" if side == 0 else "bob", "sender_before": sender_view, "receiver_before": receiver_view,
                 "receiver_record": receiver_record, "menu": [0, 1] if actions == 2 else [0, 1, "withhold"], "optima": {}}
        for reading in READINGS:
            informative = score(side, sender_view, receiver_view, receiver_record, reading, actions)
            constant = score(side, "blind", receiver_view, receiver_record, reading, actions)
            entry["optima"][reading] = {"locally_informed_sender": informative, "constant_sender": constant}
        records.append(entry)
    return records


def case(law, device, mode, masses=(1, 1, 1, 1)):
    states, per_type, all_mass = make_source(law, mode, device, masses)
    uniform_types = masses == (1, 1, 1, 1)
    if device == "concealed" and mode == "primary" and uniform_types:
        check_new_kernels(law, states, per_type)
    elif device == "predecessor" and uniform_types:
        check_old_kernels(law, mode, states, per_type)
    result = {"law": law, "device": device, "routing": mode, "type_mass_units": masses,
              "prepared_states_per_type": per_type, "common_denominator": all_mass,
              "constant_addresses": standard_table(states, all_mass),
              "constant_receiver_record_controls": constant_record_variation(states, all_mass),
              "old_bit_vs_opposite": messages_by_old_bit(states, all_mass)}
    if device == "concealed" and mode == "primary" and uniform_types:
        result["optimum"] = optimize_interfaces(states, all_mass, PRIMARY_INTERFACES, (2,))
        result["withhold"] = optimize_interfaces(states, all_mass, tuple((view, view, view) for view in PRIMARY_VIEWS), (3,))
        result["readiness_revealed"] = optimize_interfaces(states, all_mass, (("type", "type", "type"),), (2,))
        result["controls"] = {mode: standard_table(states, all_mass, gate=mode) for mode in ("terminal", "local")}
        result["full_policy_old_bit_and_gain"] = {name: adaptive_on_cut_and_bit(states, all_mass, side)
                                                   for side, name in enumerate(("alice_to_bob", "bob_to_alice"))}
        result["single_class_edit"] = {name: witness(states, all_mass, side, "bit", "blind", "guard", (1,), [(0, 0), (0, 1)])
                                       for side, name in enumerate(("alice_to_bob", "bob_to_alice"))}
        result["conditioned_type_counts"] = {view: conditional_counts(states, view) for view in PRIMARY_VIEWS}
    elif device == "predecessor" and mode == "primary":
        result["optimum"] = optimize_interfaces(states, all_mass, (("detector", "detector", "detector"),), (2,))
        result["readiness_revealed"] = optimize_interfaces(states, all_mass, (("type", "type", "type"),), (2,))
    elif device == "concealed" and mode == "commuting" and uniform_types:
        result["optimum"] = optimize_interfaces(states, all_mass, (("guard", "guard", "guard"), ("detector", "detector", "detector")), (2,))
    return result


def summary(cases, frozen):
    result = {"design_sha256": frozen, "cases": []}
    for item in cases:
        entry = {key: item[key] for key in ("law", "device", "routing", "type_mass_units", "prepared_states_per_type", "common_denominator")}
        entry["constant_addresses"] = item["constant_addresses"]
        entry["old_bit_vs_opposite_tv"] = {direction: {x: receipt["TV"] for x, receipt in comparisons.items()}
                                            for direction, comparisons in item["old_bit_vs_opposite"].items()}
        entry["constant_addresses_guard_tv"] = {direction: {x: receipt["TV"]["view_and_gain"] for x, receipt in comparisons.items()}
                                                 for direction, comparisons in item["constant_receiver_record_controls"].items()}
        if "full_policy_old_bit_and_gain" in item:
            entry["full_policy_old_bit_and_gain"] = {direction: row["maximum"]
                                                       for direction, row in item["full_policy_old_bit_and_gain"].items()}
            entry["single_class_edit_TV"] = {direction: row["TV"] for direction, row in item["single_class_edit"].items()}
        for block in ("optimum", "withhold", "readiness_revealed"):
            entry[block] = []
            for experiment in item.get(block, []):
                summary_row = {name: experiment[name] for name in ("sender", "sender_before", "receiver_before", "receiver_record", "menu")}
                summary_row["maxima"] = {read: {which: {policy: item["maximum"] for policy, item in records.items()}
                                               for which, records in sender.items()}
                                         for read, sender in experiment["optima"].items()}
                entry[block].append(summary_row)
        result["cases"].append(entry)
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    started = time.monotonic()
    frozen = json.loads((HERE / "contract.json").read_text())["design_sha256"]
    assert sha256(DESIGN.read_bytes()).hexdigest() == frozen
    cases = []
    for law in LAWS:
        cases.append(case(law, "concealed", "primary"))
        print(f"{law} concealed main complete in {time.monotonic() - started:.2f} s", flush=True)
        cases.extend(case(law, "concealed", mode) for mode in ("commuting", "reversed"))
        cases.append(case(law, "concealed", "primary", (1, 3, 1, 3)))
        cases.append(case(law, "predecessor", "primary"))
    metadata = {"design_sha256": frozen, "physical_source_sha256": sha256(CURRENT.read_bytes()).hexdigest(),
                "previous_physical_source_sha256": sha256(PHYSICAL.read_bytes()).hexdigest(),
                "counts": "Per-type equality, then multiply literal states by the declared integer type mass. No conditioning on funding.",
                "conventions": "All settings ordered 00,01,10,11. Views ordered lexicographically. Address 2 means withhold.",
                "record_scope": "The exact finite read is observed word plus gain. Whole-record transfer requires the physical conditional channel to include newly exposed H inputs.",
                "old_bit": "designated old detector terminal, known before editing where that view is allowed",
                "published_bit": "that old bit AND the visible gain; 0 on any stall"}
    result = {"metadata": metadata, "cases": cases}
    args.output.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(result, separators=(",", ":")).encode()
    (args.output / "exact_policies.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    (args.output / "summary.json").write_text(json.dumps(summary(cases, frozen), indent=2) + "\n")
    print(f"Completed {len(cases)} law/source panels in {time.monotonic() - started:.2f} s", flush=True)


if __name__ == "__main__":
    main()
