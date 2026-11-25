"""Part 8, early: the knot test in the whole of the three structures the finding names first, by projection and by the
canonical command; then the finding's four statements checked one by one."""
from __future__ import annotations

import os
import sys
import time

import knottest
import tc

T0 = time.time()
tc.cap_memory()
S = tc.load_structures()
workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
names = (['eleven (start)'] + ['eleven + settings %d%d' % (a, b) for a in (0, 1) for b in (0, 1)]
         + ['eight (start)'] + ['eight + settings %d%d' % (a, b) for a in (0, 1) for b in (0, 1)]
         + ['smallest gain: part', 'smallest gain: part + rule-Q round 1']
         + ['smallest gain finished %d%d' % (a, b) for a in (0, 1) for b in (0, 1)])
res = knottest.test_structures([(n, S[n]) for n in names], canonical=True, workers=workers)
by = {r['label']: r for r in res}

stmts = []


def st(name, ok, detail):
    stmts.append({'statement': name, 'confirmed by projection': ok[0], 'confirmed by the canonical checker': ok[1],
                  'detail': detail})
    print(('CONFIRMED ' if all(ok) else 'NOT CONFIRMED ') + name, ok, detail, flush=True)


def canon_fails(r):
    out = []
    for k in r['knots']:
        c = k.get('canonical')
        if isinstance(c, dict) and 'knot' in c and not c['knot']:
            out.append(k['knot'])
    return out


def canon_complete(r):
    return all(isinstance(k.get('canonical'), dict) and 'knot' in k['canonical'] for k in r['knots'])


def kn(r, name):
    return next(k for k in r['knots'] if k['knot'] == name)


# statement 1
four = {'even(x1,x2,x3,c)', 'even(y1,y2,y3,t)'}
el = ['eleven (start)'] + ['eleven + settings %d%d' % (a, b) for a in (0, 1) for b in (0, 1)]
p1 = all(set(knottest.failing(by[n])) == four for n in el) and all(
    not kn(by[n], f)['K2'] and kn(by[n], f)['K1'] and kn(by[n], f)['K3'] for n in el for f in four) and all(
    kn(by[n], f)['induced'] == ['0011', '0101', '1010', '1100'] for n in el for f in four)
c1 = all(canon_complete(by[n]) and set(canon_fails(by[n])) == four for n in el) and all(
    kn(by[n], f)['canonical']['K2'] is False for n in el for f in four)
st('1. 11-knot: the two four-place parity rules fail K2 in the start and all four finished structures, each inducing '
   '{0011,0101,1010,1100}; the other 9 knots and both setting knots pass', (p1, c1),
   {n: knottest.failing(by[n]) for n in el})
# statement 2
sg0 = ['smallest gain finished 00', 'smallest gain finished 01']
sg1 = ['smallest gain finished 10', 'smallest gain finished 11']
sgp = ['smallest gain: part', 'smallest gain: part + rule-Q round 1']
p2 = (all(knottest.failing(by[n]) == ['nae(x1,x2,za)'] for n in sg0)
      and all(kn(by[n], 'nae(x1,x2,za)')['induced'] == ['010', '011', '100', '101'] for n in sg0)
      and all(not kn(by[n], 'nae(x1,x2,za)')['K2'] for n in sg0)
      and all(knottest.failing(by[n]) == [] for n in sg1 + sgp))
c2 = (all(canon_complete(by[n]) for n in sg0 + sg1 + sgp) and all(canon_fails(by[n]) == ['nae(x1,x2,za)'] for n in sg0)
      and all(canon_fails(by[n]) == [] for n in sg1 + sgp))
st('2. smallest gain: nae(x1,x2,za) fails K2 at a = 0 inducing {010,011,100,101}; at a = 1 every knot passes; the part '
   'and the part after the rule-Q round pass', (p2, c2), {n: knottest.failing(by[n]) for n in sg0 + sg1 + sgp})
# statement 3 (the 8-knot part of it; the 7-, 9- and 18-knot parts are tested in the remainder of part 8)
ei = ['eight (start)'] + ['eight + settings %d%d' % (a, b) for a in (0, 1) for b in (0, 1)]
p3 = all(knottest.failing(by[n]) == ['even(y1,y2,y3,s1)'] for n in ei) and all(
    not kn(by[n], 'even(y1,y2,y3,s1)')['K2'] for n in ei)
c3 = all(canon_complete(by[n]) and canon_fails(by[n]) == ['even(y1,y2,y3,s1)'] for n in ei)
st('3 (8-knot part). even(y1,y2,y3,s1) of the 8-knot structure fails K2 in the whole, in the start and with every '
   'setting pair; every other knot passes', (p3, c3), {n: knottest.failing(by[n]) for n in ei})
# statement 4 (on these structures)
p4 = all(k['own'] for r in res for k in r['knots'])
st('4 (on these structures). every rule passes on its own', (p4, p4), None)
agree = all(k['canonical']['agrees with projection'] for r in res for k in r['knots'])
print('canonical agrees with projection on every knot:', agree, sum(len(r['knots']) for r in res), 'knots')
out = {'part': '8 (early)', 'structures': res, 'statements': stmts, 'canonical agrees with projection': agree,
       'knots checked': sum(len(r['knots']) for r in res), 'summary': [knottest.summary_row(r) for r in res],
       'example command': tc.cmd_text(S['eleven (start)'], 0), 'wall_s': round(time.time() - T0, 1)}
tc.dump('part8_early_knots.json', out)
print('wall', out['wall_s'])
