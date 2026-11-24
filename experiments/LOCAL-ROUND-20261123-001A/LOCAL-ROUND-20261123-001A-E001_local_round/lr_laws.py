"""The serial laws of LR section 3: R0, R1, R2, R3, T(d), R3L and the control.

A run's knots are named by their images under m (LR section 4): while every birth and barring has matched,
the run's structure is, up to renaming of distinctions, the sub-structure of the reference made of the image
set I, with the knots of Bar barred.  So a state is the memo key (I, Bar), and every law below reads only what
that structure holds:

  - the parent relation written by each birth (par, and children = reference children that lie in I);
  - h0 (places less parents; for a start knot, places not shared with another start knot);
  - usable(x) = h0(x) - children of x in I (0 if x is barred); loose = usable + barred;
  - which start knots meet (start_nbr); holder steps cross parent-child meetings and start meetings.

No law reads a reference knot's round of birth or anything about knots outside I.  The comparison (cutoff,
match, outcome) is in lr_search.py.  Readings where the text leaves a choice are numbered in deviations.md.
"""
from __future__ import annotations

from collections import Counter

import lr_core as C


def bits(m):
    out = []
    while m:
        low = m & -m
        out.append(low.bit_length() - 1)
        m ^= low
    return out


class State:
    __slots__ = ('I', 'Bar', 'ids', 'use', 'mem', 'loose', '_wean', 'ref')

    def __init__(self, ref, I, Bar):
        self.ref = ref
        self.I = I
        self.Bar = Bar
        ids = bits(I)
        self.ids = ids
        chi = ref.chi_mask
        h0 = ref.h0
        use = {}
        mem = 0
        loose = 0
        for x in ids:
            l = h0[x] - (chi[x] & I).bit_count()
            loose += l
            if l > 0 and not (Bar >> x) & 1:
                use[x] = l
                mem |= 1 << x
        self.use = use
        self.mem = mem
        self.loose = loose
        self._wean = None

    def nbrs(self, x):
        r = self.ref
        return (r.par_mask[x] | r.chi_mask[x] | r.start_nbr[x]) & self.I

    def children(self, x):
        return self.ref.chi_mask[x] & self.I

    def weaned(self, x):
        """LR 1.3: none of its parents is a member of the present roster."""
        return (self.ref.par_mask[x] & self.mem) == 0

    def weaned_mask(self):
        if self._wean is None:
            pm = self.ref.par_mask
            mem = self.mem
            w = 0
            for x in self.ids:
                if (pm[x] & mem) == 0:
                    w |= 1 << x
            self._wean = w
        return self._wean


class LawBase:
    """Common parts: the cutoff, made births (LR 2.3), the start roster (LR 1.2), flags."""

    name = None
    barrings_possible = False

    def __init__(self, ref):
        self.ref = ref
        self.ration = ref.ration
        self.treatment = ref.treatment
        self.r = ref.r
        self.big = False            # some roster read has a group of three or more
        self.big_where = None
        self.brood_short = False    # some brood's roster at birth has a short member (P12)
        self.brood_short_where = None
        self.barrings_possible = self.treatment == 'CANCEL-RETIRE'
        self._start_plan = {}
        self.plan_memo = {}

    # --- the comparison's cutoff (LR section 4): only births within round r are allowed
    def within(self, B):
        born = self.ref.born
        r = self.r
        return all(born[b] <= r for b in B)

    def within_bar(self, x):
        return self.ref.born[x] <= self.r          # deviations.md item 6

    # --- LR 2.3
    def remaining(self, pl, st):
        out = []
        I = st.I
        bpm = self.ref.by_par_mask
        for G, f in pl.joins.items():
            if (bpm.get(G, 0) & I) == 0:
                out.append((G, f))
        for u, (n, f) in pl.offs.items():
            made = (bpm.get((u,), 0) & I).bit_count()
            if n > made:
                out.append(((u,), f))
        return out

    def note(self, pl, where):
        if pl.big and not self.big:
            self.big = True
            self.big_where = where() if callable(where) else where
        return pl

    # --- LR 1.2: the start roster (it never changes)
    def start_roster(self):
        ref = self.ref
        hold = {u: ref.h0[u] for u in range(ref.n_start) if ref.h0[u] >= 1}
        hm = sum(1 << u for u in hold)
        fam = set()
        for u in range(ref.n_start):
            M = ref.start_nbr[u] & hm
            if M.bit_count() >= 2:
                fam.add(frozenset(bits(M)))
        return hold, fam

    def start_plan(self, recursion=True):
        pl = self._start_plan.get(recursion)
        if pl is None:
            hold, fam = self.start_roster()
            pl = C.read_plan(hold, fam, self.ration, self.treatment, recursion=recursion)
            self._start_plan[recursion] = pl
        return self.note(pl, 'start roster')

    def plan_of(self, hold, fam, recursion=True):
        key = (tuple(sorted(hold.items())), frozenset(fam), recursion)
        pl = self.plan_memo.get(key)
        if pl is None:
            pl = C.read_plan(hold, fam, self.ration, self.treatment, recursion=recursion)
            if len(self.plan_memo) > 400000:
                self.plan_memo.clear()
            self.plan_memo[key] = pl
        return pl

    def barrings(self, st):
        return []


