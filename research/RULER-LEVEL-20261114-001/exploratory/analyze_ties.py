"""Exploratory: replay the keys of tree_plus_within.py (seed 7, 80 samples) and test, at N = 6, whether the within-level knots alone
(W) or the whole pattern (P) tie some sibling pair of the tree (forced equal or forced unequal), against the outcome in the log."""
import sys, random, re, collections
import numpy as np
from pysat.solvers import Cadical195
sys.path.insert(0, 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex')
from pattern import pattern
log = open('research/RULER-LEVEL-20261114-001/exploratory/tree_plus_within.log').read().splitlines()
outc = {}
for line in log:
    m = re.match(r'^(\d+) (ruler|NOT ruler|undecided|union dead)', line)
    if m: outc[int(m.group(1))] = m.group(2)
rng = random.Random(7); keys = []
for i in range(80):
    s = rng.choice([2, 3]); W = 1 + s + s * s
    sw = [rng.randrange(2) for _ in range(s)]; d0 = [rng.randrange(s) for _ in range(s)]; d1 = [rng.randrange(s) for _ in range(s)]
    g, h1, h2 = rng.randrange(W), rng.randrange(W), rng.randrange(W)
    tree = sorted([3 * g + 0, 3 * h1 + 1, 3 * h2 + 2]); pls = [tree]
    for _ in range(rng.choice([1, 2, 3])):
        if rng.random() < 0.7:
            ws = rng.sample(range(W), 3); pls.append(sorted(3 * w for w in ws))
        else:
            ws = rng.sample(range(W), 3); a = rng.choice([1, 2]); pls.append(sorted(3 * w + a for w in ws))
    keys.append([s, sw, d0, d1, pls])
N = 6
def lvl(i): return (i + 1).bit_length() - 1
def solver(K):
    S = Cadical195()
    for a, b, c in K: S.add_clause([a + 1, b + 1, c + 1]); S.add_clause([-a - 1, -b - 1, -c - 1])
    return S
def tied(S, u, v):
    eq = S.solve(assumptions=[u + 1, v + 1]) or S.solve(assumptions=[-u - 1, -v - 1])
    ne = S.solve(assumptions=[u + 1, -v - 1]) or S.solve(assumptions=[-u - 1, v + 1])
    return (not eq) or (not ne)
tab = collections.defaultdict(collections.Counter)
for i, key in enumerate(keys, 1):
    o = outc.get(i)
    if o not in ('ruler', 'NOT ruler'): continue
    P = [tuple(int(x) for x in k) for k in pattern(key, N)]
    Wk = [k for k in P if len({lvl(x) for x in k}) == 1]
    Tk = [k for k in P if len({lvl(x) for x in k}) == 2]
    sib = []
    for k in Tk:
        ls = sorted(k, key=lvl); top = [x for x in k if lvl(x) == min(map(lvl, k))]
        kids = [x for x in k if lvl(x) == max(map(lvl, k))]
        if len(top) == 1 and len(kids) == 2: sib.append(tuple(kids))
    SW = solver(Wk); SP = solver(P)
    w_tie = any(tied(SW, u, v) for u, v in sib) if Wk else False
    p_tie = any(tied(SP, u, v) for u, v in sib)
    # any within-level tie at all (W alone), on a sample of pairs within one level
    tab[o][('W ties a sibling pair' if w_tie else 'W ties no sibling pair', 'P ties a sibling pair' if p_tie else 'P ties none')] += 1
for o, c in tab.items():
    print(o); [print('   ', k, v) for k, v in c.items()]

# ancestry of within-level knots in the tree: for each knot, the fewest levels up at which two of its members share a tree ancestor
print('--- ancestry')
tab2 = collections.defaultdict(collections.Counter)
for i, key in enumerate(keys, 1):
    o = outc.get(i)
    if o not in ('ruler', 'NOT ruler'): continue
    P = [tuple(int(x) for x in k) for k in pattern(key, N)]
    parent = {}
    for k in P:
        ls = [lvl(x) for x in k]
        if len(set(ls)) == 2:
            lo = min(ls); top = [x for x in k if lvl(x) == lo]; kids = [x for x in k if lvl(x) != lo]
            if len(top) == 1 and len(kids) == 2:
                for c in kids: parent[c] = top[0]
    def anc(x, d):
        for _ in range(d):
            x = parent.get(x)
            if x is None: return None
        return x
    mins = []
    for k in P:
        if len({lvl(x) for x in k}) != 1: continue
        best = 99
        for a in range(3):
            for b in range(a + 1, 3):
                for d in range(1, lvl(k[0]) + 1):
                    if anc(k[a], d) is not None and anc(k[a], d) == anc(k[b], d): best = min(best, d); break
        mins.append(best)
    m = min(mins) if mins else None
    tab2[o][m] += 1
for o, c in tab2.items(): print(o, dict(sorted(c.items(), key=lambda t: (t[0] is None, t[0] or 0))))
