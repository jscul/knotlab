import sys
sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/scripts')
from longrun import load_results
import joinlib_path  # noqa
from blocks2 import blocks_of, series
import joinlib as J, job
recs = {}
for d in ['/home/jscul/p-vs-np-contact-first/runs/join-growth', '/home/jscul/p-vs-np-contact-first/runs/join-growth-mem', '/home/jscul/p-vs-np-contact-first/runs/join-growth-mem2']:
    for k, r in load_results(d).items():
        if r.get('status') == 'ok': recs[k] = r
cs = dict(job.cases())
ids = sys.argv[1:] if sys.argv[1:] != ['all'] else sorted(cs)
tally = {}
for cid in ids:
    p = cs[cid]; edges = [tuple(e) for e in p['edges']]
    if cid not in recs: continue
    pend = [int(kn) for kn, v in p['surplus'].items() for _ in range(v)]
    try:
        nv, B = blocks_of(p['n'], edges, pend)
    except ValueError as e:
        print(cid, 'not covered:', e); continue
    g = recs[cid]['result']['counts']
    s = series(nv, B, len(g), None)
    s[0] -= len(pend)
    ok = s[:len(g)] == g
    first_bad = next((t for t in range(len(g)) if s[t] != g[t]), None)
    tally[(cid.split('-')[0], ok)] = tally.get((cid.split('-')[0], ok), 0) + 1
    print(cid, 'match' if ok else f'MISS from round {first_bad}', len(g) - 1, 'rounds', '' if ok else (s[:6], g[:6]), flush=True)
print(tally)
