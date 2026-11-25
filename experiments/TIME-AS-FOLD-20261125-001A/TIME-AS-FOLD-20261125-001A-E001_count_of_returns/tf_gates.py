"""The gates G1, G2, G3 of the pre-registration (run before any other run).

  g1a  the engine's rounds against the engine of the study of parts that meet again, knot for knot: the twelve named
       starts and the 227, the control under every base law, both knot laws, 18 rounds, knot bound 4,000, the guard.
  g1b  the ring study's census (bref.census_starts, 86,032 starts) under RING-LAW (parity), 10 rounds, knot bound 1,500:
       the starts set aside by the parity knot test, and the starts with a tick giving parts off (series with "past its
       start"), which must be exactly the 227 of starts.json.
  g2   every run of run1.jsonl.gz and run3.jsonl.gz of the study of parts that meet again except RECORD-k,
       ALL-JOINABLE, CARRY and FIRST, regrown: per round members, parts, classes, knots, most holders, births, joins,
       offshoots and two-knot parts against the frozen files.
  g3   25 renamed copies and 50 altered copies of parts from runs of run 1's list: the sameness test accepts every
       renamed copy and rejects every altered one; each altered copy is checked not the same by brute force.
Usage: python -B tf_gates.py g1a|g1b|g2|g3 [--procs 6]
"""
from __future__ import annotations

import argparse
import gzip
import json
import multiprocessing as mp
import os
import random
import sys
import time
from collections import Counter, defaultdict

import tf_common as C
import tf_engine as E
import tf_knots as K
import tf_series as Se

PM_BASE = {
    'RING-LAW': dict(ration='CAP-3', treatment='CANCEL-WAIT'),
    'RING-LAW+FILLERS': dict(ration='CAP-3', treatment='CANCEL-WAIT', fillers=True),
    'COPY-LAW(RETIRE)': dict(ration='FLOOR1', treatment='CANCEL-RETIRE'),
    'COPY-LAW(OFFSHOOT)': dict(ration='FLOOR1', treatment='CANCEL-OFFSHOOT'),
    'COPY-LAW(WAIT)': dict(ration='FLOOR1', treatment='CANCEL-WAIT'),
    'CAP-3(RETIRE)': dict(ration='CAP-3', treatment='CANCEL-RETIRE'),
    'CAP-3(OFFSHOOT)': dict(ration='CAP-3', treatment='CANCEL-OFFSHOOT'),
}


def _init():
    C.cap_memory()


# ----------------------------------------------------------------------------------------------------------- G1a
def g1a_job(args):
    name, stars, base, kl = args
    pm = C.import_pm()
    t0 = time.process_time()
    law = E.Law.from_base(base, knot_law=kl)
    A = E.Run(E.from_stars(stars), law, rounds=18, knot_bound=4000, clock=E.Clock(600), keep_rosters=False)
    t1 = time.process_time()
    L2 = pm.Law(knot_law=kl, **PM_BASE[base])
    B = pm.Run(pm.from_stars(stars), L2, rounds=18, knot_bound=4000, keep=False)
    t2 = time.process_time()
    SA, SB = A.S, B.S
    diffs = []
    if A.rounds_done != B.rounds_done:
        diffs.append('rounds %s %s' % (A.rounds_done, B.rounds_done))
    if (A.stop or None) != (B.stop or None):
        diffs.append('stop %s %s' % (A.stop, B.stop))
    if SA.n_knots != SB.n_knots:
        diffs.append('knots %d %d' % (SA.n_knots, SB.n_knots))
    first = None
    for i in range(min(SA.n_knots, SB.n_knots)):
        if (SA.places[i] != SB.places[i] or tuple(SA.parents[i]) != tuple(SB.parents[i])
                or SA.made[i] != SB.made[i] or SA.kind[i] != SB.kind[i]):
            first = i
            break
    if first is not None:
        diffs.append('first knot %d: %s %s / %s %s' % (first, SA.places[first], SA.parents[first],
                                                       SB.places[first], SB.parents[first]))
    if [b != E.NEVER for b in SA.bar_at] != list(SB.barred):
        diffs.append('barred distinctions differ')
    rn = []
    for ra, rb in zip(A.records, B.records):
        ka = (ra['n_births'], ra['n_joins'], ra['n_offshoots'], ra['stalled'], ra['closing'], len(ra['short']))
        kb = (rb['n_births'], rb['n_joins'], rb['n_offshoots'], rb['stalled'], rb['closing'], len(rb['short']))
        if ka != kb:
            rn.append(ra['round'])
        else:
            fa = [(b['id'], b['D'], b['f'], b['usable'], b['barred'], tuple(b['inputs'])) for b in ra['births']]
            fb = [(b['id'], b['D'], b['f'], b['usable'], b['barred'], tuple(b['inputs'])) for b in rb['births']]
            if fa != fb:
                rn.append(ra['round'])
    if rn:
        diffs.append('records differ at rounds %s' % rn[:5])
    return {'start': name, 'base': base, 'knot_law': kl, 'rounds': A.rounds_done, 'stop': A.stop,
            'guard': A.guard, 'pm_guard': B.guard, 'knots': SA.n_knots, 'same': not diffs, 'diffs': diffs,
            'sec_mine': round(t1 - t0, 2), 'sec_pm': round(t2 - t1, 2)}


