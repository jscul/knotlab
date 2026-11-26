"""sides.py: a sign to the sides (SIDE-SIGN-20261126-001).

Meeting patterns made by ordinary growth, their swaps (renamings of order two that move a knot), the sides a swap
exchanges, and the labels and signed weightings of the study (README.md).  Growth is the forbidding study's canonical
engine with the ordinary count (FORBID-EDITS-20261126-001, forbid.py, arm 'ordinary'); the starts are its census.

    sides.py precount I0 I1 [--rounds R]     structure only: swaps, kinds of sides, sizes; a JSON line per stage
"""
import sys, json, itertools, collections
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FORBID = ROOT / 'research' / 'FORBID-EDITS-20261126-001'
AUT_CAP = 20000                 # automorphisms enumerated per stage at most; more is recorded as truncated


def load(path, name):
    spec = spec_from_file_location(name, path); module = module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module); return module


_forbid = None


def forbid():
    global _forbid
    if _forbid is None:
        argv = sys.argv; sys.argv = [argv[0]]
        _forbid = load(FORBID / 'forbid.py', 'forbid_for_sides')
        sys.argv = argv
    return _forbid


def census_starts():
    return [(s[0], tuple(tuple(m) for m in s[1]), tuple(s[2])) for s in json.loads((FORBID / 'starts.json').read_text())]


def grow_rounds(supports, law, rounds):
    """the stages after 0..rounds rounds of ordinary growth (fewer if it closes or stalls), and the last status"""
    F = forbid()
    stages, status = [tuple(tuple(r) for r in supports)], "alive"
    for _ in range(rounds):
        stage, info = F.grow(stages[-1], law, 'ordinary', F.ENGINE)
        if stage is None:
            status = info['status']; break
        stages.append(stage)
    return stages, status


# ---------------------------------------------------------------- the meeting pattern as knots, pairs and loose counts

class Pattern:
    def __init__(self, supports):
        self.supports = tuple(tuple(r) for r in supports)
        self.K = len(self.supports)
        self.dist = sorted({d for r in self.supports for d in r})
        self.index = {d: i for i, d in enumerate(self.dist)}
        self.D = len(self.dist)
        h = collections.defaultdict(list)
        for k, row in enumerate(self.supports):
            for d in row: h[d].append(k)
        self.holders = {d: tuple(v) for d, v in h.items()}
        assert all(len(v) in (1, 2) for v in self.holders.values())
        self.shared = collections.defaultdict(list)          # (k, l), k < l -> sorted distinctions
        self.loose = [[] for _ in range(self.K)]
        for d in self.dist:
            v = self.holders[d]
            if len(v) == 2: self.shared[tuple(sorted(v))].append(d)
            else: self.loose[v[0]].append(d)
        self.masks = [sum(1 << self.index[d] for d in row) for row in self.supports]

    def automorphisms(self, cap=AUT_CAP):
        """permutations of the knots keeping every pair's count of shared distinctions and every knot's loose count"""
        import networkx as nx
        from networkx.algorithms.isomorphism import GraphMatcher
        G = nx.Graph()
        for k in range(self.K): G.add_node(('k', k), c=('k', len(self.loose[k]), len(self.supports[k])))
        for (k, l), ds in self.shared.items():
            G.add_node(('e', k, l), c=('e', len(ds))); G.add_edge(('k', k), ('e', k, l)); G.add_edge(('k', l), ('e', k, l))
        GM = GraphMatcher(G, G, node_match=lambda a, b: a['c'] == b['c'])
        out, truncated = [], False
        for m in GM.isomorphisms_iter():
            out.append(tuple(m[('k', k)][1] for k in range(self.K)))
            if len(out) >= cap: truncated = True; break
        return out, truncated

    def lift(self, perm, maximal=False):
        """a renaming of the distinctions over the knot involution perm: shared distinctions in order, loose in order;
        where a pair or a knot is kept, the minimal lift fixes its distinctions and the maximal lift swaps them two by two"""
        sig = {}
        def pair_up(ds):
            for i, d in enumerate(ds):
                if maximal and i + 1 < len(ds) and i % 2 == 0: sig[d] = ds[i + 1]
                elif maximal and i % 2 == 1: sig[d] = ds[i - 1]
                else: sig[d] = d
        for (k, l), ds in self.shared.items():
            img = tuple(sorted((perm[k], perm[l])))
            if img == (k, l): pair_up(ds)
            else:
                for a, b in zip(ds, self.shared[img]): sig[a] = b
        for k in range(self.K):
            if perm[k] == k: pair_up(self.loose[k])
            else:
                for a, b in zip(self.loose[k], self.loose[perm[k]]): sig[a] = b
        assert all(sig[sig[d]] == d for d in self.dist)
        return sig

    def sides(self, perm, sig):
        """the side graph: moved knots, joined through a moved shared distinction.  Kinds: 'two' (two components,
        exchanged), 'several' (more, all exchanged in pairs), 'one' (some component kept: the sides cannot be told
        apart)."""
        moved = [k for k in range(self.K) if perm[k] != k]
        adj = {k: set() for k in moved}
        for (k, l), ds in self.shared.items():
            if k in adj and l in adj and any(sig[d] != d for d in ds): adj[k].add(l); adj[l].add(k)
        comp, comps = {}, []
        for k in moved:
            if k in comp: continue
            c, todo = len(comps), [k]; comp[k] = c; members = [k]
            while todo:
                for j in adj[todo.pop()]:
                    if j not in comp: comp[j] = c; todo.append(j); members.append(j)
            comps.append(sorted(members))
        kept = [c for c, m in enumerate(comps) if comp[perm[m[0]]] == c]
        kind = 'one' if kept else ('two' if len(comps) == 2 else 'several')
        return kind, comps

    def parity_dim(self):
        rows = list(self.masks); rank = 0; piv = []
        basis = []
        for r in rows:
            for b in basis: r = min(r, r ^ b)
            if r: basis.append(r)
        return self.D - len(basis)


