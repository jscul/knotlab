"""Engine of TIME-AS-FOLD-20261125-001A-E001: one complete round with taking (any number of holders).

Written from the frozen texts only (the drafter's prototype was not seen):
  SD  research/RING-IN-BALANCE-20261123-001/definitions.md     (cited by line)
  FD  research/PARTS-MEET-AGAIN-20261124-001/definitions.md     (cited by section)
  TD  research/TIME-AS-FOLD-20261125-001/definitions.md         (cited by section)
  PR  research/TIME-AS-FOLD-20261125-001A/preregistration.md
Readings where the texts leave a choice are numbered in deviations.md of this folder (cited "dev n").

A structure keeps, for every knot, its places (fixed at birth), parents (written by the birth), round made and kind;
for every distinction its holders in order of acquisition (holders never decrease, FD 1.1) and the round at which
it was barred (never unbarred).  Because nothing is ever removed, the structure after any earlier round is a view
of the final one: knots made by round t, holders made by round t, distinctions barred by round t (dev 3).

One round (SD lines 34-67, FD 2): 1 groups, 2 owing (short read once), 3 treatment, 4 joins, 5 offshoots and the
release rule, 5' the taking rule (read on the structure at the start of the round), names, 6 demand (after the takes
unless swapped), 7 fresh (distinct inputs unless swapped; IMPLIED under parity), 8 FILLERS; fresh names.
"""
from __future__ import annotations

import itertools
import time
from collections import Counter, defaultdict

import networkx as nx

NEVER = 1 << 30

# ------------------------------------------------------------------------------------------------------- the guard
GUARD = {'pairs': 20000, 'groups': 20000, 'births': 20000, 'distinctions': 400000, 'incidences': 2000000,
         'cliques': 200000}


class GuardStop(Exception):
    """TD 1.7: the guard cuts the run short without keeping the round."""

    def __init__(self, what, value, where):
        super().__init__('%s %s > %s (%s)' % (what, value, GUARD[what], where))
        self.what, self.value, self.where = what, value, where


class LimitReached(Exception):
    """TD 1.7: 600 seconds of process time for each run A and each test; the run or test is unfinished."""


class Clock:
    """Process-time limit (time.process_time, TD 1.7: process time, not wall time)."""

    def __init__(self, limit=600.0, used=0.0):
        self.limit = limit
        self.t0 = time.process_time() - used

    def used(self):
        return time.process_time() - self.t0

    def check(self):
        if self.limit is not None and time.process_time() - self.t0 > self.limit:
            raise LimitReached('limit of %.0f s of process time reached' % self.limit)


def _guard(what, value, where, on=True):
    if on and value > GUARD[what]:
        raise GuardStop(what, value, where)


