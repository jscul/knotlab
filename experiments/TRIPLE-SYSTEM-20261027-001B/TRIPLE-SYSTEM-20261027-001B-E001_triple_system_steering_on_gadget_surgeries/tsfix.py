"""Algebras, fixtures and frozen prediction rules of TRIPLE-SYSTEM-20261027-001B-E001.

Rules (fixed before the run; KAPPA = 2 is the constant of BEYOND-CLASS2-20261027-001B-E001):
  R0 abelian triple systems: on every fixture, random free data in every minus component lift (no obstruction);
  R1 steering: for a nonabelian triple system, with x the free minus data (colorings per minus basis vector, as listed per
     algebra) and s the dual data per measured component b,
       Q(x; s) = KAPPA * sum_events sum_j sum_b < W_j^(3)(ell_0(x), .., ell_3(x)) >_b * ell_j(s_b),
     where W_j^(3) is the degree-3 Lie part of the geometric conjugator of strand j of the inserted pure braid, evaluated in n by
     the Dynkin form (1/3) sum_w M_j(w) [A_w1, [A_w2, A_w3]], and ell_k(x) = sum_a (x_a[o+2k+1] - x_a[o+2k]) e_a are the bundle
     values of the transported colorings at the insertion level;
  R2 bases: on sums of T(2, p) and 4_1, no algebra obstructs;
  R3 model agreement: for u4 the BCH model (lm.py) and the matrix model (bm.py of BEYOND-CLASS2-20261027-001B-E001) give the same Q;
  R4 lifting: for free class 3 on two minus generators, the direct layered count of BEYOND-CLASS2-20261027-001A (BCH group law on
     cp_lib's Wirtinger presentation) with fixed layer-1 data is positive exactly when Q(x; .) = 0, and then equals
     |Z1(F_p^-)|^2 (the two free layer-3 components; the layer-2 component has the trivial character and is rigid)."""
import glob
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
BX = glob.glob(os.path.join(ROOT, "experiments/BEYOND-CLASS2-20261027-001B/*E001_*"))[0]
sys.path.insert(1, BX)
sys.path.insert(2, glob.glob(os.path.join(ROOT, "proofs/COPRIME-CLASS2-20261026-001B/*P001_*"))[0])
sys.path.insert(3, glob.glob(os.path.join(ROOT, "proofs/BEYOND-CLASS2-20261027-001A/*P001_*"))[0])
from lm import LieAlg, free_nilpotent, transport  # noqa: E402
import fixtures as FX  # noqa: E402  (BEYOND-CLASS2-20261027-001B-E001: braid words, gadgets, Magnus tensors; read-only)

KAPPA = 2


def algebras(p):
    """name -> (LieAlg, free minus inputs (names), measured components (names), layer-1 restriction or None, abelian?)"""
    out = {}
    out["u4 four-way"] = (LieAlg(p, "x y w z u t".split(), [1, 1, 1, 2, 2, 3], [-1, -1, -1, 1, 1, -1],
                                 {("x", "y"): {"z": 1}, ("w", "x"): {"u": 1}, ("w", "z"): {"t": 1},
                                  ("y", "u"): {"t": -1}}), None, None, None, False)
    out["free3 (y1-, y2-)"] = (free_nilpotent(p, ["y1", "y2"], [-1, -1], 3), None, None, None, False)
    out["free3 (y1-, y2-, y3-)"] = (free_nilpotent(p, ["y1", "y2", "y3"], [-1, -1, -1], 3), None, None, None, False)
    out["free3 (x+, y1-, y2-)"] = (free_nilpotent(p, ["x", "y1", "y2"], [1, -1, -1], 3), None, None, None, False)
    out["cross4 (x+, y-)"] = (free_nilpotent(p, ["x", "y"], [1, -1], 4), None, None, None, False)
    out["free4 (x+, y1-, y2-), y1 only"] = (free_nilpotent(p, ["x", "y1", "y2"], [1, -1, -1], 4), None, None, ["y1"], False)
    out["cross3 (x+, y-)"] = (free_nilpotent(p, ["x", "y"], [1, -1], 3), None, None, None, True)
    out["cross4 mod [y,[y,[x,y]]]"] = (LieAlg(p, "x y z a b c1 c2".split(), [1, 1, 2, 3, 3, 4, 4], [1, -1, -1, -1, 1, -1, 1],
                                              {("x", "y"): {"z": 1}, ("x", "z"): {"a": 1}, ("y", "z"): {"b": 1},
                                               ("x", "a"): {"c1": 1}, ("y", "a"): {"c2": 1}, ("x", "b"): {"c2": 1}}),
                                       None, None, None, True)
    out["heisenberg (y1-, y2-)"] = (LieAlg(p, "y1 y2 z".split(), [1, 1, 2], [-1, -1, 1], {("y1", "y2"): {"z": 1}}),
                                    None, None, None, True)
    res = {}
    for name, (L, _, _, restrict, abelian) in out.items():
        top = int(L.layer.max())
        minus = [k for k in range(L.D) if L.sign[k] == -1]
        measured = [] if abelian else [k for k in minus if L.layer[k] == top]
        free = [k for k in minus if k not in measured]
        if restrict is not None:
            free = [k for k in free if L.layer[k] > 1 or L.names[k] in restrict]
        res[name] = {"L": L, "free": free, "measured": measured, "abelian": abelian}
    return res