def g1a(procs):
    jobs = []
    for name, stars in C.named_stars().items():
        for base in E.BASE_ORDER:
            for kl in ('nae', 'parity'):
                jobs.append((name, stars, base, kl))
    for name, stars in C.ring227():
        for base in E.BASE_ORDER:
            for kl in ('nae', 'parity'):
                jobs.append((name, stars, base, kl))
    C.log('G1a: %d runs on both engines' % len(jobs))
    out = []
    with mp.Pool(procs, initializer=_init, maxtasksperchild=50) as pool:
        for i, r in enumerate(pool.imap_unordered(g1a_job, jobs, chunksize=4)):
            out.append(r)
            if (i + 1) % 200 == 0:
                C.log('G1a %d/%d, differing so far %d' % (i + 1, len(jobs), sum(not x['same'] for x in out)))
    out.sort(key=lambda r: (r['start'], r['base'], r['knot_law']))
    res = {'runs': len(out), 'same': sum(r['same'] for r in out), 'differ': [r for r in out if not r['same']],
           'stops': Counter(str(r['stop']) for r in out), 'rounds_total': sum(r['rounds'] for r in out),
           'sec_mine': round(sum(r['sec_mine'] for r in out), 1), 'sec_pm': round(sum(r['sec_pm'] for r in out), 1)}
    res['pass'] = res['same'] == res['runs']
    C.write_json('g1a.json', {'summary': res, 'runs': out})
    C.log('G1a', {k: v for k, v in res.items() if k != 'differ'}, 'differ', len(res['differ']))
    return res


# ----------------------------------------------------------------------------------------------------------- G1b
def census_list():
    bref = C.import_bref()
    out = []
    for n in (3, 4, 5, 6):
        for s in bref.census_starts(n):
            out.append((s['g'], tuple(s['loose'])))
    return out


def parity_start_ok(stars):
    S = E.from_stars(stars)
    ks = list(range(S.n_knots))
    ke = K._kernel_full(S.places, ks)
    bad_r = [u for u in ks if K.rank_difference(S.places, ks, S.places[u]) != 1]
    bad_k = [u for u in ks if ke[u] != len(S.places[u]) - 1]
    return (not bad_r and not bad_k), bad_r, bad_k


def g1b_job(chunk):
    bref = C.import_bref()
    law = E.Law.from_base('RING-LAW', knot_law='parity')
    out = []
    for g, loose in chunk:
        t0 = time.process_time()
        stars = bref.census_stars(g, list(loose))
        ok, br, bk = parity_start_ok(stars)
        rec = {'g': g, 'loose': list(loose)}
        if not ok:
            rec['set_aside'] = True
            rec['disagree'] = sorted(set(br) ^ set(bk))
            out.append(rec)
            continue
        try:
            A = E.Run(E.from_stars(stars), law, rounds=10, knot_bound=1500, clock=E.Clock(600))
            if A.stop == 'limit':
                rec['unfinished'] = True
                out.append(rec)
                continue
            res = {}
            for past in (True, False):
                ser, _ = Se.build_series(A, past, clock=A.clock)
                Se.describe(ser)
                res['past' if past else 'nopast'] = any(s['ticks_off'] >= 1 for s in ser)
            rec.update(res)
            rec['rounds'] = A.rounds_done
            rec['stop'] = A.stop
        except E.LimitReached:
            rec['unfinished'] = True
        rec['sec'] = round(time.process_time() - t0, 3)
        out.append(rec)
    return out


