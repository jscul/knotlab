"""Score BREAK-EDDIES-20261119-001B-E001.  python3 -B merge.py <runner out dir> <results.json>"""
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402

PILOT_EXPLOSIVE = {0, 4, 5, 6}


def main():
    R = load_results(sys.argv[1])
    rows = [r['result'] for c, r in sorted(R.items()) if r.get('status') == 'ok']
    out = {'cases': len(R), 'ok': len(rows), 'not_ok': [c for c, r in R.items() if r.get('status') != 'ok']}
    prov = json.loads((HERE / 'pilot/grown_long.json').read_text())
    key = lambda st: (tuple(st['sizes']), tuple(map(tuple, st['edges'])))  # noqa: E731
    pidx = {key(p): i for i, p in enumerate(prov)}
    rational = [r for r in rows if r['recurrence'] and r['recurrence'].get('W')]
    out['rational'] = len(rational)
    out['families'] = defaultdict(int)
    for r in rational:
        out['families'][str(r['recurrence']['W'])] += 1
    out['families'] = dict(sorted(out['families'].items(), key=lambda kv: -kv[1]))
    # B1: pilot-rational starts keep their recurrence (same factor) to the new horizon
    b1 = []
    for r in rows:
        i = pidx.get(key(r['start']))
        if i is None or i in PILOT_EXPLOSIVE:
            continue
        b1.append(bool(r['recurrence'] and r['recurrence'].get('W')) and len(r['counts']) > len(prov[i]['counts']) - 1)
    out['B1'] = {'n': len(b1), 'held': sum(b1), 'pass': all(b1) and len(b1) > 0}
    good = lambda W: all(isinstance(w, int) and w >= 0 for w in W) and sum(W) >= 2  # noqa: E731
    out['B2'] = {'n': len(rational), 'held': sum(good(r['recurrence']['W']) for r in rational)}
    out['B2']['pass'] = out['B2']['held'] == len(rational)
    out['B3'] = {'max_group_by_round_40': sorted({r['group'][min(39, len(r['group']) - 1)] for r in rational if r['group']})}
    exp_rows = [r for r in rows if pidx.get(key(r['start'])) in PILOT_EXPLOSIVE]
    b4 = []
    for r in exp_rows:
        ok = False
        for t in range(len(r['group'])):
            others = [q['group'][t] for q in rational if len(q['group']) > t]
            if others and r['group'][t] > max(others):
                ok = True
                break
        b4.append(ok)
    out['B4'] = {'n': len(b4), 'held': sum(b4), 'groups': [r['group'] for r in exp_rows], 'pass': all(b4) and len(b4) == 4}
    theta = [r for r in rows if pidx.get(key(r['start'])) == 0]
    out['B5'] = {'theta_counts': theta[0]['counts'] if theta else None,
                 'theta_recurrence': theta[0]['recurrence'] if theta else None,
                 'pass': bool(theta) and (theta[0]['recurrence'] is None or theta[0]['recurrence'].get('order', 99) > 8)}
    b6 = []
    for r in rational:
        W = r['recurrence']['W']
        L = next(k for k, w in enumerate(W) if w)
        if L <= 3:
            b6.append(bool(r['group']) and r['group'][0] >= 3)      # round 1's largest group: three or more parents
    out['B6'] = {'n': len(b6), 'held': sum(b6), 'pass': all(b6) and len(b6) > 0}
    by_touch = defaultdict(list)
    for r in rational:
        W = r['recurrence']['W']
        by_touch[tuple(map(tuple, r['start']['edges']))].append((r['start']['sizes'], next(k for k, w in enumerate(W) if w)))
    b7 = []
    for lst in by_touch.values():
        for a, La in lst:
            for b, Lb in lst:
                d = [y - x for x, y in zip(a, b)]
                if sorted(d) == [0] * (len(d) - 1) + [1]:
                    b7.append(Lb <= La)
    out['B7'] = {'pairs': len(b7), 'held': sum(b7), 'pass': all(b7)}
    out['B8'] = {'stages_in_scope': sum(1 for r in rows if any(s in ('eddy', 'no eddy') for s in r['stages'])), 'n': len(rows)}
    out['B8']['pass'] = out['B8']['stages_in_scope'] == 0
    out['stops'] = dict(sorted(((s, sum(1 for r in rows if r['stop'] == s)) for s in {r['stop'] for r in rows})))
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: out[k].get('pass') for k in ('B1', 'B2', 'B4', 'B5', 'B6', 'B7', 'B8')}))


if __name__ == '__main__':
    main()
