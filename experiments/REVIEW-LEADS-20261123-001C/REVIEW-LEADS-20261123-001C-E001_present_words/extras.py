"""The two extra tests of the pre-registration on hidden pairs that reach 2 (parity score >= 2 - 1e-9):
 (a) the best value over ALL two-valued functions of the complete records (alternating optimisation from every parity start and
     200 random starts, four sign patterns);
 (b) for the best ten, a linear-programming test of whether the four complete-record tables have one common local explanation
     (smallest L1 residual from the local polytope; 0 means a common local explanation exists).
Extension (not pre-registered, reported as such): (a) is also run on every saved hidden pair with parity score >= 1.

usage: extras.py CUT      (CUT = 1 or 2; reads the pairs_* hidden files of the census and the extended class)
"""
import sys, glob, json, time
import numpy as np
import common as c

cut = int(sys.argv[1])
t0 = time.time()
ext_files = sorted(glob.glob(f'{c.ART}/pairs_c{cut}_k4_i5_sym*_hidden.npz'))
cen_file = f'{c.ART}/pairs_c{cut}_k3_i3_0_{ {1: 495, 2: 2635}[cut] }_hidden.npz'
def keys_of(M):
    k, _ = c.canon_keys(M.reshape(len(M), 64).astype(np.int64))
    return k
cen = np.load(cen_file); cen_M = cen['M'].astype(np.int64); cen_keys = set(keys_of(cen_M).tolist())
Ms = []; scs = []
for f in ext_files:
    d = np.load(f); m = d['M'].astype(np.int64); s = d['score']
    sel = s >= 1.0 - 1e-9
    Ms.append(m[sel]); scs.append(s[sel])
M = np.concatenate(Ms); sc = np.concatenate(scs)
k = keys_of(M)
u, first = np.unique(k, return_index=True)
M = M[first]; sc = sc[first]; k = k[first]
order = np.argsort(-sc, kind='stable'); M = M[order]; sc = sc[order]; k = k[order]
in_cen = np.array([int(x) in cen_keys for x in k])
reach = sc >= 2 - c.TOL
print(f'cut {cut}: distinct hidden tables M with parity score >= 1: {len(M)}; reaching 2: {int(reach.sum())} (in the census class: {int((reach & in_cen).sum())})', flush=True)
gen = np.zeros(len(M)); done = 0
for q in range(len(M)):
    gen[q] = c.best_general(M[q])[0]
    done += 1
    if time.time() - t0 > 520: break
print(f'general functions evaluated on {done} of {len(M)} tables, {time.time() - t0:.0f}s', flush=True)
dn = np.arange(len(M)) < done
res = dict(cut=cut, n_tables_score_ge1=int(len(M)), n_reach2=int(reach.sum()), n_reach2_census=int((reach & in_cen).sum()), general_done=int(done),
           general_gt2_reach2=int((reach & dn & (gen > 2 + c.TOL)).sum()), general_gt2_any=int((dn & (gen > 2 + c.TOL)).sum()),
           general_max_reach2=float(gen[reach & dn].max()) if (reach & dn).any() else None,
           general_max_any=float(gen[dn].max()) if dn.any() else None,
           general_max_below2=float(gen[dn & ~reach].max()) if (dn & ~reach).any() else None,
           parity_max_below2=float(sc[~reach].max()) if (~reach).any() else None)
# best ten by general value, then parity score
rank = np.lexsort((-sc[:done], -np.round(gen[:done], 9)))
ten = rank[:10]
lp = []
for q in ten:
    r, status = c.lp_local_residual(M[q])
    lp.append(dict(index=int(q), parity=float(sc[q]), general=float(gen[q]), in_census=bool(in_cen[q]), lp_residual=r, lp_status=int(status), M=M[q].tolist()))
res['best_ten_lp'] = lp
res['lp_all_feasible'] = bool(all(abs(x['lp_residual']) < 1e-9 for x in lp))
# a spread check: LP on 40 further hidden pairs that reach 2, chosen evenly from the ranking
extra = [int(q) for q in np.linspace(10, max(10, int(reach.sum()) - 1), 40).astype(int)] if reach.sum() > 10 else []
lp2 = []
for q in extra:
    if q >= done: continue
    r, status = c.lp_local_residual(M[q]); lp2.append(dict(index=q, lp_residual=r))
res['extra_lp_n'] = len(lp2); res['extra_lp_max_residual'] = max([x['lp_residual'] for x in lp2], default=None)
res['seconds'] = round(time.time() - t0, 1)
json.dump(res, open(f'{c.ART}/extras_c{cut}.json', 'w'), indent=1)
np.savez_compressed(f'{c.ART}/extras_c{cut}_tables.npz', M=M[reach], parity=sc[reach], general=gen[reach], in_census=in_cen[reach])
print(json.dumps({k_: v for k_, v in res.items() if k_ != 'best_ten_lp'}, indent=1))
for x in lp: print({k_: v for k_, v in x.items() if k_ != 'M'})
