"""ringbond.py: bonds among readings on grown stages, their holders, their symmetry and the layer above.
RING-BOND-20261127-001; README.md.

A stage is a tuple of supports under one law ('nae' or 'parity').  Its allowed states are enumerated exactly with every
state that breaks one law only (enough to say which laws are essential).

A reading is a function of a carrier of two or three distinctions, unchanged when all its places flip, using every
place, and nonconstant on the allowed states.  Two classes (the reading class is a scaffold, A? in the register):
  agree   [the carrier's distinctions all equal]
  sym     every such function up to an output flip: on a pair the agreement; on a triple (x, y, z) the four readings
          [x+y = a and y+z = b], (a, b) in {00, 01, 10, 11} ((0, 0) is the agreement)
A reading is read at a knot when it is a function, on the allowed states, of that knot's values.
A bond is three readings on pairwise disjoint carriers, none read at any single knot, every two taking all four pairs
of values, the three together missing at least one of the eight triples.  Its essential laws are those whose removal
lets a missing triple occur; it is held by them when their laws alone already miss the same triples; it is new at a
round when a knot born in that round is essential."""
import sys, json, itertools, collections
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research' / 'BUILT-BINDING-20261126-001'))
import repro as RP
forbid = RP.forbid

POP = np.array([bin(i).count('1') for i in range(1 << 16)], dtype=np.int8)


def popcount(a):
    a = a.astype(np.uint32)
    return POP[a & 0xFFFF] + POP[a >> 16]


def stages(S, law, rounds):
    """[(supports, number of knots before this round)] for rounds 0..rounds, as far as growth is funded"""
    out = [(tuple(map(tuple, S)), 0)]; st = tuple(map(tuple, S))
    for _ in range(rounds):
        nxt, status, births = forbid.grown(st, law, 'ordinary')
        if status != 'funded': break
        out.append((nxt, len(st))); st = nxt
    return out


class Stage:
    def __init__(self, sup, law):
        self.sup, self.law = sup, law
        self.names = sorted({x for r in sup for x in r}); self.idx = {x: i for i, x in enumerate(self.names)}
        n = self.n = len(self.names); assert n <= 26
        masks = [sum(1 << self.idx[x] for x in r) for r in sup]
        nviol = np.zeros(1 << n, dtype=np.int8); last = np.full(1 << n, -1, dtype=np.int16)
        allst = np.arange(1 << n, dtype=np.uint32)
        for k, m in enumerate(masks):
            c = popcount(allst & np.uint32(m)); a = bin(m).count('1')
            bad = (c % 2 == 1) if law == 'parity' else ((c == 0) | (c == a))
            nviol += bad; last[bad] = k
        keep = nviol <= 1
        self.states = allst[keep]; self.broken = np.where(nviol[keep] == 0, -1, last[keep])
        self.allowed = self.broken == -1
        del allst, nviol, last
        self.A = self.states[self.allowed]

    def bits(self, x, states=None):
        s = self.states if states is None else states
        return ((s >> np.uint32(self.idx[x])) & 1).astype(bool)

    def readings(self, cls, sizes=(2, 3)):
        """[(carrier, label, values over self.states)], nonconstant on the allowed states"""
        out = []
        for k in sizes:
            for C in itertools.combinations(self.names, k):
                b = [self.bits(x) for x in C]
                if k == 2:
                    forms = [('=', b[0] == b[1])]
                else:
                    u, v = b[0] ^ b[1], b[1] ^ b[2]
                    forms = [('=', ~u & ~v)] if cls == 'agree' else [('%d%d' % (p, q), (u == bool(p)) & (v == bool(q))) for p in (0, 1) for q in (0, 1)]
                for lab, val in forms:
                    va = val[self.allowed]
                    if va.any() and not va.all(): out.append((C, lab, val))
        return out

    def read_at(self, val):
        """the knots at which this reading is read (a function of that knot's values on the allowed states)"""
        va = val[self.allowed].astype(np.int64); out = []
        for k, r in enumerate(self.sup):
            key = np.zeros(len(self.A), dtype=np.int64)
            for j, x in enumerate(r): key |= ((self.A >> np.uint32(self.idx[x])) & 1).astype(np.int64) << j
            if len(np.unique(key)) == len(np.unique(key * 2 + va)): out.append(k)
        return out


