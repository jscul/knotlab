"""COPRIME-PAIRS-20261027-001D: zero-jump gadgets for pair failures and the edge-local count.

Blocks. A summand braid is conjugated and stabilized so that its first strand ('base') and last strand ('end') carry the base
value exactly, an internal reading strand ('read') has a class colouring different from the base at every root character, and
'copy' strands are exact copies of the reading strand (Markov stabilizations).  Connected sums of such blocks have every junction
strand equal to the pinned meridian value tau, so every strand's colour is a function of its own block's data.

Gadget for a loopless graph: vertex blocks (type theta_0), then per edge (d-1) unknot blocks + a slot-2 block (type theta_1) and
(d-1) unknot blocks + a slot-3 block (type theta_2).  Edge (u, v), u < v: one insertion of cable_d(P), P = [A12, A23], on bundles
  0: (d-1 copies of u's reading value dedicated to the edge, 1 copy of v's);  1: (d-1 base strands, r_{e,1});  2: (d-1, r_{e,2}).

Model: cd_lib.CyclicBraidModel at slope d/p; free data = coefficients of block class colourings (per block, character, component);
equations = pairings <residual, J_t^T s> with block dual colourings s, layer by layer.  Conventions as in gd / cd_lib.
"""
import glob, sys, itertools
import numpy as np
ROOT = "/home/jscul/p-vs-np-contact-first"
for i, pat in enumerate(["proofs/COPRIME-DICHOTOMY-20261027-001A/*P001_*", "experiments/COPRIME-DICHOTOMY-20261027-001B/*E002_*",
                         "experiments/TRIPLE-SYSTEM-20261027-001B/*E001_*", "proofs/COPRIME-CLASS2-20261026-001B/*P001_*"]):
    sys.path.insert(i, glob.glob(f"{ROOT}/{pat}")[0])
from cd_lib import BraidAlg, CyclicBraidModel, braid_meta, nullspace, solve_any, root_of_unity, free_graded  # noqa: E402
import gd, mlib  # noqa: E402
import cp_lib as C  # noqa: E402

UNKNOT = ([1], 2)


def inv_word(w):
    return [-g for g in reversed(w)]


def over_move(src, dst):
    if src < dst: return [q + 1 for q in range(src, dst)]
    return [-q for q in range(src, dst, -1)]


def fixed(word, n, t, p):
    return nullspace((gd.bur_word(word, n, t, p) - np.eye(n, dtype=np.int64)) % p, p)


def class_vec(word, n, t, p):
    F = fixed(word, n, t, p)
    if len(F) != 2: return None
    v = next(f for f in F if len(set(((f - f[0]) % p).tolist())) > 1)
    return (v - v[0]) % p


def separating_pair(labs):
    n = len(labs[0])
    for a in range(n):
        for b in range(n):
            if a != b and all(l[a] != l[b] for l in labs): return a, b
    return None


class Block:
    def __init__(self, word, n, tags):
        self.word, self.n, self.tags = list(word), n, list(tags)

    def move(self, src, dst):
        self.word = inv_word(over_move(src, dst)) + self.word + over_move(src, dst)
        t = list(self.tags); s = t.pop(src); t.insert(dst, s); self.tags = t

    def stabilize(self, tag):
        self.word = self.word + [self.n]; self.n += 1; self.tags = self.tags + [tag]


def zero_jump_block(word, n, roots, zeta, p, ncopies):
    labs = [class_vec(word, n, pow(zeta, c, p), p) for c in roots]
    assert all(l is not None for l in labs), "a root character without a one-dimensional class"
    qa, qb = separating_pair([[int(x) for x in l] for l in labs])
    B = Block(word, n, ["x"] * n)
    B.tags[qa] = "base"; B.tags[qb] = "read"
    B.move(B.tags.index("base"), 0)
    if ncopies:
        B.move(B.tags.index("read"), B.n - 1)
        for _ in range(ncopies): B.stabilize("copy")
    B.move(0, B.n - 1); B.stabilize("end"); B.move(B.n - 2, 0)
    assert B.tags[0] == "base" and B.tags[-1] == "end"
    return B


def plain_block(word, n):
    return Block(word, n, ["base"] + ["x"] * (n - 2) + ["end"])


def connected_sum(blocks):
    word, off, pos = [], 0, []
    for bi, B in enumerate(blocks):
        word += [(abs(x) + off) * (1 if x > 0 else -1) for x in B.word]
        for q, t in enumerate(B.tags):
            if bi > 0 and q == 0: continue
            pos.append((bi, t, off + q))
        off += B.n - 1
    return word, off + 1, pos


