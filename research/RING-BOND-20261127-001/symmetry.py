"""symmetry.py OUT.json: does anything in the growth single out one of the ring's bonds?  RING-BOND-20261127-001.

The start (0,1,3), (1,2,4), (2,0,5) has the permutations of its three knots as symmetries: the turn r (0>1>2>0, 3>4>5>3)
and the exchange s (0<>1, 4<>5).  For each round 0..ROUNDS: whether r and s (identity on every later distinction) map
the stage's knots onto themselves; the births' parents and inputs under them; and the orbits of the stage's bonds under
the group they make (agreement readings; a bond's image is again a bond of the stage).  Separately: growth from the
start under three relabellings of its distinctions and an order of its knots, compared with the relabelled growth."""
import sys, json, itertools, random, collections
import ringbond as RB

R = {0: 1, 1: 2, 2: 0, 3: 4, 4: 5, 5: 3}
X = {0: 1, 1: 0, 4: 5, 5: 4}


def compose(p, q):
    keys = set(p) | set(q)
    return {k: p.get(q.get(k, k), q.get(k, k)) for k in keys}


def group():
    e = {}; out = [e]
    frontier = [e]
    while frontier:
        nxt = []
        for g in frontier:
            for h in (R, X):
                c = compose(h, g)
                c = {k: v for k, v in c.items() if k != v}
                if all(c != o for o in out): out.append(c); nxt.append(c)
        frontier = nxt
    return out


def canon(sup):
    return sorted(tuple(sorted(r)) for r in sup)


if __name__ == '__main__':
    ROUNDS = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    S = ((0, 1, 3), (1, 2, 4), (2, 0, 5))
    G = group(); out = {'group order': len(G), 'rounds': []}
    for t, (sup, born) in enumerate(RB.stages(S, 'nae', ROUNDS)):
        fixes = [RB.automorphisms_fix(sup, g) for g in G]
        st = RB.Stage(sup, 'nae'); res = RB.bonds(st, 'agree', born=born)
        keys = {RB.bond_key(b): b for b in res['bonds']}
        orbits, seen = [], set()
        for k, b in keys.items():
            if k in seen: continue
            orb = {RB.bond_image(b, g) for g in G}
            assert orb <= set(keys), 'an image of a bond is not a bond'
            seen |= orb; orbits.append(len(orb))
        out['rounds'].append({'round': t, 'knots': len(sup), 'every symmetry maps the stage onto itself': all(fixes),
                              'bonds': len(keys), 'orbit sizes': dict(collections.Counter(orbits)),
                              'bonds fixed by every symmetry': sum(1 for o in orbits if o == 1)})
    # growth under relabellings: the relabelled growth equals the growth relabelled
    rng = random.Random(20261127); rel = []
    for trial in range(3):
        names = list(range(6)); img = names[:]; rng.shuffle(img); m = dict(zip(names, [10 + i for i in img]))
        order = list(range(3)); rng.shuffle(order)
        S2 = tuple(tuple(m[x] for x in S[i]) for i in order)
        a = RB.stages(S, 'nae', ROUNDS)[-1][0]; b = RB.stages(S2, 'nae', ROUNDS)[-1][0]
        # isomorphic with the start's distinctions matched by the relabelling and born ones free
        import networkx as nx
        def graph(sup, lab):
            g = nx.Graph()
            for k, r in enumerate(sup):
                g.add_node(('k', k), lab='knot')
                for x in r: g.add_node(('d', x), lab=lab(x)); g.add_edge(('k', k), ('d', x))
            return g
        ga = graph(a, lambda x: m.get(x, 'born')); gb = graph(b, lambda x: x if x in m.values() else 'born')
        rel.append({'trial': trial, 'knots': [len(a), len(b)],
                    'isomorphic with the start relabelled': nx.is_isomorphic(ga, gb, node_match=lambda p, q: p['lab'] == q['lab'])})
    out['relabelled growth'] = rel
    # P1.4: the choice-free reading of the three opposite pairs against 6, on round 1, and with each law removed
    import numpy as np
    sup = RB.stages(S, 'nae', 1)[1][0]; st = RB.Stage(sup, 'nae')
    def three(mask):
        A = st.states[mask]; b = {x: st.bits(x, A) for x in range(7)}
        vals = []
        for a, c in ((1, 5), (2, 3), (0, 4)):
            v = np.where(b[a] != b[c], 0, np.where(b[a] == b[6], 1, 2)); vals.append(v)
        return set(zip(*[v.tolist() for v in vals]))
    T = three(st.allowed); lost = sorted(set(itertools.product(range(3), repeat=3)) - T)
    pairs = [len({(t[a], t[b]) for t in T}) for a, b in ((0, 1), (0, 2), (1, 2))]
    out['P1.4 three-valued'] = {'values': '0 apart, 1 agree with 6, 2 agree against 6', 'triples': len(T), 'pairs (of 9)': pairs,
                               'missing': lost,
                               'with each law removed': [len(three(st.allowed | (st.broken == q))) for q in range(len(sup))],
                               'unchanged by every renaming': all(
                                   {tuple(t[[(1, 5), (2, 3), (0, 4)].index(tuple(sorted((g.get(a, a), g.get(c, c)))))]
                                          for (a, c) in ((1, 5), (2, 3), (0, 4))) for t in T} == T for g in G)}
    json.dump(out, open(sys.argv[1], 'w'), indent=1); print(json.dumps(out, indent=1))
