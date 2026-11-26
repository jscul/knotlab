"""premises.py SET OUT.jsonl [ROUNDS] [ARM]: the premises of the argument that every class fact is a function of the
start's values (README.md, "The argument"), checked on birth records, and the spanning set checked by rank.
BUILT-BINDING-20261126-001.

Premise 1  no birth takes two distinctions of one parent, and each round takes every loose distinction of every live
           knot (the engine's own asserts, rival_growth.grow, rechecked here from the records)
Premise 2  any two live knots with a common neighbour (a knot sharing a distinction with each) are parents of one
           birth of the next round
Premise 3  a birth with no fresh distinction is the only birth of its connected structure in its round, and each of
           its parents holds one loose distinction
Span       on stages of at most CAP distinctions: the allowed changes that leave every start distinction as it was
           (Z_new) are spanned by the pairs of loose distinctions at one newest birth and the loops of four through an
           older birth, two of its children and a common neighbour of theirs (a common child, or the outside point U
           when both are newest)
SET: census, heldout (closing.items), built (repro's families), sampled (fresh starts of 9 to 12 knots, families.py)."""
import sys, json, itertools, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import repro as RP, closing as CL
classes, forbid = RP.classes, RP.forbid
CAP = 400


def items(which):
    if which in ('census', 'heldout'): yield from CL.items(which)
    elif which == 'built':
        import families as FA
        for label, kw in FA.members(): yield label, RP.rings_start(**kw)[0]
    else:
        for n in (9, 10, 11, 12):
            for j, s in enumerate(forbid.sampled(n, 100, 20261212 + n, max_distinctions=30)):
                yield 'sampled %d-%d' % (n, j), forbid.supports_of(s)


def components(st):
    h = forbid.holders(st); parent = list(range(len(st)))
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for x, hs in h.items():
        for k in hs[1:]: parent[find(k)] = find(hs[0])
    return [find(k) for k in range(len(st))]


def check_round(st, births):
    h = forbid.holders(st)
    loose = {k: [x for x in st[k] if len(h[x]) == 1] for k in range(len(st))}
    live = [k for k in range(len(st)) if loose[k]]
    bad = collections.Counter()
    # premise 1
    taken = collections.Counter(x for b in births for x in b['inputs'])
    if set(taken) != {x for k in live for x in loose[k]} or any(v != 1 for v in taken.values()): bad['1: loose not taken once'] += 1
    for b in births:
        if len(set(b['parents'])) != len(b['inputs']): bad['1: two from one parent'] += 1
    # premise 2
    nbr = collections.defaultdict(set)
    for x, hs in h.items():
        if len(hs) == 2: nbr[hs[0]].add(hs[1]); nbr[hs[1]].add(hs[0])
    together = set()
    for b in births:
        for a, c in itertools.combinations(sorted(b['parents']), 2): together.add((a, c))
    for a, c in itertools.combinations(live, 2):
        if nbr[a] & nbr[c] and (a, c) not in together: bad['2: common neighbour, no common birth'] += 1
    # premise 3
    comp = components(st)
    per = collections.Counter(comp[b['parents'][0]] for b in births)
    for b in births:
        if b['f'] == 0:
            if per[comp[b['parents'][0]]] != 1: bad['3: zero-fresh birth not alone'] += 1
            if any(len(loose[p]) != 1 for p in b['parents']): bad['3: zero-fresh parent with more than one loose'] += 1
    return bad


def span_check(S, st, round_of):
    """rank of the pairs and loops of four inside F against dim Z_new"""
    names, idx, rows = RP.space(st); n = len(names)
    old = {x for r in S for x in r}
    Znew = classes.nullspace(rows + [1 << idx[x] for x in old if x in idx], n)
    h = forbid.holders(st); U = -1
    adj = collections.defaultdict(list)            # birth -> (other end, distinction), new distinctions only
    for x, hs in h.items():
        if x in old: continue
        a, b = (hs[0], hs[1]) if len(hs) == 2 else (hs[0], U)
        adj[a].append((b, x)); adj[b].append((a, x))
    gens = []
    t = max(round_of.values())
    for w in adj:
        if w == U: continue
        if round_of[w] == t:
            us = [x for o, x in adj[w] if o == U]
            gens += [(1 << idx[us[0]]) | (1 << idx[y]) for y in us[1:]]
        else:
            kids = [(o, x) for o, x in adj[w] if o != U and round_of[o] == round_of[w] + 1]
            for (v1, x1), (v2, x2) in itertools.combinations(kids, 2):
                up1 = {o: y for o, y in adj[v1] if o == U or round_of.get(o, -9) == round_of[v1] + 1}
                for o, y2 in adj[v2]:
                    if (o == U or round_of.get(o, -9) == round_of[v2] + 1) and o in up1:
                        gens.append((1 << idx[x1]) | (1 << idx[x2]) | (1 << idx[up1[o]]) | (1 << idx[y2])); break
    return {'dim Z_new': len(Znew), 'rank of pairs and loops of four': classes.rank(gens),
            'inside Z_new': classes.rank(Znew + gens) == len(Znew)}


if __name__ == '__main__':
    which, out = sys.argv[1], sys.argv[2]
    rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 6; arm = sys.argv[4] if len(sys.argv) > 4 else 'ordinary'
    tally = collections.Counter(); spans = collections.Counter()
    with open(out, 'w') as f:
        for name, S in items(which):
            st = S; round_of = {k: 0 for k in range(len(S))}; rec = {'start': name, 'rounds': []}
            for t in range(1, rounds + 1):
                nxt, status, births = forbid.grown(st, 'parity', arm)
                if status != 'funded': rec['rounds'].append({'round': t, 'end': status}); break
                bad = check_round(st, births)
                for b in births: round_of[b['knot']] = t
                st = nxt; tally['rounds read'] += 1; tally.update(bad)
                row = {'round': t, 'premises broken': dict(bad)}
                if len({x for r in st for x in r}) <= CAP:
                    sp = span_check(S, st, round_of); row['span'] = sp
                    spans['stages'] += 1; spans['equal'] += sp['dim Z_new'] == sp['rank of pairs and loops of four'] and sp['inside Z_new']
                rec['rounds'].append(row)
                if len({x for r in st for x in r}) > 20000: rec['rounds'].append({'round': t, 'end': 'size cap'}); break
            f.write(json.dumps(rec) + '\n'); f.flush()
        f.write(json.dumps({'premises': dict(tally), 'span': dict(spans)}) + '\n')
    print(dict(tally), dict(spans))
