"""Runs 5, 5b and 6: the numberings (TD 5.4) and the swaps of every case of run 4.

  cases   the cases of run 4 (first and second pass): (law, start) with a test in which C-iii holds or C holds before
          the knot test and the numberings; written to cases.json
  run5    every case under every registered numbering of its start (every numbering for a start of at most six
          distinctions; the 4n shifts otherwise), run 4's readings; whether the case survives each (some (Y', X') in
          the renamed run meets the same sense)
  run5b   a case that passes all 4n: the 200 numberings of numberings_5b.json
  run6    every case with each swap: names reversed; order of births reversed; demand before the takes; fresh by
          parents; HOLD; the ration (FLOOR1 against CAP-3); the knot law
  near    supplement (not a case under TD 2.5): the first draft's near case on the two-knot start (Y a one-member
          series) under every numbering, for the comparison with compare.json
Usage: python -B tf_run5.py cases|run5|run5b|run6|near [--procs 6]
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import multiprocessing as mp
import time
from collections import Counter

import tf_common as C
import tf_engine as E
import tf_run4 as R4
import tf_runs as RN
import tf_series as Se
import tf_tests as Tt


# ------------------------------------------------------------------------------------------------------- numberings
def labels_of(stars):
    return sorted({d for s in stars for d in s})


def registered_numberings(stars):
    """TD 5.4: every numbering of a start of at most six distinctions; otherwise the 4n numberings made of the n shifts
    of the order of distinctions, each with the distinctions as given or reversed and the knots as given or reversed."""
    labs = labels_of(stars)
    n = len(labs)
    m = len(stars)
    out = []
    if n <= 6:
        for d in itertools.permutations(labs):
            for k in itertools.permutations(range(m)):
                out.append({'dist': list(d), 'knots': list(k), 'kind': 'every'})
        return out
    for i in range(n):
        sh = labs[i:] + labs[:i]
        for drev in (False, True):
            for krev in (False, True):
                out.append({'dist': list(reversed(sh)) if drev else sh,
                            'knots': list(reversed(range(m))) if krev else list(range(m)),
                            'kind': 'shift %d%s%s' % (i, ' distinctions reversed' if drev else '',
                                                      ' knots reversed' if krev else '')})
    return out


def named_start(stars, num):
    """The start as named by a numbering: its knots in order, each the set of its distinctions' names."""
    name = {lab: i for i, lab in enumerate(num['dist'])}
    return tuple(tuple(sorted(name[d] for d in stars[si])) for si in num['knots'])


def canon_up_to_symmetry(stars, num):
    """The named start up to the start's own symmetries: the set of named knots with their knot name (the names of
    distinctions and knots are what the rules use, so two numberings give the same run exactly when they give the
    same named start)."""
    return named_start(stars, num)


def name_condition(stars, num):
    """For the two-knot start: whether the shared start distinction is the least-named place of each start knot."""
    name = {lab: i for i, lab in enumerate(num['dist'])}
    shared = [d for d in labels_of(stars) if sum(d in s for s in stars) >= 2]
    out = []
    for si in num['knots']:
        pl = [name[d] for d in stars[si]]
        out.append(all(name[d] == min(pl) for d in shared if d in stars[si]))
    return out


