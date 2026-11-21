"""Trace each source port and every real single-pair read before and after a cut."""

from itertools import product, combinations
import numpy as np
from real_algebra import (
    F,
    Mat,
    I,
    P,
    C,
    T,
    LOCAL,
    MEAS,
    PROJECTORS,
    tensor,
    outer,
    ray,
    add,
    normalize,
    local_projection,
    reduce_sites,
    diag_only,
    powers,
    group,
    instrument,
    cycling,
    real_charge,
    ideal_complex_charge,
    born,
    angles_rank,
)


def field_claim(m, cat):
    p = m.tr()
    return {
        "p": str(p),
        "joint": cat.put(m),
        "conditional": cat.put(normalize(m)) if p else None,
        "ordinary_joint": m.diag(),
        "local_marginals": [cat.put(v) for v in reduce_sites(m)],
        "locally_real_projection": cat.put(local_projection(m)),
    }


def positive_source(cat):
    # Coherently applying both cycles on the second arm changes aa to bb.
    aa, bb = [int(j == 0) for j in range(9)], [int(j == 4) for j in range(9)]
    assert (tensor(C, C) @ Mat([[x] for x in aa])).a.flatten().tolist() == bb
    result = {}
    states = {}
    for tag_kind in (
        "never_coupled",
        "coupled_kept",
        "coupled_physically_returned",
        "fully_read",
    ):
        ports = []
        for sign in (1, -1):
            v = [(x + sign * y) for x, y in zip(aa, bb)]
            m = outer(v).scale(F(1, 4))
            coherent = tag_kind in ("never_coupled", "coupled_physically_returned")
            if not coherent:
                m = diag_only(m)
            ports.append(field_claim(m, cat))
            if tag_kind == "never_coupled":
                states["path_" + ("plus" if sign == 1 else "minus")] = normalize(m)
            else:
                assert m.tr() == F(1, 2)
            # Trace an actual orthogonal copy rather than classically summing two phases.
            pieces = [
                [
                    outer(x, y).scale(F(sign ** (j + k), 4))
                    for k, y in enumerate((aa, bb))
                ]
                for j, x in enumerate((aa, bb))
            ]
            joint_tag = Mat(
                np.block([[v.a * (4 // v.d) for v in row] for row in pieces]), 4
            )
            if tag_kind in ("coupled_kept", "fully_read"):
                ports[-1]["orthogonal_tag_joint_before_trace"] = cat.put(
                    joint_tag if tag_kind == "coupled_kept" else diag_only(joint_tag)
                )
                assert pieces[0][0] + pieces[1][1] == m
            else:
                assert add([z for r in pieces for z in r], 9) == m
        result[tag_kind] = ports
    states["matched_aa_bb_dephased"] = diag_only(states["path_plus"])
    states["ordinary_aa"] = outer(aa)
    assert (
        states["path_plus"].diag()
        == states["path_minus"].diag()
        == states["matched_aa_bb_dephased"].diag()
    )
    assert (
        reduce_sites(states["path_plus"])
        == reduce_sites(states["path_minus"])
        == reduce_sites(states["matched_aa_bb_dephased"])
    )
    # Missing common second path or either conditional offer. Both path outputs retained.
    other = {}
    for offered in product((False, True), repeat=2):
        dest = (1 if offered[0] else 0) * 3 + (1 if offered[1] else 0)
        alt = [int(j == dest) for j in range(9)]
        for s in (1, -1):
            v = [x + s * y for x, y in zip(aa, alt)]
            other[str((offered, s))] = field_claim(outer(v).scale(F(1, 4)), cat)
    result["disconnected_controlled_offers"] = other
    return {
        "positive_ports": result,
        "basis_and_selector": "Complete aa pointer word and separate a route; both clean ports accepted, each with measured probability, resolved later on the preparation bench.",
    }, states


def local_raw_source(h):
    # Unnormalized pointer after one addressed path comparison, h=0 plus or h=1 minus.
    return outer((1, (-1) ** h, 0)).scale(F(1, 4))


def received_block(m, cat):
    return {
        "pointer_state": cat.put(m),
        "weight": str(m.tr()),
        "visible_to_all_real_local_effects": cat.put(local_projection(m)),
        "two_ordinary_words": m.diag(),
    }


def charge_sources(cat):
    result = {}
    source_by_mode = {}
    for cb in (1, -1):
        g = tensor(C, C if cb == 1 else C.T)
        trit = powers(tensor(C, I))
        refl = tensor(I, T)
        failures = {}
        raw = None
        for h, k in product(range(2), repeat=2):
            src = tensor(local_raw_source(h), local_raw_source(k))
            if (h, k) != (1, 1):
                failures[f"source_{h}{k}"] = {
                    "bench": field_claim(src, cat),
                    "both_wings": "admission0_no_delivery",
                    "unconditional_weight": str(src.tr()),
                }
                continue
            for ix, branch in enumerate(instrument(src, group(g))):
                if ix == 0:
                    raw = branch
                else:
                    failures[f"group_{ix}"] = {
                        "bench": field_claim(branch, cat),
                        "both_wings": "admission0_no_delivery",
                        "unconditional_weight": str(branch.tr()),
                    }
        assert (
            raw is not None
            and raw.tr() + sum(F(x["unconditional_weight"]) for x in failures.values())
            == 1
        )
        assert raw.tr() == F(1, 8)
        mode_states = {}
        for mode in ("equal", "opposite", "independent"):
            branches = {}
            for j, coin in product(range(3), range(2)):
                dest = (
                    ("equal" if coin else "opposite") if mode == "independent" else mode
                )
                need_flip = (dest == "equal") == (cb == 1)
                b = cycling(trit[j], raw)
                if need_flip:
                    b = cycling(refl, b)
                branches[(j, coin)] = b.scale(F(1, 6))
            panels = {}
            for name, labels in {
                "unannounced": {"*": list(branches)},
                "trit_announced": {
                    str(j): [(j, c) for c in range(2)] for j in range(3)
                },
                "coin_announced": {
                    str(c): [(j, c) for j in range(3)] for c in range(2)
                },
                "both_announced": {f"{j}/{c}": [(j, c)] for j, c in branches},
            }.items():
                panels[name] = {
                    label: received_block(add([branches[jc] for jc in ids], 9), cat)
                    for label, ids in labels.items()
                }
            mixed = add(branches.values(), 9)
            assert mixed.tr() == raw.tr()
            clean_modes = [
                cycling(refl, raw) if ((dest == "equal") == (cb == 1)) else raw
                for dest in ("equal", "opposite")
            ]
            clean = (
                clean_modes[("equal", "opposite").index(mode)]
                if mode != "independent"
                else (clean_modes[0] + clean_modes[1]).scale(F(1, 2))
            )
            panels["unrandomized_clean"] = {"*": received_block(clean, cat)}
            mode_states[mode] = panels
            expected = (
                real_charge(1, 1)
                if mode == "equal"
                else real_charge(1, -1)
                if mode == "opposite"
                else tensor(P, P).scale(F(1, 4))
            )
            assert normalize(mixed) == expected
            if cb == 1:
                source_by_mode[mode] = expected
                source_by_mode[mode + "_clean"] = normalize(clean)
        label_grades = {}
        for panel in mode_states["equal"]:
            label_grades[panel] = {}
            for one, two in combinations(mode_states, 2):
                grade = {}
                for label, v in mode_states[one][panel].items():
                    w = mode_states[two][panel][label]
                    grade[label] = {
                        "equal_label_rate": v["weight"] == w["weight"],
                        "equal_ordinary_joint": v["two_ordinary_words"]
                        == w["two_ordinary_words"],
                        "equal_all_real_local_transcripts": v[
                            "visible_to_all_real_local_effects"
                        ]
                        == w["visible_to_all_real_local_effects"],
                        "equal_complete_quantum_input": v["pointer_state"]
                        == w["pointer_state"],
                    }
                label_grades[panel][f"{one}/{two}"] = grade
        assert all(
            v["equal_all_real_local_transcripts"]
            for pair in label_grades["unannounced"].values()
            for v in pair.values()
        )
        assert not all(
            v["equal_all_real_local_transcripts"]
            for v in label_grades["trit_announced"]["equal/opposite"].values()
        )
        result[str(cb)] = {
            "failure_records": failures,
            "failure_delivered_record": {
                "public": 0,
                "pointers": "both absent",
                "both_keepers": "110",
                "same_failure_distribution_all_modes": True,
                "weight": str(1 - raw.tr()),
            },
            "success_before_randomization": field_claim(raw, cat),
            "whole_launch_probability_for_each_mode": str(raw.tr()),
            "disclosure_conditioned_blocks": mode_states,
            "subnormalized_accessible_label_comparisons": label_grades,
        }
    return result, source_by_mode


def p_table(m, bases, norm_conditional=True):
    return [[born(m, tensor(a, b)) for b in MEAS[bases[1]]] for a in MEAS[bases[0]]]


def tables(states, cat):
    out = {}
    for name, source in states.items():
        modes = {}
        for left, right in product(LOCAL, repeat=2):
            p = p_table(source, (left, right))
            assert sum(sum(row) for row in p) == 1
            assert [sum(x) for x in p] == [
                born(reduce_sites(source)[0], z) for z in MEAS[left]
            ]
            assert [sum(row[j] for row in p) for j in range(3)] == [
                born(reduce_sites(source)[1], z) for z in MEAS[right]
            ]
            ports = {}
            for j, k in product(range(3), repeat=2):
                effect = tensor(MEAS[left][j], MEAS[right][k])
                post = effect.scale(p[j][k])
                assert post == effect @ source @ effect
                ports[f"{j}{k}"] = [str(p[j][k]), cat.put(post)]
            modes[left + "/" + right] = {
                "physical_addresses": "Rows/columns a,b,c; all rows/columns containing the unprepared idle d have zero probability.",
                "probability_and_unnormalized_returned_state": ports,
            }
        # The idle receiver has no actual address record and a ready keeper.
        idle = {}
        for who in (0, 1):
            for setting in LOCAL:
                rr = []
                for a in MEAS[setting]:
                    effect = tensor(a, I) if who == 0 else tensor(I, a)
                    state = effect @ source @ effect
                    rr.append([str(state.tr()), cat.put(state)])
                idle[f"{who}/{setting}"] = rr
        modes["one_idle_no_far_write"] = idle
        out[name] = modes
    # A fully resolved real rank-one measurement on either wing removes its antisymmetric factor.
    assert out["equal"] == out["opposite"] == out["independent"]
    for m in ("equal", "opposite", "independent"):
        for ka in (l + "/" + h for l, h in product(LOCAL, repeat=2)):
            p1 = out[m][ka]["probability_and_unnormalized_returned_state"]
            p2 = out["independent"][ka]["probability_and_unnormalized_returned_state"]
            assert all(p1[k][0] == p2[k][0] for k in p1)
    return out


def repeat_instruments(cat):
    clean = {}
    for fs, j, basis in product(LOCAL, range(3), range(4)):
        # Calibrate each source basis word, including d, with idle padding.
        projs = MEAS[fs]
        if basis == 3:
            clean[f"{fs}/{j}/d"] = {
                "first_full_address": "d",
                "first_marked": False,
                "returned_second_address": "d",
                "again_marked": False,
            }
            continue
        raw = MEAS["word"][basis]
        rows = []
        for k, e in enumerate(projs):
            branch = e @ raw @ e
            nexts = [born(branch, v) for v in projs]
            assert sum(nexts) == branch.tr() and all(
                val == 0 for idx, val in enumerate(nexts) if idx != k
            )
            rows.append(
                {
                    "first_address": k,
                    "first_marked": k == j,
                    "p": str(branch.tr()),
                    "returned": cat.put(branch),
                    "second_subnormalized_address_frequencies": list(map(str, nexts)),
                    "both_marks_equal_whenever_branch_exists": True,
                }
            )
        clean[f"{fs}/{j}/{basis}"] = rows
    # Literal unreturned analyzer state is physical coordinate a or b after the first read.
    left = []
    for k in range(2):
        phys = MEAS["word"][k].scale(F(1, 2))
        left.append(
            {
                "observed_first": k,
                "joint_next_ordinary_after_new_ab_analyzer": [
                    str(born(phys, v)) for v in MEAS["ab"]
                ],
            }
        )
    sr = ray((0, 1, 1))
    ea = MEAS["word"][0]
    binary = (I - ea) @ sr @ (I - ea)
    full = add([MEAS["word"][j] @ sr @ MEAS["word"][j] for j in (1, 2)], 3)
    bc = [ray(v) for v in ((0, 1, 1), (0, 1, -1), (1, 0, 0))]
    assert [born(binary, q) for q in bc] == [1, 0, 0]
    assert [born(full, q) for q in bc] == [F(1, 2), F(1, 2), 0]
    return {
        "returned_full_read": clean,
        "literal_unreturned_ab_then_ab_from_a": left,
        "measuring_only_predicate_in_a_vs_full_j_on_bc_sum": {
            name: {
                "first_mark_a_p": "0",
                "complement_state": cat.put(m),
                "later_bc_sum_difference_a": list(map(str, [born(m, q) for q in bc])),
            }
            for name, m in [("binary", binary), ("full_address_grouped", full)]
        },
        "hardware_contract": "Every full/coarse probability is pushed forward through the chosen mark, addresses, stages and errors from physical_words. A disconnected analyzer is identity and delivers the actual ready/no-request label. A failed keeper after a completed measurement retains its full classical address, source state and complementary record.",
    }


def tomography(cat):
    product_effects = [tensor(a, b) for a, b in product(PROJECTORS.values(), repeat=2)]
    local_rank = angles_rank(list(PROJECTORS.values()))
    observed_rank = angles_rank(product_effects)
    asym = []
    for i, j in combinations(range(3), 2):
        m = np.zeros((3, 3), int)
        m[i, j] = 1
        m[j, i] = -1
        asym.append(Mat(m))
    odd = [tensor(a, b) for a, b in product(asym, repeat=2)]
    full_rank = angles_rank(product_effects + odd)
    assert (local_rank, observed_rank, full_rank) == (6, 36, 45)
    states = {
        "equal": real_charge(1, 1),
        "opposite": real_charge(1, -1),
        "independent": tensor(P, P).scale(F(1, 4)),
    }
    rr = {}
    for name, rho in states.items():
        rr[name] = {
            "all_36_binary_eff_complements": [
                list(
                    map(
                        str,
                        [
                            born(rho, tensor(u, v))
                            for u, v in product((a, I - a), (b, I - b))
                        ],
                    )
                )
                for a, b in product(PROJECTORS.values(), repeat=2)
            ],
            "local_projection": cat.put(local_projection(rho)),
            "hidden_component": cat.put(rho - local_projection(rho)),
        }
    assert (
        rr["equal"]["all_36_binary_eff_complements"]
        == rr["opposite"]["all_36_binary_eff_complements"]
        == rr["independent"]["all_36_binary_eff_complements"]
    )
    return {
        "ranks": {
            "local_real": local_rank,
            "visible_pair": observed_rank,
            "entire_real_symmetric": full_rank,
            "hidden": full_rank - observed_rank,
        },
        "pair_effects": [cat.put(m) for m in product_effects],
        "hidden_basis": [cat.put(m) for m in odd],
        "states": rr,
    }


def sources_and_reads(cat):
    positive, rr = positive_source(cat)
    charges, cs = charge_sources(cat)
    allstates = {**rr, **cs}
    complex_rows = {}
    for a, b in product((1, -1), repeat=2):
        complex_rows[f"{a},{b}"] = ideal_complex_charge(a, b)
        allstates[f"ideal_({a},{b})_real_part"] = real_charge(a, b)
    reads = tables(allstates, cat)
    raw_plus = reads["path_plus"]["ab/ab"][
        "probability_and_unnormalized_returned_state"
    ]
    raw_minus = reads["path_minus"]["ab/ab"][
        "probability_and_unnormalized_returned_state"
    ]
    p_match = lambda row: sum(F(x[0]) for k, x in row.items() if k[0] == k[1])
    assert p_match(raw_plus) == 1 and p_match(raw_minus) == 0
    return {
        "positive_source": positive,
        "charge_preparations": charges,
        "individual_supplied_complex_charges": complex_rows,
        "real_input_density_or_complex_real_part": {
            name: cat.put(m) for name, m in allstates.items()
        },
        "nine_setting_pairs": reads,
        "repeat_and_binary": repeat_instruments(cat),
        "tomography": tomography(cat),
        "single_setting_ordinary_emulator": {
            "algorithm": "For the selected setting pair, draw a joint ordinary label (j,k) with the probabilities below, distribute the respective coordinate, and run each ordinary keeper writer. It is calibrated for this one setting.",
            "selected": "ab/ab",
            "positive": {k: v[0] for k, v in raw_plus.items()},
            "negative": {k: v[0] for k, v in raw_minus.items()},
            "equal_keeper_bits_given_both_mark_a_on_two_active_outcomes": {
                "path_plus": "1",
                "path_minus": "0",
                "dephased": "1/2",
            },
        },
    }


def label_tables(charges, cat):
    ids = set()
    comparisons = {}
    for cb, bundle in charges.items():
        for mode, by_condition in bundle["disclosure_conditioned_blocks"].items():
            for cond, labels in by_condition.items():
                for label, row in labels.items():
                    ids.add(row["pointer_state"])
    probs = {}
    for idx in sorted(ids):
        data = cat.matrices[idx]
        m = Mat(data["rows"], data["den"])
        menu = {}
        for l, r in product(LOCAL, repeat=2):
            t = p_table(m, (l, r))
            assert sum(sum(row) for row in t) == m.tr()
            menu[l + "/" + r] = [[str(v) for v in row] for row in t]
        probs[str(idx)] = menu
    for cb, bundle in charges.items():
        d = bundle["disclosure_conditioned_blocks"]
        comparisons[cb] = {}
        for cut in d["equal"]:
            pair = {}
            for one, two in combinations(MATCH_MODES, 2):
                g = {}
                for label, block in d[one][cut].items():
                    a = probs[str(block["pointer_state"])]
                    b = probs[str(d[two][cut][label]["pointer_state"])]
                    g[label] = {
                        k: str(
                            F(1, 2)
                            * sum(
                                abs(F(x) - F(y))
                                for u, v in zip(a[k], b[k])
                                for x, y in zip(u, v)
                            )
                        )
                        for k in a
                    }
                pair[one + "/" + two] = g
            comparisons[cb][cut] = pair
    return {
        "subnormalized_menus_by_state_id": probs,
        "total_variations_by_delivered_label_and_setting": comparisons,
        "source_failures": "The no-delivery labels have the same subnormalized ready state for each matched request, including each separately tagged failure.",
    }


MATCH_MODES = ("equal", "opposite", "independent")


def whole_sector_match():
    # Fourier cos/sin rescaled to integer columns at x+y and x-y.
    from sympy import Matrix

    c = (2, -1, -1)
    s = (0, 1, -1)
    rows = [
        [c[(x + y) % 3], s[(x + y) % 3], -c[(x - y) % 3], -s[(x - y) % 3]]
        for x, y in product(range(3), repeat=2)
    ]
    rank = int(Matrix(rows).rank())
    assert rank == 4
    full = []
    for ids in combinations(range(9), 4):
        det = int(Matrix([rows[i] for i in ids]).det())
        if det:
            full = [list(ids), det]
            break
    return {
        "each_row_is_named_word_order_aa_ab_ac_ba_bb_bc_ca_cb_cc": rows,
        "rank": rank,
        "nonzero_minor": full,
        "coefficient_convention": "The independent real and imaginary parts of the same-sector and opposite-sector conjugate amplitudes multiply these columns after scaling. Pointwise equality forces all four real parameters to vanish. For real preparations the two diagonal charge populations equal 1/2.",
    }


def ideal_poststates(cat):
    # Keep the imaginary coefficient even for a unilateral read or two idle readers.
    # rho = U + omega V, with exact rational U,V. A real Hermitian effect sees
    # Re(rho)=U-V/2. Imaginary parts do not disappear merely through nonaccess.
    out = {}
    for signs in product((1, -1), repeat=2):
        inp = ideal_complex_charge(*signs)
        raws = inp["entries_in_1_omega"]
        a = Mat([[s[0] for s in row] for row in raws], 9)
        b = Mat([[s[1] for s in row] for row in raws], 9)
        ops = {name: row for name, row in MEAS.items()}
        ops["idle"] = [I]
        settings = {}
        for left, right in product(ops, repeat=2):
            rows = {}
            for i, u in enumerate(ops[left]):
                for j, v in enumerate(ops[right]):
                    e = tensor(u, v)
                    x = e @ a @ e
                    y = e @ b @ e
                    p = x.tr()
                    assert y.tr() == 0 and p == born(real_charge(*signs), e)
                    rows[f"{i}{j}"] = [str(p), cat.put(x), cat.put(y)]
            settings[left + "/" + right] = rows
        out[str(signs)] = settings
    return out


def joint_writes(quantum, mechanism):
    """Push actual address probabilities through actual ordinary keeper word maps."""
    from pointer_hardware import _basis_offer

    interface = mechanism["local_readout"]["local_analyzer_interface"]
    address = "abcd"
    settings = {"word": "ordinary", "ab": "real_ab", "hrs": "three_way"}
    lookup = {}
    for rev in (False, True):
        columns = interface[str(int(rev))]["basis_columns"]
        for ix, label in enumerate(address):
            for mark in address:
                for stages in ("00", "01", "10", "11"):
                    column = columns[f"{label}/{mark}/{stages}/1"]
                    old = column["final"]["A_record"]
                    rr = {}
                    for setting, off in settings.items():
                        branch = _basis_offer(old, off, inverse=False, reverse=rev)
                        outcomes = {}
                        for part in branch["all_four_basis_rows"]:
                            n, d = part["amplitude"]
                            q = F(n * n, d)
                            if ix < 3 and part["address"] != "d":
                                local = MEAS[setting][ix]
                                j = address.index(part["address"])
                                assert q == F(local.a[j, j], local.d)
                            outcomes[part["address"]] = [str(q), part["ordinary_word"]]
                        assert sum(F(vals[0]) for vals in outcomes.values()) == 1
                        rr[setting] = outcomes
                    key = f"{int(rev)}/{label}/{mark}/{stages}"
                    lookup[key] = {
                        "K": column["keeper"],
                        "recorded_flag": column["measured_flag"],
                        "returned_basis_before_O": old,
                        "after_O_complete_word_probabilities_if_measured": rr,
                    }
    primary = {}
    for name, rows in quantum["nine_setting_pairs"].items():
        primary[name] = {}
        for setting, table in rows.items():
            if setting == "one_idle_no_far_write":
                continue
            outcomes = {}
            for jk, v in table["probability_and_unnormalized_returned_state"].items():
                j, k = map(int, jk)
                kernels = [lookup[f"0/{address[i]}/a/11"] for i in (j, k)]
                key = "/".join(kernel["K"] for kernel in kernels)
                outcomes[key] = outcomes.get(key, F(0)) + F(v[0])
            assert sum(outcomes.values()) == 1
            primary[name][setting] = {
                code: str(prob) for code, prob in outcomes.items()
            }
    four = {}
    for name, value in quantum["reunion_and_additional_resources"][
        "known_real_distributed_reference"
    ].items():
        groups = {}
        for mode in ("unshifted", "fixed_reference_reverse_target_B"):
            d = {}
            for jk, v in value[mode].items():
                j, k = map(int, jk)
                code = "/".join(lookup[f"0/{address[i]}/a/11"]["K"] for i in (j, k))
                d[code] = d.get(code, F(0)) + F(
                    v["per_whole_preparation_and_comparison_request"]
                )
            assert sum(d.values()) == F(1, 64)
            d["110/110: source blocked before comparison"] = F(63, 64)
            groups[mode] = {k: str(x) for k, x in d.items()}
        four[name] = groups
    return {
        "one_pair_writes_selected_source_all_nine_settings": primary,
        "reference_pair_keeper_unconditional": four,
        "every_mark_and_writer_fault_output": lookup,
        "complete_joint_law": "For measured addresses j,k take the saved subnormalized port weight times the two chosen ordinary-word kernels. Joined fields include each site's actual flag, both keeper outcomes, stored address and success/fault record. An actual final ordinary word is an optional further measurement. The physically unmeasured returned pointer remains in its stored conditional density. For disclosed labels use their subnormalized table before this identical mapping. A missing or idle site uses its explicit no-write hardware record; a rejected two-pair comparison has probability 63/64 before any local query.",
    }
