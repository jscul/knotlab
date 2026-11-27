"""graded.py: the graded-order reading of a growth from its start, with its exception, tested on fresh starts.
GRADED-ORDER-20261126-001 (README.md).

The reading is LATE-VIEWS-20261126-001's late.GeneralPiece, unchanged: the valid sets of the start's map ordered by
inclusion; a birth's parents the valid sets it covers, its fresh distinctions the valid sets covering it, plus one per
chain at it. The exception this study states: a ROUTE CYCLE, two distinct blocks (outside every group cell) that meet one
group cell in two or more common knots, or two group cells sharing two knots.

    graded.py draw OUT.jsonl [KIND DRAWS PER]   seven-knot starts of a WEIGHTINGS-20261119-001B weighting (default 'grow',
                                        200,000 draws, 60 a bucket; the primary is 'tree+', 40,000 draws, 40 a bucket),
                                        seed 20261127; accepted tree-piece starts kept by stratum and route cycle, repeats
                                        removed; structure only, nothing grown
    graded.py grow LAW IN.jsonl OUT.jsonl   grow each listed start to round 24 (the look-alike study's growth, unchanged)
    graded.py score LAW GROWN.jsonl     the graded reading against the growth, round by round, both readings; a JSON line
                                        per start: stratum, route cycle, first differing round
"""
import sys, os, json, random, itertools, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
LV = os.path.join(ROOT, 'research', 'LATE-VIEWS-20261126-001')
sys.path.insert(0, LV)
import late, score                                  # the late-views study's predictor and comparison, unchanged

PER, DRAWS, SEED, ROUNDS = 60, 200000, 20261127, 24


def blocks_of(M):
    sizes, edges = late.sizes_edges(M.stars)
    n, nb, opn, live, groups, d = late.round1(sizes, edges)
    raw = {frozenset(nb[w] & M.live) for w in range(n) if len(nb[w] & M.live) >= 2}
    return [B for B in raw if not any(B < B2 for B2 in raw) and not any(B <= G for G in M.cells)]


def route_cycle(M):
    """two distinct blocks meeting one group cell in two or more common knots, or two cells sharing two knots"""
    bl = blocks_of(M)
    for G in M.cells:
        for B1, B2 in itertools.combinations(bl, 2):
            if len(B1 & B2 & G) >= 2: return True
    return any(len(G1 & G2) >= 2 for G1, G2 in itertools.combinations(M.cells, 2))


def split_pair(stars, law='nae'):
    """the advisor's static form of the exception: in some piece, a valid set (rank two or more) with two parents that
    share no parent in the graded order (the order is not lower semimodular there); computed from late.GeneralPiece
    without growing"""
    M = late.Map(stars, law)
    for pts, tree, nch in M.pieces:
        P = late.GeneralPiece(pts, M.adj, M.chains, lambda v: v < M.n, None, lambda v: 1, M.cells)
        for C, par in P.core_parents.items():
            if P.sizes_of[C] < 3: continue                  # size counts rank + 1: rank two or more
            for T1, T2 in itertools.combinations(par, 2):
                if not (P.core_parents.get(T1, set()) & P.core_parents.get(T2, set())): return True
    return False


def cells_share_two(M):
    return any(len(G1 & G2) >= 2 for G1, G2 in itertools.combinations(M.cells, 2))


def canon(sizes, edges):
    """a key for the start up to renaming (the Weisfeiler-Lehman hash of the knot multigraph with places on the knots and
    multiplicities on the pairs; two starts with one key are counted once, which can merge non-isomorphic starts only
    when the hash collides)"""
    import networkx as nx
    G = nx.Graph()
    for k, s in enumerate(sizes): G.add_node(k, p=str(s))
    mult = collections.Counter(tuple(sorted(e)) for e in edges)
    for (a, b), m in mult.items(): G.add_edge(a, b, m=str(m))
    return nx.weisfeiler_lehman_graph_hash(G, node_attr='p', edge_attr='m', iterations=4)


def rare(M):
    out = []
    if any(len(G & G2) == 1 for G, G2 in itertools.combinations(M.cells, 2)): out.append('group cells sharing a knot')
    if M.overlap[1]: out.append('group cells sharing two knots')
    if M.overlap[0]: out.append('a block meeting a group cell in two knots')
    return out


