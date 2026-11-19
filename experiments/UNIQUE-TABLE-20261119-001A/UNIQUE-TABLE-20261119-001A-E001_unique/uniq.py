"""UNIQUE-TABLE-20261119-001A: is a census arrangement the only legal arrangement with its exact bond-distance table?

An arrangement is a graph G on the distinctions (its edges): one vertex per junction and one outside vertex o ending every loose
distinction.  The junction stars span the cut space C; the table T(p) for a pair p of edges is (smallest bond, i.e. circuit of C,
containing both) - 1, computed exactly (`exact_table_v2.py`, every side; at these sizes every connected side is visited).

Per stage:
- forcing: for a pair p with T(p) = d and d + 1 <= K (the largest junction), the possible circuits of size d + 1 through p in any
  code with table T are the (d + 1)-sets containing p all of whose pairs have T <= d; if there is exactly one, it lies in every such
  code.  F = span of the forced sets.  forced_spans_C: F = C.
- same code, other junctions: every graph 2-isomorphic to G (closure of G under Whitney twists at 2-vertex separations) with every
  choice of outside vertex; those that are legal (every junction of at least 3 distinctions, any two sharing at most one, no cut
  vertex) and differ from G are arrangements with the same allowed states and so the same table.
"""
import sys
from collections import Counter, deque
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS = ROOT / 'experiments/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census'
sys.setrecursionlimit(100000)
sys.path.insert(0, str(CENSUS))
import job as CJ  # noqa: E402  (census growth, and through it RING-READ's ringread)
import exact_table_v2 as X  # noqa: E402
R, S, F, A = CJ.R, CJ.S, CJ.F, CJ.A


def stage(key, rnd):
    P = S.from_junctions(A.stars_of((tuple(key[0]), tuple(key[1]))))
    for _ in range(rnd):
        P.step(S.gf2(F.fewest), None)
    return [frozenset(b) for b in P.bits_of]


def full_table(stars):
    n_bits = len(R.owners(stars))
    return X.exact_table(stars, n_bits)


def word(s):
    return sum(1 << b for b in s)


def rank(words):
    basis = {}
    for w in words:
        R.add_row(w, basis)
    return len(basis), basis


def cliques(table, labels, s):
    """All s-sets of distinctions whose every pair has T <= s - 1."""
    nb = {x: set() for x in labels}
    for (a, b), d in table.items():
        if d <= s - 1:
            nb[a].add(b)
            nb[b].add(a)
    out = []

    def ext(cl, pool):
        if len(cl) == s:
            out.append(frozenset(cl))
            return
        for v in sorted(pool):
            if cl and v < max(cl):
                continue
            ext(cl | {v}, pool & nb[v])
    for x in labels:
        ext(frozenset([x]), nb[x])
    return out


def min_circuit(table, labels):
    """m(e) = 1 + min over f of T(e, f): the smallest circuit through e in any code with table T."""
    m = {x: 10 ** 9 for x in labels}
    for (a, b), d in table.items():
        m[a] = min(m[a], d + 1)
        m[b] = min(m[b], d + 1)
    return m


def span_words(words):
    sp = {0}
    for w in words:
        if w not in sp:
            sp |= {x ^ w for x in sp}
    return sp


def light(words_span, m, labels):
    """Does some word of the span hold an edge e while weighing less than m(e)?"""
    for w in words_span:
        if not w:
            continue
        k = w.bit_count()
        x = w
        while x:
            low = x & -x
            if k < m[low.bit_length() - 1]:
                return True
            x ^= low
    return False


