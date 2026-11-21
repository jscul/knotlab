"""Exact Kraus, Choi and Schmidt certificates for the three actual closing questions."""

from collections import defaultdict
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ANCESTOR = ROOT / "research/TWO-READERS-ONE-SURVIVING-SIGN-20261121-001A"
sys.path.insert(0, str(ANCESTOR))
from instrument_math import (
    BASE,
    I,
    IX,
    J,
    X,
    Z,
    Mat,
    Catalogue,
    add,
    apply_channel,
    born,
    compose,
    effect,
    kraus_map,
    proportional,
    rank,
    ray,
    tensor,
    zero,
    IDENTITY_CHANNEL,
)
from instrument_hardware import _target as named_assignment

SIGNS = (1, -1)
BITS = (0, 1)
FINE = tuple(product(BITS, repeat=4))
WORDS = tuple(product(SIGNS, repeat=3))
XX = tensor(X, X)
ZZ = tensor(Z, Z)
YY = tensor(J, J).scale(-1)
OPS = (XX, ZZ, YY)
P1 = lambda op, t: (IX + op.scale(t)).scale(F(1, 2))
JOINT = {(x, z, y): P1(XX, x) @ P1(ZZ, z) @ P1(YY, y) for x, z, y in WORDS}
IDEAL = {k: kraus_map(p) for k, p in JOINT.items()}
BASIS = {
    (x, z): tuple((1, 0, 0, x) if z == 1 else (0, 1, x, 0))
    for x, z in product(SIGNS, repeat=2)
}
VALID = tuple(k for k, p in JOINT.items() if p.tr())


def key(entries):
    return ",".join(map(str, entries))


def signs(f):
    x = (-1) ** (f[0] + f[1])
    z = (-1) ** (f[2] + f[3])
    return (x, z, -x * z)


def make_inputs():
    out = {f"word_{i}{j}": tensor(BASE[i], BASE[j]) for i, j in product(BITS, repeat=2)}
    vectors = {}
    for k, v in BASIS.items():
        name = "joint_" + key(k)
        vectors[name] = np.asarray(v, dtype=int)
        out[name] = ray(v)
    for (n, u), (m, v) in combinations(vectors.items(), 2):
        for e in SIGNS:
            out[f"{n}_plus_{e}_{m}"] = ray(u + e * v)
    out["unequal_cross_sign"] = ray([1, 2, 3, -1])
    out["mixed_uniform"] = IX.scale(F(1, 4))
    out["mixed_ordinary"] = Mat(np.diag([1, 2, 3, 4]), 10)
    return out


def algebra(cat):
    t = named_assignment()
    got = {
        r["physical_names"][0]: Mat(r["two_word_slots_matrix"])
        for r in t["independent_four_by_four_routes"]
        if r["column_holder"] == 17
    }
    assert [got[n] for n in (28, 29, 30)] == list(OPS)
    assert XX @ ZZ @ YY == IX.scale(-1)
    assert all(a @ b == b @ a for a, b in combinations(OPS, 2))
    assert add(JOINT.values(), 4) == IX
    rows = {}
    for k, p in JOINT.items():
        assert p @ p == p and p == p.T
        expected = ray(BASIS[k[:2]]) if k[2] == -k[0] * k[1] else zero(4)
        assert p == expected
        rows[key(k)] = {
            "projector": cat.put(p),
            "rank": rank(p.key()),
            "choi": cat.put(IDEAL[k]),
            "eigenvector_integer": BASIS[k[:2]] if p.tr() else None,
        }
    return {
        "actual_target": t,
        "three_named_matrices": {
            str(i): cat.put(m) for i, m in zip((28, 29, 30), OPS, strict=True)
        },
        "all_eight_including_impossible": rows,
        "product": cat.put(XX @ ZZ @ YY),
    }


