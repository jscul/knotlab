"""Score SCALE-THEOREM-20261119-001B-E001.  python3 -B merge.py <runner out dir> <results.json>"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'scripts'))
from longrun import load_results  # noqa: E402

SS = HERE.parents[2] / 'artifacts/SCALE-SHARE-20261119-001B/SCALE-SHARE-20261119-001B-E001_shares/results.json'


def main():
    R = load_results(sys.argv[1])
    by_n = defaultdict(list)
    for c, r in R.items():
        if r.get('status') == 'ok':
            by_n[int(c[3:5])] += r['result']['samples']
    ss = json.loads(SS.read_text())['shares']
    out = {'cases': len(R), 'not_ok': [c for c, r in R.items() if r.get('status') != 'ok'], 'by_size': {}}
    s1 = s2 = True
    regrow = Counter()
    for n, S in sorted(by_n.items()):
        tot = len(S)
        lab = Counter(x['theorem'] for x in S)
        ns = tot - lab['stall']
        inc = [x for x in S if x['theorem'] == 'in']
        grow = [x for x in inc if x['predicted'] != 'closes']
        dims = Counter(x['predicted'] for x in grow)
        why2 = Counter(x['why'] for x in grow if x['predicted'] == 'dimension 2')
        outwhy = Counter(x['why'] for x in S if x['theorem'] == 'out')
        s1 = s1 and all(x['recorded'] == x['cluster_rule'] for x in S)
        s2 = s2 and all(x['predicted'] == x['cluster_rule'] for x in inc)
        for x in S:
            if 'regrown_agree' in x:
                regrow[(n, x['regrown_agree'])] += 1
        lab_ss = ss[str(n)]['labelled']
        g_ss = {k: v for k, v in lab_ss.items() if k not in ('stall', 'closes', 'out of scope')}
        d2_ss = g_ss.get('dimension 2', 0) / sum(g_ss.values())
        mix_in = Counter(x['cluster_rule'] for x in inc)
        mix_out = Counter(x['cluster_rule'] for x in S if x['theorem'] == 'out')
        out['by_size'][n] = {'samples': tot, 'counts': {'nonstalling': ns, 'in': len(inc), 'out': lab['out'], 'growers_in': len(grow)},
                             'cluster_rule_in_class': dict(mix_in), 'cluster_rule_out_of_class': dict(mix_out),
                             'stall': lab['stall'] / tot, 'in_share_of_nonstalling': len(inc) / ns,
                             'out_S3': outwhy['S3'] / ns, 'out_S4': outwhy['S4'] / ns,
                             'in_class_growth': {k: v / len(inc) for k, v in Counter(x['predicted'] for x in inc).items()},
                             'dim2_share_of_in_class_growers': dims['dimension 2'] / len(grow) if grow else None,
                             'dim3plus_share_of_in_class_growers': sum(v for k, v in dims.items() if k.startswith('dimension') and int(k.split()[1]) >= 3) / len(grow) if grow else None,
                             'exp_share_of_in_class_growers': dims['exponential'] / len(grow) if grow else None,
                             'dim2_mechanism': {k: v / sum(why2.values()) for k, v in why2.items()},
                             'scale_share_dim2_share_of_growers': d2_ss}
    B = out['by_size']
    out['P1'] = s1
    out['P2'] = s2
    out['P3'] = all(0.55 <= B[n]['in_share_of_nonstalling'] <= 0.90 for n in B)
    out['P4'] = all(B[n]['dim2_share_of_in_class_growers'] >= 0.75 for n in B) and B[20]['dim2_share_of_in_class_growers'] > B[5]['dim2_share_of_in_class_growers']
    out['P5'] = all(B[n]['dim3plus_share_of_in_class_growers'] <= 0.01 for n in B)
    out['P6'] = len(regrow) > 0 and not any(not ok for (n, ok) in regrow)
    out['P7'] = all(abs(B[n]['dim2_share_of_in_class_growers'] - B[n]['scale_share_dim2_share_of_growers']) <= 0.05 for n in B)
    out['regrown'] = {f'{n}:{"agree" if ok else "differ"}': v for (n, ok), v in sorted(regrow.items())}
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: out[k] for k in ('not_ok', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'regrown')}))
    for n in B:
        b = B[n]
        print(n, 'in %.3f' % b['in_share_of_nonstalling'], 'd2 %.3f' % b['dim2_share_of_in_class_growers'], 'd3+ %.4f' % b['dim3plus_share_of_in_class_growers'],
              'exp %.4f' % b['exp_share_of_in_class_growers'], 'ss d2 %.3f' % b['scale_share_dim2_share_of_growers'], {k: round(v, 3) for k, v in b['dim2_mechanism'].items()})


if __name__ == '__main__':
    main()
