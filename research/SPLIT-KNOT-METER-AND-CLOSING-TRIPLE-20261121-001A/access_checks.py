"""Literal source words, allowed local changes, and independent sign tests for B294."""

import argparse
import json
import os
import subprocess
import sys
from fractions import Fraction
from itertools import permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TARGET = HERE / "access_checks.json"
ALL = tuple("".join(w) for w in product("01", repeat=3))
EVEN = tuple(w for w in ALL if w.count("1") % 2 == 0)
NAE = tuple(w for w in ALL if len(set(w)) == 2)
A_WORDS = tuple("".join(w) for w in product("01", repeat=2))


def canonical(words):
    variables = "acb"
    clauses = [" ".join(v if bit == "0" else "~" + v for v, bit in zip(variables, w))
               for w in ALL if w not in words]
    cmd = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
           "--loops", "a", "c", "--contact", "b", "--json"]
    environment = dict(os.environ, PYTHONPATH=str(ROOT / "tools"))
    report = json.loads(subprocess.check_output(cmd, text=True, env=environment, cwd=ROOT))
    assert report["is_knot"] and tuple(report["allowed"]) == words
    return {"clauses": clauses, "result": report}


def local_completions(words):
    at_a = {x: sorted(w[2] for w in words if w[:2] == x) for x in A_WORDS}
    at_b = {b: sorted(w[:2] for w in words if w[2] == b) for b in "01"}
    def transitions(table):
        return [[x, y] for x, right in table.items() for y, left in table.items()
                if set(right) <= set(left)]
    # Exhaust all simultaneous product permutations and vary either reader independently.
    autos = []
    for pa, pb in product(permutations(A_WORDS), permutations("01")):
        outputs = [pa[A_WORDS.index(w[:2])] + pb[int(w[2])] for w in words]
        if set(outputs) == set(words):
            autos.append([list(pa), list(pb)])
    a_only = sum(row[1] == list("01") for row in autos)
    b_only = sum(row[0] == list(A_WORDS) for row in autos)
    return {"remote_words_for_A": at_a, "remote_words_for_B": at_b,
            "A_directed_pairs_including_identity": transitions(at_a),
            "B_directed_pairs_including_identity": transitions(at_b),
            "all_static_synchronized_product_permutations": autos,
            "counts_A_alone_B_alone_synchronized": [a_only, b_only, len(autos)]}


def pure_only_control(words, v):
    """A real reflection fixing the source vector, but sending basis mass to forbidden words."""
    norm = sum(k * k for k in v)
    u = [[(i == j) - Fraction(2 * v[i] * v[j], norm) for j in range(4)] for i in range(4)]
    for b in "01":
        old = [int(a + b in words) for a in A_WORDS]
        out = [sum(coef * amp for coef, amp in zip(row, old)) for row in u]
        assert old == out
    forbidden = {w: [x + w[2] for j, x in enumerate(A_WORDS)
                     if x + w[2] not in words and u[j][A_WORDS.index(w[:2])]]
                 for w in words}
    assert any(forbidden.values())
    return {"reflection_normal": v, "fixed_positive_source": True,
            "forbidden_named_outputs_for_basis_inputs": forbidden}


def local_read(words, permutation):
    # The source is invariant under this local self-inverse. On a diagonal
    # mixture its expectation is the share of fixed words.
    change = {w: permutation[w[:2]] + w[2] for w in words}
    assert all(change[v] == w for w, v in change.items())
    fixed = sum(w == v for w, v in change.items())
    return {"change": change, "plus_on_positive": "1", "plus_after_B_dephasing": "1",
            "plus_after_full_dephasing": str((1 + Fraction(fixed, len(words))) / 2)}


