"""Structures on real knots, the live roster, its parts and groups, and one complete round.

Ticket RING-IN-BALANCE-20261123-001C. Written from research/RING-IN-BALANCE-20261123-001/definitions.md
alone; it shares no code with any earlier engine of the repository.

A structure is a list of knots. Every knot holds a list of distinction numbers (its places).
Every distinction has one or two holders; a loose one (one holder) is usable or barred.
`round_on(S, movers, law, born)` applies steps 1-8 of "One complete round" to the members in
`movers`: all members for the complete round, the members of one part for a move of the
part-round law.
"""

import hashlib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field

import iso


# --------------------------------------------------------------------------------------------
# laws

@dataclass(frozen=True)
class Law:
    ration: str          # 'ORD', 'CAP-k', 'RATION-k'
    treatment: str       # 'STALL' or 'CANCEL-WAIT' (the two used by ticket C)
    release: str = "RELEASE"
    fillers: bool = False
    knot_law: str = "parity"
    name: str = ""


TWO = Law("CAP-3", "CANCEL-WAIT", "RELEASE", False, "parity", "two")      # the two added rules
THREE = Law("CAP-3", "CANCEL-WAIT", "RELEASE", True, "parity", "three")   # the three added rules
ORDINARY = Law("ORD", "STALL", "RELEASE", False, "parity", "ordinary")    # (ORD, STALL)
LAWS = {"two": TWO, "three": THREE, "ordinary": ORDINARY}


def fresh_count(ration, p, D):
    """Step 7 without the closing exception."""
    q = max(D, 3 - p, 1)
    if ration == "ORD":
        return q
    m = re.fullmatch(r"CAP-(\d+)", ration)
    if m:
        return min(q, int(m.group(1)))
    m = re.fullmatch(r"RATION-(\d+)", ration)
    if m:
        return max(int(m.group(1)), 3 - p)
    raise ValueError(ration)


def seed_int(*parts):
    """Seed for a generator from (run identity, seed); independent of Python's salted str hash."""
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "big")


# --------------------------------------------------------------------------------------------
# structures

class Structure:
    def __init__(self):
        self.places = []     # knot -> list of distinctions
        self.parents = []    # knot -> tuple of parent knots ((): start knot)
        self.born = []       # knot -> round / own time at birth (0 for start knots)
        self.gen = []        # knot -> generation (birth-by-birth law)
        self.ownt = []       # knot -> own time (part-round law; a waiting member gains one)
        self.holders = []    # distinction -> list of 1 or 2 knots
        self.barred = []     # distinction -> bool
        self.usable = []     # knot -> ascending list of its usable loose distinctions
        self.nbar = []       # knot -> number of barred (loose) distinctions it holds
        self.nbrs = []       # knot -> set of knots it meets
        self.children = []   # knot -> knots that have it as a parent
        self.members = set() # knots holding at least one usable loose distinction
        self.loose_total = 0 # loose distinctions in the structure, usable or barred
        self.n_start = 0

    def nknots(self):
        return len(self.places)

    def h(self, u):
        return len(self.usable[u])

    def _new_knot(self, parents, born, gen, ownt):
        c = len(self.places)
        self.places.append([])
        self.parents.append(tuple(parents))
        self.born.append(born)
        self.gen.append(gen)
        self.ownt.append(ownt)
        self.usable.append([])
        self.nbar.append(0)
        self.nbrs.append(set())
        self.children.append([])
        return c

    def _new_dist(self, knot, barred):
        d = len(self.holders)
        self.holders.append([knot])
        self.barred.append(barred)
        self.places[knot].append(d)
        self.loose_total += 1
        if barred:
            self.nbar[knot] += 1
        else:
            self.usable[knot].append(d)
        return d

    def take(self, p, c):
        """Knot c takes one usable loose distinction of p (the lowest-numbered; which one makes no
        difference up to renaming)."""
        d = self.usable[p].pop(0)
        self.holders[d].append(c)
        self.places[c].append(d)
        self.nbrs[p].add(c)
        self.nbrs[c].add(p)
        self.loose_total -= 1
        if not self.usable[p]:
            self.members.discard(p)
        return d

    def birth(self, parents, born=None, ownt=None):
        gen = 1 + max(self.gen[p] for p in parents)
        c = self._new_knot(parents, born, gen, ownt)
        for p in parents:
            self.take(p, c)
            self.children[p].append(c)
        return c

    def give_fresh(self, c, usable, barred):
        for _ in range(usable):
            self._new_dist(c, False)
        for _ in range(barred):
            self._new_dist(c, True)
        if self.usable[c]:
            self.members.add(c)

    def check(self):
        """Internal consistency (used by the self-checks)."""
        for d, hs in enumerate(self.holders):
            assert 1 <= len(hs) <= 2, (d, hs)
            assert len(set(hs)) == len(hs)
            for k in hs:
                assert d in self.places[k]
            if len(hs) == 2:
                assert not self.barred[d]
        loose = 0
        for k in range(self.nknots()):
            us = [d for d in self.places[k] if len(self.holders[d]) == 1 and not self.barred[d]]
            bs = [d for d in self.places[k] if len(self.holders[d]) == 1 and self.barred[d]]
            assert sorted(us) == sorted(self.usable[k]), k
            assert len(bs) == self.nbar[k]
            loose += len(us) + len(bs)
            nb = {o for d in self.places[k] for o in self.holders[d] if o != k}
            assert nb == self.nbrs[k], k
            assert (k in self.members) == bool(us)
        assert loose == self.loose_total


