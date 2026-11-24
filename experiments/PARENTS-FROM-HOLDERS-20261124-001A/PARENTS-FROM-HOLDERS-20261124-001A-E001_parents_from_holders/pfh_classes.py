"""Classes of looks for one law, exact both ways (runs 2 and 3; deviations.md, items 15-23).

For one law, every structure of P1 and P2 is built; every chosen place of every structure is an item.  For each kind of
look (full, then c1, then c2) and each distance (6 down to 1) the items are put into classes:

  * told apart only by a quantity computed on the look (the unfolding of item 21; the colour refinement and the
    exhaustive search of items 15-16);
  * put together only by checked renamings (item 17): identical labelled looks; automorphisms and isomorphisms of
    whole structures, checked place by place; renamings found by the search between two looks, checked place by place;
    and the classes of the look at distance d + 1 and of the finer look, which carry over.

    from pfh_classes import LawRun
    lr = LawRun('F1R'); lr.build(); lr.compute()
"""
from __future__ import annotations

import time
from array import array
from collections import Counter, defaultdict

import pfh_auto as AU
import pfh_common as PC
import pfh_iso as ISO
import pfh_look as LK
import pfh_pop as PP
import pfh_views as VW
from pfh_struct import Struct, bits

E = PC.E
DMAX = 6
VARIANTS = ('full', 'c1', 'c2')
KCODE = {'P': 0, 'C': 1, 'S': 2}


class UF:
    __slots__ = ('p',)

    def __init__(self, n):
        self.p = array('i', range(n))

    def find(self, i):
        p = self.p
        r = i
        while p[r] != r:
            r = p[r]
        while p[i] != r:
            p[i], i = r, p[i]
        return r

    def union(self, i, j):
        a = self.find(i)
        b = self.find(j)
        if a == b:
            return False
        if a < b:
            self.p[b] = a
        else:
            self.p[a] = b
        return True


class SRec:
    """A structure of the law: P2 round, or serial state."""
    __slots__ = ('sid', 'pair', 'kind', 'round', 'run', 'state', 'T', 'offset', 'in_p1', 'in_p2', 'unfold',
                 'unr', 'guard', 'label', 'serial_key_info')


