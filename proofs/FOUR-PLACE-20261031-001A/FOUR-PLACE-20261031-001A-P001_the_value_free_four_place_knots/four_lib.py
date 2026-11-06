"""Value-free laws on four places (FOUR-PLACE-20261031-001A): shared library.

A four-place relation is a frozenset of states in {0,1}^4. It is value-free when it is unchanged by complementing all four places (a
union of antipodal pairs), and a knot when it is neither empty nor full and every three-place projection is full (K1-K3). A signed law
is the orbit of a relation under flips and permutations of the places. A 4-regular 4-uniform system is a list of lines, each a 4-tuple
of distinct points, with every point on exactly four lines. A piece has internal points (four incidences) and four ports (one incidence
each); its accepted relation is the set of port assignments that extend to a solution."""
import itertools

import networkx as nx

H4 = tuple(itertools.product((0, 1), repeat=4))
ZERO, ONE = (0, 0, 0, 0), (1, 1, 1, 1)


def flip(R, f):
    return frozenset(tuple(s[i] ^ f[i] for i in range(4)) for s in R)


def permute(R, p):
    return frozenset(tuple(s[p[i]] for i in range(4)) for s in R)


def orbit(R):
    return {flip(permute(R, p), f) for p in itertools.permutations(range(4)) for f in H4}


def canonical(R):
    return min(orbit(R), key=lambda S: (len(S), sorted(S)))


def complement(R):
    return frozenset(tuple(1 - x for x in s) for s in R)


def is_knot(R):
    R = frozenset(R)
    return 0 < len(R) < 16 and all(len({tuple(s[j] for j in range(4) if j != d) for s in R}) == 8 for d in range(4))


def value_free_knots():
    pairs, seen = [], set()
    for v in H4:
        if v not in seen:
            w = tuple(1 - x for x in v)
            pairs.append((v, w))
            seen |= {v, w}
    rels = [frozenset(s for i, pr in enumerate(pairs) if m >> i & 1 for s in pr) for m in range(1, 1 << len(pairs))]
    return [R for R in rels if is_knot(R)]


NAMES = {8: "parity", 10: "not-exactly-two", 12: "twelve", 14: "not-all-equal"}


def classes():
    out = {}
    for R in value_free_knots():
        out.setdefault(canonical(R), []).append(R)
    return {NAMES[len(c)]: sorted(m, key=sorted) for c, m in sorted(out.items(), key=lambda kv: len(kv[0]))}


# ------------------------------------------------------------------------------------------------ Schaefer polymorphisms
def closed(rels, op, arity):
    return all(tuple(op(*col) for col in zip(*states)) in R for R in rels for states in itertools.product(sorted(R), repeat=arity))


SCHAEFER = {
    "0-valid": lambda rels: all(ZERO in R for R in rels),
    "1-valid": lambda rels: all(ONE in R for R in rels),
    "Horn (and)": lambda rels: closed(rels, lambda a, b: a & b, 2),
    "dual Horn (or)": lambda rels: closed(rels, lambda a, b: a | b, 2),
    "bijunctive (majority)": lambda rels: closed(rels, lambda a, b, c: (a & b) | (a & c) | (b & c), 3),
    "affine (minority)": lambda rels: closed(rels, lambda a, b, c: a ^ b ^ c, 3),
}


def schaefer_classes(rels):
    return [name for name, test in SCHAEFER.items() if test(rels)]


# ------------------------------------------------------------------------------------------------ 4-regular 4-uniform systems
def complement_system(n, edges):
    """the 4-regular system on n points whose incidence graph is K_{n,n} minus the given (n-4)-regular bipartite edge set"""
    return [tuple(p for p in range(n) if (p, l) not in edges) for l in range(n)]


def systems(n, cubic_census=None):
    """every 4-regular 4-uniform system with n points (4 <= n <= 7), up to isomorphism, as complements in K_{n,n} of (n-4)-regular
    bipartite graphs: n = 6 from the even cycle covers of K_{6,6}, n = 7 from the cubic bipartite graphs on 7 + 7 vertices (the
    connected ones from the census, and K_{3,3} plus the cube)"""
    if n == 4:
        return [complement_system(4, set())]
    if n == 5:
        return [complement_system(5, {(i, i) for i in range(5)})]
    if n == 6:
        out = []
        for parts in ([12], [8, 4], [6, 6], [4, 4, 4]):
            edges, p0 = set(), 0
            for length in parts:
                h = length // 2                          # cycle p_0 l_0 p_1 l_1 ... on h points and h lines
                for i in range(h):
                    edges |= {(p0 + i, p0 + i), (p0 + (i + 1) % h, p0 + i)}
                p0 += h
            out.append(complement_system(6, edges))
        return out
    if n == 7:
        cubics = [[tuple(l) for l in row["lines"]] for row in cubic_census["7"]["rows"]]
        k33 = [(0, 1, 2)] * 3
        cube = [(4, 5, 6), (3, 5, 6), (3, 4, 6), (3, 4, 5)]
        cubics.append(k33 + cube)
        return [complement_system(7, {(p, l) for l, L in enumerate(C) for p in L}) for C in cubics]
    raise ValueError(n)


