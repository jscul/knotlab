"""Engine and readings of WHAT-A-BIRTH-CARRIES-20261125-001A-E001 (the course from X only, under ORD and MET).

Written from the frozen texts alone (the drafter's prototype was not seen):
  research/RING-IN-BALANCE-20261123-001/definitions.md     SD (cited by line)
  research/PARTS-MEET-AGAIN-20261124-001/definitions.md    FD (section.item)
  research/MADE-COPIER-20261125-001/definitions.md         D  (section.item)
  research/WHAT-A-BIRTH-CARRIES-20261125-001/definitions.md RD (section.item)
  research/WHAT-A-BIRTH-CARRIES-20261125-001A/preregistration.md
Readings where the texts leave a choice are numbered in deviations.md of this folder (cited W n).

The round is FD 2 (SD steps 1-8 with taking), written here again so that every value the law uses at a birth can be
recorded (RD 3.3); it is checked against the fold engine `pm.py` (imported unchanged, read-only) in run G.  The fold
engine also supplies the guard's numbers (`pm.GUARD`, RD 1.6), its named starts (`pm.STARS`, for run G only) and the
knot test (`knots.py`, FD 7), all used unchanged.

Canonical form of a course (RD 3.1): an exact isomorphism test, VF2 (networkx `GraphMatcher`), inside classes of an
invariant (counts of labels and a Weisfeiler-Lehman hash) that sorts them first; the invariant never decides equality.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import hashlib
import itertools
import os
from collections import Counter, defaultdict

import networkx as nx
from networkx.algorithms import isomorphism as iso

FOLD = ('/home/jscul/p-vs-np-contact-first/experiments/PARTS-MEET-AGAIN-20261124-001A/'
        'PARTS-MEET-AGAIN-20261124-001A-E001_meet_again')
if FOLD not in sys.path:
    sys.path.append(FOLD)      # appended: the fold folder has its own common.py
import pm      # noqa: E402  (unchanged; read-only)
import knots   # noqa: E402  (unchanged; read-only)

GUARD = dict(pm.GUARD)
ROUNDS = 4
KNOT_BOUND = 800
S_ROUND = 1          # s = 1 (RD 2.1)


class GuardStop(Exception):
    def __init__(self, what, value, where):
        super().__init__('%s %s > %s (%s)' % (what, value, GUARD[what], where))
        self.what, self.value, self.where = what, value, where


def guard(what, value, where):
    if value > GUARD[what]:
        raise GuardStop(what, value, where)


# ---------------------------------------------------------------------------------------------------------------- law
class Law:
    """ration in ORD, CAP-3, FLOOR1; treatment in CANCEL-RETIRE, CANCEL-OFFSHOOT, CANCEL-WAIT; RELEASE always;
    take None or 'MET'; choice OLDEST, NEWEST, or EVERY (the planted control: every candidate, RD 5.2); knot law
    'nae' or 'parity' (IMPLIED)."""

    def __init__(self, ration='ORD', treatment='CANCEL-RETIRE', take='MET', choice='OLDEST', knot_law='nae'):
        assert ration in ('ORD', 'CAP-3', 'FLOOR1')
        assert treatment in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT')
        assert take in (None, 'MET')
        assert choice in ('OLDEST', 'NEWEST', 'EVERY')
        assert knot_law in ('nae', 'parity')
        self.ration, self.treatment, self.take, self.choice, self.knot_law = ration, treatment, take, choice, knot_law

    def fresh(self, p, D):
        q = max(D, 3 - p, 1)
        if self.ration == 'ORD':
            return q
        if self.ration == 'CAP-3':
            return min(q, 3)
        return max(3 - p, 1)

    # what knots.test_run asks of a law
    def every_birth_fresh(self):
        return self.knot_law == 'nae'      # every ration here gives f >= 1; parity may imply

    def name(self):
        t = 'no-take' if self.take is None else 'MET(%s)' % self.choice
        return '%s/%s/RELEASE/%s/%s' % (self.ration, self.treatment, t, self.knot_law)

    def to_dict(self):
        return {'ration': self.ration, 'treatment': self.treatment, 'take': self.take, 'choice': self.choice,
                'knot_law': self.knot_law}


# ---------------------------------------------------------------------------------------------------------- structure
class St:
    """Knots with fixed place lists, distinctions with any number of holders, bars, parents, kinds, rounds made.
    Attribute names follow what knots.py reads (places, holders, parents, made, kind, removed, n_knots,
    n_distinctions)."""

    __slots__ = ('places', 'holders', 'barred', 'parents', 'made', 'kind', 'removed', 'round', 'basis', 'maker',
                 'n_start')

    def __init__(self):
        self.places, self.holders, self.barred = [], [], []
        self.parents, self.made, self.kind, self.maker = [], [], [], []
        self.removed = frozenset()
        self.round = 0
        self.basis = {}
        self.n_start = 0

    @property
    def n_knots(self):
        return len(self.places)

    @property
    def n_distinctions(self):
        return len(self.holders)

    def copy(self):
        T = St.__new__(St)
        T.places = [list(p) for p in self.places]
        T.holders = [list(h) for h in self.holders]
        T.barred = list(self.barred)
        T.parents = list(self.parents)
        T.made = list(self.made)
        T.kind = list(self.kind)
        T.maker = list(self.maker)
        T.removed = self.removed
        T.round = self.round
        T.basis = dict(self.basis)
        T.n_start = self.n_start
        return T

    def usable(self, u):
        H, B = self.holders, self.barred
        return sorted(d for d in self.places[u] if len(H[d]) == 1 and not B[d])

    def hk(self, u):
        h = k = 0
        H, B = self.holders, self.barred
        for d in self.places[u]:
            if len(H[d]) == 1:
                if B[d]:
                    k += 1
                else:
                    h += 1
        return h, k

    def meets(self, u):
        out = set()
        H = self.holders
        for d in self.places[u]:
            out.update(H[d])
        out.discard(u)
        return out


def basis_insert(B, v):
    while v:
        p = v.bit_length() - 1
        b = B.get(p)
        if b is None:
            B[p] = v
            return True
        v ^= b
    return False


def basis_contains(B, v):
    while v:
        b = B.get(v.bit_length() - 1)
        if b is None:
            return False
        v ^= b
    return True


def row_of(places):
    r = 0
    for d in places:
        r |= 1 << d
    return r


def from_stars(stars):
    """FD 2.1: a start's distinctions are named by their labels in increasing order; knots in the listed order."""
    labels = sorted({d for st in stars for d in st})
    index = {lab: i for i, lab in enumerate(labels)}
    S = St()
    S.holders = [[] for _ in labels]
    S.barred = [False] * len(labels)
    S.maker = [None] * len(labels)
    for u, st in enumerate(stars):
        assert len(set(st)) == len(st)
        P = [index[d] for d in st]
        S.places.append(P)
        for d in P:
            S.holders[d].append(u)
        S.parents.append(())
        S.made.append(0)
        S.kind.append('start')
    S.n_start = len(stars)
    for u in range(len(stars)):
        basis_insert(S.basis, row_of(S.places[u]))
    return S


