import sys, json
sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins')
import joinlib as J, job
cs = dict(job.cases())
p = cs[sys.argv[1]]; edges = [tuple(e) for e in p['edges']]
sz = J.bare_sizes(p['n'], edges, p['surplus'])
g = J.grow(sz, edges, rounds=int(sys.argv[2]), maxj=10**7, tmax=3000)
print(json.dumps({'case': sys.argv[1], 'sizes': sz, 'counts': g['counts'], 'outcome': g['outcome'], 'seconds': g['seconds']}))
