#!/usr/bin/env python3
"""Compile every kernel in this folder and confirm that its main theorems use only standard axioms.

Each kernel is a single file of core Lean 4 (no Mathlib). The toolchain is pinned in ./lean-toolchain;
with elan installed, `lean` picks it up when run from this folder.

    cd lean && python3 check.py
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
STANDARD = {"propext", "Classical.choice", "Quot.sound"}

KERNELS = {
    "ForgettingKernel": ("coexistence", "atom_isKnot", "parity_isKnot", "hub_not_knot", "tied_not_knot",
                         "absence_knot_is_knot", "parity_not_absence_knot", "no_clause_on_a_b",
                         "no_clause_on_a_k", "no_clause_on_b_k", "majority_with_free_pairs_is_full",
                         "no_two_cnf_defines_knot", "parity_chain_defines_parity"),
    "KnotKernel": ("atom_isKnot", "atomNeg_isKnot", "knot_unique", "knot_shadow_ab", "knot_shadow_ak",
                   "knot_shadow_bk", "knot_not_majority_closed", "no_two_cnf_defines_knot", "chain_defines_knot",
                   "tied_passes_old_conditions", "tied_role_swap", "tied_is_two_cnf", "tied_not_knot",
                   "cross_relational_not_knot", "cross_gated_eq_atom", "cross_gated_isKnot"),
    "CompetitionKernel": ("slice_vanishes", "opposite_in_slice", "no_knot_on_four_distinct", "no_knot_beyond_three",
                          "cube_cover", "knot_is_nae", "frustrated_least", "nae_is_knot",
                          "three_variable_classification", "strict_pairwise_no_knot",
                          "competition_pairwise_no_knot", "readings_agree_when_satisfiable", "gadget_bound",
                          "gadget_best", "gadget_projection", "every_relation_by_gadgets", "frustrated_triangle",
                          "triangles_knot_iff_frustrated", "weighted_triangle_not_knot"),
    "RingKernel": ("transfer_cases", "ring_excludes_iff", "ring_one_flip", "all_permutations_iff_parity",
                   "ring_memory", "parity3_every_length"),
    "LoopNerve": ("loop_rule", "bouquet_rule", "shape_is_nerve", "minimal_nonface_excludes_only_all",
                  "minimal_nonface_is_knot", "free_contact_binds_nothing", "knot_needs_more_values", "star_is_knot",
                  "star_injective", "three_loops_need_four_values", "four_values_knot_three_loops",
                  "boolean_contact_never_ties", "flip_involutive", "every_complex_is_a_nerve"),
}


def compile_source(source: str) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "Probe.lean"
        path.write_text(source)
        return subprocess.run(["lean", str(path)], cwd=HERE, capture_output=True, text=True, check=False)


def main() -> int:
    ok = True
    for name, theorems in KERNELS.items():
        source = (HERE / f"{name}.lean").read_text()
        probe = compile_source(source + "".join(f"\n#print axioms {name}.{t}" for t in theorems) + "\n")
        text = probe.stdout + probe.stderr
        used = {}
        for line in text.splitlines():
            match = re.search(r"'([^']+)' depends on axioms: \[(.*)\]", line)
            if match:
                used[match.group(1)] = {a.strip() for a in match.group(2).split(",") if a.strip()}
            elif re.search(r"'([^']+)' does not depend on any axioms", line):
                used[re.search(r"'([^']+)'", line).group(1)] = set()
        missing = [t for t in theorems if f"{name}.{t}" not in used]
        extra = sorted({a for axioms in used.values() for a in axioms} - STANDARD)
        good = probe.returncode == 0 and "sorry" not in text and not missing and not extra
        ok &= good
        print(f"{'ok  ' if good else 'FAIL'} {name}.lean: {len(theorems)} theorems, axioms used "
              f"{sorted({a for axioms in used.values() for a in axioms}) or 'none'}"
              + (f"; missing {missing}" if missing else "") + (f"; non-standard {extra}" if extra else ""))
        if probe.returncode != 0:
            print(text[-2000:])
    print("ALL OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
