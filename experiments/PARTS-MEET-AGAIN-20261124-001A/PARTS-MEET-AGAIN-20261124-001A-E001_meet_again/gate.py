"""Run G, the gate (prediction P0).

  part ring   - with no taking rule the engine's complete rounds equal the ring study's engine knot for knot (places,
                parents, rounds made, barred flags, stalls) on every run of G, with that engine's group order (R 1);
                IMPLIED equals LITERAL on every parity run; the knot tests of every round read.
  part rq     - on the overlap (ordinary count) the engine equals the rule-R engine (rlaw.Growth, rule R) and the rule-Q
                engine (qlaw.QGrowth) after every round, on the seven named starts and the first 400 sparse draws, both
                knot laws, both conventions (R 2).
  part brute  - parity ranks, parity kernel and the not-all-equal direct test against brute force on 600 drawn small
                structures with several holders per distinction (seed 2026112403, R 3).
  part birth  - the birth method against the direct test (and brute force where small) on 600 drawn grown structures
                (seed 2026112402).

usage: python -B gate.py ring|rq|brute|birth [--chunk i/n]
"""
import argparse
import random
import sys
import time

import common as C
import knots as K
import pm

# ------------------------------------------------------------------------------------------------------ the G laws
T3 = ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT')


def g_laws():
    """(name, my Law kwargs, ring-engine Law kwargs).  The registered list of run G (RING-LAW, RING-LAW with FILLERS,
    COPY-LAW(t), CAP-3(t), FLOOR0 and ONE-FEWER with each t, HOLD with each), plus the definitions' other base forms
    (ORD/STALL, NO-OFFSHOOT) as extras, marked."""
    out = []
    base = [('RING-LAW', dict(ration='CAP-3', treatment='CANCEL-WAIT'), True),
            ('RING-LAW+FILLERS', dict(ration='CAP-3', treatment='CANCEL-WAIT', fillers=True), True)]
    for t in T3:
        base.append(('COPY-LAW(%s)' % t, dict(ration='FLOOR1', treatment=t), True))
    for t in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT'):
        base.append(('CAP-3(%s)' % t, dict(ration='CAP-3', treatment=t), True))
    for r in ('FLOOR0', 'ONE-FEWER'):
        for t in T3:
            base.append(('%s(%s)' % (r, t), dict(ration=r, treatment=t), True))
    for nm, kw, reg in list(base):
        out.append((nm, kw, reg))
        kw2 = dict(kw, release='HOLD')
        out.append((nm + '+HOLD', kw2, reg))
    out.append(('extra ORD/STALL', dict(ration='ORD', treatment='STALL'), False))
    out.append(('extra CAP-3/STALL', dict(ration='CAP-3', treatment='STALL'), False))
    out.append(('extra CAP-3/WAIT+NO-OFFSHOOT', dict(ration='CAP-3', treatment='CANCEL-WAIT', no_offshoot=True), False))
    out.append(('extra FLOOR1/RETIRE+NO-OFFSHOOT', dict(ration='FLOOR1', treatment='CANCEL-RETIRE', no_offshoot=True),
                False))
    return out


G_STARTS = ['Ring(5,3)', 'Ring(7,3)', 'D2(5,3)', 'two-knot', 'three-knot', 'three-knot-larger', 'generator7']


def compare_ring(E, mine, theirs_S, theirs_rec, t):
    """Knot for knot after round t."""
    S = mine.snap[t]
    T = theirs_S
    if S.n_knots != T.n_knots or S.n_distinctions != T.n_distinctions:
        return 'sizes differ (%d/%d knots, %d/%d distinctions)' % (S.n_knots, T.n_knots, S.n_distinctions,
                                                                  T.n_distinctions)
    for u in range(S.n_knots):
        if list(S.places[u]) != list(T.places[u]):
            return 'places of knot %d differ: %s / %s' % (u, S.places[u], T.places[u])
        if tuple(S.parents[u]) != tuple(T.parents[u]):
            return 'parents of knot %d differ' % u
        if S.made[u] != T.made[u]:
            return 'round made of knot %d differs' % u
    for d in range(S.n_distinctions):
        if bool(S.barred[d]) != bool(T.barred[d]):
            return 'barred flag of %d differs' % d
    if theirs_rec is not None:
        mr = mine.records[t - 1]
        if bool(mr['stalled']) != bool(theirs_rec['stalled']):
            return 'stall differs'
        if bool(mr['closing']) != bool(theirs_rec['closing']):
            return 'closing differs'
    return None


