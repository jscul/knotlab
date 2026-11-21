"""Exact real quantum channels, including the untouched local spectator probes."""

from fractions import Fraction as F
from functools import reduce, lru_cache
from itertools import product
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = ROOT / "research/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001B"
sys.path.insert(0, str(PREVIOUS))
from real_algebra import Mat, tensor, identity, ray, add, born
from real_algebra import Catalogue as Catalogue, zero as zero

I = identity(2)
IX = identity(4)
X = Mat([[0, 1], [1, 0]])
Z = Mat([[1, 0], [0, -1]])
J = X @ Z
M = tensor(J, J).scale(-1)
S = {t: (IX + M.scale(t)).scale(F(1, 2)) for t in (1, -1)}
BELL_PHASE = {e: ray([1, 0, 0, e]) for e in (1, -1)}
YRHO = {t: (IX + M.scale(t)).scale(F(1, 4)) for t in (-1, 0, 1)}
BASE = (ray((1, 0)), ray((0, 1)))
MEASX = (ray((1, 1)), ray((1, -1)))


class Root:
    """A matrix over Q(sqrt(3)) as two reduced rational coefficient matrices."""

    def __init__(self, a, b=None):
        self.a = a
        self.b = Mat(np.zeros(a.a.shape, dtype=int)) if b is None else b

    def __add__(self, v):
        return Root(self.a + v.a, self.b + v.b)

    def __sub__(self, v):
        return self + v.scale(-1)

    def scale(self, u):
        return Root(self.a.scale(u), self.b.scale(u))

    def __matmul__(self, v):
        return Root(self.a @ v.a + (self.b @ v.b).scale(3), self.a @ v.b + self.b @ v.a)

    @property
    def T(self):
        return Root(self.a.T, self.b.T)

    def __eq__(self, v):
        return self.a == v.a and self.b == v.b

    def put(self, cat):
        return [cat.put(self.a), cat.put(self.b)]

    def rational(self):
        assert not any(self.b.a.flat)
        return self.a

    def tr(self):
        return (self.a.tr(), self.b.tr())


def kron(u, v):
    return Root(
        tensor(u.a, v.a) + tensor(u.b, v.b).scale(3),
        tensor(u.a, v.b) + tensor(u.b, v.a),
    )


def grouped(mat):
    return Mat(
        mat.a.reshape((2,) * 8).transpose(0, 2, 1, 3, 4, 6, 5, 7).reshape(16, 16), mat.d
    )


def group_sites(m):
    # (data_A,reference_A,data_B,reference_B) to (data_AB,reference_AB).
    return Root(grouped(m.a), grouped(m.b))


def trace_reference(m):
    v = np.trace(m.a.reshape(4, 4, 4, 4), axis1=1, axis2=3)
    return Mat(v, m.d)


def units(n=4):
    return tuple(
        Mat(np.eye(n, dtype=int)[:, i : i + 1] @ np.eye(n, dtype=int)[j : j + 1, :])
        for i, j in product(range(n), repeat=2)
    )


UNITS = units()