# --------------------------------------------------------------------------------------------------------- laws
TREATMENTS = ('STALL', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT', 'CANCEL-RETIRE', 'SHORT-TAKES')
CHOICES = ('OLDEST', 'NEWEST', 'IN-TURN', 'BY-COUNT', 'BY-RECEIVED')

BASE_LAWS = {
    'RING-LAW': dict(ration='CAP-3', treatment='CANCEL-WAIT', fillers=False),
    'RING-LAW+FILLERS': dict(ration='CAP-3', treatment='CANCEL-WAIT', fillers=True),
    'COPY-LAW(RETIRE)': dict(ration='FLOOR1', treatment='CANCEL-RETIRE', fillers=False),
    'COPY-LAW(OFFSHOOT)': dict(ration='FLOOR1', treatment='CANCEL-OFFSHOOT', fillers=False),
    'COPY-LAW(WAIT)': dict(ration='FLOOR1', treatment='CANCEL-WAIT', fillers=False),
    'CAP-3(RETIRE)': dict(ration='CAP-3', treatment='CANCEL-RETIRE', fillers=False),
    'CAP-3(OFFSHOOT)': dict(ration='CAP-3', treatment='CANCEL-OFFSHOOT', fillers=False),
}
BASE_ORDER = tuple(BASE_LAWS)


def parse_take(take):
    """A taking rule id of rules.json -> (family, k, which births).

    family: None | 'Q' | 'MET' | 'STEPS' | 'UP-TO'; which: 'both' | 'offshoot' | 'join' (MET: clauses;
    STEPS: offshoots by the kind of their parent, TD 1.4)."""
    if take is None or take == 'none':
        return None, 0, None
    base, _, which = take.partition(':')
    which = which or 'both'
    if base == 'Q':
        return 'Q', 0, which
    if base == 'MET':
        return 'MET', 0, which
    if base.startswith('STEPS-'):
        return 'STEPS', int(base[6:]), which
    if base.startswith('UP-TO-'):
        return 'UP-TO', int(base[6:]), which
    raise ValueError('unknown taking rule %r' % take)


class Law:
    FIELDS = ('ration', 'treatment', 'release', 'no_offshoot', 'fillers', 'knot_law', 'take', 'choice', 'late',
              'base_treatment', 'order_reversed', 'demand_before_takes', 'fresh_by_parents')

    def __init__(self, ration='FLOOR1', treatment='CANCEL-RETIRE', release='RELEASE', no_offshoot=False,
                 fillers=False, knot_law='nae', take=None, choice='OLDEST', late=None, base_treatment=None,
                 order_reversed=False, demand_before_takes=False, fresh_by_parents=False):
        assert treatment in TREATMENTS, treatment
        assert release in ('RELEASE', 'HOLD')
        assert knot_law in ('nae', 'parity')
        assert choice in CHOICES, choice
        if take == 'none':
            take = None
        parse_take(take)
        self.ration, self.treatment, self.release = ration, treatment, release
        self.no_offshoot, self.fillers, self.knot_law = bool(no_offshoot), bool(fillers), knot_law
        self.take, self.choice, self.late, self.base_treatment = take, choice, late, base_treatment
        self.order_reversed = bool(order_reversed)
        self.demand_before_takes = bool(demand_before_takes)
        self.fresh_by_parents = bool(fresh_by_parents)
        self.fam, self.k, self.which = parse_take(take)
        self.fresh_count(1, 1)

    @classmethod
    def from_base(cls, base, **kw):
        d = dict(BASE_LAWS[base])
        d.update(kw)
        return cls(**d)

    def key(self):
        return tuple(getattr(self, f) for f in self.FIELDS)

    def to_dict(self):
        return {f: getattr(self, f) for f in self.FIELDS}

    def replace(self, **kw):
        d = self.to_dict()
        d.update(kw)
        return Law(**d)

    def treatment_at(self, rnd):
        if self.treatment == 'SHORT-TAKES' and self.late is not None and rnd <= self.late:
            return self.base_treatment
        return self.treatment

    def take_at(self, rnd):
        if self.take is not None and self.late is not None and rnd <= self.late:
            return None
        return self.take

    def fresh_count(self, p, D):
        """SD line 61-62 (the ordinary count q = max(D, 3 - p, 1))."""
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
        """Every birth receives at least one fresh distinction (FD 7): not-all-equal with ORD, CAP-k, FLOOR1, RATION-k."""
        if self.knot_law != 'nae':
            return False
        r = self.ration
        return r in ('ORD', 'FLOOR1') or r.startswith('CAP-') or (r.startswith('RATION-') and int(r[7:]) >= 1)

    def name(self):
        bits = [self.ration, self.treatment, self.release]
        if self.base_treatment:
            bits.append('base=' + self.base_treatment)
        if self.no_offshoot:
            bits.append('NO-OFFSHOOT')
        if self.fillers:
            bits.append('FILLERS')
        bits.append('take=%s(%s)' % (self.take, self.choice) if self.take else 'take=none')
        if self.late is not None:
            bits.append('late%d' % self.late)
        for f, lab in (('order_reversed', 'order-reversed'), ('demand_before_takes', 'demand-before-takes'),
                       ('fresh_by_parents', 'fresh-by-parents')):
            if getattr(self, f):
                bits.append(lab)
        bits.append(self.knot_law)
        return '/'.join(bits)

    def __repr__(self):
        return 'Law(%s)' % self.name()


# ------------------------------------------------------------------------------------------------------ structure
class Structure:
    __slots__ = ('places', 'holders', 'bar_at', 'parents', 'made', 'kind', 'round', 'n_start', 'cand', 'span',
                 'levels', 'labels')

    def __init__(self):
        self.places = []
        self.holders = []
        self.bar_at = []
        self.parents = []
        self.made = []
        self.kind = []
        self.round = 0
        self.n_start = 0
        self.cand = set()           # knots that may hold a usable loose distinction (every member is among them)
        self.span = {}              # GF(2) basis of the knots' rows, {leading bit: row}, for IMPLIED (FD 2.8)
        self.levels = {}            # (knot, k) -> frozenset of knots exactly k parent steps above (dev 9)
        self.labels = None

    @property
    def n_knots(self):
        return len(self.places)

    @property
    def n_dist(self):
        return len(self.holders)

    def copy(self):
        T = Structure.__new__(Structure)
        T.places = [list(p) for p in self.places]
        T.holders = [list(h) for h in self.holders]
        T.bar_at = list(self.bar_at)
        T.parents = list(self.parents)
        T.made = list(self.made)
        T.kind = list(self.kind)
        T.round = self.round
        T.n_start = self.n_start
        T.cand = set(self.cand)
        T.span = dict(self.span)
        T.levels = dict(self.levels)     # own copy: entries of existing knots stay valid (parents are fixed)
        T.labels = self.labels
        return T

    def view(self, t, with_span=True):
        """The structure after round t (t <= self.round) as its own Structure (dev 3)."""
        if t == self.round:
            return self.copy()
        T = Structure.__new__(Structure)
        nk = 0
        while nk < len(self.made) and self.made[nk] <= t:
            nk += 1
        made = self.made
        T.places = [list(p) for p in self.places[:nk]]
        T.made = list(made[:nk])
        T.parents = list(self.parents[:nk])
        T.kind = list(self.kind[:nk])
        nd = 0
        for P in T.places:
            for d in P:
                if d + 1 > nd:
                    nd = d + 1
        T.holders = []
        for d in range(nd):
            hs = self.holders[d]
            T.holders.append([w for w in hs if w < nk])
        T.bar_at = [b if b <= t else NEVER for b in self.bar_at[:nd]]
        T.round = t
        T.n_start = self.n_start
        T.cand = set(range(nk))
        T.span = {}
        if with_span:
            for u in range(nk):
                span_insert(T.span, row_of(T.places[u]))
        T.levels = {key: v for key, v in self.levels.items() if key[0] < nk}
        T.labels = self.labels
        return T

    def is_barred(self, d):
        return self.bar_at[d] != NEVER

    def usable(self, u):
        H, B = self.holders, self.bar_at
        return sorted(d for d in self.places[u] if len(H[d]) == 1 and B[d] == NEVER)

    def hk(self, u):
        h = k = 0
        H, B = self.holders, self.bar_at
        for d in self.places[u]:
            if len(H[d]) == 1:
                if B[d] == NEVER:
                    h += 1
                else:
                    k += 1
        return h, k

    def meets(self, u):
        out = set()
        H = self.holders
        for d in self.places[u]:
            hs = H[d]
            if len(hs) > 1:
                out.update(hs)
        out.discard(u)
        return out

    def level(self, u, k):
        """Knots reached from u by some chain of exactly k parent steps (dev 9)."""
        key = (u, k)
        v = self.levels.get(key)
        if v is None:
            if k == 0:
                v = frozenset((u,))
            else:
                acc = set()
                for x in self.level(u, k - 1):
                    acc.update(self.parents[x])
                v = frozenset(acc)
            self.levels[key] = v
        return v

    def ancestors(self, u):
        out, stack = set(), list(self.parents[u])
        while stack:
            x = stack.pop()
            if x not in out:
                out.add(x)
                stack.extend(self.parents[x])
        return out

    def check(self):
        seen = defaultdict(list)
        for u, P in enumerate(self.places):
            assert len(set(P)) == len(P), 'knot %d lists a distinction twice' % u
            for d in P:
                seen[d].append(u)
        for d, hs in enumerate(self.holders):
            assert sorted(hs) == sorted(seen.get(d, [])), 'holders of %d' % d
            assert hs == sorted(hs, key=lambda w: self.made[w]), 'holders of %d out of order' % d
        return True


def row_of(places):
    r = 0
    for d in places:
        r |= 1 << d
    return r


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


def from_stars(stars, dist_order=None, knot_order=None):
    """A start from its stars.  FD 2.1: distinctions named by their labels in increasing order.  A numbering (TD 5.4)
    gives an order of the distinctions (the k-th listed is named k) and an order of the stars (the k-th listed is
    knot k)."""
    labels = sorted({d for star in stars for d in star})
    if dist_order is None:
        dist_order = labels
    assert sorted(dist_order) == labels
    name = {lab: i for i, lab in enumerate(dist_order)}
    if knot_order is None:
        knot_order = list(range(len(stars)))
    assert sorted(knot_order) == list(range(len(stars)))
    S = Structure()
    n = len(labels)
    S.holders = [[] for _ in range(n)]
    S.bar_at = [NEVER] * n
    for u, si in enumerate(knot_order):
        star = stars[si]
        assert len(set(star)) == len(star)
        P = [name[d] for d in star]
        S.places.append(P)
        for d in P:
            S.holders[d].append(u)
        S.parents.append(())
        S.made.append(0)
        S.kind.append('start')
    S.n_start = len(stars)
    S.cand = set(range(len(stars)))
    for u in range(len(stars)):
        span_insert(S.span, row_of(S.places[u]))
    S.labels = list(dist_order)
    return S


# ------------------------------------------------------------------------------------------------------- the roster
class Roster:
    __slots__ = ('members', 'mset', 'h', 'k', 'maxsets', 'commons', 'adj', 'groups', 'parts', 'part_of', 'incid',
                 'n_pairs', 'meets_member', 'n_cliques', 'metsets', 'member_meets', '_cache')

    def part_maxsets(self, P):
        Ps = set(P)
        return [M for M in self.maxsets if next(iter(M)) in Ps]


def maximal_family(metsets):
    """metsets: {frozenset: [common knots]} -> (maximal sets sorted by their sorted members, their common knots)."""
    items = sorted(metsets.items(), key=lambda kv: (-len(kv[0]), sorted(kv[0])))
    containing = defaultdict(list)
    kept = []
    for M, com in items:
        # M is maximal unless it lies in a set kept before (every larger set was seen first)
        best = None
        for x in M:
            lst = containing[x]
            if best is None or len(lst) < len(best):
                best = lst
        if any(M <= kept[i][0] for i in best):
            continue
        idx = len(kept)
        kept.append((M, tuple(sorted(com))))
        for x in M:
            containing[x].append(idx)
    kept.sort(key=lambda mc: sorted(mc[0]))
    return [M for M, _ in kept], [c for _, c in kept]


def build_roster(S, members_hk, mask=None, where='roster', guard=True, clock=None, want_groups=True):
    """The roster of the given members [(u, h, k)], met sets read from S (FD 1.3: a knot is not in its own met set);
    joinable: some met set contains both (SD line 27), less the masked pairs (TD 4.4); parts; groups (SD step 1)."""
    R = Roster()
    members = sorted(u for u, _, _ in members_hk)
    R.members = tuple(members)
    mset = set(members)
    R.mset = mset
    R.h = {u: h for u, h, _ in members_hk}
    R.k = {u: k for u, _, k in members_hk}
    H, P = S.holders, S.places
    inc = 0
    for u in members:
        for d in P[u]:
            inc += len(H[d]) - 1
    R.incid = inc
    _guard('incidences', inc, where, guard)
    raw = defaultdict(set)
    meets_member = set()
    for u in members:
        for d in P[u]:
            hs = H[d]
            if len(hs) > 1:
                for w in hs:
                    if w != u:
                        raw[w].add(u)
                        if w in mset:
                            meets_member.add(u)
    if clock is not None:
        clock.check()
    metsets = defaultdict(list)
    big = 0
    for w, ms in raw.items():
        if len(ms) >= 2:
            fm = frozenset(ms)
            metsets[fm].append(w)
            if len(fm) > big:
                big = len(fm)
    R.meets_member = meets_member
    R.member_meets = {w: raw[w] for w in meets_member if w in raw}
    R.metsets = metsets
    R._cache = {}
    if guard and mask is None:
        # every pair of one met set is joinable: C(m, 2) pairs at least (decided here when it applies)
        _guard('pairs', big * (big - 1) // 2, where, guard)
    R.maxsets, R.commons = maximal_family(metsets)
    adj = {u: set() for u in members}
    npairs = 0
    for M in R.maxsets:
        L = sorted(M)
        for i in range(len(L)):
            a = L[i]
            na = adj[a]
            for b in L[i + 1:]:
                if b not in na:
                    if mask is not None and mask.blocked(a, b):
                        continue
                    na.add(b)
                    adj[b].add(a)
                    npairs += 1
        if guard and npairs > GUARD['pairs']:
            _guard('pairs', npairs, where, guard)
    R.n_pairs = npairs
    R.adj = adj
    _guard('pairs', npairs, where, guard)
    if clock is not None:
        clock.check()
    # parts: components of joinable
    part_of = {}
    parts = []
    for u in members:
        if u in part_of:
            continue
        comp = [u]
        part_of[u] = -1
        stack = [u]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in part_of:
                    part_of[y] = -1
                    comp.append(y)
                    stack.append(y)
        parts.append(tuple(sorted(comp)))
    parts.sort()
    for i, Pt in enumerate(parts):
        for u in Pt:
            part_of[u] = i
    R.parts = parts
    R.part_of = part_of
    if want_groups:
        R.groups, R.n_cliques = groups_of(R, where, guard, clock)
    else:
        R.groups, R.n_cliques = None, None
    return R


def groups_of(R, where, guard=True, clock=None):
    """SD step 1: every inclusion-maximal set of >= 3 pairwise joinable members contained in no single met set (the
    maximal cliques of joinable of size >= 3 that lie in no met set), then every joinable pair in none of those.
    FD 2.1 order: the sets of three or more in lexicographic order of sorted members, then the pairs."""
    adj = R.adj
    containing = defaultdict(list)
    for i, M in enumerate(R.maxsets):
        for x in M:
            containing[x].append(i)
    big = []
    ncl = 0
    for Pt in R.parts:
        if len(Pt) == 1:
            ncl += 1
            continue
        if len(Pt) == 2:
            ncl += 1
            continue
        G = nx.Graph()
        G.add_nodes_from(Pt)
        for a in Pt:
            for b in adj[a]:
                if a < b:
                    G.add_edge(a, b)
        for Q in nx.find_cliques(G):
            ncl += 1
            if guard and ncl > GUARD['cliques']:
                _guard('cliques', ncl, where, guard)
            if len(Q) < 3:
                continue
            Qs = frozenset(Q)
            best = None
            for x in Q:
                lst = containing[x]
                if best is None or len(lst) < len(best):
                    best = lst
            if any(Qs <= R.maxsets[i] for i in best):
                continue
            big.append(tuple(sorted(Q)))
        if clock is not None:
            clock.check()
    covered = set()
    for Q in big:
        for e in itertools.combinations(Q, 2):
            covered.add(e)
    pairs = []
    for a in R.members:
        for b in adj[a]:
            if a < b and (a, b) not in covered:
                pairs.append((a, b))
    out = sorted(big) + sorted(pairs)
    _guard('groups', len(out), where, guard)
    return out, ncl


def live_members(S):
    out = []
    keep = set()
    for u in sorted(S.cand):
        h, k = S.hk(u)
        if h > 0:
            out.append((u, h, k))
            keep.add(u)
    S.cand = keep
    return out


def roster_of(S, mask=None, guard=False, clock=None, want_groups=False):
    return build_roster(S, live_members(S), mask=mask, where='read', guard=guard, clock=clock,
                        want_groups=want_groups)


# ------------------------------------------------------------------------------------------------------- the masks
class Mask:
    """TD 4.4 / FD 5.6.  'XY': no member of side A (X and its descendants) is joinable with a member of side B (P and its
    descendants); a knot on both sides is joinable with no member of either.  'ISO': no member of B is joinable with a
    member outside B.  New knots join a side when a parent is on it."""

    def __init__(self, mode, A, B):
        self.mode, self.A, self.B = mode, set(A), set(B)

    def blocked(self, a, b):
        A, B = self.A, self.B
        if self.mode == 'XY':
            return (a in A and b in B) or (a in B and b in A)
        return (a in B) != (b in B)

    def extend(self, new):
        for x, ps in new:
            if any(p in self.A for p in ps):
                self.A.add(x)
            if any(p in self.B for p in ps):
                self.B.add(x)

    def copy(self):
        return Mask(self.mode, self.A, self.B)


# --------------------------------------------------------------------------------------------------------- one round
class Residual(Exception):
    pass


def pick(cands, choice, S, parent, i_turn):
    """FD 2.5 among the sorted candidates."""
    n = len(cands)
    if choice == 'OLDEST':
        return cands[0]
    if choice == 'NEWEST':
        return cands[-1]
    if choice == 'IN-TURN':
        return cands[i_turn % n]
    if choice == 'BY-COUNT':
        return cands[len(S.places[parent]) % n]
    if choice == 'BY-RECEIVED':
        return cands[(len(S.places[parent]) - len(S.parents[parent])) % n]
    raise ValueError(choice)


def candidates(S, law, b):
    """Step 5' (FD 2.4, FD 3.2, 3.3, TD 1.4): the sorted eligible candidates of birth b, read on the structure at the
    start of the round, or None when the rule does not apply to this birth."""
    fam, k, which = law.fam, law.k, law.which
    H = S.holders
    ps = b['parents']
    if b['kind'] == 'join':
        if fam != 'MET' or which == 'offshoot':
            return None
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
        return sorted(c)
    p = ps[0]
    own = set(S.places[p])
    if fam == 'Q':
        return sorted(d for d in S.places[p] if len(H[d]) >= 2)
    if fam == 'MET':
        if which == 'join':
            return None
        c = set()
        for w in S.meets(p):
            for d in S.places[w]:
                if len(H[d]) >= 2 and d not in own:
                    c.add(d)
        return sorted(c)
    if fam in ('STEPS', 'UP-TO'):
        npp = len(S.parents[p])
        if which == 'join' and npp < 2:
            return None
        if which == 'offshoot' and npp != 1:
            return None
        levels = [k] if fam == 'STEPS' else list(range(1, k + 1))
        anc = set()
        for j in levels:
            anc |= S.level(p, j)
        c = set()
        for g in anc:
            for d in S.places[g]:
                if len(H[d]) >= 2 and d not in own:
                    c.add(d)
        return sorted(c)
    raise ValueError(fam)


def round_step(S, law, ctx=None, clock=None):
    """One complete round applied to S in place; returns its record.  GuardStop leaves S unusable (callers copy)."""
    ctx = ctx or {}
    mask = ctx.get('mask')
    rnd = S.round + 1
    treatment = law.treatment_at(rnd)
    take = law.take_at(rnd)
    mem = live_members(S)
    R = build_roster(S, mem, mask=mask, where='roster r%d' % rnd, guard=True, clock=clock)
    members = R.members
    h = R.h
    groups = R.groups
    owe = Counter()
    for g in groups:
        for u in g:
            owe[u] += 1
    short = [u for u in members if owe[u] > h[u]]
    shortset = set(short)
    rec = {'round': rnd, 'members_before': len(members), 'groups': [list(g) for g in groups], 'short': short,
           'cancelled': [], 'births': [], 'waiting': [], 'retired': [], 'held': {}, 'stalled': False,
           'residual_stall': False, 'closing': False, 'treatment': treatment, 'take': take,
           'owe': {u: owe[u] for u in members if owe[u]}, 'n_pairs': R.n_pairs, 'n_cliques': R.n_cliques,
           'incidences': R.incid, 'barred_now': []}
    if treatment == 'STALL' and short:
        rec['stalled'] = True
        S.round = rnd
        _tail(S, rec)
        return rec, R
    if treatment == 'SHORT-TAKES':
        kept, cancelled = list(groups), []
    else:
        kept = [g for g in groups if not shortset.intersection(g)]
        cancelled = [g for g in groups if shortset.intersection(g)]
    rec['cancelled'] = [list(g) for g in cancelled]
    kept_n = Counter(u for g in kept for u in g)
    canc_n = Counter(u for g in cancelled for u in g)
    births = [{'kind': 'join', 'parents': tuple(g)} for g in kept]
    _guard('births', len(births), 'joins r%d' % rnd)
    n_off, n_keep, n_bar = {}, {}, {}
    for u in members:
        if u in shortset:
            if treatment == 'CANCEL-OFFSHOOT':
                n_off[u] = h[u]
            elif treatment == 'CANCEL-WAIT':
                rec['waiting'].append(u)
            elif treatment == 'CANCEL-RETIRE':
                rec['retired'].append(u)
                n_bar[u] = h[u]
            elif treatment == 'SHORT-TAKES':
                pass
            else:
                raise AssertionError(treatment)
        else:
            rem = h[u] - kept_n[u]
            nh = canc_n[u] if law.release == 'HOLD' else 0
            assert rem >= nh >= 0
            if nh:
                n_keep[u] = nh
                rec['held'][u] = nh
            if law.no_offshoot:
                n_bar[u] = rem - nh
            else:
                n_off[u] = rem - nh
    for u in members:
        for i in range(n_off.get(u, 0)):
            births.append({'kind': 'offshoot', 'parents': (u,)})
    _guard('births', len(births), 'births r%d' % rnd)
    if law.order_reversed:
        births.reverse()
    for b in births:
        b['loose'] = []
        b['given_shared'] = []
        b['rule_takes'] = []
    recv = defaultdict(list)
    for bi, b in enumerate(births):
        for p in b['parents']:
            recv[p].append(bi)
    to_bar = []
    pending = []                      # SHORT-TAKES: (birth index, short member) still to be given a shared distinction
    for u in members:
        us = S.usable(u)
        mine = recv.get(u, [])
        joins = [bi for bi in mine if births[bi]['kind'] == 'join']
        offs = [bi for bi in mine if births[bi]['kind'] == 'offshoot']
        if law.order_reversed:
            # dev 21: the member's receivers in the reversed birth order; its kept slots stay between its joins
            # and its offshoots in that order
            seq = [('b', bi) for bi in offs] + [('keep', None)] * n_keep.get(u, 0) + [('b', bi) for bi in joins]
        else:
            seq = [('b', bi) for bi in joins] + [('keep', None)] * n_keep.get(u, 0) + [('b', bi) for bi in offs]
        seq += [('bar', None)] * n_bar.get(u, 0)
        i = 0
        for what, bi in seq:
            if i < len(us):
                d = us[i]
                i += 1
                if what == 'b':
                    births[bi]['loose'].append(d)
                elif what == 'bar':
                    to_bar.append(d)
            else:
                if what == 'b' and u in shortset and treatment == 'SHORT-TAKES':
                    pending.append((bi, u))
                else:
                    raise AssertionError('member %d has nothing left for %s' % (u, what))
        if i < len(us) and not (u in shortset and treatment == 'CANCEL-WAIT'):
            raise AssertionError('member %d left %d usable distinctions' % (u, len(us) - i))
    if pending:
        # FD 2.3: a short member takes, for each further birth, an eligible distinction it holds, held at the start of
        # the round by no other parent of that birth, not given before by it this round (dev 22)
        pending.sort()
        given = defaultdict(set)
        for bi, u in pending:
            b = births[bi]
            others = set(q for q in b['parents'] if q != u)
            allowed = [d for d in sorted(S.places[u]) if len(S.holders[d]) >= 2 and d not in given[u]
                       and not any(w in others for w in S.holders[d])]
            if not allowed:
                rec['residual_stall'] = True
                rec['residual_member'] = u
                S.round = rnd
                _tail(S, rec)
                return rec, R
            if law.choice == 'IN-TURN':
                raise ValueError('IN-TURN is not used with SHORT-TAKES')
            d = pick(allowed, law.choice, S, u, 0)
            given[u].add(d)
            b['given_shared'].append(d)
    # step 5': the taking rule, birth by birth in birth order, on the structure at the start of the round
    if take is not None:
        off_index = Counter()
        tl = law if law.take == take else law.replace(take=take)
        for b in births:
            i_turn = 0
            if b['kind'] == 'offshoot':
                p0 = b['parents'][0]
                i_turn = off_index[p0]
                off_index[p0] += 1
            cands = candidates(S, tl, b)
            if not cands:
                continue
            have = set(b['loose']) | set(b['given_shared'])
            cands = [d for d in cands if d not in have]
            if not cands:
                continue
            ch = law.choice
            if b['kind'] == 'join' and ch == 'IN-TURN':
                ch = 'OLDEST'          # FD 2.5: a join under MET(IN-TURN) takes by OLDEST
            d = pick(cands, ch, S, b['parents'][0], i_turn)
            b['rule_takes'].append(d)
    if clock is not None:
        clock.check()
    base = S.n_knots
    for bi, b in enumerate(births):
        b['id'] = base + bi
        b['inputs'] = b['loose'] + b['given_shared'] + b['rule_takes']
        assert len(set(b['inputs'])) == len(b['inputs'])
        b['shared_at_start'] = sorted(d for d in b['inputs'] if len(S.holders[d]) >= 2)
        if law.knot_law == 'parity':
            b['implied'] = span_contains(S.span, row_of(b['inputs']))     # FD 2.8 IMPLIED, against the structure
        else:                                                              # before the round, each birth alone
            b['implied'] = False
    for d in to_bar:
        S.bar_at[d] = rnd
    rec['barred_now'] = sorted(to_bar)
    for b in births:
        x = b['id']
        first = b['loose'] + b['given_shared']
        ins = first if law.demand_before_takes else first + b['rule_takes']
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
    rec['persisting'] = [u for u, _, _ in persisting]
    if mask is not None:
        mask.extend([(b['id'], b['parents']) for b in births])
    if births:
        DR = build_roster(S, [(b['id'], 1, 0) for b in births] + persisting, mask=mask,
                          where='demand r%d' % rnd, guard=True, clock=clock)
        D = Counter(u for g in DR.groups for u in g)
        rec['demand_groups'] = len(DR.groups)
        if ctx.get('capture'):
            rec['_DR'] = DR
    else:
        D = Counter()
    if law.demand_before_takes:
        for b in births:
            x = b['id']
            for d in b['rule_takes']:
                S.places[x].append(d)
                S.holders[d].append(x)
    nfresh = 0
    for b in births:
        p = len(b['parents']) if law.fresh_by_parents else len(set(b['inputs']))
        Dx = D[b['id']]
        f = 0 if b['implied'] else law.fresh_count(p, Dx)
        fu = min(f, Dx) if law.fillers else f
        b.update({'D': Dx, 'p': p, 'f': f, 'usable': fu, 'barred': f - fu})
        nfresh += f
    _guard('distinctions', S.n_dist + nfresh, 'fresh r%d' % rnd)
    rec['closing'] = any(b['implied'] for b in births)
    for b in births:
        x = b['id']
        fr = []
        for i in range(b['f']):
            d = len(S.holders)
            S.holders.append([x])
            S.bar_at.append(NEVER if i < b['usable'] else rnd)
            S.places[x].append(d)
            fr.append(d)
        b['fresh'] = fr
    if law.knot_law == 'parity':
        for b in births:
            span_insert(S.span, row_of(S.places[b['id']]))
    for b in births:
        rec['births'].append({'id': b['id'], 'kind': b['kind'], 'parents': list(b['parents']),
                              'inputs': list(b['inputs']), 'loose': b['loose'], 'given_shared': b['given_shared'],
                              'rule_takes': b['rule_takes'], 'shared_at_start': b['shared_at_start'], 'D': b['D'],
                              'p': b['p'], 'f': b['f'], 'usable': b['usable'], 'barred': b['barred'],
                              'implied': b['implied'], 'fresh': b['fresh']})
    S.round = rnd
    _tail(S, rec)
    return rec, R


def _tail(S, rec):
    nb = len(rec['births'])
    members_after = any(S.hk(u)[0] > 0 for u in S.cand)
    rec.update({'n_births': nb, 'n_joins': sum(1 for b in rec['births'] if b['kind'] == 'join'),
                'n_offshoots': sum(1 for b in rec['births'] if b['kind'] == 'offshoot'),
                'n_taking': sum(1 for b in rec['births'] if b['rule_takes'] or b['given_shared']),
                'n_takes': sum(len(b['rule_takes']) + len(b['given_shared']) for b in rec['births']),
                'jammed': bool(members_after and nb == 0), 'stopped': not members_after,
                'n_knots': S.n_knots, 'n_dist': S.n_dist})


# ------------------------------------------------------------------------------------------------------------- runs
class Run:
    """One start grown under one law (TD 1.7: 18 rounds; cut short after the first round leaving more than the knot
    bound, that round kept; the guard cuts short without keeping the round; a residual stall stops the run; the
    limit of process time makes the run unfinished).  rosters[t] is the live roster after round t."""

    def __init__(self, S0, law, rounds=18, knot_bound=4000, ctx=None, clock=None, prefix=None, keep_rosters=True,
                 on_round=None):
        self.law = law
        self.rounds_asked = rounds
        self.knot_bound = knot_bound
        self.ctx = ctx or {}
        self.clock = clock
        S = S0.copy()
        if prefix is not None:
            self.records = list(prefix['records'])
            self.rosters = list(prefix['rosters'])
        else:
            self.records = []
            self.rosters = []
        assert len(self.records) == S.round
        self.stop = None          # None | 'knots' | 'guard' | 'residual_stall' | 'limit'
        self.guard = None
        self.keep_rosters = keep_rosters
        while self.stop is None and S.round < rounds:
            T = S.copy()
            try:
                rec, R = round_step(T, law, self.ctx, clock)
            except GuardStop as g:
                self.stop = 'guard'
                self.guard = {'round': S.round + 1, 'what': g.what, 'value': g.value, 'where': g.where}
                break
            except LimitReached:
                self.stop = 'limit'
                break
            if keep_rosters:
                if len(self.rosters) == S.round:
                    self.rosters.append(R)         # the live roster after round S.round (read for round S.round+1)
                elif len(self.rosters) == S.round + 1 and self.rosters[S.round] is None:
                    self.rosters[S.round] = R
            S = T
            self.records.append(rec)
            if on_round is not None:
                on_round(self, S, rec)
            if rec['residual_stall']:
                self.stop = 'residual_stall'
                break
            if S.n_knots > knot_bound:
                self.stop = 'knots'
                break
        self.S = S
        self.rounds_done = S.round

    @property
    def unfinished(self):
        return self.stop == 'limit'

    def roster(self, t):
        """The live roster after round t (computed when missing; no guard: dev 7)."""
        while len(self.rosters) <= t:
            self.rosters.append(None)
        R = self.rosters[t]
        if R is None:
            V = self.S if t == self.S.round else self.S.view(t, with_span=False)
            R = build_roster(V, live_members(V), mask=None, where='read r%d' % t, guard=False, clock=self.clock,
                             want_groups=False)
            self.rosters[t] = R
        return R

    def summary(self):
        return {'rounds_done': self.rounds_done, 'stop': self.stop, 'guard': self.guard, 'knots': self.S.n_knots}
