"""The serial laws: R1, R2, R3 and T(d) and the control (LR section 3), and the repaired guard R3' (GCH section 4).

A run's knots are named by their images under m (LR section 4): while every birth and barring has matched, the run's
structure is, up to renaming of distinctions, the sub-structure of the reference made of the image set I, with the
knots of Bar barred.  So a state is the memo key (I, Bar), and every law below reads only what that structure holds:
the parent relation written by each birth (par; children = reference children that lie in I); h0 (places less
parents less places barred at birth, GCH section 2; for a start knot, places not shared with another start knot);
usable(x) = h0(x) - children of x in I (0 if x is barred); loose = every loose distinction, usable or barred;
which start knots meet; holder steps cross parent-child meetings and start meetings.

A birth is a triple (parents, f, usable fresh); f and the usable count come from the plan (GCH sections 1-2).
No law reads a round of birth or anything about knots outside I.  The comparison is in lr_search.py.
(The earlier study's R0 and R3L are not part of this study and are not carried over.)
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
        l0 = ref.loose0
        use = {}
        mem = 0
        loose = 0
        for x in ids:
            c = (chi[x] & I).bit_count()
            loose += l0[x] - c
            u = h0[x] - c
            if u > 0 and not (Bar >> x) & 1:
                use[x] = u
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
        """LR 1.3 (unchanged under holding, GCH 3 item 5): none of its parents is a member of the present roster."""
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


def gmask(G):
    m = 0
    for y in G:
        m |= 1 << y
    return m


class LawBase:
    """Common parts: the cutoff, made births (LR 2.3, by parents, f and barred count), the start roster, flags."""

    name = None

    def __init__(self, ref):
        self.ref = ref
        self.ration = ref.ration
        self.treatment = ref.treatment
        self.release = getattr(ref, 'release', 'RELEASE')
        self.fillers = getattr(ref, 'fillers', False)
        self.r = ref.r
        self.big = False            # some roster read has a group of three or more
        self.big_where = None
        self.big_rosters = 0        # number of distinct rosters read with such a group
        self.brood_short = False    # some brood's roster at birth has a short member
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
        return self.ref.born[x] <= self.r

    # --- LR 2.3, by kind: a planned birth (G, f, u) is made by knots with exactly the parents G, fresh count f and
    # f - u places barred at birth, up to its number.
    def made(self, G, f, u, I):
        return (self.ref.by_pfb_mask.get((G, f, f - u), 0) & I).bit_count()

    def remaining3(self, pl, st):
        out = []
        I = st.I
        for (G, f, u), n in pl.births.items():
            if n > self.made(G, f, u, I):
                out.append((G, f, u))
        return out

    def remaining(self, pl, st):
        """The earlier study's view: (parents, f) pairs."""
        seen = {}
        for G, f, u in self.remaining3(pl, st):
            seen.setdefault(G, f)
        return list(seen.items())

    def births_made(self, pl, p, st):
        """Every birth planned for p (with p among its parents), in every reading, is made."""
        I = st.I
        for (G, f, u), n in pl.member_births.get(p, {}).items():
            if self.made(G, f, u, I) < n:
                return False
        return True

    def note(self, pl, where):
        if pl.big and not self.big:
            self.big = True
            self.big_where = where() if callable(where) else where
        return pl

    def _plan(self, hold, fam, recursion=True):
        pl = C.read_plan(hold, fam, self.ration, self.treatment, recursion=recursion, release=self.release,
                         fillers=self.fillers)
        if pl.big:
            self.big_rosters += 1
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
            pl = self._plan(hold, fam, recursion=recursion)
            self._start_plan[recursion] = pl
        return self.note(pl, 'start roster')

    def start_clause_condition(self):
        """LR 2.2 and GCH 1: no start knot that acts meets a start knot that waits (in any reading of the start
        roster).  Returns the list of violating pairs (empty when the condition holds)."""
        pl = self.start_plan()
        acts = {u for u, lv in pl.acting_levels.items() if lv}
        waits = {u for u, lv in pl.waited.items() if lv} | {u for u, s in pl.status.items() if s == 'allshort'}
        bad = []
        for a in sorted(acts):
            for w in sorted(waits):
                if a != w and (self.ref.start_nbr[a] >> w) & 1:
                    bad.append((a, w))
        return bad

    def plan_of(self, hold, fam, recursion=True):
        key = (tuple(sorted(hold.items())), frozenset(fam), recursion)
        pl = self.plan_memo.get(key)
        if pl is None:
            pl = self._plan(hold, fam, recursion=recursion)
            if len(self.plan_memo) > 400000:
                self.plan_memo.clear()
            self.plan_memo[key] = pl
        return pl

    def barrings(self, st):
        return []

    def allowed(self, st):
        """The earlier study's view: (parents, f) pairs."""
        seen = {}
        for G, f, u in self.allowed3(st):
            seen.setdefault(G, f)
        return list(seen.items())

    def explain(self, st, c):
        return {'reason': 'no explanation for this law'}