def choi(rows):
    """Unnormalized Choi in (spectator quartet, output data quartet) order."""
    from math import lcm

    den = reduce(lcm, (x.d for x in rows), 1)
    return Mat(
        np.block(
            [[m.a * (den // m.d) for m in rows[i * 4 : i * 4 + 4]] for i in range(4)]
        ),
        den,
    )


def apply_channel(ch, rho):
    t = ch.a.reshape((4,) * 4)
    out = np.zeros((4, 4), dtype=object)
    for i, j in product(range(4), repeat=2):
        out += rho.a[i, j] * t[i, :, j, :]
    return Mat(out, ch.d * rho.d)


def compose(after, before):
    return choi([apply_channel(after, apply_channel(before, x)) for x in UNITS])


def kraus_map(k, n=1):
    return choi([(k @ m @ k.T).scale(F(1, n)) for m in UNITS])


def effect(ch):
    return Mat(np.trace(ch.a.reshape(4, 4, 4, 4), axis1=1, axis2=3).T, ch.d)


def proportional(first, second):
    for x, y in zip(first.a.flat, second.a.flat):
        if y:
            c = F(x * second.d, y * first.d)
            return str(c) if first == second.scale(c) else None
    return "all zero" if first == second else None


def input_library():
    states = {
        "".join(str(i) for i in divmod(j, 2)): ray([int(i == j) for i in range(4)])
        for j in range(4)
    }
    for t in (1, -1):
        u = np.array([1, 0, 0, -t])
        v = np.array([0, 1, t, 0])
        assert np.array_equal(M.a @ u, t * u) and np.array_equal(M.a @ v, t * v)
        for label, vec in [("u", u), ("v", v), ("u+v", u + v), ("u-v", u - v)]:
            states[f"{t}/{label}"] = ray(vec)
    states["cross_sign_equal"] = ray([1, 1, 1, 1])
    states["cross_sign_unequal"] = ray([1, 2, -1, 0])
    states["mixed_uniform"] = IX.scale(F(1, 4))
    states["diagonal_1234"] = Mat(np.diag([1, 2, 3, 4]), 10)
    return states


IDEAL = {t: kraus_map(P) for t, P in S.items()}
IDENTITY_CHANNEL = kraus_map(IX)


def dephased_sector(t):
    # On a sign space, conjugating by local J negates the off-diagonal in the local charge basis.
    k = tensor(J, I) @ S[t]
    return (IDEAL[t] + kraus_map(k)).scale(F(1, 2))


DSEC = {t: dephased_sector(t) for t in (1, -1)}


def effective(ops, rho, den):
    """Trace out the reference and obtain all sixteen Choi blocks over Q(sqrt(3))."""
    from math import lcm

    op_den = lcm(ops.a.d, ops.b.d)
    ref_den = lcm(rho.a.d, rho.b.d)
    width = rho.a.a.shape[0]
    target_ref_shape = (4, width, 4, width)
    op_rational = (ops.a.a * (op_den // ops.a.d)).reshape(target_ref_shape)
    op_radical = (ops.b.a * (op_den // ops.b.d)).reshape(target_ref_shape)
    ref_rational = rho.a.a * (ref_den // rho.a.d)
    ref_radical = rho.b.a * (ref_den // rho.b.d)
    rational = np.zeros((16, 16), dtype=object)
    radical = rational.copy()
    # Keep the input reference indices v,w; identify the two output reference indices q to trace.
    for q, v, w in product(range(width), repeat=3):
        p, s = ref_rational[v, w], ref_radical[v, w]
        if p == 0 and s == 0:
            continue
        left = op_rational[:, q, :, v].T.reshape(16)
        left_root = op_radical[:, q, :, v].T.reshape(16)
        right = op_rational[:, q, :, w].T.reshape(16)
        right_root = op_radical[:, q, :, w].T.reshape(16)
        direct = np.outer(left, right) + 3 * np.outer(left_root, right_root)
        crossed = np.outer(left, right_root) + np.outer(left_root, right)
        rational += p * direct + 3 * s * crossed
        radical += p * crossed + s * direct
    denominator = den * op_den * op_den * ref_den
    return Root(Mat(rational, denominator), Mat(radical, denominator))


def evaluate_dataset(channels, cat):
    zz = tensor(Z, Z)
    zx = tensor(Z, X)
    states = input_library()
    result = {}
    for name, rho in states.items():
        out = {}
        for label, ch in channels.items():
            target = apply_channel(ch, rho)
            p = target.tr()
            conditional = target.scale(1 / p) if p else None
            grade = {}
            for t, ideal in IDEAL.items():
                desired = apply_channel(ideal, rho)
                v = desired.tr()
                if v and p and desired @ desired == desired.scale(v):
                    grade[str(t)] = str(born(conditional, desired.scale(1 / v)))
            out[str(label)] = {
                "p": str(p),
                "subnormalized_state": cat.put(target),
                "conditional": cat.put(conditional) if p else None,
                "conditional_ZZ_ZX": list(
                    map(str, (born(conditional, zz), born(conditional, zx)))
                )
                if p
                else None,
                "pure_ideal_overlaps_when_defined": grade,
            }
        result[name] = out
    return result


def process_records(channels, cat):
    z = {}
    for k, ch in channels.items():
        z[str(k)] = {
            "unnormalized_choi": cat.put(ch),
            "local_spectator_probe_out": cat.put(ch.scale(F(1, 4))),
            "effect": cat.put(effect(ch)),
            "proportional_to_ideal_plus_or_minus": {
                str(t): proportional(ch, p) for t, p in IDEAL.items()
            },
            "choi_rank": rank(ch.key()),
        }
    return z


@lru_cache(maxsize=None)
def rank(key):
    from sympy import Matrix

    shape, _, entries = key
    return int(Matrix(*shape, list(entries)).rank())


def coarse(channels, decoding):
    return {
        t: add([ch for k, ch in channels.items() if decoding(k) == t], 16)
        for t in (1, -1)
    }


def residual(op, rho, ref, den):
    return (op @ kron(Root(rho), ref) @ op.T).scale(F(1, den))


def label(pair):
    return "".join(map(str, pair))