# --------------------------------------------------------------------------------------------------------- one run
def numbered_job(arg):
    case, num, sense, include_one_member = arg[:4]
    every_clock = len(arg) > 4 and arg[4]
    it = case['item']
    stars = RN.stars_of(it['start'])
    t0 = time.process_time()
    clock = E.Clock(600)
    out = {'case': case['id'], 'numbering': num, 'named_start': canon_up_to_symmetry(stars, num),
           'swap': case.get('swap'), 'sense': sense, 'item': it}
    if len(labels_of(stars)) <= 6:
        out['shared_least_in_knot'] = name_condition(stars, num)
    try:
        law = RN.law_of(it) if 'law' not in case else E.Law(**case['law'])
        rounds, kb = RN.bounds_of(it)
        S0 = E.from_stars(stars, dist_order=num['dist'], knot_order=num['knots'])
        A = E.Run(S0, law, rounds=rounds, knot_bound=kb, clock=clock)
        if A.stop == 'limit':
            out['unfinished'] = 'run A'
            return out
        ser, _ = Se.build_series(A, False, clock=clock)
        Se.describe(ser)
    except E.LimitReached:
        out['unfinished'] = 'run A'
        return out
    comps = Tt.Comparisons(A, law, rounds, kb)
    if include_one_member:
        cl = [s for s in ser if s['size'] == 1 and Se.equal_stretches(s['periods'])]
        groups = {}
        for s in cl:
            key = (tuple(sorted(set(s['periods']))), s['t0'] % 2)
            if key not in groups or s['P0'][0] < groups[key]['P0'][0]:
                groups[key] = s
        clocks = list(groups.values())
    elif every_clock:
        clocks = [s for s in ser if s['clock']]                      # dev 42: every clock of the renamed run
    else:
        clocks = R4.chosen_clocks(ser)
    out['every_clock'] = bool(every_clock)
    tests = []
    for s in clocks:
        for j in (0, 1):
            try:
                tests += Tt.run_tests(A, law, s, j, comps)
            except E.LimitReached:
                tests.append({'unfinished': True})
    out['tests'] = len(tests)
    out['C_iii_holds'] = sum(1 for t in tests if t.get('verdict_C_iii') == 'holds')
    out['C_holds'] = sum(1 for t in tests if str(t.get('verdict_C', '')).startswith('holds'))
    out['undecided_C_iii'] = sum(1 for t in tests if t.get('verdict_C_iii') == 'undecided')
    out['unfinished_tests'] = sum(1 for t in tests if t.get('unfinished'))
    if sense == 'C-iii':
        out['survives'] = out['C_iii_holds'] > 0
    else:
        out['survives'] = out['C_holds'] > 0
    out['held_tests'] = [{k: t.get(k) for k in ('t0', 'Y_size', 'Y_periods', 'j', 't_j', 'P_j', 'X',
                                                 'own_A_per_period', 'verdict_C', 'verdict_C_iii')}
                         for t in tests if t.get('verdict_C_iii') == 'holds'][:6]
    out['sec'] = round(time.process_time() - t0, 2)
    return out


def _init():
    C.cap_memory()


# --------------------------------------------------------------------------------------------------------- the cases
def find_cases():
    rows = []
    for fn in ('run4.jsonl.gz', 'run4_second.jsonl.gz'):
        try:
            with gzip.open(C.out_path(fn), 'rt') as f:
                for line in f:
                    rows.append(json.loads(line))
        except FileNotFoundError:
            pass
    cases = {}
    for r in rows:
        held_iii = r.get('verdict_C_iii') == 'holds'
        held_c = str(r.get('verdict_C', '')).startswith('holds')
        if not (held_iii or held_c):
            continue
        it = R4.item_of(r)
        key = json.dumps(it, sort_keys=True)
        c = cases.setdefault(key, {'item': it, 'senses': set(), 'tests': 0})
        if held_iii:
            c['senses'].add('C-iii')
        if held_c:
            c['senses'].add('C')
        c['tests'] += 1
    out = []
    for i, (k, c) in enumerate(sorted(cases.items())):
        c['id'] = i
        c['senses'] = sorted(c['senses'])
        out.append(c)
    C.write_json('cases.json', out)
    C.log('cases: %d' % len(out))
    return out


def run_numbered(cases, procs, out_name, numberings_of, include_one_member=False):
    args = []
    for c in cases:
        stars = RN.stars_of(c['item']['start'])
        for num in numberings_of(c, stars):
            for sense in c['senses']:
                args.append((c, num, sense, include_one_member))
    C.log('%s: %d runs' % (out_name, len(args)))
    path = C.out_path(out_name)
    t0 = time.time()
    with gzip.open(path, 'wt') as f, mp.Pool(procs, initializer=_init, maxtasksperchild=20) as pool:
        for i, r in enumerate(pool.imap_unordered(numbered_job, args)):
            f.write(json.dumps(r, sort_keys=True, default=C._default) + '\n')
            if (i + 1) % 100 == 0 or i + 1 == len(args):
                C.log('%s: %d/%d, %.0f s wall' % (out_name, i + 1, len(args), time.time() - t0))
                f.flush()
    return path


def numberings_5b(c, stars):
    d = C.load_json(C.os.path.join(C.RESEARCH, 'numberings_5b.json'))
    for s in d['starts']:
        if s['name'] == c['item']['start']:
            return [{'dist': n[0], 'knots': n[1], 'kind': '5b %d' % i} for i, n in enumerate(s['numberings'])]
    return []


SWAPS = ('names reversed', 'order of births reversed', 'demand before the takes', 'fresh by parents', 'HOLD',
         'the ration', 'the knot law')


