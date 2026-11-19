import sys, json
sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins')
import joinlib as J, reclib as R
kind, n = sys.argv[1], int(sys.argv[2])
edges = J.ring_edges(n); k = n
if kind == 'fork':
    edges += [(0, k), (k, k + 1), (k, k + 2)]; k += 3
elif kind.startswith('chain'):
    d = int(kind[5:]); prev = 0
    for _ in range(d):
        edges.append((prev, k)); prev = k; k += 1
sz = J.bare_sizes(k, edges)
g = J.grow(sz, edges, rounds=90, maxj=300000, tmax=1500)
print(json.dumps({'kind': kind, 'n': n, 'sizes': sz, 'counts': g['counts'], 'minimal': R.minimal_recurrence(g['counts']), 'outcome': g['outcome']}))
