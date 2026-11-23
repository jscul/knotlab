"""Count-level engine for ordinary growth, the guarded serial rule and the recompute-after-every-birth rule.

A presentation is kept as neighbour sets, loose counts, parents and children of knots. Distinction names are dropped:
the proposals, the demand of a newborn and the loose count of every knot depend on the neighbour sets and loose counts
only (checked against the recorded implementation by `crosscheck_*` in gate.py). The rules are those of

* ordinary growth: experiments/ORDINARY-DYNAMICS-20261120-001A/.../end_operator.py (`step`) via GENERATORS fixtures.literal_turn;
* the unguarded serial rule: experiments/TICK-BIRTHS-AND-SCARCITY-20261121-001B/.../raw.py (`facts`, `pool`, `apply`);
* the guarded serial rule: the same study's replay.py (`restored_plan`, `SerialReplay.write`).
"""
from collections import Counter, defaultdict
from itertools import combinations
import copy


def maximal_cliques(cand, verts):
    out = []
    stack = [(set(), set(verts), set())]
    while stack:
        R, P, X = stack.pop()
        if not P and not X:
            out.append(R)
            continue
        if not P:
            continue
        u = max(P | X, key=lambda y: len(cand[y] & P))
        for v in list(P - cand[u]):
            stack.append((R | {v}, P & cand[v], X & cand[v]))
            P.discard(v)
            X.add(v)
    return out


class Pres:
    """Knots 0..n-1. `loose[k]` is the number of loose distinctions, `nbr[k]` the knots sharing a distinction with k."""

    def __init__(self, nbr, loose, par, depth, nsource, fresh=None):
        self.nbr = nbr
        self.loose = loose
        self.par = par
        self.depth = depth
        self.nsource = nsource
        self.kids = [set() for _ in nbr]
        for k, ps in enumerate(par):
            for p in ps:
                self.kids[p].add(k)
        self.fresh = fresh if fresh is not None else list(loose)
        self.log = []          # (parents, child, fresh) of every birth written by `spend`
        self.spent_last = {}   # knot -> 1-based event number whose birth took its last loose distinction

    @classmethod
    def from_stars(cls, stars):
        owners = defaultdict(list)
        for k, support in enumerate(stars):
            for d in support:
                owners[d].append(k)
        nbr = [set() for _ in stars]
        loose = [0] * len(stars)
        for holders in owners.values():
            if len(holders) == 1:
                loose[holders[0]] += 1
            else:
                a, b = holders
                assert a != b and len(holders) == 2
                nbr[a].add(b)
                nbr[b].add(a)
        n = len(stars)
        return cls(nbr, loose, [()] * n, [0] * n, n)

    def copy(self):
        c = copy.copy(self)
        c.nbr = [set(s) for s in self.nbr]
        c.loose = list(self.loose)
        c.par = list(self.par)
        c.depth = list(self.depth)
        c.kids = [set(s) for s in self.kids]
        c.fresh = list(self.fresh)
        c.log = list(self.log)
        c.spent_last = dict(self.spent_last)
        return c

    def __len__(self):
        return len(self.nbr)

    # -- proposals ---------------------------------------------------------------------------------------------------
    def candidate_graph(self, live):
        cand = defaultdict(set)
        ws = set()
        for u in live:
            ws |= self.nbr[u]
        for w in ws:
            ln = [u for u in self.nbr[w] if u in live]
            for u, v in combinations(ln, 2):
                cand[u].add(v)
                cand[v].add(u)
        return cand

    def groups_among(self, live):
        """The multi-parent groups among these live knots (freelib / fastlib `groups_among`, cap None)."""
        live = set(live)
        cand = self.candidate_graph(live)
        big = []
        for c in maximal_cliques(cand, [u for u in live if cand[u]]):
            if len(c) >= 3 and not set.intersection(*[self.nbr[x] for x in c]):
                big.append(tuple(sorted(c)))
        covered = set()
        for g in big:
            covered.update(combinations(g, 2))
        pairs = [(u, v) for u in sorted(live) for v in sorted(cand[u]) if u < v and (u, v) not in covered]
        return sorted(big) + pairs

    def moves(self, limit_depth=None):
        """(groups, unary) the unguarded rule admits now: raw.moves / raw.facts."""
        live = {k for k in range(len(self)) if self.loose[k]}
        groups = []
        for g in self.groups_among(live):
            if set.intersection(*[self.kids[j] for j in g]):
                continue
            if limit_depth is not None and 1 + max(self.depth[j] for j in g) > limit_depth:
                continue
            groups.append(g)
        use = Counter(j for g in groups for j in g)
        unary = [(j,) for j in sorted(live) if self.loose[j] > use[j]
                 and (limit_depth is None or self.depth[j] + 1 <= limit_depth)]
        return groups, unary, use

    # -- one birth ---------------------------------------------------------------------------------------------------
    def spend(self, parents, fresh=None):
        """Write one birth. With `fresh` None the count is the recorded unguarded one: max(1, 3 - p, demand)."""
        assert all(self.loose[j] > 0 for j in parents)
        child = len(self)
        event = len(self.log) + 1
        for j in parents:
            self.loose[j] -= 1
            if self.loose[j] == 0:
                self.spent_last[j] = event
        self.nbr.append(set(parents))
        for j in parents:
            self.nbr[j].add(child)
        for j in parents:
            self.kids[j].add(child)
        self.kids.append(set())
        self.par.append(tuple(sorted(parents)))
        self.depth.append(1 + max((self.depth[j] for j in parents), default=-1))
        self.loose.append(0)
        if fresh is None:
            live = {k for k in range(len(self)) if self.loose[k]} | {child}
            demand = sum(1 for g in self.groups_among(live) if child in g)
            fresh = max(1, 3 - len(parents), demand)
        self.loose[child] = fresh
        self.fresh.append(fresh)
        self.log.append((tuple(sorted(parents)), child, fresh))
        return child, fresh


