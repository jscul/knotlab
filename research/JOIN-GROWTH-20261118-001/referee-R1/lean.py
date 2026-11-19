"""Referee R1 for JOIN-GROWTH-20261118-001: a lean copy of the referee's own growth engine (FRESH-COUNT-R1 / FIRST-KNOT-R1:
the complete-round joining rule and the fewest counts), written to reach a million junctions.

It drops the GF(2) basis that the full engine keeps.  The basis is used only to give an implied junction zero fresh distinctions
when its demand is zero.  Here a junction of demand zero is reported (`self.zero_demand`), so a run that never meets one is exactly
the full engine's.  Validated against the full engine in `referee_join.py validate`.
"""
import itertools
from collections import Counter, defaultdict


class Lean:
    def __init__(self, junctions):
        self.bits = [tuple(j) for j in junctions]
        self.owner = defaultdict(list)
        for k, S in enumerate(self.bits):
            for b in S:
                self.owner[b].append(k)
        self.nb = max(self.owner) + 1
        self.nbr = [set() for _ in junctions]
        for b, js in self.owner.items():
            if len(js) == 2:
                self.nbr[js[0]].add(js[1])
                self.nbr[js[1]].add(js[0])
        self.parents = [set() for _ in junctions]
        self.round = [0] * len(junctions)
        self.fresh = [len(J) for J in junctions]
        self.live = list(range(len(junctions)))
        self.rounds = 0
        self.zero_demand = 0

    def loose(self, j):
        return [b for b in self.bits[j] if len(self.owner[b]) == 1]

    def groups(self, live):
        lv = set(live)
        cand = defaultdict(set)
        for w in {p for u in lv for p in self.nbr[u]}:
            ln = sorted(u for u in self.nbr[w] if u in lv)
            for a, b in itertools.combinations(ln, 2):
                cand[a].add(b)
                cand[b].add(a)
        valid = []

        def ext(S, common, P):
            if common and any(P <= self.nbr[w] for w in common):
                return
            if len(S) >= 3 and not common:
                valid.append(frozenset(S))
            for v in sorted(P):
                ext(S + [v], common & self.nbr[v], {w for w in P if w > v and w in cand[v]})

        for u in sorted(cand):
            ext([u], set(self.nbr[u]), {w for w in cand[u] if w > u})
        vs = set(valid)
        by = defaultdict(list)
        for T in vs:
            for x in T:
                by[x].append(T)
        groups = [S for S in vs if not any(len(T) > len(S) and S < T for T in by[min(S)])]
        covered = {frozenset(p) for S in valid for p in itertools.combinations(S, 2)}
        pairs = {frozenset((a, b)) for a in cand for b in cand[a] if a < b} - covered
        return groups + list(pairs)

    def step(self):
        live = [j for j in self.live if self.loose(j)]
        if not live:
            return "closed"
        gs = self.groups(live)
        use = Counter(j for g in gs for j in g)
        lo = {j: self.loose(j) for j in live}
        if any(use[j] > len(lo[j]) for j in live):
            return "stall"
        plan, taken = [], Counter()
        for g in sorted(gs, key=sorted):
            bits = []
            for j in sorted(g):
                bits.append(lo[j][taken[j]])
                taken[j] += 1
            plan.append(bits)
        for j in live:
            for b in lo[j][taken[j]:]:
                plan.append([b])
        self.rounds += 1
        new = []
        for bits in plan:
            jid = len(self.bits)
            self.bits.append(tuple(bits))
            self.nbr.append(set())
            self.parents.append(set())
            for b in bits:
                for o in self.owner[b]:
                    self.nbr[o].add(jid)
                    self.nbr[jid].add(o)
                    self.parents[jid].add(o)
                self.owner[b].append(jid)
            self.round.append(self.rounds)
            self.fresh.append(0)
            new.append(jid)
        nxt = self.groups(new)
        demand = Counter(j for g in nxt for j in g)
        for jid in new:
            p, d = len(self.parents[jid]), demand[jid]
            if d == 0:
                self.zero_demand += 1
            k = max(d, 3 - p, 1)
            fresh = tuple(range(self.nb, self.nb + k))
            self.nb += k
            self.bits[jid] = self.bits[jid] + fresh
            for b in fresh:
                self.owner[b] = [jid]
            self.fresh[jid] = k
        self.live = [j for j in new if self.fresh[j] > 0]
        return "ok"

    def counts(self):
        c = Counter(self.round)
        return [c[r] for r in range(self.rounds + 1)]
