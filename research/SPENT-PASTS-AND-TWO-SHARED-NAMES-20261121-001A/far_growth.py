"""Actual funded local and remote offers, their exact full counts and charge-aware comparisons."""

from fractions import Fraction as F
from functools import cache
from pathlib import Path
import sys
import numpy as np
import sympy as sp

from controls import as_array, bits, clean_and_collision, legal


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR = ROOT / "research/UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001B"
sys.path.insert(0, str(PRIOR))
import growth_weights as prior


def label(a):
    return "".join(map(str, a))


def pins(physical, words):
    return dict(zip(physical, words, strict=True))


@cache
def node(law, fixed=(), second=None):
    """Each index is a bit pair on a real meeting, with optional fixed local bits."""
    return as_array(
        [
            [
                int(
                    legal((*i, *j, *fixed), law)
                    and (second is None or legal((*i, *j, *second), law))
                )
                for j in bits(2)
            ]
            for i in bits(2)
        ]
    )


@cache
def old_counts(m, variant, law, p, q, local=(), other=None):
    """Count each of four central two-name words, conditional on paid and marked names.

    This is independent of the predecessor's SAT / factor implementation and actual
    allocation engine. The central mark is the doubled meeting just after h=m//2.
    """
    h = m // 2
    t = node(law)
    left = np.linalg.matrix_power(t, h - 1) @ node(law, local, other)
    right = np.linalg.matrix_power(t, m - h)
    if variant == "witness":
        tail = node(law, (q,)) @ t @ node(law, (p,))
    else:
        tail = np.zeros((4, 4), dtype=object)
        for seam in (0, 1):
            a = as_array([int(legal((*x, p, seam), law)) for x in bits(2)])
            b = as_array([int(legal((*x, q, seam), law)) for x in bits(2)])
            tail += np.outer(b, a)
    return tuple(map(int, np.diag(right @ tail @ left)))


def physical_histogram(rows, marks, law):
    if law == "parity":
        return prior._ancestors()[1].Parity(rows).histogram(marks)
    values, report = prior._count_nae(rows, marks)
    assert values is not None, report
    return values


def certificate(rows, law):
    val = prior._certificate_columns(rows, law)
    # The full projection, its deletion tests and the canonical arity outcome are retained.
    return val


def allocation(rows, law):
    report = prior._round(rows, law)
    assert (
        report["actual_rounds_performed"] == 1
        and report["all_old_loose_names_used_once"]
    )
    return report


def matrix_offers(events, inputs, law):
    outputs = tuple(x for offer in events for x in offer["fresh_names"])
    assert sorted(inputs) == sorted(
        x for offer in events for x in offer["consumed_old_names"]
    )
    rows = []
    for i in bits(len(inputs)):
        packed = pins(inputs, i)
        row = []
        for y in bits(len(outputs)):
            full = packed | pins(outputs, y)
            row.append(
                int(
                    all(
                        legal([full[b] for b in item["new_support"]], law)
                        for item in events
                    )
                )
            )
        rows.append(row)
    return as_array(rows), outputs


def probabilities(nums):
    total = sum(nums)
    return [str(F(v, total)) for v in nums] if total else None


def matrix_prob(a):
    return [probabilities_row(row, sum(np.diag(a))) for row in a]


def probabilities_row(vals, total):
    return [str(F(v, total)) for v in vals]


def event_ratio(tallies, which):
    return str(
        F(sum(v for v, a in zip(tallies, which, strict=True) if a), sum(tallies))
    )


