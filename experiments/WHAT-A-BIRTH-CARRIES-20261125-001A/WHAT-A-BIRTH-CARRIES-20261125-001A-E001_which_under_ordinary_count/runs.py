"""Runs N, P, 1, 1b and 2 of WHAT-A-BIRTH-CARRIES-20261125-001A-E001, with the per-pair readings (RD 4.1, 4.3, 4.4).

  python -B runs.py N  --procs k
  python -B runs.py P
  python -B runs.py 1  --procs k [--time-only n]
  python -B runs.py 1b --procs k
  python -B runs.py 2

A job is one underlying numbering ν with every marked entry over it (2^h runs) under one law; the pairs (ν, A, B) and
the reading at fixed h and ν are made inside the job, where the runs are (deviations 23).
"""
import sys

sys.dont_write_bytecode = True

import argparse
import multiprocessing as mp
import os
import time
from collections import Counter, defaultdict

import common
from common import log
import wbc

ORDER_1 = (('OLDEST', 'nae'), ('OLDEST', 'parity'), ('NEWEST', 'nae'), ('NEWEST', 'parity'))
PREFIXES = (2, 3, 4)


def _init():
    common.cap_memory(6)


# ------------------------------------------------------------------------------------------------- one run record
def run_record(run, label, h, nu, a, kt, secs):
    r2 = run.round2
    M = wbc.M_formula(h, a)
    s4 = None
    if run.law.take == 'MET' and run.law.ration == 'ORD':
        J = r2['J'] if r2 else None
        s4 = {'M': M, 'J_found': J is not None}
        if J is not None:
            s4.update({
                'sole_candidate_e': J['cands'] == [run.e], 'takes_e': J['takes'] == [run.e],
                'D': J['D'], 'f': J['f'], 'places': J['places'], 'implied': J['implied'],
                'D_ok': J['D'] == 2 + M, 'f_ok': J['f'] == 2 + M, 'places_ok': J['places'] == 5 + M,
                'groups_all_pairs': J['groups_all_pairs'], 'partners_ok': J['partners_are_xoff_and_ybirths'],
                'Ystart_meets': J['Ystart_meets_J_and_ybirths'],
                'loose_inputs_ok': J['loose_inputs_other_holder_only_parent']})
        if r2:
            s4.update({'M_births': r2['M_births'], 'M_births_ok': r2['M_births'] == M,
                       'y_take_one_place': r2['y_births_take_one_place_of_Y_start'],
                       'y_births_take_e': r2['y_births_take_e'], 'every_birth_takes_e': r2['every_birth_takes_e'],
                       'n_births_r2': r2['n_births'], 'x_births_D': r2['x_births_D'],
                       'y_members': r2['y_members'], 'y_joins_offshoots': r2['y_joins_offshoots']})
        s4['all_ok'] = bool(J is not None and s4['sole_candidate_e'] and s4['takes_e'] and s4['D_ok'] and
                            s4['f_ok'] and s4['places_ok'] and not s4['implied'] and s4['groups_all_pairs'] and
                            s4['partners_ok'] and s4['Ystart_meets'] and s4['loose_inputs_ok'] and
                            s4['M_births_ok'] and s4['y_take_one_place'])
    courses = {}
    for R in PREFIXES:
        c = wbc.course(run, R)
        if c is not None:
            courses[R] = c
    return {
        'label': label, 'h': h, 'nu': nu, 'a': a, 'usable': run.usable, 'stars': run.stars,
        'law': run.law.to_dict(), 'law_name': run.law.name(),
        'rounds_read': run.rounds_read, 'stop': run.stop, 'guard': run.guard, 'knots': run.S.n_knots,
        'meet_round': run.meet_round, 'meet_how': run.meet_how, 'linking': run.linking,
        'short_after1': run.short_after1, 'implied_rounds': run.implied_rounds, 's4': s4,
        'trace_counts': run.trace_counts, 'fingerprint': wbc.run_fingerprint(run),
        'knot_test': {'verdicts': kt['verdicts'], 'n_fail': len(kt['fails']), 'fails': kt['fails'][:20],
                      'n_disagree': len(kt['disagree']), 'n_untested': len(kt['untested']),
                      'birth_vs_direct': kt['birth_vs_direct']},
        'courses': courses, 'seconds': round(secs, 3),
        'values_r2': [(e['step'], e['kind'], e['pos'], e['value']) for e in run.values.get(2, [])],
        # every round as the gate listing counts it: (kind, parents, taken names, D, f) -> number of births
        'round_summaries': {rec['round']: sorted([list(k) + [v] for k, v in Counter(
            (b['kind'], len(b['parents']), tuple(b['takes']), b['D'], b['f']) for b in rec['births']).items()])
            for rec in run.recs},
        'x_round_births': {rec['round']: sorted([list(k) + [v] for k, v in Counter(
            (b['kind'], len(b['parents']), len(b['takes']), b['D'], b['f']) for b in rec['births']
            if all(run.desc(p) == 'X only' for p in b['parents'])).items()]) for rec in run.recs if rec['round'] >= 2},
    }


