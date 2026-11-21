"""Reproduce all B258 records, with an optional check of the private source-zero probe."""

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys

from cyclic_pointer import (
    all_registers_measured,
    balanced_source_calibration,
    ordinary_cycle_checks,
    quantum_cycle_checks,
)
from knot_counts import field, fixture_checks, single_counts
from native_counts import (
    B287,
    FREEDOM,
    HERE,
    ROOT,
    canonical_checks,
    growth_checks,
    keeper_checks,
    october_checks,
)
from reader_tables import check_source_zero, reader_checks


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def source_manifest():
    files = ["knot_counts.py", "cyclic_pointer.py", "native_counts.py", "reader_tables.py",
             "run_counts.py", "preregistration.md", "design_reviews.md", "source_inputs.json", "lead_reconciliation.json"]
    bindings = {str((HERE / name).relative_to(ROOT)): digest(HERE / name) for name in files}
    prior = json.loads((HERE / "source_inputs.json").read_text())["source_sha256_by_edition"]
    for name, editions in prior.items():
        actual = digest(ROOT / name)
        assert actual in editions.values(), f"Registered source differs in both editions: {name}"
        bindings[name] = editions["research"] if editions["research"] == editions["public"] else editions
    return bindings


def build():
    native = growth_checks()
    table = reader_checks()
    all_checks = {
        "scope": HERE.name,
        "single_occupancy_and_winding": single_counts(),
        "assemblies": fixture_checks(),
        "canonical_check": canonical_checks(),
        "ordinary_growth": native,
        "october_contraction": october_checks(),
        "fixed_keeper": keeper_checks(),
        "genuine_ordinary_controlled_C": ordinary_cycle_checks(),
        "real_pointer_preparations": balanced_source_calibration(),
        "all_intermediates_physically_recorded": all_registers_measured(),
        "cyclic_quantum_instrument": quantum_cycle_checks(),
        "all_seven_question_tables": table,
        "exact_phase_gate_fields": {
            order: {
                "degree": field(order).degree,
                "modulus_ascending": field(order).mod,
            }
            for order in (3, 6, 8, 24)
        },
    }
    binds = source_manifest()
    binds.update(table["source_digests"])
    all_checks["source_sha256"] = binds
    return all_checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    argspec = parser.add_mutually_exclusive_group(required=True)
    argspec.add_argument("--write", action="store_true")
    argspec.add_argument("--check", action="store_true")
    argspec.add_argument("--compare-private-lead", action="store_true")
    args = parser.parse_args()
    if args.compare_private_lead:
        actual = check_source_zero()
        bound = json.loads((HERE / "lead_reconciliation.json").read_text())
        assert json.loads(json.dumps(actual)) == bound
        print(
            "PASS all original source-zero outputs, setting labels, probabilities and asserted score ties"
        )
        return
    result = build()
    raw = (
        json.dumps(
            result, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        + b"\n"
    )
    out = io.BytesIO()
    with gzip.GzipFile(
        filename="", mode="wb", fileobj=out, compresslevel=9, mtime=0
    ) as compressed:
        compressed.write(raw)
    packed = out.getvalue()
    output = HERE / "observations.json.gz"
    if args.write:
        output.write_bytes(packed)
    else:
        assert output.read_bytes() == packed, (
            "Exact canonical receipt differs from the published observations"
        )
    print(
        f"PASS {len(raw)} exact JSON bytes, {len(packed)} compressed bytes, sha256={hashlib.sha256(packed).hexdigest()}"
    )


if __name__ == "__main__":
    main()
