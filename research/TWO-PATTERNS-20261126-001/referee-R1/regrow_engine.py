"""Independent complete rounds for the two-pattern referee's finite checks.

Rules: RING-IN-BALANCE, "One complete round"; PARTS-MEET-AGAIN, §2;
WHAT-A-BIRTH-CARRIES, second definitions, §2. All study births receive at
least one fresh distinction. The shared definitions specify the bench starts.
No study implementation is imported.
"""

from collections import Counter, defaultdict
from itertools import combinations


class WorkLimit(Exception):
    """The referee's roster limit, reported separately from a study stop."""


def groups_of(members, peers):
    """Calculate the groups directly from the knots each member meets."""
    witnesses = defaultdict(set)
    for member in members:
        for common in peers[member]:
            witnesses[common].add(member)
    met = {frozenset(s) for s in witnesses.values() if len(s) >= 2}
    neighbors = defaultdict(set)
    containing = defaultdict(list)
    for s in met:
        if len(s) > 180:
            raise WorkLimit("more than 180 members in one met set")
        for member in s:
            containing[member].append(s)
            neighbors[member].update(s)
            neighbors[member].discard(member)
    if sum(map(len, neighbors.values())) > 120_000:
        raise WorkLimit("more than 60,000 joinable pairs")

    # Visit maximal pairwise-joinable sets once, starting with their least
    # member. A pivot covers the extensions that would otherwise be repeated.
    many = []
    visited = 0

    def extend(chosen, available, already):
        nonlocal visited
        visited += 1
        if visited > 350_000:
            raise WorkLimit("more than 350,000 maximal-set search steps")
        if not available:
            if not already and len(chosen) >= 3:
                first = min(chosen, key=lambda k: len(containing[k]))
                if not any(chosen <= s for s in containing[first]):
                    many.append(tuple(sorted(chosen)))
            return
        pivot = max(available | already, key=lambda k: len(available & neighbors[k]))
        for k in sorted(available - neighbors[pivot]):
            extend(chosen | {k}, available & neighbors[k], already & neighbors[k])
            available.remove(k)
            already.add(k)

    for k, ns in neighbors.items():
        if len(ns) >= 2:
            forward = {j for j in ns if j > k}
            if len(forward) >= 2:
                extend({k}, forward, ns - forward)
    covered = {pair for s in many for pair in combinations(s, 2)}
    pairs = [(a, b) for a, ns in neighbors.items() for b in ns if a < b and (a, b) not in covered]
    return tuple(sorted(many) + sorted(pairs))


def fresh_count(ration, parents, places_taken, demand, owing):
    minimum = max(3 - places_taken, 1)
    if ration == "ORD":
        return max(minimum, demand)
    if ration == "CAP-3":
        return min(3, max(minimum, demand))
    if ration == "FLOOR1" or len(parents) > 1:
        return minimum
    if ration == "PARENT-OWING":
        return max(2, owing)
    if ration in ("PARENT-OWING-CAP3", "PARENT-OWING-CAP4"):
        return min(int(ration[-1]), max(2, owing))
    if ration == "PARENT-OWING-1":
        return max(1, owing)
    if ration == "PARENT-OWING-PLAIN":
        return max(minimum, owing)
    if ration == "MOD2":
        return 2 + owing % 2
    return {"OFFSHOOT-TWO": 2, "OFFSHOOT-THREE": 3}[ration]


