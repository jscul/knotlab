"""lp_signed.py: the advisor's number for part A (README.md). Drop nonnegativity from lp.py's weighting: a signed
weighting of the preparation's worlds, with every observable probability nonnegative (the joint distribution of the two
complete records in each of the four address pairs), every complete record unchanged by every sender policy, and CHSH
at least a target s. The least total negative mass for each target, exactly enough to show how much cancellation the
whole-round response would need. With --hidden, a sender policy reads only its terminals (lp.py)."""
import itertools
import numpy as np
from scipy.optimize import linprog
import lp

if __name__ == '__main__':
    for law in ('parity', 'nae'):
        W = lp.worlds(law); n = len(W)
        eq = lp.ns_rows(W, True)
        # observable cells: (x, y, record A, record B) -> rows of a nonnegativity constraint
        cells = {}
        for i, w in enumerate(W):
            for x, y in itertools.product((0, 1), repeat=2):
                cells.setdefault((x, y, lp.rec_a(w, x, y), lp.rec_b(w, x, y)), [0] * n)[i] += 1
        for s in (2.0, 2.001, 2.25, 2.5, 2 * 2 ** 0.5, 3.0, 4.0):
            # variables: p_plus (n), p_minus (n); minimize sum p_minus
            c = np.concatenate([np.zeros(n), np.ones(n)])
            A_eq = [list(r) + [-v for v in r] for r in eq] + [[1] * n + [-1] * n]
            b_eq = [0] * len(eq) + [1]
            A_ub = [[-v for v in r] + list(r) for r in cells.values()]          # every observable cell >= 0
            b_ub = [0] * len(cells)
            ch = np.zeros(n)
            for sg, (x, y) in zip((1, 1, 1, -1), itertools.product((0, 1), repeat=2)):
                ch += sg * np.array(lp.corr_rows(W, x, y))
            A_ub.append(list(-ch) + list(ch)); b_ub.append(-s)                   # CHSH >= s
            r = linprog(c, A_ub=np.array(A_ub, float), b_ub=b_ub, A_eq=np.array(A_eq, float), b_eq=b_eq, bounds=(0, None), method='highs')
            print(law, 'CHSH at least %.4f:' % s, 'least negative mass %.6f' % r.fun if r.status == 0 else 'no signed weighting (status %d)' % r.status)