def part_ring(args):
    E = C.ring_engine()
    tag = ('' if not args.chunk else '_' + args.chunk.replace('/', 'of')) + ('_registered' if args.registered_only else '')
    rows = C.JsonLines('gate_ring%s.jsonl' % tag)
    agg = {'runs': 0, 'rounds_compared': 0, 'mismatches': 0, 'implied_vs_literal_runs': 0,
           'implied_vs_literal_mismatch': 0, 'knot_verdicts': 0, 'knot_fails': 0, 'method_disagreements': 0,
           'birth_vs_direct': 0, 'untested': 0, 'stops': {}}
    jobs = []
    for sname in G_STARTS:
        for rev in (False, True):
            for lname, kw, reg in g_laws():
                for kl in ('nae', 'parity'):
                    jobs.append((sname, rev, lname, kw, reg, kl))
    if args.chunk:
        i, n = map(int, args.chunk.split('/'))
        jobs = jobs[i::n]
    if args.registered_only:
        jobs = [j for j in jobs if j[4]]
    for sname, rev, lname, kw, reg, kl in jobs:
        t0 = time.time()
        S0 = pm.start(sname, reverse_names=rev)
        lawL = pm.Law(knot_law=kl, closing='LITERAL', group_order='lex', **kw)
        mine = pm.Run(S0, lawL)
        # the ring engine on the same start (its from_stars with the same names)
        stars = [list(P) for P in S0.places]
        T = E.from_stars(stars)
        elaw = E.Law(kw['ration'], kw['treatment'], kw.get('release', 'RELEASE'), no_offshoot=kw.get('no_offshoot', False),
                     fillers=kw.get('fillers', False), knot_law=kl)
        diff = compare_ring(E, mine, T, None, 0)
        compared = 0
        for t in range(1, mine.rounds_done + 1):
            if diff:
                break
            T, trec = E.round_step(T, elaw)
            diff = compare_ring(E, mine, T, trec, t)
            compared += 1
        # the ring engine's own bound: it stops after the round past 1,500 knots as this engine does
        row = {'start': sname, 'names_reversed': rev, 'law': lname, 'registered': reg, 'knot_law': kl,
               'rounds': mine.rounds_done, 'stop': mine.stop, 'guard': mine.guard, 'knots': mine.S.n_knots,
               'rounds_compared': compared, 'mismatch': diff}
        agg['runs'] += 1
        agg['rounds_compared'] += compared
        agg['mismatches'] += bool(diff)
        agg['stops'][str(mine.stop)] = agg['stops'].get(str(mine.stop), 0) + 1
        # IMPLIED against LITERAL (every distinction has at most two holders; the starts are connected)
        lawI = pm.Law(knot_law=kl, closing='IMPLIED', **kw)
        runI = pm.Run(S0, lawI)
        if kl == 'parity':
            lawL2 = pm.Law(knot_law=kl, closing='LITERAL', **kw)
            runL = pm.Run(S0, lawL2)
            agg['implied_vs_literal_runs'] += 1
            same = runI.rounds_done == runL.rounds_done and all(
                runI.snap[t].places == runL.snap[t].places and runI.snap[t].barred == runL.snap[t].barred
                for t in range(runI.rounds_done + 1))
            row['implied_equals_literal'] = same
            agg['implied_vs_literal_mismatch'] += (not same)
        # the knot tests on the primary run (IMPLIED), every round read
        kt = K.test_run(runI.snap, lawI)
        row['knot_tests'] = {'verdicts': kt['verdicts'], 'fails': kt['fails'][:40], 'n_fails': len(kt['fails']),
                             'disagree': kt['disagree'][:40], 'n_disagree': len(kt['disagree']),
                             'birth_vs_direct': kt['birth_vs_direct'], 'untested': kt['untested']}
        agg['knot_verdicts'] += kt['verdicts']
        agg['knot_fails'] += len(kt['fails'])
        agg['method_disagreements'] += len(kt['disagree'])
        agg['birth_vs_direct'] += kt['birth_vs_direct']
        agg['untested'] += len(kt['untested'])
        row['seconds'] = round(time.time() - t0, 2)
        rows.write(row)
        if diff:
            C.log('MISMATCH', sname, rev, lname, kl, diff)
    rows.close()
    C.write_json('gate_ring_summary%s.json' % tag, agg)
    C.log(agg)