def forcing(stars, table, max_rounds=20):
    """Forcing with elimination: a candidate circuit S for pair p is dropped when it strictly contains a forced word, or when
    span(F, S) holds a word lighter than m(e) at one of its edges (both impossible in a code with table T).  A pair left with a
    single candidate forces it.  Repeated to a fixed point."""
    labels = sorted(R.owners(stars))
    K = max(map(len, stars))
    m = min_circuit(table, labels)
    by_size = {s: cliques(table, labels, s) for s in range(3, K + 1)}
    containing = {}
    for s, cl in by_size.items():
        for c in cl:
            for p in combinations(sorted(c), 2):
                containing.setdefault((s, p), []).append(c)
    pairs = [(p, d + 1) for p, d in table.items() if 3 <= d + 1 <= K]
    forced, dead = set(), set()
    rounds = 0
    while rounds < max_rounds:
        rounds += 1
        Fspan = span_words([word(c) for c in forced])
        new = set()
        for p, s in pairs:
            alive = []
            for c in containing.get((s, p), []):
                if c in dead:
                    continue
                if c not in forced:
                    w = word(c)
                    if any(f != w and (f & w) == f for f in (word(x) for x in forced)) or \
                            light({x ^ w for x in Fspan}, m, labels):
                        dead.add(c)
                        continue
                alive.append(c)
            if len(alive) == 1 and alive[0] not in forced:
                new.add(alive[0])
        if not new:
            break
        forced |= new
    rC, _ = rank([word(s) for s in stars])
    rF, _ = rank([word(s) for s in forced])
    rFC, _ = rank([word(s) for s in forced] + [word(s) for s in stars])
    return {'forced': forced, 'rank_C': rC, 'rank_F': rF, 'F_within_C': rFC == rC, 'forced_spans_C': rF == rC and rFC == rC,
            'rounds': rounds, 'eliminated': len(dead), 'cliques_by_size': {s: len(c) for s, c in by_size.items()}}


def coset_test(stars, table):
    """Is there a coset S + C (S not in C) none of whose words is lighter than m(e) at one of its edges, and holding a
    representative of at least 3 distinctions all of whose pairs have T <= |S| - 1?  If not, no rival code strictly contains C.
    Exhaustive over the 2^(N - r) cosets."""
    labels = sorted(R.owners(stars))
    idx = {b: i for i, b in enumerate(labels)}
    N = len(labels)
    m = [None] * N
    mm = min_circuit(table, labels)
    for b in labels:
        m[idx[b]] = mm[b]
    Cw = sorted(span_words([sum(1 << idx[b] for b in s) for s in stars]))
    r, basis = rank([sum(1 << idx[b] for b in s) for s in stars])
    pivots = set(basis)
    free = [i for i in range(N) if i not in pivots]   # coset representatives: words on the non-pivot positions
    T = {}
    for (a, b), d in table.items():
        T[(idx[a], idx[b])] = d
        T[(idx[b], idx[a])] = d

    def ok_word(w):
        k = w.bit_count()
        x = w
        while x:
            low = x & -x
            if k < m[low.bit_length() - 1]:
                return False
            x ^= low
        return True

    def clique_at_size(w):
        bits = [i for i in range(N) if w >> i & 1]
        k = len(bits)
        return k >= 3 and all(T[(a, b)] <= k - 1 for a, b in combinations(bits, 2))
    passing = []
    for mask in range(1, 1 << len(free)):
        v = 0
        for j, i in enumerate(free):
            if mask >> j & 1:
                v |= 1 << i
        words = [v ^ c for c in Cw]
        if all(ok_word(w) for w in words) and any(clique_at_size(w) for w in words):
            passing.append(v)
    return {'cosets': (1 << len(free)) - 1, 'passing_cosets': len(passing)}


# -- the graph and its Whitney class ---------------------------------------------------------------------------------------------

def graph_of(stars):
    """Edge -> (endpoint, endpoint) with vertices 0..n-1 the junctions and n the outside vertex."""
    n = len(stars)
    own = R.owners(stars)
    return {b: (js[0], js[1]) if len(js) == 2 else (js[0], n) for b, js in own.items()}, n + 1


def stars_of_graph(edges, nv):
    st = [set() for _ in range(nv)]
    for e, (u, v) in edges.items():
        st[u].add(e)
        st[v].add(e)
    return [frozenset(s) for s in st]


def components(edges, nv, removed):
    adj = {v: set() for v in range(nv) if v not in removed}
    for e, (u, v) in edges.items():
        if u in adj and v in adj:
            adj[u].add(v)
            adj[v].add(u)
    seen, comps = set(), []
    for v in adj:
        if v in seen:
            continue
        comp, stack = {v}, [v]
        seen.add(v)
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    comp.add(y)
                    stack.append(y)
        comps.append(comp)
    return comps


