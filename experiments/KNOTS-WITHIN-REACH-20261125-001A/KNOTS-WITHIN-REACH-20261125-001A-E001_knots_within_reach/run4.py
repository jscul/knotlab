"""Run 4: the laws with a taking rule (claims 3 and 4).  T1 to T8 with two seeds of uniform takes and T9, T10 under
OLDEST, on the 17 named starts and the 219 small census starts, parity and not-all-equal, 100 rounds, 50,000 knots.
Readings at rounds 1 to 10, 25, 50, 100: knots, greatest holder steps from each start knot under the four steps (holder
steps; (a) parent steps; (b) through distinctions of at most two holders only; (c) weighted, m - 1 through a distinction
of m holders), the holder-number distribution, and the base law's greatest holder steps at the same round.  Under parity
at rounds 1 to 10 and 25: Lambda_t (rank, least number of distinctions in one rule, loose count), tied pairs of loose
distinctions at two knots with their K1-K3 verdicts and holder steps; check P.  The knot test on every knot after round
25 and on 100 later knots.
usage: python -B run4.py run --procs 4 [--limit N]      writes run4.jsonl.gz"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import time

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path

import kwr
from run5 import _View

TLAWS = ('T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10')
READ_ROUNDS = tuple(range(1, 11)) + (25, 50, 100)
LAMBDA_ROUNDS = tuple(range(1, 11)) + (25,)


def starts4():
    return list(kwr.named()['named_starts']) + ['census:%d' % i for i in kwr.small_census()]


def items():
    out = []
    for key in starts4():
        for kl in ('parity', 'nae'):
            for lab in TLAWS:
                seeds = ('takes:1', 'takes:2') if lab not in ('T9', 'T10') else ('OLDEST',)
                for sd in seeds:
                    out.append({'start': key, 'law': lab, 'knot_law': kl, 'seed': sd})
    for k, it in enumerate(out):
        it['item'] = k
    return out


# ------------------------------------------------------------------------------------------------ the four steps
def greatest_steps(S, N, sources):
    """Greatest steps from each source knot within its connected structure, under hs, (a) ps, (b) <= 2 holders,
    (c) weighted; with the holder-number distribution."""
    rows, cols, wts, rows2, cols2 = [], [], [], [], []
    hist = {}
    j = 0
    for d in range(S.n_distinctions):
        hh = [w for w in S.holders[d] if w < N]
        m = len(hh)
        hist[m] = hist.get(m, 0) + 1
        if m >= 2:
            for w in hh:
                rows.append(w)
                cols.append(N + j)
                wts.append((m - 1) / 2.0)
                if m <= 2:
                    rows2.append(w)
                    cols2.append(N + j)
            j += 1
    n = N + j
    ones = np.ones(len(rows))
    Bip = csr_matrix((ones, (rows, cols)), shape=(n, n))
    Bip2 = csr_matrix((np.ones(len(rows2)), (rows2, cols2)), shape=(n, n))
    Wt = csr_matrix((np.array(wts), (rows, cols)), shape=(n, n))
    pr, pc = [], []
    for x in range(N):
        for p in S.parents[x]:
            pr.append(x)
            pc.append(p)
    Par = csr_matrix((np.ones(len(pr)), (pr, pc)), shape=(N, N))
    out = {}
    for name, M, half in (('hs', Bip, True), ('ps', Par, False), ('hs_two_holders', Bip2, True), ('weighted', Wt, False)):
        D = shortest_path(M, method='D', directed=False, unweighted=(name != 'weighted'), indices=list(sources))
        D = D[:, :N]
        if half:
            D = D / 2.0
        g = []
        for row in D:
            f = row[np.isfinite(row)]
            g.append(float(f.max()) if len(f) else 0.0)
        out[name] = [int(round(x)) if name != 'weighted' else round(x, 3) for x in g]
    out['holders_hist'] = {str(k): v for k, v in sorted(hist.items())}
    return out


# --------------------------------------------------------------------------------------------- parity: Lambda_t
def rref(rows):
    """Fully reduced row echelon form over GF(2) (pivot = highest bit): {pivot: row}."""
    piv = {}
    for v in rows:
        for p, r in piv.items():
            if (v >> p) & 1:
                v ^= r
        if not v:
            continue
        p = v.bit_length() - 1
        for q in list(piv):
            if (piv[q] >> p) & 1:
                piv[q] ^= v
        piv[p] = v
    return piv


def lambda_t(S, N, nd):
    """Lambda_t: rules of the allowed states on loose distinctions only (row space of the knots' rules intersected
    with the span of the loose distinctions).  Columns are renumbered so that shared distinctions are the most
    significant bits; then the echelon vectors with a loose leading bit span Lambda_t."""
    loose = [d for d in range(nd) if len([w for w in S.holders[d] if w < N]) == 1]
    shared = [d for d in range(nd) if len([w for w in S.holders[d] if w < N]) >= 2]
    col = {d: i for i, d in enumerate(loose)}
    off = len(loose)
    for i, d in enumerate(shared):
        col[d] = off + i
    rows = []
    for u in range(N):
        v = 0
        for d in S.places[u]:
            if d < nd:
                v |= 1 << col[d]
        rows.append(v)
    piv = rref(rows)
    basis = [r for p, r in piv.items() if p < off]
    rank = len(basis)
    least = None
    if rank and rank <= 20:
        best = None
        # every nonzero combination (Gray code)
        cur = 0
        for k in range(1, 1 << rank):
            b = (k & -k).bit_length() - 1
            cur ^= basis[b]
            w = bin(cur).count('1')
            if best is None or w < best:
                best = w
        least = best
    elif rank:
        least = min(bin(r).count('1') for r in basis)
    # tied pairs: equal signatures over the kernel (allowed states), from the RREF in the original numbering
    rows0 = []
    for u in range(N):
        v = 0
        for d in S.places[u]:
            if d < nd:
                v |= 1 << d
        rows0.append(v)
    piv0 = rref(rows0)
    pivot_of = set(piv0)
    sig = {}
    for d in loose:
        if d in pivot_of:
            sig[d] = piv0[d] ^ (1 << d)
        else:
            sig[d] = 1 << d
    groups = {}
    for d in loose:
        groups.setdefault(sig[d], []).append(d)
    tied = []
    holder = {d: [w for w in S.holders[d] if w < N][0] for d in loose}
    for sgn, ds in groups.items():
        if len(ds) >= 2:
            for i in range(len(ds)):
                for k in range(i + 1, len(ds)):
                    a, b = ds[i], ds[k]
                    if holder[a] != holder[b]:
                        tied.append((a, b, holder[a], holder[b]))
    constant = [d for d in loose if sig[d] == 0]
    return {'rank': rank, 'least': least, 'least_exact': rank <= 20, 'loose': len(loose), 'shared': len(shared),
            'least_lt_loose': (least is not None and least < len(loose))}, tied, constant, piv0, sig


def check_P_small(S, N, nd, sig):
    """Lemma P on a stage of at most 20 distinctions: every pair of distinctions has rho = 0 or 1/2 (enumeration), and
    rho = 0 exactly when the kernel signatures are equal (loose pairs)."""
    x = np.arange(1 << nd, dtype=np.int64)
    ok = np.ones(len(x), dtype=bool)
    for u in range(N):
        m = 0
        for d in S.places[u]:
            if d < nd:
                m |= 1 << d
        par = np.zeros(len(x), dtype=np.int64)
        y = x & m
        while np.any(y):
            par ^= (y & 1)
            y >>= 1
        ok &= (par == 0)
    A = x[ok]
    Z = len(A)
    bad = 0
    for a in range(nd):
        for b in range(a + 1, nd):
            n = int(np.sum(((A >> a) ^ (A >> b)) & 1))
            if not (n == 0 or 2 * n == Z):
                bad += 1
            if a in sig and b in sig and ((n == 0) != (sig[a] == sig[b])):
                bad += 1
    return bad


# ------------------------------------------------------------------------------------------------- one run
def run_item(it):
    t0 = time.time()
    key, lab, kl, sd = it['start'], it['law'], it['knot_law'], it['seed']
    law = kwr.make_law(lab, knot_law=kl)
    ctx = {}
    if sd.startswith('takes'):
        ctx['chooser'] = kwr.UniformTakes(kwr.rng_for(key, lab, kl, sd))
    snaps_rounds = set(LAMBDA_ROUNDS)
    lam_rec = {}
    tied_rec = {}
    checkP = {'stages': 0, 'small_stages': 0, 'bad': 0}

    def on_round(g, rec):
        t = g.S.round
        if kl == 'parity' and t in snaps_rounds:
            S = g.S
            N, nd = S.n_knots, S.n_distinctions
            L, tied, const, piv0, sig = lambda_t(S, N, nd)
            lam_rec[t] = L
            if tied:
                from knots import parity_test
                pt = parity_test(S)
                Gt = kwr.Graphs(S)
                rows = []
                for a, b, u, v in tied[:50]:
                    D = Gt.hs([u])[u]
                    rows.append({'a': a, 'b': b, 'knots': [u, v], 'pass': [bool(pt['pass'][u]), bool(pt['pass'][v])],
                                 'hs': int(D[v]) if np.isfinite(D[v]) else None})
                tied_rec[t] = {'n': len(tied), 'rows': rows}
            checkP['stages'] += 1
            if nd <= 20:
                checkP['small_stages'] += 1
                checkP['bad'] += check_P_small(S, N, nd, sig)

    gr = kwr.Grown(key, law, 100, ctx=ctx, on_round=on_round, parts_every_round=False)
    S = gr.S
    rec = {'item': it['item'], 'start': key, 'law': lab, 'knot_law': kl, 'seed': sd, 'rounds_done': gr.rounds_done,
           'stop': gr.stop, 'ended': gr.ended, 'guard': gr.guard, 'knots_per_round': gr.n_knots,
           'births': gr.births(), 'takes_per_round': [r['n_takes'] for r in gr.recs]}
    reads = {}
    for t in READ_ROUNDS:
        if t > gr.rounds_done:
            continue
        N = gr.n_knots[t]
        V = _View(S, N, gr.n_dist[t])
        V.parents = S.parents[:N]
        reads[t] = {'knots': N, 'steps': greatest_steps(V, N, range(S.n_start))}
    rec['reads'] = reads
    rec['lambda'] = lam_rec
    rec['tied'] = tied_rec
    rec['check_P'] = checkP
    rec['knot_test'] = knot_test(gr, key, lab, kl)
    rec['seconds'] = round(time.time() - t0, 2)
    return rec


def knot_test(gr, key, lab, kl):
    """KD 6.2 (run 4): every knot of the structure after round 25 (or the last round), and 100 knots made after round
    25 (class `later-knots`); not-all-equal: the birth method at each knot's birth (start knots directly); parity: both
    methods on the last structure."""
    S = gr.S
    t25 = min(25, gr.rounds_done)
    N25 = gr.n_knots[t25]
    later = list(range(N25, S.n_knots))
    smp = kwr.sample_sorted(kwr.rng_for(key, lab, kl, 'later-knots'), later, 100)
    test = list(range(N25)) + sorted(smp)
    out = {'tested': len(test), 'fails': [], 'untested': 0, 'disagree': 0}
    if kl == 'parity':
        from knots import parity_test
        pt = parity_test(S)
        out['disagree'] = len(pt['disagree'])
        for u in test:
            if not pt['pass'][u]:
                out['fails'].append({'knot': u, 'round': S.made[u], 'kind': S.kind[u], 'places': len(S.places[u]),
                                     'parents': list(S.parents[u])})
        return out
    from knots import jointly_free, nae_direct
    by_round = {}
    for u in test:
        by_round.setdefault(S.made[u], []).append(u)
    for t, us in sorted(by_round.items()):
        if t == 0:
            V0 = _View(S, gr.n_knots[0], gr.n_dist[0])
            res = nae_direct(V0, us)
        else:
            Vb = _View(S, gr.n_knots[t - 1], gr.n_dist[t - 1])
            nd = gr.n_dist[t - 1]
            res = {u: jointly_free(Vb, [d for d in S.places[u] if d < nd]) for u in us}
        for u, v in res.items():
            if v is None:
                out['untested'] += 1
            elif not v:
                out['fails'].append({'knot': u, 'round': S.made[u], 'kind': S.kind[u], 'places': len(S.places[u]),
                                     'parents': list(S.parents[u])})
    return out


def base_item(it):
    """The base law's greatest holder steps at the reading rounds (L6 for T1-T4 and T9, L3 for T5-T8 and T10)."""
    key, base, kl = it['start'], it['base'], it['knot_law']
    gr = kwr.Grown(key, kwr.make_law(base, knot_law=kl), 100, parts_every_round=False)
    S = gr.S
    reads = {}
    for t in READ_ROUNDS:
        if t > gr.rounds_done:
            continue
        N = gr.n_knots[t]
        V = _View(S, N, gr.n_dist[t])
        V.parents = S.parents[:N]
        g = greatest_steps(V, N, range(S.n_start))
        reads[t] = {'knots': N, 'hs': g['hs']}
    return {'start': key, 'base': base, 'knot_law': kl, 'rounds_done': gr.rounds_done, 'stop': gr.stop,
            'ended': gr.ended, 'reads': reads, 'kind': 'base'}


