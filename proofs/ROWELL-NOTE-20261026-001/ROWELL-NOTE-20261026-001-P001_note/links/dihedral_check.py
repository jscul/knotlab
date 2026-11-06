"""Same reduction for the dihedral group D_p = F_p x| F_2 (p odd prime): end-to-end check.
Local knot: T(2,p) (closure of sigma^p) instead of the trefoil (weight p on reflection
meridians, 1 otherwise); 2-cables of the edge components; expected
     B_0 = p^{2m} Z(Gamma; q=p, y=2).
H is computed by the sign-sector method over F_p (sector = which components have
reflection meridians); the sector method is first checked against brute force."""
import sys, itertools
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, '.')
from braidlab import comp_index, components, tie_trefoils, cable
from potts_reduction import L_gamma, potts
from test_surgery import solve

P = int(sys.argv[1]) if len(sys.argv) > 1 else 5


def rank_mod(M, p):
    A = np.array(M, dtype=np.int64) % p
    r = 0
    rows, cols = A.shape
    for c in range(cols):
        piv = next((i for i in range(r, rows) if A[i, c]), None)
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        A[r] = (A[r] * pow(int(A[r, c]), p - 2, p)) % p
        for i in range(rows):
            if i != r and A[i, c]:
                A[i] = (A[i] - A[i, c] * A[r]) % p
        r += 1
        if r == rows:
            break
    return r


def sector_count_p(word, n, signs, p):
    vec = [np.eye(n, dtype=np.int64)[q] for q in range(n)]
    sg = list(signs)
    for g in word:
        i = abs(g) - 1
        va, sa, vb, sb = vec[i], sg[i], vec[i + 1], sg[i + 1]
        if g > 0:
            nx = ((vb if sa == 0 else -vb) + (0 if sb == 0 else 2) * va) % p
            vec[i], sg[i], vec[i + 1], sg[i + 1] = nx, sb, va, sa
        else:
            xo = (-vb if sb == 0 else vb) % p
            nx = ((va if sb == 0 else -va) + (0 if sa == 0 else 2) * xo) % p
            vec[i], sg[i], vec[i + 1], sg[i + 1] = vb, sb, nx, sa
    M = np.array(vec, dtype=np.int64)
    return p ** (n - rank_mod((M - np.eye(n, dtype=np.int64)) % p, p))


_W = None
def _init(w):
    global _W
    _W = w
def _sec(psi):
    word, n, ci, p = _W
    return sector_count_p(word, n, [psi[ci[q]] for q in range(n)], p)


def count_psi_p(word, n, p, procs=24):
    comps, ci = comp_index(word, n)
    pats = list(itertools.product((0, 1), repeat=len(comps)))
    with Pool(procs, initializer=_init, initargs=((word, n, ci, p),)) as pool:
        return sum(pool.map(_sec, pats, chunksize=max(1, len(pats) // 96)))


def brute_Dp(word, n, p):
    # elements (x, s): z -> (-1)^s z + x
    el = [(x, s) for s in (0, 1) for x in range(p)]
    idx = {g: i for i, g in enumerate(el)}
    mul = lambda g, h: ((g[0] + (h[0] if g[1] == 0 else -h[0])) % p, (g[1] + h[1]) % 2)
    inv = lambda g: ((-g[0] if g[1] == 0 else g[0]) % p, g[1])
    MUL = np.array([[idx[mul(a, b)] for b in el] for a in el])
    INV = np.array([idx[inv(a)] for a in el])
    tup = np.array(list(itertools.product(range(2 * p), repeat=n)), dtype=np.int64)
    cur = tup.copy()
    for g in word:
        i = abs(g) - 1
        a, b = cur[:, i].copy(), cur[:, i + 1].copy()
        if g > 0:
            cur[:, i] = MUL[MUL[a, b], INV[a]]; cur[:, i + 1] = a
        else:
            cur[:, i] = b; cur[:, i + 1] = MUL[MUL[INV[b], a], b]
    return int(np.all(cur == tup, axis=1).sum())


if __name__ == '__main__':
    import random
    random.seed(5)
    for t in range(40):
        n = random.choice([2, 3, 4])
        w = [random.choice([1, -1]) * random.randint(1, n - 1) for _ in range(random.randint(0, 8))]
        assert brute_Dp(w, n, P) == count_psi_p(w, n, P, procs=2), w
    print(f'D_{P}: sector method == brute force on 40 random braids')
    for name, (n, edges) in {'K2': (2, [(0, 1)]), 'P3': (3, [(0, 1), (1, 2)]), 'K3': (3, [(0, 1), (1, 2), (0, 2)])}.items():
        m, c = len(edges), n + len(edges)
        Hs = []
        for j in range(c + 1):
            w, N = L_gamma(n, edges)
            w, N, reps = tie_trefoils(w, N, list(range(c)), j, twists=P)
            comps = components(w, N)
            rc = [next(k for k, cc in enumerate(comps) if r in cc) for r in reps]
            nc = [1] * len(comps)
            for idx in range(m):
                nc[rc[n + idx]] = 2
            cw, cn = cable(w, N, nc, [0] * len(comps))
            Hs.append(count_psi_p(cw, cn, P))
        B = solve([P ** s for s in range(c + 1)], Hs)
        target = P ** (2 * m) * potts(n, edges, P, 2)
        print(f'D_{P} {name}: B_0 from link counts = {B[0]}, p^(2m) Z(Gamma;p,2) = {target}', 'OK' if B[0] == target else 'FAIL')
