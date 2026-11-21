"""Local controlled signed changes, both source ports, diagnostics and full repeat instruments."""

from fractions import Fraction as F
from itertools import product
from instrument_math import (
    BASE,
    BELL_PHASE,
    I,
    IDEAL,
    IDENTITY_CHANNEL,
    IX,
    J,
    M,
    MEASX,
    S,
    Root,
    add,
    apply_channel,
    born,
    coarse,
    compose,
    effective,
    effect,
    evaluate_dataset,
    group_sites,
    input_library,
    kraus_map,
    kron,
    label,
    process_records,
    tensor,
    zero,
)


DEPHASED = (BELL_PHASE[1] + BELL_PHASE[-1]).scale(F(1, 2))


def joint_controls(act_a=J, act_b=J.scale(-1)):
    def at_site(x):
        return Root(tensor(I, BASE[0]) + tensor(x, BASE[1]))

    c = group_sites(kron(at_site(act_a), at_site(act_b)))
    assert c.T @ c == Root(tensor(IX, IX))
    return c


def branches(c, an_a=MEASX, an_b=MEASX):
    return {
        (i, j): (Root(tensor(IX, a, b)) @ c)
        for i, a in enumerate(an_a)
        for j, b in enumerate(an_b)
    }


def parity(ij):
    return (-1) ** sum(ij)


def maps(ops, src):
    return {ij: effective(op, Root(src), 1).rational() for ij, op in ops.items()}


def tagged_joint(rho, cat):
    arm = [IX, M]
    rows = {}
    # The tags are actual orthogonal records for the two alternatives before recombination.
    # This stores every data block in the retained (tag=0,tag=1) register.
    for ij in product(range(2), repeat=2):
        s = parity(ij)
        block = {
            (i, j): (arm[i] @ rho @ arm[j].T).scale(F(s ** (i + j), 8))
            for i, j in product(range(2), repeat=2)
        }
        hidden = block[0, 0] + block[1, 1]
        returned = add(list(block.values()), 4)
        assert hidden == apply_channel(
            (IDENTITY_CHANNEL + kraus_map(M)).scale(F(1, 8)), rho
        )
        assert returned == apply_channel(IDEAL[s].scale(F(1, 2)), rho)
        rows[label(ij)] = {
            "blocks_given_local_X_outputs": {
                label(k): cat.put(v) for k, v in block.items()
            },
            "tag_traced": cat.put(hidden),
            "tag_uncomputed_before_recombining": cat.put(returned),
        }
    return rows


def refinement(cat):
    inputs = input_library()
    fine = {
        (t, v): kraus_map(inputs[f"{t}/{v}"]) for t, v in product((1, -1), ("u", "v"))
    }
    coarse_ch = coarse(fine, lambda k: k[0])
    for t, ch in coarse_ch.items():
        assert effect(ch) == S[t]
        assert compose(ch, ch) == ch and compose(ch, coarse_ch[-t]) == zero(16)
        assert apply_channel(ch, inputs[f"{t}/u"]) == inputs[f"{t}/u"]
        assert apply_channel(ch, inputs[f"{t}/u+v"]) == S[t].scale(F(1, 2))
    return {
        "fine_joint_refinement": process_records(fine, cat),
        "decoded": process_records(coarse_ch, cat),
        "joint_eigenbasis_prep_and_ordinary_continuations": evaluate_dataset(
            coarse_ch, cat
        ),
    }


