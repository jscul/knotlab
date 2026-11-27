"""Exact transfer, value tables and signed-product audit. Run with --pilot before the full run."""
import argparse
import itertools
import json
from fractions import Fraction
from math import isqrt, sqrt
from pathlib import Path
from time import perf_counter

import numpy as np


def bitset(indices):
    return sum(1 << i for i in indices)


def places(mask, n):
    return [i for i in range(n) if mask & (1 << i)]


def submasks(mask):
    return np.array([x for x in range(mask + 1) if x & mask == x], dtype=int)


def one_round():
    """Filter all nine-bit words backwards using the input and each fresh pair."""
    pairs = [(3, 4), (5, 6), (7, 8)]
    laws = [7] + [bitset([i, *pair]) for i, pair in enumerate(pairs)]
    listed = [w for w in range(512) if all((w & law).bit_count() % 2 == 0 for law in laws)]
    arms = {}
    for mode in ('minimum', 'pair'):
        support = []
        for word in listed:
            founder = word & 7
            for i, pair in enumerate(pairs):
                count = (word & bitset(pair)).bit_count()
                allowed_count = 1 if founder >> i & 1 else 2 * (bool(founder) and mode == 'pair')
                if count != allowed_count:
                    break
            else:
                support.append(word)
        starts = sorted({w & 7 for w in support})
        branches = {start: sum(w & 7 == start for w in support) for start in starts}
        start_masses = {w: Fraction(1, len(starts) * branches[w & 7]) for w in support}
        arms[mode + ' start'] = start_masses
        arms[mode + ' reached once'] = {w: Fraction(1, len(support)) for w in support}
    arms['listed finish'] = {w: Fraction(1, len(listed)) for w in listed}
    return laws, arms


def splits(laws):
    """Every distinction takes one of three roles; the two readers are unordered."""
    out = []
    for role in itertools.product(range(3), repeat=9):
        if role.count(2) not in (1, 2) or 0 not in role or 1 not in role:
            continue
        a, b, c = (bitset(i for i, v in enumerate(role) if v == r) for r in range(3))
        if a < b and all(not (a & law and b & law) for law in laws):
            out.append((a, b, c))
    return sorted(out, key=lambda row: (row[2].bit_count(), row[2], row[:2]))


def amplitudes(probabilities, n):
    from math import lcm
    denominator = lcm(*(p.denominator for p in probabilities.values()))
    amp = np.zeros(1 << n, dtype=np.int64)
    for word, probability in probabilities.items():
        value = int(probability * denominator)
        amp[word] = isqrt(value)
        assert amp[word] ** 2 == value
    assert amp @ amp == denominator
    return amp


def product_expectations(amp):
    """Row f flips f; transform over w gives all phase-mask correlations."""
    d = len(amp)
    words = np.arange(d)
    coefficients = amp[words[:, None] ^ words[None, :]] * amp[None, :]
    width = 1
    while width < d:
        blocks = coefficients.reshape(d, -1, 2, width)
        lo, hi = blocks[:, :, 0].copy(), blocks[:, :, 1].copy()
        blocks[:, :, 0], blocks[:, :, 1] = lo + hi, lo - hi
        width *= 2
    ny = np.array([w.bit_count() for w in range(d)])[words[:, None] & words[None, :]]
    assert np.all(coefficients[ny % 2 == 1] == 0)
    coefficients[ny % 4 == 2] *= -1
    return coefficients


def strings(holding):
    choices = submasks(holding)
    return np.repeat(choices, len(choices)), np.tile(choices, len(choices))


def scores(correlations):
    """Rows index the smaller reader. Absolute values optimize independent output signs."""
    distinct = None
    frozen = None
    for b0, b1 in itertools.combinations(range(1, len(correlations)), 2):
        plus = np.abs(correlations[b0, 1:] + correlations[b1, 1:])
        minus = np.abs(correlations[b0, 1:] - correlations[b1, 1:])
        a0 = int(plus.argmax())
        raw = int(plus[a0] + minus.max())
        frozen = raw if frozen is None else max(raw, frozen)
        if len(plus) < 2:
            continue
        # Either the best first read is used and the second differs, or the first differs.
        alt_plus = plus.copy()
        alt_plus[a0] = -1
        alt_minus = minus.copy()
        alt_minus[a0] = -1
        choice = max(plus[a0] + alt_minus.max(), alt_plus.max() + minus[a0])
        distinct = int(choice) if distinct is None else max(distinct, int(choice))

    # Include identity on either reader and repeated settings, on either reader.
    extended = 0
    for i, row in enumerate(correlations):
        others = correlations[i:]
        summed = np.abs(others + row).max(axis=1)
        differenced = np.abs(others - row).max(axis=1)
        extended = max(extended, int((summed + differenced).max()))
    return {'distinct_nonidentity': distinct, 'original_pauli_convention': frozen, 'including_identity_repeats': extended}


def value_joint(amp, a, b):
    """Direct four-bin tallies; independently accumulate each single-reader marginal."""
    aa, bb = submasks(a), submasks(b)
    words = np.flatnonzero(amp)
    weights = amp[words] ** 2
    parity = np.array([w.bit_count() % 2 for w in range(len(amp))])
    left = parity[aa[:, None] & words]
    right = parity[bb[:, None] & words]
    marg_a = np.array([(left == answer) @ weights for answer in (0, 1)])
    marg_b = np.array([(right == answer) @ weights for answer in (0, 1)])
    joint = np.array([[((left == u) * weights) @ (right == v).T for v in (0, 1)] for u in (0, 1)])
    assert np.all(joint.sum(axis=1) == marg_a[:, :, None])
    assert np.all(joint.sum(axis=0) == marg_b[:, None, :])
    return joint[0, 0] + joint[1, 1] - joint[1, 0] - joint[0, 1]


