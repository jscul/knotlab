"""Combine every ordered pair of side tables with the same cut size and evaluate it under uniform present words and under the
control weighting.

usage: pairs.py TAG [--sym] [--rows R0 R1] [--out NAME]     TAG = c{cut}_k{kmax}_i{imax} of a sides_*.npz file.
Tables are divided by the gcd of their entries (the score and the hiding do not change under scaling); a projective table
is in the allocation class if any exact table giving it is.  Pairs are reduced to unique normalised old tables M up to the
32 symmetries of common.sym_images (the whole evaluation depends on M only and is unchanged by them); counts of pairs per
class are kept.  Default: every ordered pair of projective tables.  --sym: tables are first reduced to classes under the four
row maps (swap x2<->x3, flip all values), and only unordered pairs of classes are combined; by the symmetries these stand for
every ordered pair of the projective tables.
"""
import sys, json, time
import numpy as np
from fractions import Fraction
import common as c

args = sys.argv[1:]
tag = args[0]
SYM = '--sym' in args
HIDONLY = '--hidden-only' in args
SAVEMIN = float(args[args.index('--save-min') + 1]) if '--save-min' in args else None
r0 = 0; r1 = None
if '--rows' in args:
    k = args.index('--rows'); r0 = int(args[k + 1]); r1 = int(args[k + 2])
outname = args[args.index('--out') + 1] if '--out' in args else f'{tag}{"_sym" if SYM else ""}'
t0 = time.time()
d = np.load(f'{c.ART}/sides_{tag}.npz')
meta = json.load(open(f'{c.ART}/sides_{tag}.json'))
T = d['T'].astype(np.int64); alloc0 = d['alloc']; ne = d['nonempty']
K = T.shape[2]
n_exact = len(T); n_nonempty = int(ne.sum())
idx0 = np.nonzero(ne)[0]
T = T[ne]; alloc0 = alloc0[ne]
g = np.gcd.reduce(T.reshape(len(T), -1), axis=1)
Tp = T // g[:, None, None]
flat = Tp.reshape(len(Tp), -1)
U, first, inv = np.unique(flat, axis=0, return_index=True, return_inverse=True)
inv = inv.reshape(-1)
alloc = np.zeros(len(U), dtype=bool); np.logical_or.at(alloc, inv, alloc0)
rep = np.zeros(len(U), dtype=np.int64)               # exact-table index of a representative (an allocation-class one if any)
rep[:] = first
for q in np.nonzero(alloc0)[0]:
    if not alloc0[first[inv[q]]]:
        rep[inv[q]] = q; 
Tp = U.reshape(-1, 8, K)
rep = idx0[rep]
N_proj = len(Tp)
N_orbit = None
if SYM:
    imgs = np.stack([Tp[:, p, :] for p in c.ROW_PERMS], 1).reshape(N_proj, 4, -1)            # (N,4,8K)
    canon_rows = [min(imgs[t, g].tobytes() for g in range(4)) for t in range(N_proj)]
    ids = {}
    inv2 = np.empty(N_proj, dtype=np.int64); f2 = []
    for t, kb in enumerate(canon_rows):
        if kb not in ids: ids[kb] = len(ids); f2.append(t)
        inv2[t] = ids[kb]
    f2 = np.array(f2)
    alloc_o = np.zeros(len(ids), dtype=bool); np.logical_or.at(alloc_o, inv2, alloc)
    rep_o = f2.copy()
    for q in np.nonzero(alloc)[0]:
        if not alloc[f2[inv2[q]]]: rep_o[inv2[q]] = q
    Tp = Tp[rep_o]; alloc = alloc_o; rep = rep[rep_o]
    N_orbit = len(Tp)
N = len(Tp)
ALLALLOC = bool(alloc.all())
print(f'{tag}: exact tables {n_exact}, nonempty {n_nonempty}, projective {N_proj}, tables combined {N} (allocation class {int(alloc.sum())}); '
      f'sym {SYM}; rows {r0}..{r1}', flush=True)

Af = Tp.reshape(N * 8, K).astype(np.float64)
r1 = N if r1 is None else min(r1, N)
def merge(parts):
    h1 = np.concatenate([p[0] for p in parts]); h2 = np.concatenate([p[1] for p in parts])
    M = np.concatenate([p[2] for p in parts]); ii = np.concatenate([p[3] for p in parts]); jj = np.concatenate([p[4] for p in parts])
    cnt = np.concatenate([p[5] for p in parts])
    u, f, inv = np.unique(h1, return_index=True, return_inverse=True)
    inv = inv.reshape(-1)
    tot = np.bincount(inv, weights=cnt).astype(np.int64)
    assert (h2[f][inv] == h2).all(), 'hash collision'
    return u, h2[f], M[f], ii[f], jj[f], tot
