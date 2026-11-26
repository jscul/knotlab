"""split.py: for each element of B on a stage, every partition of its support into distinction-disjoint cycles, and
whether some partition has three or more parts that are each a class label (even on every shortest change) and not read
by one knot: the advisor's criterion for a binding among independently carried facts made by the knots' laws."""
import sys, collections, itertools
sys.path.insert(0, '.')
import forced as FD, binding as BD
classes, forbid = FD.classes, FD.forbid
MC = BD.MC


def stage_data(st):
    names = sorted({x for r in st for x in r}); idx = {x: i for i, x in enumerate(names)}; n = len(names)
    holders = collections.defaultdict(list)
    for k, r in enumerate(st):
        for x in r: holders[x].append(k)
    rows = [sum(1 << idx[x] for x in r) for r in st]
    loose = sum(1 << idx[x] for x, h in holders.items() if len(h) == 1)
    Z = classes.nullspace(rows, n)
    B = FD.intersect(FD.intersect(rows, Z, n), classes.nullspace([1 << i for i in range(n) if (loose >> i) & 1], n), n)
    _, idx2, moves = MC.moves_of(st)
    local = []
    for r in st:
        ks = [idx[x] for x in r]
        mrows = [sum(((m >> i) & 1) << j for j, i in enumerate(ks)) for m in moves]
        local.append([sum(((v >> j) & 1) << i for j, i in enumerate(ks)) for v in classes.nullspace(mrows, len(ks))])
    return names, idx, holders, rows, Z, B, moves, local


def cycles_in(support, names, holders):
    """every simple cycle using only the support's distinctions (as bitmasks)"""
    es = [i for i in range(len(names)) if (support >> i) & 1]
    adj = collections.defaultdict(list)
    for i in es:
        h = holders[names[i]]; a, b = (h[0], h[1]) if len(h) == 2 else (h[0], 'U')
        adj[a].append((b, i)); adj[b].append((a, i))
    out = set(); verts = sorted(adj, key=str)
    for s in verts:
        def dfs(v, usedv, mask):
            for w, e in adj[v]:
                if (mask >> e) & 1: continue
                if w == s: out.add(mask | (1 << e)); continue
                if w in usedv or str(w) < str(s): continue
                dfs(w, usedv | {w}, mask | (1 << e))
        dfs(s, {s}, 0)
    return sorted(out)


def partitions(support, cyc):
    if support == 0: yield []; return
    low = support & -support
    for c in cyc:
        if (c & low) and (c & support) == c:
            for rest in partitions(support ^ c, [d for d in cyc if not (d & c)]):
                yield [c] + rest


def judge(st):
    names, idx, holders, rows, Z, B, moves, local = stage_data(st)
    def label(f): return all(bin(f & m).count('1') % 2 == 0 for m in moves) and any(bin(f & z).count('1') % 2 for z in Z)
    def unread(f): return not any(classes.rank(rows + loc + [f]) == classes.rank(rows + loc) for loc in local)
    res = []
    for v in B:
        cyc = cycles_in(v, names, holders); best = 0; count = 0
        for P in partitions(v, cyc):
            count += 1
            good = sum(1 for c in P if label(c) and unread(c))
            if len(P) >= 3 and good == len(P): best = max(best, len(P))
            if count > 20000: break
        res.append({'size': bin(v).count('1'), 'partitions read': count, 'parts in the best binding partition': best})
    return res


if __name__ == '__main__':
    S = forbid.supports_of(forbid.sampled(7, 300, 20261206 + 7)[239]); st = S
    for t in range(1, 4):
        st, status, births = forbid.grown(st, 'parity', 'ordinary')
        print('held out 7-239 round', t, judge(st), flush=True)
