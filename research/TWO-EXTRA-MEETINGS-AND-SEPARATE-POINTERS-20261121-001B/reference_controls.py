"""Exact access controls for disclosing a reference, reunion and repeated preparations."""

from itertools import product, combinations
import numpy as np
from real_algebra import (
    F,
    Mat,
    C,
    D,
    P,
    MEAS,
    R,
    ray,
    identity,
    zero,
    powers,
    group,
    instrument,
    tensor,
    add,
    normalize,
    partial_b,
    real_charge,
    perm_image,
    born,
)


SIGNS = tuple(product((1, -1), repeat=2))
MODES = ("equal", "opposite", "independent")


def draw(mode):
    choices = [
        (a, b)
        for a, b in SIGNS
        if mode == "independent" or (a * b == 1) == (mode == "equal")
    ]
    return {signs: F(1, len(choices)) for signs in choices}


def product_draw(first, second):
    return {
        u + v: p * q for u, p in draw(first).items() for v, q in draw(second).items()
    }


def repeated_draw(mode, persistent):
    if persistent:
        return {(a, b, a, b): p for (a, b), p in draw(mode).items()}
    return product_draw(mode, mode)


def report_read(orb):
    """Modulus squared of each Kraus polynomial at omega^orb, without complex rounding."""
    coeffs = ((1, 1, 1), (1, -1, 0), (1, 1, -2))
    den = (9, 6, 18)
    out = []
    for coeff, n in zip(coeffs, den):
        t = [0] * 3
        for i, v in enumerate(coeff):
            t[(orb * i) % 3] += v
        # Norm of x+y omega+z omega^2 in the cubic-root basis.
        out.append(
            F(sum(x * x for x in t) - t[0] * t[1] - t[1] * t[2] - t[2] * t[0], n)
        )
    assert sum(out) == 1
    return out


def four_table(
    source, *, target_signs=(1, 1), ref_signs=(1, 1), comparator=(1, 1), launch=F(1, 64)
):
    # The sampled labels are an exact spectral representation, not a label sent to the apparatus.
    out = {word: {} for word in product(range(3), repeat=2)}
    for (a, b, c, d), weight in source.items():
        signs = (
            a * target_signs[0],
            b * target_signs[1],
            c * ref_signs[0],
            d * ref_signs[1],
        )
        v = report_read(comparator[0] * (signs[0] + signs[2]))
        w = report_read(comparator[1] * (signs[1] + signs[3]))
        for i, j in out:
            # Retain full conditional spectral mixture. Each Kraus is scalar on this product ray.
            if v[i] * w[j]:
                out[i, j][(a, b, c, d)] = weight * v[i] * w[j]
    table = {
        f"{i}{j}": {
            "conditional_on_source_admission": str(sum(row.values(), F(0))),
            "per_whole_preparation_and_comparison_request": str(
                sum(row.values(), F(0)) * launch
            ),
            "poststate_unnormalized_spectral_weights": {
                str(k): str(v) for k, v in row.items()
            },
        }
        for (i, j), row in out.items()
    }
    assert sum(F(v["conditional_on_source_admission"]) for v in table.values()) == 1
    return table


def overview(table):
    p = {s: F(v["conditional_on_source_admission"]) for s, v in table.items()}
    return {
        "zero_port_on_both": str(p["00"]),
        "either_at_zero": str(sum(v for k, v in p.items() if "0" in k)),
        "agreement_of_two_ordinary_predicates_port_is_0": str(
            sum(v for k, v in p.items() if (k[0] == "0") == (k[1] == "0"))
        ),
    }


