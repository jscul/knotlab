"""Exact single- and two-request denominators, failure records and process witnesses."""

from fractions import Fraction as F
from itertools import product
from instrument_math import (
    BELL_PHASE,
    DSEC,
    IDEAL,
    IDENTITY_CHANNEL,
    I,
    IX,
    J,
    M,
    S,
    Root,
    YRHO,
    add,
    apply_channel,
    born,
    compose,
    effect,
    input_library,
    label,
    rank,
    ray,
    tensor,
    zero,
)
from coherent_meter import branches, joint_controls, maps
from mixed_reference import data_channels, local_ports, paired_ports


def sources():
    out = {}
    primary = data_channels(paired_ports(local_ports(), local_ports()), Root(YRHO[1]))
    rejects = {
        k: v
        for k, v in [
            ("primer_00", F(1, 4)),
            ("primer_01", F(1, 4)),
            ("primer_10", F(1, 4)),
            ("group_1", F(1, 16)),
            ("group_2", F(1, 16)),
        ]
    }
    out["original_hidden_equal_reference"] = [
        ("denied_" + k, None, v, IDENTITY_CHANNEL) for k, v in rejects.items()
    ] + [("admitted", label(ij), F(1, 8), channel) for ij, channel in primary.items()]
    m = branches(joint_controls())
    for mode in (
        "plus_only",
        "both_corrected",
        "both_hidden",
        "delivered_herald_no_correction",
        "wrongly_corrected",
    ):
        rows = []
        for eta in (1, -1):
            if mode == "plus_only" and eta < 0:
                rows.append(("minus_denied", None, F(1, 2), IDENTITY_CHANNEL))
                continue
            wanted = (
                1
                if mode == "both_corrected"
                else -1
                if mode == "wrongly_corrected"
                else eta
            )
            ch = maps(m, BELL_PHASE[wanted])
            for ij, k in ch.items():
                rows.append(
                    (
                        "source_plus" if eta == 1 else "source_minus",
                        label(ij),
                        F(1, 2),
                        k,
                    )
                )
        out[mode] = rows
    return out


def all_launches(cat):
    test = input_library()
    result = {}
    for key, rows in sources().items():
        branches = {}
        for src, local, prior, ch in rows:
            name = src + ":" + str(local)
            branches[name] = ch.scale(prior)
        assert (
            len(branches) == len(rows)
            and add([effect(v) for v in branches.values()], 4) == IX
        )
        single = {}
        for src, local, prior, ch in rows:
            name = src + ":" + str(local)
            joint = branches[name]
            sign = None
            if local:
                if key == "original_hidden_equal_reference":
                    sign = 1 if (local[0] == "0") == (local[1] == "0") else -1
                else:
                    sign = (-1) ** (int(local[0]) + int(local[1]))
                    if (
                        key == "delivered_herald_no_correction"
                        and src == "source_minus"
                    ):
                        sign = -sign
            single[name] = {
                "bench_prior_before_target": str(prior),
                "decoded_sign_at_cut": sign,
                "local_source_label_readable": src
                if key == "delivered_herald_no_correction"
                else ("success" if local else "no_delivery"),
                "subnormalized_choi_per_request": cat.put(joint),
                "no_measurement_data_unchanged": local is None,
                "keeper_without_stage_faults": (
                    ["110", "110"]
                    if not local
                    else [
                        (
                            "011"
                            if (
                                j == "0"
                                if key == "original_hidden_equal_reference"
                                else j == "1"
                            )
                            else "101"
                        )
                        for j in local
                    ]
                ),
                "whole_request_p_by_registered_input": {
                    n: str(born(m, effect(joint))) for n, m in test.items()
                },
            }
        two = {}
        for old, new in product(branches, repeat=2):
            ch = compose(branches[new], branches[old])
            two[old + "/" + new] = {
                "whole_two_request_choi": cat.put(ch),
                "p_on_00": str(born(test["00"], effect(ch))),
            }
        assert sum(F(x["p_on_00"]) for x in two.values()) == 1
        result[key] = {
            "single": single,
            "fresh_twice": two,
            "complete_two_source_ledger": "The bench source and fine local addresses appear in each key. On the hidden binary bench, add the two corresponding port blocks before interpreting any returned local state; the label is never delivered. Divide by trace only for nonzero blocks.",
            "two_received_keeper_words": "Read the first and second key from single separately. A rejected first request returns the complete target unchanged for the second.",
        }
    return result


def instrument_grades(cat):
    inputs = input_library()
    localj = tensor(J, I)
    e = {}
    for t in (1, -1):
        p = S[t]
        assert p @ p == p and M @ p == p.scale(t) and p.tr() == 2
        assert compose(DSEC[t], DSEC[t]) == DSEC[t] and compose(
            DSEC[-t], DSEC[t]
        ) == zero(16)
        assert rank(IDEAL[t].key()) == 1 and rank(DSEC[t].key()) == 2
        for k, r in inputs.items():
            d = apply_channel(DSEC[t], r)
            assert d == p.scale(d.tr() / 2)
        # Independent real Choi test using target/spectator preparation local to each respective reader.
        phi = BELL_PHASE[1]
        rr = Root(tensor(phi, phi))
        from instrument_math import group_sites

        local_probe = group_sites(rr).rational()
        desired = tensor(IX, p) @ local_probe @ tensor(IX, p)
        actual = (desired + tensor(IX, localj) @ desired @ tensor(IX, localj).T).scale(
            F(1, 2)
        )
        assert desired == IDEAL[t].scale(F(1, 4)) and actual == DSEC[t].scale(F(1, 4))
        assert born(
            actual.scale(1 / actual.tr()), desired.scale(1 / desired.tr())
        ) == F(1, 2)
        # On the admitted pure conditional state real antisymmetry makes both returned pure components orthogonal.
        assert (
            localj.T == localj.scale(-1)
            and localj.T @ localj == IX
            and localj @ p == p @ localj
        )
        eig = inputs[f"{t}/u"]
        assert apply_channel(IDEAL[t], inputs["00"]) == eig.scale(F(1, 2))
        from real_algebra import partial_b

        negative = partial_b(eig, 2, 2)
        # Pick a definite negative-eigenvalue ordinary signed superposition on its partial transpose.
        vec = [0, 1, t, 0]
        witness = ray(vec)
        assert born(witness, negative) == F(-1, 2)
        e[str(t)] = {
            "sign_projector": cat.put(p),
            "ideal_choi": cat.put(IDEAL[t]),
            "actual_choi": cat.put(DSEC[t]),
            "independent_local_spectators_input": cat.put(local_probe),
            "ideal_probe_output": cat.put(desired),
            "literal_probe_output": cat.put(actual),
            "ideal_record_given_product_00": cat.put(eig),
            "partial_transpose": cat.put(negative),
            "negative_eigenvalue": "-1/2",
            "witness": cat.put(witness),
            "two_orthogonal_pure_components_for_every_real_conditional_output": [
                "phi",
                "(J tensor I) phi",
            ],
            "spectator_and_target_worst_squared_fidelity": "1/2",
        }
    return {
        "independent_process_spectator_and_product_obstruction": e,
        "proof_inputs_and_fixed_continuations": {
            k: cat.put(r) for k, r in inputs.items()
        },
        "rank_one_instrument_can_only_be_refined_into_constant_proportional_maps": True,
    }
