"""Score MANY-VALUED-20261119-001B-E001.  python3 -B merge.py <runner out dir> <results.json>"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'scripts'))
from longrun import load_results  # noqa: E402


def main():
    R = load_results(sys.argv[1])
    ok = {c: r['result'] for c, r in R.items() if r.get('status') == 'ok'}
    out = {'cases': len(R), 'not_ok': [c for c, r in R.items() if r.get('status') != 'ok']}
    P = [p for c, x in sorted(ok.items()) if c.startswith('P-') for p in x['points']]
    pilot = 40                                     # the first 40 points were read in the pilot; M1 is scored on the rest
    rest = P[pilot:]
    uniq = [p for p in rest if p['M'].get('classes') == 1 and p['M'].get('own_in_list')]
    starts = {}
    for p in rest:
        starts.setdefault(json.dumps(p['key']), []).append(p['M'].get('classes') == 1)
    out['M1'] = {'points': len(rest), 'unique_and_the_stage': len(uniq), 'share': round(len(uniq) / max(len(rest), 1), 4),
                 'by_start': {'starts': len(starts), 'all_unique': sum(all(v) for v in starts.values())},
                 'M_pool': dict(Counter(str(p['M'].get('classes')) for p in P)),
                 'stage_pool': dict(Counter(str(p['stage'].get('classes')) for p in P)),
                 'pass_': len(uniq) >= 0.95 * len(rest)}
    X = ok.get('X', {})
    out['M2'] = {'same_states': X.get('same_states'), 'grow_A': X.get('grow_A'), 'grow_B': X.get('grow_B'),
                 'pass_': bool(X.get('same_states')) and X.get('grow_A') != X.get('grow_B')}
    sev = [p for p in P if (p['M'].get('classes') or 0) > 1]
    out['M2_readout'] = {'points_with_several_classes_M_pool': len(sev),
                         'agree': sum(len({json.dumps(c) for c in p['M']['counts_by_class']}) == 1 for p in sev)}
    T = [t for c, x in sorted(ok.items()) if c.startswith('T-') for t in x['trajectories']]
    clean = [t for t in T if not t['redundant']]
    bad = [t for t in clean if not all(t['agree']) or (t['verdicts'] and t['verdicts'][-1] in ('several', 'none'))]
    out['M3'] = {'trajectories': len(T), 'without_redundant_knot': len(clean), 'undefined_or_disagree': len(bad), 'examples': bad[:5],
                 'pass_': not bad}
    out['T_readout'] = {'final': dict(Counter(t['verdicts'][-1] if t['verdicts'] else '-' for t in T)),
                        'ever_unique': sum('unique' in t['verdicts'] for t in T),
                        'ended_several': sum(bool(t['verdicts']) and t['verdicts'][-1] == 'several' for t in T),
                        'ended_none': sum(bool(t['verdicts']) and t['verdicts'][-1] == 'none' for t in T)}
    out['verdicts'] = {k: bool(out[k]['pass_']) for k in ('M1', 'M2', 'M3')}
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out['verdicts']))


if __name__ == '__main__':
    main()