def stars_of(sizes, edges):
    stars = [[] for _ in sizes]; d = 0
    for a, b in edges: stars[a].append(d); stars[b].append(d); d += 1
    for k, s in enumerate(sizes):
        while len(stars[k]) < s: stars[k].append(d); d += 1
    return stars


def draw_cycles(out, kind, draws, per, seed):
    """starts whose map has a piece with a cycle (accepted otherwise), up to PER a bucket by the number of pieces with a
    cycle and whether a piece also has chains; repeats removed up to renaming; structure only"""
    path = ROOT + '/experiments/WEIGHTINGS-20261119-001B/WEIGHTINGS-20261119-001B-E001_weights/weightlib.py'
    spec = importlib.util.spec_from_file_location('wl', path); WL = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(WL)
    rng = random.Random(seed); kept = collections.defaultdict(list); seen = set(); tally = collections.Counter()
    for i in range(draws):
        sizes, edges = WL.sample(kind, int(os.environ.get('KNOTS', '7')), rng)
        stars = stars_of(sizes, edges)
        M = late.Map(stars)
        if M.cls != 'in': continue
        cyc = [p for p in M.pieces if not p[1]]
        if not cyc: continue
        b = (len(cyc), any(p[2] for p in cyc))
        tally[b] += 1
        key = canon(sizes, edges)
        if key in seen or len(kept[b]) >= per: continue
        seen.add(key); kept[b].append({'weighting': kind, 'draw': i, 'sizes': sizes, 'edges': edges, 'stars': stars,
                                       'pieces with a cycle': len(cyc), 'chains on a cycle piece': b[1]})
    with open(out, 'w') as f:
        for b in sorted(kept, key=str):
            for x in kept[b]: f.write(json.dumps(x) + '\n')
    print({str(k): v for k, v in tally.items()}, {str(b): len(v) for b, v in kept.items()})


def sample_start(WL, kind, n, rng):
    """a weighting's draw; 'tree+sPP' is the tree+ weighting with one more loose distinction on each knot with chance
    PP/100 (a scaffold of this line: it gives pendant points and chains to tree+ starts)"""
    if kind.startswith('tree+s'):
        q = int(kind[6:]) / 100
        sizes, edges = WL.sample('tree+', n, rng)
        return [s + (1 if rng.random() < q else 0) for s in sizes], edges
    return WL.sample(kind, n, rng)


def draw_twins(out, kind, draws, per, seed, exclude=()):
    """accepted tree-piece starts by the twin flags (twins.py): twins with a chain at a common grandparent, twins
    without one, and starts without twins, up to PER each; repeats removed up to renaming (and of EXCLUDE); also the
    count of drawn accepted starts whose core does not finish within the cap (an unending core); structure only"""
    import twins as TW
    path = ROOT + '/experiments/WEIGHTINGS-20261119-001B/WEIGHTINGS-20261119-001B-E001_weights/weightlib.py'
    spec = importlib.util.spec_from_file_location('wl', path); WL = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(WL)
    rng = random.Random(seed); kept = collections.defaultdict(list); seen = set(exclude); tally = collections.Counter()
    for i in range(draws):
        sizes, edges = sample_start(WL, kind, int(os.environ.get('KNOTS', '7')), rng)
        stars = stars_of(sizes, edges)
        M = late.Map(stars)
        if M.cls != 'in': continue
        if not all(t for _, t, _ in M.pieces): continue
        key = canon(sizes, edges)
        first = key not in seen
        import signal
        class _Late(Exception): pass
        def _al(*_): raise _Late()
        signal.signal(signal.SIGALRM, _al); signal.alarm(5)
        try:
            T = TW.twins(stars, chained_only=False); signal.alarm(0)
        except (RuntimeError, _Late):
            signal.alarm(0)
            if first: tally['unending core (over the cap of core births, or 5 s)'] += 1; seen.add(key)
            continue
        b = 'twins, chained' if any(t['chained'] for t in T) else ('twins, not chained' if T else 'no twins')
        if first: tally[b] += 1
        if not first or len(kept[b]) >= per: seen.add(key); continue
        seen.add(key); kept[b].append({'weighting': kind, 'draw': i, 'sizes': sizes, 'edges': edges, 'stars': stars,
                                       'twins': b})
    with open(out, 'w') as f:
        for b in sorted(kept):
            for x in kept[b]: f.write(json.dumps(x) + '\n')
    print(json.dumps({'distinct accepted tree-piece starts drawn': dict(tally), 'kept': {b: len(v) for b, v in kept.items()}}))