def from_stars(stars):
    """A start from its list of knots, each a list of distinction numbers."""
    S = Structure()
    holders = defaultdict(list)
    for i, st in enumerate(stars):
        assert len(set(st)) == len(st), st
        for d in st:
            holders[d].append(i)
    assert all(len(h) <= 2 for h in holders.values()), "a distinction has at most two holders"
    for _ in stars:
        S._new_knot((), 0, 0, 0)
    for d in sorted(holders):
        hs = holders[d]
        nd = len(S.holders)
        S.holders.append(list(hs))
        S.barred.append(False)
        for k in hs:
            S.places[k].append(nd)
        if len(hs) == 1:
            S.usable[hs[0]].append(nd)
            S.loose_total += 1
        else:
            a, b = hs
            S.nbrs[a].add(b)
            S.nbrs[b].add(a)
    S.members = {k for k in range(len(stars)) if S.usable[k]}
    S.n_start = len(stars)
    return S


def ring_stars(n, a):
    """Ring(n, a): knot i shares one distinction with knot i+1 (mod n) and holds a loose ones."""
    return [[(i - 1) % n, i] + [n + i * a + j for j in range(a)] for i in range(n)]


def d2_stars(n, a):
    """D2(n, a): members 0..n-1 (a loose each) and dead knots w_i = knot n+i; w_i shares two
    distinctions with member i and two with member i+1."""
    stars = []
    for i in range(n):
        j = (i - 1) % n
        stars.append([4 * i, 4 * i + 1, 4 * j + 2, 4 * j + 3] + [4 * n + i * a + t for t in range(a)])
    for i in range(n):
        stars.append([4 * i, 4 * i + 1, 4 * i + 2, 4 * i + 3])
    return stars


def dw_stars(n, a):
    """DW(n, a): as D2 with single meetings; w_i also meets w_{i-1} and w_{i+1}."""
    stars = []
    for i in range(n):
        j = (i - 1) % n
        stars.append([3 * i, 3 * j + 1] + [3 * n + i * a + t for t in range(a)])
    for i in range(n):
        j = (i - 1) % n
        stars.append([3 * i, 3 * i + 1, 3 * j + 2, 3 * i + 2])
    return stars


GENERATOR7 = [[0, 1, 2, 9, 10, 11], [0, 1, 3], [4, 5, 12, 13, 14], [6, 7, 15, 16, 17],
              [2, 3, 4, 6, 18, 19, 20], [7, 8, 21, 22], [5, 8, 23, 24]]


def start_stars(name):
    m = re.fullmatch(r"(Ring|D2|DW)\((\d+),\s*(\d+)\)", name)
    if m:
        kind, n, a = m.group(1), int(m.group(2)), int(m.group(3))
        return {"Ring": ring_stars, "D2": d2_stars, "DW": dw_stars}[kind](n, a)
    if name == "GEN7":
        return GENERATOR7
    if name == "TWO-THREE":       # two three-place knots sharing one distinction
        return [[0, 1, 2], [0, 3, 4]]
    if name == "LONE-FOUR":       # a lone four-place knot
        return [[0, 1, 2, 3]]
    raise ValueError(name)


def make_start(name):
    return from_stars(start_stars(name))


# --------------------------------------------------------------------------------------------
# the live roster: met sets, joinable, parts, groups

def met_sets(S, roster, eligible=None):
    """For every knot x that meets at least two knots of `roster` (the knots counted as members),
    the set of them it meets. A knot does not meet itself, so x is never in its own set.
    `eligible(x)` (optional) says whether x may serve as a common knot. Returns {x: frozenset}."""
    acc = defaultdict(list)
    for y in roster:
        for x in S.nbrs[y]:
            acc[x].append(y)
    out = {}
    for x, ys in acc.items():
        if len(ys) >= 2 and (eligible is None or eligible(x)):
            out[x] = frozenset(ys)
    return out


