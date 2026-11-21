"""Replay the complete ordinary and normalized signed word records on the registered switch."""

import argparse
from fractions import Fraction
import gzip
import hashlib
from io import BytesIO
from itertools import product
import json
import os
from pathlib import Path
import resource
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
RESEARCH = ROOT / "research" / TICKET
OUTPUT = ROOT / "artifacts" / TICKET / HERE.name


def exact_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def compressed(value):
    encoded = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    buffer = BytesIO()
    with gzip.GzipFile(filename="", fileobj=buffer, mode="wb", mtime=0) as stream:
        stream.write(encoded)
    return buffer.getvalue()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def store(path, content, *, check):
    if check:
        if path.read_bytes() != content:
            raise SystemExit(f"Replay differs at {path.relative_to(ROOT)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def limit_resources():
    limit = 4 * 1024**3
    _, hard = resource.getrlimit(resource.RLIMIT_AS)
    cap = limit if hard == resource.RLIM_INFINITY else min(limit, hard)
    resource.setrlimit(resource.RLIMIT_AS, (cap, hard))
    if hasattr(os, "sched_getaffinity"):
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
    for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[name] = "1"


def canonical_keeper():
    """All assignments to 19 other places reduce the 22-place keeper to five ternary fibers."""
    words = list(product((0, 1), repeat=3))
    names = ("a", "b", "c")
    fibers = {
        "other_parity_even": ([w for w in words if sum(w) % 2 == 0], 2**18),
        "other_parity_odd": ([w for w in words if sum(w) % 2 == 1], 2**18),
        "other_nae_all_zero": ([w for w in words if any(w)], 1),
        "other_nae_all_one": ([w for w in words if not all(w)], 1),
        "other_nae_mixed": (words, 2**19 - 2),
    }
    receipts = {}
    for name, (allowed, count) in fibers.items():
        clauses = [
            " ".join(("-" if bit else "") + letter for letter, bit in zip(names, word))
            for word in words
            if word not in allowed
        ]
        cnf = "; ".join(clauses) if clauses else "a -a"
        command = [
            sys.executable,
            "-B",
            "-m",
            "knotlab",
            "check",
            "--cnf",
            cnf,
            "--loops",
            "a",
            "b",
            "--contact",
            "c",
            "--json",
        ]
        verification = subprocess.run(
            command,
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT / "tools")},
            check=True,
            text=True,
            capture_output=True,
        )
        result = json.loads(verification.stdout)
        assert result["allowed"] == ["".join(map(str, word)) for word in allowed]
        assert result["binding"] == (len(allowed) < 8)
        assert result["coexistence"] and result["invisible_in_parts"] and result["loss_on_erasure"]
        receipts[name] = dict(cnf=cnf, rest_assignments=count, canonical=result)
    return receipts