def g1b(procs, sample=None):
    starts = census_list()
    C.log('G1b: %d starts enumerated' % len(starts))
    if sample:
        rng = random.Random(sample[1])
        starts = rng.sample(starts, sample[0])
    chunks = [starts[i:i + 50] for i in range(0, len(starts), 50)]
    rows = []
    with mp.Pool(procs, initializer=_init, maxtasksperchild=20) as pool:
        for i, part in enumerate(pool.imap_unordered(g1b_job, chunks)):
            rows.extend(part)
            if (i + 1) % 40 == 0:
                C.log('G1b %d/%d chunks, %d starts, %.1f s of process time in the starts' % (
                    i + 1, len(chunks), len(rows), sum(r.get('sec', 0) for r in rows)))
    return rows


def g1b_report(rows, n_enumerated):
    ref = {(r['atlas_index'], tuple(r['loose'])) for r in C.starts()['ring_study_returning_starts']}
    aside = [r for r in rows if r.get('set_aside')]
    unf = [r for r in rows if r.get('unfinished')]
    past = {(r['g'], tuple(r['loose'])) for r in rows if r.get('past')}
    nopast = {(r['g'], tuple(r['loose'])) for r in rows if r.get('nopast')}
    res = {'starts_enumerated': n_enumerated, 'starts_run': len(rows), 'set_aside_parity_knot_test': len(aside),
           'set_aside_disagreements': sum(1 for r in aside if r.get('disagree')), 'unfinished': len(unf),
           'with_a_tick_giving_parts_off_past': len(past), 'with_a_tick_giving_parts_off_nopast': len(nopast),
           'equal_to_the_ring_study_list': past == ref, 'missing_from_mine': sorted(ref - past)[:50],
           'extra_in_mine': sorted(past - ref)[:50],
           'stops': Counter(str(r.get('stop')) for r in rows if not r.get('set_aside'))}
    res['pass'] = (res['equal_to_the_ring_study_list'] and len(aside) == 316 and n_enumerated == 86032
                   and not unf)
    return res


# ------------------------------------------------------------------------------------------------------------ G2
def g2_law(lf):
    tr = lf['treatment']
    return E.Law(ration=lf['ration'], treatment=tr, release=lf['release'], no_offshoot=lf['no_offshoot'],
                 fillers=lf['fillers'], knot_law=lf['knot_law'], take=lf['take'], choice=lf['choice'],
                 late=lf['late'], base_treatment=lf['base_treatment'], order_reversed=lf['order_reversed'],
                 demand_before_takes=lf['demand_before_takes'], fresh_by_parents=lf['fresh_by_parents'])


def two_knot_parts(R):
    n = 0
    for P in R.parts:
        if len(P) != 2:
            continue
        a, b = P
        if (R.h[a], R.k[a], R.h[b], R.k[b]) != (2, 0, 2, 0):
            continue
        if a in R.meets_member or b in R.meets_member:
            continue
        if any(a in M and b in M for M in R.maxsets):
            n += 1
    return n


def round_stats(A, t):
    from tf_tests import classes_of
    R = A.roster(t)
    S = A.S
    nk = K.knots_upto(S, t)
    mh = 0
    for hs in S.holders:
        c = 0
        for w in hs:
            if w < nk:
                c += 1
        if c > mh:
            mh = c
    cls = classes_of(S, R, t)
    row = {'t': t, 'members': len(R.members), 'parts': len(R.parts), 'classes': len(set(cls)),
           'max_holders': mh, 'knots': nk, 'N2': two_knot_parts(R)}
    if t >= 1:
        rec = A.records[t - 1]
        row.update({'births': rec['n_births'], 'joins': rec['n_joins'], 'offshoots': rec['n_offshoots']})
    return row


START_ALIASES = {}


def g2_job(row):
    stars = C.named_stars()[row['start']]
    law = g2_law(row['law_fields'])
    A = E.Run(E.from_stars(stars), law, rounds=8, knot_bound=1500, clock=E.Clock(600))
    mine = [round_stats(A, t) for t in range(A.rounds_done + 1)]
    ref = row['per_round']
    keys = ('members', 'parts', 'classes', 'max_holders', 'knots', 'births', 'joins', 'offshoots', 'N2')
    bad = []
    for a, b in zip(mine, ref):
        for k in keys:
            if a.get(k) != b.get(k):
                bad.append((a['t'], k, a.get(k), b.get(k)))
    if len(mine) != len(ref):
        bad.append(('rounds', len(mine) - 1, len(ref) - 1))
    if (A.stop or None) != (row['stop'] or None):
        bad.append(('stop', A.stop, row['stop']))
    return {'run': row['run'], 'start': row['start'], 'law': row['law'], 'rounds': len(ref), 'mine_rounds': len(mine),
            'ok': not bad, 'bad': bad[:10]}


