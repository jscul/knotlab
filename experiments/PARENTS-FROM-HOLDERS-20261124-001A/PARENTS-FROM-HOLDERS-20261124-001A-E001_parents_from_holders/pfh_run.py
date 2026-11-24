"""Runs 2 to 5 for one law: classes of looks on P1 and P2 (distances 1 to 6, the full look and the two coarser looks),
the written-out pairs, one pair followed from round to round, and the whole-structure renamings.

    python -B pfh_run.py --law F1R        # one of R3W, F1O, F1R, ORD

Writes, in artifacts/PARENTS-FROM-HOLDERS-20261124-001A/PARENTS-FROM-HOLDERS-20261124-001A-E001_parents_from_holders/:
  <law>_P1.json, <law>_P2.json, <law>_P1P2.json   one file per law and population
  pairs_<law>.json                               run 4 (pairs with renamings, the followed pair) and run 5
and, in the session scratchpad (not an output), classes_<law>.pkl.gz: the class of every place (for run 6).
A hard address-space cap of 8 GB is set on the process.  Requires checks.json with every check passed (run 1).
"""
from __future__ import annotations

import argparse
import gzip
import json
import pickle
import resource
import sys
import time

import pfh_common as PC


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--law', required=True, choices=sorted(PC.SHORT_LAW))
    ap.add_argument('--mem-gb', type=float, default=8.0)
    a = ap.parse_args()
    lim = int(a.mem_gb * (1 << 30))
    resource.setrlimit(resource.RLIMIT_AS, (lim, lim))
    PC.check_frozen()
    chk = json.loads((PC.OUT / 'checks.json').read_text())
    if not chk.get('pass'):
        raise SystemExit('run 1 has not passed: no other run is made')
    import pfh_classes as CL
    import pfh_iso as ISO
    import pfh_report as RP

    t0 = time.time()

    def log(*x):
        print('%8.1fs' % (time.time() - t0), *x, flush=True)
    lr = CL.LawRun(a.law, log=log)
    lr.build()
    lr.compute()
    log('classes done; search statistics', dict(ISO.STATS))
    tabs = RP.population_tables(lr)
    log('population tables done')
    law = PC.LAW_NAMES[lr.fam]
    common = {'law': law, 'law_short': a.law, 'starts': lr.pairs, 'rounds_checked': lr.rounds_checked,
              'p2_rounds': {s: len(lr.lineages[s]) for s in lr.pairs},
              'p2_events': lr.p2_events, 'n_structures': len(lr.structs), 'n_places': lr.n_items,
              'test_stats': {'%s d=%d' % k: v for k, v in lr.test_stats.items()},
              'in_look_checked': {'%s d=%d' % k: v for k, v in lr.in_look_checked.items()},
              'in_look_sampled': {'%s d=%d' % k: v for k, v in lr.in_look_sampled.items()},
              'whole_structure_links': lr.whole_stats, 'search_stats': dict(ISO.STATS),
              'serial_replay_checked': lr.replay, 'serial_prefix_checks': lr.prefix_checks,
              'command': ' '.join(sys.argv)}
    pops = tabs['populations']
    groups = {'P1': [p for p in pops if p.startswith('P1') and p != 'P1P2'],
              'P2': [p for p in pops if p.startswith('P2')],
              'P1P2': ['P1P2']}
    for name, plist in groups.items():
        obj = dict(common)
        obj['population'] = name
        obj['sub_populations'] = plist
        obj['tables'] = {k: {p: t[p] for p in plist} for k, t in tabs['tables'].items()}
        obj['least_distance_no_confusable_pair'] = {k: v for k, v in tabs['least_distance_no_confusable_pair'].items()
                                                    if k.split(' ', 1)[1] in plist}
        PC.write_json(PC.OUT / ('%s_%s.json' % (a.law, name)), obj)
    log('population files written')
    # run 4
    wp = RP.written_pairs(lr, 'full', 'P2')
    log('written pairs done')
    if a.law == 'F1O':
        fol = advisor_pair(lr, RP)
    else:
        ch = RP.choose_followed(lr, 'full')
        fol = None
        if ch is not None:
            d, start, i, j = ch
            fol = RP.followed_pair(lr, start, i, j, 'full', 10)
            fol['chosen_at_distance'] = d
            fol['chosen_pair'] = [RP.item_record(lr, i), RP.item_record(lr, j)]
    log('followed pair done')
    # run 5
    wr = RP.whole_renamings(lr, 2000)
    log('whole renamings done')
    out = dict(common)
    out.update({'written_pairs_P2_full': wp, 'followed_pair': fol, 'whole_structure_renamings': wr,
                'least_distance_no_confusable_pair': tabs['least_distance_no_confusable_pair'],
                'seconds': round(time.time() - t0, 1),
                'peak_rss_mb': round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)})
    PC.write_json(PC.OUT / ('pairs_%s.json' % a.law), out)
    # classes for run 6
    meta = {'labels': [r.label for r in lr.structs], 'kinds': lr.kinds.tobytes(), 'sid_of': lr.sid_of.tobytes(),
            'cls': {'%s %d' % k: v.tobytes() for k, v in lr.cls.items()}}
    PC.SCRATCH.mkdir(parents=True, exist_ok=True)
    with gzip.open(PC.SCRATCH / ('classes_%s.pkl.gz' % a.law), 'wb') as fh:
        pickle.dump(meta, fh, protocol=4)
    log('done', out['seconds'], 's, peak', out['peak_rss_mb'], 'MB')


def advisor_pair(lr, RP):
    """The advisor's pair on the two-knot start (deviations.md, item 28), followed through every P2 round."""
    start = 'TWO-KNOT'
    sids = lr.lineages[start]
    T = None
    for sid in sids:
        rec = lr.structs[sid]
        if rec.round >= 2:
            T = rec.T
            o = rec.offset
            break
    offs = sorted(x for x in range(T.n) if T.parents[x] == (0,) and T.made[x] == 1)
    a1, a2 = offs
    j = [x for x in range(T.n) if set(T.parents[x]) == {a1, a2}][0]
    pA = [e for e, y in T.sh[a1] if y == 0][0]
    pj = [e for e, y in T.sh[a1] if y == j][0]
    i0 = o + T.item_index[(a1, pA)]
    j0 = o + T.item_index[(a1, pj)]
    nmax = len(sids) + 2
    fol = RP.followed_pair(lr, start, i0, j0, 'full', nmax)
    fol['pair'] = 'the advisor\'s pair: a1 = %d (offshoot of start knot 0), its place with knot 0 and with j = %d' % (a1, j)
    return fol


if __name__ == '__main__':
    main()