class RelStage(Stage):
    """the layer above: variables are readings, and each law is a bond's relation (its missing words forbidden);
    laws: [(variables, set of forbidden words as integers, first variable the highest bit)]"""
    def __init__(self, laws):
        self.sup = tuple(tuple(v) for v, f in laws); self.law = 'relations'
        self.names = sorted({x for v, f in laws for x in v}); self.idx = {x: i for i, x in enumerate(self.names)}
        n = self.n = len(self.names); assert n <= 26
        allst = np.arange(1 << n, dtype=np.uint32)
        nviol = np.zeros(1 << n, dtype=np.int8); last = np.full(1 << n, -1, dtype=np.int16)
        for k, (v, forb) in enumerate(laws):
            code = np.zeros(1 << n, dtype=np.int64)
            for x in v: code = code * 2 + ((allst >> np.uint32(self.idx[x])) & 1)
            bad = np.isin(code, list(forb))
            nviol += bad; last[bad] = k
        keep = nviol <= 1
        self.states = allst[keep]; self.broken = np.where(nviol[keep] == 0, -1, last[keep])
        self.allowed = self.broken == -1; self.A = self.states[self.allowed]


def to_int(boolarr):
    """a bool array as a Python int bitset (bit i = entry i)"""
    if len(boolarr) == 0: return 0
    return int.from_bytes(np.packbits(boolarr.astype(np.uint8), bitorder='little').tobytes(), 'little')


def words(vals, mask):
    """the set of triples (or tuples) of values taken on the states selected by mask"""
    code = np.zeros(int(mask.sum()), dtype=np.int64)
    for v in vals: code = code * 2 + v[mask]
    return set(np.unique(code).tolist())


def bonds(stage, cls='agree', sizes=(2, 3), born=0):
    """every bond on the stage.  born: knots with index >= born were born in the stage's last round"""
    R = stage.readings(cls, sizes)
    unread = [i for i, (C, lab, v) in enumerate(R) if not stage.read_at(v)]
    U = [R[i] for i in unread]; N = len(U)
    nA = len(stage.A)
    va = [v[stage.allowed] for C, lab, v in U]
    found = []
    if N >= 3:
        V = np.array(va, dtype=np.float32)                     # readings x allowed states
        def counts(T, K):
            g11 = T @ T.T; t = T.sum(1)
            return g11, t[:, None] - g11, t[None, :] - g11, K - t[:, None] - t[None, :] + g11
        g = counts(V, nA)
        free = (g[0] > 0) & (g[1] > 0) & (g[2] > 0) & (g[3] > 0)   # every pair of values occurs
        names = sorted({x for C, lab, v in U for x in C}); col = {x: p for p, x in enumerate(names)}
        inc = np.zeros((N, len(names)), dtype=np.float32)
        for t, (C, lab, v) in enumerate(U):
            for x in C: inc[t, col[x]] = 1
        ok = free & ((inc @ inc.T) == 0)                       # free and on disjoint carriers
        rng = np.random.default_rng(0); KS = 256
        cand = set()
        for i in range(N):
            js = np.flatnonzero(ok[i]); js = js[js > i]
            if len(js) < 2: continue
            sub = V[js]; okj = np.triu(ok[np.ix_(js, js)], 1)
            for a in (0, 1):
                Sa = np.flatnonzero(V[i] == a)
                samp = Sa if len(Sa) <= KS else rng.choice(Sa, KS, replace=False)
                h = counts(sub[:, samp], len(samp))
                Z = okj & ((h[0] == 0) | (h[1] == 0) | (h[2] == 0) | (h[3] == 0))
                for p, q in np.argwhere(Z): cand.add((i, int(js[p]), int(js[q])))
        Vi = V.astype(np.int8)
        for i, j, k in sorted(cand):                           # exact: a triple is missing on every allowed state
            code = 4 * Vi[i].astype(np.int16) + 2 * Vi[j] + Vi[k]
            if len(np.unique(code)) < 8: found.append((i, j, k))
    # bitsets over every kept state (allowed, or breaking one law)
    ALL = (1 << len(stage.states)) - 1
    yes = {}
    def yes_all(t):
        if t not in yes: yes[t] = to_int(U[t][2])
        return yes[t]
    allowed_all = to_int(stage.allowed)
    broken = [to_int(stage.broken == q) for q in range(len(stage.sup))]
    out = []
    for i, j, k in found:
        ys = [yes_all(t) for t in (i, j, k)]
        missing, essential = [], set()
        for w in range(8):
            cell = ALL
            for p, y in enumerate(ys): cell &= y if (w >> (2 - p)) & 1 else ALL ^ y
            if cell & allowed_all: continue
            missing.append(w)
            for q in range(len(stage.sup)):
                if cell & broken[q]: essential.add(q)
        essential = sorted(essential)
        out.append({'readings': [[list(U[t][0]), U[t][1]] for t in (i, j, k)],
                    'missing': ['{:03b}'.format(m) for m in missing], 'essential': essential,
                    'new': any(q >= born for q in essential) if born else None})
    return {'distinctions': stage.n, 'allowed': nA, 'readings': len(R), 'unread readings': N, 'bonds': out}