def build_gadget(nv, edges, d, types, zeta, p, zero_jump=True, P=None, pad=0):
    """types: {0: (word, n, roots), 1: ..., 2: ...} for the vertex, slot-2 and slot-3 blocks"""
    P = mlib.X12_23 if P is None else P
    lo = {v: sum(1 for (a, b) in edges if a == v) for v in range(nv)}
    hi = {v: sum(1 for (a, b) in edges if b == v) for v in range(nv)}
    blocks, kinds = [], []
    for v in range(nv):
        w, n, roots = types[0][:3]
        if zero_jump:
            blocks.append(zero_jump_block(w, n, roots, zeta, p, (d - 1) * lo[v] + hi[v])); kinds.append(("vertex", v))
        else:
            blocks.append(plain_block(w, n)); kinds.append(("vertex", v))
            for _ in range(d - 2): blocks.append(Block(*UNKNOT, ["base", "end"])); kinds.append(("vcopy", v))
    for e in range(len(edges)):
        for k in (1, 2):
            w, n, roots = types[k][:3]
            for _ in range(d - 1): blocks.append(Block(*UNKNOT, ["base", "end"])); kinds.append(("zero", e, k))
            blocks.append(zero_jump_block(w, n, roots, zeta, p, 0) if zero_jump else plain_block(w, n))
            kinds.append(("private", e, k))
    for _ in range(pad): blocks.append(Block(*UNKNOT, ["base", "end"])); kinds.append(("pad",))
    word, n, pos = connected_sum(blocks)

    def strands(bi, tag):
        return [q for (b, t, q) in pos if b == bi and t == tag]
    vb = {kinds[i][1]: i for i in range(len(kinds)) if kinds[i][0] == "vertex"}
    used = {v: 0 for v in range(nv)}
    events = []
    for e, (u, v) in enumerate(edges):
        assert u < v
        if zero_jump:
            cu, cv = strands(vb[u], "copy"), strands(vb[v], "copy")
            b0 = cu[used[u]: used[u] + d - 1] + [cv[used[v]]]; used[u] += d - 1; used[v] += 1
        else:
            b0 = strands(vb[u], "end") + [strands(i, "end")[0] for i in range(len(kinds)) if kinds[i] == ("vcopy", u)] + strands(vb[v], "end")
        bks = [b0]
        for k in (1, 2):
            zeros = [strands(i, "end")[0] for i in range(len(kinds)) if kinds[i] == ("zero", e, k)][:d - 1]
            pi = next(i for i in range(len(kinds)) if kinds[i] == ("private", e, k))
            bks.append(zeros + (strands(pi, "read") if zero_jump else strands(pi, "end")))
        chosen = [s for bl in bks for s in bl]
        assert chosen == sorted(chosen) and len(chosen) == 3 * d
        target = n - 3 * d
        assert all(s <= target + i for i, s in enumerate(chosen)), "insertion does not fit: add padding"
        gam = gd.gather(chosen, n, target)
        events.append((len(word) + len(gam), target, [[target + j * d + i for i in range(d)] for j in range(3)]))
        word += gam + C.cable(P, d, offset=target) + inv_word(gam)
    return word, n, events, blocks, kinds, pos


def block_classes(blocks, kinds, pos, n, d, zeta, p, zero_jump=True):
    """{(block, character): class colouring in the gadget's top labelling}"""
    out = {}
    for bi, B in enumerate(blocks):
        if kinds[bi][0] not in ("vertex", "private"): continue
        first = min(q for (b, t, q) in pos if b == bi) - (0 if bi == 0 else 1)
        for c in range(1, d):
            v = class_vec(B.word, B.n, pow(zeta, c, p), p)
            if v is None: continue
            g = np.zeros(n, dtype=np.int64)
            g[first:first + B.n] = v
            if not zero_jump: g[first + B.n:] = v[-1]
            out[(bi, c)] = g % p
    return out


def site(kind):
    return ("v", kind[1]) if kind[0] == "vertex" else ("e", kind[1])


