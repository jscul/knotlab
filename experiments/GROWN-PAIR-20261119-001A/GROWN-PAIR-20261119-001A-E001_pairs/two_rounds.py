"""After other_states.py (not a prediction): for the other-state grown groups whose next stages had isomorphic tables, the stage two
rounds on (round + 2 from the same start), compared the same way (P4 says "within two rounds").
Run: .venv/bin/python -B two_rounds.py runs/grown-pair -> two_rounds.json beside the artifacts."""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts'))
import pairs2 as P2  # noqa: E402
from longrun import load_results  # noqa: E402
A = ROOT / 'artifacts/GROWN-PAIR-20261119-001A/GROWN-PAIR-20261119-001A-E001_pairs'


def main(out_dir):
    recs = load_results(out_dir)
    by_prov = {(st['index'], st['round']): st['stars'] for c, r in recs.items() if r['status'] == 'ok' for st in r['result']['stages']}
    groups = json.loads((A / 'other_states.json').read_text())['group_list']
    res = Counter()
    for g in groups:
        if not g['next_tables_isomorphic']:
            continue
        nxt = []
        for c in g['reps']:
            i, r = next((i, r) for i, r in c['prov'] if r > 0)
            nxt.append(by_prov.get((i, r + 2)))
        if not all(nxt):
            res['round_plus_2_missing'] += 1
            continue
        gs = [P2.coloured_table([frozenset(s) for s in n]) for n in nxt]
        if all(P2.iso(gs[0], x) for x in gs[1:]):
            cs = [P2.coloured_table([frozenset(s) for s in n], True) for n in nxt]
            res['tables_isomorphic_states_' + ('agree' if all(P2.iso(cs[0], x) for x in cs[1:]) else 'differ')] += 1
        else:
            res['tables_differ'] += 1
    (A / 'two_rounds.json').write_text(json.dumps(dict(res), indent=1))
    print(dict(res))


if __name__ == '__main__':
    main(sys.argv[1])
