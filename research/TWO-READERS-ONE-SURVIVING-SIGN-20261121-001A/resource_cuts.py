"""Subnormalized source histories, their lawful interventions, and delivered-state comparisons."""

from fractions import Fraction as F
from itertools import product
from instrument_math import (
    BELL_PHASE,
    I,
    IX,
    J,
    YRHO,
    IDEAL,
    Root,
    Mat,
    identity,
    kron,
    label,
    tensor,
)
from mixed_reference import TURNS, TURN
from coherent_meter import DEPHASED, branches, joint_controls, parity
from real_algebra import C, T, group, instrument, real_charge, ideal_complex_charge
from sources_and_reads import local_raw_source


def combine(items):
    items = list(items)
    total = items[0].scale(0)
    for m in items:
        total = total + m
    return total


def rotate(g, rho):
    return g @ rho @ g.T


def word_diagonal(m):
    return list(zip(m.a.diag(), m.b.diag()))


def packet(m, cat):
    return {
        "Q_sqrt3_coefficients": m.put(cat),
        "weight_Q_sqrt3": list(map(str, m.tr())),
        "all_joint_word_probabilities_Q_sqrt3": word_diagonal(m),
    }


def logical_encodings():
    # Wnum/sqrt(2) has columns r and s. All two-register physical density matrices are over Q(sqrt(3)).
    wnum = Root(Mat([[1, 0], [-1, 0], [0, 0]]), Mat([[0, 1], [0, 1], [0, -2]], 3))
    w2 = kron(wnum, wnum).scale(F(1, 2))
    assert w2.T @ w2 == Root(IX)
    assert (wnum.T @ Root(C) @ wnum).scale(F(1, 2)) == TURN
    assert (wnum.T @ Root(T) @ wnum).scale(F(1, 2)) == Root(Mat([[-1, 0], [0, 1]]))
    from sympy import Matrix, eye, sqrt, simplify, diag

    c = Matrix(C.a.tolist())
    u = Matrix.hstack(
        Matrix([1, 1, 1]) / sqrt(3),
        Matrix([1, -1, 0]) / sqrt(2),
        Matrix([1, 1, -2]) / sqrt(6),
    )
    lifted = diag(u, 1) @ diag(c, 1)
    assert simplify(lifted.T @ lifted) == eye(4)
    assert lifted[:3, :2] == u[:, 1:3]
    assert (lifted.T @ lifted)[3, 3] == 1
    return w2