def g2(procs):
    rows = []
    for fn in ('run1.jsonl.gz', 'run3.jsonl.gz'):
        with gzip.open(os.path.join(C.PM_ART, fn), 'rt') as f:
            for line in f:
                r = json.loads(line)
                lf = r['law_fields']
                if lf['joinable'] != 'MET' or lf['take'] in ('CARRY', 'FIRST'):
                    continue
                rows.append({'run': r['run'], 'start': r['start'], 'law': r['law'], 'law_fields': lf,
                             'per_round': r['per_round'], 'stop': r['stop'], 'names_reversed': r['names_reversed']})
    assert all(not r['names_reversed'] for r in rows)
    C.log('G2: %d runs' % len(rows))
    out = []
    with mp.Pool(procs, initializer=_init, maxtasksperchild=50) as pool:
        for i, r in enumerate(pool.imap_unordered(g2_job, rows, chunksize=4)):
            out.append(r)
            if (i + 1) % 200 == 0:
                C.log('G2 %d/%d, bad %d' % (i + 1, len(rows), sum(not x['ok'] for x in out)))
    res = {'runs': len(out), 'rounds': sum(r['rounds'] for r in out), 'mismatching_runs': sum(not r['ok'] for r in out),
           'examples': [r for r in out if not r['ok']][:20]}
    res['pass'] = res['mismatching_runs'] == 0 and res['runs'] == 1134
    C.write_json('g2.json', {'summary': res, 'runs': sorted(out, key=lambda r: (r['run'], r['start'], r['law']))})
    C.log('G2', {k: v for k, v in res.items() if k != 'examples'})
    return res


# ------------------------------------------------------------------------------------------------------------ G3
class FakeRoster:
    def __init__(self, members, h, k, maxsets):
        self.members = tuple(sorted(members))
        self.h, self.k = dict(h), dict(k)
        self.maxsets = [frozenset(M) for M in maxsets]
        self.parts = [self.members]
        self.part_of = {u: 0 for u in self.members}
        self._cache = {}