def clusters(sup, m):
    """connected sets of at most m knots (two knots meet when they share a distinction), as sorted tuples"""
    h = forbid.holders(sup); nb = collections.defaultdict(set)
    for x, ks in h.items():
        for a in ks:
            for b in ks:
                if a != b: nb[a].add(b)
    out = set(); frontier = {(k,) for k in range(len(sup))}; out |= frontier
    for _ in range(m - 1):
        nxt = set()
        for c in frontier:
            for k in set().union(*(nb[q] for q in c)) - set(c):
                nxt.add(tuple(sorted(c + (k,))))
        nxt -= out; out |= nxt; frontier = nxt
    return sorted(out, key=lambda c: (len(c), c))


def reading_clauses(C, lab, var):
    """CNF defining a fresh variable r <-> reading(C) (agreement only), var: distinction -> solver variable"""
    assert lab == '='
    xs = [var[x] for x in C]; return xs


def local_bonds(sup, law, m, cls='agree', check=True):
    """bonds held by a connected set H of at most m knots: found on H's own laws (every law of H essential there, no
    reading read at a knot of H), then checked on the whole stage: the same missing triples, every other triple
    present, and no reading read at any knot of the stage (by a solver)."""
    from pysat.solvers import Minisat22
    found = {}
    for H in clusters(sup, m):
        sub = tuple(sup[q] for q in H)
        st = Stage(sub, law)
        res = bonds(st, cls, born=0)
        for b in res['bonds']:
            if len(b['essential']) != len(H): continue
            key = bond_key(b)
            if key in found and len(found[key]['holders']) <= len(H): continue
            found[key] = {'readings': b['readings'], 'missing': b['missing'], 'holders': list(H)}
    if not check: return list(found.values())
    names = sorted({x for r in sup for x in r}); var = {x: i + 1 for i, x in enumerate(names)}; top = [len(names)]
    def fresh():
        top[0] += 1; return top[0]
    base = []
    for r in sup:
        v = [var[x] for x in r]
        if law == 'nae': base += [v, [-u for u in v]]
        else:
            for bits in itertools.product((0, 1), repeat=len(v)):
                if sum(bits) % 2 == 1: base.append([-u if b else u for u, b in zip(v, bits)])
    def define(C, vmap, cl):
        """a variable equal to [C all equal] under the variable map vmap; clauses appended to cl"""
        r = fresh(); xs = [vmap[x] for x in C]
        # r -> all equal: r -> (x_i <-> x_0)
        for x in xs[1:]: cl += [[-r, -xs[0], x], [-r, xs[0], -x]]
        # all equal -> r
        cl += [[r] + [-x for x in xs], [r] + list(xs)]
        return r
    out = []
    for b in found.values():
        cl = list(base); rs = [define(C, var, cl) for C, lab in b['readings']]
        s = Minisat22(bootstrap_with=cl); present = []
        for w in range(8):
            ok = s.solve(assumptions=[r if (w >> (2 - p)) & 1 else -r for p, r in enumerate(rs)]); present.append(ok)
        s.delete()
        missing = ['{:03b}'.format(w) for w in range(8) if not present[w]]
        # read at a knot of the stage: two allowed states equal on the knot's values with different reading values
        read = False
        if missing == b['missing']:
            var2 = {x: fresh() for x in names}
            cl2 = list(base)
            for r in sup:
                v = [var2[x] for x in r]
                if law == 'nae': cl2 += [v, [-u for u in v]]
                else:
                    for bits in itertools.product((0, 1), repeat=len(v)):
                        if sum(bits) % 2 == 1: cl2.append([-u if bb else u for u, bb in zip(v, bits)])
            r1 = [define(C, var, cl2) for C, lab in b['readings']]; r2 = [define(C, var2, cl2) for C, lab in b['readings']]
            s = Minisat22(bootstrap_with=cl2)
            for k, r in enumerate(sup):
                same = []
                for x in r:
                    e = fresh(); same.append(e)
                    s.add_clause([-e, -var[x], var2[x]]); s.add_clause([-e, var[x], -var2[x]])
                for a, c in zip(r1, r2):           # read at this knot: no two such states differ in the reading
                    if not s.solve(assumptions=same + [a, -c]): read = True; break
                if read: break
            s.delete()
        out.append(dict(b, **{'stage missing': missing, 'same relation on the stage': missing == b['missing'],
                              'read at a knot of the stage': read}))
    return out


