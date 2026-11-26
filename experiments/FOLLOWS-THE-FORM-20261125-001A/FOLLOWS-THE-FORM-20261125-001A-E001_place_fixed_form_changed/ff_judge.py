"""Judging of FOLLOWS-THE-FORM-20261125-001A-E001: every prediction by its "Fails when" entry, from the per-run records,
the study readings and the controls.  Writes summary.json and summary.md.

  python -B ff_judge.py replication     # PR1, PR2, PR3, PR5 against disclosed.json (prints the first differences)
  python -B ff_judge.py summary         # every prediction; summary.json and summary.md
"""
import sys

sys.dont_write_bytecode = True

import argparse
import json
import os
from collections import Counter

import ff_core as C
import ff_read as FR


def load_studies(runset):
    p = C.out_path('studies_%s.jsonl.gz' % runset)
    if not os.path.exists(p):
        return None
    return list(C.read_jsonl(p))


def load_tables(runset):
    p = C.out_path('tables_%s.json' % runset)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


# ------------------------------------------------------------------------------------------------- replication
def pr1(studies, disc):
    mine = {}
    for s in studies:
        rs, kl, fam, first, take, ration, treat = s['key']
        mine[(take, ration, treat, first, fam)] = s
    rows = []
    first_diff = None
    n_same = n_rbr = 0
    for d in disc['studies']:
        k = (d['take'], d['ration'], d['treatment'], d['first'], d['family'])
        s = mine.get(k)
        if s is None:
            rows.append({'study': k, 'missing': True})
            first_diff = first_diff or {'study': k, 'what': 'missing in this reading'}
            continue
        cd = sorted(sorted(c) for c in d['classes'])
        cm = sorted(sorted(c) for c in s['classes'])
        same_R = d['R*'] == s['R*']
        same_c = cd == cm
        rbr = d['runs read by round'] == s['runs read by round']
        n_rbr += rbr
        if same_R and same_c:
            n_same += 1
        elif first_diff is None:
            first_diff = {'study': k, 'R* disclosed': d['R*'], 'R* here': s['R*'],
                          'classes disclosed': len(cd), 'classes here': len(cm),
                          'runs read by round disclosed': d['runs read by round'],
                          'runs read by round here': s['runs read by round']}
            if not same_c:
                # the first class that differs, as sets
                sd = {frozenset(c) for c in cd}
                sm = {frozenset(c) for c in cm}
                first_diff['in disclosed only'] = [sorted(c) for c in sd - sm][:3]
                first_diff['here only'] = [sorted(c) for c in sm - sd][:3]
    return {'studies': len(disc['studies']), 'same': n_same, 'runs read by round the same': n_rbr,
            'verdict': 'holds' if n_same == len(disc['studies']) and len(mine) == len(disc['studies']) else 'fails',
            'first differing': first_diff}


def compare_cells(want, got, path=()):
    """Every leaf of `want` and of `got`; returns the list of differing cells (path, disclosed, here)."""
    out = []
    if isinstance(want, dict) or isinstance(got, dict):
        want = want if isinstance(want, dict) else {}
        got = got if isinstance(got, dict) else {}
        for k in list(want) + [k for k in got if k not in want]:
            out += compare_cells(want.get(k), got.get(k), path + (k,))
        return out
    if want != got:
        out.append({'cell': ' / '.join(path), 'disclosed': want, 'here': got})
    return out


def pr_tables(T, disc, keys):
    """keys: [(disclosed table key, this reading's table key, subkey or None)]"""
    diffs = []
    n = 0
    for dk, mk_, sub in keys:
        want = disc['tables'][dk]
        got = T.get(mk_)
        if sub is not None:
            want = want[sub]
            got = (got or {}).get(sub)
        cells = compare_cells(want, got, (dk,) + ((sub,) if sub else ()))
        n += _count_leaves(want)
        diffs += cells
    return {'cells compared (disclosed leaves)': n, 'differing cells': len(diffs), 'first differing': diffs[:1],
            'all differing': diffs, 'verdict': 'holds' if not diffs else 'fails'}


def _count_leaves(x):
    if isinstance(x, dict):
        return sum(_count_leaves(v) for v in x.values())
    return 1


def replication():
    disc = C.load_disclosed()
    st = load_studies('R1')
    T = load_tables('R1')
    out = {}
    out['PR1'] = pr1(st, disc)
    out['PR2'] = pr_tables(T, disc, [('first told apart, mixed', 'first told apart, mixed', None),
                                     ('first told apart, second', 'first told apart, second', None)])
    out['PR3'] = pr_tables(T, disc, [('depth, chains, first seeds A to E together (told apart / pairs)',
                                      'depth, chains, first seeds A to E together (told apart / pairs)', None)])
    keys = []
    for tk in ('after the first round', 'fates on the window',
               'the count profile (studies in which the class is a function of it)', 'R*'):
        for fam in ('mixed', 'second'):
            keys.append((tk, tk, fam))
    out['PR5'] = pr_tables(T, disc, keys)
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('what', choices=('replication', 'summary'))
    a = ap.parse_args()
    if a.what == 'replication':
        res = replication()
        for k, v in res.items():
            vv = {x: y for x, y in v.items() if x != 'all differing'}
            print(k, json.dumps(vv, indent=1)[:3000])
            if 'all differing' in v:
                print('  differing cells:', len(v['all differing']))
                for c in v['all differing'][:40]:
                    print('   ', c)
    else:
        import ff_summary
        ff_summary.main()
