"""Test families for HANDLE-COUNT-20261106-001A: Robertson-Seymour-Thomas trisum braces built from cubes and prisms, and the plain
three-fold spaces obtained by decorating them (THREEFOLD-GRAMMAR-20261030-001A, Theorem 6: T14 on signed points, Fano blocks on repeated
points). Deterministic given the seed."""
import random

import networkx as nx

import seymour_lib as SL
import twist_lib as TW


def planar_pool():
    out = {'cube': nx.hypercube_graph(3)}
    for k in (3, 4, 5):
        out['prism%d' % (2 * k)] = nx.circular_ladder_graph(2 * k)
    return {k: nx.convert_node_labels_to_integers(v) for k, v in out.items()}


def faces_of(g):
    ok, emb = nx.check_planarity(g)
    seen, faces = set(), []
    for u, v in emb.edges():
        if (u, v) not in seen:
            faces.append(emb.traverse_face(u, v, mark_half_edges=seen))
    return faces


def trisum_brace(seed, nsum, pool=None):
    """iterated trisums: at each step a 4-face of a planar piece, disjoint from earlier squares and with its edges still present, gets two
    fresh planar braces glued on (each along one of its 4-faces, colours matched), and the square's edges are deleted"""
    pool = pool or planar_pool()
    r = random.Random(seed)
    names = sorted(pool)
    G = nx.relabel_nodes(pool[r.choice(names)], lambda v: ('a', v))
    pieces = [G.copy()]
    used = set()
    cnt = 0
    for _ in range(nsum):
        cands = []
        for P in pieces:
            for f in faces_of(P):
                if len(f) == 4 and not (set(f) & used) and all(G.has_edge(f[j], f[(j + 1) % 4]) for j in range(4)):
                    cands.append(tuple(f))
        if not cands:
            break
        C = r.choice(sorted(cands, key=str))
        col = nx.bipartite.color(G)
        new = []
        for _t in range(2):
            cnt += 1
            B = pool[r.choice(names)]
            colB = nx.bipartite.color(B)
            fb = r.choice(sorted([f for f in faces_of(B) if len(f) == 4], key=str))
            seq = None
            for rot in range(4):
                for rev in (False, True):
                    s = list(fb[rot:] + fb[:rot])
                    if rev:
                        s = s[::-1]
                    if all(colB[s[j]] == col[C[j]] for j in range(4)):
                        seq = s
                        break
                if seq:
                    break
            mp = {seq[j]: C[j] for j in range(4)}
            new.append(nx.relabel_nodes(B, lambda v, cnt=cnt: mp.get(v, ('b%d' % cnt, v))))
        for Bn in new:
            G.add_edges_from(Bn.edges())
        G.remove_edges_from([(C[j], C[(j + 1) % 4]) for j in range(4)])
        used |= set(C)
        pieces += new
    return G


def system(G):
    """(lines, point index, line index) of a cubic bipartite graph with balanced colour classes"""
    col = nx.bipartite.color(G)
    pts = sorted((v for v in G if col[v] == 0), key=str)
    lns = sorted((v for v in G if col[v] == 1), key=str)
    assert len(pts) == len(lns)
    pid = {v: k for k, v in enumerate(pts)}
    lid = {v: k for k, v in enumerate(lns)}
    return [tuple(pid[w] for w in G[l]) for l in lns], pid, lid


def pfaffian_signing(G):
    """a Pfaffian signing of a trisum brace (glued Kasteleyn signings, SEYMOUR-COUNT B Lemma 2), as incidences (line, point) of system(G)"""
    H, pid, lid = system(G)
    lines = set(lid)
    leaves, squares = SL.trisum_tree(G, lines)
    neg = TW.kasteleyn_tree_signing(leaves)
    out = []
    for e in neg:
        a, b = tuple(e)
        l, p = (a, b) if a in lines else (b, a)
        out.append((lid[l], pid[p]))
    return H, sorted(out), len(squares)


def decoration_cost(H, negs):
    """atoms that grammar_lib.decorate spends on a signing: two per point with one or two negations (T14), one per point with three
    (a Fano block; repeated points do not occur in simple systems)"""
    per = {}
    for i, p in negs:
        per[p] = per.get(p, 0) + 1
    return sum(2 if k in (1, 2) else 1 for k in per.values())


def cheap_switching(H, negs, seed=0, rounds=2000):
    """a switching-equivalent signing (same Pfaffian class) that lowers decoration_cost, by greedy switching at lines and points"""
    r = random.Random(seed)
    cur = set(map(tuple, negs))
    best = decoration_cost(H, cur)
    incid_line = {i: [(i, p) for p in l] for i, l in enumerate(H)}
    incid_pt = {}
    for i, l in enumerate(H):
        for p in l:
            incid_pt.setdefault(p, []).append((i, p))
    moves = [incid_line[i] for i in incid_line] + [incid_pt[p] for p in incid_pt]
    for _ in range(rounds):
        mv = r.choice(moves)
        nxt = cur ^ set(mv)
        c = decoration_cost(H, nxt)
        if c <= best:
            cur, best = nxt, c
    return sorted(cur), best


def min_signing(H, negs):
    """a signing with the fewest negated incidences in the switching class of negs (MaxSAT over point and line switches): (negs, count)"""
    from pysat.examples.rc2 import RC2
    from pysat.formula import WCNF
    neg = set(map(tuple, negs))
    n = 1 + max(max(l) for l in H)
    w = WCNF()
    for i, l in enumerate(H):
        for p in l:
            a, b = p + 1, n + i + 1
            if (i, p) in neg:
                w.append([a, b], weight=1)
                w.append([-a, -b], weight=1)
            else:
                w.append([-a, b], weight=1)
                w.append([a, -b], weight=1)
    with RC2(w) as rc:
        model = rc.compute()
        cost = rc.cost
    on = {v for v in model if v > 0}
    out = []
    for i, l in enumerate(H):
        for p in l:
            flip = ((p + 1) in on) != ((n + i + 1) in on)
            if ((i, p) in neg) != flip:
                out.append((i, p))
    return sorted(out), cost


def edge_atoms(H, negs):
    """a plain system: a Fano atom on every negated incidence (i, p), as in KNOT-COUPLING-20261031-001A (the Fano plane with one incidence
    of its root line moved onto the edge: line i holds the atom's point r0 instead of p, and the root line holds r1, r2 and p). At the
    knot's law the atom is an exact negation, so the result is a plain three-fold space iff (H, negs) is not colourable."""
    import threefold_lib as T
    out = [list(l) for l in H]
    n = 1 + max(max(l) for l in H)
    root = T.FANO[0]
    others = [l for l in T.FANO if l != root]
    for i, p in negs:
        r = list(range(n, n + 7))
        n += 7
        out[i][out[i].index(p)] = r[root[0]]
        out.append([r[root[1]], r[root[2]], p])
        for l in others:
            out.append([r[q] for q in l])
    return [tuple(l) for l in out]
