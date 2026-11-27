"""tree.py SET OUT.jsonl [LIMIT]: the frozen test of SELECTED-KNOTS-20261127-001 (README.md, "Frozen").

For each start: its families (THIRD-LAYER's twokinds.families) and, for each pair of families A, B, the distance d(A, B):
the least number of shared distinctions on a route of knots from a live knot of A to a live knot of B in the start
(each step between two knots that share a distinction).  At rounds 0 to 4 of ordinary parity growth (until a round
stalls, closes or passes 300 distinctions):
  SK1  for every pair, the least change flipping l_A and l_B and no other family's fact equals d(A, B) + 2 + 2t;
  SK2  for every nonempty proper set T of families, the least change flipping the sum of T's facts equals the least
       pair cost from a family in T to one outside it;
  SK3  at the scales k = 8 and k = 12, the sums of family facts that no change of at most k flips form a space whose
       dimension is the number of clusters of families, two joined when d + 2 + 2t <= k, less one;
  SK4  with the nodes of the families' tree (single linkage by d) as places and a second-layer knot at each node with
       two or more children, every layer-three class fact (a parity on the layer-two values that their own least
       changes keep) is read by a single second-layer knot: no third-layer fact held by no part;
  read under the shortest changes (MC.moves_of): the number of family sums that are class facts."""
import sys, json, itertools, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
for d in ('BUILT-BINDING-20261126-001', 'THIRD-LAYER-20261126-001'): sys.path.insert(0, str(ROOT / 'research' / d))
import repro as RP, minflip as MF, twokinds as TK
forbid, classes = RP.forbid, RP.classes
CAP, SUMS_MAX = 300, 6


def least_exact(st, parities, kmax=60):
    """the least allowed change meeting each support in `parities` with the given parity (minflip's method)"""
    from pysat.solvers import Minisat22
    from pysat.card import CardEnc, EncType
    names = sorted({x for r in st for x in r}); idx = {x: i + 1 for i, x in enumerate(names)}
    top = [len(names)]; base = []
    def new(): top[0] += 1; return top[0]
    def xor(vs, val):
        if not vs:
            if val: base.append([])
            return
        acc = vs[0]
        for y in vs[1:]:
            z = new(); base.extend([[-z, acc, y], [-z, -acc, -y], [z, -acc, y], [z, acc, -y]]); acc = z
        base.append([acc] if val else [-acc])
    for r in st: xor([idx[x] for x in r], 0)
    for sup, val in parities: xor([idx[x] for x in sup], val)
    lits = [idx[x] for x in names]
    def sat(k):
        card = CardEnc.atmost(lits=lits, bound=k, top_id=top[0], encoding=EncType.seqcounter)
        s2 = Minisat22(bootstrap_with=base + card.clauses); ok = s2.solve()
        w = sum(1 for l in lits if s2.get_model()[l - 1] > 0) if ok else None
        s2.delete(); return w
    w = sat(kmax)
    if w is None: return 'more than %d' % kmax
    lo, hi = 0, w
    while hi - lo > 1:
        mid = (lo + hi) // 2; w2 = sat(mid)
        if w2 is None: lo = mid
        else: hi = w2
    return hi


def distances(S, fams):
    h = forbid.holders(S); nbr = collections.defaultdict(set)
    for x, hs in h.items():
        if len(hs) == 2 and hs[0] != hs[1]: nbr[hs[0]].add(hs[1]); nbr[hs[1]].add(hs[0])
    D = {}
    for i, A in enumerate(fams):
        dist = {k: 0 for k in A}; frontier = list(A)
        while frontier:
            nxt = []
            for u in frontier:
                for v in nbr[u]:
                    if v not in dist: dist[v] = dist[u] + 1; nxt.append(v)
            frontier = nxt
        for j, B in enumerate(fams):
            if j > i: D[(i, j)] = min(dist.get(k, 10 ** 9) for k in B)
    return D


def clusters(m, D, t, k):
    parent = list(range(m))
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for (i, j), d in D.items():
        if d + 2 + 2 * t <= k: parent[find(i)] = find(j)
    return len({find(i) for i in range(m)})


