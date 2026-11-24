"""Engine of RING-IN-BALANCE-20261123-001A, on real knots.

Written from the frozen text alone:
  research/RING-IN-BALANCE-20261123-001/definitions.md      (shared definitions)
  research/RING-IN-BALANCE-20261123-001A/preregistration.md (ticket A)
  research/ORDINARY-DYNAMICS-20261120-001/end_operator.md   ("The operator on the present end", text only)

Every knot is a list of distinction numbers; every distinction has one or two holders.  For every knot the
engine keeps its parents, the round it was made in, the distinctions it took and the fresh ones it received;
for every loose distinction whether it is usable or barred.

Conventions that make no difference up to renaming (definitions, last paragraph of "One complete round"):
groups are processed in lexicographic order of their sorted member tuples; a member gives its usable loose
distinctions in increasing number; new knots are numbered joins first (group order), then offshoots (member
order); fresh distinctions are numbered in the order of the new knots, usable ones before barred ones.

Readings taken where the text left a choice are listed in deviations.md of this experiment family.
"""
from __future__ import annotations

import itertools
import re
from collections import Counter, defaultdict

import networkx as nx

# =====================================================================================================  laws

TREATMENTS = ('STALL', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT', 'CANCEL-RETIRE')
RELEASES = ('RELEASE', 'HOLD')
KNOT_LAWS = ('parity', 'nae')
_RATION_RE = re.compile(r'^(ORD|ONE-FEWER|FLOOR0|FLOOR1|CAP-(\d+)|RATION-(\d+))$')


class Law:
    """A knot law, a ration, a treatment of a short member, a release rule and the extras."""

    __slots__ = ('ration', 'treatment', 'release', 'no_offshoot', 'fillers', 'knot_law')

    def __init__(self, ration='ORD', treatment='STALL', release='RELEASE', no_offshoot=False,
                 fillers=False, knot_law='parity'):
        m = _RATION_RE.match(ration)
        if not m:
            raise ValueError('unknown ration %r' % ration)
        if m.group(2) is not None and int(m.group(2)) < 1:
            raise ValueError('CAP-k needs k >= 1')
        if m.group(3) is not None and int(m.group(3)) < 0:
            raise ValueError('RATION-k needs k >= 0')
        if treatment not in TREATMENTS:
            raise ValueError('unknown treatment %r' % treatment)
        if release not in RELEASES:
            raise ValueError('unknown release rule %r' % release)
        if knot_law not in KNOT_LAWS:
            raise ValueError('unknown knot law %r' % knot_law)
        if no_offshoot and treatment == 'CANCEL-OFFSHOOT':
            # The definitions do not combine them (A4 lists NO-OFFSHOOT only with STALL, CANCEL-WAIT, CANCEL-RETIRE).
            raise ValueError('NO-OFFSHOOT is not defined together with CANCEL-OFFSHOOT')
        self.ration = ration
        self.treatment = treatment
        self.release = release
        self.no_offshoot = bool(no_offshoot)
        self.fillers = bool(fillers)
        self.knot_law = knot_law

    # step 7
    def fresh_count(self, p, D):
        q = max(D, 3 - p, 1)
        r = self.ration
        if r == 'ORD':
            return q
        if r.startswith('CAP-'):
            return min(q, int(r[4:]))
        if r.startswith('RATION-'):
            return max(int(r[7:]), 3 - p)
        if r == 'ONE-FEWER':
            return min(q, max(3 - p, 0, q - 1))
        if r == 'FLOOR0':
            return max(3 - p, 0)
        if r == 'FLOOR1':
            return max(3 - p, 1)
        raise AssertionError(r)

    def key(self):
        return (self.ration, self.treatment, self.release, self.no_offshoot, self.fillers, self.knot_law)

    def __eq__(self, other):
        return isinstance(other, Law) and self.key() == other.key()

    def __hash__(self):
        return hash(self.key())

    def replace(self, **kw):
        d = dict(zip(('ration', 'treatment', 'release', 'no_offshoot', 'fillers', 'knot_law'), self.key()))
        d.update(kw)
        return Law(**d)

    def name(self):
        s = '%s/%s/%s' % (self.ration, self.treatment, self.release)
        if self.no_offshoot:
            s += '+NO-OFFSHOOT'
        if self.fillers:
            s += '+FILLERS'
        if self.knot_law != 'parity':
            s += '/' + self.knot_law
        return s

    def to_dict(self):
        return {'ration': self.ration, 'treatment': self.treatment, 'release': self.release,
                'no_offshoot': self.no_offshoot, 'fillers': self.fillers, 'knot_law': self.knot_law,
                'name': self.name()}

    def __repr__(self):
        return 'Law(%s)' % self.name()


ORDINARY = Law('ORD', 'STALL')
TWO_ADDED = Law('CAP-3', 'CANCEL-WAIT', 'RELEASE')
THREE_ADDED = Law('CAP-3', 'CANCEL-WAIT', 'RELEASE', fillers=True)

# ================================================================================================  structure


class Structure:
    """A finite set of knots over distinctions; each distinction has one or two holders."""

    __slots__ = ('places', 'holders', 'barred', 'parents', 'made', 'taken', 'fresh', 'own_time',
                 'n_loose', 'live', 'round', 'labels')

    def __init__(self):
        self.places = []     # knot -> list of distinction ids
        self.holders = []    # distinction -> list of 1 or 2 knot ids
        self.barred = []     # distinction -> bool (meaningful for loose distinctions)
        self.parents = []    # knot -> tuple of parent knots (() for a start knot)
        self.made = []       # knot -> round it was made in (0 for a start knot)
        self.taken = []      # knot -> tuple of distinctions taken from its parents
        self.fresh = []      # knot -> tuple of fresh distinctions it received
        self.own_time = []   # knot -> own time (part-round law; = rounds taken part in under complete rounds)
        self.n_loose = []    # knot -> number of loose distinctions it holds
        self.live = set()    # knots holding at least one loose distinction
        self.round = 0       # number of rounds (or moves) applied
        self.labels = None   # for a start built from stars: distinction id -> given label

    # ---------------------------------------------------------------- basics
    @property
    def n_knots(self):
        return len(self.places)

    @property
    def n_distinctions(self):
        return len(self.holders)

    def copy(self):
        T = Structure.__new__(Structure)
        T.places = [list(p) for p in self.places]
        T.holders = [list(h) for h in self.holders]
        T.barred = list(self.barred)
        T.parents = list(self.parents)
        T.made = list(self.made)
        T.taken = list(self.taken)
        T.fresh = list(self.fresh)
        T.own_time = list(self.own_time)
        T.n_loose = list(self.n_loose)
        T.live = set(self.live)
        T.round = self.round
        T.labels = self.labels
        return T

    def is_loose(self, d):
        return len(self.holders[d]) == 1

    def loose(self, u):
        return [d for d in self.places[u] if len(self.holders[d]) == 1]

    def usable(self, u):
        return sorted(d for d in self.places[u] if len(self.holders[d]) == 1 and not self.barred[d])

    def hk(self, u):
        h = k = 0
        for d in self.places[u]:
            if len(self.holders[d]) == 1:
                if self.barred[d]:
                    k += 1
                else:
                    h += 1
        return h, k

    def neighbors(self, u):
        """Knots that meet u (share a distinction with it)."""
        out = set()
        for d in self.places[u]:
            for x in self.holders[d]:
                if x != u:
                    out.add(x)
        return out

    def total_loose(self):
        return sum(self.n_loose[u] for u in self.live)

    def any_barred_loose(self):
        return any(self.barred[d] for u in self.live for d in self.places[u] if len(self.holders[d]) == 1)

    # ---------------------------------------------------------------- building
    def _new_distinction(self, holder, barred=False):
        d = len(self.holders)
        self.holders.append([holder])
        self.barred.append(bool(barred))
        return d

    def _new_knot(self, taken, parents, made, own_time):
        x = len(self.places)
        self.places.append(list(taken))
        self.parents.append(tuple(parents))
        self.made.append(made)
        self.taken.append(tuple(taken))
        self.fresh.append(())
        self.own_time.append(own_time)
        self.n_loose.append(0)
        for d in taken:
            hs = self.holders[d]
            if len(hs) != 1:
                raise AssertionError('distinction %d taken but not loose' % d)
            if self.barred[d]:
                raise AssertionError('barred distinction %d taken' % d)
            old = hs[0]
            hs.append(x)
            self.n_loose[old] -= 1
            if self.n_loose[old] == 0:
                self.live.discard(old)
        return x

    def _give_fresh(self, x, n_usable, n_barred):
        ids = []
        for i in range(n_usable + n_barred):
            d = self._new_distinction(x, barred=(i >= n_usable))
            self.places[x].append(d)
            ids.append(d)
        self.fresh[x] = tuple(ids)
        self.n_loose[x] += len(ids)
        if self.n_loose[x] > 0:
            self.live.add(x)
        return ids

    def check(self):
        """Internal consistency of the incidence lists."""
        seen = defaultdict(list)
        for u, P in enumerate(self.places):
            if len(set(P)) != len(P):
                raise AssertionError('knot %d lists a distinction twice' % u)
            for d in P:
                seen[d].append(u)
        for d, hs in enumerate(self.holders):
            if sorted(hs) != sorted(seen.get(d, [])):
                raise AssertionError('holders of %d inconsistent' % d)
            if not 1 <= len(hs) <= 2:
                raise AssertionError('distinction %d has %d holders' % (d, len(hs)))
        for u in range(self.n_knots):
            nl = sum(1 for d in self.places[u] if len(self.holders[d]) == 1)
            if nl != self.n_loose[u] or ((nl > 0) != (u in self.live)):
                raise AssertionError('loose bookkeeping of knot %d' % u)
        return True

    def knot_record(self, u):
        h, k = self.hk(u)
        return {'id': u, 'places': list(self.places[u]), 'parents': list(self.parents[u]),
                'made': self.made[u], 'taken': list(self.taken[u]), 'fresh': list(self.fresh[u]),
                'usable': [d for d in self.places[u] if len(self.holders[d]) == 1 and not self.barred[d]],
                'barred': [d for d in self.places[u] if len(self.holders[d]) == 1 and self.barred[d]],
                'h': h, 'k': k}

    def to_dict(self):
        return {'round': self.round, 'knots': [self.knot_record(u) for u in range(self.n_knots)],
                'holders': [list(h) for h in self.holders], 'barred': [int(b) for b in self.barred]}


# ===================================================================================================  starts

def from_stars(stars):
    """A start from its list of knots, each a list of distinction labels (the records' stars)."""
    labels = sorted({d for star in stars for d in star})
    index = {lab: i for i, lab in enumerate(labels)}
    S = Structure()
    S.labels = labels
    S.holders = [[] for _ in labels]
    S.barred = [False] * len(labels)
    for u, star in enumerate(stars):
        if len(set(star)) != len(star):
            raise ValueError('knot %d lists a distinction twice' % u)
        P = [index[d] for d in star]
        S.places.append(P)
        for d in P:
            S.holders[d].append(u)
        S.parents.append(())
        S.made.append(0)
        S.taken.append(())
        S.fresh.append(())
        S.own_time.append(0)
    for d, hs in enumerate(S.holders):
        if len(hs) > 2:
            raise ValueError('distinction %r has %d holders' % (labels[d], len(hs)))
    S.n_loose = [sum(1 for d in P if len(S.holders[d]) == 1) for P in S.places]
    S.live = {u for u in range(len(S.places)) if S.n_loose[u] > 0}
    S.check()
    return S


def ring_stars(n, a):
    if n < 2:
        raise ValueError('a ring needs n >= 2')
    stars = []
    for i in range(n):
        stars.append([(i - 1) % n, i] + [n + i * a + j for j in range(a)])
    return stars


def ring(n, a):
    """Ring(n, a): knot i shares one distinction with knot i+1 (mod n) and holds a loose distinctions."""
    return from_stars(ring_stars(n, a))


def d2_stars(n, a):
    if n < 2:
        raise ValueError('D2 needs n >= 2')
    # members 0..n-1, dead knots w_i = n + i; w_i shares x_i0, x_i1 with member i and y_i0, y_i1 with member i+1
    def x(i, j):
        return 4 * i + j
    def y(i, j):
        return 4 * i + 2 + j
    base = 4 * n
    stars = []
    for i in range(n):
        stars.append([base + i * a + j for j in range(a)] + [x(i, 0), x(i, 1), y((i - 1) % n, 0), y((i - 1) % n, 1)])
    for i in range(n):
        stars.append([x(i, 0), x(i, 1), y(i, 0), y(i, 1)])
    return stars


def d2(n, a):
    """D2(n, a): cycle through dead knots, doubled."""
    return from_stars(d2_stars(n, a))


def dw_stars(n, a):
    if n < 2:
        raise ValueError('DW needs n >= 2')
    # p_i: member i -- w_i ; q_i: member i+1 -- w_i ; e_i: w_i -- w_{i+1}
    def p(i):
        return 3 * i
    def q(i):
        return 3 * i + 1
    def e(i):
        return 3 * i + 2
    base = 3 * n
    stars = []
    for i in range(n):
        stars.append([base + i * a + j for j in range(a)] + [p(i), q((i - 1) % n)])
    for i in range(n):
        stars.append([p(i), q(i), e((i - 1) % n), e(i)])
    return stars


def dw(n, a):
    """DW(n, a): cycle through dead knots that meet one another."""
    return from_stars(dw_stars(n, a))


GENERATOR7_STARS = [[0, 1, 2, 9, 10, 11], [0, 1, 3], [4, 5, 12, 13, 14], [6, 7, 15, 16, 17],
                    [2, 3, 4, 6, 18, 19, 20], [7, 8, 21, 22], [5, 8, 23, 24]]


def generator7():
    """The seven-knot generator (GENERATORS-20261120-001)."""
    return from_stars(GENERATOR7_STARS)


# ===============================================================================================  the roster

class Roster:
    """The live roster (or a roster given explicitly, as in the demand step)."""

    __slots__ = ('members', 'member_set', 'h', 'k', 'maxsets', 'commons', 'parts', 'part_of',
                 'meets_member', 'past_start', 'part_past_start', '_cache')

    def __init__(self, members, h, k, maxsets, commons, meets_member):
        self.members = tuple(sorted(members))
        self.member_set = frozenset(self.members)
        self.h = h
        self.k = k
        self.maxsets = maxsets          # list of frozensets (inclusion-maximal met sets), sorted
        self.commons = commons          # parallel list: tuple of the knots whose met set is exactly that set
        self.meets_member = meets_member  # set of members that meet a member
        self.past_start = not meets_member
        # parts: connected components of joinable
        parent = {u: u for u in self.members}

        def find(u):
            while parent[u] != u:
                parent[u] = parent[parent[u]]
                u = parent[u]
            return u
        for M in maxsets:
            it = iter(M)
            a = find(next(it))
            for b in it:
                b = find(b)
                if a != b:
                    parent[b] = a
        comp = defaultdict(list)
        for u in self.members:
            comp[find(u)].append(u)
        self.parts = sorted(tuple(sorted(c)) for c in comp.values())
        self.part_of = {}
        for i, P in enumerate(self.parts):
            for u in P:
                self.part_of[u] = i
        self.part_past_start = [not any(u in meets_member for u in P) for P in self.parts]
        self._cache = {}

    def part_maxsets(self, i):
        key = ('pm', i)
        if key not in self._cache:
            P = set(self.parts[i])
            self._cache[key] = [M for M in self.maxsets if next(iter(M)) in P]
        return self._cache[key]

    def summary(self):
        return {'members': len(self.members), 'parts': len(self.parts),
                'h': sorted(self.h[u] for u in self.members),
                'k': sorted(self.k[u] for u in self.members),
                'metset_sizes': sorted(len(M) for M in self.maxsets)}

    def to_dict(self):
        return {'members': [[u, self.h[u], self.k[u]] for u in self.members],
                'maxsets': [sorted(M) for M in self.maxsets],
                'commons': [list(c) for c in self.commons],
                'parts': [list(P) for P in self.parts],
                'past_start': self.past_start}


def maximal_sets(set_commons):
    """set_commons: dict frozenset -> list of common knots.  Returns the inclusion-maximal sets, sorted."""
    items = sorted(set_commons.items(), key=lambda kv: (-len(kv[0]), sorted(kv[0])))
    by_member = defaultdict(list)
    kept = []
    for M, com in items:
        m0 = min(M, key=lambda x: len(by_member[x]))
        if any(M <= kept[i][0] for i in by_member[m0]):
            continue
        idx = len(kept)
        kept.append((M, tuple(sorted(com))))
        for x in M:
            by_member[x].append(idx)
    kept.sort(key=lambda kc: sorted(kc[0]))
    return [M for M, _ in kept], [c for _, c in kept]


def build_roster(S, members_hk):
    """Roster of the given members [(u, h, k)], with met sets read from the structure S."""
    mset = {u for u, _, _ in members_hk}
    h = {u: hu for u, hu, _ in members_hk}
    k = {u: ku for u, _, ku in members_hk}
    raw = defaultdict(set)
    meets_member = set()
    for u in mset:
        for w in S.neighbors(u):
            raw[w].add(u)
            if w in mset:
                meets_member.add(u)
    sc = defaultdict(list)
    for w, ms in raw.items():
        if len(ms) >= 2:
            sc[frozenset(ms)].append(w)
    maxsets, commons = maximal_sets(sc)
    return Roster(mset, h, k, maxsets, commons, meets_member)


def live_members(S):
    out = []
    for u in sorted(S.live):
        h, k = S.hk(u)
        if h > 0:
            out.append((u, h, k))
    return out


def live_roster(S):
    """The live roster of a structure: the knots holding at least one usable loose distinction."""
    return build_roster(S, live_members(S))


# ===================================================================================================  groups

def groups_from(members, maxsets):
    """Step 1: the inclusion-maximal sets of >= 3 pairwise joinable members contained in no single met set,
    then every joinable pair contained in none of those.  Sorted lexicographically."""
    G = nx.Graph()
    G.add_nodes_from(members)
    by_member = defaultdict(list)
    for i, M in enumerate(maxsets):
        L = sorted(M)
        for x in L:
            by_member[x].append(i)
        G.add_edges_from(itertools.combinations(L, 2))
    big = []
    for Q in nx.find_cliques(G):
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
    pairs = []
    for a, b in G.edges():
        e = (a, b) if a < b else (b, a)
        if e not in covered:
            pairs.append(e)
    return sorted(big + pairs)


def roster_groups(roster, part_index=None):
    if part_index is None:
        return groups_from(roster.members, roster.maxsets)
    return groups_from(roster.parts[part_index], roster.part_maxsets(part_index))


# ====================================================================================================  round

def _apply_round(S, law, part=None, demand_scope='part'):
    """One complete round (steps 1-8) applied in place; with `part`, to the members of that part alone."""
    rnd = S.round + 1
    mem = live_members(S)
    roster = build_roster(S, mem)
    if part is not None:
        part = tuple(sorted(part))
        if part not in roster.parts:
            raise ValueError('not a part of the live roster')
        pi = roster.parts.index(part)
        act_members = list(part)
        act_maxsets = roster.part_maxsets(pi)
    else:
        act_members = list(roster.members)
        act_maxsets = roster.maxsets
    h = {u: roster.h[u] for u in act_members}
    total_loose = S.total_loose()
    # 1. groups
    groups = groups_from(act_members, act_maxsets)
    # 2. owing; shortness read once
    owe = Counter(u for g in groups for u in g)
    short = sorted(u for u in act_members if owe[u] > h[u])
    shortset = set(short)
    rec = {'round': rnd, 'part': list(part) if part is not None else None,
           'n_members_before': len(act_members), 'groups': [list(g) for g in groups],
           'short': short, 'cancelled': [], 'births': [], 'waiting': [], 'retired': [], 'held': {},
           'barred_no_offshoot': {}, 'closing': False, 'stalled': False, 'jammed': False, 'stopped': False}
    # 3. treatment
    if law.treatment == 'STALL' and short:
        rec['stalled'] = True
        S.round = rnd
        rec.update(_round_tail(S, rec, act_members))
        return rec
    cancelled = [g for g in groups if shortset.intersection(g)]
    kept = [g for g in groups if not shortset.intersection(g)]
    rec['cancelled'] = [list(g) for g in cancelled]
    canc_count = Counter(u for g in cancelled for u in g)
    avail = {u: S.usable(u) for u in act_members}
    ptr = {u: 0 for u in act_members}
    births = []   # (kind, parents, taken)
    # 4. joins
    for g in kept:
        taken = []
        for u in g:
            taken.append(avail[u][ptr[u]])
            ptr[u] += 1
        births.append(('join', g, taken))
    # 5. offshoots, release rule, extras; treatment of the short members
    to_bar = []
    for u in sorted(act_members):
        rem = avail[u][ptr[u]:]
        if u in shortset:
            if law.treatment == 'CANCEL-OFFSHOOT':
                for d in rem:
                    births.append(('offshoot', (u,), [d]))
            elif law.treatment == 'CANCEL-WAIT':
                rec['waiting'].append(u)
            elif law.treatment == 'CANCEL-RETIRE':
                rec['retired'].append(u)
                to_bar.extend(rem)
            else:
                raise AssertionError
        else:
            nh = canc_count[u] if law.release == 'HOLD' else 0
            keep, off = rem[:nh], rem[nh:]
            if nh:
                rec['held'][u] = nh
            if law.no_offshoot:
                if off:
                    rec['barred_no_offshoot'][u] = len(off)
                to_bar.extend(off)
            else:
                for d in off:
                    births.append(('offshoot', (u,), [d]))
    for d in to_bar:
        S.barred[d] = True
    # make the new knots (taken distinctions now shared)
    new = []
    for kind, parents, taken in births:
        ot = 1 + max(S.own_time[p] for p in parents)
        x = S._new_knot(taken, parents, rnd, ot)
        new.append((x, kind, parents, taken))
    # members of the moved roster that keep a usable loose distinction (waiting, holding)
    persisting = []
    for u in act_members:
        hu, ku = S.hk(u)
        if hu > 0:
            persisting.append((u, hu, ku))
    # 6. demand
    demand_members = [(x, 1, 0) for x, _, _, _ in new] + persisting
    if part is not None and demand_scope == 'all':
        actset = set(act_members)
        demand_members += [(u, hh, kk) for (u, hh, kk) in mem if u not in actset]
    droster = build_roster(S, demand_members)
    dgroups = groups_from(droster.members, droster.maxsets)
    D = Counter(u for g in dgroups for u in g)
    # 7. closing exception (parity only): a new knot that takes every loose distinction of the structure
    closing = (law.knot_law == 'parity' and len(new) == 1 and len(new[0][3]) == total_loose)
    rec['closing'] = closing
    for x, kind, parents, taken in new:
        p = len(parents)
        Dx = D[x]
        f = 0 if closing else law.fresh_count(p, Dx)
        # 8. FILLERS
        fu = min(f, Dx) if law.fillers else f
        fb = f - fu
        S._give_fresh(x, fu, fb)
        rec['births'].append({'id': x, 'kind': kind, 'parents': list(parents), 'taken': list(taken),
                              'D': Dx, 'f': f, 'usable': fu, 'barred': fb})
    for u, _, _ in persisting:
        S.own_time[u] += 1
    S.round = rnd
    rec.update(_round_tail(S, rec, act_members))
    return rec


def _round_tail(S, rec, act_members):
    members_after = any(S.hk(u)[0] > 0 for u in S.live)
    nb = len(rec['births'])
    return {'n_births': nb,
            'n_joins': sum(1 for b in rec['births'] if b['kind'] == 'join'),
            'n_offshoots': sum(1 for b in rec['births'] if b['kind'] == 'offshoot'),
            'fresh_total': sum(b['f'] for b in rec['births']),
            'jammed': bool(members_after and nb == 0),
            'stopped': not members_after,
            'n_knots': S.n_knots, 'n_distinctions': S.n_distinctions}


def round_step(S, law, inplace=False):
    """One complete round.  Returns (new structure, record of the round)."""
    T = S if inplace else S.copy()
    rec = _apply_round(T, law)
    return T, rec


def part_round_step(S, law, part, inplace=False, demand_scope='part'):
    """One complete round applied to the members of ONE part only, the other parts left as they are.

    demand_scope='part' (default): the demand roster of step 6 holds the moved part's new knots and its old
    members that keep a usable distinction; 'all' adds every member of the other parts as it stands."""
    T = S if inplace else S.copy()
    rec = _apply_round(T, law, part=part, demand_scope=demand_scope)
    return T, rec


# ============================================================================================  the knot test

class GF2Basis:
    """A basis over the field of two elements, vectors as Python ints, with pivot = leading bit.
    Basis vectors are never changed after insertion, so the last insertions can be undone."""

    __slots__ = ('piv', 'log')

    def __init__(self):
        self.piv = {}
        self.log = []

    def insert(self, v):
        piv = self.piv
        while v:
            p = v.bit_length() - 1
            b = piv.get(p)
            if b is None:
                piv[p] = v
                self.log.append(p)
                return True
            v ^= b
        return False

    def mark(self):
        return len(self.log)

    def rollback(self, mark):
        log = self.log
        piv = self.piv
        while len(log) > mark:
            del piv[log.pop()]

    def rank(self):
        return len(self.piv)


def column_vectors(S):
    return [sum(1 << u for u in hs) for hs in S.holders]


def gf2_rank_columns(cols):
    B = GF2Basis()
    for v in cols:
        B.insert(v)
    return B.rank()


def parity_rank_values(S):
    """For every knot v: rank(H) - rank(H with the columns of v's places removed), over GF(2).

    H has one row per knot and one column per distinction.  The ranks are computed by elimination on the
    column vectors (exact bit arithmetic); rank(H without the columns S_v) for all v at once by a
    divide-and-conquer over the knots with an undoable basis.  The knot passes when the value is one."""
    N = S.n_knots
    cols = column_vectors(S)
    full = gf2_rank_columns(cols)
    res = [0] * N
    B = GF2Basis()
    stamp = [-1] * S.n_distinctions
    counter = [0]

    def add_side(lo, hi, excl_lo, excl_hi):
        # add columns with a holder in [lo,hi) and none in [excl_lo, excl_hi)
        counter[0] += 1
        c = counter[0]
        for u in range(lo, hi):
            for d in S.places[u]:
                if stamp[d] == c:
                    continue
                stamp[d] = c
                if any(excl_lo <= x < excl_hi for x in S.holders[d]):
                    continue
                B.insert(cols[d])

    def rec(lo, hi):
        if hi - lo == 1:
            res[lo] = B.rank()
            return
        mid = (lo + hi) // 2
        m = B.mark()
        add_side(mid, hi, lo, mid)
        rec(lo, mid)
        B.rollback(m)
        add_side(lo, mid, mid, hi)
        rec(mid, hi)
        B.rollback(m)

    if N:
        rec(0, N)
    return [full - r for r in res], full


def parity_rank_values_naive(S, knots=None):
    """The same values by a fresh row elimination per knot (for small structures; self-checks)."""
    rows = [sum(1 << d for d in P) for P in S.places]
    full = _row_rank(rows)
    out = []
    for v in (range(S.n_knots) if knots is None else knots):
        mask = ~sum(1 << d for d in S.places[v])
        out.append(full - _row_rank([r & mask for r in rows]))
    return out


def _row_rank(rows):
    B = GF2Basis()
    for r in rows:
        B.insert(r)
    return B.rank()


def articulation_points(nv, adj):
    disc = [-1] * nv
    low = [0] * nv
    ap = [False] * nv
    timer = 0
    for root in range(nv):
        if disc[root] != -1:
            continue
        disc[root] = low[root] = timer
        timer += 1
        root_children = 0
        stack = [(root, -1, iter(adj[root]))]
        while stack:
            u, par, it = stack[-1]
            pushed = False
            for w in it:
                if disc[w] == -1:
                    disc[w] = low[w] = timer
                    timer += 1
                    stack.append((w, u, iter(adj[w])))
                    pushed = True
                    break
                elif w != par:
                    if disc[w] < low[u]:
                        low[u] = disc[w]
            if pushed:
                continue
            stack.pop()
            if stack:
                p = stack[-1][0]
                if low[u] < low[p]:
                    low[p] = low[u]
                if p == root:
                    root_children += 1
                elif low[u] >= disc[p]:
                    ap[p] = True
        if root_children >= 2:
            ap[root] = True
    return ap


def parity_cut_test(S):
    """Cut method: one vertex per knot and one for the outside; an edge between the two holders of each shared
    distinction and an edge to the outside for each loose one.  A knot passes when it is not a cut vertex
    (all its edges reach one component of the rest; see deviations.md, D1)."""
    N = S.n_knots
    O = N
    adj = [[] for _ in range(N + 1)]
    for hs in S.holders:
        if len(hs) == 2:
            a, b = hs
            adj[a].append(b)
            adj[b].append(a)
        else:
            a = hs[0]
            adj[a].append(O)
            adj[O].append(a)
    ap = articulation_points(N + 1, adj)
    return [not ap[v] for v in range(N)]


def parity_knot_test(S):
    """Both parity methods on every knot.  Returns a dict with per-knot verdicts and their agreement."""
    vals, full = parity_rank_values(S)
    rank_pass = [v == 1 for v in vals]
    cut_pass = parity_cut_test(S)
    disagree = [u for u in range(S.n_knots) if rank_pass[u] != cut_pass[u]]
    return {'n_knots': S.n_knots, 'rank_H': full,
            'rank_fail': [u for u in range(S.n_knots) if not rank_pass[u]],
            'cut_fail': [u for u in range(S.n_knots) if not cut_pass[u]],
            'disagree': disagree,
            'all_pass': not disagree and all(rank_pass),
            'rank_values_not_one': {u: vals[u] for u in range(S.n_knots) if vals[u] != 1}}


def nae_knot_test(S, knots=None, solver='minisat22'):
    """Not-all-equal: for each knot, each of the 2^|S| assignments of its places is checked with a SAT solver;
    it passes when exactly the non-constant ones extend to an allowed state of the whole structure."""
    from pysat.solvers import Solver
    fails = []
    calls = 0
    with Solver(name=solver) as sat:
        for P in S.places:
            vs = [d + 1 for d in P]
            sat.add_clause(vs)
            sat.add_clause([-v for v in vs])
        for u in (range(S.n_knots) if knots is None else knots):
            P = S.places[u]
            m = len(P)
            ok = True
            for mask in range(1 << m):
                assum = [(d + 1) if (mask >> i) & 1 else -(d + 1) for i, d in enumerate(P)]
                ext = sat.solve(assumptions=assum)
                calls += 1
                constant = (mask == 0 or mask == (1 << m) - 1)
                if ext == constant:
                    ok = False
                    break
            if not ok:
                fails.append(u)
    return {'n_knots': S.n_knots, 'fail': fails, 'all_pass': not fails, 'sat_calls': calls}


def extension_test_parity(before, after):
    """A round extends when every allowed state before it is the restriction of an allowed state after it.
    Under parity: rank(H_after) - rank(H_after on the new distinctions) == rank(H_before)."""
    r_old = gf2_rank_columns(column_vectors(before))
    cols_new = column_vectors(after)
    r_new = gf2_rank_columns(cols_new)
    r_fresh = gf2_rank_columns(cols_new[before.n_distinctions:])
    dim_before = before.n_distinctions - r_old
    dim_restricted = before.n_distinctions - r_new + r_fresh
    return {'extends': dim_before == dim_restricted, 'dim_before': dim_before, 'dim_restricted': dim_restricted}


# ===============================================================================================  sameness

def roster_graph(roster, members=None):
    """Bipartite graph: one vertex per member coloured (h, k), one per inclusion-maximal met set."""
    if members is None:
        members = roster.members
        msets = roster.maxsets
    else:
        ms = set(members)
        msets = [M for M in roster.maxsets if next(iter(M)) in ms]
    G = nx.Graph()
    for u in members:
        G.add_node(('m', u), c='m%d,%d' % (roster.h[u], roster.k[u]))
    for i, M in enumerate(msets):
        G.add_node(('s', i), c='s')
        for u in M:
            G.add_edge(('s', i), ('m', u))
    return G


def _cheap_sig(roster, members=None):
    if members is None:
        members = roster.members
        msets = roster.maxsets
    else:
        ms = set(members)
        msets = [M for M in roster.maxsets if next(iter(M)) in ms]
    deg = Counter()
    for M in msets:
        for u in M:
            deg[u] += 1
    return (len(members), tuple(sorted((roster.h[u], roster.k[u], deg[u]) for u in members)),
            tuple(sorted(len(M) for M in msets)))


class SigCache:
    """Invariants first; a positive answer is always decided by an exact isomorphism test (VF2)."""

    def __init__(self):
        self.cheap = {}
        self.wl = {}
        self.graph = {}
        self.vf2_calls = 0

    def _key(self, roster, members):
        return (id(roster), None if members is None else tuple(members))

    def cheap_sig(self, roster, members=None):
        k = self._key(roster, members)
        if k not in self.cheap:
            self.cheap[k] = _cheap_sig(roster, members)
        return self.cheap[k]

    def g(self, roster, members=None):
        k = self._key(roster, members)
        if k not in self.graph:
            self.graph[k] = roster_graph(roster, members)
        return self.graph[k]

    def wl_hash(self, roster, members=None):
        k = self._key(roster, members)
        if k not in self.wl:
            self.wl[k] = nx.weisfeiler_lehman_graph_hash(self.g(roster, members), node_attr='c', iterations=4)
        return self.wl[k]

    def same(self, r1, m1, r2, m2):
        if self.cheap_sig(r1, m1) != self.cheap_sig(r2, m2):
            return False
        if self.wl_hash(r1, m1) != self.wl_hash(r2, m2):
            return False
        self.vf2_calls += 1
        return nx.is_isomorphic(self.g(r1, m1), self.g(r2, m2), node_match=lambda a, b: a['c'] == b['c'])


def same_rosters(r1, r2, cache=None):
    cache = cache or SigCache()
    return cache.same(r1, None, r2, None)


def same_parts(r1, part1, r2, part2, cache=None):
    cache = cache or SigCache()
    return cache.same(r1, tuple(part1), r2, tuple(part2))


# ==================================================================================================  a run

class Run:
    """One start grown under one law through a stated number of rounds (or until a stated number of knots)."""

    def __init__(self, start, law, rounds, knot_cap=None, hook=None, hook_needs_before=False, label=None):
        self.law = law
        self.label = label
        self.rounds_asked = rounds
        self.knot_cap = knot_cap
        S = start.copy()
        self.rosters = [live_roster(S)]
        self.records = []
        self.cut_off = False
        if hook is not None:
            hook(S, 0, None, None)
        for r in range(1, rounds + 1):
            # hook_needs_before: True, or the last round for which the hook needs the structure before the round
            nb = hook_needs_before is True or (not isinstance(hook_needs_before, bool) and r <= hook_needs_before)
            before = S.copy() if nb else None
            rec = _apply_round(S, law)
            self.records.append(rec)
            self.rosters.append(live_roster(S))
            if hook is not None:
                hook(S, r, rec, before)
            if knot_cap is not None and S.n_knots > knot_cap:
                self.cut_off = True
                break
        self.S = S
        self.rounds_done = len(self.records)
        self.cache = SigCache()
        self._desc = None

    # ---------------------------------------------------------- descent
    def descent_step(self, t):
        """For each member after round t, the members after round t-1 it descends from."""
        prev = self.rosters[t - 1].member_set
        out = {}
        for x in self.rosters[t].members:
            if x in prev:
                out[x] = (x,)               # it kept a usable distinction (waited or held): itself
            else:
                if self.S.made[x] != t:
                    raise AssertionError('member %d after round %d neither old nor new' % (x, t))
                ps = self.S.parents[x]
                for p in ps:
                    if p not in prev:
                        raise AssertionError('parent not a member')
                out[x] = ps
        return out

    def descent(self):
        if self._desc is None:
            self._desc = [None] + [self.descent_step(t) for t in range(1, self.rounds_done + 1)]
        return self._desc

    def ancestry(self, s, start_labels):
        """start_labels: dict member@s -> label.  Yields (t, dict member@t -> frozenset of labels)."""
        desc = self.descent()
        anc = {u: frozenset([lab]) for u, lab in start_labels.items()}
        yield s, anc
        for t in range(s + 1, self.rounds_done + 1):
            step = desc[t]
            new = {}
            for x, src in step.items():
                if len(src) == 1:
                    a = anc.get(src[0])
                    if a is not None:
                        new[x] = a
                else:
                    acc = frozenset()
                    for p in src:
                        a = anc.get(p)
                        if a is not None:
                            acc = acc | a
                    if acc:
                        new[x] = acc
            anc = new
            yield t, anc

    # ---------------------------------------------------------- returns
    def find_returns(self):
        """For every part Y after round s (past its start), the least t > s at which it returns, with the
        parts given off.  Ordered by least s, then least t."""
        if hasattr(self, '_returns'):
            return self._returns
        out = []
        self.mixed_parts = []
        R = self.rounds_done
        for s in range(0, R):
            ros = self.rosters[s]
            cand = [i for i in range(len(ros.parts)) if ros.part_past_start[i]]
            if not cand:
                continue
            pending = set(cand)
            labels = {u: ros.part_of[u] for u in ros.members}
            for t, anc in self.ancestry(s, labels):
                if t == s:
                    continue
                if not pending:
                    break
                rt = self.rosters[t]
                byY = defaultdict(list)
                alive = set()
                for j, P in enumerate(rt.parts):
                    A = frozenset()
                    for x in P:
                        a = anc.get(x)
                        if a is not None:
                            A = A | a
                    alive |= A
                    if len(A) == 1:
                        byY[next(iter(A))].append(j)
                    elif len(A) > 1:
                        self.mixed_parts.append((s, t, j, sorted(A)))
                for Y in sorted(pending):
                    if Y not in alive:
                        pending.discard(Y)       # ended (or only in mixed parts)
                        continue
                    Ds = byY.get(Y, [])
                    match = None
                    for j in Ds:
                        if self.cache.same(ros, ros.parts[Y], rt, rt.parts[j]):
                            match = j
                            break
                    if match is not None:
                        off = [rt.parts[j] for j in Ds if j != match]
                        out.append({'s': s, 'part_index': Y, 'part': list(ros.parts[Y]),
                                    'part_size': len(ros.parts[Y]), 't': t, 'period': t - s,
                                    'same_index': match, 'same_part': list(rt.parts[match]),
                                    'n_off': len(off), 'off_sizes': sorted(len(P) for P in off),
                                    'off_parts': [list(P) for P in off]})
                        pending.discard(Y)
        out.sort(key=lambda r: (r['s'], r['t'], r['part_index']))
        self._returns = out
        return out

    def first_return(self, with_parts_off=None):
        for r in self.find_returns():
            if with_parts_off is None or (r['n_off'] > 0) == with_parts_off:
                return r
        return None

    # ---------------------------------------------------------- whole roster
    def same_roster_rounds(self, t1, t2):
        return self.cache.same(self.rosters[t1], None, self.rosters[t2], None)

    def in_balance(self, s, T):
        R = self.rounds_done
        if s + T > R:
            return False
        if any(rec['n_births'] == 0 for rec in self.records):
            return False
        return all(self.same_roster_rounds(t, t + T) for t in range(s, R - T + 1))

    def balance_summary(self, max_T=None):
        """For each period T, the least s such that roster(t+T) is the same as roster(t) for all t >= s."""
        R = self.rounds_done
        out = []
        for T in range(1, (max_T or R) + 1):
            if T > R:
                break
            s_best = None
            for t in range(R - T, -1, -1):
                if self.same_roster_rounds(t, t + T):
                    s_best = t
                else:
                    break
            if s_best is not None:
                out.append({'T': T, 's': s_best, 'comparisons': R - T - s_best + 1})
        births_every_round = all(rec['n_births'] > 0 for rec in self.records)
        return {'periods': out, 'births_every_round': births_every_round}

    # ---------------------------------------------------------- kinds
    def kind(self):
        recs = self.records
        if any(r['stalled'] for r in recs):
            return 'stalled'
        if any(r['jammed'] for r in recs):
            return 'jammed'
        if any(r['stopped'] for r in recs):
            return 'stopped'
        rets = self.find_returns()
        if any(r['n_off'] > 0 for r in rets):
            return 'returns giving parts off'
        if rets:
            return 'returns giving none off'
        return 'grows to the bound with no return found'

    def first_event(self):
        for r in self.records:
            for key in ('stalled', 'jammed', 'stopped'):
                if r[key]:
                    return {'event': key, 'round': r['round']}
        return None

    def max_descendant_parts(self):
        """Over every part Y after every round s and every t > s: the largest number of parts of the roster after
        round t holding descendants of Y.  A growth in which no part ever comes apart keeps this at most one."""
        best_c, best_at = 0, None
        for s in range(0, self.rounds_done):
            ros = self.rosters[s]
            labels = {u: ros.part_of[u] for u in ros.members}
            for t, anc in self.ancestry(s, labels):
                if t == s:
                    continue
                cnt = Counter()
                for P in self.rosters[t].parts:
                    A = set()
                    for x in P:
                        A |= anc.get(x, frozenset())
                    for y in A:
                        cnt[y] += 1
                for y in sorted(cnt):
                    if cnt[y] > best_c:
                        best_c, best_at = cnt[y], {'s': s, 'part_index': y, 't': t}
        return best_c, best_at

    # ---------------------------------------------------------- tracking a part
    def track(self, s, members):
        """Descendant members of the given members of roster s at every later round, with the parts they form."""
        labels = {u: 0 for u in members}
        out = []
        for t, anc in self.ancestry(s, labels):
            rt = self.rosters[t]
            dm = sorted(anc)
            parts = sorted({rt.part_of[x] for x in dm})
            whole = [j for j in parts if all(x in anc for x in rt.parts[j])]
            out.append({'t': t, 'members': dm, 'parts': parts, 'whole_parts': whole})
        return out

    def descendant_knots(self, s, members):
        """All knots made after round s that descend (through parents) from the given knots."""
        src = set(members)
        out = []
        desc = set(src)
        for x in range(self.S.n_knots):
            if self.S.made[x] <= s:
                continue
            if any(p in desc for p in self.S.parents[x]):
                desc.add(x)
                out.append(x)
        return out

    # ---------------------------------------------------------- traces
    def trace(self, with_births=False):
        rows = []
        for t, ros in enumerate(self.rosters):
            row = {'round': t}
            row.update(ros.summary())
            if t == 0:
                row['births'] = 0
                row['fresh_total'] = 0
                if with_births:
                    row['birth_list'] = []
            else:
                rec = self.records[t - 1]
                row['births'] = rec['n_births']
                row['fresh_total'] = rec['fresh_total']
                if with_births:
                    row['birth_list'] = sorted([len(b['parents']), b['f']] for b in rec['births'])
                row['n_knots'] = rec['n_knots']
                row['stalled'] = rec['stalled']
                row['jammed'] = rec['jammed']
                row['stopped'] = rec['stopped']
            rows.append(row)
        return rows

    def summary(self):
        rets = self.find_returns()
        fr = rets[0] if rets else None
        fo = self.first_return(True)
        def brief(r):
            if r is None:
                return None
            return {k: r[k] for k in ('s', 't', 'period', 'part_size', 'n_off', 'off_sizes')}
        return {'law': self.law.to_dict(), 'label': self.label, 'rounds_asked': self.rounds_asked,
                'rounds_done': self.rounds_done, 'cut_off': self.cut_off, 'knots': self.S.n_knots,
                'kind': self.kind(), 'first_event': self.first_event(),
                'first_return': brief(fr), 'first_return_with_parts_off': brief(fo),
                'n_returns': len(rets), 'mixed_parts': len(getattr(self, 'mixed_parts', []))}


# ======================================================================================  standard law lists

A4_RATIONS = ('ORD', 'ONE-FEWER', 'FLOOR0', 'FLOOR1', 'RATION-2', 'RATION-3', 'RATION-4', 'CAP-2', 'CAP-3', 'CAP-4')


def a4_laws():
    laws = []
    for r in A4_RATIONS:
        for t in TREATMENTS:
            laws.append(Law(r, t))
        for t in ('STALL', 'CANCEL-WAIT', 'CANCEL-RETIRE'):
            laws.append(Law(r, t, no_offshoot=True))
    return laws
