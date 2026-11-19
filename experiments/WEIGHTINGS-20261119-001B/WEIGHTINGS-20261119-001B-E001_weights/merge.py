"""Score WEIGHTINGS-20261119-001B-E001 (W1-W11 of research/WEIGHTINGS-20261119-001/preregistration.md).
python3 -B merge.py <runner out dir> <results.json>"""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'scripts'))
from longrun import load_results  # noqa: E402

COMMON, MIN_GROWERS = 0.10, 20


def dimnum(lbl):
    return int(lbl.split()[1]) if lbl and lbl.startswith('dimension') else None


def three(lbl):
    return (dimnum(lbl) or 0) >= 3


def summary(S, n):
    tot = len(S)
    cls = Counter(x['cls'] for x in S)
    ns = tot - cls['stall']
    inc = [x for x in S if x['cls'] == 'in']
    grow = [x for x in inc if x['growth'] != 'closes']
    g = Counter(x['growth'] for x in grow)
    t3 = sum(v for k, v in g.items() if three(k))
    return {
        'samples': tot,
        'class_of_all': {k: v / tot for k, v in sorted(cls.items())},
        'out_reasons_of_all': {k: v / tot for k, v in sorted(Counter(x['why'] for x in S if x['cls'] == 'out').items())},
        'in_of_all': len(inc) / tot, 'in_of_nonstalling': len(inc) / ns if ns else None,
        'in_class_growth_of_all': {k: v / tot for k, v in sorted(Counter(x['growth'] for x in inc).items())},
        'in_growers': len(grow),
        'of_in_growers': {k: v / len(grow) for k, v in sorted(g.items())} if grow else {},
        'counts': {'in': len(inc), 'in_growers': len(grow), 'three_plus': t3, 'exp': g['exponential'],
                   'growth': dict(sorted(g.items()))},
        'three_plus_of_all': t3 / tot, 'exp_of_all': g['exponential'] / tot,
        'three_plus_of_in_growers': t3 / len(grow) if grow else None,
        'exp_of_in_growers': g['exponential'] / len(grow) if grow else None,
        'dim2_mechanism': dict(sorted(Counter(x['why'] for x in grow if x['growth'] == 'dimension 2').items())),
        'over_five_places_of_all': sum(x['max_places'] > 5 for x in S) / tot,
        'three_plus_of_in_growers_max5': (lambda G: sum(three(x['growth']) for x in G) / len(G) if G else None)(
            [x for x in grow if x['max_places'] <= 5]),
        'cycle_free_of_all': sum(x['pairs'] == n - 1 for x in S) / tot,
        'common': bool(grow) and len(grow) >= MIN_GROWERS and (t3 / len(grow) >= COMMON or g['exponential'] / len(grow) >= COMMON),
    }


def main():
    R = load_results(sys.argv[1])
    T, raw = {}, {}
    regrow = Counter()
    bad = []
    for cid, r in sorted(R.items()):
        if r.get('status') != 'ok':
            bad.append(cid)
            continue
        kind, n = cid.rsplit('-n', 1)
        n = int(n)
        S = r['result']['samples']
        raw[(kind, n)] = S
        row = summary(S, n)
        if kind == 'tree':
            row['mean_ray_leaves'] = sum(x['ray_leaves'] for x in S) / len(S)
            row['expected_ray_leaves'] = (n - 1) * (1 - 2 / n) ** (n - 3)
        if kind == 'tree+':
            row['by_extra'] = {}
            for k in (0, 1, 2, 3):
                sub = [x for x in S if min(x['extra'], 3) == k]
                if sub:
                    row['by_extra'][str(k) + ('+' if k == 3 else '')] = summary(sub, n)
        if kind == 'grow':
            row['expected_cycle_free_floor'] = (2 / 3) ** (n - 1)
        T.setdefault(kind, {})[n] = row
        for x in S:
            if 'regrown_agree' in x:
                regrow[(kind, n, x['regrown_kind'], x['regrown_agree'])] += 1
    W = {}
    t = T['tree']
    c3 = {n: t[n]['counts']['three_plus'] for n in t}
    W['W1'] = c3[5] == 0 and c3[6] == 0 and 70 <= c3[7] <= 130 and 31 <= c3[8] <= 73 and c3[7] > c3[8]
    W['W2'] = all(abs(t[n]['mean_ray_leaves'] - t[n]['expected_ray_leaves']) <= 0.05 * t[n]['expected_ray_leaves'] for n in t)
    trees = [k for k in T if k == 'tree' or k.startswith('tree-s')]
    W['W3'] = all(T[k][n]['in_of_all'] == 1.0 for k in trees for n in T[k])
    W['W4'] = all(T[k][n]['counts']['exp'] == 0 for k in trees for n in T[k])
    W['W5'] = t[16]['three_plus_of_all'] > 0.10 and t[20]['three_plus_of_all'] > 0.20
    tp = T['tree+']
    W['W6'] = (all((tp[n]['exp_of_in_growers'] or 0) >= 0.10 for n in tp if n >= 8)
               and all(tp[n]['by_extra']['0']['counts']['exp'] == 0 and tp[n]['by_extra']['0']['in_of_all'] == 1.0 for n in tp))
    g = T['grow']
    W['W7'] = (all((g[n]['exp_of_in_growers'] or 0) > 0.5 for n in g if n >= 10 and g[n]['in_growers'] >= MIN_GROWERS)
               and all((g[n]['three_plus_of_in_growers'] or 0) < 0.02 for n in g))
    W['W8'] = (T['tree'][20]['three_plus_of_all'] >= T['tree-s25'][20]['three_plus_of_all'] >= T['tree-s50'][20]['three_plus_of_all']
               >= T['tree-s100'][20]['three_plus_of_all'])
    cf = T['config']
    W['W9'] = (all(cf[n]['class_of_all'].get('stall', 0) > 0.40 for n in cf)
               and all(cf[n]['of_in_growers'].get('dimension 2', 0) >= 0.70 and (cf[n]['three_plus_of_in_growers'] or 0) < 0.02
                       for n in cf if cf[n]['in_growers'] >= MIN_GROWERS))
    W['W10'] = sum(regrow.values()) > 0 and not any(not ok for (_, _, _, ok) in regrow)
    W['W11'] = all(g[n]['cycle_free_of_all'] >= g[n]['expected_cycle_free_floor']
                   - 3 * math.sqrt(g[n]['expected_cycle_free_floor'] * (1 - g[n]['expected_cycle_free_floor']) / g[n]['samples']) for n in g)
    out = {'not_ok': bad, 'verdicts': W, 'table': T,
           'regrown': {f'{k}-n{n}:{s}:{"agree" if ok else "differ"}': v for (k, n, s, ok), v in sorted(regrow.items())},
           'common': {k: [n for n in sorted(T[k]) if T[k][n]['common']] for k in T}}
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(W), 'not ok:', bad)
    print('common:', json.dumps(out['common']))
    print('regrown:', sum(v for k, v in out['regrown'].items() if k.endswith('agree')), 'agree,',
          sum(v for k, v in out['regrown'].items() if k.endswith('differ')), 'differ')
    for kind, rows in T.items():
        for n, r in sorted(rows.items()):
            print(f"{kind:9s} {n:2d} stall {r['class_of_all'].get('stall', 0):.2f} out {r['class_of_all'].get('out', 0):.2f}"
                  f" in {r['in_of_all']:.2f} growers {r['in_growers']:4d}",
                  {k: round(v, 3) for k, v in r['of_in_growers'].items()}, f"3+/all {r['three_plus_of_all']:.3f}")


if __name__ == '__main__':
    main()
