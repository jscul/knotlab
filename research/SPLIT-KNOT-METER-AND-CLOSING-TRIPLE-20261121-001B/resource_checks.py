"""Forward gate columns, source flags and local spectator resource tests."""

from fractions import Fraction as F
from itertools import product
import gzip
import json
import numpy as np
from triple_instrument import (
    ANCESTOR,
    BASE,
    BITS,
    FINE,
    I,
    IX,
    JOINT,
    IDEAL,
    SIGNS,
    XX,
    ZZ,
    YY,
    X,
    Z,
    Mat,
    add,
    apply_channel,
    born,
    compose,
    effect,
    key,
    kraus_map,
    P1,
    program,
    rank,
    ray,
    signs,
    tensor,
    zero,
    IDENTITY_CHANNEL,
)


def forward_circuit(cat):
    # Independent integer circuit on (A_data,B_data,A_x,B_x,A_z,B_z). Input map has four columns.
    h = np.array([[1, 1], [1, -1]], dtype=object)

    def hgate(state, bit):
        out = np.zeros_like(state)
        for i in range(64):
            current = (i >> bit) & 1
            for j in BITS:
                out[(i & ~(1 << bit)) | (j << bit)] += h[j, current] * state[i]
        return out

    def cx(state, c, t):
        out = np.zeros_like(state)
        for i in range(64):
            out[i ^ (((i >> c) & 1) << t)] += state[i]
        return out

    init = np.zeros((64, 4), dtype=object)
    for data in range(4):
        for u, v in product(BITS, repeat=2):
            init[(data << 4) | (u << 3) | (u << 2) | (v << 1) | v, data] = 1
    gates = {}
    for ordering in product(BITS, repeat=2):
        state = init.copy()
        for s in BITS:
            for mode in ("z", "x") if ordering[s] else ("x", "z"):
                if mode == "x":
                    state = cx(state, 3 - s, 5 - s)
                else:
                    state = hgate(cx(hgate(state, 5 - s), 1 - s, 5 - s), 5 - s)
        for t in (3, 2, 1, 0):
            state = hgate(state, t)
        reps = {}
        declared, _ = program(reversed_order=ordering)
        for f in FINE:
            fa = sum(v << (3 - i) for i, v in enumerate(f))
            k = Mat(state[fa::16], 32)
            assert kraus_map(k) == declared[f]
            reps[key(f)] = cat.put(k)
        assert Mat(state.T @ state, 1024) == IX
        gates["reverse_" + key(ordering)] = reps
    return {
        "raw_K_on_all_six_computational_bits": gates,
        "meter_preparation": "equal pairs (00+11)/sqrt2 on A28 B28 and independently on A29 B29",
        "normalization": "initial /2; four H gates in the two controlled Z decompositions, followed by four H on the individual meters; total /32",
        "pair_carriers_after_actual_ordinary_read": "product of the four recorded computational bits; multiplying by the four true inverse analyzers changes them into their recorded real X eigenvectors, independently of returned data.",
    }


