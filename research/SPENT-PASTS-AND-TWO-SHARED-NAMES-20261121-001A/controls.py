"""Exact independent calculations on physical words and their erased or recorded pasts."""

from fractions import Fraction as F
from itertools import product
import numpy as np


def bits(n):
    return list(product((0, 1), repeat=n))


def legal(word, law):
    return len(set(word)) > 1 if law == "nae" else sum(word) % 2 == 0


def as_array(rows):
    return np.asarray(rows, dtype=object)


def clean_and_collision(ns, spent):
    n = sum(ns)
    w = sum(x * x for x in ns)
    if not n:
        return {"status": "empty no launch"}
    return {
        "full_word_count": int(n),
        "sum_squared_pasts": int(w),
        "clean_success": str(F(w, (1 << spent) * n)),
        "all_other_characters": str(1 - F(w, (1 << spent) * n)),
        "two_independent_same_end": str(F(w, n * n)),
        "different_ends": str(1 - F(w, n * n)),
    }


def prob_table(gram):
    """Joint signed Hadamard changes or ordinary reads on three marks, all entries."""
    v = bits(3)
    norm = np.trace(gram)
    p = {}
    moments = {}
    for s in v:
        z = []
        for out in v:
            amp = as_array(
                [
                    int(all(t or a == b for a, b, t in zip(x, out, s)))
                    * (-1) ** sum(t * a * b for t, a, b in zip(s, x, out))
                    for x in v
                ]
            )
            z.append(F(int(amp @ gram @ amp), int(norm) << sum(s)))
        assert sum(z) == 1 and min(z) >= 0
        key = "".join(map(str, s))
        p[key] = list(map(str, z))
        moments[key] = sum((-1) ** sum(o) * x for o, x in zip(v, z))
    t = sum(moments[s] for s in ["100", "010", "001"])
    minus = moments["111"] - t
    plus = moments["111"] + t
    return {
        "rows_lex_outcomes": p,
        "full_eight_moments": {k: str(w) for k, w in moments.items()},
        "signed_M_bound_two": str(minus),
        "all_plus_bound_four": str(plus),
        "literal_max_absolute_two_patterns": str(max(abs(minus), abs(plus))),
    }


def core_fixture(law):
    """First three unilateral children. x is spent, loose words comprise (p_i,q_i) at each."""
    old = bits(3)
    end = bits(6)
    allowed = as_array(
        [
            [
                int(
                    legal(x, law)
                    and all(legal((x[i], *y[2 * i : 2 * i + 2]), law) for i in range(3))
                )
                for y in end
            ]
            for x in old
        ]
    )
    assert all(c in (0, 1) for c in allowed.flat)
    ways = allowed.sum(axis=0)
    n, w = int(allowed.sum()), int(ways @ ways)
    unobserved = [1, 3, 5]
    all_gram = allowed.T @ allowed

    def trace_unmarked(g):
        reduced = np.zeros((8, 8), dtype=object)
        for i, a in enumerate(end):
            for j, b in enumerate(end):
                if all(a[k] == b[k] for k in unobserved):
                    reduced[
                        int("".join(map(str, a[::2])), 2),
                        int("".join(map(str, b[::2])), 2),
                    ] += g[i, j]
        return reduced

    raw = trace_unmarked(all_gram)
    cl = trace_unmarked(np.outer(ways, ways))
    # Compute every physical erasure character and verify the nonselective trace.
    collected = np.zeros((64, 64), dtype=object)
    branch = {}
    for h in old:
        signs = as_array([(-1) ** sum(i * j for i, j in zip(h, x)) for x in old])
        b = signs @ allowed
        collected += np.outer(b, b)
        branch["".join(map(str, h))] = {
            "signed_integer_end_amplitudes": list(map(int, b)),
            "probability": str(F(int(b @ b), 8 * n)),
        }
    assert np.array_equal(collected, 8 * all_gram)
    assert F(branch["000"]["probability"]) == F(w, 8 * n)
    # Retaining the old word leaves a genuine distinguishing record while the clean
    # character is selected. A one-bit tag gives an intermediate Gram matrix.
    partial = sum(
        (np.outer(a.sum(axis=0), a.sum(axis=0)) for a in [allowed[:4], allowed[4:]]),
        np.zeros((64, 64), dtype=object),
    )
    change_two = as_array([[int(j == (i ^ 6)) for j in range(8)] for i in range(8)])
    cross = {
        "changed_new_places": "p0,p1 on the first two child holdings; p2 unread",
        "retained_moment": str(F(int(np.trace(raw @ change_two)), int(np.trace(raw)))),
        "all_clean_moment": str(F(int(np.trace(cl @ change_two)), int(np.trace(cl)))),
    }
    return {
        "change_on_two_children": cross,
        "past_word_and_end_order": "lex; end p0,q0,p1,q1,p2,q2, reader p0,p1,p2",
        "ways": list(map(int, ways)),
        "integer_A_by_full_old_word": allowed.tolist(),
        "ways_and_heralds": clean_and_collision(ways, 3),
        "retained_averaged": prob_table(raw),
        "all_clean": prob_table(cl),
        "diagonal_counted": prob_table(np.diag(np.diag(raw))),
        "diagonal_squared": prob_table(np.diag(np.diag(cl))),
        "true_character_measured_but_all_outcomes_ignored": prob_table(
            trace_unmarked(collected)
        ),
        "tag_first_spent_bit_then_clean": prob_table(trace_unmarked(partial)),
        "tag_first_spent_bit_clean_chance": str(F(int(np.trace(partial)), 8 * n)),
        "tag_every_spent_bit_clean_chance": "1/8",
        "tag_every_spent_bit_then_clean_equals_retained": True,
        "coherent_uncompute_tag_then_clean_equals_all_clean": True,
        "all_character_branches": branch,
    }


