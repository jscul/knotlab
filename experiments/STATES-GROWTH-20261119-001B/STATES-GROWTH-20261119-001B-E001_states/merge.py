"""Score STATES-GROWTH-20261119-001B-E001.  python3 -B merge.py <runner out dir> <results.json>"""
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402
sys.path.insert(0, str(ROOT / 'experiments/TOUCH-CENSUS-20261118-001B/TOUCH-CENSUS-20261118-001B-E001_arrangements'))


def triangle_or_double(key):
    sizes, flat = key
    pairs = list(itertools.combinations(range(len(sizes)), 2))
    m = dict(zip(pairs, flat))
    if any(v >= 2 for v in flat):
        return True
    return any(m.get((a, b)) and m.get((a, c)) and m.get((b, c)) for a, b, c in itertools.combinations(range(len(sizes)), 3))


def main():
    R = load_results(sys.argv[1])
    ok = {c: r['result'] for c, r in R.items() if r.get('status') == 'ok'}
    out = {'cases': len(R), 'not_ok': [c for c, r in R.items() if r.get('status') != 'ok']}
    A = ok.get('A', {})
    out['A1'] = dict(A, pass_=A.get('states_stars') == 18 and A.get('same_states') and A.get('minimal_constraints') == 8
                     and A.get('admissible_irredundant_presentations') == 2 and A.get('duplicate_pair_minimal') == 1)
    st = [s for c, x in sorted(ok.items()) if c.startswith('B-') for s in x['stages']]
    v = Counter((s['verdict'], 'redundant' if s['redundant'] else 'irredundant') for s in st)
    irr = [s for s in st if not s['redundant']]
    sat = sum(s['verdict'] == 'saturated' for s in irr) / max(len(irr), 1)
    out['B1'] = {'stages': len(st), 'verdicts': {' / '.join(k): n for k, n in sorted(v.items())},
                 'saturated_share_irredundant': round(sat, 4), 'pass_': 0.85 <= sat <= 0.92}
    T = [t for c, x in sorted(ok.items()) if c.startswith('C-') for t in x['trajectories']]
    c1 = c2 = 0
    for t in T:
        for k, a in enumerate(t['agree']):
            if all(x == 'saturated' for x in t['verdicts'][:k + 1]):
                c1 += not a
            if not a and t['verdicts'][k] == 'saturated':
                c2 += 1
    und = [t for t in T if 'undefined' in t['verdicts']]
    c3 = [triangle_or_double(t['key']) for t in und]
    out['C1'] = {'trajectories': len(T), 'disagreements_while_saturated': c1, 'pass_': c1 == 0}
    out['C2'] = {'disagreements_after_a_saturated_stage': c2, 'pass_': c2 == 0}
    out['C3'] = {'undefined': len(und), 'with_triangle_or_double': sum(c3), 'pass_': all(c3)}
    out['C_readout'] = {'first_verdicts': dict(Counter(t['verdicts'][0] if t['verdicts'] else '-' for t in T)),
                        'ever_undefined': len(und), 'ever_sharpened': sum('sharpened' in t['verdicts'] for t in T)}
    D = ok.get('D', {}).get('pairs', [])
    both3 = [p for p in D if p['three_connected_a'] and p['three_connected_b']]
    out['D1'] = {'pairs': len(D), 'both_three_connected': len(both3), 'iso_among_them': sum(p['iso'] for p in both3),
                 'pass_': all(p['iso'] for p in both3)}
    out['D2'] = {'iso_share': round(sum(p['iso'] for p in D) / max(len(D), 1), 4), 'pass_': sum(p['iso'] for p in D) >= len(D) / 2}
    out['verdicts'] = {k: bool(out[k]['pass_']) for k in ('A1', 'B1', 'C1', 'C2', 'C3', 'D1', 'D2')}
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out['verdicts']))


if __name__ == '__main__':
    main()
