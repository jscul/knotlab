"""The decorated test (MODE-BOND-20261117-001, part A, the thread's own code, 2026-11-17).

For a pattern whose four-address orbits have every assignment feasible at every depth (F = all, checked), states of an orbit are
bit masks over its assignments.
- Saturation. Every orbit above the bottom band takes its states in F[r0]; masks are read inside it (for these 13, F = all).
- Decorations. Members fix some addresses of an orbit (a subcube) and, through a child's subtree, restrict the child's state to an
  induced set. Fam[t] is the family of realisable restrictions of a type-t orbit by members in it and its subtree: subcubes
  intersected with the sets induced through the block from the children's families (a fixpoint). The undecorated restriction is all
  states.
- Conditions. For each non-product composite T on the periodic part of the saturated automaton (composite.py), from type t to type t'
  (here the self-similar type to itself), the lower side can impose on the upper orbit x any set T^-1(L) with L in Fam[t'].
- Backward closure (only pairs with M1 nonempty and M1 != M2 are kept: equal masks stay equal on the way up). Pairs[t]: pairs (M1, M2) of masks on a type-t orbit's states, reached from a crossing top x by going up through
  blocks: M1 the states from which some state of x meeting a condition is reachable, M2 those from which some state of x is, under
  one choice of decorations (a subcube at each orbit on the way, a set of Fam on every other child).
- Gadget: a pair at a type found at level 3 with M1 nonempty and M1 != M2. Fixing that level-3 orbit to a state of M2 minus M1, with
  the decorations and the lower members, is impossible, while some state of M1 is possible.
Witnesses are kept, so that a gadget's decorations can be read back."""
import itertools
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
sys.path.insert(0, str(ROOT / 'research/TWO-ENDS-20261117-001'))
from window_tree import WindowTree  # noqa: E402
from composite import automaton, is_product  # noqa: E402


def cubes(m):
    """All subcubes of {0,1}^m as masks over the 2^m assignments (fix each address to 0, 1, or leave it free)."""
    out = set()
    for spec in itertools.product((None, 0, 1), repeat=m):
        mask = 0
        for x in range(1 << m):
            if all(v is None or ((x >> i) & 1) == v for i, v in enumerate(spec)):
                mask |= 1 << x
        out.add(mask)
    return sorted(out)


def bits(mask):
    out, i = [], 0
    while mask:
        if mask & 1:
            out.append(i)
        mask >>= 1
        i += 1
    return out


