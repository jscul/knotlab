"""Theorem F's check (BLOCK-REACH-20261116-001, the thread's own code, 2026-11-16): the least r such that every window of r consecutive
block steps, along every path of orbit types and at every remaining depth, composes to a rectangular relation (the product of its two
projections). Then L_N(k, s) >= 1 + ceil(s/r) for every s >= 1 and every N >= k + s (proof.md, Theorem F).

A block step from an orbit of type t to its child orbit ci at remaining depth rho = N - (level) - 1 relates an assignment of the orbit to
an assignment of the child orbit when the block's knots hold and every other child's subtree is feasible with rho levels below it
(F_rho); this is the group relation of BRANCH-DEPTH-20261112-001A's splicing lemma, the group being the child orbit with the side
subtrees of the orbit's other children. A window of r steps starting at remaining depth rho uses rho, rho - 1, ..., rho - r + 1, which
must be >= 0; for rho >= r0 + r - 1 every step uses the stable F, so finitely many windows are checked."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from window_tree import WindowTree  # noqa: E402,F401


def compose(R, S):
    by = {}
    for a, b in S:
        by.setdefault(a, set()).add(b)
    return frozenset((a, c) for a, b in R for c in by.get(b, ()))


def rectangular(R):
    A = {a for a, _ in R}
    B = {b for _, b in R}
    return len(R) == len(A) * len(B)


class Steps:
    def __init__(self, tree, rmax=12):
        self.tree = tree
        F = tree.feasible(rmax + 8)
        self.r0 = next(r for r in range(rmax + 7) if F[r] == F[r + 1])
        self.F = F
        self.cache = {}

    def rel(self, t, ci, rho):
        """(child type, relation) of the step from type t to child ci with rho levels below the child."""
        rho = min(rho, self.r0)
        key = (t, ci, rho)
        if key not in self.cache:
            tree = self.tree
            c = tree.children[t][ci][0]
            pairs = tree.step(t, self.F[rho], ci, frozenset((x, x) for x in range(1 << tree.m[t])))
            self.cache[key] = (c, frozenset(pairs))
        return self.cache[key]

    def window_ok(self, r, rho, log=None):
        """Every r-step window starting at remaining depth rho (steps at rho, rho - 1, ..., rho - r + 1) is rectangular. Empty
        compositions (type paths no state realises) pass and are counted in log['empty']."""
        tree = self.tree
        for t0 in range(len(tree.types)):
            frontier = {(t0, frozenset((x, x) for x in range(1 << tree.m[t0])))}
            for i in range(r):
                nxt = set()
                for t, R in frontier:
                    for ci in range(len(tree.children[t])):
                        c, S = self.rel(t, ci, rho - i)
                        nxt.add((c, compose(R, S)))
                frontier = nxt
            for _, R in frontier:
                if not R:
                    if log is not None:
                        log['empty'] = log.get('empty', 0) + 1
                elif not rectangular(R):
                    return False
        return True

    def stable_closure(self, cap=500):
        """At stable depth: the least r whose windows all forget, or None when the sets of r-window compositions repeat first (then
        no length forgets: a rectangular window stays rectangular, or empty, when lengthened)."""
        tree = self.tree
        S = frozenset((c, R) for t in range(len(tree.types)) for ci in range(len(tree.children[t]))
                      for c, R in [self.rel(t, ci, self.r0)])
        seen = set()
        for r in range(1, cap + 1):
            if all((not R) or rectangular(R) for _, R in S):
                return r
            if S in seen:
                return None
            seen.add(S)
            S = frozenset((c2, compose(R, S2)) for c, R in S for ci in range(len(tree.children[c]))
                          for c2, S2 in [self.rel(c, ci, self.r0)])
        raise RuntimeError('no repeat within cap')

    def least_r(self, rmax=12, log=None):
        """Least r whose windows forget at every remaining depth (both tiers), searched up to rmax."""
        for r in range(1, rmax + 1):
            if all(self.window_ok(r, rho, log) for rho in range(r - 1, self.r0 + r)):
                return r
        return None


def least_forget(key, rmax=12):
    """r_stable: least r at stable depth (closure; None = never), which gives the bound for N >= k + s + r0 - 1; r_all: least r at
    every remaining depth, which gives it for every N >= k + s. Steps do not restrict the path child's own assignment by F (its
    subtree belongs to later groups)."""
    try:
        tree = WindowTree(key)
    except ValueError:
        return dict(small_orbits=False)
    st = Steps(tree)
    log = {}
    rs = st.stable_closure()
    ra = st.least_r(rmax, log) if rs is not None else None
    return dict(small_orbits=True, r_stable=rs, r_all=ra, r=ra, r0=st.r0, types=len(tree.types), empty_windows=log.get('empty', 0))