def incidence_graph(lines):
    g = nx.Graph()
    for i, L in enumerate(lines):
        for p in L:
            g.add_edge(("l", i), ("p", p))
    return g


def is_regular_system(lines, k=4):
    n = 1 + max(max(L) for L in lines)
    deg = [0] * n
    for L in lines:
        for p in L:
            deg[p] += 1
    return len(lines) == n and all(d == k for d in deg) and all(len(set(L)) == k for L in lines)


# ------------------------------------------------------------------------------------------------ solvability on small systems
def line_mask(L, npts, R):
    m = 0
    for a in range(1 << npts):
        if tuple(a >> p & 1 for p in L) in R:
            m |= 1 << a
    return m


def failing_count(lines, members, stop_at_first=False):
    """number of choices of one member relation per line (in the line's order) that leave no solution"""
    n = 1 + max(max(L) for L in lines)
    per_line = [[line_mask(L, n, R) for R in members] for L in lines]
    full = (1 << (1 << n)) - 1
    fail = total = 0

    def dfs(i, acc):
        nonlocal fail, total
        if stop_at_first and fail:
            return
        if i == len(lines):
            total += 1
            fail += acc == 0
            return
        for m in per_line[i]:
            dfs(i + 1, acc & m)
    dfs(0, full)
    return fail, total


# ------------------------------------------------------------------------------------------------ pieces
def structures(k, norep=False):
    """line sets on internal points 0..k-1 (four incidences each) and ports k..k+3 (one each), k + 1 lines of four distinct points,
    up to renaming internal points and ports"""
    allsets = list(itertools.combinations(range(k + 4), 4))
    out, seen = [], set()

    def key(lines):
        best = None
        for pi in itertools.permutations(range(k)):
            for pp in itertools.permutations(range(k, k + 4)):
                mp = list(pi) + list(pp)
                kk = tuple(sorted(tuple(sorted(mp[p] for p in L)) for L in lines))
                if best is None or kk < best:
                    best = kk
        return best

    def rec(i, start, deg, chosen):
        if i == k + 1:
            if all(deg[p] == 4 for p in range(k)) and all(deg[p] == 1 for p in range(k, k + 4)):
                kk = key(chosen)
                if kk not in seen:
                    seen.add(kk)
                    out.append(list(chosen))
            return
        for j in range(start, len(allsets)):
            L = allsets[j]
            if any(deg[p] + 1 > (4 if p < k else 1) for p in L) or (norep and L in chosen):
                continue
            for p in L:
                deg[p] += 1
            chosen.append(L)
            rec(i + 1, j, deg, chosen)
            chosen.pop()
            for p in L:
                deg[p] -= 1
    rec(0, 0, [0] * (k + 4), [])
    return out


def port_relation(acc, k):
    """port assignments (bits = ports k..k+3) extendable within the accepted full-assignment mask"""
    out = set()
    a = 0
    while acc:
        if acc & 1:
            out.add(tuple(a >> p & 1 for p in range(k, k + 4)))
        acc >>= 1
        a += 1
    return frozenset(out)


def accepted_relations(lines, k, members):
    """{accepted port relation: one choice of member relations per line producing it}"""
    npts = k + 4
    per_line = [[(line_mask(L, npts, R), R) for R in members] for L in lines]
    found = {}

    def dfs(i, acc, choice):
        if acc == 0:
            return
        if i == len(lines):
            rel = port_relation(acc, k)
            found.setdefault(rel, list(choice))
            return
        for m, R in per_line[i]:
            choice.append(R)
            dfs(i + 1, acc & m, choice)
            choice.pop()
    dfs(0, (1 << (1 << npts)) - 1, [])
    return found


def link_form(rel):
    """('=' or '!=', (a, b), (c, d)) if rel = (port a rel port b) x {0,1}^2 on the other two ports, else None"""
    for a, b in itertools.combinations(range(4), 2):
        c, d = [j for j in range(4) if j not in (a, b)]
        for kind, ok in (("=", lambda x, y: x == y), ("!=", lambda x, y: x != y)):
            target = frozenset(s for s in H4 if ok(s[a], s[b]))
            if rel == target:
                return kind, (a, b), (c, d)
    return None


# ------------------------------------------------------------------------------------------------ satisfiability and regularization
def cnf(lines, rels, nvars):
    clauses = []
    for L, R in zip(lines, rels):
        for s in H4:
            if s not in R:
                clauses.append([(-(p + 1) if s[j] else (p + 1)) for j, p in enumerate(L)])
    return clauses


def sat(lines, rels):
    from pysat.solvers import Minisat22
    n = 1 + max(max(L) for L in lines)
    with Minisat22(bootstrap_with=cnf(lines, rels, n)) as s:
        return s.solve()


def flip_place(R, j):
    return frozenset(tuple(x ^ (i == j) for i, x in enumerate(s)) for s in R)


