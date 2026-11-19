"""A loop's equation and ratio from the cluster rule's counts (LOOP-CATALOGUE-20261119-001B).

For a rational count (one loop), Berlekamp-Massey gives the least recurrence; its annihilator is factored over the integers
(sympy) and the factor holding the largest real root is the loop's equation, written in y = 1/x as the literature's return
equation would be.  For an algebraic count (two loops or more), no short recurrence exists, and the ratio is read from the counts
with the t^(-5/2) correction of tree-like animals (RING-PAIR-20261119-001)."""
import sys
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eddy as E  # noqa: E402
sys.path.insert(0, str(E.ROOT / 'experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins'))
import reclib as R  # noqa: E402

x, y = sp.symbols('x y')


def equation(sizes, edges, N=120):
    c = E.Cl.series(sizes, edges, N)
    if not isinstance(c, list):
        return {'kind': str(c)}
    rec = R.minimal_recurrence(c, starts=range(2, 30), spare=3)
    if rec is not None and rec[0] <= 30:
        L, st, p = rec
        P = sum(sp.Integer(q) * x ** k for k, q in enumerate(p))
        best = None
        for f, _ in sp.factor_list(P)[1]:
            roots = [complex(r) for r in sp.Poly(f, x).nroots(n=30)]
            real = [r.real for r in roots if abs(r.imag) < 1e-12]
            if real:
                top = max(real)
                if best is None or top > best[0]:
                    best = (top, f)
        if best is not None:
            f = best[1]
            d = sp.degree(f, x)
            g = sp.expand(sp.simplify(f.subs(x, 1 / y) * y ** d))
            return {'kind': 'rational', 'order': L, 'ratio': round(best[0], 6), 'factor_x': str(sp.expand(f)),
                    'equation_y': str(sp.factor(g)) + ' = 0', 'counts': c[:16]}
    t = N - 1
    r = c[t] / c[t - 1]
    lam = r * (t / (t - 1)) ** 2.5
    return {'kind': 'algebraic', 'ratio': round(lam, 4), 'raw_ratio': round(r, 4), 'counts': c[:16]}
