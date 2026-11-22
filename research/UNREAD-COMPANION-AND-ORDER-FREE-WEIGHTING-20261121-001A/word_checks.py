"""Independent literal five-word, partial-trace and spectral checks for the unread companion."""

import argparse
import json
import os
import subprocess
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "word_checks.json"
TRIPLES = tuple("".join(t) for t in product("01", repeat=3))
PAIRS = tuple("".join(t) for t in product("01", repeat=2))
LAWS = {
    "even": tuple(t for t in TRIPLES if t.count("1") % 2 == 0),
    "not_all_equal": tuple(t for t in TRIPLES if len(set(t)) == 2),
}


def words_for(first, companion, shared):
    index = "acb".index(shared)
    return [x + tail for x, tail in product(TRIPLES, PAIRS)
            if x in LAWS[first] and x[index] + tail in LAWS[companion]]


def canonical_projection(first, companion, shared, target):
    visible = "acb" if target == "first" else "de" + shared
    hidden = [name for name in "acbde" if name not in visible]
    clauses = []
    for names, law in (("acb", first), (shared + "de", companion)):
        for forbidden in TRIPLES:
            if forbidden not in LAWS[law]:
                clauses.append(" ".join(v if b == "0" else "~" + v for v, b in zip(names, forbidden)))
    command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
               "--loops", *visible[:2], "--contact", visible[2], "--witnesses", *hidden, "--json"]
    raw = subprocess.check_output(command, cwd=ROOT, text=True, env=dict(os.environ, PYTHONPATH=str(ROOT / "tools")))
    report = json.loads(raw)
    assert report["is_knot"] and set(report["allowed"]) == set(LAWS[first if target == "first" else companion])
    return {"order": visible, "forgotten": hidden, "allowed": report["allowed"], "K1_K2_K3": report["is_knot"]}


def conditional_words_and_weights(words, shared):
    idx = "acb".index(shared)
    by_s = [[w for w in words if w[idx] == str(s)] for s in range(2)]
    wcounts = [len(block) for block in by_s]
    assert sum(wcounts) == len(words) and wcounts[0] == wcounts[1]
    forbidden = {x: sorted(w[3:] for w in words if w.startswith(x)) for x in TRIPLES}
    tails = [sorted({w[3:] for w in block}) for block in by_s]
    exclusive = [sorted(set(tails[s]) - set(tails[1 - s])) for s in range(2)]
    assert all(exclusive)
    gamma = Fraction(len(set(tails[0]) & set(tails[1])), len(tails[0]))
    # One contribution for every equal unread word at the matrix-product trace.
    numerator = [[len(set(forbidden[x]) & set(forbidden[y])) for y in TRIPLES] for x in TRIPLES]
    diagonal = [[numerator[i][j] if i == j else 0 for j in range(8)] for i in range(8)]
    assert sum(numerator[i][i] for i in range(8)) == len(words)
    # The real Gram coefficients reconstruct every matrix element, including zeros.
    for i, x in enumerate(TRIPLES):
        for j, y in enumerate(TRIPLES):
            expected = 0 if not forbidden[x] or not forbidden[y] else len(tails[0]) * (1 if x[idx] == y[idx] else gamma)
            assert numerator[i][j] == expected
    conditions = {}
    for s, block in enumerate(by_s):
        first_words = sorted({w[:3] for w in block})
        assert set(block) == {x + t for x, t in product(first_words, tails[s])}
        conditions[str(s)] = {"first_words": first_words, "unread_words": tails[s],
                              "exclusive_unread_words": exclusive[s], "basis_term_count": len(block),
                              "per_launch_sector_weight": "1/2"}
    unread_word_table = {pair: {"mathematical_weight": str(Fraction(sum(w[3:] == pair for w in words), len(words))),
                                "accessible_word_support": sorted(w[:3] for w in words if w[3:] == pair)}
                         for pair in PAIRS}
    return {"order": TRIPLES, "common_denominator": len(words), "unread_word_table_not_reported": unread_word_table,
            "coherent_reduced_numerator": numerator,
            "diagonal_reduced_numerator": diagonal, "shared_value_conditions": conditions,
            "normalized_unread_overlap": str(gamma),
            "nonzero_reduced_eigenvalues_on_accessible_names": [str((1 + gamma) / 2), str((1 - gamma) / 2)]}


