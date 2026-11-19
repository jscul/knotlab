"""Score NATIVE-SPINE-20261119-001B-E001.  python3 -B merge.py <runner out dir> <results.json>"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'scripts'))
from longrun import load_results  # noqa: E402


def main():
    R = load_results(sys.argv[1])
    rows = {c: r['result'] for c, r in sorted(R.items()) if r.get('status') == 'ok'}
    out = {'cases': len(R), 'ok': len(rows), 'not_ok': [c for c, r in R.items() if r.get('status') != 'ok']}
    out['S1'] = {c: all(not x['N']['perfect'] for x in r['rows']) for c, r in rows.items()}
    out['S2'] = {c: all(not x['M']['perfect'] for x in r['rows']) for c, r in rows.items()}
    out['S3'] = {c: all(not x['F']['perfect'] for x in r['rows']) for c, r in rows.items()}
    out['S4'] = {c: all(x['forced'] is not None and x['forced'] < 1 for x in r['rows'] if x['t'] >= 6) for c, r in rows.items()}
    out['S5_starts'] = {c: any(x['M']['collided_singles'] > 0 for x in r['rows'] if x['t'] <= 13) for c, r in rows.items()}
    out['S5'] = sum(out['S5_starts'].values()) >= 8
    for k in ('S1', 'S2', 'S3', 'S4'):
        out[k + '_pass'] = len(out[k]) == 10 and all(out[k].values())
    out['readouts'] = {c: [{'t': x['t'], 'count': x['count'], 'forced': x['forced'], 'null_perfect': x.get('null_perfect'),
                            **{r: {k: x[r][k] for k in ('left_with_one', 'ties', 'single_depth2', 'collided_singles',
                                                        'right_hit_once', 'kept_depth2_share')} for r in 'MF'}}
                           for x in r['rows']] for c, r in rows.items()}
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: out[k] for k in ('ok', 'not_ok', 'S1_pass', 'S2_pass', 'S3_pass', 'S4_pass', 'S5')}))


if __name__ == '__main__':
    main()
