"""strata.py: structure only, before any start is scored: for each start with a piece with a cycle, whether the core of
each piece finishes by rank 25 (Lemma R's round rule on nodes, GRADED-ORDER-20261126-001/order.py), whether the pieces
hold chains, and twins (twins.py, cycles=True). CYCLE-READ-20261127-001, README.md.

    strata.py FILE.jsonl ...      one line a start, then the counts by stratum"""
import sys, os, json, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'GRADED-ORDER-20261126-001'))
import order, twins
late = order.late


def stratum(stars):
    M = late.Map(stars, 'nae')
    order.NodePiece.round1_groups = late.round1(*late.sizes_edges(stars))[4]
    order.NodePiece.max_rank = 25
    out = []
    try:
        for pts, tree, nch in M.pieces:
            try:
                P = order.NodePiece(pts, M.adj, M.chains, lambda v: v < M.n, None, lambda v: 1, M.cells)
                fin = 'finishes' if P.finished else 'does not finish by rank 25'
            except RuntimeError:
                fin = 'unending (over the cap)'
            out.append({'cycle by count': not tree, 'core': fin, 'chains': nch})
    finally:
        order.NodePiece.round1_groups = None; order.NodePiece.max_rank = None
    try: T = twins.twins(stars, chained_only=False, cycles=True)
    except RuntimeError: return out, 'twins not read (core over the cap)'
    return out, ('twins, chained' if any(t['chained'] for t in T) else 'twins, not chained' if T else 'no twins')


if __name__ == '__main__':
    tally = collections.Counter()
    for fn in sys.argv[1:]:
        for i, l in enumerate(open(fn)):
            x = json.loads(l)
            pcs, tw = stratum(x['stars'])
            cyc = [p for p in pcs if p['cycle by count']]
            key = ('core ' + ' / '.join(sorted({p['core'] for p in cyc})),
                   'chains on it' if any(p['chains'] for p in cyc) else 'no chains on it', tw)
            tally[(fn,) + key] += 1
            print(json.dumps({'file': fn, 'line': i + 1, 'draw': x.get('draw', x.get('index')), 'pieces': pcs,
                              'twins': tw}), flush=True)
    for k, v in sorted(tally.items()): print(v, k)
