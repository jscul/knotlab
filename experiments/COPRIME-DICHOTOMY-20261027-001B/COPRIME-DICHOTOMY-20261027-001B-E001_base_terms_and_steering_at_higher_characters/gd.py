"""COPRIME-DICHOTOMY-20261027-001B: Squier duality at a character t of order d, summand braids with vanishing local forms
(negative amphichiral knots; (k,1)-cables of T(2,p)), gadget surgeries with d-strand bundles, and the predicted steering form.
Measurement uses cd_lib.CyclicBraidModel (COPRIME-DICHOTOMY-20261027-001A-P001) at slope d/p."""
import itertools
import numpy as np
from cd_lib import GLie, BraidAlg, CyclicBraidModel, solve_any, nullspace, root_of_unity, free_graded, quotient, pair_failures
import cp_lib as C
import mlib


# ------------------------------------------------------------------------------------------------ Burau and Squier forms
def bur(n, g, t, p):
    """Fox-colour matrix of one letter at the character t (top colours to bottom colours)"""
    M = np.eye(n, dtype=np.int64)
    i = abs(g) - 1
    ti = pow(t, p - 2, p)
    if g > 0:
        M[i, i], M[i, i + 1], M[i + 1, i], M[i + 1, i + 1] = (1 - ti) % p, ti, 1, 0
    else:
        M[i, i], M[i, i + 1], M[i + 1, i], M[i + 1, i + 1] = 0, 1, t % p, (1 - t) % p
    return M


def bur_word(word, n, t, p):
    M = np.eye(n, dtype=np.int64)
    for g in word: M = bur(n, g, t, p) @ M % p
    return M


def squier(n, t, p):
    """J_t: lower unitriangular, J[q, q'] = (t - 1) t^(q - q' - 1) for q > q'; Bur_{1/t}(g)^T J Bur_t(g) = J"""
    J = np.eye(n, dtype=np.int64)
    for q in range(n):
        for q2 in range(q):
            J[q, q2] = (t - 1) * pow(t, q - q2 - 1, p) % p
    return J


def kappa(t, p):
    ti = pow(t, p - 2, p)
    return (ti * ti - ti) % p


# ------------------------------------------------------------------------------------------------ summands
AMPH = {"4_1": ([1, -2, 1, -2], 3), "6_3": ([1, 1, -2, 1, -2, -2], 3), "8_9": ([1, 1, 1, -2, 1, -2, -2, -2], 3),
        "8_17": ([1, 1, -2, 1, -2, 1, -2, -2], 3), "8_18": ([1, -2] * 4, 3)}
CHIRAL = {"3_1": ([1, 1, 1], 2), "5_2": ([1, 1, 1, 2, -1, 2], 3), "6_1": ([1, 1, 2, -1, -3, 2, -3], 4),
          "7_5": ([1] * 4 + [2, -1, 2, 2], 3), "8_5": ([1, 1, 1, -2, 1, 1, 1, -2], 3)}
UNKNOT = ([1], 2)


def cable_k1(word, n, k):
    """(k,1)-cable of the closure of word on n strands: blackboard k-cable plus delta_k^(1 - k * writhe) on the first bundle"""
    out = C.cable(word, k)
    w = sum(1 if g > 0 else -1 for g in word)
    j = 1 - k * w
    delta = list(range(1, k))
    out += delta * j if j > 0 else [-g for g in reversed(delta)] * (-j)
    return out, n * k


def torus_cable(p, k):
    return cable_k1([1] * p, 2, k)


# ------------------------------------------------------------------------------------------------ gadgets
def gather(positions, n, target_start):
    """braid moving the strands at the given (increasing) positions, as over-strands, to target_start, target_start + 1, ...
    (target block to the right of every chosen strand's start is not required: strands move right over unchosen ones only;
    returns the word and the final permutation)"""
    pos = list(range(n))           # pos[q] = strand currently at position q
    where = {s: q for q, s in enumerate(pos)}
    word = []
    chosen = [pos[q] for q in positions]
    for k in reversed(range(len(chosen))):
        s = chosen[k]
        tgt = target_start + k
        q = where[s]
        assert q <= tgt
        while q < tgt:
            word.append(q + 1)     # positive letter at positions (q, q+1): strand at q moves right as the over-strand
            other = pos[q + 1]
            pos[q], pos[q + 1] = other, s
            where[other], where[s] = q, q + 1
            q += 1
    return word


