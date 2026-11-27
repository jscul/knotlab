"""nae_pres.py LAW OUT.jsonl: part (d), the reader's question under each law.  ONE-STATEMENT-20261127-001; README.md.

For each census start S: its allowed states under LAW (nae or parity) on its named distinctions, and its loose set.
A presentation of that pair is a set of as many knots as S has, each holding at least three distinctions, each loose
distinction held once and every other twice, connected, whose allowed states under LAW are exactly S's.  Each knot's
support must allow every state of S (under parity: an even number of ones; under not-all-equal: not all equal), so the
search runs over those supports only, covering the first short distinction first.  Recorded per start: the number of
presentations, of distinct family partitions (families as groups of loose distinctions) and of distinct trees."""
import sys, json, itertools, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research' / 'MARKED-LOOSE-20261127-001'))
import presentations as PR
forbid = PR.forbid


def allowed(sup, names, law):
    idx = {x: i for i, x in enumerate(names)}; n = len(names); masks = [sum(1 << idx[x] for x in r) for r in sup]
    out = []
    for s in range(1 << n):
        ok = True
        for m in masks:
            c = bin(s & m).count('1')
            if (law == 'parity' and c % 2) or (law == 'nae' and (c == 0 or c == bin(m).count('1'))): ok = False; break
        if ok: out.append(s)
    return frozenset(out)


def presentations(S, law, limit=20000):
    names = sorted({x for r in S for x in r}); n = len(names); idx = {x: i for i, x in enumerate(names)}
    h = forbid.holders(S); target = [1 if len(h[x]) == 1 else 2 for x in names]
    sol = allowed(S, names, law)
    def valid(T):
        k = bin(T).count('1')
        for s in sol:
            c = bin(s & T).count('1')
            if (law == 'parity' and c % 2) or (law == 'nae' and (c == 0 or c == k)): return False
        return True
    cands = [T for T in range(1 << n) if bin(T).count('1') >= 3 and valid(T)]
    by_col = collections.defaultdict(list)
    for T in cands:
        for j in range(n):
            if (T >> j) & 1: by_col[j].append(T)
    found = []; k = len(S)
    def dfs(chosen, counts):
        if len(found) >= limit: return
        short = [j for j in range(n) if counts[j] < target[j]]
        if not short:
            if len(chosen) == k: found.append(tuple(sorted(chosen)))
            return
        if len(chosen) >= k: return
        j = short[0]
        for T in by_col[j]:
            if chosen and T < chosen[-1] and False: continue
            if T in chosen: continue
            ok = all(counts[i] + ((T >> i) & 1) <= target[i] for i in range(n))
            if ok:
                new = [counts[i] + ((T >> i) & 1) for i in range(n)]
                dfs(chosen + [T], new)
    dfs([], [0] * n)
    uniq = sorted(set(found))
    pres = []
    for P in uniq:
        sup = tuple(tuple(names[j] for j in range(n) if (T >> j) & 1) for T in P)
        if PR.connected(sup) and allowed(sup, names, law) == sol: pres.append(sup)
    return pres, len(found) >= limit


if __name__ == '__main__':
    law, out = sys.argv[1], sys.argv[2]
    tally = collections.Counter()
    with open(out, 'w') as f:
        for i, s in enumerate(forbid.census()):
            S = forbid.supports_of(s)
            pres, capped = presentations(S, law)
            trees = {PR.tree_of(P) for P in pres}; parts = {t[0] for t in trees}
            own = PR.tree_of(S)
            rec = {'start': 'census %d' % i, 'presentations': len(pres), 'capped': capped, 'family partitions': len(parts),
                   'trees': len(trees), 'own tree among them': own in trees}
            if len(trees) > 1: rec['example'] = [list(map(list, P)) for P in pres[:2]]
            tally['starts'] += 1; tally['one presentation'] += len(pres) == 1
            tally['partition not fixed'] += len(parts) > 1; tally['tree not fixed'] += len(trees) > 1; tally['capped'] += capped
            tally['own presentation missing'] += not (own in trees)
            f.write(json.dumps(rec) + '\n'); f.flush()
        f.write(json.dumps({'tally': dict(tally)}) + '\n')
    print(dict(tally))
