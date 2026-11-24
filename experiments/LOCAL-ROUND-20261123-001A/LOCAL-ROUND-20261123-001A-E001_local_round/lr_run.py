"""One registered run: a start, a law family, a cutoff and a guard law, with the three kinds of order.

    python -B lr_run.py --start 'D2(4,3)' --ration RATION-3 --treatment CANCEL-WAIT --cutoff 1 --law R1 \
        --cap 10000000 --budget 420 --id 'D2(4,3)-R3W__r1__R1'

Writes artifacts/LOCAL-ROUND-20261123-001A/LOCAL-ROUND-20261123-001A-E001_local_round/runs/<slug>.json (gzipped when
larger than 15 MB).  A hard address-space cap of 8 GB is set on the process.
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE.parents[2] / 'artifacts' / HERE.parent.name / HERE.name / 'runs'


def slug(s):
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', s).strip('_')


def surplus_offshoot(ref, event, parent_I):
    """deviations.md item 27: the first mismatch is an offshoot (u,) of a knot whose image waits in the
    reference, and the reference's offshoots of m(u) with that fresh count are all images already."""
    if event[0] != 'birth' or len(event[1]) != 1:
        return False
    u = event[1][0]
    fa = event[2]
    if not ref.waited.get(u):
        return False
    offs = [x for x in ref.by_par.get((u,), ()) if ref.fresh[x] == fa]
    return all((parent_I >> x) & 1 for x in offs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', required=True)
    ap.add_argument('--ration', required=True)
    ap.add_argument('--treatment', required=True)
    ap.add_argument('--cutoff', type=int, required=True)
    ap.add_argument('--law', required=True)
    ap.add_argument('--cap', type=int, required=True)
    ap.add_argument('--budget', type=float, required=True)
    ap.add_argument('--id', required=True)
    ap.add_argument('--seeds', type=int, default=200)
    ap.add_argument('--mem-gb', type=float, default=8.0)
    a = ap.parse_args()
    lim = int(a.mem_gb * (1 << 30))
    resource.setrlimit(resource.RLIMIT_AS, (lim, lim))

    import lr_core as C
    import lr_reference as RF
    import lr_laws as L
    from lr_search import Runner

    t0 = time.time()
    ref = RF.RefData(C.start_stars(a.start), a.ration, a.treatment, a.cutoff)
    law = L.make_law(ref, a.law)
    run = Runner(ref, law)
    out = {'id': a.id, 'start': a.start, 'law_family': [a.ration, a.treatment], 'cutoff': a.cutoff, 'law': a.law,
           'reference': ref.summary(), 'command': ' '.join(sys.argv)}
    print(a.id, 'reference', ref.summary(), flush=True)

    # every order
    eo = run.every_order(a.cap, a.budget)
    least = None
    if eo.get('least_n') is not None and eo['examples']:
        exs = [e for e in eo['examples'] if e['births'] == eo['least_n']]
        out['least_mismatches_waiter_surplus'] = [surplus_offshoot(ref, e['event'], e['parent_key'][0]) for e in exs]
        ex = exs[0]
        I, Bar = ex['parent_key']
        path = run.path_to(I, Bar)
        if path is None:
            raise AssertionError('no order reaches the recorded state')
        order = path + [tuple(ex['event'][1])]
        least = {'births': eo['least_n'], 'exact': True, 'order': [list(B) for B in order],
                 'event': ex['event'], 'listing': run.listing(order),
                 'waiter_surplus_offshoot': surplus_offshoot(ref, ex['event'], I)}
        for e in eo['examples']:
            e['parent_key'] = [hex(e['parent_key'][0]), hex(e['parent_key'][1])]
    out['every_order'] = eo
    print(a.id, 'every order', {k: eo.get(k) for k in ('finished', 'stopped', 'least_n', 'keys', 'searched_to_births',
                                                       'mismatch_edges', 'orders', 'seconds', 'peak_rss_mb')}, flush=True)

    # sampled
    t1 = time.time()
    samp = run.sampled(range(a.seeds))
    t2 = time.time()
    xl = run.xlast()
    t3 = time.time()

    def tally(outs):
        c = {'match': 0, 'mismatch': 0, 'underbuild': 0}
        for o in outs:
            c[o['outcome']] += 1
        return c

    def least_of(outs, key):
        mm = [o for o in outs if o['outcome'] == 'mismatch']
        if not mm:
            return None
        o = min(mm, key=lambda o: (o['births'], o.get(key, 0)))
        order = [tuple(e[1]) for e in o['events'] if e[0] == 'birth']
        return {'births': o['births'], key: o.get(key), 'order': [list(B) for B in order],
                'listing': run.listing(order)}

    out['sampled'] = {'n': len(samp), 'counts': tally(samp), 'seconds': round(t2 - t1, 2),
                      'least_found': least_of(samp, 'seed'),
                      'orders': [{k: v for k, v in o.items() if k != 'events' or o['outcome'] != 'match'}
                                 for o in samp]}
    out['xlast'] = {'n': len(xl), 'counts': tally(xl), 'seconds': round(t3 - t2, 2),
                    'least_found': least_of(xl, 'x'),
                    'orders': [{k: v for k, v in o.items() if k != 'events' or o['outcome'] != 'match'} for o in xl]}
    for kind in ('sampled', 'xlast'):
        for o in out[kind]['orders']:
            if o['outcome'] == 'mismatch' and 'events' in o:
                ev = o['events'][-1]
                if ev[0] == 'birth':
                    # the state before the mismatching birth
                    I = ref.start_mask
                    for e in o['events'][:-1]:
                        if e[0] == 'birth':
                            I |= 1 << e[3]
                    o['waiter_surplus_offshoot'] = surplus_offshoot(ref, ['birth', ev[1], ev[2]], I)
    if least is None:
        cands = [x for x in (out['sampled']['least_found'], out['xlast']['least_found']) if x]
        if cands:
            b = min(cands, key=lambda x: x['births'])
            least = dict(b)
            least['exact'] = False
    out['least_differing_order'] = least
    closing = []
    for o in samp + xl:
        closing.extend(o.get('closing', []))
    out['closing_bit'] = {
        'every_order_firings': eo.get('closing_firings', 0),
        'every_order_matched_received_none': eo.get('closing_matched_none', 0),
        'every_order_events': eo.get('closing_events', []),
        'sampled_and_xlast_firings': len(closing),
        'sampled_and_xlast_matched_received_none': sum(1 for c in closing if c['matched_received_none']),
        'reference_closing_knots': ref.closing_knots}
    out['group_of_three_or_more'] = {'seen': law.big, 'first_where': law.big_where}
    out['brood_roster_with_short_member'] = {'seen': law.brood_short, 'first_where': law.brood_short_where}
    out['seconds'] = round(time.time() - t0, 2)
    out['peak_rss_mb'] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    data = json.dumps(out, default=str)
    path = OUT / (slug(a.id) + '.json')
    if len(data) > 15_000_000:
        with gzip.open(str(path) + '.gz', 'wt') as fh:
            fh.write(data)
    else:
        path.write_text(data)
    print(a.id, 'sampled', out['sampled']['counts'], 'xlast', out['xlast']['counts'],
          'least', (least or {}).get('births'), (least or {}).get('exact'), 'big', law.big,
          'total s', out['seconds'], flush=True)


if __name__ == '__main__':
    main()
