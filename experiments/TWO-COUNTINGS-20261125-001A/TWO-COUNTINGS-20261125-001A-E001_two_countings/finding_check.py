"""The knot-test finding's statements and per-structure table checked against part 8 (early and remainder)."""
from __future__ import annotations

import json

import tc

A = tc.ART + '/'
p8 = json.load(open(A + 'part8_knots.json'))
early = json.load(open(A + 'part8_early_knots.json'))
by = {}
for s in p8['structures']:
    for lab in s['labels']:
        by[lab] = s
S = tc.load_structures()


def fails(name):
    s = by['structures.json: ' + name]
    return sorted(k['knot'] for k in s['knots'] if not k['whole'])


def canon_fails(name):
    s = by['structures.json: ' + name]
    out = []
    for k in s['knots']:
        c = k.get('canonical')
        if not (isinstance(c, dict) and 'knot' in c):
            return None
        if not c['knot']:
            out.append(k['knot'])
    return sorted(out)


def all_canon_agree(name):
    s = by['structures.json: ' + name]
    return all(isinstance(k.get('canonical'), dict) and k['canonical'].get('agrees with projection') for k in s['knots'])


rows = []
expect = {}
for n in S:
    if n.startswith('eleven'):
        expect[n] = ['even(x1,x2,x3,c)', 'even(y1,y2,y3,t)']
    elif n.startswith('ten'):
        expect[n] = ['even(x1,x2,x3,c)']
    elif n.startswith('smallest gain finished 0'):
        expect[n] = ['nae(x1,x2,za)']
    elif n.startswith('eight ('):
        expect[n] = ['even(y1,y2,y3,s1)']
    elif n.startswith('eight +'):
        expect[n] = ['even(y1,y2,y3,s1)']
    else:
        expect[n] = []
dis = []
for n in S:
    f = fails(n)
    cf = canon_fails(n)
    own = [k['knot'] for k in by['structures.json: ' + n]['knots'] if not k['own']]
    s = by['structures.json: ' + n]
    k2 = all(not k['K2'] and k['K1'] and k['K3'] for k in s['knots'] if not k['whole'])
    ok = f == sorted(expect[n]) and (cf is None or cf == sorted(expect[n])) and not own and k2
    rows.append({'structure': n, 'knots': s['n_knots'], 'distinctions': s['n_distinctions'],
                 'fail in the whole (projection)': f, 'fail in the whole (canonical)': cf if cf is not None else
                 'projection only (more than 20 distinctions)', 'fail on their own': own,
                 'every failure is K2 alone': k2, 'canonical agrees with projection on every knot': all_canon_agree(n)
                 if cf is not None else None, 'the finding': sorted(expect[n]), 'agrees with the finding': ok})
    if not ok:
        dis.append(n)
n_canon = sum(s['knots'] for s in [{'knots': r['knots']} for r in rows if r['fail in the whole (canonical)'] !=
                                    'projection only (more than 20 distinctions)'])
out = {'per structure': rows, 'structures disagreeing with the finding': dis,
       'canonical knots of the 33 (at most 20 distinctions)': n_canon,
       'knots of the 33 by projection only': sum(r['knots'] for r in rows if r['fail in the whole (canonical)'] ==
                                                 'projection only (more than 20 distinctions)')}
tc.dump('part8_finding_check.json', out)
for r in rows:
    print(r['structure'], r['fail in the whole (projection)'], r['fail in the whole (canonical)'], r['agrees with the finding'])
print('disagreements:', dis, 'canonical knots', out['canonical knots of the 33 (at most 20 distinctions)'],
      'projection only', out['knots of the 33 by projection only'])
