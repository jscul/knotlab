"""Core of LOCAL-ROUND-20261123-001A-E001: groups, plans, starts, and this study's own complete round.

Written from the frozen texts alone:
  research/RING-IN-BALANCE-20261123-001/definitions.md   (the shared definitions, "the definitions")
  research/LOCAL-ROUND-20261123-001/definitions.md       (this epic's definitions, "LR")
  research/LOCAL-ROUND-20261123-001A/preregistration.md  (the pre-registration)

It shares no code with the reference engine (ticket A of RING-IN-BALANCE), which is used only by
lr_reference.py and the gate.  Readings where the text leaves a choice are numbered in deviations.md.

A roster here is a dict member -> holding and a family of met sets (frozensets of members, each of size
at least two).  Groups are the definitions' step 1; a plan is LR section 2.1.
"""
from __future__ import annotations

import itertools
from collections import Counter, defaultdict

RATIONS = ('ORD', 'RATION-3', 'FLOOR1')
TREATMENTS = ('STALL', 'CANCEL-WAIT', 'CANCEL-RETIRE', 'CANCEL-OFFSHOOT')


# ============================================================================================ groups

def maximal_cliques(adj):
    """Bron-Kerbosch with pivoting.  adj: dict vertex -> set of neighbours (no self loops)."""
    out = []

    def bk(R, P, X):
        if not P:
            if not X:
                out.append(frozenset(R))
            return
        piv = max(P | X, key=lambda w: len(adj[w] & P))
        for v in sorted(P - adj[piv]):
            bk(R | {v}, P & adj[v], X & adj[v])
            P = P - {v}
            X = X | {v}

    verts = set(adj)
    seen = set()
    for s in sorted(verts):
        if s in seen:
            continue
        comp = {s}
        stack = [s]
        while stack:
            v = stack.pop()
            for w in adj[v]:
                if w not in comp:
                    comp.add(w)
                    stack.append(w)
        seen |= comp
        if len(comp) >= 2:
            bk(set(), set(comp), set())
    return out


def compute_groups(members, family):
    """Definitions step 1 (lines 36-38).  members: iterable of members; family: iterable of met sets.
    First every inclusion-maximal set of at least three pairwise joinable members contained in no single
    met set; then every joinable pair contained in none of those.  Returns a sorted list of sorted tuples."""
    adj = {u: set() for u in members}
    by_member = defaultdict(list)
    for M in family:
        for u in M:
            by_member[u].append(M)
            adj[u].update(M)
    for u in adj:
        adj[u].discard(u)
    big = []
    for C in maximal_cliques(adj):
        if len(C) < 3:
            continue
        u0 = min(C, key=lambda x: len(by_member[x]))
        if any(C <= M for M in by_member[u0]):
            continue
        big.append(tuple(sorted(C)))
    covered = set()
    for C in big:
        covered.update(itertools.combinations(C, 2))
    pairs = []
    for u in adj:
        for v in adj[u]:
            if u < v and (u, v) not in covered:
                pairs.append((u, v))
    return sorted(big + pairs)


def components(members, family):
    """Parts: connected components of joinable (definitions line 27)."""
    par = {u: u for u in members}

    def find(u):
        while par[u] != u:
            par[u] = par[par[u]]
            u = par[u]
        return u
    for M in family:
        it = iter(M)
        a = find(next(it))
        for b in it:
            b = find(b)
            if a != b:
                par[b] = a
    comp = defaultdict(set)
    for u in members:
        comp[find(u)].add(u)
    return sorted((frozenset(c) for c in comp.values()), key=min)


# ============================================================================================ fresh counts

def fresh_ration(ration, p, D=None):
    """Definitions step 7, line 62 (no closing exception).  D is needed only under ORD."""
    if ration == 'RATION-3':
        return max(3, 3 - p)
    if ration == 'FLOOR1':
        return max(3 - p, 1)
    if ration == 'ORD':
        return max(D, 3 - p, 1)
    raise ValueError(ration)


# ============================================================================================ plans (LR 2.1)

