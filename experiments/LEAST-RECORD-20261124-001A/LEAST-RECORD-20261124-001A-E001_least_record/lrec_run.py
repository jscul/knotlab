"""Runs 2, 5, 6 and 7 of LEAST-RECORD-20261124-001A for one law and one chain of stamps (deviations.md, items 20, 22, 23).

    python -B lrec_run.py --law F1R --chain G       # chains: G, P, H, N, M for R3W, F1O, F1R, ORD; P3 for H-C3W, ...

Writes, in artifacts/LEAST-RECORD-20261124-001A/LEAST-RECORD-20261124-001A-E001_least_record/:
  <stamp>_<law>_<population>.json     one file per stamp, law and population (P1, P2, P1P2; or P3)
  pairs_<stamp>_<law>.json            run 5: the confusable pair with the fewest knots, by population
and in the session scratchpad the class table of every stamp (not an output).  Requires checks.json (run 1 passed) and
generations.json (run 3).
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

CHAINS = {
    'G': ['GENERATION', 'GENERATION-MOD-3', 'GENERATION-MOD-2'],
    'P': ['PARENT-COUNT', 'JOIN'],
    'H': ['HAS-CHILD+START-KNOT', 'HAS-CHILD', 'START-KNOT'],
    'N': ['NONE'],
    'M': ['NOT-MEMBER'],
    'P3': ['GENERATION', 'GENERATION-MOD-3', 'NONE'],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--law', required=True, choices=sorted(PC.SHORT_LAW))
    ap.add_argument('--chain', required=True, choices=sorted(CHAINS))
    ap.add_argument('--mem-gb', type=float, default=8.0)
    a = ap.parse_args()
    lim = int(a.mem_gb * (1 << 30))
    resource.setrlimit(resource.RLIMIT_AS, (lim, lim))
    PC.check_frozen()
    if not json.loads((PC.OUT / 'checks.json').read_text()).get('pass'):
        raise SystemExit('run 1 has not passed')
    gens = json.loads((PC.OUT / 'generations.json').read_text())
    hold = a.law in PC.HOLD_LAWS
    if hold != (a.chain == 'P3'):
        raise SystemExit('chain P3 is for the laws with holding, and only them')
    chain = list(CHAINS[a.chain])
    if a.chain == 'G' and a.law == 'R3W':
        for key, m in gens['moduli_for_run_6'].items():
            if key.startswith('R3W ') and 'GENERATION-MOD-%d' % m not in chain:
                chain.append('GENERATION-MOD-%d' % m)
    import pfh_classes as CL
    import pfh_iso as ISO
    import pfh_report as RP

    t0 = time.time()

    def log(*x):
        print('%8.1fs' % (time.time() - t0), *x, flush=True)
    lr = CL.LawRun(a.law, log=log)
    lr.build()
    first = chain[0]
    for stamp in chain:
        finer = first if stamp != first else None
        ts = time.time()
        lr.compute_stamp(stamp, finer=finer)
        tabs = RP.population_tables(lr, stamp)
        common = {'stamp': stamp, 'law': PC.LAW_NAMES[lr.fam], 'law_short': a.law, 'starts': lr.pairs,
                  'condition': {st: {'holds': c[0], 'fails_at': c[1]} for st, c in lr.cond.items()},
                  'rounds_checked': lr.rounds_checked, 'lineage_rounds': {s: len(lr.lineages[s]) for s in lr.pairs},
                  'n_structures': len(lr.structs), 'n_places': lr.n_items, 'carried_over_from': finer,
                  'test_stats': {'d=%d' % d: lr.test_stats[(stamp, d)] for d in range(1, 7)},
                  'in_look_checked': {'d=%d' % d: lr.in_look_checked[(stamp, d)] for d in range(1, 7)},
                  'in_look_sampled': {'d=%d' % d: lr.in_look_sampled[(stamp, d)] for d in range(1, 7)},
                  'whole_structure_links': lr.whole_stats.get(stamp), 'search_stats': dict(ISO.STATS),
                  'seconds_for_this_stamp': round(time.time() - ts, 1), 'command': ' '.join(sys.argv)}
        pops = tabs['populations']
        if hold:
            groups = {'P3': [p for p in pops if p.startswith('P3')]}
        else:
            groups = {'P1': [p for p in pops if p.startswith('P1') and not p.startswith('P1P2')],
                      'P2': [p for p in pops if p.startswith('P2')],
                      'P1P2': [p for p in pops if p.startswith('P1P2')]}
        for name, plist in groups.items():
            obj = dict(common)
            obj['population'] = name
            obj['sub_populations'] = plist
            obj['tables'] = {k: {p: t[p] for p in plist} for k, t in tabs['tables'].items()}
            for key in ('least_distance_no_confusable_pair', 'least_distance_rule_counted',
                        'least_distance_rule_counted_with_variant_second_guard'):
                obj[key] = {p: tabs[key][p] for p in plist}
            PC.write_json(PC.OUT / ('%s_%s_%s.json' % (stamp, a.law, name)), obj)
        # run 5: the smallest confusable pair, at the largest distance with one, by population
        pairs = {}
        targets = ['P3'] if hold else ['P1P2 | holds', 'P1P2 | fails', 'P2 | holds', 'P1 | holds']
        for pop in targets:
            if pop not in pops:
                continue
            ds = [d for d in range(6, 0, -1) if tabs['tables']['d=%d' % d][pop]['mixed_classes'] > 0]
            pairs[pop] = RP.smallest_pair(lr, stamp, pop, ds[0]) if ds else None
        obj = dict(common)
        obj['smallest_pairs'] = pairs
        PC.write_json(PC.OUT / ('pairs_%s_%s.json' % (stamp, a.law)), obj)
        meta = {'labels': [r.label for r in lr.structs], 'kinds': lr.kinds.tobytes(), 'sid_of': lr.sid_of.tobytes(),
                'cls': {'%d' % d: lr.cls[(stamp, d)].tobytes() for d in range(1, 7)}}
        PC.SCRATCH.mkdir(parents=True, exist_ok=True)
        with gzip.open(PC.SCRATCH / ('classes_%s_%s.pkl.gz' % (a.law, stamp)), 'wb') as fh:
            pickle.dump(meta, fh, protocol=4)
        log('stamp %s done: least distance with no confusable pair %s; with a rule that counts %s' % (
            stamp, {p: tabs['least_distance_no_confusable_pair'][p] for p in groups and
                    ([p for p in ('P1P2 | holds', 'P1P2 | fails', 'P2 | holds', 'P1 | holds', 'P3') if p in pops])},
            {p: tabs['least_distance_rule_counted'][p] for p in
             [p for p in ('P1P2 | holds', 'P1P2 | fails', 'P2 | holds', 'P1 | holds', 'P3') if p in pops]}))
    log('done; peak %.1f MB' % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0))


if __name__ == '__main__':
    main()
