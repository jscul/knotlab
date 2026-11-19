"""Score EXPLOSIVE-20261119-001B-E001.  python3 -B merge.py <runner out dir> <results.json>"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'scripts'))
from longrun import load_results  # noqa: E402


def main():
    R = load_results(sys.argv[1])
    not_ok = [c for c, r in R.items() if r.get('status') != 'ok']
    pop = defaultdict(list)
    tries = Counter()
    for cid, r in sorted(R.items()):
        if r.get('status') != 'ok':
            continue
        for x in r['result']['starts']:
            key = x['tag'] if not x['tag'].startswith('ref') else 'ref'
            pop[key].append(x)
        tries[cid] = r['result'].get('tries')
    out = {'not_ok': not_ok, 'tries': dict(tries), 'populations': {}}
    x1_fail, x1b_fail = [], []
    def dimof(m):
        return m.split(' (')[0]
    for key, v in pop.items():
        filled0 = [x for x in v if all(b == 0 for b in x['b1'])]
        cyc = [x for x in v if any(b > 0 for b in x['b1'])]
        settled0 = [x for x in filled0 if x['measured'] != 'undecided']
        agree = [x for x in settled0 if x['reading'] == dimof(x['measured'])]
        x1_fail += [x for x in settled0 if x['reading'] != dimof(x['measured'])]
        settled1 = [x for x in cyc if x['measured'] != 'undecided']
        x1b_fail += [x for x in settled1 if x['measured'] == 'closes' or x['measured'].startswith('dimension')]
        expl = [x for x in v if x['measured'] == 'explosive']
        out['populations'][key] = {
            'starts': len(v), 'by_cycles_of_three': dict(Counter(min(x['tri'], 6) for x in v)),
            'filled_b1_zero': len(filled0), 'settled_b1_zero': len(settled0), 'agree_b1_zero': len(agree),
            'filled_b1_positive': len(cyc), 'settled_b1_positive': len(settled1),
            'b1_positive_measured': dict(Counter(x['measured'] for x in cyc)),
            'measured': dict(Counter(x['measured'] for x in v)),
            'explosive': len(expl),
            'explosive_features': dict(Counter((max(x['b1']) > 0, max(x['b2']) > 0, x['overlap_point'], x['overlap_block']) for x in expl)),
            'largest_group_max': max((max(x['groups']) for x in v), default=None),
            'largest_group_b1_zero_max': max((max(x['groups']) for x in filled0), default=None)}
    expl_all = sorted([x for k, v in pop.items() if k != 'ref' for x in v if x['measured'] == 'explosive'], key=lambda x: (x['n'], sum(x['sizes'])))
    out['smallest_explosive'] = [{k: x[k] for k in ('tag', 'n', 'sizes', 'edges', 'tri', 'b1', 'b2', 'overlap_point', 'overlap_block', 'counts', 'groups', 'outcome')} for x in expl_all[:5]]
    out['ref'] = [{k: x[k] for k in ('tag', 'n', 'max_places', 'tri', 'b1', 'b2', 'overlap_point', 'overlap_block', 'reading', 'measured', 'counts', 'groups')} for x in pop.get('ref', [])]
    out['X1'] = not x1_fail
    out['X1b'] = not x1b_fail
    out['X1b_failures'] = [{k: x[k] for k in ('tag', 'n', 'sizes', 'edges', 'reading', 'measured', 'counts')} for x in x1b_fail[:10]]
    out['X1_failures'] = [{k: x[k] for k in ('tag', 'n', 'sizes', 'edges', 'reading', 'measured', 'counts')} for x in x1_fail[:10]]
    out['X2'] = out['populations'].get('cap5', {}).get('explosive', 0) == 0 and out['populations'].get('cycle5', {}).get('explosive', 0) == 0
    out['X3'] = out['populations'].get('cap7', {}).get('explosive', 0) >= 1
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, default=str) + '\n')
    print(json.dumps({k: out[k] for k in ('not_ok', 'X1', 'X1b', 'X2', 'X3', 'populations')}, indent=1)[:6000])
    print('smallest explosive:', json.dumps(out['smallest_explosive'][:2])[:1500])


if __name__ == '__main__':
    main()
