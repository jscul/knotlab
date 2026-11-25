"""Run 5: the growing end (KD 5) under not-all-equal, L0, L1, L3, L6, L7 on every census start, rounds 1 to 3 (1 to 4
on three- and four-knot starts), within the stage cap; integer arithmetic; strata, nested counts, headline levels, S with
the member shuffle and the pair shuffle, L-W, betweenness; the history weighting on stages of at most 20 distinctions;
checks N and I there; the knot test on every knot of every stage computed, once at its birth.
Swaps on three- and four-knot starts: the delay horizon of 10 rounds, the stage cap 40 members and 60 shared.
usage: python -B run5.py run --procs 4 [--limit N] [--laws L0,L1]      writes run5_<law>.jsonl.gz"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import time
from fractions import Fraction

import numpy as np

import ge
import kwr

LAWS5 = ('L0', 'L1', 'L3', 'L6', 'L7')
HORIZON = 6
CAP = (30, 50)
CAP_SWAP = (40, 60)
STAGE_SECONDS = 60.0


def items(laws=LAWS5):
    """Every census start: the 219 three- and four-knot starts in file order, then the 3,157 five-knot starts in the
    registered order of five_knot_order.json (so that a prefix cut for time is a uniform sample of them, R 28); the
    laws L0, L1, L3, L6, L7 within each start."""
    out = []
    C = kwr.census()
    order = kwr.small_census() + kwr.five_order()['order']
    for i in order:
        x = C[i]
        for lab in laws:
            out.append({'start': 'census:%d' % i, 'index': i, 'n': x['n'], 'law': lab})
    for k, it in enumerate(out):
        it['item'] = k
    return out


def member_sets(S, N, members):
    """Dm(x): bitmask of the members m (of the stage) that are x or an ancestor of x, for every knot x of S."""
    bit = {m: 1 << i for i, m in enumerate(members)}
    Dm = [0] * S.n_knots
    for x in range(S.n_knots):
        v = bit.get(x, 0) if x < N else 0
        for p in S.parents[x]:
            v |= Dm[p]
            if p < N and p in bit:
                v |= bit[p]
        Dm[x] = v
    return bit, Dm


def delays(gr, t, members, horizon):
    """KD 5.5: for each pair of members of the stage after round t, delta (1..horizon), 'never' (growth ended before
    the descendants meet) or 'undecided'; ancestor pairs marked."""
    S = gr.S
    N = gr.n_knots[t]
    bit, Dm = member_sets(S, N, members)
    first = {}
    last_round = gr.rounds_done
    for x in range(N, S.n_knots):
        r = S.made[x]
        if r > t + horizon:
            break
        m = Dm[x]
        if m & (m - 1) == 0:
            continue
        idx = [i for i in range(len(members)) if (m >> i) & 1]
        for a in range(len(idx)):
            for b in range(a + 1, len(idx)):
                key = (idx[a], idx[b])
                if key not in first:
                    first[key] = r - t
    ended_within = gr.ended is not None and last_round <= t + horizon
    out = {}
    anc = {}
    for a in range(len(members)):
        for b in range(a + 1, len(members)):
            u, v = members[a], members[b]
            if (Dm[v] >> a) & 1 or (Dm[u] >> b) & 1:
                anc[(u, v)] = True
            d = first.get((a, b))
            if d is not None:
                out[(u, v)] = d
            elif ended_within:
                out[(u, v)] = 'never'
            else:
                out[(u, v)] = 'undecided'
    return out, anc


def stage(gr, t, it, horizon, cap, shuffle_rng, hist_ok=True):
    """All readings of the stage after round t."""
    S = gr.S
    N, nd = gr.n_knots[t], gr.n_dist[t]
    members = gr.members[t]
    nshared = sum(1 for d in range(nd) if len([w for w in S.holders[d] if w < N]) >= 2)
    rec = {'round': t, 'knots': N, 'distinctions': nd, 'members': len(members), 'shared': nshared}
    if len(members) > cap[0] or nshared > cap[1]:
        rec['status'] = 'not run (stage cap)'
        return rec
    c0 = time.process_time()
    ms = kwr.met_sets(S, members, N)
    parts = kwr.parts_of(S, members, N, ms)
    part_of = {u: i for i, P in enumerate(parts) for u in P}
    past = kwr.past_its_start(S, members, N)
    W, widx = kwr.ws_from(S, members, members, N, ms)
    G = kwr.Graphs(S, N)
    Dh = G.hs(members)
    dl, anc = delays(gr, t, members, horizon)
    try:
        sc = ge.StageCount(S, N, nd)
        Z = sc.Z()
    except ge.WidthExceeded as e:
        rec['status'] = 'not finished (elimination width %s)' % e.args[0]
        return rec
    rec.update({'Z': str(Z), 'parts': [list(P) for P in parts], 'past_its_start': past})
    pairs = []
    for a in range(len(members)):
        for b in range(a + 1, len(members)):
            u, v = members[a], members[b]
            same = part_of[u] == part_of[v]
            d = dl[(u, v)]
            if anc.get((u, v)):
                stratum = 'v'
            elif not same and past:
                stratum = 'ii'
            elif not same:
                stratum = 'vi'           # different parts while the roster is not past its start (R 21)
            elif d == 'never':
                stratum = 'iii'
            elif d == 'undecided':
                stratum = 'iv'
            else:
                stratum = 'i'
            p = {'u': u, 'v': v, 'part': part_of[u] if same else None, 'delta': d, 'stratum': stratum,
                 'hs': int(Dh[u][v]) if np.isfinite(Dh[u][v]) else None,
                 'ws': int(W[u][widx[v]]) if np.isfinite(W[u][widx[v]]) else None,
                 'lam': [sc.lam[u], sc.lam[v]], 'sig': [len(sc.shared[u]), len(sc.shared[v])]}
            if same:
                gZ, Nn = sc.pair(u, v)
                p['gZ'] = str(gZ)
                p['N'] = str(Nn)
            pairs.append(p)
            if time.process_time() - c0 > STAGE_SECONDS:
                rec['status'] = 'not finished (over %d s)' % STAGE_SECONDS
                return rec
    rec['pairs'] = pairs
    rec['strata'] = {s: sum(1 for p in pairs if p['stratum'] == s) for s in ('i', 'ii', 'iii', 'iv', 'v', 'vi')}
    rec['orders'] = orders(pairs, Z, sc)
    rec['LW'] = lw(pairs, Z)
    rec['betweenness'] = betweenness(pairs, members, part_of)
    rec['shuffle'] = shuffles(pairs, Z, sc, parts, shuffle_rng)
    if nd <= 20 and hist_ok:
        rec['small'] = small_checks(gr, t, pairs, sc, Z)
    rec['status'] = 'computed'
    rec['seconds'] = round(time.process_time() - c0, 3)
    return rec


def _x_values(pairs, Z, sc, which):
    """Exact strength values (larger = more strongly related): |kappa|, |gamma| or -rho."""
    out = []
    for p in pairs:
        gZ, Nn = int(p['gZ']), int(p['N'])
        if which == 'kappa':
            Du, Dv = 2 ** p['lam'][0] - 1, 2 ** p['lam'][1] - 1
            out.append(Fraction(abs(gZ), Z * Du * Dv))
        elif which == 'gamma':
            out.append(Fraction(abs(gZ), Z))
        else:
            out.append(-Fraction(Nn, Z))
    return out


def _y_values(pairs, key):
    return [-(p['delta'] if key == 'delta' else p[key]) for p in pairs]


def orders(pairs, Z, sc):
    """Concordant, discordant, tied comparisons in stratum (i) for X in |kappa|, |gamma|, rho and Y in delta, ws,
    hs, with the three nested counts; S = concordant - discordant; the sign of kappa at each ws."""
    P = [p for p in pairs if p['stratum'] == 'i']
    out = {'n': len(P)}
    if len(P) < 2:
        return out
    lamset = [tuple(sorted(p['lam'])) for p in P]
    sigset = [tuple(sorted(p['sig'])) for p in P]
    L = np.array([[a == b for b in lamset] for a in lamset])
    Sg = np.array([[a == b for b in sigset] for a in sigset])
    masks = {'i-1': None, 'i-2': L, 'i-3': L & Sg}
    for xw in ('kappa', 'gamma', 'rho'):
        X = ge.dense_rank(_x_values(P, Z, sc, xw))
        for yk in ('delta', 'ws', 'hs'):
            Y = _y_values(P, yk)
            for lvl, m in masks.items():
                c, d, ti = ge.order_counts(X, Y, m)
                out['%s|%s|%s' % (xw, yk, lvl)] = [c, d, ti]
    signs = {}
    for p in P:
        k = int(p['gZ'])
        s = '+' if k > 0 else ('-' if k < 0 else '0')
        signs.setdefault(str(p['ws']), {}).setdefault(s, 0)
        signs[str(p['ws'])][s] += 1
    out['kappa_sign_by_ws'] = signs
    return out


def lw(pairs, Z):
    """KD 5.10: |gamma| strictly larger whenever ws strictly smaller, over pairs of stratum (i)."""
    P = [p for p in pairs if p['stratum'] == 'i']
    if len(P) < 2:
        return {'tests': False}
    g = [abs(int(p['gZ'])) for p in P]
    w = [p['ws'] for p in P]
    tests = False
    fails = strict = 0
    for i in range(len(P)):
        for j in range(len(P)):
            if w[i] < w[j]:
                tests = True
                if g[i] <= g[j]:
                    fails += 1
                    if g[i] < g[j]:
                        strict += 1
    return {'tests': tests, 'failing_comparisons': fails, 'strict_reversals': strict, 'holds': tests and fails == 0}


def betweenness(pairs, members, part_of):
    """KD 5.11: u, v, w of one part with ws(u,v) + ws(v,w) = ws(u,w): |gamma(u,w)| <= min(|gamma(u,v)|, |gamma(v,w)|);
    each unordered {u, w} with each v between once."""
    g, w = {}, {}
    for p in pairs:
        if p.get('gZ') is None or p['ws'] is None:
            continue
        g[(p['u'], p['v'])] = g[(p['v'], p['u'])] = abs(int(p['gZ']))
        w[(p['u'], p['v'])] = w[(p['v'], p['u'])] = p['ws']
    tested = failing = 0
    examples = []
    by_part = {}
    for u in members:
        by_part.setdefault(part_of[u], []).append(u)
    for P in by_part.values():
        for i in range(len(P)):
            for k in range(i + 1, len(P)):
                u, x = P[i], P[k]
                if (u, x) not in w:
                    continue
                for v in P:
                    if v in (u, x) or (u, v) not in w or (v, x) not in w:
                        continue
                    if w[(u, v)] + w[(v, x)] == w[(u, x)]:
                        tested += 1
                        if g[(u, x)] > min(g[(u, v)], g[(v, x)]):
                            failing += 1
                            if len(examples) < 3:
                                examples.append([u, v, x])
    return {'tested': tested, 'failing': failing, 'examples': examples}


def shuffles(pairs, Z, sc, parts, rng):
    """The member shuffle (KD 5.7) for |kappa| and |gamma| against delta, and the pair shuffle's variance."""
    within = [p for p in pairs if p.get('gZ') is not None]
    out = {}
    if len(within) < 2:
        return out
    yk = {(p['u'], p['v']): (-p['delta'] if p['stratum'] == 'i' else None) for p in within}
    for xw in ('kappa', 'gamma'):
        X = ge.dense_rank(_x_values(within, Z, sc, xw))
        Svals, exact = ge.shuffle_S([(p['u'], p['v']) for p in within], X, yk, parts, rng)
        P = [i for i, p in enumerate(within) if p['stratum'] == 'i']
        c, d, _ = ge.order_counts([X[i] for i in P], [yk[(within[i]['u'], within[i]['v'])] for i in P])
        Sobs = c - d
        var_pair = ge.kendall_var_pair_shuffle([X[i] for i in P], [yk[(within[i]['u'], within[i]['v'])] for i in P])
        out[xw] = {'S': Sobs, 'perms': int(len(Svals)), 'exact': exact, 'mean': float(np.mean(Svals)),
                   'var': float(np.var(Svals)), 'p_ge': float(np.mean(Svals >= Sobs)),
                   'p_le': float(np.mean(Svals <= Sobs)), 'pair_shuffle_var': str(var_pair)}
    return out


