"""layers.py: do several rings' whole-loop classes obey a rule among themselves?  LAYERS-20261126-001 (a check by the
thread, not registered); README.md.  Exploration before any freeze.

Under parity a stage's allowed changes Z are the null space of its knots' laws (loose distinctions free). As in
BOTH-LONG-20261126-001's graph reading (knots as vertices, a shared distinction as a line between its two holders, a loose
distinction as a line to one unconstrained vertex), the moves are the shortest cycles through each distinction, every
tie kept up to TIE_CAP; H is their span and the classes are Z/H. A ring's LABEL is the parity of its own shared ring
distinctions at the start; it is a class label when it has even overlap with every move and odd overlap with some
allowed change. The LABELS' JOINT RANK is the dimension of the values the ring labels take together over the allowed
states; it is less than the number of labels exactly when some sum of labels is fixed (a relation among the rings).
Also read: whether one round keeps the allowed changes of the old distinctions (their projection) unchanged.

    layers.py explore OUT.jsonl        the constructed multi-ring starts, at the start and after rounds of growth under
                                       the ordinary count and the two forbidding arms (one fewer, the arity floor)"""
import sys, json, itertools, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'TWO-CLASS-SIGN-20261126-001'))
import classes
forbid = classes.forbid
TIE_CAP = 64


def build(rings, joins, loose=2):
    """knots as lists of distinction ids: each ring a cycle of knots sharing one distinction with each neighbour;
    joins: ('share', (r, i), (s, j)) makes knot j of ring s the same knot as knot i of ring r; ('touch', (r, i), (s, j))
    gives them one shared distinction; ('chain', (r, i), (s, j), k) puts a path of k knots between them"""
    knots = []; ring_knots = []; ring_dist = []; nd = [0]
    def d():
        nd[0] += 1; return nd[0] - 1
    alias = {}
    for r, n in enumerate(rings):
        ids = []
        for i in range(n):
            key = (r, i)
            ids.append(key)
        ring_knots.append(ids)
    for j in joins:
        if j[0] == 'share': alias[j[2]] = j[1]
    def res(key):
        while key in alias: key = alias[key]
        return key
    names = {}
    for r, ids in enumerate(ring_knots):
        for key in ids:
            k = res(key)
            if k not in names: names[k] = len(knots); knots.append([])
    for r, n in enumerate(rings):
        rd = []
        for i in range(n):
            a = names[res((r, i))]; b = names[res((r, (i + 1) % n))]
            x = d(); knots[a].append(x); knots[b].append(x); rd.append(x)
        ring_dist.append(rd)
    for j in joins:
        if j[0] == 'touch':
            a = names[res(j[1])]; b = names[res(j[2])]; x = d(); knots[a].append(x); knots[b].append(x)
        if j[0] == 'chain':
            a = names[res(j[1])]; b = names[res(j[2])]; prev = a
            for _ in range(j[3]):
                knots.append([]); c = len(knots) - 1; x = d(); knots[prev].append(x); knots[c].append(x); prev = c
            x = d(); knots[prev].append(x); knots[b].append(x)
    for k in knots:
        while len(k) < 3: k.append(d())               # every knot at least three places
    sys.path.insert(0, str(HERE.parent / 'LATE-VIEWS-20261126-001'))
    import late                                       # round-1 groups read from the start alone
    sizes, edges = late.sizes_edges(knots)
    sh = collections.Counter(x for e in edges for x in e)
    demand = late.round1([len(k) + 10 for k in knots], edges)[5]
    for i, k in enumerate(knots):                     # funded: loose distinctions max(loose, demand)
        for _ in range(max(loose, demand[i]) - (len(k) - sh[i])): k.append(d())
    return tuple(tuple(k) for k in knots), ring_dist


def null(rows, n):
    return classes.nullspace(rows, n)


