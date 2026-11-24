"""Run 2: the two small starts under the nine laws, 12 rounds.  The parity knot test by both methods for every knot
at rounds 0 to 12 and the extension test for every round; the fresh count of every birth and the closing flag; the
roster under FLOOR1 and ONE-FEWER compared with FLOOR0 at every round (deviations.md C4).  Under not-all-equal: the
births compared with parity at every round (A-D19) and the not-all-equal test for every knot at round 0 and after every
round r <= 10 while the structure has at most 600 knots (C5).  Evidence for P4 and P5.  Writes run2.json."""
import time

from cpcommon import E, SMALL_STARTS, TREATMENTS3, log, nine_laws, resources, write

R = 12
NAE_R = 10
NAE_CAP = 600


class ParityHook:
    def __init__(self):
        self.rows = []

    def __call__(self, S, r, rec, before):
        res = E.parity_knot_test(S)
        row = {'round': r, 'n_knots': S.n_knots, 'rank_fail': res['rank_fail'], 'cut_fail': res['cut_fail'],
               'disagree': res['disagree'], 'all_pass': res['all_pass']}
        if r >= 1:
            ext = E.extension_test_parity(before, S)
            row['extends'] = ext['extends']
            row['ext_dims'] = [ext['dim_before'], ext['dim_restricted']]
            row['closing'] = rec['closing']
        self.rows.append(row)


class NaeHook:
    def __init__(self):
        self.rows = []
        self.skipped = []
        self.seconds = 0.0

    def __call__(self, S, r, rec, before):
        if r > NAE_R:
            return
        if S.n_knots > NAE_CAP:
            self.skipped.append({'round': r, 'n_knots': S.n_knots})
            return
        t0 = time.time()
        res = E.nae_knot_test(S)
        self.seconds += time.time() - t0
        self.rows.append({'round': r, 'n_knots': S.n_knots, 'fail': res['fail'], 'sat_calls': res['sat_calls']})


def comparable(rec):
    return {'groups': rec['groups'], 'short': rec['short'], 'cancelled': rec['cancelled'],
            'waiting': rec['waiting'], 'retired': rec['retired'], 'closing': rec['closing'],
            'births': [(b['id'], tuple(b['parents']), tuple(b['taken']), b['kind'], b['D'], b['f'], b['usable'],
                        b['barred']) for b in rec['births']]}


def identical_roster(r1, r2):
    return (r1.members == r2.members and all(r1.h[u] == r2.h[u] and r1.k[u] == r2.k[u] for u in r1.members)
            and set(r1.maxsets) == set(r2.maxsets))


def same_roster(run1, t1, run2, t2):
    """deviations.md C4: the definitions' sameness.  The identity renaming is tried first (an exact sufficient test,
    as in ticket B's B13); otherwise the engine's exact test (invariants, then VF2)."""
    a, b = run1.rosters[t1], run2.rosters[t2]
    if identical_roster(a, b):
        return True, 'identity'
    return run1.cache.same(a, None, b, None), 'engine'