# ---------------------------------------------------------------------------------------------- rule R and rule Q
def part_rq(args):
    rlaw, qlaw = C.rq_engines()
    lib = rlaw.lib
    starts = list(lib.recorded_sources().items())
    draws = []
    for dr in lib.p3_draws():
        draws.append(('draw a%d/%d' % (dr['arm'], dr['draw']), dr['stars']))
        if len(draws) == 400:
            break
    allstarts = [(n, s) for n, s in starts] + draws
    jobs = [(n, s, kl, conv, rule) for n, s in allstarts for kl in ('nae', 'parity') for conv in ('O', 'N')
            for rule in ('R', 'Q')]
    if args.chunk:
        i, n = map(int, args.chunk.split('/'))
        jobs = jobs[i::n]
    rows = C.JsonLines('gate_rq%s.jsonl' % ('' if not args.chunk else '_' + args.chunk.replace('/', 'of')))
    agg = {'runs': 0, 'rounds_compared': 0, 'mismatches': 0, 'outcomes': {}}
    for name, stars, kl, conv, rule in jobs:
        t0 = time.time()
        choice = 'OLDEST' if conv == 'O' else 'NEWEST'
        if rule == 'R':
            law = pm.Law('ORD', 'SHORT-TAKES', choice=choice, knot_law=kl, loose_order='desc')
        else:
            law = pm.Law('ORD', 'STALL', take='Q', choice=choice, knot_law=kl, loose_order='desc')
        S0 = pm.from_stars([list(s) for s in stars])
        mine = pm.Run(S0, law)
        R = mine.rounds_done
        last_cmp = R
        # mine keeps a stall round (no change); theirs ends at a stall: compare through the stall round
        stall_round = next((r['round'] for r in mine.records if r['stalled'] or r['residual_stall']), None)
        horizon = min(R, stall_round) if stall_round else R
        if horizon == 0:
            row = {'start': name, 'knot_law': kl, 'conv': conv, 'rule': rule, 'rounds_mine': R, 'stop': mine.stop,
                   'rounds_compared': 0, 'mismatch': None, 'note': 'no round read'}
            rows.write(row)
            agg['runs'] += 1
            continue
        if rule == 'R':
            g = rlaw.Growth([tuple(s) for s in stars], kl, rule='R', convention=conv, check=False, bound_next=True)
        else:
            g = qlaw.QGrowth([tuple(s) for s in stars], kl, conv, reread=True, bound_next=True)
        g.run(horizon, 1000000)
        diff = None
        compared = 0
        n_at = g.n_at
        for t in range(1, horizon + 1):
            if t > len(g.rounds):
                # theirs has no round t: a stall, residual stall or closing
                rec = mine.records[t - 1]
                theirs = g.outcome
                ok = ((theirs == 'stall' and rec['stalled']) or (theirs == 'residual_stall' and rec['residual_stall'])
                      or (theirs == 'closed' and rec['stopped']))
                if t == stall_round and ok:
                    compared += 1
                elif not ok:
                    diff = 'round %d: theirs ended (%s), mine %s' % (t, theirs, {k: rec[k] for k in (
                        'stalled', 'residual_stall', 'stopped', 'n_births')})
                break
            if g.rounds[t - 1].get('fresh_lower_bound'):
                break
            S = mine.snap[t]
            if S.n_knots != n_at[t]:
                diff = 'round %d: knots %d / %d' % (t, S.n_knots, n_at[t])
                break
            bad = None
            for u in range(S.n_knots):
                if sorted(S.places[u]) != sorted(g.stars[u]):
                    bad = 'round %d: knot %d places %s / %s' % (t, u, sorted(S.places[u]), sorted(g.stars[u]))
                    break
            if bad:
                diff = bad
                break
            ps_mine = [b['parents'] for b in mine.records[t - 1]['births']]
            ps_theirs = [list(p) for p in g.rounds[t - 1]['parents']]
            if ps_mine != ps_theirs:
                diff = 'round %d: parents differ' % t
                break
            compared += 1
        if diff is None and stall_round and stall_round <= R and len(g.rounds) >= stall_round and \
                not g.rounds[stall_round - 1].get('fresh_lower_bound'):
            diff = 'round %d: mine stalls, theirs made the round' % stall_round
        row = {'start': name, 'knot_law': kl, 'conv': conv, 'rule': rule, 'rounds_mine': R, 'stop': mine.stop,
               'guard': mine.guard, 'their_outcome': g.outcome, 'their_rounds': len(g.rounds),
               'rounds_compared': compared, 'mismatch': diff, 'seconds': round(time.time() - t0, 2)}
        rows.write(row)
        agg['runs'] += 1
        agg['rounds_compared'] += compared
        agg['mismatches'] += bool(diff)
        agg['outcomes'][g.outcome] = agg['outcomes'].get(g.outcome, 0) + 1
        if diff:
            C.log('MISMATCH', name, kl, conv, rule, diff)
    rows.close()
    C.write_json('gate_rq_summary%s.json' % ('' if not args.chunk else '_' + args.chunk.replace('/', 'of')), agg)
    C.log(agg)


