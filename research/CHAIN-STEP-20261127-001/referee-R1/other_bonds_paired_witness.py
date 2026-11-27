"""Direct raw truth table for the second checked chain on census entry 87 at round two."""

import argparse
from collections import Counter
import gzip
from itertools import combinations
import json
from pathlib import Path
from time import perf_counter

import numpy as np


HERE = Path(__file__).resolve().parent
FIXED = ((1, 3, 7), (6, 11, 16))
THIRD = (2, 4, 5)


def bits(names):
    return sum(1 << x for x in names)


def equal(states, names):
    mask = bits(names)
    intersection = states & mask
    return (intersection == 0) | (intersection == mask)


def mixed_witnesses(states, laws, names):
    value = equal(states, names)
    witnesses = []
    for i, law in enumerate(laws):
        source = states & bits(law)
        for fixed_local in np.unique(source):
            matches = source == fixed_local
            first = np.flatnonzero(matches & ~value)
            second = np.flatnonzero(matches & value)
            if len(first) and len(second):
                a, b = int(states[first[0]]), int(states[second[0]])
                assert a & bits(law) == b & bits(law)
                assert not equal(a, names) and equal(b, names)
                witnesses.append({"law": i, "agreement_zero_state": a, "agreement_one_state": b})
                break
    return witnesses


def minimal_sources(supports, violated_on_111, chain):
    m = len(supports)
    patterns, counts = np.unique(violated_on_111, return_counts=True)
    violation_count = dict(zip(map(int, patterns), map(int, counts)))
    sufficient = {
        retained for retained in range(1 << m)
        if all(retained & broken for broken in violation_count)
    }
    minimal = []
    for retained in sufficient:
        laws = [i for i in range(m) if retained >> i & 1]
        if any((retained ^ (1 << i)) in sufficient for i in laws):
            continue
        minimal.append({"law_indices": laws, "laws": [supports[i] for i in laws],
                        "outside_chain": sorted(set(laws).difference(chain))})
    return {
        "all_minimal_law_sets_excluding_111": sorted(minimal, key=lambda item: item["law_indices"]),
        "111_source_assignments_restored_by_one_deleted_law": [violation_count.get(1 << j, 0) for j in range(m)],
    }


