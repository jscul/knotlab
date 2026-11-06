"""CLASS4-LOCALITY-20261028-001A: exact locality of class-4 zero-jump gadget equations in intrinsic layer-3 coordinates.

The model (pf_lib.Gadget) solves each layer with a particular solution chosen by a linear solver, then adds the free data times the
block class colourings.  For a block b with layer-3 data and component k, the solver's particular solution X may contain a multiple
of b's class colouring v_b.  The intrinsic coordinate removes it: Phi[b, k] = (X[read_b, k] - X[base_b, k]) / v_b[read_b] (v_b
vanishes on base_b and not on read_b), and intrinsic = model + Phi.  For fixed layer-<=2 data the layer-4 equations are affine in
the layer-3 data, E = A c + b; in intrinsic coordinates b_int = b - A Phi.  The global system of a graph gadget is compared with the
system assembled from single-edge gadgets (each converted to its own intrinsic coordinates).  The experiment library of
CLASS4-PAIRS-20261028-001B-E001 (c4_lib) is imported read-only."""
import glob, os, sys
ROOT = "/home/jscul/p-vs-np-contact-first"
sys.path.insert(0, glob.glob(f"{ROOT}/experiments/CLASS4-PAIRS-20261028-001B/*E001_*")[0])
from c4_lib import *  # noqa: E402,F401
from cd_lib import solve_any  # noqa: E402


def layer_colours(G, vals):
    """the colours V (n, D) of one sample after solving layers 1..top (particular solutions as in Gadget.evaluate)"""
    L, p, n, d = G.L, G.p, G.n, G.d
    ch = lambda k: int(L.chars[k]) % d
    V = np.zeros((1, n, L.D), dtype=np.int64)
    add = {}
    for j, (bi, k) in enumerate(G.var):
        add[k] = (add.get(k, 0) + vals[j] * G.cls[(bi, ch(k))][None, :]) % p
    for lay in range(1, int(L.layer.max()) + 1):
        R = G.Mo.run(V)
        for k in [k for k in range(L.D) if L.layer[k] == lay]:
            X, bad = solve_any(G.Mo.Lin[ch(k)], (-R[:, :, k]).T % p, p)
            V[:, :, k] = (X.T + add.get(k, 0)) % p
    return V[0]


def block_pos(G, bi):
    qs = [q for (b, t, q) in G.pos if b == bi]
    return min(qs) - (0 if bi == 0 else 1), [q for (b, t, q) in G.pos if b == bi and t == "read"][0]


def phi_vector(G, vals, var3):
    """the solver's class component Phi on the layer-3 variables var3 (layer-3 data set to zero)"""
    L, p, d = G.L, G.p, G.d
    v = vals.copy(); v[var3] = 0
    V = layer_colours(G, v)
    out = np.zeros(len(var3), dtype=np.int64)
    for i, j in enumerate(var3):
        bi, k = G.var[j]
        base, read = block_pos(G, bi)
        cv = G.cls[(bi, int(L.chars[k]) % d)]
        assert cv[base] % p == 0 and cv[read] % p, "class colouring must vanish on base and not on read"
        out[i] = ((V[read, k] - V[base, k]) * pow(int(cv[read]), p - 2, p)) % p
    return out