def build_gadget(nv, edges, d, vertex_summand, private_summand):
    """base: for each vertex v its summand followed by (d - 2) unknot blocks (copies of the vertex colour c_v); then, for every
    edge, three private blocks, each (d - 1) unknot blocks (copies of the colour before) and a private summand.  Edge (u, v)
    with u < v gets one insertion of cable_d(P4) on the bundles
      0: (r_u, copies of c_u, r_v), reading X_v - X_u at every character (the d bundle coefficients t^(d-1-i) sum to 0);
      k = 1, 2, 3: (copies, r_P), reading the private coordinate z_P = c_P - c_(before P).
    Returns word, n, events [(middle level, offset, bundles)], vertex reading strands, private bundles."""
    blocks, kinds = [], []
    for v in range(nv):
        blocks.append(vertex_summand); kinds.append(("vertex", v))
        blocks += [UNKNOT] * (d - 2); kinds += [("copy", v)] * (d - 2)
    for e in range(len(edges)):
        for k in range(3):
            blocks += [UNKNOT] * (d - 1); kinds += [("pcopy", e, k)] * (d - 1)
            blocks.append(private_summand); kinds.append(("private", e, k))
    base, n = C.connected_sum(blocks)
    last, off = [], 0
    for (w, nb) in blocks:
        last.append(off + nb - 1); off += nb - 1
    vstr = {kd[1]: last[i] for i, kd in enumerate(kinds) if kd[0] == "vertex"}
    vcopies = {v: [last[i] for i, kd in enumerate(kinds) if kd == ("copy", v)] for v in range(nv)}
    pb = {}
    for e in range(len(edges)):
        for k in range(3):
            cps = [last[i] for i, kd in enumerate(kinds) if kd == ("pcopy", e, k)]
            prv = [last[i] for i, kd in enumerate(kinds) if kd == ("private", e, k)][0]
            pb[(e, k)] = cps + [prv]
    word = list(base)
    events = []
    for e, (u, v) in enumerate(edges):
        assert u < v
        bundles = [[vstr[u]] + vcopies[u] + [vstr[v]]] + [pb[(e, k)] for k in range(3)]
        chosen = [s for bl in bundles for s in bl]
        assert chosen == sorted(chosen), "bundle strands must appear left to right in bundle order"
        target = n - 4 * d
        gam = gather(chosen, n, target)
        mid_bundles = [[target + j * d + i for i in range(d)] for j in range(4)]   # positions at the middle level
        events.append((len(word) + len(gam), target, mid_bundles))
        word += gam + C.cable(mlib.P4, d, offset=target) + [-g for g in reversed(gam)]
    return word, n, events, vstr, pb


# ------------------------------------------------------------------------------------------------ measurement and prediction
def layered(Mo, inputs, upto):
    """solve layers < upto (free odd components from inputs), return relator values (bs, n+1, D), labels V and lower ok"""
    A, p, n = Mo.A, Mo.p, Mo.n
    bs = next(iter(inputs.values())).shape[0]
    V = np.zeros((bs, n, A.D), dtype=np.int64)
    ok = np.ones(bs, dtype=bool)
    for lay in range(1, upto):
        R = Mo.run(V)
        for k in [k for k in range(A.D) if A.layer[k] == lay]:
            X, bad = solve_any(Mo.Lin[int(A.chars[k])], (-R[:, :, k]).T % p, p)
            ok &= ~bad
            V[:, :, k] = (X.T + (inputs[k] if k in inputs else 0)) % p
    return Mo.run(V), V, ok


