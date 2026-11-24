"""T2: any grown stage (REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B, "T2").

Stages: (targets) every stage of at most 16 distinctions met in T1, under every law assignment met there; (draws) the first
two stages (stage 0, the start, and stage 1) of the 280 funded sparse draws of REVIEW-LEADS-20261123-001A (lib.p3_draws,
seed 2026112301), under both laws (every founder even parity, or every founder not-all-equal) and every assignment of
laws to the newborns, when the stage has at most 16 distinctions.
Observer choices: every Alice x1, x2, x3 and Bob y1, y2, y3 among the stage's distinctions with x2, x3 exactly tied (always
equal or always unequal over the stage's allowed words), y2, y3 likewise, and no knot holding distinctions of both
observers.  Each unordered choice is tested once: the order of x2, x3, the order of y2, y3 and the exchange of Alice and
Bob leave hiding and the score unchanged (checked here on drawn choices), so each tested choice stands for 8 ordered ones.
The supplied setting births are added through the table of old allowed words (the scorer's weighting), hidden or not.

Writes t2_<pop>_<choices>_<lo>-<hi>.json (counts, largest hidden score, symmetry check) and t2_hits_... .jsonl (every
hidden excess, at most 20 per stage written in full, all counted).
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --pop targets|draws
  [--choices 2|3] [--lo 0 --hi 100000]
"""
import argparse
import itertools
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402

LAWS3 = {2: ('even', 'nae'), 3: ('even', 'odd', 'nae')}


def allowed_words(stars, laws):
    """Bit matrix (N_allowed x D) of the allowed words of a structure, distinctions in sorted order."""
    names = sorted({d for s in stars for d in s})
    pos = {d: i for i, d in enumerate(names)}
    D = len(names)
    idx = np.arange(1 << D, dtype=np.int64)
    ok = np.ones(1 << D, dtype=bool)
    for s, law in zip(stars, laws):
        sm = sum(((idx >> pos[d]) & 1) for d in s)
        k = len(s)
        ok &= ((sm != 0) & (sm != k)) if law == 'nae' else (sm % 2 == (0 if law == 'even' else 1))
    w = idx[ok]
    B = ((w[:, None] >> np.arange(D)[None, :]) & 1).astype(np.int8)
    return names, B


# map from the 16 counts over (x1, x2, y1, y2) to the 64-entry table, for tie constants cx, cy (x3 = x2 ^ cx, y3 = y2 ^ cy)
MAP = {}
for cx in (0, 1):
    for cy in (0, 1):
        m = np.zeros(16, dtype=np.int64)
        for x1, x2, y1, y2 in itertools.product((0, 1), repeat=4):
            xa = x1 * 4 + x2 * 2 + (x2 ^ cx)
            xb = y1 * 4 + y2 * 2 + (y2 ^ cy)
            m[(x1 * 2 + x2) * 4 + y1 * 2 + y2] = xa * 8 + xb
        MAP[cx, cy] = m


class Cache:
    """Evaluation of normalized 64-entry tables, cached: (hidden, float score or None, exact or None)."""

    def __init__(self):
        self.d = {}
        self.ev = c.Evaluator()

    def run(self, T):
        """T: (n, 64) int64 counts (entries < 2^17).  Returns list of (hidden, fscore, exact)."""
        g = np.gcd.reduce(T, axis=1)
        g[g == 0] = 1
        T = T // g[:, None]
        keys = [r.tobytes() for r in T]
        new = {}
        for i, k in enumerate(keys):
            if k not in self.d and k not in new:
                new[k] = i
        if new:
            ids = list(new.values())
            evs = self.ev.run([T[i] for i in ids])
            for i, e in zip(ids, evs):
                self.d[keys[i]] = (e[0] and e[1], e[2], e[3])
        return [self.d[k] for k in keys], T


