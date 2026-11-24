"""Core of the engine: groups, plans, starts, and the engine's own complete round.

First written for LOCAL-ROUND-20261123-001A-E001 and copied here, unchanged where the earlier laws are concerned, then
extended for GUARD-CAP-AND-HOLD-20261124-001A-E001 from:
  research/GUARD-CAP-AND-HOLD-20261124-001/definitions.md  ("GCH": the cap in a plan, the fillers, holding)
  research/LOCAL-ROUND-20261123-001/definitions.md         ("LR")
  research/RING-IN-BALANCE-20261123-001/definitions.md     (the shared definitions)

It shares no code with the reference engine (ticket A of RING-IN-BALANCE), which is used only by lr_reference.py
and the gate.  Readings where the texts leave a choice are numbered in deviations.md.

A roster here is a dict member -> holding and a family of met sets (frozensets of members, each of size at least
two).  Groups are the shared definitions' step 1; a plan is LR section 2.1 with GCH sections 1-3.
"""
from __future__ import annotations

import itertools
from collections import Counter, defaultdict

RATIONS = ('ORD', 'RATION-3', 'FLOOR1', 'CAP-3')
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
    """Shared definitions step 1 (lines 36-38).  First every inclusion-maximal set of at least three pairwise
    joinable members contained in no single met set; then every joinable pair contained in none of those.
    Returns a sorted list of sorted tuples."""
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
    """Parts: connected components of joinable (shared definitions line 27)."""
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
    """Shared definitions step 7, line 62, and GCH section 1 (no closing exception).  D is needed under ORD and
    CAP-3."""
    if ration == 'RATION-3':
        return max(3, 3 - p)
    if ration == 'FLOOR1':
        return max(3 - p, 1)
    if ration == 'ORD':
        return max(D, 3 - p, 1)
    if ration == 'CAP-3':
        return min(max(D, 3 - p, 1), 3)
    raise ValueError(ration)


# ============================================================================================ plans (LR 2.1, GCH 1-3)

class Plan:
    """The plan of a roster.

    births: Counter (parents, f, usable fresh) -> number planned, over every reading (GCH section 3, item 3).
    member_births: member -> Counter of the births that have it among their parents.
    status: member -> its last status: 'acts' (acted and was carried no further), 'retires', 'stalls', 'idle'
        (its part was idle in its last reading, GCH 3 item 2), 'allshort' (idle with every member short), and, for
        the control (no further reading), 'waits' or 'stays'.
    acting_levels: member -> the readings (0 = the roster itself) in which it acted; acting_level: the first.
    stayers: member -> [(reading, kept)].  detail: per birth (parents, D, f, usable, reading), for the gate.
    joins and offs keep the earlier study's view (joins: parents -> f; offs: member -> [number, f]).
    big: some roster read has a group of three or more.  short_top: a member of the roster itself is short."""

    __slots__ = ('joins', 'offs', 'status', 'big', 'short_top', 'stalled', 'levels', 'acting_level',
                 'acting_levels', 'births', 'member_births', 'stayers', 'detail', 'retire_level', 'waited')

    def __init__(self):
        self.joins = {}
        self.offs = {}
        self.status = {}
        self.big = False
        self.short_top = False
        self.stalled = False
        self.levels = 0
        self.acting_level = {}
        self.acting_levels = defaultdict(list)
        self.births = Counter()
        self.member_births = defaultdict(Counter)
        self.stayers = defaultdict(list)
        self.detail = []
        self.retire_level = {}
        self.waited = defaultdict(list)

    def to_dict(self):
        return {'births': [[list(G), f, u, n] for (G, f, u), n in sorted(self.births.items())],
                'status': {str(u): s for u, s in sorted(self.status.items())},
                'acting_levels': {str(u): v for u, v in sorted(self.acting_levels.items())},
                'stayers': {str(u): v for u, v in sorted(self.stayers.items())},
                'big': self.big, 'short_top': self.short_top, 'stalled': self.stalled, 'levels': self.levels}


