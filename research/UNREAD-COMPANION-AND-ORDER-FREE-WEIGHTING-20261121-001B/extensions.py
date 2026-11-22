"""Exact old weights, stepwise histories, and a direct four-state physical transfer."""

from fractions import Fraction as F
from itertools import product
import numpy as np


def kernel(prior, children):
    """Every actual child inherits its conditional share. Retain refused mass explicitly."""
    assert sum(prior.values()) in (0, 1)
    assert all(len(v) == len(set(v)) for v in children.values())
    keep = {}
    denial = F()
    for o, v in prior.items():
        if not children.get(o):
            denial += v
            continue
        for x in children[o]:
            keep[x] = keep.get(x, F()) + F(v, len(children[o]))
    return keep, denial


def text(dist):
    return {k: str(v) for k, v in dist.items()}


def single_checks():
    examples = {
        "empty_both": ({}, {}),
        "none_extend": ({"0": F(1, 2), "1": F(1, 2)}, {}),
        "uniform_but_lost_affine_old_word": (
            {"0": F(1, 2), "1": F(1, 2)},
            {"0": ["00", "01"]},
        ),
        "zero_prior_on_lost_affine_word": ({"0": F(1), "1": F(0)}, {"0": ["00", "01"]}),
        "unequal_full_fibres_uniform_old": (
            {"0": F(1, 2), "1": F(1, 2)},
            {"0": ["00"], "1": ["10", "11"]},
        ),
        "unequal_fibres_repaired_prior": (
            {"0": F(1, 3), "1": F(2, 3)},
            {"0": ["00"], "1": ["10", "11"]},
        ),
        "biased_prior_on_flat_affine_fibres": (
            {"0": F(3, 4), "1": F(1, 4)},
            {"0": ["00", "01"], "1": ["10", "11"]},
        ),
        "nonlinear_extension_full_and_flat": (
            {w: F(1, 4) for w in ("00", "01", "10", "11")},
            {w: [w + str(int(w == "11"))] for w in ("00", "01", "10", "11")},
        ),
        "zero_coordinates_live_relation": ({"": F(1)}, {"": ["0", "1"]}),
    }
    out = {}
    for name, (prior, children) in examples.items():
        u, denied = kernel(prior, children)
        targets = sorted({j for lst in children.values() for j in lst})
        if targets:
            assert sum(len(ch) for ch in children.values()) == len(targets)
            uniform = {v: F(1, len(targets)) for v in targets}
            marginal = {
                old: F(len(children.get(old, [])), len(targets)) for old in prior
            }
        else:
            uniform, marginal = None, None
        normalized = (
            {v: w / sum(u.values()) for v, w in u.items()} if sum(u.values()) else None
        )
        assert sum(u.values()) + denied == sum(prior.values())
        out[name] = {
            "original_prior": text(prior),
            "children": children,
            "fresh_uniform": text(uniform) if uniform else None,
            "old_law_of_uniform_new": text(marginal) if marginal else None,
            "equal_child_subprobability": text(u),
            "unconditional_denied": str(denied),
            "conditional_after_selecting_survivors": text(normalized)
            if normalized
            else None,
            "equals_uniform_without_postselection": bool(uniform) and u == uniform,
            "recovers_prior_unchanged_without_rejection": bool(prior) and denied == 0,
        }
    return out


