"""The touch census's dimensions against Theorem 5 (RELAY-IDENT-20261119-001B).

For every arrangement of TOUCH-CENSUS-20261118-001 (its recorded runs, `runs/touch-census`; 26,441 arrangements of 1 to 5 knots
with 3 to 5 places), with the census's measured dimension:
- the knot graph K: simple (no two knots sharing two distinctions), connected, a tree or not;
- for simple connected trees that do not stall (open >= d at every live knot), Theorem 5's prediction: the pieces of X+ (parity
  classes holding a live knot), each knot's s = open - d pendant points with R(open) rays, an infinite piece's chain count, and
  D = max(chains of an infinite piece, 2 if a piece is finite and q >= 2), or 0 (closes) if q = 1 and the piece is finite;
- the mechanism behind D = 2: two chains in one class, a relay, or both.
The census's sizes are given, not bare, so open_k = places - shared; the proofs use only open_k and d_k.
Prediction (T1): on every such simple tree, D equals the census's measured dimension (0 for a start that closes).  Readouts: the
same prediction on tree-shaped arrangements with double touches (outside the proofs, which assume K simple), and the census's
dimension-two arrangements by kind.
python3 -B tally.py <out.json>"""
import importlib.util
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402
sys.path.insert(0, str(ROOT / 'experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins'))
import joinlib as J  # noqa: E402


def edges_of(key):
    sizes, flat = key
    e = []
    for (i, j), m in zip(itertools.combinations(range(len(sizes)), 2), flat):
        e += [(i, j)] * m
    return list(sizes), e


def predict(sizes, edges):
    n = len(sizes)
    sh = Counter()
    nb = defaultdict(set)
    for a, b in edges:
        sh[a] += 1
        sh[b] += 1
        nb[a].add(b)
        nb[b].add(a)
    opn = [sizes[k] - sh[k] for k in range(n)]
    live = [k for k in range(n) if opn[k] >= 1]
    P = J.S.from_junctions(J.stars_from(sizes, edges))
    groups = P.groups_among(live)
    d = Counter()
    for g in groups:
        for j in g:
            d[j] += 1
    if any(d[k] > opn[k] for k in live):
        return {'stall': True}
    if any(len(g) > 2 for g in groups):
        return {'out': 'S3'}
    # pieces: parity classes of the tree restricted to live knots, joined through candidates
    X = nx.Graph()
    X.add_nodes_from(live)
    for w in range(n):
        for a, b in itertools.combinations(sorted(nb[w] & set(live)), 2):
            X.add_edge(a, b)
    pieces = []
    for comp in nx.connected_components(X):
        rays = 0
        for k in comp:
            s = opn[k] - d[k]
            R = 0 if opn[k] >= 3 else (1 if opn[k] == 2 else 2)
            rays += s * R
        pieces.append((sorted(comp), rays))
    q = len(pieces)
    finite = [p for p in pieces if p[1] == 0]
    if q == 0:
        D, why = 0, 'no live knot'
    elif q == 1 and finite:
        D, why = 0, 'one finite piece: closes'
    else:
        D = max([r for _, r in pieces if r > 0] + ([2] if finite else []))
        two_chain = any(r == 2 for _, r in pieces)
        why = {(True, True): 'relay and two chains', (True, False): 'relay', (False, True): 'two chains', (False, False): ''}[
            (bool(finite), two_chain)] if D == 2 else f'{D} chains' if D != 1 else 'one chain per piece'
    return {'D': D, 'why': why, 'pieces': [[p, r] for p, r in pieces], 'q': q}


def main():
    dest = Path(sys.argv[1])
    R = load_results(str(ROOT / 'runs/touch-census'))
    rows = []
    for cid, r in R.items():
        if r.get('status') != 'ok':
            continue
        for a in r['result']['arrangements']:
            rows.append((a['key'], a['dim'], a['outcome']))
    out = {'arrangements': len(rows), 'kinds': Counter(), 'census_dim_all': Counter(), 'dim2_by_kind': Counter(),
           'compare': Counter(), 'stall_or_out': Counter(), 'why_D2': Counter(), 'D': Counter(), 'disagree_max_share': Counter(),
           'disagree_examples': []}
    for key, dim, outcome in rows:
        sizes, edges = edges_of(key)
        n = len(sizes)
        pairs = {tuple(sorted(e)) for e in edges}
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from(pairs)
        connected = n > 0 and nx.is_connected(G)
        simple = all(m <= 1 for m in key[1])
        shape = 'tree-shaped' if connected and len(pairs) == n - 1 else ('with a cycle' if connected else 'not connected')
        kind = f"{shape}, {'simple' if simple else 'double touches'}"
        out['kinds'][kind] += 1
        out['census_dim_all'][str(dim)] += 1
        if dim == 2:
            out['dim2_by_kind'][kind] += 1
        if shape != 'tree-shaped' or n < 2:
            continue
        p = predict(sizes, edges)
        if p.get('stall') or p.get('out'):
            out['stall_or_out'][kind] += 1
            continue
        measured = dim if dim is not None else (0 if outcome == 'closed' else None)
        ok = measured == p['D']
        out['compare'][f"{kind}: {'agree' if ok else 'differ'}"] += 1
        if ok:
            out['D'][f"{kind}: {p['D']}"] += 1
            if p['D'] == 2:
                out['why_D2'][f"{kind}: {p['why']}"] += 1
        else:
            out['disagree_max_share'][str(max(key[1]))] += 1
            if len(out['disagree_examples']) < 8:
                out['disagree_examples'].append([key, dim, outcome, p['D'], p['why']])
    for k in list(out):
        if isinstance(out[k], Counter):
            out[k] = dict(sorted(out[k].items()))
    dest.write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: v for k, v in out.items() if k != 'disagree_examples'}, indent=1))


if __name__ == '__main__':
    main()