def ord_demand(births, roster_members):
    """LR 2.1 step 4 (ORD) and GCH section 1 (CAP-3): D of each birth (index) in the roster whose members are the
    births of one reading, each with holding 1, and whose met sets are, for each member of that reading's roster,
    the births it is a parent of, when at least two."""
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


def read_plan(hold, family, ration, treatment, recursion=True, release='RELEASE', fillers=False):
    """LR section 2.1 with GCH sections 1-3.

    hold: dict member -> holding (>= 1); family: met sets.  recursion=False gives one reading only (steps 1-4): the
    control (a waiter, or a stayer, is given nothing further to do) and this engine's own complete round.

    Each reading is one pass over one part.  In it: groups and owing; shortness; the treatment; under RELEASE a
    member that is not short has its holding less its kept groups as offshoots; under HOLD its holding less all its
    groups, and it keeps one distinction for each cancelled group (a stayer when it keeps at least one).  Fresh
    counts: by the ration, with D among the births of the same reading; under FILLERS min(f, D) of them are usable.
    A reading that plans no birth and no retirement leaves its part idle.  The waiters and stayers (each with what
    it kept) form the next roster, read again part by part (GCH 3 item 2; under RELEASE with waiting this is LR's
    waiters' roster, and an idle part is an all-short part)."""
    plan = Plan()

    def reading(members, hold_now, fam, depth):
        plan.levels += 1
        carried = {}
        for P in components(members, fam):
            Pfam = [M for M in fam if M <= P]
            groups = compute_groups(sorted(P), Pfam)
            if any(len(g) >= 3 for g in groups):
                plan.big = True
            owe = Counter(u for g in groups for u in g)
            short = {u for u in P if owe[u] > hold_now[u]}
            if depth == 0 and short:
                plan.short_top = True
            if treatment == 'STALL' and short:
                plan.stalled = True
                for u in P:
                    plan.status[u] = 'stalls'
                continue
            kept = [g for g in groups if not short.intersection(g)]
            kc = Counter(u for g in kept for u in g)
            cc = Counter(u for g in groups if short.intersection(g) for u in g)
            births = list(kept)
            retire = []
            nxt = {}
            acted = []
            for u in sorted(P):
                h = hold_now[u]
                if u in short:
                    if treatment == 'CANCEL-OFFSHOOT':
                        births.extend([(u,)] * h)
                        acted.append(u)
                    elif treatment == 'CANCEL-RETIRE':
                        retire.append(u)
                    elif treatment == 'CANCEL-WAIT':
                        nxt[u] = ('waits', h)
                    else:
                        raise AssertionError(treatment)
                else:
                    acted.append(u)
                    if release == 'HOLD':
                        births.extend([(u,)] * (h - owe[u]))
                        if cc[u]:
                            nxt[u] = ('stays', cc[u])
                    else:
                        births.extend([(u,)] * (h - kc[u]))
            if not births and not retire:
                # an idle part: its stayers and waiters are recorded for this reading (GCH 3 item 1: "a stayer in
                # this reading"), and the recursion stops (GCH 3 item 2)
                lab = 'allshort' if all(u in short for u in P) else 'idle'
                for u, (kind, h) in nxt.items():
                    if kind == 'stays':
                        plan.stayers[u].append((depth, h))
                    else:
                        plan.waited[u].append(depth)
                for u in P:
                    plan.status[u] = lab
                continue
            Ds = ord_demand(births, sorted(P))
            for G, D in zip(births, Ds):
                f = fresh_ration(ration, len(G), D)
                uf = min(f, D) if fillers else f
                key = (G, f, uf)
                plan.births[key] += 1
                for v in G:
                    plan.member_births[v][key] += 1
                plan.detail.append((G, D, f, uf, depth))
                if len(G) == 1:
                    ent = plan.offs.get(G[0])
                    if ent is None:
                        plan.offs[G[0]] = [1, f]
                    else:
                        ent[0] += 1
                else:
                    plan.joins[G] = f
            for u in retire:
                plan.status[u] = 'retires'
                plan.retire_level[u] = depth
            for u in acted:
                plan.acting_levels[u].append(depth)
                plan.acting_level.setdefault(u, depth)
            for u, (kind, h) in nxt.items():
                if kind == 'stays':
                    plan.stayers[u].append((depth, h))
                else:
                    plan.waited[u].append(depth)
                if recursion:
                    carried[u] = h
                else:
                    plan.status[u] = kind
            for u in acted:
                if u not in nxt:
                    plan.status[u] = 'acts'
        if carried:
            cs = set(carried)
            fam2 = set()
            for M in fam:
                M2 = M & cs
                if len(M2) >= 2:
                    fam2.add(frozenset(M2))
            reading(sorted(cs), carried, fam2, depth + 1)

    members = sorted(u for u, h in hold.items() if h >= 1)
    reading(members, {u: hold[u] for u in members}, set(frozenset(M) for M in family), 0)
    return plan


