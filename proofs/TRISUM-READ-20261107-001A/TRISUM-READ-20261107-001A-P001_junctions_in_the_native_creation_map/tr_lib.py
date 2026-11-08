"""Junctions in the native creation map, for TRISUM-READ-20261107-001.

A plain edge-atom trisum space (HANDLE-COUNT A's families: a Fano atom on every signed incidence of a minimal Pfaffian signing of a
trisum brace) is read canonically:
- its atoms are the minimal sides of 2-edge cuts of the incidence graph (7 lines, 7 points); an atom's root is its line on the cut, and
  the loaded line is the skeleton line on the other cut edge;
- contracting every atom back to an edge leaves the trisum skeleton, a cubic brace; its junctions are all its trisectors (two points and
  two lines, pairwise non-adjacent, whose removal leaves at least three components), and the junction lines are their lines;
- the leaves are the planar pieces of the skeleton split at every trisector; an atom belongs to the leaf of its edge.
The native creation map gives each ordered pair (a, b) the order-free vector (K4^(3), the Fano plane, census 58) of removing a and gluing
at b, or None when b shows fewer than six patterns (GENUS-READ A). a blocks b when removing a does not create at b (None included).
"""
import collections
import gzip
import importlib.util
import itertools
import json
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2] if (HERE.parents[2] / "AGENTS.md").exists() else Path.cwd()
for d in ("proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane",
          "proofs/THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue",
          "proofs/SEYMOUR-COUNT-20261030-001B/SEYMOUR-COUNT-20261030-001B-P001_polynomial_counting_on_seymours_cubic_bound",
          "proofs/TWIST-COUNT-20261030-001A/TWIST-COUNT-20261030-001A-P001_the_knots_junction_is_a_similitude",
          "proofs/THREEFOLD-SURFACES-20261030-001A/THREEFOLD-SURFACES-20261030-001A-P001_fano_atoms_are_handles",
          "proofs/HANDLE-COUNT-20261106-001A/HANDLE-COUNT-20261106-001A-P001_junctions_are_paid_for_by_atoms"):
    if str(ROOT / d) not in sys.path:
        sys.path.insert(0, str(ROOT / d))
import seymour_lib as SL  # noqa: E402


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------------------------------------ canonical structure
def incidence(H):
    g = nx.Graph()
    for i, l in enumerate(H):
        for p in l:
            g.add_edge(('L', i), ('P', p))
    return g


def atom_sides(H):
    """the minimal sides of 2-edge cuts of the incidence graph"""
    B = incidence(H)
    sides = set()
    for e in list(B.edges()):
        B.remove_edge(*e)
        for f in nx.bridges(B):
            B.remove_edge(*f)
            comps = sorted(nx.connected_components(B), key=len)
            B.add_edge(*f)
            if len(comps) == 2:
                sides.add(frozenset(comps[0]))
        B.add_edge(*e)
    return B, [X for X in sides if not any(Y < X for Y in sides)]


def structure(H):
    B, mins = atom_sides(H)
    G = B.copy()
    atoms = []
    for X in sorted(mins, key=lambda X: sorted(map(str, X))):
        bd = [(u, w) for u in X for w in B[u] if w not in X]
        assert len(bd) == 2 and sum(1 for v in X if v[0] == 'L') == 7 and sum(1 for v in X if v[0] == 'P') == 7, bd
        (u1, w1), (u2, w2) = bd
        G.remove_nodes_from(X)
        G.add_edge(w1, w2)
        atoms.append({"lines": sorted(v[1] for v in X if v[0] == 'L'), "root": [u[1] for u, w in bd if u[0] == 'L'][0],
                      "loaded": [w[1] for u, w in bd if w[0] == 'L'][0], "edge": (w1, w2)})
    assert all(d == 3 for _, d in G.degree())
    lines = {v for v in G if v[0] == 'L'}
    T = SL.all_trisectors(G, lines)
    leaves, squares = SL.trisum_tree(G, lines)
    assert {frozenset(s) for s in squares} == T
    owner = {l: k for k, A in enumerate(atoms) for l in A["lines"]}
    junction = sorted({v[1] for t in T for v in t if v[0] == 'L'})
    mates = {frozenset(v[1] for v in t if v[0] == 'L') for t in T}
    sq = {v for t in T for v in t}
    leaf = {}
    for i, (h, sqs) in enumerate(leaves):
        for v in h:
            if v[0] == 'L' and v not in sq:
                leaf[v[1]] = i
    for k, A in enumerate(atoms):
        w1, w2 = A["edge"]
        ends = [i for i, (h, sqs) in enumerate(leaves) if h.has_edge(w1, w2)]
        assert len(ends) == 1, ends
        for l in A["lines"]:
            leaf[l] = ends[0]
    return {"n": len(H), "G": G, "atoms": atoms, "owner": owner, "atom lines": set(owner),
            "core": {l for A in atoms for l in A["lines"] if l != A["root"]}, "roots": {A["root"] for A in atoms},
            "loaded": {A["loaded"] for A in atoms}, "skeleton": {v[1] for v in lines}, "junction": set(junction), "mates": mates,
            "trisectors": T, "leaf": leaf, "leaves": len(leaves)}


