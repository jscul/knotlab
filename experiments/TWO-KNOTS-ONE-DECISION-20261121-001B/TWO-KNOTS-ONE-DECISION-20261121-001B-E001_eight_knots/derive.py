"""Derive the eight-holding launch laws without shared implementation or reference tables."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path


FREEZE = "83095b5467e30fb395e0005986fbb07fea14e3e8ad67a2e45fb94f7c7d3a41a2"
LEFT = (0, 3, 5, 6)
RIGHT = (1, 2, 4, 7)
MARK_OWNERS = tuple((h, h ^ (1 << b)) for h in range(8) for b in range(3) if not h & (1 << b))
HOLDINGS = tuple(tuple(e for e, owners in enumerate(MARK_OWNERS) if h in owners) for h in range(8))
CHARGES = (0, 0, 0, 0, 0, 0, 0, 1)
N = len(MARK_OWNERS)
FAILURE = 8


def local_word(w, marks):
    return sum((w >> e & 1) << i for i, e in enumerate(marks))


def binary_words(charges):
    return tuple(w for w in range(1 << N) if all(local_word(w, h).bit_count() % 2 == b
                                                  for h, b in zip(HOLDINGS, charges)))


def physical_equations():
    """Represent each polynomial as a set of its present terms over F_2."""
    for e in range(N):
        yield ("undo", e), {("d", e, e)}, 0
        for h, holding in enumerate(HOLDINGS):
            yield ("preserve", e, h), {("d", e, f) for f in holding}, 0
    for h, holding in enumerate(HOLDINGS):
        for e, f in combinations(holding, 2):
            yield ("commute", h, e, f), {("d", e, f), ("d", f, e)}, 0
        for f in range(N):
            yield ("return", h, f), {("d", e, f) for e in holding}, 0
        sign_terms = {("s", e) for e in holding}
        phase_terms = {("d", e, f) for e, f in combinations(sorted(holding), 2)}
        yield ("ordered_sign", h), sign_terms ^ phase_terms, CHARGES[h]


def strict_obstruction():
    """Eliminate the changes needed to cancel the sum of all eight sign rows."""
    rows = list(physical_equations())
    target = set()
    rhs = 0
    witness = set()
    for i, (name, terms, value) in enumerate(rows):
        if name[0] == "ordered_sign":
            target ^= terms
            rhs ^= value
            witness.add(i)
    basis = {}
    for i, (name, terms, value) in enumerate(rows):
        if name[0] == "ordered_sign":
            continue
        row, provenance = set(terms), {i}
        while row:
            p = min(row)
            if p not in basis:
                basis[p] = row, provenance
                break
            other_row, other_provenance = basis[p]
            row ^= other_row
            provenance ^= other_provenance
        assert value == 0
    while target:
        p = min(target)
        row, provenance = basis[p]
        target ^= row
        witness ^= provenance
    certified_terms = set()
    certified_rhs = 0
    for k in witness:
        _, terms, rhs_of_k = rows[k]
        certified_terms ^= terms
        certified_rhs ^= rhs_of_k
    assert not certified_terms and certified_rhs == rhs == 1
    return [{"origin": rows[k][0], "terms": sorted(rows[k][1]), "rhs": rows[k][2]} for k in sorted(witness)]


def recalibrate(mark, carrier):
    second = MARK_OWNERS[mark][1]
    corrected = tuple(b ^ (h == second) for h, b in enumerate(CHARGES))
    solutions = binary_words(corrected)
    assert len(solutions) == len(carrier) and set(solutions) == {w ^ solutions[0] for w in carrier}
    # Zero flips are feasible. Choose the lexicographically first sign string in increasing mark order.
    signs = min(solutions, key=lambda s: tuple(s >> e & 1 for e in range(N)))
    return {"mark": mark, "reversed_occurrence": [second, mark],
            "disagreement_setting": [next(h for h in MARK_OWNERS[mark] if h in LEFT),
                                     next(h for h in MARK_OWNERS[mark] if h in RIGHT)],
            "corrected_local_charge": corrected, "signs": signs,
            "raw_hidden_words": sorted(signs ^ w for w in carrier)}


def table(accepted_words, launch_words, signs=0, occurrence=None, allowed=None):
    """Pair both readers' restrictions of one diagonal source, or place all mass on refusal."""
    def answer(h, word):
        raw = local_word(word ^ signs, HOLDINGS[h])
        return raw ^ (1 << HOLDINGS[h].index(occurrence[1])) if occurrence and h == occurrence[0] else raw

    rows = []
    for l, r in product(LEFT, RIGHT):
        shared = sorted(set(HOLDINGS[l]) & set(HOLDINGS[r]))
        trials = Counter((answer(l, w), answer(r, w)) for w in accepted_words)
        if allowed:
            assert all(lw in allowed[l] and rw in allowed[r] for lw, rw in trials)
        agree = (sum(count for (lw, rw), count in trials.items()
                     if (lw >> HOLDINGS[l].index(shared[0]) & 1) == (rw >> HOLDINGS[r].index(shared[0]) & 1))
                 if shared else sum(trials.values()))
        missing = launch_words - len(accepted_words)
        cells = [[lw, rw, n] for (lw, rw), n in sorted(trials.items())]
        if missing:
            cells.append([FAILURE, FAILURE, missing])
        rows.append({"settings": [l, r], "shared_marks": shared, "nonzero_cells": cells,
                     "zero_cells_over_failure_augmented_alphabet": 81 - len(cells),
                     "accepted_denominator": len(accepted_words) or None,
                     "launch_denominator": launch_words, "recorded_wins": agree,
                     "raw_agreements_or_disjoint": len(accepted_words)})
    return {"launch_settings_weight": "1/16", "joint_launch_denominator": launch_words * 16,
            "ordinary_cell_count": 1024, "cell_count_with_failure": 1296,
            "accepted_source_attempts_per_setting": len(accepted_words), "launch_attempts_per_setting": launch_words,
            "recorded_wins_all_settings": sum(row["recorded_wins"] for row in rows), "settings": rows}


