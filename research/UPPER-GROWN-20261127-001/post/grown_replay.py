"""post/grown_replay.py OUT.json: the thread's own replay of referee R1's growth-made witness.  The ten-knot start is
grown one ordinary round by the study's own engine (RING-BOND's ringbond.stages); the six carriers are read on the
grown stage by enumerating every state; the upper words (pairwise disagreement of the A, B and C pairs) and each law's
deletion are checked."""
import sys, json, itertools
import numpy as np
sys.path.insert(0, '.')
import boxes as BX
RB = BX.RB
W = json.load(open('referee-R1/open_witness.json'))
S = tuple(tuple(k) for k in W['start']); C = W['six_disjoint_carriers']
sts = RB.stages(S, 'nae', 1); sup, born = sts[1]
out = {'grown by the study engine equals the referee stage': sorted(map(sorted, sup)) == sorted(map(sorted, W['grown_supports'])),
       'births': [list(k) for k in sup[born:]]}
names = sorted({x for k in sup for x in k}); idx = {x: i for i, x in enumerate(names)}; n = len(names)
s = np.arange(1 << n, dtype=np.uint32); bit = lambda x, st: ((st >> np.uint32(idx[x])) & 1).astype(np.int8)
def allowed(ks):
    m = np.ones(len(s), dtype=bool)
    for k in ks:
        c = sum(bit(x, s) for x in k); m &= (c > 0) & (c < len(k))
    return s[m]
def upper(A):
    ag = [np.all([bit(x, A) == bit(c[0], A) for x in c], axis=0) for c in C]
    u = [ag[0] != ag[1], ag[2] != ag[3], ag[4] != ag[5]]
    return set(zip(*[v.astype(int).tolist() for v in u]))
A = allowed(sup); U = upper(A)
out['states'] = int(len(A)); out['upper words'] = len(U); out['upper 111 missing'] = (1, 1, 1) not in U
out['each law needed (111 restored when removed)'] = [(1, 1, 1) in upper(allowed([k for i, k in enumerate(sup) if i != q])) for q in range(len(sup))]
out['on the start alone (6 distinctions of births absent): upper 111 missing'] = None
json.dump(out, open(sys.argv[1], 'w'), indent=1); print(json.dumps(out))