def small_checks(gr, t, pairs, sc, Z):
    """On a stage of at most 20 distinctions: check I (Z, gamma Z, N against enumeration), check N (Lemma N for every
    loose distinction of each member pair, every pair of members), and the history weighting's rho."""
    S = gr.S
    N, nd = gr.n_knots[t], gr.n_dist[t]
    A = ge.enumerate_states(S, N, nd)
    out = {'Z_ok': len(A) == Z, 'I_bad': 0, 'N_bad': 0, 'pairs': 0}
    alloweds = [ge.enumerate_states(S, gr.n_knots[r], gr.n_dist[r]) for r in range(t + 1)]
    num, den = ge.history_weights(alloweds, gr.n_dist[:t + 1])
    hist = {}
    for p in pairs:
        u, v = p['u'], p['v']
        lu, lv = ge.loose_of(S, u, N), ge.loose_of(S, v, N)
        if not lu or not lv or not sc.shared[u] or not sc.shared[v]:
            continue
        Ze, gZe, Ne = ge.enum_pair(S, A, u, v, lu[0], lv[0], N)
        out['pairs'] += 1
        if p.get('gZ') is not None and (int(p['gZ']), int(p['N'])) != (gZe, Ne):
            out['I_bad'] += 1
        want = Fraction(gZe, len(A) * (2 ** len(lu) - 1) * (2 ** len(lv) - 1))
        for a in lu:
            for b in lv:
                _, _, ne = ge.enum_pair(S, A, u, v, a, b, N)
                if 1 - 2 * Fraction(ne, len(A)) != want:
                    out['N_bad'] += 1
        a, b = lu[0], lv[0]
        diff = (((A >> a) ^ (A >> b)) & 1).astype(bool)
        rho_h = Fraction(int(sum(num[diff])) if diff.any() else 0, den)
        hist[(u, v)] = rho_h
    # the order test under the history weighting, stratum (i), against delta, nested counts
    P = [p for p in pairs if p['stratum'] == 'i' and (p['u'], p['v']) in hist]
    if len(P) >= 2:
        X = ge.dense_rank([abs(1 - 2 * hist[(p['u'], p['v'])]) for p in P])
        Y = _y_values(P, 'delta')
        lamset = [tuple(sorted(p['lam'])) for p in P]
        sigset = [tuple(sorted(p['sig'])) for p in P]
        L = np.array([[a == b for b in lamset] for a in lamset])
        Sg = np.array([[a == b for b in sigset] for a in sigset])
        out['history_orders'] = {lvl: list(ge.order_counts(X, Y, m)) for lvl, m in
                                 (('i-1', None), ('i-2', L), ('i-3', L & Sg))}
    out['history_rho'] = {'%d,%d' % k: str(v) for k, v in hist.items()}
    return out


