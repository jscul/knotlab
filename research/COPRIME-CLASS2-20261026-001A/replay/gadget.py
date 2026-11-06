"""Claim 5 (gadget lemma): for a graph with n vertices and m edges, the
alternating F4-trilinear form

    A = sum over edges e = uv of (x_u + x_v) ^ p_e ^ s_e     on F4^(n + 2m)

satisfies #{(a, b) : A(a, b, .) = 0} = 4^(2m - n) * Z(64, 15), where
Z(Q, v) = sum over s: V -> [Q] of prod over edges uv of (1 + v [s(u) = s(v)]).

Coordinates: x_v (v < n), then p_e = coordinate n + 2e, s_e = n + 2e + 1.
(f1 ^ f2 ^ f3)(a, b, c) = det of the 3x3 matrix [f_k(a); f_k(b); f_k(c)].

Independent replay code: written from scratch, standard library only.
"""
from itertools import product

from f4 import MUL, all_vectors, dot
from cohomology import det3, count_vanishing_pairs


def functionals(n, edges):
    D = n + 2 * len(edges)
    out = []
    for e, (u, v) in enumerate(edges):
        f1 = [0] * D
        f1[u] ^= 1
        f1[v] ^= 1
        f2 = [0] * D
        f2[n + 2 * e] = 1
        f3 = [0] * D
        f3[n + 2 * e + 1] = 1
        out.append((f1, f2, f3))
    return D, out


def form_value(fs, a, b, c):
    t = 0
    for f1, f2, f3 in fs:
        t ^= det3([dot(f1, a), dot(f2, a), dot(f3, a)],
                  [dot(f1, b), dot(f2, b), dot(f3, b)],
                  [dot(f1, c), dot(f2, c), dot(f3, c)])
    return t


def tensor(n, edges):
    """T[i][j] = (A(e_i, e_j, e_k))_k."""
    D, fs = functionals(n, edges)
    E = [[1 if t == i else 0 for t in range(D)] for i in range(D)]
    T = [[[form_value(fs, E[i], E[j], E[k]) for k in range(D)] for j in range(D)]
         for i in range(D)]
    return D, fs, T


def count_by_rank(n, edges):
    """Exact: sum over a of 4^(D - rank of b -> A(a, b, .))."""
    D, _, T = tensor(n, edges)
    return count_vanishing_pairs(T, D)


def count_naive(n, edges):
    """Literal double loop over all pairs (a, b); A(a, b, .) = 0 is tested on
    the basis vectors c = e_k (feasible only for tiny D)."""
    D, fs, T = tensor(n, edges)
    total = 0
    for a in all_vectors(D):
        # functional b -> (A(a, b, e_k))_k as a D x D matrix, built once per a
        rows = [[0] * D for _ in range(D)]
        for i, ai in enumerate(a):
            if ai:
                for j in range(D):
                    for k in range(D):
                        rows[j][k] ^= MUL[ai][T[i][j][k]]
        for b in all_vectors(D):
            ok = True
            for k in range(D):
                s = 0
                for j, bj in enumerate(b):
                    if bj:
                        s ^= MUL[bj][rows[j][k]]
                if s:
                    ok = False
                    break
            total += ok
    return total


def check_alternating(n, edges, samples=200, seed=5):
    """A(a, a, c) = A(a, c, c) = 0 and symmetric under transpositions (char 2)."""
    import random
    rng = random.Random(seed)
    D, fs = functionals(n, edges)
    for _ in range(samples):
        a, b, c = ([rng.randrange(4) for _ in range(D)] for _ in range(3))
        v = form_value(fs, a, b, c)
        assert form_value(fs, a, a, c) == 0 and form_value(fs, a, c, c) == 0
        assert v == form_value(fs, b, a, c) == form_value(fs, a, c, b)


def potts_Z_bruteforce(n, edges, Q=64, v=15):
    total = 0
    for s in product(range(Q), repeat=n):
        w = 1
        for a, b in edges:
            if s[a] == s[b]:
                w *= 1 + v
        total += w
    return total


def potts_Z_fk(n, edges, Q=64, v=15):
    """Fortuin-Kasteleyn: sum over edge subsets S of v^|S| Q^(components)."""
    total = 0
    m = len(edges)
    for mask in range(1 << m):
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        k = 0
        for e in range(m):
            if mask >> e & 1:
                k += 1
                ra, rb = find(edges[e][0]), find(edges[e][1])
                if ra != rb:
                    parent[ra] = rb
        comps = sum(1 for x in range(n) if find(x) == x)
        total += v ** k * Q ** comps
    return total


GRAPHS = {
    'K2': (2, [(0, 1)]),
    'P3': (3, [(0, 1), (1, 2)]),
    'K3': (3, [(0, 1), (1, 2), (0, 2)]),
    # extras (multigraph and disconnected cases appear in the braid realisations)
    'double edge': (2, [(0, 1), (0, 1)]),
    'two disjoint edges': (4, [(0, 1), (2, 3)]),
    'star K1,3': (4, [(0, 1), (0, 2), (0, 3)]),
}


def count_naive_gray(n, edges):
    """Literal enumeration of all pairs (a, b) without any rank argument: for
    each a, walk b through F4^D = F2^(2D) in binary Gray-code order, keeping
    the vector (A(a, b, e_k))_k up to date by one XOR per step, and count the
    b where it is zero."""
    from f4 import pack, scale_bits
    D, _, T = tensor(n, edges)
    total = 0
    for a in all_vectors(D):
        rows = [[0] * D for _ in range(D)]
        for i, ai in enumerate(a):
            if ai:
                for j in range(D):
                    for k in range(D):
                        rows[j][k] ^= MUL[ai][T[i][j][k]]
        packed = [pack(r) for r in rows]
        # bit 2j of b's F2-coordinates adds 1*e_j, bit 2j+1 adds w*e_j
        steps = []
        for j in range(D):
            steps.append(packed[j])
            steps.append(scale_bits(2, *packed[j]))
        lo = hi = 0
        count = 1                                  # b = 0
        for t in range(1, 1 << (2 * D)):
            flip = (t & -t).bit_length() - 1       # Gray code: bit that changes
            slo, shi = steps[flip]
            lo ^= slo
            hi ^= shi
            if not (lo | hi):
                count += 1
        total += count
    return total