def involutions(auts):
    ident = tuple(range(len(auts[0])))
    return [p for p in auts if p != ident and all(p[p[k]] == k for k in range(len(p)))]


# ---------------------------------------------------------------- allowed states, labels and signed weightings

STATE_CAP = 22          # states are enumerated when the parity dimension (parity) or the distinction count (NAE) is at most this


def parity_basis(P):
    """a basis of the allowed states under parity: assignments in which every knot holds an even number of 1s"""
    piv = {}                                             # pivot distinction -> reduced knot row
    for r in P.masks:
        for b, row in piv.items():
            if r >> b & 1: r ^= row
        if r:
            b = r.bit_length() - 1
            for c in list(piv):
                if piv[c] >> b & 1: piv[c] ^= r
            piv[b] = r
    free = [i for i in range(P.D) if i not in piv]
    basis = []
    for f in free:
        v = 1 << f
        for b, row in piv.items():
            if row >> f & 1: v |= 1 << b
        basis.append(v)
    return basis


def states(P, law):
    import numpy as np
    if law == 'parity':
        basis = parity_basis(P)
        if len(basis) > STATE_CAP: return None
        x = np.zeros(1, dtype=np.uint64)
        for v in basis: x = np.concatenate([x, x ^ np.uint64(v)])
        return np.sort(x)
    if P.D > STATE_CAP: return None
    x = np.arange(1 << P.D, dtype=np.uint64)
    ok = np.ones(len(x), dtype=bool)
    for m in P.masks:
        y = x & np.uint64(m); ok &= (y != 0) & (y != np.uint64(m))
    return x[ok]


def bits(x, idx):
    import numpy as np
    X = np.empty((len(x), len(idx)), dtype=np.int8)
    for j, i in enumerate(idx): X[:, j] = (x >> np.uint64(i)) & np.uint64(1)
    return X


def apply_sig(x, P, sig):
    """the swap applied to states given as masks"""
    import numpy as np
    y = np.zeros_like(x)
    for d in P.dist:
        i, j = P.index[d], P.index[sig[d]]
        y |= ((x >> np.uint64(i)) & np.uint64(1)) << np.uint64(j)
    return y


