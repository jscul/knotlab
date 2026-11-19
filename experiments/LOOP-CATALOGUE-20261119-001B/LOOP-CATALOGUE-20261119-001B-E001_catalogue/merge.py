"""Score LOOP-CATALOGUE-20261119-001B-E001.  python3 -B merge.py <runner out dir> <results.json>

E1-E4 (parts E and S), C1-C4 (part C), I1-I3 (part I), R1-R2 (parts R and R8), as in the pre-registration."""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402


def is_exp(cls):
    return isinstance(cls, str) and cls.startswith('exp')


def series_div(a, b, n=12):
    """a / b as a power series, both starting at their lowest nonzero term."""
    ia = next(i for i, x in enumerate(a) if x)
    ib = next(i for i, x in enumerate(b) if x)
    a, b = a[ia:], b[ib:]
    q = []
    r = list(a) + [0] * n
    for k in range(n):
        c = r[k] / b[0]
        q.append(c)
        for j, x in enumerate(b):
            if k + j < len(r):
                r[k + j] -= c * x
    return ia - ib, q


def root_of(poly_y):
    """1 / the root in (0, 1) of sum c_k y^k = 1."""
    p = list(poly_y)
    p[0] -= 1
    r = [x.real for x in np.roots(p[::-1]) if abs(x.imag) < 1e-9 and 0 < x.real < 1]
    return 1 / min(r) if r else None


def minimal_by_growth(U):
    """Among the grown undecided starts, the exponential ones none of whose single reductions feeds itself (by the rule, or by
    the growth recorded in U)."""
    sys.path.insert(0, str(HERE))
    import catalogue as CT
    known = {CT.canon(x['sizes'], [tuple(e) for e in x['edges']]): is_exp(x['growth']) for x in U}
    out, unknown = [], 0
    for x in U:
        if not is_exp(x['growth']):
            continue
        ok = True
        for parts in CT.reductions(x['n'], [tuple(e) for e in x['edges']], x['spares']):
            for p in parts:
                sz, e = CT.start(*p)
                v = CT.rule_verdict(sz, e)
                if v is None:
                    v = known.get(CT.canon(sz, e))
                    if v is None:
                        unknown += 1
                if v:
                    ok = False
        if ok:
            out.append({'sizes': x['sizes'], 'edges': x['edges'], 'counts': x['counts'][:20]})
    return {'entries': out, 'reductions_unknown': unknown}


