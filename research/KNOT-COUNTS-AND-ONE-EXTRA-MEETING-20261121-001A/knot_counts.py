"""Exact finite occupation-count amplitudes and transported local questions.

Cyclotomic elements are represented by ascending polynomial coefficients modulo
the indicated cyclotomic polynomial. A probability is an exact numerator and a
strictly positive exact denominator in the same field.
"""

from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import gcd, lcm, pi
import cmath
from sympy import Poly, Symbol, cyclotomic_poly


class Field:
    def __init__(self, n):
        self.n = n
        x = Symbol("x")
        self.mod = tuple(
            int(c) for c in reversed(Poly(cyclotomic_poly(n, x), x).all_coeffs())
        )
        self.degree = len(self.mod) - 1
        self.zero = (0,) * self.degree
        self.one = (1,) + (0,) * (self.degree - 1)
        values = [self.one]
        for j in range(1, n):
            values.append(self.reduce((0,) + values[-1]))
        self.roots = tuple(values)
        assert self.reduce((0,) + values[-1]) == self.one

    def reduce(self, coefficients):
        c = list(coefficients)
        for i in range(len(c) - 1, self.degree - 1, -1):
            v = c.pop()
            if v:
                start = i - self.degree
                for j, a in enumerate(self.mod[:-1]):
                    if a:
                        c[j + start] -= v * a
        c.extend([0] * (self.degree - len(c)))
        return tuple(c)

    def root(self, exponent):
        return self.roots[exponent % self.n]

    def add(self, a, b):
        return tuple(x + y for x, y in zip(a, b))

    def scale(self, q, a):
        return tuple(q * x for x in a)

    def sub(self, a, b):
        return tuple(x - y for x, y in zip(a, b))

    def sum(self, values):
        c = list(self.zero)
        for row in values:
            for j, x in enumerate(row):
                c[j] += x
        return tuple(c)

    @lru_cache(30000)
    def mul(self, a, b):
        if a == self.zero or b == self.zero:
            return self.zero
        if a == self.one:
            return b
        if b == self.one:
            return a
        raw = [0] * (2 * self.degree - 1)
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b):
                    if y:
                        raw[i + j] += x * y
        return self.reduce(raw)

    def prod(self, values):
        result = self.one
        for x in values:
            result = self.mul(result, x)
        return result

    @lru_cache(30000)
    def conj(self, a):
        return self.sum(self.scale(x, self.root(-j)) for j, x in enumerate(a) if x)

    def sq(self, a):
        return self.mul(a, self.conj(a))

    def serialize(self, a):
        def scalar(x):
            return int(x) if int(x) == x else str(x)

        if not any(a[1:]):
            return scalar(a[0])
        return list(map(scalar, a))

    def ratio(self, a, b):
        if b == self.zero:
            return None
        ix = next(i for i, x in enumerate(b) if x)
        scalar = Fraction(a[ix], b[ix])
        if a == self.scale(scalar, b):
            return str(scalar)
        return [self.serialize(a), self.serialize(b)]

    def approximate(self, a):
        return sum(float(x) * cmath.exp(2j * pi * k / self.n) for k, x in enumerate(a))


@lru_cache
def field(n):
    return Field(n)


FIXTURES = {
    "disjoint_ternaries": ((0, 1, 2), (3, 4, 5)),
    "shared_ternaries": ((0, 1, 2), (0, 3, 4)),
    "mixed_width": ((0, 1, 2), (0, 3, 4, 5)),
    "shared_four": ((0, 1, 2, 3), (0, 4, 5, 6)),
    "three_parent": ((0, 1, 3), (0, 2, 4), (1, 2, 5)),
}