def direct_projectors(amp, a, b):
    """One complex pair of local read menus per split. Apply projections directly to the amplitude."""
    na, nb = a.bit_count(), b.bit_count()
    n = len(amp).bit_length() - 1
    c = (len(amp) - 1) ^ (a | b)
    order = places(a, n) + places(b, n) + places(c, n)
    state = amp.reshape([2] * n, order='F').transpose(order).reshape(1 << na, 1 << nb, -1)
    rng = np.random.default_rng(217 + 17 * a + b)

    def two_menus(dim):
        out = []
        for _ in range(2):
            h = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))
            q, _ = np.linalg.qr(h)
            proj = q[:, ::2] @ q[:, ::2].conj().T
            out.append([proj, np.eye(dim) - proj])
        return out

    left, right = two_menus(1 << na), two_menus(1 << nb)
    expect_left = np.array([[np.linalg.norm(np.einsum('ij,jbc->ibc', p, state)) ** 2 for p in setting] for setting in left])
    expect_right = np.array([[np.linalg.norm(np.einsum('ij,ajc->aic', q, state)) ** 2 for q in setting] for setting in right])
    joint = np.zeros((2, 2, 2, 2))
    for x, y, u, v in itertools.product(range(2), repeat=4):
        after_a = np.einsum('ij,jbc->ibc', left[x][u], state)
        joint[x, y, u, v] = np.linalg.norm(np.einsum('ij,ajc->aic', right[y][v], after_a)) ** 2
    error = max(np.abs(joint.sum(axis=3) - expect_left[:, None, :]).max(),
                np.abs(joint.sum(axis=2) - expect_right[None, :, :]).max())
    return float(error / (amp @ amp))


def audit(name, probabilities, n, divisions):
    amp = amplitudes(probabilities, n)
    total = int(amp @ amp)
    table = product_expectations(amp)
    rows = []
    for a, b, c in divisions:
        if a.bit_count() > b.bit_count():
            a, b = b, a
        fa, za = strings(a)
        fb, zb = strings(b)
        paired = table[fa[:, None] | fb, za[:, None] | zb]
        values = value_joint(amp, a, b)
        assert np.array_equal(values, table[0, submasks(a)[:, None] | submasks(b)])
        p_scores = scores(paired)
        v_scores = scores(values)
        rows.append({'small_reader': places(a, n), 'other_reader': places(b, n), 'unread': places(c, n),
                     'pauli_numerators': p_scores, 'value_numerator_distinct': v_scores['distinct_nonidentity'],
                     'value_numerator_with_constants_and_repeats': v_scores['including_identity_repeats'],
                     'value_setting_pairs_nonempty': (len(values) - 1) * (values.shape[1] - 1),
                     'pauli_setting_pairs_nonidentity': (len(fa) - 1) * (len(fb) - 1),
                     'direct_projector_marginal_error': direct_projectors(amp, a, b)})
    record = {'weighting': name, 'weight_denominator': total,
              'words_in_distinction_order': {format(w, f'0{n}b')[::-1]: str(p) for w,p in probabilities.items()},
              'rows': rows}
    if name == 'pair start':
        record['frozen_spot_numerators'] = [int(table[f,z]) for f,z in
                [(0, bitset([0,7])), (bitset([0,1,3,5,7,8]),0), (0,bitset([0,1,7,8]))]]
        record['masses_given_unread_2_zero_before_normalization'] = [
            [str(sum((p for w,p in probabilities.items() if not w & 4 and w & 1 == x and w >> 7 & 1 == y), Fraction()))
             for y in (0,1)] for x in (0,1)]
    if n == 2:
        # Independent unrestricted bound/attainment via the two largest singular values
        # of the three single-distinction product correlations.
        f, z = strings(1)
        g, h = strings(2)
        mat = table[f[1:,None] | g[1:], z[1:,None] | h[1:]] / total
        sv = np.linalg.svd(mat, compute_uv=False)
        record['correlations_Z_X_Y'] = mat.tolist()
        record['unrestricted_control'] = 2 * sqrt(sv[0] ** 2 + sv[1] ** 2)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    then = perf_counter()
    laws, arms = one_round()
    divisions = splits(laws)
    if args.pilot:
        # Three splits cover the largest total holding, the balanced case and a singleton.
        reps = [(6, 2), (4, 3), (6, 1)]
        pilot = []
        for sizes in reps:
            matches = [s for s in divisions if sorted((s[0].bit_count(), s[1].bit_count()), reverse=True) == list(sizes)]
            if matches:
                pilot.append(matches[0])
        divisions = pilot
        arms = {'pair start': arms['pair start']}
    records = [audit(name, dist, 9, divisions) for name, dist in arms.items()]
    for name, support in [('even pair', [0, 3]), ('three words', [0, 1, 2])]:
        records.append(audit(name, {w: Fraction(1, len(support)) for w in support}, 2, [(1, 2, 0)]))
    out = {'pilot': args.pilot, 'listed_laws': [places(s, 9) for s in laws], 'records': records,
           'seconds': perf_counter() - then}
    if args.pilot:
        print(json.dumps({'splits': len(divisions), 'seconds': out['seconds']}))
    else:
        Path(__file__).with_name('read_tables.json').write_text(json.dumps(out, indent=2) + '\n')
        print(json.dumps({'weightings_and_controls': len(records), 'seconds': out['seconds']}))


if __name__ == '__main__':
    main()