def knot_tests(gr, upto):
    """KD 6.1, 6.2 (run 5): every knot made by round `upto`, once at its birth by the birth method (start knots
    directly at round 0); the direct test on every knot of at most 12 places on the structure after round `upto`."""
    S = gr.S
    out = {'tested': 0, 'fails': [], 'untested': 0, 'direct_compared': 0, 'disagree': 0}
    Nup = gr.n_knots[upto]
    verdict = {}
    S0 = _View(S, gr.n_knots[0], gr.n_dist[0])
    v0 = kwr.knots.nae_direct(S0, list(range(gr.n_knots[0])))
    verdict.update(v0)
    for t in range(1, upto + 1):
        Sb = _View(S, gr.n_knots[t - 1], gr.n_dist[t - 1])
        nd = gr.n_dist[t - 1]
        for x in range(gr.n_knots[t - 1], gr.n_knots[t]):
            I = [d for d in S.places[x] if d < nd]
            verdict[x] = kwr.knots.jointly_free(Sb, I)
    St = _View(S, Nup, gr.n_dist[upto])
    small = [u for u in range(Nup) if len(S.places[u]) <= 12]
    direct = kwr.knots.nae_direct(St, small)
    for u in range(Nup):
        v = verdict.get(u)
        if v is None:
            out['untested'] += 1
            continue
        out['tested'] += 1
        if not v:
            out['fails'].append({'knot': u, 'round': S.made[u], 'kind': S.kind[u], 'parents': list(S.parents[u])})
        if u in direct:
            out['direct_compared'] += 1
            if direct[u] != v:
                out['disagree'] += 1
    return out


