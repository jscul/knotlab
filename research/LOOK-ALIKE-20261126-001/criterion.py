"""criterion.py: the criterion tried on phase 1, then frozen for phase 2 (README, addendum).
A local reader's VIEW of a start: in each reading, each kind of birth counted per round.  From round K on, each kind's
count is fitted by a polynomial of degree D - 1 (D the start's dimension) through rounds K - D + 1 .. K; the view is
FIXED BY ROUND K when that fit gives every later round read exactly.  The criterion predicts, for two starts of one
kind, whether their births are nested in each round after K from the fitted counts alone, and so the first round
r0 from which they agree up to the count."""
import json, collections
K = 8

def view(x, R):
    return [collections.Counter({json.dumps(k): v for k, v in row[R]}) for row in x['rows']]

def dim(x):
    return int(x['kind'].split()[1]) if x['kind'].startswith('dim') else None

def fit(counts, D, t):
    """Lagrange extrapolation of a polynomial of degree D-1 through rounds K-D+1..K (1-based) to round t"""
    xs = list(range(K - D + 1, K + 1)); ys = [counts[i - 1] for i in xs]
    tot = 0.0
    for i, xi in enumerate(xs):
        term = ys[i]
        for j, xj in enumerate(xs):
            if j != i: term *= (t - xj) / (xi - xj)
        tot += term
    return round(tot)

def predicted(x, R, upto):
    V = view(x, R); D = dim(x); kinds = set().union(*V[:K]) if len(V) >= K else set()
    out = []
    for t in range(1, upto + 1):
        if t <= K: out.append(V[t - 1])
        else: out.append(collections.Counter({k: fit([v[k] for v in V], D, t) for k in kinds if fit([v[k] for v in V], D, t) > 0}))
    return out

def fixed_by_K(x, R):
    V = view(x, R); P = predicted(x, R, len(V))
    return all(P[i] == V[i] for i in range(len(V)))

def first_nested(A, B, n):
    flags = [not (A[i] - B[i]) or not (B[i] - A[i]) for i in range(n)]
    k = n
    while k > 0 and flags[k - 1]: k -= 1
    return k + 1 if k < n else None
