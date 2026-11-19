import sys
from collections import Counter
from pathlib import Path
import networkx as nx
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import eddy as E, sampler as S
for n in (6, 8, 12):
    live_share, tot, cyc_all, cyc_live, cyc_live_long, rb = [], 0, 0, 0, 0, 0
    for s in range(n * 1000000, n * 1000000 + 20000):
        sz, e = S.sample(n, s)
        A = E.Cl.analyse(sz, e)
        if not A['scope'] or A['stall']:
            continue
        tot += 1
        live = set(A['live'])
        live_share.append(len(live) / n)
        G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(set(e))
        for c in nx.chordless_cycles(G):
            cyc_all += 1
            if set(c) <= live:
                cyc_live += 1
                if len(c) == 5 or len(c) >= 7:
                    cyc_live_long += 1
        rb += sum(p[2] for p in E.pieces(A)) > 0
    print(n, 'growers', tot, 'live share', round(sum(live_share) / tot, 3), 'chordless cycles/grower', round(cyc_all / tot, 2),
          'all-live', round(cyc_live / tot, 3), 'all-live of length 5 or 7+', round(cyc_live_long / tot, 4), 'with a loop', rb, flush=True)
