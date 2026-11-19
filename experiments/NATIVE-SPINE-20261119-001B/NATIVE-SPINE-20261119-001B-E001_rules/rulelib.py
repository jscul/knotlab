"""Three spine rules and the uniqueness of the spine matching (NATIVE-SPINE-20261119-001B).

The growth and the spine relation are JUNCTION-KINDS' (`spinelib.py`): a junction j of round t is related to its ancestors at exact
depths 2 and 3, each with m(a, j) parent chains.  Each rule keeps, for every j, a subset of those ancestors:
- N (the newest ancestor): the ancestors at depth 2, the newer of the two rounds;
- M (most chains): the ancestors, at either depth, with the largest m(a, j);
- F (fewest chains): those with the smallest.
A rule picks the spine at round t when the relation it keeps is a perfect matching of round t with rounds t - 2 and t - 3 together:
every j keeps exactly one ancestor, and every junction of those two rounds is kept by exactly one j.
The full relation's perfect matching is unique exactly when the relation has no alternating cycle (Hopcroft-Karp's matching,
then a cycle search in the graph directed left to right along unmatched pairs and right to left along matched ones)."""
import importlib.util
import sys
from collections import Counter, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_spec = importlib.util.spec_from_file_location('jk_spinelib', ROOT / 'experiments/JUNCTION-KINDS-20261119-001B/JUNCTION-KINDS-20261119-001B-E001_kinds/spinelib.py')
S = importlib.util.module_from_spec(_spec)
sys.modules['jk_spinelib'] = S
sys.path.insert(0, str(_spec.origin and Path(_spec.origin).parent))
_spec.loader.exec_module(S)


def relation(par, by_round, t):
    """{j: {(depth, a): m}} for round t."""
    return {j: {(k, a): m for k in (2, 3) for a, m in S.ancestors(par, j, k).items()} for j in by_round[t]}


def keep(rel, rule):
    out = {}
    for j, cand in rel.items():
        if rule == 'N':
            out[j] = [x for x in cand if x[0] == 2]
        else:
            best = (max if rule == 'M' else min)(cand.values())
            out[j] = [x for x, m in cand.items() if m == best]
    return out


def is_perfect(kept, by_round, t):
    right = Counter(x for v in kept.values() for x in v)
    rset = {(2, a) for a in by_round.get(t - 2, [])} | {(3, a) for a in by_round.get(t - 3, [])}
    ones = sum(1 for v in kept.values() if len(v) == 1)
    return {'left_with_one': ones, 'left': len(kept), 'right_hit_once': sum(1 for x in rset if right.get(x, 0) == 1),
            'right': len(rset), 'perfect': ones == len(kept) and all(right.get(x, 0) == 1 for x in rset) and set(right) <= rset}


def match_assignment(left, adj):
    """Hopcroft-Karp returning the matching {left: right}."""
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
        stack, path = [(u, iter(adj[u]))], []
        while stack:
            x, it = stack[-1]
            moved = False
            for v in it:
                w = mv.get(v)
                if w is None:
                    for y, vv in zip([s[0] for s in stack], path + [v]):
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

    while True:
        found, dist = bfs()
        if not found:
            break
        for u in left:
            if mu[u] is None:
                dfs(u, dist)
    return mu


def unique_perfect(rel):
    """(perfect, unique): a perfect matching exists, and it is the only one (no alternating cycle)."""
    left = list(rel)
    adj = {j: list(c) for j, c in rel.items()}
    mu = match_assignment(left, adj)
    right = {x for c in rel.values() for x in c}
    if any(v is None for v in mu.values()) or len(right) != len(left):
        return False, None
    mv = {v: u for u, v in mu.items()}
    # directed graph: left u -> right v (unmatched), right v -> left mv[v]; an alternating cycle is a directed cycle
    nodes = [('L', u) for u in left] + [('R', v) for v in right]
    nxt = {('L', u): [('R', v) for v in adj[u] if v != mu[u]] for u in left}
    nxt.update({('R', v): [('L', mv[v])] for v in right})
    color = {n: 0 for n in nodes}
    for s in nodes:
        if color[s]:
            continue
        stack = [(s, iter(nxt[s]))]
        color[s] = 1
        while stack:
            n, it = stack[-1]
            adv = False
            for w in it:
                if color[w] == 1:
                    return True, False
                if color[w] == 0:
                    color[w] = 1
                    stack.append((w, iter(nxt[w])))
                    adv = True
                    break
            if not adv:
                color[n] = 2
                stack.pop()
    return True, True


