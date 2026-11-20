"""Independently replay structural tables and selected exact local value laws."""

from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = ROOT / ("experiments/FORBIDDING-JOIN-20261120-001B/"
                "FORBIDDING-JOIN-20261120-001B-E001_free_readings/verify.py")
spec = spec_from_file_location("independent_counts", PRIOR)
old_verifier = module_from_spec(spec)
spec.loader.exec_module(old_verifier)

DATA = ROOT / "artifacts" / HERE.parent.name / HERE.name / "exact_tables.json.gz"
SETTINGS = tuple(product((0, 1), repeat=2))
REMOTE_PAIRS = (((0, 1), (2, 3)), ((0, 2), (1, 3)))


def scope(supports):
    return tuple(sorted({d for row in supports for d in row}))


def immutable(supports):
    return tuple(tuple(row) for row in supports)


def normalized(record):
    result = {key: Fraction(n, record["denominator"]) for key, n in record["positive_cells"].items()}
    assert sum(result.values()) == 1
    return result


def verify_certificates(old_or_new, certificates, law):
    given = {"supports": old_or_new, "support_certificates": certificates,
             "every_displayed_support_lawful": all(row["eligible"] for row in certificates)}
    old_verifier.check_certificates(given, law)


def check_value_records(source, row, law, checked):
    base, edited, final = (immutable(records) for records in (source["base"], row["edited_supports"], row["final_supports"]))
    if len(scope(final)) > 21:
        return
    start_states, start_positions = old_verifier.brute_states(base, law)
    edited_states, edited_positions = old_verifier.brute_states(edited, law)
    final_states, final_positions = old_verifier.brute_states(final, law)
    prior = scope(base)
    edited_bits = scope(edited)
    appended = tuple(d for d in edited_bits if d not in prior)
    base_codes = old_verifier.encode(start_states, start_positions, prior)
    compatible_edited = np.isin(old_verifier.encode(edited_states, edited_positions, prior), base_codes)
    compatible_final = np.isin(old_verifier.encode(final_states, final_positions, prior), base_codes)
    carried = compatible_final.copy()
    if law == "parity":
        carried &= old_verifier.encode(final_states, final_positions, appended) == 0
    else:
        assert np.count_nonzero(compatible_edited) == len(start_states) * (1 << len(appended))
    edited_codes = old_verifier.encode(final_states, final_positions, edited_bits)
    sizes = np.bincount(edited_codes)
    assert len(np.unique(edited_codes)) == len(edited_states)
    weights = row["state_weightings"]
    assert weights["prepared_old_total"] == len(start_states)
    assert weights["uniform_edited_total"] == len(edited_states)
    assert weights["uniform_final_total"] == len(final_states)
    assert Fraction(*weights["uniform_edited_mass_on_prepared_old_relation"]) == Fraction(
        int(np.count_nonzero(compatible_edited)), len(edited_states))
    assert Fraction(*weights["uniform_final_mass_on_prepared_old_relation"]) == Fraction(
        int(np.count_nonzero(compatible_final)), len(final_states))
    lift_count = len(start_states) * ((1 << len(appended)) if law == "nae" else 1)
    assert len(np.unique(edited_codes[carried])) == lift_count
    for side in row["local_records"]:
        before = tuple(side["structure"]["before_values_order"])
        old = tuple(side["structure"]["after_old_values_order"])
        after = old + tuple(side["physical_fresh_ids_in_record_order"])
        code = old_verifier.encode(final_states[carried], final_positions, before + after)
        fiber = sizes[edited_codes[carried]]
        actual = defaultdict(Fraction)
        for degree in np.unique(fiber):
            local, counts = np.unique(code[fiber == degree], return_counts=True)
            for value, n in zip(local, counts, strict=True):
                word = format(int(value), f"0{len(before) + len(after)}b")
                joined = "|".join((word[:len(before)], word[len(before):len(before) + len(old)], word[len(before) + len(old):]))
                actual[joined] += Fraction(int(n), lift_count * int(degree))
        assert normalized(side["carried_old_state_full"]) == actual
        uniform = old_verifier.encode(final_states, final_positions, after)
        values, counts = np.unique(uniform, return_counts=True)
        actual_uniform = {format(int(word), f"0{len(after)}b"): Fraction(int(n), len(final_states))
                          for word, n in zip(values, counts, strict=True)}
        assert normalized(side["uniform_final_after_only"]) == actual_uniform
        checked["brute_local_records"] += 1
    checked["brute_contexts"] += 1