def history_checks():
    old = {"u": F(1, 2), "v": F(1, 2)}
    branches = {"u": ["a", "b"], "v": ["c"]}
    middle, missing = kernel(old, branches)
    assert not missing
    examples = {
        "same_old_final_counts_unequal_path_probabilities": (1, 3, 4),
        "nonuniform_intermediate_but_uniform_final": (1, 1, 2),
        "different_total_descendants_per_old": (1, 2, 2),
    }
    out = {}
    for name, sizes in examples.items():
        young = {h: [h + str(i) for i in range(n)] for h, n in zip("abc", sizes)}
        final, missing = kernel(middle, young)
        assert not missing
        direct = {
            o: [g for h in mids for g in young[h]] for o, mids in branches.items()
        }
        one_lift, missing = kernel(old, direct)
        assert not missing
        global_measure = {g: F(1, len(final)) for g in final}
        out[name] = {
            "initial": text(old),
            "middle_children": branches,
            "terminal_children": young,
            "middle_stepwise": text(middle),
            "final_stepwise": text(final),
            "one_direct_equal_division": text(one_lift),
            "uniform_final": text(global_measure),
            "restriction_of_uniform_final_to_old": {
                o: str(sum(global_measure[g] for g in gs)) for o, gs in direct.items()
            },
            "products_of_degrees": {
                g: len(mids) * len(young[h])
                for o, mids in branches.items()
                for h in mids
                for g in young[h]
            },
        }
    first = {"r": F(1)}
    one = {"r": ["a", "b"]}
    two = {"a": ["u"], "b": ["u", "v"]}
    mid, _ = kernel(first, one)
    merged, _ = kernel(mid, two)
    assert merged == {"u": F(3, 4), "v": F(1, 4)}
    out["coarsened_terminals_two_histories_to_one_endpoint"] = {
        "initial": text(first),
        "first": one,
        "second": two,
        "retain_histories_and_equal_split_per_step": {
            "rau": "1/2",
            "rbu": "1/4",
            "rbv": "1/4",
        },
        "merge_after_stepwise_division": text(merged),
        "uniform_fine_histories_pushed_down": {"u": "2/3", "v": "1/3"},
        "uniform_terminal_labels": {"u": "1/2", "v": "1/2"},
        "why_different": "After omitting history, a reported terminal u no longer determines the intermediate coordinate.",
    }
    assert (
        out["same_old_final_counts_unequal_path_probabilities"]["final_stepwise"]
        != out["same_old_final_counts_unequal_path_probabilities"][
            "one_direct_equal_division"
        ]
    )
    assert (
        out["nonuniform_intermediate_but_uniform_final"]["final_stepwise"]
        == out["nonuniform_intermediate_but_uniform_final"]["uniform_final"]
    )
    return out


def transfer_checks():
    """Two doubly shared names at each meeting on the spent-witness cycle.

    These exact tables use ordinary Boolean counts on the stated physical topology.
    Their independent comparison to actual reached rosters is made by replay.py.
    """
    pairs = list(product((0, 1), repeat=2))
    boundary = [
        np.array(
            [[int(len(set((s, *u, *v))) > 1) for v in pairs] for u in pairs],
            dtype=object,
        )
        for s in (0, 1)
    ]
    trans = np.array(
        [[int(len(set((*u, *v))) > 1) for v in pairs] for u in pairs], dtype=object
    )
    mark = np.diag([1, 0, 0, 1]).astype(object)
    out = {}
    for k in (1, 2, 3):
        H = np.linalg.matrix_power(trans, k)
        totals, event = {}, {}
        for s, t in product((0, 1), repeat=2):
            tail = boundary[t] @ trans @ boundary[s]
            totals[s, t] = int(np.trace(H @ H @ tail))
            event[s, t] = int(np.trace(H @ mark @ H @ tail))
        z, z_e = sum(totals.values()), sum(event.values())
        n = sum((2 - int(s == t)) * v for (s, t), v in totals.items())
        n_e = sum((2 - int(s == t)) * v for (s, t), v in event.items())
        before, after = F(z_e, z), F(n_e, n)
        T = np.array([[1, 2], [2, 2]], dtype=object)
        small = np.linalg.matrix_power(T, k)
        a, b = small[0, :]
        changed_numer = 8 * (
            2 * (-2) ** k * (7 * a * a + 16 * a * b + 7 * b * b)
            - (2 * a + 3 * b) * (7 * a + 9 * b)
        )
        corr = sum((-1) ** (s + t) * v for (s, t), v in totals.items())
        corr_e = sum((-1) ** (s + t) * v for (s, t), v in event.items())
        assert changed_numer == z_e * corr - z * corr_e == 2 * (n_e * z - z_e * n)
        assert (-1) ** k * (after - before) > 0
        out[str(2 * k)] = {
            "end_names_zero_one_counts": {
                "".join(map(str, st)): {
                    "old_total": val,
                    "event_old": event[st],
                    "NAE_fresh_ways": 2 - int(st[0] == st[1]),
                }
                for st, val in totals.items()
            },
            "old_total": z,
            "old_event": z_e,
            "new_total": n,
            "new_event": n_e,
            "old_U": str(before),
            "new_U": str(after),
            "transported_L": str(before),
            "signed_change": str(after - before),
            "distance_in_holder_meetings": k + 1,
            "numerator_test": str(changed_numer),
        }
    return {
        "pair_order": ["00", "01", "10", "11"],
        "internal_NAE_transfer": trans.tolist(),
        "fixed_old_bit_endpoint_matrices": [q.tolist() for q in boundary],
        "marked_link_equality_diagonal": [1, 0, 0, 1],
        "repaired_family": out,
    }
