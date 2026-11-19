"""Score SCALE-SHARE-20261119-001B-E001.  python3 -B merge.py <runner out dir> <results.json>"""
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402


def base(c):
    return c.replace(' [break shape]', '')


def main():
    R = load_results(sys.argv[1])
    per = defaultdict(list)
    G = {}
    for cid, r in R.items():
        if r.get('status') != 'ok':
            continue
        if cid.startswith('S-'):
            per[int(cid[3:5])] += r['result']['samples']
        else:
            G[cid] = r['result']['samples']
    out = {'shares': {}, 'spot_checks': {}}
    for n in sorted(per):
        s = per[n]
        lab, dis, tw = defaultdict(float), defaultdict(float), sum(x['weight'] for x in s)
        brk_l = brk_d = 0.0
        for x in s:
            b = base(x['class'])
            lab[b] += 1 / len(s)
            dis[b] += x['weight'] / tw
            if '[break shape]' in x['class']:
                brk_l += 1 / len(s)
                brk_d += x['weight'] / tw
        grow_l = {k: v for k, v in lab.items() if k not in ('stall', 'closes', 'out of scope')}
        grow_d = {k: v for k, v in dis.items() if k not in ('stall', 'closes', 'out of scope')}
        gl, gd = sum(grow_l.values()), sum(grow_d.values())
        ess = tw ** 2 / sum(x['weight'] ** 2 for x in s)
        ns = [x for x in s if base(x['class']) != 'stall']
        feats = {k: sum(x[k] for x in s) / len(s) for k in ('m', 'cycle_rank', 'open_per_knot', 'over_demanded')}
        feats['cycle_rank_non_stalled'] = sum(x['cycle_rank'] for x in ns) / len(ns) if ns else None
        feats['P_none_over'] = sum(1 for x in s if x['over_demanded'] == 0) / len(s)
        out['shares'][n] = {'samples': len(s), 'labelled': dict(lab), 'distinct': dict(dis), 'features': feats,
                            'non_stall_labelled': 1 - lab.get('stall', 0.0),
                            'break_among_non_stalled': (sum(1 for x in ns if '[break shape]' in x['class']) / len(ns)) if ns else None,
                            'closes_among_non_stalled': (sum(1 for x in ns if base(x['class']) == 'closes') / len(ns)) if ns else None,
                            'break_shape': {'labelled': brk_l, 'distinct': brk_d},
                            'among_growing_labelled': {k: v / gl for k, v in grow_l.items()} if gl else {},
                            'among_growing_distinct': {k: v / gd for k, v in grow_d.items()} if gd else {},
                            'distinct_effective_sample_size': ess}
    for cid, s in G.items():
        cnt = defaultdict(int)
        for x in s:
            cnt[(x['grown'], '[break shape]' in x['class'])] += 1
        out['spot_checks'][cid] = {f'{a}{" (break shape)" if b else ""}': v for (a, b), v in cnt.items()}
    import math
    sh = out['shares']
    ns = {n: sh[n]['non_stall_labelled'] for n in sh}
    P = {}
    P['P1_open_per_knot'] = {n: (sh[n]['features']['open_per_knot'], math.sqrt(5 / n)) for n in sh}
    P['P1'] = all(math.sqrt(5 / n) / 1.5 <= sh[n]['features']['open_per_knot'] <= 1.5 * math.sqrt(5 / n) for n in sh if n >= 8)
    P['P2'] = (all(ns[a] >= ns[b] - 0.01 for a, b in zip(sorted(n for n in ns if n >= 7), sorted(n for n in ns if n >= 7)[1:]))
               and 0.12 <= ns.get(12, 0) <= 0.22 and 0.06 <= ns.get(16, 0) <= 0.13 and 0.03 <= ns.get(20, 0) <= 0.08)
    rate = {n: -math.log(ns[n]) / n for n in ns if ns[n] > 0}
    P['P3_rates'] = rate
    P['P3'] = all(rate[b] >= rate[a] - 0.01 for a, b in zip([n for n in sorted(rate) if n >= 10], [n for n in sorted(rate) if n >= 10][1:])) and \
        all(sh[n]['features']['P_none_over'] >= math.exp(-sh[n]['features']['over_demanded']) - 0.01 for n in sh)
    cl = {n: sh[n]['closes_among_non_stalled'] for n in sh}
    P['P4'] = cl.get(16, 1) < cl.get(6, 0)
    ok5 = True
    for n in sh:
        poly = {k: v for k, v in sh[n]['labelled'].items() if k.startswith('dimension')}
        if not poly:
            continue
        top = max(poly, key=poly.get)
        r = poly.get('dimension 2', 0) / poly['dimension 1'] if poly.get('dimension 1') else None
        if top != 'dimension 2' or (r is not None and not 2.5 <= r <= 6) or poly.get('dimension 3', 0) > 0.02 or \
                any(int(k.split()[1]) >= 4 for k in poly):
            ok5 = False
    P['P5'] = ok5
    P['P6'] = all(sh[n]['labelled'].get('ring (exponential)', 0) <= 0.03 for n in sh)
    oos = {n: sh[n]['labelled'].get('out of scope', 0) for n in sh}
    P['P7'] = max(oos.values()) <= 0.02 and max(oos, key=oos.get) in (7, 8, 10)
    diff = {n: sum(abs(sh[n]['labelled'].get(k, 0) - sh[n]['distinct'].get(k, 0)) for k in set(sh[n]['labelled']) | set(sh[n]['distinct'])) for n in sh}
    P['P8_diff'] = diff
    P['P8'] = diff.get(20, 1) <= diff.get(6, 0) and diff.get(16, 1) <= 0.05
    sc = out['spot_checks']
    P['P9'] = all(v.get('differs', 0) == 0 for v in sc.values())
    P['P10'] = all((sh[n]['break_among_non_stalled'] or 0) <= 0.05 for n in sh)
    census5 = {'stall': 0.436, 'closes': 0.125, 'dimension 1': 0.081, 'dimension 2': 0.358}
    if 5 in sh:
        N5 = sh[5]['samples']
        chi = sum((sh[5]['labelled'].get(k, 0) * N5 - p * N5) ** 2 / (p * N5) for k, p in census5.items())
        P['check_n5_chi_square_4_classes'] = chi
    out['predictions'] = P
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in P.items() if not k.endswith('_rates') and not k.endswith('_diff') and not k.startswith('P1_')}))
    for n, v in out['shares'].items():
        print(n, {k: round(x, 4) for k, x in sorted(v['labelled'].items())}, 'break', round(v['break_shape']['labelled'], 4),
              'ESS', round(v['distinct_effective_sample_size']))
    print(out['spot_checks'])


if __name__ == '__main__':
    main()
