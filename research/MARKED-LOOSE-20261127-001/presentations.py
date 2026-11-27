"""presentations.py OUT.jsonl: what the allowed states and the marked loose distinctions tell a reader of the families'
tree.  MARKED-LOOSE-20261127-001; README.md.

A reader sees a start's allowed states (the solutions of its parity laws) on its named distinctions, and which of them
are loose.  Any other start with the same allowed states and the same loose set is, to that reader, the same start.
For each census start S: every *presentation* of the same pair, that is every set of knots (as many as S has, each a
law in S's law space, with at least three places) in which each loose distinction is held once and every other
distinction twice, whose laws span S's law space (so the allowed states are the same) and whose knots are connected;
for each, its families (live knots joined when some knot shares a distinction with each), each as its group of loose
distinctions, and its tree (for every threshold of the families' distance d, the partition of the loose distinctions
into the clusters of families joined at d at most that threshold).  Recorded: the number of presentations, how many
distinct family partitions and distinct trees they give."""
import sys, json, itertools, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
for d in ('BUILT-BINDING-20261126-001', 'THIRD-LAYER-20261126-001', 'SELECTED-KNOTS-20261127-001'): sys.path.insert(0, str(ROOT / 'research' / d))
import repro as RP, twokinds as TK, tree as TR
classes, forbid = RP.classes, RP.forbid


def span_all(rows):
    out = {0}
    for r in rows: out |= {x ^ r for x in out}
    return sorted(out)


def presentations(S, limit=20000):
    names, idx, rows = RP.space(S); n = len(names)
    h = forbid.holders(S)
    target = [1 if len(h[x]) == 1 else 2 for x in names]
    L = span_all(rows); r = classes.rank(rows); k = len(S)
    cands = [v for v in L if bin(v).count('1') >= 3]
    found = []
    def dfs(start, chosen, counts):
        if len(found) >= limit: return
        if len(chosen) == k:
            if counts == target and classes.rank(chosen) == r: found.append(list(chosen))
            return
        # prune: a distinction still short needs a later vector holding it
        for i in range(start, len(cands)):
            v = cands[i]; ok = True; new = list(counts)
            for j in range(n):
                if (v >> j) & 1:
                    new[j] += 1
                    if new[j] > target[j]: ok = False; break
            if ok: dfs(i + 1, chosen + [v], new)
    dfs(0, [], [0] * n)
    pres = []
    for P in found:
        sup = tuple(tuple(names[j] for j in range(n) if (v >> j) & 1) for v in P)
        pres.append(sup)
    return pres, len(found) >= limit


def connected(sup):
    h = forbid.holders(sup); parent = list(range(len(sup)))
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for x, hs in h.items():
        for q in hs[1:]: parent[find(q)] = find(hs[0])
    return len({find(i) for i in range(len(sup))}) == 1


def tree_of(sup):
    fams, ls = TK.families(sup)
    groups = [frozenset(l) for l in ls]
    if len(fams) < 2: return frozenset(groups), frozenset()
    D = TR.distances(sup, fams)
    levels = []
    for thr in sorted(set(D.values())):
        parent = list(range(len(fams)))
        def find(a):
            while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
            return a
        for (i, j), d in D.items():
            if d <= thr: parent[find(i)] = find(j)
        cl = collections.defaultdict(set)
        for i in range(len(fams)): cl[find(i)] |= groups[i]
        levels.append((thr, frozenset(frozenset(c) for c in cl.values())))
    return frozenset(groups), frozenset(levels)


if __name__ == '__main__':
    out = sys.argv[1]
    tally = collections.Counter()
    with open(out, 'w') as f:
        for name, S in TK.items('census', 10 ** 9) if False else ((('census %d' % i), forbid.supports_of(s)) for i, s in enumerate(forbid.census())):
            pres, capped = presentations(S)
            pres = [P for P in pres if connected(P)]
            trees = {tree_of(P) for P in pres}
            parts = {t[0] for t in trees}
            own = tree_of(S)
            rec = {'start': name, 'presentations': len(pres), 'capped': capped, 'family partitions': len(parts),
                   'trees': len(trees), 'own tree among them': own in trees}
            tally['starts'] += 1; tally['partition not recovered'] += len(parts) > 1; tally['tree not recovered'] += len(trees) > 1
            tally['capped'] += capped
            if len(trees) > 1:
                rec['example'] = [[list(map(list, P)) for P in pres[:1]], [list(map(list, P)) for P in pres if tree_of(P) != own][:1]]
            f.write(json.dumps(rec) + '\n'); f.flush()
        f.write(json.dumps({'tally': dict(tally)}) + '\n')
    print(dict(tally))