def cuts(cat):
    w2 = logical_encodings()
    src = Root(BELL_PHASE[1])
    refl = Root(Mat([[-1, 0], [0, 1]]))
    old = {}
    raw = None
    for hk in product(range(2), repeat=2):
        pre = tensor(local_raw_source(hk[0]), local_raw_source(hk[1]))
        if hk != (1, 1):
            old["source_" + label(hk)] = pre
        else:
            for k, rho in enumerate(instrument(pre, group(tensor(C, C)))):
                if k:
                    old["group_" + str(k)] = rho
                else:
                    raw = rho
    assert raw.tr() == F(1, 8)
    assert sum(x.tr() for x in old.values()) + raw.tr() == 1
    assert rotate(w2, src).rational() == raw.scale(8)
    physical_trit = {}
    for j in range(3):
        physical_trit[j] = rotate(kron(TURNS[j], refl), src)
        expected = rotate(Root(tensor([identity(3), C, C.T][j], T)), Root(raw.scale(8)))
        assert rotate(w2, physical_trit[j]) == expected
    original = combine(physical_trit.values()).scale(F(1, 3))
    assert original.rational() == YRHO[1]
    for t in (1, -1):
        assert rotate(w2, Root(YRHO[t])).rational() == real_charge(1, t)
    ops = branches(joint_controls())
    from instrument_math import effective

    def run(ref):
        return {a: effective(o, ref, 1) for a, o in ops.items()}

    def source_grade(sub):
        # Corrections may leave real sqrt(3) coherences; do not discard those when a label is disclosed.
        out = run(sub)
        return {label(k): v.put(cat) for k, v in out.items()}

    shares = {}
    independent = {}
    for u, v in product(range(3), repeat=2):
        j = (u + v) % 3
        tagged = physical_trit[j]
        corrected = rotate(kron(TURNS[-u % 3], TURNS[v] @ refl), tagged)
        disclosed = rotate(kron(TURNS[-j % 3], refl), tagged)
        assert corrected == disclosed == src
        local_bad = rotate(kron(TURNS[-u % 3], TURNS[v] @ refl), original)
        for ij, ch in run(corrected).items():
            assert ch.rational() == IDEAL[parity(ij)].scale(F(1, 2))
        shares[label((u, v))] = {
            "j": j,
            "physical_9_words_on_source_admission": packet(
                rotate(w2, tagged).scale(F(1, 9)), cat
            ),
            "logical_given_labels": packet(tagged, cat),
            "per_original_source_request": "1/72",
            "before_any_repair_fine_choi": source_grade(tagged),
            "communicated_and_repaired": packet(disclosed, cat),
            "physically_repaired_without_message": packet(corrected, cat),
            "corrected_four_port_choi": source_grade(corrected),
        }
        independent[label((u, v))] = {
            "logical_subnormalized_given_success": packet(original.scale(F(1, 9)), cat),
            "physical_9word_joint_block": packet(
                rotate(w2, original).scale(F(1, 9)), cat
            ),
            "input_to_target_if_dummy_shares_used_as_actual_keys": packet(
                local_bad, cat
            ),
            "fake_repair_fine_choi": source_grade(local_bad),
            "per_original_source_request": "1/72",
        }
    marginals = {}
    for site, value in product((0, 1), range(3)):
        avg = combine([physical_trit[(value + x) % 3] for x in range(3)]).scale(F(1, 3))
        assert avg == original
        marginals[f"{site}/{value}"] = {
            "pointer_pair_subnormalized_given_success": packet(avg.scale(F(1, 3)), cat),
            "single_share_readable_without_message": value,
            "twirl_uncertain": True,
        }
    whole = {}
    for j, pre in physical_trit.items():
        for name, g in [
            ("no_undo", kron(TURNS[0], TURNS[0])),
            ("correct", kron(TURNS[-j % 3], refl)),
            ("wrong_trit", kron(TURNS[(-j - 1) % 3], refl)),
            ("omit_B_transposition", kron(TURNS[-j % 3], TURNS[0])),
        ]:
            m = rotate(g, pre)
            if name == "correct":
                assert m == src
            whole[f"{j}/{name}"] = {
                "physical_reference_if_in_cycle_code": packet(rotate(w2, m), cat),
                "data_fine": source_grade(m),
                "weight_given_admission": "1/3",
                "whole_launch_weight": "1/24",
            }
    independent_coins = {str(c): packet(original.scale(F(1, 2)), cat) for c in (0, 1)}
    # Entire joint pure pointer |psi_j> or same reduced state with an orthogonal inaccessible preparation record.
    # A genuinely coherent purification is shown blockwise. A classical disclosed trit has only diagonal blocks.
    # Undo C^j coherently, then the trit is a product of the known equal amplitudes; erase/remove by running its preparation backwards.
    flags = {}
    bare = [kron(TURNS[j], refl) for j in range(3)]
    for j, k in product(range(3), repeat=2):
        full = (bare[j] @ src @ bare[k].T).scale(F(1, 3))
        undo_j = kron(TURNS[-j % 3], refl)
        undo_k = kron(TURNS[-k % 3], refl)
        returned = undo_j @ full @ undo_k.T
        assert returned == src.scale(F(1, 3))
        flags[label((j, k))] = {
            "coherent_trit_blocks_before_return": full.put(cat),
            "after_controlled_return": returned.put(cat),
            "classical_or_irreversibly_resolved_trit": (
                full if j == k else full.scale(0)
            ).put(cat),
        }
    labels = {}
    for eps in (1, -1):
        # Q_s=(I+i*s*J)/2 (Y=i*J). This is an ideal complex orientation flag, outside the real-source port list.
        labels[str(eps)] = {
            "conditional_logical_real_part": cat.put(YRHO[1]),
            "conditional_logical_imaginary_part": cat.put(
                (tensor(J, I) + tensor(I, J)).scale(F(eps, 4))
            ),
            "physical_3x3_basis_charge_density": ideal_complex_charge(-eps, -eps),
            "conditional_weight": "1/2",
            "product_of_single_site_projections": True,
        }
    return {
        "old_source": {
            "ordinary_seed": "aa; individual primer and a three-way comparison on both successful minus primers",
            "rejected_local_receivers": "both blank, no cut label, independent target unchanged",
            "physical_bench_rejections": {
                k: {"p": str(x.tr()), "physical_9word_full": cat.put(x)}
                for k, x in old.items()
            },
            "admitted_preturn": packet(Root(raw), cat),
            "admission": "1/8",
            "actual_T_at_B": cat.put(T),
        },
        "cycle_logical_two_register_isometry_W_tensor_W": w2.put(cat),
        "physical_hidden_equal_reference": packet(rotate(w2, original), cat),
        "logical_hidden_equal_reference": packet(original, cat),
        "turns_and_corrections": whole,
        "disjoint_shares": shares,
        "one_share_marginal": marginals,
        "independent_dummy_shares": independent,
        "absent_shares": {
            "input": packet(original, cat),
            "delivered_target_fine": source_grade(original),
        },
        "source_independent_shared_coin": independent_coins,
        "formal_complex_charge_labels": labels,
        "purification_vs_classical_labels": flags,
        "preturn_meter": source_grade(src),
        "cut_can_keep_hidden_trit_and_run_mixed_reference_instrument_without_access": True,
    }


def binary_source(cat):
    # Unnormalized density of each real aa/bb source branch in code and all nine old ordinary word frequencies.
    iz = Root(tensor(I, Mat([[1, 0], [0, -1]])))
    result = {}
    for e in (1, -1):
        rho = Root(BELL_PHASE[e])
        repaired = rotate(iz if e < 0 else Root(IX), rho)
        false = rotate(iz if e > 0 else Root(IX), rho)
        assert (
            repaired.rational() == BELL_PHASE[1] and false.rational() == BELL_PHASE[-1]
        )
        result[str(e)] = {
            "full_request_probability": "1/2",
            "original_9_word_frequencies_given_this_source_port": [
                "1/2",
                "0",
                "0",
                "0",
                "1/2",
                "0",
                "0",
                "0",
                "0",
            ],
            "complete_source_state": packet(rho, cat),
            "correct_Z_or_identity": packet(repaired, cat),
            "wrong_Z_or_identity": packet(false, cat),
            "ordinary_bench_source_latch": "plus" if e == 1 else "minus",
        }
    assert BELL_PHASE[1].diag() == BELL_PHASE[-1].diag() == DEPHASED.diag()
    result["hidden_mixture"] = packet(Root(DEPHASED), cat)
    return result
