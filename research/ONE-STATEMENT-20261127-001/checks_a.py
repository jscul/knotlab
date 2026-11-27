"""checks_a.py OUT.json: part (a), the advisor's checkable claims (README.md, "Frozen").  ONE-STATEMENT-20261127-001.

a1  The nine facts of three rings of four (family facts p_i, q_i; ring facts R_i = p_i + q_i), as functions modulo the
    one relation (the sum of all six family facts is fixed): every basis of the space of relations among them (840),
    those in which every fact lies in at most two relations, those whose relations meet in a cycle (two relations meet
    when they share a fact), and those in which the six family facts each lie in exactly one relation.
a2  On the grown three-rings-of-four start at round 5 (the shared-fact witness, SELECTED-KNOTS-20261127-001/overlap.py),
    for each of the three four-place relations (p_i, q_i with the other two rings' facts): which single law removals
    free it (all 16 values).
a3  Rings of 10, 4 and 4 knots (split attachments, double links): for the big ring, the triple R_1 = p_1 + q_1 and the
    quadruple (p_1, q_1, R_2, R_3), each as the set of first-layer laws summing to it at round 2; their sizes in places
    and in distinctions (the union of the laws' distinctions).
a4  The advisor's three smallest pairs of presentations: same allowed states? same loose set? families of each."""
import sys, json, itertools, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
for d in ('BUILT-BINDING-20261126-001', 'THIRD-LAYER-20261126-001', 'SELECTED-KNOTS-20261127-001'): sys.path.insert(0, str(ROOT / 'research' / d))
import repro as RP, twokinds as TK
classes, forbid = RP.classes, RP.forbid
out = {}

# ---- a1
fam = [1 << i for i in range(6)]                                # p1 q1 p2 q2 p3 q3
places = fam + [fam[0] | fam[1], fam[2] | fam[3], fam[4] | fam[5]]
names = ['p1', 'q1', 'p2', 'q2', 'p3', 'q3', 'R1', 'R2', 'R3']
ALL = 0b111111
def is_rel(c): # c: subset of the nine places whose sum is 0 or the all-ones vector (fixed)
    v = 0
    for j in range(9):
        if (c >> j) & 1: v ^= places[j]
    return v in (0, ALL)
rels = [c for c in range(1, 1 << 9) if is_rel(c)]
def rank(vs):
    piv = {}
    for v in vs:
        for q in sorted(piv, reverse=True):
            if (v >> q) & 1: v ^= piv[q]
        if v: piv[v.bit_length() - 1] = v
    return len(piv)
dim = rank(rels)
bases = [B for B in itertools.combinations(rels, dim) if rank(list(B)) == dim]
def holders(B, j): return sum((c >> j) & 1 for c in B)
two = [B for B in bases if all(holders(B, j) <= 2 for j in range(9))]
def has_cycle(B):
    edges = [(a, b) for a, b in itertools.combinations(range(len(B)), 2) if B[a] & B[b]]
    parent = list(range(len(B)))
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for a, b in edges:
        if find(a) == find(b): return True
        parent[find(a)] = find(b)
    return False
def is_ring4(B):
    deg = [sum(1 for b in range(len(B)) if b != a and B[a] & B[b]) for a in range(len(B))]
    return len(B) == 4 and all(d == 2 for d in deg) and has_cycle(B)
fam_loose = [B for B in two if all(holders(B, j) == 1 for j in range(6))]
out['a1'] = {'relations': len(rels), 'dimension': dim, 'bases': len(bases), 'every fact in at most two relations': len(two),
             'of those, relations meeting in a cycle': sum(has_cycle(B) for B in two),
             'of those, four relations meeting in one ring': sum(is_ring4(B) for B in two),
             'of those, six family facts each in exactly one relation': len(fam_loose),
             'that basis': [[names[j] for j in range(9) if (c >> j) & 1] for c in (fam_loose[0] if fam_loose else [])]}

# ---- a2
S, rings, loose = RP.rings_start(R=3, n=4, attach='split', link='double')
fams, ls = TK.families(S)
st, status, births = forbid.grown(S, 'parity', 'ordinary')
famcar = []
for i in range(3):
    f1 = [f for f in fams if set(f) <= set(rings[i])]
    famcar.append([[x for b in births if set(b['parents']) <= set(f) for x in b['fresh']] for f in f1])
for t in range(2, 6): st, status, births = forbid.grown(st, 'parity', 'ordinary')
nm, idx, rows = RP.space(st)
quads = []
for i in range(3):
    others = [loose[j] for j in range(3) if j != i]
    quads.append([famcar[i][0], famcar[i][1]] + others)
res = []
for i, q in enumerate(quads):
    fs = [sum(1 << idx[x] for x in c) for c in q]
    base = len(RP.tuples(rows, len(nm), fs))
    frees = {'start': 0, 'born': 0}
    for j in range(len(rows)):
        if len(RP.tuples(rows[:j] + rows[j + 1:], len(nm), fs)) == 16: frees['start' if j < len(S) else 'born'] += 1
    res.append({'quadruple of ring %d' % (i + 1): base, 'single removals freeing it': frees})
