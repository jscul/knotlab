"""Reproduce the two-pointer preparation, complete ordinary records and real measurement tables."""

import argparse
import gzip
from hashlib import sha256
import io
import json
from pathlib import Path

from real_algebra import Catalogue
from sources_and_reads import (
    sources_and_reads,
    label_tables,
    whole_sector_match,
    ideal_poststates,
    joint_writes,
)
from reference_controls import reference_controls, ancillary_access


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COUNT = "KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001"
ERASE = "ERASURE-AND-CLOSING-SIGNS-20261121-001A"
IDLE = "IDLE-PHASE-AND-TREE-CLOSURE-20261121-001A"


def bindings():
    src = [
        HERE / name
        for name in (
            "replay.py",
            "real_algebra.py",
            "sources_and_reads.py",
            "reference_controls.py",
            "pointer_hardware.py",
            "preregistration.md",
            "design_reviews.md",
        )
    ]
    src.extend(
        ROOT / "research" / (COUNT + "A") / name
        for name in (
            "cyclic_pointer.py",
            "native_counts.py",
            "knot_counts.py",
            "results.md",
        )
    )
    src.extend(
        ROOT / "research" / COUNT / name
        for name in ("phase_comparison.md", "phase_check.py")
    )
    src.extend(
        ROOT / "research" / ERASE / name for name in ("ordinary_routes.py", "keeper.py")
    )
    src.append(ROOT / "research" / IDLE / "physical_composition.py")
    for t, desc in (
        (COUNT + "A", "counts"),
        (COUNT + "Z", "synthesis"),
        (ERASE, "keeper"),
        (IDLE, "composition"),
    ):
        p = ROOT / "proofs" / t / (t + "-P001_" + desc)
        src.extend((p / "manifest.json", p / "proof.md"))
    return {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in src}


def build():
    from pointer_hardware import hardware_checks

    cat = Catalogue()
    a = sources_and_reads(cat)
    a["subnormalized_label_tables"] = label_tables(a["charge_preparations"], cat)
    a["sector_matching_minor"] = whole_sector_match()
    a["complex_calibrator_full_poststates_in_1_omega"] = ideal_poststates(cat)
    a["reunion_and_additional_resources"] = reference_controls(cat)
    a["generic_shared_real_ancillary_states"] = ancillary_access(cat)
    a["physical_words"] = hardware_checks()
    a["actual_keeper_pushforward"] = joint_writes(a, a["physical_words"])
    a["matrix_library"] = cat.matrices
    a["source_sha256"] = bindings()
    return a


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    obj = build()
    data = (
        json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        + "\n"
    ).encode()
    stream = io.BytesIO()
    with gzip.GzipFile(
        filename="", mode="wb", fileobj=stream, compresslevel=9, mtime=0
    ) as g:
        g.write(data)
    packed = stream.getvalue()
    path = HERE / "observations.json.gz"
    if args.write:
        path.write_bytes(packed)
    elif path.read_bytes() != packed:
        raise AssertionError(
            "Reconstructed exact observations differ from their frozen receipt"
        )
    print(
        f"PASS. {len(data)} exact JSON bytes, {len(packed)} gzip bytes, {len(obj['matrix_library'])} distinct exact matrices. SHA-256 {sha256(packed).hexdigest()}"
    )


if __name__ == "__main__":
    main()
