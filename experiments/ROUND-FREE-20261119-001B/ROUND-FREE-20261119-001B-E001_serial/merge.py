"""Score ROUND-FREE-20261119-001B-E001.  python3 -B merge.py <runner out dir> <results.json>"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402
_spec = importlib.util.spec_from_file_location('rf_job', HERE / 'job.py')
job = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(job)
GROWING = ['pair33', 'pair44', 'chain333', 'ring44445', 'ring55555', 'ring-pair', 'two-rings']


def main():
    R = load_results(sys.argv[1])
    res = {cid: r['result'] for cid, r in R.items() if r.get('status') == 'ok'}
    out = {'P1': {}, 'P2': {}, 'P3': {}, 'per_start': {}}
    for s in list(job.starts()):
        rd = res.get(f'{s}-round')
        row = {'round_by_rank': rd['by_rank'][:12] if rd else None, 'round_outcome': rd and rd['outcome']}
        for law in ('uniform', 'joins-first'):
            runs = [res.get(f'{s}-{law}-{sd:02d}') for sd in range(20)]
            sigs = {json.dumps([r['by_rank'], r['parents_fresh']]) for r in runs if r}
            outs = [r['outcome'] for r in runs if r]
            first4 = [r['by_rank'][:4] for r in runs if r]
            row[law] = {'distinct_structures': len(sigs), 'outcomes': {o: outs.count(o) for o in set(outs)},
                        'any_matches_round_ranks_0_3': any(f == rd['by_rank'][:4] for f in first4) if rd else None,
                        'examples': [r['by_rank'][:10] for r in runs[:4] if r]}
            if s in GROWING:
                out['P1'][f'{s}/{law}'] = len(sigs) >= 2
                out['P2'][f'{s}/{law}'] = not row[law]['any_matches_round_ranks_0_3']
        out['per_start'][s] = row
    u = out['per_start']['pair33']['uniform']['outcomes']
    out['P3'] = {'closes_in_some': u.get('closed', 0) >= 1, 'grows_past_400_in_some': u.get('cap', 0) >= 1, 'outcomes': u}
    out['verdict'] = {'P1': all(out['P1'].values()), 'P2': all(out['P2'].values()),
                      'P3': out['P3']['closes_in_some'] and out['P3']['grows_past_400_in_some']}
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1))
    print(json.dumps(out['verdict']), json.dumps(out['P1']), json.dumps(out['P2']), json.dumps(out['P3']))


if __name__ == '__main__':
    main()
