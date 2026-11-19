"""Merge WALL-READ-20261119-001A-P001's machine-check run into machine_check.json: python3 -B merge.py <out dir> <machine_check.json>."""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402


def main(out, dest):
    R = load_results(out)
    bad_status = {k: v.get('status') for k, v in R.items() if v.get('status') != 'ok'}
    res = {k: v['result'] for k, v in R.items() if v.get('status') == 'ok'}
    m1 = {k: {x: r[x] for x in ('n', 'T', 'predicted_keys', 'predicted_next', 'next_parents', 'engine_ok', 'roster_ok',
                                'engine_next_ok', 'roster_next_ok', 'engine_end', 'roster_end', 'hub_knots', 'max_places')}
          for k, r in res.items() if k.startswith('part-')}
    m2 = {k: r['ok'] for k, r in res.items() if k.startswith('ctl-')}
    tally, kseen, bad = Counter(), Counter(), []
    for k, r in res.items():
        if k.startswith('lem-'):
            tally.update(r['tally'])
            kseen.update({int(a): b for a, b in r['k_any'].items()})
            bad += r['bad']
    out_ = {
        'M1': {'cases': m1, 'held': bool(m1) and all(v['engine_ok'] and v['roster_ok'] and v['engine_next_ok'] and v['roster_next_ok']
                                                    for v in m1.values()) and len(m1) == 3},
        'M2': {'cases': m2, 'held': len(m2) == 5 and all(m2.values())},
        'M3_M4': {'tally': dict(tally), 'k_any': dict(sorted(kseen.items())), 'bad': bad[:20],
                  'M3_held': tally.get('lemma2 FAIL', 0) == 0 and tally.get('stages', 0) > 0,
                  'M4_held': tally.get('lemma3 FAIL', 0) == 0},
        'not_ok': bad_status,
    }
    Path(dest).write_text(json.dumps(out_, indent=1) + '\n')
    print(json.dumps({k: (v['held'] if 'held' in v else {x: v[x] for x in v if x.endswith('held')}) if isinstance(v, dict) else v
                      for k, v in out_.items()}, indent=1))
    print(json.dumps(out_['M3_M4']['tally']))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
