"""Checks of the knot tests against brute force before any registered run (TD 7: "each checked against brute force on
small structures before use").  Writes knot_checks.json.

1. Drawn small structures (seed 2026112501): 2 to 8 knots of 2 to 6 places over at most 16 distinctions, any number
   of holders.  For drawn sets I: joint freedom by peeling + pieces against every assignment; the rank difference
   after peeling against the rank difference of the whole matrix; and per knot the brute verdict against the peeled
   ranks, the kernel and the direct SAT test (both knot laws).
2. Grown structures: every named start of at most 9 distinctions and drawn small starts, grown 1 to 4 rounds under
   every base law, the control and ten taking rules (OLDEST and BY-COUNT), both knot laws, while the structure has at
   most 16 distinctions; test_run (the methods used in the runs) against brute force at the last round and at every round.
"""
from __future__ import annotations

import itertools
import random
import sys
import time

import tf_common as C
import tf_engine as E
import tf_knots as K


def brute_free(places_list, I):
    dists = sorted({d for P in places_list for d in P} | set(I))
    idx = {d: i for i, d in enumerate(dists)}
    rows = []
    for P in places_list:
        r = 0
        for d in P:
            r |= 1 << idx[d]
        rows.append(r)
    seen = set()
    imask = 0
    for d in I:
        imask |= 1 << idx[d]
    for a in range(1 << len(dists)):
        ok = True
        for r in rows:
            x = a & r
            if x == 0 or x == r:
                ok = False
                break
        if ok:
            seen.add(a & imask)
    want = 0
    sub = imask
    # count subsets of imask
    n = bin(imask).count('1')
    return len(seen) == (1 << n)


def draw_structure(rng):
    nk = rng.randint(2, 8)
    nd = rng.randint(4, 16)
    places = []
    for _ in range(nk):
        m = rng.randint(2, min(6, nd))
        places.append(sorted(rng.sample(range(nd), m)))
    used = sorted({d for P in places for d in P})
    ren = {d: i for i, d in enumerate(used)}
    places = [[ren[d] for d in P] for P in places]
    holders = [[] for _ in used]
    for u, P in enumerate(places):
        for d in P:
            holders[d].append(u)
    return places, holders


def check_drawn(n=1500, seed=2026112501):
    rng = random.Random(seed)
    res = {'structures': 0, 'free_checks': 0, 'free_bad': 0, 'rank_checks': 0, 'rank_bad': 0, 'knots': 0,
           'knot_bad': {'parity_ranks': 0, 'parity_kernel': 0, 'nae_direct': 0}, 'failing_knots': {'parity': 0,
                                                                                                 'nae': 0}}
    for _ in range(n):
        places, holders = draw_structure(rng)
        nk = len(places)
        res['structures'] += 1
        pl = K.Peel(places, holders, range(nk))
        nd = len(holders)
        for _ in range(4):
            I = sorted(rng.sample(range(nd), rng.randint(1, min(5, nd))))
            core = pl.core(I)
            v = K.pieces_free(places, holders, core, I)
            b = brute_free(places, I)
            res['free_checks'] += 1
            if v != b:
                res['free_bad'] += 1
            rd = K.rank_difference(places, sorted(core), I)
            rd0 = K.rank_difference(places, list(range(nk)), I)
            res['rank_checks'] += 1
            if rd != rd0:
                res['rank_bad'] += 1
        bp = K.brute(places, 'parity')
        bn = K.brute(places, 'nae')
        if bp != K.brute_slow(places, 'parity') or bn != K.brute_slow(places, 'nae'):
            res['brute_vs_slow_bad'] = res.get('brute_vs_slow_bad', 0) + 1
        ke = K._kernel_full(places, list(range(nk)))
        sv = K.NaeDirect(places)
        for u in range(nk):
            res['knots'] += 1
            core = pl.core(places[u], keep=(u,))
            r = K.rank_difference(places, sorted(core), places[u]) == 1
            if r != bp[u]:
                res['knot_bad']['parity_ranks'] += 1
            if (ke[u] == len(places[u]) - 1) != bp[u]:
                res['knot_bad']['parity_kernel'] += 1
            if sv.passes(places[u]) != bn[u]:
                res['knot_bad']['nae_direct'] += 1
            res['failing_knots']['parity'] += int(not bp[u])
            res['failing_knots']['nae'] += int(not bn[u])
        sv.close()
    return res