def projectors_program(
    f,
    *,
    source=(1, 1),
    active=(True, True, True, True),
    reversed_order=(False, False),
    frames=(I, I),
):
    """Four coherent route contributions before final sum over meter controls."""
    x, z, _ = signs(f)
    terms = {}
    for u, v in product(BITS, repeat=2):
        sites = []
        for site, frame in enumerate(frames):
            a = frame @ X @ frame.T if u and active[site] else I
            b = frame @ Z @ frame.T if v and active[2 + site] else I
            sites.append(a @ b if reversed_order[site] else b @ a)
        terms[(u, v)] = tensor(*sites).scale(
            (x * source[0]) ** u * (z * source[1]) ** v
        )
    return terms


def program(
    *,
    source=(1, 1),
    active=(True, True, True, True),
    reversed_order=(False, False),
    frames=(I, I),
    tags=(False, False),
):
    channels = {}
    fine_arms = {}
    for f in FINE:
        groups = defaultdict(list)
        for uv, mat in projectors_program(
            f,
            source=source,
            active=active,
            reversed_order=reversed_order,
            frames=frames,
        ).items():
            h = tuple(a if on else "*" for a, on in zip(uv, tags, strict=True))
            groups[h].append(mat)
        k = {h: add(mats, 4) for h, mats in groups.items()}
        channels[f] = add([kraus_map(m, 64) for m in k.values()], 16)
        fine_arms[f] = k
    assert add([effect(v) for v in channels.values()], 4) == IX
    return channels, fine_arms


def pack_ch(cat, c, full=False):
    if not full:
        return cat.put(c)
    e = effect(c)
    return {
        "unnormalized_choi": cat.put(c),
        "effect": cat.put(e),
        "normalized_local_probe_suboutput": cat.put(c.scale(F(1, 4))),
        "rank": rank(c.key()),
        "matches_ideal": {key(k): proportional(c, IDEAL[k]) for k in VALID},
    }


def graded(ch, cat, full=False):
    co = {k: add([v for f, v in ch.items() if signs(f) == k], 16) for k in WORDS}
    ret = {
        "four_raw_bits_in_order_A28_B28_A29_B29": {
            key(f): pack_ch(cat, v, full) for f, v in ch.items()
        },
        "decoded_xyz": {key(k): pack_ch(cat, v, full) for k, v in co.items()},
    }
    if full:
        datasets = {}
        for s, rho in make_inputs().items():
            rows = {}
            for k, m in co.items():
                mat = apply_channel(m, rho)
                p = mat.tr()
                rows[key(k)] = {
                    "p": str(p),
                    "subnormalized_data": cat.put(mat),
                    "conditional_data": cat.put(mat.scale(1 / p)) if p else None,
                }
            assert sum(F(info["p"]) for info in rows.values()) == 1
            datasets[s] = rows
        ret["registered_ordinary_coherent_mixed_inputs"] = datasets
        ret["fine_physical_probabilities_by_input"] = {
            s: {key(f): str(born(rho, effect(m))) for f, m in ch.items()}
            for s, rho in make_inputs().items()
        }
    return ret, co


def fine_routes(mats, cat):
    return {
        key(f): {key(k): cat.put(m) for k, m in row.items()} for f, row in mats.items()
    }