class LawRun:
    def __init__(self, short, log=print):
        self.short = short
        self.fam = PC.SHORT_LAW[short]
        self.log = log
        self.timings = {}
        self.in_look_checked = Counter()
        self.in_look_sampled = Counter()

    # ================================================================================ building
    def build(self):
        t0 = time.time()
        pairs = [p for p in PC.gate_pairs() if p[1] == self.fam]
        self.pairs = [p[0] for p in pairs]
        self.rounds_checked = {p[0]: p[2] for p in pairs}
        self.structs = []
        self.lineages = {}       # start -> list of sids of P2 rounds
        self.p2_events = {}
        self.serial = {}         # start -> list of (SerialRun, [sids])
        serial_cfg = defaultdict(list)
        for cid, start, fam, r in PP.serial_configs():
            if fam == self.fam:
                serial_cfg[start].append((cid, r))
        self.replay = []
        self.prefix_checks = []
        for start in self.pairs:
            S0, rounds, events = PP.p2_lineage(start, self.fam, self.rounds_checked[start])
            self.p2_events[start] = events
            sids = []
            for t, S in enumerate(rounds, 1):
                rec = SRec()
                rec.sid = len(self.structs)
                rec.pair = start
                rec.kind = 'P2'
                rec.round = t
                rec.run = None
                rec.state = None
                rec.T = Struct.from_engine(S, label='%s %s round %d' % (start, self.short, t))
                rec.in_p2 = True
                rec.in_p1 = t <= self.rounds_checked[start]
                rec.label = rec.T.label
                self.structs.append(rec)
                sids.append(rec.sid)
            self.lineages[start] = sids
            Ref = rounds[-1]
            runs = []
            for cid, r in serial_cfg.get(start, []):
                SR = PP.SerialRun(cid, start, self.fam, r)
                self.replay.append({'run': cid, 'seeds': SR.replay})
                # the serial reference is a prefix of the P2 lineage (same engine, start and law)
                RS = SR.ref.S
                ok = RS.n_knots <= Ref.n_knots and all(
                    list(RS.places[x]) == list(Ref.places[x]) and tuple(RS.parents[x]) == tuple(Ref.parents[x])
                    for x in range(RS.n_knots))
                self.prefix_checks.append({'run': cid, 'reference_knots': RS.n_knots, 'prefix_of_P2': ok})
                if not ok:
                    raise RuntimeError('%s: the serial reference is not a prefix of the P2 lineage' % cid)
                ss = []
                for i in range(len(SR.states)):
                    rec = SRec()
                    rec.sid = len(self.structs)
                    rec.pair = start
                    rec.kind = 'serial'
                    rec.round = None
                    rec.run = cid
                    rec.state = i
                    rec.T = SR.struct(i)
                    rec.in_p1 = True
                    rec.in_p2 = False
                    rec.label = rec.T.label
                    self.structs.append(rec)
                    ss.append(rec.sid)
                runs.append((SR, ss))
            self.serial[start] = runs
        # items
        off = 0
        kinds = array('b')
        sid_of = array('i')
        for rec in self.structs:
            rec.offset = off
            T = rec.T
            for k in T.kinds:
                kinds.append(KCODE[k])
                sid_of.append(rec.sid)
            off += len(T.items)
        self.n_items = off
        self.kinds = kinds
        self.sid_of = sid_of
        self.timings['build'] = round(time.time() - t0, 1)
        self.log('[%s] built %d structures, %d chosen places, %.1fs' % (self.short, len(self.structs), off,
                                                                         time.time() - t0))

    # ================================================================================ unfoldings, guards
    def prepare(self):
        t0 = time.time()
        self.intern = {v: {} for v in VARIANTS}
        # unfold[v][d] : array over items; unr[v] per structure: list over depth k of lists over knots
        self.unf = {v: {d: array('i', [0]) * self.n_items for d in range(1, DMAX + 1)} for v in VARIANTS}
        for rec in self.structs:
            T = rec.T
            rec.unr = {}
            for v in VARIANTS:
                rv, unr = unfold_with_knots(T, v, DMAX, self.intern[v])
                for d in range(1, DMAX + 1):
                    a = self.unf[v][d]
                    o = rec.offset
                    for i, c in enumerate(rv[d]):
                        a[o + i] = c
                rec.unr[v] = unr
            ds = T.dist_start()
            dm = T.dist_member()
            g = []
            for (x, e) in T.items:
                a = ds[x]
                b = dm[x] if dm[x] >= 0 else 10 ** 6
                g.append((a, b))
            rec.guard = g
        self.timings['prepare'] = round(time.time() - t0, 1)
        self.log('[%s] unfoldings and guards, %.1fs; interned %s' % (
            self.short, time.time() - t0, {v: len(self.intern[v]) for v in VARIANTS}))

    # ================================================================================ links valid everywhere
    def whole_links(self):
        """Automorphisms of P2 structures from the record; isomorphisms between serial states and automorphisms within
        them, found by the search on whole structures.  Each is checked place by place.  Returns a list of item pairs."""
        t0 = time.time()
        links = []
        stats = Counter()
        # P2: generators from the record
        for start in self.pairs:
            for sid in self.lineages[start]:
                rec = self.structs[sid]
                T = rec.T
                ns = sum(1 for x in range(T.n) if T.is_start[x])
                RG = AU.RecordGenerators(T, ns)
                gens = list(RG.generators())
                stats['p2_generators'] += len(gens)
                stats['p2_candidates_failed'] += RG.failed
                for i, j in AU.orbit_links(T, gens):
                    links.append((rec.offset + i, rec.offset + j))
        # serial: whole-state isomorphisms and automorphisms
        wintern = {}
        for start in self.pairs:
            for SR, ss in self.serial[start]:
                groups = defaultdict(list)
                for sid in ss:
                    T = self.structs[sid].T
                    sv, _ = VW.unfold(T, 'full', 1, wintern, stable=True)
                    st = sv['stable']
                    inv = (T.n, len(T.items), tuple(sorted(Counter(st).items())))
                    groups[inv].append((sid, st))
                for inv, members in groups.items():
                    reps = []    # (sid, graph)
                    for sid, st in members:
                        T = self.structs[sid].T
                        G = AU.whole_graph(T)
                        done = False
                        for rsid, RGr in reps:
                            m = ISO.find_renaming(RGr, G)
                            stats['serial_state_tests'] += 1
                            if m is None:
                                continue
                            TA = self.structs[rsid].T
                            sm = AU.structure_map(TA, T, m)
                            if sm is None:
                                stats['serial_state_map_failed'] += 1
                                continue
                            pm = AU.places_map(TA, T, *sm)
                            oa = self.structs[rsid].offset
                            ob = self.structs[sid].offset
                            for i, j in pm.items():
                                links.append((oa + i, ob + j))
                            stats['serial_state_isomorphic'] += 1
                            done = True
                            break
                        if not done:
                            reps.append((sid, G))
                            # automorphisms within this state
                            stats['serial_state_classes'] += 1
                            links.extend(self._state_automorphisms(sid, st, stats))
        self.timings['whole_links'] = round(time.time() - t0, 1)
        self.whole_stats = dict(stats)
        self.log('[%s] whole-structure links %d, %s, %.1fs' % (self.short, len(links), dict(stats), time.time() - t0))
        return links

    def _state_automorphisms(self, sid, st, stats):
        rec = self.structs[sid]
        T = rec.T
        o = rec.offset
        uf = UF(len(T.items))
        out = []
        byv = defaultdict(list)
        for i, c in enumerate(st):
            byv[c].append(i)
        for c, its in byv.items():
            if len(its) < 2:
                continue
            r = its[0]
            Gr = None
            for p in its[1:]:
                if uf.find(p) == uf.find(r):
                    continue
                if Gr is None:
                    Gr = AU.whole_graph(T, root=T.items[r])
                Gp = AU.whole_graph(T, root=T.items[p])
                m = ISO.find_renaming(Gr, Gp)
                stats['serial_auto_tests'] += 1
                if m is None:
                    stats['serial_auto_none'] += 1
                    continue
                sm = AU.structure_map(T, T, m)
                if sm is None:
                    stats['serial_auto_map_failed'] += 1
                    continue
                pm = AU.places_map(T, T, *sm)
                for i, j in pm.items():
                    if i != j and uf.union(i, j):
                        out.append((o + i, o + j))
                stats['serial_automorphisms'] += 1
        return out

    # ================================================================================ identity links at d
    def identity_links(self, d):
        """Items whose looks at d are literally the same (deviations.md items 17(iii), 18): consecutive P2 rounds by the
        rule of item 18; serial states of one start by equal labelled looks."""
        links = []
        # P2 consecutive rounds
        for start in self.pairs:
            sids = self.lineages[start]
            for a, b in zip(sids, sids[1:]):
                TA = self.structs[a].T
                TB = self.structs[b].T
                dist = self._delta_dist(TA, TB)
                oa = self.structs[a].offset
                ob = self.structs[b].offset
                for i, (x, e) in enumerate(TA.items):
                    if dist[x] < 0 or dist[x] > d:
                        j = TB.item_index[(x, e)]
                        links.append((oa + i, ob + j))
        # serial states: labelled looks
        for start in self.pairs:
            keyid = {}
            for SR, ss in self.serial[start]:
                RS = SR.ref.S
                nbr = _nbr_masks(RS)
                for sid in ss:
                    rec = self.structs[sid]
                    T = rec.T
                    st = SR.states[rec.state]
                    if st['extra'] is not None:
                        continue      # the structure after a mismatching birth: no identity links (item 5)
                    I, Bar = st['key']
                    o = rec.offset
                    for x in range(T.n):
                        if not T.sh[x]:
                            continue
                        rx = T.ref_id[x]
                        ball = 1 << rx
                        fr = ball
                        for _ in range(d):
                            new = 0
                            for y in bits(fr):
                                new |= nbr[y]
                            new &= I & ~ball
                            if not new:
                                break
                            ball |= new
                            fr = new
                        nb = 0
                        for y in bits(ball):
                            nb |= nbr[y]
                        kb = (ball, nb & I, Bar & ball)
                        for e, z in T.sh[x]:
                            key = (rx, e, kb)
                            i = o + T.item_index[(x, e)]
                            j = keyid.get(key)
                            if j is None:
                                keyid[key] = i
                            else:
                                links.append((j, i))
        return links

    def _delta_dist(self, TA, TB):
        changed = []
        for y in range(TB.n):
            if y >= TA.n:
                changed.append(y)
            elif TA.knot_signature(y) != TB.knot_signature(y):
                changed.append(y)
        return TB.multi_bfs(changed)

    # ================================================================================ the classes
    def compute(self, vlist=VARIANTS, dlist=None, test_log_every=20000):
        self.prepare()
        wl = self.whole_links()
        dlist = list(range(DMAX, 0, -1)) if dlist is None else dlist
        self.cls = {}
        self.test_stats = {}
        self.class_reps = {}
        for v in vlist:
            for d in dlist:
                t0 = time.time()
                uf = UF(self.n_items)
                st = Counter()
                unf = self.unf[v][d]
                # inherited classes (d + 1, same kind of look; same d, finer look)
                for src in ((v, d + 1), (_finer(v), d)):
                    if src in self.cls:
                        c = self.cls[src]
                        for i in range(self.n_items):
                            if c[i] != i:
                                if unf[i] != unf[c[i]]:
                                    raise AssertionError('an inherited link joins different unfoldings')
                                uf.union(i, c[i])
                        st['inherited_from_%s_%d' % src] = 1
                if v == 'full' and d == DMAX:
                    for i, j in wl:
                        if unf[i] != unf[j]:
                            raise AssertionError('a whole-structure link joins different unfoldings')
                        uf.union(i, j)
                if v == 'full':
                    il = self.identity_links(d)
                    st['identity_links'] = len(il)
                    for i, j in il:
                        if unf[i] != unf[j]:
                            raise AssertionError('an identity link joins different unfoldings')
                        uf.union(i, j)
                # components within unfolding groups
                groups = defaultdict(set)
                for i in range(self.n_items):
                    groups[unf[i]].add(uf.find(i))
                st['unfolding_groups'] = len(groups)
                st['components'] = sum(len(s) for s in groups.values())
                todo = [(g, sorted(s)) for g, s in groups.items() if len(s) > 1]
                st['groups_to_test'] = len(todo)
                ntest = 0
                for g, comps in todo:
                    # representative of each component: the item in the smallest structure
                    reps = [self._best_rep(uf, c) for c in comps]
                    class_reps = []
                    crinv = {}
                    for r in reps:
                        placed = False
                        for cr in class_reps:
                            ntest += 1
                            res = self.alike(r, cr, v, d, crinv, st)
                            if res:
                                uf.union(r, cr)
                                placed = True
                                break
                        if not placed:
                            class_reps.append(r)
                    if ntest and ntest % test_log_every == 0:
                        self.log('[%s] %s d%d tests %d' % (self.short, v, d, ntest))
                st['tests'] = ntest
                cls = array('i', [0]) * self.n_items
                for i in range(self.n_items):
                    cls[i] = uf.find(i)
                self.cls[(v, d)] = cls
                st['classes'] = len(set(cls))
                self.sample_in_look(v, d, 1000)
                st['seconds'] = round(time.time() - t0, 1)
                self.test_stats[(v, d)] = dict(st)
                self.log('[%s] %s d=%d: %s' % (self.short, v, d, dict(st)))

    def _best_rep(self, uf, root):
        # the root is an item index; prefer it (already the smallest index in its component)
        return root

    # ================================================================================ one comparison
    def look(self, i, v, d):
        """Extract the look of item i; its knots are coloured by unfoldings computed on the extracted look alone, and
        the look's root unfolding is checked against the structure-wide value used for grouping."""
        rec = self.structs[self.sid_of[i]]
        T = rec.T
        x, e = T.items[i - rec.offset]
        L = LK.extract(T, x, e, d, v)
        root, unr = VW.in_look(L, self.intern[v])
        if root != self.unf[v][d][i]:
            raise AssertionError('the unfolding computed on the look differs from the structure-wide one: item %d' % i)
        if unr[x] != rec.unr[v][d][x]:
            raise AssertionError('a knot unfolding computed on the look differs from the structure-wide one')
        self.in_look_checked[(v, d)] += 1
        G, info = LK.compress(L, extra=unr)
        return L, G, info

    def alike(self, i, j, v, d, crinv, st):
        """True when a checked renaming carries the look of item i onto that of item j; False when they are told apart
        (colour refinement on the looks, or the exhaustive search)."""
        Li, Gi, Ii = self._cached_look(i, v, d)
        Lj, Gj, Ij = self._cached_look(j, v, d)
        if Gi.n != Gj.n or sorted(Gi.colour) != sorted(Gj.colour):
            st['told_apart_by_colours'] += 1
            return False
        m = greedy_renaming(Gi, Gj)
        if m is None:
            ki = self._crinv(i, Gi, v, d, crinv)
            kj = self._crinv(j, Gj, v, d, crinv)
            if ki != kj:
                st['told_apart_by_refinement'] += 1
                return False
            m = ISO.find_renaming(Gi, Gj)
            if m is None:
                st['told_apart_by_search'] += 1
                return False
            st['alike_by_search'] += 1
        else:
            st['alike_by_greedy'] += 1
        km, dm = LK.full_renaming(Li, Ii, Lj, Ij, m)
        ok, why = LK.check_renaming(Li, Lj, km, dm)
        if not ok:
            raise AssertionError('renaming failed its check: %s' % why)
        return True

    _lc = None

    def _cached_look(self, i, v, d):
        if self._lc is None or self._lc[0] != (v, d):
            self._lc = ((v, d), {})
        c = self._lc[1]
        r = c.get(i)
        if r is None:
            if len(c) > 300:
                c.clear()
            r = self.look(i, v, d)
            c[i] = r
        return r

    def _crinv(self, i, G, v, d, crinv):
        k = crinv.get(i)
        if k is None:
            k = ISO.cr_invariant(G, self.intern_cr(v, d))[0]
            crinv[i] = k
        return k

    def intern_far(self, v):
        """Interning for unfoldings computed on looks beyond distance 6 (run 4), compared only with one another."""
        if not hasattr(self, '_ifar'):
            self._ifar = {}
        return self._ifar.setdefault(v, {})

    def sample_in_look(self, v, d, k, seed=0):
        """Check on k random places that the unfolding computed on the extracted look equals the structure-wide value
        used to group places (deviations.md, item 32).  lr.look raises on a difference."""
        rng = __import__('random').Random(seed * 1000 + d)
        for _ in range(min(k, self.n_items)):
            i = rng.randrange(self.n_items)
            self.look(i, v, d)
            self.in_look_sampled[(v, d)] += 1

    def intern_cr(self, v, d):
        if not hasattr(self, '_icr'):
            self._icr = {}
        return self._icr.setdefault((v, d), {})


