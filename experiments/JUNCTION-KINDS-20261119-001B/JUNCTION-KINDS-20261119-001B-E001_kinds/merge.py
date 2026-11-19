"""Score JUNCTION-KINDS-20261119-001B-E001.  python3 -B merge.py <runner out dir> <results.json>"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'scripts'))
from longrun import load_results  # noqa: E402


def thirds_rise(v):
    if len(v) < 6:
        return None
    k = len(v) // 3
    return max(v[-k:]) > max(v[:k])


def main():
    R = load_results(sys.argv[1])
    rows = {c: r['result'] for c, r in sorted(R.items()) if r.get('status') == 'ok'}
    out = {'cases': len(R), 'ok': len(rows), 'not_ok': [c for c, r in R.items() if r.get('status') != 'ok']}
    out['J1'] = {c: thirds_rise(r['shares']) for c, r in rows.items()}
    out['J1_pass'] = all(v for v in out['J1'].values())
    out['J2'] = {c: thirds_rise(r['kinds']) for c, r in rows.items()}
    out['J2_pass'] = all(v for v in out['J2'].values())
    j3 = {}
    for c, r in rows.items():
        if c[0] == 'T':          # a perfect matching at every round from 4 on, and the recurrence holds at every one of them
            want = list(range(4, len(r['counts'])))
            j3[c] = r['recurrence_rounds'] == want and all(h['matched'] == h['left'] == h['right'] for h in r['hall'])
        elif c[0] == 'C':        # a matching saturating the smaller side at every round past the lags
            j3[c] = len(r['hall']) > 0 and all(h['matched'] == min(h['left'], h['right']) for h in r['hall'])
    out['J3'] = j3
    out['J3_pass'] = all(j3.values())
    j4 = {c: len(r.get('spines_both_halves', [])) for c, r in rows.items() if c[0] == 'T'}
    out['J4'] = j4
    out['J4_pass'] = all(v == 0 for v in j4.values()) and len(j4) == 10
    j5 = {}
    for c, r in rows.items():
        d = r['d']
        if c[0] == 'T':
            j5[c] = all(x == 0 for x in d[1:])           # t >= 4
        elif c[0] == 'Q':
            nz = [i for i, x in enumerate(d) if x != 0]
            rec = all(d[i] == -d[i - 2] - d[i - 3] for i in range(max(3, 6), len(d)))
            j5[c] = bool(nz) and rec
    out['J5'] = j5
    out['J5_pass'] = all(j5.values())
    out['readouts'] = {c: {'shares': r['shares'], 'kinds': r['kinds'], 'single_matched': [(h['t'], h['single_matched'], h['left'])
                                                                                          for h in r['hall']],
                           'spines_first_half': r.get('spines_first_half'), 'types': r.get('types')} for c, r in rows.items()}
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: out[k] for k in ('ok', 'not_ok', 'J1_pass', 'J2_pass', 'J3_pass', 'J4_pass', 'J5_pass')}))


if __name__ == '__main__':
    main()
