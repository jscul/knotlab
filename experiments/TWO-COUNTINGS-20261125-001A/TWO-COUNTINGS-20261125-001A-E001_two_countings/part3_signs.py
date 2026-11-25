"""Part 3: the 512 sign assignments of the 11-knot structure's nine parity knots (PR part 3; R 14, 15), both countings,
all two-valued functions (and parities), hidden; with the knot test of every start and finished structure by projection
(part 8's share for part 3) and P8's two checks."""
from __future__ import annotations

import sys
import time
from fractions import Fraction as Fr
from multiprocessing import Pool

import lemma
import specs
import tc

S = tc.load_structures()
BASE = S['eleven (start)']
PAR = [i for i, (r, _) in enumerate(BASE) if r in ('even', 'odd')]
assert len(PAR) == 9


def signed(idx):
    ks = list(BASE)
    for bit, i in enumerate(PAR):
        ks[i] = ('odd' if (idx >> bit) & 1 else 'even', BASE[i][1])
    return ks


def tie(states, H, p, q):
    vals = {((int(w) >> H.idx[p]) & 1) ^ ((int(w) >> H.idx[q]) & 1) for w in states}
    return 'equality' if vals == {0} else 'inequality' if vals == {1} else 'none'


def one(idx):
    tc.cap_memory()
    ks = signed(idx)
    KA, KB = specs.setting_knots()
    sp = {'name': 'signs %03d' % idx, 'pre': [ks], 'KA': KA, 'KB': KB, 'recA': specs.REC_A, 'recB': specs.REC_B}
    r = lemma.run_spec(sp, mixed=False)
    v = r['variants'][0]
    H0 = tc.History([ks])
    out = {'index': idx, 'signs': [ks[i][0] for i in PAR], 'start allowed': len(H0.A[0]),
           'tie x2,x3': tie(H0.A[0], H0, 'x2', 'x3'), 'tie y2,y3': tie(H0.A[0], H0, 'y2', 'y3')}
    for name in ('from the start', 'from the finish'):
        x = v['rows'][name]
        out[name] = {'score_all': tc.fstr(x['score_all']), 'score_parity': tc.fstr(x['score_parity']),
                     'score_parity_abs': tc.fstr(x['score_parity_abs']), 'change_first': tc.fstr(x['change_first']),
                     'change_second': tc.fstr(x['change_second']), 'hidden': x['hidden'],
                     'verdict': x.get('verdict')}
    out['allowed at the finish'] = v['info']['allowed at the finish']
    # knot test by projection, start and four finished structures
    kt = {}
    for label, struct in [('start', ks)] + [('finished %d%d' % (a, b), ks + KA[a] + KB[b]) for a in (0, 1) for b in (0, 1)]:
        pt = tc.project_test(struct)
        kt[label] = {'fail': [{'knot': k['knot'], 'K1': k['K1'], 'K2': k['K2'], 'K3': k['K3'], 'induced': k['induced']}
                              for k in pt['knots'] if not k['whole']],
                     'own fail': [k['knot'] for k in pt['knots'] if not k['own']], 'n_knots': pt['n_knots']}
    out['knot test'] = kt
    return out


def main():
    T0 = time.time()
    tc.cap_memory()
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    with Pool(nproc) as pool:
        rows = list(pool.imap(one, range(512), chunksize=8))
    four = {'even(x1,x2,x3,c)', 'even(y1,y2,y3,t)', 'odd(x1,x2,x3,c)', 'odd(y1,y2,y3,t)'}
    # P8 (a): the two four-place rules fail K2 in all 512 (in the start and in every finished structure)
    p8a = all(all({f['knot'] for f in kt['fail']} >= set() and
                  sum(1 for f in kt['fail'] if f['knot'] in four and not f['K2']) == 2
                  for kt in r['knot test'].values()) for r in rows)
    other_fails = sorted({(r['index'], lab, f['knot']) for r in rows for lab, kt in r['knot test'].items()
                          for f in kt['fail'] if f['knot'] not in four})
    own_fails = sorted({(r['index'], lab, k) for r in rows for lab, kt in r['knot test'].items() for k in kt['own fail']})
    at = {r['index'] for r in rows if r['from the finish']['score_all'] == '20/9' and r['from the finish']['hidden']}
    ineq = {r['index'] for r in rows if r['tie x2,x3'] == 'inequality' and r['tie y2,y3'] == 'inequality'}
    start_above = [r['index'] for r in rows if Fr(r['from the start']['score_all']) > 2]
    start_not_hidden = [r['index'] for r in rows if not r['from the start']['hidden']]
    start_not2 = [r['index'] for r in rows if Fr(r['from the start']['score_all']) != 2]
    from collections import Counter
    summary = {
        'assignments': len(rows),
        'finish: hidden at 20/9': len(at),
        'finish: score values (all two-valued functions, hidden or not)': {str(k): v for k, v in Counter(
            (r['from the finish']['score_all'], r['from the finish']['hidden']) for r in rows).most_common()},
        'start: score values': {str(k): v for k, v in Counter((r['from the start']['score_all'], r['from the start']['hidden'])
                                            for r in rows).most_common()},
        'start: above 2': start_above, 'start: not hidden': start_not_hidden, 'start: not exactly 2': start_not2,
        'ties x2,x3 and y2,y3 both inequalities': len(ineq),
        'P8: the 128 at 20/9 are exactly those with both ties inequalities': at == ineq,
        'P8: both four-place rules fail K2 in all 512 (start and every finished structure)': p8a,
        'other rules failing in the whole (index, structure, rule)': other_fails,
        'rules failing on their own': own_fails,
        'tie kinds': {str(k): v for k, v in Counter((r['tie x2,x3'], r['tie y2,y3']) for r in rows).most_common()},
        'four-place rules’ induced relations (start), by tie kinds': {},
    }
    rel = {}
    for r in rows:
        key = '%s / %s' % (r['tie x2,x3'], r['tie y2,y3'])
        for f in r['knot test']['start']['fail']:
            rel.setdefault(key, {}).setdefault(f['knot'][:4] + f['knot'][f['knot'].index('('):], set()).add(
                ' '.join(f['induced']))
    summary['four-place rules’ induced relations (start), by tie kinds'] = {
        k: {kk: sorted(vv) for kk, vv in v.items()} for k, v in rel.items()}
    out = {'part': 3, 'summary': summary, 'rows': rows, 'wall_s': round(time.time() - T0, 1), 'processes': nproc}
    tc.dump('part3_signs.json', out)
    print({k: v for k, v in summary.items() if not isinstance(v, list) or len(v) < 10})
    print('wall', out['wall_s'])


if __name__ == '__main__':
    main()
