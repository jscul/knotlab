"""Post hoc, after referee R1: W read from every factor of the counts' minimal recurrence, not from the rate.

By the transfer argument the counts' generating function is P(y) + Q(y)/(1 - W(y)), with only powers of 1 - y in P's and Q's
denominators, so every factor of the minimal recurrence other than x - 1 (taken with its multiplicity, in y = 1/x) divides
den(W) - num(W).  Each rational start is given the smallest family member (posthoc.family's range and size key) that every factor
divides; a start no single member fits is reported as such.  The recurrence is found by exact Berlekamp-Massey over Q from round
t0 = 1, holding on every later term with 2L + 4 to spare.
python3 -B posthoc_full.py <runner out dir> [<ref out dir>] <out.json>"""
import importlib.util
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'scripts'))
from longrun import load_results  # noqa: E402

x, y = sp.symbols('x y')


def bm(seq):
    """Exact Berlekamp-Massey: the connection polynomial C (C[0] = 1) of the shortest recurrence."""
    s = [Fraction(v) for v in seq]
    C, B, L, m, b = [Fraction(1)], [Fraction(1)], 0, 1, Fraction(1)
    for n in range(len(s)):
        d = s[n] + sum(C[i] * s[n - i] for i in range(1, L + 1))
        if d == 0:
            m += 1
            continue
        T = C[:]
        coef = d / b
        C = C + [Fraction(0)] * (len(B) + m - len(C))
        for i, v in enumerate(B):
            C[i + m] -= coef * v
        if 2 * L <= n:
            L, B, b, m = n + 1 - L, T, d, 1
        else:
            m += 1
    return C[:L + 1], L


def recurrence(counts, t0=1):
    s = counts[t0:]
    for k in range(8, len(s) + 1):
        C, L = bm(s[:k])
        if len(s) - 2 * L < 2 * L + 4 and k == len(s):
            break
        if 2 * L + 4 <= k and all(sum(C[i] * s[n - i] for i in range(L + 1)) == 0 for n in range(L, len(s))):
            return C, L
    return None, None


def members():
    rows = []
    for L, a, b, c, d in itertools.product(range(1, 8), range(5), range(2), range(2), range(2)):
        num = y ** L * (1 + y) ** a * (1 + y + y ** 2) ** b * (1 + y * (1 + y) ** 2) ** c
        den = (1 - y) ** d
        ways = float('inf') if d else (2 ** a) * (3 ** b) * (5 ** c)
        if ways < 2:
            continue
        name = f'y^{L}' + (f' (1+y)^{a}' if a else '') + (' (1+y+y^2)' if b else '') + (' F_2' if c else '') + (' / (1-y)' if d else '')
        rows.append((L + a + 2 * b + 3 * c + d, name, sp.Poly(sp.expand(den - num), y)))
    return sorted(rows, key=lambda t: (t[0], t[1]))


def main():
    args = sys.argv[1:]
    dest = Path(args[-1])
    rows = []
    for d in args[:-1]:
        R = load_results(d)
        rows += [(c, r['result']) for c, r in sorted(R.items()) if r.get('status') == 'ok']
    fam = members()
    out = {'rational': 0, 'by_W': Counter(), 'by_rate_W_to_full_W': Counter(), 'starts': []}
    for cid, r in rows:
        rec = r.get('recurrence')
        if not rec or 'rate' not in rec:
            continue
        C, L = recurrence(r['counts'])
        if C is None:
            out['starts'].append({'case': cid, 'full_W': 'no recurrence found by this reader'})
            continue
        out['rational'] += 1
        char = sp.Poly(sum(sp.Rational(C[i].numerator, C[i].denominator) * x ** (L - i) for i in range(L + 1)), x)
        facs = [(f, m) for f, m in sp.factor_list(char.as_expr())[1] if sp.Poly(f, x) != sp.Poly(x - 1, x)]
        need = [(sp.Poly(sp.expand(y ** sp.degree(f, x) * f.subs(x, 1 / y)), y), m) for f, m in facs if sp.degree(f, x) > 0 and f != x]
        hit = None
        for _, name, P in fam:
            if all(sp.rem(P, g ** m).is_zero for g, m in need):
                hit = name
                break
        full = hit or 'no single member (two loops or more)'
        out['by_W'][full] += 1
        out['by_rate_W_to_full_W'][f"{rec.get('factor')} -> {full}"] += 1
        out['starts'].append({'case': cid, 'sizes': r['start']['sizes'], 'order': L, 'factors': [str(f) for f, _ in facs],
                              'rate_factor': rec.get('factor'), 'full_W': full})
    out['by_W'] = dict(out['by_W'])
    out['by_rate_W_to_full_W'] = dict(out['by_rate_W_to_full_W'])
    dest.write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != 'starts'}, indent=1))


if __name__ == '__main__':
    main()