def same_meeting(rA, rB):
    if rA.meet_round is None or rA.meet_round != rB.meet_round:
        return None
    m = rA.meet_round
    la = sorted(x['key'] for x in rA.linking)
    lb = sorted(x['key'] for x in rB.linking)
    if la != lb:
        return False

    def births(run):
        out = []
        for rec in run.recs:
            t = rec['round']
            if t < 2 or t > m:
                continue
            for b in rec['births']:
                if not any(run.desc(p) == 'X only' for p in b['parents']):
                    continue
                item = (t, run.kkey[b['id']], b['kind'], tuple(sorted(run.kkey[p] for p in b['parents'])),
                        tuple(run.dkey[d] for d in b['loose']), tuple(run.dkey[d] for d in b['takes']),
                        b['implied'])
                if t < m:
                    item += (b['D'], b['p'], b['f'])
                out.append(item)
        return sorted(out)
    return births(rA) == births(rB)


# ------------------------------------------------------------------------------------------------------- one job
def job(args):
    label, h, nu, stars, entries, lawd, do_pairs = args
    t0 = time.time()
    law = wbc.Law(**lawd)
    runs = []
    recs = []
    for a, usable in entries:
        t1 = time.time()
        r = wbc.RunState(stars, usable, law)
        kt = wbc.knot_test(r)
        recs.append(run_record(r, label, h, nu, a, kt, time.time() - t1))
        runs.append((a, tuple(usable), r))
    # local classes of courses at each prefix (exact: VF2)
    local = {}
    reps = {}
    for R in PREFIXES:
        reg = wbc.Registry()
        ids = []
        for rec in recs:
            c = rec['courses'].get(R)
            ids.append(None if c is None else reg.classify(c))
        local[R] = ids
        reps[R] = [(cid, c, inv) for inv, lst in reg.buckets.items() for cid, c, _ in lst]
    for i, rec in enumerate(recs):
        rec['local_class'] = {R: local[R][i] for R in PREFIXES}
    pairs = []
    handed = None
    if do_pairs:
        for i, (a, A, rA) in enumerate(runs):
            for j, (b, B, rB) in enumerate(runs):
                if a >= b:
                    continue
                last = min(rA.rounds_read, rB.rounds_read)
                fd = wbc.compare_values(rA, rB, last)
                Jk = rA.kkey[rA.round2['J']['id']] if (rA.round2 and rA.round2['J']) else None
                ce = {R: (local[R][i] == local[R][j]) for R in PREFIXES
                      if local[R][i] is not None and local[R][j] is not None}
                pairs.append({'h': h, 'nu': nu, 'a': a, 'b': b, 'A': list(A), 'B': list(B),
                              'mA': rA.meet_round, 'mB': rB.meet_round, 'howA': rA.meet_how, 'howB': rB.meet_how,
                              'same_meeting': same_meeting(rA, rB), 'course_equal': ce, 'last_both': last,
                              'fd': fd, 'fd_is_J_demand': bool(fd and fd['round'] == 2 and Jk is not None and
                                                               fd['pos'] == ['D', Jk]),
                              'linkA': sorted(x['class'] for x in rA.linking or []),
                              'linkB': sorted(x['class'] for x in rB.linking or [])})
        handed = handed_reading(runs, local, h)
    return {'label': label, 'h': h, 'nu': nu, 'law': lawd, 'recs': recs, 'reps': reps, 'pairs': pairs,
            'handed': handed, 'seconds': round(time.time() - t0, 2)}


