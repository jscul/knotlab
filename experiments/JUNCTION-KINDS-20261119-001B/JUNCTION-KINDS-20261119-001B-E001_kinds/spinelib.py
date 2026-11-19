"""Out-shares, sum-equitable kinds and ancestor spines of a growth (JUNCTION-KINDS-20261119-001B).

- The parents of a junction born in round t >= 1 are the junctions of round t - 1 that gave it a bit; its share to each is 1/p.
- The out-share of j is s(j) = sum over its children c of 1/p(c).
- Sum-equitable kinds (forward): kind_0 is one kind; kind_h(j) is the map from kind_{h-1} classes to the total share j sends into
  each, over its children.  Refined to depth H, for junctions whose futures reach that depth.
- Ancestors at exact depth k: the junctions reached from j by k parent steps; m(a, j) is the number of parent chains from j to a.
- The spine relation at lags (l1, l2) between round t and rounds t - l1 and t - l2 relates j to its ancestors at those exact depths
  (all of them, or only those with m = 1).  A perfect matching between round t and the two earlier rounds together is found by
  Hopcroft-Karp."""
import sys
from collections import Counter, defaultdict, deque
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kindlib as K  # noqa: E402


def grow(st, rounds, maxj):
    P = K.start(st)
    for _ in range(rounds):
        r = P.step(K.E.J.F.fewest, None)
        if r is None or r['new'] == 0:
            break
        if len(P.bits_of) > maxj:
            break
    return P


def family(P):
    n = len(P.bits_of)
    par = [[] for _ in range(n)]
    ch = [[] for _ in range(n)]
    for c in range(n):
        if P.round_of[c] == 0:
            continue
        ps = sorted({o for b in P.bits_of[c][:P.parents[c]] for o in P.owner[b] if o != c})
        par[c] = ps
        for o in ps:
            ch[o].append(c)
    by_round = defaultdict(list)
    for j in range(n):
        by_round[P.round_of[j]].append(j)
    return par, ch, by_round


def out_shares(P, ch):
    return [sum((Fraction(1, P.parents[c]) for c in ch[j]), Fraction(0)) for j in range(len(ch))]


def sum_kinds(P, ch, H):
    n = len(ch)
    T = P.rounds
    kind = [0] * n
    tab = {}
    for h in range(1, H + 1):
        new = [None] * n
        for j in range(n):
            if P.round_of[j] + h <= T:
                tot = defaultdict(Fraction)
                for c in ch[j]:
                    tot[kind[c]] += Fraction(1, P.parents[c])
                new[j] = tab.setdefault((h, tuple(sorted(tot.items()))), len(tab))
        kind = [k if k is not None else -1 for k in new]
    return kind


def ancestors(par, j, k):
    """{ancestor: number of parent chains} at exact depth k."""
    cur = Counter({j: 1})
    for _ in range(k):
        nxt = Counter()
        for x, m in cur.items():
            for p in par[x]:
                nxt[p] += m
        cur = nxt
    return cur


def matching(left, adj):
    """Hopcroft-Karp; returns the size of a maximum matching.  adj[u] lists right vertices."""
    INF = float('inf')
    mu, mv = {u: None for u in left}, {}
    def bfs():
        dist, q, found = {}, deque(), False
        for u in left:
            if mu[u] is None:
                dist[u] = 0
                q.append(u)
            else:
                dist[u] = INF
        while q:
            u = q.popleft()
            for v in adj[u]:
                w = mv.get(v)
                if w is None:
                    found = True
                elif dist[w] == INF:
                    dist[w] = dist[u] + 1
                    q.append(w)
        return found, dist
    def dfs(u, dist):
        stack = [(u, iter(adj[u]))]
        path = []
        while stack:
            x, it = stack[-1]
            moved = False
            for v in it:
                w = mv.get(v)
                if w is None:
                    # augment along the stack
                    for (y, _), vv in zip(stack, path + [v]):
                        pass
                    seq = [s[0] for s in stack]
                    vs = path + [v]
                    for y, vv in zip(seq, vs):
                        mu[y] = vv
                        mv[vv] = y
                    return True
                if dist.get(w) == dist[x] + 1:
                    stack.append((w, iter(adj[w])))
                    path.append(v)
                    moved = True
                    break
            if not moved:
                dist[x] = INF
                stack.pop()
                if path:
                    path.pop()
        return False
    size = 0
    while True:
        found, dist = bfs()
        if not found:
            break
        for u in left:
            if mu[u] is None and dfs(u, dist):
                size += 1
    return size


def spine(P, par, by_round, t, lags, only_single=False):
    """Matching size, left size and right size of the spine relation at round t, and the degree sets on both sides."""
    left = by_round[t]
    right = set()
    for l in lags:
        right |= set(by_round.get(t - l, []))
    adj = {}
    for j in left:
        nb = []
        for l in lags:
            for a, m in ancestors(par, j, l).items():
                if not only_single or m == 1:
                    nb.append((l, a))
        adj[j] = nb
    deg_r = Counter(v for nb in adj.values() for v in nb)
    size = matching(left, adj)
    return {'t': t, 'left': len(left), 'right': len(right), 'matched': size,
            'deg_left': sorted(Counter(len(nb) for nb in adj.values()).items()),
            'deg_right': sorted(Counter(deg_r.get((l, a), 0) for l in lags for a in by_round.get(t - l, [])).items())}


def interval_types(par, j, k, memo=None):
    """{ancestor a at exact depth k: the unfolded chain type of [a, j]}: depth 0 is (); depth k is the sorted tuple of the types of
    [a, p] over j's parents p that reach a in k - 1 steps."""
    if k == 0:
        return {j: ()}
    out = defaultdict(list)
    for p in par[j]:
        for a, ty in interval_types(par, p, k - 1).items():
            out[a].append(ty)
    return {a: tuple(sorted(v)) for a, v in out.items()}


def typed_relation(P, par, by_round, t, lags):
    """[(j, lag, a, type)] for round t."""
    rel = []
    for j in by_round[t]:
        for l in lags:
            for a, ty in interval_types(par, j, l).items():
                rel.append((j, l, a, (l, ty)))
    return rel


def biregular_sets(rels, by_round, lags, types, max_size=4):
    """Subsets T of `types` (up to max_size) for which, on every round given, every junction of round t has the same number e of
    T-ancestors and every junction of rounds t - l has exactly e T-descendants in round t for each l; returns [(T, e)]."""
    import itertools
    good = []
    for size in range(1, max_size + 1):
        for T in itertools.combinations(types, size):
            Ts = set(T)
            e_all = set()
            ok = True
            for t, rel in rels.items():
                dl, dr = Counter(), Counter()
                for j, l, a, ty in rel:
                    if ty in Ts:
                        dl[j] += 1
                        dr[(l, a)] += 1
                vals = {dl.get(j, 0) for j in by_round[t]}
                vals |= {dr.get((l, a), 0) for l in lags for a in by_round.get(t - l, [])}
                e_all |= vals
                if len(e_all) != 1 or 0 in e_all:
                    ok = False
                    break
            if ok:
                good.append((T, e_all.pop()))
    return good
