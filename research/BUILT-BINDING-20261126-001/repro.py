"""repro.py: the binding referee's constructions rebuilt with the thread's own code, and the origin test.
BUILT-BINDING-20261126-001; README.md.

Starts are built here from their description (rings of n knots, each ring knot holding two loose distinctions; for every
pair of rings two connecting knots holding none, one attached to each ring); growth is the canonical engine
(forbid.grown); every reading below is linear algebra over two values on the stage's own laws, checked against a solver
where stated.  For a family of carriers (sets of distinctions, each read as the parity of its values):

    tuples        the joint values the carriers take on the allowed states (laws read as even), and whether every
                  proper sub-family is free (one parity rule binding them)
    facts         under each reading of a small change (SHORT, UPTO5): each carrier a class label, and read by no
                  single knot
    deletion      for each knot law in turn, removed: whether the carriers then take every tuple
    origin        whether each carrier is, as a function of the allowed states, a function of the start's
                  distinctions alone (its parity plus a sum of the stage's laws is supported on start distinctions);
                  if every one is, the start's representatives, their joint values on the start's allowed states (the
                  relation is then the start's, by the projection lemma), and whether they were facts at the start
The rings' new carriers at round t (t >= 1) are the fresh distinctions of the round-t births whose parents all lie in
one ring's lineage, ring by ring."""
import sys, json, itertools, collections, functools, operator
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import built as BU
classes, forbid, MC, T2 = BU.classes, BU.forbid, BU.MC, BU.T2


def rings_start(R=3, n=5, attach='split', link='detour', detour=3, connector_loose=0, link_connectors=False,
                link_middles=False, one_connector_loose=False, middle_loose=False):
    """R rings of n knots, two loose each; for each pair of rings a connecting knot on each side.  attach: 'split' (the
    connecting knot shares one distinction with ring knots p and p + 2) or 'paired' (two with ring knot 2p).  link:
    'double' (the two connecting knots share two distinctions) or 'detour' (one, plus a chain of `detour` knots each
    meeting the next twice).  connector_loose: loose distinctions at each connecting knot.  link_connectors: the first
    connecting knots of the pairs share one distinction pairwise (the referee's modification for the cuts)."""
    rows = []; name = itertools.count()
    def knot(): rows.append([]); return len(rows) - 1
    def share(*ks):
        x = next(name)
        for k in ks: rows[k].append(x)
        return x
    rings = [[knot() for _ in range(n)] for _ in range(R)]
    for ring in rings:
        for i in range(n): share(ring[i], ring[(i + 1) % n])
    loose = [[] for _ in range(R)]
    for r, ring in enumerate(rings):
        for k in ring:
            for _ in range(2): loose[r].append(share(k))
    port = collections.Counter(); firsts = []; connectors = []; middles = []
    for r, s in itertools.combinations(range(R), 2):
        L, Rk = knot(), knot(); connectors += [L, Rk]; firsts.append(L)
        for i, side in ((r, L), (s, Rk)):
            p = port[i]; port[i] += 1
            if attach == 'paired':
                share(rings[i][(2 * p) % n], side); share(rings[i][(2 * p) % n], side)
            else:
                share(rings[i][p % n], side); share(rings[i][(p + 2) % n], side)
        if link == 'apart':                    # the control: no link; each connecting knot keeps its places as loose
            for side in (L, Rk):
                for _ in range(2): share(side)
            continue
        share(L, Rk)
        if link == 'detour':
            prev = L
            for h in range(detour):
                k = knot(); connectors.append(k); share(prev, k); share(prev, k); prev = k
                if h == detour // 2: middles.append(k)
            share(prev, Rk); share(prev, Rk)
        else:
            share(L, Rk)
    if link_connectors:
        for a, b in itertools.combinations(firsts, 2): share(a, b)
    if link_middles:                       # the referee's modification for the cuts: middles joined, one loose each
        for a, b in itertools.combinations(middles, 2): share(a, b)
        for k in middles: share(k)
    for k in connectors:
        for _ in range(connector_loose): share(k)
    if one_connector_loose: share(connectors[0])
    if middle_loose: share(middles[0])          # one loose distinction at the middle knot of the first detour
    return tuple(tuple(r) for r in rows), rings, loose