def handed_reading(runs, local, h):
    """RD 4.4 at fixed h and ν over a = 1 … h, at each prefix every run reached (deviations 15)."""
    idx = [i for i, (a, _, _) in enumerate(runs) if a >= 1]
    out = {}
    jkeys = set()
    for i in idx:
        r = runs[i][2]
        if r.round2 and r.round2['J']:
            jkeys.add(r.kkey[r.round2['J']['id']])
    for R in PREFIXES:
        if any(runs[i][2].rounds_read < R for i in idx):
            continue
        cls = defaultdict(list)
        for i in idx:
            cls[local[R][i]].append(i)
        P = frozenset(frozenset(v) for v in cls.values())
        if len(P) == 1:
            out[R] = {'verdict': 'no difference', 'n_classes': 1, 'P': [[runs[i][0] for i in v] for v in cls.values()]}
            continue
        pos_vals = defaultdict(dict)
        order = {}
        for i in idx:
            r = runs[i][2]
            for t in range(2, R + 1):
                for n, e in enumerate(r.values.get(t, [])):
                    key = (t, e['step'], e['pos'])
                    pos_vals[key][i] = e['value']
                    order.setdefault(key, (t, e['step'], n))
        inducing = []
        d_only = []
        for key, vals in pos_vals.items():
            part = defaultdict(list)
            for i in idx:
                part[repr(vals.get(i, 'absent'))].append(i)
            Q = frozenset(frozenset(v) for v in part.values())
            if Q == P:
                inducing.append(key)
                if key[1] == 6:
                    part2 = defaultdict(list)
                    for i in idx:
                        v = vals.get(i)
                        part2[repr(v[0] if v is not None else 'absent')].append(i)
                    if frozenset(frozenset(v) for v in part2.values()) == P:
                        d_only.append(key)
        inducing.sort(key=lambda k: order[k])
        first = inducing[0] if inducing else None

        def describe(key):
            t, step, pos = key
            d = {'round': t, 'step': step, 'pos_kind': pos[0]}
            if len(pos) > 1 and isinstance(pos[1], str):
                d['is_J'] = pos[1] in jkeys
            return d
        out[R] = {'verdict': 'handed in one value' if inducing else 'composed over several births',
                  'n_classes': len(P), 'P': sorted(sorted(runs[i][0] for i in v) for v in P),
                  'P_entries': sorted(sorted(list(runs[i][1]) for i in v) for v in P),
                  'n_inducing': len(inducing), 'first_inducing': describe(first) if first else None,
                  'inducing_kinds': sorted(Counter((k[0], k[1], k[2][0]) for k in inducing).items()),
                  'first_is_count': bool(first and first[1] in (2, 6, 7)),
                  'demand_alone_induces': bool(first and first in d_only),
                  'J_demand_r2_induces': any(k[0] == 2 and k[1] == 6 and k[2][1] in jkeys for k in inducing)}
    return out


# -------------------------------------------------------------------------------------------------- the reducer
class Merge:
    """Global classes of courses per key (VF2 inside invariant buckets) and the run index."""

    def __init__(self):
        self.reg = defaultdict(wbc.Registry)
        self.map = {}

    def add(self, key, res):
        for R, lst in res['reps'].items():
            reg = self.reg[key + (R,)]
            for cid, c, inv in lst:
                self.map[(key, res['h'], res['nu'], R, cid)] = reg.classify(c, inv)

    def gid(self, key, h, nu, R, cid):
        return None if cid is None else self.map[(key, h, nu, R, cid)]


def law_key(lawd):
    return (lawd['ration'], lawd['treatment'], lawd['take'], lawd['choice'], lawd['knot_law'])


