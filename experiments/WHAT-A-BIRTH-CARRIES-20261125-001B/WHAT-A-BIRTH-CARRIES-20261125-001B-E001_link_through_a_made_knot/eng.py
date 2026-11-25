"""Engine of WHAT-A-BIRTH-CARRIES-20261125-001B-E001: one complete round with taking (FD 2, RELEASE) with the rules of
BD2 2 (takes of a sole candidate, the owing rations, SHORT-BY, the ration controls, J-EACH-PART), and the gate's
MET(OLDEST) and MET(NEWEST).

Written from the frozen texts alone (the drafter's prototype was not seen):
  research/RING-IN-BALANCE-20261123-001/definitions.md        SD (cited by line)
  research/PARTS-MEET-AGAIN-20261124-001/definitions.md       FD (section.item)
  research/MADE-COPIER-20261125-001/definitions.md, _b.md     D, DB
  research/WHAT-A-BIRTH-CARRIES-20261125-001/definitions.md   RD (ticket A)
  research/WHAT-A-BIRTH-CARRIES-20261125-001/definitions_b.md BD2 (this ticket)
  research/WHAT-A-BIRTH-CARRIES-20261125-001B/preregistration.md
Readings taken where the texts leave a choice are numbered in deviations.md of this folder (cited B n).

The round is written again (as ticket A's `wbc.py` did, which it follows step by step) so that every value the law
uses at a birth is recorded (RD 3.3); it is checked against the fold engine `pm.py` (imported unchanged, read-only)
in run G.  The fold engine supplies the guard's numbers (`pm.GUARD`) and its named starts for run G; `knots.py`
supplies the knot test (FD 7), unchanged.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import itertools
from collections import Counter, defaultdict

import networkx as nx

FOLD = ('/home/jscul/p-vs-np-contact-first/experiments/PARTS-MEET-AGAIN-20261124-001A/'
        'PARTS-MEET-AGAIN-20261124-001A-E001_meet_again')
WBC = ('/home/jscul/p-vs-np-contact-first/experiments/WHAT-A-BIRTH-CARRIES-20261125-001A/'
       'WHAT-A-BIRTH-CARRIES-20261125-001A-E001_which_under_ordinary_count')
for _p in (FOLD, WBC):
    if _p not in sys.path:
        sys.path.append(_p)      # appended: both folders have their own common.py
import pm      # noqa: E402  (unchanged; read-only)
import knots   # noqa: E402  (unchanged; read-only)

GUARD = dict(pm.GUARD)
ROUNDS = 7
KNOT_BOUND = 1500


class GuardStop(Exception):
    def __init__(self, what, value, where):
        super().__init__('%s %s (%s)' % (what, value, where))
        self.what, self.value, self.where = what, value, where


class Guard:
    """The fold engine's limits, times a multiplier (run P2), with the peak counts of a run (BD2 1.2)."""

    def __init__(self, mult=1):
        self.mult = mult
        self.lim = {k: v * mult for k, v in GUARD.items()}
        self.peak = Counter()

    def __call__(self, what, value, where):
        if value > self.peak[what]:
            self.peak[what] = value
        if value > self.lim[what]:
            raise GuardStop(what, value, where)


# ---------------------------------------------------------------------------------------------------------------- law
RATIONS_RECORDED = ('FLOOR1', 'CAP-3', 'ORD')
RATIONS_OWING = ('PARENT-OWING', 'PARENT-OWING-CAP3', 'PARENT-OWING-CAP4', 'OFFSHOOT-TWO', 'OFFSHOOT-THREE',
                 'PARENT-OWING-1', 'PARENT-OWING-PLAIN', 'MOD2')
TREATMENTS = ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT', 'SHORT-BY')
TAKES = (None, 'MET', 'MET-SOLE', 'STEPS1-SOLE', 'STEPS2-SOLE', 'J-EACH-PART')


