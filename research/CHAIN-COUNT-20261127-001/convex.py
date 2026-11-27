"""convex.py: structure only. P1 (convexity of the nodes holding a base): two core nodes of one rank that both hold a
chain base q and share a core parent also share a core parent holding q. Counted per start against chained twins."""
import sys, os, json, itertools, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'GRADED-ORDER-20261126-001'))
import order, twins
late = order.late
def fails(stars):
    M = late.Map(stars, 'nae'); out = []
    order.NodePiece.round1_groups = late.round1(*late.sizes_edges(stars))[4]
    try:
        for pts, tree, nch in M.pieces:
            P = order.NodePiece(pts, M.adj, M.chains, lambda v: v < M.n, None, lambda v: 1, M.cells)
            based = {q for q in M.chains if M.chains[q]}
            kids = collections.defaultdict(list)
            for n, ps in P.core_parents.items():
                for T in ps: kids[T].append(n)
            for U, ks in kids.items():
                for X, Y in itertools.combinations(ks, 2):
                    for q in P.points_of[X] & P.points_of[Y] & based:
                        if not any(q in P.points_of[W] for W in P.core_parents[X] & P.core_parents[Y]):
                            out.append(P.sizes_of[X] - 1)
    finally: order.NodePiece.round1_groups = None
    return out
tally = collections.Counter()
for fn in sys.argv[1:]:
    for l in open(fn):
        x = json.loads(l)
        try: f = fails(x['stars']); T = twins.twins(x['stars'])
        except RuntimeError: continue
        M = late.Map(x['stars'], 'nae')
        if M.cls != 'in' or not all(t for _, t, _ in M.pieces): continue
        tr = min((t['rank'] for t in T), default=None)
        tally[('chained twins' if T else 'no chained twins', 'P1 fails' if f else 'P1 holds')] += 1
        if f and T: tally[('fail rank - twin rank', min(f) - tr)] += 1
for k, v in sorted(tally.items(), key=str): print(v, k)
