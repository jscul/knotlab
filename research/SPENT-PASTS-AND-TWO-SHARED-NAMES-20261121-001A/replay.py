"""Reproduce both independent B252 observation files and the source-hash receipt."""

import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path

import built_independent
import controls
import far_growth


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STAGE = HERE / "stage_observations.json.gz"
REMOTE = HERE / "remote_observations.json.gz"
RECEIPT = HERE / "receipt.json"


def digest_bytes(data):
    return sha256(data).hexdigest()


def packed(value):
    return gzip.compress(
        (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(),
        mtime=0,
    )


def canonical_json(value):
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    ).encode()


def reverse_index(i, n):
    return sum(((i >> j) & 1) << (n - 1 - j) for j in range(n))


def vote_signature(n, w, dense, scores):
    return int(n), int(w), tuple(dense), tuple(sorted(scores))


def walk(obj):
    if isinstance(obj, dict):
        if "whole_current_weights" in obj and "single_holder_results" in obj:
            yield obj
        else:
            for child in obj.values():
                yield from walk(child)
    elif isinstance(obj, (list, tuple)):
        for child in obj:
            yield from walk(child)


def crosscheck(built, worker):
    signatures = {}
    for name, history in built.items():
        for frame in history:
            count = frame["complete_lex_count_table"]
            denom = frame["weights"]
            scores = [
                tuple(m["signed_scores"])
                for m in frame["local_score_and_full_integer_grams"].values()
            ]
            key = vote_signature(
                denom["full_word_count"], denom["sum_squared_pasts"], count, scores
            )
            signatures.setdefault(key, []).append((name, frame))
    observed = Counter()
    named = 0
    entries = 0
    for one in walk(worker["built_histories"]):
        marks = one["whole_current_weights"]
        saved = marks["counts_by_current_word_int"]
        width = len(saved).bit_length() - 1
        dense = [saved[reverse_index(i, width)] for i in range(len(saved))]
        records = [site["read"] for site in one["single_holder_results"]]
        if one["three_holder_result"].get("read"):
            records.append(one["three_holder_result"]["read"])
        scores = [
            tuple(
                rec[k]["settings_and_scores"]["signed_M_XXX_minus_three_XZZ"]
                for k in ["unread_past_D", "pure_squared_count"]
            )
            for rec in records
        ]
        key = vote_signature(
            marks["N_complete_words"], marks["W_sum_squared_past_counts"], dense, scores
        )
        assert key in signatures
        # First match using labelled marks, then compare all eight probabilities at all eight settings.
        matches = [
            frame
            for _, frame in signatures[key]
            if sorted(tuple(x["physical_triple_in_bit_order"]) for x in records)
            == sorted(
                tuple(s["marks"])
                for s in frame["local_score_and_full_integer_grams"].values()
            )
        ]
        assert matches or not records
        if records:
            tables = {
                tuple(s["marks"]): s
                for s in matches[0]["local_score_and_full_integer_grams"].values()
            }
            for rec in records:
                marked = tuple(rec["physical_triple_in_bit_order"])
                for db, kind in [
                    ("D_gram", "unread_past_D"),
                    ("Q_gram", "pure_squared_count"),
                ]:
                    e = controls.prob_table(controls.as_array(tables[marked][db]))
                    for st, row in rec[kind]["settings_and_scores"][
                        "every_joint_probability"
                    ].items():
                        sk = "".join("1" if v == "X" else "0" for v in st)
                        direct = [
                            str(
                                F(
                                    row["numerators"][reverse_index(i, 3)],
                                    row["denominator"],
                                )
                            )
                            for i in range(8)
                        ]
                        assert direct == e["rows_lex_outcomes"][sk], (st, marked)
                        entries += 8
                named += 1
        observed[key] += 1
    assert observed == Counter({key: len(value) for key, value in signatures.items()})
    return {
        "complete_built_law_stages": sum(observed.values()),
        "named_three_reader_placements": named,
        "independently_recomputed_probability_entries": entries,
        "all_compared": True,
    }