# ============================================================================== brood laws R1, R2, R3, R3'

class BroodLaw(LawBase):
    """R1, R2, R3 (LR section 3) and R3' (GCH section 4): statuses by LR 2.1-2.2 with GCH's plan; a guard on each
    remaining birth and barring."""

    def __init__(self, ref, guard):
        super().__init__(ref)
        assert guard in ('R1', 'R2', 'R3', "R3'")
        self.guard = guard
        self.name = guard
        self.bmemo = {}

    def brood_of(self, st, x):
        """LR 1.4: the smallest B containing x such that, for every knot of B and every parent of it, all children
        of that parent are in B.  Returns (B, parents of the brood) as masks."""
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
        """LR 1.4: a brood's roster at birth (members with h0 >= 1, holdings h0; for each parent p of the brood,
        the members that are children of p, when at least two) and its plan (LR 2.1 with GCH 1-3)."""
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
            pl = self._plan(hold, fam)
            if len(self.bmemo) > 400000:
                self.bmemo.clear()
            self.bmemo[B] = pl
        if pl.short_top and not self.brood_short:
            self.brood_short = True
            self.brood_short_where = sorted(bits(B))
        return self.note(pl, lambda: 'brood %s' % sorted(bits(B)))

    # ------------------------------------------------------------------ has given (GCH section 4)
    def has_given(self, st, p, memo):
        """A parent has given when it is no member of the present roster; or when every parent of every knot of
        its own brood has given, every birth planned for it in every reading is made, and its part, in the
        readings of that brood, is idle.  A start knot's brood is the start roster."""
        if p in memo:
            return memo[p]
        if not (st.mem >> p) & 1:
            memo[p] = True
            return True
        memo[p] = False
        if p < self.ref.n_start:
            pl = self.start_plan()
            P = 0
        else:
            B, P = self.brood_of(st, p)
            pl = self.brood_plan(st, B, P)
        ok = all(self.has_given(st, q, memo) for q in bits(P))
        if ok:
            ok = self.births_made(pl, p, st)
        if ok:
            ok = pl.status.get(p) in ('idle', 'allshort')
        memo[p] = ok
        return ok

    def why_not_given(self, st, p):
        """The reason a member parent has not given."""
        if not (st.mem >> p) & 1:
            return None
        if p < self.ref.n_start:
            pl = self.start_plan()
            P = 0
        else:
            B, P = self.brood_of(st, p)
            pl = self.brood_plan(st, B, P)
        memo = {}
        notgiven = [q for q in bits(P) if not self.has_given(st, q, memo)]
        if notgiven:
            return {'knot': p, 'why': 'a parent of its brood has not given', 'those_parents': notgiven}
        if not self.births_made(pl, p, st):
            missing = [[list(G), f, u, n - self.made(G, f, u, st.I)] for (G, f, u), n in pl.member_births[p].items()
                       if self.made(G, f, u, st.I) < n]
            return {'knot': p, 'why': 'a birth planned for it is not made', 'missing_births': missing}
        return {'knot': p, 'why': 'its part is not idle in the readings of its brood', 'status': pl.status.get(p)}

    # ------------------------------------------------------------------ the guards
    def guard_ok(self, st, G, P, memo=None):
        """R1: every knot of G weaned.  R2: and every child of each of their parents.  R3: the brood containing G
        is all-weaned (no parent of the brood is a member).  R3': every parent of every knot of the brood has
        given."""
        if self.guard == 'R3':
            return (P & st.mem) == 0
        if self.guard == "R3'":
            if memo is None:
                memo = {}
            return all(self.has_given(st, q, memo) for q in bits(P))
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
        """Yield (plan, brood mask or None for the start roster, parents mask) for every roster a member reads
        (LR 2.2)."""
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

    def allowed3(self, st):
        if self.stalled_globally():
            return []
        out = []
        mem = st.mem
        memo = {}
        for pl, B, P in self.readings(st):
            for G, f, u in self.remaining3(pl, st):
                if gmask(G) & ~mem:
                    continue
                if not self.within(G):
                    continue
                if B is not None and not self.guard_ok(st, G, P, memo):
                    continue
                out.append((G, f, u))
        return out

    def barrings(self, st):
        """A member whose last status is 'retires' is barred when the guard allows it and every birth planned for
        it in an earlier reading is made (deviations.md item 12)."""
        if not self.barrings_possible:
            return []
        out = []
        memo = {}
        for pl, B, P in self.readings(st):
            for u, s in pl.status.items():
                if s != 'retires' or not (st.mem >> u) & 1 or not self.within_bar(u):
                    continue
                if not self.births_made(pl, u, st):
                    continue
                if B is not None and not self.guard_ok(st, (u,), P, memo):
                    continue
                out.append(u)
        return sorted(set(out))

    # ------------------------------------------------------------------ why a reference knot was never made
    def explain(self, st, c):
        ref = self.ref
        G = ref.par[c]
        f = ref.fresh[c]
        u = f - ref.barred0[c]
        out = {'knot': c, 'parents': list(G), 'f': f, 'usable': u, 'round': ref.born[c]}
        dead = [y for y in G if not (st.mem >> y) & 1]
        if dead:
            out['reason'] = 'a parent holds no usable distinction'
            out['parents_not_members'] = dead
            return out
        if all(y < ref.n_start for y in G):
            pl, B, P = self.start_plan(), None, 0
        else:
            B, P = self.brood_of(st, G[0])
            pl = self.brood_plan(st, B, P)
        if (G, f, u) not in self.remaining3(pl, st):
            out['reason'] = 'not a remaining birth of the plan its parents read'
            out['plan_status_of_parents'] = {str(y): pl.status.get(y) for y in G}
            out['planned_for_parents'] = {str(y): [[list(g), ff, uu, n] for (g, ff, uu), n in
                                                   pl.member_births.get(y, {}).items()] for y in G}
            return out
        if B is None:
            out['reason'] = 'allowed (a start birth): not explained'
            return out
        if self.guard == 'R1':
            bad = [{'knot': y, 'member_parents': bits(ref.par_mask[y] & st.mem)} for y in G
                   if ref.par_mask[y] & st.mem]
            out['reason'] = 'R1: a knot of the parent set is not weaned'
            out['not_weaned'] = bad
        elif self.guard == 'R2':
            W = st.weaned_mask()
            bad = []
            for y in G:
                for p in ref.par[y]:
                    for c2 in bits(ref.chi_mask[p] & st.I & ~W):
                        bad.append({'knot': c2, 'member_parents': bits(ref.par_mask[c2] & st.mem)})
            out['reason'] = 'R2: a knot sharing a parent with the parent set is not weaned'
            out['not_weaned'] = bad
        elif self.guard == 'R3':
            out['reason'] = 'R3: a parent of the brood is still a member'
            out['member_parents_of_brood'] = bits(P & st.mem)
        else:
            memo = {}
            bad = [q for q in bits(P) if not self.has_given(st, q, memo)]
            out['reason'] = "R3': a parent of the brood has not given"
            out['not_given'] = [self.why_not_given(st, q) for q in bad]
        return out