def forced_fraction(rel):
    """Share of the round's junctions whose partner is the same in every perfect matching (the ceiling of the advisor's
    forced-choice reading of "newest"): matched pairs whose ends lie in different strongly connected components of the
    alternating digraph.  None if there is no perfect matching."""
    left = list(rel)
    adj = {j: list(c) for j, c in rel.items()}
    mu = match_assignment(left, adj)
    if any(v is None for v in mu.values()):
        return None
    mv = {v: u for u, v in mu.items()}
    right = {x for c in rel.values() for x in c}
    nodes = [('L', u) for u in left] + [('R', v) for v in right]
    nxt = {('L', u): [('R', v) for v in adj[u] if v != mu[u]] for u in left}
    nxt.update({('R', v): ([('L', mv[v])] if v in mv else []) for v in right})
    index, low, onst, st, comp, c = {}, {}, set(), [], {}, 0
    counter = 0
    for s in nodes:
        if s in index:
            continue
        work = [(s, iter(nxt[s]))]
        index[s] = low[s] = counter
        counter += 1
        st.append(s)
        onst.add(s)
        while work:
            n, it = work[-1]
            adv = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = counter
                    counter += 1
                    st.append(w)
                    onst.add(w)
                    work.append((w, iter(nxt[w])))
                    adv = True
                    break
                if w in onst:
                    low[n] = min(low[n], index[w])
            if adv:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[n])
            if low[n] == index[n]:
                while True:
                    w = st.pop()
                    onst.discard(w)
                    comp[w] = c
                    if w == n:
                        break
                c += 1
    forced = sum(1 for u in left if comp[('L', u)] != comp[('R', mu[u])])
    return forced / len(left)


def rule_stats(kept, rel):
    """Ties, depth split and collisions of a rule's single picks."""
    single = {j: v[0] for j, v in kept.items() if len(v) == 1}
    hits = Counter(single.values())
    return {'ties': sum(1 for v in kept.values() if len(v) > 1), 'single': len(single),
            'single_depth2': sum(1 for x in single.values() if x[0] == 2),
            'collided_singles': sum(1 for x in single.values() if hits[x] > 1),
            'kept_depth2_share': (sum(1 for v in kept.values() for x in v if x[0] == 2) / max(1, sum(len(v) for v in kept.values())))}


def shuffled_has_perfect(rel, seed, swaps_per_edge=10):
    """Null: a degree-preserving shuffle of the relation (double swaps), then whether it still has a perfect matching."""
    import random
    rng = random.Random(seed)
    edges = [(j, x) for j, c in rel.items() for x in c]
    have = set(edges)
    for _ in range(swaps_per_edge * len(edges)):
        i, k = rng.randrange(len(edges)), rng.randrange(len(edges))
        (u1, v1), (u2, v2) = edges[i], edges[k]
        if u1 == u2 or v1 == v2 or (u1, v2) in have or (u2, v1) in have:
            continue
        have -= {(u1, v1), (u2, v2)}
        have |= {(u1, v2), (u2, v1)}
        edges[i], edges[k] = (u1, v2), (u2, v1)
    adj = {j: [] for j in rel}
    for u, v in edges:
        adj[u].append(v)
    mu = match_assignment(list(rel), adj)
    return all(v is not None for v in mu.values())
