"""The touch census's growth classes against the identification theorems, on the whole class (DOUBLE-IDENT-20261119-001B).

For every arrangement in the class of DOUBLE-IDENT's machine check ((S3), (S4) on live knots, no stall, any multiplicity), read the
growth class off the relayed extended complex, piece by piece:
- a finite piece: closes if it is the only piece, else relays (dimension 2);
- an infinite piece whose core (live knots and pendant points) is a tree: dimension = its number of rays (CHAIN-IDENT, Theorem 2);
- a piece whose core holds one cycle and is bare (every block on it a pair, no other block, no pendant point): dimension 1
  (constant counts);
- any other piece with a cycle: exponential (LOOP-CATALOGUE's eddies: a loop that is not bare; two cycles branch).
The start's class is the largest over its pieces.  Prediction (D1): it equals the census's measured class (closed = 0, the
measured dimension, or exponential) on every arrangement in the class.  Readout: the census's two-dimensional growths by mechanism.
python3 -B dims.py <out.json>"""
import importlib.util
import itertools
import json
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_s = importlib.util.spec_from_file_location('dc', ROOT / 'proofs/DOUBLE-IDENT-20261119-001A/DOUBLE-IDENT-20261119-001A-P001_doubles/machine_check.py')
DC = importlib.util.module_from_spec(_s)
_s.loader.exec_module(DC)
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402


def predict(sizes, edges):
    n, nb, opn, live, groups, d = DC.data(sizes, edges)
    ls = set(live)
    loose = sum(opn[k] for k in live)
    if loose <= 1:
        return 0, 'closes (at most one loose distinction)'
    blocks = [tuple(sorted(nb[w] & ls)) for w in range(n) if len(nb[w] & ls) >= 2]
    rays = Counter()
    pend = Counter()
    for k in live:
        s = opn[k] - d[k]
        pend[k] = s
        rays[k] = s * (0 if opn[k] >= 3 else (1 if opn[k] == 2 else 2))
    G = nx.Graph()
    G.add_nodes_from(('v', k) for k in live)
    for i, B in enumerate(blocks):
        for v in B:
            G.add_edge(('v', v), ('b', i))
    pieces = []
    for comp in nx.connected_components(G):
        H = G.subgraph(comp)
        kn = [x[1] for x in comp if x[0] == 'v']
        cyc = H.number_of_edges() - H.number_of_nodes() + 1
        bl = [blocks[x[1]] for x in comp if x[0] == 'b']
        R = sum(rays[k] for k in kn)
        P = sum(pend[k] for k in kn)
        if cyc == 0:
            pieces.append(('finite', 0) if R == 0 else ('rays', R))
        elif cyc == 1 and P == 0 and all(len(B) == 2 for B in bl):
            pieces.append(('bare cycle', 1))
        else:
            pieces.append(('exp', None))
    if any(k == 'exp' for k, _ in pieces):
        return 'exp', 'a cycle that is not bare, or two cycles'
    q = len(pieces)
    if q == 1 and pieces[0][0] == 'finite':
        return 0, 'one finite piece: closes'
    vals = [v for k, v in pieces if k in ('rays', 'bare cycle')] + ([2] if any(k == 'finite' for k, _ in pieces) else [])
    D = max(vals)
    if D == 2:
        why = sorted({'relay' if k == 'finite' else ('two chains' if v == 2 else '') for k, v in pieces} - {''})
        return 2, ' and '.join(why)
    return D, f'{D}'


def one(item):
    key, dim, outcome = item
    sizes, edges = DC.edges_of(key)
    c = DC.classify(sizes, edges)
    if c not in ('in', 'one loose', 'none'):
        return key, dim, outcome, c, None, None
    D, why = predict(sizes, edges)
    return key, dim, outcome, c, D, why


def main():
    dest = Path(sys.argv[1])
    R = load_results(str(ROOT / 'runs/touch-census'))
    items = [((tuple(a['key'][0]), tuple(a['key'][1])), a['dim'], a['outcome'])
             for r in R.values() if r.get('status') == 'ok' for a in r['result']['arrangements']]
    with Pool(6) as p:
        res = p.map(one, items, chunksize=40)
    out = {'arrangements': len(res), 'compare': Counter(), 'pred_vs_measured': Counter(), 'dim2_by_class': Counter(),
           'dim2_why': Counter(), 'disagree': []}
    for key, dim, outcome, c, D, why in res:
        measured = 'exp' if (dim is None and outcome in ('alive', 'big', 'timed')) else (dim if dim is not None else (0 if outcome == 'closed' else outcome))
        if dim is not None and dim >= 5:
            measured = 'exp'
        if dim == 2:
            out['dim2_by_class'][c if c != 'in' else 'in the class'] += 1
        if D is None:
            continue
        ok = (D == measured) or (D == 'exp' and measured == 'exp')
        out['compare']['agree' if ok else 'differ'] += 1
        out['pred_vs_measured'][f'{D} | {measured}'] += 1
        if ok and D == 2:
            out['dim2_why'][why] += 1
        if not ok and len(out['disagree']) < 15:
            out['disagree'].append([list(map(list, key)), dim, outcome, D, why])
    for k in list(out):
        if isinstance(out[k], Counter):
            out[k] = dict(sorted(out[k].items()))
    dest.write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: v for k, v in out.items() if k != 'disagree'}, indent=1), len(out['disagree']))


if __name__ == '__main__':
    main()
