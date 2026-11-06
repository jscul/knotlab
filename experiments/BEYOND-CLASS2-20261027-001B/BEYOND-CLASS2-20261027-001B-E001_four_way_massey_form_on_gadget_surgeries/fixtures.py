"""Fixtures and frozen prediction rules of BEYOND-CLASS2-20261027-001B-E001.

Prediction rules (from the theory, fixed before the run; the constant KAPPA was read off in scoping, see contract):
  R0 (base)     on S^3_2 of a connected sum of knots whose twisted H^1 at -1 is one-dimensional, Q = 0;
  R1 (steering) inserting the 2-cable of a pure braid P with geometric conjugators in the third lower central term, at
                level l and offset o (bundles (o + 2j, o + 2j + 1)), adds KAPPA * sum_j Lam_j(c) ell_j(s), with
                Lam_j(c) = sum_{(i1,i2,i3)} M_j(i1 i2 i3) ell_i1(c_y) ell_i2(c_x) ell_i3(c_w), M_j the degree-3 Magnus part of
                the conjugator W_j of P, and ell_k(c) = c[o + 2k + 1] - c[o + 2k] for the colors c transported to level l;
                insertions add (sequential insertions are independent);
  R2 (gadget)   on the gadget manifold of a loopless multigraph, Q = KAPPA * sum over edges of the P4 tensor with leaf 0 =
                s_v - s_u and leaves k = 1, 2, 3 equal to s_{b+2k} - s_{b+2k-1} (top colors, b = n + 6e);
  R3 (counts)   sector-1 homomorphism count of a base S^3_2(K) = p^(N+4) * p^(3N), N = dim H^1(M; F_p^-); sector 0 count 1;
  R4 (lifting)  a layer-1 class triple lifts to G (independent group-law count > 0) exactly when Q(c; .) = 0."""
import glob
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(1, glob.glob(os.path.join(ROOT, "proofs/COPRIME-CLASS2-20261026-001B/*P001_*"))[0])
sys.path.insert(2, glob.glob(os.path.join(ROOT, "proofs/BEYOND-CLASS2-20261027-001A/*P001_*"))[0])
import cp_lib as C      # noqa: E402  (read-only: cable, connected_sum, Wirtinger presentation)
import bc_lib as Bc     # noqa: E402  (read-only: Fox calculus, BCH four-way group, direct layered count)
import mlib             # noqa: E402
from bm import transport  # noqa: E402

KAPPA = 2               # bm convention (y = J^T s); the level model (y = J s) has -KAPPA
KNOTS = {"4_1": ([1, -2, 1, -2], 3), "5_2": ([1, 1, 1, 2, -1, 2], 3)}
BRAIDS = {"P4": mlib.P4, "P4B": mlib.P4B}


def torus_sum(N, p):
    """closure of s1^p s2^p ... sN^p: connected sum of N copies of T(2, p), N + 1 strands"""
    return sum(([k] * p for k in range(1, N + 1)), []), N + 1


def knot_sum(name, N):
    return C.connected_sum([KNOTS[name]] * N)


def build(base, inserts):
    """inserts: (base level, braid name, offset, gamma), stacked in list order at equal levels; each becomes
    gamma . cable(braid, 2, offset) . gamma^-1.  Returns the word and the events (mid level, offset, braid)"""
    word, events, prev = [], [], 0
    for lev, braid, off, gamma in sorted(inserts, key=lambda t: t[0]):
        word += base[prev:lev] + list(gamma)
        events.append((len(word), off, braid))
        word += C.cable(BRAIDS[braid], 2, offset=off) + [-g for g in reversed(gamma)]
        prev = lev
    return word + base[prev:], events


def gadget(n, edges, p):
    """vertex v <-> strand v (1..n); edge e = (u, v), u < v: private strands b+1..b+6 (b = n + 6e); gamma drags strand v
    then strand u over to positions b, b - 1; base = connected sum of N = n + 6m copies of T(2, p)"""
    m = len(edges)
    N = n + 6 * m
    base, nstr = torus_sum(N, p)
    word, events, leaves = [], [], []
    for e, (u, v) in enumerate(edges):
        u, v = min(u, v), max(u, v)
        b = n + 6 * e
        gam = list(range(v + 1, b + 1)) + list(range(u + 1, b))
        word += gam
        events.append((len(word), b - 1, "P4"))
        word += C.cable(mlib.P4, 2, offset=b - 1) + [-g for g in reversed(gam)]
        leaves.append([(u, v)] + [(b + 2 * k - 1, b + 2 * k) for k in (1, 2, 3)])
    return word + base, nstr, events, leaves, N


def tensors(p):
    return {name: mlib.degree3_tensor(w, 4, p) for name, w in BRAIDS.items()}


def predicted_Q(cols, word, events, p, T, kappa=KAPPA, swap02=False):
    """rule R1 with transported leaves; cols: dict y, x, w, s of (batch, n) top colorings"""
    bs = cols["s"].shape[0]
    pred = np.zeros(bs, dtype=np.int64)
    for lev, off, braid in events:
        mid = {nm: transport(v, word, lev, p) for nm, v in cols.items()}
        order = [2, 1, 0, 3] if swap02 else [0, 1, 2, 3]

        def ell(nm, k):
            k = order[k]
            return (mid[nm][:, off + 2 * k + 1] - mid[nm][:, off + 2 * k]) % p

        for j in range(4):
            lam = np.zeros(bs, dtype=np.int64)
            for (i1, i2, i3), v in T[braid][j].items():
                lam = (lam + v * ell("y", i1) * ell("x", i2) * ell("w", i3)) % p
            pred = (pred + kappa * lam * ell("s", j)) % p
    return pred


