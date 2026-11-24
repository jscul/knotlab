"""Run 5: every start of up to five knots of the earlier census (3,376 starts), those passing the parity knot test at
round 0, under FLOOR0 and FLOOR1 with each of CANCEL-RETIRE, CANCEL-OFFSHOOT, CANCEL-WAIT; 10 rounds, cut off past
1,500 knots (A-D9).  Per start and law: whether a part copies itself (deviations.md C7) and the smallest such part,
and whether any knot fails the parity knot test (both methods) at any round, with the first such round (C12).

  run5.py --check     the enumeration against 19 / 200 / 3,157 and against the earlier census's records
  run5.py --measure K time K starts of five knots spread over the census (no outcome printed)
  run5.py             the full run on 8 processes: run5.json (tables) and run5_starts.json.gz (one record per start)
"""
import argparse
import multiprocessing as mp
import time
from collections import Counter, defaultdict

from cpcensus import earlier_census, stars, starts
import resource

from cpcommon import E, copy_returns, is_two_knot_part, log, resources, write

R = 10
CAP = 1500
LAWS = [('FLOOR0', 'CANCEL-RETIRE'), ('FLOOR0', 'CANCEL-OFFSHOOT'), ('FLOOR0', 'CANCEL-WAIT'),
        ('FLOOR1', 'CANCEL-RETIRE'), ('FLOOR1', 'CANCEL-OFFSHOOT'), ('FLOOR1', 'CANCEL-WAIT')]
EXPECTED = {3: 19, 4: 200, 5: 3157}
EXPECTED_SET_ASIDE = {3: 0, 4: 3, 5: 29}
WORKERS = 8


class FirstFailHook:
    """The parity knot test (both methods) after every round from 1 until the first round with a failing knot."""

    def __init__(self):
        self.first = None
        self.n_fail = 0
        self.fail_knots = []
        self.disagree = []
        self.rounds_tested = 0
        self.zero_fresh_in_fail_round = None

    def __call__(self, S, r, rec, before):
        if r == 0 or self.first is not None:
            return
        self.rounds_tested += 1
        res = E.parity_knot_test(S)
        if res['disagree']:
            self.disagree.append({'round': r, 'knots': res['disagree'][:10]})
        failing = sorted(set(res['rank_fail']) | set(res['cut_fail']))
        if failing:
            self.first = r
            self.zero_fresh_in_fail_round = any(b['f'] == 0 for b in rec['births'])
            self.n_fail = len(failing)
            self.fail_knots = [{'id': u, 'made': S.made[u], 'p': len(S.parents[u]), 'fresh': len(S.fresh[u])}
                               for u in failing[:6]]


def one_start(item):
    n, idx, g, loose = item
    t0 = time.time()
    S = E.from_stars(stars(g, loose))
    par = E.parity_knot_test(S)
    rec = {'n': n, 'i': idx, 'g': g, 'loose': loose, 'dead': loose.count(0), 'members': n - loose.count(0),
           'set_aside': not par['all_pass'], 'kt0': {'rank_fail': par['rank_fail'], 'cut_fail': par['cut_fail'],
                                                    'disagree': par['disagree']}}
    if rec['set_aside']:
        rec['sec'] = round(time.time() - t0, 3)
        return rec
    laws = {}
    for ration, tr in LAWS:
        hk = FirstFailHook()
        run = E.Run(S, E.Law(ration, tr), R, knot_cap=CAP, hook=hk)
        knots = [S.n_knots] + [r['n_knots'] for r in run.records]
        Rb = max(t for t, k in enumerate(knots) if k <= CAP)
        crs = copy_returns(run)
        crs_b = [r for r in crs if r['t'] <= Rb]
        first = min(crs, key=lambda r: (len(r['part']), r['s'], r['t'])) if crs else None
        laws['%s|%s' % (ration, tr)] = {
            'kind': run.kind(), 'rounds': run.rounds_done, 'cut': run.cut_off, 'knots': run.S.n_knots, 'Rb': Rb,
            'copy': bool(crs), 'copy_min': (len(first['part']) if first else None),
            'copy_min_at': ([first['s'], first['t'], first['period']] if first else None),
            'copy_sizes': sorted({len(r['part']) for r in crs}),
            'copy_two_knot': any(is_two_knot_part(run.rosters[r['s']], run.rosters[r['s']].parts.index(tuple(r['part'])))
                                 for r in crs),
            'copy_b': bool(crs_b), 'copy_min_b': (min(len(r['part']) for r in crs_b) if crs_b else None),
            'kt_first_fail': hk.first, 'kt_first_fail_b': (hk.first if hk.first is not None and hk.first <= Rb
                                                           else None),
            'kt_n_fail': hk.n_fail, 'kt_zero_fresh_in_fail_round': hk.zero_fresh_in_fail_round, 'kt_fail_knots': hk.fail_knots, 'kt_disagree': hk.disagree,
            'kt_rounds_tested': hk.rounds_tested, 'mixed': len(getattr(run, 'mixed_parts', []))}
    rec['laws'] = laws
    rec['sec'] = round(time.time() - t0, 3)
    return rec


