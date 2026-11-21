"""The archived native motion, October contraction, and actual complete-word keeper."""

from collections import Counter
from functools import lru_cache
from itertools import product
from pathlib import Path
import gzip
import json
import os
import subprocess
import sys

from knot_counts import FIXTURES, coeffs, field

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FREEDOM = (
    ROOT
    / "experiments/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A-E001_freedom"
)
B287 = ROOT / "research/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001A"


def canonical_checks():
    result = {}
    for m, law in product(range(2, 9), ("parity", "nae")):
        bits = [f"b_{j}" for j in range(m)]
        expected = {
            x
            for x in range(1 << m)
            if ((x.bit_count() % 2 == 0) if law == "parity" else 0 < x.bit_count() < m)
        }
        chunks = [
            " ".join(("~" if x >> i & 1 else "") + b for i, b in enumerate(bits))
            for x in range(1 << m)
            if x not in expected
        ]
        cmd = [
            sys.executable,
            "-B",
            "-m",
            "knotlab",
            "check",
            "--cnf",
            ";".join(chunks),
            "--loops",
            *bits[:-1],
            "--contact",
            bits[-1],
            "--json",
        ]
        done = subprocess.run(
            cmd,
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT / "tools")},
            capture_output=True,
            text=True,
        )
        if m == 2:
            assert done.returncode and "at least two loops" in done.stderr
            result[f"{m}/{law}"] = {
                "projection_test_passes": True,
                "canonical_refusal": done.stderr.strip(),
            }
            continue
        assert done.returncode == 0, done.stderr
        r = json.loads(done.stdout)
        assert r["is_knot"]
        assert len(r["allowed"]) == len(expected)
        result[f"{m}/{law}"] = r
    return result


def growth_checks():
    if str(FREEDOM) not in sys.path:
        sys.path.insert(0, str(FREEDOM))
    import ordinary

    original_ids = FREEDOM.parent.name, FREEDOM.name
    archived_sources = ROOT / "artifacts" / original_ids[0] / original_ids[1] / "histories.json.gz"
    archive = json.loads(gzip.decompress(archived_sources.read_bytes()))
    hosts = {case["label"]: case["stages"][0] for case in archive["cases"] if case["mode"] == "host"}
    assert len(hosts) == 2
    try:
        generated = ordinary.hosted()
    except ModuleNotFoundError as error:
        # The public edition omits an unrelated batch-launch service imported by
        # the old generator. Its authenticated physical input words are published.
        if error.name != "longrun":raise
    else:
        assert {k:[list(row) for row in val] for k,val in generated.items()} == hosts
    stages = {
        "single_3": [[0, 1, 2]],
        "single_4": [[0, 1, 2, 3]],
        "two_ternary": [[0, 1, 2], [0, 3, 4]],
        "three_parent": [[0, 1, 3], [0, 2, 4], [1, 2, 5]],
        **hosts,
    }
    out = {}
    for key, stars in stages.items():
        for law in ("parity", "nae"):
            log, after = ordinary.advance(stars, law)
            n = max(map(max, stars)) + 1
            trial = {
                "initial": stars,
                "step": log,
                "next_holdings": after,
                "four_source_descriptions_share_this_actual_structural_offer": [
                    "positive_uniform",
                    "magnitude",
                    "oriented_product",
                    "conjugate_product",
                ],
            }
            if after is None:
                trial["completion_comparison"] = "No new stage from this offer."
            elif (m := max(map(max, after)) + 1) > 18:
                trial["completion_comparison"] = {
                    "censored_distinctions": m,
                    "registered_cutoff": 18,
                }
            else:
                masks = [sum(1 << b for b in row) for row in after]

                def allowed(x):
                    return all(
                        (
                            (x & d).bit_count() % 2 == 0
                            if law == "parity"
                            else (x & d) not in (0, d)
                        )
                        for d in masks
                    )

                cnt = Counter(x & ((1 << n) - 1) for x in range(1 << m) if allowed(x))
                f, _, a = coeffs(stars, [law] * len(stars))
                z = f.sum(f.sq(word[0]) for word in a.values())
                total = sum(cnt.values())
                trial["completion_comparison"] = {
                    "raw_child_inputs": 1 << m,
                    "legal_children": total,
                    "old_support_size": len(a),
                    "all_old_input_extension_counts": {x: cnt[x] for x in a},
                    "equal_uniform_ordinary": all(cnt[x] * len(a) == total for x in a),
                    "equal_product_diagonal": all(
                        f.scale(cnt[x], z) == f.scale(total, f.sq(row[0]))
                        for x, row in a.items()
                    ),
                }
            out[f"{key}/{law}"] = trial
    return out