def small_starts(rng, n):
    out = []
    for i in range(n):
        nk = rng.randint(1, 3)
        nd = rng.randint(3, 8)
        stars = []
        for _ in range(nk):
            m = rng.randint(3, min(5, nd))
            stars.append(sorted(rng.sample(range(nd), m)))
        out.append(('drawn%d' % i, stars))
    return out


def check_grown(seed=2026112502, n_drawn=12, max_dist=16):
    rng = random.Random(seed)
    starts = [(k, v) for k, v in C.named_stars().items() if len({d for s in v for d in s}) <= 9]
    starts += small_starts(rng, n_drawn)
    takes = [None, 'Q', 'MET', 'MET:join', 'MET:offshoot', 'STEPS-1', 'STEPS-2', 'UP-TO-2', 'STEPS-1:join',
             'STEPS-2:offshoot', 'STEPS-3']
    res = {'runs': 0, 'knot_rounds': 0, 'bad_last': 0, 'bad_every': 0, 'fails_seen': {'parity': 0, 'nae': 0},
           'untested': 0, 'disagree': 0, 'extension_bad': 0, 'kernel_cuts': 0, 'examples_bad': []}
    for sname, stars in starts:
        for base in E.BASE_ORDER:
            for take in takes:
                for choice in (['OLDEST'] if take is None else ['OLDEST', 'BY-COUNT']):
                    for kl in ('nae', 'parity'):
                        law = E.Law.from_base(base, knot_law=kl, take=take, choice=choice)
                        S = E.from_stars(stars)
                        recs = []
                        for r in range(4):
                            T = S.copy()
                            try:
                                rec, _ = E.round_step(T, law)
                            except E.GuardStop:
                                break
                            if T.n_dist > max_dist:
                                break
                            S = T
                            recs.append(rec)
                        if not recs:
                            continue
                        res['runs'] += 1
                        out = K.test_run(S, recs, law, direct_rounds='every')
                        res['disagree'] += len(out['disagree'])
                        res['untested'] += len(out['untested'])
                        res['extension_bad'] += len(out['extension_bad'])
                        res['kernel_cuts'] += len(out['cuts'])
                        fails = {f['knot'] for f in out['fails']}
                        for t in range(S.round + 1):
                            nk = K.knots_upto(S, t)
                            br = K.brute([S.places[u] for u in range(nk)], kl)
                            for u in range(nk):
                                res['knot_rounds'] += 1
                                if (u in fails) == br[u]:
                                    if t == S.round:
                                        res['bad_last'] += 1
                                    res['bad_every'] += 1
                                    if len(res['examples_bad']) < 10:
                                        res['examples_bad'].append([sname, base, take, choice, kl, t, u])
                        res['fails_seen'][kl] += len(fails)
    return res


def main():
    t0 = time.time()
    a = check_drawn()
    C.log('drawn', a)
    b = check_grown()
    C.log('grown', b)
    ok = (a['free_bad'] == 0 and a['rank_bad'] == 0 and not any(a['knot_bad'].values()) and b['bad_every'] == 0
          and b['disagree'] == 0 and b['untested'] == 0 and b['extension_bad'] == 0)
    C.write_json('knot_checks.json', {'drawn': a, 'grown': b, 'ok': ok, 'seconds': round(time.time() - t0, 1)})
    C.log('ok' if ok else 'FAILED')


if __name__ == '__main__':
    C.cap_memory()
    main()
