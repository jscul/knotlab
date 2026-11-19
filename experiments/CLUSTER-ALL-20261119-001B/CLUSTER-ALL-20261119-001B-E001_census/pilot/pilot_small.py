import sys
sys.path.insert(0, '.')
sys.path.insert(0, "..")
import clusters as Cl
J = Cl.J
def grown(sizes, edges, rounds=16):
    g = J.grow(sizes, edges, rounds=rounds, maxj=20000, tmax=60)
    return g['outcome'], g['counts']
tests = {'lone3': ([3], []), 'lone5': ([5], []), 'pair33': ([3, 3], [(0, 1)]), 'pair44': ([4, 4], [(0, 1)]), 'pair35': ([3, 5], [(0, 1)]),
         'pair-apart?': ([3, 4], [(0, 1), (0, 1)]), 'chain333': ([3, 3, 3], [(0, 1), (1, 2)]), 'ring3x4': ([4, 4, 4], [(0, 1), (1, 2), (2, 0)]),
         'ring5x4': ([4] * 5, J.ring_edges(5)), 'ring5x5': ([5] * 5, J.ring_edges(5)), 'star': ([3, 4, 3, 3], [(1, 0), (1, 2), (1, 3)])}
for k, (sz, e) in tests.items():
    pred = Cl.series(sz, e, 16)
    out, c = grown(sz, e)
    print(k, out, c[:14], '| rule', pred if not isinstance(pred, list) else pred[:14], 'EQUAL' if isinstance(pred, list) and pred[:len(c)] == c[:16] else '')