def october_checks():
    f = field(12)

    def coefficient(kind, bits):
        a, b, c = bits
        s = a + b + c
        if kind == "parity":
            return f.one if s % 2 == 0 else f.zero
        if s in (0, 3):
            return f.zero
        if kind == "old":
            return f.scale((-1) ** (a + (s == 2)), f.one)
        if kind == "positive":
            return f.one
        val = f.root(2 * s - 3)
        return f.conj(val) if kind == "conjugate" else val

    local = {
        k: {x: coefficient(k, tuple(x >> i & 1 for i in range(3))) for x in range(8)}
        for k in ("old", "positive", "product", "conjugate", "parity")
    }
    for x, c in local["old"].items():
        s = [x >> i & 1 for i in range(3)]
        assert (
            f.mul(c, f.root(3 + 2 * s[0] + 8 * s[1] + 8 * s[2])) == local["product"][x]
        )
    allrows = {}
    for k in (2, 3):
        names = [(i, j) for i in range(k + 1) for j in range(k + 1 - i)]
        ext = [names.index(x) for x in ((0, 0), (k, 0), (0, k))]
        rows = [
            tuple(names.index(t) for t in ((i, j), (i + 1, j), (i, j + 1)))
            for i in range(k)
            for j in range(k - i)
        ]
        theta = [0] * len(names)
        for row in rows:
            for b, exp in zip(row, (2, 8, 8)):
                theta[b] += exp
        summaries = {}
        for kind in (
            "old",
            "positive",
            "product",
            "conjugate",
            "parity",
            "product_undo_internal",
            "old_one_changed_first",
            "old_all_changed_first",
            "old_names_reversed",
        ):
            tensor = [f.zero] * 8
            counts = [0] * 8
            for x in range(1 << len(names)):
                bit = [(x >> j) & 1 for j in range(len(names))]
                raw = local[
                    kind
                    if kind in local
                    else "product"
                    if kind == "product_undo_internal"
                    else "old"
                ]
                if kind == "old_names_reversed":
                    decoded = [bit[-1 - j] for j in range(len(names))]
                else:
                    decoded = bit
                mon = []
                for i, row in enumerate(rows):
                    vals = [decoded[j] for j in row]
                    if kind == "old_all_changed_first" or (
                        i == 0 and kind == "old_one_changed_first"
                    ):
                        vals[0], vals[1] = vals[1], vals[0]
                    mon.append(raw[sum(v << j for j, v in enumerate(vals))])
                amp = f.prod(mon)
                boundary = sum(decoded[b] << j for j, b in enumerate(ext))
                if amp == f.zero:
                    continue
                counts[boundary] += 1
                if kind == "product_undo_internal":
                    amp = f.mul(
                        amp,
                        f.root(
                            -sum(
                                decoded[b] * theta[b]
                                for b in range(len(names))
                                if b not in ext
                            )
                        ),
                    )
                tensor[boundary] = f.add(tensor[boundary], amp)
            if kind == "product_undo_internal":
                source = stored
                assert all(
                    f.mul(
                        source[x],
                        f.root(
                            3 * len(rows)
                            + sum(((x >> j) & 1) * theta[b] for j, b in enumerate(ext))
                        ),
                    )
                    == y
                    for x, y in enumerate(tensor)
                )
            if kind == "product_undo_internal":
                restored = [
                    f.mul(
                        y,
                        f.root(
                            -3 * len(rows)
                            - sum(((x >> j) & 1) * theta[b] for j, b in enumerate(ext))
                        ),
                    )
                    for x, y in enumerate(tensor)
                ]
                assert restored == stored
                summaries["product_undo_internal_and_external"] = {
                    "tensor": list(map(f.serialize, restored)),
                    "equals_original_signed_contraction_exactly": True,
                }
            if kind == "old":
                stored = tensor
            if kind == "old_names_reversed":
                assert tensor == stored
            compare = local[kind] if kind in local else local["old"]
            anchor = next(x for x in compare if compare[x] != f.zero)
            prop = (
                all(
                    f.mul(y, compare[anchor]) == f.mul(compare[x], tensor[anchor])
                    for x, y in enumerate(tensor)
                )
                and tensor[anchor] != f.zero
            )
            summaries[kind] = {
                "fixed_coefficient_order": "exterior mask a+2b+4c",
                "tensor": list(map(f.serialize, tensor)),
                "unsigned_witness_count": counts,
                "scalar_multiple_of_enrolled_law": prop,
                "scalar_when_defined": f.ratio(tensor[anchor], compare[anchor])
                if prop
                else None,
            }
        allrows[k] = {
            "holdings": rows,
            "exterior": ext,
            "multiplicity_angle_exponents": theta,
            "tensors": summaries,
        }
    return {
        "field": 12,
        "local": {
            k: {x: f.serialize(y) for x, y in v.items()} for k, v in local.items()
        },
        "contractions": allrows,
    }