def predictions():
    carrier = binary_words((0,) * len(HOLDINGS))
    assert N == 12 and len(carrier) == 32
    strict = strict_obstruction()
    assert not binary_words(CHARGES)
    minimum = [recalibrate(e, carrier) for e in range(N)]
    first = minimum[0]
    signed_words = tuple(tuple(w for w in range(8) if w.bit_count() % 2 == b) for b in CHARGES)
    nae_words = tuple(w for w in range(1 << N) if all(0 < local_word(w, h) < 7 for h in HOLDINGS))
    strict_table = table((), 1)
    calibrated = table(carrier, len(carrier), first["signs"], first["reversed_occurrence"], signed_words)
    disagreements = [row["settings"] for row in calibrated["settings"]
                     if row["recorded_wins"] != row["accepted_denominator"]]
    assert disagreements == [first["disagreement_setting"]]
    return {
        "design_sha256": FREEZE, "holdings": HOLDINGS, "mark_owners": MARK_OWNERS,
        "charge_by_holder": CHARGES, "left": LEFT, "right": RIGHT, "ordinary_unsigned_carrier": carrier,
        "output_code": "Bits in integer words are placed from low to high in the holder's listed order; 8 is failure.",
        "strict": {"refusal": "0 = 1 in universal signed-change equations", "xor_certificate": strict,
                   "table": strict_table},
        "calibration": {"minimum_count": 1, "all_minimum_options": minimum, "chosen": first,
                        "ordinary_masks": [0] * N, "table": calibrated,
                        "explicit_quantum_preparation": (
                            "Use both copies of the 32-dimensional word space in the normalized state "
                            "sum_w |w,w>/sqrt(32). The raw operators are diagonal with eigenvalues "
                            "(-1)^(w_e+s_e). Flip the displayed auxiliary only at the listed occurrence. "
                            "Equivalently draw one of the listed raw hidden words uniformly before both questions."
                        )},
        "all_even": {"table": table(carrier, len(carrier))},
        "not_all_equal": {"accepted_physical_words": nae_words, "table": table(nae_words, 1 << N)},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = (json.dumps(predictions(), sort_keys=True, indent=2) + "\n").encode()
    with args.output.open("xb") as stream:
        stream.write(payload)
    print(sha256(payload).hexdigest(), args.output)


if __name__ == "__main__":
    main()
