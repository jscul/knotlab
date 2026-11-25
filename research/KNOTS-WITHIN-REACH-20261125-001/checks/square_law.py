"""The thread's later look inside the one-round counts that the study's registered reading labelled "undecided".

Reads the study's own raw records (run2.jsonl.gz) and tests every one-round count P(u, r) against 3r^2 + 3r + 1,
the count of a six-regular pattern.  No growth is rerun.  Run from anywhere:
  .venv/bin/python -B research/KNOTS-WITHIN-REACH-20261125-001/checks/square_law.py
Writes square_law.json beside itself.
"""
import collections
import gzip
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
RUN2 = os.path.join(ROOT, 'artifacts', 'KNOTS-WITHIN-REACH-20261125-001A',
                    'KNOTS-WITHIN-REACH-20261125-001A-E001_knots_within_reach', 'run2.jsonl.gz')


def six_regular(r):
    return 3 * r * r + 3 * r + 1


def main():
    labels = collections.Counter()
    rows = collections.defaultdict(list)
    facts = {}
    with gzip.open(RUN2, 'rt') as f:
        for line in f:
            d = json.loads(line)
            if d['kind'] not in ('census', 'named', 'P only'):
                continue
            for which in ('at_T', 'at_2T'):
                at = d.get(which) or {}
                P = at.get('P') if isinstance(at, dict) else None
                if not isinstance(P, dict):
                    continue
                cf = P.get('counted_from') or []
                for v in (cf.values() if isinstance(cf, dict) else cf):
                    if not isinstance(v, dict) or 'P' not in v:
                        continue
                    seq = v['P']
                    n = 0
                    while n < len(seq) and seq[n] == six_regular(n):
                        n += 1
                    exact_through = n - 1
                    labels[(d['law'], v.get('label'), exact_through >= 5)] += 1
                    if exact_through >= 5:
                        key = f"{d['law']} | {d['start']} | round {at.get('round')}"
                        rows[key].append({'member': v.get('member'), 'exact through r': exact_through,
                                          'label': v.get('label'), 'counts': seq[:exact_through + 2]})
                        facts[key] = {'members of the part': P.get('members'), 'parts': d['parts_per_round'][-1],
                                      'births per round, polynomial in the round (constant, linear, quadratic)':
                                          d['births_reading'].get('poly'),
                                      'members per round, first 12': d['members_per_round'][:12]}
    out = {'what': 'one-round counts equal to 3r^2 + 3r + 1 from r = 0 through at least r = 5',
           'readings by law, label, and whether they match': {f'{k[0]} | {k[1]} | {k[2]}': n for k, n in sorted(labels.items(), key=str)},
           'matching readings': sum(len(v) for v in rows.values()),
           'longest exact match (r)': max(x['exact through r'] for v in rows.values() for x in v),
           'runs': {k: {'facts': facts[k], 'exact through r, by sampled member': sorted(x['exact through r'] for x in v),
                        'members': v} for k, v in sorted(rows.items())}}
    with open(os.path.join(HERE, 'square_law.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print(out['matching readings'], 'readings match;', 'longest through r =', out['longest exact match (r)'])
    for k, v in out['runs'].items():
        print(k, v['exact through r, by sampled member'], v['facts']['members of the part'])


if __name__ == '__main__':
    main()