def archived_clear(words):
    """Test the actual older equal-row route without an oracle that selects unread words."""
    output = {}
    for w in words:
        a, c, b, d, e = map(int, w)
        if a != c:
            output[w] = {"readable_row_herald": "unequal"}
            continue
        saved_a = a
        rows = [w]
        c ^= 1 - saved_a
        rows.append(f"{a}{c}{b}{d}{e}")
        a ^= saved_a
        rows.append(f"{a}{c}{b}{d}{e}")
        rows.append(f"{a}{c}0{d}{e}")
        output[w] = {"readable_row_herald": "equal", "candidate_named_words": rows,
                     "first_illegal_step": next((j for j, attempt in enumerate(rows) if attempt not in words), None)}
    return output


def matrix_product(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def transpose(a):
    return list(map(list, zip(*a)))


def determinant(a):
    return a[0][0] * a[1][1] - a[0][1] * a[1][0]


def sector_protocol(words, first, shared):
    if shared != "a" or first != "not_all_equal":
        return None
    traces = {}
    for word in words:
        a, c, b, d, e = map(int, word)
        fixed_c = 1 - a
        # Reader A exchanges c with its blank prepared opposite the value it actually read.
        # B then exchanges b with a blank 0. The unread names never change.
        stages = [word, f"{a}{fixed_c}{b}{d}{e}", f"{a}{fixed_c}0{d}{e}"]
        assert all(w in words for w in stages)
        assert all(x[0] == word[0] and x[3:] == word[3:] for x in stages)
        traces[word] = {"public_s": str(a), "physical_named_words": stages, "private_pair_before_filter": f"{c}{b}"}
    sectors = {}
    for a in "01":
        cmat = [[int(any(w.startswith(a + c + b) for w in words)) for b in "01"] for c in "01"]
        det = determinant(cmat)
        assert abs(det) == 1
        inv = [[cmat[1][1] // det, -cmat[0][1] // det], [-cmat[1][0] // det, cmat[0][0] // det]]
        assert matrix_product(inv, cmat) == [[1, 0], [0, 1]]
        gram = matrix_product(transpose(cmat), cmat)
        effect = matrix_product(transpose(inv), inv)
        assert gram[0][0] + gram[1][1] == 3 and determinant(gram) == 1
        assert effect[0][0] + effect[1][1] == 3 and determinant(effect) == 1
        diag_weight = sum(sum(row) * effect[i][i] for i, row in enumerate(cmat))
        assert diag_weight == 4
        sectors[a] = {"positive_conditional_amplitude_numerator": cmat, "normalization_squared": 3,
                      "B_gram_numerator": gram, "gram_characteristic_coefficients": [1, -3, 1],
                      "filter_numerator": inv, "filter_scale_squared": "(3-sqrt(5))/2",
                      "filter_times_input_numerators": matrix_product(inv, cmat),
                      "diagonal_admission_coefficient_before_scale_squared": str(Fraction(diag_weight, 3)),
                      "failure_rank": 1}
    return {"complete_named_inputs": traces, "sector_filter": sectors,
            "positive_admission": "(3-sqrt(5))/3", "diagonal_admission_for_same_filter": "2*(3-sqrt(5))/3"}


def exchanged_two_place_names():
    for f, g in product(LAWS, repeat=2):
        original = words_for(f, g, "a")
        renamed = words_for(f, g, "c")
        assert {w[1] + w[0] + w[2:] for w in original} == set(renamed)
    return True


def compute():
    cases = {}
    for shared in ("b", "a"):
        for first, companion in product(LAWS, repeat=2):
            words = words_for(first, companion, shared)
            reduced = conditional_words_and_weights(words, shared)
            old = archived_clear(words)
            assert any(row.get("first_illegal_step") is not None for row in old.values())
            cases[f"{shared}/{first}/{companion}"] = {
                "whole_words": words, "projection_first": canonical_projection(first, companion, shared, "first"),
                "projection_companion": canonical_projection(first, companion, shared, "companion"),
                "trace_unread": reduced, "archived_equal_row_route": old,
                "fixed_shared_reader_protocol": sector_protocol(words, first, shared),
            }
    return {"source_word_order": "acbde", "operator_on_unread_names": "identity",
            "both_two_place_reader_locations_agree_after_named_exchange": exchanged_two_place_names(), "cases": cases}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    raw = json.dumps(compute(), sort_keys=True, indent=2) + "\n"
    if args.write:
        OUTPUT.write_text(raw)
    else:
        assert OUTPUT.read_text() == raw
    print("Checked all eight placements and law pairs, both preparations and 16 physical ternary projections.")
