"""distances.py: do the two distances of a class both grow? (README.md). Under parity a structure is read as a graph:
knots as vertices, each shared distinction an edge between its two holders, and with loose values free each loose
distinction an edge to one extra unconstrained vertex (so the allowed changes are exactly the cycles). The moves are the
shortest cycles through each edge, every tie kept (the motion study's rule); H their span; the classes S/H.
    d_change  the shortest cycle outside H (found among the literature's Horton candidates, a shortest path from a vertex
              to each end of an edge, which contain a shortest cycle outside any subspace)
    d_read    the least set of distinctions with even overlap with every move and odd overlap with some cycle (a class
              label), by an exact solver (z3), one class generator at a time
Rings of n knots with two loose distinctions each, grown round by round under ordinary growth (canonical engine), loose
free and pinned.

    distances.py rings NMAX ROUNDS
    distances.py census|extension ROUNDS COUNT     a seeded uniform sample of starts (random.Random(20261127))"""
import sys, json, itertools, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'TWO-CLASS-SIGN-20261126-001'))
import classes
forbid = classes.forbid
import networkx as nx
import z3
TIE_CAP = 64
READ_ARG, CHANGE_ARG = [None], [None]
CAP_HITS = [0]


def graph(supports, pinned):
    held = forbid.holders(supports)
    assert all(len(h) in (1, 2) for h in held.values()), 'a distinction with more than two holders'
    edges = []                       # (u, v, distinction)
    INF = len(supports)
    for d, hs in sorted(held.items()):
        if len(hs) == 2: edges.append((hs[0], hs[1], d))
        elif not pinned: edges.append((hs[0], INF, d))
    G = nx.MultiGraph()
    G.add_nodes_from(range(len(supports) + (0 if pinned else 1)))
    for k, (u, v, d) in enumerate(edges): G.add_edge(u, v, key=k)
    return G, edges


def cyc_vec(path_edges):
    v = 0
    for k in path_edges: v ^= 1 << k
    return v


def shortest_paths_edges(G, s, t, avoid):
    """edge-index sets of the shortest s-t paths avoiding edge `avoid` (up to TIE_CAP)"""
    H = nx.MultiGraph(G); H.remove_edge(*avoid)
    try: L = nx.shortest_path_length(H, s, t)
    except nx.NetworkXNoPath: return []
    out = []
    for p in nx.all_shortest_paths(nx.Graph(H), s, t):
        # expand parallel edges
        choices = [[k for k in H[a][b]] for a, b in zip(p, p[1:])]
        for ch in itertools.product(*choices):
            out.append(ch)
            if len(out) >= TIE_CAP: CAP_HITS[0] += 1; return out
    return out


def moves(G, edges):
    M = set()
    for k, (u, v, d) in enumerate(edges):
        if u == v: M.add(1 << k); continue
        for p in shortest_paths_edges(G, u, v, (u, v, k)):
            M.add(cyc_vec(p) ^ (1 << k))
    return M


def basis_of(vecs):
    piv = {}
    for v in vecs:
        while v:
            p = v.bit_length() - 1
            if p in piv: v ^= piv[p]
            else: piv[p] = v; break
    return piv


def in_span(piv, v):
    while v:
        p = v.bit_length() - 1
        if p not in piv: return False
        v ^= piv[p]
    return True


def horton_change(G, edges, Hpiv):
    best = None; Gs = nx.Graph()
    for u, v, k in G.edges(keys=True): Gs.add_edge(u, v)
    for s in G.nodes:
        try: pred = nx.single_source_shortest_path(Gs, s)
        except Exception: continue
        def path_edges(t):
            p = pred[t]; out = []
            for a, b in zip(p, p[1:]): out.append(min(G[a][b]))
            return out
        for u, v, k in G.edges(keys=True):
            if u not in pred or v not in pred: continue
            c = cyc_vec(path_edges(u)) ^ cyc_vec(path_edges(v)) ^ (1 << k)
            if c == 0: continue
            w = bin(c).count('1')
            if best is not None and w >= best: continue
            # a closed walk; its edge set is a cycle-space element
            if not in_span(Hpiv, c): best = w; CHANGE_ARG[0] = c
    return best


