"""Engine of PARTS-MEET-AGAIN-20261124-001A: one complete round with taking, distinctions with any number of holders.

Written from the frozen text alone (the drafter's prototype was not seen):
  research/RING-IN-BALANCE-20261123-001/definitions.md        "the shared definitions" (cited SD line n)
  research/PARTS-MEET-AGAIN-20261124-001/definitions.md       "the definitions"        (cited D section.item)
  research/PARTS-MEET-AGAIN-20261124-001A/preregistration.md  "the pre-registration"
Readings taken where the text leaves a choice are numbered in deviations.md of this folder (cited R n).

A structure: knots with fixed place lists; every distinction has one or more holders (D 1.1); a loose distinction may be
barred.  Parents are written by each birth (D 1.4).  The round (D 2, SD lines 34-67):
  1 groups -> 2 owing/short -> 3 treatment -> 4 joins -> 5 offshoots/release -> 5' taking rule -> 6 demand -> 7 fresh
  (IMPLIED or LITERAL closing) -> 8 FILLERS; then names (D 2.1).
"""
from __future__ import annotations

import itertools
from collections import Counter, defaultdict

import networkx as nx

# ---------------------------------------------------------------------------------------------------------- the guard
GUARD = {'pairs': 20000, 'groups': 20000, 'births': 20000, 'distinctions': 400000, 'incidences': 2000000,
         'cliques': 200000}
KNOT_BOUND = 1500
ROUNDS = 8


class GuardStop(Exception):
    """The guard of the pre-registration ("Runs (frozen)", Bounds): the round is not read."""

    def __init__(self, what, value, where):
        super().__init__('%s %s > %s (%s)' % (what, value, GUARD[what], where))
        self.what, self.value, self.where = what, value, where


def _guard(what, value, where):
    if value > GUARD[what]:
        raise GuardStop(what, value, where)


