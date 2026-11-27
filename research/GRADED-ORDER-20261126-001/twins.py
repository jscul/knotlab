"""twins.py: the exception to the node reading's decoupling (post hoc): two core births of one round, built by the round
rule, that share two parents C and D, with a chain based at a point of a common parent of C and D. README.md.

    twins.py FILE.jsonl ...     the starts of the files that have such twins (each start's stars), and a count"""
import sys, json, gzip, itertools
import order, late


def twins(stars, law='nae', chained_only=True):
    """twin births of the core: two core births of one round sharing two parents C and D; with chained_only, only those
    with a chain based at a point of a common parent of C and D"""
    M = late.Map(stars, law); out = []
    if M.cls != 'in' or not all(t for _, t, _ in M.pieces): return out
    order.NodePiece.round1_groups = late.round1(*late.sizes_edges(stars))[4]
    try:
        for pts, tree, nch in M.pieces:
            P = order.NodePiece(pts, M.adj, M.chains, lambda v: v < M.n, None, lambda v: 1, M.cells)
            chained = {v for v in pts if M.chains.get(v, 0)}
            for A, B in itertools.combinations(list(P.points_of), 2):
                if P.sizes_of[A] != P.sizes_of[B] or P.sizes_of[A] < 3: continue
                common = P.core_parents[A] & P.core_parents[B]
                for C, D in itertools.combinations(common, 2):
                    ch = any(P.points_of[T] & chained for T in P.core_parents[C] & P.core_parents[D])
                    if ch or not chained_only:
                        out.append({'rank': P.sizes_of[A] - 1, 'shared parents': len(common), 'chained': ch}); break
    finally:
        order.NodePiece.round1_groups = None
    return out


if __name__ == '__main__':
    n = has = 0
    for fn in sys.argv[1:]:
        op = gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)
        for l in op:
            x = json.loads(l)
            try: t = twins(x['stars'])
            except Exception: continue
            n += 1
            if t: has += 1; print(json.dumps({'file': fn, 'draw': x.get('draw', x.get('index')), 'name': x.get('name'), 'twins': t[:3]}))
    print(json.dumps({'starts': n, 'with twins': has}))
