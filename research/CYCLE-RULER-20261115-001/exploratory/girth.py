"""Exploratory: the shortest cycle of knots (Berge girth, in knots) of the cyclic census descriptions, read on levels 0..7, against the
outcome (read at depth 9). Also the shortest cycle through a cross-level knot."""
import sys, gzip, json, collections
import networkx as nx
sys.path.insert(0, 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex')
from pattern import pattern
exec(open('research/CYCLE-RULER-20261115-001/exploratory/discriminator.py').read().split('N = int')[0].split("recs = ")[0])
recs = [json.loads(l) for l in gzip.open('artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt')]
exec("def outcome(a):" + open('research/CYCLE-RULER-20261115-001/exploratory/discriminator.py').read().split("def outcome(a):")[1].split("N = int")[0])
NL = 7
tab = collections.defaultdict(collections.Counter)
for a in recs:
    if 'key' not in a: continue
    o = outcome(a)
    if o in ('no join', 'undecided', 'dead'): continue
    P = [tuple(int(x) for x in k) for k in pattern(a['key'], NL)]
    G = nx.Graph()
    for j, k in enumerate(P):
        for x in k: G.add_edge(('v', x), ('k', j))
    if G.number_of_nodes() == 0 or nx.is_forest(G): continue
    g = nx.girth(G) // 2
    tab[o][g if g < 8 else '8+'] += 1
for o, c in sorted(tab.items()): print(o, dict(sorted(c.items(), key=lambda t: str(t[0]))))