class _View:
    """The structure after an earlier round, as a prefix of knots and distinctions of S (places are fixed at birth;
    holders beyond the prefix are filtered)."""

    def __init__(self, S, N, nd):
        self.places = S.places[:N]
        self.holders = [[w for w in hs if w < N] for hs in S.holders[:nd]]
        self.removed = set()
        self.n_knots = N
        self.n_distinctions = nd


def run_item(it, horizon=HORIZON, cap=CAP, label='primary'):
    t0 = time.time()
    small = it['n'] in (3, 4)
    tmax = 4 if small else 3
    law = kwr.make_law(it['law'])
    gr = kwr.Grown(it['start'], law, tmax + horizon)
    rng = kwr.rng_for(it['start'], it['law'], 'nae', 'shuffle')
    rec = {'item': it['item'], 'start': it['start'], 'index': it['index'], 'n': it['n'], 'law': it['law'],
           'label': label, 'horizon': horizon, 'cap': list(cap), 'rounds_done': gr.rounds_done, 'stop': gr.stop,
           'ended': gr.ended, 'births': gr.births()[:tmax + horizon], 'stages': []}
    last_birth = max([r['round'] for r in gr.recs if r['births'] > 0], default=0)
    computed = 0
    for t in range(1, tmax + 1):
        if t > gr.rounds_done or t > last_birth:
            break
        st = stage(gr, t, it, horizon, cap, rng)
        rec['stages'].append(st)
        if st['status'] == 'computed':
            computed = t
    if computed and label == 'primary':
        rec['knot_test'] = knot_tests(gr, computed)
    rec['seconds'] = round(time.time() - t0, 2)
    return rec