def select_sources(cat):
    phase_maps = {p: program(source=p)[0] for p in product(SIGNS, repeat=2)}
    controls = {}
    for s, maps in phase_maps.items():
        for f, c in maps.items():
            x, z, _ = signs(f)
            real = (s[0] * x, s[1] * z, -s[0] * s[1] * x * z)
            assert c == IDEAL[real].scale(F(1, 4))
        controls["resolved_or_wrong" + key(s)] = {
            key(f): cat.put(c) for f, c in maps.items()
        }
    for mode, probs in [
        ("independent_bench_ports", {s: F(1, 4) for s in phase_maps}),
        ("same_hidden_ports", {(1, 1): F(1, 2), (-1, -1): F(1, 2)}),
        ("only_28_uncorrected", {(1, 1): F(1, 2), (-1, 1): F(1, 2)}),
        ("only_29_uncorrected", {(1, 1): F(1, 2), (1, -1): F(1, 2)}),
    ]:
        maps = {
            f: add([phase_maps[s][f].scale(v) for s, v in probs.items()], 16)
            for f in FINE
        }
        for f, m in maps.items():
            if mode == "independent_bench_ports":
                assert effect(m) == IX.scale(F(1, 16))
            if mode == "same_hidden_ports":
                assert effect(m) == P1(YY, signs(f)[2]).scale(F(1, 8))
        controls[mode] = {
            "hidden_fine_choi": {key(f): cat.put(v) for f, v in maps.items()},
            "per_central_label_conditional_choi": {
                key(s): {key(f): cat.put(v.scale(pr)) for f, v in phase_maps[s].items()}
                for s, pr in probs.items()
            },
            "zero_other_labels": True,
            "individual_label_frequencies": [
                str(sum(pr for s, pr in probs.items() if s[i] == -1)) for i in BITS
            ],
        }
    # The actual older labelled source recovered by complementary local trit shares.
    ancestor = json.load(gzip.open(ANCESTOR / "observations.json.gz", "rt"))
    cut = ancestor["reference_source_cuts"]
    old = ancestor["matrix_library"]
    inherited = {}
    for labels, rec in cut["disjoint_shares"].items():
        raw = old[rec["physically_repaired_without_message"]["Q_sqrt3_coefficients"][0]]
        recovered = Mat(raw["rows"], raw["den"])
        assert recovered == ray([1, 0, 0, 1])
        inherited[labels] = {
            "old_original_herald": rec["per_original_source_request"],
            "pure_pair_after_two_local_repairs": cat.put(recovered),
            "as_unadvertised_extra_plus_one_declared_pair_cross_reader_rank": 4,
        }
    return {
        "crossed_phase_sources": controls,
        "nine_actual_hidden_source_share_paths": inherited,
    }


def arm_gateway(available, cat=None):
    slots = [(0, 1) if a else (None,) for a in available]
    fine = {}
    for i, k, j, l in product(slots[0], slots[0], slots[1], slots[1]):
        tx = P1(XX, (-1) ** (i + k)) if available[0] else IX
        tz = P1(ZZ, (-1) ** (j + l)) if available[1] else IX
        n = 2 ** sum(available)
        fine[(i, k, j, l)] = kraus_map(tz @ tx, n)
    assert add([effect(c) for c in fine.values()], 4) == IX
    return fine


def whole_requests(cat):
    admission = {a: arm_gateway(a) for a in product(BITS, repeat=2)}
    result = {}
    traces = {}
    for policies in product(("correct_both", "plus_only"), repeat=2):
        request = {}
        for hk in product(SIGNS, repeat=2):
            avail = tuple(p == "correct_both" or h == 1 for p, h in zip(policies, hk))
            for f, c in admission[avail].items():
                read = key(hk) + "/" + key(f)
                request[read] = c.scale(F(1, 4))
        assert add([effect(c) for c in request.values()], 4) == IX
        name = "/".join(policies)
        traces[name] = request
        result[name] = {
            "all_source_ports_then_four_local_records": {
                f: cat.put(c) for f, c in request.items()
            },
            "full_two_pair_acceptance": str(F(1, 2) ** policies.count("plus_only")),
        }
    denied = {}
    for mask, c in admission.items():
        denied[key(mask)] = {
            "partial_fine_choi": {key(f): cat.put(v) for f, v in c.items()},
            "atomic_preflight_refusal_if_incomplete": cat.put(IDENTITY_CHANNEL)
            if not all(mask)
            else None,
        }
    repeat = {}
    # All first/second exact histories are indexed by the recorded first and second maps, including every failure.
    mult = {}
    for px, first in traces.items():
        for pz, last in traces.items():
            tab = {}
            for k, m in first.items():
                for l, n in last.items():
                    a, b = cat.put(m), cat.put(n)
                    if (a, b) not in mult:
                        mult[a, b] = cat.put(compose(n, m))
                    tab[k + ";" + l] = mult[a, b]
            repeat[px + "/" + pz] = {
                "all_ordered_subnormalized_choi": tab,
                "both_complete": str(
                    F(result[px]["full_two_pair_acceptance"])
                    * F(result[pz]["full_two_pair_acceptance"])
                ),
            }
    third = {}
    for pol in product(("correct_both", "plus_only"), repeat=3):
        rows = {}
        for h in product(SIGNS, repeat=3):
            ok = tuple(p == "correct_both" or e > 0 for p, e in zip(pol, h))
            rows[key(h)] = {
                "whole_prior": "1/8",
                "two_primary_and_verification_source_present": ok,
            }
        third["/".join(pol)] = {
            "all_original_source_ports": rows,
            "all_three": str(F(1, 2) ** pol.count("plus_only")),
        }
    return {
        "binary_sources": result,
        "all_missing_resource_masks": denied,
        "both_requests_with_every_denial": repeat,
        "two_plus_optional_third_source": third,
        "direct_partial_rule": "After a primary partial history with Choi C, if the third reference is admitted, every local pair i,k has the complete map (P_y(.)P_y/2) composed after C for y=(-1)^(i+k); a denied third leaves C. A display agreement needs the hardware validity marks as well.",
    }


