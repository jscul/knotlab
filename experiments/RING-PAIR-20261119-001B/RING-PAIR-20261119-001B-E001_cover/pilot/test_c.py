import sys, time, json
sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/scripts')
from longrun import load_results
from animals import orbit_counts
from gamma import complex_of
import joinlib as J, job
N = int(sys.argv[1]); which = sys.argv[2:]
recs = {}
for d in ['/home/jscul/p-vs-np-contact-first/runs/join-growth', '/home/jscul/p-vs-np-contact-first/runs/join-growth-mem', '/home/jscul/p-vs-np-contact-first/runs/join-growth-mem2']:
    for k, r in load_results(d).items():
        if r.get('status') == 'ok': recs[k] = r
cs = dict(job.cases())
for cid in which:
    p = cs[cid]; edges = [tuple(e) for e in p['edges']]
    sz, E, big, tri = complex_of(p['n'], edges)
    assert not big
    E2 = list(E); k = p['n']; pend = []
    for kn, v in p['surplus'].items():
        for _ in range(v):
            E2.append((int(kn), k)); pend.append(k); k += 1
    t = time.time()
    oc = orbit_counts(k, E2, tri, N)
    # pendant singletons are not junctions: remove them at t = 0
    oc[0] -= len(pend)
    g = recs[cid]['result']['counts']
    print(cid, 'H', [int(x) if x.denominator == 1 else str(x) for x in oc], 'grown', g[:N], 'match', [int(x) for x in oc] == g[:N], round(time.time() - t, 1), flush=True)
