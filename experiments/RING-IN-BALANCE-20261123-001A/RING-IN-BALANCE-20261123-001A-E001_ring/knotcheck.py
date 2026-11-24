"""A hook that runs the parity knot test (both methods) and the extension test after each round of a run."""
import time

from common import E


class ParityChecker:
    def __init__(self, last_round):
        self.last_round = last_round
        self.rows = []
        self.seconds = 0.0

    def __call__(self, S, r, rec, before):
        if r > self.last_round:
            return
        t0 = time.time()
        res = E.parity_knot_test(S)
        row = {'round': r, 'n_knots': S.n_knots, 'rank_H': res['rank_H'],
               'n_rank_fail': len(res['rank_fail']), 'n_cut_fail': len(res['cut_fail']),
               'n_disagree': len(res['disagree']), 'rank_fail': res['rank_fail'][:20],
               'cut_fail': res['cut_fail'][:20], 'disagree': res['disagree'][:20],
               'all_pass': res['all_pass']}
        if res['rank_fail']:
            # which kind of knot fails: made in which round, how many fresh
            row['failing_knots'] = [{'id': u, 'made': S.made[u], 'parents': len(S.parents[u]),
                                     'fresh': len(S.fresh[u]), 'places': len(S.places[u])}
                                    for u in res['rank_fail'][:10]]
        if r >= 1:
            if before is None:
                raise AssertionError('extension test needs the structure before the round')
            ext = E.extension_test_parity(before, S)
            row['extends'] = ext['extends']
            row['ext_dims'] = [ext['dim_before'], ext['dim_restricted']]
            row['closing'] = rec['closing']
        self.seconds += time.time() - t0
        self.rows.append(row)

    def summary(self):
        return {'rounds_checked': [r['round'] for r in self.rows],
                'all_knots_pass': all(r['all_pass'] for r in self.rows),
                'methods_agree': all(r['n_disagree'] == 0 for r in self.rows),
                'all_rounds_extend': all(r.get('extends', True) for r in self.rows),
                'knots_checked': sum(r['n_knots'] for r in self.rows),
                'first_failing_round': next((r['round'] for r in self.rows if r['n_rank_fail'] or r['n_cut_fail']),
                                            None),
                'first_non_extending_round': next((r['round'] for r in self.rows if r.get('extends') is False), None),
                'seconds': round(self.seconds, 1)}
