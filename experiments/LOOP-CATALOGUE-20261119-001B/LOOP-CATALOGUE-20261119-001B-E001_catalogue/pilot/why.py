import sys
from collections import Counter
from pathlib import Path
import networkx as nx
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import eddy as E, sampler as S
n = int(sys.argv[1]); M = int(sys.argv[2])
tab = Counter(); kr = []; long_ok = Counter()
for s in range(n * 1000000, n * 1000000 + M):
    sz, e = S.sample(n, s)
    A = E.Cl.analyse(sz, e)
    if not A['scope'] or A['stall']:
        continue
    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(set(e))
    simple_rank = G.number_of_edges() - n + 1
    multi = len(e) - G.number_of_edges()
    cyc = [len(c) for c in nx.chordless_cycles(G)]
    has_long = any(L == 5 or L >= 7 for L in cyc)
    P = E.pieces(A)
    rb = sum(p[2] for p in P)
    v = E.eddy(sz, e)
    kr.append(simple_rank + multi)
    tab[('block_rank>0' if rb else 'block_rank=0', 'long_chordless' if has_long else 'no_long', str(v))] += 1
    for L in cyc:
        long_ok[L] += 1
print(n, 'growers', len(kr), 'mean knot cycle rank', round(sum(kr) / len(kr), 2))
for k, v in sorted(tab.items()): print('  ', k, v)
print('  chordless cycle lengths', dict(sorted(long_ok.items())))
