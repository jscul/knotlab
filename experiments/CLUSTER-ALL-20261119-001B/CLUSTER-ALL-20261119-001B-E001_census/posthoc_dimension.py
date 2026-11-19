"""Post hoc: the rule's long-horizon growth class (dimension.py) and its chain count against the touch census's measured dimension,
on every census arrangement (TOUCH-CENSUS-20261118-001's runs; the referee's last 100 not in them).
python3 -B posthoc_dimension.py <out.json>"""
import importlib.util
import json
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from dimension import growth_class, chains  # noqa: E402
import clusters as Cl  # noqa: E402
sys.path.insert(0, str(Cl.ROOT / 'scripts'))
from longrun import load_results  # noqa: E402
_spec = importlib.util.spec_from_file_location('cj', HERE / 'job.py')
job = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(job)


def one(item):
    key, d = item
    sz, e = job.edges_of(key)
    g = growth_class(sz, e)
    ch = chains(sz, e)
    acyc = [c for c, cy in ch if not cy] if ch else []
    cyc = any(cy for c, cy in ch) if ch else False
    return [list(key[0]), list(key[1])], d, g, (max(acyc) if acyc else None), cyc


if __name__ == '__main__':
    R = load_results(str(Cl.ROOT / 'runs/touch-census'))
    items = []
    for cid, r in R.items():
        if r.get('status') != 'ok':
            continue
        for a in r['result']['arrangements']:
            items.append(((tuple(a['key'][0]), tuple(a['key'][1])), a['dim']))
    with Pool(6) as p:
        res = p.map(one, items, chunksize=40)
    T = Counter((str(g), str(d)) for _, d, g, _, _ in res)
    agree = sum(1 for _, d, g, _, _ in res if g not in ('out', 'unsettled', 'exp', 'stall') and d == g)
    poly = sum(1 for _, d, g, _, _ in res if g not in ('out', 'unsettled', 'exp', 'stall'))
    chain_ok = sum(1 for _, d, g, c, cyc in res if g not in ('out', 'unsettled', 'exp', 'stall') and not cyc and c == g)
    out = {'arrangements': len(res), 'table_rule_vs_census': {f'{a} | {b}': n for (a, b), n in sorted(T.items())},
           'polynomial_agree': [agree, poly], 'chain_count_equals_dimension': [chain_ok, poly],
           'exponential': [r for r in res if r[2] == 'exp']}
    Path(sys.argv[1]).write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != 'exponential'}, indent=1), len(out['exponential']))