def read_distance(edges, Mbasis, Sbasis, Hpiv):
    m = len(edges)
    gens = [b for b in Sbasis if not in_span(Hpiv, b)]
    best = None
    for g in gens[:4]:
        opt = z3.Optimize(); z = [z3.Bool('z%d' % i) for i in range(m)]
        def parity(vec):
            terms = [z[i] for i in range(m) if (vec >> i) & 1]
            if not terms: return z3.BoolVal(False)
            x = terms[0]
            for t in terms[1:]: x = z3.Xor(x, t)
            return x
        for b in Mbasis: opt.add(z3.Not(parity(b)))
        opt.add(parity(g))
        h = opt.minimize(z3.Sum([z3.If(zi, 1, 0) for zi in z]))
        opt.set('timeout', 60000)
        if opt.check() == z3.sat:
            mdl = opt.model(); w = mdl.eval(z3.Sum([z3.If(zi, 1, 0) for zi in z])).as_long()
            if best is None or w < best:
                best = w; READ_ARG[0] = sum(1 << i for i in range(m) if z3.is_true(mdl.eval(z[i])))
        else:
            return 'not run (solver)'
    return best


def analyse(supports, pinned):
    G, edges = graph(supports, pinned)
    CAP_HITS[0] = 0
    M = moves(G, edges)
    Hpiv = basis_of(M)
    Sb = [b for b in nx.cycle_basis(nx.Graph(G))]   # placeholder, replaced below
    # cycle space basis with multiedges: spanning tree + each non-tree edge
    T = nx.minimum_spanning_tree(nx.Graph(G)); tree = set()
    for a, b in T.edges(): tree.add(min(G[a][b]))
    Sbasis = []
    for u, v, k in G.edges(keys=True):
        if k in tree: continue
        p = nx.shortest_path(T, u, v)
        c = (1 << k) ^ cyc_vec([min(G[a][b]) for a, b in zip(p, p[1:])])
        Sbasis.append(c)
    dS, dH = len(basis_of(Sbasis)), len(Hpiv)
    out = {'knots': len(supports), 'distinctions': len(edges), 'dim S': dS, 'dim H': dH, 'classes': 2 ** (dS - dH),
           'tie cap reached': CAP_HITS[0]}
    if dS > dH:
        out['d_change'] = horton_change(G, edges, Hpiv)
        out['d_read'] = read_distance(edges, list(Hpiv.values()), Sbasis, Hpiv)
        z, r = READ_ARG[0], CHANGE_ARG[0]
        if isinstance(out['d_read'], int) and z is not None and r is not None:
            Spiv = basis_of(Sbasis)
            out['the least label is also an allowed change'] = in_span(Spiv, z)
            out['the least change is also a class label'] = (all(bin(r & h).count('1') % 2 == 0 for h in Hpiv.values())
                                                             and any(bin(r & b).count('1') % 2 == 1 for b in Sbasis))   # odd on some allowed change (the advisor's fix)
            out['the least change, as distinctions'] = [edges[i][2] for i in range(len(edges)) if (r >> i) & 1]
    return out


def grown_rows(name, st, rounds):
    for r in range(0, rounds + 1):
        if r:
            new, status, b = forbid.grown(st, 'parity', 'ordinary')
            if status != 'funded': return
            st = new
        row = {'structure': name, 'round': r}
        for pin in (False, True): row['loose pinned' if pin else 'loose free'] = analyse(st, pin)
        print(json.dumps(row), flush=True)


if __name__ == '__main__' and sys.argv[1] in ('census', 'extension'):
    import random
    rounds, count = int(sys.argv[2]), int(sys.argv[3])
    S = forbid.census() if sys.argv[1] == 'census' else forbid.extension()
    picks = sorted(random.Random(20261127).sample(range(len(S)), count))
    for i in picks: grown_rows('%s %d' % (sys.argv[1], i), forbid.supports_of(S[i]), rounds)
    sys.exit()

if __name__ == '__main__':
    nmax, rounds = int(sys.argv[2]), int(sys.argv[3])
    for n in range(4, nmax + 1):
        st = classes.ring(n, 2)
        for r in range(0, rounds + 1):
            if r:
                new, status, b = forbid.grown(st, 'parity', 'ordinary')
                if status != 'funded': break
                st = new
            row = {'ring': n, 'round': r}
            for pin in (False, True): row['loose pinned' if pin else 'loose free'] = analyse(st, pin)
            print(json.dumps(row), flush=True)