# ------------------------------------------------------------------------------------------------ maps
def free(v):
    return None if v is None else (v[0], v[2], v[3])


def load_map(path):
    d = json.load(gzip.open(path, "rt"))
    H = [tuple(l) for l in d["lines"]]
    ex = {int(a): {int(b): (None if v is None else tuple(bool(x) for x in v)) for b, v in r["row"].items()} for a, r in d["rows"].items()}
    return d, H, ex


def creates(ex, a, b):
    v = ex[a].get(b)
    return v is not None and any(v)


def blocks(ex, n):
    """B[l]: removals that do not create at l; D[l]: removals at which l is degenerate"""
    B = {l: {a for a in range(n) if a != l and not creates(ex, a, l)} for l in range(n)}
    D = {l: {a for a in range(n) if a != l and ex[a].get(l) is None} for l in range(n)}
    return B, D


def pinned_apart(ex, n, A):
    """pairs of lines outside A, never degenerate at removals outside A, each the only removal outside A that blocks the other"""
    B, D = blocks(ex, n)
    Bp = {l: B[l] - A for l in range(n)}
    Dp = {l: D[l] - A for l in range(n)}
    return {frozenset((a, b)) for a, b in itertools.combinations(range(n), 2) if a not in A and b not in A
            and not Dp[a] and not Dp[b] and Bp[a] == {b} and Bp[b] == {a}}


def yesno_atoms(ex, n):
    """atoms read by yes/no creation alone: core = lines no removal blocks; a root = a line created at by exactly six removals, all core;
    its atom = the root and those six"""
    B, D = blocks(ex, n)
    core = {l for l in range(n) if not B[l]}
    atoms = []
    for r in range(n):
        cr = {a for a in range(n) if a != r and creates(ex, a, r)}
        if len(cr) == 6 and cr <= core:
            atoms.append(frozenset(cr | {r}))
    return core, atoms


# ------------------------------------------------------------------------------------------------ refinement
def union_of_pair_classes(P, n, rel):
    seen = {}
    for a in range(n):
        for b in range(n):
            if a != b and seen.setdefault(P[a][b], rel(a, b)) != rel(a, b):
                return False
    return True


def union_of_vertex_classes(cls, n, S):
    seen = {}
    return all(seen.setdefault(cls[a], a in S) == (a in S) for a in range(n))


def report(H, ex, RL):
    """every frozen test on one space"""
    st = structure(H)
    n = st["n"]
    nat = lambda a, b: free(ex[a].get(b))  # noqa: E731
    yn = lambda a, b: creates(ex, a, b)  # noqa: E731
    P = RL.pair_refine(n, nat)
    Dg = [P[a][a] for a in range(n)]
    V = RL.vertex_refine(n, yn)
    B, D = blocks(ex, n)
    core, yatoms = yesno_atoms(ex, n)
    out = {
        "points": 1 + max(max(l) for l in H), "lines": n, "atoms": len(st["atoms"]), "junctions": len(st["trisectors"]),
        "junction lines": len(st["junction"]), "loaded junction lines": len(st["junction"] & st["loaded"]),
        "P1 same atom is a union of native pair classes": union_of_pair_classes(
            P, n, lambda a, b: a in st["owner"] and b in st["owner"] and st["owner"][a] == st["owner"][b]),
        "P1 skeleton lines are a union of native diagonal classes": union_of_vertex_classes(Dg, n, st["skeleton"]),
        "P1 junction lines are a union of native diagonal classes": union_of_vertex_classes(Dg, n, st["junction"]),
        "P1 roots are a union of native diagonal classes": union_of_vertex_classes(Dg, n, st["roots"]),
        "P1 loaded lines are a union of native diagonal classes": union_of_vertex_classes(Dg, n, st["loaded"]),
        "P1 square-mates are a union of native pair classes": union_of_pair_classes(P, n, lambda a, b: frozenset((a, b)) in st["mates"]),
        "P2 junction lines are a union of yes/no colour classes": union_of_vertex_classes(V, n, st["junction"]),
        "P3 the lines no removal blocks are the atom cores": core == st["core"],
        "P4 yes/no creation reads the atoms (root and its six creators)": sorted(map(sorted, yatoms)) == sorted(A["lines"] for A in st["atoms"]),
        "P5 the pairs pinned apart from the atoms are the trisectors' line pairs": pinned_apart(ex, n, st["atom lines"]) == st["mates"],
        "P6 every pinned pair (yes/no alone) is a trisector's line pair": pinned_apart(ex, n, set()) <= st["mates"],
        "P7 same leaf is a union of native pair classes": union_of_pair_classes(
            P, n, lambda a, b: a in st["leaf"] and b in st["leaf"] and st["leaf"][a] == st["leaf"][b]),
        "pinned pairs (yes/no alone)": len(pinned_apart(ex, n, set())),
    }
    return out