# ============================================================================== brood laws R1, R2, R3

class BroodLaw(LawBase):
    """R1, R2, R3 (LR section 3): statuses by LR 2.1-2.2; a guard on each remaining birth and barring."""

    def __init__(self, ref, guard):
        super().__init__(ref)
        assert guard in ('R1', 'R2', 'R3')
        self.guard = guard
        self.name = guard
        self.bmemo = {}

    def brood_of(self, st, x):
        """LR 1.4: the smallest B containing x such that, for every knot of B and every parent of it, all
        children of that parent are in B.  Returns (B, parents of the brood) as masks."""
        ref = self.ref
        I = st.I
        B = 1 << x
        P = 0
        frontier = B
        while frontier:
            newP = 0
            for y in bits(frontier):
                newP |= ref.par_mask[y]
            newP &= ~P
            P |= newP
            add = 0
            for p in bits(newP):
                add |= ref.chi_mask[p] & I
            frontier = add & ~B
            B |= frontier
        return B, P

    def brood_plan(self, st, B, P):
        """LR 1.4: a brood's roster at birth (members with h0 >= 1, holdings h0; for each parent p of the
        brood, the members that are children of p, when at least two) and its plan (LR 2.1)."""
        pl = self.bmemo.get(B)
        if pl is None:
            ref = self.ref
            hold = {y: ref.h0[y] for y in bits(B) if ref.h0[y] >= 1}
            hm = sum(1 << y for y in hold)
            fam = set()
            for p in bits(P):
                M = ref.chi_mask[p] & st.I & hm
                if M.bit_count() >= 2:
                    fam.add(frozenset(bits(M)))
            pl = C.read_plan(hold, fam, self.ration, self.treatment)
            if len(self.bmemo) > 400000:
                self.bmemo.clear()
            self.bmemo[B] = pl
        if pl.short_top and not self.brood_short:
            self.brood_short = True
            self.brood_short_where = sorted(bits(B))
        return self.note(pl, lambda: 'brood %s' % sorted(bits(B)))

    def guard_ok(self, st, G, P):
        """R1: every knot of G weaned.  R2: and every child of each of their parents.  R3: the brood
        containing G is all-weaned (no parent of the brood is a member)."""
        if self.guard == 'R3':
            return (P & st.mem) == 0
        ref = self.ref
        if self.guard == 'R1':
            return all((ref.par_mask[y] & st.mem) == 0 for y in G)
        W = st.weaned_mask()
        for y in G:
            if not (W >> y) & 1:
                return False
            for p in ref.par[y]:
                ch = ref.chi_mask[p] & st.I
                if ch & ~W:
                    return False
        return True

    def stalled_globally(self):
        return self.treatment == 'STALL' and self.start_plan().stalled

    def readings(self, st):
        """Yield (plan, brood mask or None for the start roster, parents mask) for every roster a member
        reads (LR 2.2)."""
        ref = self.ref
        if st.mem & ref.start_mask:
            yield self.start_plan(), None, 0
        seen = 0
        for x in bits(st.mem & ~ref.start_mask):
            if (seen >> x) & 1:
                continue
            B, P = self.brood_of(st, x)
            seen |= B
            yield self.brood_plan(st, B, P), B, P

    def allowed(self, st):
        if self.stalled_globally():
            return []
        out = []
        mem = st.mem
        for pl, B, P in self.readings(st):
            for G, f in self.remaining(pl, st):
                Gm = 0
                for y in G:
                    Gm |= 1 << y
                if Gm & ~mem:
                    continue
                if not self.within(G):
                    continue
                if B is not None and not self.guard_ok(st, G, P):
                    continue
                out.append((G, f))
        return out

    def barrings(self, st):
        if not self.barrings_possible:
            return []
        out = []
        for pl, B, P in self.readings(st):
            for u, s in pl.status.items():
                if s != 'retires' or not (st.mem >> u) & 1 or not self.within_bar(u):
                    continue
                if B is not None and not self.guard_ok(st, (u,), P):
                    continue
                out.append(u)
        return sorted(set(out))


