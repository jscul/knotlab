"""Rebuild the complete B295 instrument, resource certificates and two receiving banks."""

from argparse import ArgumentParser
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import gzip
import io
import json
from triple_instrument import (
    BASE,
    BITS,
    HERE,
    ROOT,
    Catalogue,
    algebra,
    born,
    destructive,
    direct_third,
    effect,
    make_inputs,
    repeat,
    signs,
    tensor,
    two_pairs,
)
from resource_checks import (
    forward_circuit,
    missing_direct_and_privacy,
    select_sources,
    spectral_ledger,
    spent_and_direct,
    whole_requests,
)

OLD = "TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001"
ONE = "TWO-READERS-ONE-SURVIVING-SIGN-20261121-001"
ERASE = "ERASURE-AND-CLOSING-SIGNS-20261121-001A"


def bindings():
    selected = list(HERE.glob("*.py")) + [
        HERE / "preregistration.md",
        HERE / "design_reviews.md",
    ]
    for sub, files in {
        OLD: ["founders.py", "independent_checks.md"],
        OLD + "A": ["six_knots.md"],
        OLD + "B": [
            "real_algebra.py",
            "sources_and_reads.py",
            "reference_controls.py",
            "pointer_hardware.py",
        ],
        ONE: ["decision.md", "independent_checks.md"],
        ONE + "A": [
            "instrument_math.py",
            "instrument_hardware.py",
            "coherent_meter.py",
            "observations.json.gz",
        ],
        ERASE: ["ordinary_routes.py", "keeper.py"],
    }.items():
        selected.extend(ROOT / "research" / sub / f for f in files)
    for t, slug in [
        (OLD + "B", "pointers"),
        (OLD + "Z", "synthesis"),
        (ONE + "A", "instrument"),
        (ONE + "Z", "synthesis"),
        (ERASE, "keeper"),
    ]:
        base = ROOT / "proofs" / t / (t + "-P001_" + slug)
        selected.extend([base / "manifest.json", base / "proof.md"])
    a = OLD + "A"
    fam = a + "-E001_meetings"
    selected.extend(
        [
            ROOT / "artifacts" / a / fam / "matched_and_signed.json.gz",
            ROOT / "experiments" / a / fam / "contract.json",
        ]
    )
    return {
        str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
        for p in sorted(selected)
    }


def maths(cat):
    roster = algebra(cat)
    primary, controls, fine = two_pairs(cat)
    one, low, co = destructive(cat)
    return {
        "actual_growth_and_signed_name": roster,
        "coherent_two_pairs": primary,
        "local_orders_frames_tags_and_disconnected_offers": controls,
        "one_pair_effects_and_returned_words": one,
        "direct_30_and_disagreement_controls": direct_third(cat, fine),
        "repeated_joint_channels": repeat(cat, fine, low),
        "independent_full_gate_circuit": forward_circuit(cat),
        "resource_source_labels": select_sources(cat),
        "whole_request_weights_and_partial_states": whole_requests(cat),
        "untouched_spectators_and_cost": spectral_ledger(cat, co),
        "spent_meters_and_joint_audit": spent_and_direct(cat, fine),
        "coverage_and_partial_direct_queries": missing_direct_and_privacy(cat),
        "ordinary_coherent_and_mixed_input_library": {
            name: cat.put(state) for name, state in make_inputs().items()
        },
    }, fine


def joined(cat, hw, channels):
    intact = hw["intact_fine_records"]
    rows = {}
    for orient in product(BITS, repeat=2):
        for f, ch in channels.items():
            signature = "".join(map(str, orient)) + "/" + "".join(map(str, f))
            row = intact[signature]
            outcomes = {
                site: tuple(row["bank_status"][site]["reported_signs"])
                for site in ("A", "B")
            }
            assert set(outcomes.values()) == {signs(f)}
            assert row["physical_classical_messages_sent"] == 4
            rows[signature] = {
                "whole_hardware_trace_key": signature,
                "ordinary_signs_delivered": outcomes,
                "simultaneous_two_ternary_words": row[
                    "simultaneous_actual_keeper_words_A_B"
                ],
                "data_map_given_both_corrected_sources": cat.put(ch),
                "subnormalized_map_per_two_plus_only_source_requests": cat.put(
                    ch.scale(F(1, 4))
                ),
                "probability_on_mixed_input": str(effect(ch).tr() / 4),
                "probability_on_primary_ordinary_00": str(
                    born(tensor(BASE[0], BASE[0]), effect(ch))
                ),
            }
    return rows


def render():
    from closing_hardware import hardware_checks

    cat = Catalogue()
    res, fine = maths(cat)
    hw = hardware_checks()
    res["actual_two_receiving_banks"] = hw
    res["every_fine_physical_join"] = joined(cat, hw, fine)
    res["matrix_catalogue"] = cat.matrices
    res["source_sha256"] = bindings()
    res["readout_guide"] = {
        "rank_one_data_projectors": "Label order x,z,y refers to physical names 28,29,30. Sixteen fine bit keys are A28,B28,A29,B29. The data basis is 00,01,10,11.",
        "canonical_matrices": "Each integer matrix ID indexes matrix_catalogue. Its common positive denominator applies entrywise. An unnormalized Choi block (i,j) is the full subnormalized output from |i><j|. Dividing by four is the output of the complete normalized local spectator probe. Every matrix acts as identity on any inaccessible additional spectator.",
        "full_output_reconstruction": "Multiply each target map as indicated, keep or normalize only nonzero outcomes. Intact fine record fixes all the spent local meter addresses, stored archive cells and the ordinary receipt histories. Partial completion preserves exactly the already addressed projectors with the listed source histories. For held quantum tags use the supplied off-diagonal Gram recipe before discarding the tag.",
        "resource_class": "Separated local real operations and classical messages; complex extensions are permitted only to strengthen the upper bounds. Every delivered flag and residual shared system counts in the Schmidt-number budget.",
    }
    return res


def packed(obj):
    raw = (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()
    out = io.BytesIO()
    with gzip.GzipFile(
        fileobj=out, filename="", mode="wb", mtime=0, compresslevel=9
    ) as g:
        g.write(raw)
    return out.getvalue()


def main():
    a = ArgumentParser(description=__doc__)
    g = a.add_mutually_exclusive_group(required=True)
    for item in ("write", "check", "math-only"):
        g.add_argument("--" + item, action="store_true")
    opt = a.parse_args()
    if opt.math_only:
        c = Catalogue()
        rows, _ = maths(c)
        print(
            f"{len(c.matrices)} exact matrices and {len(rows)} mathematics ledgers verified"
        )
        return
    obj = render()
    data = packed(obj)
    output = HERE / "observations.json.gz"
    if opt.write:
        output.write_bytes(data)
    elif output.read_bytes() != data:
        raise ValueError("Canonical replay differs from the stored evidence")
    print(
        f"{len(obj['matrix_catalogue'])} matrices; {len(obj['every_fine_physical_join'])} primary banks/ports; {len(data)} bytes; SHA-256 {sha256(data).hexdigest()}"
    )


if __name__ == "__main__":
    main()