# ------------------------------------------------------------------------------------------------ fast exact rows
_CT = None


def engine():
    """CHAIN-TRANSFER B's tree_lib (its TL is CHAIN-TRANSFER A's transfer_lib: solutions, PY, verdict_from_masks)"""
    global _CT
    if _CT is None:
        _CT = load("tr_ct_tree_lib", ROOT / "proofs/CHAIN-TRANSFER-20261106-001B/CHAIN-TRANSFER-20261106-001B-P001_the_source_rule_on_larger_trees"
                   / "tree_lib.py")
    return _CT


def fast_masks(AN, Y, sig, others):
    """TL.near_masks by one matrix product per pattern of Y: for each pattern k and points x < w, the pairs of values (x, w) that occur
    are read from N11 = S_k^T S_k and the column sums of S_k (S_k: the solutions showing pattern k, restricted to the other points).
    Counts are exact in float32 (below 2^24)."""
    import numpy as np
    TL = engine().TL
    AN = np.asarray(AN)
    pat = {p: i for i, p in enumerate(TL.PY)}
    lut = np.full(8, -1, dtype=np.int64)
    for p, i in pat.items():
        lut[p[0] * 4 + p[1] * 2 + p[2]] = i
    yv = [(AN[:, Y[j]].astype(np.int64) ^ sig[j]) for j in range(3)]
    yi = lut[yv[0] * 4 + yv[1] * 2 + yv[2]]
    assert (yi >= 0).all()
    if len(np.unique(yi)) != 6:
        return None
    O = AN[:, others]
    m = len(others)
    M1 = np.zeros(m, dtype=np.int64)
    M2 = np.zeros((m, m), dtype=np.int64)
    for k in range(6):
        Sk = O[yi == k].astype(np.float32)
        nk = Sk.shape[0]
        c = Sk.sum(axis=0, dtype=np.float64).astype(np.int64)
        N11 = np.rint(Sk.T @ Sk).astype(np.int64)
        M1 |= ((c > 0).astype(np.int64) << (2 * k + 1)) | (((nk - c) > 0).astype(np.int64) << (2 * k))
        ci, cj = c[:, None], c[None, :]
        M2 |= ((N11 > 0).astype(np.int64) << (4 * k + 3)) | (((ci - N11) > 0).astype(np.int64) << (4 * k + 1)) | \
            (((cj - N11) > 0).astype(np.int64) << (4 * k + 2)) | (((nk - ci - cj + N11) > 0).astype(np.int64) << (4 * k))
    iu = np.triu_indices(m, 1)
    return {int(x) for x in M1}, {int(x) for x in M2[iu]}


def exact_row(H, n, M):
    """one row of the exact creation map of the plain space H (every line's signs 0): {L: None or the 4 far-side verdicts}, and the
    number of solutions of H minus line M (as CHAIN-TRANSFER B's exact_row, with fast_masks in place of TL.near_masks)"""
    TL = engine().TL
    AN = TL.solutions([tuple(l) for l in H], [(0, 0, 0)] * len(H), n, skip=M)
    out = {}
    for L in range(len(H)):
        if L != M:
            Y = list(H[L])
            mm = fast_masks(AN, Y, (0, 0, 0), [q for q in range(n) if q not in Y])
            out[L] = None if mm is None else TL.verdict_from_masks(*mm)
    return out, len(AN)
