"""Parity growth with the fresh count left to a rule (FRESH-COUNT-20261118-001B).

A junction is one even-parity constraint on its distinctions (bits).  A bit is loose while it lies in one junction and shared once a
second junction takes it.  Two junctions are neighbours when they share a bit.  One round of the joining policy of
CUBIC-FROM-A-KNOT-20261117-001, with groups of any size (cap=None) or capped at three as in the original (cap=3):

  the live junctions hold loose bits; two live junctions are candidates when they have a common neighbour; a valid set is a set of
  at least three pairwise candidates with no neighbour common to all of them; the groups are the maximal valid sets (capped: every
  valid triple) and every candidate pair contained in none of them; each live junction gives one loose bit to each group containing
  it, and each remaining loose bit gets a junction of its own (an offshoot, the junction with one parent).  If a junction is in more
  groups than it has loose bits, the round is unavailable: a stall.

Each group becomes a new junction on its chosen bits; a count rule then gives every new junction its fresh bits.  Every loose bit is
used in every round, so after a round the live junctions are exactly the new ones that received fresh bits.  The demand of a new
junction is the number of groups of the next round containing it, computed from the presentation after the round (lookahead) with
every new junction counted live.  A new junction's parity is implied by the old equations exactly when it takes every loose bit of
the presentation (the old junctions form one connected pattern, so the only cuts made of loose bits are the empty cut and the cut of
everything); `linalg=True` also tests this by elimination over GF(2), as a check.
"""
import itertools
import random
from collections import defaultdict


class Presentation:
    def __init__(self, a, linalg=False):
        self.bits_of = [list(range(a))]
        self.owner = {b: [0] for b in range(a)}
        self.nbits = a
        self.nbr = [set()]
        self.parents = [0]
        self.fresh = [a]
        self.round_of = [0]
        self.demand_at_birth = [None]
        self.rounds = 0
        self.live = [0]
        self.linalg = linalg
        self.basis = {}
        if linalg:
            self._add_row(0)
        self.implied_mismatch = 0

    # -- GF(2), used only as a check -------------------------------------------------------------------------------------------
    def _mask(self, bits):
        m = 0
        for b in bits:
            m |= 1 << b
        return m

    def _reduce(self, x):
        while x:
            r = self.basis.get(x.bit_length() - 1)
            if r is None:
                return x
            x ^= r
        return 0

    def _add_row(self, j):
        x = self._reduce(self._mask(self.bits_of[j]))
        if x:
            self.basis[x.bit_length() - 1] = x

    # -- the policy ---------------------------------------------------------------------------------------------------------------
    def loose(self, j):
        return [b for b in self.bits_of[j] if len(self.owner[b]) == 1]

    def groups_among(self, live, cap=None):
        """The multi-parent groups of the complete-round policy among these live junctions."""
        lv = set(live)
        cand = defaultdict(set)
        for w in range(len(self.bits_of)):
            ln = [u for u in self.nbr[w] if u in lv]
            for u, v in itertools.combinations(ln, 2):
                cand[u].add(v)
                cand[v].add(u)
        valid = set()

        def ext(S, P):
            if len(S) >= 2:
                common = set.intersection(*[self.nbr[x] for x in S])
                # every set between S and S + P keeps a common neighbour w whose neighbours hold P: none of them is valid
                if any(P <= self.nbr[w] for w in common):
                    return
                if len(S) >= 3 and not common:
                    valid.add(frozenset(S))
            if cap is not None and len(S) >= cap:
                return
            for v in sorted(P):
                ext(S + [v], {w for w in P if w > v and w in cand[v]})

        for u in sorted(lv):
            ext([u], {w for w in cand[u] if w > u})
        big = [S for S in valid if not any(S < T for T in valid)] if cap is None else list(valid)
        covered = set()
        for S in big:
            for p in itertools.combinations(sorted(S), 2):
                covered.add(p)
        pairs = [frozenset((u, v)) for u in sorted(lv) for v in sorted(cand[u]) if u < v and (u, v) not in covered]
        return sorted(big, key=sorted) + sorted(pairs, key=sorted)

    def step(self, rule, cap=None, rng=None, compare_cap=False):
        """One complete round.  Returns a dict, or None on a stall."""
        live = [j for j in self.live if self.loose(j)]
        if not live:
            return {'new': 0}
        gs = self.groups_among(live, cap)
        out = {}
        if compare_cap:
            other = self.groups_among(live, 3 if cap is None else None)
            out['cap_agrees'] = sorted(map(sorted, gs)) == sorted(map(sorted, other))
            out['max_group'] = max((len(g) for g in gs), default=0)
        use = defaultdict(int)
        for g in gs:
            for j in g:
                use[j] += 1
        lo = {j: self.loose(j) for j in live}
        if any(use[j] > len(lo[j]) for j in live):
            return None
        all_loose = sorted(b for j in live for b in lo[j])
        plan, taken = [], {j: 0 for j in live}
        for g in gs:
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
            jid = len(self.bits_of)
            self.bits_of.append(list(bits))
            self.nbr.append(set())
            for b in bits:
                for o in self.owner[b]:
                    self.nbr[o].add(jid)
                    self.nbr[jid].add(o)
                self.owner[b].append(jid)
            self.parents.append(len(bits))
            self.fresh.append(0)
            self.round_of.append(self.rounds)
            self.demand_at_birth.append(None)
            new.append(jid)
        nxt = self.groups_among(new, cap)
        demand = defaultdict(int)
        for g in nxt:
            for j in g:
                demand[j] += 1
        info = []
        for jid in new:
            old_bits = self.bits_of[jid]
            implied = sorted(old_bits) == all_loose
            if self.linalg:
                lin = self._reduce(self._mask(old_bits)) == 0
                if lin != implied:
                    self.implied_mismatch += 1
            info.append(dict(j=jid, p=len(old_bits), d=demand[jid], implied=implied,
                             parent_fresh=[self.fresh[o] for b in old_bits for o in self.owner[b] if o != jid]))
        ks = rule(self, info, rng)
        for jid, k, inf in zip(new, ks, info):
            if k == 0 and not inf['implied']:
                raise ValueError('a rule dropped old states: zero fresh bits on a junction whose parity is not implied')
            for _ in range(k):
                b = self.nbits
                self.nbits += 1
                self.bits_of[jid].append(b)
                self.owner[b] = [jid]
            self.fresh[jid] = k
            self.demand_at_birth[jid] = inf['d']
            if self.linalg:
                self._add_row(jid)
        self.live = [j for j in new if self.fresh[j] > 0]
        out['new'] = len(new)
        return out

    # -- summaries -----------------------------------------------------------------------------------------------------------------
    def counts_by_round(self):
        c = defaultdict(int)
        for r in self.round_of:
            c[r] += 1
        return [c[r] for r in range(self.rounds + 1)]

    def offshoots_by_round(self):
        c = defaultdict(int)
        for j, r in enumerate(self.round_of):
            if self.parents[j] == 1:
                c[r] += 1
        return [c[r] for r in range(self.rounds + 1)]

    def forced_bits(self):
        """Bits with one value in every allowed state: the bridges of the junction graph with every loose bit wired to one
        outside vertex (a cut of size one)."""
        n = len(self.bits_of)
        OUT = n
        adj = defaultdict(list)          # vertex -> [(other, bit)]
        for b, js in self.owner.items():
            u, v = (js[0], OUT) if len(js) == 1 else (js[0], js[1])
            adj[u].append((v, b))
            adj[v].append((u, b))
        disc, low, bridges, t = {}, {}, [], 0
        for root in list(adj):
            if root in disc:
                continue
            disc[root] = low[root] = t
            t += 1
            stack = [(root, None, iter(adj[root]))]
            while stack:
                u, pb, it = stack[-1]
                advanced = False
                for v, b in it:
                    if b == pb:
                        continue
                    if v not in disc:
                        disc[v] = low[v] = t
                        t += 1
                        stack.append((v, b, iter(adj[v])))
                        advanced = True
                        break
                    low[u] = min(low[u], disc[v])
                if not advanced:
                    stack.pop()
                    if stack:
                        w = stack[-1][0]
                        low[w] = min(low[w], low[u])
                        if low[u] > disc[w]:
                            bridges.append(pb)
        return sorted(bridges)


