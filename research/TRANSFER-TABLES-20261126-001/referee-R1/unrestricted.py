"""Certify unrestricted CHSH values and negativities on the one-round fixture.

For an unread value c, H[c] is the integer coefficient matrix of its pure
state. The joint state is the sum of these pure-state projectors divided by D,
the sum of squared coefficients. All H[c] have Schmidt rank at most two.
Let u and v be the two Schmidt coefficients, allowing v = 0. Put m = u²+v²
and e = u²v². The maximum CHSH contribution of this unnormalized pure state
is 2 sqrt(m²+4e). In its Schmidt basis the correlation matrix is diagonal
with entries 2uv, -2uv, m. For unit Bloch vectors of the two smaller-reader
settings, their sum and difference are orthogonal with squared lengths adding
to four. Optimizing the two larger-reader directions and then these lengths
gives twice the square root of the sum of the two largest squared entries.
Compression to the Schmidt supports also allows Hermitian contractions. Their
extreme points are involutions. If one setting is constant, its reader's
settings commute and CHSH is at most 2m.

Summing these conditional optima gives an upper bound for the mixture. The
code checks its attainment with a single pair of settings for each reader.
In every violating case there is one entangled conditional state. Its two
orthogonal columns give the Schmidt basis. The smaller reader uses Z and X
on these two words. The larger reader distinguishes this pair of local states
from the remaining terms. On the pair it uses the normalized mZ ± 2uvX.
On each remaining term both its settings give the sign of the smaller
reader's Z. The exact disjoint supports and signs are checked below.

The partial transpose of the entangled pure term has one negative eigenvalue
-uv. The product terms have disjoint larger-reader support from that term,
so its negative eigenvalue survives in the sum. A second check constructs the
partial transpose entry by entry and diagonalizes it. The code uses only the
definitions of the transfer law, reader splits and supplied coherent state.
"""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import product
import json
from math import isqrt, lcm, sqrt
import os
import resource

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                 "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"
soft, hard = resource.getrlimit(resource.RLIMIT_AS)
cap = min(item for item in (soft, hard, 2 * 1024**3) if item != resource.RLIM_INFINITY)
resource.setrlimit(resource.RLIMIT_AS, (cap, hard))

import numpy as np


OLD = (0, 1, 2)
PAIRS = ((3, 4), (5, 6), (7, 8))
LAWS = [set(OLD)] + [{i, *pair} for i, pair in enumerate(PAIRS)]


def reader_splits():
    splits = []
    for roles in product(range(3), repeat=9):
        if roles.count(2) not in (1, 2) or 0 not in roles or 1 not in roles:
            continue
        readers = [tuple(i for i, r in enumerate(roles) if r == k) for k in range(3)]
        a, b, unread = readers
        if a < b and all(not (law.intersection(a) and law.intersection(b)) for law in LAWS):
            splits.append((a, b, unread))
    return sorted(splits, key=lambda s: (len(s[2]), s[2], s[0]))


def project(word, labels):
    return sum(((word >> label) & 1) << i for i, label in enumerate(labels))


def amplitudes(lift, counting):
    words = []
    for word in range(512):
        founder = project(word, OLD)
        if founder.bit_count() % 2:
            continue
        occupancies = [project(word, pair).bit_count() for pair in PAIRS]
        for i, count in enumerate(occupancies):
            old_input = (founder >> i) & 1
            if counting == "finish":
                fits = (count % 2 == old_input)
            else:
                required = 1 if old_input else 2 * int(lift == "pair" and founder != 0)
                fits = (count == required)
            if not fits:
                break
        else:
            words.append(word)
    sizes = Counter(project(word, OLD) for word in words)
    if counting == "start":
        weights = {w: Fraction(1, len(sizes) * sizes[project(w, OLD)]) for w in words}
    else:
        weights = {w: Fraction(1, len(words)) for w in words}
    denominator = lcm(*(weight.denominator for weight in weights.values()))
    coefficients = {w: isqrt(int(p * denominator)) for w, p in weights.items()}
    assert all(Fraction(v*v, denominator) == weights[w] for w, v in coefficients.items())
    assert sum(v*v for v in coefficients.values()) == denominator
    return coefficients, denominator


def conditional_states(amplitude, large, small, unread):
    shape = (2**len(large), 2**len(small))
    states = {}
    for word, strength in amplitude.items():
        c = project(word, unread)
        if c not in states:
            states[c] = np.zeros(shape, dtype=np.int64)
        states[c][project(word, large), project(word, small)] = strength
    return states


def schmidt_data(state):
    gram = state.T @ state
    square = gram @ gram
    mass = int(gram.trace())
    tr2 = int(square.trace())
    tr3 = int((square @ gram).trace())
    # The Gram matrix is positive. Its third elementary symmetric function
    # vanishes precisely when at most two Schmidt coefficients are nonzero.
    assert mass**3 - 3 * mass * tr2 + 2 * tr3 == 0
    return mass, (mass**2 - tr2) // 2


