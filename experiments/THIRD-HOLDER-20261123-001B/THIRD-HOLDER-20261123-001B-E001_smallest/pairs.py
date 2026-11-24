"""Combine side tables in pairs and evaluate them (THIRD-HOLDER-20261123-001B pre-registration, "Census"; pairing as in
REVIEW-LEADS-20261123-001C's pairs.py).

usage: pairs.py TAG [--tagB TAGB] [--mode lemma|full] [--rows R0 R1] [--out NAME]

Both sides use the same cut size.  Tables are divided by the gcd of their entries (scaling a side changes no evaluated
quantity).  Alice's table T_A and Bob's T_B give the old table M = T_A T_B^T.

--mode full   every ordered pair of projective tables is combined; M is normalised, deduplicated up to the 32 symmetries of
              the evaluation, tested for hiding exactly and scored (ticket C's method).
--mode lemma  every ordered pair is classified exactly by the reduction below, and only the pairs it cannot exclude are
              combined, normalised, deduplicated and scored.

The reduction (proved in deviations.md, item 4; checked against --mode full in gates.py).  For a side table T write
p_b(T) = T^T W_b (one entry per value of the shared distinctions).  Alice's complete record hides Bob's setting iff
T_A p_0(T_B) || T_A p_1(T_B); Bob's iff T_B p_0(T_A) || T_B p_1(T_A).  (1) If p_0 || p_1 for both tables ("parallel"), the
four record tables have one common local explanation (hidden value = the shared distinctions, weight p_0 p_1 entrywise), so
the pair is hidden and the score is at most 2.  (2) If a table has rank 1, M has rank 1 and the score is at most 2 (the
pair is hidden).  (3) Otherwise a hidden pair has a non-parallel side, say Bob's, and then Alice's hiding needs the kernel
of T_A to meet the plane span(p_0(T_B), p_1(T_B)); with one shared distinction that never happens for rank 2, so every
excess needs two shared distinctions.  The test depends on T_A only through its kernel and on T_B only through that plane,
so it is decided once per (kernel, plane) class, exactly in integers.  (4) If M has rank at most 2 it has a non-negative
factorization through two values (the columns of M span a pointed two-dimensional cone with two extreme columns), and by
(1)-(3) with one shared two-valued factor the score is at most 2; so an excess needs both tables of rank at least 3, and the
hiding side, whose kernel is non-zero, of rank exactly 3.  Every hidden pair that is not excluded by (1), (2) or (4) is
combined and scored, in the orientation with the non-parallel side as Bob (the evaluation is unchanged by exchanging the
observers).  With --count-hidden, kind (4) is not used, and the hidden pairs are counted exactly.
"""
import sys, json, time, math, itertools
import numpy as np
from fractions import Fraction
import common as c

args = sys.argv[1:]
tag = args[0]
tagB = args[args.index('--tagB') + 1] if '--tagB' in args else tag
mode = args[args.index('--mode') + 1] if '--mode' in args else 'lemma'
# --count-hidden: hiding side of rank 2 or 3 (every hidden pair not of kind (1) or (2) is enumerated, so hidden pairs are counted
# exactly); default: hiding side of rank 3 and partner of rank >= 3 (kind (4) below excluded without enumeration)
COUNT_HIDDEN = '--count-hidden' in args
STATS_ONLY = '--stats-only' in args
r0, r1 = 0, None
if '--rows' in args:
    k = args.index('--rows'); r0 = int(args[k + 1]); r1 = int(args[k + 2])
outname = args[args.index('--out') + 1] if '--out' in args else f'{tag}__{tagB}_{mode}'
t0 = time.time()
def log(*a):
    print(f'[{time.time() - t0:7.1f}s]', *a, flush=True)