acc = {'all': [], 'alc': []}
n_pairs = 0; n_zero = 0; n_zero_total = 0; n_hidden_pairs = 0; n_hidden_alloc_pairs = 0; n_alloc_pairs = 0
CH = max(1, 200000 // N)
if SYM and N > 5000: CH = max(1, 400000 // N)
for s in range(r0, r1, CH):
    e = min(r1, s + CH)
    jlo = s if SYM else 0
    NJ = N - jlo
    Mc = (Af[s * 8:e * 8] @ Af[jlo * 8:].T).reshape(e - s, 8, NJ, 8).transpose(0, 2, 1, 3).reshape(-1, 8, 8)
    Mi = np.rint(Mc).astype(np.int64)
    ii = np.repeat(np.arange(s, e), NJ); jj = np.tile(np.arange(jlo, N), e - s)
    valid = (jj >= ii) if SYM else np.ones(len(ii), dtype=bool)
    pos = Mi.sum((1, 2)) > 0
    n_zero += int((valid & ~pos).sum())
    nz = valid & pos
    Mi = Mi[nz]; ii = ii[nz]; jj = jj[nz]
    gg = np.gcd.reduce(Mi.reshape(len(Mi), 64), axis=1)
    Mn = Mi // gg[:, None, None]
    hA, hB = c.hidden_batch(Mn)
    hid = hA & hB
    al = alloc[ii] & alloc[jj]
    n_pairs += len(Mn); n_hidden_pairs += int(hid.sum()); n_hidden_alloc_pairs += int((hid & al).sum()); n_alloc_pairs += int(al.sum())
    if HIDONLY:
        Mn = Mn[hid]; ii = ii[hid]; jj = jj[hid]; al = al[hid]
        if len(Mn) == 0: continue
    flatM = Mn.reshape(len(Mn), 64)
    h1, h2 = c.canon_keys(flatM.astype(np.int64))
    for name, sel in (('all', slice(None)), ('alc', al)):
        if ALLALLOC and name == 'alc': continue
        hh = h1[sel]; 
        if hh.size == 0: continue
        u, f, cnt = np.unique(hh, return_index=True, return_counts=True)
        acc[name].append((u, h2[sel][f], flatM[sel][f].astype(np.int32), ii[sel][f], jj[sel][f], cnt))
    for name in acc:
        if sum(len(p[0]) for p in acc[name]) > 1500000:
            acc[name] = [merge(acc[name])]
    if (s - r0) % (CH * 10) == 0:
        print(f'  rows {s}/{r1}  pairs so far {n_pairs}  {time.time() - t0:.0f}s', flush=True)

uA, _, MA, iiA, jjA, cntA = merge(acc['all'])
if ALLALLOC:
    uL, ML, iiL, jjL, cntL = uA, MA, iiA, jjA, cntA
else:
    uL, _, ML, iiL, jjL, cntL = merge(acc['alc']) if acc['alc'] else (np.array([], dtype=np.int64),) * 6
nU = len(uA)
is_alc = np.zeros(nU, dtype=bool)
if len(uL): is_alc[np.searchsorted(uA, uL)] = True
cnt_alc = np.zeros(nU, dtype=np.int64)
if len(uL): cnt_alc[np.searchsorted(uA, uL)] = cntL
print(f'unique normalised old tables M: {nU} (in the allocation class {int(is_alc.sum())}); pairs {n_pairs}; {time.time() - t0:.0f}s', flush=True)

M = MA.reshape(-1, 8, 8).astype(np.int64)
hA, hB = c.hidden_batch(M); hid = hA & hB
print(f'hidden unique M: {int(hid.sum())}; {time.time() - t0:.0f}s', flush=True)
score = c.score_batch_c(M)
print(f'scored uniform; {time.time() - t0:.0f}s', flush=True)
ctrl = c.score_batch_c(M, control=True)
print(f'scored control; {time.time() - t0:.0f}s', flush=True)
tv = c.tv_batch(M)

def top(mask, name, k=3):
    if not mask.any(): return dict(name=name, none=True)
    ids = np.nonzero(mask)[0]
    o = ids[np.argsort(-score[ids])[:k]]
    return [dict(i=int(iiA[q]), j=int(jjA[q]), score=float(score[q]), tv=float(tv[q]), hidden=bool(hid[q]), pairs=int(cntA[q]),
                 M=M[q].tolist()) for q in o]

summary = dict(tag=tag, sym=SYM, hidden_only=HIDONLY, cut=int(np.log2(K)), exact_tables=n_exact, nonempty_tables=n_nonempty, projective_tables=N_proj, tables_combined=N, allocation_tables=int(alloc.sum()),
               rows=[r0, r1], pairs_evaluated=n_pairs, pairs_with_no_word=n_zero, alloc_pairs=n_alloc_pairs, pairs_hidden=n_hidden_pairs,
               pairs_hidden_alloc=n_hidden_alloc_pairs, unique_M=nU, unique_M_alloc=int(is_alc.sum()), unique_M_hidden=int(hid.sum()),
               unique_M_hidden_alloc=int((hid & is_alc).sum()),
               max_score_hidden=float(score[hid].max()) if hid.any() else None,
               max_score_hidden_alloc=float(score[hid & is_alc].max()) if (hid & is_alc).any() else None,
               max_score_all=float(score.max()), max_score_all_alloc=float(score[is_alc].max()) if is_alc.any() else None,
               max_control_all=float(ctrl.max()), max_control_hidden=float(ctrl[hid].max()) if hid.any() else None,
               n_hidden_ge2=int((hid & (score >= 2 - c.TOL)).sum()), n_hidden_gt2=int((hid & (score > 2 + c.TOL)).sum()),
               n_hidden_ge2_alloc=int((hid & is_alc & (score >= 2 - c.TOL)).sum()),
               n_hidden_gt2_alloc=int((hid & is_alc & (score > 2 + c.TOL)).sum()),
               n_all_gt2=int((score > 2 + c.TOL).sum()), n_all_gt2_alloc=int((is_alc & (score > 2 + c.TOL)).sum()),
               n_control_gt2=int((ctrl > 2 + c.TOL).sum()),
               seconds=round(time.time() - t0, 1))
# exact verification of every hidden M that reaches 2 within the tolerance
reach = np.nonzero(hid & (score >= 2 - c.TOL))[0]
exact_gt2 = []
exact_vals = {}
for q in reach:
    v = c.exact_best(M[q])[0]
    exact_vals[int(q)] = v
    if v > 2: exact_gt2.append(int(q))
summary['hidden_reaching_2_exact_check'] = dict(n=len(reach), exact_gt2=len(exact_gt2),
                                               exact_max=str(max(exact_vals.values())) if exact_vals else None)
# exact value of the largest scores of each kind
def exact_top(mask):
    if not mask.any(): return None
    q = int(np.nonzero(mask)[0][np.argmax(score[mask])])
    v, combo, pat = c.exact_best(M[q])
    return dict(M_index=q, i=int(iiA[q]), j=int(jjA[q]), exact=str(v), float=float(v), combo=combo, pattern=pat, hidden=bool(hid[q]), pairs=int(cntA[q]),
                tv_exact=str(c.exact_tv(M[q])), M=M[q].tolist())
summary['top_hidden'] = exact_top(hid); summary['top_hidden_alloc'] = exact_top(hid & is_alc)
summary['top_all'] = exact_top(np.ones(nU, dtype=bool)); summary['top_all_alloc'] = exact_top(is_alc)
mm = ~hid
summary['top_nonhidden'] = exact_top(mm); summary['top_nonhidden_alloc'] = exact_top(mm & is_alc)
# structures of the representative tables
def struct(i, alloc_pref=True):
    e = meta['structures'][int(rep[i])]
    return e['alloc_struct'] if (alloc_pref and e['alloc_struct'] is not None) else e['struct']
for k in ('top_hidden', 'top_hidden_alloc', 'top_all', 'top_all_alloc', 'top_nonhidden', 'top_nonhidden_alloc'):
    if summary[k]:
        summary[k]['side_A'] = struct(summary[k]['i']); summary[k]['side_B'] = struct(summary[k]['j'])
        summary[k]['T_A'] = Tp[summary[k]['i']].tolist(); summary[k]['T_B'] = Tp[summary[k]['j']].tolist()
# histogram of scores of hidden unique M
vals, cn = np.unique(np.round(score[hid], 6), return_counts=True)
summary['hidden_score_histogram'] = {str(v): int(k) for v, k in zip(vals[-12:], cn[-12:])}
summary['hidden_score_distinct_values'] = int(len(vals))
vals, cn = np.unique(np.round(score, 6), return_counts=True)
summary['all_score_top_values'] = {str(v): int(k) for v, k in zip(vals[-8:], cn[-8:])}
json.dump(summary, open(f'{c.ART}/pairs_{outname}_{r0}_{r1}_summary.json', 'w'), indent=1, default=str)
# hidden unique tables, for the extra tests
sv = hid if SAVEMIN is None else (hid & (score >= SAVEMIN))
np.savez_compressed(f'{c.ART}/pairs_{outname}_{r0}_{r1}_hidden.npz', M=M[sv].astype(np.int32), score=score[sv], ctrl=ctrl[sv], tv=tv[sv],
                    i=iiA[sv], j=jjA[sv], pairs=cntA[sv], alloc=is_alc[sv], rep=rep, Tp=Tp.astype(np.int32), alloc_tab=alloc,
                    exact_gt2=np.array(exact_gt2, dtype=np.int64))
print(json.dumps({k: v for k, v in summary.items() if not k.startswith('top_')}, indent=1, default=str))
for k in ('top_hidden', 'top_hidden_alloc', 'top_all', 'top_all_alloc', 'top_nonhidden'):
    s = summary[k]
    if s: print(k, s['exact'], s['float'], 'pairs', s['pairs'], 'tv', s['tv_exact'])
print(f'done {time.time() - t0:.0f}s')