def _finer(v):
    return {'c1': 'full', 'c2': 'c1'}.get(v)


def _nbr_masks(S):
    N = S.n_knots
    nbr = [0] * N
    for h in S.holders:
        if len(h) == 2:
            a, b = h
            nbr[a] |= 1 << b
            nbr[b] |= 1 << a
    return nbr


def greedy_renaming(GA, GB):
    """Match breadth-first from x, neighbours paired by (edge label, colour) in index order; checked edge by edge.
    Returns the vertex map or None (then the exhaustive search decides)."""
    n = GA.n
    if n != GB.n:
        return None
    m = [-1] * n
    used = [False] * n
    m[0] = 0
    used[0] = True
    q = [0]
    ca = GA.colour
    cb = GB.colour
    if ca[0] != cb[0]:
        return None
    k = 0
    while k < len(q):
        u = q[k]
        k += 1
        ub = m[u]
        ga = {}
        for w, lab in GA.adj[u]:
            if m[w] < 0:
                key = (lab, ca[w])
                L = ga.get(key)
                if L is None:
                    ga[key] = [w]
                else:
                    L.append(w)
        if not ga:
            continue
        gb = {}
        for w, lab in GB.adj[ub]:
            if not used[w]:
                key = (lab, cb[w])
                L = gb.get(key)
                if L is None:
                    gb[key] = [w]
                else:
                    L.append(w)
        for key, ws in ga.items():
            vs = gb.get(key)
            if vs is None or len(vs) < len(ws):
                return None
            for w, z in zip(ws, vs):
                m[w] = z
                used[z] = True
                q.append(w)
    for z in m:
        if z < 0:
            return None
    if ISO._check_map(GA, GB, m):
        return m
    return None