def check_row(source, row, law, checked):
    groups = row["receipt"]["groups"]
    held = Counter(d for support in row["edited_supports"] for d in support)
    owned_bits = [sum(held[d] == 1 for d in support) for support in row["edited_supports"]]
    demand = Counter(holder for group in groups for holder in group)
    stalled = any(demand[i] > count for i, count in enumerate(owned_bits))
    assert stalled == (row["receipt"]["status"] == "stall")
    births = row["receipt"]["births"]
    assert not births if stalled else bool(births)
    final = Counter(d for support in row["final_supports"] for d in support)
    alice, bob = source["marks"]
    if source.get("mechanism", "S") == "S":
        bits = [int(final[d] == 2) for d in (alice, bob)]
    else:
        bits = [int(any(not birth["fresh"] and alice in dict(birth["old_inputs"]).values() for birth in births)),
                int(final[source["optional"][1]] == 2)]
    assert bits == row["bits"]
    assert row["trial_counts"] == [int(list(pair) == bits) for pair in SETTINGS]
    assert not any(set(source["readers"]) <= set(group) for group in groups)
    checked["structural_contexts"] += 1

    if "local_records" in row:
        for order in ("edited", "final"):
            verify_certificates(row[order + "_supports"], row[order + "_support_certificate"], law)
        for key in ("prepared_old", "uniform_edited", "uniform_final"):
            mass = row["state_weightings"][key + "_total"]
            assert row["state_weightings"][key + "_joint_counts"] == [mass * n for n in row["trial_counts"]]
        check_value_records(source, row, law, checked)


def compare_distributions(left, right, mode):
    if left["structure"] != right["structure"]:
        return Fraction(1)
    a, b = normalized(left[mode]), normalized(right[mode])
    return sum(abs(a.get(key, 0) - b.get(key, 0)) for key in set(a) | set(b)) / 2


def check_table(source, law, data, checked):
    rows = data["contexts"]
    assert [tuple(row["settings"]) for row in rows] == list(SETTINGS)
    for row in rows:
        check_row(source, row, law, checked)
    expected_e = [1 if row["bits"][0] == row["bits"][1] else -1 for row in rows]
    assert data["correlations"] == expected_e
    assert data["signed_s"] == expected_e[0] + expected_e[1] + expected_e[2] - expected_e[3]
    expected = {signs: sum(sign * e for sign, e in zip(signs, expected_e, strict=True))
                for signs in product((-1, 1), repeat=4) if signs.count(-1) % 2}
    assert {tuple(row["signs"]): row["score"] for row in data["sign_scores"]} == expected
    assert data["maximum"] == max(expected.values())
    for side, pairs in enumerate(REMOTE_PAIRS):
        for own, (a, b) in enumerate(pairs):
            tv_bit = int(rows[a]["bits"][side] != rows[b]["bits"][side])
            assert tv_bit == data["selected_bit_far_setting_tv"][side][own]
            for mode, observed in data["accessible_record_far_setting_tv"].items():
                if mode == "structure_only":
                    assert observed[side][own] == int(rows[a]["structural_records"][side] != rows[b]["structural_records"][side])
                else:
                    tv_full = compare_distributions(rows[a]["local_records"][side], rows[b]["local_records"][side], mode)
                    assert Fraction(*observed[side][own]) == tv_full
                    assert tv_full >= tv_bit


def main():
    record = json.loads(gzip.decompress(DATA.read_bytes()))
    checked = Counter()
    assert len(record["robustness"]) == 33
    assert sum("ineligible" in row for row in record["robustness"]) == 3
    for row in record["built"] + record["robustness"]:
        for law, table in row.get("law_tables", {}).items():
            check_table(row, law, table, checked)
    checked["canonical_projected_relations"] = old_verifier.canonical_verdict.cache_info().currsize
    print(json.dumps(dict(checked)))


if __name__ == "__main__":
    main()
