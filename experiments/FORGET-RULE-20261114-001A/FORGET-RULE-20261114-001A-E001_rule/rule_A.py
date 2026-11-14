"""FORGET-RULE-20261114-001A, the thread's sufficient rule A: separation of the top ports from the depth-r ports in the peeled
layered composite, along every call word, decided by a finite top-down automaton (the advisor's construction, with a free-from-above
flag so that a child port nothing above constrains can be peeled where it occurs once). Rule A implies forgetting (proved in the
pre-registration): every peeling it performs eliminates a distinction occurring in exactly one constraint of the composite, which is
exact for NAE, and a disconnected system has a product solution set."""
import itertools, json, sys
from pathlib import Path
R = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(R / "experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex"))
import reach_dp as DP


def full2(rel):
    S = [s for s in range(len(rel)) if rel[s]]
    for drop in range(3):
        keep = [j for j in range(3) if j != drop]
        if len({tuple((s >> j) & 1 for j in keep) for s in S}) < 4:
            return False
    return True


def block_step(flat, chosen, G, holder, nports, free_ports):
    """Peel the block of `flat` with call `chosen` as the outgoing interface. Ports in free_ports are peelable. Returns
    (partition of the 'top' port nodes and 'bottom' argument positions as a list of labels, set of free argument positions)."""
    calls = flat["calls"]
    hyper = []
    for j, (c, a) in enumerate(calls):
        if j == chosen:
            continue
        if c == "K":
            hyper.append([set(a), True])
        else:
            g = G[c]
            if g.all():
                continue
            hyper.append([set(a), full2(g)])
    args = list(calls[chosen][1])
    interface = set(args) | {p for p in range(nports) if p not in free_ports}
    changed = True
    while changed:
        changed = False
        cnt = {}
        for h, _ in hyper:
            for x in h:
                cnt[x] = cnt.get(x, 0) + 1
        for idx, (h, peelable) in enumerate(hyper):
            if peelable and any(cnt[x] == 1 and x not in interface for x in h):
                hyper.pop(idx); changed = True; break
    par = {}
    def f(x):
        par.setdefault(x, x)
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for h, _ in hyper:
        h = list(h)
        for x in h[1:]:
            par[f(x)] = f(h[0])
    used = {x for h, _ in hyper for x in h}
    free_args = set()
    for k, x in enumerate(args):
        if x not in used and (x >= nports or x in free_ports):
            free_args.add(k)
    # node labels: top j -> f(j); bottom k -> f(args[k])
    top = [f(j) for j in range(nports)]
    bottom = [f(x) for x in args]
    return top, bottom, free_args


def canon(partition_labels):
    seen = {}
    return tuple(seen.setdefault(l, len(seen)) for l in partition_labels)


def transition(state, top, bottom, free_args):
    sigma, marks, _ = state
    nt = len(sigma)
    par = {}
    def f(x):
        par.setdefault(x, x)
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    def un(a, b):
        par[f(a)] = f(b)
    for j in range(nt):
        un(("t", j), ("s", sigma[j]))
        un(("t", j), ("p", top[j]))
    for k in range(3):
        un(("b", k), ("p", bottom[k]))
    marked_roots = {f(("s", m)) for m in marks}
    lab = [f(("b", k)) for k in range(3)]
    s2 = canon(lab)
    m2 = frozenset(s2[k] for k in range(3) if lab[k] in marked_roots)
    return (s2, m2, frozenset(free_args))


def decide(defs, max_states=10_000):
    prep = DP.Preparation(defs)
    S = prep.flat(prep.S)
    selfs = [j for j, (c, _) in enumerate(S["calls"]) if c == prep.S]
    steps = {}
    def S_step(i, F):
        key = (i, F)
        if key not in steps:
            steps[key] = block_step(S, i, prep.G, prep.S, 3, F)
        return steps[key]
    # start: a generic copy of S (every stretch of the tree must forget for the gap argument, not only those from main's top);
    # nothing is assumed free from above, which only peels less and so stays sound
    starts = set()
    init = (tuple(range(3)), frozenset(range(3)), frozenset())
    for i in selfs:
        top, bottom, fa = S_step(i, frozenset())
        starts.add(transition(init, top, bottom, fa))
    live = lambda st: bool(st[1])
    graph, frontier = {}, [s for s in starts if live(s)]
    seen = set(frontier)
    while frontier:
        st = frontier.pop()
        nxt = set()
        for i in selfs:
            top, bottom, fa = S_step(i, st[2])
            t = transition(st, top, bottom, fa)
            if live(t):
                nxt.add(t)
        graph[st] = nxt
        for t in nxt:
            if t not in seen:
                seen.add(t); frontier.append(t)
        if len(seen) > max_states:
            return dict(rule_A=None, reason="cap")
    # cycle detection and longest path among live states
    color, depth = {}, {}
    sys.setrecursionlimit(10000)
    def dfs(u):
        color[u] = 1; best = 0
        for v in graph.get(u, ()):
            if color.get(v) == 1:
                return None
            if color.get(v) is None:
                d = dfs(v)
                if d is None:
                    return None
            best = max(best, depth[v] + 1)
        color[u] = 2; depth[u] = best
        return best
    longest = 0
    for s in [s for s in starts if live(s)]:
        if color.get(s) is None:
            d = dfs(s)
            if d is None:
                return dict(rule_A=False, live_states=len(seen))
        longest = max(longest, depth[s] + 1)
    return dict(rule_A=True, r_bound=longest + 1, live_states=len(seen))
