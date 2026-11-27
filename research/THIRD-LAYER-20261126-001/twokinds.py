"""twokinds.py SET OUT.jsonl [LIMIT]: the advisor's claim T (THIRD-LAYER-20261126-001, README.md "Frozen").

Families: the live knots of the start (those holding a loose distinction), two of them joined when some knot shares a
distinction with each (the engine's candidate rule, fastlib.candidates), taken in connected classes. A family's fact
l_A is the parity of its knots' loose distinctions.  On each start, rounds 0 to 4 of ordinary parity growth (until it
stalls, closes or passes 300 distinctions):
  T1  no birth has parents descended from two families (lineage through parents)
  T2  at round 0 the facts l_A take the joint values of one parity rule with every proper subfamily free (m >= 3),
      or are tied (m = 2), or fixed (m = 1), m the number of families, for a connected start
  T3  the least change flipping each l_A (minflip.least) is at least its round-0 value plus 2t at round t
  T4  under changes of at most five distinctions (UPTO5) the class facts' dimension is the same at rounds 3 and 4, and
      from round 3 every l_A is a class fact"""
import sys, json, itertools, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research' / 'BUILT-BINDING-20261126-001')); sys.path.insert(0, str(HERE))
import repro as RP, minflip as MF, closing as CL, built as BU
forbid, classes = RP.forbid, RP.classes
CAP = 300


def families(S):
    h = forbid.holders(S)
    loose = {k: [x for x in S[k] if len(h[x]) == 1] for k in range(len(S))}
    live = [k for k in range(len(S)) if loose[k]]
    nbr = collections.defaultdict(set)
    for x, hs in h.items():
        if len(hs) == 2: nbr[hs[0]].add(hs[1]); nbr[hs[1]].add(hs[0])
    parent = {k: k for k in live}
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for w in range(len(S)):
        ln = [u for u in nbr[w] if u in parent]
        for u in ln[1:]: parent[find(u)] = find(ln[0])
    fam = collections.defaultdict(list)
    for k in live: fam[find(k)].append(k)
    fams = sorted(fam.values())
    return fams, [[x for k in f for x in loose[k]] for f in fams]


def _unused(S):
    return len(set(CL.components(S).values())) <= 1 if False else len({id(v) for v in []}) == 0


def labels_dim(st):
    names, idx, rows = RP.space(st)
    _, i2, up = RP.T2.moves_upto(st, 5)
    Hp = classes.nullspace(up, len(names))
    return classes.rank(rows + Hp) - classes.rank(rows), rows, Hp, idx


def run(name, S, rounds=4):
    fams, ls = families(S); m = len(fams)
    of = {k: i for i, f in enumerate(fams) for k in f}
    rec = {'start': name, 'knots': len(S), 'families': m, 'rounds': []}
    # T2
    names, idx, rows = RP.space(S)
    if m:
        occ = RP.tuples(rows, len(names), [sum(1 << idx[x] for x in l) for l in ls])
        rec['T2 tuples'] = len(occ); rec['T2 one rule, every proper subfamily free'] = RP.one_rule(occ, m) if m >= 2 else len(occ) == 1
    st = S; lineage = {k: {of[k]} if k in of else set() for k in range(len(S))}; L0 = None; t1 = 0
    for t in range(0, rounds + 1):
        if t:
            nxt, status, births = forbid.grown(st, 'parity', 'ordinary')
            if status != 'funded': rec['rounds'].append({'round': t, 'end': status}); break
            for b in births:
                fs = set().union(*(lineage[p] for p in b['parents'])); lineage[b['knot']] = fs
                if len(fs) > 1: t1 += 1
            st = nxt
        nd = len({x for r in st for x in r})
        if nd > CAP: rec['rounds'].append({'round': t, 'end': 'not read'}); break
        row = {'round': t, 'least flips': [MF.least(st, l, kmax=40) for l in ls]}
        if t >= 3:
            d, rws, Hp, ix = labels_dim(st)
            row['UPTO5 class facts'] = d
            row['every l_A a class fact'] = all(classes.rank(rws + Hp + [sum(1 << ix[x] for x in l)]) == classes.rank(rws + Hp) for l in ls) if m >= 2 else None
        rec['rounds'].append(row)
    rec['T1 births across families'] = t1
    return rec


def items(which, limit):
    if which in ('census', 'heldout'):
        it = CL.items(which)
        if which == 'census':
            import random
            S = list(it); rng = random.Random(20261215); it = rng.sample(S, min(limit, len(S)))
        yield from it
    elif which == 'sampled':
        for n in (9, 10, 11, 12):
            for j, s in enumerate(forbid.sampled(n, 100, 20261212 + n, max_distinctions=30)): yield 'sampled %d-%d' % (n, j), forbid.supports_of(s)
    elif which == 'merge':                     # the control: one dead knot meets two rings' knots, merging their families
        import families as FA
        for label, kw in FA.members():
            if kw['R'] != 3: continue
            S, rings, loose = RP.rings_start(**kw)
            x = max(d for r in S for d in r) + 1
            S = tuple(list(S) + [(x, x + 1, x + 2)])
            S = tuple(tuple(r) + ((x, x + 1) if i == rings[0][0] else (x + 2,) if i == rings[1][0] else ()) for i, r in enumerate(S[:-1])) + (S[-1],)
            yield label + ' + a dead knot meeting rings 1 and 2', S
    else:
        import families as FA
        for label, kw in FA.members(): yield label, RP.rings_start(**kw)[0]
        yield 'the 14-knot start', BU.build('base')[0]


if __name__ == '__main__':
    which, out = sys.argv[1], sys.argv[2]; limit = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    with open(out, 'w') as f:
        for name, S in items(which, limit):
            f.write(json.dumps(run(name, S)) + '\n'); f.flush()
