"""Original distributed reference, its complete three-port read, and the binary oracle control."""

from fractions import Fraction as F
from itertools import product
from instrument_math import (
    I,
    IX,
    J,
    YRHO,
    DSEC,
    Root,
    add,
    apply_channel,
    coarse,
    compose,
    effective,
    effect,
    evaluate_dataset,
    group_sites,
    identity,
    input_library,
    kron,
    label,
    process_records,
    residual,
    tensor,
    trace_reference,
    zero,
)

TURN = Root(I.scale(F(-1, 2)), J.scale(F(1, 2)))
UNIT = Root(IX)
TURNS = (Root(I), TURN, TURN.T)


def local_ports(binary=False, data_frame=1, ref_frame=1):
    g = kron(TURNS[data_frame % 3], TURNS[ref_frame % 3])
    g2 = g @ g
    assert g2 @ g == UNIT
    if binary:
        marked = (UNIT + g + g2).scale(F(1, 3))
        return [(marked, 1), (UNIT - marked, 1)]
    return [(UNIT + g + g2, 9), (UNIT - g, 6), (UNIT + g - g2.scale(2), 18)]


def paired_ports(left, right):
    return {
        (i, j): (group_sites(kron(a, b)), n * m)
        for i, (a, n) in enumerate(left)
        for j, (b, m) in enumerate(right)
    }


def parity_flag(ports):
    return 1 if (ports[0] == 0) == (ports[1] == 0) else -1


def data_channels(ports, ref):
    return {ij: effective(op, ref, d).rational() for ij, (op, d) in ports.items()}


def primary_evidence(cat):
    out = {}
    for binary in (False, True):
        local = local_ports(binary)
        joint = paired_ports(local, local)
        family = "clean_binary_oracle" if binary else "actual_three_path_ports"
        rows = {}
        for relation in (-1, 0, 1):
            ref = Root(YRHO[relation])
            channels = data_channels(joint, ref)
            summed = coarse(channels, parity_flag)
            assert add([effect(m) for m in channels.values()], 4) == IX
            for ij, ch in channels.items():
                m = 1 if binary else (1 if ij[0] == 0 else 2) * (1 if ij[1] == 0 else 2)
                t = parity_flag(ij)
                expected = (
                    DSEC[t * relation].scale(F(1, 2 * m))
                    if relation
                    else (DSEC[t] + DSEC[-t]).scale(F(1, 4 * m))
                )
                assert ch == expected
            port_states = {}
            for ij, (op, den) in joint.items():
                full = residual(op, input_library()["00"], ref, den)
                reduced = Root(
                    trace_reference(full.a), trace_reference(full.b)
                ).rational()
                assert reduced == apply_channel(channels[ij], input_library()["00"])
                port_states[label(ij)] = {
                    "joint_data_reference_on_ordinary_00": full.put(cat),
                    "op_num_Q_sqrt3": op.put(cat),
                    "squared_denominator": den,
                    "physical_local_returned_path_addresses_0a_1b_2c": list(ij),
                    "keeper_flag_port_zero": [i == 0 for i in ij],
                }
            records = {
                "reference": ref.put(cat),
                "fine_channels": process_records(channels, cat),
                "decoded": process_records(summed, cat),
                "fine_all_inputs": evaluate_dataset(channels, cat),
                "decoded_all_inputs": evaluate_dataset(summed, cat),
                "residual_recipes": port_states,
            }
            if relation == 1:
                fresh = {}
                reuse = {}
                for ij, (op, den) in joint.items():
                    for kl, (next_op, next_den) in joint.items():
                        key = label(ij) + "/" + label(kl)
                        a = compose(channels[kl], channels[ij])
                        b = effective(next_op @ op, ref, den * next_den).rational()
                        if parity_flag(ij) != parity_flag(kl):
                            assert a == zero(16) and b == zero(16)
                        if (ij[0] == 0) != (kl[0] == 0) or (ij[1] == 0) != (kl[1] == 0):
                            assert b == zero(16)
                        fresh[key] = cat.put(a)
                        reuse[key] = cat.put(b)
                totals = [effect(compose(summed[u], summed[v])) for u, v in product((1, -1), repeat=2)]
                assert add(totals, 4) == IX
                records["two_reads"] = {
                    "fresh_reference_fine_choi": fresh,
                    "same_post_reference_fine_choi": reuse,
                    "fresh_source_admission": "1/64",
                    "reuse_source_admission": "1/8",
                    "reuse_joint_recipe": "For ports f,g use O_g O_f, squared denominator n_g n_f, on the one initial source. All first and second path latches are retained; the second comparison path and keeper are fresh.",
                    "fresh_joint_recipe": "Apply O_f on data and first reference, then O_g on data and independent second reference, retaining first reference and both path/keeper records.",
                }
            rows[str(relation)] = records
        out[family] = rows
    frame = {}
    for db, rb in product((1, -1), repeat=2):
        p = paired_ports(local_ports(), local_ports(data_frame=db, ref_frame=rb))
        c = coarse(data_channels(p, Root(YRHO[1])), parity_flag)
        for t in (-1, 1):
            assert c[t] == DSEC[t * db * rb]
        frame[f"data_B_{db}/reference_B_{rb}"] = process_records(c, cat)
    out["frame_controls"] = frame
    # The recorded local comparison is available with just one addressed wing.
    one = {}
    for side in ("A", "B", "none"):
        l = local_ports() if side == "A" else [(UNIT, 1)]
        r = local_ports() if side == "B" else [(UNIT, 1)]
        ops = paired_ports(l, r)
        ch = data_channels(ops, Root(YRHO[1]))
        one[side] = {
            "fine_data": process_records(ch, cat),
            "joint_ops": {label(ij): [op.put(cat), d] for ij, (op, d) in ops.items()},
            "decoded_sign": None,
            "other_bank": "110 ready",
        }
    out["one_or_no_addressed"] = one
    return out