def old_far_chain(m, variant, law):
    src = prior._parallel_source(m, variant)
    rows = src.supports
    p, q = src.provenance["designated_loose_names"]
    old = allocation(rows, law)
    births = old["births"]
    after = old["full_new_supports"]
    new, end = matrix_offers(births, (p, q), law)
    full = as_array([old_counts(m, variant, law, *x) for x in bits(2)])
    assert physical_histogram(rows, (p, q, *src.marks), law) == list(full.flat)
    ns = full.sum(axis=1)
    new_counts = ns @ new
    assert list(new_counts) == physical_histogram(after, end, law)
    rec = {}
    for mode, func in [
        ("copied_pair", lambda x: label(x)),
        ("copied_equality", lambda x: str(int(x[0] == x[1]))),
        ("only_first_bit", lambda x: str(x[0])),
        ("no_copy", lambda x: ""),
    ]:
        groups = {}
        for j, x in enumerate(bits(2)):
            groups.setdefault(func(x), []).append(j)
        original = {k: full[:, ix].sum(axis=1) for k, ix in groups.items()}
        final = {k: f @ new for k, f in original.items()}
        masses = {
            k: [int(sum(f)), int(f @ f), int(sum(final[k])), int(final[k] @ final[k])]
            for k, f in original.items()
        }
        totals = [sum(t[i] for t in masses.values()) for i in range(4)]
        rec[mode] = {
            "word_chance_order": [
                "old ordinary",
                "old all clean with copy",
                "new ordinary",
                "new all clean with copy",
            ],
            "rows": {
                k: {
                    "old_count_by_p_q": list(map(int, original[k])),
                    "grown_count_by_current_end": list(map(int, final[k])),
                    "raw_mass": t,
                    "chance": [str(F(a, b)) for a, b in zip(t, totals)],
                }
                for k, t in masses.items()
            },
        }
    all_marks = tuple(src.marks)
    result = {
        "m": m,
        "variant": variant,
        "law": law,
        "old_roster": rows,
        "actual_round": old,
        "old_canonical_checks": certificate(rows, law),
        "new_canonical_checks": certificate(after, law),
        "marked_physical_names": all_marks,
        "old_and_new_holder_counts": [
            [len(prior._owners(r)[b]) for b in all_marks] for r in [rows, after]
        ],
        "separation_actual_new_births_to_mark": prior._holder_distances(
            after, births, all_marks
        ),
        "old_loose_names": [p, q],
        "new_loose_names": end,
        "old_counts": list(map(int, ns)),
        "new_counts": list(map(int, new_counts)),
        "old_ways": clean_and_collision(ns, prior._width(rows) - 2),
        "new_ways": clean_and_collision(new_counts, prior._width(after) - len(end)),
        "certified_by_second_full_word_count": True,
        "persistent_copies": rec,
    }
    if law == "nae":
        orig = rec["copied_equality"]["rows"]["1"]["chance"]
        result["ordinary_equality_change"] = str(F(orig[2]) - F(orig[0]))
    return result


def offer_names(events, which):
    return [x for x in events if any(i in x["consumed_old_names"] for i in which)]


def choose_banks(events, local):
    ans = []
    for i in local:
        [act] = offer_names(events, [i])
        assert act["consumed_old_names"] == (i,) and len(act["fresh_names"]) == 2
        ans.append(act)
    return ans