class Plan:
    """The plan of a roster.  joins: dict sorted parent tuple -> fresh count; offs: dict member ->
    [number of planned offshoots, fresh count]; status: dict member -> 'acts' | 'retires' | 'stalls' |
    'allshort'.  big: some roster read in the recursion has a group of three or more.  short_top: a member
    of the roster itself (not a waiters' roster) is short.  levels: number of rosters read."""

    __slots__ = ('joins', 'offs', 'status', 'big', 'short_top', 'stalled', 'levels', 'acting_level')

    def __init__(self):
        self.joins = {}
        self.offs = {}
        self.status = {}
        self.big = False
        self.short_top = False
        self.stalled = False
        self.levels = 0
        self.acting_level = {}

    def births(self):
        out = [(G, f) for G, f in self.joins.items()]
        for u, (n, f) in self.offs.items():
            out.extend([((u,), f)] * n)
        return out

    def to_dict(self):
        return {'joins': [[list(G), f] for G, f in sorted(self.joins.items())],
                'offs': {str(u): v for u, v in sorted(self.offs.items())},
                'status': {str(u): s for u, s in sorted(self.status.items())},
                'big': self.big, 'short_top': self.short_top, 'stalled': self.stalled, 'levels': self.levels}


def ord_demand(births, roster_members):
    """LR 2.1 step 4, ORD: D of each birth (index) in the roster whose members are the plan's births, each
    with holding 1, and whose met sets are, for each member of the plan's roster, the births it is a parent
    of, when at least two."""
    by_parent = defaultdict(list)
    for i, G in enumerate(births):
        for u in G:
            by_parent[u].append(i)
    fam = set()
    for u in roster_members:
        L = by_parent.get(u, [])
        if len(L) >= 2:
            fam.add(frozenset(L))
    groups = compute_groups(range(len(births)), fam)
    D = Counter(i for g in groups for i in g)
    return [D[i] for i in range(len(births))]


def read_plan(hold, family, ration, treatment, recursion=True):
    """LR section 2.1.  hold: dict member -> holding (>= 1); family: iterable of met sets (frozensets of
    members).  recursion=False gives steps 1-4 only (the control: a waiter is given nothing to do)."""
    plan = Plan()

    def level(members, fam, depth):
        plan.levels += 1
        groups = compute_groups(members, fam)
        if any(len(g) >= 3 for g in groups):
            plan.big = True
        owe = Counter(u for g in groups for u in g)
        short = {u for u in members if owe[u] > hold[u]}
        if depth == 0 and short:
            plan.short_top = True
        if treatment == 'STALL':
            if short:
                plan.stalled = True
                for u in members:
                    plan.status[u] = 'stalls'
                return
        allshort = set()
        if treatment == 'CANCEL-WAIT' and recursion:
            for P in components(members, fam):
                if all(u in short for u in P):
                    allshort |= P
        kept = [g for g in groups if not short.intersection(g)]
        kc = Counter(u for g in kept for u in g)
        births = list(kept)
        waiters = []
        for u in sorted(members):
            if u in short:
                if treatment == 'CANCEL-OFFSHOOT':
                    births.extend([(u,)] * hold[u])
                    plan.status[u] = 'acts'
                    plan.acting_level[u] = depth
                elif treatment == 'CANCEL-RETIRE':
                    plan.status[u] = 'retires'
                elif treatment == 'CANCEL-WAIT':
                    if u in allshort:
                        plan.status[u] = 'allshort'
                    elif recursion:
                        waiters.append(u)
                    else:
                        plan.status[u] = 'waits'      # the control: given nothing to do
                else:
                    raise AssertionError(treatment)
            else:
                births.extend([(u,)] * (hold[u] - kc[u]))
                plan.status[u] = 'acts'
                plan.acting_level[u] = depth
        if ration == 'ORD':
            Ds = ord_demand(births, members)
        else:
            Ds = [None] * len(births)
        for G, D in zip(births, Ds):
            f = fresh_ration(ration, len(G), D)
            if len(G) == 1:
                u = G[0]
                ent = plan.offs.get(u)
                if ent is None:
                    plan.offs[u] = [1, f]
                else:
                    if ent[1] != f:
                        raise AssertionError('two fresh counts for offshoots of one member')
                    ent[0] += 1
            else:
                if G in plan.joins:
                    raise AssertionError('a join planned twice')
                plan.joins[G] = f
        if waiters:
            ws = set(waiters)
            fam2 = set()
            for M in fam:
                M2 = M & ws
                if len(M2) >= 2:
                    fam2.add(frozenset(M2))
            level(sorted(ws), fam2, depth + 1)

    members = sorted(u for u, h in hold.items() if h >= 1)
    level(members, set(frozenset(M) for M in family), 0)
    return plan