def source_paths(words):
    # Copy each control into a private bit before applying either clear.
    report = {}
    for w in words:
        a, c, b = map(int, w)
        p = a ^ c
        a_first = f"{a ^ p}{c}{b}"
        b_first = f"{a}{c}{b ^ b}"
        joined = f"{a ^ p}{c}{b ^ b}"
        report[w] = {"private_after_copies": f"{p}{b}", "after_A_first": a_first,
                     "A_first_lawful": a_first in words, "after_B_first": b_first,
                     "B_first_lawful": b_first in words, "joined": joined,
                     "joined_lawful": joined in words}
    return report


def joint_reversible_clear():
    audit = {}
    for ma, mb in product(range(2), repeat=2):
        routes = {}
        for w in EVEN:
            a, c, b = map(int, w)
            after = f"{a ^ ma}{c}{b ^ mb}"
            back = f"{int(after[0]) ^ ma}{after[1]}{int(after[2]) ^ mb}"
            assert back == w and (after in EVEN) == (ma == mb)
            routes[w] = {"after": after, "still_even": after in EVEN}
        audit[f"{ma}{mb}"] = routes
    return audit


def equal_row_protocol():
    paths = {}
    for w in NAE:
        a, c, b = map(int, w)
        if a != c:
            paths[w] = {"herald": "unequal", "word_after_refusal": w,
                        "target_coupled": False, "issued_data_ports": []}
            continue
        # Alice copies a to an initially zero meter. Conditional single-bit
        # gates keep its value while changing her actual source to 01.
        stages = [w, w, f"{a}{c ^ (1 - a)}{b}", f"{a ^ a}{c ^ (1 - a)}{b}"]
        stages.extend([stages[-1], stages[-1][:2] + "0"])
        meters = f"{a}{1 - b}"
        assert all(x in NAE for x in stages) and stages[-1] == "010" and meters[0] == meters[1]
        paths[w] = {"herald": "equal", "physical_source_history": stages,
                    "private_meter_after_B_complement": meters}
    return paths


def whole_nae_one_bit_transfer():
    """Old A and B words have first been copied to private registers."""
    rows = {}
    for w in NAE:
        a, c, b = map(int, w)
        stages = [w]
        # Store original a,c,b as controls. A first moves only the equal rows.
        u, v = a, c
        if (a, c) == (0, 0):
            v ^= 1
        stages.append(f"{u}{v}{b}")
        if (a, c) == (1, 1):
            u ^= 1
        stages.append(f"{u}{v}{b}")
        # Both possible current A rows are unequal. B can now clear.
        stages.append(f"{u}{v}0")
        if (a, c) == (1, 0):
            v ^= 1
        stages.append(f"{u}{v}0")
        if (a, c) == (1, 0):
            u ^= 1
        stages.append(f"{u}{v}0")
        assert stages[-1] == "010" and all(x in NAE for x in stages)
        assert all(sum(i != j for i, j in zip(x, y)) <= 1 for x, y in zip(stages, stages[1:]))
        rows[w] = {"physical_words": stages, "private_source": w}
    return rows