def path_mark_and_full_read(cat):
    """Copy a local three-alternative route before recombination or resolve actual input addresses."""
    def observed_effect(x):
        return Root(effect(x.a), effect(x.b)).rational()

    coeffs = ((1, 1, 1), (1, -1, 0), (1, 1, -2))
    norms = (9, 6, 18)
    powers = [kron(TURNS[l], TURNS[l]) for l in range(3)]
    regular = local_ports()
    ref = Root(YRHO[1])
    result = {}
    for tagA, tagB in ((True, False), (False, True), (True, True)):
        maps = {}
        fine = {}
        for i, j in product(range(3), repeat=2):
            fields = {}
            for a, b in product(
                range(3) if tagA else (None,), range(3) if tagB else (None,)
            ):
                na = regular[i][0] if a is None else powers[a].scale(coeffs[i][a])
                nb = regular[j][0] if b is None else powers[b].scale(coeffs[j][b])
                op = group_sites(kron(na, nb))
                fields[str((a, b))] = [op.put(cat), norms[i] * norms[j]]
                fine[(i, j, a, b)] = effective(op, ref, norms[i] * norms[j])
            parts = [ch for (p, q, _, _), ch in fine.items() if (i, j) == (p, q)]
            maps[(i, j)] = Root(
                add([x.a for x in parts], 16), add([x.b for x in parts], 16)
            )
            fields["state_recipe"] = (
                "For tag indices h,k the retained pre-read joint tag block is O_h(rho tensor sigma)O_k^T/n. A physical read resolves its diagonal blocks; summing those gives the ignored-tag data."
            )
            result[f"complete_tag_operators/{int(tagA)}{int(tagB)}/{i}{j}"] = fields

        assert add([observed_effect(v) for v in maps.values()], 4) == IX
        for ij, ch in maps.items():
            assert observed_effect(ch) == IX.scale(
                (F(1, 3) if tagA else (F(1, 2) if ij[0] == 0 else F(1, 4)))
                * (F(1, 3) if tagB else (F(1, 2) if ij[1] == 0 else F(1, 4)))
            )
        result[f"which_route_kept_or_physically_read/{int(tagA)}{int(tagB)}"] = {
            "data_choi_when_ignored": {label(k): v.put(cat) for k, v in maps.items()},
            "data_choi_after_which_route_ordinary_read": {
                str(k): v.put(cat) for k, v in fine.items()
            },
            "decoded_when_ignored": {
                str(t): [
                    cat.put(
                        add([v.a for k, v in maps.items() if parity_flag(k) == t], 16)
                    ),
                    cat.put(
                        add([v.b for k, v in maps.items() if parity_flag(k) == t], 16)
                    ),
                ]
                for t in (1, -1)
            },
        }
    clean = data_channels(paired_ports(regular, regular), ref)
    result["algebraic_sum_after_true_uncompute_equals_untagged"] = {}
    for i, j in product(range(3), repeat=2):
        oc = group_sites(kron(regular[i][0], regular[j][0]))
        oc2 = oc.scale(0)
        for a, b in product(range(3), repeat=2):
            oc2 = oc2 + group_sites(kron(powers[a], powers[b])).scale(
                coeffs[i][a] * coeffs[j][b]
            )
        assert oc2 == oc
        result["algebraic_sum_after_true_uncompute_equals_untagged"][f"{i}{j}"] = [
            cat.put(clean[(i, j)]),
            oc2.put(cat),
        ]
    from instrument_math import BASE, Mat, kraus_map
    from real_algebra import C, real_charge
    import numpy as np

    projectors = [tensor(a, b) for a, b in product(BASE, repeat=2)]
    rows = {
        (l, *ij): compose(ch, kraus_map(proj))
        for l, proj in enumerate(projectors)
        for ij, ch in clean.items()
    }
    result["two_fully_read_input_data_words_then_clean_offer"] = process_records(
        rows, cat
    )
    fullref = real_charge(1, 1)
    # Use all 3 x 3 *physical* word addresses after resolving the reference. A resolved ternary word may leave its prior logical plane.
    local = []
    for row in coeffs:
        v = kron(TURNS[0], Root(identity(3))).scale(0)
        for l, g in enumerate((identity(3), C, C.T)):
            v = v + kron(TURNS[l], Root(g)).scale(row[l])
        local.append(v)

    def rg(m):
        ar = (
            m.a.reshape(2, 3, 2, 3, 2, 3, 2, 3)
            .transpose(0, 2, 1, 3, 4, 6, 5, 7)
            .reshape(36, 36)
        )
        return Mat(ar, m.d)

    big_joint = {}
    for i, j in product(range(3), repeat=2):
        un = kron(local[i], local[j])
        big_joint[i, j] = Root(rg(un.a), rg(un.b))
    logged = {}
    for a, b in product(range(3), repeat=2):
        p = Mat(np.diag([int(k == a * 3 + b) for k in range(9)]))
        sigma = Root(p @ fullref @ p)
        chans = {
            ij: effective(op, sigma, norms[ij[0]] * norms[ij[1]])
            for ij, op in big_joint.items()
        }
        assert add([observed_effect(v) for v in chans.values()], 4) == IX.scale(F(1, 9))
        logged[f"{a}{b}"] = {
            "true_resolved_word_probability": "1/9",
            "joint_input_reference": sigma.put(cat),
            "fine_data": {label(ij): c.put(cat) for ij, c in chans.items()},
        }
    result["both_actual_reference_words_fully_read"] = logged
    result["resolved_three_word_reference_joint_operators"] = {
        label(ij): [op.put(cat), norms[ij[0]] * norms[ij[1]]]
        for ij, op in big_joint.items()
    }
    return result
