"""Machine check for CAP-CHAINS-20261119-001A-P001 (a separate algorithm, same task).

Part 1, Theorem 1 (cap 5, every knot live) on every graph it can concern.
- **The graphs.** Every connected simple graph of 1 to NMAX knots with no cycle of length 3, 4 or 6 (with every knot live, the
  class excludes them: Lemma 1) such that deg_k + sum over w in N(k) of (deg_w - 1) <= 5 at every knot: the necessary condition p_k >= sh_k + open_k
  >= deg_k + d_k. They are enumerated by adding one knot at a time, up to isomorphism; both conditions pass to connected subgraphs.
- **Checked on each graph:** its non-leaves form one path or one cycle (Lemma 2).
- **Checked on each open assignment.** That is, every assignment open_k in [max(1, d_k), 5 - deg_k], a superset of what
  multiplicities and surplus can realize. The pieces and rays of the relayed map are counted from the definitions, written here,
  and no piece carries more than two rays (Theorem 1).

Part 2, the program's own reader. On every graph of Part 1 with at most NREAD knots, every simple start (p_k = deg_k + open_k, 3
<= p_k <= 5) is read by DOUBLE-IDENT's classify and dims.predict. No start in the class is read as three or more dimensions.

Part 3, the touch census. Every census arrangement in the class with no dead knot has at most two rays in a piece, by the counter
of Part 1. Multiplicities are as recorded.

Part 4, the two families of Theorem 2.
- S_R: cap 6, all live, R rays in one piece.
- T_h: cap 5, with dead hubs, 3·2^(h-1) rays in one piece.

For each: the class, the largest knot, the ray count, dims.predict, the growth against the relayed cover per round to round TM, and
the engine's per-round counts (joinlib.grow) with their finite differences.

python3 -B machine_check.py <out.json>"""
import importlib.util
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_s = importlib.util.spec_from_file_location('st_lib_cc', ROOT / 'experiments/SCALE-THEOREM-20261119-001B/SCALE-THEOREM-20261119-001B-E001_shares/scalelib.py')
SL = importlib.util.module_from_spec(_s)
sys.modules['st_lib_cc'] = SL
_s.loader.exec_module(SL)
DC, DM = SL.DC, SL.DM
J = DC.J
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402

NMAX, NREAD, TM, ROUNDS = 12, 9, 8, 24


# ---- Part 1: an independent ray counter, from the definitions ---------------------------------------------------------------
def rays_per_piece(n, nbr, opn):
    """nbr: knot -> set of neighbours (simple); opn: knot -> open count (live iff >= 1).  Returns (list of ray counts per piece,
    live knots).  Groups are candidate pairs (the class has no group of three); d_k counts k's partners."""
    live = {k for k in range(n) if opn[k] >= 1}
    blocks = [frozenset(nbr[w] & live) for w in range(n) if len(nbr[w] & live) >= 2]
    partners = defaultdict(set)
    for B in blocks:
        for u, v in itertools.combinations(sorted(B), 2):
            partners[u].add(v)
            partners[v].add(u)
    d = {k: len(partners[k]) for k in live}
    R = {1: 2, 2: 1}
    ray = {k: (opn[k] - d[k]) * R.get(opn[k], 0) for k in live}
    # pieces: components of the point-block incidence
    G = nx.Graph()
    G.add_nodes_from(('p', k) for k in live)
    for i, B in enumerate(blocks):
        for k in B:
            G.add_edge(('b', i), ('p', k))
    pieces = [sorted(x[1] for x in comp if x[0] == 'p') for comp in nx.connected_components(G)]
    out = []
    for P in pieces:
        out.append(sum(ray[k] for k in P))
    # a relay adds two rays to a finite piece; a finite piece has no ray and no cycle, so it is at most two
    return out, d


def girth_ok(G):
    """No cycle of length 3, 4 or 6: what the class leaves when every knot is live (Lemma 1)."""
    if nx.girth(G) < 5:
        return False
    return not any(len(c) == 6 for c in nx.simple_cycles(G, length_bound=6))


def cap_ok(G, cap):
    return all(G.degree(k) + sum(G.degree(w) - 1 for w in G[k]) <= cap for k in G)


def enumerate_graphs(cap, nmax):
    levels = {1: [nx.empty_graph(1)]}
    for n in range(1, nmax):
        seen = defaultdict(list)
        for G in levels[n]:
            nodes = list(G.nodes())
            for r in range(1, min(len(nodes), 5) + 1):
                for S in itertools.combinations(nodes, r):
                    H = G.copy()
                    H.add_node(n)
                    H.add_edges_from((n, s) for s in S)
                    if not cap_ok(H, cap) or not girth_ok(H):
                        continue
                    h = nx.weisfeiler_lehman_graph_hash(H, iterations=4)
                    if any(nx.is_isomorphic(H, K) for K in seen[h]):
                        continue
                    seen[h].append(H)
        levels[n + 1] = [K for v in seen.values() for K in v]
    return levels


