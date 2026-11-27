"""post/chain_and_orbits.py OUT.json: after the frozen run (not a frozen prediction).  Bonds on short chains with no ring
and no growth, and the orbits of the ring's round-3 bonds under the stage's whole symmetry (every renaming of knots and
distinctions that maps the stage onto itself, by graph matching)."""
import sys, json, collections
sys.path.insert(0, '.')
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher
import ringbond as RB
out = {'chains': {}}
for P in [((0, 1, 2), (2, 3, 4)), ((0, 1, 2), (2, 3, 4), (4, 5, 6)), ((0, 1, 2, 3), (3, 4, 5, 6)), ((6, 7, 8), (7, 9, 10), (8, 11, 12))]:
    b = RB.bonds(RB.Stage(P, 'nae'), 'agree')['bonds']
    out['chains'][str(P)] = {'bonds': len(b), 'every law essential': sum(1 for x in b if len(x['essential']) == len(P)), 'example': b[:1]}
S = ((0, 1, 3), (1, 2, 4), (2, 0, 5))
for t in (1, 2, 3):
    sup, born = RB.stages(S, 'nae', t)[t]
    g = nx.Graph()
    for k, r in enumerate(sup):
        g.add_node(('k', k), t='k')
        for x in r: g.add_node(('d', x), t='d'); g.add_edge(('k', k), ('d', x))
    autos = [{a[1]: c[1] for a, c in m.items() if a[0] == 'd'} for m in GraphMatcher(g, g, node_match=lambda a, c: a['t'] == c['t']).isomorphisms_iter()]
    bl = RB.bonds(RB.Stage(sup, 'nae'), 'agree', born=born)['bonds']
    keys = {RB.bond_key(x): x for x in bl}; seen = set(); sizes = collections.Counter()
    for k, x in keys.items():
        if k in seen: continue
        orb = {RB.bond_image(x, p) for p in autos}; assert orb <= set(keys); seen |= orb; sizes[len(orb)] += 1
    out['round %d' % t] = {'symmetries': len(autos), 'bonds': len(bl), 'orbit sizes': dict(sorted(sizes.items())), 'fixed bonds': sizes.get(1, 0)}
json.dump(out, open(sys.argv[1], 'w'), indent=1, default=list); print(json.dumps({k: v for k, v in out.items() if k != 'chains'}), {k: v['bonds'] for k, v in out['chains'].items()})