def stage_choices(stars, laws):
    """All unordered observer choices of a stage and their tables.  Returns (names, list of choices (x1,x2,x3,y1,y2,y3) as
    distinction names, array (n, 64) of counts, number of tied pairs)."""
    names, B = allowed_words(stars, laws)
    D = len(names)
    N = B.shape[0]
    if N == 0:
        return names, [], np.zeros((0, 64), dtype=np.int64), 0
    Bf = B.astype(np.float64)
    eq = Bf.T @ Bf + (1 - Bf).T @ (1 - Bf)            # number of allowed words with x_i == x_j
    ties = [(i, j, 0 if eq[i, j] == N else 1) for i in range(D) for j in range(i + 1, D) if eq[i, j] in (0, N)]
    pos = {d: i for i, d in enumerate(names)}
    kmask = [0] * D
    for k, s in enumerate(stars):
        for d in s:
            kmask[pos[d]] |= 1 << k
    opts = []
    for (i, j, cx) in ties:
        for x1 in range(D):
            if x1 in (i, j):
                continue
            opts.append((x1, i, j, cx, kmask[x1] | kmask[i] | kmask[j]))
    chosen, tabs = [], []
    for p in range(len(opts)):
        x1, x2, x3, cx, ma = opts[p]
        qs = [q for q in range(p + 1, len(opts)) if not (opts[q][4] & ma)]
        if not qs:
            continue
        ia = 2 * B[:, x1].astype(np.int64) + B[:, x2]
        IB = np.stack([2 * B[:, opts[q][0]].astype(np.int64) + B[:, opts[q][1]] for q in qs], axis=1)
        idx = 4 * ia[:, None] + IB + 16 * np.arange(len(qs))[None, :]
        cnt = np.bincount(idx.ravel(), minlength=16 * len(qs)).reshape(len(qs), 16)
        T = np.zeros((len(qs), 64), dtype=np.int64)
        for r, q in enumerate(qs):
            y1, y2, y3, cy, _ = opts[q]
            T[r, MAP[cx, cy]] = cnt[r]
            chosen.append((names[x1], names[x2], names[x3], names[y1], names[y2], names[y3]))
        tabs.append(T)
    T = np.concatenate(tabs) if tabs else np.zeros((0, 64), dtype=np.int64)
    # diagnostic: pairs of tied pairs on four different distinctions, and those with no knot holding both pairs
    disjoint = [(p, q) for p in range(len(ties)) for q in range(p + 1, len(ties))
                if not ({ties[p][0], ties[p][1]} & {ties[q][0], ties[q][1]})]
    apart = [(p, q) for p, q in disjoint
             if not ((kmask[ties[p][0]] | kmask[ties[p][1]]) & (kmask[ties[q][0]] | kmask[ties[q][1]]))]
    STAGE_DIAG.update(disjoint=len(disjoint), apart=len(apart))
    return names, chosen, T, len(ties)


STAGE_DIAG = {}


def orientations(T):
    """The 8 ordered versions of an unordered choice: swap x2/x3, swap y2/y3, exchange Alice and Bob."""
    M = T.reshape(8, 8)
    sw = np.array([((x >> 2) & 1) * 4 + (x & 1) * 2 + ((x >> 1) & 1) for x in range(8)])
    out = []
    for a in (np.arange(8), sw):
        for b in (np.arange(8), sw):
            X = M[np.ix_(a, b)]
            out.append(X.reshape(64))
            out.append(X.T.reshape(64))
    return np.array(out)


def target_stages(choices, lo, hi):
    """Yield (key, stars, laws) for every stage of at most 16 distinctions met in T1 (same growth, same assignments)."""
    tk = {t['tid']: t['knots'] for t in c.load_targets()}
    starts = [json.loads(l) for l in (c.ART / 'starts.jsonl').open()]
    ch = LAWS3[choices]
    for si in range(lo, min(hi, len(starts))):
        s = starts[si]
        stars, laws, names, obs, sub = c.start_stars(tk[s['tid']], s['mask'])
        h = c.grow(stars, 'nae')
        nf = h['n_at'][0]
        A, mode = c.assignments(h['n_at'][-1] - nf, (s['tid'], s['mask']), k=choices)
        for t, n in enumerate(h['n_at']):
            if h['D_at'][t] > c.T2_DMAX:
                continue
            nb = n - nf
            R = np.unique(A[:, :nb], axis=0) if nb else np.zeros((1, 0), dtype=np.int8)
            for r in R:
                L = list(laws) + [ch[int(v)] for v in r]
                nm = [tuple(names[d] if d < len(names) else f'f{d}' for d in st) for st in h['stars'][:n]]
                yield dict(si=si, tid=s['tid'], mask=s['mask'], t=t, laws=[ch[int(v)] for v in r]), nm, L


