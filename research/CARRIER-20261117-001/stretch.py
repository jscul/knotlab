"""Theorem S's check (CARRIER-20261117-001, the thread's own code, 2026-11-17): can a bond skip r consecutive groups?

Groups as in Theorem F: group j holds O_(k+j), the side subtrees of O_(k+j-1)'s other children, and the knots placed at O_(k+j-1). If
groups i, ..., i + r - 1 hold no member of a bond B meeting level k and level k + s, B splits into a left part (marks outside the proper
subtree of O_(k+i-1), O_(k+i-1) itself allowed) and a right part (marks strictly below O_(k+i+r-1)). An assignment of B is forbidden
only if the up signature X of O_(k+i-1) left by the left marks and the below signature Y of O_(k+i+r-1) left by the right marks miss
the composed relation W of the r steps (side subtrees unmarked). MARK-RATE's families give every X (U) and every Y (below); if every
cut pair meets every r-window W, no r consecutive groups can be skipped, so L_N(k, s) >= 1 + ceil(s/r) (proof.md, Theorem S). With
r = 1 this is MARK-RATE's Theorem M; a rectangular W always passes, so it also covers Theorem F. Stable depth, r0 = 0."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/MARK-RATE-20261116-001'))
sys.path.insert(0, str(ROOT / 'research/BLOCK-REACH-20261116-001'))
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from marks import Marks  # noqa: E402
from forget import compose  # noqa: E402
from window_tree import WindowTree  # noqa: E402


def windows(mk, r):
    """Every (start type, end type, composed relation) over paths of r block steps at stable depth."""
    tree = mk.tree
    out = set()
    for t0 in range(len(tree.types)):
        if not mk.U[t0]:
            continue
        fr = {(t0, frozenset((x, x) for x in range(1 << tree.m[t0])))}
        for _ in range(r):
            nxt = set()
            for t, R in fr:
                for ci in range(len(tree.children[t])):
                    c, S = mk.step(t, ci)
                    nxt.add((c, compose(R, S)))
            fr = nxt
        for c, R in fr:
            out.add((t0, c, R))
    return out


def passes(mk, r, below_cache):
    for t0, c, W in windows(mk, r):
        dom = {x for x, y in W if y in mk.Fc[c]}
        ran = {y for x, y in W if x in mk.Ufree[t0]}
        if c not in below_cache:
            below_cache[c] = mk.below(c)
        for X in mk.U[t0]:
            Xr = X & dom
            if not Xr:
                continue
            for Y in below_cache[c]:
                Yr = Y & ran
                if Yr and not any(x in Xr and y in Yr for x, y in W):
                    return False
    return True


def least_stretch(key, rmax=8):
    tree = WindowTree(key)
    mk = Marks(tree)
    if mk.r0 != 0:
        return dict(r0=mk.r0, r=None, note='r0 > 0: not handled')
    cache = {}
    for r in range(1, rmax + 1):
        if passes(mk, r, cache):
            return dict(r0=0, r=r)
    return dict(r0=0, r=None)
