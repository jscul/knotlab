"""post/l2_extra.py OUT.json: after the frozen run (not a frozen prediction).  For each disjoint-carrier cluster at the
ring's round 2 whose readings' joint image J is smaller than what its bonds allow, is the extra relation implied by other
bonds on the same readings, and if not, is it a relation of four or more readings in which every smaller set is free?"""
import sys, json, itertools, collections
import numpy as np
sys.path.insert(0, '.')
import ringbond as RB, layer2 as L2

S = ((0, 1, 3), (1, 2, 4), (2, 0, 5))
sup, born = RB.stages(S, 'nae', 2)[2]
st = RB.Stage(sup, 'nae'); bl = RB.bonds(st, 'agree', born=born)['bonds']
rd = [frozenset((tuple(C), lab) for C, lab in b['readings']) for b in bl]
def vals(r):
    C, lab = r; b = [st.bits(x, st.A) for x in C]; v = np.ones(len(st.A), dtype=bool)
    for y in b[1:]: v &= (y == b[0])
    return v.astype(np.int64)
res = L2.run(sup, born, 3)
out = []
# rebuild clusters with J != conj from the layer2 code path
by_r = collections.defaultdict(list)
for k, rs in enumerate(rd):
    for r in rs: by_r[r].append(k)
clusters = set()
for k in range(len(bl)):
    for r in rd[k]:
        for k2 in by_r[r]:
            if k2 > k:
                u = rd[k] | rd[k2]; cs = [set(C) for C, lab in u]
                if all(not (a & b) for a, b in itertools.combinations(cs, 2)): clusters.add((k, k2))
for c in sorted(clusters):
    u = sorted(set().union(*(rd[q] for q in c)))
    V = [vals(r) for r in u]; n = len(u)
    code = np.zeros(len(st.A), dtype=np.int64)
    for v in V: code = code * 2 + v
    J = set(np.unique(code).tolist())
    def allowed_by(bonds_idx):
        ok = set()
        for w in range(1 << n):
            bits = [(w >> (n - 1 - p)) & 1 for p in range(n)]
            good = True
            for q in bonds_idx:
                pos = [u.index((tuple(C), lab)) for C, lab in bl[q]['readings']]
                if '{}{}{}'.format(*[bits[p] for p in pos]) in bl[q]['missing']: good = False; break
            if good: ok.add(w)
        return ok
    conj = allowed_by(c)
    inside = [q for q in range(len(bl)) if rd[q] <= set(u)]
    conj_all = allowed_by(inside)
    extra = sorted(conj_all - J)
    rec = {'cluster': [bl[q]['readings'] for q in c], 'readings': n, 'J': len(J), 'conj': len(conj),
           'bonds inside its readings': len(inside), 'conj of all of them': len(conj_all)}
    if extra:
        # every proper subset of the readings free?  (the joint image projected to each set of n-1 readings is full)
        proj = [len({tuple(((w >> (n - 1 - p)) & 1) for p in range(n) if p != d) for w in J}) for d in range(n)]
        rec['missing beyond every bond'] = ['{:0{}b}'.format(w, n) for w in extra]
        rec['projections forgetting one reading (of %d)' % (1 << (n - 1))] = proj
    out.append(rec)
json.dump(out, open(sys.argv[1], 'w'), indent=1)
print(collections.Counter((r['J'] == r['conj'], r['J'] == r['conj of all of them']) for r in out))
for r in out:
    if 'missing beyond every bond' in r: print(json.dumps(r)[:600])