class Law:
    def __init__(self, ration='FLOOR1', treatment='CANCEL-RETIRE', take='MET-SOLE', knot_law='nae', choice=None):
        assert ration in RATIONS_RECORDED + RATIONS_OWING, ration
        assert treatment in TREATMENTS, treatment
        assert take in TAKES, take
        assert knot_law in ('nae', 'parity')
        if take == 'MET':
            assert choice in ('OLDEST', 'NEWEST')
        if treatment == 'SHORT-BY':
            assert ration in ('FLOOR1', 'CAP-3')
        self.ration, self.treatment, self.take, self.knot_law, self.choice = ration, treatment, take, knot_law, choice

    def fresh(self, kind, p, D, o):
        """f for a birth that is not implied: SD step 7 (p distinct inputs, D demand); the owing rations on FLOOR1
        for joins and o, the parent's owing, for offshoots (BD2 2.2, 2.3, 2.5, 2.6; B 9)."""
        r = self.ration
        if r in RATIONS_OWING:
            if kind != 'offshoot':
                return max(3 - p, 1)
            if r == 'PARENT-OWING':
                return max(2, o)
            if r == 'PARENT-OWING-CAP3':
                return min(max(2, o), 3)
            if r == 'PARENT-OWING-CAP4':
                return min(max(2, o), 4)
            if r == 'OFFSHOOT-TWO':
                return 2
            if r == 'OFFSHOOT-THREE':
                return 3
            if r == 'PARENT-OWING-1':
                return max(1, o)
            if r == 'PARENT-OWING-PLAIN':
                return max(o, 3 - p, 1)
            if r == 'MOD2':
                return 2 + (o % 2)
            raise AssertionError(r)
        q = max(D, 3 - p, 1)
        if r == 'ORD':
            return q
        if r == 'CAP-3':
            return min(q, 3)
        return max(3 - p, 1)

    # what knots.test_run asks of a law: every listed ration gives every birth at least one fresh distinction, so
    # under not-all-equal every birth is fresh (FD 7); under parity a birth may be implied
    def every_birth_fresh(self):
        return self.knot_law == 'nae'

    def name(self):
        t = 'no-take' if self.take is None else (self.take if self.take != 'MET' else 'MET(%s)' % self.choice)
        return '%s/%s/RELEASE/%s/%s' % (self.ration, self.treatment, t, self.knot_law)

    def to_dict(self):
        return {'ration': self.ration, 'treatment': self.treatment, 'take': self.take, 'knot_law': self.knot_law,
                'choice': self.choice}


# ---------------------------------------------------------------------------------------------------------- structure
class St:
    """Knots with fixed place lists, distinctions with any number of holders, bars, parents, kinds, rounds made, the
    maker of each fresh distinction.  Attribute names follow what knots.py reads."""

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

    def level(self, u, k):
        cur = {u}
        for _ in range(k):
            nxt = set()
            for x in cur:
                nxt.update(self.parents[x])
            cur = nxt
        return cur

    def ancestors(self, u):
        out, stack = set(), list(self.parents[u])
        while stack:
            x = stack.pop()
            if x not in out:
                out.add(x)
                stack.extend(self.parents[x])
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
    __slots__ = ('members', 'h', 'k', 'sc', 'maxsets', 'adj', 'groups', 'n_cliques', 'n_pairs', 'parts', 'part_of')


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