def all_items():
    items = []
    for n in (3, 4, 5):
        for i, (g, loose) in enumerate(starts(n)):
            items.append((n, i, g, loose))
    return items


def check():
    out = {'by_n': {}}
    mine = {n: starts(n) for n in (3, 4, 5)}
    earlier = earlier_census((3, 4, 5))
    for n in (3, 4, 5):
        m = mine[n]
        e = earlier[n]
        same_list = [(g, list(lo)) for g, lo in m] == [(g, lo) for g, lo, _ in e]
        set_aside_mine = []
        for g, lo in m:
            S = E.from_stars(stars(g, lo))
            if not E.parity_knot_test(S)['all_pass']:
                set_aside_mine.append([g, lo])
        set_aside_earlier = [[g, lo] for g, lo, sa in e if sa]
        out['by_n'][str(n)] = {'starts': len(m), 'expected': EXPECTED[n], 'count_ok': len(m) == EXPECTED[n],
                               'earlier_records': len(e), 'same_identities_and_order': same_list,
                               'set_aside': len(set_aside_mine), 'set_aside_expected': EXPECTED_SET_ASIDE[n],
                               'set_aside_same_as_earlier': set_aside_mine == set_aside_earlier,
                               'set_aside_list': set_aside_mine}
        log('n = %d: %d starts (expected %d), same as earlier census: %s; set aside %d (expected %d), same ones: %s'
            % (n, len(m), EXPECTED[n], same_list, len(set_aside_mine), EXPECTED_SET_ASIDE[n],
               set_aside_mine == set_aside_earlier))
    out['total'] = sum(len(mine[n]) for n in (3, 4, 5))
    out['ok'] = all(v['count_ok'] and v['same_identities_and_order'] and v['set_aside_same_as_earlier'] and
                    v['set_aside'] == v['set_aside_expected'] for v in out['by_n'].values()) and out['total'] == 3376
    out['resources'] = resources()
    write('run5_census_check.json', out)
    return out


def tables(recs):
    """Counts by law; by law and number of knots; by law and number of dead knots; by law, knots and dead knots."""
    T = {}
    for ration, tr in LAWS:
        key = '%s|%s' % (ration, tr)
        rows = defaultdict(Counter)
        for r in recs:
            if r['set_aside']:
                continue
            v = r['laws'][key]
            for dim in ('all', 'n=%d' % r['n'], 'dead=%d' % r['dead'], 'n=%d,dead=%d' % (r['n'], r['dead'])):
                c = rows[dim]
                c['starts'] += 1
                c['copy'] += int(v['copy'])
                c['copy_two_knot'] += int(v['copy_two_knot'])
                c['kt_fail'] += int(v['kt_first_fail'] is not None)
                c['copy_and_kt_fail'] += int(v['copy'] and v['kt_first_fail'] is not None)
                c['copy_b'] += int(v['copy_b'])
                c['kt_fail_b'] += int(v['kt_first_fail_b'] is not None)
                c['cut_off'] += int(v['cut'])
        T[key] = {dim: dict(c) for dim, c in sorted(rows.items())}
    return T