def local(kf, m, s, law, k=1):
    if law == "parity":
        a = kf.one if s % 2 == 0 else kf.zero
        return a, a, a
    if s in (0, m):
        return kf.zero, kf.zero, kf.zero
    k %= m
    angle = kf.n * k * s // (2 * m)
    amp = kf.sub(kf.one, kf.root(2 * angle))
    negative = (k * s // m) % 2
    raw_sine = kf.mul(kf.root(-kf.n // 4), kf.sub(kf.root(angle), kf.root(-angle)))
    mag = kf.scale((-1) ** negative, raw_sine)
    phase = kf.scale((-1) ** negative, kf.root(angle - kf.n // 4))
    assert kf.mul(mag, phase) == amp
    return amp, mag, phase


def coeffs(rows, laws, winds=None):
    f = field(lcm(4, *(2 * len(row) for row in rows)))
    v = max(max(r) for r in rows) + 1
    winds = winds or [1] * len(rows)
    masks = [sum(1 << x for x in row) for row in rows]
    table = {}
    for x in range(1 << v):
        sectors = [
            local(f, len(h), (m & x).bit_count(), law, k)
            for h, m, law, k in zip(rows, masks, laws, winds)
        ]
        amp, mag, ph = (f.prod(c) for c in zip(*sectors))
        if amp != f.zero:
            table[x] = (amp, mag, ph)
    return f, v, table


def raw_forms(f, a):
    return {
        k: {x: f.serialize(r[j]) for x, r in a.items()}
        for j, k in enumerate(("amplitude", "magnitude", "phase"))
    }


def single_counts():
    studies = {}
    for m in range(2, 9):
        f = field(lcm(12, 2 * m))
        ms = {}
        for k in range(1, m):
            terms = []
            for s in range(m + 1):
                u, a, ph = local(f, m, s, "nae", k)
                den = f.sq(f.sub(f.one, f.root(f.n * k // m)))
                terms.append(
                    {
                        "s": s,
                        "admitted": 0 < s < m,
                        "raw_amplitude": f.serialize(u),
                        "raw_abs": f.serialize(a),
                        "phase_if_nonzero": None if u == f.zero else f.serialize(ph),
                        "squared_factor": f.ratio(f.sq(u), den),
                    }
                )
            good = all(row["phase_if_nonzero"] is not None for row in terms[1:-1])
            assert good == (gcd(k, m) == 1)
            slope = []
            if good:
                phase = [local(f, m, s, "nae", k)[2] for s in range(1, m)]
                slope = [f.mul(a, f.conj(b)) for a, b in zip(phase[1:], phase)]
            ms[k] = {
                "primitive": good,
                "coefficients": terms,
                "constant_single_name_slope": None
                if not good
                else len(set(slope)) <= 1,
                "neighbor_phase_ratios": [f.serialize(x) for x in slope],
            }
        third = [f.sq(f.sub(f.one, f.root(f.n * s // 3))) for s in range(m + 1)]
        studies[m] = {
            "field": f.n,
            "winding": ms,
            "literal_third_raw_chances_relative_to_first": [
                f.ratio(x, f.scale(3, f.one)) for x in third
            ],
            "literal_third_masked_by_original": [
                f.ratio(x if 0 < s < m else f.zero, f.scale(3, f.one))
                for s, x in enumerate(third)
            ],
            "false_raw_support": [
                s for s, z in enumerate(third) if (z != f.zero) != (0 < s < m)
            ],
            "parity": [int(s % 2 == 0) for s in range(m + 1)],
        }
    return studies


def compact(x, row):
    return sum(((x >> b) & 1) << i for i, b in enumerate(row))


def one_shared_turn_test(f, a):
    by_weight = defaultdict(list)
    for x in a:
        by_weight[x.bit_count()].append(x)
    for rows in by_weight.values():
        for x in rows:
            for y in rows:
                if a[x][2] != a[y][2]:
                    return {
                        "possible": False,
                        "same_total_opposite_requirements": [x, y],
                        "values": [f.serialize(a[t][2]) for t in (x, y)],
                    }
    # A possible scalar and common angle across all Hamming weights. Enumerate
    # any required root of the first relation analytically via integer powers.
    weights = sorted(by_weight)
    base = weights[0]
    s0 = a[by_weight[base][0]][2]
    angles = {u: j for j, u in enumerate(f.roots)}
    ratios = {
        s - base: angles[f.mul(a[by_weight[s][0]][2], f.conj(s0))] for s in weights[1:]
    }
    if not ratios:
        return {"possible": True, "representative_angle_turns": "0"}
    step = min(ratios)
    for t in range(step):
        turn = Fraction(ratios[step] + t * f.n, step * f.n)
        if all(
            (k * turn - Fraction(v, f.n)).denominator == 1 for k, v in ratios.items()
        ):
            return {"possible": True, "representative_angle_turns": str(turn)}
    return {"possible": False, "weight_classes_disagree": ratios}


def block_test(f, a, n, split):
    bound = (1 << split) - 1
    adjacency = defaultdict(list)
    for x, (_, _, p) in a.items():
        L = ("left", x & bound)
        R = ("right", x >> split)
        adjacency[L].append((R, p))
        adjacency[R].append((L, p))
    potentials = {}
    for root in adjacency:
        if root in potentials:
            continue
        potentials[root] = f.one
        queue = [root]
        while queue:
            here = queue.pop()
            for next_, v in adjacency[here]:
                need = f.mul(v, f.conj(potentials[here]))
                if next_ not in potentials:
                    potentials[next_] = need
                    queue.append(next_)
                elif need != potentials[next_]:
                    return {
                        "possible": False,
                        "inconsistent_at": [here, next_],
                        "required": f.serialize(need),
                        "existing": f.serialize(potentials[next_]),
                    }
    return {
        "possible": True,
        "factor": {"%s/%s" % k: f.serialize(v) for k, v in potentials.items()},
    }


def moments(f, v, table, angle_exp):
    norm = f.sum(f.sq(r[0]) for r in table.values())
    states = set(table)
    denom = f.scale(len(states), f.one)
    out = []
    diff = 0
    # Endpoint Fourier sums over every disjoint read/change pair. Store common
    # numerator scale separately and all ordinary integer counts.
    for d in range(1 << v):
        pairs = [(x, x ^ d) for x in sorted(states) if x ^ d in states]
        terms = {}
        for x, y in pairs:
            u = f.mul(f.conj(table[y][0]), table[x][0])
            u0 = f.mul(table[y][1], table[x][1])
            slope = sum(
                angle_exp[j] * (1 - 2 * ((x >> j) & 1)) for j in range(v) if d >> j & 1
            )
            assert u == f.mul(u0, f.root(-slope))
            terms[x] = u, u0
        allowed = ((1 << v) - 1) ^ d
        z = allowed
        while True:
            signs = {x: (-1) ** ((x & z).bit_count()) for x, _ in pairs}
            nu = f.sum(f.scale(signs[x], vals[0]) for x, vals in terms.items())
            mag = f.sum(f.scale(signs[x], vals[1]) for x, vals in terms.items())
            count = sum(signs.values())
            assert f.conj(nu) == nu and f.conj(mag) == mag
            match = f.mul(denom, nu) == f.scale(count, norm)
            diff += not match
            out.append([d, z, count, f.serialize(nu), f.serialize(mag)])
            if not z:
                break
            z = (z - 1) & allowed
    return {
        "columns": [
            "change",
            "read",
            "uniform_freedom_numerator",
            "fixed_change_F_numerator",
            "absF_numerator_also_F_cotransported",
        ],
        "uniform_denominator": len(states),
        "weighted_denominator": f.serialize(norm),
        "disagreements_uniform_fixedF": diff,
        "rows": out,
    }


def fixture_checks():
    rowsets = {**{f"single_{m}": (tuple(range(m)),) for m in range(2, 9)}, **FIXTURES}
    evidence = {}
    for label, rows in rowsets.items():
        entries = {}
        laws_list = [("parity",) * len(rows), ("nae",) * len(rows)]
        if len(rows) == 2:
            laws_list.extend((("parity", "nae"), ("nae", "parity")))
        for laws in laws_list:
            f, v, a = coeffs(rows, laws)
            norms = f.sum(f.sq(t[0]) for t in a.values())
            scales = f.prod(
                f.sq(f.sub(f.one, f.root(f.n // len(h)))) if law == "nae" else f.one
                for h, law in zip(rows, laws)
            )
            angles = [
                sum(
                    f.n // (2 * len(h))
                    for h, law in zip(rows, laws)
                    if j in h and law == "nae"
                )
                for j in range(v)
            ]
            shift = f.root(-sum(law == "nae" for law in laws) * (f.n // 4))
            for x, t in a.items():
                assert (
                    f.mul(shift, f.root(sum(angles[j] for j in range(v) if x >> j & 1)))
                    == t[2]
                )
            projections = {}
            for idx, (h, law) in enumerate(zip(rows, laws)):
                got = {compact(x, h) for x in a}
                expected = {
                    u
                    for u in range(1 << len(h))
                    if (
                        u.bit_count() % 2 == 0
                        if law == "parity"
                        else 0 < u.bit_count() < len(h)
                    )
                }
                assert got == expected
                forgotten = [
                    len({(u & ((1 << j) - 1)) | ((u >> (j + 1)) << j) for u in got})
                    for j in range(len(h))
                ]
                assert all(q == 1 << (len(h) - 1) for q in forgotten)
                projections[idx] = {
                    "words": sorted(got),
                    "K1": len(got) < 1 << len(h),
                    "K2_counts": forgotten,
                    "K3": bool(got),
                }
            entries["/".join(laws)] = {
                "field": f.n,
                "lawful_words": len(a),
                "raw_scale_squared": f.serialize(scales),
                "raw_norm_squared": f.serialize(norms),
                "normalized_each_word": {
                    x: f.ratio(f.sq(t[0]), norms) for x, t in a.items()
                },
                "exact_F": raw_forms(f, a),
                "global_phase": f.serialize(shift),
                "per_named_distinction_exponents": angles,
                "uniform_angle": one_shared_turn_test(f, a),
                "full_projection": projections,
                "same_word_magnitudes": len({t[1] for t in a.values()}) == 1,
            }
            if label in FIXTURES or label in ("single_3", "single_4"):
                entries["/".join(laws)]["moments"] = moments(f, v, a, angles)
            if label == "single_5" and laws == ("nae",):
                controls = {}
                for k in (1, 2, 3, 4):
                    ff, _, aa = coeffs(rows, laws, [k])
                    controls[k] = {s: block_test(ff, aa, v, s) for s in range(1, v)}
                entries["/".join(laws)]["two_readers_arbitrary_diagonal_per_block"] = (
                    controls
                )
        evidence[label] = {"holdings": rows, "laws": entries}
    return evidence
