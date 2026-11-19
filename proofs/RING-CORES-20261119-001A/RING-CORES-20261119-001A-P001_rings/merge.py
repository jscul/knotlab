"""Merge RING-CORES-20261119-001A-P001's machine check.  python3 -B merge.py <runner out dir> <machine_check.json> <result.json>"""
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'scripts'))
from longrun import load_results  # noqa: E402


def main():
    R = load_results(sys.argv[1])
    bad_cases = [c for c, r in R.items() if r.get('status') != 'ok']
    by_L = defaultdict(list)
    classify = {}
    for cid, r in sorted(R.items()):
        if r.get('status') != 'ok':
            continue
        if cid.startswith('ring'):
            by_L[int(cid.split('-')[1])] += r['result']['words']
        else:
            classify[int(cid.split('-')[1])] = r['result']
    table, fails = {}, []
    for L, ws in sorted(by_L.items()):
        rounds = [w['rounds'] for w in ws]
        exp = [w for w in ws if not w['bare']]
        row = {'words': len(ws), 'in_class': sum(w['class'] == 'in' for w in ws), 'forced': sum(w['forced'] for w in ws),
               'max_places': max(w['max_places'] for w in ws), 'bare': sum(w['bare'] for w in ws),
               'reading_ok': sum((w['reading'] == 'dimension 1') if w['bare'] else (w['reading'] == 'exponential') for w in ws),
               'engine_equals_formula': sum(w['engine_equals_formula'] for w in ws), 'closed_equals_direct': sum(w['closed_equals_direct'] for w in ws),
               'rounds_min': min(rounds), 'rounds_median': statistics.median(rounds),
               'rate_min': min((w['rate'] for w in exp), default=None), 'rate_max': max((w['rate'] for w in exp), default=None),
               'distinct_rates': len({round(w['rate'], 9) for w in exp})}
        table[L] = row
        n = row['words']
        for k, name in (('in_class', 'K1 class'), ('forced', 'K1 forced'), ('reading_ok', 'K2'), ('engine_equals_formula', 'K3'), ('closed_equals_direct', 'K4')):
            if row[k] != n:
                fails.append(f'{name} at L = {L}: {row[k]} of {n}')
        if row['max_places'] > 5:
            fails.append(f'K1 places at L = {L}')
    # K5: the advisor's predicted rates
    def find(L, pred):
        return sorted({round(w['rate'], 4) for w in by_L.get(L, []) if pred(w['word'])})
    sp = lambda w: sum(1 for x in w if x[0] == 'P' and x[1] == 1)  # noqa: E731
    lv = lambda w: [x[1] for x in w if x[0] == 'L']  # noqa: E731
    k5 = {'C5 two spares (predicted 1.2628)': find(5, lambda w: sp(w) == 2 and not lv(w)),
          'C7 leaf b = 1 and one spare (predicted 1.2377)': find(7, lambda w: lv(w) == [1] and sp(w) == 1),
          'C9 three leaves b = 0 (predicted 1.2207)': find(9, lambda w: lv(w) == [0, 0, 0] and sp(w) == 0),
          'C14 one spare (predicted 1.0970)': find(14, lambda w: sp(w) == 1 and not lv(w))}
    k6 = {n: v['tally'] for n, v in classify.items()}
    k6_bad = {n: v['bad'] for n, v in classify.items() if v['bad']}
    if k6_bad:
        fails.append('K6')
    if bad_cases:
        fails.append(f'cases not ok: {bad_cases}')
    rates = Counter()
    for L, ws in by_L.items():
        for w in ws:
            if not w['bare']:
                rates[round(w['rate'], 4)] += 1
    out = {'table': table, 'K5': k5, 'K6': k6, 'K6_bad': k6_bad, 'fastest': rates.most_common(1) and max(rates),
           'slowest': rates and min(rates), 'distinct_rates': len(rates), 'failures': fails}
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, default=str) + '\n')
    res = {'schema_version': 3, 'artifact_id': 'RING-CORES-20261119-001A-P001', 'kind': 'proof', 'ticket': 'RING-CORES-20261119-001A',
           'proof': 'RING-CORES-20261119-001A-P001', 'status': 'passed' if not fails else 'failed',
           'checks': {'K1_K4_by_L': table, 'K5': k5, 'K6': k6}, 'failures': fails}
    Path(sys.argv[3]).write_text(json.dumps(res, indent=1, default=str) + '\n')
    print(json.dumps({'failures': fails, 'K5': k5}, indent=1))
    for L, row in table.items():
        print(L, row)
    print({n: v for n, v in k6.items()})


if __name__ == '__main__':
    main()
