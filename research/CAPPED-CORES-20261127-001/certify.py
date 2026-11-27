"""certify.py: structure only. For each start whose node core passed the cap in TWO-EXCEPTIONS-20261127-001's counts,
build the node core rank by rank (Lemma R's round rule from the round-1 groups and offshoots, each birth a node) and
certify, piece by piece:
  FINISHES       the core runs out of births within a larger cap (BIG births);
  SUBSET FINISH  some rank's m births all share one parent: then every later rank is all the (k+1)-sets of them, and the
                 core ends after 2^m - m - 1 more births (the literature's Boolean lattice);
  REPEATS        the parent incidence between ranks r - 1 and r is isomorphic to that between ranks s - 1 and s for some
                 s < r: the round rule reads only that incidence, so the core repeats with period r - s forever;
  UNRESOLVED     none of these within BIG births or rank 60.
A start's class is its worst piece's (repeats or unresolved over finishes). Draws are those of counts.py with its seed.

    certify.py KIND KNOTS DRAWS SEED PER [BIG]"""
import sys, os, json, random, importlib.util, collections, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'GRADED-ORDER-20261126-001'))
import graded, order
late = order.late
import networkx as nx


def core_ranks(pts, M, groups, big, max_rank=60):
    """yield (rank, nodes, parent map) for the pure node core of one piece, rank 1 up; stop at big births"""
    adj = M.adj; is_knot = lambda v: v < M.n
    base = {}; nid = 0; par = {}
    knots = [v for v in pts if is_knot(v)]
    ones = [frozenset(g) for g in groups if set(g) <= set(pts)]
    ones += [frozenset([k, q]) for q in pts if not is_knot(q) for k in adj[q] if is_knot(k)]
    layer = []
    for C in ones:
        n = ('n', nid); nid += 1; par[n] = frozenset(('k', v) for v in C if is_knot(v)); layer.append(n)
    r = 1
    while layer and r <= max_rank:
        yield r, layer, par
        if nid > big: return
        nxt = []
        for S in order.round_rule(layer, par, big - nid):
            n = ('n', nid); nid += 1; par[n] = frozenset(S); nxt.append(n)
        layer, r = nxt, r + 1
    if not layer: yield r, [], par


def incidence(layer, par):
    G = nx.Graph()
    for n in layer:
        G.add_node(n, side=1)
        for T in par[n]: G.add_node(('p',) + tuple(T) if isinstance(T, tuple) else T, side=0); G.add_edge(n, ('p',) + tuple(T) if isinstance(T, tuple) else T)
    return G


def classify_piece(pts, M, groups, big):
    seen = collections.defaultdict(list)       # WL hash -> [(rank, graph)]
    total = 0; traj = []
    try:
        for c in _walk(pts, M, groups, big, seen, traj): return c
    except RuntimeError:
        return {'class': 'unresolved', 'births by rank': traj}
    return {'class': 'unresolved', 'births by rank': traj}


def _walk(pts, M, groups, big, seen, traj):
    total = 0
    for r, layer, par in core_ranks(pts, M, groups, big):
        traj.append(len(layer))
        if not layer: yield {'class': 'finishes', 'births': total, 'last rank': r - 1}; return
        total += len(layer)
        if r >= 2 and len(layer) >= 3 and frozenset.intersection(*[par[n] for n in layer]):
            m = len(layer)
            yield {'class': 'subset finish', 'births': total + 2 ** m - m - 1, 'rank': r, 'm': m}; return
        if r >= 2:
            G = incidence(layer, par)
            h = nx.weisfeiler_lehman_graph_hash(G, node_attr='side', iterations=4)
            for s, H in seen[h]:
                if nx.is_isomorphic(G, H, node_match=lambda a, b: a['side'] == b['side']):
                    yield {'class': 'repeats', 'rank': r, 'period': r - s, 'births per round': len(layer)}; return
            seen[h].append((r, G))


def classify_start(stars, big):
    M = late.Map(stars, 'nae')
    groups = late.round1(*late.sizes_edges(stars))[4]
    out = []
    for pts, tree, nch in M.pieces:
        out.append(classify_piece(pts, M, groups, big))
    rank = {'finishes': 0, 'subset finish': 0, 'repeats': 1, 'unresolved': 2}
    worst = max(out, key=lambda c: rank[c['class']])
    return worst['class'], out


if __name__ == '__main__':
    kind, n, draws, seed, per = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    big = int(sys.argv[6]) if len(sys.argv) > 6 else 20000
    spec = importlib.util.spec_from_file_location('wl', graded.ROOT + '/experiments/WEIGHTINGS-20261119-001B/WEIGHTINGS-20261119-001B-E001_weights/weightlib.py')
    WL = importlib.util.module_from_spec(spec); spec.loader.exec_module(WL)
    rng = random.Random(seed); seen = {}; tally = collections.Counter(); per_draw = collections.Counter(); done = 0
    os.environ['CORE_CAP'] = '5000'; order.NodePiece.cap = 5000
    for i in range(draws):
        sizes, edges = graded.sample_start(WL, kind, n, rng)
        stars = graded.stars_of(sizes, edges)
        M = late.Map(stars)
        if M.cls != 'in': continue
        key = graded.canon(sizes, edges)
        if key not in seen:
            # the counts' cap test (5,000 families, 250,000 pairs): only starts over it are certified here
            order.NodePiece.round1_groups = late.round1(*late.sizes_edges(stars))[4]; order.NodePiece.max_rank = 25
            capped = False
            try:
                for pts, tree, nch in M.pieces: order.NodePiece(pts, M.adj, M.chains, lambda v: v < M.n, None, lambda v: 1, M.cells)
            except RuntimeError: capped = True
            finally: order.NodePiece.round1_groups = None; order.NodePiece.max_rank = None
            if not capped: seen[key] = None; continue
            if done >= per: seen[key] = 'not certified (past the prefix)'
            else:
                cls, pieces = classify_start(stars, big); done += 1; seen[key] = cls
                print(json.dumps({'draw': i, 'class': cls, 'pieces': pieces}), flush=True)
            tally[seen[key]] += 1
        if seen[key] is not None: per_draw[seen[key]] += 1
    print(json.dumps({'weighting': kind, 'knots': n, 'draws': draws, 'seed': seed, 'big': big, 'per': per,
                      'capped distinct starts': dict(tally), 'capped accepted draws with repeats': dict(per_draw)}))