def run_jobs(label, jobs, procs, outname):
    rec_out = common.JsonLines(outname + '_runs.jsonl.gz')
    pair_out = common.JsonLines(outname + '_pairs.jsonl.gz')
    hand_out = common.JsonLines(outname + '_handed.jsonl.gz')
    merge = Merge()
    index = []
    t0 = time.time()
    done = 0
    with mp.Pool(procs, initializer=_init) as pool:
        for res in pool.imap(job, jobs, chunksize=1):
            key = law_key(res['law'])
            merge.add(key, res)
            for rec in res['recs']:
                rec['global_class'] = {R: merge.gid(key, res['h'], res['nu'], R, rec['local_class'][R])
                                       for R in PREFIXES}
                rec_out.write(rec)
                index.append({'key': key, 'h': rec['h'], 'nu': rec['nu'], 'a': rec['a'], 'usable': rec['usable'],
                              'rounds_read': rec['rounds_read'], 'stop': rec['stop'],
                              'guard': rec['guard'] and rec['guard']['what'], 'gc': rec['global_class'],
                              'meet': rec['meet_round'], 'meet_how': rec['meet_how'],
                              'link': [(x['class'], x['is_X_start'], x['is_Y_start'], x['holds_e'])
                                       for x in rec['linking'] or []],
                              's4': rec['s4'], 'short': rec['short_after1'], 'implied': rec['implied_rounds'],
                              'kt': rec['knot_test'], 'fp': rec['fingerprint'], 'sec': rec['seconds'],
                              'knots': rec['knots']})
            for p in res['pairs']:
                p['key'] = key
                pair_out.write(p)
            if res['handed'] is not None:
                hand_out.write({'key': key, 'h': res['h'], 'nu': res['nu'], 'handed': res['handed']})
            done += 1
            if done % 50 == 0 or done == len(jobs):
                log(label, 'jobs', done, '/', len(jobs), 'elapsed %.0fs' % (time.time() - t0))
    rec_out.close()
    pair_out.close()
    hand_out.close()
    common.write_json(outname + '_index.json.gz', index)
    vf2 = {repr(k): {'classes': r.n, 'vf2_calls': r.vf2_calls} for k, r in merge.reg.items()}
    common.write_json(outname + '_classes.json', vf2)
    return time.time() - t0


def jobs_class(label, hs, order, treatment='CANCEL-RETIRE', ration='ORD', take='MET', do_pairs=True):
    jobs = []
    for choice, kl in order:
        for h in hs:
            for nu, stars, entries in common.class_by_nu(h):
                lawd = {'ration': ration, 'treatment': treatment, 'take': take, 'choice': choice, 'knot_law': kl}
                jobs.append((label, h, nu, stars, entries, lawd, do_pairs))
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('which', choices=('N', 'P', '1', '1r', '1b', '2'))
    ap.add_argument('--procs', type=int, default=4)
    ap.add_argument('--time-only', type=int, default=0)
    a = ap.parse_args()
    common.check_frozen()
    common.cap_memory(6)
    if a.which == '1':
        jobs = jobs_class('1', (3, 4), ORDER_1)
        assert sum(len(j[4]) for j in jobs) == 17280
        if a.time_only:
            # a small part of run 1, timed (not a registered output): the first jobs of each block
            sel = []
            for blk in range(4):
                b = [j for j in jobs if (j[5]['choice'], j[5]['knot_law']) == ORDER_1[blk]]
                sel += [j for j in b if j[1] == 3][:a.time_only] + [j for j in b if j[1] == 4][:a.time_only]
            t0 = time.time()
            with mp.Pool(a.procs, initializer=_init) as pool:
                out = pool.map(job, sel, chunksize=1)
            for r in out:
                log('time', r['h'], r['law']['choice'], r['law']['knot_law'], r['seconds'], 's for', len(r['recs']),
                    'runs; max run %.2fs' % max(x['seconds'] for x in r['recs']))
            log('timed part: %.1fs wall for %d runs' % (time.time() - t0, sum(len(r['recs']) for r in out)))
            return
        secs = run_jobs('1', jobs, a.procs, 'run1')
    elif a.which == '1r':
        # run 1 resumed after its cut, for take-the-newest under parity only (deviations 32): the same jobs, in
        # the registered order (h = 3 then h = 4, numberings in list order), written as the second part of run 1
        jobs = jobs_class('1', (3, 4), (('NEWEST', 'parity'),))
        assert sum(len(j[4]) for j in jobs) == 4320
        secs = run_jobs('1', jobs, a.procs, 'run1r')
    elif a.which == '1b':
        jobs = []
        for tr in ('CANCEL-OFFSHOOT', 'CANCEL-WAIT'):
            jobs += jobs_class('1b', (3,), ORDER_1, treatment=tr)
        assert sum(len(j[4]) for j in jobs) == 7680
        secs = run_jobs('1b', jobs, a.procs, 'run1b')
    elif a.which == 'N':
        jobs = []
        for kl in ('nae', 'parity'):
            for nu, stars, entries in common.class_by_nu(3):
                jobs.append(('N', 3, nu, stars, entries,
                             {'ration': 'ORD', 'treatment': 'CANCEL-RETIRE', 'take': None, 'choice': 'OLDEST',
                              'knot_law': kl}, False))
            Nn = common.numberings()
            ent = [(aa, sorted(Nn['class_h_by_a']['made-4|a=%d' % aa][0]['usable'])) for aa in range(5)]
            st = [Nn['class_h_by_a']['made-4|a=%d' % aa][0]['stars'] for aa in range(5)]
            assert all(s == st[0] for s in st)
            jobs.append(('N', 4, 0, st[0], ent, {'ration': 'ORD', 'treatment': 'CANCEL-RETIRE', 'take': None,
                                                 'choice': 'OLDEST', 'knot_law': kl}, False))
        assert sum(len(j[4]) for j in jobs) == 1930
        secs = run_jobs('N', jobs, a.procs, 'runN')
    elif a.which in ('P', '2'):
        secs = pair_starts(a.which)
    log('run', a.which, 'wall %.1fs' % secs)


