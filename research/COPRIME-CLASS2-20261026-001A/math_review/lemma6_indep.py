"""Independent check of Lemma 6 (TRIPLE-PRODUCT-20261026-001D): for A = sum_e (x_u + x_v) ^ p_e ^ s_e on F_q^{n+2m},
N(A) = #{(a,b): A(a,b,.) = 0} = q^{2m-n} Z(q^3, q^2-1), and Z = Q^k v^{n-k} T(1+Q/v, 1+v).
Written from scratch (no repo code). q in {2, 4}."""
import itertools, sys
from fractions import Fraction

# F4 = {0,1,2,3}, 2 = w, 3 = w^2 = w + 1
LOG = {1: 0, 2: 1, 3: 2}; EXP = [1, 2, 3]
def m4(a, b):
    return 0 if a == 0 or b == 0 else EXP[(LOG[a] + LOG[b]) % 3]
def inv4(a):
    return EXP[(-LOG[a]) % 3]
def mul(q):
    return (lambda a, b: a & b) if q == 2 else m4
def inv(q):
    return (lambda a: 1) if q == 2 else inv4

def rank(rows, q):
    rows = [r[:] for r in rows]
    f, iv = mul(q), inv(q)
    rk, ncol = 0, len(rows[0]) if rows else 0
    for c in range(ncol):
        piv = next((i for i in range(rk, len(rows)) if rows[i][c]), None)
        if piv is None:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        s = iv(rows[rk][c]); rows[rk] = [f(s, x) for x in rows[rk]]
        for i in range(len(rows)):
            if i != rk and rows[i][c]:
                g = rows[i][c]; rows[i] = [x ^ f(g, y) for x, y in zip(rows[i], rows[rk])]
        rk += 1
    return rk

def form_terms(n, edges):
    """list of (functional1, functional2, functional3) as coefficient vectors; det of the three"""
    d = n + 2 * len(edges)
    terms = []
    for e, (u, v) in enumerate(edges):
        l1 = [0] * d; l1[u] ^= 1; l1[v] ^= 1
        l2 = [0] * d; l2[n + 2 * e] = 1
        l3 = [0] * d; l3[n + 2 * e + 1] = 1
        terms.append((l1, l2, l3))
    return d, terms

def N_count(n, edges, q):
    f = mul(q)
    d, terms = form_terms(n, edges)
    # T(a, b, c) = sum_terms det[[l1(a), l1(b), l1(c)], [l2(a), ...], [l3(a), ...]]; char 2 so det = permanent
    def ev(l, x):
        s = 0
        for i, li in enumerate(l):
            if li and x[i]:
                s ^= f(li, x[i])
        return s
    basis = [[1 if i == j else 0 for i in range(d)] for j in range(d)]
    tot = 0
    for a in itertools.product(range(q), repeat=d):
        la = [[ev(l, a) for l in t] for t in terms]
        if not any(any(x) for x in la):
            tot += q ** d; continue
        # matrix M[b_j][c_k] = T(a, e_j, e_k)
        M = [[0] * d for _ in range(d)]
        for t, lat in zip(terms, la):
            if not any(lat):
                continue
            for j in range(d):
                lb = [t[r][j] for r in range(3)]
                if not any(lb):
                    continue
                for k in range(d):
                    lc = [t[r][k] for r in range(3)]
                    if not any(lc):
                        continue
                    s = 0
                    for p in itertools.permutations(range(3)):
                        s ^= f(f(lat[p[0]], lb[p[1]]), lc[p[2]])
                    M[j][k] ^= s
        tot += q ** (d - rank(M, q))
    return tot

def potts(n, edges, Q, v):
    tot = 0
    for s in itertools.product(range(Q), repeat=n):
        p = 1
        for a, b in edges:
            if s[a] == s[b]:
                p *= 1 + v
        tot += p
    return tot

def potts_fk(n, edges, Q, v):
    """Fortuin-Kasteleyn: sum_S Q^{k(S)} v^{|S|}"""
    tot = 0
    m = len(edges)
    for mask in range(1 << m):
        par = list(range(n))
        def fd(x):
            while par[x] != x:
                par[x] = par[par[x]]; x = par[x]
            return x
        cnt = 0
        for i in range(m):
            if mask >> i & 1:
                cnt += 1
                a, b = fd(edges[i][0]), fd(edges[i][1])
                if a != b:
                    par[a] = b
        k = len({fd(x) for x in range(n)})
        tot += Q ** k * v ** cnt
    return tot

def tutte(n, edges, x, y):
    m = len(edges)
    def rk(mask):
        par = list(range(n))
        def fd(z):
            while par[z] != z:
                par[z] = par[par[z]]; z = par[z]
            return z
        r = 0
        for i in range(m):
            if mask >> i & 1:
                a, b = fd(edges[i][0]), fd(edges[i][1])
                if a != b:
                    par[a] = b; r += 1
        return r
    rE = rk((1 << m) - 1)
    tot = Fraction(0)
    for mask in range(1 << m):
        r = rk(mask)
        tot += Fraction(x - 1) ** (rE - r) * Fraction(y - 1) ** (bin(mask).count('1') - r)
    return tot, n - rE

GRAPHS2 = {
    "C4": (4, [(0, 1), (1, 2), (2, 3), (3, 0)]),
    "K4": (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]),
    "loop+edge": (2, [(0, 0), (0, 1)]),
    "triple edge": (2, [(0, 1)] * 3),
    "star K13": (4, [(0, 1), (0, 2), (0, 3)]),
    "two components": (4, [(0, 1), (2, 3)]),
}
GRAPHS4 = {
    "loop+edge": (2, [(0, 0), (0, 1)]),
    "triple edge": (2, [(0, 1)] * 3),
    "P3": (3, [(0, 1), (1, 2)]),
}
ok = True
for q, G in ((2, GRAPHS2), (4, GRAPHS4)):
    Q, v = q ** 3, q * q - 1
    for name, (n, edges) in G.items():
        N = N_count(n, edges, q)
        Z = potts(n, edges, Q, v) if Q ** n <= 300000 else None
        Zfk = potts_fk(n, edges, Q, v)
        tv, k = tutte(n, edges, 1 + Fraction(Q, v), 1 + v)
        pred = Fraction(q) ** (2 * len(edges) - n) * Zfk
        good = (N == pred) and (Z is None or Z == Zfk) and Zfk == Q ** k * v ** (n - k) * tv
        ok &= good
        print(f"q={q} {name}: N={N} q^(2m-n)Z={pred} Z={Zfk} (direct {Z}) Tutte point ({1 + Fraction(Q, v)}, {1 + v}) ok={good}", flush=True)
print("ALL OK" if ok else "FAIL")
