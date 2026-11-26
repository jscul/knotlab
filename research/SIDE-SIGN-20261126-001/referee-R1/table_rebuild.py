"""Count signed pairs of distinction readings with exact integers."""
from collections import defaultdict
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
GROWTH = HERE.parents[1] / 'FORBID-EDITS-20261126-001'
sys.path.insert(0, str(GROWTH))
import forbid


def allowed_words(rows, law):
    masks = [sum(1 << d for d in row) for row in rows]
    for word in range(1 << max(m.bit_length() for m in masks)):
        if law == 'parity':
            ok = all((word & m).bit_count() % 2 == 0 for m in masks)
        else:
            ok = all(word & m and (word & m) != m for m in masks)
        if ok:
            yield word


def lift(rows, knots):
    holders = defaultdict(list)
    for d, support in forbid.holders(rows).items():
        holders[tuple(sorted(support))].append(d)
    p = {}
    for support, bits in holders.items():
        image = holders[tuple(sorted(knots[h] for h in support))]
        if len(bits) != len(image):
            raise ValueError("Knot action does not lift")
        p.update(zip(sorted(bits), sorted(image)))
    assert all(p[p[d]] == d for d in p)
    return [p[d] for d in range(len(p))]


def weights(w, perm):
    pairs = [(i, j) for i, j in enumerate(perm) if i < j]
    bits = [(w >> i & 1, w >> j & 1) for i, j in pairs]
    different = sum(a != b for a, b in bits)
    both = sum(a * b for a, b in bits)
    fixed = different == 0
    opposite = len(pairs) * 2 == len(perm) and different == len(pairs)
    return {
        'equal positive': 1,
        'odd number of unlike pairs negative': (-1) ** different,
        'odd number of double ones negative': (-1) ** both,
        'fixed positive, others negative': 1 if fixed else -1,
        'opposite negative, others positive': -1 if opposite else 1,
        'fixed minus opposite, others zero': int(fixed) - int(opposite),
    }


def count_pairs(words, masses, n):
    counts = {}
    for i, j in combinations(range(n), 2):
        row = [0] * 4
        for word, mass in zip(words, masses):
            row[2 * (word >> i & 1) + (word >> j & 1)] += mass
        counts[i, j] = row
        counts[j, i] = [row[0], row[2], row[1], row[3]]
    return counts


def score(rows):
    z = [sum(t) for t in rows]
    if 0 in z:
        return 0, None
    if any(v * total < 0 for t, total in zip(rows, z) for v in t):
        return 1, None
    if len(set(z)) != 1:
        return 2, None
    a = lambda t: t[0] + t[1]
    b = lambda t: t[0] + t[2]
    if a(rows[0]) != a(rows[1]) or a(rows[2]) != a(rows[3]) or b(rows[0]) != b(rows[2]) or b(rows[1]) != b(rows[3]):
        return 3, None
    corr = [t[0] - t[1] - t[2] + t[3] for t in rows]
    best = Fraction(max(abs(sum(corr) - 2 * v) for v in corr), abs(z[0]))
    return (5 if best > 2 else 4), best


def readings(counts, n, square):
    best = None
    gate = [0] * 6
    record = {}
    for four in combinations(range(n), 4):
        for j in range(1, 4):
            a = (four[0], four[j])
            b = tuple(x for x in four if x not in a)
            raw = [counts[i, k] for i, k in product(a, b)]
            rows = [[v * v for v in row] for row in raw] if square else raw
            g, s = score(rows)
            gate[g] += 1
            if s is not None and (best is None or s > best):
                best = s
                record = dict(a=a, b=b, sums=raw, masses=rows, Z=list(map(sum, rows)), best=str(s))
    return dict(first_failed_gate_or_pass=gate, optimum=record)


def inspect(rows, perm, law):
    words = list(allowed_words(rows, law))
    values = [weights(w, perm) for w in words]
    results = {}
    for name in values[0]:
        masses = [v[name] for v in values]
        counts = count_pairs(words, masses, len(perm))
        results[name] = dict(total=sum(masses), negative=masses.count(-1), zero=masses.count(0),
                             linear=readings(counts, len(perm), False), squared=readings(counts, len(perm), True))
    return dict(rows=rows, perm=perm, states=len(words), trials=results)


def cases():
    start = json.loads((GROWTH / 'starts.json').read_text())[3097]
    base = forbid.supports_of(start)
    for law in ('parity', 'nae'):
        for i in (0, 1):
            rows = base if i == 0 else forbid.grown(base, law, 'ordinary')[0]
            knots = [0, 2, 1, 4, 3] + list(range(5, len(rows)))
            yield f'five-knot census input 3097 {law} round {i}', rows, lift(rows, knots), law
    rows = forbid.supports_of((4, [(0, 1, 1), (1, 2, 1), (2, 3, 1), (0, 3, 1)], [2] * 4))
    for law in ('parity', 'nae'):
        yield f'four-knot ring {law} start', rows, lift(rows, [2, 3, 0, 1]), law


if __name__ == '__main__':
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    out = {}
    for i, (name, rows, perm, law) in enumerate(cases()):
        if limit is not None and i >= limit:
            break
        out[name] = inspect(rows, perm, law)
    print(json.dumps(out, indent=1))
