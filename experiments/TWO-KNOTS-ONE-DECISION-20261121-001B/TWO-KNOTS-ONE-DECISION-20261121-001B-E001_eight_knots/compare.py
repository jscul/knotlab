"""Compare sealed predictions, the shared experiment, and archived probabilities."""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path


SEALED_PREDICTIONS = "d65aa60b9e20625e641e5a5afee92da17d5c504fef6d38be21d13f7439203bf4"


def law(cells, den):
    result = {(a, b): Fraction(x, den) for a, b, x in cells}
    assert sum(result.values()) == 1
    return result


def source_displayed(rows, phase):
    return {tuple(row["settings"]): (law(row[phase]["cells"], row[phase]["denominator"]) if row[phase] else None)
            for row in rows}


def verify_geometry(sealed, shared_result, archive):
    assert sealed["mark_owners"] == archive["cube_sharing"] == shared_result["mark_owners"]
    assert sealed["holdings"] == archive["cube_stars"] == shared_result["physical_holding_mark_names"]
    assert sealed["left"] == shared_result["roles"][0]
    assert sealed["right"] == shared_result["roles"][1]
    assert sealed["design_sha256"] == shared_result["design_sha256"]


def verify_named_certificate(sealed):
    holdings = sealed["holdings"]
    columns = set()
    rhs = 0
    counts = Counter()
    for row in sealed["strict"]["xor_certificate"]:
        kind, *names = row["origin"]
        if kind == "preserve":
            mark, h = names
            expected = {("d", mark, f) for f in holdings[h]}
        elif kind == "undo":
            mark, = names
            expected = {("d", mark, mark)}
        elif kind == "commute":
            h, e, f = names
            assert e != f and e in holdings[h] and f in holdings[h]
            expected = {("d", e, f), ("d", f, e)}
        elif kind == "return":
            h, f = names
            expected = {("d", e, f) for e in holdings[h]}
        else:
            assert kind == "ordered_sign"
            h, = names
            expected = {("s", e) for e in holdings[h]}
            expected.update(("d", a, b) for a, b in combinations(sorted(holdings[h]), 2))
        assert expected == {tuple(term) for term in row["terms"]}
        signed = sealed["charge_by_holder"][h] if kind == "ordered_sign" else 0
        assert signed == row["rhs"]
        columns ^= expected
        rhs ^= signed
        counts[kind] += 1
    assert not columns and rhs == 1 and counts["ordered_sign"] == len(holdings)
    return counts


def archive_displayed(archive):
    # Published slots are lexical three-bit strings. Internal bit zero is the first listed place.
    words = [int(f"{value:03b}"[::-1], 2) for value in range(8)]
    return {tuple(row["inputs"]): law([(a, b, x) for (a, b), x in zip(product(words, repeat=2),
                                                                    row["numerator"], strict=True) if x],
                                    row["denominator"])
            for row in archive["cube_all_pairs"]}


def comparisons(sealed, computed, archive):
    reference = archive_displayed(archive)
    hold_checks = {}
    pairs = tuple(reference)
    for case in ("strict", "calibration", "all_even", "not_all_equal"):
        predicted = sealed[case]["table"]["settings"]
        actual = computed["fresh"]["calibrated" if case == "calibration" else case]["rows"]
        by_setting = source_displayed(actual, "launch")
        accepted = source_displayed(actual, "accepted")
        assert set(by_setting) == set(reference)
        for row in predicted:
            launch = law(row["nonzero_cells"], row["launch_denominator"])
            subset = [cell for cell in row["nonzero_cells"] if cell[0] < 8 and cell[1] < 8]
            conditional = law(subset, row["accepted_denominator"]) if row["accepted_denominator"] else None
            assert by_setting[tuple(row["settings"])] == launch
            assert accepted[tuple(row["settings"])] == conditional
        hold_checks[case] = "all 1,296 launch cells and every defined accepted cell agree"

    def compare_variant(case):
        observed = source_displayed(computed["fresh"][case]["rows"], "launch")
        details = []
        for setting in pairs:
            union = observed[setting].keys() | reference[setting].keys()
            differences = [p for p in union if observed[setting].get(p, 0) != reference[setting].get(p, 0)]
            examples = [{"words": p, "measured": str(observed[setting].get(p, 0)),
                         "published": str(reference[setting].get(p, 0))} for p in sorted(differences)]
            variation = sum(abs(observed[setting].get(p, 0) - reference[setting].get(p, 0)) for p in union) / 2
            details.append(dict(settings=setting, differing_cells=len(differences),
                                total_variation=str(variation), all_differences=examples))
        return details

    literal = compare_variant("literal_uniform")
    calibration = compare_variant("calibrated")
    strict = compare_variant("strict")
    assert all(row["differing_cells"] == 0 for row in literal)
    assert [row["settings"] for row in calibration if row["differing_cells"]] == [(0, 1)]
    assert len(calibration[0]["all_differences"]) == 16 and calibration[0]["total_variation"] == "1"
    assert all(row["total_variation"] == "1" for row in strict)
    for key in ("all_even", "calibrated"):
        for policies, panel in computed["tag_controls"][key]["fresh_panels"].items():
            for row in panel["rows"]:
                bad = tuple(row["score"].get(f"{wing}/wrong_word", "0") for wing in (0, 1))
                assert bad == tuple("1/2" if word in ("held", "ignored") else "0" for word in policies.split("/"))
    off_diagonal = computed["postmeasurement_write_and_pre_read_admission"]["off_diagonal_matrix_entry"]
    assert off_diagonal["not_ready"] == "1/32" and off_diagonal["disconnected"] == "0"
    return {"independent_predictions_vs_shared_compiler_and_physical_read": hold_checks,
            "reference_comparison": {"literal_uniform": literal, "calibrated": calibration, "strict": strict,
                                     "literal_biased": compare_variant("literal_biased")},
            "named_xor_certificate_row_counts": verify_named_certificate(sealed),
            "tag_and_writer_controls_rechecked": True}


