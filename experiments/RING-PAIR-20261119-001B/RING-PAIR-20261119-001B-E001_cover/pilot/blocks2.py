"""Exact series of the cover model by the block-tree recursion, with complete blocks.
Model H: the candidate complex X of a bare start is the union, over knots w, of the full simplex on w's neighbours N(w) (every
two of them are candidates through w, every three a sunflower), plus a K2 block {r, o} for each surplus distinction o at r.
Junctions of round t = deck orbits of connected vertex sets of size t + 1 in the universal cover of X (a tree of these blocks),
containing a knot.
U(B, z) = y * prod_{B' at z, B' != B} Phi(B', z),  Phi(B, z) = prod_{w in B, w != z} (1 + U(B, w)).
C = sum_x A_x - sum_B sum_{S subset B, |S| >= 2} (|S| - 1) prod_{v in S} U(B, v),  A_x = y prod_{B at x} Phi(B, x)."""
import itertools
from collections import defaultdict
from blocks import mul, add, one, shift
def blocks_of(n, edges, pendants=()):
    nb = defaultdict(set)
    for a, b in edges:
        nb[a].add(b); nb[b].add(a)
    B = [tuple(sorted(nb[w])) for w in range(n) if len(nb[w]) >= 2]
    # every pair inside one block only (no two common neighbours)
    seen = {}
    for blk in B:
        for p in itertools.combinations(blk, 2):
            if p in seen: raise ValueError(f'pair {p} in two blocks {seen[p]} and {blk}')
            seen[p] = blk
    k = n
    for r in pendants:
        B.append((r, k)); k += 1
    return k, B
def series(nv, blocks, N, knots=None):
    at = defaultdict(list)
    for i, B in enumerate(blocks):
        for z in B: at[z].append(i)
    U = {(i, z): [0] * (N + 1) for i, B in enumerate(blocks) for z in B}
    def phi(i, z, U):
        r = one(N)
        for w in blocks[i]:
            if w != z: r = mul(r, add(one(N), U[(i, w)]), N)
        return r
    for it in range(N + 1):
        new = {}
        for (i, z) in U:
            r = one(N)
            for j in at[z]:
                if j != i: r = mul(r, phi(j, z, U), N)
            new[(i, z)] = shift(r, N)
        if new == U: break
        U = new
    C = [0] * (N + 1)
    for x in range(nv):
        r = one(N)
        for i in at[x]: r = mul(r, phi(i, x, U), N)
        C = add(C, shift(r, N))
    for i, B in enumerate(blocks):
        for m in range(2, len(B) + 1):
            for S in itertools.combinations(B, m):
                pr = one(N)
                for v in S: pr = mul(pr, U[(i, v)], N)
                C = add(C, [-(m - 1) * v for v in pr])
    return C[1:]