def analyse(supports, ring_dist, old=None):
    names = sorted({x for r in supports for x in r}); idx = {x: i for i, x in enumerate(names)}; n = len(names)
    holders = collections.defaultdict(list)
    for k, r in enumerate(supports):
        for x in r: holders[x].append(k)
    rows = [sum(1 << idx[x] for x in r) for r in supports]
    Z = null(rows, n)
    U = len(supports)
    adj = collections.defaultdict(list)                # vertex -> [(other, distinction index)]
    for x, h in holders.items():
        a, b = (h[0], h[1]) if len(h) == 2 else (h[0], U)
        adj[a].append((b, idx[x])); adj[b].append((a, idx[x]))
    moves = set(); capped = 0
    for x, h in holders.items():
        a, b = (h[0], h[1]) if len(h) == 2 else (h[0], U); e = idx[x]
        dist = {a: 0}; Q = [a]
        for v in Q:
            for w, f in adj[v]:
                if f != e and w not in dist: dist[w] = dist[v] + 1; Q.append(w)
        if b not in dist: continue
        paths = [(b, 0)]; out = []
        while paths and len(out) < TIE_CAP:
            v, mask = paths.pop()
            if v == a: out.append(mask); continue
            for w, f in adj[v]:
                if f != e and dist.get(w, -9) == dist[v] - 1: paths.append((w, mask | (1 << f)))
        if paths: capped += 1
        for m in out: moves.add(m | (1 << e))
    dH = classes.rank(list(moves))
    res = {'distinctions': n, 'dim Z': len(Z), 'dim H': dH, 'classes': 2 ** (len(Z) - dH), 'ties capped': capped}
    labels = []
    for r, rd in enumerate(ring_dist):
        lab = sum(1 << idx[x] for x in rd if x in idx)
        is_label = all(bin(lab & m).count('1') % 2 == 0 for m in moves) and any(bin(lab & z).count('1') % 2 for z in Z)
        labels.append((r, lab, is_label))
    res['ring labels'] = [r for r, lab, ok in labels if ok]
    sums = []                                         # which sums of ring parities are class labels
    for k in range(1, len(labels) + 1):
        for sub in itertools.combinations(range(len(labels)), k):
            lab = 0
            for r in sub: lab ^= labels[r][1]
            if all(bin(lab & m).count('1') % 2 == 0 for m in moves) and any(bin(lab & z).count('1') % 2 for z in Z):
                sums.append(list(sub))
    res['sums of ring parities that are labels'] = sums
    L = [lab for r, lab, ok in labels if ok]
    M = [sum(((bin(lab & z).count('1') % 2) << j) for j, z in enumerate(Z)) for lab in L]
    res['labels joint rank'] = classes.rank(M)
    if old is not None:                               # the old distinctions' allowed changes, before and after
        oidx = [idx[x] for x in old if x in idx]
        omask = sum(1 << i for i in oidx)
        proj = [z & omask for z in Z]
        res['old allowed changes kept'] = None
    return res, Z, idx


def projection_kept(start, stage):
    """whether the allowed changes of the start's distinctions are the same before and after"""
    def basis_on(supports, keep):
        names = sorted({x for r in supports for x in r}); idx = {x: i for i, x in enumerate(names)}
        rows = [sum(1 << idx[x] for x in r) for r in supports]
        Z = null(rows, len(names))
        ks = sorted(keep); out = []
        for z in Z:
            out.append(sum(((z >> idx[x]) & 1) << i for i, x in enumerate(ks)))
        return out
    old = {x for r in start for x in r}
    a = basis_on(start, old); b = basis_on(stage, old)
    ra, rb, rab = classes.rank(a), classes.rank(b), classes.rank(a + b)
    return {'start rank': ra, 'after rank': rb, 'same': ra == rb == rab}


STRUCTURES = [
    ('one ring of 5', [5], []),
    ('one ring of 7', [7], []),
    ('one ring of 4', [4], []),
    ('two rings of 5 sharing a knot', [5, 5], [('share', (0, 0), (1, 0))]),
    ('two rings of 5 touching', [5, 5], [('touch', (0, 0), (1, 0))]),
    ('two rings of 5 joined by a chain of 1', [5, 5], [('chain', (0, 0), (1, 0), 1)]),
    ('two rings of 5 joined by a chain of 2', [5, 5], [('chain', (0, 0), (1, 0), 2)]),
    ('three rings of 5 sharing a knot', [5, 5, 5], [('share', (0, 0), (1, 0)), ('share', (0, 0), (2, 0))]),
    ('three rings of 5 touching in a cycle', [5, 5, 5], [('touch', (0, 0), (1, 0)), ('touch', (1, 2), (2, 0)), ('touch', (2, 2), (0, 2))]),
    ('two rings of 4 touching', [4, 4], [('touch', (0, 0), (1, 0))]),
    ('three rings of 4 touching in a cycle', [4, 4, 4], [('touch', (0, 0), (1, 0)), ('touch', (1, 2), (2, 0)), ('touch', (2, 2), (0, 2))]),
]


def explore(out):
    with open(out, 'w') as f:
        for name, rings, joins in STRUCTURES:
            start, rd = build(rings, joins)
            rec = {'structure': name, 'knots': len(start), 'stages': {}}
            rec['stages']['start'] = analyse(start, rd)[0]
            for arm in ('ordinary', 'one_fewer', 'arity_floor'):
                st = start
                for t in (1, 2):
                    if arm != 'ordinary' and t > 1: break
                    nxt, status, births = forbid.grown(st, 'parity', arm)
                    if status != 'funded': rec['stages']['%s round %d' % (arm, t)] = status; break
                    a = analyse(nxt, rd)[0]
                    a['old allowed changes'] = projection_kept(start, nxt)
                    a['births with no fresh distinction'] = sum(1 for b in births if b['f'] == 0)
                    rec['stages']['%s round %d' % (arm, t)] = a; st = nxt
            f.write(json.dumps(rec) + '\n'); f.flush()
            print(name, json.dumps({k: (v if isinstance(v, str) else {kk: v[kk] for kk in ('classes', 'ring labels', 'sums of ring parities that are labels') if kk in v} | ({'kept': v['old allowed changes']['same'], 'no fresh': v['births with no fresh distinction']} if 'old allowed changes' in v else {})) for k, v in rec['stages'].items()}), flush=True)


if __name__ == '__main__':
    if sys.argv[1] == 'explore': explore(sys.argv[2])
