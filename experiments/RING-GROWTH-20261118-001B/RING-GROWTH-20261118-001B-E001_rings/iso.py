import sys
import networkx as nx
from networkx.algorithms import isomorphism
from model import junctions, parents
from ring import ring
sys.path.append(str(__import__('pathlib').Path(__file__).resolve().parents[3] / 'experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots'))
import startlib as S
F = S.F
n = 5; T = int(sys.argv[1])
P = S.from_junctions(ring([4,4,4,4,5])); P.linalg = False
for _ in range(T): P.step(F.fewest, None)
G = nx.MultiDiGraph()
for j in range(len(P.bits_of)):
    G.add_node(j, r=P.round_of[j], fresh=P.fresh[j] if P.round_of[j] > 0 else -1, five=(P.round_of[j] == 0 and len(P.bits_of[j]) == 5))
for b, js in P.owner.items():
    if len(js) == 2:
        u, v = sorted(js)
        if P.round_of[u] == 0 and P.round_of[v] == 0:
            G.add_edge(u, v); G.add_edge(v, u)
        else:
            G.add_edge(v, u)
J = junctions(n, T)
H = nx.MultiDiGraph()
idx = {k: i for i, k in enumerate(J)}
from model import demand
for k, t in J.items():
    H.add_node(idx[k], r=t, fresh=demand(*k, n) if t > 0 else -1, five=(t == 0 and k[0] == (0, 0)))
for (v, S_), t in J.items():
    if t == 0: continue
    for p in parents(v, S_, n):
        H.add_edge(idx[(v, S_)], idx[p])
# round-0 adjacency (the ring's shared distinctions) in H
ring0 = [k for k, t in J.items() if t == 0]
# add ring edges between round-0 classes: (a,-a) shares with (a+1, -a-1)
def c0(a): 
    q = a // n; return ((a - n*q, -a + n*q), ())
for a in range(n):
    H.add_edge(idx[c0(a + 3)], idx[c0(a)]); H.add_edge(idx[c0(a)], idx[c0(a + 3)])
print(G.number_of_nodes(), H.number_of_nodes(), G.number_of_edges(), H.number_of_edges())
nm = isomorphism.categorical_node_match(['r', 'fresh', 'five'], [0, 0, False])
GM = isomorphism.MultiDiGraphMatcher(G, H, node_match=nm)
print('isomorphic:', GM.is_isomorphic())