def build_roster(S, mem, where, G, parts=False):
    """SD step 1 (and step 6 for the demand roster), FD 1.3 (a knot is not in its own met set), with the guard's
    checks in the fold engine's order (as ticket A's engine, W 3)."""
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
    G('incidences', inc, where)
    if cnt:
        c = max(cnt.values()) - 1
        G('pairs', c * (c - 1) // 2, where)
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
        G('pairs', m * (m - 1) // 2, where)
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
        G('pairs', npairs, where)
    R.n_pairs = npairs
    Gr = nx.Graph()
    Gr.add_nodes_from(members)
    for a in members:
        for b in adj[a]:
            if a < b:
                Gr.add_edge(a, b)
    big = []
    ncl = 0
    lim = G.lim['cliques']
    for Q in nx.find_cliques(Gr):
        ncl += 1
        if ncl > lim:
            G('cliques', ncl, where)
        if len(Q) < 3:
            continue
        Qs = frozenset(Q)
        q0 = min(Qs, key=lambda x: len(by_member[x]))
        if any(Qs <= maxsets[i] for i in by_member[q0]):
            continue
        big.append(tuple(sorted(Q)))
    if ncl > G.peak['cliques']:
        G.peak['cliques'] = ncl
    covered = set()
    for Q in big:
        covered.update(itertools.combinations(Q, 2))
    pairs = sorted((a, b) for a in members for b in adj[a] if a < b and (a, b) not in covered)
    groups = sorted(big) + pairs
    G('groups', len(groups), where)
    R.sc = dict(sc)
    R.maxsets = maxsets
    R.adj = adj
    R.groups = groups
    R.n_cliques = ncl
    R.parts = R.part_of = None
    if parts:
        roster_parts(R)
    return R


def roster_parts(R):
    """Parts: components of joinable, in order of their smallest member."""
    seen = {}
    parts = []
    for u in R.members:
        if u in seen:
            continue
        comp = []
        stack = [u]
        seen[u] = len(parts)
        while stack:
            x = stack.pop()
            comp.append(x)
            for y in R.adj[x]:
                if y not in seen:
                    seen[y] = len(parts)
                    stack.append(y)
        parts.append(tuple(sorted(comp)))
    R.parts = parts
    R.part_of = seen
    return parts


def live_members(S):
    out = []
    for u in range(S.n_knots):
        h, k = S.hk(u)
        if h > 0:
            out.append((u, h, k))
    return out


def classes_of_parts(S, parts):
    """FD 1.6: link two parts when a member of one holds a distinction a member of the other holds; the classes."""
    n = len(parts)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    by_d = {}
    for i, P in enumerate(parts):
        for u in P:
            for d in S.places[u]:
                q = by_d.get(d)
                if q is None:
                    by_d[d] = i
                else:
                    a, b = find(q), find(i)
                    if a != b:
                        parent[b] = a
    return [find(i) for i in range(n)]


# ------------------------------------------------------------------------------------------------------------- round
def candidates(S, law, b, R):
    """The taking rule's candidates for birth b, read on the structure at the start of the round, sorted by name:
    [(d, suppliers)], suppliers the knots that supply d (RD 3.3 item 5; B 6)."""
    H = S.holders
    take = law.take
    ps = b['parents']
    sup = defaultdict(set)
    if b['kind'] == 'join':
        if take not in ('MET', 'MET-SOLE'):
            return []
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
        if take in ('MET', 'MET-SOLE'):
            src = S.meets(p)
        elif take == 'STEPS1-SOLE':
            src = S.level(p, 1)
        elif take == 'STEPS2-SOLE':
            src = S.level(p, 2)
        elif take == 'J-EACH-PART':
            mine = R.part_of[p]
            for w in R.members:
                if R.part_of[w] == mine:
                    continue
                for d in S.places[w]:
                    if len(H[d]) >= 2:
                        sup[d].add(w)
            src = ()
        else:
            raise AssertionError(take)
        for w in src:
            for d in S.places[w]:
                if len(H[d]) >= 2 and d not in own:
                    sup[d].add(w)
    have = set(b['loose'])
    return [(d, tuple(sorted(sup[d]))) for d in sorted(sup) if d not in have]


def play_round(S, law, G):
    """One complete round with taking (FD 2, RELEASE) applied to S in place; the caller works on a copy, so that a
    guard stop leaves the structure as it was.  Returns the round's record with every value RD 3.3 reads."""
    rnd = S.round + 1
    mem = live_members(S)
    R = build_roster(S, mem, 'roster', G, parts=(law.take == 'J-EACH-PART'))
    members, h = R.members, R.h
    groups = R.groups
    owe = Counter(u for g in groups for u in g)
    short = [u for u in members if owe[u] > h[u]]
    shortset = set(short)
    kept = [g for g in groups if not shortset.intersection(g)]
    cancelled = [g for g in groups if shortset.intersection(g)]
    kept_cnt = Counter(u for g in kept for u in g)
    births = [{'kind': 'join', 'parents': tuple(g), 'off_index': -1} for g in kept]
    G('births', len(births), 'joins')
    act = {}
    n_off = {}
    n_keep = {}
    for u in members:
        if u in shortset:
            if law.treatment == 'CANCEL-OFFSHOOT':
                act[u] = 'offshoot'
                n_off[u] = h[u]
            elif law.treatment == 'CANCEL-WAIT':
                act[u] = 'wait'
            elif law.treatment == 'CANCEL-RETIRE':
                act[u] = 'retire'
            else:   # SHORT-BY (BD2 2.4)
                n = min(h[u], owe[u] - h[u])
                n_off[u] = n
                n_keep[u] = h[u] - n
                act[u] = 'short-by %d keep %d' % (n, h[u] - n)
        else:
            act[u] = 'none'
            n_off[u] = h[u] - kept_cnt[u]
            assert n_off[u] >= 0
    for u in members:
        for i in range(n_off.get(u, 0)):
            births.append({'kind': 'offshoot', 'parents': (u,), 'off_index': i})
    G('births', len(births), 'births')
    # FD 2.1: each member gives its usable loose distinctions, in increasing name, to its births in birth order;
    # under SHORT-BY a short member's offshoots take its first ones and it keeps the rest (B 8)
    recv = defaultdict(list)
    for bi, b in enumerate(births):
        b['loose'] = []
        for p in b['parents']:
            recv[p].append(bi)
    to_bar = []
    kept_by = {}
    for u in members:
        us = S.usable(u)
        lst = recv.get(u, [])
        a = act[u]
        if a == 'retire':
            assert not lst
            to_bar.extend(us)
            continue
        if a == 'wait':
            assert not lst
            continue
        if a.startswith('short-by'):
            assert len(lst) == n_off[u]
            for bi, d in zip(lst, us):
                births[bi]['loose'].append(d)
            kept_by[u] = us[len(lst):]
            continue
        assert len(lst) == len(us), (u, lst, us)
        for bi, d in zip(lst, us):
            births[bi]['loose'].append(d)
    # step 5': the taking rule, read on the structure at the start of the round, birth by birth
    take = law.take
    for b in births:
        b['cands'] = []
        b['takes'] = []
        if take is not None and (b['kind'] == 'offshoot' or take in ('MET', 'MET-SOLE')):
            c = candidates(S, law, b, R)
            b['cands'] = c
            if c:
                if take == 'MET':
                    b['takes'] = [c[0][0]] if law.choice == 'OLDEST' else [c[-1][0]]
                elif take == 'J-EACH-PART':
                    b['takes'] = [d for d, _ in c]
                elif len(c) == 1:          # a sole candidate (BD2 2.1)
                    b['takes'] = [c[0][0]]
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
        DR = build_roster(S, [(b['id'], 1, 0) for b in births] + persisting, 'demand', G)
        D = Counter(u for g in DR.groups for u in g)
    nfresh = 0
    for b in births:
        b['p'] = len(set(b['inputs']))
        b['D'] = D[b['id']]
        b['o'] = owe[b['parents'][0]] if b['kind'] == 'offshoot' else None
        b['f'] = 0 if b['implied'] else law.fresh(b['kind'], b['p'], b['D'], b['o'])
        nfresh += b['f']
    G('distinctions', S.n_distinctions + nfresh, 'fresh')
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
            'persisting': persisting, 'closing': any(b['implied'] for b in births), 'barred_now': to_bar,
            'kept_by': kept_by}


# --------------------------------------------------------------------------------------------------------------- run
class Run:
    """A start grown under one law (BD2 1.2): at most `rounds` rounds; a run stops after the first round that leaves
    more than `knot_bound` knots (that round is read); the guard stops a run without reading the round.

    A run may continue another from its structure after round s (`base`, `base_round`), with every usable loose
    distinction of the knots `bar` barred after round s (BD2 4.4; B 12): the barred runs and the lasting reruns."""

    def __init__(self, law, stars=None, rounds=ROUNDS, knot_bound=KNOT_BOUND, mult=1, base=None, base_round=None,
                 bar=(), keep_records=True):
        self.law = law
        self.G = Guard(mult)
        self.rounds_asked = rounds
        if base is None:
            S = from_stars(stars)
            self.snaps = [S.copy()]
            self.recs = []
            self.base_round = 0
        else:
            assert base_round <= base.rounds_read
            S = base.snaps[base_round].copy()
            self.snaps = list(base.snaps[:base_round])
            self.recs = list(base.recs[:base_round])
            self.base_round = base_round
            for u in bar:
                for d in S.usable(u):
                    S.barred[d] = True
            self.snaps.append(S.copy())
        self.bar = sorted(bar)
        self.stop = None
        self.guard = None
        # a structure already past the knot bound is not grown further (the base stopped there)
        if base is not None and S.n_knots > knot_bound:
            self.stop = 'knots'
        while self.stop is None and S.round < rounds:
            T = S.copy()
            try:
                rec = play_round(T, law, self.G)
            except GuardStop as g:
                self.stop = 'guard'
                self.guard = {'round': S.round + 1, 'what': g.what, 'where': g.where, 'value': g.value}
                break
            S = T
            self.recs.append(rec if keep_records else None)
            self.snaps.append(S.copy())
            if S.n_knots > knot_bound:
                self.stop = 'knots'
                break
        self.S = S
        self.rounds_read = S.round

    def peaks(self):
        return dict(self.G.peak)


def run_stars(stars, law, rounds=ROUNDS, knot_bound=KNOT_BOUND, mult=1):
    return Run(law, stars=stars, rounds=rounds, knot_bound=knot_bound, mult=mult)
