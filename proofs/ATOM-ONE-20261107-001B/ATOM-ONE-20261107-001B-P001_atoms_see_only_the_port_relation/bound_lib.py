"""Atoms see only the port relation, for ATOM-ONE-20261107-001B.

The setting is GLUE-READ A's: a closed Fano atom B (its other elements present; by ticket A every Fano atom of a knot space is this, up to
gauge) meets a removal's side at one cut, whose port relation is R. Creation at a line b of B is an OR over local configurations of b's
points with one or two further points (PENDANT-LINE A), each given as a mask.

Three families of further points:
- B's own points and ports (the closed atom alone: B's own verdict);
- deep points of the removal's side, with any relation compatible with R (GLUE-READ A's bound);
- deep points behind B's other elements: behind a line, any relation compatible with not-all-equal on its points (the exact relation its
  closed side shows, ticket A); behind a point, a copy of it or a free point.
A mixed pair joins a deep point of the removal's side with a deep point behind another element.
"""
import importlib.util
import itertools
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


PL = load("ao_b_port_lib", ROOT / "proofs/GLUE-READ-20261106-001A/GLUE-READ-20261106-001A-P001_creation_is_decided_by_the_receiving_cut/"
          "port_lib.py")
AL = load("ao_b_atom_lib", ROOT / "proofs/ATOM-ONE-20261107-001A/ATOM-ONE-20261107-001A-P001_an_atom_with_a_line_removed_is_transparent/"
          "atom_lib.py")
TL = PL.TL
SINGLES, PAIRS = PL.deep_relations()
NAE = 126
PYI = TL.PYI


def single_arrays(rels):
    out = np.zeros((len(rels), 8, 2), dtype=bool)
    for i, r in enumerate(rels):
        for zc in range(8):
            for v in (0, 1):
                out[i, zc, v] = (r >> (zc + 8 * v)) & 1
    return out


def pair_arrays(rels):
    out = np.zeros((len(rels), 8, 2, 2), dtype=bool)
    for i, r in enumerate(rels):
        for b in range(32):
            if (r >> b) & 1:
                out[i, b & 7, (b >> 3) & 1, (b >> 4) & 1] = True
    return out


LINE_S = single_arrays(sorted(SINGLES[NAE]))
LINE_P = pair_arrays(sorted(PAIRS[NAE]))
PT_S = np.zeros((2, 8, 2), dtype=bool)          # behind a point z (code 0/1 = its bit): a copy, or free
PT_S[0, 0, 0] = PT_S[0, 1, 1] = True
PT_S[1, 0, :] = PT_S[1, 1, :] = True
PT_P = []
for _T in range(1, 16):
    _a = np.zeros((8, 2, 2), dtype=bool)
    for _j, (_v, _w) in enumerate(itertools.product((0, 1), repeat=2)):
        if (_T >> _j) & 1:
            _a[0, _v, _w] = True
            _a[1, 1 - _v, 1 - _w] = True
    PT_P.append(_a)
PT_P = np.array(PT_P)
W1 = np.array([[1 << (y * 2 + v) for v in (0, 1)] for y in range(6)], dtype=np.int64)
W2 = np.array([[[1 << (y * 4 + v + 2 * w) for w in (0, 1)] for v in (0, 1)] for y in range(6)], dtype=np.int64)


def masks1(M):
    return set((M * W1).reshape(-1, 12).sum(axis=1).tolist())


def masks2(M):
    return set((M * W2).reshape(-1, 24).sum(axis=1).tolist())


def letters():
    return [(kind, perm, x, b) for kind in ("line", "point") for (perm, x, b) in TL.final_letters(kind)]


def case(kind, perm, x, b, R, behind_alone=False):
    """B's own verdict v0, GLUE-READ A's bound v1 (every deep relation of the removal's side), the bound with every mixed pair added v2;
    with behind_alone, also v3: B's own masks with every deep point behind B's other elements (singly, in pairs, with B's points), and
    no deep point of the removal's side. None when b shows fewer than six patterns."""
    fr = TL.frag_step(kind, perm, x, None)
    sols, idx = TL.solve(fr)
    slots = fr["slots"]
    Y = list(fr["lines"][b])
    rows = [m for m in sols if (R >> TL._bits3(m, idx, slots)) & 1]
    yp = {TL._bits3(m, idx, Y) for m in rows}
    if len(yp) != 6 or 0 in yp or 7 in yp:
        return None
    v0 = TL.final_verdict((kind, R, frozenset(), frozenset()), perm, x, b, deep=False)
    m1, m2 = TL.final_relations((kind, R, frozenset(SINGLES[R]), frozenset(PAIRS[R])), perm, x, b)
    v1 = TL.verdict_from_masks(m1, m2)
    elems = [("line", tuple(fr["lines"][i])) for i in fr["lines"] if i != b] + [("point", (v,)) for v in fr["vars"] if v[0] == "n"]
    yi = np.array([PYI[TL._bits3(m, idx, Y)] for m in rows])
    sc = np.array([TL._bits3(m, idx, slots) for m in rows])
    ec = [np.array([sum(TL._val(m, idx, v) << j for j, v in enumerate(ev)) for m in rows]) for ek, ev in elems]
    S_of = [LINE_S if ek == "line" else PT_S for ek, ev in elems]
    far_s = single_arrays(sorted(SINGLES[R]))

    def table(c1, n1_, c2, n2_):
        T = np.zeros((6, n1_, n2_), dtype=bool)
        T[yi, c1, c2] = True
        return T

    mixed = set()
    for e in range(len(elems)):
        T = table(ec[e], 8, sc, 8)
        mixed |= masks2(np.einsum("yab,iav,jbw->ijyvw", T, S_of[e], far_s) > 0)
    v2 = TL.verdict_from_masks(m1, set(m2) | mixed)
    if not behind_alone:
        return v0, v1, v2
    n1, n2 = TL.final_relations((kind, R, frozenset(), frozenset()), perm, x, b, deep=False)
    n1, n2 = set(n1), set(n2)
    P_of = [LINE_P if ek == "line" else PT_P for ek, ev in elems]
    vv = [np.array([TL._val(m, idx, v) for m in rows]) for v in fr["vars"] if v not in Y]
    for e in range(len(elems)):
        Te = np.zeros((6, 8), dtype=bool)
        Te[yi, ec[e]] = True
        n1 |= masks1(np.einsum("ya,iav->iyv", Te, S_of[e]) > 0)
        n2 |= masks2(np.einsum("ya,iavw->iyvw", Te, P_of[e]) > 0)
        for vals in vv:
            n2 |= masks2(np.einsum("yab,iav->iyvb", table(ec[e], 8, vals, 2), S_of[e]) > 0)
        for f in range(e + 1, len(elems)):
            n2 |= masks2(np.einsum("yab,iav,jbw->ijyvw", table(ec[e], 8, ec[f], 8), S_of[e], S_of[f]) > 0)
    v3 = TL.verdict_from_masks(n1, n2)
    return v0, v1, v2, v3


def passes_free():
    """a free relation at one cut of a closed Fano atom: for every opened element D (a removed line, or a point split into free copies) and
    every other element X0, the patterns on X0's channels against all patterns"""
    return AL.freeness("L") + AL.freeness("P")
