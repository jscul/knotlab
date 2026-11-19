"""WEIGHTINGS-20261119-001B: three weightings of starts other than SCALE-SHARE's, frozen before any sample was classified.

Each returns (sizes, edges) for a connected start of n knots; edges list one entry per shared distinction.
- tree: a uniform random labelled tree on n knots (Pruefer code), every knot at the bare size max(3, shared + round-1 demand), no
  surplus.  Bare sizes never stall: this is the weighting where stalls do not dominate.
- tree+: the same tree plus r extra lines between uniformly chosen non-adjacent pairs, r Poisson with mean 1, at bare sizes: cycles
  of every length, mostly long.
- grow: knots added one at a time, A106's "growth process that adds knots one at a time".  Knot 0 has k places, k uniform in
  {3, 4, 5}; each new knot draws k the same way, shares one distinction with an existing knot chosen in proportion to its open
  places, and with probability 1/3 one more with a second existing knot chosen the same way (if it has an open place left); places
  are fixed, so stalls can occur.  If no existing knot has an open place the start is redrawn.
- tree-sP (P = 25, 50, 100, added on the advisor's advice before the freeze): the bare tree, with each knot given one surplus
  distinction independently with probability P%: the one-knob path from the bare tree towards crowded open places.
- config (added on the advisor's advice before the freeze): a configuration model.  Each knot has k places, k uniform in {3, 4, 5};
  the places are joined by a uniformly random partial matching (every partial matching of the places equally likely, so the number
  of lines is weighted by its count of matchings), conditioned on no line joining two places of one knot and on a connected start.
  It weights descriptions by their place labellings rather than counting each description once, as SCALE-SHARE did.
The theorem's reader is SCALE-THEOREM's (scalelib.theorem_class), i.e. DOUBLE-IDENT's class and rule."""
import importlib.util
import math
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_spec = importlib.util.spec_from_file_location('st_lib', ROOT / 'experiments/SCALE-THEOREM-20261119-001B/SCALE-THEOREM-20261119-001B-E001_shares/scalelib.py')
SL = importlib.util.module_from_spec(_spec)
sys.modules['st_lib'] = SL
_spec.loader.exec_module(SL)
J = SL.DC.J


def prufer_tree(n, rng):
    if n == 1:
        return []
    if n == 2:
        return [(0, 1)]
    code = [rng.randrange(n) for _ in range(n - 2)]
    deg = [1] * n
    for x in code:
        deg[x] += 1
    edges = []
    for x in code:
        leaf = min(i for i in range(n) if deg[i] == 1)
        edges.append(tuple(sorted((leaf, x))))
        deg[leaf] -= 1
        deg[x] -= 1
    u, v = [i for i in range(n) if deg[i] == 1]
    edges.append((u, v))
    return edges


def poisson(lam, rng):
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


def bare(n, edges):
    return J.bare_sizes(n, edges)


def sample(kind, n, rng):
    if kind == 'tree':
        e = prufer_tree(n, rng)
        return bare(n, e), e
    if kind.startswith('tree-s'):
        q = int(kind[6:]) / 100
        e = prufer_tree(n, rng)
        sur = {str(k): 1 for k in range(n) if rng.random() < q}
        return J.bare_sizes(n, e, sur), e
    if kind == 'config':
        while True:
            sizes = [rng.choice((3, 4, 5)) for _ in range(n)]
            owner = [k for k in range(n) for _ in range(sizes[k])]
            N = len(owner)
            logw = [math.lgamma(N + 1) - math.lgamma(N - 2 * m + 1) - math.lgamma(m + 1) - m * math.log(2) for m in range(N // 2 + 1)]
            top = max(logw)
            m = rng.choices(range(N // 2 + 1), weights=[math.exp(x - top) for x in logw])[0]
            pts = rng.sample(range(N), 2 * m)
            e = [tuple(sorted((owner[pts[2 * i]], owner[pts[2 * i + 1]]))) for i in range(m)]
            if any(a == b for a, b in e) or not J.connected(n, e):
                continue
            return sizes, sorted(e)
    if kind == 'tree+':
        e = prufer_tree(n, rng)
        have = set(e)
        non = [(i, j) for i in range(n) for j in range(i + 1, n) if (i, j) not in have]
        r = min(poisson(1.0, rng), len(non))
        e = e + rng.sample(non, r)
        return bare(n, e), e
    if kind == 'grow':
        while True:
            sizes = [rng.choice((3, 4, 5))]
            opn = [sizes[0]]
            e = []
            ok = True
            for k in range(1, n):
                sizes.append(rng.choice((3, 4, 5)))
                opn.append(sizes[-1])
                tot = sum(opn[:k])
                if tot == 0:
                    ok = False
                    break
                links = 2 if rng.random() < 1 / 3 else 1
                used = set()
                for _ in range(links):
                    cand = [i for i in range(k) if opn[i] > 0 and i not in used]
                    if not cand or opn[k] == 0:
                        break
                    w = [opn[i] for i in cand]
                    i = rng.choices(cand, weights=w)[0]
                    e.append((i, k))
                    opn[i] -= 1
                    opn[k] -= 1
                    used.add(i)
            if ok:
                return sizes, e
    raise ValueError(kind)


def canon(sizes, edges):
    n = len(sizes)
    M = [[0] * n for _ in range(n)]
    for a, b in edges:
        M[a][b] += 1
        M[b][a] += 1
    return SL.SC.edges_of(sizes, M)


def classify(sizes, edges):
    """DOUBLE-IDENT's fine class ('stall', 'out', 'none', 'one loose', 'in') and, outside stalls and 'out', the theorem's growth
    class with its reason (dims.predict), on the canonical edge list SCALE-THEOREM used."""
    sz, e = canon(sizes, edges)
    c = SL.DC.classify(sz, e)
    if c in ('stall', 'out'):
        return c, None, None, sz, e
    D, why = SL.DM.predict(sz, e)
    return c, D, why, sz, e