def spectral_ledger(cat, destructive):
    b = ray([1, 0, 0, 1])
    # Independent local entanglement target A–spectator A and target B–spectator B, then reorder by (spectator AB, target AB).
    local = tensor(b, b)

    def interchange(m):
        a = m.a.reshape((2,) * 8)
        return Mat(a.transpose(0, 2, 1, 3, 4, 6, 5, 7).reshape(16, 16), m.d)

    probe = interchange(local)
    witness = {}
    for xyz, p in JOINT.items():
        k = tensor(IX, p)
        raw = k @ probe @ k
        assert raw == IDEAL[xyz].scale(F(1, 4))
        if not p.tr():
            witness[key(xyz)] = {
                "p": "0",
                "undefined_conditional": True,
                "raw": cat.put(raw),
            }
            continue
        assert raw == tensor(p, p).scale(F(1, 4))
        repart = interchange(raw.scale(4))
        left = Mat(np.trace(repart.a.reshape(4, 4, 4, 4), axis1=1, axis2=3), repart.d)
        assert left == IX.scale(F(1, 4))
        old = apply_channel(destructive[xyz], p)
        assert born(old, p) == F(1, 2)
        dprobe = destructive[xyz].scale(F(1, 4))
        assert dprobe == tensor(p, old).scale(F(1, 4))
        witness[key(xyz)] = {
            "p": "1/4",
            "unnormalized_with_spectators": cat.put(raw),
            "left_reduced_normalized": cat.put(left),
            "squared_Schmidt": ["1/4"] * 4,
            "cut_rank": rank(left.key()),
            "pure_entanglement_bits": 2,
            "one_pair_destructive_conditional_data": cat.put(old),
            "one_pair_original_spectator_probe_branch": cat.put(dprobe),
            "squared_overlap": "1/2",
        }
    # A source with rank four but low entropy: only a heralded filter makes it two uniform pairs.
    w = [F(13, 16), F(1, 16), F(1, 16), F(1, 16)]
    transmit = [F(1, 13), F(1), F(1), F(1)]
    ok = [p * f for p, f in zip(w, transmit)]
    fail = [p * (1 - f) for p, f in zip(w, transmit)]
    assert ok == [F(1, 16)] * 4 and fail == [F(3, 4), 0, 0, 0]
    return {
        "untouched_local_spectators": cat.put(probe),
        "complete_case": witness,
        "initially_local_across_labs": True,
        "separated_resource_budget": {
            "zero_pairs": 1,
            "one_corrected_pair": 2,
            "two_corrected_pairs": 4,
            "exact_effects_only_minimum_binary_pairs": 1,
            "complete_report_and_return_minimum_binary_pairs": 2,
            "worst_pure_state_overlap_with_correct_effects_one_pair": "1/2",
        },
        "four_level_source": {
            "initial_Schmidt_probabilities": list(map(str, w)),
            "initial_entropy_formula": "4 - 13 log2(13)/16",
            "filter_squared_singular_values": list(map(str, transmit)),
            "both_original_ports": {"success_mass": "1/4", "failure_mass": "3/4"},
            "subnormalized_success_Schmidt_weights": list(map(str, ok)),
            "subnormalized_rejection": list(map(str, fail)),
            "initial_entropy_less_than_one_exact_integer_test": 13**13 > 2**48,
        },
    }


