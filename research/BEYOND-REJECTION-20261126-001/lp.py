"""lp.py: part A of BEYOND-REJECTION-20261126-001 (README.md). The earlier edit study's whole-round preparation
(WHOLE-STAGE-SETTINGS-20261120-001C, its result.md) at the level of the readers' records: four preparations (u, v),
Alice's three old terminal values t, Bob's the same values carried through the correspondences, permuted by the net
interchange of P^u Q^v P^u Q^v under parity (identity unless u = v = 1, then a cycle of the three), or any values under
not-all-equal (every combination is allowed there). A free address x (y) funds the round exactly when x = u and y = v;
otherwise it stalls. Each reader reads 1 exactly when its round is funded and its designated terminal (the first) is 1.
A reader's complete record: its own preparation bit, its three terminals, whether its round was funded.

The weighting is any nonnegative weighting of the preparation's worlds (its allowed old states), so on these records any
distribution on the allowed (u, v, t_A, t_B). Three questions, each a linear program solved exactly:
  1. the earlier uniform weighting (calibration: must give 9/4);
  2. the largest CHSH with fixed addresses and every complete record unchanged by the far address;
  3. the same, with every sender policy allowed: the sender's address any function of its own visible record (its
     preparation bit and terminals), and the receiver's complete record unchanged by the sender's choice of policy.
     Policy no-signalling is equivalent to: the receiver's record jointly with the sender's visible record does not
     depend on the sender's address.
  With --hidden, question 3 lets a policy read only the sender's terminals (its shortage hidden from it)."""
import itertools, sys
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog

T = list(itertools.product((0, 1), repeat=3))
CYCLE = (2, 0, 1)          # (PQ)^2 with P = (0 1), Q = (1 2): label i is carried to CYCLE[i]


def worlds(law):
    out = []
    for u, v in itertools.product((0, 1), repeat=2):
        for ta in T:
            if law == 'parity':
                if u and v:
                    tb = tuple(ta[CYCLE.index(i)] for i in range(3))
                else:
                    tb = ta
                out.append((u, v, ta, tb))
            else:
                for tb in T: out.append((u, v, ta, tb))
    return out


def outcome(w, x, y):
    u, v, ta, tb = w
    f = int(x == u and y == v)
    return f, (f & ta[0], f & tb[0])


def rec_a(w, x, y): u, v, ta, tb = w; return (u, ta, outcome(w, x, y)[0])
def rec_b(w, x, y): u, v, ta, tb = w; return (v, tb, outcome(w, x, y)[0])
HIDDEN = '--hidden' in sys.argv        # the sender's policy reads only its terminals, not its preparation bit


def vis_a(w): return w[2] if HIDDEN else (w[0], w[2])
def vis_b(w): return w[3] if HIDDEN else (w[1], w[3])


def corr_rows(W, x, y):
    return [1 if outcome(w, x, y)[1][0] == outcome(w, x, y)[1][1] else -1 for w in W]


def ns_rows(W, policy):
    """equality rows: each reader's record distribution (jointly with the sender's visible record if policy) the
    same for either far address"""
    rows = []
    for side in (0, 1):
        for own in (0, 1):
            keys = {}
            for i, w in enumerate(W):
                for far in (0, 1):
                    x, y = (own, far) if side == 0 else (far, own)
                    r = rec_a(w, x, y) if side == 0 else rec_b(w, x, y)
                    if policy: r = (r, vis_b(w) if side == 0 else vis_a(w))
                    keys.setdefault(r, [[0] * len(W), [0] * len(W)])[far][i] += 1
            for r, (k0, k1) in keys.items():
                rows.append([a - b for a, b in zip(k0, k1)])
    return rows


def solve(law, policy):
    W = worlds(law)
    best = None
    for signs in itertools.product((1, -1), repeat=4):
        if signs.count(-1) % 2 == 0: continue
        c = np.zeros(len(W))
        for s, (x, y) in zip(signs, itertools.product((0, 1), repeat=2)):
            c -= s * np.array(corr_rows(W, x, y))
        A = np.array(ns_rows(W, policy) + [[1] * len(W)], dtype=float)
        b = np.zeros(len(A)); b[-1] = 1
        r = linprog(c, A_eq=A, b_eq=b, bounds=(0, None), method='highs')
        if r.status != 0: continue
        if best is None or -r.fun > best[0]: best = (-r.fun, r.x, signs)
    return best, W


def exact(W, p, signs, policy):
    p = [Fraction(x).limit_denominator(1000) for x in p]
    tot = sum(p); p = [x / tot for x in p]
    ok = all(sum(a * b for a, b in zip(row, p)) == 0 for row in ns_rows(W, policy))
    s = sum(sg * sum(q * cr for q, cr in zip(p, corr_rows(W, x, y))) for sg, (x, y) in zip(signs, itertools.product((0, 1), repeat=2)))
    return s, ok, p


if __name__ == '__main__':
    for law in ('parity', 'nae'):
        W = worlds(law)
        uni = [Fraction(1, len(W))] * len(W) if law == 'parity' else None
        if uni:
            E = [sum(q * cr for q, cr in zip(uni, corr_rows(W, x, y))) for x, y in itertools.product((0, 1), repeat=2)]
            print(law, 'uniform weighting: correlations', [str(e) for e in E], 'CHSH', E[0] + E[1] + E[2] - E[3])
        for policy in (False, True):
            best, W = solve(law, policy)
            if best is None:
                print(law, 'every sender policy' if policy else 'fixed addresses', ': no weighting satisfies the constraints'); continue
            s, ok, p = exact(W, best[1], best[2], policy)
            support = [(w, str(q)) for w, q in zip(W, p) if q]
            print(law, 'every sender policy' if policy else 'fixed addresses', ': largest CHSH %.6f, exact %s, constraints hold exactly: %s' % (best[0], s, ok))
            print('   signs', best[2], 'support', support[:12], '...' if len(support) > 12 else '')