def coupled(m, arm, law):
    src = prior._parallel_source(m, "witness")
    p, q = src.provenance["designated_loose_names"]
    u = prior._width(src.supports)
    v = u + 1
    h = m // 2
    rows = list(src.supports)
    rows[h] = (*rows[h], u, v)
    if arm == "cap":
        d, f = u + 2, u + 3
        rows.append((p, d, f))
        remote = (q, d, f)
    else:
        remote = (p, q)
    rows = tuple(rows)
    act = allocation(rows, law)
    new = act["full_new_supports"]
    births = act["births"]
    local_events = choose_banks(births, (u, v))
    rem_events = offer_names(births, remote)
    assert len(rem_events) + len(local_events) == len(births)
    if arm == "cap":
        assert len(rem_events) == 3 and all(
            len(e["consumed_old_names"]) == 1 for e in rem_events
        )
    else:
        assert len(rem_events) == 1 and set(rem_events[0]["consumed_old_names"]) == {
            p,
            q,
        }
    local_matrix, local_out = matrix_offers(local_events, (u, v), law)
    remote_matrix, remote_out = matrix_offers(rem_events, remote, law)

    def old(a, r, other=None):
        if arm == "cap":
            y, b, c = r
            return sum(
                sum(old_counts(m, "witness", law, x, y, a, other))
                for x in (0, 1)
                if legal((x, b, c), law)
            )
        x, y = r
        return sum(old_counts(m, "witness", law, x, y, a, other))

    local = bits(2)
    rem = bits(len(remote))
    count = as_array([[old(a, r) for r in rem] for a in local])
    old_gram = as_array(
        [[sum(old(a, r, b) for r in rem) for b in local] for a in local]
    )
    ns = count.reshape(-1)
    assert list(ns) == physical_histogram(rows, (u, v, *remote), law)
    assert np.array_equal(np.diag(old_gram), count.sum(axis=1))
    Q = local_matrix.T @ count @ remote_matrix
    assert list(Q.flat) == physical_histogram(new, (*local_out, *remote_out), law)
    # A trace over the actual written old words carries a common old word on the two alternatives.
    c = remote_matrix.sum(axis=1)
    old_u_gram = local_matrix.T @ np.diag(count @ c) @ local_matrix
    square_gram = Q @ Q.T
    local_counts = Q.sum(axis=1)
    assert np.array_equal(np.diag(old_u_gram), local_counts)
    labels = bits(4)
    eq = [z[0] == z[2] for z in labels]
    herald = [z[0] == z[1] and z[2] == z[3] for z in labels]
    both = [a and b for a, b in zip(herald, eq)]

    def summarize(weights):
        success = F(event_ratio(weights, herald))
        good = F(event_ratio(weights, both))
        return {
            "complete_four_bit_packet": probabilities(weights),
            "first_fresh_bits_agree": event_ratio(weights, eq),
            "both_unaries_have_equal_output_bits": str(success),
            "all_other_outcomes": str(1 - success),
            "herald_and_two_equal_pairs_match": str(good),
            "two_pairs_match_given_herald": str(good / success) if success else None,
            "herald_interpretation": "For NAE an equal output pair certifies the opposite old bit. Under parity it certifies an even pair and input zero, not which common value the pair took.",
            "singleton_chances_one": [
                event_ratio(weights, [z[i] == 1 for z in labels]) for i in range(4)
            ],
        }

    flat = local_matrix.T @ count.sum(axis=1)
    assert len(set(local_matrix.sum(axis=1))) == 1
    record = {
        "m": m,
        "arm": arm,
        "law": law,
        "old_roster": rows,
        "actual_round": act,
        "old_canonical_checks": certificate(rows, law),
        "new_canonical_checks": certificate(new, law),
        "second_method_all_fixed_old_and_new_counts_agree": True,
        "central_old_holder": h,
        "cap_holder": len(rows) - 1 if arm == "cap" else None,
        "old_remote_names": remote,
        "old_local_names": [u, v],
        "local_children": local_events,
        "remote_children": rem_events,
        "old_to_new_local_slots": [
            [i, e["fresh_names"]] for i, e in zip((u, v), local_events)
        ],
        "new_local_loose_names": local_out,
        "new_remote_loose_names": remote_out,
        "new_actual_remote_birth_to_four_read_names": prior._holder_distances(
            new, rem_events, local_out
        ),
        "new_actual_remote_birth_to_old_local_inputs": prior._holder_distances(
            new, rem_events, (u, v)
        ),
        "old_cap_or_far_parent_meetings_to_old_local_inputs": prior._holder_distances(
            rows, [{"holder": (len(rows) - 1 if arm == "cap" else 0)}], (u, v)
        ),
        "all_four_new_local_names_one_holder": [
            len(prior._owners(new)[i]) for i in local_out
        ],
        "old_lawful_projected_end_count_matrix_rows_uv_cols_remote": count.tolist(),
        "new_ends_counts_rows_local_cols_remote": Q.tolist(),
        "old_ways": clean_and_collision(ns, prior._width(rows) - len(remote) - 2),
        "new_ways": clean_and_collision(
            Q.reshape(-1), prior._width(new) - len(local_out) - len(remote_out)
        ),
        "old_local_retained_density": matrix_prob(old_gram),
        "old_local_clean_density": matrix_prob(count @ count.T),
        "post_local_retained_density": matrix_prob(old_u_gram),
        "post_local_clean_density": matrix_prob(square_gram),
        "post_local_ordinary": summarize(local_counts),
        "post_local_clean": summarize(np.diag(square_gram)),
        "post_local_old_uniform_and_remote_stochastic_B_over_c": summarize(flat),
        "local_bool_offer_rows_uv_cols_four_fresh": local_matrix.tolist(),
        "remote_bool_offer": remote_matrix.tolist(),
        "global_old_source_proportional_full_core_and_cap_additional_words_per_old": (
            3 if law == "nae" else 2
        )
        if arm == "cap"
        else 1,
    }
    assert all(
        r["canonical_K1_K2_K3"]
        for r in record["old_canonical_checks"] + record["new_canonical_checks"]
    )
    record["same_input_operation_controls"] = operation_controls(
        count, local_matrix, remote_matrix
    )
    return record


@cache
def canonical(value):
    return str(sp.radsimp(sp.cancel(value)))


def norm_record(mat, denom=1):
    return [
        [canonical(mat[i, j] / denom) for j in range(mat.cols)] for i in range(mat.rows)
    ]