def preserved_records():
    result = {}
    old, new = bits(3), bits(6)
    for law in ("parity", "nae"):
        a = [
            (
                x,
                as_array(
                    [
                        int(
                            all(
                                legal((x[i], *y[2 * i : 2 * i + 2]), law)
                                for i in range(3)
                            )
                        )
                        for y in new
                    ]
                ),
            )
            for x in old
            if legal(x, law)
        ]
        for label, sector in [
            ("whole_old_word", lambda x: x),
            ("pair_word", lambda x: x[:2]),
            ("equality_only", lambda x: (int(x[0] == x[1]),)),
            ("first_bit", lambda x: x[:1]),
            ("none", lambda x: ()),
        ]:
            groups = {}
            for x, vec in a:
                groups.setdefault(sector(x), []).append(vec)
            records = {}
            before = [len(group) for group in groups.values()]
            raw = [sum(map(sum, group)) for group in groups.values()]
            weights = [sum(k * k for k in sum(group)) for group in groups.values()]
            for (key, group), u, v, w in zip(groups.items(), before, raw, weights):
                records["".join(map(str, key))] = {
                    "old": str(F(u, sum(before))),
                    "ordinary_after": str(F(v, sum(raw))),
                    "clean_after": str(F(w, sum(weights))),
                    "new_char_zero_integer_end_amplitudes": list(map(int, sum(group))),
                }
            result[f"{law}/{label}"] = {
                "complete_record_chances": records,
                "extensions_each_allowed_full_old_word": [
                    int(sum(vec)) for x, vec in a
                ],
                "old_record_norm_total": sum(before),
                "new_clean_record_norm_total": int(sum(weights)),
                "clean_launch_with_record": str(F(sum(weights), 8 * sum(raw))),
            }
    result["abstract_equally_many_children_overlapping_rows"] = {
        "arithmetic_binary_B": [[1, 1, 0], [0, 1, 1]],
        "row_sums": [2, 2],
        "row_gram": [[2, 1], [1, 2]],
        "old_spectator_amplitudes": [[1, 1], [1, 0]],
        "old_norms": [2, 1],
        "new_norms": [6, 2],
        "old_first_chance": "2/3",
        "grown_first_chance": "3/4",
    }
    result["refusal_and_empty"] = {
        "binary_B": [[1], [0], [0]],
        "tags_for_refused_input": ["input-1", "input-2"],
        "uniform_input_granted": "1/3",
        "refused_individually": ["1/3", "1/3"],
        "zero_input_support": "no launch",
        "empty_coordinate_with_one_word": "1",
        "no_nonzero_selected_state": "undefined conditional",
    }
    return result


