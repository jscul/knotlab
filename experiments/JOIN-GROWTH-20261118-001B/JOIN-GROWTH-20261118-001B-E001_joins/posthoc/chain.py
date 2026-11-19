import sys, json
sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins')
import joinlib as J, reclib as R
n, depth = int(sys.argv[1]), int(sys.argv[2])
edges = J.ring_edges(n); prev = 0; k = n
for d in range(depth):
    edges.append((prev, k)); prev = k; k += 1
sz = J.bare_sizes(k, edges)
g = J.grow(sz, edges, rounds=90, maxj=300000, tmax=1200)
print(json.dumps({'n': n, 'depth': depth, 'sizes': sz, 'counts': g['counts'], 'minimal': R.minimal_recurrence(g['counts']), 'outcome': g['outcome']}))
