"""cubic.py OUT.jsonl N COUNT SEED [--chunk I/C]: boxes on closed systems of three-place knots.  UPPER-GROWN-20261127-001.

A connected system of three-place not-all-equal knots in which every distinction is held twice is a connected cubic
graph read the other way round: knots are its points, distinctions its links.  For N points, COUNT seeded draws of
networkx.random_regular_graph(3, N) (the weighting is that generator's), connected and simple, kept once up to
isomorphism.  For each: the full bond search (RING-BOND's definition), the boxes it forms, and each box's upper image."""
import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import networkx as nx
import boxes as BX
RB = BX.RB


def graphs(n, count, seed):
    out = []
    for k in range(count):
        g = nx.random_regular_graph(3, n, seed=seed + k)
        if not nx.is_connected(g): continue
        if any(nx.is_isomorphic(g, h) for h in out): continue
        out.append(g)
    return out


def system(g):
    edge = {tuple(sorted(e)): i for i, e in enumerate(g.edges())}
    return tuple(tuple(sorted(edge[tuple(sorted((v, w)))] for w in g[v])) for v in sorted(g.nodes()))


if __name__ == '__main__':
    out, n, count, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    G = graphs(n, count, seed)
    if '--chunk' in sys.argv:
        ci, cn = map(int, sys.argv[sys.argv.index('--chunk') + 1].split('/')); G = G[ci::cn]
    with open(out, 'w') as f:
        for g in G:
            t0 = time.time(); S = system(g)
            b = RB.bonds(RB.Stage(S, 'nae'), 'agree')['bonds']; bx = BX.find_boxes(b)
            recs = [BX.read_box(S, x, len(S)) for x in bx[:50]]
            f.write(json.dumps({'points': n, 'links': sorted(map(list, g.edges())), 'bonds': len(b), 'boxes': len(bx),
                                'boxes read': len(recs), 'upper missing exactly one': sum(1 for r in recs if len(r['upper missing']) == 1),
                                'every knot needed': sum(1 for r in recs if len(r.get('laws needed', [])) == len(S)),
                                'example': recs[:1], 'seconds': round(time.time() - t0, 1)}) + '\n'); f.flush()
