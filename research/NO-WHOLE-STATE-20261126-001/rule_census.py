"""rule_census.py: the frozen census of README.md, part E (preregistration.md). Rule R: the values of two distinctions
commute exactly when some knot holds both. Every closed, twice-held parity pattern of the 20 November census
(FOUR-READINGS-20261120-001A, census.json: 173 types, every simple connected sharing with at least three places per
holder and at most seven holders), the eight-knot closure of three-label subsets, and the three patterns of parts.py.

Per pattern (knots as lists of distinction ids, each distinction held by exactly two knots):
    R1  under R, do the knots' operators commute pairwise (so one state can make every knot definite)?
    R2  if so, the parity R forces on the sum of the knots' signs (the closing sign when every older knot is even)
    R3  with any choice of which unheld pairs fail to commute (pairs a common knot holds always commute), all knots'
        operators commuting: is an odd sum attainable? an even one? (a linear system over GF(2))
    plus, after the advisor's reading: planarity (the literature's criterion for a signed-identity reading, against the
    stored verdict), outerplanarity (R3 should fail exactly on outerplanar patterns), knots commuting with every value
    under R, cut knots, the closed form of R1 for simple patterns, a shuffle test (R2 unchanged under relabelling where
    R1 holds), named types, outerplanar controls with repeated meetings, and part counting against the state's counts on
    two four-knot closures sharing one knot.
Each type has one vote; the census's labelled count is a second weighting, reported beside it."""
import sys, json, itertools, random
from pathlib import Path
import networkx as nx
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import values_commute as vc, parts                              # noqa: E402


def from_ends(ends):
    n = 1 + max(v for e in ends for v in e)
    return [[i for i, e in enumerate(ends) if u in e] for u in range(n)]


def from_pattern(pattern):
    names = sorted({d for k, _ in pattern for d in k}, key=str)
    idx = {d: i for i, d in enumerate(names)}
    return [[idx[d] for d in k] for k, _ in pattern], [p for _, p in pattern]


def analyse(knots):
    m = 1 + max(d for k in knots for d in k)
    holders = {d: [u for u, k in enumerate(knots) if d in k] for d in range(m)}
    assert all(len(h) == 2 for h in holders.values()), 'every distinction held twice'
    held = lambda i, j: bool(set(holders[i]) & set(holders[j]))
    unheld = [(i, j) for i, j in itertools.combinations(range(m), 2) if not held(i, j)]
    word = [d for k in knots for d in sorted(k)]
    pos = {}
    for t, d in enumerate(word): pos.setdefault(d, []).append(t)
    inter = lambda i, j: (lambda a, b, x, y: a < x < b < y or x < a < y < b)(*pos[i], *pos[j])
    # constraints: for each pair of knots, the number of non-commuting place pairs between them is even
    rows = []
    for u, v in itertools.combinations(range(len(knots)), 2):
        r = 0
        for p, (i, j) in enumerate(unheld):
            r ^= ((i in knots[u] and j in knots[v]) ^ (j in knots[u] and i in knots[v])) << p
        rows.append(r)
    cost = sum(1 << p for p, (i, j) in enumerate(unheld) if inter(i, j))
    allR = (1 << len(unheld)) - 1
    R1 = all((r & allR).bit_count() % 2 == 0 for r in rows)
    R2 = (cost & allR).bit_count() % 2 if R1 else None
    # R3: is the cost functional in the row space of the constraints? if so every solution gives the same parity (0)
    piv = {}
    for r in rows:
        while r:
            h = r.bit_length() - 1
            if h in piv: r ^= piv[h]
            else: piv[h] = r; break
    c = cost
    while c:
        h = c.bit_length() - 1
        if h not in piv: break
        c ^= piv[h]
    odd_attainable = c != 0
    # under R a knot commutes with every value when each distinction off it fails to commute with an even number of its places
    central = sum(all(sum(1 for e in k if (min(e, f), max(e, f)) in set(unheld)) % 2 == 0 for f in range(m) if f not in k)
                  for k in knots)
    G = nx.Graph(); G.add_nodes_from(range(len(knots)))
    G.add_edges_from(tuple(holders[d]) for d in range(m))
    A = G.copy(); A.add_edges_from(('apex', u) for u in range(len(knots)))
    return {'knots': len(knots), 'distinctions': m, 'unheld pairs': len(unheld), 'R1 knots commute under R': R1,
            'R2 sum forced under R': None if R2 is None else ('odd' if R2 else 'even'),
            'R3 odd attainable': odd_attainable, 'knots commuting with every value under R': central,
            'planar': nx.check_planarity(G)[0], 'outerplanar': nx.check_planarity(A)[0],
            'cut knots': len(list(nx.articulation_points(G)))}