def unfold_with_knots(T, variant, dmax, intern):
    """The unfoldings of item 21 for every place (depths 1..dmax), and for every knot the unfolding of depth k entered
    from no side (k = 0..dmax), used to colour the knots of a look: a knot at distance j of the look of depth d is
    coloured by its unfolding of depth d - j, a function of the look by the argument of item 21."""
    n = T.n
    sh = T.sh
    mk = VW.marks_of(T, variant)
    get = intern.get

    def iid(key):
        c = get(key)
        if c is None:
            c = len(intern)
            intern[key] = c
        return c
    back = []
    for u in range(n):
        L = []
        for e, w in sh[u]:
            j = None
            for kk, (e2, w2) in enumerate(sh[w]):
                if e2 == e:
                    j = kk
                    break
            L.append(j)
        back.append(L)
    prev = [[iid(('m', mk[u]))] * len(sh[u]) for u in range(n)]
    unr = [[iid(('u0', mk[u])) for u in range(n)]]
    roots = {}
    for d in range(1, dmax + 1):
        root = []
        nxt = []
        un = []
        for u in range(n):
            L = sh[u]
            ch = [prev[w][back[u][i]] for i, (e, w) in enumerate(L)]
            row = []
            for i in range(len(L)):
                rest = tuple(sorted(ch[:i] + ch[i + 1:]))
                root.append(iid(('r', mk[u], ch[i], rest)))
                row.append(iid(('v', mk[u], rest)))
            nxt.append(row)
            un.append(iid(('u', mk[u], tuple(sorted(ch)))))
        roots[d] = root
        unr.append(un)
        prev = nxt
    return roots, unr