def mandatory_guess(m):
    # In a real Schmidt basis the source is (sqrt(5)|00>+|11>)/sqrt(6).
    # Separate its diagonal part from the coefficient of sqrt(5)/6.
    cross = [[int({i, j} == {0, 3}) for j in range(4)] for i in range(4)]
    def transpose_on_a(arr):
        return [[arr[2 * (j // 2) + i % 2][2 * (i // 2) + j % 2]
                 for j in range(4)] for i in range(4)]
    pt = transpose_on_a(cross)
    difference = [[cross[i][j] - pt[i][j] for j in range(4)] for i in range(4)]
    identity = [[int(i == j) for j in range(4)] for i in range(4)]
    j_pair = [[-val for val in row] for row in m]
    assert difference == j_pair
    assert [[sum(difference[i][k] * difference[k][j] for k in range(4))
             for j in range(4)] for i in range(4)] == identity
    assert transpose_on_a(m) == j_pair
    def pairing(a, b):
        return sum(a[i][j] * b[j][i] for i in range(4) for j in range(4))
    assert pairing(j_pair, cross) == 2
    for t in (-1, 1):
        target = [[Fraction(identity[i][j] + t * m[i][j], 4) for j in range(4)] for i in range(4)]
        assert pairing(j_pair, target) == -t
    return {"source_cross_coefficient": "sqrt(5)/6", "cross_minus_partial_transpose": difference,
            "absolute_eigenvalues_of_difference_in_coefficient_units": [1] * 4,
            "target_difference_trace_norm": 2, "local_measured_observable": "J_source tensor J_data",
            "guessed_sign": "minus product of reader outcomes",
            "optimal_equal_prior_correct_probability": "1/2+sqrt(5)/6"}


def dot(u, v):
    return sum(x * y for x, y in zip(u, v))


def signed_probe():
    # Independently construct M=−J⊗J from its action on ordinary basis words.
    states = list(product(range(2), repeat=2))
    m = [[0] * 4 for _ in states]
    for k, (x, y) in enumerate(states):
        dest = states.index((1 - x, 1 - y))
        m[dest][k] = -((-1) ** (x + y))
    p = {sign: [[Fraction(int(i == j) + sign * m[i][j], 2) for j in range(4)]
                for i in range(4)] for sign in (-1, 1)}
    effects = {}
    sym = [(1, 0), (0, 1), (1, 1)]
    for left, right in product(sym, repeat=2):
        w = [left[i] * right[j] for i, j in states]
        terms = {s: dot(w, [dot(row, w) for row in p[s]]) /
                 (2 * dot(left, left) * dot(right, right)) for s in (-1, 1)}
        assert terms[1] == terms[-1] == Fraction(1, 4)
        effects[f"{left}|{right}"] = str(terms[1])
    response = {str(s): [str(row[0]) for row in p[s]] for s in (-1, 1)}
    return {"M": m, "P_t_on_input_ket_00": response,
            "nine_separating_real_product_probes_on_either_Pt_over_two": effects}


def compute():
    work = {}
    for label, words, normal, swap in (
        ("parity", EVEN, [1, 1, -1, -1], dict(zip(A_WORDS, reversed(A_WORDS)))),
        ("not_all_equal", NAE, [1, -1, 0, 1], dict(zip(A_WORDS, ("00", "10", "01", "11")))),
    ):
        compatibility = local_completions(words)
        expected = [4, 1, 8] if label == "parity" else [2, 1, 4]
        assert compatibility["counts_A_alone_B_alone_synchronized"] == expected
        work[label] = {"canonical": canonical(words), "compatibility": compatibility,
                       "coherence_read": local_read(words, swap),
                       "actual_state_only": pure_only_control(words, normal),
                       "synchronous_offer": source_paths(words)}
    assert all(row["joined_lawful"] for row in work["parity"]["synchronous_offer"].values())
    assert sum(row["joined_lawful"] for row in work["not_all_equal"]["synchronous_offer"].values()) == 3
    c = [[int(a + b in NAE) for b in "01"] for a in A_WORDS]
    gram = [[sum(row[i] * row[j] for row in c) for j in range(2)] for i in range(2)]
    assert gram == [[3, 2], [2, 3]]
    work["not_all_equal"]["equal_herald_single_bit_paths"] = equal_row_protocol()
    work["not_all_equal"]["source_reduced_B"] = [[str(Fraction(k, len(NAE))) for k in row] for row in gram]
    work["parity"]["atomic_clear_with_independently_set_private_controls"] = joint_reversible_clear()
    work["not_all_equal"]["whole_source_one_bit_transfer"] = whole_nae_one_bit_transfer()
    work["sign_probes"] = signed_probe()
    work["not_all_equal"]["guess_every_launch"] = mandatory_guess(work["sign_probes"]["M"])
    return work


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the JSON evidence instead of verifying")
    args = parser.parse_args()
    data = json.dumps(compute(), indent=2, sort_keys=True) + "\n"
    if args.write:
        TARGET.write_text(data)
    else:
        assert TARGET.read_text() == data, "access evidence differs from the replay"
    print("Both source laws, every declared local permutation and all nine real product probes checked.")