def measure_Q(Mo, inputs, layer, comp, s):
    """<o, (J_t^T s, 0)> at component comp of the given layer (t = its character), s: (bs, n) dual cocycles at 1/t"""
    A, p, n = Mo.A, Mo.p, Mo.n
    R, V, ok = layered(Mo, inputs, layer)
    t = pow(A.zeta, int(A.chars[comp]), p)
    J = squier(n, t, p)
    y = (s @ J) % p
    return (R[:, :n, comp] * y).sum(axis=1) % p, ok, R, V


def leaf_values(word, n, level, bundle, colours, t, p):
    """bundle functional sum_i t^(d-1-i) c_i on the colours at the given level (reverse-order bundle product)"""
    col = (colours @ bur_word(word[:level], n, t, p).T) % p
    d = len(bundle)
    return sum(pow(t, d - 1 - i, p) * col[:, s] for i, s in enumerate(bundle)) % p


def predict_Q(L, A, word, n, events, data_top, s_top, comp, p, k_override=None, tensor=None, reverse=True):
    """kappa_t sum_events sum_j <W_j^(3)(leaves of all odd data)>_comp * ell_j(s), t = character of comp.
    data_top: {component index: (bs, n) top values} for every odd free component (all layers); s_top: (bs, n) at 1/t"""
    T3 = tensor or mlib.degree3_tensor(mlib.P4, 4, p)
    inv3 = pow(3, p - 2, p)
    t = pow(A.zeta, int(L.chars[comp]), p)
    tinv = pow(t, p - 2, p)
    bs = s_top.shape[0]
    total = np.zeros(bs, dtype=np.int64)
    for (level, off, bundles) in events:
        leaves = np.zeros((bs, 4, L.D), dtype=np.int64)
        for k, vals in data_top.items():
            tk = pow(A.zeta, int(L.chars[k]), p)
            for j, bl in enumerate(bundles):
                b = bl if reverse else list(reversed(bl))
                leaves[:, j, k] = leaf_values(word, n, level, b, vals, tk, p)
        for j, bl in enumerate(bundles):
            b = bl if reverse else list(reversed(bl))
            dual = leaf_values(word, n, level, b, s_top, tinv, p)
            Lam = np.zeros((bs, L.D), dtype=np.int64)
            for (i1, i2, i3), v in T3[j].items():
                Lam = (Lam + v * L.br(leaves[:, i1], L.br(leaves[:, i2], leaves[:, i3]))) % p
            total = (total + Lam[:, comp] * inv3 % p * dual) % p
    kap = kappa(t, p) if k_override is None else k_override % p
    return total * kap % p


# ------------------------------------------------------------------------------------------------ algebras
def four_way(p, d, e=1):
    return GLie.from_brackets(p, d, "x y w z u t".split(), [1, 1, 1, 2, 2, 3], [e, -e, -e, 0, 0, -e],
                              {("x", "y"): {"z": 1}, ("w", "x"): {"u": 1}, ("w", "z"): {"t": 1}, ("y", "u"): {"t": -1}})


def p2_quotient(L, d=None):
    """quotient by the ideal generated by every failing pair [n_a, n_b] (a, b, a + b nonzero mod d)"""
    d = L.d if d is None else d
    vecs = []
    for a in range(1, d):
        for b in range(1, d):
            if (a + b) % d:
                vecs += [L.br(L.unit(i), L.unit(j))[0] for i in L.comp(a, d) for j in L.comp(b, d)]
    vecs = [v for v in vecs if v.any()]
    return quotient(L, vecs) if vecs else L


def layer4_algebra(p, d, e=1):
    """P2-quotient of free class 4 on (x: trivial, y: e, v: -e), modulo the layer-3 odd triples of layer-1 elements
    [[y, v], y] and [[y, v], v]: layer 3 never obstructs, layer-4 triples through the free layer-2 classes survive"""
    F = p2_quotient(free_graded(p, d, [0, e, -e], 4, ["x", "y", "v"]))
    iy, iv = F.idx["y"], F.idx["v"]
    yv = F.br(F.unit(iy), F.unit(iv))
    return quotient(F, [F.br(yv, F.unit(iy))[0], F.br(yv, F.unit(iv))[0]])