def draw(out, kind='grow', draws=DRAWS, per=PER, seed=SEED, exclude=()):
    path = ROOT + '/experiments/WEIGHTINGS-20261119-001B/WEIGHTINGS-20261119-001B-E001_weights/weightlib.py'
    spec = importlib.util.spec_from_file_location('wl', path); WL = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(WL)
    rng = random.Random(seed); kept = collections.defaultdict(list); seen = set(exclude); tally = collections.Counter()
    for i in range(draws):
        sizes, edges = WL.sample(kind, int(os.environ.get('KNOTS', '7')), rng)
        stars = stars_of(sizes, edges)
        key = canon(sizes, edges)
        M = late.Map(stars)
        if M.cls != 'in': tally[M.cls] += 1; continue
        if not all(tree for _, tree, _ in M.pieces): tally['a piece with a cycle'] += 1; continue
        r = rare(M)
        if not r: tally['accepted, no rare stratum'] += 1; continue
        rc = route_cycle(M)
        for s in r: tally[(s, rc)] += 1
        b = (r[0], rc)
        if key in seen or len(kept[b]) >= per: continue
        seen.add(key); kept[b].append({'weighting': kind, 'draw': i, 'sizes': sizes, 'edges': edges, 'stars': stars, 'strata': r,
                                       'route cycle': rc, 'split pair': split_pair(stars), 'cells share two': cells_share_two(M),
                                       'pendant points': len(M.chains)})
    with open(out, 'w') as f:
        for b in sorted(kept, key=str):
            for x in kept[b]: f.write(json.dumps(x) + '\n')
    print(json.dumps({str(k): v for k, v in sorted(tally.items(), key=str)}, indent=1))
    print({str(b): len(v) for b, v in kept.items()})


def grow(law, src, out):
    sys.path.insert(0, os.path.join(ROOT, 'research', 'LOOK-ALIKE-20261126-001'))
    import alike
    with open(out, 'w') as f:
        for l in open(src):
            x = json.loads(l)
            g = alike.grow(x['stars'], rounds=ROUNDS, knot_law=law)
            x.update(g); x.update({'knot law': law, 'kind': alike.kind([r['n'] for r in g['rows']], g['end'])})
            f.write(json.dumps(x) + '\n'); f.flush()


def score_file(law, src):
    for l in open(src):
        x = json.loads(l); st = {}
        P, why = late.predict(x['stars'], ROUNDS, law, static=st, general=True)
        M = late.Map(x['stars'], law)
        row = {'draw': x.get('draw', x.get('index')), 'name': x.get('name'), 'weighting': x.get('weighting'), 'law': law,
               'strata': x.get('strata'), 'stratum': st.get('stratum'), 'route cycle': route_cycle(M),
               'split pair': split_pair(x['stars'], law), 'cells share two': cells_share_two(M),
               'pendant points': len(M.chains), 'end': x['end'], 'rounds read': len(x['rows'])}
        if P is None: row['first differing round'] = 'not predicted: ' + why
        else: row['first differing round'] = score.compare(P, x)
        print(json.dumps(row), flush=True)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'draw': draw(sys.argv[2], *(sys.argv[3:4] or ['grow']), *[int(a) for a in sys.argv[4:6]])
    elif cmd == 'twins':                     # graded.py twins OUT KIND DRAWS PER SEED PRIOR.jsonl...
        prior = set()
        for fn in sys.argv[7:]:
            for l in open(fn):
                x = json.loads(l)
                if 'sizes' in x: prior.add(canon(x['sizes'], x['edges']))
        draw_twins(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), prior)
    elif cmd == 'cycles': draw_cycles(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]))
    elif cmd == 'heldout':                   # graded.py heldout OUT KIND DRAWS PER SEED PRIOR.jsonl...: repeats of PRIOR excluded
        prior = set()
        for fn in sys.argv[7:]:
            for l in open(fn):
                x = json.loads(l); prior.add(canon(x['sizes'], x['edges']))
        draw(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), prior)
    elif cmd == 'grow': grow(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == 'score': score_file(sys.argv[2], sys.argv[3])
