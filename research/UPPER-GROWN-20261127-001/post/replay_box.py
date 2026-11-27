"""post/replay_box.py OUT.json: replays, by enumerating every state (no solver), the first read box of each twelve-point
closed system with a box: its upper image and whether each knot is needed."""
import sys, json, glob
import numpy as np
sys.path.insert(0, '.')
import cubic as CU
G = {tuple(sorted(map(tuple, sorted(map(list, g.edges()))))): g for g in CU.graphs(12, 3000, 1012)}
out = []
for f in sorted(glob.glob('out/cubic_12_*.jsonl')):
    for l in open(f):
        r = json.loads(l)
        if not r['boxes']: continue
        K = list(CU.system(G[tuple(map(tuple, r['links']))]))     # the same numbering as the run
        s = np.arange(1 << 18, dtype=np.uint32); bit = lambda x, st: ((st >> np.uint32(x)) & 1).astype(np.int8)
        def allowed(ks):
            m = np.ones(len(s), dtype=bool)
            for k in ks:
                c = sum(bit(x, s) for x in k); m &= (c > 0) & (c < 3)
            return s[m]
        box = r['example'][0]['box']
        def words(A):
            ups = []
            for (c0, v0), (c1, v1) in box:
                ag = lambda C: np.all([bit(x, A) == bit(C[0], A) for x in C], axis=0)
                ups.append((ag(c0) == ag(c1)) if (v0 + v1) % 2 == 1 else (ag(c0) != ag(c1)))
            return set(zip(*[u.astype(int).tolist() for u in ups]))
        W = words(allowed(K)); miss = sorted({(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)} - W)
        need = [q for q in range(12) if set(miss) & words(allowed([k for i, k in enumerate(K) if i != q]))]
        out.append({'bonds': r['bonds'], 'missing': miss, 'reported': r['example'][0]['upper missing'], 'knots needed': len(need)})
json.dump(out, open(sys.argv[1], 'w'), indent=1)
print(len(out), sum(1 for o in out if len(o['missing']) == 1 and [''.join(map(str, o['missing'][0]))] == o['reported']), sum(1 for o in out if o['knots needed'] == 12))