def joinable_adjacency(family):
    adj = defaultdict(set)
    for M in family:
        for u in M:
            adj[u].update(M)
    for u in adj:
        adj[u].discard(u)
    return adj


def components(nodes, adj):
    seen = set()
    comps = []
    for s in sorted(nodes):
        if s in seen:
            continue
        seen.add(s)
        comp = [s]
        stack = [s]
        while stack:
            v = stack.pop()
            for u in adj.get(v, ()):
                if u not in seen:
                    seen.add(u)
                    comp.append(u)
                    stack.append(u)
        comps.append(frozenset(comp))
    return comps


def maximal_cliques(adj, nodes=None):
    """Bron-Kerbosch with pivoting, run per connected component."""
    out = []

    def bk(R, P, X):
        if not P:
            if not X:
                out.append(frozenset(R))
            return
        piv = max(P | X, key=lambda w: len(adj[w] & P))
        for v in [w for w in P if w not in adj[piv]]:
            bk(R | {v}, P & adj[v], X & adj[v])
            P.remove(v)
            X.add(v)

    if nodes is None:
        nodes = set(adj)
    for comp in components(nodes, adj):
        if len(comp) == 1:
            continue
        bk(set(), set(comp), set())
    return out


def maximal_sets(family):
    """The inclusion-maximal sets of a family of frozensets."""
    by_member = defaultdict(list)
    for M in family:
        for u in M:
            by_member[u].append(M)
    out = []
    for M in family:
        u0 = min(M, key=lambda u: len(by_member[u]))
        if not any(M < N for N in by_member[u0]):
            out.append(M)
    return out


def compute_groups(family):
    """Step 1. family: the distinct met sets (each of at least two members).
    First every inclusion-maximal set of at least three pairwise joinable members contained in no
    single met set (these are exactly the maximal cliques of joinable of size >= 3 contained in no
    met set); then every joinable pair contained in none of those."""
    adj = joinable_adjacency(family)
    by_member = defaultdict(list)
    for M in family:
        for u in M:
            by_member[u].append(M)
    big = []
    for C in maximal_cliques(adj):
        if len(C) >= 3:
            u0 = min(C, key=lambda u: len(by_member[u]))
            if not any(C <= M for M in by_member[u0]):
                big.append(C)
    big_by = defaultdict(list)
    for C in big:
        for u in C:
            big_by[u].append(C)
    pairs = []
    for u in adj:
        for v in adj[u]:
            if u < v and not any(v in C for C in big_by[u]):
                pairs.append(frozenset((u, v)))
    groups = big + pairs
    groups.sort(key=lambda G: (len(G), sorted(G)))
    return groups


def roster_family(S, members, eligible=None):
    return set(met_sets(S, members, eligible).values())


def parts_of(S, members, eligible=None):
    fam = roster_family(S, members, eligible)
    return components(members, joinable_adjacency(fam)), fam


def roster_summary(S, members=None):
    """Numbers of the C0 trace for the roster (whole roster unless `members` is given)."""
    mem = set(S.members if members is None else members)
    fam = roster_family(S, mem)
    parts = components(mem, joinable_adjacency(fam))
    mx = maximal_sets(fam)
    return {
        "members": len(mem),
        "parts": len(parts),
        "h_sorted": sorted(S.h(u) for u in mem),
        "maximal_met_set_sizes_sorted": sorted(len(M) for M in mx),
    }


def past_start(S, members):
    """No member of `members` meets a member."""
    return not any(x in S.members for u in members for x in S.nbrs[u])


# --------------------------------------------------------------------------------------------
# sameness

def roster_graph(S, members, family=None, eligible=None):
    """Incidence graph of members (coloured by (h, k)) and the inclusion-maximal met sets."""
    mem = sorted(members)
    if family is None:
        family = roster_family(S, set(mem), eligible)
    mx = sorted((tuple(sorted(M)) for M in maximal_sets(family)))
    idx = {u: i for i, u in enumerate(mem)}
    col = [iso.stable_int(("m", S.h(u), S.nbar[u])) for u in mem]
    adj = [[] for _ in mem]
    mcol = iso.stable_int(("M",))
    for M in mx:
        j = len(col)
        col.append(mcol)
        adj.append([])
        for u in M:
            adj[idx[u]].append(j)
            adj[j].append(idx[u])
    return iso.Graph(col, adj)


