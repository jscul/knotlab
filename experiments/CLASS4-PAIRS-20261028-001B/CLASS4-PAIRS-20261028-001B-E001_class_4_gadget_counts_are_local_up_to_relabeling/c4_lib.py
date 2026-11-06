"""CLASS4-PAIRS-20261028-001B: top-layer (class-4) count-locality of zero-jump gadget knots, by affine linear algebra.

For fixed layer-<=2 data D on the solution variety (all private equations of layers 2-3 hold; they do not involve layer-3 data),
the layer-4 equations of a gadget are affine in its layer-3 free data c: E(c) = A c + b.  The global system (the gadget of a
graph) is compared with the local system assembled from single-edge gadgets: private rows per edge; each vertex row = the vertex's
own terms (single edge with zero private data) + the sum over incident edges of (single-edge row - the same row at zero private
data).  Count-locality up to relabeling: A_global = A_local and b_global - b_local lies in the column space of A_local, so the
number of layer-3 completions is the same for every D.  The gadget model is pf_lib (COPRIME-PAIRS-20261027-001D, read-only)."""
import itertools, sys, glob
ROOT = "/home/jscul/p-vs-np-contact-first"
sys.path.insert(0, glob.glob(f"{ROOT}/experiments/COPRIME-PAIRS-20261027-001D/*E002_*")[0])
from pf_lib import *  # noqa: E402,F401
from cd_lib import rank, nullspace  # noqa: E402


def var_index(G, L):
    V, E = {}, {}
    for j, s in enumerate(G.var_sites()): V.setdefault(s + (int(L.layer[G.var[j][1]]),), []).append(j)
    for c, s in enumerate(G.eq_sites()): E.setdefault(s + (int(L.layer[G.eqs[c][1]]),), []).append(c)
    return V, E


def affine_system(G, base, cols, rows, rng):
    """A, b with E[rows](base + c on cols) = A c + b; affineness verified at 3 random points"""
    p, n = G.p, len(cols)
    X = np.repeat(base[None, :], n + 4, axis=0)
    for i, j in enumerate(cols): X[1 + i, j] = (X[1 + i, j] + 1) % p
    rnd = rng.integers(0, p, (3, n))
    for k in range(3): X[n + 1 + k, cols] = (X[n + 1 + k, cols] + rnd[k]) % p
    E = G.evaluate(X)[:, rows] % p
    b = E[0]; A = ((E[1:n + 1] - b) % p).T
    ok = all(((A @ rnd[k] + b) % p == E[n + 1 + k]).all() for k in range(3))
    return A % p, b % p, ok


def solvable(A, b, p):
    if A.size == 0: return not (b % p).any(), 0
    rA = rank(A % p, p)
    return rank(np.concatenate([A, b[:, None]], axis=1) % p, p) == rA, A.shape[1] - rA


def in_colspace(A, v, p):
    if A.size == 0: return not (v % p).any()
    return rank(np.concatenate([A, v[:, None]], axis=1) % p, p) == rank(A % p, p)


