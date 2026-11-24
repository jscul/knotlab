"""Pairs of side tables evaluated by the compiled pair_eval.c (THIRD-HOLDER-20261123-001B-E001), for classes too large for
pairs.py.  Same evaluation as pairs.py; the pairs scored are those the reduction of pairlib.py cannot exclude (or every
ordered pair with --full).  Tables are first reduced to one per orbit under the four row maps of a side (pairlib.orbit_reps).

usage: pairs_c.py prep TAG [--tagB TAGB] [--full] [--name NAME] [--per-run PAIRS]
       pairs_c.py eval NAME RUN            (one run = one range of class pairs, listed by prep)
       pairs_c.py merge NAME
"""
import sys, os, json, time, math, subprocess, glob
import numpy as np
from fractions import Fraction
import common as c, pairlib as pl

t0 = time.time()
def log(*a): print(f'[{time.time() - t0:7.1f}s]', *a, flush=True)
cmd = sys.argv[1]

def write_input(path, SA, SB, gA, gB, qA, qB):
    K = SA['T'].shape[2]
    offA = np.zeros(len(gA) + 1, np.int64); offA[1:] = np.cumsum([len(g) for g in gA])
    offB = np.zeros(len(gB) + 1, np.int64); offB[1:] = np.cumsum([len(g) for g in gB])
    memA = np.concatenate(gA) if gA else np.zeros(0, np.int64); memB = np.concatenate(gB) if gB else np.zeros(0, np.int64)
    with open(path, 'wb') as f:
        np.array([K, len(SA['T']), len(SB['T']), len(gA), len(gB), len(qA)], np.int32).tofile(f)
        for arr in (SA['T'], SB['T'], SA['knots'], SA['extra'], SB['knots'], SB['extra'], offA, memA, offB, memB, qA, qB):
            np.asarray(arr).astype(np.int32).tofile(f)
        np.ascontiguousarray(np.stack(c.Cf)).astype(np.float64).tofile(f)
        np.ascontiguousarray(c.Wf).astype(np.float64).tofile(f)