def interfaces():
    results = {}
    for law in ("parity", "nae"):
        partial = as_array(
            [[int(legal((*r, z), law)) for z in (0, 1)] for r in bits(2)]
        )
        child = as_array([[int(legal((z, *y), law)) for y in bits(2)] for z in (0, 1)])
        old = partial @ partial.T
        counted = partial @ np.diag(child.sum(axis=1)) @ partial.T
        later = partial @ child
        clean = later @ later.T

        def matrix(x):
            return [[str(F(v, int(np.trace(x)))) for v in row] for row in x]

        # A disjoint, closed two-holder companion contributes its own full-word count to each live word.
        close = sum(legal(w, law) for w in bits(3))
        assert matrix(counted) == matrix(old) and matrix(clean * close**2) == matrix(
            clean
        )
        results[law] = {
            "status": "One-interface attachment and closed companion are static controls, not an unscheduled partial ordinary round.",
            "old_rows": [[0, 1, 2]],
            "new_rows": [[0, 1, 2], [2, 3, 4]],
            "untouched_loose_names": [0, 1],
            "initial_reduced": matrix(old),
            "new_retained": matrix(counted),
            "new_clean": matrix(clean),
            "source_U_equal": str(F(old[0, 0] + old[3, 3], int(np.trace(old)))),
            "new_U_equal": str(
                F(counted[0, 0] + counted[3, 3], int(np.trace(counted)))
            ),
            "new_clean_equal": str(F(clean[0, 0] + clean[3, 3], int(np.trace(clean)))),
            "disjoint_closed_companion_rows": [[5, 6, 7], [5, 6, 7]],
            "closed_ordinary_scalar": close,
            "closed_squared_scalar": close**2,
            "old_local_law_U_and_Q_unchanged_by_disconnected_factor": True,
        }
    return results


def score_bounds():
    rows = []
    for assignments in bits(6):
        z0, x0, z1, x1, z2, x2 = [(-1) ** v for v in assignments]
        xxx = x0 * x1 * x2
        mix = x0 * z1 * z2 + z0 * x1 * z2 + z0 * z1 * x2
        rows.append([list(assignments), xxx - mix, xxx + mix])
    return {
        "all_64_local_deterministic_assignments": rows,
        "sharp_abs_minus": max(abs(j) for _, j, _ in rows),
        "sharp_abs_plus": max(abs(j) for _, _, j in rows),
    }


def observer_scope():
    """A complete local single-bit menu need not span every real joint effect."""
    identity = np.eye(2, dtype=int)
    x = as_array([[0, 1], [1, 0]])
    z = as_array([[1, 0], [0, -1]])
    j = as_array([[0, -1], [1, 0]])
    yy = -np.kron(j, j)
    i4 = np.eye(4, dtype=int)
    r, s = i4 + yy, i4 - yy
    assert np.array_equal(r @ r, 2 * r) and np.array_equal(s @ s, 2 * s)
    for a, b in product([identity, x, z], repeat=2):
        e = np.kron(a, b)
        assert np.trace(r @ e) == np.trace(s @ e)
    return {
        "states_numerators_over_four": [r.tolist(), s.tolist()],
        "local_menus_are_equal": True,
        "joint_real_YY_moments": [
            str(F(np.trace(r @ yy), 4)),
            str(F(np.trace(s @ yy), 4)),
        ],
        "status": "Abstract effect-span control; no such signed read is attributed to ordinary growth.",
    }


def parity_examples():
    return {
        "connected_open_parity": "If there are d twice-held names, h holders, and at least one loose name, each allowed loose word has 2^(d-h+1) spent completions. One compatible sign constraint applies to its loose parity.",
        "connected_closed_parity": "There is one empty loose word, with 2^(d-h+1) pasts when signed knot equations are consistent and zero otherwise.",
        "two_components_control": {
            "holders": [[0, 1, 2], [3, 4, 5]],
            "separate_even_conditions": ["012", "345"],
            "supported_six_bit_ends": sum(
                legal(a[:3], "parity") and legal(a[3:], "parity") for a in bits(6)
            ),
        },
        "one_loose_signed_abstract": {
            "holders": [[0, 1, 2], [0, 1]],
            "law": "even",
            "loose_bit": 2,
            "end_counts": [2, 0],
            "status": "Abstract incidence relation. The pinned bit in the first holding fails K2 and the second has only two places.",
        },
        "inconsistent_closed_signed_example": {
            "two_identical_holders": [[0, 1, 2], [0, 1, 2]],
            "parity_rhs": [0, 1],
            "empty_end_count": 0,
        },
        "closed_even_example": {
            "two_identical_holders": [[0, 1, 2], [0, 1, 2]],
            "parity_rhs": [0, 0],
            "empty_end_count": 4,
        },
    }