class Case:
    def __init__(self, gens, slots, p=11, d=5, cls=4, zero_jump=True):
        self.p, self.d, self.gens, self.slots, self.zj = p, d, gens, slots, zero_jump
        self.L = free_graded(p, d, gens, cls)
        self.T = summand_types(p, d, slots)
        self.top = int(self.L.layer.max())
        self.K2 = Gadget(self.L, d, p, self.T, 2, [(0, 1)], zero_jump=zero_jump)
        self.VK, self.EK = var_index(self.K2, self.L)

    # site helpers
    def low(self, V, site): return [j for k, c in V.items() if k[:2] == site and k[2] < self.top - 1 for j in c]
    def l3(self, V, site): return [j for k, c in V.items() if k[:2] == site and k[2] == self.top - 1 for j in c]
    def rows(self, E, site, layers): return [c for k, cs in E.items() if k[:2] == site and k[2] in layers for c in cs]

    def variety_point(self, su, sv, rng):
        """random layer-<=2 private data on the edge's variety (layer-2/3 private equations hold).  Slot-1 layer-1 data are
        enumerated against the layer-2 equations, slot-1 layer-2 data solved affinely from the layer-3 equations (slot-2 data
        zero), then slot-2 data drawn from the kernel of the (homogeneous linear) equations; verified at the end."""
        K2, p, L = self.K2, self.p, self.L
        cols = self.low(self.VK, ("e", 0))
        lay = {j: int(L.layer[K2.var[j][1]]) for j in cols}; slot = {j: K2.kinds[K2.var[j][0]][2] for j in cols}
        a1 = [j for j in cols if slot[j] == 1 and lay[j] == 1]; a2 = [j for j in cols if slot[j] == 1 and lay[j] == 2]
        s2 = [j for j in cols if slot[j] == 2]
        r2 = self.rows(self.EK, ("e", 0), {2}); r3 = self.rows(self.EK, ("e", 0), {3}); r23 = r2 + r3
        vu, vv = self.low(self.VK, ("v", 0)), self.low(self.VK, ("v", 1))

        def ev(rows_):
            X = np.zeros((len(rows_), len(K2.var)), dtype=np.int64)
            X[:, vu] = su; X[:, vv] = sv
            for i, rw in enumerate(rows_):
                for j, x in rw.items(): X[i, j] = x
            return K2.evaluate(X) % p
        if not (su - sv).any():
            return {j: int(x) for j, x in zip(cols, rng.integers(0, p, len(cols)))}
        C1 = list(itertools.product(range(p), repeat=len(a1)))
        X = np.zeros((len(C1), len(K2.var)), dtype=np.int64); X[:, vu] = su; X[:, vv] = sv
        if a1: X[:, a1] = np.array(C1, dtype=np.int64)
        E = evaluate_chunked(K2, X) % p
        good = [C1[i] for i in np.nonzero(~E[:, r2].any(axis=1))[0]]
        for attempt in range(40):
            x1 = dict(zip(a1, good[rng.integers(0, len(good))]))
            base = ev([x1] + [{**x1, j: 1} for j in a2])
            A = ((base[1:, r3] - base[0, r3]) % p).T
            ok, _ = solvable(A, (-base[0, r3]) % p, p) if a2 else (not base[0, r3].any(), 0)
            if not ok: continue
            y = np.zeros(len(a2), dtype=np.int64)
            if a2:
                Aug = np.concatenate([A, ((-base[0, r3]) % p)[:, None]], axis=1)
                ker = nullspace(Aug % p, p)
                sols = [k for k in ker if k[-1] % p]
                if not sols: continue
                v = np.array(sols[0]); y = (v[:-1] * pow(int(v[-1]), p - 2, p)) % p
                kk = nullspace(A % p, p)
                if len(kk): y = (y + rng.integers(0, p, len(kk)) @ np.array(kk)) % p
            x12 = {**x1, **dict(zip(a2, y.tolist()))}
            base2 = ev([x12] + [{**x12, j: 1} for j in s2])
            M = ((base2[1:, r23] - base2[0, r23]) % p).T
            if base2[0, r23].any(): continue
            ker = nullspace(M % p, p) if s2 else []
            z = (rng.integers(0, p, len(ker)) @ np.array(ker)) % p if len(ker) else np.zeros(len(s2), dtype=np.int64)
            x = {**x12, **dict(zip(s2, z.tolist()))}
            assert not ev([x])[0, r23].any(), "variety point check failed"
            return x
        return {j: 0 for j in cols}

    def graph(self, nv, edges, states, rng):
        """compare the global and local affine systems over the layer-3 data for one configuration"""
        p, L = self.p, self.L
        G = Gadget(L, self.d, p, self.T, nv, edges, zero_jump=self.zj)
        VG, EG = var_index(G, L)
        base = np.zeros(len(G.var), dtype=np.int64)
        for v in range(nv): base[self.low(VG, ("v", v))] = states[v]
        pis = []
        for e, (u, v) in enumerate(edges):
            x = self.variety_point(states[u], states[v], rng); pis.append(x)
            kc = self.low(self.VK, ("e", 0)); gc = self.low(VG, ("e", e))
            for jk, jg in zip(kc, gc): base[jg] = x[jk]
        var3 = [j for v in range(nv) for j in self.l3(VG, ("v", v))] + [j for e in range(len(edges)) for j in self.l3(VG, ("e", e))]
        rows = [c for e in range(len(edges)) for c in self.rows(EG, ("e", e), {self.top})] + \
               [c for v in range(nv) for c in self.rows(EG, ("v", v), {self.top})]
        Eb = G.evaluate(base[None, :])[0] % p
        variety = not Eb[[c for e in range(len(edges)) for c in self.rows(EG, ("e", e), {2, 3})]].any()
        AG, bG, affG = affine_system(G, base, var3, rows, rng)
        col = {}
        for v in range(nv):
            for i, j in enumerate(self.l3(VG, ("v", v))): col[("v", v, i)] = var3.index(j)
        for e in range(len(edges)):
            for i, j in enumerate(self.l3(VG, ("e", e))): col[("e", e, i)] = var3.index(j)
        row = {}; r = 0
        for e in range(len(edges)):
            for i in range(len(self.rows(EG, ("e", e), {self.top}))): row[("e", e, i)] = r; r += 1
        for v in range(nv):
            for i in range(len(self.rows(EG, ("v", v), {self.top}))): row[("v", v, i)] = r; r += 1
        AL = np.zeros_like(AG); bL = np.zeros_like(bG)
        done, affL = set(), True
        k3 = self.l3(self.VK, ("v", 0)) + self.l3(self.VK, ("v", 1)) + self.l3(self.VK, ("e", 0))
        krows = self.rows(self.EK, ("e", 0), {self.top}) + self.rows(self.EK, ("v", 0), {self.top}) + self.rows(self.EK, ("v", 1), {self.top})
        npr = len(self.rows(self.EK, ("e", 0), {self.top})); nvr = len(self.rows(self.EK, ("v", 0), {self.top}))
        n0, n1 = len(self.l3(self.VK, ("v", 0))), len(self.l3(self.VK, ("v", 1)))
        for e, (u, v) in enumerate(edges):
            kb = np.zeros(len(self.K2.var), dtype=np.int64)
            kb[self.low(self.VK, ("v", 0))] = states[u]; kb[self.low(self.VK, ("v", 1))] = states[v]
            for j, x in pis[e].items(): kb[j] = x
            Ak, bk, a1 = affine_system(self.K2, kb, k3, krows, rng)
            kb0 = kb.copy(); kb0[self.low(self.VK, ("e", 0))] = 0
            Ak0, bk0, a2 = affine_system(self.K2, kb0, k3, krows, rng)
            affL &= a1 and a2
            kc = [col[("v", u, i)] for i in range(n0)] + [col[("v", v, i)] for i in range(n1)] + \
                 [col[("e", e, i)] for i in range(len(self.l3(self.VK, ("e", 0))))]
            for i in range(npr):
                AL[row[("e", e, i)], kc] = Ak[i]; bL[row[("e", e, i)]] = bk[i]
            for side, vert in ((0, u), (1, v)):
                for i in range(nvr):
                    kr, rr = npr + side * nvr + i, row[("v", vert, i)]
                    AL[rr, kc] = (AL[rr, kc] + Ak[kr] - Ak0[kr]) % p; bL[rr] = (bL[rr] + bk[kr] - bk0[kr]) % p
                    if vert not in done: AL[rr, kc] = (AL[rr, kc] + Ak0[kr]) % p; bL[rr] = (bL[rr] + bk0[kr]) % p
                done.add(vert)
        for vert in range(nv):
            if vert in done: continue
            kb = np.zeros(len(self.K2.var), dtype=np.int64)
            kb[self.low(self.VK, ("v", 0))] = states[vert]; kb[self.low(self.VK, ("v", 1))] = states[vert]
            Ak0, bk0, _ = affine_system(self.K2, kb, k3, krows, rng)
            for i in range(nvr):
                rr = row[("v", vert, i)]; kc = [col[("v", vert, j)] for j in range(n0)]
                AL[rr, kc] = (AL[rr, kc] + Ak0[npr + i][:n0]) % p; bL[rr] = (bL[rr] + bk0[npr + i]) % p
        okG, kG = solvable(AG, (-bG) % p, p); okL, kL = solvable(AL, (-bL) % p, p)
        return {"variety": bool(variety), "affine": bool(affG and affL), "layer-3 variables": len(var3), "rows": len(rows),
                "global (solvable, kernel dim)": [bool(okG), int(kG)], "local (solvable, kernel dim)": [bool(okL), int(kL)],
                "counts equal": bool(okG == okL and (kG == kL or not okG)), "A equal": bool((AG == AL).all()),
                "b difference in column space": bool(in_colspace(AL, (bG - bL) % p, p)), "b equal": bool((bG == bL).all())}

    def slot1_solution(self, su, sv, rng, tries=30):
        """slot-1 data (every layer below the top) solving every private equation with slot-2 data zero, built layer by layer:
        layer-1 data enumerated against the layer-2 equations, then each higher layer solved affinely from the next layer's
        equations; None if no solution is found"""
        K2, p, L = self.K2, self.p, self.L
        vu = [j for k, c in self.VK.items() if k[:2] == ("v", 0) for j in c]; vv = [j for k, c in self.VK.items() if k[:2] == ("v", 1) for j in c]
        ep = [j for k, c in self.VK.items() if k[:2] == ("e", 0) for j in c]
        q1 = {lay: [j for j in ep if K2.kinds[K2.var[j][0]][2] == 1 and int(L.layer[K2.var[j][1]]) == lay] for lay in range(1, self.top)}
        rp = {lay: [c for k, cs in self.EK.items() if k[:2] == ("e", 0) and k[2] == lay for c in cs] for lay in range(2, self.top + 1)}

        def ev(xs):
            X = np.zeros((len(xs), len(K2.var)), dtype=np.int64); X[:, vu] = su; X[:, vv] = sv
            for i, x in enumerate(xs):
                for j, val in x.items(): X[i, j] = val
            return K2.evaluate(X) % p
        C1 = list(itertools.product(range(p), repeat=len(q1[1])))
        X = np.zeros((len(C1), len(K2.var)), dtype=np.int64); X[:, vu] = su; X[:, vv] = sv
        if q1[1]: X[:, q1[1]] = np.array(C1, dtype=np.int64)
        E = evaluate_chunked(K2, X) % p
        good = [C1[i] for i in np.nonzero(~E[:, rp[2]].any(axis=1))[0]] if rp[2] else C1
        for _ in range(tries):
            x = dict(zip(q1[1], good[rng.integers(0, len(good))]))
            ok = True
            for lay in range(2, self.top):
                cols, rows = q1[lay], rp[lay + 1]
                if not cols: continue
                B = ev([x] + [{**x, j: 1} for j in cols])
                A = ((B[1:, rows] - B[0, rows]) % p).T
                rhs = (-B[0, rows]) % p
                good_, _ = solvable(A, rhs, p)
                if not good_: ok = False; break
                Aug = np.concatenate([A, rhs[:, None]], axis=1)
                sol = [k for k in nullspace(Aug % p, p) if k[-1] % p]
                if not sol and rhs.any(): ok = False; break
                y = np.zeros(len(cols), dtype=np.int64) if not sol else (np.array(sol[0][:-1]) * pow(int(sol[0][-1]), p - 2, p)) % p
                kk = nullspace(A % p, p)
                if len(kk): y = (y + rng.integers(0, p, len(kk)) @ np.array(kk)) % p
                x = {**x, **dict(zip(cols, y.tolist()))}
            if ok and not ev([x])[0, [c for lay in rp for c in rp[lay]]].any():
                return x
        return None

    def linear_structure(self, rng, nsamp=8):
        """at a diagonal, a random and a pair-failing vertex pair: for sampled slot-1 data solving the private equations with
        slot-2 data zero, the private equations (all layers) are homogeneous affine in slot-2 data, and the endpoint vertex terms
        (vertex rows minus their value at zero private data) are additive in slot-2 data on the kernel, with no slot-2-free term.
        Also: vertex rows vanish at zero private data for random pairs, private rows vanish at the diagonal."""
        K2, p, L = self.K2, self.p, self.L
        vu = [j for k, c in self.VK.items() if k[:2] == ("v", 0) for j in c]; vv = [j for k, c in self.VK.items() if k[:2] == ("v", 1) for j in c]
        ep = [j for k, c in self.VK.items() if k[:2] == ("e", 0) for j in c]
        q1 = [j for j in ep if K2.kinds[K2.var[j][0]][2] == 1]; q2 = [j for j in ep if K2.kinds[K2.var[j][0]][2] == 2]
        rp = [c for k, cs in self.EK.items() if k[:2] == ("e", 0) for c in cs]
        rv = [c for k, cs in self.EK.items() if k[0] == "v" and k[2] == self.top for c in cs]

        def ev(su, sv, P1, P2):
            X = np.zeros((len(P1), len(K2.var)), dtype=np.int64); X[:, vu] = su; X[:, vv] = sv; X[:, q1] = P1; X[:, q2] = P2
            return K2.evaluate(X) % p
        lt_v = sum(int(ev(rng.integers(0, p, len(vu)), rng.integers(0, p, len(vv)), np.zeros((1, len(q1)), dtype=np.int64),
                          np.zeros((1, len(q2)), dtype=np.int64))[0, rv].any()) for _ in range(10))
        s = rng.integers(0, p, len(vu))
        lt_p = int(ev(s, s, rng.integers(0, p, (100, len(q1))), rng.integers(0, p, (100, len(q2))))[:, rp].any(axis=1).sum())
        vk = [vu.index(j) for j in vu if int(L.layer[K2.var[j][1]]) == 1 and int(L.chars[K2.var[j][1]]) % self.d == self.slots[0] % self.d]
        D = np.zeros(len(vu), dtype=np.int64); D[vk] = rng.integers(1, p, len(vk))
        pairs = [("diagonal", (lambda x: (x, x))(rng.integers(0, p, len(vu)))), ("random", (rng.integers(0, p, len(vu)), rng.integers(0, p, len(vu)))),
                 ("pair-failing (0, D)", (np.zeros(len(vu), dtype=np.int64), D))]
        out = []
        for name, (su, sv) in pairs:
            bad = {"not homogeneous-affine": 0, "flow not additive": 0, "flow has a slot-2-free term": 0}
            got = 0
            for _ in range(nsamp):
                x = self.slot1_solution(su, sv, rng)
                if x is None: continue
                got += 1
                P1 = np.array([x[j] for j in q1], dtype=np.int64)
                n2 = len(q2); Z = np.zeros(n2, dtype=np.int64)
                rnd = rng.integers(0, p, (3, n2))
                Ex = ev(su, sv, np.repeat(P1[None, :], 1 + n2 + 3, axis=0), np.concatenate([Z[None, :], np.eye(n2, dtype=np.int64), rnd]))
                M = ((Ex[1:1 + n2, rp] - Ex[0, rp]) % p).T
                if Ex[0, rp].any() or not all(((M @ rnd[k] + Ex[0, rp]) % p == Ex[1 + n2 + k, rp]).all() for k in range(3)):
                    bad["not homogeneous-affine"] += 1; continue
                ker = nullspace(M % p, p) if M.size else np.eye(n2, dtype=np.int64)
                E0 = ev(su, sv, np.zeros((1, len(q1)), dtype=np.int64), Z[None, :])[0]
                if ((Ex[0, rv] - E0[rv]) % p).any(): bad["flow has a slot-2-free term"] += 1
                if len(ker):
                    Kk = np.array(ker); a, b = (rng.integers(0, p, (2, len(Kk))) @ Kk) % p
                    Eab = ev(su, sv, np.repeat(P1[None, :], 3, axis=0), np.stack([a, b, (a + b) % p]))
                    fa, fb, fab = [(Eab[k, rv] - E0[rv]) % p for k in range(3)]
                    if ((fa + fb - fab) % p).any(): bad["flow not additive"] += 1
            out.append({"pair": name, "samples": got, **bad})
        return {"vertex terms nonzero at zero private data (10 pairs)": lt_v, "private rows nonzero at the diagonal (100)": lt_p,
                "pairs": out}

    def deficit(self, rng):
        """rank-witness ingredients: at (0, D), some private equation is nonzero for random private data, and zero private data
        solve; at the diagonal every private equation vanishes (from linear_structure)"""
        K2, p, L = self.K2, self.p, self.L
        vu = [j for k, c in self.VK.items() if k[:2] == ("v", 0) for j in c]; vv = [j for k, c in self.VK.items() if k[:2] == ("v", 1) for j in c]
        ep = [j for k, c in self.VK.items() if k[:2] == ("e", 0) for j in c]
        rp = [c for k, cs in self.EK.items() if k[:2] == ("e", 0) for c in cs]
        vk = [vu.index(j) for j in vu if int(L.layer[K2.var[j][1]]) == 1 and int(L.chars[K2.var[j][1]]) % self.d == self.slots[0] % self.d]
        out = []
        for side in (0, 1):
            D = np.zeros(len(vu), dtype=np.int64); D[vk] = rng.integers(1, p, len(vk))
            su, sv = (np.zeros(len(vu), dtype=np.int64), D) if side == 0 else (D, np.zeros(len(vu), dtype=np.int64))
            X = np.zeros((51, len(K2.var)), dtype=np.int64); X[:, vu] = su; X[:, vv] = sv
            X[1:, ep] = rng.integers(0, p, (50, len(ep)))
            E = K2.evaluate(X) % p
            out.append({"side": "(0, D)" if side == 0 else "(D, 0)", "zero data solve": bool(not E[0, rp].any()),
                        "random data violating": int(E[1:, rp].any(axis=1).sum())})
        return out