# ============================================================================== T(d)

class TLaw(BroodLaw):
    """T(d) (LR section 3): R3's reading within holder-step distance d of the proposed parent set."""

    def __init__(self, ref, d):
        super().__init__(ref, 'R3')
        self.d = d
        self.name = 'T(%d)' % d
        if self.treatment == 'CANCEL-RETIRE':
            raise NotImplementedError('T(d) is registered without retiring')

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

    def allowed3(self, st):
        mem = st.mem
        cands = set()
        for u in bits(mem):
            cands.add((u,))
            rd = self.reading(st, 1 << u)
            if rd is None:
                continue
            pl, _ = rd
            for G, f, uu in self.remaining3(pl, st):
                if len(G) > 1 and u in G:
                    cands.add(G)
        out = []
        for G in sorted(cands):
            Gm = gmask(G)
            if Gm & ~mem or not self.within(G):
                continue
            rd = self.reading(st, Gm)
            if rd is None:
                continue
            pl, ok = rd
            if not ok:
                continue
            for G2, f, uu in self.remaining3(pl, st):
                if G2 == G:
                    out.append((G, f, uu))
        return out

    def barrings(self, st):
        return []


# ============================================================================== the control

class Control(LawBase):
    """The depth guard with the originals supplied (LR section 3, Control), with GCH's plan (one reading)."""

    name = 'CONTROL'

    def layer_reading(self, st):
        ref = self.ref
        if not st.mem:
            return None
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
                # places not shared with a knot of depth k - 1, less places barred at birth (deviations.md item 14)
                h = ref.places[x] - (st.nbrs(x) & Lprev).bit_count() - ref.barred0[x]
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
            made[(tuple(bits(st.nbrs(c) & Lk)), ref.fresh[c], ref.fresh[c] - ref.barred0[c])] += 1
        return k, pl, made, Lk

    def allowed3(self, st):
        rd = self.layer_reading(st)
        if rd is None:
            return []
        k, pl, made, Lk = rd
        if pl.stalled:
            return []
        out = []
        mem = st.mem
        for (G, f, u), n in pl.births.items():
            if n > made[(G, f, u)] and (gmask(G) & ~mem) == 0 and self.within(G):
                out.append((G, f, u))
        return out

    def barrings(self, st):
        if not self.barrings_possible:
            return []
        rd = self.layer_reading(st)
        if rd is None:
            return []
        k, pl, made, Lk = rd
        return sorted(u for u, s in pl.status.items()
                      if s == 'retires' and (st.mem >> u) & 1 and self.within_bar(u))

    def explain(self, st, c):
        ref = self.ref
        G = ref.par[c]
        f = ref.fresh[c]
        u = f - ref.barred0[c]
        out = {'knot': c, 'parents': list(G), 'f': f, 'usable': u, 'round': ref.born[c]}
        dead = [y for y in G if not (st.mem >> y) & 1]
        if dead:
            out['reason'] = 'a parent holds no usable distinction'
            out['parents_not_members'] = dead
            return out
        k, pl, made, Lk = self.layer_reading(st)
        out['layer_depth'] = k
        out['least_depth_members'] = bits(Lk & st.mem)
        if gmask(G) & ~Lk:
            out['reason'] = 'its parents are not in the layer of least depth: a member of depth %d is given nothing ' \
                            'more to do' % k
        else:
            out['reason'] = 'not a remaining birth of the layer plan'
            out['plan_status_of_parents'] = {str(y): pl.status.get(y) for y in G}
        return out


def make_law(ref, name):
    if name in ('R1', 'R2', 'R3', "R3'", 'R3P'):
        return BroodLaw(ref, "R3'" if name == 'R3P' else name)
    if name == 'CONTROL':
        return Control(ref)
    if name.startswith('T('):
        return TLaw(ref, int(name[2:-1]))
    raise ValueError(name)