def dendrogram_layer3(m, D):
    """SK4: the nodes of the families' tree (clusters at every threshold of d, single linkage) as places, each node's
    fact the sum of its families' facts; a second-layer knot for every node with two or more children (the node and its
    children); the layer-two values C2 over the places (family values of even weight); the dimension of the layer-three
    class facts: parities on C2 even on C2's own least nonzero words, not fixed on C2"""
    levels = sorted(set(D.values()))
    nodes = {frozenset([i]) for i in range(m)}; children = {}
    parent = list(range(m))
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for thr in levels:
        before = {find(i) for i in range(m)}
        groups_before = collections.defaultdict(set)
        for i in range(m): groups_before[find(i)].add(i)
        for (i, j), d in D.items():
            if d <= thr: parent[find(i)] = find(j)
        groups = collections.defaultdict(set)
        for i in range(m): groups[find(i)].add(i)
        for g in groups.values():
            g = frozenset(g)
            if g in nodes: continue
            kids = [frozenset(h) for h in groups_before.values() if h <= g]
            nodes.add(g); children[g] = kids
    root = frozenset(range(m)); nodes.discard(root)                # the root's fact is fixed (the one relation)
    places = sorted(nodes, key=lambda g: (len(g), sorted(g)))
    pos = {g: i for i, g in enumerate(places)}
    knots = []
    for g, kids in children.items():
        if len(kids) >= 2: knots.append(sorted([pos[g]] if g in pos else []) + sorted(pos[h] for h in kids))
    words = set()
    for F in range(1 << m):
        if bin(F).count('1') % 2: continue
        words.add(sum((bin(sum(1 << i for i in g) & F).count('1') % 2) << j for j, g in enumerate(places)))
    nz = [w for w in words if w]
    if not nz: return {'places': len(places), 'knots': knots, 'layer-three dimension': 0}
    wmin = min(bin(w).count('1') for w in nz); least = [w for w in nz if bin(w).count('1') == wmin]
    def rank(vs):
        piv = {}
        for v in vs:
            for q in sorted(piv, reverse=True):
                if (v >> q) & 1: v ^= piv[q]
            if v: piv[v.bit_length() - 1] = v
        return len(piv)
    n = len(places)
    def nullspace(vs):                                    # all subsets T (as ints) even on every v in vs
        return [T for T in range(1 << n) if all(bin(T & v).count('1') % 2 == 0 for v in vs)] if n <= 16 else None
    even_least = nullspace(least); fixed = nullspace(list(words))
    if even_least is None: return {'places': n, 'second-layer knots': knots, 'note': 'too many places'}
    facts = [T for T in even_least if T not in set(fixed)]
    local = []
    for kn in knots:
        km = sum(1 << q for q in kn)
        local += [T for T in even_least if T & ~km == 0]
    span_local = rank(local + fixed)
    unread = [T for T in facts if rank(local + fixed + [T]) > span_local]
    return {'places': n, 'second-layer knots': knots, 'least layer-two change': wmin,
            'layer-three dimension': (n - rank(least)) - (n - rank(list(words))),
            'layer-three facts read by no single second-layer knot (dimension)': rank(local + fixed + unread) - span_local}


def run(name, S, rounds=4):
    fams, ls = TK.families(S); m = len(fams)
    rec = {'start': name, 'families': m, 'rounds': []}
    if m < 2: rec['note'] = 'fewer than two families'; return rec
    D = distances(S, fams); rec['distances'] = {'%d-%d' % k: v for k, v in D.items()}
    if m <= 10: rec['SK4'] = dendrogram_layer3(m, D)
    st = S
    for t in range(0, rounds + 1):
        if t:
            nxt, status, births = forbid.grown(st, 'parity', 'ordinary')
            if status != 'funded': rec['rounds'].append({'round': t, 'end': status}); break
            st = nxt
        if len({x for r in st for x in r}) > CAP: rec['rounds'].append({'round': t, 'end': 'not read'}); break
        row = {'round': t, 'SK1 failures': [], 'SK2 failures': []}
        pair = {}
        for (i, j), d in D.items():
            w = least_exact(st, [(ls[c], 1 if c in (i, j) else 0) for c in range(m)]); pair[(i, j)] = w
            if w != d + 2 + 2 * t: row['SK1 failures'].append([i, j, d, w])
        sums = {}
        if m <= SUMS_MAX:
            for r in range(1, m):
                for T in itertools.combinations(range(m), r):
                    if 0 not in T: continue                   # T and its complement give the same fact
                    w = MF.least(st, [x for a in T for x in ls[a]], kmax=60); sums[T] = w
                    pred = min(D[(min(a, b), max(a, b))] + 2 + 2 * t for a in T for b in range(m) if b not in T)
                    if w != pred: row['SK2 failures'].append([list(T), pred, w])
            for k in (8, 12):
                kept = sum(1 for T, w in sums.items() if isinstance(w, str) or (isinstance(w, int) and w > k))
                dim = (kept + 1).bit_length() - 1 if kept + 1 == 1 << ((kept + 1).bit_length() - 1) else None
                row['SK3 k=%d' % k] = {'kept sums': kept, 'dimension': dim, 'predicted': clusters(m, D, t, k) - 1}
            names, idx, rows = RP.space(st); _, ix, short = RP.MC.moves_of(st)
            Hp = classes.nullspace(short, len(names)); base = classes.rank(rows + Hp)
            row['shortest reading: kept sums'] = sum(1 for T in sums if classes.rank(rows + Hp + [sum(1 << idx[x] for a in T for x in ls[a])]) == base)
        rec['rounds'].append(row)
    return rec


if __name__ == '__main__':
    which, out = sys.argv[1], sys.argv[2]; limit = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    with open(out, 'w') as f:
        for name, S in TK.items(which, limit):
            f.write(json.dumps(run(name, S)) + '\n'); f.flush()