# ------------------------------------------------------------------ linear algebra on named distinctions

def space(st):
    names = sorted({x for r in st for x in r}); idx = {x: i for i, x in enumerate(names)}
    rows = [sum(1 << idx[x] for x in r) for r in st]
    return names, idx, rows


def vec(xs, idx): return sum(1 << idx[x] for x in xs)


def tuples(rows, n, fs):
    Z = classes.nullspace(rows, n)
    gens = [tuple(bin(f & z).count('1') % 2 for f in fs) for z in Z]
    occ = {tuple(0 for _ in fs)}
    for g in gens: occ |= {tuple((a + b) % 2 for a, b in zip(o, g)) for o in occ}
    return occ


def one_rule(occ, k):
    """every proper sub-family free and the whole bound by one parity rule"""
    if len(occ) != 2 ** (k - 1): return False
    for drop in range(k):
        if len({tuple(o[j] for j in range(k) if j != drop) for o in occ}) != 2 ** (k - 1): return False
    return True


def facts(st, fs, moves, idx):
    names, _, rows = space(st); Z = classes.nullspace(rows, len(names))
    local = []
    for r in st:
        ks = [idx[x] for x in r]
        mrows = [sum(((m >> i) & 1) << j for j, i in enumerate(ks)) for m in moves]
        local.append([sum(((v >> j) & 1) << i for j, i in enumerate(ks)) for v in classes.nullspace(mrows, len(ks))])
    out = []
    for f in fs:
        label = all(bin(f & m).count('1') % 2 == 0 for m in moves) and any(bin(f & z).count('1') % 2 for z in Z)
        unread = not any(classes.rank(rows + loc + [f]) == classes.rank(rows + loc) for loc in local)
        out.append([label, unread])
    return out


def old_representative(f, rows, oldmask):
    """g supported on oldmask with f + g in span(rows), or None (f then depends on new values)"""
    piv = {}
    for r in rows:
        v, t = r & ~oldmask, r
        for p in sorted(piv, reverse=True):
            if (v >> p) & 1: v ^= piv[p][0]; t ^= piv[p][1]
        if v: piv[v.bit_length() - 1] = (v, t)
    v, t = f & ~oldmask, f
    for p in sorted(piv, reverse=True):
        if (v >> p) & 1: v ^= piv[p][0]; t ^= piv[p][1]
    return None if v else t


def analyse(S, st, carriers, rounds_of_knot=None):
    """carriers: lists of distinction names on stage st; S the start"""
    names, idx, rows = space(st); n = len(names)
    fs = [vec(c, idx) for c in carriers]; k = len(fs)
    occ = tuples(rows, n, fs)
    sol = {tuple(v) for v in BU.tuples_solver(st, carriers)}
    assert occ == sol, 'linear and solver disagree'
    rec = {'carriers': [len(c) for c in carriers], 'tuples': len(occ), 'of': 2 ** k, 'one rule': one_rule(occ, k)}
    _, i1, short = MC.moves_of(st); _, i2, up = T2.moves_upto(st, 5)
    assert i1 == idx == i2
    rec['SHORT'] = facts(st, fs, short, idx); rec['UPTO5'] = facts(st, fs, up, idx)
    if rec['one rule']:
        frees = []
        for j in range(len(rows)):
            if len(tuples(rows[:j] + rows[j + 1:], n, fs)) == 2 ** k: frees.append(j)
        rec['laws whose removal frees every tuple'] = {'start knots': sum(1 for j in frees if j < len(S)),
                                                       'born knots': sum(1 for j in frees if j >= len(S)),
                                                       'of start / born': [len(S), len(st) - len(S)]}
    old = {x for r in S for x in r}; oldmask = sum(1 << idx[x] for x in old if x in idx)
    reps = [old_representative(f, rows, oldmask) for f in fs]
    rec['origin'] = {'each carrier a function of the start values': [g is not None for g in reps]}
    if all(g is not None for g in reps):
        n0, i0, r0 = space(S)
        g0 = [sum(1 << i0[names[i]] for i in range(n) if (g >> i) & 1) for g in reps]
        occ0 = tuples(r0, len(n0), g0)
        rec['origin']['the same joint values at the start'] = occ0 == occ
        rec['origin']['tuples at the start'] = len(occ0)
        _, j1, s0 = MC.moves_of(S); _, j2, u0 = T2.moves_upto(S, 5)
        rec['origin'].update({'start representatives (sizes)': [bin(g).count('1') for g in g0],
                              'relation on the start\'s allowed states': one_rule(occ0, k),
                              'facts at the start, SHORT': facts(S, g0, s0, i0), 'facts at the start, UPTO5': facts(S, g0, u0, i0),
                              'sum of the representatives a sum of start laws': classes.rank(r0 + [functools.reduce(operator.xor, g0)]) == classes.rank(r0)})
    return rec