# -------------------------------------------------------------------------------------------------- brute force
def random_structure(rng):
    nk = rng.randint(2, 7)
    D = rng.randint(4, 14)
    places = []
    for _ in range(nk):
        m = rng.randint(2, min(6, D))
        places.append(sorted(rng.sample(range(D), m)))
    used = sorted({d for P in places for d in P})
    ren = {d: i for i, d in enumerate(used)}
    return [[ren[d] for d in P] for P in places]


def part_brute(args):
    rng = random.Random(2026112403)
    agg = {'structures': 0, 'knot_verdicts': 0, 'failing': 0, 'mismatch_ranks': 0, 'mismatch_kernel': 0,
           'mismatch_nae': 0, 'max_holders_hist': {}}
    rows = C.JsonLines('gate_brute.jsonl')
    for i in range(600):
        stars = random_structure(rng)
        S = pm.from_stars_any(stars)
        mh = max(len(h) for h in S.holders)
        agg['max_holders_hist'][mh] = agg['max_holders_hist'].get(mh, 0) + 1
        bp, _ = K.brute(S, 'parity')
        bn, _ = K.brute(S, 'nae')
        rk = K.parity_ranks(S)
        ke = K.parity_kernel(S)
        nd = K.nae_direct(S, S.knots())
        mm = []
        for u in S.knots():
            agg['knot_verdicts'] += 2
            agg['failing'] += (not bp[u]) + (not bn[u])
            if (rk[u] == 1) != bp[u]:
                agg['mismatch_ranks'] += 1
                mm.append(('ranks', u))
            if (ke[u] == len(S.places[u]) - 1) != bp[u]:
                agg['mismatch_kernel'] += 1
                mm.append(('kernel', u))
            if nd[u] != bn[u]:
                agg['mismatch_nae'] += 1
                mm.append(('nae', u))
        agg['structures'] += 1
        rows.write({'i': i, 'stars': stars, 'parity_pass': [bp[u] for u in S.knots()],
                    'nae_pass': [bn[u] for u in S.knots()], 'mismatch': mm})
    rows.close()
    C.write_json('gate_brute_summary.json', agg)
    C.log(agg)