def _init():
    kwr.cap_memory(6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd')
    ap.add_argument('--procs', type=int, default=4)
    ap.add_argument('--limit', type=int, default=None)
    a = ap.parse_args()
    if a.cmd == 'base':
        its = [{'start': k, 'base': b, 'knot_law': kl} for k in starts4() for b in ('L6', 'L3')
               for kl in ('parity', 'nae')]
        fn, path = base_item, kwr.out_path('run4_base.jsonl.gz')
        done = {(r['start'], r['base'], r['knot_law']) for r in kwr.read_jsonl(path)}
        its = [x for x in its if (x['start'], x['base'], x['knot_law']) not in done]
    else:
        its = items()
        if a.limit:
            its = its[:a.limit]
        fn, path = run_item, kwr.out_path('run4.jsonl.gz')
        done = {r['item'] for r in kwr.read_jsonl(path)}
        its = [x for x in its if x['item'] not in done]
    kwr.log('run 4 (%s): %d items' % (a.cmd, len(its)))
    W = kwr.JsonlWriter(path)
    t0 = time.time()
    with mp.Pool(a.procs, initializer=_init, maxtasksperchild=100) as pool:
        for k, rec in enumerate(pool.imap_unordered(fn, its, chunksize=2)):
            W.write(rec)
            if (k + 1) % 200 == 0 or k + 1 == len(its):
                kwr.log('run 4 (%s): %d/%d, %.0fs' % (a.cmd, k + 1, len(its), time.time() - t0))
    W.close()


if __name__ == '__main__':
    main()
