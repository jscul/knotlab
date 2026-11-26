"""control_r.py: expectation 1's control. Lemma R of REDUCE-BLOCKS-20261119-001 (refereed): from round 1 on, ordinary
growth reads a start only through its live knots, their open counts and the down-closure of its live-neighbour sets
(the sets of live knots that share a distinction with one knot). Two starts with the same such data, up to a
relabelling of the live knots, must grow alike from round 1.  This lists every pair of grown starts with the same
data (the maximal live-neighbour sets fix the down-closure) and whether they agree exactly from round 1."""
import json, sys, itertools, collections
def rdata(stars):
    cnt = collections.Counter(d for k in stars for d in k)
    n = len(stars); loose = [sum(1 for d in k if cnt[d] == 1) for k in stars]
    live = [i for i in range(n) if loose[i] > 0]
    nb = [set(j for j in range(n) if j != i and set(stars[i]) & set(stars[j])) for i in range(n)]
    sets = {frozenset(j for j in nb[w] if j in live) for w in range(n)}
    sets = {s for s in sets if s and not any(s < t for t in sets)}
    best = None
    for perm in itertools.permutations(live):
        m = {v: i for i, v in enumerate(perm)}
        key = (tuple(loose[v] for v in perm), tuple(sorted(tuple(sorted(m[v] for v in s)) for s in sets)))
        if best is None or key < best: best = key
    return best
if __name__ == '__main__':
    xs = [json.loads(l) for p in sys.argv[1:] for l in open(p)]
    groups = collections.defaultdict(list)
    for x in xs: groups[json.dumps(rdata(x['stars']))].append(x)
    pairs = [(a, b) for g in groups.values() for a, b in itertools.combinations(g, 2)]
    same = sum(1 for a, b in pairs if [r['sig1'] for r in a['rows']] == [r['sig1'] for r in b['rows']])
    print(json.dumps({'starts': len(xs), 'pairs with the same data': len(pairs), 'of which identical in sig1 from round 1': same,
                      'pairs': [[[a['n knots'], a['index']], [b['n knots'], b['index']]] for a, b in pairs]}))