def verify_completions(formal):
    """Cross-check complete effect entries against required singleton data and exact integer spectra."""
    from completed_menu import ARCHIVE

    original = json.loads(gzip.decompress(ARCHIVE.read_bytes()))["uniform_switch"]
    archive_sign_table = []
    for physical_arm, arm in zip(original["directions"], formal["loads"], strict=True):
        nodes = physical_arm["traces"]["loaded"]["nodes"]
        cohort = arm["full_cohort"]
        input_ids, output_ids = cohort["input_ids"], cohort["output_ids"]
        event_prob = {
            (n["id"], e["target"]): Fraction(e["chance_given_source"])
            for n in nodes
            if n["id"] in input_ids
            for e in n["enabled_events"]
        }
        ops = cohort["operations"]
        marked = ops["active_one_output_effects"]
        for y, effect in zip(output_ids, marked["effect_numerators"], strict=True):
            for i, w in enumerate(input_ids):
                assert Fraction(effect[i][i], marked["denominator"]) == event_prob.get((w, y), 0)
                for j, v in enumerate(input_ids):
                    if not event_prob.get((w, y)) or not event_prob.get((v, y)):
                        assert effect[i][j] == 0
        for name in ("matched_reflection", "binary_characters"):
            v = ops[name]["amplitude_numerators"]
            divisor = ops[name]["squared_column_denominator"]
            for i, w in enumerate(input_ids):
                for j, z in enumerate(input_ids):
                    assert sum(row[i] * row[j] for row in v) == divisor * int(i == j)
                for row, y in zip(v, output_ids, strict=True):
                    assert Fraction(row[i] ** 2, divisor) == event_prob.get((w, y), 0)
        reports = {
            "ordinary": ops["classical_uniform_center_and_shift"]["reported"],
            "matched": ops["matched_reflection"]["reports"],
            "label_ordered": ops["binary_characters"]["reports"],
            "one_active_outgoing_mark": marked["reports"],
        }
        target_chances = {k: [r["target"]["plus"], r["target"]["minus"]] for k, r in reports.items()}
        assert target_chances == {
            "ordinary": ["1/8", "1/8"],
            "matched": ["0", "1/4"],
            "label_ordered": ["1/4", "0"],
            "one_active_outgoing_mark": ["1/4", "0"],
        }
        for r in reports.values():
            for kind in ("singleton_a", "singleton_b", "dephased", "plus", "minus"):
                assert Fraction(r["target"][kind]) + Fraction(r["complement"][kind]) == 1
        for i in input_ids:
            expected = {y for w, y in event_prob if w == i}
            produced = [
                control["targets_by_input"][input_ids.index(i)]
                for control in ops["classical_uniform_center_and_shift"]["conditional"].values()
            ]
            assert len(produced) == 8 and set(produced) == expected
        perms = arm["symmetry"]["permutations"]
        assert sum(p["transposition"] for p in perms) == 6
        assert sum(p["odd"] and p["fixes_target"] for p in perms) == 3
        archive_sign_table.append(
            dict(
                old_words=len(input_ids),
                complete_words=len(output_ids),
                singleton_offers=len(event_prob),
                target_plus_minus=target_chances,
                past_fixed_transpositions=sum(p["transposition"] for p in perms),
            )
        )
    assert len(archive_sign_table) == 2
    return archive_sign_table