def g3(seed=2026112503):
    """Parts from runs of run 1's list (the first runs in its order, grown here for this gate only)."""
    rng = random.Random(seed)
    named = C.named_stars()
    pool = []
    takes = [None, 'Q', 'MET', 'STEPS-1', 'STEPS-2', 'MET:join', 'STEPS-1:join']
    for name in ('two-knot', 'three-knot', 'Ring(5,3)', 'D2(4,3)', 'generator7'):
        for base in E.BASE_ORDER:
            for take in takes:
                law = E.Law.from_base(base, knot_law='nae', take=take, choice='OLDEST')
                A = E.Run(E.from_stars(named[name]), law, rounds=8, knot_bound=1500)
                for t in range(A.rounds_done + 1):
                    R = A.roster(t)
                    for P in R.parts:
                        if 2 <= len(P) <= 40:
                            ms = Se.part_data(R, P)[2]
                            if ms:
                                pool.append((name, base, take, t, P, {u: R.h[u] for u in P},
                                             {u: R.k[u] for u in P}, [sorted(M) for M in ms]))
    rng.shuffle(pool)
    renamed = []
    for item in pool[:25]:
        name, base, take, t, P, h, k, ms = item
        R1 = FakeRoster(P, h, k, ms)
        perm = list(P)
        rng.shuffle(perm)
        off = 1000
        mp_ = {u: off + perm.index(u) * 7 + 3 for u in P}
        R2 = FakeRoster([mp_[u] for u in P], {mp_[u]: h[u] for u in P}, {mp_[u]: k[u] for u in P},
                        [[mp_[x] for x in M] for M in ms])
        ok = Se.same_parts(R1, R1.members, R2, R2.members)
        ok2 = Se.same_parts(FakeRoster(P, h, k, ms), tuple(sorted(P)), FakeRoster([mp_[u] for u in P],
                            {mp_[u]: h[u] for u in P}, {mp_[u]: k[u] for u in P}, [[mp_[x] for x in M] for M in ms]),
                            tuple(sorted(mp_[u] for u in P)), force_vf2=True)
        renamed.append({'from': [name, base, take, t], 'size': len(P), 'accepted': ok, 'accepted_vf2': ok2})
    small = [it for it in pool if len(it[4]) <= 7]
    altered = []
    kinds = ['h', 'k', 'drop member from a met set', 'add member to a met set', 'swap h of two members',
             'merge two met sets', 'split a met set']
    i = 0
    while len(altered) < 50 and i < 10000:
        it = small[i % len(small)]
        i += 1
        name, base, take, t, P, h, k, ms = it
        h2, k2, ms2 = dict(h), dict(k), [list(M) for M in ms]
        kind = kinds[len(altered) % len(kinds)]
        u = rng.choice(P)
        if kind == 'h':
            h2[u] = h2[u] + 1
        elif kind == 'k':
            k2[u] = k2[u] + 1
        elif kind == 'drop member from a met set':
            M = rng.choice(ms2)
            if len(M) <= 2:
                continue
            M.remove(rng.choice(M))
        elif kind == 'add member to a met set':
            M = rng.choice(ms2)
            out = [x for x in P if x not in M]
            if not out:
                continue
            M.append(rng.choice(out))
        elif kind == 'swap h of two members':
            a, b = rng.sample(P, 2)
            if h2[a] == h2[b]:
                continue
            h2[a] = h2[a] + 1
            h2[b] = h2[b] - 1 if h2[b] > 1 else h2[b] + 2
        elif kind == 'merge two met sets':
            if len(ms2) < 2:
                continue
            a, b = rng.sample(range(len(ms2)), 2)
            ms2[a] = sorted(set(ms2[a]) | set(ms2[b]))
            del ms2[b]
        else:
            M = rng.choice(ms2)
            if len(M) < 4:
                continue
            ms2.remove(M)
            ms2 += [M[:len(M) // 2] + [M[-1]], M[len(M) // 2:]]
        # keep a family of maximal sets
        fs = {frozenset(M) for M in ms2}
        fs = [M for M in fs if not any(M < O for O in fs)]
        R1 = FakeRoster(P, h, k, ms)
        R2 = FakeRoster(P, h2, k2, fs)
        brute_same = Se.same_brute(R1, R1.members, R2, R2.members)
        if brute_same:
            continue                       # the alteration made no difference up to renaming: not an altered copy
        test = Se.same_parts(R1, R1.members, R2, R2.members)
        test2 = Se.same_parts(FakeRoster(P, h, k, ms), R1.members, FakeRoster(P, h2, k2, fs), R2.members,
                              force_vf2=True)
        altered.append({'from': [name, base, take, t], 'size': len(P), 'kind': kind, 'rejected': not test,
                        'rejected_vf2': not test2, 'brute_not_same': True})
    # supplement (not the gate): renamed copies of every drawn part of 7 to 40 members, up to 300 (the VF2 path)
    big = [it for it in pool if len(it[4]) >= 7][:300]
    sup = 0
    for it in big:
        name, base, take, t, P, h, k, ms = it
        perm = list(P)
        rng.shuffle(perm)
        mp_ = {u: 5000 + perm.index(u) for u in P}
        if Se.same_parts(FakeRoster(P, h, k, ms), tuple(sorted(P)), FakeRoster([mp_[u] for u in P],
                         {mp_[u]: h[u] for u in P}, {mp_[u]: k[u] for u in P}, [[mp_[x] for x in M] for M in ms]),
                         tuple(sorted(mp_[u] for u in P))):
            sup += 1
    res = {'renamed': len(renamed), 'renamed_accepted': sum(r['accepted'] for r in renamed), 'altered': len(altered),
           'altered_rejected': sum(r['rejected'] for r in altered), 'pool_parts': len(pool),
           'renamed_accepted_vf2': sum(r['accepted_vf2'] for r in renamed),
           'altered_rejected_vf2': sum(r['rejected_vf2'] for r in altered),
           'supplement_large_renamed': len(big), 'supplement_large_accepted': sup}
    res['pass'] = (res['renamed'] == 25 and res['renamed_accepted'] == 25 and res['altered'] == 50
                   and res['altered_rejected'] == 50)
    C.write_json('g3.json', {'summary': res, 'renamed': renamed, 'altered': altered})
    C.log('G3', res)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('what')
    ap.add_argument('--procs', type=int, default=6)
    ap.add_argument('--sample', type=int, default=0)
    a = ap.parse_args()
    C.cap_memory()
    if a.what == 'g1a':
        g1a(a.procs)
    elif a.what == 'g1b':
        rows = g1b(a.procs, sample=(a.sample, 2026112504) if a.sample else None)
        n_enum = 86032
        res = g1b_report(rows, len(census_list()))
        if a.sample:
            res['sample'] = a.sample
            C.write_json('g1b_timing_sample.json', {'summary': res, 'seconds': [r.get('sec') for r in rows]})
        else:
            C.write_json('g1b.json', {'summary': res}, gz=False)
            C.write_json('g1b_rows.json.gz', rows, gz=True)
        C.log('G1b', res)
    elif a.what == 'g2':
        g2(a.procs)
    elif a.what == 'g3':
        g3()


if __name__ == '__main__':
    main()
