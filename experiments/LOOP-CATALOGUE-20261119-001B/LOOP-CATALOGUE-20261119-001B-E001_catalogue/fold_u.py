"""Fold part U in full (after its isolated rerun B4): the main run's finished U shards and B4's 27, scored as merge.py scores U1 and
U2.  merge.py's U2 counts a reduction grown to 'over limit' as not feeding; U2_strict (post hoc) also splits the entries into those
minimal on every reduction decided ('firm') and those with a reduction over the limit or never grown ('provisional').
python3 -B fold_u.py <main out dir> <B4 out dir> <out.json>"""
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('lc_merge', HERE / 'merge.py')
M = importlib.util.module_from_spec(spec)
sys.modules['lc_merge'] = M
spec.loader.exec_module(M)


def strict(U):
    sys.path.insert(0, str(HERE))
    import catalogue as CT
    known = {CT.canon(x['sizes'], [tuple(e) for e in x['edges']]): x['growth'] for x in U}
    out, why = {'firm': [], 'provisional': [], 'not_minimal': 0}, Counter()
    for x in U:
        if not M.is_exp(x['growth']):
            continue
        status = 'firm'
        for parts in CT.reductions(x['n'], [tuple(e) for e in x['edges']], x['spares']):
            for p in parts:
                sz, e = CT.start(*p)
                v = CT.rule_verdict(sz, e)
                if v is None:
                    g = known.get(CT.canon(sz, e))
                    if g is None or g in ('over limit', 'killed from outside'):
                        why['ungrown' if g is None else 'over limit'] += 1
                        status = 'provisional' if status == 'firm' else status
                        continue
                    v = M.is_exp(g)
                if v:
                    status = 'not minimal'
        if status == 'not minimal':
            out['not_minimal'] += 1
        else:
            out[status].append({k: x[k] for k in ('sizes', 'edges', 'spares', 'meet', 'broken', 'growth', 'counts')})
    out['unknown_reductions'] = dict(why)
    return out


def main():
    main_dir, iso_dir, dest = sys.argv[1:4]
    U = []
    for d in (main_dir, iso_dir):
        R = M.load_results(d)
        for c, r in sorted(R.items()):
            if c.startswith('U-') and r.get('status') == 'ok':
                U += r['result']['starts']
    um = [x for x in U if x['meet']]
    out = {'starts': len(U), 'classes': dict(Counter(x['growth'] for x in U)),
           'exponential': sum(M.is_exp(x['growth']) for x in U), 'meet': len(um),
           'meet_exponential': sum(M.is_exp(x['growth']) for x in um),
           'broken_exponential': sum(M.is_exp(x['growth']) for x in U if x['broken'] and not x['meet']),
           'out_of_scope_exponential': sum(M.is_exp(x['growth']) for x in U if not x['scope'] and not x['meet'] and not x['broken']),
           'over_limit': sum(1 for x in U if x['growth'] in ('over limit', 'killed from outside')),
           'U2': M.minimal_by_growth(U), 'U2_strict': strict(U),
           'by_shape': {f'{k}/{g}': n for (k, g), n in sorted(Counter(('meet' if x['meet'] else 'overlap' if x['broken'] else 'other',
                                                                      x['growth']) for x in U).items())}}
    out['U1_pass'] = out['meet_exponential'] == 0
    Path(dest).write_text(json.dumps(out, indent=1, default=str))
    S = out['U2_strict']
    print(json.dumps({k: v for k, v in out.items() if k not in ('U2', 'U2_strict')}), 'minimal by growth:', len(out['U2']['entries']),
          'unknown reductions:', out['U2']['reductions_unknown'], 'strict: firm', len(S['firm']), 'provisional', len(S['provisional']),
          'not minimal', S['not_minimal'], S['unknown_reductions'])


if __name__ == '__main__':
    main()