# ============================================================================================ starts

def d2_stars(n, a=3):
    """D2(n, a), shared definitions lines 147-149."""
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
    """Ring(n, a), shared definitions line 145."""
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


# ============================================================================================ own complete round

class Str:
    """A structure on real knots, for this engine's own complete rounds (the gate)."""

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
        self.D = [None] * len(stars)        # demand of each birth, as the plan found it
        self.fu = [None] * len(stars)       # (f, usable fresh) of each birth
        self.held = {}                      # stayers of the last round: knot -> kept
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


def own_round(S, ration, treatment, release='RELEASE', fillers=False, fresh_override=None):
    """One complete round, computed through the plan (GCH section 1): one reading (LR 2.1 steps 1-4, with GCH's
    HOLD and FILLERS) of the live roster with its present holdings; its births are made with the fresh counts,
    demands and usable counts of that reading; short members retire (CANCEL-RETIRE) by having their usable
    distinctions barred; waiters and stayers keep what they hold.  The closing exception: a lone birth that takes
    every loose distinction receives none.  fresh_override only builds altered controls for the gate."""
    rnd = S.round + 1
    hold = {}
    for u in range(len(S.places)):
        h = len(S.usable(u))
        if h:
            hold[u] = h
    fam = S.roster(hold)
    pl = read_plan(hold, fam, ration, treatment, recursion=False, release=release, fillers=fillers)
    rec = {'round': rnd, 'births': len(pl.detail), 'stalled': pl.stalled,
           'retired': sorted(u for u, s in pl.status.items() if s == 'retires'),
           'held': {u: v[-1][1] for u, v in pl.stayers.items()}}
    S.round = rnd
    avail = {u: S.usable(u) for u in hold}
    for u in rec['retired']:
        for d in avail[u]:
            S.barred[d] = True
        avail[u] = []
    new = []
    for G, D, f, uf, depth in pl.detail:
        x = len(S.places)
        taken = [avail[u].pop() for u in G]
        S.places.append(list(taken))
        S.parents.append(tuple(G))
        S.born.append(rnd)
        S.D.append(D)
        S.fu.append((f, uf))
        for d in taken:
            assert len(S.holders[d]) == 1 and not S.barred[d]
            S.holders[d].append(x)
        new.append(x)
    closing = len(new) == 1 and S.n_loose() == 0
    rec['closing'] = closing
    for x in new:
        f, uf = S.fu[x]
        if closing:
            f, uf = 0, 0
            S.fu[x] = (0, 0)
        if fresh_override is not None:
            f, uf = fresh_override(len(S.parents[x]), f, uf)
            S.fu[x] = (f, uf)
        for i in range(f):
            d = len(S.holders)
            S.holders.append([x])
            S.barred.append(i >= uf)
            S.places[x].append(d)
    S.held = dict(rec['held'])
    return rec