@lru_cache
def apparatus():
    if str(B287) not in sys.path:
        sys.path.insert(0, str(B287))
    import physical_composition

    return physical_composition, physical_composition._routes()


def keeper_checks():
    physical, routes = apparatus()
    result = {}
    rows_index = {f"single_{m}": (tuple(range(m)),) for m in range(3, 9)}
    rows_index.update(
        shared_ternaries=FIXTURES["shared_ternaries"],
        mixed_width=FIXTURES["mixed_width"],
    )
    for label, rows in rows_index.items():
        laws_list = [("nae",) * len(rows), ("parity",) * len(rows)]
        if len(rows) == 2:
            laws_list.extend((("nae", "parity"), ("parity", "nae")))
        for laws in laws_list:
            winds = [(1,) * len(rows), (-1,) * len(rows)]
            if len(rows) == 2:
                winds.append((1, -1))
            if label == "single_5":
                winds.append((2,))
            for wind in dict.fromkeys(winds):
                f, n, a = coeffs(rows, laws, wind)
                z = f.sum(f.sq(r[0]) for r in a.values())
                fixed = sum(1 << h[1] for h in rows)
                configurations = {
                    "one_occupied_per_remainder": fixed,
                    "all_exterior_zero": 0,
                    "absent_v": None,
                }
                for which, bits in configurations.items():
                    key = f"{label}/{'-'.join(laws)}/{','.join(map(str, wind))}/{which}"
                    if bits is None:
                        result[key] = {
                            "status": "missing physical source for v",
                            "K": "110",
                            "outcomes": [],
                        }
                        continue
                    pair = [a.get(bits | j, (f.zero,) * 3) for j in (0, 1)]
                    data = 245
                    for j in range(1, n):
                        data = (data & ~(1 << (j - 1))) | (((bits >> j) & 1) << (j - 1))
                    launches = []
                    for reverse in (False, True):
                        raw = physical.basis_words(reverse, data)
                        wires = {}
                        for j, start in enumerate(("c", "a")):
                            wires[start] = {
                                f"{int(one)}{int(two)}": physical.readout_word(
                                    raw[start], stages=(one, two), reverse=reverse
                                )
                                for one, two in product((False, True), repeat=2)
                            }
                        refused = {
                            "missing": physical.readout_word(None, reverse=reverse),
                            "nonready": physical.readout_word(
                                routes.encode(data, keeper="011", reverse=reverse),
                                reverse=reverse,
                            ),
                            "damaged_register": physical.readout_word(
                                raw["a"] ^ (1 << routes._guard(routes.Q, reverse)[0]),
                                reverse=reverse,
                            ),
                            "disconnected_permission": physical.readout_word(
                                raw["a"], reverse=reverse, present=False
                            ),
                        }
                        launches.append(
                            {
                                "reversed_encoding": reverse,
                                "physical": wires,
                                "refusals": refused,
                            }
                        )
                    src = {}
                    for typ in (
                        "F",
                        "conjugate_F",
                        "modulus",
                        "positive",
                        "incoherent_modulus",
                        "singleton_0",
                        "singleton_1",
                    ):
                        v = [
                            r[0]
                            if typ in ("F", "incoherent_modulus")
                            else f.conj(r[0])
                            if typ == "conjugate_F"
                            else r[1]
                            if typ == "modulus"
                            else f.one
                            if r[0] != f.zero
                            else f.zero
                            for r in pair
                        ]
                        if typ.startswith("singleton"):
                            v = [
                                vv if j == int(typ[-1]) else f.zero
                                for j, vv in enumerate(v)
                            ]
                        den = f.sum(f.sq(u) for u in v)
                        base_norm = (
                            f.scale(len(a), f.one)
                            if typ.startswith("singleton") or typ == "positive"
                            else z
                        )
                        rec = {
                            "initial_two_amplitudes_before_global_normalization": list(
                                map(f.serialize, v)
                            ),
                            "unconditional_ordinary_exterior_probability": f.ratio(
                                den, base_norm
                            ),
                        }
                        if typ.startswith("singleton"):
                            rec["independently_initialized_basis_control_admission"] = (
                                "0" if den == f.zero else "1"
                            )
                        if den == f.zero:
                            rec.update(status="no admitted alternative", readout=None)
                            src[typ] = rec
                            continue
                        probes = {}
                        phase_ratio = None
                        if all(t[0] != f.zero for t in pair):
                            phase_ratio = f.mul(pair[1][2], f.conj(pair[0][2]))
                        for h, phase in [
                            ("fixed", f.one),
                            ("quarter_turn_q1", f.root(f.n // 4)),
                            (
                                "remove_F_relative_phase",
                                f.conj(phase_ratio) if phase_ratio else f.one,
                            ),
                            (
                                "apply_F_relative_phase_to_question",
                                phase_ratio if phase_ratio else f.one,
                            ),
                        ]:
                            u0, u1 = v[0], f.mul(v[1], phase)
                            for direction in (1, -1):
                                it = f.root(direction * f.n // 4)
                                numerators = (
                                    f.sq(f.sub(u0, f.mul(it, u1))),
                                    f.sq(f.sub(u1, f.mul(it, u0))),
                                )
                                if typ == "incoherent_modulus":
                                    numerators = (den, den)
                                assert f.add(*numerators) == f.scale(2, den)
                                probs = [
                                    f.ratio(nu, f.scale(2, den)) for nu in numerators
                                ]
                                probes[
                                    f"{h}/{'inverse_B' if direction == 1 else 'B'}"
                                ] = {
                                    "terminal_word_q0_q1": probs,
                                    "unnormalized_field_amplitudes_before_division_by_sqrt2": None
                                    if typ == "incoherent_modulus"
                                    else [
                                        f.serialize(f.sub(u0, f.mul(it, u1))),
                                        f.serialize(f.sub(u1, f.mul(it, u0))),
                                    ],
                                    "K_distributions_ready_101_011": {
                                        "11": ["0", *probs],
                                        "10": [probs[0], "0", probs[1]],
                                        "01": ["0", "1", "0"],
                                        "00": ["1", "0", "0"],
                                    },
                                }
                        rec.update(status="accepted", probes=probes)
                        src[typ] = rec
                    checks = {}
                    if src['F']['status'] == 'accepted':
                        for direction in ('B','inverse_B'):
                            for left,lp,right,rp in (('F','fixed','modulus','apply_F_relative_phase_to_question'),
                                                    ('modulus','fixed','F','remove_F_relative_phase')):
                                aleft=src[left]['probes'][f'{lp}/{direction}']['K_distributions_ready_101_011']
                                aright=src[right]['probes'][f'{rp}/{direction}']['K_distributions_ready_101_011']
                                assert aleft==aright
                                checks[f'{left}/{lp}={right}/{rp}/{direction}']=True
                    result[key] = {
                        "field": f.n,
                        "word_pair": (bits, bits | 1),
                        "data_preload": data,
                        "coefficient_norm": f.serialize(z),
                        "physical_routes": launches,
                        "verified_fixed_and_transported_ports":checks,
                        "sources": src,
                    }
    return result
