"""Rebuild exact conditional data maps, source histories and both-law physical records."""

import argparse
from fractions import Fraction as F
import gzip
from hashlib import sha256
import io
from itertools import product
import json
from pathlib import Path
from instrument_math import Catalogue, IX, add, effect, input_library, born
from coherent_meter import (
    coherent_evidence,
    branches,
    joint_controls,
    maps,
    parity,
    BELL_PHASE,
)
from mixed_reference import (
    path_mark_and_full_read,
    primary_evidence,
    data_channels,
    paired_ports,
    local_ports,
    Root,
    YRHO,
    parity_flag,
)
from resource_cuts import cuts, binary_source
from launch_records import all_launches, instrument_grades

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = "TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001"
SIX = "TWO-KNOTS-ONE-DECISION-20261121-001"
ERASE = "ERASURE-AND-CLOSING-SIGNS-20261121-001A"
IDLE = "IDLE-PHASE-AND-TREE-CLOSURE-20261121-001A"
COUNT = "KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001A"


def source_bindings():
    sources = list(HERE.glob("*.py")) + [
        HERE / "preregistration.md",
        HERE / "design_reviews.md",
    ]
    folders = {
        OLD: ["independent_checks.md", "founders.py", "real_readers.py"],
        OLD + "A": ["six_knots.md"],
        OLD + "B": [
            "pointer_hardware.py",
            "real_algebra.py",
            "sources_and_reads.py",
            "reference_controls.py",
            "observations.json.gz",
        ],
        SIX: ["mechanism.md", "measurement.py"],
        ERASE: ["ordinary_routes.py", "keeper.py"],
        IDLE: ["physical_composition.py"],
        COUNT: ["cyclic_pointer.py", "knot_counts.py", "native_counts.py"],
    }
    for folder, files in folders.items():
        sources.extend(ROOT / "research" / folder / f for f in files)
    bind = [
        (ERASE, "keeper"),
        (IDLE, "composition"),
        (COUNT, "counts"),
        (OLD + "B", "pointers"),
        (OLD + "Z", "synthesis"),
        (SIX + "P", "measurement"),
        (SIX + "Z", "synthesis"),
    ]
    for ticket, slug in bind:
        pr = ROOT / "proofs" / ticket / (ticket + "-P001_" + slug)
        sources.extend([pr / "manifest.json", pr / "proof.md"])
    a = OLD + "A"
    sources.extend(
        [
            ROOT
            / "artifacts"
            / a
            / (a + "-E001_meetings")
            / "matched_and_signed.json.gz",
            ROOT / "experiments" / a / (a + "-E001_meetings") / "contract.json",
        ]
    )
    return {
        str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
        for p in sorted(sources)
    }


def physical_join(cat, hardware):
    ports = hardware["local_interface"]["local_port_word_dictionary"]
    intact = {}
    for scheme, src, ch, raw in [
        ("binary_meter", F(1), maps(branches(joint_controls()), BELL_PHASE[1]), parity),
        (
            "reference_group",
            F(1, 8),
            data_channels(paired_ports(local_ports(), local_ports()), Root(YRHO[1])),
            parity_flag,
        ),
    ]:
        margins = {}
        expected = (
            (F(1, 2), F(1, 2))
            if scheme == "binary_meter"
            else (F(1, 2), F(1, 4), F(1, 4))
        )
        for site in (0, 1):
            for a, r in enumerate(expected):
                e = add([effect(v) for k, v in ch.items() if k[site] == a], 4)
                assert e == IX.scale(r)
                margins[f"{site}/{a}"] = {
                    "p_given_source_success": str(r),
                    "effect": cat.put(e),
                }
        banks = {}
        for reverse, stages_a, stages_b in product(
            ("0", "1"), ("00", "01", "10", "11"), ("00", "01", "10", "11")
        ):
            m = {}
            for (i, j), v in ch.items():
                local = [
                    ports[reverse][f"{scheme}/{'abc'[n]}/{s}/full"]
                    for n, s in ((i, stages_a), (j, stages_b))
                ]
                # Delivery requires both correct, physically written K words. A partial write can be a wrong word.
                valid = all(z["keeper_matches_flag"] for z in local)
                m[f"{i}{j}"] = {
                    "complete_word_history_keys": [
                        [reverse, f"{scheme}/{'abc'[n]}/{s}/full"]
                        for n, s in ((i, stages_a), (j, stages_b))
                    ],
                    "physical_keepers": [z["keeper"] for z in local],
                    "valid_keeper_pair": valid,
                    "intended_measured_sign": raw((i, j)),
                    "complete_word_pair_decodes": raw((i, j)) if valid else None,
                    "p_given_00_and_source_success": str(
                        born(input_library()["00"], effect(v))
                    ),
                    "whole_request_choi_even_if_write_failed": cat.put(v.scale(src)),
                }
            banks[f"{reverse}/{stages_a}/{stages_b}"] = m
        intact[scheme] = {
            "both_wing_fine_margins": margins,
            "all_stage_faults": banks,
            "source_rate_bound_in_tables": str(src),
            "consumed_source": "correct both binary heralds"
            if scheme == "binary_meter"
            else "prior hidden equal, admitted 1/8",
        }
    return intact


