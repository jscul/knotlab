"""Theorem M's check (MARK-RATE-20261116-001, the thread's own code, 2026-11-16): can a bond skip one level?

For an orbit type t, a down signature is the set of assignments of the orbit consistent with some assignment of finitely many marked
distinctions in the orbit's subtree (the orbit itself included, with the knots placed at it and below); an up signature is the set of
assignments of the orbit consistent with some assignment of marked distinctions outside its proper subtree (the orbit itself included,
with the knots placed above it but not at it). D(t) and U(t) are the families of all nonempty such sets over every finite marking, at
the stable depth (F constant). A bond meeting level k and level k + s that has no member in group i (the side subtrees of O_(k+i-1)'s
other children, and the step from O_(k+i-1) to O_(k+i)) splits into a left part, whose marks give an up signature X of O_(k+i-1), and a
right part, whose marks give a down signature Y of O_(k+i); some assignment of the bond is forbidden only if X × Y misses the step
relation T. Group i introduces O_(k+i), so the right part's marks lie strictly below it: Y comes from marks in O_(k+i)'s children's
subtrees, with the knots placed at O_(k+i), and no pin on O_(k+i) itself. If every X in U(t) and every such Y meet T at every step t -> c, no group can be skipped, so a bond has a member in each of
groups 1, ..., s - 1, and L_N(k, s) >= s + 1 (proof.md, Theorem M). The families here are supersets of the achievable ones (markings
of any distinctions, with no requirement that the parts be free), which keeps the test sound; a signature is cut to the values a full state can take there (extending through the step), since a part
whose marks no full state realises is itself constrained and cannot belong to a bond."""
import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from window_tree import WindowTree  # noqa: E402


def pins(m):
    """Every partial pin of m coordinates, as (mask, value)."""
    out = []
    for choice in itertools.product((None, 0, 1), repeat=m):
        mask = sum(1 << i for i, c in enumerate(choice) if c is not None)
        val = sum((c << i) for i, c in enumerate(choice) if c is not None)
        out.append((mask, val))
    return out


