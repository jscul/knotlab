"""Exact series of the cover-animal model H by the block-tree recursion.
Blocks: K2 = Gamma edges in no filled triangle; K3 = filled triangles.  U(B, z) = y * prod_{B' at z, B' != B} Phi(B', z),
Phi(K2{z,w}, z) = 1 + U(K2, w), Phi(K3{z,w1,w2}, z) = (1 + U(K3,w1))(1 + U(K3,w2)).  Orbits of connected sets:
C = sum_x A_x - sum_K2 U_a U_b - sum_K3 (U_aU_b + U_aU_c + U_bU_c + 2 U_aU_bU_c), A_x = y prod_{B at x} Phi(B, x).
C = sum_t c(t) y^(t+1)."""
from collections import defaultdict
def mul(a, b, N):
    out = [0] * (N + 1)
    for i, x in enumerate(a):
        if x:
            for j in range(0, N + 1 - i):
                if b[j]: out[i + j] += x * b[j]
    return out
def add(a, b): return [x + y for x, y in zip(a, b)]
def one(N): return [1] + [0] * N
def shift(a, N): return [0] + a[:N]
def series(n, E, tri, N):
    tris = [tuple(t) for t, _ in tri]
    in_tri = set()
    for a, b, c in tris:
        for p in [(a, b), (b, c), (a, c)]: in_tri.add(tuple(sorted(p)))
    blocks = [('K2', tuple(sorted(e))) for e in E if tuple(sorted(e)) not in in_tri] + [('K3', t) for t in tris]
    at = defaultdict(list)
    for B in blocks:
        for z in B[1]: at[z].append(B)
    U = {(B, z): [0] * (N + 1) for B in blocks for z in B[1]}
    def phi(B, z, U):
        others = [w for w in B[1] if w != z]
        r = one(N)
        for w in others: r = mul(r, add(one(N), U[(B, w)]), N)
        return r
    for it in range(N + 1):
        new = {}
        for (B, z) in U:
            r = one(N)
            for B2 in at[z]:
                if B2 != B: r = mul(r, phi(B2, z, U), N)
            new[(B, z)] = shift(r, N)
        U = new
    C = [0] * (N + 1)
    for x in range(n):
        r = one(N)
        for B in at[x]: r = mul(r, phi(B, x, U), N)
        C = add(C, shift(r, N))
    for B in blocks:
        vs = B[1]
        if B[0] == 'K2':
            C = add(C, [-v for v in mul(U[(B, vs[0])], U[(B, vs[1])], N)])
        else:
            a, b, c = [U[(B, v)] for v in vs]
            s = add(add(mul(a, b, N), mul(a, c, N)), mul(b, c, N))
            s = add(s, [2 * v for v in mul(mul(a, b, N), c, N)])
            C = add(C, [-v for v in s])
    return C[1:]   # c(0), c(1), ...
if __name__ == '__main__':
    import sys
    from gamma import complex_of
    import joinlib as J
    R = J.ring_edges(5)
    sz, E, big, tri = complex_of(10, R + J.ring_edges(5, 5) + [(0, 5)])
    print(series(10, E, tri, 20))
    print([10, 14, 24, 42, 78, 154, 310, 638, 1346, 2888, 6278, 13822, 30776, 69168, 156748, 357928])