if cmd == 'prep':
    args = sys.argv[2:]
    tag = args[0]; tagB = args[args.index('--tagB') + 1] if '--tagB' in args else tag
    full = '--full' in args
    name = args[args.index('--name') + 1] if '--name' in args else f'{tag}__{tagB}_{"full" if full else "lemma"}'
    per_run = int(args[args.index('--per-run') + 1]) if '--per-run' in args else 200_000_000
    SA = pl.orbit_reps(pl.load(tag)); SB = SA if tagB == tag else pl.orbit_reps(pl.load(tagB))
    K = SA['T'].shape[2]
    log(f'{tag} x {tagB}: projective tables {SA["n_projective"]} / {SB["n_projective"]}, orbit representatives {len(SA["T"])} / {len(SB["T"])}')
    meta = dict(tagA=tag, tagB=tagB, full=full, shared=int(math.log2(K)), exact_tables=[SA['n_exact'], SB['n_exact']],
                projective_tables=[SA['n_projective'], SB['n_projective']], orbit_reps=[len(SA['T']), len(SB['T'])],
                ordered_pairs_projective=SA['n_projective'] * SB['n_projective'])
    CA = pl.classify(SA['T']); CB = CA if SB is SA else pl.classify(SB['T'])
    meta['rank_counts'] = [{int(k): int(v) for k, v in zip(*np.unique(CC['rank'], return_counts=True))} for CC in (CA, CB)]
    meta['parallel_reps'] = [int(CA['par'].sum()), int(CB['par'].sum())]
    log('classified', meta['rank_counts'], meta['parallel_reps'])
    if full:
        gA = [np.arange(len(SA['T']))]; gB = [np.arange(len(SB['T']))]; qA = np.array([0]); qB = np.array([0])
    else:
        selA = np.nonzero(CA['rank'] == 3)[0]
        selB = np.nonzero(~CB['par'] & (CB['rank'] >= 3))[0]
        uK, invK = pl.classes(np.concatenate([CA['rank'][selA][:, None], CA['key'][selA]], 1))
        uP, invP = pl.classes(CB['P'][selB])
        CM = pl.compat_matrix(uK, uP, K)
        gA = [selA[invK == g] for g in range(len(uK))]
        gB = [selB[invP == g] for g in range(len(uP))]
        qA, qB = np.nonzero(CM)
        meta.update(alice_role_reps=int(len(selA)), bob_role_reps=int(len(selB)), kernel_classes=int(len(uK)), plane_classes=int(len(uP)),
                    compatible_class_pairs=int(len(qA)))
    # split large Alice groups so that no class pair holds more than a twentieth of a run
    lim = max(1, per_run // 20)
    gA2 = []; qA2 = []; qB2 = []
    sub = [None] * len(gA)                     # sub-groups of each Alice group
    biggestB = {}
    for a, b in zip(qA, qB): biggestB[a] = max(biggestB.get(a, 0), len(gB[b]))
    for a in range(len(gA)):
        step = max(1, lim // max(1, biggestB.get(a, 1)))
        sub[a] = list(range(len(gA2), len(gA2) + (len(gA[a]) + step - 1) // step))
        for i0 in range(0, len(gA[a]), step): gA2.append(gA[a][i0:i0 + step])
        if len(gA[a]) == 0: sub[a] = []
    for a, b in zip(qA, qB):
        for a2 in sub[a]: qA2.append(a2); qB2.append(b)
    gA = gA2; qA = np.array(qA2, dtype=np.int64); qB = np.array(qB2, dtype=np.int64)
    npairs = np.array([len(gA[a]) * len(gB[b]) for a, b in zip(qA, qB)], dtype=np.int64)
    meta['pairs_to_evaluate'] = int(npairs.sum())
    # runs: consecutive ranges of class pairs with about per_run pairs each
    runs = []; s = 0; acc = 0
    for q in range(len(npairs)):
        acc += int(npairs[q])
        if acc >= per_run:
            runs.append([s, q + 1]); s = q + 1; acc = 0
    if s < len(npairs) or not runs: runs.append([s, len(npairs)])
    meta['runs'] = runs
    np.savez_compressed(f'{c.ART}/pc_{name}_reps.npz', repA=SA['rep'], repB=SB['rep'], TA=SA['T'], TB=SB['T'], kA=SA['knots'], eA=SA['extra'],
                        kB=SB['knots'], eB=SB['extra'], orbA=SA['orbit_size'], orbB=SB['orbit_size'])
    write_input(f'{c.ART}/pc_{name}.in', SA, SB, gA, gB, qA, qB)
    json.dump(meta, open(f'{c.ART}/pc_{name}_meta.json', 'w'), indent=1)
    log(json.dumps({k: v for k, v in meta.items() if k != 'runs'}))
    log(f'{len(runs)} runs')

elif cmd == 'eval':
    # eval NAME RUN  (a run listed by prep)   or   eval NAME Q0 Q1  (an explicit range of class pairs)
    name = sys.argv[2]
    meta = json.load(open(f'{c.ART}/pc_{name}_meta.json'))
    if len(sys.argv) > 4:
        q0, q1 = int(sys.argv[3]), int(sys.argv[4]); run = f'q{q0}_{q1}'
    else:
        run = int(sys.argv[3]); q0, q1 = meta['runs'][run]
    out = f'{c.ART}/pc_{name}_run{run}'
    p = subprocess.run(['timeout', '590', f'{c.ART}/pair_eval', f'{c.ART}/pc_{name}.in', out, str(q0), str(q1)], capture_output=True, text=True)
    if p.returncode != 0:
        print('pair_eval failed', p.returncode, p.stdout, p.stderr); sys.exit(1)
    r = json.load(open(out + '.json'))
    log(f'run {run} class pairs {q0}..{q1}: pairs {r["pairs"]}, hidden {r["pairs_hidden"]}, unique hidden {r["unique_hidden_M"]}, '
        f'>= 2 - 1e-9: {r["unique_ge2_float"]}, > 2 + 1e-9: {r["unique_gt2_float"]}, max {r["max_score_float"]:.12f}, cpu {r["cpu_seconds"]}s')

elif cmd == 'merge':
    name = sys.argv[2]
    meta = json.load(open(f'{c.ART}/pc_{name}_meta.json'))
    R = np.load(f'{c.ART}/pc_{name}_reps.npz')
    tot = dict(pairs=0, pairs_no_word=0, pairs_hidden=0, pairs_alice_hidden_only=0, unique_hidden_M_sum_over_runs=0)
    hist = np.zeros(401, np.int64); maxf = 0.0
    recs = []
    # the run outputs present must tile the class pairs [0, NQ) exactly (runs may have been re-split)
    files = sorted(glob.glob(f'{c.ART}/pc_{name}_run*.json'))
    rs = [(json.load(open(f)), f) for f in files]
    rs.sort(key=lambda t: t[0]['class_pairs'][0])
    nq_total = meta['runs'][-1][1]; pos = 0; used = []
    for r, f in rs:
        a_, b_ = r['class_pairs']
        if a_ == pos and b_ > a_: used.append((r, f)); pos = b_
        elif a_ < pos: continue                       # superseded by a run already used
    missing = [] if pos == nq_total else [f'class pairs from {pos}']
    summ_runs = []
    for r, f in used:
        summ_runs.append(os.path.basename(f))
        for k in ('pairs', 'pairs_no_word', 'pairs_hidden', 'pairs_alice_hidden_only'): tot[k] += r[k]
        tot['unique_hidden_M_sum_over_runs'] += r['unique_hidden_M']
        hist += np.array(r['hist_score_x100']); maxf = max(maxf, r['max_score_float'])
        raw = np.fromfile(f.replace('.json', '.near'), dtype=np.int32).reshape(-1, 70)
        recs.append(raw)
    assert not missing, f'missing runs {missing}'
    assert tot['pairs'] == meta['pairs_to_evaluate'], (tot['pairs'], meta['pairs_to_evaluate'])
    near = np.concatenate(recs) if recs else np.zeros((0, 70), np.int32)
    # merge the near lists of the runs: same canonical old table -> keep the smallest pair, add the pair counts
    summ = dict(meta); summ.update(tot); summ['max_score_float'] = maxf; summ['run_files'] = summ_runs
    summ['hist_score_x100_nonzero'] = {f'{i / 100:.2f}': int(v) for i, v in enumerate(hist) if v}
    uniq = {}
    for rec in near:
        key = rec[:64].tobytes(); pr = int(rec[68:70].copy().view(np.int64)[0])
        e = uniq.get(key)
        if e is None: uniq[key] = [rec[:64].copy(), int(rec[64]), int(rec[65]), int(rec[66]), int(rec[67]), pr]
        else:
            e[5] += pr
            if (int(rec[66]), int(rec[67])) < (e[3], e[4]): e[1:5] = [int(rec[64]), int(rec[65]), int(rec[66]), int(rec[67])]
    log(f'near-2 old tables: {len(near)} records, {len(uniq)} distinct')
    # exact check: a value above 2 differs from 2 by at least 1/lcm of the four denominators; the float value is within 1e-13
    excess = []; n_exact2 = 0; n_lcm = 0; n_frac = 0; exact_max = None
    for key, (M, a, b, kn, ex, pr) in uniq.items():
        M = M.reshape(8, 8).astype(np.int64)
        f = float(c.score_batch_c(M[None])[0])
        dens = [int(c.W[a_] @ M @ c.W[b_]) for a_ in (0, 1) for b_ in (0, 1)]
        L = 1
        for d_ in dens: L = L * d_ // math.gcd(L, d_)
        if f <= 2 + 1e-12 and L < 10 ** 11:
            v = None; n_lcm += 1                   # exact value at most 2
        else:
            v = c.exact_best(M, slack=1e-9)[0]; n_frac += 1
        if v is not None and v > 2:
            excess.append(dict(score=str(v), score_float=float(v), knots=kn, extra_holders=ex, a=a, b=b, pairs=pr,
                               change=str(c.exact_tv(M)), M=M.tolist()))
        if v is not None and (exact_max is None or v > exact_max): exact_max = v
    excess.sort(key=lambda e: (e['knots'], e['extra_holders'], -e['score_float']))
    summ['near2_distinct'] = len(uniq); summ['near2_decided_by_denominator_bound'] = n_lcm; summ['near2_decided_by_fractions'] = n_frac
    summ['n_excess_old_tables'] = len(excess)
    if excess: summ['max_hidden_score_exact'] = max((e['score'] for e in excess), key=lambda s: Fraction(s))
    elif uniq: summ['max_hidden_score_exact'] = f'at most 2 ({len(uniq)} old tables within 1e-9 of 2, none above)'
    else: summ['max_hidden_score_exact'] = f'below 2 - 1e-9 (float max {maxf})'
    # structures of the smallest excess pairs
    for e in excess[:200]:
        e['rep_A'] = int(R['repA'][e['a']]); e['rep_B'] = int(R['repB'][e['b']])
        e['T_A'] = R['TA'][e['a']].tolist(); e['T_B'] = R['TB'][e['b']].tolist()
    summ['excess'] = excess
    summ['excess_scores'] = sorted({e['score'] for e in excess}, key=lambda s: -float(Fraction(s)))
    json.dump(summ, open(f'{c.ART}/pc_{name}_summary.json', 'w'), indent=1, default=str)
    print(json.dumps({k: v for k, v in summ.items() if k not in ('excess', 'runs', 'hist_score_x100_nonzero')}, indent=1, default=str))
    for e in excess[:5]: print('  excess', e['score'], 'knots', e['knots'], 'extra', e['extra_holders'], 'change', e['change'])
    log('done')