def operation_controls(F0, L0, B0):
    """The full surviving vectors factor; I-K*K gives the named complementary port."""
    f = sp.Matrix(F0.tolist())
    l = sp.Matrix(L0.tolist())
    b = sp.Matrix(B0.tolist())
    n = sp.trace(f * f.T)
    local_gram = l * l.T
    local_trace = sp.trace(local_gram)
    le = local_gram / local_trace
    source_local = f * f.T
    local_selected = l.T * source_local * l / (n * local_trace)
    lplus = sp.trace(local_selected)
    lc = [sum(L0[i, :]) for i in range(L0.shape[0])]
    tagged_local = (
        l.T * sp.diag(*[source_local[i, i] / lc[i] for i in range(f.rows)]) * l / n
    )
    eq_indices = [i for i, z in enumerate(bits(4)) if z[0] == z[2]]

    def eq_chance(g):
        norm = sp.trace(g)
        return canonical(sum(g[i, i] for i in eq_indices) / norm) if norm else None

    output = {
        "local_first_fresh_equal_given_local_success_remote_ignored": eq_chance(
            local_selected
        ),
        "local_first_fresh_equal_for_two_unconditional_tagged_normalized_offers": eq_chance(
            tagged_local
        ),
        "old_pure_count_matrix": F0.tolist(),
        "old_squared_norm": int(n),
        "local_success_effect_on_inputs": norm_record(le),
        "local_alpha_squared": str(1 / local_trace),
        "local_complete_ignored_remote": {
            "success": canonical(lplus),
            "failure": canonical(1 - lplus),
            "success_subnormalized_output_matrix": norm_record(local_selected),
            "failure_subnormalized_output": "sqrt(I-local_effect) * old_local_matrix * sqrt(I-local_effect), with old_local_matrix = F F^T / old_squared_norm.",
        },
        "both_sides_tag_old_input_marginal_in_unread_local_tag_output_bank": norm_record(
            tagged_local
        ),
        "rows_and_spaces": "Input amplitudes f(i,j)/sqrt(N) with N=sum f^2. L and R here have old rows, new columns. The selected local is L^T/sqrt(trace(L L^T)); remote matrices scale analogously. Each failed branch retains its own input-sized output space. The four joint state amplitude matrices are A_local f A_remote^T / sqrt(N), where A is the selected map or the stored principal square root of I−K*K; normalize by the indicated mass on selection.",
        "tagged_remote_channel": "Input i goes to |i> times the normalized row of the Boolean matrix. Every old identity remains distinct on refusal. Sum all hidden tags and both complete ports; the displayed unconditioned local marginal is independent of this choice.",
    }
    c = tuple(sum(row) for row in B0.tolist())
    assert all(c)
    mode = {}
    for name, scale in [
        ("plain", tuple(sp.S(1) for _ in c)),
        ("unit_rows", tuple(sp.S(1) / sp.sqrt(i) for i in c)),
        ("unit_row_sums", tuple(sp.S(1) / i for i in c)),
    ]:
        r = sp.diag(*scale) * b
        gram = r * r.T
        rn = sp.trace(gram)
        e = gram / rn
        survived = f * e * f.T
        rplus = sp.trace(survived) / n
        both = l.T * survived * l / (n * local_trace)
        pp = sp.trace(both)
        pm = lplus - pp
        mp = rplus - pp
        mm = 1 - lplus - rplus + pp
        mode[name] = {
            "remote_input_factors": list(map(canonical, scale)),
            "remote_alpha_squared": canonical(1 / rn),
            "remote_success_effect": norm_record(e),
            "remote_failure_effect": norm_record(sp.eye(e.rows) - e),
            "success_plus_complement_all_four_probabilities": {
                "++": canonical(pp),
                "+-": canonical(pm),
                "-+": canonical(mp),
                "--": canonical(mm),
            },
            "local_matrix_given_two_successes": norm_record(both, pp) if pp else None,
            "local_first_fresh_equal_given_two_successes": eq_chance(both),
            "local_first_fresh_equal_given_local_success_remote_failure": eq_chance(
                local_selected - both
            ),
            "local_matrix_with_success_on_local_and_failure_on_remote_subnormalized": norm_record(
                local_selected - both
            ),
            "unconditioned_remote_ignored_local_success": canonical(pp + pm),
            "unconditioned_remote_ignored_local_failure": canonical(mp + mm),
            "remote_ignored_all_local_words_unchanged": True,
        }
        assert sp.simplify(pp + pm + mp + mm - 1) == 0
    output["coherent_remote_weightings_with_complete_instruments"] = mode
    return output