# ============================================================================================ starts

def d2_stars(n, a=3):
    """D2(n, a), definitions lines 147-149: members 0..n-1 holding a loose each; dead knots w_i = knot n+i,
    sharing two distinctions with member i and two with member i+1 (mod n)."""
    stars = [[] for _ in range(2 * n)]
    lab = 0
    for i in range(n):
        for _ in range(2):
            stars[n + i].append(lab); stars[i].append(lab); lab += 1
        for _ in range(2):
            stars[n + i].append(lab); stars[(i + 1) % n].append(lab); lab += 1
    for i in range(n):
        for _ in range(a):
            stars[i].append(lab); lab += 1
    return stars


def ring_stars(n, a=3):
    """Ring(n, a), definitions line 145: knot i shares one distinction with knot i+1 (mod n) and holds a."""
    stars = [[] for _ in range(n)]
    lab = 0
    for i in range(n):
        stars[i].append(lab); stars[(i + 1) % n].append(lab); lab += 1
    for i in range(n):
        for _ in range(a):
            stars[i].append(lab); lab += 1
    return stars


GEN7 = [[0, 1, 2, 9, 10, 11], [0, 1, 3], [4, 5, 12, 13, 14], [6, 7, 15, 16, 17],
        [2, 3, 4, 6, 18, 19, 20], [7, 8, 21, 22], [5, 8, 23, 24]]
TWO_KNOT = [[0, 1, 2], [0, 3, 4]]
THREE_KNOT = [[0, 1, 2, 3], [0, 1, 4, 5], [2, 3, 6, 7]]
LONE_FOUR = [[0, 1, 2, 3]]
SCC = [[1, 2, 3, 7, 8], [1, 4, 9, 10], [2, 5, 11, 12], [3, 6, 13, 14], [4, 15, 16], [5, 17, 18], [6, 19, 20]]
C8X3 = [[0, 1, 30, 31, 32, 33, 34, 56, 57], [4, 5, 2, 3, 35, 36, 37, 60, 61], [8, 9, 6, 7, 38, 39, 40, 64, 65],
        [12, 13, 10, 11, 41, 42, 43], [16, 17, 14, 15, 44, 45, 46, 58, 59], [20, 21, 18, 19, 47, 48, 49, 62, 63],
        [24, 25, 22, 23, 50, 51, 52, 66, 67], [28, 29, 26, 27, 53, 54, 55], [0, 1, 2, 3], [4, 5, 6, 7],
        [8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18, 19], [20, 21, 22, 23], [24, 25, 26, 27], [28, 29, 30, 31],
        [56, 57, 58, 59], [60, 61, 62, 63], [64, 65, 66, 67]]


def start_stars(name):
    if name.startswith('D2(') or name.startswith('Ring('):
        inner = name[name.index('(') + 1:-1]
        n, a = (int(x) for x in inner.split(','))
        return d2_stars(n, a) if name.startswith('D2') else ring_stars(n, a)
    return {'GEN7': GEN7, 'TWO-KNOT': TWO_KNOT, 'THREE-KNOT': THREE_KNOT, 'LONE-FOUR': LONE_FOUR,
            'SCC': SCC, 'C8X3': C8X3}[name]


START_TITLES = {'GEN7': 'the seven-knot generator', 'TWO-KNOT': 'two-knot', 'THREE-KNOT': 'three-knot',
                'LONE-FOUR': 'lone four-place', 'SCC': 'the start-clause counterexample',
                'C8X3': 'the cycle of eight with three extra dead knots'}