def swapped(c, swap):
    it = dict(c['item'])
    law = RN.law_of(it)
    d = law.to_dict()
    num = None
    stars = RN.stars_of(it['start'])
    if swap == 'names reversed':
        num = {'dist': list(reversed(labels_of(stars))), 'knots': list(range(len(stars))), 'kind': 'names reversed'}
    elif swap == 'order of births reversed':
        d['order_reversed'] = True
    elif swap == 'demand before the takes':
        d['demand_before_takes'] = True
    elif swap == 'fresh by parents':
        d['fresh_by_parents'] = True
    elif swap == 'HOLD':
        d['release'] = 'HOLD'
    elif swap == 'the ration':
        d['ration'] = 'CAP-3' if d['ration'] == 'FLOOR1' else 'FLOOR1'
    elif swap == 'the knot law':
        d['knot_law'] = 'parity' if d['knot_law'] == 'nae' else 'nae'
    if num is None:
        num = {'dist': labels_of(stars), 'knots': list(range(len(stars))), 'kind': 'as given'}
    return dict(c, law=d, swap=swap), num


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('what')
    ap.add_argument('--procs', type=int, default=6)
    ap.add_argument('--cases', default=None, help='comma-separated case ids (default every case)')
    a = ap.parse_args()
    C.cap_memory()
    if a.what == 'cases':
        find_cases()
        return
    cases = C.load_json(C.out_path('cases.json'))
    if a.cases:
        keep = {int(x) for x in a.cases.split(',')}
        cases = [c for c in cases if c['id'] in keep]
    if a.what == 'run5':
        run_numbered(cases, a.procs, 'run5.jsonl.gz', lambda c, stars: registered_numberings(stars))
    elif a.what == 'run5b':
        run_numbered(cases, a.procs, 'run5b.jsonl.gz', numberings_5b)
    elif a.what == 'near':
        near = [{'id': 'near-%s-%s' % (ch, kl), 'senses': ['C-iii'],
                 'item': {'group': 'main', 'start': 'two-knot', 'base': 'COPY-LAW(OFFSHOOT)', 'rule': 'STEPS-1',
                          'choice': ch, 'knot_law': kl}} for ch in ('OLDEST', 'IN-TURN') for kl in ('nae', 'parity')]
        run_numbered(near, a.procs, 'run5_near_case.jsonl.gz', lambda c, stars: registered_numberings(stars),
                     include_one_member=True)
    elif a.what == 'run5-every-clock':
        # dev 42: the numberings of the STEPS-2 cases that did not pass under run 5, every clock tested
        done = {}
        with gzip.open(C.out_path('run5.jsonl.gz'), 'rt') as f:
            for line in f:
                r = json.loads(line)
                done[(r['case'], json.dumps(r['numbering'], sort_keys=True))] = r
        args = []
        for c in cases:
            if c['item']['rule'] != 'STEPS-2':
                continue
            stars = RN.stars_of(c['item']['start'])
            for num in registered_numberings(stars):
                r = done.get((c['id'], json.dumps(num, sort_keys=True)))
                if r is not None and not r.get('survives'):
                    args.append((c, num, 'C-iii', False, True))
        C.log('run 5, every clock: %d runs' % len(args))
        path = C.out_path('run5_every_clock.jsonl.gz')
        t0 = time.time()
        with gzip.open(path, 'wt') as f, mp.Pool(a.procs, initializer=_init, maxtasksperchild=20) as pool:
            for i, r in enumerate(pool.imap_unordered(numbered_job, args)):
                f.write(json.dumps(r, sort_keys=True, default=C._default) + '\n')
                if (i + 1) % 100 == 0 or i + 1 == len(args):
                    C.log('every clock: %d/%d, %.0f s wall' % (i + 1, len(args), time.time() - t0))
                    f.flush()
    elif a.what in ('run6', 'run6-every-clock'):
        ev = a.what == 'run6-every-clock'
        args = []
        for c in cases:
            for sw in SWAPS:
                cc, num = swapped(c, sw)
                for sense in c['senses']:
                    args.append((cc, num, sense, False, ev))
        C.log('%s: %d runs' % (a.what, len(args)))
        path = C.out_path('run6.jsonl.gz' if not ev else 'run6_every_clock.jsonl.gz')
        with gzip.open(path, 'wt') as f, mp.Pool(a.procs, initializer=_init, maxtasksperchild=20) as pool:
            for i, r in enumerate(pool.imap_unordered(numbered_job, args)):
                f.write(json.dumps(r, sort_keys=True, default=C._default) + '\n')


if __name__ == '__main__':
    main()