def run():
    historic = {
        f"{m}/{v}/{law}": old_far_chain(m, v, law)
        for m in [2, 4, 6, 8]
        for v in (["witness", "direct"] if m in (2, 4) else ["witness"])
        for law in ["nae", "parity"]
    }
    pairs = {}
    for m in (6, 8, 10):
        for law in ("nae", "parity"):
            a = coupled(m, "uncapped", law)
            b = coupled(m, "cap", law)

            def matrices_same(key):
                return a[key] == b[key]

            def difference(key):
                return str(
                    F(a[key]["first_fresh_bits_agree"])
                    - F(b[key]["first_fresh_bits_agree"])
                )

            av = a["post_local_ordinary"]
            bv = b["post_local_ordinary"]
            a["matched_source_local_states_across_arms"] = {
                "ordinary_full_local_density_identical": matrices_same(
                    "old_local_retained_density"
                ),
                "erased_full_local_density_identical": matrices_same(
                    "old_local_clean_density"
                ),
                "erased_local_diagonal_identical": np.diag(
                    a["old_local_clean_density"]
                ).tolist()
                == np.diag(b["old_local_clean_density"]).tolist(),
                "global_prior_same_on_every_full_old_core_word_by_constant_cap_extension": True,
                "full_arms_differ_by_paid_cap_and_remote_history": True,
                "local_XZ_basis": "Complete real X/Z product menu; entrywise reduced matrices supplied.",
            }
            compare = {
                "ordinary_A_minus_B_first_fresh_equality": difference(
                    "post_local_ordinary"
                ),
                "clean_A_minus_B_first_fresh_equality": difference("post_local_clean"),
                "flat_remote_division_A_minus_B_first_fresh_equality": difference(
                    "post_local_old_uniform_and_remote_stochastic_B_over_c"
                ),
                "ordinary_A_minus_B_herald_decoded_equality": str(
                    F(av["two_pairs_match_given_herald"])
                    - F(bv["two_pairs_match_given_herald"])
                ),
                "entire_ordinary_local_diagonals_equal": av["complete_four_bit_packet"]
                == bv["complete_four_bit_packet"],
                "entire_clean_local_diagonals_equal": a["post_local_clean"][
                    "complete_four_bit_packet"
                ]
                == b["post_local_clean"]["complete_four_bit_packet"],
            }
            assert a["matched_source_local_states_across_arms"][
                "ordinary_full_local_density_identical"
            ]
            pairs[f"{m}/{law}"] = {
                "A_remote_binary": a,
                "B_neutral_old_cap": b,
                "matched_reached_local_packet": compare,
            }
    return {
        "historic_witness_and_direct_full_records": historic,
        "two_arms_genuinely_loose_local_post_age": pairs,
    }


if __name__ == "__main__":

    result = run()
    for k, v in result["two_arms_genuinely_loose_local_post_age"].items():
        print(
            k,
            v["matched_reached_local_packet"],
            v["A_remote_binary"]["matched_source_local_states_across_arms"],
        )


def general_relay(k):
    """Independent two-by-two all-length determinant for the relay's old loose equality."""
    assert k >= 1
    t = sp.Matrix([[1, 2], [2, 2]])
    h = t**k
    g = t ** (k - 1)
    a, b = h[0, :]
    j = 2 * sp.ones(2)
    p = sp.diag(1, 0)
    c = sp.Matrix([[89, 100], [100, 112]])
    V = h * c * g
    W = -h * p * g
    x = (j * V).trace()
    y = V[0, 0] + 1
    z = (j * W).trace()
    w = W[0, 0] - 1
    determinant = x * w - z * y
    direct = 4 * (-2) ** k * (53 * a * a + 64 * a * b - 11 * b * b) - 2 * (
        106 * a * a + 281 * a * b + 186 * b * b
    )
    A = F(int(2 * (3 * x - z) - (3 * y - w)), int(4 * (3 * x - z) - (3 * y - w)))
    B = F(int(2 * x - y), int(4 * x - y))
    assert determinant == direct and (A - B) * (-1) ** k > 0
    return {
        "k": k,
        "X,Y,X_signed,Y_signed": list(map(int, (x, y, z, w))),
        "determinant": int(determinant),
        "old_equal_uv_in_neutral_arm": str(B),
        "old_equal_uv_after_remote_fibre_tilt": str(A),
        "ordinary_same_packet_first_fresh_A_minus_B": str((A - B) / 9),
        "sign": (-1) ** k,
    }