def check_population():
    """Compare the names and missing words, using the independently produced six-reading table."""
    pairs = {}
    with gzip.open(HERE / "other_bonds_paired_all.jsonl.gz", "rt") as f:
        for line in f:
            row = json.loads(line)
            for record in row["fixed_pairs"]:
                bonds = {tuple(b["third"]): b["missing_words"] for b in record["bonds"]}
                for i, j in record["chain_and_pair_slots"]:
                    pairs[(row["start"], row["round"], i, j)] = bonds
    counts = Counter()
    with gzip.open(HERE / "stage_readings.jsonl.gz", "rt") as f:
        for line in f:
            row = json.loads(line)
            key = (row["start"], row["round"], row["chain_number"] - 1)
            for j in range(3):
                actual = pairs[key + (j,)]
                others = {tuple(sorted(z)) for k, z in enumerate(row["carriers"]) if k // 2 != j}
                for z in actual:
                    counts["fixed_pair_bond_incidences"] += 1
                    counts["third_among_the_other_four_named_carriers"] += z in others
            for bond in row["other_bonds_on_the_six_named_readings"]:
                counts["additional_named_bonds"] += 1
                names = [(ord(s[0]) - ord("A")) * 2 + int(s[1]) for s in bond["readings"]]
                good = 0
                for j in range(3):
                    if 2 * j not in names or 2 * j + 1 not in names:
                        continue
                    k, = [k for k in names if k // 2 != j]
                    z = tuple(sorted(row["carriers"][k]))
                    missing = pairs[key + (j,)].get(z)
                    good += missing == bond["missing_words"] == ["111"]
                    assert bond["mixed_fixes_by_upper_pair_and_function"][j] == [0, 0]
                assert good == 1
                counts["matched_third_missing_word_and_determination"] += 1
    assert counts["third_among_the_other_four_named_carriers"] == counts["matched_third_missing_word_and_determination"]
    return counts


def main():
    start = perf_counter()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    with gzip.open(HERE / "stages.jsonl.gz", "rt") as f:
        stage = next(row for line in f if (row := json.loads(line))["start"] == 87 and row["round"] == 2)
    laws = stage["supports"]
    chain = stage["checked_chains"][1]
    n = max(map(max, laws)) + 1
    size = 1 << (n - 3 if args.pilot else n)
    raw = np.arange(size, dtype=np.uint32)
    violated = np.zeros(size, dtype=np.uint16)
    for j, law in enumerate(laws):
        violated |= equal(raw, law).astype(np.uint16) << j
    agrees = [equal(raw, carrier) for carrier in (*FIXED, THIRD)]
    triple_code = agrees[0].astype(np.uint8) * 4 + agrees[1].astype(np.uint8) * 2 + agrees[2]
    allowed = raw[violated == 0]
    counts = np.bincount(triple_code[violated == 0], minlength=8)
    a_both = (agrees[0] & agrees[1])[violated == 0]
    a_either = (agrees[0] | agrees[1])[violated == 0]
    code = triple_code[violated == 0]
    words = {}
    for i, freq in enumerate(counts):
        idx = code == i
        both = sorted(map(int, np.unique(a_both[idx])))
        either = sorted(map(int, np.unique(a_either[idx])))
        if freq:
            assert both == [int(i & 6 == 6)] and either == [int(bool(i & 6))]
        words[format(i, "03b")] = {"source_states": int(freq), "upper_both": both, "upper_either": either}
    mixed = [{"carrier": c, "knot_witnesses": mixed_witnesses(allowed, laws, c)} for c in (*FIXED, THIRD)]
    report = {
        "stage": "second round of the four-knot census entry numbered 87",
        "checked_chain_number_counting_from_one": 2, "checked_chain_law_indices": chain, "source_laws": laws,
        "raw_state_encoding": "Bit i is the value of raw distinction i. A law index counts from zero.",
        "source_distinctions": n, "raw_assignments_examined": size,
        "allowed_source_assignments": len(allowed), "fixed_upper_pair": FIXED,
        "third_carrier": THIRD, "words_in_the_order_first_second_third": words, "mixed_witnesses": mixed,
    }
    report.update(minimal_sources(laws, violated[triple_code == 7], chain))
    xy = (equal(allowed, FIXED[0]).astype(np.uint8) * 2 + equal(allowed, FIXED[1])) * 2
    outside = sorted(set(range(n)).difference(*FIXED))
    bonds = []
    checked = 0
    for size_c in (2, 3):
        for z in combinations(outside, size_c):
            checked += 1
            wordset = np.bincount(xy + equal(allowed, z), minlength=8)
            present = [i for i in range(8) if wordset[i]]
            if len(present) < 8 and all(len({i & mask for i in present}) == 4 for mask in (3, 5, 6)):
                if len(mixed_witnesses(allowed, laws, z)) == len(laws):
                    bonds.append({"third": z, "missing": [format(i, "03b") for i in range(8) if not wordset[i]]})
            if args.pilot and checked >= 24:
                break
        if args.pilot:
            break
    report["third_carriers_examined"] = checked
    if not args.pilot:
        assert np.count_nonzero(counts) == 7 and counts[7] == 0
        assert all(len(row["knot_witnesses"]) == len(laws) for row in mixed)
        report["all_fixed_pair_bonds_by_direct_full_enumeration"] = bonds
        assert any(rec["third"] == THIRD and rec["missing"] == ["111"] for rec in bonds)
        report["separate_full_population_named_carrier_crosscheck"] = check_population()
    else:
        report["pilot_scope"] = "Initial one-eighth of the raw truth table. Missing words here have no whole-stage force."
    report["seconds"] = round(perf_counter() - start, 3)
    target = HERE / ("other_bonds_paired_witness_pilot.json" if args.pilot else "other_bonds_paired_witness.json")
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(size, len(allowed), list(map(int, counts)), report["seconds"])


if __name__ == "__main__":
    main()