def twists(edges, nv):
    """Graphs obtained by one Whitney twist at a 2-vertex separation {u, v}: exchange u and v on the edges joining them to a
    proper nonempty union of the components of G - {u, v}."""
    out = []
    for u, v in combinations(range(nv), 2):
        comps = components(edges, nv, {u, v})
        if len(comps) < 2:
            continue
        for k in range(1, len(comps)):
            for side in combinations(range(len(comps)), k):
                inside = set().union(*(comps[i] for i in side))
                new = {}
                for e, (a, b) in edges.items():
                    ends = [a, b]
                    other = b if a in (u, v) else a
                    if (a in (u, v)) != (b in (u, v)) and other in inside:
                        ends = [{u: v, v: u}.get(x, x) for x in ends]
                    new[e] = (ends[0], ends[1])
                out.append(new)
    return out


def whitney_class(stars, limit=5000):
    edges, nv = graph_of(stars)
    key = lambda E: frozenset(s for s in stars_of_graph(E, nv) if s)  # noqa: E731  the vertex stars, unlabelled
    seen = {key(edges): edges}
    queue = deque([edges])
    while queue and len(seen) < limit:
        E = queue.popleft()
        for E2 in twists(E, nv):
            k = key(E2)
            if k not in seen:
                seen[k] = E2
                queue.append(E2)
    return list(seen.values()), nv, len(seen) >= limit


def legal(junctions, all_bits):
    cover = Counter(b for s in junctions for b in s)
    if any(cover[b] not in (1, 2) for b in all_bits) or any(len(s) < 3 for s in junctions):
        return False
    for a, b in combinations(junctions, 2):
        if len(a & b) > 1:
            return False
    return True


def no_cut_vertex(edges, nv):
    """With the outside vertex left out when it ends nothing."""
    used = {x for e in edges.values() for x in e}
    vs = [v for v in range(nv) if v in used]
    for v in vs:
        if len(components({e: uv for e, uv in edges.items() if v not in uv}, nv, {v} | (set(range(nv)) - set(vs)))) > 1:
            return False
    return True


def blocks_of(edges, nv):
    """Blocks (2-connected pieces, bridges included) of the graph, as lists of edges, with the outside vertex dropped when
    it ends nothing."""
    import networkx as nx
    G = nx.MultiGraph()
    for e, (u, v) in edges.items():
        G.add_edge(u, v, key=e)
    simple = nx.Graph(G)
    out = []
    for comp in nx.biconnected_components(simple):
        es = [e for e, (u, v) in edges.items() if u in comp and v in comp]
        out.append((set(comp), es))
    return out


def cut_vertices(edges):
    import networkx as nx
    G = nx.Graph()
    for e, (u, v) in edges.items():
        G.add_edge(u, v)
    return set(nx.articulation_points(G))


def same_code_rivals(stars, limit=20000):
    """Every legal arrangement other than the truth whose junctions span the same equations.  Legal: every junction of at least
    3 distinctions, any two sharing at most one, and no cut vertex but the outside one.  By Whitney's theorem the graphs with
    the same cut space are the truth's blocks, each twisted within its Whitney class and re-glued at one vertex; legality makes
    the glue vertex the outside vertex, so each block picks its outside vertex (or none, when there is a single block)."""
    truth = frozenset(stars)
    bits = sorted(R.owners(stars))
    edges, nv = graph_of(stars)
    o = nv - 1
    if not any(o in uv for uv in edges.values()):
        pass  # closed: the outside vertex ends nothing and is ignored below
    blocks = blocks_of(edges, nv)
    options = []
    capped = False
    for verts, es in blocks:
        sub = {e: edges[e] for e in es}
        sub_stars = [frozenset(e for e in es if v in edges[e]) for v in sorted(verts)]
        # Whitney class of the block, as graphs on its own vertices
        seen = {}
        start = sub
        key = lambda E: frozenset(frozenset(e for e, uv in E.items() if v in uv) for v in verts)  # noqa: E731
        seen[key(start)] = start
        queue = deque([start])
        while queue and len(seen) < limit:
            E = queue.popleft()
            for E2 in twists_on(E, verts):
                k = key(E2)
                if k not in seen:
                    seen[k] = E2
                    queue.append(E2)
        capped |= len(seen) >= limit
        opts = []
        for E in seen.values():
            st = {v: frozenset(e for e, uv in E.items() if v in uv) for v in verts}
            for w in sorted(verts) + ([None] if len(blocks) == 1 else []):
                opts.append(frozenset(s for v, s in st.items() if v != w and s))
        options.append(opts)
    rivals = set()
    total = 1
    for opts in options:
        total *= len(opts)
    if total > limit * 10:
        return rivals, total, True
    def rec(i, acc):
        if i == len(options):
            junctions = frozenset(acc)
            if junctions != truth and legal(junctions, bits):
                rivals.add(junctions)
            return
        for opt in options[i]:
            rec(i + 1, acc | opt)
    rec(0, frozenset())
    return rivals, total, capped