def regularize(nvars, constraints, piece):
    """constraints: list of (4 distinct variables, relation); piece: (lines over internal 0..4 and ports 5..8, relations, kind, (a, b),
    (c, d)) with accepted relation (port a kind port b) x {0,1}^2. Returns (lines, relations) of a 4-regular 4-uniform system that is
    solvable iff the instance is. kind '=' : copies equal around a cycle; '!=' : copies alternate around an even cycle."""
    plines, prels, kind, (pa, pb), (pc, pd) = piece
    occ = {x: [] for x in range(nvars)}
    for ci, (vs, R) in enumerate(constraints):
        for j, x in enumerate(vs):
            occ[x].append((ci, j))
    lines, rels, nxt = [], [], 0
    copies = {}
    for x in range(nvars):
        d = len(occ[x])
        if d == 0:
            continue
        m = max(d, 2)
        if kind == "!=" and m % 2:
            m += 1
        copies[x] = list(range(nxt, nxt + m))
        nxt += m
    cons_lines = []
    for ci, (vs, R) in enumerate(constraints):
        cons_lines.append([None] * 4)
    spare = {}
    for x, cs in copies.items():
        for i, (ci, j) in enumerate(occ[x]):
            cons_lines[ci][j] = (cs[i], i % 2 if kind == "!=" else 0)
        for i, c in enumerate(cs):
            spare[c] = 2 - (1 if i < len(occ[x]) else 0)        # 4 incidences = 2 link ports + original + spares
    for ci, (vs, R) in enumerate(constraints):
        pts = [cons_lines[ci][j][0] for j in range(4)]
        RR = R
        for j in range(4):
            if cons_lines[ci][j][1]:
                RR = flip_place(RR, j)                           # this copy carries the complement of the variable
        lines.append(tuple(pts))
        rels.append(RR)
    free_ports = []                                             # (line index, position) awaiting a point
    for x, cs in copies.items():
        m = len(cs)
        for i in range(m):
            base = nxt
            nxt += 5                                            # five internal points of this piece copy
            mp = {q: base + q for q in range(5)}
            mp[5 + pa], mp[5 + pb] = cs[i], cs[(i + 1) % m]
            for L, R in zip(plines, prels):
                idx = len(lines)
                pts = []
                for pos, q in enumerate(L):
                    if q in (5 + pc, 5 + pd):
                        pts.append(None)
                        free_ports.append((idx, pos))
                    else:
                        pts.append(mp[q])
                lines.append(pts)
                rels.append(R)
    # free ports: first the copies' spare incidences, then absorber points, four ports each
    targets = [c for c in sorted(spare) for _ in range(spare[c])]
    assert len(free_ports) >= len(targets) and (len(free_ports) - len(targets)) % 4 == 0
    unused = list(free_ports)
    for c in targets:                                           # never put a point twice on one line
        k = next(i for i, (idx, pos) in enumerate(unused) if c not in lines[idx])
        idx, pos = unused.pop(k)
        lines[idx][pos] = c
    rest = sorted(unused)                                       # absorbers take ports with stride len/4, from distinct lines
    G = len(rest) // 4
    for g in range(G):
        for idx, pos in rest[g::G]:
            lines[idx][pos] = nxt
        nxt += 1
    return [tuple(L) for L in lines], rels


# ------------------------------------------------------------------------------------------------ sign-nonsingular signings
def permanent01(rows, n):
    """number of perfect matchings (Ryser) of an n x n 0/1 matrix given as row bitmasks"""
    total = 0
    for S in range(1, 1 << n):
        prod = 1
        for r in rows:
            c = bin(r & S).count("1")
            if c == 0:
                prod = 0
                break
            prod *= c
        total += (-1) ** (n - bin(S).count("1")) * prod
    return total


def det_int(M):
    """exact integer determinant (Bareiss)"""
    M = [row[:] for row in M]
    n, sign, prev = len(M), 1, 1
    for k in range(n - 1):
        if M[k][k] == 0:
            sw = next((i for i in range(k + 1, n) if M[i][k] != 0), None)
            if sw is None:
                return 0
            M[k], M[sw] = M[sw], M[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) // prev
        prev = M[k][k]
    return sign * M[n - 1][n - 1]


def sns_signing_exists(lines):
    """does some +-1 signing of the incidence matrix have |det| = number of perfect matchings? Signs on a spanning forest are fixed
    to +1 (row and column sign changes preserve |det|), the remaining incidences range over all signs"""
    n = len(lines)
    edges = [(l, p) for l, L in enumerate(lines) for p in L]
    g = nx.Graph()
    g.add_edges_from((("l", l), ("p", p)) for l, p in edges)
    forest = {tuple(sorted(e)) for e in nx.minimum_spanning_edges(g, data=False)}
    free = [(l, p) for l, p in edges if tuple(sorted((("l", l), ("p", p)))) not in forest]
    per = permanent01([sum(1 << p for p in L) for L in lines], n)
    for signs in itertools.product((1, -1), repeat=len(free)):
        M = [[0] * n for _ in range(n)]
        for l, p in edges:
            M[l][p] = 1
        for (l, p), s in zip(free, signs):
            M[l][p] = s
        if abs(det_int(M)) == per:
            return True, per
    return False, per