def remote_data():
    cases = far_growth.run()
    for name, pair in cases["two_arms_genuinely_loose_local_post_age"].items():
        m, law = name.split("/")
        if law == "nae":
            a = far_growth.general_relay(int(m) // 2)
            match = pair["matched_reached_local_packet"]
            assert (
                match["ordinary_A_minus_B_first_fresh_equality"]
                == a["ordinary_same_packet_first_fresh_A_minus_B"]
            )
            assert match["flat_remote_division_A_minus_B_first_fresh_equality"] == "0"
            pair["independent_all_length_evaluation"] = a
    core = {law: controls.core_fixture(law) for law in ("parity", "nae")}
    assert core["parity"]["change_on_two_children"]["retained_moment"] == "0"
    assert core["parity"]["change_on_two_children"]["all_clean_moment"] == "1"
    return {
        "funded_cases": cases,
        "same_first_round_literal_positive_fixture": core,
        "old_ordinary_or_spectator_records": controls.preserved_records(),
        "one_interface_and_disconnected": controls.interfaces(),
        "full_effect_vs_offered_XZ": controls.observer_scope(),
        "component_parity": controls.parity_examples(),
        "literal_score_signs_and_classical_bounds": controls.score_bounds(),
        "built_independent": built_independent.run(),
    }


def source_bindings(extra):
    prior = far_growth.prior
    files = set(map(str, extra))
    files |= {
        str(path.relative_to(ROOT))
        for path in [
            built_independent.ARCHIVE,
            prior.GROWTH,
            prior.COUNTING,
            far_growth.PRIOR / "growth_weights.py",
            far_growth.PRIOR / "results.md",
            far_growth.PRIOR / "observations.json.gz",
            ROOT / "research/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A/counting.md",
            ROOT / "research/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A/growth_motion.md",
            ROOT / "research/BOND-CLOSURE-20261120-001/bond_radius.md",
            ROOT / "research/BOND-CLOSURE-20261120-001/criterion.md",
            ROOT / "research/ORDINARY-DYNAMICS-20261120-001/end_operator.md",
            ROOT / "research/THREE-READERS-AND-GROWTH-20261120-001A/results.md",
            ROOT / "research/JOINT-PARENTS-AND-ERASURE-20261120-001B/results.md",
            *HERE.glob("*.py"),
            HERE / "historical_fixture.txt",
            HERE / "preregistration.md",
            HERE / "design_reviews.json",
        ]
    }
    files.update(prior.ENGINE_INPUTS)
    return {name: digest_bytes((ROOT / name).read_bytes()) for name in sorted(files)}


def save_or_check(path, data, check):
    if check:
        assert path.read_bytes() == data, f"Canonical replay differs at {path.name}"
    else:
        path.write_bytes(data)
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": len(data),
        "sha256": digest_bytes(data),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--component", choices=["all", "remote", "stages"], default="all"
    )
    opts = parser.parse_args()
    if opts.component != "stages":
        remote = remote_data()
        row = save_or_check(REMOTE, packed(remote), opts.check)
        print(row, flush=True)
        if opts.component == "remote":
            return
    import stage_replay

    stages = stage_replay.run()
    stage_row = save_or_check(STAGE, packed(stages), opts.check)
    print(stage_row, flush=True)
    if opts.component == "stages":
        return
    checks = crosscheck(remote["built_independent"], stages)
    raw = source_bindings(stages["source_sha256"])
    receipt = {
        "status": "registered scientific measurements complete; independent referee pending",
        "preregistration_sha256": digest_bytes(
            (HERE / "preregistration.md").read_bytes()
        ),
        "remote_and_independent_control_archive": row,
        "full_stages_archive": stage_row,
        "independent_built_check": checks,
        "source_sha256": raw,
        "canonical_checker_code_sha256_after_guide_title_normalization": {
            str(q.relative_to(ROOT)): digest_bytes(
                q.read_bytes().replace(b"docs/KNOT_INTUITION.md", b"INTUITIONS.md")
            )
            for q in sorted((ROOT / "tools/knotlab").glob("*.py"))
        },
        "private_ways_squared_script_optional": "Historical source SHA-256 4bd90354c38e35fc242f4340c59687ec6ebc2bb560543a36086e91e00389febc. Only its already published mathematics and the saved text outputs are needed here.",
    }
    print(
        save_or_check(RECEIPT, canonical_json(receipt), opts.check), checks, flush=True
    )


if __name__ == "__main__":
    main()
