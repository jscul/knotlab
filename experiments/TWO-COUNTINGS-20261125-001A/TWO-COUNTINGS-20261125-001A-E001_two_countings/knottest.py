"""Part 8 machinery: the knot test in the whole structure by projection and by the canonical command (TD 10, R 10-11)."""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor

import tc


def test_structures(items, canonical=True, workers=4, deadline=None, log=print):
    """items: [(label, knots)].  Returns [{label, ..., knots: [...]}].  Canonical checks run in `workers` threads, each one
    subprocess at a time; a structure is not started after `deadline` (time.time() value), its knots marked cut."""
    out = []
    jobs = []
    for label, ks in items:
        ks = [tc.as_knot(k) for k in ks]
        r = tc.project_test(ks)
        r['label'] = label
        r['structure'] = [tc.kstr(k) for k in ks]
        out.append(r)
        if canonical:
            if r['n_distinctions'] > 20:
                for k in r['knots']:
                    k['canonical'] = 'not run (more than 20 distinctions; projection only, as registered)'
            else:
                jobs.append((len(out) - 1, ks))
    if canonical and jobs:
        def one(job_i):
            si, ks = job_i
            if deadline is not None and time.time() > deadline:
                return si, None
            res = []
            for i in range(len(ks)):
                res.append(tc.canonical_check(ks, i))
            return si, res
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for si, res in ex.map(one, jobs):
                r = out[si]
                if res is None:
                    for k in r['knots']:
                        k['canonical'] = 'canonical check not run (cut)'
                    continue
                for k, c in zip(r['knots'], res):
                    if 'error' in c:
                        k['canonical'] = {'error': c['error']}
                        continue
                    agree = (c['allowed'] == k['induced'] and c['K1'] == k['K1'] and c['K2'] == k['K2']
                             and c['K3'] == k['K3'] and c['knot'] == k['whole'])
                    k['canonical'] = {'K1': c['K1'], 'K2': c['K2'], 'K3': c['K3'], 'knot': c['knot'],
                                      'agrees with projection': agree}
                log('canonical done: %s' % r['label'])
    return out


def failing(r):
    return [k['knot'] for k in r['knots'] if not k['whole']]


def summary_row(r):
    fails = [k for k in r['knots'] if not k['whole']]
    return {'structure': r['label'], 'knots': r['n_knots'], 'distinctions': r['n_distinctions'],
            'allowed states': r['n_states'],
            'fail in the whole': ['%s (%s)' % (k['knot'], ', '.join(x for x in ('K1', 'K2', 'K3') if not k[x]))
                                  for k in fails],
            'fail on their own': [k['knot'] for k in r['knots'] if not k['own']],
            'canonical': _canon_status(r)}


def _canon_status(r):
    st = set()
    for k in r['knots']:
        c = k.get('canonical')
        if isinstance(c, dict):
            if 'error' in c:
                st.add('error')
            else:
                st.add('agrees' if c['agrees with projection'] else 'DISAGREES')
        elif c is None:
            st.add('not run')
        else:
            st.add(c)
    return sorted(st)