def run_swap(it):
    """The swaps on three- and four-knot starts: horizon 10 rounds; stage cap 40 members and 60 shared."""
    a = run_item(it, horizon=10, cap=CAP, label='swap horizon 10')
    b = run_item(it, horizon=HORIZON, cap=CAP_SWAP, label='swap cap 40/60')
    # the cap swap only adds stages over the primary cap; keep those
    b['stages'] = [s for s in b['stages'] if s['members'] > CAP[0] or s['shared'] > CAP[1]]
    return [a, b]


def _init():
    kwr.cap_memory(6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd')
    ap.add_argument('--procs', type=int, default=4)
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--laws', default=','.join(LAWS5))
    ap.add_argument('--first', type=int, default=None, help='only the first N starts (in file order)')
    a = ap.parse_args()
    laws = a.laws.split(',')
    its = items(laws)
    if a.first:
        seen = []
        for it in its:
            if it['index'] not in seen:
                seen.append(it['index'])
        keep = set(seen[:a.first])
        its = [it for it in its if it['index'] in keep]
    if a.limit:
        its = its[:a.limit]
    if a.cmd == 'swap':
        its = [it for it in its if it['n'] in (3, 4)]
        fn, name = run_swap, 'run5_swaps.jsonl.gz'
    else:
        fn, name = run_item, None
    writers = {}
    done = set()
    for lab in laws:
        p = kwr.out_path(name or 'run5_%s.jsonl.gz' % lab)
        for r in kwr.read_jsonl(p):
            done.add((r['item'], r.get('label')))
    its = [it for it in its if (it['item'], 'primary') not in done] if a.cmd != 'swap' else \
        [it for it in its if (it['item'], 'swap horizon 10') not in done]
    kwr.log('run 5 (%s): %d items to run' % (a.cmd, len(its)))
    t0 = time.time()
    with mp.Pool(a.procs, initializer=_init, maxtasksperchild=200) as pool:
        for k, res in enumerate(pool.imap_unordered(fn, its, chunksize=4)):
            recs = res if isinstance(res, list) else [res]
            for rec in recs:
                p = kwr.out_path(name or 'run5_%s.jsonl.gz' % rec['law'])
                if p not in writers:
                    writers[p] = kwr.JsonlWriter(p)
                writers[p].write(rec)
            if (k + 1) % 200 == 0 or k + 1 == len(its):
                kwr.log('run 5: %d/%d items, %.0fs' % (k + 1, len(its), time.time() - t0))
    for w in writers.values():
        w.close()


if __name__ == '__main__':
    main()
