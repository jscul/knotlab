"""Post hoc reading of BREAK-EDDIES-20261119-001B-E001 (after the frozen read-out; labelled so in the note).

B2*: the frozen W was read from the irreducible factor holding the largest root, which drops a factor the counts' series cancels
(x^7 - (1 + x)^2 = (x^2 + x + 1)(x^5 - x^4 + x^2 - x - 1)).  Here each rational start's rate is matched instead against the
catalogue's family W = y^L (1 + y)^a (1 + y + y^2)^b (1 + y(1 + y)^2)^c / (1 - y)^d, L = 1..7, a = 0..4, b, c, d = 0..1, with at
least two ways round; a match is to 10^-6.
python3 -B posthoc.py <runner out dir> [<ref out dir>] <out.json>"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'scripts'))
from longrun import load_results  # noqa: E402


def poly_mul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, z in enumerate(b):
            out[i + j] += x * z
    return out


def family():
    rows = []
    for L, a, b, c, d in itertools.product(range(1, 8), range(5), range(2), range(2), range(2)):
        num = [0] * L + [1]
        for _ in range(a):
            num = poly_mul(num, [1, 1])
        for _ in range(b):
            num = poly_mul(num, [1, 1, 1])
        for _ in range(c):
            num = poly_mul(num, [1, 1, 2, 1])
        den = [1, -1] if d else [1]
        # W = num / den = 1  <=>  num - den = 0
        p = list(num) + [0] * max(0, len(den) - len(num))
        for k, v in enumerate(den):
            p[k] -= v
        roots = [r.real for r in np.roots(p[::-1]) if abs(r.imag) < 1e-10 and 0 < r.real < 1]
        if not roots:
            continue
        ways = (2 ** a) * (3 ** b) * (5 ** c) if not d else float('inf')
        if ways < 2:
            continue
        name = f'y^{L}' + (f' (1+y)^{a}' if a else '') + (' (1+y+y^2)' if b else '') + (' F_2' if c else '') + (' / (1-y)' if d else '')
        rows.append((1 / min(roots), name, L + a + 2 * b + 3 * c))
    return rows


def main():
    args = sys.argv[1:]
    dest = Path(args[-1])
    rows = []
    for d in args[:-1]:
        R = load_results(d)
        rows += [r['result'] for c, r in sorted(R.items()) if r.get('status') == 'ok']
    fam = sorted(family(), key=lambda t: t[2])
    out = {'rational': 0, 'matched': 0, 'by_W': {}, 'unmatched': []}
    for r in rows:
        rec = r.get('recurrence')
        if not rec or 'rate' not in rec:
            continue
        out['rational'] += 1
        hit = next((name for rate, name, _ in fam if abs(rate - rec['rate']) < 1e-6), None)
        if hit:
            out['matched'] += 1
            out['by_W'][hit] = out['by_W'].get(hit, 0) + 1
        else:
            out['unmatched'].append([r['start']['sizes'], rec['rate'], rec.get('factor')])
    dest.write_text(json.dumps(out, indent=1))
    print(json.dumps(out)[:1500])


if __name__ == '__main__':
    main()