def random_grown(rng):
    """A drawn grown structure: a small start, then 1 to 4 rounds of 1 to 4 births; each birth takes 1 to 4 distinctions
    existing before its round (any number of holders) and receives 1 or 2 fresh ones (R 3)."""
    nk = rng.randint(1, 3)
    D = rng.randint(3, 8)
    stars = []
    for _ in range(nk):
        m = rng.randint(3, min(5, D))
        stars.append(sorted(rng.sample(range(D), m)))
    used = sorted({d for P in stars for d in P})
    ren = {d: i for i, d in enumerate(used)}
    stars = [[ren[d] for d in P] for P in stars]
    S = pm.from_stars_any(stars)
    snaps = [S.copy()]
    for r in range(rng.randint(1, 4)):
        T = S.copy()
        nd = T.n_distinctions
        births = []
        for _ in range(rng.randint(1, 4)):
            k = rng.randint(1, min(4, nd))
            births.append(sorted(rng.sample(range(nd), k)))
        for ins in births:
            x = T.n_knots
            T.places.append(list(ins))
            T.parents.append(())
            T.made.append(r + 1)
            T.kind.append('drawn')
            for d in ins:
                T.holders[d].append(x)
        for x in range(S.n_knots, T.n_knots):
            for _ in range(rng.randint(1, 2)):
                d = len(T.holders)
                T.holders.append([x])
                T.barred.append(False)
                T.places[x].append(d)
        T.round = r + 1
        S = T
        snaps.append(S.copy())
    return snaps


def part_birth(args):
    rng = random.Random(2026112402)
    agg = {'structures': 0, 'knots': 0, 'failing': 0, 'mismatch_direct': 0, 'mismatch_brute': 0, 'brute_checked': 0,
           'untested': 0}
    rows = C.JsonLines('gate_birth.jsonl')
    for i in range(600):
        snaps = random_grown(rng)
        S = snaps[-1]
        direct = K.nae_direct(S, S.knots())
        bf = None
        if S.n_distinctions <= 18:
            bf, _ = K.brute(S, 'nae')
            agg['brute_checked'] += 1
        mm = []
        for u in S.knots():
            t = S.made[u]
            if t == 0:
                b = K.nae_direct(snaps[0], [u])[u]
            else:
                b = K.birth_method(snaps[t - 1], snaps[t], u)
            agg['knots'] += 1
            if b is None:
                agg['untested'] += 1
                continue
            agg['failing'] += (not direct[u])
            if b != direct[u]:
                agg['mismatch_direct'] += 1
                mm.append(('direct', u))
            if bf is not None and bf[u] != direct[u]:
                agg['mismatch_brute'] += 1
                mm.append(('brute', u))
        agg['structures'] += 1
        rows.write({'i': i, 'places': S.places, 'made': S.made, 'direct': [direct[u] for u in S.knots()],
                    'mismatch': mm})
    rows.close()
    C.write_json('gate_birth_summary.json', agg)
    C.log(agg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('part', choices=('ring', 'rq', 'brute', 'birth'))
    ap.add_argument('--chunk', default=None)
    ap.add_argument('--mem', type=float, default=8)
    ap.add_argument('--registered-only', action='store_true')
    args = ap.parse_args()
    C.cap_memory(args.mem)
    {'ring': part_ring, 'rq': part_rq, 'brute': part_brute, 'birth': part_birth}[args.part](args)


if __name__ == '__main__':
    main()