# ------------------------------------------------------------------------------------------------------------ roster
class Roster:
    __slots__ = ('members', 'h', 'k', 'sc', 'maxsets', 'adj', 'groups', 'n_cliques', 'n_pairs')


def maximal_sets(sc):
    items = sorted(sc, key=lambda M: (-len(M), sorted(M)))
    by_member = defaultdict(list)
    kept = []
    for M in items:
        m0 = min(M, key=lambda x: len(by_member[x]))
        if any(M <= kept[i] for i in by_member[m0]):
            continue
        idx = len(kept)
        kept.append(M)
        for x in M:
            by_member[x].append(idx)
    return kept, by_member


def build_roster(S, mem, where):
    """SD step 1 (and step 6 for the demand roster), FD 1.3 (a knot is not in its own met set), with the guard's
    checks in the fold engine's order (W 3)."""
    R = Roster()
    mem = sorted(mem)
    members = [u for u, _, _ in mem]
    R.members = members
    R.h = {u: h for u, h, _ in mem}
    R.k = {u: k for u, _, k in mem}
    P, H = S.places, S.holders
    inc = 0
    cnt = Counter()
    for u in members:
        for d in P[u]:
            inc += len(H[d]) - 1
            cnt[d] += 1
    guard('incidences', inc, where)
    if cnt:
        c = max(cnt.values()) - 1
        guard('pairs', c * (c - 1) // 2, where)
    raw = defaultdict(set)
    for u in members:
        for d in P[u]:
            for w in H[d]:
                if w != u:
                    raw[w].add(u)
    sc = defaultdict(list)
    for w, ms in raw.items():
        if len(ms) >= 2:
            sc[frozenset(ms)].append(w)
    if sc:
        m = max(len(M) for M in sc)
        guard('pairs', m * (m - 1) // 2, where)
    maxsets, by_member = maximal_sets(sc)
    adj = {u: set() for u in members}
    npairs = 0
    for M in maxsets:
        L = sorted(M)
        for i, a in enumerate(L):
            Aa = adj[a]
            for b in L[i + 1:]:
                if b not in Aa:
                    Aa.add(b)
                    adj[b].add(a)
                    npairs += 1
        guard('pairs', npairs, where)
    R.n_pairs = npairs
    G = nx.Graph()
    G.add_nodes_from(members)
    for a in members:
        for b in adj[a]:
            if a < b:
                G.add_edge(a, b)
    big = []
    ncl = 0
    for Q in nx.find_cliques(G):
        ncl += 1
        if ncl > GUARD['cliques']:
            guard('cliques', ncl, where)
        if len(Q) < 3:
            continue
        Qs = frozenset(Q)
        q0 = min(Qs, key=lambda x: len(by_member[x]))
        if any(Qs <= maxsets[i] for i in by_member[q0]):
            continue
        big.append(tuple(sorted(Q)))
    covered = set()
    for Q in big:
        covered.update(itertools.combinations(Q, 2))
    pairs = sorted((a, b) for a in members for b in adj[a] if a < b and (a, b) not in covered)
    groups = sorted(big) + pairs
    guard('groups', len(groups), where)
    R.sc = dict(sc)
    R.maxsets = maxsets
    R.adj = adj
    R.groups = groups
    R.n_cliques = ncl
    return R


def live_members(S):
    out = []
    for u in range(S.n_knots):
        h, k = S.hk(u)
        if h > 0:
            out.append((u, h, k))
    return out


# ------------------------------------------------------------------------------------------------------------- round
def candidates(S, b):
    """MET (FD 3.3), both clauses, read on the structure at the start of the round.  Returns sorted
    [(d, suppliers)], suppliers the knots that supply d (W 6)."""
    H = S.holders
    ps = b['parents']
    sup = defaultdict(set)
    if b['kind'] == 'join':
        common = None
        for p in ps:
            m = S.meets(p)
            common = m if common is None else (common & m)
        common = (common or set()) - set(ps)
        held = set()
        for p in ps:
            held.update(S.places[p])
        for w in common:
            for d in S.places[w]:
                if len(H[d]) >= 2 and d not in held:
                    sup[d].add(w)
    else:
        p = ps[0]
        own = set(S.places[p])
        for w in S.meets(p):
            for d in S.places[w]:
                if len(H[d]) >= 2 and d not in own:
                    sup[d].add(w)
    have = set(b['loose'])
    return [(d, tuple(sorted(sup[d]))) for d in sorted(sup) if d not in have]


def play_round(S, law):
    """One complete round with taking (FD 2) applied to S in place.  Raises GuardStop with S unchanged in meaning
    (the caller works on a copy).  Returns the round's record, with everything RD 3.3 reads."""
    rnd = S.round + 1
    mem = live_members(S)
    R = build_roster(S, mem, 'roster')
    members, h = R.members, R.h
    groups = R.groups
    owe = Counter(u for g in groups for u in g)
    short = [u for u in members if owe[u] > h[u]]
    shortset = set(short)
    kept = [g for g in groups if not shortset.intersection(g)]
    cancelled = [g for g in groups if shortset.intersection(g)]
    kept_cnt = Counter(u for g in kept for u in g)
    births = [{'kind': 'join', 'parents': tuple(g), 'off_index': -1} for g in kept]
    guard('births', len(births), 'joins')
    act = {}
    n_off = {}
    bar_from = []
    for u in members:
        if u in shortset:
            if law.treatment == 'CANCEL-OFFSHOOT':
                act[u] = 'offshoot'
                n_off[u] = h[u]
            elif law.treatment == 'CANCEL-WAIT':
                act[u] = 'wait'
            else:
                act[u] = 'retire'
                bar_from.append(u)
        else:
            act[u] = 'none'
            n_off[u] = h[u] - kept_cnt[u]
            assert n_off[u] >= 0
    for u in members:
        for i in range(n_off.get(u, 0)):
            births.append({'kind': 'offshoot', 'parents': (u,), 'off_index': i})
    guard('births', len(births), 'births')
    # FD 2.1: each member gives its usable loose distinctions, in increasing name, to its births in birth order
    recv = defaultdict(list)
    for bi, b in enumerate(births):
        b['loose'] = []
        for p in b['parents']:
            recv[p].append(bi)
    to_bar = []
    for u in members:
        us = S.usable(u)
        lst = recv.get(u, [])
        if u in shortset and law.treatment == 'CANCEL-RETIRE':
            assert not lst
            to_bar.extend(us)
            continue
        if u in shortset and law.treatment == 'CANCEL-WAIT':
            assert not lst
            continue
        assert len(lst) == len(us), (u, lst, us)
        for bi, d in zip(lst, us):
            births[bi]['loose'].append(d)
    # step 5': the taking rule, read on the structure at the start of the round, birth by birth
    for b in births:
        b['cands'] = []
        b['takes'] = []
        if law.take == 'MET':
            c = candidates(S, b)
            b['cands'] = c
            if c:
                if law.choice == 'OLDEST':
                    b['takes'] = [c[0][0]]
                elif law.choice == 'NEWEST':
                    b['takes'] = [c[-1][0]]
                else:
                    b['takes'] = [d for d, _ in c]
        b['inputs'] = b['loose'] + b['takes']
        assert len(set(b['inputs'])) == len(b['inputs'])
        b['take_holders'] = {d: tuple(S.holders[d]) for d in b['takes']}
    base = S.n_knots
    for bi, b in enumerate(births):
        b['id'] = base + bi
        if law.knot_law == 'parity':
            b['implied'] = basis_contains(S.basis, row_of(b['inputs']))
        else:
            b['implied'] = False
    for d in to_bar:
        S.barred[d] = True
    for b in births:
        x = b['id']
        S.places.append(list(b['inputs']))
        S.parents.append(tuple(sorted(b['parents'])))
        S.made.append(rnd)
        S.kind.append(b['kind'])
        for d in b['inputs']:
            S.holders[d].append(x)
    persisting = []
    for u in members:
        hu, ku = S.hk(u)
        if hu > 0:
            persisting.append((u, hu, ku))
    # step 6: demand, met sets read after the takes and before the fresh distinctions
    DR = None
    D = Counter()
    if births:
        DR = build_roster(S, [(b['id'], 1, 0) for b in births] + persisting, 'demand')
        D = Counter(u for g in DR.groups for u in g)
    nfresh = 0
    for b in births:
        b['p'] = len(set(b['inputs']))
        b['D'] = D[b['id']]
        b['f'] = 0 if b['implied'] else law.fresh(b['p'], b['D'])
        nfresh += b['f']
    guard('distinctions', S.n_distinctions + nfresh, 'fresh')
    for b in births:
        x = b['id']
        b['fresh'] = []
        for _ in range(b['f']):
            d = len(S.holders)
            S.holders.append([x])
            S.barred.append(False)
            S.maker.append(x)
            S.places[x].append(d)
            b['fresh'].append(d)
    for b in births:
        basis_insert(S.basis, row_of(S.places[b['id']]))
    S.round = rnd
    return {'round': rnd, 'members': members, 'h': dict(h), 'k': dict(R.k), 'groups': groups, 'owe': dict(owe),
            'short': short, 'cancelled': cancelled, 'act': act, 'births': births, 'roster': R, 'demand': DR,
            'persisting': persisting, 'closing': any(b['implied'] for b in births), 'barred_now': to_bar}


def plain_run(stars, law, rounds=6, knot_bound=KNOT_BOUND):
    """A run with no bars and no readings (run G's comparison with the fold engine)."""
    S = from_stars(stars)
    snaps, recs = [S.copy()], []
    stop = guard_ = None
    while S.round < rounds:
        T = S.copy()
        try:
            rec = play_round(T, law)
        except GuardStop as g:
            stop, guard_ = 'guard', {'round': S.round + 1, 'what': g.what, 'where': g.where}
            break
        S = T
        rec.pop('roster')
        rec.pop('demand')
        recs.append(rec)
        snaps.append(S.copy())
        if S.n_knots > knot_bound:
            stop = 'knots'
            break
    return snaps, recs, stop, guard_


# ----------------------------------------------------------------------------------------------------------- answers
def hkey(*parts):
    return hashlib.blake2b(repr(parts).encode(), digest_size=8).hexdigest()


# --------------------------------------------------------------------------------------------------------------- run
DESC_NAMES = {(True, False): 'X only', (False, True): 'Y only', (True, True): 'both', (False, False): 'neither'}


class RunState:
    """A run of one marked entry under one law, with the readings of RD 3 kept round by round."""

    def __init__(self, stars, usable, law, rounds=ROUNDS, knot_bound=KNOT_BOUND, analyse=True, bars=True):
        self.stars = [list(s) for s in stars]
        self.usable = sorted(usable)
        self.law = law
        S = from_stars(stars)
        sizes = [len(s) for s in stars]
        assert len(stars) == 2
        # X's start knot has three places, Y's h + 1 (RD 2.1)
        self.xs = sizes.index(3) if sizes.count(3) == 1 else 0
        self.ys = 1 - self.xs
        self.h = sizes[self.ys] - 1
        sh = set(S.places[0]) & set(S.places[1])
        assert len(sh) == 1
        self.e = sh.pop()
        self.kkey = ['s%d' % u for u in range(S.n_knots)]      # start knots answer by order (RD 3.2)
        self.dkey = ['d%d' % d for d in range(S.n_distinctions)]  # start distinctions by name
        self.dx, self.dy = [False] * S.n_knots, [False] * S.n_knots
        self.X, self.Y = [], []
        self.snaps = [S.copy()]
        self.recs = []
        self.values = {}           # round -> list of entries (RD 3.3)
        self.meet_round = None
        self.meet_how = None
        self.linking = None
        self.short_after1 = []     # (round, knot, made)
        self.implied_rounds = []
        self.round2 = None
        self.stop = None
        self.guard = None
        self.trace_counts = {}
        self.analyse = analyse
        self.bars_applied = []
        while self.stop is None and S.round < rounds:
            T = S.copy()
            try:
                rec = play_round(T, law)
            except GuardStop as g:
                self.stop = 'guard'
                self.guard = {'round': S.round + 1, 'what': g.what, 'where': g.where, 'value': g.value}
                break
            S = T
            self._after_round(S, rec, bars)
            self.snaps.append(S.copy())
            if S.n_knots > knot_bound:
                self.stop = 'knots'
                break
        self.S = S
        self.rounds_read = S.round

    # ------------------------------------------------------------------------------------------------------------
    def desc(self, u):
        return DESC_NAMES[(self.dx[u], self.dy[u])]

    def _after_round(self, S, rec, bars):
        t = rec['round']
        # names and answers of the new knots and their fresh distinctions (RD 3.2)
        for b in rec['births']:
            pk = tuple(sorted(self.kkey[p] for p in b['parents']))
            k = hkey('b', t, b['kind'], pk, b['off_index'])
            self.kkey.append(k)
            assert len(self.kkey) == b['id'] + 1
            for i, d in enumerate(b['fresh']):
                assert d == len(self.dkey)
                self.dkey.append(hkey('f', k, i))
            dx = any(self.dx[p] for p in b['parents'])
            dy = any(self.dy[p] for p in b['parents'])
            self.dx.append(dx)
            self.dy.append(dy)
        if t == S_ROUND:
            for b in rec['births']:
                if b['parents'] == (self.xs,):
                    self.X.append(b['id'])
                    self.dx[b['id']] = True
                elif b['parents'] == (self.ys,):
                    self.Y.append(b['id'])
                    self.dy[b['id']] = True
            assert len(self.X) == 2 and len(self.Y) == self.h, (self.X, self.Y)
            if bars:
                # RD 2.3: after round 1, bar every usable loose distinction of each Y member whose round-1 input
                # is not among the listed names (W 8)
                ok = set(self.usable)
                byid = {b['id']: b for b in rec['births']}
                for y in self.Y:
                    inp = byid[y]['loose'][0]
                    if inp not in ok:
                        for d in S.usable(y):
                            S.barred[d] = True
                            self.bars_applied.append(d)
            self.recs.append(self._light(rec))
            return
        if self.analyse:
            self._analyse(S, rec)
        self.recs.append(self._light(rec))

    def _light(self, rec):
        out = {k: v for k, v in rec.items() if k not in ('roster', 'demand')}
        out['n_groups'] = len(rec['groups'])
        out['births'] = [{k: v for k, v in b.items() if k not in ('take_holders',)} for b in rec['births']]
        return out

    # ------------------------------------------------------------------------------------------------- RD 3.3
    def _analyse(self, S, rec):
        t = rec['round']
        desc = self.desc
        kk = self.kkey
        dk = self.dkey
        made = S.made

        def kn(u):
            return (kk[u], desc(u), made[u] == 0)
        xo = [u for u in rec['members'] if desc(u) == 'X only']
        xos = set(xo)
        entries = []
        # step 1: each group holding a member from X only, in group order (W 9)
        rankc = Counter()
        member_groups = defaultdict(list)
        for g in rec['groups']:
            for u in g:
                member_groups[u].append(g)
            if not xos.intersection(g):
                continue
            xk = tuple(sorted(kk[u] for u in g if u in xos))
            r = rankc[xk]
            rankc[xk] += 1
            entries.append({'step': 1, 'pos': ('g', xk, r), 'kind': 'group',
                            'value': (len(g), tuple(sorted(desc(u) for u in g))),
                            'part': [kn(u) for u in g]})
        # step 2: each member from X only: owing, short
        for u in xo:
            co = sorted({v for g in member_groups[u] for v in g})
            entries.append({'step': 2, 'pos': ('m', kk[u]), 'kind': 'member',
                            'value': (rec['owe'].get(u, 0), u in rec['short']), 'part': [kn(v) for v in co]})
        # step 3: the treatment's act
        for u in xo:
            co = sorted({v for g in member_groups[u] for v in g})
            entries.append({'step': 3, 'pos': ('a', kk[u]), 'kind': 'act', 'value': rec['act'][u],
                            'part': [kn(v) for v in co]})
        # steps 4-7: each birth with a parent from X only, in birth order
        xb = [b for b in rec['births'] if any(p in xos for p in b['parents'])]
        DR = rec['demand']
        dgroups = defaultdict(list)
        if DR is not None:
            for g in DR.groups:
                for u in g:
                    dgroups[u].append(g)
        for b in xb:
            bk = kk[b['id']]
            entries.append({'step': 4, 'pos': ('b', bk), 'kind': 'birth',
                            'value': (b['kind'], tuple(sorted(kk[p] for p in b['parents'])),
                                      tuple(dk[d] for d in b['loose'])),
                            'part': [kn(p) for p in b['parents']],
                            'loose_from': [(dk[d], kn(p)) for p in b['parents'] for d in b['loose']
                                           if d in S.places[p]]})
        for b in xb:
            bk = kk[b['id']]
            cands = [(dk[d], tuple(sorted(kk[w] for w in sup))) for d, sup in b['cands']]
            entries.append({'step': 5, 'pos': ('c', bk), 'kind': 'candidates',
                            'value': (tuple(sorted(cands)), tuple(sorted(dk[d] for d in b['takes']))),
                            'part': [(dk[d], [kn(w) for w in sup]) for d, sup in b['cands']],
                            'taken': [dk[d] for d in b['takes']]})
        for b in xb:
            bk = kk[b['id']]
            x = b['id']
            partners = sorted({v for g in dgroups.get(x, []) for v in g} - {x})
            entries.append({'step': 6, 'pos': ('D', bk), 'kind': 'demand',
                            'value': (b['D'], tuple(sorted(desc(v) for v in partners))),
                            'part': [kn(v) for v in partners]})
        for b in xb:
            bk = kk[b['id']]
            entries.append({'step': 7, 'pos': ('f', bk), 'kind': 'fresh',
                            'value': (b['p'], b['implied'], b['f']), 'part': []})
        entries.append({'step': 8, 'pos': ('w',), 'kind': 'roundwide', 'value': (rec['closing'], None), 'part': []})
        self.values[t] = entries
        # S1 (Q1): short members after round 1, with an implied birth in an earlier round
        for u in rec['short']:
            self.short_after1.append((t, u, made[u], bool(self.implied_rounds)))
        if rec['closing']:
            self.implied_rounds.append(t)
        # FD's trace in counts, and joint births (W 16)
        dxs = self.dx
        dys = self.dy
        tr = Counter()
        joint = 0
        for b in rec['births']:
            if all(dxs[p] for p in b['parents']):
                tr[(b['kind'], len(b['parents']), b['D'], b['f'])] += 1
            if any(dxs[p] for p in b['parents']) and any(dys[p] for p in b['parents']):
                joint += 1
        self.trace_counts[t] = {'trace': sorted([list(k) + [v] for k, v in tr.items()]), 'joint_births': joint}
        # the meeting round (RD 3.4)
        if self.meet_round is None:
            how = []
            for g in rec['groups']:
                if any(dxs[u] for u in g) and any(dys[u] for u in g):
                    how.append('group')
                    break
            if DR is not None:
                for g in DR.groups:
                    if any(dxs[u] for u in g) and any(dys[u] for u in g):
                        how.append('demand group')
                        break
            took = False
            for b in rec['births']:
                px = any(dxs[p] for p in b['parents'])
                py = any(dys[p] for p in b['parents'])
                for d, hs in b['take_holders'].items():
                    if (px and any(dys[w] for w in hs)) or (py and any(dxs[w] for w in hs)):
                        took = True
                if took:
                    break
            if took:
                how.append('take')
            if how:
                self.meet_round = t
                self.meet_how = how
                self.linking = self._linking(S, rec)
        if t == 2:
            self.round2 = self._s4(S, rec)

    def _linking(self, S, rec):
        """RD 3.5: knots made at or before the round before, whose met set in the round's roster or demand roster
        holds a knot descended from X and one descended from Y; each with its FD 5.7 class (W 12)."""
        t = rec['round']
        dxs, dys = self.dx, self.dy
        found = {}
        for R in (rec['roster'], rec['demand']):
            if R is None:
                continue
            for M, ws in R.sc.items():
                xs = [u for u in M if dxs[u]]
                ys = [u for u in M if dys[u]]
                if not xs or not ys:
                    continue
                for w in ws:
                    if S.made[w] > t - 1:
                        continue
                    found.setdefault(w, []).append((xs, ys))
        out = []
        for w in sorted(found):
            cls = None
            for xs, ys in found[w]:
                for u in xs:
                    au = ancestors(S, u)
                    if w not in au:
                        continue
                    for v in ys:
                        if w in ancestors(S, v) and not (w in S.parents[u] and w in S.parents[v]):
                            cls = 'ancestral common knot'
                            break
                    if cls:
                        break
                if cls:
                    break
            if cls is None:
                cls = 'made, no ancestor of both' if S.made[w] > 0 else 'start knot, no recorded ancestor of both'
            out.append({'knot': w, 'key': self.kkey[w], 'made': S.made[w], 'descent': self.desc(w), 'class': cls,
                        'is_X_start': w == self.xs, 'is_Y_start': w == self.ys,
                        'holds_e': self.e in S.places[w]})
        return out

    def _s4(self, S, rec):
        """The values S3 and S4 speak of, read in round 2 (checked against the formula elsewhere)."""
        xs = set(self.X)
        J = None
        for b in rec['births']:
            if b['kind'] == 'join' and set(b['parents']) == xs:
                J = b
        usable_y = [y for y in self.Y if any(not S.barred[d] for d in self.snaps[1].places[y]
                                               if len(self.snaps[1].holders[d]) == 1)]
        uy = set(usable_y)
        ybirths = [b for b in rec['births'] if any(p in uy for p in b['parents'])]
        ystart_places = set(self.snaps[1].places[self.ys])
        xoff = [b['id'] for b in rec['births'] if b['kind'] == 'offshoot' and b['parents'][0] in xs]
        out = {'J': None, 'M_births': len(ybirths), 'n_births': len(rec['births']),
               'y_births_take_one_place_of_Y_start': all(len(b['takes']) == 1 and b['takes'][0] in ystart_places
                                                          for b in ybirths),
               'y_births_take_e': sum(1 for b in ybirths if b['takes'] == [self.e]),
               'x_offshoots': len(xoff),
               'y_members': [(y, rec['h'].get(y), rec['owe'].get(y, 0), y in rec['short']) for y in usable_y],
               'y_joins_offshoots': [(sum(1 for b in ybirths if b['kind'] == 'join' and y in b['parents']),
                                      sum(1 for b in ybirths if b['kind'] == 'offshoot' and b['parents'][0] == y))
                                     for y in usable_y],
               'every_birth_takes_e': all(b['takes'] == [self.e] for b in rec['births']),
               'x_births_D': [b['D'] for b in rec['births'] if any(p in xs for p in b['parents'])]}
        if J is not None:
            DR = rec['demand']
            jg = [g for g in DR.groups if J['id'] in g]
            partners = sorted({v for g in jg for v in g} - {J['id']})
            ymeets = S.meets(self.ys)
            out['J'] = {'id': J['id'], 'cands': [d for d, _ in J['cands']], 'takes': J['takes'], 'D': J['D'],
                        'f': J['f'], 'p': J['p'], 'places': len(S.places[J['id']]), 'implied': J['implied'],
                        'groups_all_pairs': all(len(g) == 2 for g in jg),
                        'partners_are_xoff_and_ybirths': set(partners) == set(xoff) | {b['id'] for b in ybirths},
                        'Ystart_meets_J_and_ybirths': J['id'] in ymeets and all(b['id'] in ymeets for b in ybirths),
                        'loose_inputs_other_holder_only_parent': all(
                            set(self.snaps[1].holders[d]) <= set(J['parents']) for d in J['loose'])}
        return out


def ancestors(S, u):
    out, stack = set(), list(S.parents[u])
    while stack:
        x = stack.pop()
        if x not in out:
            out.add(x)
            stack.extend(S.parents[x])
    return out


# ------------------------------------------------------------------------------------------- the course (RD 3.1)
def course(run, R):
    """The course from X only after round s through round R, names forgotten, in reduced form (W 10): knots and the
    distinctions held by two or more of its knots are nodes; a distinction held by one of its knots is a leaf label
    on that knot.  Returns (node labels, edges) with local indices, or None if the run did not read round R."""
    if run.rounds_read < R:
        return None
    S = run.snaps[R]
    s1 = run.snaps[S_ROUND]
    nd_s = s1.n_distinctions
    ks = [u for u in range(S.n_knots) if S.made[u] >= S_ROUND and run.desc(u) == 'X only']
    kidx = {u: i for i, u in enumerate(ks)}
    dlab = {}
    dhold = defaultdict(list)
    for u in ks:
        for d in S.places[u]:
            dhold[d].append(kidx[u])
            if d not in dlab:
                if d < nd_s:
                    org = 'E'
                else:
                    org = 'FX' if run.desc(S.maker[d]) == 'X only' else 'FO'
                dlab[d] = '%s:%d' % (org, 1 if S.barred[d] else 0)
    labels = []
    for u in ks:
        cnts = []
        for r in range(max(S.made[u], S_ROUND), R + 1):
            hu, ku = run.snaps[r].hk(u)
            cnts.append('%d.%d' % (hu, ku))
        leafs = sorted(dlab[d] for d in S.places[u] if len(dhold[d]) == 1)
        lc = Counter(leafs)
        labels.append('K|%d|%s|%d|%s|%s' % (S.made[u], S.kind[u], len(S.places[u]), ','.join(cnts),
                                           ','.join('%s*%d' % (k, v) for k, v in sorted(lc.items()))))
    edges = []
    nk = len(ks)
    for d in sorted(dhold):
        hs = dhold[d]
        if len(hs) >= 2:
            j = len(labels)
            labels.append('D|' + dlab[d])
            for i in hs:
                edges.append((i, j, 'i'))
    for u in ks:
        for p in S.parents[u]:
            if p in kidx:
                edges.append((kidx[u], kidx[p], 'p'))
    return {'labels': labels, 'edges': edges, 'n_knots': nk}


def course_graph(c):
    G = nx.Graph()
    for i, l in enumerate(c['labels']):
        G.add_node(i, l=l)
    for a, b, t in c['edges']:
        G.add_edge(a, b, t=t)
    return G


def course_invariant(c):
    G = course_graph(c)
    lab = hashlib.blake2b(repr(sorted(Counter(c['labels']).items())).encode(), digest_size=8).hexdigest()
    wl = nx.weisfeiler_lehman_graph_hash(G, node_attr='l', edge_attr='t', iterations=4)
    return '%d|%d|%s|%s' % (c['n_knots'], len(c['labels']), lab, wl)


_NM = iso.categorical_node_match('l', None)
_EM = iso.categorical_edge_match('t', None)


def same_course(c1, c2, g1=None, g2=None):
    """Exact: VF2 on the labelled graphs (labels include rounds, so parent arcs keep their direction)."""
    if c1['n_knots'] != c2['n_knots'] or len(c1['labels']) != len(c2['labels']) or \
            len(c1['edges']) != len(c2['edges']):
        return False
    if sorted(c1['labels']) != sorted(c2['labels']):
        return False
    g1 = g1 if g1 is not None else course_graph(c1)
    g2 = g2 if g2 is not None else course_graph(c2)
    return iso.GraphMatcher(g1, g2, node_match=_NM, edge_match=_EM).is_isomorphic()


class Registry:
    """Classes of courses: invariant buckets, VF2 inside a bucket."""

    def __init__(self):
        self.buckets = defaultdict(list)    # inv -> [(class id, course, graph)]
        self.n = 0
        self.vf2_calls = 0

    def classify(self, c, inv=None):
        inv = inv or course_invariant(c)
        g = course_graph(c)
        for cid, c2, g2 in self.buckets[inv]:
            self.vf2_calls += 1
            if same_course(c, c2, g, g2):
                return cid
        cid = self.n
        self.n += 1
        self.buckets[inv].append((cid, c, g))
        return cid


# --------------------------------------------------------------------------------------- attribution (RD 4.3)
def align(EA, EB):
    """Pairs the entries of one round of two runs (W 9): entries at the same position (by answers) are paired; the
    rest are paired by rank within a step; an entry left over is paired with nothing.  Order: run A's, then B's
    leftovers at the end of their step."""
    out = []
    steps = sorted({e['step'] for e in EA} | {e['step'] for e in EB})
    for st in steps:
        a = [e for e in EA if e['step'] == st]
        b = [e for e in EB if e['step'] == st]
        bpos = {e['pos']: i for i, e in enumerate(b)}
        used = set()
        pairs = []
        unA = []
        for e in a:
            j = bpos.get(e['pos'])
            if j is not None and j not in used:
                used.add(j)
                pairs.append([e, b[j]])
            else:
                pairs.append([e, None])
                unA.append(len(pairs) - 1)
        unB = [j for j in range(len(b)) if j not in used]
        for i, j in zip(unA, unB):
            pairs[i][1] = b[j]
        for j in unB[len(unA):]:
            pairs.append([None, b[j]])
        out.extend(pairs)
    return out


def _part_keys(e):
    if e is None:
        return {}
    if e['kind'] == 'candidates':
        return {}
    return {x[0]: x for x in e['part']}


def differing_part(ea, eb):
    """The knots of the first differing entry's differing part, after replacing each differing candidate by the
    knot(s) that supply it (RD 4.3)."""
    kind = (ea or eb)['kind']
    if kind == 'candidates':
        ca = {} if ea is None else {d: sup for d, sup in ea['part']}
        cb = {} if eb is None else {d: sup for d, sup in eb['part']}
        knots_ = []
        for d, sup in ca.items():
            if d not in cb or sorted(x[0] for x in cb[d]) != sorted(x[0] for x in sup):
                knots_.extend(sup)
        for d, sup in cb.items():
            if d not in ca or sorted(x[0] for x in ca[d]) != sorted(x[0] for x in sup):
                knots_.extend(sup)
        if not knots_:
            ta = set(ea['taken']) if ea else set()
            tb = set(eb['taken']) if eb else set()
            for d in ta ^ tb:
                knots_.extend(ca.get(d, []) or cb.get(d, []))
        return knots_
    pa, pb = _part_keys(ea), _part_keys(eb)
    out = [v for k, v in pa.items() if k not in pb] + [v for k, v in pb.items() if k not in pa]
    if not out and kind == 'birth' and ea is not None and eb is not None:
        # the same parents, different loose inputs: the parents that gave them (W 11)
        la = dict(ea.get('loose_from', []))
        lb = dict(eb.get('loose_from', []))
        for d in set(la) ^ set(lb):
            out.append(la.get(d) or lb.get(d))
    return out


def classify_part(kind, ea, eb, part):
    if kind == 'roundwide':
        return 'round-wide'
    if kind == 'fresh' and ea is not None and eb is not None and ea['value'][1] != eb['value'][1]:
        return 'round-wide'        # the implied flag (RD 4.3)
    descs = [x[1] for x in part]
    if any(d == 'Y only' for d in descs):
        return 'through the meeting'
    if any(d in ('both', 'neither') for d in descs):
        if part and all(x[2] for x in part):
            return 'a third part (a start knot)'
        return 'a third part'
    return 'unclassified'


def first_difference(EA, EB):
    """The first differing entry of one round (RD 3.3 order) and its class; None when the round's values agree."""
    for ea, eb in align(EA, EB):
        if ea is not None and eb is not None and ea['value'] == eb['value']:
            continue
        kind = (ea or eb)['kind']
        part = differing_part(ea, eb)
        cls = classify_part(kind, ea, eb, part)
        pos = (ea or eb)['pos']
        return {'pos': pos if isinstance(pos, str) else list(pos), 'step': (ea or eb)['step'], 'kind': kind,
                'value_A': None if ea is None else ea['value'], 'value_B': None if eb is None else eb['value'],
                'part': [list(x) for x in part], 'class': cls}
    return None


def compare_values(runA, runB, last_round):
    """The first round 2..last_round where the values used at X's births differ, with its attribution."""
    for t in range(S_ROUND + 1, last_round + 1):
        EA, EB = runA.values.get(t), runB.values.get(t)
        if EA is None or EB is None:
            return None
        fd = first_difference(EA, EB)
        if fd is not None:
            fd['round'] = t
            return fd
    return None


# ---- the hand-written records (attribution_records.json): the same core on pre-aligned entries
def record_entries(lst):
    out = []
    for i, e in enumerate(lst):
        k = e['kind']
        if k == 'group':
            out.append({'step': i, 'pos': e['at'], 'kind': 'group',
                        'value': (e['size'], tuple(sorted(m['descent'] for m in e['members']))),
                        'part': [(m['id'], _rdesc(m['descent']), m.get('start', False)) for m in e['members']]})
        elif k == 'candidates':
            out.append({'step': i, 'pos': e['at'], 'kind': 'candidates',
                        'value': (tuple(sorted((c['d'], c['supplier']['id']) for c in e['value'])), ()),
                        'part': [(c['d'], [(c['supplier']['id'], _rdesc(c['supplier']['descent']),
                                            c['supplier'].get('start', False))]) for c in e['value']],
                        'taken': []})
        elif k == 'demand':
            out.append({'step': i, 'pos': e['at'], 'kind': 'demand',
                        'value': (e['value'], tuple(sorted(m['descent'] for m in e['members']))),
                        'part': [(m['id'], _rdesc(m['descent']), m.get('start', False)) for m in e['members']]})
        elif k == 'implied':
            out.append({'step': i, 'pos': e['at'], 'kind': 'fresh', 'value': (None, e['value'], None), 'part': []})
        else:
            raise ValueError(k)
    return out


def _rdesc(d):
    return {'X only': 'X only', 'Y only': 'Y only', 'both': 'both', 'neither': 'neither'}[d]


def record_attribution(rec):
    EA, EB = record_entries(rec['A']), record_entries(rec['B'])
    # the records are aligned by "at"; give both the same step numbers by position of "at"
    order = {}
    for e in EA + EB:
        order.setdefault(e['pos'], len(order))
    for e in EA + EB:
        e['step'] = order[e['pos']]
    fd = first_difference(EA, EB)
    return fd


# ------------------------------------------------------------------------------------------------- utilities
def run_fingerprint(run):
    h = hashlib.blake2b(digest_size=16)
    for S in run.snaps:
        h.update(repr((S.places, S.barred, S.parents, S.kind, S.made)).encode())
    h.update(repr((run.stop, run.guard and (run.guard['round'], run.guard['what']))).encode())
    return h.hexdigest()


def knot_test(run):
    out = knots.test_run(run.snaps, run.law)
    return {'verdicts': out['verdicts'], 'fails': out['fails'], 'disagree': out['disagree'],
            'untested': out['untested'], 'birth_vs_direct': out['birth_vs_direct']}


def M_formula(h, a):
    return a * (h - 1) - a * (a - 1) // 2