def weightings(P, sig, kind, comps, x, law):
    """the frozen weightings, each an int8 vector over the allowed states (README.md, 'What is weighted')"""
    import numpy as np
    full = np.uint64((1 << P.D) - 1)
    sx = apply_sig(x, P, sig)
    S = sx == x; A = sx == (x ^ full)
    pairs = sorted({tuple(sorted((P.index[d], P.index[sig[d]]))) for d in P.dist if sig[d] != d})
    out = {'U': np.ones(len(x), dtype=np.int8)}
    q1 = np.zeros(len(x), dtype=np.uint64); q0 = np.zeros(len(x), dtype=np.uint64)
    for i, j in pairs:
        a = (x >> np.uint64(i)) & np.uint64(1); b = (x >> np.uint64(j)) & np.uint64(1)
        q1 ^= a & b; q0 ^= (a ^ np.uint64(1)) & (b ^ np.uint64(1))
    out['W1'] = (1 - 2 * q1.astype(np.int8)).astype(np.int8)
    out['W1c'] = (1 - 2 * q0.astype(np.int8)).astype(np.int8)
    if kind == 'two':
        side = [{d for k in c for d in P.supports[k] if all(h in c for h in P.holders[d])} for c in comps]
        m = [sum(1 << P.index[d] for d in s) for s in side]
        n = [np.bitwise_count(x & np.uint64(mm)).astype(np.uint64) & np.uint64(1) for mm in m]
        out['W2'] = (1 - 2 * (n[0] & n[1]).astype(np.int8)).astype(np.int8)
    if A.any():
        out['W3'] = (S.astype(np.int8) - A.astype(np.int8)).astype(np.int8)
    moved = np.uint64(sum(1 << P.index[d] for d in P.dist if sig[d] != d))
    Am = (sx ^ x) == moved                                # flipped on the moved distinctions (kept on the others)
    if Am.any() and not (Am == A).all():
        out['W3m'] = (S.astype(np.int8) - Am.astype(np.int8)).astype(np.int8)
    if S.any():
        out['W1k'] = (out['W1'] * S).astype(np.int8)       # on kept states: the sign of the swap on the held distinctions
    if kind == 'two':
        c = [np.bitwise_count(x & np.uint64(mm)).astype(np.int64) for mm in m]
        out['W4'] = np.sign(c[0] - c[1]).astype(np.int8)  # odd under the swap: which side holds more
    mp = np.bitwise_count(x & moved).astype(np.int64) & 1
    labels = {'N': int(len(x)), 'n_S': int(S.sum()), 'n_A': int(A.sum()), 'n_A_moved': int(Am.sum()), 'pairs': len(pairs),
              'fixed_distinctions': sum(1 for d in P.dist if sig[d] == d),
              'W1c is plus or minus W1': bool(len(set(mp.tolist())) == 1)}
    labels['det'] = 1 if ((labels['N'] - labels['n_S']) // 2) % 2 == 0 else -1
    return out, labels


def pair_tables(X, w):
    """signed sums over the allowed states: Z, m1[s] = sum w x_s, M11[s, t] = sum w x_s x_t (exact integers)"""
    import numpy as np
    Z = int(w.astype(np.int64).sum())
    m1 = np.zeros(X.shape[1], dtype=np.int64); M11 = np.zeros((X.shape[1], X.shape[1]), dtype=np.int64)
    for c in range(0, X.shape[0], 1 << 18):
        Xc = X[c:c + (1 << 18)].astype(np.float64); wc = w[c:c + (1 << 18)].astype(np.float64)
        m1 += np.rint(wc @ Xc).astype(np.int64)
        M11 += np.rint(Xc.T @ (Xc * wc[:, None])).astype(np.int64)
    return Z, m1, M11


def four(Z, m1, M11):
    """M[a][b][s, t] for a, b in 0, 1"""
    import numpy as np
    s = m1[:, None]; t = m1[None, :]
    M = [[None, None], [None, None]]
    M[1][1] = M11; M[1][0] = s - M11; M[0][1] = t - M11; M[0][0] = Z - s - t + M11
    return M


def best_chsh(Z, M, cand1, cand2, disjoint, reading):
    """over placements s1 < s2 in cand1, t1 < t2 in cand2 with every (s, t) holder-disjoint: the gates, the largest CHSH
    among placements passing G0-G3, and the hits.  R1: signed count; R2: squared signed sums (README.md, 'Readings')."""
    import numpy as np
    from fractions import Fraction
    res = {'placements': 0, 'G0': 0, 'G1': 0, 'G2': 0, 'G3': 0, 'hits': [], 'best': None}
    c1 = list(cand1); c2 = list(cand2)
    if len(c1) < 2 or len(c2) < 2: return res
    I = np.array(c1); J = np.array(c2)
    sub = lambda A: A[np.ix_(I, J)]
    Ms = [[sub(M[a][b]) for b in (0, 1)] for a in (0, 1)]
    dj = sub(disjoint)
    if reading == 'R1':
        if Z == 0: valid = np.zeros_like(dj); g0 = False
        else:
            sg = 1 if Z > 0 else -1; g0 = True
            valid = dj & (Ms[0][0] * sg >= 0) & (Ms[0][1] * sg >= 0) & (Ms[1][0] * sg >= 0) & (Ms[1][1] * sg >= 0)
        num = (Ms[0][0] + Ms[1][1] - Ms[0][1] - Ms[1][0]) * (1 if Z >= 0 else -1)
        den = abs(Z)
    else:
        big = max(abs(int(v)) for a in (0, 1) for b in (0, 1) for v in np.ravel(Ms[a][b])) > 1 << 30
        sq = [[(Ms[a][b].astype(object) if big else Ms[a][b].astype(np.int64)) ** 2 for b in (0, 1)] for a in (0, 1)]
        S = sq[0][0] + sq[0][1] + sq[1][0] + sq[1][1]
        valid = dj & (S > 0)
        g0 = True
    n1, n2 = len(c1), len(c2)
    best = None
    for a in range(n1):
        for b in range(a + 1, n1):
            for c in range(n2):
                for d in range(c + 1, n2):
                    if not (dj[a, c] and dj[a, d] and dj[b, c] and dj[b, d]): continue
                    res['placements'] += 1
                    cells = ((a, c), (a, d), (b, c), (b, d))
                    if reading == 'R1':
                        if not g0: continue
                        res['G0'] += 1
                        if not all(valid[i, j] for i, j in cells): continue
                        res['G1'] += 1; res['G2'] += 1; res['G3'] += 1
                        e = [int(num[i, j]) for i, j in cells]
                        val = max(abs(sum(e) - 2 * e[k]) for k in range(4))
                        ch = Fraction(val, den)
                    else:
                        if not all(valid[i, j] for i, j in cells): continue
                        res['G0'] += 1
                        res['G1'] += 1
                        Ss = [S[i, j] for i, j in cells]
                        if len(set(Ss)) != 1: continue
                        res['G2'] += 1
                        # no signalling: reader 1's marginal at s does not depend on t, reader 2's at t not on s
                        m1_ = lambda i, j, v: sq[v][0][i, j] + sq[v][1][i, j]
                        m2_ = lambda i, j, v: sq[0][v][i, j] + sq[1][v][i, j]
                        if not (m1_(a, c, 1) == m1_(a, d, 1) and m1_(b, c, 1) == m1_(b, d, 1) and
                                m2_(a, c, 1) == m2_(b, c, 1) and m2_(a, d, 1) == m2_(b, d, 1)): continue
                        res['G3'] += 1
                        e = [sq[0][0][i, j] + sq[1][1][i, j] - sq[0][1][i, j] - sq[1][0][i, j] for i, j in cells]
                        val = max(abs(sum(e) - 2 * e[k]) for k in range(4))
                        ch = Fraction(int(val), int(Ss[0]))
                    if best is None or ch > best: best = ch
                    if ch > 2: res['hits'].append(((c1[a], c1[b]), (c2[c], c2[d]), str(ch)))
    res['best'] = None if best is None else str(best)
    return res


# ---------------------------------------------------------------- parity at any size: exact quadratic sums

class Quad:
    """a quadratic function c + l.y + sum_{a<b} A_ab y_a y_b over GF(2)^n, rows of A as bit masks (symmetric, zero
    diagonal)"""
    def __init__(self, n):
        self.n, self.A, self.l, self.c = n, [0] * n, 0, 0

    def add_product(self, u, v):
        """add <u, y><v, y>"""
        self.l ^= u & v
        for r in range(self.n):
            if u >> r & 1: self.A[r] ^= v
            if v >> r & 1: self.A[r] ^= u
        for r in range(self.n): self.A[r] &= ~(1 << r)

    def copy(self):
        q = Quad(self.n); q.A, q.l, q.c = list(self.A), self.l, self.c; return q


def gauss(q, extra=0):
    """sum over y of (-1)^(q(y) + <extra, y>), exactly"""
    A, l, c = list(q.A), q.l ^ extra, q.c
    alive = (1 << q.n) - 1
    factor = 1
    while alive:
        a = (alive & -alive).bit_length() - 1
        row = A[a] & alive
        if row == 0:
            if l >> a & 1: return 0
            factor *= 2; alive &= ~(1 << a); continue
        b = (row & -row).bit_length() - 1
        alive &= ~((1 << a) | (1 << b))
        u = A[a] & alive; v = A[b] & alive; la = l >> a & 1; lb = l >> b & 1
        # (u.y + la)(v.y + lb) = <u,y><v,y> + lb<u,y> + la<v,y> + la lb
        l ^= u & v
        r = u
        while r:
            t = (r & -r).bit_length() - 1; A[t] ^= v; r &= r - 1
        r = v
        while r:
            t = (r & -r).bit_length() - 1; A[t] ^= u; r &= r - 1
        for t in (u & v,):
            r = t
            while r:
                s = (r & -r).bit_length() - 1; A[s] &= ~(1 << s); r &= r - 1
        if lb: l ^= u
        if la: l ^= v
        c ^= la & lb
        factor *= 2
    return factor * (-1) ** c


def parity_quadratic_tables(P, sig, kind, comps, name):
    """Z, m1, M11 for the parity law and a quadratic weighting (U, W1, W1c, W2), exactly, at any size"""
    import numpy as np
    basis = parity_basis(P); n = len(basis)
    col = [sum(1 << i for i, b in enumerate(basis) if b >> P.index[d] & 1) for d in P.dist]
    q = Quad(n)
    if name in ('W1', 'W1c'):
        pairs = sorted({tuple(sorted((P.index[d], P.index[sig[d]]))) for d in P.dist if sig[d] != d})
        for i, j in pairs:
            q.add_product(col[i], col[j])
            if name == 'W1c':                         # (1 - a)(1 - b) = ab + a + b + 1
                q.l ^= col[i] ^ col[j]; q.c ^= 1
    elif name == 'W2':
        side = [{d for k in cc for d in P.supports[k] if all(h in cc for h in P.holders[d])} for cc in comps]
        u = [0, 0]
        for t in (0, 1):
            for d in side[t]: u[t] ^= col[P.index[d]]
        q.add_product(u[0], u[1])
    D = P.D
    Z = gauss(q)
    g1 = [gauss(q, col[s]) for s in range(D)]
    m1 = np.array([(Z - g) // 2 for g in g1], dtype=object)
    M11 = np.zeros((D, D), dtype=object)
    for s in range(D):
        for t in range(s, D):
            v = Z - g1[s] - g1[t] + gauss(q, col[s] ^ col[t]) if s != t else 2 * (Z - g1[s])
            M11[s, t] = M11[t, s] = v // 4
    return Z, m1, M11


# ---------------------------------------------------------------- one stage: every class of swaps, both lifts

def involution_classes(auts, invs):
    """one swap from each class of swaps that a renaming of the pattern carries into one another"""
    pool, reps = set(invs), []
    inverse = {a: tuple(sorted(range(len(a)), key=lambda k: a[k])) for a in auts}
    while pool:
        s = min(pool); reps.append(s)
        for a in auts:
            ai = inverse[a]
            pool.discard(tuple(a[s[ai[k]]] for k in range(len(s))))
    return reps


def candidates(P, sig, kind, comps):
    if kind == 'two':
        return [sorted(P.index[d] for k in c for d in P.supports[k] if all(h in c for h in P.holders[d])) for c in comps]
    moved = sorted(P.index[d] for d in P.dist if sig[d] != d)
    return [moved, moved]


def disjoint_matrix(P):
    import numpy as np
    H = [set(P.holders[d]) for d in P.dist]
    return np.array([[not (H[s] & H[t]) for t in range(P.D)] for s in range(P.D)], dtype=bool)


NAMES = ('U', 'W1', 'W1c', 'W1k', 'W2', 'W3', 'W3m', 'W4')


def annotate(P, x, w, hit):
    """for a hit: is the weight a function of the four read values (the sign sits on the reads themselves, and no two
    completions of one reading differ in sign); do the readers' holders meet (FORBID-EDITS's stricter separation)"""
    import numpy as np
    reads = list(hit[0]) + list(hit[1])
    key = np.zeros(len(x), dtype=np.int64)
    for j, i in enumerate(reads): key |= (((x >> np.uint64(i)) & np.uint64(1)).astype(np.int64) << j)
    on_reads = all(len(set(w[key == k].tolist())) <= 1 for k in range(16))
    h1 = {h for i in hit[0] for h in P.holders[P.dist[i]]}; h2 = {h for i in hit[1] for h in P.holders[P.dist[i]]}
    meet = any(set(P.supports[a]) & set(P.supports[b]) for a in h1 for b in h2)
    return {'sign on the reads only': on_reads, 'holders meet': meet, 'nonzero states': int((w != 0).sum())}


def analyse(P, law, extra=None, gauss_path=False):
    """every class of swaps of the stage, both lifts: kind of sides, labels, and for each weighting and reading the gates
    and the largest CHSH.  extra: further named weightings {name: function(x) -> int8 vector} (named cases only)."""
    import numpy as np
    auts, trunc = P.automorphisms()
    invs = involutions(auts)
    if not invs: return {'swaps': 0, 'truncated': trunc, 'classes': []}
    x = None if gauss_path else states(P, law)
    if x is None and law != 'parity':
        return {'swaps': len(invs), 'truncated': trunc, 'classes': 'not run: too many states'}
    X = bits(x, list(range(P.D))) if x is not None else None
    dj = disjoint_matrix(P)
    out = []
    for p in involution_classes(auts, invs):
        lifts = [(False, P.lift(p, False))]
        mx = P.lift(p, True)
        if mx != lifts[0][1]: lifts.append((True, mx))
        for maximal, sig in lifts:
            kind, comps = P.sides(p, sig)
            c1, c2 = candidates(P, sig, kind, comps)
            row = {'perm': p, 'lift': 'max' if maximal else 'min', 'kind': kind, 'sides': [len(c) for c in comps],
                   'readers': [len(c1), len(c2)], 'weightings': {}}
            if x is not None:
                ws, labels = weightings(P, sig, kind, comps, x, law)
                if extra:
                    for nm, f in extra.items(): ws[nm] = f(x)
                row['labels'] = labels
                for nm, w in ws.items():
                    Z, m1, M11 = pair_tables(X, w)
                    M = four(Z, m1, M11)
                    row['weightings'][nm] = {'Z': Z, **{r: best_chsh(Z, M, c1, c2, dj, r) for r in ('R1', 'R2')}}
                    for r in ('R1', 'R2'):
                        hs = row['weightings'][nm][r]['hits']
                        hs[:20] = [h + (annotate(P, x, w, h),) for h in hs[:20]]
            else:
                for nm in ('U', 'W1', 'W1c') + (('W2',) if kind == 'two' else ()):
                    Z, m1, M11 = parity_quadratic_tables(P, sig, kind, comps, nm)
                    M = four(Z, m1.astype(object), M11)
                    M = [[np.array(M[a][b], dtype=object) for b in (0, 1)] for a in (0, 1)]
                    row['weightings'][nm] = {'Z': int(Z), **{r: best_chsh(int(Z), M, c1, c2, dj, r) for r in ('R1', 'R2')}}
            out.append(row)
    return {'swaps': len(invs), 'truncated': trunc, 'classes': out}


def stage_rows(i, rounds=2):
    """the census rows of start i: every stage after 0..rounds rounds with a swap, under both laws"""
    F = forbid()
    base = F.supports_of(census_starts()[i])
    rows = []
    for law in ('parity', 'nae'):
        stages, status = grow_rounds(base, law, rounds)
        for r, st in enumerate(stages):
            P = Pattern(st)
            res = analyse(P, law)
            if not res['swaps']: continue
            rows.append(json.loads(json.dumps({'start': i, 'law': law, 'round': r, 'K': P.K, 'D': P.D, **res}, default=str)))
    return rows


def run(i0, i1, rounds=2):
    for i in range(i0, min(i1, len(census_starts()))):
        for row in stage_rows(i, rounds): print(json.dumps(row), flush=True)


# ---------------------------------------------------------------- the structural pre-count

def precount(i0, i1, rounds):
    starts = census_starts()
    F = forbid()
    for i in range(i0, min(i1, len(starts))):
        base = F.supports_of(starts[i])
        for law in ('parity', 'nae'):
            stages, status = grow_rounds(base, law, rounds)
            for r, st in enumerate(stages):
                P = Pattern(st)
                auts, trunc = P.automorphisms()
                inv = involutions(auts)
                kinds = collections.Counter()
                for p in inv:
                    for maximal in (False, True):
                        sig = P.lift(p, maximal)
                        kind, comps = P.sides(p, sig)
                        kinds[('max' if maximal else 'min', kind)] += 1
                print(json.dumps({'start': i, 'law': law, 'round': r, 'status': status if r == len(stages) - 1 else 'grown',
                                  'K': P.K, 'D': P.D, 'parity_dim': P.parity_dim(), 'auts': len(auts), 'truncated': trunc,
                                  'involutions': len(inv), 'kinds': {f'{a}:{b}': c for (a, b), c in sorted(kinds.items())}}),
                      flush=True)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'run':
        run(int(sys.argv[2]), int(sys.argv[3]))
    if cmd == 'precount':
        R = int(sys.argv[sys.argv.index('--rounds') + 1]) if '--rounds' in sys.argv else 2
        precount(int(sys.argv[2]), int(sys.argv[3]), R)