def main():
    out = {'R': R, 'runs': {}, 'P4': {}, 'P5': {}}
    for sname, mk in SMALL_STARTS:
        runs = {}
        for law in nine_laws():
            key = '%s|%s' % (sname, law.name())
            ph = ParityHook()
            run = E.Run(mk(), law, R, hook=ph, hook_needs_before=True)
            nh = NaeHook()
            nrun = E.Run(mk(), law.replace(knot_law='nae'), R, hook=nh)
            per_round = [comparable(a) == comparable(b) for a, b in zip(nrun.records, run.records)]
            fresh = [b['f'] for rec in run.records for b in rec['births']]
            zero_f = [{'round': rec['round'], 'id': b['id'], 'parents': b['parents'], 'D': b['D']}
                      for rec in run.records for b in rec['births'] if b['f'] == 0]
            v = {'start': sname, 'law': law.to_dict(), 'rounds_done': run.rounds_done, 'knots': run.S.n_knots,
                 'kind': run.kind(),
                 'parity_rows': [{k: r[k] for k in r if k not in ('rank_fail', 'cut_fail', 'disagree')} |
                                 {'n_rank_fail': len(r['rank_fail']), 'n_cut_fail': len(r['cut_fail']),
                                  'n_disagree': len(r['disagree']), 'rank_fail': r['rank_fail'][:20],
                                  'cut_fail': r['cut_fail'][:20]} for r in ph.rows],
                 'all_knots_pass': all(r['all_pass'] for r in ph.rows),
                 'methods_agree': all(not r['disagree'] for r in ph.rows),
                 'all_rounds_extend': all(r.get('extends', True) for r in ph.rows),
                 'closing_ever': any(r.get('closing', False) for r in ph.rows),
                 'n_births': len(fresh), 'min_fresh': min(fresh) if fresh else None, 'zero_fresh_births': zero_f,
                 'max_parents': max((len(b['parents']) for rec in run.records for b in rec['births']), default=0),
                 'max_D': max((b['D'] for rec in run.records for b in rec['births']), default=0),
                 'nae': {'births_equal_every_round': all(per_round) and len(nrun.records) == len(run.records),
                         'first_unequal_round': next((i + 1 for i, x in enumerate(per_round) if not x), None),
                         'closing_ever_nae': any(rec['closing'] for rec in nrun.records),
                         'rows': [{'round': r['round'], 'n_knots': r['n_knots'], 'n_fail': len(r['fail']),
                                   'fail': r['fail'][:20], 'sat_calls': r['sat_calls']} for r in nh.rows],
                         'rounds_tested': [r['round'] for r in nh.rows], 'rounds_skipped_past_600': nh.skipped,
                         'all_pass': all(not r['fail'] for r in nh.rows),
                         'knots_checked': sum(r['n_knots'] for r in nh.rows),
                         'sat_calls': sum(r['sat_calls'] for r in nh.rows), 'seconds': round(nh.seconds, 1)}}
            runs[law.name()] = run
            out['runs'][key] = v
            log(key, 'knots', run.S.n_knots, 'parity pass', v['all_knots_pass'], 'agree', v['methods_agree'],
                'extend', v['all_rounds_extend'], 'closing', v['closing_ever'], 'min f', v['min_fresh'],
                '| NAE births equal', v['nae']['births_equal_every_round'], 'NAE pass', v['nae']['all_pass'],
                'rounds', v['nae']['rounds_tested'], 'knots', v['nae']['knots_checked'])
        # P4: FLOOR1 and ONE-FEWER against FLOOR0, same treatment, every round
        for tr in TREATMENTS3:
            base = runs[E.Law('FLOOR0', tr).name()]
            for ration in ('FLOOR1', 'ONE-FEWER'):
                other = runs[E.Law(ration, tr).name()]
                rows = []
                for t in range(R + 1):
                    ok, how = same_roster(base, t, other, t)
                    rows.append({'round': t, 'same': ok, 'how': how})
                rec_equal = all(comparable(a) == comparable(b) for a, b in zip(base.records, other.records))
                out['P4']['%s|%s vs FLOOR0|%s' % (sname, ration, tr)] = {
                    'same_roster_every_round': all(r['same'] for r in rows),
                    'decided_by': sorted({r['how'] for r in rows}), 'records_identical': rec_equal,
                    'rows_not_same': [r for r in rows if not r['same']]}
    p4 = out['P4']
    rr = out['runs']
    out['P4_verdict'] = {
        'same_roster': all(v['same_roster_every_round'] for v in p4.values()),
        'every_birth_fresh': all(v['min_fresh'] is not None and v['min_fresh'] >= 1 for v in rr.values()),
        'all_knots_pass_both_methods': all(v['all_knots_pass'] and v['methods_agree'] for v in rr.values()),
        'every_round_extends': all(v['all_rounds_extend'] for v in rr.values()),
        'closing_never': not any(v['closing_ever'] for v in rr.values())}
    out['P4_verdict']['pass'] = all(out['P4_verdict'].values())
    out['P5_verdict'] = {
        'births_equal': all(v['nae']['births_equal_every_round'] for v in rr.values()),
        'nae_all_pass': all(v['nae']['all_pass'] for v in rr.values()),
        'nae_knots_checked': sum(v['nae']['knots_checked'] for v in rr.values()),
        'nae_sat_calls': sum(v['nae']['sat_calls'] for v in rr.values())}
    out['P5_verdict']['pass'] = out['P5_verdict']['births_equal'] and out['P5_verdict']['nae_all_pass']
    out['resources'] = resources()
    log('P4', out['P4_verdict'])
    log('P5', out['P5_verdict'])
    write('run2.json', out)


if __name__ == '__main__':
    main()