# ============================================================================== R3L

class R3L(BroodLaw):
    """R3L (LR section 3): read the present roster (ANY) and its parts."""

    def __init__(self, ref):
        super().__init__(ref, 'R3')
        self.name = 'R3L'

    def present(self, st):
        """Present met sets (every knot a common knot, a knot not in its own met set) and parts."""
        mem = st.mem
        fams = set()
        for w in st.ids:
            M = st.nbrs(w) & mem
            if M.bit_count() >= 2:
                fams.add(M)
        par = {u: u for u in bits(mem)}

        def find(u):
            while par[u] != u:
                par[u] = par[par[u]]
                u = par[u]
            return u
        for M in fams:
            b = bits(M)
            a = find(b[0])
            for y in b[1:]:
                y = find(y)
                if y != a:
                    par[y] = a
        parts = {}
        for u in par:
            parts.setdefault(find(u), []).append(u)
        out = []
        for P in parts.values():
            Pm = sum(1 << u for u in P)
            out.append((sorted(P), Pm, [M for M in fams if M & Pm]))
        return out

    def part_reading(self, st):
        """For each part: ('untouched', plan) | ('touched', None) | ('nothing', None)."""
        ref = self.ref
        res = []
        for P, Pm, fams in self.present(st):
            has_child = any(ref.chi_mask[u] & st.I for u in P)
            if not has_child:
                if all((ref.par_mask[u] & st.mem) == 0 for u in P):
                    hold = {u: st.use[u] for u in P}
                    pl = self.note(self.plan_of(hold, [frozenset(bits(M)) for M in fams]), 'untouched part')
                    res.append(('untouched', P, Pm, pl))
                else:
                    res.append(('nothing', P, Pm, None))
            else:
                res.append(('touched', P, Pm, None))
        return res

    def _touched_births(self, st, Pm):
        out = []
        mem = st.mem
        for pl, B, P in self.readings(st):
            for G, f in self.remaining(pl, st):
                Gm = 0
                for y in G:
                    Gm |= 1 << y
                if Gm & ~mem or not (Gm & Pm):
                    continue
                out.append((G, f))
        return out

    def allowed(self, st):
        if self.stalled_globally():
            return []
        out = {}
        for kind, P, Pm, pl in self.part_reading(st):
            if kind == 'untouched':
                for G, f in self.remaining(pl, st):
                    out[G] = f
            elif kind == 'touched':
                for G, f in self._touched_births(st, Pm):
                    out[G] = f
        return [(G, f) for G, f in out.items() if self.within(G)]

    def barrings(self, st):
        if not self.barrings_possible:
            return []
        out = set()
        for kind, P, Pm, pl in self.part_reading(st):
            if kind == 'untouched':
                for u, s in pl.status.items():
                    if s == 'retires':
                        out.add(u)
            elif kind == 'touched':
                for pl2, B, PP in self.readings(st):
                    for u, s in pl2.status.items():
                        if s == 'retires' and (Pm >> u) & 1:
                            out.add(u)
        return sorted(u for u in out if (st.mem >> u) & 1 and self.within_bar(u))


# ============================================================================== T(d)