def lie_W3(L, M, A):
    p = L.p
    third = pow(3, p - 2, p)
    out = np.zeros_like(A[0])
    for (i1, i2, i3), v in M.items():
        out = (out + v * L.br(A[i1], L.br(A[i2], A[i3]))) % p
    return out * third % p


def predicted_Q(L, word, events, inputs, svals, T, kappa=KAPPA, braid_override=None, drop_last=False, swap02=False):
    """rule R1; inputs: {k: (bs, n) colorings}, svals: {b: (bs, n) colorings}"""
    p = L.p
    bs = next(iter(svals.values())).shape[0]
    pred = np.zeros(bs, dtype=np.int64)
    evs = events[:-1] if drop_last else events
    for lev, off, braid in evs:
        mids = {k: transport(v, word, lev, p) for k, v in inputs.items()}
        smid = {b: transport(v, word, lev, p) for b, v in svals.items()}
        order = [2, 1, 0, 3] if swap02 else [0, 1, 2, 3]
        A = []
        for leaf in range(4):
            q = order[leaf]
            vec = np.zeros((bs, L.D), dtype=np.int64)
            for k, mv in mids.items():
                vec[:, k] = (mv[:, off + 2 * q + 1] - mv[:, off + 2 * q]) % p
            A.append(vec)
        Mt = T[braid_override or braid]
        for j in range(4):
            lam = lie_W3(L, Mt[j], A)
            q = order[j]
            for b, sm in smid.items():
                pred = (pred + kappa * lam[:, b] * ((sm[:, off + 2 * q + 1] - sm[:, off + 2 * q]) % p)) % p
    return pred


def fixture_words(p):
    """name -> (word, strands, events, summands); events (mid level, offset, braid)"""
    out = {}
    if p == 5:
        base, n = FX.knot_sum("4_1", 4)
        w, ev = FX.build(base, [(0, "P4", 0, [])])
        out["4_1x4 + P4 (0,0)"] = (w, n, ev, 4)
    base, n = FX.torus_sum(8, p)
    w, ev = FX.build(base, [(0, "P4", 1, []), (3 * p, "P4B", 0, [])])
    out[f"T(2,{p})x8 + P4 (0,1) + P4B ({3 * p},0)"] = (w, n, ev, 8)
    for gname, (nv, edges) in ({"K3": (3, [(1, 2), (2, 3), (1, 3)])} if p == 5 else
                              {"C4": (4, [(1, 2), (2, 3), (3, 4), (1, 4)])}).items():
        w, nstr, ev, leaves, N = FX.gadget(nv, edges, p)
        out[f"gadget {gname}"] = (w, nstr, ev, N)
    return out


def base_words(p):
    out = {}
    base, n = FX.torus_sum(4, p)
    out[f"T(2,{p})x4"] = (base, n, [], 4)
    if p == 5:
        base, n = FX.knot_sum("4_1", 3)
        out["4_1x3"] = (base, n, [], 3)
    return out