def closed_form_R1(ends):
    """the advisor's closed form for simple patterns: knots that share, (d_u - 1)(d_v - 1) = t; knots that do not,
    d_u d_v = t (mod 2), t their common neighbours"""
    G = nx.Graph(ends)
    for u, v in itertools.combinations(G, 2):
        t = len(set(G[u]) & set(G[v])); du, dv = G.degree(u), G.degree(v)
        if ((du - 1) * (dv - 1) - t if G.has_edge(u, v) else du * dv - t) % 2: return False
    return True


def shuffled(knots, rng):
    m = 1 + max(d for k in knots for d in k)
    rename = list(range(m)); rng.shuffle(rename)
    out = [[rename[d] for d in k] for k in knots]; rng.shuffle(out)
    for k in out: rng.shuffle(k)
    return out


def word_counts(knots, read):
    """words on the read set allowed by part counting (knots wholly inside it) and by the state the signed knots
    stabilise (every product of knots whose distinctions left over after cancelling lie inside it): 2^(|read| - rank)"""
    read = set(read); n = len(knots)
    def rank(vecs):
        piv = {}; r = 0
        for v in vecs:
            while v:
                h = v.bit_length() - 1
                if h in piv: v ^= piv[h]
                else: piv[h] = v; r += 1; break
        return r
    star = [sum(1 << d for d in k) for k in knots]
    closed = [s for k, s in zip(knots, star) if set(k) <= read]
    state = []
    for size in range(1, n + 1):
        for U in itertools.combinations(range(n), size):
            x = 0
            for u in U: x ^= star[u]
            if x and all((x >> d) & 1 == 0 or d in read for d in range(x.bit_length())): state.append(x)
    return 2 ** (len(read) - rank(closed)), 2 ** (len(read) - rank(state))