class IntrinsicCase(Case):
    def parallel_point(self, su, sv, rng, tries=60):
        """a variety point preferring nonzero slot-1 layer-1 data (possible off the diagonal when the states are parallel)"""
        kc = self.low(self.VK, ("e", 0))
        x = self.variety_point(su, sv, rng)
        for _ in range(tries):
            if any(x[j] for j in kc[:2]): return x, True
            x = self.variety_point(su, sv, rng)
        return x, bool(any(x[j] for j in kc[:2]))

    def graph_int(self, nv, edges, states, rng, prefer_slot1=False):
        p, L = self.p, self.L
        G = Gadget(L, self.d, p, self.T, nv, edges, zero_jump=self.zj)
        VG, EG = var_index(G, L)
        base = np.zeros(len(G.var), dtype=np.int64)
        for v in range(nv): base[self.low(VG, ("v", v))] = states[v]
        pis, active = [], False
        kc = self.low(self.VK, ("e", 0))
        for e, (u, v) in enumerate(edges):
            if prefer_slot1:
                x, act = self.parallel_point(states[u], states[v], rng)
                active |= act and bool((np.asarray(states[u]) - np.asarray(states[v])).any() % p)
            else:
                x = self.variety_point(states[u], states[v], rng)
            pis.append(x)
            for jk, jg in zip(kc, self.low(VG, ("e", e))): base[jg] = x[jk]
        var3 = [j for v in range(nv) for j in self.l3(VG, ("v", v))] + [j for e in range(len(edges)) for j in self.l3(VG, ("e", e))]
        rows = [c for e in range(len(edges)) for c in self.rows(EG, ("e", e), {self.top})] + \
               [c for v in range(nv) for c in self.rows(EG, ("v", v), {self.top})]
        Eb = G.evaluate(base[None, :])[0] % p
        variety = not Eb[[c for e in range(len(edges)) for c in self.rows(EG, ("e", e), {2, 3})]].any()
        AG, bG, affG = affine_system(G, base, var3, rows, rng)
        bGi = (bG - AG @ phi_vector(G, base, var3)) % p
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
        AL = np.zeros_like(AG); bL = np.zeros_like(bG); bLr = np.zeros_like(bG)
        done, affL = set(), True
        k3 = self.l3(self.VK, ("v", 0)) + self.l3(self.VK, ("v", 1)) + self.l3(self.VK, ("e", 0))
        krows = self.rows(self.EK, ("e", 0), {self.top}) + self.rows(self.EK, ("v", 0), {self.top}) + self.rows(self.EK, ("v", 1), {self.top})
        npr = len(self.rows(self.EK, ("e", 0), {self.top})); nvr = len(self.rows(self.EK, ("v", 0), {self.top}))
        n0, n1 = len(self.l3(self.VK, ("v", 0))), len(self.l3(self.VK, ("v", 1)))

        def single(kb):
            Ak, bk, a = affine_system(self.K2, kb, k3, krows, rng)
            return Ak, bk, (bk - Ak @ phi_vector(self.K2, kb, k3)) % p, a
        for e, (u, v) in enumerate(edges):
            kb = np.zeros(len(self.K2.var), dtype=np.int64)
            kb[self.low(self.VK, ("v", 0))] = states[u]; kb[self.low(self.VK, ("v", 1))] = states[v]
            for j, x in pis[e].items(): kb[j] = x
            Ak, bkr, bk, a1 = single(kb)
            kb0 = kb.copy(); kb0[self.low(self.VK, ("e", 0))] = 0
            Ak0, bk0r, bk0, a2 = single(kb0)
            affL &= a1 and a2
            kcol = [col[("v", u, i)] for i in range(n0)] + [col[("v", v, i)] for i in range(n1)] + \
                   [col[("e", e, i)] for i in range(len(self.l3(self.VK, ("e", 0))))]
            for i in range(npr):
                AL[row[("e", e, i)], kcol] = Ak[i]; bL[row[("e", e, i)]] = bk[i]; bLr[row[("e", e, i)]] = bkr[i]
            for side, vert in ((0, u), (1, v)):
                for i in range(nvr):
                    kr, rr = npr + side * nvr + i, row[("v", vert, i)]
                    AL[rr, kcol] = (AL[rr, kcol] + Ak[kr] - Ak0[kr]) % p
                    bL[rr] = (bL[rr] + bk[kr] - bk0[kr]) % p; bLr[rr] = (bLr[rr] + bkr[kr] - bk0r[kr]) % p
                    if vert not in done:
                        AL[rr, kcol] = (AL[rr, kcol] + Ak0[kr]) % p; bL[rr] = (bL[rr] + bk0[kr]) % p; bLr[rr] = (bLr[rr] + bk0r[kr]) % p
                done.add(vert)
        for vert in range(nv):
            if vert in done: continue
            kb = np.zeros(len(self.K2.var), dtype=np.int64)
            kb[self.low(self.VK, ("v", 0))] = states[vert]; kb[self.low(self.VK, ("v", 1))] = states[vert]
            Ak0, bk0r, bk0, _ = single(kb)
            for i in range(nvr):
                rr = row[("v", vert, i)]; kcol = [col[("v", vert, j)] for j in range(n0)]
                AL[rr, kcol] = (AL[rr, kcol] + Ak0[npr + i][:n0]) % p
                bL[rr] = (bL[rr] + bk0[npr + i]) % p; bLr[rr] = (bLr[rr] + bk0r[npr + i]) % p
        diff = (bGi - bL) % p
        return {"variety": bool(variety), "affine": bool(affG and affL), "layer-3 variables": len(var3), "rows": len(rows),
                "A equal": bool((AG == AL).all()), "intrinsic constant parts equal": bool(not diff.any()),
                "rows differing (intrinsic)": [k for k, rr in row.items() if diff[rr]][:12],
                "raw constant parts equal": bool(not ((bG - bLr) % p).any()), "slot-1 data off the diagonal": bool(active)}
