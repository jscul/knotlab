"""One registered run: a start, a law family, a cutoff and a guard, with the three kinds of order.

    python -B gch_run.py --start 'D2(4,3)' --family CAP3W --cutoff 1 --law R3 --id 'CAP3W-D2(4,3)__r1__R3'

The law is R1, R2, R3, R3P (the repaired guard R3'), CONTROL or T(d).  The every-order search is capped at two
million keys (checked when a level is complete) with no time budget.  Writes
artifacts/GUARD-CAP-AND-HOLD-20261124-001A/GUARD-CAP-AND-HOLD-20261124-001A-E001_guard_cap_hold/runs/<slug>.json.
A hard address-space cap of 8 GB is set on the process.
"""
from __future__ import annotations

import argparse
import json
import re
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE.parents[2] / 'artifacts' / 'GUARD-CAP-AND-HOLD-20261124-001A' / \
    'GUARD-CAP-AND-HOLD-20261124-001A-E001_guard_cap_hold' / 'runs'


def slug(s):
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', s).strip('_')


def surplus_offshoot(ref, event, parent_I):
    """The earlier study's item 27: the first mismatch is an offshoot (u,) of a knot whose image waits in the
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
    ap.add_argument('--family', required=True)
    ap.add_argument('--cutoff', type=int, required=True)
    ap.add_argument('--law', required=True)
    ap.add_argument('--cap', type=int, default=2_000_000)
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
    from gch_configs import NAMES

    fam = NAMES[a.family]
    t0 = time.time()
    ref = RF.RefData(C.start_stars(a.start), fam[0], fam[1], a.cutoff, release=fam[2], fillers=fam[3])
    law = L.make_law(ref, a.law)
    if law.start_clause_condition():
        raise SystemExit('the start clause condition fails: %s' % law.start_clause_condition())
    run = Runner(ref, law)
    out = {'id': a.id, 'start': a.start, 'family': a.family, 'law_family': list(fam), 'cutoff': a.cutoff,
           'law': law.name, 'reference': ref.summary(), 'command': ' '.join(sys.argv)}
    print(a.id, 'reference', ref.summary(), flush=True)

    eo = run.every_order(a.cap)
    least = None
    if eo.get('least_n') is not None and eo['examples']:
        exs = [e for e in eo['examples'] if e['births'] == eo['least_n']]
        out['least_mismatches_waiter_surplus'] = [surplus_offshoot(ref, e['event'], e['parent_key'][0]) for e in exs]
        ex = exs[0]
        I, Bar = ex['parent_key']
        path = run.path_to(I, Bar)
        if path is None:
            raise AssertionError('no order reaches the recorded state')
        ev = ex['event']
        order = path + [(tuple(ev[1]), ev[2], ev[3])] if ev[0].startswith('birth') else path
        least = {'births': eo['least_n'], 'exact': True, 'order': [[list(B), f, u] for B, f, u in order],
                 'event': ev, 'listing': run.listing(order),
                 'waiter_surplus_offshoot': surplus_offshoot(ref, ev, I)}
        for e in eo['examples']:
            e['parent_key'] = [hex(e['parent_key'][0]), hex(e['parent_key'][1])]
    out['every_order'] = eo
    print(a.id, 'every order', {k: eo.get(k) for k in ('finished', 'stopped', 'least_n', 'keys', 'searched_to_births',
                                                       'mismatch_edges', 'orders', 'seconds', 'peak_rss_mb')},
          flush=True)

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
        order = [(tuple(e[1]), e[2], e[3]) for e in o['events'] if e[0] == 'birth']
        return {'births': o['births'], key: o.get(key), 'order': [[list(B), f, u] for B, f, u in order],
                'listing': run.listing(order)}

    def reasons(outs):
        c = {}
        for o in outs:
            if o['outcome'] == 'underbuild' and o.get('why'):
                w = o['why']
                k = '%s | first never made: %s' % (w.get('why', {}).get('reason', 'retirement not made'),
                                                   w.get('first_never_made'))
                c[k] = c.get(k, 0) + 1
        return c

    def keep(o):
        return {k: v for k, v in o.items() if k != 'events' or o['outcome'] != 'match'}

    out['sampled'] = {'n': len(samp), 'counts': tally(samp), 'seconds': round(t2 - t1, 2),
                      'least_found': least_of(samp, 'seed'), 'underbuild_reasons': reasons(samp),
                      'orders': [keep(o) for o in samp]}
    out['xlast'] = {'n': len(xl), 'counts': tally(xl), 'seconds': round(t3 - t2, 2),
                    'least_found': least_of(xl, 'x'), 'underbuild_reasons': reasons(xl),
                    'orders': [keep(o) for o in xl]}
    for kind in ('sampled', 'xlast'):
        for o in out[kind]['orders']:
            if o['outcome'] == 'mismatch' and 'events' in o:
                ev = o['events'][-1]
                if ev[0] == 'birth':
                    I = ref.start_mask
                    for e in o['events'][:-1]:
                        if e[0] == 'birth':
                            I |= 1 << e[4]
                    o['waiter_surplus_offshoot'] = surplus_offshoot(ref, ['birth', ev[1], ev[2]], I)
    if least is None:
        cands = [x for x in (out['sampled']['least_found'], out['xlast']['least_found']) if x]
        if cands:
            b = min(cands, key=lambda x: x['births'])
            least = dict(b)
            least['exact'] = False
    out['least_differing_order'] = least
    # the first underbuilding order found, with its explanation
    ub = None
    for o in samp + xl:
        if o['outcome'] == 'underbuild':
            ub = {'births': o['births'], 'why': o.get('why'), 'seed': o.get('seed'), 'x': o.get('x'),
                  'order': [[e[1], e[2], e[3]] for e in o.get('events', []) if e[0] == 'birth']}
            break
    if ub is None and eo.get('underbuild_examples'):
        ub = {'every_order_example': eo['underbuild_examples'][0]}
    out['underbuild_example'] = ub
    closing = []
    for o in samp + xl:
        closing.extend(o.get('closing', []))
    out['closing_bit'] = {
        'every_order_firings': eo.get('closing_firings', 0),
        'every_order_matched_received_none': eo.get('closing_matched_none', 0),
        'sampled_and_xlast_firings': len(closing),
        'sampled_and_xlast_matched_received_none': sum(1 for c in closing if c['matched_received_none']),
        'reference_closing_knots': ref.closing_knots}
    out['group_of_three_or_more'] = {'seen': law.big, 'first_where': law.big_where,
                                     'rosters_read_with_one': law.big_rosters}
    out['brood_roster_with_short_member'] = {'seen': law.brood_short, 'first_where': law.brood_short_where}
    out['seconds'] = round(time.time() - t0, 2)
    out['peak_rss_mb'] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / (slug(a.id) + '.json')).write_text(json.dumps(out, default=str))
    print(a.id, 'sampled', out['sampled']['counts'], 'xlast', out['xlast']['counts'],
          'least', (least or {}).get('births'), (least or {}).get('exact'), 'total s', out['seconds'], flush=True)


if __name__ == '__main__':
    main()
