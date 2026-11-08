"""Creation between glue lines depends only on the switching class, for SWITCH-PROOF-20261108-001A.

A plain edge-atom space X_S is a glue H (a cubic incidence system) with a Fano atom on every incidence of a signing S (HANDLE-COUNT A's
FA.edge_atoms). The signed glue (H, S) is H with the incidences of S negated: a line is satisfied when its literals x_q xor s are not all
equal. Its creation map uses the same test as the plain space's, with the gluing line's signs (CHAIN-TRANSFER A's near masks).
- atom_report(): the edge atom's own lines, exhaustively: what its points do given its glue point p.
- switching_witness(): a set U of points and lines with S' = S xor delta(U), when there is one.
- signed_row(): one row of the signed glue's creation map.
"""
import collections
import itertools
import json
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2] if (HERE.parents[2] / "AGENTS.md").exists() else Path.cwd()
TRA = ROOT / "proofs/TRISUM-READ-20261107-001A/TRISUM-READ-20261107-001A-P001_junctions_in_the_native_creation_map"
SWA = ROOT / "proofs/SWITCH-READ-20261108-001A/SWITCH-READ-20261108-001A-P001_placements_in_one_switching_class"
sys.path.insert(0, str(TRA))
sys.path.insert(0, str(SWA))
import tr_lib as TR  # noqa: E402
import sw_lib as SW  # noqa: E402
FAMILY = SW.FAM


def atom_report():
    """the edge atom on incidence (i, p): points r0..r6, the root line {r1, r2, p} and the six other Fano lines; line i holds r0"""
    T = FAMILY.FA
    import threefold_lib as TF
    F = [tuple(l) for l in TF.FANO]
    root, others = F[0], F[1:]
    lines = [(("r", root[1]), ("r", root[2]), "p")] + [tuple(("r", q) for q in l) for l in others]
    names = [("r", i) for i in range(7)] + ["p"]
    sols = []
    for vals in itertools.product((0, 1), repeat=8):
        v = dict(zip(names, vals))
        if all(len({v[x] for x in l}) > 1 for l in lines):
            sols.append(v)
    r0, r1, r2 = ("r", root[0]), ("r", root[1]), ("r", root[2])
    inner = [("r", q) for q in range(7) if ("r", q) not in (r0, r1, r2)]
    tied = all(s[r0] == s[r1] == s[r2] == 1 - s["p"] for s in sols)
    both = all({s[q] for s in sols if s["p"] == pv} == {0, 1} for q in inner for pv in (0, 1))
    pairs = all({(s[q], s[w]) for s in sols} == {(0, 0), (0, 1), (1, 0), (1, 1)} for q, w in itertools.combinations(inner, 2))
    per_p = {pv: sum(1 for s in sols if s["p"] == pv) for pv in (0, 1)}
    complement = all({tuple(1 - s[q] for q in inner) for s in sols if s["p"] == 0} == {tuple(s[q] for q in inner) for s in sols if s["p"] == 1}
                     for _ in [0])
    return {"solutions": len(sols), "per value of p": per_p, "r0 = r1 = r2 = not p": tied,
            "each inner point takes both values for each p": both, "each pair of inner points takes all four pairs": pairs,
            "the inner configurations for p = 1 are those for p = 0 complemented": complement}


def atom_contacts(H, glue):
    """in FA.edge_atoms's output (glue lines first, then seven lines per atom on seven fresh points): each atom's points lie only on
    its own seven lines, except one of them (r0), which also lies on exactly one glue line; and each glue line keeps its other points"""
    g, n0 = len(glue), 1 + max(max(l) for l in glue)
    k = (len(H) - g) // 7
    ok = len(H) == g + 7 * k
    for a in range(k):
        own = set(range(g + 7 * a, g + 7 * a + 7))
        pts = set(range(n0 + 7 * a, n0 + 7 * a + 7))
        outside = [(i, q) for i, l in enumerate(H) if i not in own for q in l if q in pts]
        ok &= len(outside) == 1 and outside[0][0] < g
    ok &= all(sum(1 for q in H[i] if q not in glue[i]) <= 1 for i in range(g))
    return ok, k


def signing_of_space(H, glue):
    """the signing a plain space carries: the incidences (i, p) whose point the space's glue line i holds an atom point in place of;
    ok when the glue lines differ from the glue only there"""
    n0 = 1 + max(max(l) for l in glue)
    diffs = [(i, j) for i in range(len(glue)) for j in range(3) if H[i][j] != glue[i][j]]
    return sorted((i, glue[i][j]) for i, j in diffs), all(H[i][j] >= n0 for i, j in diffs)


def switching_witness(glue, S, T):
    """a set U (('L', i) and ('P', p) vertices) with T = S xor delta(U), or None"""
    g = SW.incidence_of_glue(glue)
    E = SW.incidences(S) ^ SW.incidences(T)
    col = {}
    for s0 in g:
        if s0 in col:
            continue
        col[s0] = 0
        stack = [s0]
        while stack:
            u = stack.pop()
            for w in g[u]:
                c = col[u] ^ (frozenset((u, w)) in E)
                if w not in col:
                    col[w] = c
                    stack.append(w)
                elif col[w] != c:
                    return None
    return {v for v, c in col.items() if c}


def signs_of(glue, signing):
    neg = {tuple(x) for x in signing}
    return [tuple(1 if (i, p) in neg else 0 for p in l) for i, l in enumerate(glue)]


def switched(glue, signing, U):
    """the signing S xor delta(U)"""
    neg = {tuple(x) for x in signing}
    for i, l in enumerate(glue):
        for p in l:
            if (("L", i) in U) != (("P", p) in U):
                neg ^= {(i, p)}
    return sorted(neg)


def signed_row(glue, signs, a):
    """{b: None or the 4 far-side verdicts} for removing line a of the signed glue and gluing at each other line b"""
    TL = TR.engine().TL
    n = 1 + max(max(l) for l in glue)
    AN = TL.solutions([tuple(l) for l in glue], signs, n, skip=a)
    out = {}
    for b, l in enumerate(glue):
        if b != a:
            mm = TR.fast_masks(AN, list(l), signs[b], [q for q in range(n) if q not in l])
            out[b] = None if mm is None else TL.verdict_from_masks(*mm)
    return out