class Growth:
    """Hold the distinctions, parents and complete, past-round birth names.

    A table shared by two growths interns full keys. Equal tokens therefore
    mean exactly equal making in those growths, without a digest comparison.
    """

    def __init__(self, stars, roles, ration="ORD", treatment="CANCEL-WAIT", take=None,
                 name_table=None, start_keys=None):
        self.ration, self.treatment, self.take = ration, treatment, take
        self.round = 0
        self.name_table = {} if name_table is None else name_table
        labels = {d: i for i, d in enumerate(sorted({d for s in stars for d in s}))}
        self.places = [[labels[d] for d in s] for s in stars]
        self.holders = [[] for _ in labels]
        for u, s in enumerate(self.places):
            assert len(s) == len(set(s))
            for d in s:
                self.holders[d].append(u)
        self.peers = [set() for _ in stars]
        for holders in self.holders:
            for a, b in combinations(holders, 2):
                self.peers[a].add(b)
                self.peers[b].add(a)
        self.active = {}
        for u, s in enumerate(self.places):
            loose = sorted(d for d in s if len(self.holders[d]) == 1)
            if loose:
                self.active[u] = loose
        self.parents = [() for _ in stars]
        self.ancestry = [frozenset([tag]) for tag in roles]
        self.tokens = []
        counts = Counter()
        for i, tag in enumerate(roles):
            key = ("start", tag, counts[tag]) if start_keys is None else start_keys[i]
            self.tokens.append(self.intern(key))
            counts[tag] += 1
        self.next_groups = None

    def intern(self, key):
        return self.name_table.setdefault(key, len(self.name_table))

    def retire(self, tag):
        ids = [u for u in self.active if tag in self.ancestry[u]]
        for u in ids:
            del self.active[u]
        self.next_groups = None
        return len(ids)

    def sole_take(self, parents):
        if self.take is None:
            return None
        if self.take == "MET-SOLE":
            suppliers = set.intersection(*(self.peers[p] for p in parents))
        elif len(parents) > 1:
            return None
        elif self.take == "STEPS1-SOLE":
            suppliers = self.parents[parents[0]]
        elif self.take == "STEPS2-SOLE":
            suppliers = {g for p in self.parents[parents[0]] for g in self.parents[p]}
        else:
            raise ValueError(self.take)
        held = {d for p in parents for d in self.places[p]}
        eligible = set()
        for supplier in suppliers:
            for d in self.places[supplier]:
                if d not in held and len(self.holders[d]) >= 2:
                    eligible.add(d)
                    if len(eligible) >= 2:
                        return None
        return next(iter(eligible), None)

    def step(self):
        members = tuple(sorted(self.active))
        groups = self.next_groups if self.next_groups is not None else groups_of(members, self.peers)
        owing = Counter(u for group in groups for u in group)
        short = {u for u in members if owing[u] > len(self.active[u])}
        kept = [group for group in groups if short.isdisjoint(group)]
        used = Counter(u for group in kept for u in group)
        children = kept.copy()
        next_active = {}
        for u in members:
            if u in short and self.treatment != "CANCEL-OFFSHOOT":
                if self.treatment == "CANCEL-WAIT":
                    next_active[u] = self.active[u]
                else:
                    assert self.treatment == "CANCEL-RETIRE"
            else:
                children.extend([(u,)] * (len(self.active[u]) - used[u]))

        # Every candidate is read before the first birth takes anything.
        takes = [self.sole_take(ps) for ps in children]
        loose = {u: iter(s) for u, s in self.active.items()}
        start = len(self.parents)
        births = tuple(range(start, start + len(children)))
        self.peers.extend(set() for _ in births)
        ordinal = Counter()
        for child, ps, take in zip(births, children, takes):
            inputs = [next(loose[p]) for p in ps]
            if take is not None:
                inputs.append(take)
            self.places.append(inputs)
            for d in inputs:
                for partner in self.holders[d]:
                    self.peers[partner].add(child)
                    self.peers[child].add(partner)
                self.holders[d].append(child)
            self.parents.append(ps)
            self.ancestry.append(frozenset.union(*(self.ancestry[p] for p in ps)))
            key = ("offshoot" if len(ps) == 1 else "join", tuple(sorted(self.tokens[p] for p in ps)))
            self.tokens.append(self.intern((key, ordinal[key])))
            ordinal[key] += 1
        # Every birth here will hold a usable distinction. Loose distinctions
        # meet nobody, so adding them leaves these groups as the next roster.
        new_roster = list(next_active) + list(births)
        self.next_groups = groups_of(new_roster, self.peers)
        demand = Counter(u for group in self.next_groups for u in group)
        fresh = {}
        for child, ps in zip(births, children):
            count = fresh_count(self.ration, ps, len(self.places[child]), demand[child], owing[ps[0]])
            supply = list(range(len(self.holders), len(self.holders) + count))
            self.holders.extend([child] for _ in supply)
            self.places[child].extend(supply)
            next_active[child] = supply
            fresh[child] = count
        self.active = next_active
        self.round += 1
        return {"members": members, "groups": groups, "short": short, "births": births,
                "fresh": fresh, "takes": sum(d is not None for d in takes)}


def pattern(name):
    """The named patterns, or a census name encoding sharing, loose counts and site."""
    if name == "source":
        return [[0, 1, 2, 9, 10, 11], [0, 1, 3], [4, 5, 12, 13, 14], [6, 7, 15, 16, 17],
                [2, 3, 4, 6, 18, 19, 20], [7, 8, 21, 22], [5, 8, 23, 24]], 0
    if name == "ring":
        return [[(u - 1) % 5, u, *(5 + 3*u + j for j in range(3))] for u in range(5)], 0
    if name == "copier":
        return [[0, 1, 2], [0, 3, 4]], 0
    if name == "stub":
        return [[]], 0
    topology, rest = name.split(":")
    counts, site = rest.split("@")
    shares = {"g1": [], "g3": [(0, 1)], "g6": [(0, 1), (0, 2)],
              "g7": [(0, 1), (0, 2), (1, 2)]}[topology]
    stars = [[] for _ in counts]
    for d, (a, b) in enumerate(shares):
        stars[a].append(d)
        stars[b].append(d)
    nxt = len(shares)
    for s, c in zip(stars, counts):
        s.extend(range(nxt, nxt + int(c)))
        nxt += int(c)
    return stars, int(site)


def joined(a, b, steps, join, mark=None, stub_extra=0):
    """Return a joined start and its origin tags. A mark is (tag, site, loose count)."""
    stars, roles, sites, offsets = [], [], {}, {}
    nxt = 0
    for tag, name in (("A", a), ("B", b)):
        if name is None:
            continue
        s, i = pattern(name)
        offsets[tag] = len(stars)
        sites[tag] = len(stars) + i
        distinctions = {d for row in s for d in row}
        change = {d: j for j, d in enumerate(sorted(distinctions), nxt)}
        nxt += len(change)
        stars.extend([[change[d] for d in row] for row in s])
        roles.extend([tag]*len(s))
    chain = [sites["A"]]
    if b is not None:
        for _ in range(steps-1):
            chain.append(len(stars))
            stars.append([])
            roles.append("link")
        chain.append(sites["B"])
        for u, v in zip(chain, chain[1:]):
            if join == "share":
                stars[u].append(nxt)
                stars[v].append(nxt)
                nxt += 1
            else:
                assert join == "meeting"
                stars[u].extend([nxt, nxt+3])
                stars[v].extend([nxt+1, nxt+2, nxt+4])
                stars.append([nxt, nxt+1, nxt+2])
                roles.append("spent")
                nxt += 5
        for u in chain:
            is_stub = (u == chain[0] and a == "stub") or (u == chain[-1] and b == "stub")
            target = (3 + stub_extra) if is_stub else (3 if u in chain[1:-1] else 0)
            n = max(0, target-len(stars[u]))
            stars[u].extend(range(nxt, nxt+n))
            nxt += n
    if mark is not None:
        tag, i, n = mark
        stars[offsets[tag]+i].extend(range(nxt, nxt+n))
    return stars, roles