def ordinary_layer(pres, law="parity"):
    """The plan of one complete ordinary parent step on the presentation: parents, fresh counts, or the shortages.

    Recomputed here from the live knots (every knot with a loose distinction) exactly as end_operator.step does."""
    live = {k for k in range(len(pres)) if pres.loose[k]}
    if not live:
        return "closed", (), (), ()
    multi = [g for g in pres.groups_among(live)]
    used = Counter(j for g in multi for j in g)
    scarce = tuple((k, used[k] - pres.loose[k]) for k in sorted(live) if used[k] > pres.loose[k])
    if scarce:
        return "stall", (), (), scarce
    parents = list(multi) + [(k,) for k in sorted(live) for _ in range(pres.loose[k] - used[k])]
    # demand: groups of the children among themselves; children of one parent form a block
    sib = defaultdict(set)
    for i, g in enumerate(parents):
        for p in g:
            sib[p].add(i)
    cand = defaultdict(set)
    for blk in sib.values():
        for a, b in combinations(sorted(blk), 2):
            cand[a].add(b)
            cand[b].add(a)
    blocks = [frozenset(b) for b in sib.values()]
    big = []
    for c in maximal_cliques(cand, [u for u in range(len(parents)) if cand[u]]):
        if len(c) >= 3 and not any(c <= b for b in blocks):
            big.append(tuple(sorted(c)))
    covered = set()
    for g in big:
        covered.update(combinations(g, 2))
    demand = Counter()
    for g in big:
        for i in g:
            demand[i] += 1
    for u in range(len(parents)):
        for v in cand[u]:
            if u < v and (u, v) not in covered:
                demand[u] += 1
                demand[v] += 1
    implied = law == "parity" and len(parents) == 1
    fresh = tuple(0 if implied else max(1, 3 - len(g), demand[i]) for i, g in enumerate(parents))
    return "extend", tuple(parents), fresh, ()


def apply_layer(pres, parents, fresh):
    """Write every birth of a funded parent step, in the order given."""
    for g, f in zip(parents, fresh, strict=True):
        pres.spend(g, f)