def basis_density_complex_product_real(s):
    # A single complex one-pointer density is (P - i*s*D/sqrt(3))/2.
    # Four pure factors have a rational real part after collecting even powers of i.
    out = zero(81)
    for k in (0, 2, 4):
        for positions in combinations(range(4), k):
            sign = (-1) ** (k // 2)
            for idx in positions:
                sign *= s[idx]
            factors = [D if i in positions else P for i in range(4)]
            out = out + tensor(*factors).scale(F(sign, 16 * 3 ** (k // 2)))
    return out


def direct_four_effects():
    # Direct independent effect calculation in the 81-dimensional four-register word basis.
    # Initial ordering A0,B0,A1,B1; transform to local A0,A1,B0,B1 and read.
    g = tensor(C, C)
    effects = [(k.T @ k).scale(F(1, n)) for k, n in group(g)]
    reverse = []
    for e, f in product(effects, repeat=2):
        local = tensor(e, f)
        reversed_array = (
            local.a.reshape((3,) * 8).transpose(0, 2, 1, 3, 4, 6, 5, 7).reshape(81, 81)
        )
        reverse.append(Mat(reversed_array, local.d))
    raw = {s: basis_density_complex_product_real(s) for s in product((1, -1), repeat=4)}
    direct = {}
    for s, m in raw.items():
        probs = [born(m, e) for e in reverse]
        formula = [
            F(v["conditional_on_source_admission"])
            for v in four_table({s: F(1)}).values()
        ]
        assert probs == formula and sum(probs) == 1
        direct[str(s)] = list(map(str, probs))
    return direct


def group_tables(cat):
    g = tensor(C, C)
    directions = {
        "same_native_word_orientation": g,
        "second_physically_reversed": tensor(C, C.T),
    }
    rows = {}
    source = {
        mode: add([real_charge(a, b).scale(w) for (a, b), w in draw(mode).items()], 9)
        for mode in MODES
    }
    states = {**source, "raw_private_minus_pair": tensor(ray(R), ray(R))}
    for name, rho in states.items():
        probes = {}
        for oriented, un in directions.items():
            ops = group(un)
            writes = []
            for m in instrument(rho, ops):
                writes.append(
                    {
                        "p": str(m.tr()),
                        "raw": cat.put(m),
                        "conditional": cat.put(normalize(m)) if m.tr() else None,
                    }
                )
            assert sum(F(j["p"]) for j in writes) == 1
            probes[oriented] = writes
        rows[name] = probes
    tag = {}
    a = states["raw_private_minus_pair"]
    ints = lambda vals, n: add(vals, n)
    # Full 3x3 tag block before discarding an orthogonal copy. The clean history is their sum.
    coeff = ((1, 1, 1), (1, -1, 0), (1, 1, -2))
    den = (9, 6, 18)
    for key, un in directions.items():
        ps = powers(un)
        by = {}
        for j, (coef, q) in enumerate(zip(coeff, den)):
            allblocks = [
                [
                    ((l @ a @ r.T).scale(F(coef[k] * coef[h], q)))
                    for h, r in enumerate(ps)
                ]
                for k, l in enumerate(ps)
            ]
            hidden = ints([allblocks[k][k] for k in range(3)], 9)
            clean = ints([m for row in allblocks for m in row], 9)
            assert clean == instrument(a, group(un))[j]
            by[str(j)] = {
                "kept_tag_blocks": [[cat.put(b) for b in row] for row in allblocks],
                "ignored_tag": {"p": str(hidden.tr()), "joint": cat.put(hidden)},
                "physically_returned_or_never_coupled": {
                    "p": str(clean.tr()),
                    "joint": cat.put(clean),
                },
            }
        assert sum(F(v["ignored_tag"]["p"]) for v in by.values()) == 1
        tag[key] = by
    return {
        "complete_global_before_cut_or_after_reunion": rows,
        "group_source_path_keeper_untouched_retained_returned": tag,
    }


def singleton_and_idle():
    c4 = perm_image((1, 2, 0, 3))
    ground = {}
    for i, j in product(range(4), repeat=2):
        v = [int(k == 4 * i + j) for k in range(16)]
        single = ray(v)
        ground[f"{i}{j}"] = {}
        for first, second in (
            (c4, c4),
            (c4, c4.T),
            (c4, identity(4)),
            (identity(4), c4),
            (identity(4), identity(4)),
        ):
            test = tensor(first, second)
            ms = instrument(single, group(test))
            assert sum(x.tr() for x in ms) == 1
            ground[f"{i}{j}"][str((first.key(), second.key()))] = [
                {"p": str(x.tr()), "post_ordinary_subnormal": x.diag()} for x in ms
            ]
    real_bases = {
        "word": [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)],
        "ab": [(1, 1, 0, 0), (1, -1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)],
        "hrs": [(1, 1, 1, 0), (1, -1, 0, 0), (1, 1, -2, 0), (0, 0, 0, 1)],
    }
    singles = {}
    for name, words in real_bases.items():
        es = [ray(w) for w in words]
        assert add(es, 4) == identity(4)
        singles[name] = [[str(F(e.a[k, k], e.d)) for e in es] for k in range(4)]
    return {
        "address_effect_probabilities": singles,
        "group_ports_including_idle_d_every_singleton_and_missing_offer": ground,
    }


def reference_controls(cat):
    tables = {}
    for first, second in product(MODES, repeat=2):
        key = f"target_{first}/reference_{second}"
        src = product_draw(first, second)
        table = four_table(src)
        passive = {}
        for s, t in product((1, -1), repeat=2):
            p = four_table(
                src, target_signs=(s, t), ref_signs=(s, t), comparator=(s, t)
            )
            assert p == table
            passive[f"{s}/{t}"] = (
                "all ordinary port and spectral poststate entries identical in transported coordinates"
            )
        physical = four_table(src, target_signs=(1, -1))
        tables[key] = {
            "unshifted": table,
            "independent_passive_frame_reversal": passive,
            "fixed_reference_reverse_target_B": physical,
            "unshifted_summary": overview(table),
            "physical_reversal_summary": overview(physical),
        }
    assert (
        overview(tables["target_equal/reference_equal"]["unshifted"])[
            "agreement_of_two_ordinary_predicates_port_is_0"
        ]
        == "1"
    )
    assert (
        overview(tables["target_opposite/reference_equal"]["unshifted"])[
            "agreement_of_two_ordinary_predicates_port_is_0"
        ]
        == "0"
    )
    repeats = {}
    for mode, carry in product(MODES, (False, True)):
        start = product_draw(mode, mode)
        if carry:
            # Reuse the enrolled real three-port comparison at the bench before separation.
            # Both zero ports of inverse-comparison select the same actual local charge
            # on the two copies, without determining what that charge was.
            prep = four_table(start, ref_signs=(-1, -1))
            keep = F(prep["00"]["conditional_on_source_admission"])
            select = {
                s: w / keep for s, w in start.items() if s[0] == s[2] and s[1] == s[3]
            }
            assert select == repeated_draw(mode, True)
        else:
            prep = None
            keep = F(1)
        table = four_table(repeated_draw(mode, carry), launch=keep / 64)
        repeats[f"{mode}/" + ("same_hidden_draw" if carry else "fresh_hidden_draw")] = {
            "table": table,
            "summary": overview(table),
            "full_preparation_admission": str(keep / 64),
            "all_bench_persistence_filter_ports_on_two_admitted_inputs": prep,
            "persistence_filter": "Before separation two inverse comparisons select 00. All other bench ports are retained and give no local delivery."
            if carry
            else "No further preparation filter.",
        }
    for tag in ("same_hidden_draw", "fresh_hidden_draw"):
        e = repeats["equal/" + tag]["table"]
        o = repeats["opposite/" + tag]["table"]
        assert [u["conditional_on_source_admission"] for u in e.values()] == [
            u["conditional_on_source_admission"] for u in o.values()
        ]
    source_opps = {
        "source_00": "1/4",
        "source_01": "1/4",
        "source_10": "1/4",
        "group_1": "1/16",
        "group_2": "1/16",
        "admitted": "1/8",
    }
    four_launches = {
        f"{one}/{two}": str(F(u) * F(v))
        for one, u in source_opps.items()
        for two, v in source_opps.items()
    }
    assert sum(F(v) for v in four_launches.values()) == 1
    return {
        "reunion_and_source_tags": group_tables(cat),
        "known_real_distributed_reference": tables,
        "two_target_copies": repeats,
        "whole_launch_source_ports": four_launches,
        "whole_launch_note": "Two distinct, independently heralded source programs. Every ordinary comparison is made when both admissions are present. Any other admitted wing's local pointer is kept at the bench for this joint comparison; refusals write no result. The two independent base programs give admission 1/64. For the persistent-draw control only, the real two-site persistence filters at the bench contribute the additionally reported ports and acceptance. Each local zero test compares the two copies with one cycle reversed before their separation.",
        "exact_81_word_direct_effect_crosscheck": direct_four_effects(),
        "group_and_all_singleton_controls": singleton_and_idle(),
    }


def ancillary_access(cat):
    # Reverse B's target and reference indices separately before regrouping the two local labs.
    delta = real_charge(1, 1) - real_charge(1, -1)
    assert partial_b(delta, 3, 3) == delta.scale(-1)
    ans = {}
    mtx = {
        mode: add([real_charge(a, b).scale(w) for (a, b), w in draw(mode).items()], 9)
        for mode in MODES
    }
    mtx["classically_shared_a_or_b"] = (
        tensor(MEAS["word"][0], MEAS["word"][0])
        + tensor(MEAS["word"][1], MEAS["word"][1])
    ).scale(F(1, 2))
    vec = [1 if j in (0, 4) else 0 for j in range(9)]
    mtx["real_coherent_aa_bb"] = ray(vec)
    for name, sigma in mtx.items():
        ds = tensor(delta, sigma)
        regroup = lambda m: Mat(
            m.a.reshape((3,) * 8).transpose(0, 2, 1, 3, 4, 6, 5, 7).reshape((81, 81)),
            m.d,
        )
        obs = (regroup(ds) + partial_b(regroup(ds), 9, 9)).scale(F(1, 2))
        anc = (sigma - partial_b(sigma, 3, 3)).scale(F(1, 2))
        assert obs == regroup(tensor(delta, anc))
        dist = bool(np.any(obs.a))
        if dist:
            # The elementary real skew forms supply a concrete pair of local positive tests.
            block = []
            for a, b in combinations(range(3), 2):
                u = np.zeros((3, 3), int)
                u[a, b] = 1
                u[b, a] = -1
                block.append(Mat(u))
            found = None
            for u, v in product(block, repeat=2):
                k1 = tensor(D, u)
                k2 = tensor(D, v)
                # ||D||=sqrt(3), ||u||=1. The half-scaled controls are contractions.
                e1 = (identity(9) + k1.scale(F(1, 2))).scale(F(1, 2))
                e2 = (identity(9) + k2.scale(F(1, 2))).scale(F(1, 2))
                diff = born(obs, tensor(e1, e2))
                if diff:
                    found = [cat.put(e1), cat.put(e2), str(diff)]
                    break
            assert found
        else:
            found = None
        ans[name] = {
            "symmetric_under_B_transposition": anc == zero(9),
            "real_local_separation": dist,
            "pointer_reference_reordered_hidden_coordinate_l1": str(
                F(sum(abs(x) for x in obs.a.flat), obs.d)
            ),
            "explicit_real_effect_ids_and_probability_difference_if_available": found,
        }
    return ans