def structure_graph(S, knots, colour):
    """Incidence graph of the given knots and every distinction they hold; knots coloured by
    colour(knot) (round, own time at birth or generation), distinctions by barred or not."""
    ks = sorted(knots)
    idx = {k: i for i, k in enumerate(ks)}
    lev = [colour(k) for k in ks]
    col = [iso.stable_int(("k", c)) for c in lev]
    adj = [[] for _ in ks]
    didx = {}
    dcol = {False: iso.stable_int(("d", False)), True: iso.stable_int(("d", True))}
    for k in ks:
        for d in S.places[k]:
            j = didx.get(d)
            if j is None:
                j = len(col)
                didx[d] = j
                col.append(dcol[S.barred[d]])
                adj.append([])
                lev.append(None)
            adj[idx[k]].append(j)
            adj[j].append(idx[k])
    return iso.Graph(col, adj, lev)


# --------------------------------------------------------------------------------------------
# one round

@dataclass
class RoundResult:
    stalled: bool = False
    births: list = field(default_factory=list)   # (knot, p, D, f, usable)
    waiting: list = field(default_factory=list)
    groups: int = 0
    kept: int = 0
    closing: bool = False


class PartInteraction(Exception):
    """Raised when a move of one part would read a member of another part."""


def round_on(S, movers, law, born, interaction_check=False):
    """Steps 1-8 of one complete round applied to the members in `movers`.

    The complete round passes every member. The part-round law passes the members of one part;
    with interaction_check=True it raises PartInteraction if any knot meets both a knot of the
    moving part's demand roster and a member outside it (then the other parts would not be
    "left as they are")."""
    assert law.release == "RELEASE" and law.treatment in ("STALL", "CANCEL-WAIT")
    movers = sorted(movers)
    mset = set(movers)
    family = roster_family(S, mset)
    if interaction_check:
        _check_isolated(S, mset)
    groups = compute_groups(family)
    owe = Counter()
    for G in groups:
        for u in G:
            owe[u] += 1
    short = {u for u in movers if owe[u] > S.h(u)}
    res = RoundResult(groups=len(groups))
    if short and law.treatment == "STALL":
        res.stalled = True
        return res
    kept = [G for G in groups if not (G & short)]
    res.kept = len(kept)
    kc = Counter()
    for G in kept:
        for u in G:
            kc[u] += 1
    plan = [tuple(sorted(G)) for G in kept]
    for u in movers:
        if u not in short:
            plan.extend([(u,)] * (S.h(u) - kc[u]))     # RELEASE: offshoots from every leftover
    new = []
    for P in plan:
        new.append(S.birth(P, born=born, ownt=S.ownt[P[0]] + 1))
    keepers = [u for u in movers if S.usable[u]]
    assert set(keepers) == short, "under RELEASE only the short members keep anything"
    droster = set(new) | set(keepers)
    if interaction_check:
        _check_isolated(S, droster)
    dgroups = compute_groups(roster_family(S, droster))
    D = Counter()
    for G in dgroups:
        for u in G:
            D[u] += 1
    closing = law.knot_law == "parity" and len(new) == 1 and S.loose_total == 0
    res.closing = closing
    for c in new:
        p = len(S.parents[c])
        d = D[c]
        f = 0 if closing else fresh_count(law.ration, p, d)
        us = min(f, d) if law.fillers else f
        S.give_fresh(c, us, f - us)
        res.births.append((c, p, d, f, us))
    for u in short:
        S.ownt[u] += 1
    res.waiting = sorted(short)
    return res


def _check_isolated(S, roster):
    for x in {x for y in roster for x in S.nbrs[y]}:
        inside = sum(1 for y in S.nbrs[x] if y in roster)
        outside = sum(1 for y in S.nbrs[x] if y in S.members and y not in roster)
        if inside and outside and inside + outside >= 2:
            raise PartInteraction(f"knot {x} meets the moving part and another member")


def complete_rounds(start, law, rounds):
    """Grow a start under complete rounds; returns (structure, list of per-round records)."""
    S = make_start(start)
    hist = []
    for r in range(1, rounds + 1):
        if not S.members:
            hist.append({"round": r, "status": "stopped"})
            break
        res = round_on(S, S.members, law, born=r)
        if res.stalled:
            hist.append({"round": r, "status": "stalled"})
            break
        rec = {"round": r, "status": "ok" if res.births else "jammed", "births": len(res.births),
               "fresh_total": sum(b[3] for b in res.births),
               "births_sorted": sorted([b[1], b[3]] for b in res.births)}
        rec.update(roster_summary(S))
        hist.append(rec)
        if not res.births:
            break
    return S, hist
