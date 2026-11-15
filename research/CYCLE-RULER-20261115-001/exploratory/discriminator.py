"""Exploratory (on committed census records, depth 9): the advisor's discriminator. A cross-level knot is 'on a cycle' when it lies in
a biconnected block of the incidence graph holding another knot (some cycle of knots passes through two of its members). Tabulate,
for the cyclic census descriptions, whether any cross-level knot is on a cycle, against the outcome."""
import sys, gzip, json, collections
import networkx as nx
sys.path.insert(0, 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex')
from pattern import pattern
recs = [json.loads(l) for l in gzip.open('artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt')]
def outcome(a):
    fl = a['flags']; un = a['union']; Ls = [l['L_N'] for l in a['levels']]
    if fl['no_join']: return 'no join'
    if un == 'dead': return 'dead'
    if un != 'alive': return 'undecided'
    if any(x == 'none' for x in Ls): return 'no bond'
    if any(x == 'undecided' for x in Ls): return 'undecided'
    if all(isinstance(x, int) for x in Ls) and len(set(Ls)) == 1: return 'direct'
    if all(isinstance(x, int) for x in Ls) and all(Ls[i] == i + 3 for i in range(4)): return 'chained'
    return 'other'
N = int(sys.argv[1]) if len(sys.argv) > 1 else 9
def lvl(i): return (int(i) + 1).bit_length() - 1
def features(key):
    P = [tuple(int(x) for x in k) for k in pattern(key, N)]
    G = nx.Graph()
    for j, k in enumerate(P):
        for x in k: G.add_edge(('v', x), ('k', j))
    cross = {j for j, k in enumerate(P) if len({lvl(x) for x in k}) == 2}
    if G.number_of_nodes() == 0 or nx.is_forest(G): return 'acyclic', None, None
    on_cycle = set(); within_on_cycle = False
    for comp in nx.biconnected_components(G):
        ks = [n[1] for n in comp if n[0] == 'k']
        if len(ks) >= 2:
            for j in ks:
                if j in cross: on_cycle.add(j)
                else: within_on_cycle = True
    return 'cyclic', len(on_cycle) > 0, within_on_cycle
tab = collections.defaultdict(collections.Counter)
for a in recs:
    if 'key' not in a: continue
    o = outcome(a)
    if o in ('no join',): continue
    kind, cross_cyc, within_cyc = features(a['key'])
    if kind == 'acyclic': continue
    tab[o][('a cross-level knot on a cycle' if cross_cyc else 'no cross-level knot on a cycle')] += 1
for o, c in sorted(tab.items()): print(o, dict(c))