def two_pairs(cat):
    correct, arms = program()
    main, co = graded(correct, cat, True)
    for f, ch in correct.items():
        assert arms[f]["*", "*"] == JOINT[signs(f)].scale(4)
        assert ch == IDEAL[signs(f)].scale(F(1, 4))
    assert all(co[k] == IDEAL[k] for k in WORDS)
    margins = {}
    for a in product(BITS, repeat=2):
        for site in (0, 1):
            selected = add(
                [
                    effect(ch)
                    for f, ch in correct.items()
                    if (f[site], f[site + 2]) == a
                ],
                4,
            )
            assert selected == IX.scale(F(1, 4))
            margins[f"{site}/{key(a)}"] = cat.put(selected)
    main["local_record_effects_before_disclosure"] = margins
    main["raw_amplitude_numerators_with_denominator_8"] = fine_routes(arms, cat)
    variants = {}
    for order in product((False, True), repeat=2):
        ch, a = program(reversed_order=order)
        if order[0] == order[1]:
            assert ch == correct
        else:
            assert all(effect(v) == IX.scale(F(1, 16)) for v in ch.values())
        out, _ = graded(ch, cat)
        out["amplitude_numerators_over_8"] = fine_routes(a, cat)
        variants["local_reverse_order_" + key(order)] = out
    for active in product((False, True), repeat=4):
        ch, _ = program(active=active)
        variants["connected_local_controls_" + key(active)] = graded(ch, cat)[0]
    for tx, tz in product((False, True), repeat=2):
        ch, a = program(tags=(tx, tz))
        out, _ = graded(ch, cat)
        out["physical_tag_gram_recipe"] = (
            "For tag h,k the complete retained output block at this fine port is K_h rho K_k^T/64; resolving the ordinary tag retains its diagonal blocks. Coherently uncompute prior to analyzing meters to sum all K_h before squaring."
        )
        out["K_h"] = fine_routes(a, cat)
        for f in FINE:
            assert add(a[f].values(), 4) == arms[f]["*", "*"]
        variants["kept_tag_" + key((tx, tz))] = out
    for fa, fb in product(BITS, repeat=2):
        wA = (I, X)[fa]
        wB = (I, X)[fb]
        w = tensor(wA, wB)
        ch, a = program(frames=(wA, wB))
        for f, m in ch.items():
            assert m == kraus_map(w @ JOINT[signs(f)] @ w.T, 4)
        variants["passive_independent_frames_" + key((fa, fb))] = graded(ch, cat)[0]
    return main, variants, correct


def destructive(cat):
    fine = {}
    clean = {}
    for f in FINE:
        i, k, u, v = f
        x = (-1) ** (i + k)
        z = (-1) ** (u + v)
        fixed = tensor(BASE[u], BASE[v])
        num = fixed @ (IX + XX.scale(x))
        c = kraus_map(num, 8)
        t = (x, z, -x * z)
        assert effect(c) == JOINT[t].scale(F(1, 4))
        assert c == tensor(JOINT[t], fixed).scale(F(1, 4))
        fine[f] = c
        clean[key(f)] = cat.put(num)
    report, co = graded(fine, cat, True)
    for t in VALID:
        assert effect(co[t]) == JOINT[t]
        out = apply_channel(co[t], JOINT[t])
        assert born(out, JOINT[t]) == F(1, 2)
    report["numerators_over_sqrt8"] = clean
    report["one_pair_first_XX_then_two_basis_measurements"] = (
        "Time order in the four-bit keys is A28,B28,ordinary target A/B values. Record aggregates by the parity of each pair, the gate input data are now |uv>."
    )
    return report, fine, co


def direct_third(cat, first):
    answer = {}
    for coupling, display in product(SIGNS, repeat=2):
        rows = {}
        for f, prior in first.items():
            t = signs(f)
            for i, k in product(BITS, repeat=2):
                raw = (-1) ** (i + k)
                next_op = P1(YY, coupling * raw)
                ch = compose(kraus_map(next_op, 2), prior)
                expect = prior.scale(F(1, 2)) if coupling * raw == t[2] else zero(16)
                assert ch == expect
                rows[key((*f, i, k))] = {
                    "data_choi": cat.put(ch),
                    "physical_direct_sign": raw,
                    "inferred_sign": t[2],
                    "displayed_direct_sign": display * raw,
                    "raw_and_reported_match": raw == t[2],
                    "final_display_agrees": display * raw == t[2],
                }
        answer[f"coupling_{coupling}/display_{display}"] = rows
    return answer


def repeat(cat, ideal, destructive):
    result = {}
    for name, first, second in [
        ("two_then_two", ideal, ideal),
        ("one_then_two", destructive, ideal),
        ("one_then_one", destructive, destructive),
        ("two_then_one", ideal, destructive),
    ]:
        records = {}
        total_equal = zero(4)
        for f, g in product(FINE, repeat=2):
            c = compose(second[g], first[f])
            if signs(f) == signs(g):
                total_equal = total_equal + effect(c)
            records[key(f) + "/" + key(g)] = cat.put(c)
        want = IX.scale(F(1, 2)) if name.startswith("one") else IX
        assert total_equal == want
        result[name] = {
            "all_256_fine_choi": records,
            "same_triple_effect": cat.put(total_equal),
            "same_triple_rate": str(F(1, 2) if name.startswith("one") else F(1)),
        }
    return result
