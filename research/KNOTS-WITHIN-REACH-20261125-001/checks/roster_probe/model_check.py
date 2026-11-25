"""Directions 2 and 3 of the probe.
(2) Is the roster after round t, with its one-step relation, the same as this model: the ordered ways of writing t - 1 as a sum of
    m non-negative whole numbers, two of them one step apart when one unit moves from one term to another, plus one extra member
    attached to each of the m sums that have a single non-zero term?  Tested by an exact isomorphism search.
(3) m knots of m + 1 places, each sharing one distinction with every other (the start of FIRST-KNOT-20261118-001's Proposition 4),
    for m = 3, 4, 5, 6: the count at one round from the best-placed member."""
import sys, os, json, itertools, collections, time
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
HERE = os.path.dirname(os.path.abspath(__file__))
X = ROOT + '/experiments/KNOTS-WITHIN-REACH-20261125-001A/KNOTS-WITHIN-REACH-20261125-001A-E001_knots_within_reach'
sys.dont_write_bytecode = True
sys.path.insert(0, X)
import networkx as nx
import kwr
pm = kwr.pm

def touching(m):
    """m knots of m + 1 places, each pair sharing one distinction of its own; two loose each."""
    d = itertools.count()
    pair = {frozenset(p): next(d) for p in itertools.combinations(range(m), 2)}
    return [[pair[frozenset((i, j))] for j in range(m) if j != i] + [next(d), next(d)] for i in range(m)]

def roster_graph(G, t):
    S = G.S; members = G.members[t]; upto = G.n_knots[t]
    ms = kwr.met_sets(S, members, upto)
    g = nx.Graph(); g.add_nodes_from(members)
    for w, M in ms.items():
        for a, b in itertools.combinations(sorted(M), 2):
            g.add_edge(a, b)
    return g

def model(m, s):
    """compositions of s into m parts, unit moves; plus a pendant at each s*e_i."""
    g = nx.Graph()
    def comps(n, k):
        if k == 1:
            yield (n,); return
        for i in range(n + 1):
            for rest in comps(n - i, k - 1):
                yield (i,) + rest
    pts = list(comps(s, m)); g.add_nodes_from(pts)
    for p in pts:
        for i in range(m):
            if p[i] == 0: continue
            for j in range(m):
                if j == i: continue
                q = list(p); q[i] -= 1; q[j] += 1
                g.add_edge(p, tuple(q))
    for i in range(m):
        tip = tuple(s if k == i else 0 for k in range(m))
        g.add_edge(tip, ('extra', i))
    return g

def ball_counts(g):
    best = None
    for s in g.nodes:
        d = nx.single_source_shortest_path_length(g, s)
        cnt = collections.Counter(d.values()); seq = []; tot = 0
        for r in range(max(cnt) + 1):
            tot += cnt[r]; seq.append(tot)
        if best is None:
            best = seq
        else:
            L = max(len(best), len(seq))
            best = [max(best[r] if r < len(best) else best[-1], seq[r] if r < len(seq) else seq[-1]) for r in range(L)]
    return best

out = {'matching': [], 'touching starts': []}
law = kwr.make_law('L0', 'nae')
for m, rounds, stages in ((3, 16, (4, 8, 12, 16)), (4, 10, (4, 6, 8, 10)), (5, 8, (4, 6, 8))):
    G = kwr.Grown('touching-%d' % m, law, rounds, S=pm.from_stars(touching(m)), parts_every_round=False)
    for t in stages:
        if t > G.S.round: continue
        g = roster_graph(G, t); mod = model(m, t - 1)
        t0 = time.time()
        same_size = (g.number_of_nodes(), g.number_of_edges()) == (mod.number_of_nodes(), mod.number_of_edges())
        iso = same_size and (sorted(d for _, d in g.degree()) == sorted(d for _, d in mod.degree())) and nx.is_isomorphic(g, mod)
        out['matching'].append({'m': m, 'round': t, 'members': g.number_of_nodes(), 'one-step pairs': g.number_of_edges(),
                                'model members': mod.number_of_nodes(), 'model pairs': mod.number_of_edges(), 'the same up to renaming': bool(iso),
                                'seconds': round(time.time() - t0, 2)})
        print(out['matching'][-1], flush=True)
# census starts of each class against the model
cs = json.load(open(ROOT + '/research/KNOTS-WITHIN-REACH-20261125-001A/census_starts.json'))
for idx, m in ((19, 3), (164, 3), (214, 3), (2086, 3), (177, 4), (218, 4), (3195, 4)):
    G = kwr.Grown('census:%d' % idx, law, 9, parts_every_round=False)
    for t in (6, 9):
        g = roster_graph(G, t); mod = model(m, t - 1)
        iso = (g.number_of_nodes(), g.number_of_edges()) == (mod.number_of_nodes(), mod.number_of_edges()) and nx.is_isomorphic(g, mod)
        out['matching'].append({'start': 'census:%d' % idx, 'm': m, 'round': t, 'members': g.number_of_nodes(), 'the same up to renaming': bool(iso)})
        print(out['matching'][-1], flush=True)
# direction 3: the count at one round for m = 3..6
for m, rounds in ((3, 30), (4, 24), (5, 16), (6, 12)):
    G = kwr.Grown('touching-%d' % m, law, rounds, S=pm.from_stars(touching(m)), parts_every_round=False)
    t = G.S.round
    g = roster_graph(G, t)
    deg = collections.Counter(d for _, d in g.degree())
    env = ball_counts(g) if g.number_of_nodes() <= 4000 else None
    rec = {'m': m, 'rounds done': t, 'stop': G.stop, 'knots': G.n_knots[-1], 'members per round': [len(x) for x in G.members][:10],
           'members': g.number_of_nodes(), 'most within one step': max(deg), 'greatest count at each r': env[:10] if env else None}
    out['touching starts'].append(rec); print(rec, flush=True)
json.dump(out, open(os.path.join(HERE, 'model_check.json'), 'w'), indent=1)