# ------------------------------------------------------------------------------------------------------------- laws
TREATMENTS = ('STALL', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT', 'CANCEL-RETIRE', 'SHORT-TAKES')
TAKES = (None, 'Q', 'CARRY', 'MET', 'STEPS-1', 'STEPS-2', 'UP-TO-1', 'UP-TO-2', 'FIRST')
JOINABLE = ('MET', 'RECORD-2', 'RECORD-3', 'ALL')
CHOICES = ('OLDEST', 'NEWEST', 'IN-TURN', 'BY-COUNT', 'BY-RECEIVED')


class Law:
    """A knot law, a ration, a treatment, a release rule, extras, a taking rule with its choice, the joinable relation,
    the closing, the late start and the swaps.  Gate-only options: group_order ('study' = D 2.1: groups of three or
    more first, then pairs; 'lex' = the ring engine's one lexicographic list) and loose_order ('asc' = D 2.1; 'desc' =
    the rule-R/Q engines' "last listed first")."""

    FIELDS = ('ration', 'treatment', 'release', 'no_offshoot', 'fillers', 'knot_law', 'closing', 'take', 'joinable',
              'choice', 'late', 'base_treatment', 'order_reversed', 'demand_before_takes', 'fresh_by_parents',
              'group_order', 'loose_order', 'carry_filter')

    def __init__(self, ration='FLOOR1', treatment='CANCEL-RETIRE', release='RELEASE', no_offshoot=False,
                 fillers=False, knot_law='nae', closing='IMPLIED', take=None, joinable='MET', choice='OLDEST',
                 late=None, base_treatment=None, order_reversed=False, demand_before_takes=False,
                 fresh_by_parents=False, group_order='study', loose_order='asc', carry_filter=False):
        assert treatment in TREATMENTS, treatment
        assert release in ('RELEASE', 'HOLD')
        assert knot_law in ('nae', 'parity')
        assert closing in ('IMPLIED', 'LITERAL')
        assert take in TAKES, take
        assert joinable in JOINABLE
        assert choice in CHOICES + ('ALL-CHOICES',)
        assert group_order in ('study', 'lex') and loose_order in ('asc', 'desc')
        if late is not None:
            assert take in ('Q',) or treatment == 'SHORT-TAKES', 'the late start is defined for Q and SHORT-TAKES'
            if treatment == 'SHORT-TAKES':
                assert base_treatment in TREATMENTS and base_treatment != 'SHORT-TAKES'
        self.ration, self.treatment, self.release = ration, treatment, release
        self.no_offshoot, self.fillers, self.knot_law, self.closing = bool(no_offshoot), bool(fillers), knot_law, closing
        self.take, self.joinable, self.choice, self.late, self.base_treatment = take, joinable, choice, late, base_treatment
        self.order_reversed, self.demand_before_takes = bool(order_reversed), bool(demand_before_takes)
        self.fresh_by_parents, self.group_order, self.loose_order = bool(fresh_by_parents), group_order, loose_order
        self.carry_filter = bool(carry_filter)   # replay only (R 10): CARRY takes the oldest not already taken
        self.fresh_count(1, 1)   # validates the ration

    def key(self):
        return tuple(getattr(self, f) for f in self.FIELDS)

    def __eq__(self, o):
        return isinstance(o, Law) and self.key() == o.key()

    def __hash__(self):
        return hash(self.key())

    def replace(self, **kw):
        d = {f: getattr(self, f) for f in self.FIELDS}
        d.update(kw)
        return Law(**d)

    def to_dict(self):
        return {f: getattr(self, f) for f in self.FIELDS}

    def treatment_at(self, rnd):
        if self.treatment == 'SHORT-TAKES' and self.late is not None and rnd <= self.late:
            return self.base_treatment
        return self.treatment

    def take_at(self, rnd):
        if self.take is not None and self.late is not None and rnd <= self.late:
            return None
        return self.take

    # SD step 7 and D 2.7
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
        raise ValueError('unknown ration %r' % r)

    def every_birth_fresh(self):
        """Whether every birth receives a fresh distinction (D 7: ORD, CAP-k, FLOOR1, RATION-k under not-all-equal)."""
        if self.knot_law == 'parity':
            return False
        r = self.ration
        return r in ('ORD', 'FLOOR1') or r.startswith('CAP-') or (r.startswith('RATION-') and int(r[7:]) >= 1)

    def name(self):
        bits = [self.ration, self.treatment if self.late is None or self.treatment != 'SHORT-TAKES'
                else 'SHORT-TAKES<-%s' % self.base_treatment, self.release]
        if self.no_offshoot:
            bits.append('NO-OFFSHOOT')
        if self.fillers:
            bits.append('FILLERS')
        if self.take:
            bits.append('%s(%s)' % (self.take, self.choice))
        elif self.treatment == 'SHORT-TAKES':
            bits.append('choice=%s' % self.choice)
        if self.joinable != 'MET':
            bits.append(self.joinable)
        if self.late is not None:
            bits.append('late%d' % self.late)
        for f, lab in (('order_reversed', 'order-reversed'), ('demand_before_takes', 'demand-before-takes'),
                       ('fresh_by_parents', 'fresh-by-parents')):
            if getattr(self, f):
                bits.append(lab)
        if self.closing != 'IMPLIED':
            bits.append(self.closing)
        if self.group_order != 'study':
            bits.append('groups-' + self.group_order)
        if self.loose_order != 'asc':
            bits.append('loose-' + self.loose_order)
        if self.carry_filter:
            bits.append('carry-filter')
        return '/'.join(bits) + '/' + self.knot_law

    def __repr__(self):
        return 'Law(%s)' % self.name()


# ----------------------------------------------------------------------------------------------------------- structure
class St:
    """A structure: knots and distinctions; any number of holders; parents written by each birth."""

    __slots__ = ('places', 'holders', 'barred', 'parents', 'made', 'kind', 'removed', 'round', 'labels', 'n_start',
                 'cand', 'span', '_lev')

    def __init__(self):
        self.places, self.holders, self.barred = [], [], []
        self.parents, self.made, self.kind = [], [], []
        self.removed = set()
        self.round = 0
        self.labels = None
        self.n_start = 0
        self.cand = set()      # knots that may hold a usable loose distinction (members are among them)
        self.span = None       # GF(2) echelon basis of the knots' rows {leading bit: row}
        self._lev = {}         # cache: (knot, k) -> frozenset of knots exactly k parent steps above

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
        T.removed = set(self.removed)
        T.round = self.round
        T.labels = self.labels
        T.n_start = self.n_start
        T.cand = set(self.cand)
        T.span = dict(self.span) if self.span is not None else None
        # entries for knots that exist now stay valid (parents are fixed); a branch adds its own later knots
        T._lev = dict(self._lev)
        return T

    def knots(self):
        return [u for u in range(len(self.places)) if u not in self.removed]

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

    def eligible(self, u):
        """u's distinctions with two or more holders (read at the start of a round: D 2.2)."""
        H = self.holders
        return [d for d in self.places[u] if len(H[d]) >= 2]

    def meets(self, u):
        out = set()
        H = self.holders
        for d in self.places[u]:
            out.update(H[d])
        out.discard(u)
        return out

    def level(self, u, k):
        """Knots reached from u by a chain of exactly k parent steps (R 7)."""
        key = (u, k)
        v = self._lev.get(key)
        if v is None:
            if k == 0:
                v = frozenset((u,))
            else:
                prev = self.level(u, k - 1)
                acc = set()
                for x in prev:
                    acc.update(self.parents[x])
                v = frozenset(acc)
            self._lev[key] = v
        return v

    def ancestors(self, u):
        """All recorded ancestors of u (one or more parent steps)."""
        out, stack = set(), list(self.parents[u])
        while stack:
            x = stack.pop()
            if x not in out:
                out.add(x)
                stack.extend(self.parents[x])
        return out

    def row(self, u):
        r = 0
        for d in self.places[u]:
            r |= 1 << d
        return r

    def check(self):
        seen = defaultdict(list)
        for u, P in enumerate(self.places):
            if u in self.removed:
                assert not P
                continue
            assert len(set(P)) == len(P), 'knot %d lists a distinction twice' % u
            for d in P:
                seen[d].append(u)
        for d, hs in enumerate(self.holders):
            assert sorted(hs) == sorted(seen.get(d, [])), 'holders of %d inconsistent' % d
        return True

    def to_dict(self):
        return {'round': self.round, 'places': self.places, 'parents': [list(p) for p in self.parents],
                'made': self.made, 'barred': [i for i, b in enumerate(self.barred) if b],
                'removed': sorted(self.removed)}


def span_insert(span, v):
    while v:
        p = v.bit_length() - 1
        b = span.get(p)
        if b is None:
            span[p] = v
            return True
        v ^= b
    return False


def span_contains(span, v):
    while v:
        b = span.get(v.bit_length() - 1)
        if b is None:
            return False
        v ^= b
    return True


def build_span(S):
    sp = {}
    for u in S.knots():
        span_insert(sp, S.row(u))
    return sp


def from_stars(stars, reverse_names=False):
    """A start from its stars (D 2.1: distinctions named by the stars' labels in increasing order; the swap "names
    reversed" names them in decreasing order of label)."""
    labels = sorted({d for star in stars for d in star})
    n = len(labels)
    if reverse_names:
        index = {lab: n - 1 - i for i, lab in enumerate(labels)}
        names = list(reversed(labels))
    else:
        index = {lab: i for i, lab in enumerate(labels)}
        names = labels
    S = St()
    S.labels = names
    S.holders = [[] for _ in range(n)]
    S.barred = [False] * n
    for u, star in enumerate(stars):
        assert len(set(star)) == len(star)
        P = [index[d] for d in star]
        S.places.append(P)
        for d in P:
            S.holders[d].append(u)
        S.parents.append(())
        S.made.append(0)
        S.kind.append('start')
    S.n_start = len(stars)
    S.cand = set(range(len(stars)))
    S.span = build_span(S)
    S.check()
    return S


# ------------------------------------------------------------------------------------------------------- named starts
def ring_stars(n, a):
    return [[(i - 1) % n, i] + [n + i * a + j for j in range(a)] for i in range(n)]


STARS = {
    'Ring(5,3)': [[4, 0, 5, 6, 7], [0, 1, 8, 9, 10], [1, 2, 11, 12, 13], [2, 3, 14, 15, 16], [3, 4, 17, 18, 19]],
    'Ring(7,3)': [[6, 0, 7, 8, 9], [0, 1, 10, 11, 12], [1, 2, 13, 14, 15], [2, 3, 16, 17, 18], [3, 4, 19, 20, 21],
                  [4, 5, 22, 23, 24], [5, 6, 25, 26, 27]],
    'D2(5,3)': [[20, 21, 22, 0, 1, 18, 19], [23, 24, 25, 4, 5, 2, 3], [26, 27, 28, 8, 9, 6, 7],
                [29, 30, 31, 12, 13, 10, 11], [32, 33, 34, 16, 17, 14, 15], [0, 1, 2, 3], [4, 5, 6, 7],
                [8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18, 19]],
    'two-knot': [[0, 1, 2], [0, 3, 4]],
    'three-knot': [[0, 1, 2, 3], [0, 1, 4, 5], [2, 3, 6, 7]],
    'three-knot-larger': [[0, 1, 2, 3], [0, 1, 4, 5], [2, 3, 6, 7, 8]],
    'generator7': [[0, 1, 2, 9, 10, 11], [0, 1, 3], [4, 5, 12, 13, 14], [6, 7, 15, 16, 17], [2, 3, 4, 6, 18, 19, 20],
                   [7, 8, 21, 22], [5, 8, 23, 24]],
}
RING_STARTS = ('Ring(5,3)', 'Ring(7,3)', 'D2(5,3)')
COPIER_STARTS = ('two-knot', 'three-knot', 'Ring(5,3)')
LATE_S0 = {'Ring(5,3)': 2, 'Ring(7,3)': 2, 'D2(5,3)': 2, 'three-knot': 2, 'three-knot-larger': 2, 'two-knot': 3}


def start(name, reverse_names=False):
    return from_stars(STARS[name], reverse_names=reverse_names)


# --------------------------------------------------------------------------------------------------------- the roster
class Roster:
    """Members, met sets (D 1.3: a knot is not in its own met set), the joinable relation, groups, parts, classes."""

    __slots__ = ('members', 'mset', 'h', 'k', 'maxsets', 'commons', 'adj', 'groups', 'parts', 'part_of', 'incid',
                 'n_pairs', 'meets_member', '_classes', 'S', 'n_cliques')

    def __init__(self):
        pass


def met_sets(S, members, early_pairs=False):
    """{frozenset(met set): [common knots]} for every knot whose met set has at least two members; and incidences."""
    mset = set(members)
    H = S.holders
    inc = 0
    for u in members:
        for d in S.places[u]:
            inc += len(H[d]) - 1
    _guard('incidences', inc, 'met sets')
    if early_pairs:
        # the members holding one distinction all lie in the met set of each of its holders but themselves, so the
        # joinable pairs number at least C(c - 1, 2), c the most members holding one distinction (deviations 43)
        cnt = Counter()
        for u in members:
            for d in S.places[u]:
                cnt[d] += 1
        if cnt:
            c = max(cnt.values()) - 1
            _guard('pairs', c * (c - 1) // 2, 'met sets')
    raw = defaultdict(set)
    meets_member = set()
    for u in members:
        for d in S.places[u]:
            for w in H[d]:
                if w != u:
                    raw[w].add(u)
                    if w in mset:
                        meets_member.add(u)
    sc = defaultdict(list)
    for w, ms in raw.items():
        if len(ms) >= 2:
            sc[frozenset(ms)].append(w)
    return sc, inc, meets_member


def maximal_sets(sc):
    items = sorted(sc.items(), key=lambda kv: (-len(kv[0]), sorted(kv[0])))
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


def record_sets(S, members, k):
    """RECORD-k (D 3.3): for each knot g, the members having g at most k parent steps above them (sets of >= 2)."""
    by_g = defaultdict(set)
    for u in members:
        for j in range(1, k + 1):
            for g in S.level(u, j):
                by_g[g].add(u)
    return [frozenset(v) for v in by_g.values() if len(v) >= 2]


def groups_from(members, maxsets, adj, order='study', where=''):
    """SD step 1 on a joinable graph `adj`: maximal cliques of >= 3 contained in no single met set; then pairs in none.
    Ordered as D 2.1 ('study') or the ring engine's single lexicographic list ('lex')."""
    by_member = defaultdict(list)
    for i, M in enumerate(maxsets):
        for x in M:
            by_member[x].append(i)
    G = nx.Graph()
    G.add_nodes_from(members)
    for a, nb in adj.items():
        for b in nb:
            if a < b:
                G.add_edge(a, b)
    big = []
    nclq = 0
    for Q in nx.find_cliques(G):
        nclq += 1
        if nclq > GUARD['cliques']:
            _guard('cliques', nclq, where)
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
    if order == 'lex':
        out = sorted(big + pairs)
    else:
        out = sorted(big) + sorted(pairs)
    _guard('groups', len(out), where)
    return out, nclq


def build_roster(S, members_hk, law, mask=None, where='roster'):
    """The roster of the given members [(u, h, k)], met sets read from S; joinable per the law; mask removes pairs."""
    R = Roster()
    R.S = S
    R.members = tuple(sorted(u for u, _, _ in members_hk))
    R.mset = frozenset(R.members)
    R.h = {u: h for u, h, _ in members_hk}
    R.k = {u: k for u, _, k in members_hk}
    sc, inc, meets_member = met_sets(S, R.members, early_pairs=(mask is None and law.joinable != 'ALL'))
    R.incid = inc
    R.meets_member = meets_member
    if mask is None and law.joinable != 'ALL' and sc:
        # every pair inside one met set is joinable, so the joinable pairs number at least C(m, 2) for the largest met
        # set: the guard on candidate pairs is decided here when it applies, before the costly maximal sets
        # (deviations 43; the stop is the one the later check would make)
        m = max(len(M) for M in sc)
        _guard('pairs', m * (m - 1) // 2, where)
    R.maxsets, R.commons = maximal_sets(sc)
    adj = defaultdict(set)
    if law.joinable == 'ALL':
        _guard('pairs', len(R.members) * (len(R.members) - 1) // 2, where)
        for a in R.members:
            adj[a] = set(R.members) - {a}
    else:
        npairs = 0
        for M in R.maxsets:
            L = sorted(M)
            for i, a in enumerate(L):
                for b in L[i + 1:]:
                    if b not in adj[a]:
                        adj[a].add(b)
                        adj[b].add(a)
                        npairs += 1
            _guard('pairs', npairs, where)
        if law.joinable.startswith('RECORD-'):
            for M in record_sets(S, R.members, int(law.joinable[7:])):
                L = sorted(M)
                for i, a in enumerate(L):
                    for b in L[i + 1:]:
                        if b not in adj[a]:
                            adj[a].add(b)
                            adj[b].add(a)
                            npairs += 1
                _guard('pairs', npairs, where)
    if mask is not None:
        for a in list(adj):
            for b in list(adj[a]):
                if mask.blocked(a, b):
                    adj[a].discard(b)
    R.adj = adj
    R.n_pairs = sum(len(v) for v in adj.values()) // 2
    _guard('pairs', R.n_pairs, where)
    R.groups, R.n_cliques = groups_from(R.members, R.maxsets, adj, law.group_order, where)
    # parts: components of joinable
    parent = {u: u for u in R.members}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, nb in adj.items():
        for b in nb:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra
    comp = defaultdict(list)
    for u in R.members:
        comp[find(u)].append(u)
    R.parts = sorted(tuple(sorted(c)) for c in comp.values())
    R.part_of = {}
    for i, P in enumerate(R.parts):
        for u in P:
            R.part_of[u] = i
    R._classes = None
    return R


def roster_classes(R):
    """D 1.6: link two parts when a member of one holds a distinction a member of the other holds; classes are the
    connected sets of parts.  Returns class index per part."""
    if R._classes is not None:
        return R._classes
    S = R.S
    n = len(R.parts)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    by_d = {}
    for u in R.members:
        pu = R.part_of[u]
        for d in S.places[u]:
            q = by_d.get(d)
            if q is None:
                by_d[d] = pu
            else:
                ra, rb = find(q), find(pu)
                if ra != rb:
                    parent[rb] = ra
    roots = {}
    cls = []
    for i in range(n):
        r = find(i)
        if r not in roots:
            roots[r] = len(roots)
        cls.append(roots[r])
    R._classes = cls
    return cls


def live_members(S):
    out = []
    keep = set()
    for u in sorted(S.cand):
        if u in S.removed:
            continue
        h, k = S.hk(u)
        if h > 0:
            out.append((u, h, k))
            keep.add(u)
    S.cand = keep
    return out


def roster_of(S, law, mask=None):
    return build_roster(S, live_members(S), law, mask, 'roster')


# --------------------------------------------------------------------------------------------------------- the masks
class Mask:
    """D 5.6.  mode 'XY': no member of side A (X and its descendants) is joinable with a member of side B (Y and its
    descendants).  mode 'ISO': no member of side B is joinable with any member outside B.  A new knot is on a side when
    one of its parents is (D 4.2)."""

    def __init__(self, mode, A, B):
        self.mode, self.A, self.B = mode, set(A), set(B)

    def blocked(self, a, b):
        A, B = self.A, self.B
        if self.mode == 'XY':
            return (a in A and b in B) or (a in B and b in A)
        return (a in B) != (b in B)

    def extend(self, new):
        """new: [(knot, parents)]."""
        for x, ps in new:
            if any(p in self.A for p in ps):
                self.A.add(x)
            if any(p in self.B for p in ps):
                self.B.add(x)

    def copy(self):
        return Mask(self.mode, self.A, self.B)


# --------------------------------------------------------------------------------------------------------- one round
def _pick(cands, choice, S, parent_for_count, i_turn):
    """The choice among sorted candidates (D 2.5)."""
    n = len(cands)
    if choice == 'OLDEST':
        return cands[0]
    if choice == 'NEWEST':
        return cands[-1]
    if choice == 'IN-TURN':
        return cands[i_turn % n]
    if choice == 'BY-COUNT':
        return cands[len(S.places[parent_for_count]) % n]
    if choice == 'BY-RECEIVED':
        return cands[(len(S.places[parent_for_count]) - len(S.parents[parent_for_count])) % n]
    raise ValueError(choice)


class ResidualStall(Exception):
    pass


def take_candidates(S, take, b, members_parts=None):
    """Candidates of the taking rule for birth b (read on the structure at the start of the round), sorted by name;
    returns a list of candidate lists (one per take; CARRY: one per parent)."""
    H = S.holders
    ps = b['parents']
    have = set(b['inputs'])
    if take == 'CARRY':
        out = []
        for p in ps:
            if S.parents[p]:
                pp = set(S.parents[p])
                c = sorted(d for d in S.places[p] if len(H[d]) >= 2 and any(w in pp for w in H[d]))
            else:
                c = sorted(d for d in S.places[p] if len(H[d]) >= 2)
            out.append(c)
        return out
    if b['kind'] == 'join':
        if take != 'MET':
            return []
        common = None
        for p in ps:
            m = S.meets(p)
            common = m if common is None else (common & m)
        common = (common or set()) - set(ps)
        held = set()
        for p in ps:
            held.update(S.places[p])
        c = set()
        for w in common:
            for d in S.places[w]:
                if len(H[d]) >= 2 and d not in held:
                    c.add(d)
        return [sorted(c - have)]
    p = ps[0]
    own = set(S.places[p])
    if take == 'Q':
        return [sorted(d for d in S.places[p] if len(H[d]) >= 2 and d not in have)]
    if take == 'MET':
        c = set()
        for w in S.meets(p):
            for d in S.places[w]:
                if len(H[d]) >= 2 and d not in own:
                    c.add(d)
        return [sorted(c - have)]
    if take.startswith('STEPS-') or take.startswith('UP-TO-'):
        k = int(take.split('-')[-1])
        levels = [k] if take.startswith('STEPS-') else list(range(1, k + 1))
        anc = set()
        for j in levels:
            anc |= S.level(p, j)
        c = set()
        for g in anc:
            for d in S.places[g]:
                if len(H[d]) >= 2 and d not in own:
                    c.add(d)
        return [sorted(c - have)]
    if take == 'FIRST':
        # nearest recorded ancestors (fewest parent steps) whose member descendants lie in two or more parts (R 9)
        desc_parts = members_parts
        seen = {p}
        frontier = {p}
        while frontier:
            nxt = set()
            for x in frontier:
                for y in S.parents[x]:
                    if y not in seen:
                        seen.add(y)
                        nxt.add(y)
            frontier = nxt
            G = [g for g in frontier if len(desc_parts.get(g, ())) >= 2]
            if G:
                c = set()
                for g in G:
                    for d in S.places[g]:
                        if len(H[d]) >= 2 and d not in own:
                            c.add(d)
                return [sorted(c - have)]
        return [[]]
    raise ValueError(take)


def round_step(S, law, ctx=None):
    """One complete round applied to S in place.  Returns the round's record.  Raises GuardStop (nothing changed).
    ctx (optional): {'mask': Mask, 'choice_of': f(birth)->choice name or None, 'chooser': f(key, cands)->d}."""
    ctx = ctx or {}
    mask = ctx.get('mask')
    choice_of = ctx.get('choice_of')
    chooser = ctx.get('chooser')
    rnd = S.round + 1
    treatment = law.treatment_at(rnd)
    take = law.take_at(rnd)
    mem = live_members(S)
    R = build_roster(S, mem, law, mask, 'roster r%d' % rnd)
    members = R.members
    h = R.h
    groups = R.groups
    owe = Counter(u for g in groups for u in g)
    short = [u for u in members if owe[u] > h[u]]
    shortset = set(short)
    rec = {'round': rnd, 'members_before': len(members), 'groups': [list(g) for g in groups], 'short': short,
           'cancelled': [], 'births': [], 'waiting': [], 'retired': [], 'held': {}, 'stalled': False,
           'residual_stall': False, 'closing': False, 'treatment': treatment, 'take': take, 'owe': dict(owe),
           'n_pairs': R.n_pairs, 'n_cliques': R.n_cliques, 'incidences': R.incid}
    if treatment == 'STALL' and short:
        rec['stalled'] = True
        S.round = rnd
        _tail(S, rec)
        return rec
    if treatment == 'SHORT-TAKES':
        kept, cancelled = list(groups), []
    else:
        kept = [g for g in groups if not shortset.intersection(g)]
        cancelled = [g for g in groups if shortset.intersection(g)]
    rec['cancelled'] = [list(g) for g in cancelled]
    kept_cnt = Counter(u for g in kept for u in g)
    canc_cnt = Counter(u for g in cancelled for u in g)
    births = [{'kind': 'join', 'parents': tuple(g)} for g in kept]
    _guard('births', len(births), 'joins r%d' % rnd)
    n_off = {}
    n_keep = {}
    to_bar_n = {}       # member -> number of its usable distinctions (after joins and keeps) to bar
    for u in members:
        if u in shortset:
            if treatment == 'CANCEL-OFFSHOOT':
                n_off[u] = h[u]
            elif treatment == 'CANCEL-WAIT':
                rec['waiting'].append(u)
            elif treatment == 'CANCEL-RETIRE':
                rec['retired'].append(u)
                to_bar_n[u] = h[u]
            elif treatment == 'SHORT-TAKES':
                pass
            else:
                raise AssertionError(treatment)
        else:
            rem = h[u] - kept_cnt[u]
            nh = canc_cnt[u] if law.release == 'HOLD' else 0
            assert rem >= nh
            if nh:
                n_keep[u] = nh
                rec['held'][u] = nh
            if law.no_offshoot:
                to_bar_n[u] = rem - nh
            else:
                n_off[u] = rem - nh
    for u in members:
        for i in range(n_off.get(u, 0)):
            births.append({'kind': 'offshoot', 'parents': (u,), 'off_index': i})
    _guard('births', len(births), 'births r%d' % rnd)
    if law.order_reversed:
        births.reverse()
    # hand out the usable loose distinctions (D 2.1); receivers per member in birth order, KEEP slots between (R 4)
    recv = defaultdict(list)
    for bi, b in enumerate(births):
        for p in b['parents']:
            recv[p].append(bi)
    keep_d = {}
    bar_d = []
    for b in births:
        b['inputs'] = []
        b['loose'] = []
        b['given_shared'] = []
        b['rule_takes'] = []
    pending_shared = []   # (birth index, short member)
    for u in members:
        us = S.usable(u)
        if law.loose_order == 'desc':
            us = us[::-1]
        lst = recv.get(u, [])                      # u's births in the (possibly reversed) birth order
        fwd_births = list(reversed(lst)) if law.order_reversed else lst
        fwd = [('b', bi) for bi in fwd_births if births[bi]['kind'] == 'join'] + \
              [('keep', None)] * n_keep.get(u, 0) + \
              [('b', bi) for bi in fwd_births if births[bi]['kind'] == 'offshoot']
        seq = list(reversed(fwd)) if law.order_reversed else fwd
        seq += [('bar', None)] * to_bar_n.get(u, 0)
        di = 0
        for kind, bi in seq:
            if di < len(us):
                d = us[di]
                di += 1
                if kind == 'b':
                    births[bi]['loose'].append(d)
                    births[bi]['inputs'].append(d)
                elif kind == 'keep':
                    keep_d.setdefault(u, []).append(d)
                else:
                    bar_d.append(d)
            else:
                if kind == 'b':
                    assert u in shortset and treatment == 'SHORT-TAKES', 'a member ran out of distinctions'
                    pending_shared.append((bi, u))
                else:
                    raise AssertionError('nothing left to keep or bar')
        if di < len(us) and not (u in shortset and treatment == 'CANCEL-WAIT'):
            raise AssertionError('member %d left %d distinctions unassigned' % (u, len(us) - di))
    # SHORT-TAKES (D 2.3): further births of a short member take an allowed eligible distinction it holds
    if pending_shared:
        pending_shared.sort()
        given = defaultdict(set)
        for bi, u in pending_shared:
            b = births[bi]
            others = [q for q in b['parents'] if q != u]
            allowed = [d for d in sorted(S.eligible(u)) if d not in given[u]
                       and not any(q in others for q in S.holders[d])]
            if not allowed:
                rec['residual_stall'] = True
                rec['residual_member'] = u
                S.round = rnd
                _tail(S, rec)
                return rec
            ch = law.choice
            if choice_of is not None:
                ch = choice_of(S, b) or ch
            if chooser is not None:
                d = chooser(('short', bi, u), allowed)
            else:
                if ch == 'IN-TURN':
                    raise ValueError('IN-TURN is not used with SHORT-TAKES')
                d = _pick(allowed, ch, S, u, 0)
            given[u].add(d)
            b['given_shared'].append(d)
            b['inputs'].append(d)
    # step 5': the taking rule, read on the structure at the start of the round, birth by birth in birth order
    if take is not None:
        mparts = None
        if take == 'FIRST':
            mparts = defaultdict(set)
            for m in members:
                pm_ = R.part_of[m]
                for g in S.ancestors(m):
                    mparts[g].add(pm_)
        off_seen = Counter()
        for bi, b in enumerate(births):
            i_turn = 0
            if b['kind'] == 'offshoot':
                i_turn = off_seen[b['parents'][0]]
                off_seen[b['parents'][0]] += 1
            if b['kind'] == 'join' and take not in ('MET', 'CARRY'):
                continue
            ch = law.choice
            if choice_of is not None:
                ch = choice_of(S, b) or ch
            clists = take_candidates(S, take, b, mparts)
            for ci, cands in enumerate(clists):
                if take == 'CARRY':
                    if law.carry_filter:
                        cands = [d for d in cands if d not in b['inputs']]
                    if cands:
                        d = cands[0]
                        if d not in b['inputs']:
                            b['rule_takes'].append(d)
                            b['inputs'].append(d)
                    continue
                cands = [d for d in cands if d not in b['inputs']]
                if not cands:
                    continue
                if chooser is not None and not (b['kind'] == 'join' and ch == 'IN-TURN'):
                    d = chooser(('take', bi), cands)
                else:
                    c2 = ch
                    if b['kind'] == 'join' and ch == 'IN-TURN':
                        c2 = 'OLDEST'
                    pc = b['parents'][0]
                    d = _pick(cands, c2, S, pc, i_turn)
                b['rule_takes'].append(d)
                b['inputs'].append(d)
    # names of the new knots: birth order
    base = S.n_knots
    for bi, b in enumerate(births):
        b['id'] = base + bi
        assert len(set(b['inputs'])) == len(b['inputs'])
    # shared at the start of the round, the closing test (against the structure before the round), loose total
    total_loose = sum(1 for d in range(S.n_distinctions) if len(S.holders[d]) == 1)
    for b in births:
        b['shared_at_start'] = sorted(d for d in b['inputs'] if len(S.holders[d]) >= 2)
        if law.knot_law == 'parity' and law.closing == 'IMPLIED':
            v = 0
            for d in b['inputs']:
                v |= 1 << d
            b['implied'] = span_contains(S.span, v)
        else:
            b['implied'] = False
    literal_close = (law.knot_law == 'parity' and law.closing == 'LITERAL' and len(births) == 1
                     and len(births[0]['inputs']) == total_loose)
    # barring (retire, NO-OFFSHOOT)
    for d in bar_d:
        S.barred[d] = True
    # make the new knots; the rule takes are added before the demand step unless the swap says otherwise
    for b in births:
        x = b['id']
        first = b['loose'] + b['given_shared']
        later = b['rule_takes']
        ins = first if law.demand_before_takes else first + later
        S.places.append(list(ins))
        S.parents.append(tuple(sorted(b['parents'])))
        S.made.append(rnd)
        S.kind.append(b['kind'])
        for d in ins:
            S.holders[d].append(x)
        S.cand.add(x)
    persisting = []
    for u in members:
        hu, ku = S.hk(u)
        if hu > 0:
            persisting.append((u, hu, ku))
    # step 6: demand
    dmembers = [(b['id'], 1, 0) for b in births] + persisting
    if mask is not None:
        mask.extend([(b['id'], b['parents']) for b in births])
    if births:
        DR = build_roster(S, dmembers, law, mask, 'demand r%d' % rnd)
        D = Counter(u for g in DR.groups for u in g)
        rec['demand_groups'] = len(DR.groups)
    else:
        D = Counter()
    if law.demand_before_takes:
        for b in births:
            x = b['id']
            for d in b['rule_takes']:
                S.places[x].append(d)
                S.holders[d].append(x)
    # step 7, 8: fresh distinctions, closing, FILLERS
    nfresh = 0
    for b in births:
        p = len(b['parents']) if law.fresh_by_parents else len(set(b['inputs']))
        Dx = D[b['id']]
        if b['implied'] or literal_close:
            f = 0
        else:
            f = law.fresh_count(p, Dx)
        fu = min(f, Dx) if law.fillers else f
        b.update({'D': Dx, 'p': p, 'f': f, 'usable': fu, 'barred': f - fu})
        nfresh += f
    _guard('distinctions', S.n_distinctions + nfresh, 'fresh r%d' % rnd)
    rec['closing'] = bool(literal_close or any(b['implied'] for b in births))
    for b in births:
        x = b['id']
        fr = []
        for i in range(b['f']):
            d = len(S.holders)
            S.holders.append([x])
            S.barred.append(i >= b['usable'])
            S.places[x].append(d)
            fr.append(d)
        b['fresh'] = fr
    for b in births:
        span_insert(S.span, S.row(b['id']))
    for b in births:
        rec['births'].append({'id': b['id'], 'kind': b['kind'], 'parents': list(b['parents']),
                              'inputs': list(b['inputs']), 'loose': b['loose'], 'given_shared': b['given_shared'],
                              'rule_takes': b['rule_takes'], 'shared_at_start': b['shared_at_start'],
                              'D': b['D'], 'p': b['p'], 'f': b['f'], 'usable': b['usable'], 'barred': b['barred'],
                              'implied': b['implied'], 'fresh': b['fresh']})
    rec['kept_by_hold'] = {u: v for u, v in keep_d.items()}
    S.round = rnd
    _tail(S, rec)
    return rec


def _tail(S, rec):
    nb = len(rec['births'])
    members_after = any(S.hk(u)[0] > 0 for u in S.cand if u not in S.removed)
    rec.update({'n_births': nb, 'n_joins': sum(1 for b in rec['births'] if b['kind'] == 'join'),
                'n_offshoots': sum(1 for b in rec['births'] if b['kind'] == 'offshoot'),
                'n_taking': sum(1 for b in rec['births'] if b['rule_takes'] or b['given_shared']),
                'n_takes': sum(len(b['rule_takes']) + len(b['given_shared']) for b in rec['births']),
                'jammed': bool(members_after and nb == 0), 'stopped': not members_after,
                'n_knots': S.n_knots - len(S.removed), 'n_distinctions': S.n_distinctions})


# --------------------------------------------------------------------------------------------------------------- runs
class Run:
    """One start grown under one law: the bounds (8 rounds; stop after the first round leaving more than 1,500 knots),
    the guard, a residual stall stops the run (D 2.3).  Keeps the structure after every round (snapshots)."""

    def __init__(self, S0, law, rounds=ROUNDS, knot_bound=KNOT_BOUND, ctx=None, keep=True, from_round=None,
                 records=None, snapshots=None, on_round=None):
        self.law = law
        self.rounds_asked = rounds
        self.knot_bound = knot_bound
        self.ctx = ctx or {}
        S = S0.copy()
        # a comparison run starts at round S0.round with run A's earlier structures and records as a prefix
        self.snap = (list(snapshots) if snapshots is not None else []) + [S.copy()]
        self.records = list(records) if records is not None else []
        assert len(self.snap) == S.round + 1 and len(self.records) == S.round
        self.stop = None            # None, 'knots', 'guard', 'residual_stall'
        self.guard = None
        self.on_round = on_round
        while self.stop is None and S.round < rounds:
            try:
                T = S.copy()
                rec = round_step(T, law, self.ctx)
            except GuardStop as g:
                self.stop = 'guard'
                self.guard = {'round': S.round + 1, 'what': g.what, 'value': g.value, 'where': g.where}
                break
            S = T
            self.records.append(rec)
            if keep:
                self.snap.append(S.copy())
            if on_round is not None:
                on_round(self, S, rec)
            if rec['residual_stall']:
                self.stop = 'residual_stall'
                break
            if S.n_knots - len(S.removed) > knot_bound:
                self.stop = 'knots'
                break
        self.S = S
        self.rounds_done = S.round

    def state(self, t):
        return self.snap[t]

    def summary(self):
        return {'law': self.law.name(), 'rounds_done': self.rounds_done, 'stop': self.stop, 'guard': self.guard,
                'knots': self.S.n_knots - len(self.S.removed)}


def from_stars_any(stars):
    """A structure from stars with any number of holders per distinction (drawn test structures)."""
    return from_stars(stars)