def verify_histories(index_path, archive_path):
    index_data = index_path.read_bytes()
    index = json.loads(index_data)
    counted = Counter()
    codes = index["record_codes"]

    def check(table):
        assert sum(entry[-1] for entry in table["digits"]) == table["denominator"]
        assert all(w > 0 and all(0 <= i < len(codes) for i in (*a, *b)) for _, a, b, w in table["digits"])

    with gzip.open(archive_path, "rt") as stream:
        for record in stream:
            row = json.loads(record)
            counted[row["case"], row["panel"]] += 1
            raw = row["records"]
            if isinstance(raw, list):
                for table in raw:
                    check(table)
            elif raw is not None:
                check(raw)
            else:
                assert row["panel"] == "two_slot_privacy_witness"

    for case, summary in index["summary"].items():
        assert counted[case, "single_reader_pair"] == counted[case, "single_reader_return"] == 64
        assert counted[case, "joint_two_slots"] == 625
        assert counted[case, "held_reader_sweep"] == 16
        assert counted[case, "unilateral_then_adapt"] == counted[case, "remote_adapts_to_own_first_bit"] == 2
        odd = any(x["odd_charge_hypothesis"] for x in summary["held_reader_sweeps"])
        for sweep in summary["held_reader_sweeps"]:
            successful = not odd or all(Fraction(x["counted"]) >= 1 for x in sweep["bound_rows"])
            assert successful
        assert sum(weight["divergent"] for weight in summary["two_slots"]["privacy"]) == counted[
            case, "two_slot_privacy_witness"
        ]

    return dict(index_sha256=sha256(index_data).hexdigest(), compressed_history_sha256=sha256(archive_path.read_bytes()).hexdigest(),
                stored_rows=sum(counted.values()), stored_rows_by_case_and_panel={
                    f"{case}/{panel}": n for (case, panel), n in sorted(counted.items())
                }, case_count=len(index["summary"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--fresh", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check-histories", action="store_true")
    args = parser.parse_args()
    predicted = args.predictions.read_bytes()
    seal = sha256(predicted).hexdigest()
    if seal != SEALED_PREDICTIONS:
        raise ValueError("the independent prediction file changed")
    sealed = json.loads(predicted)
    with gzip.open(args.fresh, "rt") as stream:
        fresh = json.load(stream)
    archive_source = args.archive.read_bytes()
    archive = json.loads(archive_source)
    verify_geometry(sealed, fresh, archive)
    report = {"independent_prediction_sha256": seal, "reference_file": args.archive.as_posix(),
              "reference_sha256": sha256(archive_source).hexdigest(),
              "shared_output_sha256": sha256(args.fresh.read_bytes()).hexdigest(),
              **comparisons(sealed, fresh, archive)}
    if args.check_histories:
        folder = args.fresh.parent
        report["history_archive_validation"] = verify_histories(folder / "history_index.json", folder / "histories.jsonl.gz")
    with args.output.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
