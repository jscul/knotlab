"""Part C: clusters of the unrolled candidate map by size, split by which parts of the start their points lie in (brute force on
the cover, walk normal forms; RING-PAIR-20261119-001's pilot animals.py, with each cluster's parts recorded).
Deck orbits are counted as sum over root points x of (clusters containing x) / size."""
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/RING-PAIR-20261119-001B/RING-PAIR-20261119-001B-E001_cover/pilot'))
sys.path.insert(0, str(ROOT / 'experiments/RING-PAIR-20261119-001B/RING-PAIR-20261119-001B-E001_cover'))
import animals  # noqa: E402
import covermodel as M  # noqa: E402


def shares(n, edges, part_of, N):
    """part_of: knot -> part label.  Returns {size: {frozenset(parts): orbit count}} for sizes 1..N (bare starts in RING-PAIR's
    scope; the complex is the blocks of covermodel, given to the walk as pairs within each block and triangles... here every
    block is a full simplex, so the walk complex's filled cells are all triangles inside blocks)."""
    nv, B = M.blocks_of(n, edges)
    E = sorted({tuple(sorted(p)) for b in B for p in __import__('itertools').combinations(b, 2)})
    tri = [(t, []) for b in B for t in __import__('itertools').combinations(b, 3)]
    nbrs = animals.make(nv, E, tri)
    out = defaultdict(lambda: defaultdict(Fraction))
    for x in range(nv):
        def rec(cur, untried, seen, size):
            parts = frozenset(part_of[v[-1]] for v in cur)
            out[size][parts] += Fraction(1, size)
            if size == N:
                return
            untried = list(untried)
            while untried:
                v = untried.pop()
                new = [u for u in nbrs(v) if u not in seen]
                rec(cur | {v}, untried + new, seen | set(new), size + 1)
        root = (x,)
        rec(frozenset([root]), list(nbrs(root)), {root} | set(nbrs(root)), 1)
    return {k: {tuple(sorted(p)): int(c) if c.denominator == 1 else float(c) for p, c in v.items()} for k, v in out.items()}


def shares_general(sizes, edges, part_of, N):
    """As shares, for any start in CLUSTER-ALL-20261119-001's scope without hyperedges or relays: the complex of clusters.py's blocks
    with its pendants drawn as points (a leaf) or paths of N points (an endless chain; a point with two chains for open = 1).
    Clusters must contain a knot; orbits are counted as sum over knot roots of (clusters containing x) / (knots in the cluster).
    Pendant points take their knot's part label."""
    import itertools
    sys.path.insert(0, str(ROOT / 'experiments/CLUSTER-ALL-20261119-001B/CLUSTER-ALL-20261119-001B-E001_census'))
    import clusters as Cl
    A = Cl.analyse(sizes, edges)
    assert A['scope'] and not A['stall'] and not A.get('hyper')
    n = A['n']
    E = set()
    for i, b in enumerate(A['blocks']):
        E |= {tuple(sorted(p)) for p in A['bedges'][i]}
    tri = [(t, []) for i, b in enumerate(A['blocks']) for t in itertools.combinations(b, 3)
           if all(tuple(sorted(p)) in A['bedges'][i] for p in itertools.combinations(t, 2))]
    lab = dict(part_of)
    k = n
    for w, kinds in A['pend'].items():
        for kind in kinds:
            if kind == 0:
                E.add((w, k)); lab[k] = part_of[w]; k += 1
            else:
                for _ in range(1 if kind == 1 else 2):
                    prev = w
                    for _ in range(N):
                        E.add((prev, k)); lab[k] = part_of[w]; prev = k; k += 1
    nbrs = animals.make(k, sorted(E), tri)
    knots = set(A['live'])
    out = defaultdict(lambda: defaultdict(Fraction))
    for x in knots:
        def rec(cur, untried, seen, size):
            kn = sum(1 for v in cur if v[-1] in knots)
            parts = frozenset(lab[v[-1]] for v in cur)
            out[size][parts] += Fraction(1, kn)
            if size == N:
                return
            untried = list(untried)
            while untried:
                v = untried.pop()
                new = [u for u in nbrs(v) if u not in seen]
                rec(cur | {v}, untried + new, seen | set(new), size + 1)
        root = (x,)
        rec(frozenset([root]), list(nbrs(root)), {root} | set(nbrs(root)), 1)
    return {k2: {tuple(sorted(p)): (int(c) if c.denominator == 1 else float(c)) for p, c in v.items()} for k2, v in out.items()}
