"""Referee R1 (MARK-RATE-20261116-001): my own signature families and Theorem M test, written from proof.md (Lemma S, Theorem M),
on my own block DP (research/DIRECT-REACH-20261115-001/referee-R1/referee_blocks.py). No study code.

Representation: an assignment of an m-address orbit is an int < 2^m (bit i = element i); a SET of assignments is an int bitmask over
the 2^m assignments; a family is a Python set of such bitmasks (nonempty sets only).
  D(t)     down signatures: marks in the orbit's subtree, the orbit itself included (pins), knots placed at the orbit and below.
  below(t) marks strictly below the orbit (no pin on it), knots placed at the orbit and below: one down signature per child, joined
           through the block.
  U(t)     up signatures: marks outside the orbit's proper subtree (pins on the orbit allowed), knots not placed at the orbit or below;
           the union over every context (parent type, child index) in which the type occurs, and the root.
  Ufree(t) the union over contexts of the values the orbit takes with no marks, given everything outside its proper subtree.
Stable depth only (r0 = 0 is required by Theorem M)."""
import itertools

from referee_blocks import Blocks


def pin_masks(m):
    """Every partial pin of m coordinates as a bitmask over the 2^m assignments."""
    out = []
    for choice in itertools.product((None, 0, 1), repeat=m):
        bm = 0
        for x in range(1 << m):
            if all(c is None or ((x >> i) & 1) == c for i, c in enumerate(choice)):
                bm |= 1 << x
        out.append(bm)
    return out


def to_set(bm):
    return frozenset(i for i in range(bm.bit_length()) if (bm >> i) & 1)


class MyMarks:
    def __init__(self, key, cap=300000):
        self.B = B = Blocks(key)
        self.r0, F = B.r0()
        self.Fc = F[self.r0]
        self.cap = cap
        n = len(B.types)
        self.n = n
        self.pins = {m: pin_masks(m) for m in set(B.m)}
        self.fc = [sum(1 << x for x in self.Fc[t]) for t in range(n)]
        # rows: per type, the distinct (x, child projections) of the block's solutions
        self.rows = []
        for t in range(n):
            rs = set()
            for x, y in B.sols[t]:
                rs.add((x, tuple(B.proj(y, pos) for _, pos in B.kids[t])))
            self.rows.append(sorted(rs))
        self.D = self._down()
        self.U = self._up()
        self.Ufree = self._ufree()

    def _join(self, t, combo, X=None, ci=None):
        """X None: the set of orbit values x with some solution whose every child projection lies in combo (bitmasks).
        Else: the set of child-ci values from solutions with x in X (bitmask) and every other child in combo."""
        out = 0
        for x, zs in self.rows[t]:
            if X is not None and not (X >> x) & 1:
                continue
            ok = True
            for k, z in enumerate(zs):
                if k == ci:
                    continue
                if not (combo[k] >> z) & 1:
                    ok = False
                    break
            if ok:
                out |= 1 << (x if ci is None else zs[ci])
        return out

    def _down(self):
        B = self.B
        D = [set(self.fc[t] & p for p in self.pins[B.m[t]]) - {0} for t in range(self.n)]
        changed = True
        while changed:
            changed = False
            for t in range(self.n):
                fams = [sorted(D[c]) for c, _ in B.kids[t]]
                add = set()
                for combo in itertools.product(*fams):
                    base = self._join(t, combo)
                    if base:
                        for p in self.pins[B.m[t]]:
                            v = base & p
                            if v and v not in D[t]:
                                add.add(v)
                if add:
                    D[t] |= add
                    changed = True
                if sum(len(d) for d in D) > self.cap:
                    raise RuntimeError('down families too large')
        return D

    def below(self, t):
        B = self.B
        out = set()
        for combo in itertools.product(*[sorted(self.D[c]) for c, _ in B.kids[t]]):
            v = self._join(t, combo)
            if v:
                out.add(v)
        return out

    def _up(self):
        B = self.B
        U = [set() for _ in range(self.n)]
        U[0] = set(((1 << (1 << B.m[0])) - 1) & p for p in self.pins[B.m[0]]) - {0}
        changed = True
        while changed:
            changed = False
            for t in range(self.n):
                if not U[t]:
                    continue
                kids = B.kids[t]
                for ci, (c, _) in enumerate(kids):
                    fams = [sorted(self.D[c2]) if k != ci else [None] for k, (c2, _) in enumerate(kids)]
                    add = set()
                    for X in sorted(U[t]):
                        for combo in itertools.product(*fams):
                            base = self._join(t, combo, X=X, ci=ci)
                            if base:
                                for p in self.pins[B.m[c]]:
                                    v = base & p
                                    if v and v not in U[c]:
                                        add.add(v)
                    if add:
                        U[c] |= add
                        changed = True
                if sum(len(u) for u in U) > self.cap:
                    raise RuntimeError('up families too large')
        return U

    def _ufree(self):
        B = self.B
        Uf = [0] * self.n
        Uf[0] = (1 << (1 << B.m[0])) - 1
        changed = True
        while changed:
            changed = False
            for t in range(self.n):
                if not Uf[t]:
                    continue
                kids = B.kids[t]
                combo = [self.fc[c] for c, _ in kids]
                for ci, (c, _) in enumerate(kids):
                    v = self._join(t, combo, X=Uf[t], ci=ci)
                    if v & ~Uf[c]:
                        Uf[c] |= v
                        changed = True
        return Uf

    def step(self, t, ci):
        """The block step at stable depth as a set of (x, z)."""
        B = self.B
        return B.kids[t][ci][0], B.down(t, ci, self.Fc, frozenset((x, x) for x in range(1 << B.m[t])))

    def no_skip(self):
        B = self.B
        for t in range(self.n):
            for ci in range(len(B.kids[t])):
                c, T = self.step(t, ci)
                dom = 0
                ran = 0
                for x, z in T:
                    if (self.fc[c] >> z) & 1:
                        dom |= 1 << x
                    if (self.Ufree[t] >> x) & 1:
                        ran |= 1 << z
                bel = self.below(c)
                for X in self.U[t]:
                    Xr = X & dom
                    if not Xr:
                        continue
                    for Y in bel:
                        Yr = Y & ran
                        if Yr and not any((Xr >> x) & 1 and (Yr >> z) & 1 for x, z in T):
                            return False, (t, ci, sorted(to_set(Xr)), sorted(to_set(Yr)))
        return True, None