def core_shape(G):
    core = [k for k in G if G.degree(k) >= 2]
    if len(core) <= 1:
        return 'star or smaller'
    C = G.subgraph(core)
    degs = [C.degree(k) for k in core]
    if not nx.is_connected(C) or max(degs) > 2:
        return 'other'
    return 'cycle' if all(x == 2 for x in degs) else 'path'


def part1(levels, cap):
    out = {}
    worst = 0
    for n, gs in levels.items():
        shapes = Counter()
        assignments = 0
        for G in gs:
            shapes[core_shape(G)] += 1
            nbr = {k: set(G[k]) for k in G}
            deg = {k: G.degree(k) for k in G}
            dd = {k: sum(deg[w] - 1 for w in G[k]) for k in G}
            ranges = [range(max(1, dd[k]), cap - deg[k] + 1) for k in range(n)]
            for opn in itertools.product(*ranges):
                rp, d = rays_per_piece(n, nbr, list(opn))
                assert all(d[k] == dd[k] for k in range(n))
                assignments += 1
                worst = max([worst] + rp)
        out[n] = {'graphs': len(gs), 'core': dict(shapes), 'assignments': assignments}
    return out, worst


# ---- Part 2: the program's reader on simple starts --------------------------------------------------------------------------
def part2(levels, cap):
    tally = Counter()
    for n, gs in levels.items():
        if n > NREAD or n < 2:
            continue
        for G in gs:
            e = sorted(tuple(sorted(x)) for x in G.edges())
            deg = {k: G.degree(k) for k in G}
            ranges = [range(max(3, deg[k] + 1), cap + 1) for k in range(n)]
            for sizes in itertools.product(*ranges):
                sizes = list(sizes)
                c = DC.classify(sizes, e)
                if c in ('stall', 'out'):
                    tally[c] += 1
                    continue
                D, why = DM.predict(sizes, e)
                tally[(c, SL.label(D))] += 1
    bad = [k for k in tally if isinstance(k, tuple) and k[0] == 'in' and k[1].startswith('dimension') and int(k[1].split()[1]) >= 3]
    return {' | '.join(map(str, k)) if isinstance(k, tuple) else k: v for k, v in sorted(tally.items(), key=str)}, bad


def part2b(nmax, cap):
    """Lemma 1's 6-cycle step on the program's reader: every simple all-live start, up to nmax knots and within the cap, whose
    graph has girth >= 5 and a 6-cycle is out of the class."""
    tally = Counter()
    for n in range(6, nmax + 1):
        for G in nx.graph_atlas_g() if n <= 7 else []:
            if G.number_of_nodes() != n or not nx.is_connected(G) or nx.girth(G) < 5 or not cap_ok(G, cap):
                continue
            if not any(len(c) == 6 for c in nx.simple_cycles(G, length_bound=6)):
                continue
            e = sorted(tuple(sorted(x)) for x in G.edges())
            deg = {k: G.degree(k) for k in G}
            for sizes in itertools.product(*[range(max(3, deg[k] + 1), cap + 1) for k in range(n)]):
                tally[DC.classify(list(sizes), e)] += 1
    return dict(tally)


# ---- Part 3: the touch census -----------------------------------------------------------------------------------------------
def part3():
    R = load_results(str(ROOT / 'runs/touch-census'))
    keys = [(tuple(a['key'][0]), tuple(a['key'][1])) for r in R.values() if r.get('status') == 'ok' for a in r['result']['arrangements']]
    tally = Counter()
    worst = 0
    for key in keys:
        sizes, e = DC.edges_of(key)
        n = len(sizes)
        if DC.classify(sizes, e) not in ('in', 'one loose', 'none'):
            continue
        sh = Counter()
        nbr = defaultdict(set)
        for a, b in e:
            sh[a] += 1
            sh[b] += 1
            nbr[a].add(b)
            nbr[b].add(a)
        opn = [sizes[k] - sh[k] for k in range(n)]
        if min(opn) < 1:
            tally['in the class, with a dead knot'] += 1
            continue
        rp, d = rays_per_piece(n, {k: nbr[k] for k in range(n)}, opn)
        tally['in the class, every knot live'] += 1
        worst = max([worst] + rp)
    return dict(tally), worst


