"""SCALE-SHARE-20261119-001B: arrangements of n knots sampled uniformly over labelled descriptions (Metropolis, as the
TOUCH-CENSUS referee's six-knot sampler: one multiplicity or one size moved by one, feasible states kept), classified by the
cluster rule of CLUSTER-ALL-20261119-001B, and weighted to distinct arrangements by |Aut| / n!."""
import itertools
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CA = ROOT / 'experiments/CLUSTER-ALL-20261119-001B/CLUSTER-ALL-20261119-001B-E001_census'
sys.path.insert(0, str(CA))
import clusters as Cl  # noqa: E402
import dimension as D  # noqa: E402
J = Cl.J


def connected(n, M):
    seen, st = {0}, [0]
    while st:
        x = st.pop()
        for y in range(n):
            if M[x][y] and y not in seen:
                seen.add(y)
                st.append(y)
    return len(seen) == n


def chain(n, n_samples, seed, burn=None, thin=None, dense=False):
    """dense: start from a ring with every pair of neighbours sharing two distinctions (degrees 4), else from a path."""
    rng = random.Random(f'scale-share-{n}-{seed}')
    burn = burn or 400 * n * n
    thin = thin or 30 * n * n
    sizes = [5] * n
    M = [[0] * n for _ in range(n)]
    if dense:
        for i in range(n):
            M[i][(i + 1) % n] = M[(i + 1) % n][i] = 2
    else:
        for i in range(n - 1):
            M[i][i + 1] = M[i + 1][i] = 1
    pairs = list(itertools.combinations(range(n), 2))
    out, step = [], 0
    while len(out) < n_samples:
        step += 1
        if rng.random() < 0.7:
            i, j = rng.choice(pairs)
            m = M[i][j] + rng.choice((-1, 1))
            if m >= 0:
                old = M[i][j]
                M[i][j] = M[j][i] = m
                if not (sum(M[i]) <= sizes[i] and sum(M[j]) <= sizes[j] and connected(n, M)):
                    M[i][j] = M[j][i] = old
        else:
            i = rng.randrange(n)
            sz = sizes[i] + rng.choice((-1, 1))
            if 3 <= sz <= 5 and sum(M[i]) <= sz:
                sizes[i] = sz
        if step > burn and step % thin == 0:
            out.append((list(sizes), [row[:] for row in M]))
    return out


def edges_of(sizes, M):
    n = len(sizes)
    return list(sizes), [(i, j) for i in range(n) for j in range(i + 1, n) for _ in range(M[i][j])]


def automorphisms(sizes, M):
    """|Aut|: renamings keeping sizes and multiplicities, by refinement (backtracking within classes of equal size and degree
    profile)."""
    n = len(sizes)
    sig = [(sizes[i], tuple(sorted(M[i][j] for j in range(n) if j != i))) for i in range(n)]
    order = sorted(range(n), key=lambda i: sig[i])
    count = 0
    img = [None] * n
    used = [False] * n

    def ok(k, v):
        u = order[k]
        if sig[u] != sig[v]:
            return False
        for kk in range(k):
            w = order[kk]
            if M[u][w] != M[v][img[w]]:
                return False
        return True

    def rec(k):
        nonlocal count
        if k == n:
            count += 1
            return
        for v in range(n):
            if not used[v] and ok(k, v):
                used[v] = True
                img[order[k]] = v
                rec(k + 1)
                used[v] = False
    rec(0)
    return count


def break_shape(sizes, e):
    """The six-knot break of CLUSTER-ALL: a merged block (simplices sharing two knots) with a missing pair."""
    A = Cl.analyse(sizes, e)
    if not A.get('scope') or A.get('stall'):
        return False
    import itertools as it
    for i, B in enumerate(A['blocks']):
        if A['bedges'][i] is None:
            continue
        full = {tuple(sorted(p)) for p in it.combinations(B, 2)}
        if {tuple(sorted(p)) for p in A['bedges'][i]} != full:
            return True
    return False


def features(sizes, M):
    """Rule-free features: shared distinctions m, cycle rank m - n + 1, mean open places per knot; and the number of knots whose
    round-1 demand exceeds their open places."""
    n = len(sizes)
    sz, e = edges_of(sizes, M)
    m = len(e)
    sh = [sum(M[i]) for i in range(n)]
    opn = [sizes[i] - sh[i] for i in range(n)]
    live = [k for k in range(n) if opn[k] >= 1]
    P = J.S.from_junctions(J.stars_from(sz, e))
    d = [0] * n
    for g in P.groups_among(live):
        for j in g:
            d[j] += 1
    over = sum(1 for k in live if d[k] > opn[k])
    return {'m': m, 'cycle_rank': m - n + 1, 'open_per_knot': sum(opn) / n, 'over_demanded': over}


def classify(sizes, M):
    sz, e = edges_of(sizes, M)
    A = Cl.analyse(sz, e)
    if not A['scope']:
        return 'out of scope'
    if A['stall']:
        return 'stall'
    tag = 'break shape' if break_shape(sz, e) else ''
    g = D.growth_class(sz, e)
    if g == 0:
        cls = 'closes'
    elif g == 'exp':
        cls = 'ring (exponential)'
    elif g == 'unsettled':
        cls = 'unsettled'
    else:
        cls = f'dimension {g}'
    return cls + (' [break shape]' if tag else '')