def predicted_Q_closed_form(cols, leaves, p, T, kappa=KAPPA):
    """rule R2: leaves from top colors only"""
    bs = cols["s"].shape[0]
    pred = np.zeros(bs, dtype=np.int64)
    for lv in leaves:
        def ell(nm, k):
            a, b = lv[k]
            return (cols[nm][:, b] - cols[nm][:, a]) % p
        for j in range(4):
            lam = np.zeros(bs, dtype=np.int64)
            for (i1, i2, i3), v in T["P4"][j].items():
                lam = (lam + v * ell("y", i1) * ell("x", i2) * ell("w", i3)) % p
            pred = (pred + kappa * lam * ell("s", j)) % p
    return pred


# ---------------------------------------------------------------- fixture lists (frozen)
BASES_LEVEL = [("T25", 5, 1), ("T25", 5, 2), ("T25", 5, 3), ("4_1", 5, 1), ("4_1", 5, 2),
               ("T27", 7, 1), ("T27", 7, 2), ("5_2", 7, 1), ("5_2", 7, 2)]          # full tables, level model
BASES_BRAID = [(5, 4), (5, 8), (7, 4), (7, 8), (11, 4), (13, 4)]                     # T(2,p) sums, braid model, samples

# steering fixtures: (name, base spec, p, inserts); base spec ("knot", name, N) or ("torus", N)
STEERING = [
    ("4_1x4 P4 (0,0)", ("knot", "4_1", 4), 5, [(0, "P4", 0, [])]),
    ("4_1x4 P4 (4,1)", ("knot", "4_1", 4), 5, [(4, "P4", 1, [])]),
    ("4_1x4 P4 (6,0)", ("knot", "4_1", 4), 5, [(6, "P4", 0, [])]),
    ("4_1x4 P4 (9,1)", ("knot", "4_1", 4), 5, [(9, "P4", 1, [])]),
    ("5_2x4 P4 (0,0)", ("knot", "5_2", 4), 7, [(0, "P4", 0, [])]),
    ("5_2x4 P4 (5,1)", ("knot", "5_2", 4), 7, [(5, "P4", 1, [])]),
    ("T(2,5)x8 P4 (0,1)", ("torus", 8), 5, [(0, "P4", 1, [])]),
    ("T(2,7)x8 P4 (0,0)", ("torus", 8), 7, [(0, "P4", 0, [])]),
    ("T(2,11)x8 P4 (33,1)", ("torus", 8), 11, [(33, "P4", 1, [])]),
    ("T(2,13)x8 P4 (0,1)", ("torus", 8), 13, [(0, "P4", 1, [])]),
    ("4_1x4 P4B (0,0)", ("knot", "4_1", 4), 5, [(0, "P4B", 0, [])]),
    ("4_1x4 P4B (6,1)", ("knot", "4_1", 4), 5, [(6, "P4B", 1, [])]),
    ("T(2,7)x8 P4B (0,1)", ("torus", 8), 7, [(0, "P4B", 1, [])]),
    ("4_1x4 P4 (0,0) + P4B (8,1)", ("knot", "4_1", 4), 5, [(0, "P4", 0, []), (8, "P4B", 1, [])]),
    ("T(2,7)x8 P4 (0,0) + P4 (0,1)", ("torus", 8), 7, [(0, "P4", 0, []), (0, "P4", 1, [])]),
    ("T(2,5)x12 under-dragged P4", ("torus", 12), 5, [(0, "P4", 4, [-2, -3, -4])]),
    ("T(2,7)x12 shifted P4B", ("torus", 12), 7, [(14, "P4B", 3, [9, 8, 7, 6, 5, 4])]),
]
STEERING_LEVEL = [("4_1x4 P4 (6,0)", ("knot", "4_1", 4), 5, [(6, "P4", 0, [])]),
                  ("4_1x4 P4B (0,0)", ("knot", "4_1", 4), 5, [(0, "P4B", 0, [])])]
LIFT_FIXTURE = ("4_1x4 P4 (0,0)", ("knot", "4_1", 4), 5, [(0, "P4", 0, [])])
GRAPHS = {"K2": (2, [(1, 2)]), "P3": (3, [(1, 2), (2, 3)]), "digon": (2, [(1, 2), (1, 2)]),
          "K3": (3, [(1, 2), (2, 3), (1, 3)]), "K1,3": (4, [(1, 2), (1, 3), (1, 4)]),
          "C4": (4, [(1, 2), (2, 3), (3, 4), (1, 4)])}
GADGET_PRIMES = [5, 7, 11]
COUNTS = [("4_1", ([1, -2, 1, -2], 3), 5, 1, 1), ("T(2,5)", ([1] * 5, 2), 5, 1, 1),
          ("T(2,5)#T(2,5)", ([1] * 5 + [2] * 5, 3), 5, 2, 1), ("4_1 sector 0", ([1, -2, 1, -2], 3), 5, 1, 0)]
SAMPLES = 64
LIFT_SAMPLES = 40


def base_word(spec, p):
    if spec[0] == "knot":
        return knot_sum(spec[1], spec[2])
    return torus_sum(spec[1], p)