# ---- Part 4: the families ---------------------------------------------------------------------------------------------------
def family_S(R):
    """Cap 6, all live: a cubic tree with R leaves (R - 2 branch knots on a path, each end branch carrying two arms, each inner one
    arm), every edge subdivided once, every arm ending branch - a - leaf."""
    edges, nxt = [], 0

    def new():
        nonlocal nxt
        nxt += 1
        return nxt - 1
    branches = [new() for _ in range(R - 2)]
    for b, b2 in zip(branches, branches[1:]):
        u = new()
        edges += [(b, u), (u, b2)]
    for i, b in enumerate(branches):
        arms = 3 - (1 if i > 0 else 0) - (1 if i < len(branches) - 1 else 0)
        for _ in range(arms):
            a, l = new(), new()
            edges += [(b, a), (a, l)]
    n = nxt
    return J.bare_sizes(n, edges), [tuple(sorted(x)) for x in edges]


def family_T(h):
    """Cap 5 with dead hubs: hub H (3 places, all shared) with three members M (5 places); each member joins a connector X (3
    places) whose other neighbour is a member of a new hub with two fresh members (depth < h) or an end K (3 places)."""
    sizes, edges = [], []

    def new(p):
        sizes.append(p)
        return len(sizes) - 1

    def hub(depth, entry=None):
        H = new(3)
        members = [entry] if entry is not None else []
        while len(members) < 3:
            members.append(new(5))
        for M in members:
            edges.append((H, M))
        for M in members[(1 if entry is not None else 0):]:
            X = new(3)
            edges.append((M, X))
            if depth < h:
                M2 = new(5)
                edges.append((X, M2))
                hub(depth + 1, M2)
            else:
                K = new(3)
                edges.append((X, K))
    hub(1)
    return sizes, [tuple(sorted(x)) for x in edges]


def read_family(sizes, e, rounds):
    n = len(sizes)
    c = DC.classify(sizes, e)
    sh = Counter()
    nbr = defaultdict(set)
    for a, b in e:
        sh[a] += 1
        sh[b] += 1
        nbr[a].add(b)
        nbr[b].add(a)
    opn = [sizes[k] - sh[k] for k in range(n)]
    rp, d = rays_per_piece(n, {k: nbr[k] for k in range(n)}, opn)
    D, why = DM.predict(sizes, e)
    DC.T = TM
    a, b = DC.growth(sizes, e), DC.model(sizes, e)
    agree = all(a.get(t, {}) == b.get(t, {}) for t in range(TM + 1) if t in a or t in b)
    g = J.grow(sizes, e, rounds=rounds)
    cs = g['counts']
    diffs = [cs]
    for _ in range(max(1, (D if isinstance(D, int) else 2))):
        diffs.append([y - x for x, y in zip(diffs[-1], diffs[-1][1:])])
    return {'knots': n, 'max_places': max(sizes), 'dead': sum(o == 0 for o in opn), 'class': c, 'rays_per_piece': sorted(rp, reverse=True),
            'reading': SL.label(D), 'agree_to_round': TM if agree else None, 'engine': {k: g[k] for k in ('outcome', 'rounds', 'junctions')},
            'counts': cs, 'last_differences': {f'order {i}': diffs[i][-6:] for i in range(1, len(diffs))}}


def main():
    dest = Path(sys.argv[1])
    levels = enumerate_graphs(5, NMAX)
    p1, worst1 = part1(levels, 5)
    p2, bad2 = part2(levels, 5)
    p2b = part2b(7, 5)
    p3, worst3 = part3()
    fam = {}
    for R in (3, 4, 5, 6):
        s, e = family_S(R)
        fam[f'S_{R}'] = read_family(s, e, ROUNDS if R <= 5 else 18)
    for h in (1, 2):
        s, e = family_T(h)
        fam[f'T_{h}'] = read_family(s, e, ROUNDS if h == 1 else 16)
    for L, leaf in ((5, False), (7, False), (8, False), (7, True)):
        e = [(i, (i + 1) % L) for i in range(L)] + ([(0, L)] if leaf else [])
        n = L + (1 if leaf else 0)
        e = [tuple(sorted(x)) for x in e]
        fam[f'C_{L}' + (' with a leaf' if leaf else '')] = read_family(J.bare_sizes(n, e), e, 16)
    out = {'part1': p1, 'part1_most_rays_in_a_piece': worst1, 'part2': p2, 'part2_three_plus_in_class': bad2, 'part2b_six_cycles': p2b,
           'part3': p3, 'part3_most_rays_in_a_piece': worst3, 'families': fam}
    dest.write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: v for k, v in out.items() if k != 'families'}, default=str)[:3000])
    for k, v in fam.items():
        print(k, {x: v[x] for x in ('knots', 'max_places', 'dead', 'class', 'rays_per_piece', 'reading', 'agree_to_round')}, v['last_differences'])


if __name__ == '__main__':
    main()