def main():
    R = load_results(sys.argv[1])
    out = {'cases_not_ok': [[c, r.get('status')] for c, r in R.items() if r.get('status') != 'ok']}
    grown, stats = [], defaultdict(lambda: defaultdict(float))
    for cid, r in R.items():
        if r.get('status') != 'ok' or not (cid.startswith('E-') or cid.startswith('S-')):
            continue
        n = int(cid[3:5])
        for g in r['result']['grown']:
            grown.append(dict(g, part=cid[0], n=n))
        for k, v in r['result']['stats'].items():
            stats[(cid[0], n)][k] += v
    e1 = [g for g in grown if g['rule'] == 'True']
    out['E1'] = {'n': len(e1), 'exponential': sum(is_exp(g['growth']) for g in e1),
                 'exact_equal': sum(g['equal_to_rule'] for g in e1 if g['exact']), 'exact_n': sum(1 for g in e1 if g['exact']),
                 'not_exp': [[g['part'], g['n'], g.get('seed', g.get('sample')), g['growth']] for g in e1 if not is_exp(g['growth'])][:20]}
    e2 = [g for g in grown if g['rule'] in ('False', 'out')]
    out['E2'] = {'n': len(e2), 'exponential': [[g['part'], g['n'], g.get('seed', g.get('sample')), g['counts'][:12]] for g in e2 if is_exp(g['growth'])][:20]}
    e3 = [g for g in grown if g['rule'] == 'unreliable' and g.get('meet')]
    e3b = [g for g in grown if g['rule'] == 'unreliable' and not g.get('meet')]
    e3c = [g for g in grown if g['rule'] == 'out-loop']
    out['E3'] = {'n': len(e3), 'exponential': sum(is_exp(g['growth']) for g in e3),
                 'readout_missing_pair_loops': {'n': len(e3b), 'exponential': sum(is_exp(g['growth']) for g in e3b)},
                 'readout_out_of_scope_loops': {'n': len(e3c), 'exponential': sum(is_exp(g['growth']) for g in e3c)}}
    tab = {}
    e4 = True
    for (part, n), s in sorted(stats.items()):
        G = max(s['growers'], 1)
        row = {'growers': int(s['growers']), 'live_share': round(s['live_share'] / G, 4),
               'all_live_share_of_cycles': round(s['all_live'] / max(s['cycles'], 1), 5),
               'all_live_long_per_grower': round(s['all_live_long'] / G, 6), 'with_loop_share': round(s['with_block_cycle'] / G, 6)}
        tab[f'{part}-{n}'] = row
        if n >= 6:
            e4 &= row['live_share'] < 0.3 and row['all_live_share_of_cycles'] < 0.02 and row['with_loop_share'] < 0.001
    out['E4'] = {'by_size': tab, 'pass': e4}
    out['E1']['pass'] = out['E1']['exponential'] == len(e1) and all(g['equal_to_rule'] for g in e1 if g['exact'])
    out['E2']['pass'] = not out['E2']['exponential']
    out['E3']['pass'] = out['E3']['exponential'] == 0

    C = [r['result'] for c, r in sorted(R.items()) if c.startswith('C-') and r.get('status') == 'ok']
    c1 = [{'sizes': x['entry']['sizes'], 'class': x['growth_class'], 'exact': x['exact'], 'equal': x['equal_to_rule'],
           'nae_equal': x['nae_equal']} for x in C]
    out['C1'] = {'entries': c1, 'pass': all(is_exp(x['class']) and (x['equal'] or not x['exact']) and x['nae_equal'] for x in c1)}
    rows2 = []

    def c2(rec, W, eq, exact):
        if exact and W and W.get('rate') and eq.get('kind') == 'rational':
            rows2.append(abs(W['rate'] - eq['ratio']) <= 1e-5)
    for x in C:
        c2(x, x['W'], x['equation'], x['exact'])
    I = [r['result'] for c, r in sorted(R.items()) if c.startswith('I-') and r.get('status') == 'ok']
    for x in I:
        for row in x['interfaces']:
            c2(row, row['W'], row['equation'], row['exact'])
    RR = [r['result'] for c, r in sorted(R.items()) if c.startswith('R-') and r.get('status') == 'ok']
    for x in RR:
        c2(x, x['W'], x['equation'], True)
    out['C2'] = {'checked': len(rows2), 'agree': sum(rows2), 'pass': all(rows2) and len(rows2) > 0}
    one = [x for x in C if x['exact'] and x['W']]
    out['C3'] = {'exact_one_loop_entries': len(one), 'W1': [x['W']['W1'] for x in one], 'pass': all(x['W']['W1'] == 2 for x in one)}
    out['C4'] = {'kinds': [x['equation'].get('kind') for x in C], 'pass': all(x['equation'].get('kind') != 'algebraic' for x in C)}

    want = {'spare': [1, 1], 'lone': [1, 1], 'lone+spare': [1, 1, 1], 'path2': [1, 2, 1]}
    i1, i2, i3, i3_alg = [], [], [], []
    for x in I:
        base = x['W']
        brate = x['base'].get('ratio')
        for row in x['interfaces']:
            if row['exact']:
                i1.append(row['equal_to_rule'])
            if row['on_loop'] and base and row['W'] and row['kind'] in want and row['exact']:
                sh, q = series_div(row['W']['W'], base['W'])
                w = want[row['kind']]
                i2.append(sh == 0 and all(abs(q[k] - (w[k] if k < len(w) else 0)) < 1e-9 for k in range(10)))
            r = row['equation'].get('ratio')
            if brate and r:
                i3.append(r > brate + 1e-9)
            if row['kind'] == 'ring5':
                i3_alg.append(row['equation'].get('kind') == 'algebraic')
    out['I1'] = {'n': len(i1), 'equal': sum(i1), 'pass': all(i1)}
    out['I2'] = {'n': len(i2), 'agree': sum(i2), 'pass': all(i2) and len(i2) > 0}
    out['I3'] = {'n': len(i3), 'raised': sum(i3), 'ring_joins': len(i3_alg), 'algebraic': sum(i3_alg), 'pass': all(i3) and all(i3_alg)}

    r1 = []
    for x in RR:
        n = x['n']
        if x['spare']:
            L = n if n % 2 else n // 2
            Wt = [0] * L + [1, 1]
            got = x['W']['W'][:L + 4] if x['W'] else None
            r1.append(bool(got) and got[:L + 2] == Wt and not any(got[L + 2:]) and x['equal_to_rule'])
        else:
            c = x['counts']
            r1.append(all(v == n for v in c) and x['equal_to_rule'])
    out['R1'] = {'n': len(r1), 'held': sum(r1), 'pass': all(r1) and len(r1) == 12}
    R8 = {r['result']['hang_at']: r['result'] for c, r in R.items() if c.startswith('R8-') and r.get('status') == 'ok'}
    w0, w1 = root_of([0, 0, 0, 0, 1, 1]), root_of([0, 0, 0, 0, 1, 2, 1])
    got = {k: v['equation'].get('ratio') for k, v in R8.items()}
    out['R2'] = {'want': {'0': round(w0, 6), '1': round(w1, 6)}, 'got': got,
                 'pass': len(got) == 2 and abs(got[0] - w0) < 1e-5 and abs(got[1] - w1) < 1e-5}
    U = [x for c, r in sorted(R.items()) if c.startswith('U-') and r.get('status') == 'ok' for x in r['result']['starts']]
    um = [x for x in U if x['meet']]
    out['U1'] = {'n': len(U), 'exponential': sum(is_exp(x['growth']) for x in U), 'meet': len(um),
                 'meet_exponential': sum(is_exp(x['growth']) for x in um),
                 'broken_exponential': sum(is_exp(x['growth']) for x in U if x['broken'] and not x['meet']),
                 'out_of_scope_exponential': sum(is_exp(x['growth']) for x in U if not x['scope'] and not x['meet'] and not x['broken'])}
    out['U1']['pass'] = out['U1']['meet_exponential'] == 0
    out['U2'] = {'minimal_by_growth': minimal_by_growth(U)}
    out['verdicts'] = {k: bool(out[k]['pass']) for k in ('E1', 'E2', 'E3', 'E4', 'C1', 'C2', 'C3', 'C4', 'I1', 'I2', 'I3', 'R1', 'R2', 'U1')}
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out['verdicts'], default=bool))


if __name__ == '__main__':
    main()