out['a2'] = {'start laws': len(S), 'round': 5, 'quadruples': res}

# ---- a3
def rings_sizes(sizes):
    rows_ = []; nm_ = itertools.count()
    def knot(): rows_.append([]); return len(rows_) - 1
    def share(*ks):
        x = next(nm_)
        for k in ks: rows_[k].append(x)
        return x
    rg = [[knot() for _ in range(n)] for n in sizes]
    for ring in rg:
        for i in range(len(ring)): share(ring[i], ring[(i + 1) % len(ring)])
    lo = [[share(k) for k in ring for _ in range(2)] for ring in rg]
    port = collections.Counter()
    for r, s in itertools.combinations(range(len(sizes)), 2):
        L, Rk = knot(), knot()
        for i, side in ((r, L), (s, Rk)):
            p = port[i]; port[i] += 1; n = len(rg[i])
            share(rg[i][p % n], side); share(rg[i][(p + 2) % n], side)
        share(L, Rk); share(L, Rk)
    return tuple(tuple(x) for x in rows_), rg, lo
S, rg, lo = rings_sizes([10, 4, 4])
fams, ls = TK.families(S)
st, status, births = forbid.grown(S, 'parity', 'ordinary')
f1 = [f for f in fams if set(f) <= set(rg[0])]
pc = [[x for b in births if set(b['parents']) <= set(f) for x in b['fresh']] for f in f1]
st, status, births = forbid.grown(st, 'parity', 'ordinary')
nm, idx, rows = RP.space(st)
def law_set(cars):
    target = 0
    for c in cars:
        for x in c: target ^= 1 << idx[x]
    # solve sum of rows = target (rows independent while loose distinctions exist)
    piv = {}; tag = {}
    for k, r in enumerate(rows):
        v, tg = r, 1 << k
        for q in sorted(piv, reverse=True):
            if (v >> q) & 1: v ^= piv[q]; tg ^= tag[q]
        if v: piv[v.bit_length() - 1] = v; tag[v.bit_length() - 1] = tg
    v, tg = target, 0
    for q in sorted(piv, reverse=True):
        if (v >> q) & 1: v ^= piv[q]; tg ^= tag[q]
    assert v == 0, 'not a sum of laws'
    K = [k for k in range(len(rows)) if (tg >> k) & 1]
    return K, len({x for k in K for x in st[k]})
tri = law_set([lo[0], pc[0], pc[1]]); quad = law_set([pc[0], pc[1], lo[1], lo[2]])
out['a3'] = {'families of the big ring': len(f1), 'triple R1 = p1 + q1': {'places': 3, 'laws': len(tri[0]), 'distinctions': tri[1]},
             'quadruple p1 q1 R2 R3': {'places': 4, 'laws': len(quad[0]), 'distinctions': quad[1]}}

# ---- a4
def analyse_pair(P1, P2):
    def info(P):
        nm_, ix, rws = RP.space(P); h = forbid.holders(P)
        return {'states': 2 ** (len(nm_) - classes.rank(rws)), 'names': nm_, 'span': sorted(set(RP.tuples(rws, len(nm_), [1 << i for i in range(len(nm_))]))),
                'loose': sorted(x for x in nm_ if len(h[x]) == 1), 'families': TK.families(P)[1]}
    a, b = info(P1), info(P2)
    return {'same names': a['names'] == b['names'], 'same allowed states': a['span'] == b['span'], 'states': [a['states'], b['states']],
            'same loose set': a['loose'] == b['loose'], 'loose sets': [a['loose'], b['loose']],
            'families (as loose groups)': [a['families'], b['families']]}
x1, x2, y, z1, z2, w, v = 'x1 x2 y z1 z2 w v'.split()
pairs = {'i': ([(x1, x2, y), (y, z1, z2, w), (z1, z2, v)], [(x1, x2, v, w), (y, z1, z2, w), (z1, z2, v)])}
r12, r23, r34, r41, l1, l2, l3, l4 = 'r12 r23 r34 r41 l1 l2 l3 l4'.split()
ring = [(r41, r12, l1), (r12, r23, l2), (r23, r34, l3), (r34, r41, l4)]; K5 = (l1, l2, l3, l4)
pairs['ii'] = (ring, ring[1:] + [K5])
a1_, a2_, c, l, m, b_ = 'a1 a2 c l m b'.split()
pairs['iii'] = ([(a1_, a2_, c, l), (b_, c, m), (a1_, a2_, b_)], [(b_, c, l), (a1_, a2_, c, m), (a1_, a2_, b_)])
out['a4'] = {k: analyse_pair(*v) for k, v in pairs.items()}
json.dump(out, open(sys.argv[1], 'w'), indent=1, default=list); print(json.dumps(out, indent=1, default=list)[:4000])