if __name__ == '__main__':
    census = json.load(open(vc.ART / 'census.json'))
    rows = []
    for t, e in enumerate(census):
        a = analyse(from_ends([tuple(x) for x in e['sharing']]))
        a.update({'type': t, 'atlas': e['atlas'], 'labelled': e['labelled'], 'operator (signed identities)': e['operator'],
                  'reached by ordinary growth': bool(e['restored_last_holders'])})
        rows.append(a)
    (HERE / 'rule_census.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
    def tally(sel, w):
        S = [r for r in rows if sel(r)]
        W = lambda f: sum(w(r) for r in S if f(r))
        return {'types': W(lambda r: True), 'R1 commute': W(lambda r: r['R1 knots commute under R']),
                'R2 odd': W(lambda r: r['R2 sum forced under R'] == 'odd'), 'R2 even': W(lambda r: r['R2 sum forced under R'] == 'even'),
                'R3 odd attainable': W(lambda r: r['R3 odd attainable'])}
    for wname, w in (('one vote per type', lambda r: 1), ('one vote per labelled pattern', lambda r: r['labelled'])):
        for sname, sel in (('all 173', lambda r: True), ('reached', lambda r: r['reached by ordinary growth']),
                           ('reached, operator-positive', lambda r: r['reached by ordinary growth'] and r['operator (signed identities)']),
                           ('reached, operator-negative', lambda r: r['reached by ordinary growth'] and not r['operator (signed identities)']),
                           ('operator-negative', lambda r: not r['operator (signed identities)'])):
            print(json.dumps({'weighting': wname, 'set': sname, **tally(sel, w)}))
    print(json.dumps({'closed form of R1 agrees': sum(closed_form_R1([tuple(x) for x in census[r['type']]['sharing']]) ==
                                                      r['R1 knots commute under R'] for r in rows), 'of': len(rows),
                      'planar = no signed-identity reading': sum(r['planar'] == (not r['operator (signed identities)']) for r in rows),
                      'outerplanar types': sum(r['outerplanar'] for r in rows),
                      'R3 odd attainable = not outerplanar': sum(r['R3 odd attainable'] == (not r['outerplanar']) for r in rows)}))
    rng = random.Random(20261127); moved = 0; tried = 0
    for r in rows:
        if not r['R1 knots commute under R']: continue
        k0 = from_ends([tuple(x) for x in census[r['type']]['sharing']])
        for _ in range(20):
            a = analyse(shuffled(k0, rng)); tried += 1
            moved += a['R2 sum forced under R'] != r['R2 sum forced under R']
    print(json.dumps({'shuffle test': {'relabellings': tried, 'R2 changed': moved}}))
    named = {'K6': nx.complete_graph(6), 'K7': nx.complete_graph(7), 'K1,3,3': nx.complete_multipartite_graph(1, 3, 3),
             'K3,4': nx.complete_bipartite_graph(3, 4), 'two four-knot closures sharing one knot':
             nx.Graph([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (0, 4), (0, 5), (0, 6), (4, 5), (4, 6), (5, 6)])}
    for name, H in named.items():
        hit = [r for r in rows if nx.is_isomorphic(nx.Graph([tuple(x) for x in census[r['type']]['sharing']]), H)]
        print(json.dumps({name: {k: hit[0][k] for k in ('type', 'R1 knots commute under R', 'R2 sum forced under R',
                                 'R3 odd attainable', 'operator (signed identities)', 'reached by ordinary growth',
                                 'knots commuting with every value under R', 'cut knots')} if hit else 'not in the census'}))
    twin = from_ends([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (0, 4), (0, 5), (0, 6), (4, 5), (4, 6), (5, 6)])
    print(json.dumps({'two four-knot closures sharing one knot, the shared knot read': dict(zip(
        ('words by part counting', 'words in the stabilised state'), word_counts(twin, twin[0])))}))
    def ring(n, mult):
        knots = [[] for _ in range(n)]; d = 0
        for u in range(n):
            for _ in range(mult): knots[u].append(d); knots[(u + 1) % n].append(d); d += 1
        return knots
    for name, knots in (('ring of three, meetings doubled', ring(3, 2)), ('ring of four, meetings doubled', ring(4, 2)),
                        ('ring of five, meetings doubled', ring(5, 2)), ('ring of four, meetings tripled', ring(4, 3))):
        print(json.dumps({'outerplanar control, ' + name: analyse(knots)}))
    for n in (4, 5, 6, 7):
        S = [r for r in rows if r['knots'] == n]
        print(json.dumps({'knots': n, 'types': len(S), 'R1 commute': sum(r['R1 knots commute under R'] for r in S),
                          'R2 odd': sum(r['R2 sum forced under R'] == 'odd' for r in S),
                          'R3 odd attainable': sum(r['R3 odd attainable'] for r in S)}))
    print(json.dumps({'eight-knot closure': analyse(from_ends(vc.subsets_closure(3)))}))
    for name, make in (('three readers', parts.ghz), ('nine-distinction square', parts.square),
                       ('two readers, 3-place knots', parts.two_reader)):
        knots, signs = from_pattern(make()[0])
        print(json.dumps({name: analyse(knots), 'signs given': signs}))