class TLaw(BroodLaw):
    """T(d) (LR section 3): R3's reading within holder-step distance d of the proposed parent set."""

    def __init__(self, ref, d):
        super().__init__(ref, 'R3')
        self.d = d
        self.name = 'T(%d)' % d
        if self.treatment == 'CANCEL-RETIRE':
            raise NotImplementedError('T(d) is registered under (RATION-3, CANCEL-WAIT) only')

    def ball(self, st, Bm):
        W = Bm
        frontier = Bm
        for _ in range(self.d):
            add = 0
            for x in bits(frontier):
                add |= st.nbrs(x)
            frontier = add & ~W
            if not frontier:
                break
            W |= frontier
        return W

    def reading(self, st, Bm):
        """Returns (plan, guard) for the reading around the parent set Bm, or None for a mixed set."""
        ref = self.ref
        W = self.ball(st, Bm)
        if (Bm & ~ref.start_mask) == 0:
            smem = 0
            for u in bits(W & ref.start_mask):
                if ref.h0[u] >= 1:
                    smem |= 1 << u
            fam = set()
            for s in bits(W & ref.start_mask):
                M = ref.start_nbr[s] & smem
                if M.bit_count() >= 2:
                    fam.add(frozenset(bits(M)))
            hold = {u: ref.h0[u] for u in bits(smem)}
            pl = self.note(self.plan_of(hold, fam), 'start roster within W')
            return pl, True
        if Bm & ref.start_mask:
            return None
        I = st.I
        B = Bm
        P = 0
        frontier = Bm
        while frontier:
            newP = 0
            for y in bits(frontier):
                newP |= ref.par_mask[y] & W
            newP &= ~P
            P |= newP
            add = 0
            for p in bits(newP):
                add |= ref.chi_mask[p] & I & W
            frontier = add & ~B
            B |= frontier
        hold = {y: ref.h0[y] for y in bits(B) if ref.h0[y] >= 1}
        hm = sum(1 << y for y in hold)
        fam = set()
        for p in bits(P):
            M = ref.chi_mask[p] & I & W & hm
            if M.bit_count() >= 2:
                fam.add(frozenset(bits(M)))
        pl = self.plan_of(hold, fam)
        if pl.short_top and not self.brood_short:
            self.brood_short = True
            self.brood_short_where = sorted(bits(B))
        self.note(pl, lambda: 'brood within d %s' % sorted(bits(B)))
        return pl, (P & st.mem) == 0

    def allowed(self, st):
        ref = self.ref
        mem = st.mem
        cands = set()
        for u in bits(mem):
            cands.add((u,))
            rd = self.reading(st, 1 << u)
            if rd is None:
                continue
            pl, _ = rd
            for G, f in self.remaining(pl, st):
                if len(G) > 1 and u in G:
                    cands.add(G)
        out = []
        bpm = ref.by_par_mask
        for G in sorted(cands):
            Gm = 0
            for y in G:
                Gm |= 1 << y
            if Gm & ~mem or not self.within(G):
                continue
            rd = self.reading(st, Gm)
            if rd is None:
                continue
            pl, ok = rd
            if not ok:
                continue
            if len(G) > 1:
                f = pl.joins.get(G)
                if f is None or (bpm.get(G, 0) & st.I):
                    continue
                out.append((G, f))
            else:
                ent = pl.offs.get(G[0])
                if ent is None:
                    continue
                n, f = ent
                if n > (bpm.get(G, 0) & st.I).bit_count():
                    out.append((G, f))
        return out


# ============================================================================== the control

class Control(LawBase):
    """The depth guard with the originals supplied (LR section 3, Control)."""

    name = 'CONTROL'

    def layer_reading(self, st):
        ref = self.ref
        if not st.mem:
            return None
        # depth: holder-step distance to the nearest start knot
        depth = {}
        frontier = ref.start_mask & st.I
        seen = frontier
        layers = [frontier]
        while frontier:
            add = 0
            for x in bits(frontier):
                add |= st.nbrs(x)
            frontier = add & ~seen
            seen |= frontier
            if frontier:
                layers.append(frontier)
        k = None
        for i, L in enumerate(layers):
            if L & st.mem:
                k = i
                break
        if k is None:
            raise AssertionError('a member not reached from the start')
        Lk = layers[k]
        Lk1 = layers[k + 1] if k + 1 < len(layers) else 0
        if k == 0:
            pl = self.start_plan(recursion=False)
        else:
            Lprev = layers[k - 1]
            hold = {}
            for x in bits(Lk):
                h = ref.places[x] - (st.nbrs(x) & Lprev).bit_count()
                if h >= 1:
                    hold[x] = h
            hm = sum(1 << x for x in hold)
            fam = set()
            for w in bits(Lprev):
                M = st.nbrs(w) & hm
                if M.bit_count() >= 2:
                    fam.add(frozenset(bits(M)))
            pl = self.note(self.plan_of(hold, fam, recursion=False), lambda: 'layer %d' % k)
        made = Counter()
        for c in bits(Lk1):
            made[tuple(bits(st.nbrs(c) & Lk))] += 1
        return k, pl, made

    def allowed(self, st):
        rd = self.layer_reading(st)
        if rd is None:
            return []
        k, pl, made = rd
        if pl.stalled:
            return []
        out = []
        mem = st.mem
        for G, f in pl.joins.items():
            if made[G] == 0 and all((mem >> y) & 1 for y in G) and self.within(G):
                out.append((G, f))
        for u, (n, f) in pl.offs.items():
            if n > made[(u,)] and (mem >> u) & 1 and self.within((u,)):
                out.append(((u,), f))
        return out

    def barrings(self, st):
        if not self.barrings_possible:
            return []
        rd = self.layer_reading(st)
        if rd is None:
            return []
        k, pl, made = rd
        return sorted(u for u, s in pl.status.items()
                      if s == 'retires' and (st.mem >> u) & 1 and self.within_bar(u))