class Gadget:
    """the counting model of one gadget for one algebra"""

    def __init__(self, L, d, p, types, nv, edges, zero_jump=True, pad=0):
        self.L, self.d, self.p = L, d, p
        self.zeta = root_of_unity(p, d)
        self.word, self.n, self.events, self.blocks, self.kinds, self.pos = build_gadget(nv, edges, d, types, self.zeta, p,
                                                                                       zero_jump, pad=pad)
        self.A = BraidAlg(L, self.zeta)
        self.Mo = CyclicBraidModel(self.word, self.n, self.A, p)
        self.cls = block_classes(self.blocks, self.kinds, self.pos, self.n, d, self.zeta, p, zero_jump)
        top = int(L.layer.max())
        ch = lambda k: int(L.chars[k]) % d
        # free data: (block, component) for components below the top layer at a character with a class on the block
        self.var = [(bi, k) for (bi, c) in self.cls for k in range(L.D) if ch(k) == c and L.layer[k] < top]
        self.var.sort(key=lambda x: (int(L.layer[x[1]]), x[0], x[1]))
        # equations: (block, component) for components of layer >= 2 whose dual character has a class on the block
        self.eqs = [(bi, k) for (bi, c) in self.cls for k in range(L.D) if L.layer[k] >= 2 and ch(k) % d and (-ch(k)) % d == c]
        self.nv, self.edges = nv, edges

    def site_of(self, bi):
        return site(self.kinds[bi])

    def evaluate(self, vals):
        """vals: (bs, len(var)) -> (bs, len(eqs)) equation values, layer by layer with particular solutions"""
        L, p, n, d = self.L, self.p, self.n, self.d
        ch = lambda k: int(L.chars[k]) % d
        bs = len(vals)
        V = np.zeros((bs, n, L.D), dtype=np.int64)
        add = {}
        for j, (bi, k) in enumerate(self.var):
            add[k] = (add.get(k, 0) + vals[:, j:j + 1] * self.cls[(bi, ch(k))][None, :]) % p
        out = np.zeros((bs, len(self.eqs)), dtype=np.int64)
        for lay in range(1, int(L.layer.max()) + 1):
            R = self.Mo.run(V)
            for col, (bi, k) in enumerate(self.eqs):
                if L.layer[k] == lay:
                    t = pow(self.zeta, ch(k), p)
                    J = gd.squier(n, t, p)
                    out[:, col] = (R[:, :n, k] @ ((J.T @ self.cls[(bi, (-ch(k)) % d)]) % p)) % p
            for k in [k for k in range(L.D) if L.layer[k] == lay]:
                X, bad = solve_any(self.Mo.Lin[ch(k)], (-R[:, :, k]).T % p, p)
                V[:, :, k] = (X.T + add.get(k, 0)) % p
        return out

    def var_sites(self):
        return [self.site_of(bi) for (bi, k) in self.var]

    def eq_sites(self):
        return [self.site_of(bi) for (bi, k) in self.eqs]


# ------------------------------------------------------------------------------------------------ edge counts and locality
def summand_types(p, d, slots):
    """summand braids whose root characters are exactly R(theta): amphichiral 3-braids (gd.AMPH) at odd order, (k,1)-cables of
    T(2,p) at even order 2k"""
    zeta = root_of_unity(p, d)
    out = {}
    for i, th in enumerate(slots):
        o = d // int(np.gcd(th % d, d))
        if o % 2 == 1:
            want = {th % d, (-th) % d}
            for name, (w, n) in gd.AMPH.items():
                act = {c for c in range(1, d) if len(fixed(w, n, pow(zeta, c, p), p)) > 1}
                if act == want and all(class_vec(w, n, pow(zeta, c, p), p) is not None for c in want):
                    out[i] = (w, n, sorted(want), name); break
        else:
            k = o // 2
            w, n = gd.torus_cable(p, k)
            out[i] = (w, n, sorted(al for al in range(1, d) if (al * k) % d == d // 2), f"C_{k} of T(2,{p})")
        assert i in out, f"no summand for slot {i} (theta = {th})"
    return out


def evaluate_chunked(G, vals, chunk=20000):
    out = []
    for s in range(0, len(vals), chunk):
        out.append(G.evaluate(vals[s:s + chunk]))
    return np.concatenate(out) if out else np.zeros((0, len(G.eqs)), dtype=np.int64)


def edge_count(G, su, sv, chunk=20000):
    """single-edge gadget: number of private configurations solving every equation for vertex states su, sv; also the number of
    nonzero vertex-dual pairings on those solutions"""
    p = G.p
    vs = G.var_sites()
    iu = [j for j, s in enumerate(vs) if s == ("v", 0)]; iv = [j for j, s in enumerate(vs) if s == ("v", 1)]
    ip = [j for j, s in enumerate(vs) if s[0] == "e"]
    combos = np.array(list(itertools.product(range(p), repeat=len(ip))), dtype=np.int64)
    vals = np.zeros((len(combos), len(G.var)), dtype=np.int64)
    vals[:, ip] = combos; vals[:, iu] = su; vals[:, iv] = sv
    E = evaluate_chunked(G, vals, chunk) % p
    vcols = [c for c, s in enumerate(G.eq_sites()) if s[0] == "v"]
    pcols = [c for c, s in enumerate(G.eq_sites()) if s[0] == "e"]
    sol_priv = ~E[:, pcols].any(axis=1)
    vbad = int(E[sol_priv][:, vcols].any(axis=1).sum()) if vcols else 0
    return int(sol_priv.sum()), vbad, len(combos), combos[sol_priv]
