"""Pilot: forward kinds.  kind_0 = one kind; kind_h(j) = the multiset of (kind_{h-1}(child), 1/p(child)) over j's children.
Distinct kinds of depth h among the junctions of each round, and whether depth h and h + 1 split them alike."""
import json, sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import kindlib as K
ROOT = HERE.parents[3]
pop = json.loads((ROOT / 'experiments/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/population.json').read_text())
cat = json.loads((ROOT / 'experiments/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue/catalogue.json').read_text())
T, H = int(sys.argv[1]), int(sys.argv[2])
names = sys.argv[3].split(',')
def get(nm):
    return pop[int(nm[2:])] if nm.startswith('G-') else cat[int(nm[2:])]
for nm in names:
    P = K.start(get(nm))
    for t in range(T):
        r = P.step(K.E.J.F.fewest, None)
        if r is None or r['new'] == 0 or len(P.bits_of) > 200000:
            break
    T2 = P.rounds
    n = len(P.bits_of)
    ch = defaultdict(list)
    for c in range(n):
        if P.round_of[c] == 0:
            continue
        par = {o for b in P.bits_of[c][:P.parents[c]] for o in P.owner[b] if o != c}
        for o in par:
            ch[o].append(c)
    kind = [0] * n
    tab = {}
    rows = []
    prev_part = None
    for h in range(1, H + 1):
        new = [None] * n
        for j in range(n):
            if P.round_of[j] + h <= T2:
                key = tuple(sorted(Counter((kind[c], Fraction(1, P.parents[c])) for c in ch[j]).items()))
                new[j] = tab.setdefault((h, key), len(tab))
        # distinct kinds per round, for rounds that reach depth h
        per = [len({new[j] for j in range(n) if P.round_of[j] == t}) for t in range(0, T2 - h + 1)]
        # does depth h split the junctions (that have depth h) like depth h-1?
        same = None
        if h > 1:
            cls_prev, cls_new = defaultdict(set), defaultdict(set)
            for j in range(n):
                if new[j] is not None:
                    cls_new[new[j]].add(kind[j])
            same = all(len(v) == 1 for v in cls_new.values())
            nprev = len({kind[j] for j in range(n) if new[j] is not None}); nnew = len({new[j] for j in range(n) if new[j] is not None})
        rows.append((h, per[-6:], max(per), (nprev, nnew) if h > 1 else None))
        kind = [k if k is not None else -1 for k in new]
    print(nm, 'rounds', T2, 'counts', P.counts_by_round()[-3:])
    for r in rows: print('   depth', r[0], 'kinds in last rounds', r[1], 'max', r[2], 'classes (depth h-1, h) on the same junctions', r[3])