def funded_draws():
    sys.path.insert(0, str(c.RL_A))
    import lib as rl  # REVIEW-LEADS-20261123-001A lib.py: p3_draws (seed 2026112301)
    sys.path.pop(0)
    out = []
    for dr in rl.p3_draws():
        stars = dr['stars']
        try:
            end = c.from_stars_ext(stars)
        except ValueError:
            continue
        f = {}
        for law in ('parity', 'nae'):
            f[law] = c.EO.step(end, law).status == 'extend'
        out.append((dr, f))
    return out


def draw_stages(choices, lo, hi, stats):
    """Yield (key, stars, laws) for stages 0 and 1 of the funded draws under both laws, at most 16 distinctions."""
    ch = LAWS3[choices]
    draws = funded_draws()
    stats['draws'] = len(draws)
    stats['funded'] = {law: sum(1 for _, f in draws if f[law]) for law in ('parity', 'nae')}
    for i, (dr, f) in enumerate(draws):
        if not (lo <= i < hi):
            continue
        for flaw in ('parity', 'nae'):
            if not f[flaw]:
                continue
            stars = [tuple(s) for s in dr['stars']]
            founders = ['even' if flaw == 'parity' else 'nae'] * len(stars)
            key = dict(arm=dr['arm'], draw=dr['draw'], founders=flaw)
            D0 = len({d for s in stars for d in s})
            if D0 <= c.T2_DMAX:
                yield dict(key, t=0, laws=[]), stars, founders
            # stage 1: the not-all-equal structure rule (no closing) whenever some knot is not-all-equal
            hn = c.grow(stars, 'nae', rounds=1, dmax=10 ** 9)
            nb = hn['n_at'][-1] - len(stars)
            if flaw == 'nae':
                variants = [(hn, None)]
            else:
                hp = c.grow(stars, 'parity', rounds=1, dmax=10 ** 9)
                if hp['closing']:
                    variants = [(hn, 'some_nae'), (hp, 'all_parity')]
                else:
                    # the two rules differ only at a closing birth (checked: same births)
                    stats['parity_rule_same_as_nae'] = stats.get('parity_rule_same_as_nae', 0) + (hp['stars'] == hn['stars'])
                    stats['parity_rule_compared'] = stats.get('parity_rule_compared', 0) + 1
                    variants = [(hn, None)]
            for h, which in variants:
                n = h['n_at'][-1]
                if h['D_at'][-1] > c.T2_DMAX or n == len(stars):
                    continue
                nb = n - len(stars)
                for r in itertools.product(range(len(ch)), repeat=nb):
                    lawsr = [ch[v] for v in r]
                    if which == 'some_nae' and 'nae' not in lawsr:
                        continue           # all parity: the closing structure applies
                    if which == 'all_parity':
                        if lawsr != ['even']:
                            continue       # one closing stage: the sole birth is parity with its implied sign
                        stars1 = h['stars'][:n]
                        nm, Bw = allowed_words(stars, founders)
                        pos = {d: i for i, d in enumerate(nm)}
                        par = Bw[:, [pos[d] for d in stars1[-1]]].sum(1) % 2
                        stats['closing_implied_constant'] = stats.get('closing_implied_constant', 0) + int(par.min() == par.max())
                        imp = 'even' if int(par[0]) == 0 else 'odd'
                        yield dict(key, t=1, laws=[f'{imp}(implied closing)'], closing=True), stars1, founders + [imp]
                        continue
                    yield dict(key, t=1, laws=lawsr), h['stars'][:n], founders + lawsr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pop', required=True, choices=('targets', 'draws'))
    ap.add_argument('--choices', type=int, default=2, choices=(2, 3))
    ap.add_argument('--lo', type=int, default=0)
    ap.add_argument('--hi', type=int, default=10 ** 9)
    ap.add_argument('--symcheck', type=int, default=300, help='tables per run checked under the 8 orientations')
    args = ap.parse_args()
    t0 = time.time()
    cache = Cache()
    stats = dict(pop=args.pop, choices=args.choices, lo=args.lo, hi=args.hi, stages=0, distinct_structures=0,
                 stages_with_no_word=0, stages_without_tie=0, choices_tested=0, choices_ordered=0, hidden=0, excess=0,
                 best_hidden=None, best_hidden_exact=None, best_hidden_where=None, by_t=Counter(),
                 sym_checked=0, sym_equal=0, closing_stages=0)
    hits = []
    seen = {}
    rng = np.random.default_rng(2026112342)
    gen = target_stages(args.choices, args.lo, args.hi) if args.pop == 'targets' else draw_stages(args.choices, args.lo, args.hi, stats)
    for key, stars, laws in gen:
        stats['stages'] += 1
        stats['by_t'][key['t']] += 1
        if key.get('closing'):
            stats['closing_stages'] += 1
        skey = tuple(sorted((l, tuple(sorted(s))) for s, l in zip(stars, laws)))
        if skey in seen:
            r = seen[skey]
        else:
            names, chosen, T, nties = stage_choices(stars, laws)
            if len(T):
                evs, Tn = cache.run(T)
            else:
                evs, Tn = [], T
            hid = [e[0] for e in evs]
            exc = [e[0] and e[2] is not None and e[2] > 2 for e in evs]
            bf = max([e[1] for e in evs if e[0] and e[1] is not None], default=None)
            bx = max([e[2] for e in evs if e[0] and e[2] is not None], default=None)
            r = dict(n=len(chosen), hidden=sum(hid), excess=sum(exc), best=bf, bestx=bx, nties=nties,
                     ex=[(chosen[i], Tn[i].tolist(), str(evs[i][2])) for i in range(len(chosen)) if exc[i]][:20])
            r['diag'] = (nties > 0, STAGE_DIAG.get('disjoint', 0) > 0, STAGE_DIAG.get('apart', 0) > 0)
            STAGE_DIAG.clear()
            seen[skey] = r
            stats['distinct_structures'] += 1
            # symmetry check on drawn choices
            if len(T) and stats['sym_checked'] < args.symcheck:
                for i in rng.choice(len(T), size=min(3, len(T)), replace=False):
                    O = orientations(Tn[i])
                    eo, _ = cache.run(O)
                    stats['sym_checked'] += 1
                    same = all(e[0] == eo[0][0] for e in eo) and (not eo[0][0] or
                                                                  max(e[1] for e in eo) - min(e[1] for e in eo) < 1e-12)
                    stats['sym_equal'] += bool(same)
        stats['choices_tested'] += r['n']
        stats['choices_ordered'] += 8 * r['n']
        stats['hidden'] += r['hidden']
        stats['excess'] += r['excess']
        if r['nties'] == 0:
            stats['stages_without_tie'] += 1
        dg = r.get('diag', (False, False, False))
        stats['stages_with_a_tie'] = stats.get('stages_with_a_tie', 0) + dg[0]
        stats['stages_with_two_disjoint_ties'] = stats.get('stages_with_two_disjoint_ties', 0) + dg[1]
        stats['stages_with_two_ties_no_common_knot'] = stats.get('stages_with_two_ties_no_common_knot', 0) + dg[2]
        if r['best'] is not None and (stats['best_hidden'] is None or r['best'] > stats['best_hidden']):
            stats['best_hidden'] = r['best']
            stats['best_hidden_where'] = key
            stats['best_hidden_exact'] = None if r['bestx'] is None else str(r['bestx'])
        if r['excess']:
            hits.append(dict(key=key, knots=[c.fmt_knot(l, tuple(map(str, s))) for s, l in zip(stars, laws)],
                             distinctions=len({d for s in stars for d in s}), knots_n=len(stars), excess=r['excess'],
                             examples=r['ex']))
    stats['by_t'] = dict(stats['by_t'])
    stats['seconds'] = round(time.time() - t0, 1)
    stats['exact_calls'] = cache.ev.exact_calls
    tag = f"{args.pop}_c{args.choices}_{args.lo}-{min(args.hi, 10 ** 6)}"
    (c.ART / f't2_{tag}.json').write_text(json.dumps(stats, indent=1, default=str))
    c.dump(c.ART / f't2_hits_{tag}.jsonl', hits)
    print(json.dumps({k: v for k, v in stats.items() if k not in ('best_hidden_where',)}, default=str))


if __name__ == '__main__':
    main()