# ============================================================================== R0

class R0(LawBase):
    """The record's birth-by-birth law (definitions lines 108-126, ANY) with LR section 3's additions."""

    name = 'R0'

    def present_groups(self, st, extra=None):
        """Groups of the present roster.  extra = parent tuple of a new knot counted as a member before it
        receives anything (PRESENT-ORD's d): it is given the id -1."""
        ref = self.ref
        use = dict(st.use)
        nb_extra = None
        if extra is not None:
            for p in extra:
                use[p] -= 1
                if use[p] == 0:
                    del use[p]
            use[-1] = 0
            nb_extra = set(extra)
        memset = set(use)
        fam = set()
        for w in st.ids:
            M = {y for y in bits(st.nbrs(w)) if y in memset}
            if nb_extra is not None and w in nb_extra:
                M.add(-1)
            if len(M) >= 2:
                fam.add(frozenset(M))
        if nb_extra is not None:
            M = {y for y in nb_extra if y in memset}
            if len(M) >= 2:
                fam.add(frozenset(M))
        groups = C.compute_groups(sorted(memset), fam)
        return groups, use

    def is_open(self, st, G):
        ref = self.ref
        Gm = 0
        for y in G:
            Gm |= 1 << y
        for c in bits(ref.chi_mask[G[0]] & st.I):
            if (ref.par_mask[c] & Gm) == Gm:
                return False
        return True

    def reading(self, st):
        groups, use = self.present_groups(st)
        if any(len(g) >= 3 for g in groups) and not self.big:
            self.big = True
            self.big_where = 'present roster'
        opn = [g for g in groups if self.is_open(st, g)]
        cnt = Counter(u for g in opn for u in g)
        return opn, cnt

    def barrings(self, st):
        if not self.barrings_possible:
            return []
        opn, cnt = self.reading(st)
        return sorted(u for u in st.use if cnt[u] > st.use[u] and self.within_bar(u))

    def allowed(self, st):
        opn, cnt = self.reading(st)
        use = st.use
        moves = []
        if self.ration == 'ORD':                       # PRESENT-ORD with FIRST-COME
            moves.extend(opn)
            moves.extend((u,) for u in sorted(use) if use[u] > cnt[u])
        else:
            short = {u for u in use if cnt[u] > use[u]}
            joins = [g for g in opn if not short.intersection(g)]
            cj = Counter(u for g in joins for u in g)
            moves.extend(joins)
            for u in sorted(use):
                if u in short:
                    if self.treatment == 'CANCEL-OFFSHOOT':
                        moves.append((u,))
                elif use[u] > cj[u]:
                    moves.append((u,))
        out = []
        for G in moves:
            if not self.within(G):
                continue
            p = len(G)
            if self.ration == 'ORD':
                groups, _ = self.present_groups(st, extra=G)
                d = sum(1 for g in groups if -1 in g)
                f = max(d, 3 - p, 1)
            else:
                f = C.fresh_ration(self.ration, p)
            out.append((G, f))
        return out


def make_law(ref, name):
    if name in ('R1', 'R2', 'R3'):
        return BroodLaw(ref, name)
    if name == 'R3L':
        return R3L(ref)
    if name == 'R0':
        return R0(ref)
    if name == 'CONTROL':
        return Control(ref)
    if name.startswith('T('):
        return TLaw(ref, int(name[2:-1]))
    raise ValueError(name)
