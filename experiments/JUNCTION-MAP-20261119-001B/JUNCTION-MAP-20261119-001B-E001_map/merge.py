"""Score JUNCTION-MAP-20261119-001B-E001.  python3 -B merge.py <runner out dir> <results.json>"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'scripts'))
from longrun import load_results  # noqa: E402


def main():
    R = load_results(sys.argv[1])
    rows = {c: r['result'] for c, r in sorted(R.items()) if r.get('status') == 'ok'}
    out = {'cases': len(R), 'ok': len(rows), 'not_ok': [c for c, r in R.items() if r.get('status') != 'ok']}
    st = [(c, s) for c, x in rows.items() for s in x['stages']]
    out['G'] = {'stages': len(st), 'held': sum(s['gate'] for _, s in st)}
    out['G']['pass'] = out['G']['held'] == len(st)
    out['status'] = dict(Counter(s['status'] for _, s in st))
    ov = [(c, s) for c, s in st if s['status'] == 'overlap']
    j1 = [isinstance(s['map'], list) and s['map'][0] == 1 for _, s in ov]
    out['J1'] = {'n': len(ov), 'held': sum(j1), 'misses': [[c, s['s'], s['map']] for (c, s), ok in zip(ov, j1) if not ok][:10],
                 'pass': all(j1) and len(j1) > 0}
    cl = [(c, s) for c, s in st if s['status'] == 'clean']
    j2 = [isinstance(s['map'], list) and s['map'][0] is None for _, s in cl]
    out['J2'] = {'n': len(cl), 'held': sum(j2), 'misses': [[c, s['s'], s['map']] for (c, s), ok in zip(cl, j2) if not ok][:10],
                 'pass': all(j2) and len(j2) > 0}
    br = [(c, x) for c, x in rows.items() if c[0] in 'BF']
    j3 = [isinstance(x['J3'], list) and x['J3'][0] is not None and x['J3'][0] <= 2 for _, x in br]
    out['J3'] = {'n': len(br), 'held': sum(j3), 'pass': all(j3) and len(j3) > 0}
    out['verdicts'] = {k: out[k]['pass'] for k in ('G', 'J1', 'J2', 'J3')}
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1))
    print(json.dumps(out['verdicts']), json.dumps(out['status']))


if __name__ == '__main__':
    main()