def extra_tables(recs):
    out = {}
    for ration, tr in LAWS:
        key = '%s|%s' % (ration, tr)
        vs = [r['laws'][key] for r in recs if not r['set_aside']]
        out[key] = {
            'kinds': dict(Counter(v['kind'] for v in vs)),
            'smallest_copy_size': dict(sorted(Counter(str(v['copy_min']) for v in vs if v['copy']).items())),
            'first_fail_round': dict(sorted(Counter(str(v['kt_first_fail']) for v in vs
                                                    if v['kt_first_fail'] is not None).items())),
            'failing_knot_kinds_at_first_fail': dict(sorted(Counter(
                'p=%d,fresh=%d' % (k['p'], k['fresh']) for v in vs for k in v['kt_fail_knots']).items())),
            'methods_disagree_runs': sum(1 for v in vs if v['kt_disagree']),
            'failing_runs_with_zero_fresh_birth_in_first_fail_round': sum(
                1 for v in vs if v['kt_first_fail'] is not None and v['kt_zero_fresh_in_fail_round']),
            'failing_runs': sum(1 for v in vs if v['kt_first_fail'] is not None),
            'copying_runs_where_no_two_knot_part_copies': sum(1 for v in vs if v['copy'] and not v['copy_two_knot']),
            'failing_knots_are_start_knots_at_first_fail': sum(1 for v in vs for k in v['kt_fail_knots']
                                                                if k['p'] == 0),
            'mixed_parts_runs': sum(1 for v in vs if v['mixed']),
            'cut_off_runs': sum(1 for v in vs if v['cut'])}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--measure', type=int, default=0)
    a = ap.parse_args()
    if a.check:
        check()
        return
    items = all_items()
    if a.measure:
        five = [it for it in items if it[0] == 5]
        step = max(1, len(five) // a.measure)
        sample = five[::step][:a.measure]
        t0 = time.time()
        secs = []
        for it in sample:
            rec = one_start(it)
            secs.append(rec['sec'])
        tot = time.time() - t0
        n3 = sum(1 for it in items if it[0] == 3)
        n4 = sum(1 for it in items if it[0] == 4)
        mean = tot / len(sample)
        log('measured %d five-knot starts in %.1f s: %.3f s per start (max %.2f s)' % (len(sample), tot, mean,
                                                                                        max(secs)))
        log('projection for %d starts on %d processes: about %.0f s (five-knot rate used for all)' % (
            len(items), WORKERS, mean * len(items) / WORKERS))
        return
    chk = check()
    if not chk['ok']:
        raise SystemExit('census check failed')
    t0 = time.time()
    with mp.get_context('fork').Pool(WORKERS) as pool:
        recs = list(pool.imap(one_start, items, chunksize=4))
    wall = time.time() - t0
    recs.sort(key=lambda r: (r['n'], r['i']))
    out = {'R': R, 'cap': CAP, 'laws': ['%s|%s' % x for x in LAWS], 'n_starts': len(recs),
           'n_set_aside': sum(r['set_aside'] for r in recs),
           'set_aside_by_n': dict(Counter(str(r['n']) for r in recs if r['set_aside'])),
           'n_run': sum(not r['set_aside'] for r in recs),
           'tables': tables(recs), 'extra': extra_tables(recs),
           'slowest_starts': sorted(([r['n'], r['g'], r['loose'], r['sec']] for r in recs),
                                    key=lambda x: -x[3])[:10],
           'wall_seconds': round(wall, 1), 'workers': WORKERS, 'cpu_seconds_sum_of_starts': round(sum(r['sec'] for r in
                                                                                                    recs), 1)}
    out['resources'] = resources()
    out['resources']['peak_rss_mb_largest_worker'] = round(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
                                                           / 1024.0, 1)
    write('run5.json', out)
    write('run5_starts.json', {'starts': [{k: v for k, v in r.items() if k != 'sec'} for r in recs]}, gz=True)
    log('wall %.1f s' % wall)


if __name__ == '__main__':
    main()
