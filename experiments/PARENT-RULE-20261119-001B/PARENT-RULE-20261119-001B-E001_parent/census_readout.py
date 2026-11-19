"""PARENT-RULE-20261119-001B part C read-out.  Run: .venv/bin/python -B census_readout.py runs/parent-census -> census.json."""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402


def main(out_dir):
    recs = load_results(out_dir)
    c = Counter()
    ex = []
    status = Counter(r['status'] for r in recs.values())
    for cid, r in sorted(recs.items()):
        if r['status'] != 'ok':
            continue
        c.update(r['result']['counts'])
        ex += r['result']['examples']
    verdict = {
        'C1': c['viol_P1+'] == 0 and c['viol_P2'] == 0 and c['peel_not_previous'] == 0 and c['depth_below_round'] == 0,
        'C2': c['Q_once_larger'] == 0 and c['Q_two_larger'] == 0,
        'R1': c['R_full_once_open_not_rigid'] == 0 and c['R_full_once_open_capped'] == 0,
    }
    out = {'shards': dict(status), 'counts': dict(sorted(c.items())), 'verdicts': verdict, 'examples': ex[:40]}
    dest = ROOT / 'artifacts/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent'
    (dest / 'census.json').write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != 'examples'}, indent=1))
    print(Counter(e['violation'] for e in ex))


if __name__ == '__main__':
    main(sys.argv[1])