def build():
    from instrument_hardware import hardware_checks

    cat = Catalogue()
    hardware = hardware_checks()
    rec = {
        "ledger_rules": {
            "matrices": "Integers/denominator; two IDs mean A + sqrt(3) B. All probabilities are rational unless their real and sqrt(3) coefficients are shown.",
            "process_order": "Choi indexes (input spectator word, output word) with 00,01,10,11. Each 4x4 block i,j is the actual output on |i><j|. Joint-operation rows use (data AB, reference AB).",
            "whole_joint_state": "For operation O (numerator matrix and squared denominator n), source sigma and input rho, use O(rho tensor sigma)O^T/n, before or after code conversion specified by W. A nonzero branch can be normalized by its trace. Grouped mixtures sum each contributing subnormalized state. All fine paths and all zero probabilities remain represented.",
            "probes": "The local data–spectator Bell preparations start independent across readers. No spectator enters any gate.",
            "applied_controller": "Physical gates have canonical positive permutation lifts, calibrated real signs/splitters, and fixed q,s encodings. Ports in the corpus identify actual prior word histories; there is no extra firing-sensitive growth event.",
        },
        "hardware": hardware,
        "physical_word_probability_join": physical_join(cat, hardware),
        "mixed_reference": primary_evidence(cat),
        "reference_route_record_controls": path_mark_and_full_read(cat),
        "coherent_meter": coherent_evidence(cat),
        "reference_source_cuts": cuts(cat),
        "two_path_source": binary_source(cat),
        "complete_request_and_repeat": all_launches(cat),
        "conditional_fidelity_and_choi": instrument_grades(cat),
    }
    rec["matrix_library"] = cat.matrices
    rec["source_sha256"] = source_bindings()
    return rec


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    switch = parser.add_mutually_exclusive_group(required=True)
    switch.add_argument("--write", action="store_true")
    switch.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record = build()
    data = (json.dumps(record, separators=(",", ":"), sort_keys=True) + "\n").encode()
    stream = io.BytesIO()
    with gzip.GzipFile(
        filename="", mode="wb", fileobj=stream, mtime=0, compresslevel=9
    ) as f:
        f.write(data)
    packed = stream.getvalue()
    dst = HERE / "observations.json.gz"
    if args.write:
        dst.write_bytes(packed)
    elif dst.read_bytes() != packed:
        raise ValueError("Reconstruction differs from the archived canonical bytes.")
    print(
        f"{len(record['matrix_library'])} exact matrices; {len(packed)} bytes; sha256 {sha256(packed).hexdigest()}"
    )
    print(
        "16 input-unit channels, physical words, source flags, repeat branches and fine/coarse instruments passed."
    )


if __name__ == "__main__":
    main()