class Marks:
    def __init__(self, tree, cap=200000):
        self.tree = tree
        F = tree.feasible(20)
        self.r0 = next(r for r in range(19) if F[r] == F[r + 1])
        self.Fc = F[self.r0]
        self.cap = cap
        self.D = self._down()
        self.U = self._up()
        self.Ufree = self._up_free()

    def _down(self):
        tree, Fc = self.tree, self.Fc
        n = len(tree.types)
        D = [{frozenset(x for x in Fc[t] if (x & mask) == val) for mask, val in pins(tree.m[t])} - {frozenset()} for t in range(n)]
        changed = True
        while changed:
            changed = False
            for t in range(n):
                kids = tree.children[t]
                options = [sorted(D[c], key=sorted) for c, _ in kids]
                new = set(D[t])
                # windows grouped by child restriction, once
                rows = [(x, [tree.restrict(y, pos) for _, pos in kids]) for x, y in tree.W[t]]
                for combo in itertools.product(*options):
                    base = frozenset(x for x, zs in rows if all(z in Yc for z, Yc in zip(zs, combo)))
                    if not base:
                        continue
                    for mask, val in pins(tree.m[t]):
                        Y = frozenset(x for x in base if (x & mask) == val)
                        if Y and Y not in new:
                            new.add(Y)
                if len(new) != len(D[t]):
                    D[t] = new
                    changed = True
                if sum(len(d) for d in D) > self.cap:
                    raise RuntimeError('down families too large')
        return D

    def _up(self):
        tree, D = self.tree, self.D
        n = len(tree.types)
        U = [set() for _ in range(n)]
        U[0] = {frozenset(x for x in range(1 << tree.m[0]) if (x & mask) == val) for mask, val in pins(tree.m[0])} - {frozenset()}
        changed = True
        while changed:
            changed = False
            for t in range(n):
                if not U[t]:
                    continue
                kids = tree.children[t]
                rows = [(x, [tree.restrict(y, pos) for _, pos in kids]) for x, y in tree.W[t]]
                for ci, (c, _) in enumerate(kids):
                    others = [sorted(D[c2], key=sorted) if k != ci else [None] for k, (c2, _) in enumerate(kids)]
                    new = set(U[c])
                    for X in list(U[t]):
                        for combo in itertools.product(*others):
                            base = frozenset(zs[ci] for x, zs in rows if x in X and
                                             all(k == ci or z in Yc for k, (z, Yc) in enumerate(zip(zs, combo))))
                            if not base:
                                continue
                            for mask, val in pins(tree.m[c]):
                                Z = frozenset(z for z in base if (z & mask) == val)
                                if Z:
                                    new.add(Z)
                    if len(new) != len(U[c]):
                        U[c] = new
                        changed = True
                if sum(len(u) for u in U) > self.cap:
                    raise RuntimeError('up families too large')
        return U

    def _up_free(self):
        """For each type, the union over contexts of the values its orbit can take given everything outside its proper subtree with no
        marks (a superset of the up-feasible set in any one context)."""
        tree, Fc = self.tree, self.Fc
        n = len(tree.types)
        Uf = [set() for _ in range(n)]
        Uf[0] = set(range(1 << tree.m[0]))
        changed = True
        while changed:
            changed = False
            for t in range(n):
                if not Uf[t]:
                    continue
                kids = tree.children[t]
                for x, y in tree.W[t]:
                    if x not in Uf[t]:
                        continue
                    zs = [tree.restrict(y, pos) for _, pos in kids]
                    for ci, (c, _) in enumerate(kids):
                        if all(k == ci or zs[k] in Fc[c2] for k, (c2, _) in enumerate(kids)) and zs[ci] not in Uf[c]:
                            Uf[c].add(zs[ci])
                            changed = True
        return Uf

    def below(self, c):
        """Down signatures of an orbit of type c from marks strictly below it (its children's subtrees), with no pin on the orbit's
        own coordinates: the right part of a skipped group i starts below O_(k+i), which group i introduces."""
        tree, D = self.tree, self.D
        kids = tree.children[c]
        rows = [(x, [tree.restrict(y, pos) for _, pos in kids]) for x, y in tree.W[c]]
        out = set()
        for combo in itertools.product(*[sorted(D[c2], key=sorted) for c2, _ in kids]):
            Y = frozenset(x for x, zs in rows if all(z in Yc for z, Yc in zip(zs, combo)))
            if Y:
                out.add(Y)
        return out

    def step(self, t, ci):
        tree = self.tree
        c = tree.children[t][ci][0]
        return c, frozenset(tree.step(t, self.Fc, ci, frozenset((x, x) for x in range(1 << tree.m[t]))))

    def no_skip(self):
        """True when no group can be skipped at any step; else a witness (t, ci, X, Y)."""
        tree = self.tree
        for t in range(len(tree.types)):
            for ci in range(len(tree.children[t])):
                c, T = self.step(t, ci)
                below = self.below(c)
                # a full state realising the left part takes a value of O_(k+i-1) that extends through the step to a feasible
                # child; one realising the right part takes a value of O_(k+i) that the step reaches from an up-feasible value: a part none of whose
                # values survives is constrained by itself, so not part of a bond; pairs meeting T are unaffected by the cut
                dom = {x for x, y in T if y in self.Fc[c]}
                ran = {y for x, y in T if x in self.Ufree[t]}
                for X in self.U[t]:
                    Xr = X & dom
                    if not Xr:
                        continue
                    for Y in below:
                        Yr = Y & ran
                        if Yr and not any(x in Xr and y in Yr for x, y in T):
                            return False, (t, ci, sorted(Xr), sorted(Yr))
        return True, None


def check(key):
    try:
        tree = WindowTree(key)
    except ValueError:
        return dict(small_orbits=False)
    mk = Marks(tree)
    ok, witness = mk.no_skip()
    return dict(small_orbits=True, r0=mk.r0, no_skip=ok, witness=witness, D_sizes=[len(d) for d in mk.D],
                U_sizes=[len(u) for u in mk.U])