# ---------------------------------------------------------------------------- P and 2: made-5 against made-6
def pair_starts(which):
    import json
    t0 = time.time()
    reg = common.numberings()['registered']
    out = {'runs': [], 'comparisons': []}
    if which == 'P':
        laws = [('CAP-3', 'EVERY', kl) for kl in ('nae', 'parity')]
        cells = lambda h: list(range(h + 1))
    else:
        laws = [('ORD', ch, kl) for ch in ('OLDEST', 'NEWEST') for kl in ('nae', 'parity')]
        cells = lambda h: [h]
    for ration, ch, kl in laws:
        law = wbc.Law(ration, 'CANCEL-RETIRE', 'MET', ch, kl)
        runs = {}
        for h in (5, 6):
            stars = reg['made-%d' % h]
            for a in cells(h):
                usable = list(range(3, 3 + a))
                t1 = time.time()
                r = wbc.RunState(stars, usable, law)
                kt = wbc.knot_test(r)
                rec = run_record(r, which, h, 'registered', a, kt, time.time() - t1)
                out['runs'].append(rec)
                runs[(h, a)] = (r, rec)
        aa = 0 if which == 'P' else None
        r5, c5 = runs[(5, 0 if which == 'P' else 5)]
        r6, c6 = runs[(6, 0 if which == 'P' else 6)]
        last = min(r5.rounds_read, r6.rounds_read)
        ce = {}
        for R in PREFIXES:
            if R <= last:
                ce[R] = wbc.same_course(c5['courses'][R], c6['courses'][R])
        fd = wbc.compare_values(r5, r6, last)
        # P's criterion (RD 5.2): the course first differs at round 3; the first differing entry is X's round-3
        # joins' candidates; the extra candidate supplied by Y's start knot; class a third part (a start knot)
        crit = None
        if which == 'P':
            first_course_diff = min([R for R, v in ce.items() if not v], default=None)
            joins3 = fd is not None and fd['round'] == 3 and fd['kind'] == 'candidates'
            is_join = False
            sup_y = False
            if joins3:
                bk = fd['pos'][1]
                kn = [u for u in range(r5.S.n_knots) if r5.kkey[u] == bk]
                is_join = bool(kn) and r5.S.kind[kn[0]] == 'join' and r5.S.made[kn[0]] == 3
                sup_y = bool(fd['part']) and all(x[0] == r5.kkey[r5.ys] for x in fd['part'])
            crit = {'first_course_difference_round': first_course_diff, 'first_values_round': fd and fd['round'],
                    'entry_is_round3_join_candidates': joins3 and is_join, 'supplied_by_Y_start_knot': sup_y,
                    'class': fd and fd['class'],
                    'passes': first_course_diff == 3 and joins3 and is_join and sup_y and
                    fd['class'] == 'a third part (a start knot)'}
            # the candidate counts of X's round-3 joins in both runs
            for nm, r in (('made-5', r5), ('made-6', r6)):
                rec3 = [x for x in r.recs if x['round'] == 3]
                if rec3:
                    xj = [b for b in rec3[0]['births'] if b['kind'] == 'join' and
                          all(r.desc(p) == 'X only' for p in b['parents'])]
                    crit['x_round3_joins_takes_' + nm] = [len(b['takes']) for b in xj]
        out['comparisons'].append({'law': law.name(), 'rounds_compared': last, 'course_equal': ce, 'fd': fd,
                                   'criterion': crit})
        log(which, law.name(), 'course equal', ce, 'first difference', fd and (fd['round'], fd['kind'],
                                                                            fd['class']), crit)
    for rec in out['runs']:
        rec['courses_inv'] = {R: wbc.course_invariant(c) for R, c in rec['courses'].items()}
    common.write_json('run%s.json.gz' % which, out)
    return time.time() - t0


if __name__ == '__main__':
    main()
