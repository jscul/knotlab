import sys, collections
sys.path.insert(0, '.')
import layers as LY
LY.TIE_CAP = 10**6
sys.path.insert(0, '../LATE-VIEWS-20261126-001')
import late

def funded(knots, extra=0, minimum=2):
    knots = [list(k) for k in knots]; nd = [1 + max(x for k in knots for x in k)]
    sizes, edges = late.sizes_edges(knots); sh = collections.Counter(x for e in edges for x in e)
    dem = late.round1([len(k) + 10 for k in knots], edges)[5]
    for i, k in enumerate(knots):
        for _ in range(max(minimum, dem[i] + extra) - (len(k) - sh[i])): k.append(nd[0]); nd[0] += 1
    return tuple(tuple(k) for k in knots)

def tree():
    # centre 0; knots 1..3 on it; two more on each (4..9): nine shared distinctions
    edges = [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 6), (2, 7), (3, 8), (3, 9)]
    knots = [[] for _ in range(10)]
    for d, (a, b) in enumerate(edges): knots[a].append(d); knots[b].append(d)
    return knots, edges

def report(name, start, rd):
    st, status, births = LY.forbid.grown(start, 'parity', 'ordinary')
    if status != 'funded': print(name, status); return
    a = LY.analyse(st, rd)[0]
    old = {x for k in start for x in k}
    left = [sum(1 for x in k if x in old and sum(1 for kk in st if x in kk) == 1) for k in st[:len(start)]]
    print(name, 'classes', a['classes'], 'ring labels', a['sums of ring parities that are labels'], 'old knots keeping loose', sum(1 for v in left if v), 'capped', a['ties capped'], flush=True)

knots, edges = tree()
allshared = [list(range(9))]
report('ten-knot tree, demand funded', funded(knots), allshared)
report('ten-knot tree, demand + 1', funded(knots, extra=1), allshared)
for n in (4, 5, 7):
    s, rd = LY.build([n], [])
    report('ring of %d as built' % n, s, rd)
    ring = [[i, (i + 1) % n] for i in range(n)]
    ring = [[ (i - 1) % n, i] for i in range(n)]
    report('ring of %d, demand + 1' % n, funded(ring, extra=1, minimum=0), [list(range(n))])
