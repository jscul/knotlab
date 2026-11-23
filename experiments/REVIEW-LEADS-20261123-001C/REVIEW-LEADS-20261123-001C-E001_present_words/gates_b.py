"""Gate row G, part 2: brute-force enumeration of all words of the four finished structures agrees with the side-table product
on 200 random pairs (100 per cut size), including pairs in the allocation class; the control weighting does not exceed 2 on them."""
import json, sys
import numpy as np
import common as c, brute

rng = np.random.default_rng(20261123)
res = dict(pairs=0, mismatches=0, details=[])
ctrl_max = 0.0
for cut, tag in ((1, 'c1_k3_i3'), (2, 'c2_k3_i3')):
    d = np.load(f'{c.ART}/sides_{tag}.npz'); meta = json.load(open(f'{c.ART}/sides_{tag}.json'))
    T = d['T'].astype(np.int64); alloc = d['alloc']; ne = np.nonzero(d['nonempty'])[0]
    al_idx = np.nonzero(alloc & d['nonempty'])[0]
    n_ok = 0
    for t in range(100):
        # half of the pairs have both sides in the allocation class
        pool = al_idx if t % 2 == 0 else ne
        i = int(rng.choice(pool)); j = int(rng.choice(pool))
        eA = meta['structures'][i]; eB = meta['structures'][j]
        sA = eA['alloc_struct'] if (t % 2 == 0 and eA['alloc_struct']) else eA['struct']
        sB = eB['alloc_struct'] if (t % 2 == 0 and eB['alloc_struct']) else eB['struct']
        M = T[i] @ T[j].T
        if M.sum() == 0:
            continue
        M_bf = brute.old_counts(sA, sB)
        good = np.array_equal(M, M_bf)
        for a in (0, 1):
            for b in (0, 1):
                J, nv = brute.joint_record_counts(sA, sB, a, b, cut)
                good &= np.array_equal(J, c.F[a].T @ M @ c.F[b])
        # score and hiding from the brute-force joint tables equal those from M
        s_M = float(c.score_batch_c(M[None])[0]); hA, hB = c.hidden_batch(M[None])
        ctrl = float(c.score_batch_c(M[None], control=True)[0]); ctrl_max = max(ctrl_max, ctrl)
        res['pairs'] += 1; res['mismatches'] += (not good)
        if not good: res['details'].append(dict(cut=cut, i=i, j=j))
        n_ok += good
    print(f'cut {cut}: 100 random pairs drawn, {n_ok} nonempty and agreeing with brute force')
print(f"brute force vs side-table product: {res['pairs']} pairs checked, {res['mismatches']} mismatches; control weighting largest score on them {ctrl_max:.9f}")

# the starter's exact hidden flag, largest change and score agree with the batched evaluation on 3000 random census pairs (cut 2)
ns = c.load_starter(); evaluate = ns['evaluate']
d = np.load(f'{c.ART}/sides_c2_k3_i3.npz'); T2 = d['T'].astype(np.int64)
mism = 0; nh = 0; n3 = 0
for _ in range(3000):
    i, j = rng.integers(len(T2), size=2)
    M = T2[i] @ T2[j].T
    if M.sum() == 0: continue
    r = evaluate(M)
    if r is None: continue
    s0, h0, tv0, _ = r
    hA, hB = c.hidden_batch(M[None]); s1 = c.score_batch_c(M[None])[0]
    n3 += 1; nh += bool(h0)
    if bool(hA[0] and hB[0]) != bool(h0) or abs(s0 - s1) > 1e-9 or abs(float(tv0) - c.tv_batch(M[None])[0]) > 1e-9: mism += 1
print(f'starter evaluate vs batched evaluation on {n3} random census pairs (cut 2): {mism} mismatches; hidden among them {nh}')
res['starter_check'] = dict(n=n3, mismatches=mism, hidden=nh)
ok = res['mismatches'] == 0 and mism == 0 and res['pairs'] >= 190 and ctrl_max <= 2 + 1e-9
print('GATE PART 2:', 'PASS' if ok else 'FAIL')
res['control_max_on_pairs'] = ctrl_max
json.dump(res, open(c.ART + '/gates_b.json', 'w'), indent=1)
sys.exit(0 if ok else 1)
