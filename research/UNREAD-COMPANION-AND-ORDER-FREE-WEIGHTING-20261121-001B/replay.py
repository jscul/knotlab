"""Reproduce fair reveals through five distinctions, history controls and ordinary growth."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as F
import gzip
from hashlib import sha256
import io
import json
from pathlib import Path

from extensions import history_checks, single_checks, transfer_checks
from finite_relations import control_checks, count_supports
from growth_weights import growth_checks
from marked_archive import ARCHIVE, audit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = "ENTANGLEMENT-READ-20261120-001"
ENG = "ORDINARY-DYNAMICS-20261120-001"
NAE = "NAE-GROWTH-20261119-001"
HEAVY = "HEAVY-GROWTH-20261119-001"


def source_files():
    targets = list(HERE.glob("*.py")) + [
        HERE / "preregistration.md",
        HERE / "design_reviews.json",
        HERE / "prior_work.md",
        HERE / "historical_replay.txt",
        ARCHIVE / "exact_readings.json.gz",
        ARCHIVE / "summary.json",
    ]
    for lane, docs in {
        OLD: ["decision.md", "preregistration.md"],
        ENG: ["end_operator.md"],
        NAE: ["nae_growth.md"],
        HEAVY: ["sources.md", "pure.md"],
    }.items():
        targets.extend(ROOT / "research" / lane / f for f in docs)
    for lane, slug in [
        (OLD + "A", "common_state"),
        (OLD + "Z", "synthesis"),
        (ENG + "Z", "synthesis"),
        (NAE + "Z", "epic_closure"),
        (HEAVY, "heavy"),
    ]:
        b = ROOT / "proofs" / lane / (lane + "-P001_" + slug)
        targets.extend([b / "proof.md", b / "manifest.json"])
    for ticket, slug, names in [
        (
            OLD + "B",
            "separated_readings",
            ("contract.json", "run.py", "summarize.py", "exact_counts.py"),
        ),
        (ENG + "A", "ordinary", ("contract.json",)),
        (NAE + "B", "nae", ("contract.json",)),
    ]:
        b = ROOT / "experiments" / ticket / (ticket + "-E001_" + slug)
        targets.extend(b / name for name in names)
    return {
        p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest()
        for p in sorted(targets)
    }


def physical_summary(p):
    by_group = defaultdict(Counter)
    table = {}
    for name, row in p["registered_sources"].items():
        for law, branch in row["laws"].items():
            counts = by_group[row["cohort"], law]
            counts["sources"] += 1
            counts[branch["status"]] += 1
            w = branch.get("weights")
            if w:
                label = {None: "undecided", True: "equal", False: "unequal"}[
                    w["constant_full_old_fibre"]
                ]
                counts[label] += 1
                mark = w["marked_projection"]
                table[name + "/" + law] = {
                    "source": row["cohort"],
                    "status": branch["status"],
                    "births": len(branch["births"]),
                    "full_fibre": label,
                    "old_completions": w["moments_of_full_old_fibre"],
                    "one_marked_pair_equality": mark["equality_event"],
                    "marked_U_TV": mark["marked_TV_U_grown_vs_U_initial"],
                    "marked_L_TV": mark["marked_TV_L_grown_vs_U_initial"],
                    "witnessed_full_fibre_sizes": [
                        x["total_extensions"]
                        for x in w["actual_old_word_and_complete_extension_witnesses"]
                    ],
                    "maximum_registered_indices": p["method"]["cap"],
                }
    return {
        "groups": {"/".join(k): dict(v) for k, v in sorted(by_group.items())},
        "all_fresh_and_fixed": table,
    }


def join_transfer(p, t):
    out = {}
    for m, row in p["fixed_parallel_name_chains"].items():
        witness = row["witness"]["laws"]["nae"]
        ref = t["repaired_family"][m]
        assert witness["one_birth_spends_both_designated_loose_names"]
        (birth,) = witness["births"]
        assert birth["fresh_grant"] == 1 and len(birth["consumed_old_names"]) == 2
        mark = witness["weights"]["marked_projection"]["equality_event"]
        assert [
            F(mark[k]["probability"]) for k in ("before_U", "after_U", "after_L")
        ] == [F(ref[k]) for k in ("old_U", "new_U", "transported_L")]
        distances = [
            d["minimum_number_of_holder_meetings"]
            for d in witness["holder_meetings_from_each_birth_to_the_mark"]
        ]
        assert distances == [ref["distance_in_holder_meetings"]]
        par = row["witness"]["laws"]["parity"]
        (closing,) = par["births"]
        assert closing["fresh_grant"] == 0
        gate = closing["binary_closing_arity_certificate"]
        assert (
            not gate["canonical_K1_K2_K3"]
            and gate["relation_K1_K2_K3_without_arity_gate"]
        )
        control = {}
        for law, arm in row["direct"]["laws"].items():
            assert all(len(b["consumed_old_names"]) == 1 for b in arm["births"])
            assert arm["weights"]["constant_full_old_fibre"]
            control[law] = [len(b["fresh_names"]) for b in arm["births"]]
        out[m] = {
            "independent_exact_distributions_agree": True,
            "names_consumed": birth["consumed_old_names"],
            "fresh": birth["fresh_names"],
            "meetings_to_mark": distances[0],
            "parity_binary_arity": gate,
            "original_direct_control_fresh_grants": control,
            "old": ref["old_U"],
            "new": ref["new_U"],
            "change": ref["signed_change"],
        }
    return out


def compute():
    finite = count_supports()
    archive = audit()
    transfer = transfer_checks()
    physical = growth_checks()
    private_sha = "eccc2a101efa8338bbd027441ef22888f3ca08be2a2f08f877f60f5ae5f0fb80"
    assert [finite[str(n)]["nonempty_passing"] for n in (2, 3, 4)] == [11, 51, 307]
    return {
        "full_labelled_finite_census": finite,
        "literal_fixed_order_controls": control_checks(),
        "nonuniform_support_and_empty_cuts": single_checks(),
        "history_examples": history_checks(),
        "independent_analytic_physical_evaluation": transfer,
        "actual_funded_growth": physical,
        "growth_scope_summary": physical_summary(physical),
        "merge_two_physical_methods": join_transfer(physical, transfer),
        "archived_233_placement_audit": archive,
        "source_sha256": source_files(),
        "private_script_comparator": {
            "historical_sha256": private_sha,
            "replayed_prior_nonempty_counts": [[11, 15], [51, 255], [307, 65535]],
            "file": "historical_replay.txt",
            "private_file_required_by_public_check": False,
        },
        "measure": "0 is the least significant coordinate in the little-endian relation masks. Archived marked arrays retain their original written coordinate order. Initial/transport and uniform-stage weights are charged separately at every actual stage.",
    }


def packed(record):
    raw = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
    out = io.BytesIO()
    with gzip.GzipFile(
        filename="", fileobj=out, mode="wb", mtime=0, compresslevel=8
    ) as sink:
        sink.write(raw)
    return out.getvalue()


def main():
    a = argparse.ArgumentParser(description=__doc__)
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    opts = a.parse_args()
    record = compute()
    data = packed(record)
    p = HERE / "observations.json.gz"
    if opts.write:
        p.write_bytes(data)
    elif p.read_bytes() != data:
        raise ValueError(
            "The complete weighting evidence differs from its canonical replay"
        )
    print(
        f"{len(data)} bytes; {record['full_labelled_finite_census']['5']['nonempty_passing']} five-bit passing relations; {len(record['archived_233_placement_audit']['all_first_grown_selected_integer_marked_weightings'])} law-placement records; SHA-256 {sha256(data).hexdigest()}"
    )


if __name__ == "__main__":
    main()