# ---- tables ---------------------------------------------------------------------------------------------------------
def load(tg):
    d = np.load(f'{c.ART}/sides_{tg}.npz')
    T = d['T'].astype(np.int64); ne = d['nonempty']
    kn = d['knots'].astype(np.int64); ex = d['extra'].astype(np.int64)
    idx0 = np.nonzero(ne)[0]
    T = T[ne]; kn = kn[ne]; ex = ex[ne]
    g = np.gcd.reduce(T.reshape(len(T), -1), axis=1)
    Tp = T // g[:, None, None]
    flat = Tp.reshape(len(Tp), -1)
    U, inv = np.unique(flat, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    # representative exact table: fewest knots, then fewest extra holders
    order = np.lexsort((ex, kn, inv))
    first = np.ones(len(order), dtype=bool); first[1:] = inv[order][1:] != inv[order][:-1]
    rep = np.empty(len(U), dtype=np.int64); rep[inv[order][first]] = order[first]
    return dict(T=U.reshape(len(U), 8, -1), rep=idx0[rep], knots=kn[rep], extra=ex[rep], n_exact=int(len(d['T'])),
                n_nonempty=int(ne.sum()), mult=np.bincount(inv, minlength=len(U)))

SA = load(tag)
SB = SA if tagB == tag else load(tagB)
K = SA['T'].shape[2]
assert SB['T'].shape[2] == K
NA, NB = len(SA['T']), len(SB['T'])
log(f'{tag} x {tagB}: exact tables {SA["n_exact"]} / {SB["n_exact"]}, projective {NA} / {NB}, shared distinctions {int(math.log2(K))}')

summary = dict(tagA=tag, tagB=tagB, mode=mode, shared=int(math.log2(K)), exact_tables=[SA['n_exact'], SB['n_exact']],
               projective_tables=[NA, NB], ordered_pairs=NA * NB)

def supp_mask(T):
    return ((T.sum(1) > 0) * (1 << np.arange(K))).sum(1)

# ---- scoring of a stream of (i, j) pairs: M = T_A[i] T_B[j]^T ---------------------------------------------------------
class Scorer:
    def __init__(s):
        s.parts = []; s.n_pairs = 0; s.n_zero = 0; s.n_hidden = 0
    def add(s, TA, TB, ii, jj, sizeA, sizeB):
        """TA (n,8,K), TB (n,8,K) for the pairs; sizeA/B = (knots, extra) arrays."""
        M = np.einsum('nxk,nyk->nxy', TA, TB)
        pos = M.reshape(len(M), -1).sum(1) > 0
        s.n_pairs += len(M); s.n_zero += int((~pos).sum())
        M = M[pos]; ii = ii[pos]; jj = jj[pos]
        kn = sizeA[0][pos] + sizeB[0][pos]; ex = sizeA[1][pos] + sizeB[1][pos]
        if len(M) == 0: return
        g = np.gcd.reduce(M.reshape(len(M), 64), axis=1)
        M = M // g[:, None, None]
        hA, hB = c.hidden_batch(M); hid = hA & hB
        s.n_hidden += int(hid.sum())
        flat = M.reshape(len(M), 64)
        h1, h2 = c.canon_keys(flat)
        # per key keep the pair with the smallest size (knots, then extra holders)
        o = np.lexsort((ex, kn, h1))
        f = np.ones(len(o), dtype=bool); f[1:] = h1[o][1:] != h1[o][:-1]
        cnt = np.diff(np.append(np.nonzero(f)[0], len(o)))
        sel = o[f]
        s.parts.append((h1[sel], h2[sel], flat[sel].astype(np.int64), ii[sel], jj[sel], kn[sel], ex[sel], hid[sel], cnt))
        if sum(len(p[0]) for p in s.parts) > 2_000_000:
            s.parts = [s.merge()]
    def merge(s):
        cols = [np.concatenate([p[q] for p in s.parts]) for q in range(9)]
        h1, h2, flat, ii, jj, kn, ex, hid, cnt = cols
        o = np.lexsort((ex, kn, h1))
        f = np.ones(len(o), dtype=bool); f[1:] = h1[o][1:] != h1[o][:-1]
        starts = np.nonzero(f)[0]
        tot = np.add.reduceat(cnt[o], starts) if len(o) else cnt[:0]
        sel = o[f]
        assert (h2[o] == np.repeat(h2[sel], np.diff(np.append(starts, len(o))))).all(), 'hash collision'
        return (h1[sel], h2[sel], flat[sel], ii[sel], jj[sel], kn[sel], ex[sel], hid[sel], tot)

def evaluate_unique(parts, scorer):
    if not parts:
        return dict(unique_M=0)
    h1, h2, flat, ii, jj, kn, ex, hid, cnt = parts
    M = flat.reshape(-1, 8, 8)
    out = dict(unique_M=int(len(M)), unique_M_hidden=int(hid.sum()))
    score = c.score_batch_c(M)
    log(f'scored {len(M)} unique old tables')
    out['max_score_all'] = float(score.max())
    out['max_score_hidden_float'] = float(score[hid].max()) if hid.any() else None
    near = np.nonzero(hid & (score >= 2 - c.TOL))[0]
    exact = {}
    for q in near:
        exact[int(q)] = c.exact_best(M[q], slack=1e-9)[0]
    log(f'exact check of {len(near)} hidden old tables reaching 2 within 1e-9')
    gt2 = [q for q, v in exact.items() if v > 2]
    out['n_hidden_reach2'] = int(len(near)); out['n_hidden_gt2'] = len(gt2)
    out['n_hidden_eq2_exact'] = sum(1 for v in exact.values() if v == 2)
    out['max_score_hidden_exact'] = str(max(exact.values())) if exact else None
    out['n_all_gt2_float'] = int((score > 2 + c.TOL).sum())
    # top non-hidden
    if (~hid).any():
        q = int(np.nonzero(~hid)[0][np.argmax(score[~hid])])
        out['top_nonhidden'] = dict(exact=str(c.exact_best(M[q], slack=1e-9)[0]), change=str(c.exact_tv(M[q])), i=int(ii[q]), j=int(jj[q]))
    # control weighting
    ctrl = c.score_batch_c(M, control=True)
    out['max_control'] = float(ctrl.max())
    ex_list = []
    for q in sorted(gt2, key=lambda q: (int(kn[q]), int(ex[q]), -exact[q])):
        ex_list.append(dict(score=str(exact[q]), score_float=float(exact[q]), knots=int(kn[q]), extra_holders=int(ex[q]), i=int(ii[q]),
                            j=int(jj[q]), pairs=int(cnt[q]), change=str(c.exact_tv(M[q])), M=M[q].tolist()))
    out['excess'] = ex_list
    vals, cn = np.unique(np.round(score[hid], 6), return_counts=True)
    out['hidden_score_top_values'] = {str(v): int(k) for v, k in zip(vals[-8:], cn[-8:])}
    return out

sizeA_all = (SA['knots'], SA['extra']); sizeB_all = (SB['knots'], SB['extra'])

if mode == 'full':
    r1 = NA if r1 is None else min(r1, NA)
    sc = Scorer()
    CH = max(1, 300000 // NB)
    for s in range(r0, r1, CH):
        e = min(r1, s + CH)
        ii = np.repeat(np.arange(s, e), NB); jj = np.tile(np.arange(NB), e - s)
        sc.add(SA['T'][ii], SB['T'][jj], ii, jj, (SA['knots'][ii], SA['extra'][ii]), (SB['knots'][jj], SB['extra'][jj]))
        if ((s - r0) // CH) % 50 == 0: log(f'rows {s}/{r1}, pairs {sc.n_pairs}')
    parts = sc.merge() if sc.parts else None
    summary.update(rows=[r0, r1], pairs_combined=sc.n_pairs, pairs_no_word=sc.n_zero, pairs_hidden=sc.n_hidden)
    summary.update(evaluate_unique(parts, sc))
else:
    # ---- exact classification --------------------------------------------------------------------------------------------
    import pairlib as pl
    def classify(S):
        return pl.classify(S['T'])

    CA = classify(SA); CB = CA if SB is SA else classify(SB)
    for nm, CC in (('A', CA), ('B', CB)):
        log(f'side {nm}: rank counts {dict(zip(*np.unique(CC["rank"], return_counts=True)))}; parallel {int(CC["par"].sum())}, '
            f'non-parallel {int((~CC["par"]).sum())}')
    summary['rank_counts'] = [{int(k): int(v) for k, v in zip(*np.unique(CC['rank'], return_counts=True))} for CC in (CA, CB)]
    summary['parallel_counts'] = [int(CA['par'].sum()), int(CB['par'].sum())]
    assert ((CA['rank'] == 1) <= CA['par']).all() and ((CB['rank'] == 1) <= CB['par']).all()

    # counts of ordered pairs with an allowed old word, by support classes
    def nonzero_pairs(maskA, maskB):
        hA = np.bincount(CA['supp'][maskA], minlength=1 << K); hB = np.bincount(CB['supp'][maskB], minlength=1 << K)
        S = np.array([[1 if (a & b) else 0 for b in range(1 << K)] for a in range(1 << K)])
        return int(hA @ S @ hB)
    allA = np.ones(NA, bool); allB = np.ones(NB, bool)
    summary['pairs_with_word'] = nonzero_pairs(allA, allB)
    pp = nonzero_pairs(CA['par'], CB['par'])                                   # kind (1): hidden, local
    r1q = nonzero_pairs(CA['rank'] == 1, ~CB['par'])                           # kind (2), Alice rank 1, Bob non-parallel
    q1r = nonzero_pairs(~CA['par'], CB['rank'] == 1)                           # mirror
    summary['hidden_pairs_kind1_both_parallel'] = pp
    summary['hidden_pairs_kind2_rank1_with_nonparallel'] = r1q + q1r

    # kernel classes (Alice role: rank 2 or 3) and plane classes (Bob role: non-parallel)
    def classes(keys):
        u, inv = np.unique(keys, axis=0, return_inverse=True)
        return u, inv.reshape(-1)
    if COUNT_HIDDEN:
        selA = np.nonzero((CA['rank'] == 2) | (CA['rank'] == 3))[0]
        selB = np.nonzero(~CB['par'])[0]
    else:
        selA = np.nonzero(CA['rank'] == 3)[0]
        selB = np.nonzero(~CB['par'] & (CB['rank'] >= 3))[0]
    kA = np.concatenate([CA['rank'][selA][:, None], CA['key'][selA]], 1)
    uK, invK = classes(kA)
    uP, invP = classes(CB['P'][selB]) if len(selB) else (np.zeros((0, 6), np.int64), np.zeros(0, np.int64))
    log(f'kernel classes {len(uK)} (Alice role), plane classes {len(uP)} (Bob role)')
    summary['kernel_classes'] = int(len(uK)); summary['plane_classes'] = int(len(uP))

    def compat_matrix(uK, uP):
        return pl.compat_matrix(uK, uP, K)
    CM = compat_matrix(uK, uP)
    log(f'compatible (kernel, plane) classes: {int(CM.sum())}')
    summary['compatible_class_pairs'] = int(CM.sum())

    # Bob-side test for a candidate pair: Bob's table (non-parallel, as B) has its own kernel; Alice's table has its p-plane
    # unless parallel.  Build the same classes for that test: kernels of side B, planes of side A.
    selB2 = np.nonzero((CB['rank'] == 2) | (CB['rank'] == 3))[0] if COUNT_HIDDEN else np.nonzero(CB['rank'] == 3)[0]
    kB = np.concatenate([CB['rank'][selB2][:, None], CB['key'][selB2]], 1)
    uK2, invK2 = classes(kB) if len(selB2) else (np.zeros((0, 7), np.int64), np.zeros(0, np.int64))
    selA2 = np.nonzero(~CA['par'])[0]
    uP2, invP2 = classes(CA['P'][selA2]) if len(selA2) else (np.zeros((0, 6), np.int64), np.zeros(0, np.int64))
    CM2 = compat_matrix(uK2, uP2)
    kid_B = np.full(NB, -1); kid_B[selB2] = invK2
    pid_A = np.full(NA, -1); pid_A[selA2] = invP2

    groupsA = [[] for _ in range(len(uK))]
    for t, g in zip(selA, invK): groupsA[g].append(t)
    groupsB = [[] for _ in range(len(uP))]
    for t, g in zip(selB, invP): groupsB[g].append(t)
    groupsA = [np.array(g, dtype=np.int64) for g in groupsA]; groupsB = [np.array(g, dtype=np.int64) for g in groupsB]
    gi, gj = np.nonzero(CM)
    est = int(sum(len(groupsA[a]) * len(groupsB[b]) for a, b in zip(gi, gj)))
    log(f'pairs in compatible classes (before the Bob-side test): {est}')
    summary['pairs_alice_side_compatible'] = est
    summary['count_hidden'] = COUNT_HIDDEN
    summary['alice_role_tables'] = int(len(selA)); summary['bob_role_tables'] = int(len(selB))
    if STATS_ONLY:
        json.dump(summary, open(f'{c.ART}/pairs_{outname}_stats.json', 'w'), indent=1, default=str)
        print(json.dumps(summary, indent=1, default=str)); sys.exit(0)
    sc = Scorer()
    n_cand = 0; n_cand_Apar = 0; n_cand_Aq = 0
    bufA = []; bufB = []; nbuf = 0
    def flush():
        global bufA, bufB, nbuf
        if not bufA: return
        ii = np.concatenate(bufA); jj = np.concatenate(bufB)
        sc.add(SA['T'][ii], SB['T'][jj], ii, jj, (SA['knots'][ii], SA['extra'][ii]), (SB['knots'][jj], SB['extra'][jj]))
        bufA = []; bufB = []; nbuf = 0
    for q, (a, b) in enumerate(zip(gi, gj)):
        A = groupsA[a]; B = groupsB[b]
        ii = np.repeat(A, len(B)); jj = np.tile(B, len(A))
        # Bob's hiding: Alice parallel, or Bob's kernel meets Alice's plane
        okB = CA['par'][ii].copy()
        q2 = ~okB
        if q2.any():
            kb = kid_B[jj[q2]]; pa = pid_A[ii[q2]]
            good = (kb >= 0) & (pa >= 0)
            res = np.zeros(int(q2.sum()), dtype=bool)
            res[good] = CM2[kb[good], pa[good]]
            okB[q2] = res
        nzw = (CA['supp'][ii] & CB['supp'][jj]) != 0
        keep = okB & nzw
        ii = ii[keep]; jj = jj[keep]
        n_cand += len(ii); n_cand_Apar += int(CA['par'][ii].sum()); n_cand_Aq += int((~CA['par'][ii]).sum())
        if len(ii):
            bufA.append(ii); bufB.append(jj); nbuf += len(ii)
        if nbuf > 400000: flush()
        if q % 20000 == 0: log(f'class pair {q}/{len(gi)}, candidates {n_cand}')
    flush()
    log(f'candidate pairs (hidden, not excluded by (1) or (2)): {n_cand}')
    summary['candidate_pairs'] = n_cand
    summary['candidate_pairs_alice_parallel'] = n_cand_Apar
    summary['candidate_pairs_both_nonparallel'] = n_cand_Aq
    parts = sc.merge() if sc.parts else None
    summary['candidate_pairs_hidden_check'] = sc.n_hidden            # must equal candidate_pairs
    summary['candidate_pairs_no_word'] = sc.n_zero
    # hidden ordered pairs in all: kind (1) + kind (2) + candidates in both orientations
    if tagB == tag and COUNT_HIDDEN:
        summary['hidden_ordered_pairs'] = pp + r1q + q1r + 2 * n_cand_Apar + n_cand_Aq
    summary.update(evaluate_unique(parts, sc))

summary['seconds'] = round(time.time() - t0, 1)
# structures of the excess pairs (first 50, smallest first)
for e in summary.get('excess', [])[:50]:
    for side, S, key in (('A', SA, 'i'), ('B', SB, 'j')):
        e[f'T_{side}'] = S['T'][e[key]].tolist(); e[f'rep_{side}'] = int(S['rep'][e[key]])
json.dump(summary, open(f'{c.ART}/pairs_{outname}_summary.json', 'w'), indent=1, default=str)
print(json.dumps({k: v for k, v in summary.items() if k != 'excess'}, indent=1, default=str))
print('excess pairs (unique old tables):', len(summary.get('excess', [])))
for e in summary.get('excess', [])[:5]:
    print('  ', e['score'], 'knots', e['knots'], 'extra', e['extra_holders'], 'change', e['change'])
log('done')