# ============================================================================================ own complete round

class Str:
    """A structure on real knots, for this study's own complete rounds (the gate)."""

    def __init__(self, stars):
        labels = sorted({d for s in stars for d in s})
        idx = {lab: i for i, lab in enumerate(labels)}
        self.places = [[idx[d] for d in s] for s in stars]
        self.holders = [[] for _ in labels]
        for u, P in enumerate(self.places):
            for d in P:
                self.holders[d].append(u)
        assert all(1 <= len(h) <= 2 for h in self.holders)
        self.barred = [False] * len(labels)
        self.parents = [()] * len(stars)
        self.born = [0] * len(stars)
        self.round = 0

    def usable(self, u):
        return [d for d in self.places[u] if len(self.holders[d]) == 1 and not self.barred[d]]

    def n_loose(self):
        return sum(1 for h in self.holders if len(h) == 1)

    def nbrs(self, u):
        out = set()
        for d in self.places[u]:
            for x in self.holders[d]:
                if x != u:
                    out.add(x)
        return out

    def roster(self, hold):
        """Met sets read from the structure for the members of hold (a knot does not meet itself)."""
        acc = defaultdict(set)
        for u in hold:
            for w in self.nbrs(u):
                acc[w].add(u)
        return {frozenset(s) for s in acc.values() if len(s) >= 2}


def own_round(S, ration, treatment, release='RELEASE', fresh_override=None):
    """One complete round, steps 1-8 of the definitions (lines 34-67), in place.  RELEASE by default;
    release='HOLD' and fresh_override exist only to build altered controls for the gate."""
    rnd = S.round + 1
    hold = {}
    for u in range(len(S.places)):
        h = len(S.usable(u))
        if h:
            hold[u] = h
    fam = S.roster(hold)
    groups = compute_groups(sorted(hold), fam)
    owe = Counter(u for g in groups for u in g)
    short = {u for u in hold if owe[u] > hold[u]}
    rec = {'round': rnd, 'groups': len(groups), 'short': sorted(short), 'births': 0, 'stalled': False}
    S.round = rnd
    if treatment == 'STALL' and short:
        rec['stalled'] = True
        return rec
    kept = [g for g in groups if not short.intersection(g)]
    cancelled = [g for g in groups if short.intersection(g)]
    cc = Counter(u for g in cancelled for u in g)
    avail = {u: S.usable(u) for u in hold}
    births = []
    for g in kept:
        births.append((g, [avail[u].pop() for u in g]))
    for u in sorted(hold):
        if u in short:
            if treatment == 'CANCEL-OFFSHOOT':
                while avail[u]:
                    births.append(((u,), [avail[u].pop()]))
            elif treatment == 'CANCEL-RETIRE':
                for d in avail[u]:
                    S.barred[d] = True
                avail[u] = []
            elif treatment != 'CANCEL-WAIT':
                raise AssertionError(treatment)
        else:
            keep = cc[u] if release == 'HOLD' else 0
            while len(avail[u]) > keep:
                births.append(((u,), [avail[u].pop()]))
    new = []
    for parents, taken in births:
        x = len(S.places)
        S.places.append(list(taken))
        S.parents.append(tuple(parents))
        S.born.append(rnd)
        for d in taken:
            assert len(S.holders[d]) == 1 and not S.barred[d]
            S.holders[d].append(x)
        new.append(x)
    # step 6: demand
    dhold = {x: 1 for x in new}
    for u in hold:
        h = len(S.usable(u))
        if h:
            dhold[u] = h
    dgroups = compute_groups(sorted(dhold), S.roster(dhold))
    D = Counter(u for g in dgroups for u in g)
    closing = len(new) == 1 and S.n_loose() == 0
    rec['closing'] = closing
    for x in new:
        p = len(S.parents[x])
        f = 0 if closing else fresh_ration(ration, p, D[x])
        if fresh_override is not None:
            f = fresh_override(p, f)
        for _ in range(f):
            d = len(S.holders)
            S.holders.append([x])
            S.barred.append(False)
            S.places[x].append(d)
    rec['births'] = len(new)
    return rec
