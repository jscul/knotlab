"""Score DROPPED-JUNCTION-20261119-001B-E001.  python3 -B merge.py <runner out dir> <results.json>"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'scripts'))
from longrun import load_results  # noqa: E402


def is_exp(c):
    return isinstance(c, str) and c.startswith('exp')


def main():
    R = load_results(sys.argv[1])
    S = [s for c, r in sorted(R.items()) if r.get('status') == 'ok' for s in r['result']['starts']]
    out = {'cases': len(R), 'not_ok': [c for c, r in R.items() if r.get('status') != 'ok'], 'starts': len(S)}
    ed = [s for s in S if s['kind'] == 'eddy']
    d1 = []
    for s in ed:
        orig = next(c for c in s['choices'] if c['drop'] == 'out')
        others = [c for c in s['choices'] if c['drop'] != 'out']
        d1.append(is_exp(orig['class']) and not any(is_exp(c['class']) for c in others))
    out['D1'] = {'eddies': len(ed), 'held': sum(d1), 'misses': [s['name'] for s, ok in zip(ed, d1) if not ok], 'pass_': all(d1)}
    out['D2'] = {'eddies': len(ed), 'held': sum(s['original_is_unique_top'] for s in ed),
                 'pass_': all(s['original_is_unique_top'] for s in ed)}
    sm = [s for s in S if s['kind'] == 'sample']
    changed = 0
    for s in sm:
        orig = next(c for c in s['choices'] if c['drop'] == 'out')['class']
        if any(c['class'] != orig for c in s['choices'] if c['drop'] != 'out'):
            changed += 1
    top_rule = 0
    for s in sm:
        if s['original_is_unique_top']:
            top_rule += 1
    # the largest-point rule (drop the unique point of largest degree) against the original, where they differ
    inv = [s for s in sm if not s['original_is_unique_top']]
    rule_differs = 0
    for s in inv:
        deg = {c['drop']: c['degree'] for c in s['choices']}
        top = max(deg.values())
        tops = [k for k, d in deg.items() if d == top]
        if len(tops) == 1:
            orig = next(c for c in s['choices'] if c['drop'] == 'out')['class']
            pick = next(c for c in s['choices'] if c['drop'] == tops[0])['class']
            rule_differs += pick != orig
    out['D3'] = {'samples': len(sm), 'original_is_unique_top': top_rule, 'another_choice_changes_class': changed,
                 'original_not_unique_top': len(inv), 'largest_rule_changes_class_there': rule_differs,
                 'pass_': rule_differs >= 1,
                 'original_classes': dict(Counter(next(c for c in s['choices'] if c['drop'] == 'out')['class'] for s in sm)),
                 'other_classes': dict(Counter(c['class'] for s in sm for c in s['choices'] if c['drop'] != 'out'))}
    out['verdicts'] = {k: bool(out[k]['pass_']) for k in ('D1', 'D2', 'D3')}
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out['verdicts']))


if __name__ == '__main__':
    main()