def compare_ordinary_replay(ordinary, formal):
    """Bind the independently reconstructed menus, preparations and pointer to the signed calculation."""
    registered = (12, 13)
    for arm, mathematics in zip(ordinary["directions"], formal["loads"], strict=True):
        cohort = mathematics["full_cohort"]
        prepared = mathematics["same_ordinary_history_cross"]
        raw_menu = arm["product_structure"]
        assert raw_menu["incoming_groups"] == [list(group) for group in cohort["old_loose_groups"]]
        assert [row["outgoing"] for row in raw_menu["centers"]] == [
            list(group) for group in cohort["new_loose_groups"]
        ]
        assert [row["center"] for row in raw_menu["centers"]] == cohort["corrective_centers"]
        event_rows = [offer for center in raw_menu["centers"] for offer in center["original_edges"]]
        lookup = {(offer["input_node"], offer["target"]): offer for offer in event_rows}
        assert len(lookup) == 128
        inputs, outputs = cohort["input_ids"], cohort["output_ids"]
        for i, old in enumerate(inputs):
            for j, new in enumerate(outputs):
                assert bool(cohort["arch_legal_support"][j][i]) == ((old, new) in lookup)
        selection = arm["original_enrollment"]["exact_selection"]
        assert prepared["pair_selection"] == selection["pair_selected"] == "1/8"
        assert selection["pair_selected_and_target"] == selection["pair_rejected_and_target"] == "1/64"
        assert selection["target_any_intake"] == "1/32"
        for w in registered:
            assert selection["both_input_masses"][str(w)] == prepared["unfiltered_intakes"][w] == "1/16"
        readings = arm["original_readings"]
        actual = readings["post_word"]
        computed = cohort["operations"]["classical_uniform_center_and_shift"]["reported"]
        for w, z in (
            ("a", "singleton_a"),
            ("b", "singleton_b"),
            ("mixture", "dephased"),
            ("plus", "plus"),
            ("minus", "minus"),
        ):
            for port in ("target", "complement"):
                assert actual[port][w] == computed[port][z]
        for name in (
            "named_firing_and_post_word",
            "incoming_firing_and_post_word",
            "physically_latched_firing_and_post_word",
        ):
            assert Fraction(readings[name]["sharp_possible_sign_contrast_from_this_calibration"]) == 0
        assert Fraction(actual["sharp_possible_sign_contrast_from_this_calibration"]) == Fraction(1, 4)
        assert all(
            r["whole_literal_menu_count"] == 4 and r["probability_of_original_complete_target"] == 0
            for r in arm["active_two_mark_preload"]["cohort"]
        )
        laws = arm["original_law_status"]
        assert laws["nae"]["lawfully_admitted_enrolled_attempts"] == 0
        assert laws["parity"]["lawfully_admitted_enrolled_attempts"] == 144
    keeper = ordinary["altered_keeper_attachment"]["original_and_augmented_control_comparison"]
    assert keeper["exact_tests"] == 3960 and keeper["differences"] == []
    assert keeper["readable_native_trigger_count"] == 0
    return dict(
        ordinary_kernel_checks=keeper["exact_tests"],
        verified_ordinary_offers_per_loading=128,
        dual_law_control_readings=ordinary["separate_two_law_loose_swap"][
            "independently_reproduced_crossing_count"
        ],
        standalone_keeper_knot_updates_under_both_laws=keeper[
            "individually_legal_keeper_pair_updates_under_both_laws"
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="require byte equality with every registered output"
    )
    args = parser.parse_args()
    limit_resources()

    # Leave the native-controller replay in a separate process, including its own memory limit.
    ordinary_command = [sys.executable, "-B", str(HERE / "physical.py")]
    if args.check:
        ordinary_command.append("--check")
    subprocess.run(ordinary_command, check=True)
    from symmetry import run

    formal = run()
    checks = verify_completions(formal)
    numbers = compressed(formal)
    store(OUTPUT / "completions.json.gz", numbers, check=args.check)
    physical_path = OUTPUT / "physical.json.gz"
    physical = json.loads(gzip.decompress(physical_path.read_bytes()))
    ordinary_checks = compare_ordinary_replay(physical, formal)
    sources = dict(physical["sources"])
    variants = dict(physical.get("public_source_variants", {}))
    # The public CLI labels three unrelated demo messages with the public guide's name.
    cli = "tools/knotlab/cli.py"
    sources[cli] = "c2ec94f3b8059049def1ef6c8c17e0e3a5d09d7c2d1d55234348a1189ea1d7bc"
    variants[cli] = "23d2cd2cf37a55367b8588c8b4ea9c3296bdc071a101c93eeb479f35439e8e1c"
    sources["tools/knotlab/__main__.py"] = (
        "c8a9d98b4dba941783360150b96b4be3004afaec6f602d2368bedc87b75ef7a4"
    )
    for path in [
        *HERE.glob("*.py"),
        HERE / "identity.json",
        HERE / "contract.json",
        RESEARCH / "preregistration.md",
        RESEARCH / "review_candidate_v2.md",
        RESEARCH / "design_for_review.md",
        RESEARCH / "design_reviews.md",
        RESEARCH / "partial_manifest_at_activation.json",
    ]:
        sources[str(path.relative_to(ROOT))] = digest(path.read_bytes())
    for relative, expected in sources.items():
        assert digest((ROOT / relative).read_bytes()) in (expected, variants.get(relative)), relative

    receipt = dict(
        ticket=TICKET,
        experiment=HERE.name,
        evidence_stage="exploratory",
        source_contribution=0,
        status="complete",
        scientific_referee="pending",
        inputs=dict(sorted(sources.items())),
        public_source_variants=variants,
        canonical_22_mark_keeper_fibers=canonical_keeper(),
        outputs={
            "physical.json.gz": digest(physical_path.read_bytes()),
            "completions.json.gz": digest(numbers),
        },
        checks=checks,
        independently_reconstructed_records=ordinary_checks,
        census={k: v for k, v in formal["stencils"].items() if k != "normalized_bitmaps"},
        full_archive={
            k: v
            for k, v in formal["global_archived_columns"].items()
            if k not in ("other_columns", "loads")
        },
    )
    encoded = exact_bytes(receipt)
    store(OUTPUT / "receipt.json", encoded, check=args.check)
    print(
        f"Full replay {digest(encoded)}. Two original loads, all singleton menus and both complete sign ports agree."
    )


if __name__ == "__main__":
    main()
