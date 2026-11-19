"""Merge REDUCE-BLOCKS-20261119-001A-P001's machine check.  python3 -B merge.py <out dir>[,<out dir>...] <machine_check.json> <result.json>
(a later directory's ok case replaces an earlier error: the census amendment run)"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'scripts'))
from longrun import load_results  # noqa: E402


def main():
    R = {}
    for d in sys.argv[1].split(','):
        for cid, r in load_results(d).items():
            if cid not in R or R[cid].get('status') != 'ok':
                R[cid] = r
    not_ok = [c for c, r in R.items() if r.get('status') != 'ok']
    T = {'census': Counter(), 'rand': Counter(), 'stage': Counter()}
    bad = {'census': [], 'rand': [], 'stage': []}
    for cid, r in sorted(R.items()):
        if r.get('status') != 'ok':
            continue
        k = cid.split('-')[0]
        T[k].update(r['result']['tally'])
        bad[k] += r['result']['bad']
    fails = [f'H{i + 1}' for i, k in enumerate(('census', 'rand', 'stage')) if T[k]['differ'] > 0]
    if not_ok:
        fails.append(f'cases not ok: {not_ok}')
    out = {'H1': dict(T['census']), 'H2': dict(T['rand']), 'H3': dict(T['stage']), 'bad': bad, 'failures': fails}
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1) + '\n')
    res = {'schema_version': 3, 'artifact_id': 'REDUCE-BLOCKS-20261119-001A-P001', 'kind': 'proof', 'ticket': 'REDUCE-BLOCKS-20261119-001A',
           'proof': 'REDUCE-BLOCKS-20261119-001A-P001', 'status': 'passed' if not fails else 'failed',
           'checks': {k: out[k] for k in ('H1', 'H2', 'H3')}, 'failures': fails}
    Path(sys.argv[3]).write_text(json.dumps(res, indent=1) + '\n')
    print(json.dumps(out, indent=1)[:3000])


if __name__ == '__main__':
    main()