def coherent_evidence(cat):
    ctrl = joint_controls()
    ops = branches(ctrl)
    out = {}
    for e in (1, -1, 0):
        src = BELL_PHASE[e] if e else DEPHASED
        ch = maps(ops, src)
        sub = coarse(ch, parity)
        for ij, v in ch.items():
            expected = (
                IDEAL[e * parity(ij)].scale(F(1, 2))
                if e
                else (IDENTITY_CHANNEL + kraus_map(M)).scale(F(1, 8))
            )
            assert v == expected
        assert add([effect(g) for g in ch.values()], 4) == IX
        rec = {
            "input_resource": cat.put(src),
            "fine": process_records(ch, cat),
            "decoded": process_records(sub, cat),
            "all_fine_inputs": evaluate_dataset(ch, cat),
            "all_decoded_inputs": evaluate_dataset(sub, cat),
            "returned_meter_projectors": {
                label(ij): cat.put(tensor(MEASX[ij[0]], MEASX[ij[1]])) for ij in ch
            },
            "whole_output_recipes": {
                label(ij): [op.put(cat), 1] for ij, op in ops.items()
            },
        }
        if e == 1:
            fresh = {}
            reuse = {}
            raw_bits = {}
            for first, next_port in product(ch, ch):
                f = label(first) + "/" + label(next_port)
                fresh[f] = cat.put(compose(ch[next_port], ch[first]))
                repeated = effective(
                    ops[next_port] @ ops[first], Root(src), 1
                ).rational()
                reuse[f] = cat.put(repeated)
                bare = tensor(BASE[first[0]], BASE[first[1]])
                unreturned = compose(maps(ops, bare)[next_port], ch[first])
                raw_bits[f] = cat.put(unreturned)
                assert repeated == compose(
                    maps(ops, tensor(MEASX[first[0]], MEASX[first[1]]))[next_port],
                    ch[first],
                )
                if parity(first) != parity(next_port):
                    assert compose(ch[next_port], ch[first]) == zero(16)
            eq_reuse = add(
                [
                    effect(
                        compose(maps(ops, tensor(MEASX[a[0]], MEASX[a[1]]))[b], ch[a])
                    )
                    for a, b in product(ch, ch)
                    if parity(a) == parity(b)
                ],
                4,
            )
            rec["two_reads"] = {
                "fresh_choi": fresh,
                "reuse_after_analyzer_return_choi": reuse,
                "reuse_literal_readout_basis_without_analyzer_return_choi": raw_bits,
                "same_sign_on_reuse_effect": cat.put(eq_reuse),
                "same_sign_on_reuse_by_basis": [
                    (str(born(input_library()[k], eq_reuse)))
                    for k in ("00", "01", "10", "11")
                ],
                "fresh_same_sign_effect": cat.put(IX),
                "fresh_meter_requirement": "Every successful second clean read consumes another independent prepared meter.",
            }
        out[str(e)] = rec
    controls = {}
    for a, b in [
        ("disconnected_A", "B"),
        ("A", "disconnected_B"),
        ("none", "none"),
        ("A", "reverse_B"),
    ]:
        local_a = I if a in ("disconnected_A", "none") else J
        local_b = (
            I
            if b in ("disconnected_B", "none")
            else (J if b == "reverse_B" else J.scale(-1))
        )
        o = branches(joint_controls(local_a, local_b))
        ch = maps(o, BELL_PHASE[1])
        controls[f"{a}/{b}"] = {
            "fine": process_records(ch, cat),
            "decoded": process_records(coarse(ch, parity), cat),
            "basis_outcomes": evaluate_dataset(coarse(ch, parity), cat),
            "residual_recipes": {label(ij): [op.put(cat), 1] for ij, op in o.items()},
        }
    for side in ("only_A", "only_B", "neither"):
        c = joint_controls(
            J if side == "only_A" else I, J.scale(-1) if side == "only_B" else I
        )
        o = branches(
            c, MEASX if side == "only_A" else (I,), MEASX if side == "only_B" else (I,)
        )
        ch = maps(o, BELL_PHASE[1])
        controls[side] = {
            "fine": process_records(ch, cat),
            "decoded_sign": None,
            "residual_recipes": {label(ij): [op.put(cat), 1] for ij, op in o.items()},
        }
    # A real read of either control word stores a physically distinguishable arm. Keep both refinements.
    for site in ("A", "B", "both"):
        fine = {}
        resolved_A = range(2) if site in ("A", "both") else ("*",)
        resolved_B = range(2) if site in ("B", "both") else ("*",)
        for i, j in product(resolved_A, resolved_B):
            selector = tensor(BASE[i] if i != "*" else I, BASE[j] if j != "*" else I)
            src = selector @ BELL_PHASE[1] @ selector
            for ij, op in ops.items():
                fine[(i, j, *ij)] = effective(op, Root(src), 1).rational()
        assert add([effect(v) for v in fine.values()], 4) == IX
        controls["fully_read_control_" + site] = process_records(fine, cat)
    # Copy/read the unknown target word before addressing the meter.
    zprojs = [tensor(x, y) for x, y in product(BASE, repeat=2)]
    fine = {
        (j, *ij): compose(v, kraus_map(p))
        for j, p in enumerate(zprojs)
        for ij, v in maps(ops, BELL_PHASE[1]).items()
    }
    controls["fully_read_target_word_before_offer"] = process_records(fine, cat)
    controls["actual_retained_tag_and_physical_uncompute"] = {
        name: tagged_joint(rho, cat) for name, rho in input_library().items()
    }
    out["faults_and_which_arm"] = controls
    out["joint_refinement"] = refinement(cat)
    return out
