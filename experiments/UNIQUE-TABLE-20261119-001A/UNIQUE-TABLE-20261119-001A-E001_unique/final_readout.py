"""UNIQUE-TABLE-20261119-001A final classification, after realize.py (not a prediction): every population and control stage is
one of
- other_states: a legal arrangement (B1-B4) with different equations and the same exact table exists (realize.json);
- same_states: a legal arrangement with the same equations and other junctions exists (B4 applied);
- unique: neither, and the bound is decided (forcing spans the equations, or the one-missing search is exhaustive);
- undecided.
Also the 3-connected criterion corrected after the run: a same-equation rival exists exactly when the loose set has at least three
distinctions and at most one junction holds two or more loose ones (that junction becoming the outside).
Run: .venv/bin/python -B final_readout.py runs/unique-table runs/unique-table-amend  -> final.json beside the artifacts."""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts'))
import uniq as U  # noqa: E402
from longrun import load_results  # noqa: E402
A = ROOT / 'artifacts/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique'


def main(*dirs):
    recs = {}
    for d in dirs:
        for c, r in load_results(d).items():
            if c not in recs or r['status'] == 'ok':
                recs[c] = r
    real = json.loads((A / 'realize.json').read_text())
    other = {x['case'] for x in real['other_codes'] if x['legal_realizations']}
    code_only = {x['case'] for x in real['other_codes'] if not x['legal_realizations']}
    out = {'cases': dict(Counter(r['status'] for r in recs.values()))}
    rows = {'population': [], 'controls': []}
    for c, r in sorted(recs.items()):
        if c.startswith('dev'):
            continue
        part = 'population' if c.startswith('pop') else 'controls'
        if r['status'] != 'ok':
            rows[part].append((c, None))
            continue
        rows[part].append((c, r['result']))
    for part, items in rows.items():
        cls = Counter()
        by_conn = {}
        for c, res in items:
            if res is None:
                k = 'not_run'
            else:
                stars = U.stage(res['key'], res['round'])
                n = len(stars)
                same = 0
                if res['same_code_rivals']:
                    rivals, _, _ = U.same_code_rivals(stars)
                    same = sum(1 for x in rivals if len(x) <= n)
                decided = res['forced_spans_C'] or (res.get('one_missing', {}).get('applicable')
                                                    and not res['one_missing'].get('capped'))
                if c in other:
                    k = 'other_states'
                elif same:
                    k = 'same_states'
                elif decided:
                    k = 'unique'
                else:
                    k = 'undecided'
                by_conn.setdefault(res['connectivity'], Counter())[k] += 1
            cls[k] += 1
        out[f'{part}_stages'] = len(items)
        out[f'{part}_classes'] = dict(cls)
        out[f'{part}_by_connectivity'] = {a: dict(b) for a, b in sorted(by_conn.items())}
    out['other_states_stages'] = sorted(other)
    out['code_only_other_equations_without_legal_arrangement'] = len(code_only - other)
    # corrected 3-connected criterion
    agree = Counter()
    for part, items in rows.items():
        for c, res in items:
            if res is None or res['connectivity'] != 'three':
                continue
            stars = U.stage(res['key'], res['round'])
            own = U.R.owners(stars)
            loose_at = Counter(js[0] for b, js in own.items() if len(js) == 1)
            heavy = sum(1 for v in loose_at.values() if v >= 2)
            crit = res['loose'] >= 3 and heavy <= 1
            agree[f'criterion={crit},rival={res["same_code_rivals"] > 0}'] += 1
    out['three_connected_corrected_criterion'] = dict(agree)
    (A / 'final.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main(*sys.argv[1:])
