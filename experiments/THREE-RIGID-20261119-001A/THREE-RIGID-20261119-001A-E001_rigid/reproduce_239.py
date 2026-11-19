"""THREE-RIGID-20261119-001A, after the freeze (not part of the frozen test): Codex's GROWN-END-READING-20261119-001 construction,
rebuilt from its description in this program's engine, as far as is feasible at 239 junctions.
- The split core G: index junctions u_0..u_20; a middle junction w_ij for each pair {i, j}, meeting u_i and u_j, with a spoke to
  hub h0 when the pair's difference (the representative of j - i or i - j in 1..10) is at most 5, else to hub h1.
- The start: G without e = u_0 w_01, plus junctions U (meeting s = u_0) and V (meeting t = w_01), each with two loose distinctions.
- Checked here: legality, meeting once; the law's round gives 239 junctions and 643 distinctions; the renaming sigma (indices 2 and
  3 exchanged, names mapped by type) fixes every distinction at the growing end; sigma does not carry the equations; 105
  edge-disjoint paths join the hubs (maximum flow), so every bond separating them has at least 105 distinctions.
- Not checked here: that sigma keeps every pair and triple reading (198,135 and about 41 million), which Codex proves by the hub
  argument and its explicit small shores; exact bonds at this size are beyond this program's enumerators.
Run: .venv/bin/python -B reproduce_239.py -> reproduce_239.json beside the artifacts."""
import importlib.util
import json
import sys
from itertools import combinations
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import rigid_job as J  # noqa: E402
EX, L = J.EX, J.L
N = 21


def diff(i, j):
    d = (j - i) % N
    return d if d <= 10 else N - d


def build():
    names = {}
    junction = {}

    def edge(key, a, b):
        names[key] = len(names)
        junction.setdefault(a, set()).add(names[key])
        junction.setdefault(b, set()).add(names[key])
    for i, j in combinations(range(N), 2):
        w = ('w', i, j)
        edge(('in', i, j, i), ('u', i), w)
        edge(('in', i, j, j), ('u', j), w)
        edge(('spoke', i, j), w, ('h', 0 if diff(i, j) <= 5 else 1))
    return names, junction


def main():
    names, junction = build()
    e = names[('in', 0, 1, 0)]
    s, t = ('u', 0), ('w', 0, 1)
    for k in (s, t):
        junction[k].discard(e)
    nxt = max(names.values()) + 1
    junction[s].add(nxt)
    junction['U'] = {nxt, nxt + 1, nxt + 2}
    junction[t].add(nxt + 3)
    junction['V'] = {nxt + 3, nxt + 4, nxt + 5}
    order = sorted(junction, key=str)
    start = [frozenset(junction[k]) for k in order]
    out = {'start_junctions': len(start), 'start_distinctions': len(L.owners(start)),
           'meet_once': L.max_shared(start) < 2, 'every_junction_at_least_3': all(len(x) >= 3 for x in start)}
    stage = EX.grow1(start)
    out['round_1_junctions'] = len(stage)
    out['round_1_distinctions'] = len(L.owners(stage))
    # sigma: exchange indices 2 and 3 on names, by type
    swap = {2: 3, 3: 2}
    inv = {v: k for k, v in names.items()}
    sig = {}
    for x in L.owners(stage):
        if x in inv:
            key = inv[x]
            if key[0] == 'in':
                _, i, j, k = key
                i2, j2, k2 = swap.get(i, i), swap.get(j, j), swap.get(k, k)
                a, b = sorted((i2, j2))
                sig[x] = names[('in', a, b, k2)]
            else:
                _, i, j = key
                a, b = sorted((swap.get(i, i), swap.get(j, j)))
                sig[x] = names[('spoke', a, b)]
        else:
            sig[x] = x
    out['sigma_is_a_bijection'] = sorted(sig.values()) == sorted(sig)
    live = L.live_set(stage)
    out['live_junctions'] = len(live)
    out['sigma_fixes_the_growing_end'] = all(sig[x] == x for j in live for x in stage[j])
    labels = sorted(L.owners(stage))
    idx = {x: i for i, x in enumerate(labels)}
    w = [sum(1 << idx[x] for x in st) for st in stage]
    m = [sum(1 << idx[sig[x]] for x in st) for st in stage]
    out['sigma_carries_the_equations'] = L.rank(w + m) == L.rank(w)
    # hubs: maximum number of edge-disjoint paths in the junction graph (outside vertex included)
    g = nx.MultiGraph()
    for b, js in L.owners(stage).items():
        g.add_edge(*(js if len(js) == 2 else (js[0], 'o')))
    hub0 = order.index(('h', 0))
    hub1 = order.index(('h', 1))
    h = nx.Graph()
    for u, v in g.edges():
        if h.has_edge(u, v):
            h[u][v]['capacity'] += 1
        else:
            h.add_edge(u, v, capacity=1)
    out['edge_disjoint_paths_between_hubs'] = nx.maximum_flow_value(h, hub0, hub1)
    dest = ROOT / 'artifacts/THREE-RIGID-20261119-001A/THREE-RIGID-20261119-001A-E001_rigid'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'reproduce_239.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