def held_by(sup, law, bond, essential):
    """do the essential laws alone miss the same triples? (enumerates the distinctions of those knots and the carriers)"""
    sub = [sup[q] for q in essential]
    names = sorted({x for r in sub for x in r} | {x for C, lab in bond['readings'] for x in C})
    idx = {x: i for i, x in enumerate(names)}; n = len(names)
    allst = np.arange(1 << n, dtype=np.uint32); ok = np.ones(1 << n, dtype=bool)
    for r in sub:
        m = sum(1 << idx[x] for x in r); c = popcount(allst & np.uint32(m))
        ok &= (c % 2 == 0) if law == 'parity' else ((c > 0) & (c < len(r)))
    A = allst[ok]; code = np.zeros(len(A), dtype=np.int64)
    for C, lab in bond['readings']:
        b = [((A >> np.uint32(idx[x])) & 1).astype(bool) for x in C]
        if len(C) == 2: v = b[0] == b[1]
        else:
            u, w = b[0] ^ b[1], b[1] ^ b[2]
            p, q = (0, 0) if lab == '=' else (int(lab[0]), int(lab[1]))
            v = (u == bool(p)) & (w == bool(q))
        code = code * 2 + v.astype(np.int64)
    missing = sorted(set(range(8)) - set(np.unique(code).tolist()))
    return ['{:03b}'.format(m) for m in missing] == bond['missing']


def automorphisms_fix(sup, perm):
    """does the permutation of distinctions (dict, identity elsewhere) map the supports onto themselves?"""
    img = sorted(tuple(sorted(perm.get(x, x) for x in r)) for r in sup)
    return img == sorted(tuple(sorted(r)) for r in sup)


def bond_key(b):
    return tuple(sorted((tuple(sorted(C)), lab) for C, lab in b['readings']))


def bond_image(b, perm):
    """the bond's readings under a permutation of distinctions (a 'sym' label changes with the order of its carrier;
    only agreement readings are mapped here)"""
    assert all(lab == '=' for C, lab in b['readings'])
    return tuple(sorted((tuple(sorted(perm.get(x, x) for x in C)), lab) for C, lab in b['readings']))
