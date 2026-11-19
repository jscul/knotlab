"""Merge DEAD-CAP-20261119-001A-P001's machine check.  python3 -B merge.py <runner out dir> <machine_check.json> <result.json>"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'scripts'))
from longrun import load_results  # noqa: E402

THETA = 2.3830


def main():
    R = load_results(sys.argv[1])
    not_ok = [c for c, r in R.items() if r.get('status') != 'ok']
    d1 = Counter()
    d1_bad = []
    starts = defaultdict(list)
    tries = Counter()
    for cid, r in sorted(R.items()):
        if r.get('status') != 'ok':
            continue
        res = r['result']
        if cid.startswith('d1'):
            for k, v in res['tally'].items():
                d1[k] += v
            d1_bad += res['bad']
        else:
            key = cid.split('-')[0]
            starts[key] += res['starts']
            tries[key] += res.get('tries', 0)
    fails = []
    if d1_bad:
        fails.append(f'D1: {len(d1_bad)}')
    summary = {}
    allst = [x for v in starts.values() for x in v]
    for key, v in starts.items():
        ranks = Counter(max(x['ranks']) for x in v)
        summary[key] = {'starts': len(v), 'counts_equal': sum(x['counts_equal'] for x in v), 'reading_agree': sum(x['agree_reading'] for x in v),
                        'by_top_rank': dict(sorted(ranks.items())), 'readings': dict(Counter(x['reading'] for x in v)),
                        'rounds_min': min((x['rounds'] for x in v), default=None), 'd4': [sum(sum(x['d4']) for x in v), sum(len(x['d4']) for x in v)],
                        'max_rate': max((x['rate'] for x in v), default=None), 'max_dead': max((x['dead'] for x in v), default=None)}
        if summary[key]['counts_equal'] != len(v):
            fails.append(f'D2 {key}: {len(v) - summary[key]["counts_equal"]}')
        if summary[key]['reading_agree'] != len(v):
            fails.append(f'D3 {key}: {len(v) - summary[key]["reading_agree"]}')
        if summary[key]['d4'][0] != summary[key]['d4'][1]:
            fails.append(f'D4 {key}')
    fam = {x['tag']: x for x in starts.get('fam', [])}
    th = fam.get('theta', {})
    d5 = (th.get('ranks') and max(th['ranks']) == 2 and th['counts_equal'] and abs(th['rate'] - THETA) < 1e-3
          and all(fam[f'T_{h}']['counts_equal'] and fam[f'T_{h}']['reading'] == f'dimension {3 * 2 ** (h - 1)}' for h in (1, 2, 3)))
    if not d5:
        fails.append('D5')
    over = [x for x in allst if x['tag'] in ('rand', 'skel', 'census') and x['rate'] > THETA + 1e-6]
    d6 = not over
    smallest_rank2 = min((x['n'] for x in allst if max(x['ranks']) >= 2), default=None)
    rates_rank2 = sorted({round(x['rate'], 4) for x in allst if max(x['ranks']) >= 2})
    out = {'not_ok': not_ok, 'D1': dict(d1), 'D1_bad': d1_bad[:20], 'summary': summary, 'tries': dict(tries), 'D5': d5,
           'theta': {k: th.get(k) for k in ('counts_equal', 'rate', 'rounds', 'series_to_25')}, 'D6_holds': d6,
           'D6_faster': [[x['n'], x['rate'], x['ranks'], x['sizes'], x['edges']] for x in over[:10]],
           'smallest_rank2_sampled': smallest_rank2, 'rank2_rates': rates_rank2[:40], 'n_rank2_rates': len(rates_rank2),
           'failures': fails}
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, default=str) + '\n')
    res = {'schema_version': 3, 'artifact_id': 'DEAD-CAP-20261119-001A-P001', 'kind': 'proof', 'ticket': 'DEAD-CAP-20261119-001A',
           'proof': 'DEAD-CAP-20261119-001A-P001', 'status': 'passed' if not fails else 'failed',
           'checks': {'D1': dict(d1), 'D2_D4': summary, 'D5': d5, 'D6_holds': d6}, 'failures': fails}
    Path(sys.argv[3]).write_text(json.dumps(res, indent=1, default=str) + '\n')
    print(json.dumps({k: out[k] for k in ('not_ok', 'D1', 'summary', 'D5', 'theta', 'D6_holds', 'smallest_rank2_sampled', 'n_rank2_rates', 'failures')}, indent=1, default=str)[:6000])


if __name__ == '__main__':
    main()
