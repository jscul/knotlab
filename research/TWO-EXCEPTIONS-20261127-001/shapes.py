"""shapes.py: structure only. On each start whose node core finishes, the first round at which Lemma R's round rule on the
extended nodes (CHAIN-COUNT-20261127-001, ext.py) differs from the extended nodes' parent sets, and the shape of the
difference: every family the round rule makes that no extended node has as its parents (EXTRA), and every parent set
P(y) the round rule does not make (MISSING), each described by its members' chain totals and cores.
  MERGE  (chained twins): one extra family {(T1,a),(T2,a),(D1,a-e),(D2,a-e)} = the union of two missing P(y)
  SPLIT  (failed lifts): two extra families, each one lift with all shortenings, whose union is one missing P(y)

    shapes.py FILE.jsonl ... [--rounds R]"""
import sys, os, json, gzip, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'CHAIN-COUNT-20261127-001'))
import ext
order, twins, late = ext.order, ext.twins, ext.late


def shape(extra, missing):
    """merge: one family the round rule makes holds every member of the cluster's missing parent sets (and possibly
    pure twins that hold no chain base); split: the round rule's families cover exactly one missing parent set"""
    ex = [frozenset(S) for S in extra]; mi = [frozenset(S) for S in missing]
    if len(ex) == 1 and mi and frozenset().union(*mi) <= ex[0]:
        return 'merge' if frozenset().union(*mi) == ex[0] else 'merge with pure twins'
    if len(mi) == 1 and len(ex) >= 2 and frozenset().union(*ex) == mi[0]: return 'split'
    return 'other'


def kind_of(X, missing):
    """the mechanism of one family X the round rule makes and no extended node has as parents: a TWIN FAMILY has upper
    members (T_i, a) on one vector with two cores or more and lower members on one vector a - e with two cores or more
    (Lemma D's chained-twin case); a LIFT SPLIT lies inside one missing parent set (two lifts with no common parent)"""
    X = frozenset(X); tot = lambda x: sum(a for _, a in x[1])
    hi = max(tot(x) for x in X); up = [x for x in X if tot(x) == hi]; lo = [x for x in X if tot(x) < hi]
    if lo and len({x[1] for x in up}) == 1 and len({x[0] for x in up}) >= 2 \
            and len({x[1] for x in lo}) == 1 and len({x[0] for x in lo}) >= 2:
        return 'twin family'
    if any(X < frozenset(M) for M in missing): return 'lift split'
    return 'other'


def first_failure(stars, R):
    M = late.Map(stars, 'nae')
    if M.cls != 'in': return None
    order.NodePiece.round1_groups = late.round1(*late.sizes_edges(stars))[4]
    order.NodePiece.max_rank = 25
    out = None
    try:
        for pts, tree, nch in M.pieces:
            P = order.NodePiece(pts, M.adj, M.chains, lambda v: v < M.n, None, lambda v: 1, M.cells)
            if not P.finished: return None
            by_round, par = ext.extended(P, M.chains, R)
            for t in range(1, R):
                want = order.round_rule(by_round[t], par)
                have = collections.Counter(par[y] for y in by_round[t + 1] if len(par[y]) >= 2)
                if want != have:
                    extra = list((want - have).elements()); missing = list((have - want).elements())
                    kinds = collections.Counter(kind_of(S, missing) for S in set(extra))
                    f = {'round': t + 1, 'shapes': dict(kinds)}
                    if out is None or f['round'] < out['round']: out = f
                    break
    finally:
        order.NodePiece.round1_groups = None; order.NodePiece.max_rank = None
    return out or {'round': None}


def conditions(stars):
    """N1 (chained twins), N2 and N3 failures, as ext.py and twins.py read them"""
    r = ext.check_start(stars, 2)
    T = twins.twins(stars, cycles=True)
    return {'N1': not T, 'N2': not r['star fails'], 'N3': not r['n3 fails']} if r else None


if __name__ == '__main__':
    R = int(sys.argv[sys.argv.index('--rounds') + 1]) if '--rounds' in sys.argv else 10
    tally = collections.Counter()
    for fn in [a for a in sys.argv[1:] if a.endswith(('.jsonl', '.gz'))]:
        op = gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)
        for l in op:
            x = json.loads(l)
            try:
                c = conditions(x['stars']); f = first_failure(x['stars'], R)
            except RuntimeError: tally['core over the cap'] += 1; continue
            if c is None or f is None: tally['core does not finish'] += 1; continue
            key = ('N1' if c['N1'] else 'not N1') + ' ' + ('N2' if c['N2'] else 'not N2') + ' ' + ('N3' if c['N3'] else 'not N3')
            tally[(key, 'lemma holds' if f['round'] is None else 'fails: ' + ','.join(sorted(f['shapes'])))] += 1
            if f['round'] is not None:
                print(json.dumps({'file': os.path.basename(fn), 'draw': x.get('draw', x.get('index')), 'conditions': key, **f}), flush=True)
    for k, v in sorted(tally.items(), key=str): print(v, k)
