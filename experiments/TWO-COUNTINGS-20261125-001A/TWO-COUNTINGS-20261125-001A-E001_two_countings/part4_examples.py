"""Part 4: the examples E0-E7 of TD 8.2 (R 25-27), and the two other h2 candidates of Known 7 beside (not predicted)."""
from __future__ import annotations

import time
from fractions import Fraction as Fr

import lemma
import orders
import part2_lemma
import specs
import tc

T0 = time.time()
tc.cap_memory()
S = tc.load_structures()
E11 = S['eleven (start)']
KA, KB = specs.setting_knots()
PAIRS = lemma.PAIRS


def spec(name, KA_, KB_, recA=specs.REC_A, recB=specs.REC_B, post=None):
    sp = {'name': name, 'pre': [E11], 'KA': KA_, 'KB': KB_, 'recA': recA, 'recB': recB}
    if post is not None:
        sp['variants'] = [{'label': 'only', 'post': {ab: post for ab in PAIRS}}]
    return sp


items = []


def run(label, breaks, sp, counting='from the start'):
    r = lemma.run_spec(sp)
    v = r['variants'][0]['rows']
    row = v[counting]
    items.append({'example': label, 'breaks (TD 8.2)': breaks, 'counting': counting,
                  'score_all': tc.fstr(row['score_all']), 'score_parity': tc.fstr(row['score_parity']),
                  'score_parity_abs': tc.fstr(row['score_parity_abs']),
                  'change_first': tc.fstr(row['change_first']), 'change_second': tc.fstr(row['change_second']),
                  'hidden': row['hidden'], 'kept': {k: tc.fstr(x) for k, x in row['kept'].items()},
                  'hypotheses (counting from the start)': v['from the start'].get('hypotheses'),
                  'P3: a score above 2 or a record changed': row['score_all'] > 2 or not row['hidden'],
                  'all rows': part2_lemma.compact_run(r)})
    print(label, items[-1]['score_all'], items[-1]['change_first'], items[-1]['change_second'], items[-1]['hidden'],
          v['from the start']['hypotheses']['fails'], flush=True)


run('E0', 'none', spec('E0', KA, KB))
run('E1', 'the premise (no start before the settings)', spec('E1', KA, KB), counting='from the finish')
# E2: construction order 11 (index 11 of the list, R 25)
o11 = orders.ORD['eleven_registered_400']['orders'][11]
e2 = orders.evaluate_order(('eleven_registered_400', 11, o11))
items.append({'example': 'E2', 'breaks (TD 8.2)': "h1′, and h4's first clause as a consequence",
              'counting': 'from the start (nothing), renormalised', **{k: e2[k] for k in (
                  'order', 'in class', 'class detail', 'score_all', 'score_parity', 'score_parity_abs', 'change_first',
                  'change_second', 'hidden', 'weight lost')},
              'P3: a score above 2 or a record changed': Fr(e2['score_all']) > 2 or not e2['hidden']})
print('E2', e2['score_all'], e2['hidden'], e2['weight lost'], flush=True)
e2b = orders.evaluate_order(('eleven_registered_400', 10, orders.ORD['eleven_registered_400']['orders'][10]))
beside = [{'example': 'E2 read as the 11th order (index 10), beside, not judged', **{k: e2b[k] for k in (
    'order', 'in class', 'score_all', 'hidden', 'weight lost')}}]
# E3: the first setting knot nae(x1, x2 or x3, s1), nothing fresh; record (x1,x2,x3,s1)
KA3 = {0: [('nae', ('x1', 'x2', 's1'))], 1: [('nae', ('x1', 'x3', 's1'))]}
run('E3', 'h2 (renormalised)', spec('E3', KA3, KB, recA=['x1', 'x2', 'x3', 's1']))
# E4: both setting knots hold one fresh z
KA4 = {0: [('nae', ('x1', 'x2', 'z'))], 1: [('nae', ('x1', 'x3', 'z'))]}
KB4 = {0: [('nae', ('y1', 'y2', 'z'))], 1: [('nae', ('y1', 'y3', 'z'))]}
run('E4', "h3′", spec('E4', KA4, KB4, recA=['x1', 'x2', 'x3', 'z'], recB=['y1', 'y2', 'y3', 'z']))
# E5: a later even(za, zb, x1), nothing fresh
run('E5', "h4, first clause (renormalised)", spec('E5', KA, KB, post=[[('even', ('za', 'zb', 'x1'))]]))
# E6: the first record holds zb
run('E6', 'h4, record clause', spec('E6', KA, KB, recA=['x1', 'x2', 'x3', 'zb']))
# E7: a later even(zb, w, x1), w fresh; first record (x1,x2,x3,w)
run('E7', 'h4, record clause', spec('E7', KA, KB, recA=['x1', 'x2', 'x3', 'w'], post=[[('even', ('zb', 'w', 'x1'))]]))
# Known 7's two other h2 candidates, beside
for w in ('h1', 'h2'):
    KAw = {0: [('nae', ('x1', 'x2', w))], 1: [('nae', ('x1', 'x3', w))]}
    r = lemma.run_spec(spec('h2 candidate w = %s' % w, KAw, KB, recA=['x1', 'x2', 'x3', w]))
    row = r['variants'][0]['rows']['from the start']
    beside.append({'example': 'other h2 candidate nae(x1, x2 or x3, %s), beside (Known 7), not judged' % w,
                   'score_all': tc.fstr(row['score_all']), 'hidden': row['hidden'],
                   'change_first': tc.fstr(row['change_first']), 'change_second': tc.fstr(row['change_second']),
                   'kept': {k: tc.fstr(x) for k, x in row['kept'].items()},
                   'hypotheses': row['hypotheses']})
    print(beside[-1]['example'], beside[-1]['score_all'], beside[-1]['hidden'], beside[-1]['kept'], flush=True)
P3 = all(x['P3: a score above 2 or a record changed'] for x in items if x['example'] != 'E0')
out = {'part': 4, 'examples': items, 'beside': beside, 'P3 holds': P3, 'wall_s': round(time.time() - T0, 1)}
tc.dump('part4_examples.json', out)
print('P3', P3, 'wall', out['wall_s'])