def twists_on(edges, verts):
    """One Whitney twist at a 2-vertex separation {u, v} of the block on vertices verts."""
    out = []
    vs = sorted(verts)
    nvmax = max(vs) + 1
    for u, v in combinations(vs, 2):
        comps = [c for c in components(edges, nvmax, {u, v} | (set(range(nvmax)) - set(vs)))]
        if len(comps) < 2:
            continue
        for k in range(1, len(comps)):
            for side in combinations(range(len(comps)), k):
                inside = set().union(*(comps[i] for i in side))
                new = {}
                for e, (a, b) in edges.items():
                    ends = [a, b]
                    other = b if a in (u, v) else a
                    if (a in (u, v)) != (b in (u, v)) and other in inside:
                        ends = [{u: v, v: u}.get(x, x) for x in ends]
                    new[e] = (ends[0], ends[1])
                out.append(new)
    return out


def check_rival(rival, table, C_words):
    """A found rival is verified directly: legal, its own exact table equals T, and whether its equations equal the truth's."""
    rt = full_table(sorted(rival, key=sorted))
    same_table = rt == table
    r1, _ = rank(C_words)
    r2, _ = rank(C_words + [word(s) for s in rival])
    r3, _ = rank([word(s) for s in rival])
    return {'same_table': same_table, 'same_states': r1 == r2 == r3}


def one_missing(stars, table, forced, cap=1 << 16):
    """When the forced equations F have rank n - 1 (n = number of true junctions): every code of rank n containing F is
    F + <S>; test every coset S + F (S not in F) for a code whose exact table equals T, and report those different from C."""
    labels = sorted(R.owners(stars))
    idx = {b: i for i, b in enumerate(labels)}
    N = len(labels)
    Fw = [sum(1 << idx[b] for b in s) for s in forced]
    rF, basis = rank(Fw)
    Cw = [sum(1 << idx[b] for b in s) for s in stars]
    rC, _ = rank(Cw)
    if rF != rC - 1:
        return {'applicable': False}
    free = [i for i in range(N) if i not in basis]
    if (1 << len(free)) > cap:
        return {'applicable': True, 'capped': True, 'cosets': 1 << len(free)}
    target = {(idx[a], idx[b]): d for (a, b), d in table.items()}
    target.update({(j, i): d for (i, j), d in list(target.items())})
    Cspan = span_words(Cw)
    hits, same = 0, 0
    for mask in range(1, 1 << len(free)):
        v = 0
        for j, i in enumerate(free):
            if mask >> j & 1:
                v |= 1 << i
        code = span_words(Fw + [v])
        if code_table_matches(code, target, N):
            if code == Cspan:
                same += 1
            else:
                hits += 1
    return {'applicable': True, 'capped': False, 'cosets': (1 << len(free)) - 1, 'codes_matching_other_than_C': hits,
            'cosets_giving_C': same}


def code_table_matches(code, target, N):
    """Pair minima over the circuits (minimal nonzero words) of a code, compared with the target table."""
    words = sorted((w for w in code if w), key=lambda w: (w.bit_count(), w))
    minimal = []
    best = {}
    for w in words:
        if any((w & c) == c for c in minimal):
            continue
        minimal.append(w)
        bits = [i for i in range(N) if w >> i & 1]
        k = len(bits) - 1
        for a, b in combinations(bits, 2):
            if (a, b) not in best:
                best[(a, b)] = k
                if target[(a, b)] < k:
                    return False      # the target's minimum is smaller than any circuit can now give? keep checking below
                if target[(a, b)] != k:
                    return False
    return all(best.get((a, b)) == target[(a, b)] for a in range(N) for b in range(a + 1, N))