def ring_carriers(st_before, births, lineage):
    """the fresh distinctions of the births whose parents all lie in one lineage, per lineage; and the new lineages"""
    car = collections.defaultdict(list); new = {}
    for b in births:
        ls = {lineage.get(p) for p in b['parents']}
        if len(ls) == 1 and None not in ls:
            l = ls.pop(); car[l] += list(b['fresh']); new[b['knot']] = l
    return car, new


def run_rings(label, S, rings, rounds=3, law='parity', arm='ordinary', cap=500):
    lineage = {k: r for r, ring in enumerate(rings) for k in ring}
    rec = {'family': label, 'knots': len(S), 'distinctions': len({x for r in S for x in r}), 'law': law, 'arm': arm, 'rounds': []}
    st = S; carriers = None
    for t in range(1, rounds + 1):
        nxt, status, births = forbid.grown(st, law, arm)
        if status != 'funded': rec['rounds'].append({'round': t, 'end': status}); break
        car, new = ring_carriers(st, births, lineage); lineage.update(new); st = nxt
        nd = len({x for r in st for x in r})
        row = {'round': t, 'distinctions': nd}
        if carriers is not None and len(carriers) == len(rings) and nd <= cap and law == 'parity':
            row['carriers born in round %d' % (t - 1)] = analyse(S, st, [carriers[r] for r in range(len(rings))])
        elif carriers is not None and law == 'nae':
            row['carriers born in round %d' % (t - 1)] = nae_tuples(st, [carriers[r] for r in range(len(rings))])
        carriers = car if len(car) == len(rings) else None
        rec['rounds'].append(row)
        if nd > cap: break
    return rec


def nae_tuples(st, carriers):
    from pysat.solvers import Minisat22
    names = sorted({x for r in st for x in r}); idx = {x: i + 1 for i, x in enumerate(names)}
    occ = []
    for vals in itertools.product((0, 1), repeat=len(carriers)):
        s = Minisat22(); top = [len(names)]
        for r in st:
            v = [idx[x] for x in r]; s.add_clause(v); s.add_clause([-u for u in v])
        for c, val in zip(carriers, vals):
            acc = idx[c[0]]
            for x in c[1:]:
                y = idx[x]; top[0] += 1; z = top[0]
                s.add_clause([-z, acc, y]); s.add_clause([-z, -acc, -y]); s.add_clause([z, -acc, y]); s.add_clause([z, acc, -y]); acc = z
            s.add_clause([acc] if val else [-acc])
        if s.solve(): occ.append(vals)
        s.delete()
    return {'tuples': len(occ), 'of': 2 ** len(carriers)}


if __name__ == '__main__':
    out = sys.argv[1]
    with open(out, 'w') as f:
        for label, kw in [('three rings of five, detour (the referee\'s 30 knots)', dict()),
                          ('three rings of five, two direct links', dict(link='double')),
                          ('three rings of five, paired attachments', dict(attach='paired', link='double'))]:
            S, rings, loose = rings_start(**kw)
            r = run_rings(label, S, rings); f.write(json.dumps(r) + '\n'); f.flush(); print(json.dumps(r)[:1500], flush=True)