def spent_and_direct(cat, first):
    """For a deliberate dirty-meter readdress, include the actual product state on the four carriers."""
    from triple_instrument import make_inputs

    histories = {}
    for returned in (False, True):
        tab = {}
        same = zero(4)
        xplus = zero(4)
        for f, g in product(FINE, repeat=2):
            local = []
            for s in BITS:
                if returned:
                    px = (I + X.scale((-1) ** (f[s] + g[s]))).scale(F(1, 2))
                    pz = (I + Z.scale((-1) ** (f[s + 2] + g[s + 2]))).scale(F(1, 2))
                    l = pz @ px
                else:
                    # Raw |f> controls remain after analyzing the first two meters.
                    l = (Z if f[s + 2] else I) @ (X if f[s] else I)
                local.append(l)
            next_map = kraus_map(tensor(*local), 1 if returned else 16)
            c = compose(next_map, first[f])
            tab[key(f) + "/" + key(g)] = cat.put(c)
            if signs(f) == signs(g):
                same = same + effect(c)
            if signs(g)[0] == 1:
                xplus = xplus + effect(c)
        assert same == (P1(XX, 1).scale(F(1, 2)) if returned else IX.scale(F(1, 4)))
        assert xplus == (IX if returned else IX.scale(F(1, 2)))
        histories[str(returned)] = {
            "all_256_spent_readdress_choi": tab,
            "same_triple_effect": cat.put(same),
            "second_28_positive_effect": cat.put(xplus),
            "first_equals_second_by_input": {
                s: str(born(r, same)) for s, r in make_inputs().items()
            },
        }
    histories["clean_admission_boundary"] = (
        "A physical attempt to present an already measured meter and its receipts as fresh is refused. The deliberate readdresses above instead preserve the old marks and address the known product carrier using fresh readout work. Their second measurement is a different instrument."
    )
    # Joint Bell decoding with a co-located gate, used only as an audit of location and poststate.
    cx = Mat([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    h = Mat([[1, 1], [1, -1]])
    decode = tensor(h, I) @ cx
    joint_read = {}
    for u, v in product(BITS, repeat=2):
        p = tensor(BASE[u], BASE[v])
        k = p @ decode
        t = ((-1) ** u, (-1) ** v, -((-1) ** (u + v)))
        raw = kraus_map(k, 2)
        repaired = kraus_map(decode.T @ k, 4)
        assert effect(raw) == JOINT[t] and repaired == IDEAL[t]
        joint_read[key((u, v))] = {
            "decoded": t,
            "two_locally_read_target_words": cat.put(raw),
            "inverse_at_the_same_joint_laboratory": cat.put(repaired),
            "data_returns_to_original_separated_readers": False,
        }
    histories["co_located_joint_read_vs_undo"] = joint_read
    return histories


def missing_direct_and_privacy(cat):
    events = {}
    for ok in product(BITS, repeat=3):
        primary = arm_gateway(ok[:2])
        dirs = (0, 1) if ok[2] else (None,)
        tab = {}
        for f, p in primary.items():
            for i, k in product(dirs, repeat=2):
                y = (-1) ** (i + k) if ok[2] else None
                q = kraus_map(P1(YY, y), 2) if ok[2] else IDENTITY_CHANNEL
                after = compose(q, p)
                tab[key((*f, i, k))] = cat.put(after)
        events[key(ok)] = {"all_source_missing_and_recorded_ports": tab}
    # Each reader knows one uniformly random fine bit for each requested measurement until a message arrives.
    table = {}
    for f in FINE:
        for mask in product(BITS, repeat=4):
            bysite = {}
            for s in BITS:
                permits = mask[2 * (1 - s) : 2 * (1 - s) + 2]
                local = f[s], f[s + 2]
                remote = f[1 - s], f[3 - s]
                opts = []
                for p in product(BITS, repeat=2):
                    if any(m and r != t for m, r, t in zip(permits, remote, p)):
                        continue
                    x, z = ((-1) ** (a + b) for a, b in zip(local, p))
                    opts.append((x, z, -x * z))
                for newly in (False, True):
                    allowed = [w for w in opts if not newly or w[2] == signs(f)[2]]
                    bysite[f"{s}/direct_known_{int(newly)}"] = {
                        "candidate_triples": allowed,
                        "primary_archive_complete": all(permits),
                        "joint_label_deducible": len(allowed) == 1,
                        "individual_primary_sign_is_known": list(map(bool, permits)),
                        "direct_third_requires_own_and_remote_fresh_third_port": newly,
                    }
            table[key(f) + "/" + key(mask)] = bysite
    return {
        "all_eight_physical_source_masks": events,
        "compatible_triples_given_actually_disclosed_local_bits_on_the_maximally_mixed_input": table,
        "use_rule": "Inference is recorded separately from actual writes. One primary sign and an independently read third can mathematically determine a missing second sign; the fixed primary presence gate still withholds its complete archived triple.",
    }
