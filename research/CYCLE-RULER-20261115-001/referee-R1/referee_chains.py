"""Referee CYCLE-RULER-R1 (light, fresh code): the advisor's discriminator read as stated (a descending chain from level 3 to level
3 + s none of whose knots lies on a cycle of knots), against the study's test (any cross-level knot anywhere on a cycle), and Berge
girth at N = 7 and N = 9, on LEVEL-REACH's 1,288 descriptions. Pattern builder: LEVEL-REACH-R1's referee fresh_pattern.py. Graph
algorithms: networkx (biconnected blocks; a knot is on a cycle iff its block holds another knot)."""
import gzip, json, collections, importlib.util, sys
from pathlib import Path
import networkx as nx
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('fp', ROOT / 'research/LEVEL-REACH-20261114-001/referee-R1/codex/fresh_pattern.py')
fp = importlib.util.module_from_spec(spec); spec.loader.exec_module(fp)
lvl = lambda v: (v + 1).bit_length() - 1
res = {}
for l in gzip.open(ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/results.jsonl.gz', 'rt'):
    r = json.loads(l)
    if r['status'] == 'ok': res[r['result']['case']] = r['result']
def outcome(a):
    fl = a['flags']; un = a['union']['verdict']; Ls = [x['L_N'] for x in a['levels']]
    if fl['no_join']: return 'no join'
    if un == 'dead': return 'dead'
    if un != 'alive': return 'undecided'
    if any(x == 'none' for x in Ls): return 'no bond'
    if any(x == 'undecided' for x in Ls): return 'undecided'
    if all(isinstance(x, int) for x in Ls) and len(set(Ls)) == 1: return 'direct'
    if all(isinstance(x, int) for x in Ls) and all(Ls[i] == i + 3 for i in range(4)): return 'chained'
    return 'other'
def analyse(key, N):
    K = [tuple(k) for k in fp.build(key, N)]
    G = nx.Graph()
    for j, k in enumerate(K):
        for x in k: G.add_edge(('v', x), ('k', j))
    if G.number_of_nodes() == 0 or nx.is_forest(G):
        return {'cyclic': False}
    oncyc = set()
    for comp in nx.biconnected_components(G):
        ks = [n[1] for n in comp if n[0] == 'k']
        if len(ks) >= 2: oncyc |= set(ks)
    cross = [j for j, k in enumerate(K) if len({lvl(x) for x in k}) == 2]
    girth = nx.girth(G) // 2
    free_chain = {}
    for s in range(1, 5):
        R = set(range(2**3 - 1, 2**4 - 1))  # level 3
        for i in range(1, s + 1):
            nxt = set()
            for j in cross:
                if j in oncyc: continue
                k = K[j]; up = [x for x in k if lvl(x) == 2 + i]; lo = [x for x in k if lvl(x) == 3 + i]
                if up and lo and set(up) & R: nxt |= set(lo)
            R = nxt
        free_chain[s] = bool(R)
    return {'cyclic': True, 'cross_on_cycle': any(j in oncyc for j in cross), 'girth': girth, 'free_chain': free_chain}
tab = collections.defaultdict(collections.Counter); g7 = collections.defaultdict(collections.Counter); ex = {}
for c, a in res.items():
    o = outcome(a)
    if o == 'no join': continue
    f9 = analyse(a['key'], 9)
    if not f9['cyclic']: continue
    fc = f9['free_chain']
    tab[o][('study test: cross knot on a cycle' if f9['cross_on_cycle'] else 'study test: none'),
           ('cycle-free chain at every s' if all(fc.values()) else ('at some s' if any(fc.values()) else 'at no s'))] += 1
    if o in ('chained', 'direct', 'other') and all(fc.values()): ex.setdefault(o, c)
    f7 = analyse(a['key'], 7)
    g7[o]['acyclic at N=7' if not f7['cyclic'] else 'girth %d at N=7' % f7['girth']] += 1
out = {"discriminator (N=9, cyclic descriptions)": {o: {' | '.join(k): v for k, v in c.items()} for o, c in tab.items()},
       "girth read at N=7 (descriptions cyclic at N=9)": {o: dict(c) for o, c in g7.items()}, "examples": ex}
(Path(__file__).with_suffix('.json')).write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