def attaining_reads(states, entangled):
    large, small = next(iter(states.values())).shape
    a0, a1 = np.eye(large), np.eye(large)
    b0, b1 = np.eye(small), np.eye(small)
    if not entangled:
        return a0, a1, b0, b1

    active, = entangled
    state = states[active]
    first, second = np.flatnonzero(np.any(state, axis=0))
    u = state[:, first].astype(float)
    v = state[:, second].astype(float)
    assert not np.any(u * v)
    schmidt_rows = set(np.flatnonzero(u + v))
    b0[second, second] = -1
    b1[[first, second], :] = b1[[second, first], :]
    sign_by_row = {}
    for c, conditional in states.items():
        if c == active:
            continue
        rows, cols = np.nonzero(conditional)
        assert schmidt_rows.isdisjoint(rows)
        signs = {int(b0[j, j]) for j in cols}
        sign, = signs
        for row in rows:
            assert sign_by_row.setdefault(row, sign) == sign
            a0[row, row] = a1[row, row] = sign

    s, t = np.linalg.norm(u), np.linalg.norm(v)
    u /= s
    v /= t
    identity = np.outer(u, u) + np.outer(v, v)
    z = np.outer(u, u) - np.outer(v, v)
    x = np.outer(u, v) + np.outer(v, u)
    mass, twice_product = s*s + t*t, 2*s*t
    length = np.hypot(mass, twice_product)
    a0 += (mass*z + twice_product*x) / length - identity
    a1 += (mass*z - twice_product*x) / length - identity
    return a0, a1, b0, b1


def direct_negativity(states, denominator):
    large, small = next(iter(states.values())).shape
    pt = np.zeros((large*small, large*small), dtype=np.int64)
    for state in states.values():
        nonzero = [(i, j, state[i, j]) for i, j in zip(*np.nonzero(state))]
        for (i, j, v), (k, l, w) in product(nonzero, repeat=2):
            pt[i*small+l, k*small+j] += v*w
    assert int(pt.trace()) == denominator and np.array_equal(pt.T, pt)
    ev = np.linalg.eigvalsh(pt)
    return float(-np.minimum(ev, 0).sum() / denominator)


def certify(amplitude, denominator, split):
    a, b, unread = split
    large, small = (a, b) if len(a) >= len(b) else (b, a)
    states = conditional_states(amplitude, large, small, unread)
    invariants = {c: schmidt_data(h) for c, h in states.items()}
    assert sum(m for m, _ in invariants.values()) == denominator
    entangled = [c for c, (_, e) in invariants.items() if e > 0]
    a0, a1, b0, b1 = attaining_reads(states, entangled)
    for read in (a0, a1, b0, b1):
        assert np.allclose(read.T, read, atol=1e-12, rtol=0)
        assert np.allclose(read @ read, np.eye(len(read)), atol=1e-12, rtol=0)
    achieved = sum(np.vdot(h, a0 @ h @ (b0+b1).T + a1 @ h @ (b0-b1).T)
                   for h in states.values()) / denominator
    product_mass = sum(m for m, e in invariants.values() if e == 0)
    root, ent_product = 0, 0
    if entangled:
        m, ent_product = invariants[entangled[0]]
        root = m*m + 4*ent_product
    optimum = 2 * (product_mass + sqrt(root)) / denominator
    negativity = sqrt(ent_product) / denominator
    direct = direct_negativity(states, denominator)
    assert abs(achieved - optimum) < 1e-12 and abs(direct - negativity) < 1e-12
    return {
        "conditional": [[c, m, e] for c, (m, e) in sorted(invariants.items())],
        "exact": [product_mass, root, ent_product, denominator],
        "witness_CHSH": round(float(achieved), 12),
        "partial_transpose_negativity": round(direct, 12),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    splits = reader_splits()
    assert len(splits) == 30
    if args.limit is not None:
        splits = splits[:args.limit]
    settings = (("minimum", "start"), ("minimum", "once"), ("pair", "start"),
                ("pair", "once"), ("pair", "finish"))
    raw = {f"{lift}_{counting}": amplitudes(lift, counting) for lift, counting in settings}
    rows = []
    for split in splits:
        checks = {name: certify(*data, split) for name, data in raw.items()}
        rows.append({"A": split[0], "B": split[1], "unread": split[2], "checks": checks})
    summary = {}
    for name in raw:
        counts = Counter(tuple(row["checks"][name]["exact"]) for row in rows)
        summary[name] = [{"exact": key, "splits": n} for key, n in sorted(counts.items())]
    print(json.dumps({
        "conditional_key": ["unread bits packed in listed order, first bit least significant",
                            "squared coefficient norm m", "squared Schmidt product e"],
        "exact_key": ["product mass numerator p", "entangled CHSH radicand r",
                      "negativity radicand e", "squared normalization D"],
        "formulas": {"unrestricted_CHSH": "2*(p+sqrt(r))/D", "negativity": "sqrt(e)/D"},
        "unrestricted_reads": "Hermitian involutions including constant and repeated settings",
        "weightings": {name: {"words": len(data[0]), "D": data[1]} for name, data in raw.items()},
        "summary": summary, "splits": rows,
    }, indent=1))


if __name__ == "__main__":
    main()