# -- count rules -----------------------------------------------------------------------------------------------------------------
# A rule returns one fresh count per new junction.  `floored` keeps every old allowed state and makes every junction hold at least
# three bits (the program's smallest knot); at a junction whose parity is already implied it applies no floor (openness wins: fresh
# bits there would have a forced parity).

def floored(inf, k):
    if inf['implied']:
        return k
    return max(k, 3 - inf['p'], 1)


def uniform(c):
    def rule(P, info, rng):
        return [c for _ in info]
    rule.__name__ = f'uniform{c}'
    return rule


def fewest(P, info, rng):
    """The fewest fresh bits that keep the next round available, every junction a knot and every old state allowed."""
    return [floored(i, i['d']) for i in info]


def axis(P, info, rng):
    """The demand, and one surplus bit at every offshoot."""
    return [floored(i, i['d'] + (1 if i['p'] == 1 else 0)) for i in info]


def inherit(how):
    def rule(P, info, rng):
        return [floored(i, how(i['parent_fresh'])) for i in info]
    rule.__name__ = f'inherit_{how.__name__}'
    return rule


def balance(P, info, rng):
    """As many fresh bits as old ones taken."""
    return [floored(i, i['p']) for i in info]


def blind(K):
    def rule(P, info, rng):
        return [floored(i, rng.randint(1, K)) for i in info]
    rule.__name__ = f'blind{K}'
    return rule


def surplus(q):
    def rule(P, info, rng):
        return [floored(i, i['d'] + (1 if (i['d'] > 0 and rng.random() < q) else 0)) for i in info]
    rule.__name__ = f'surplus{q}'
    return rule


def crossed_then_fewest(a):
    """Fewest, except that each junction of round a - 1 (the level below the top of the 2^a pattern) gets one surplus bit."""
    def rule(P, info, rng):
        ks = fewest(P, info, rng)
        return [k + (1 if P.rounds == a - 1 else 0) for k in ks]
    rule.__name__ = f'crossed{a}'
    return rule


def run(a, rule, rounds, cap=None, seed=0, max_junctions=2000, linalg=False, compare_cap=False):
    rng = random.Random(seed)
    P = Presentation(a, linalg=linalg)
    outcome, log = 'alive', []
    for _ in range(rounds):
        r = P.step(rule, cap, rng, compare_cap=compare_cap)
        if r is None:
            outcome = 'stall'
            break
        log.append(r)
        if r['new'] == 0:
            outcome = 'closed'
            break
        if len(P.bits_of) > max_junctions:
            outcome = 'big'
            break
    return P, outcome, log