class Decorated:
    def __init__(self, key, fam_cap=20000):
        self.tree = tree = WindowTree(key)
        F = tree.feasible(20)
        self.r0 = next(r for r in range(19) if F[r] == F[r + 1])
        self.Fc = F[self.r0]
        self.f_all = all(len(F[r][t]) == 1 << tree.m[t] for r in range(12) for t in range(len(tree.types)))
        self.nt = len(tree.types)
        # saturated: every orbit's state lies in F[r0]; the undecorated restriction is F[r0], and cubes are cut to it
        self.full = [sum(1 << x for x in self.Fc[t]) for t in range(self.nt)]
        self.cubes = [sorted({c & self.full[t] for c in cubes(tree.m[t])} - {0}) for t in range(self.nt)]
        # XM[t][a-tuple] = mask of parent states allowed with children states a
        self.XM = []
        for t in range(self.nt):
            d = {}
            for x, y in tree.W[t]:
                a = tuple(tree.restrict(y, pos) for c, pos in tree.children[t])
                d[a] = d.get(a, 0) | (1 << x)
            self.XM.append(d)
        self.fam_cap = fam_cap
        self.fam = self._families()

    def induced(self, t, restr):
        """Mask of type-t states allowed when child j is restricted to restr[j] (masks)."""
        out = 0
        sets = [bits(r) for r in restr]
        for a in itertools.product(*sets):
            out |= self.XM[t].get(a, 0)
        return out

    def _table(self, t):
        """For a type with two children: T[a1, a2] = mask of parent states allowed with children states a1, a2 (uint32)."""
        tree = self.tree
        n1, n2 = (1 << tree.m[c] for c, _ in tree.children[t])
        T = np.zeros((n1, n2), dtype=np.int64)
        for a, m in self.XM[t].items():
            T[a[0], a[1]] = m
        return T

    @staticmethod
    def _bitmat(masks, n):
        return ((np.array(masks, dtype=np.int64)[:, None] >> np.arange(n)) & 1).astype(bool)

    def induced_many(self, t, fam1, fam2):
        """All induced masks for children restricted to S1 in fam1 and S2 in fam2 (a type with two children), as a set."""
        T = self._table(t)
        n1, n2 = T.shape
        B2 = self._bitmat(fam2, n2)                      # (k2, n2)
        # G[k2, a1] = OR over a2 in S2 of T[a1, a2]
        G = np.zeros((len(fam2), n1), dtype=np.int64)
        for a2 in range(n2):
            G |= np.where(B2[:, a2][:, None], T[:, a2][None, :], 0)
        B1 = self._bitmat(fam1, n1)                      # (k1, n1)
        out = set()
        step = max(1, 2_000_000 // max(1, len(fam2)))
        for i in range(0, len(fam1), step):
            R = np.zeros((min(step, len(fam1) - i), len(fam2)), dtype=np.int64)
            for a1 in range(n1):
                R |= np.where(B1[i:i + step, a1][:, None], G[:, a1][None, :], 0)
            out.update(int(x) for x in np.unique(R))
        return out

    def _families(self):
        tree = self.tree
        fam = [{self.full[t]} for t in range(self.nt)]
        changed = True
        while changed:
            changed = False
            famp = [sorted({c & S for c in self.cubes[t] for S in fam[t]} - {0}) for t in range(self.nt)]
            for t in range(self.nt):
                kids = [c for c, _ in tree.children[t]]
                if len(kids) == 2:
                    new = self.induced_many(t, famp[kids[0]], famp[kids[1]])
                else:
                    new = {self.induced(t, combo) for combo in itertools.product(*[famp[c] for c in kids])}
                new = {m & self.full[t] for m in new} - {0}
                if not new <= fam[t]:
                    fam[t] |= new
                    changed = True
                    if len(fam[t]) > self.fam_cap:
                        raise RuntimeError('family of type %d over %d' % (t, self.fam_cap))
        self.famp = [sorted({c & S for c in self.cubes[t] for S in fam[t]} - {0}) for t in range(self.nt)]
        return [sorted(f) for f in fam]

    def pre_many(self, t, j, M, fam_other):
        """For a type with two children, M on child j: the masks Pre(M, S) for every S in fam_other (array aligned with it)."""
        T = self._table(t)
        if j == 1:
            T = T.T
        n_j, n_o = T.shape
        H = np.zeros(n_o, dtype=np.int64)                # H[a_o] = OR over a_j in M of T[a_j, a_o]
        for a in bits(M):
            H |= T[a, :]
        B = self._bitmat(fam_other, n_o)
        R = np.zeros(len(fam_other), dtype=np.int64)
        for a_o in range(n_o):
            R |= np.where(B[:, a_o], H[a_o], 0)
        return R

    def pre(self, t, j, M, restr_other):
        """Type-t states from which child j can be in M, the other children in their restrictions."""
        restr = list(restr_other)
        restr.insert(j, M)
        return self.induced(t, restr)

    def periodic_nonproducts(self, lmax=400):
        """Every composite on the periodic part of the saturated automaton that is not a product: (start type, end type, T).
        The same construction as composite.automaton, keeping the whole list."""
        tree, Fc = self.tree, self.Fc
        steps = {}
        for t in range(self.nt):
            for ci in range(len(tree.children[t])):
                steps[(t, ci)] = tree.step(t, Fc, ci, frozenset((x, x) for x in Fc[t]))

        def compose(T, t, ci):
            by = {}
            for x, z in steps[(t, ci)]:
                by.setdefault(x, set()).add(z)
            c = tree.children[t][ci][0]
            return frozenset((a, z) for a, x in T for z in by.get(x, ()) if z in Fc[c])

        level = frozenset((t, t, frozenset((x, x) for x in Fc[t])) for t in range(self.nt))
        seen, seq = {}, []
        for l in range(lmax + 1):
            if level in seen:
                start = seen[level]
                break
            seen[level] = l
            seq.append(level)
            level = frozenset((t0, tree.children[t][ci][0], compose(T, t, ci)) for t0, t, T in level
                              for ci in range(len(tree.children[t])))
        cyc = set().union(*seq[start:])
        return sorted((t0, t1, T) for t0, t1, T in cyc if not is_product(T)), start, len(seq) - start

    def conditions(self):
        """{start type: sorted list of condition masks}: T^-1(L) over L in Fam'[end type], for each periodic non-product T,
        leaving out the empty set and the whole set (which constrain nothing)."""
        nonprod, _, _ = self.periodic_nonproducts()
        out = {}
        for t0, t1, T in nonprod:
            by = {}
            for a, z in T:
                by.setdefault(z, 0)
                by[z] |= 1 << a
            for L in self.famp[t1]:
                C = 0
                for z in bits(L):
                    C |= by.get(z, 0)
                if C and C != self.full[t0]:
                    out.setdefault(t0, set()).add(C)
        return {t: sorted(v) for t, v in out.items()}

    def closure(self, start_type, conds, max_pairs=500000, stop_types=None):
        """Backward closure from crossing tops of start_type with the given conditions (masks on start_type's states).
        Returns Pairs as dict type -> dict (M1, M2) -> witness."""
        tree = self.tree
        parents = {}
        for t in range(self.nt):
            for j, (c, pos) in enumerate(tree.children[t]):
                parents.setdefault(c, []).append((t, j))
        pairs = {t: {} for t in range(self.nt)}
        work = []
        for C in conds:
            for cube in self.cubes[start_type]:
                M1, M2 = C & cube, cube
                if M1 and M1 != M2 and (M1, M2) not in pairs[start_type]:
                    pairs[start_type][(M1, M2)] = ('base', C, cube)
                    work.append((start_type, M1, M2))
        while work:
            c, M1, M2 = work.pop()
            for t, j in parents.get(c, []):
                others = [k for k in range(len(tree.children[t])) if k != j]
                if len(others) == 1:
                    fo = self.famp[tree.children[t][others[0]][0]]
                    R1, R2 = self.pre_many(t, j, M1, fo), self.pre_many(t, j, M2, fo)
                    cand = {(int(a), int(b), k) for k, (a, b) in enumerate(zip(R1, R2)) if a and a != b}
                    seen_pp, todo = set(), []
                    for a, b, k in cand:
                        if (a, b) not in seen_pp:
                            seen_pp.add((a, b))
                            todo.append((a, b, (fo[k],)))
                else:
                    todo = []
                    for restr in itertools.product(*[self.famp[tree.children[t][k][0]] for k in others]):
                        a = self.pre(t, j, M1, restr)
                        b = self.pre(t, j, M2, restr) if a else 0
                        if a and a != b:
                            todo.append((a, b, restr))
                for P1, P2, restr in todo:
                    for cube in self.cubes[t]:
                        N1, N2 = P1 & cube, P2 & cube
                        if N1 and N1 != N2 and (N1, N2) not in pairs[t]:
                            pairs[t][(N1, N2)] = ('up', c, M1, M2, j, restr, cube)
                            work.append((t, N1, N2))
                            if stop_types is not None and t in stop_types:
                                return pairs  # a gadget at a target type: enough for an existence check
                            if sum(len(p) for p in pairs.values()) > max_pairs:
                                raise RuntimeError('closure over %d pairs' % max_pairs)
        return pairs


def level_types(tree, k):
    ts = {0}
    for _ in range(k):
        ts = {c for t in ts for c, _ in tree.children[t]}
    return sorted(ts)


def gadgets(D, k=3, max_pairs=500000, first_only=False):
    """All gadgets: for every start type with conditions, the closure, then the pairs at types found at level k with
    0 != M1 != M2. Returns (list of (start type, level-k type, M1, M2, witness), closure sizes)."""
    out, sizes = [], {}
    tk = level_types(D.tree, k)
    for t0, conds in D.conditions().items():
        pairs = D.closure(t0, conds, max_pairs=max_pairs, stop_types=set(tk) if first_only else None)
        sizes[t0] = {t: len(p) for t, p in pairs.items() if p}
        for t in tk:
            for (M1, M2), w in pairs[t].items():
                if M1 and M1 != M2:
                    out.append((t0, t, M1, M2, w))
    return out, sizes, pairs if out else None
