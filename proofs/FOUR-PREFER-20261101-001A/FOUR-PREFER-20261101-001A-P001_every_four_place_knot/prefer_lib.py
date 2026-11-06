"""Four-place laws that prefer a value (FOUR-PREFER-20261101-001A): shared library.

Builds on four_lib (FOUR-PLACE-20261031-001A, bound by hash). Classes are numbered by sorting their canonical relations by (number of
states, sorted states); class 0 is parity, 3 not-exactly-two, 11 twelve, 18 not-all-equal, 19 the clause. A piece has internal points
0..k-1 (four incidences each) and ports k..k+3 (one incidence each); its accepted relation lists port assignments in port order."""
import itertools
import sys
from pathlib import Path

import networkx as nx

FOUR_A = Path(__file__).resolve().parents[2] / "FOUR-PLACE-20261031-001A/FOUR-PLACE-20261031-001A-P001_the_value_free_four_place_knots"
sys.path.insert(0, str(FOUR_A))
import four_lib as F  # noqa: E402

H4 = F.H4


def all_knots():
    out = []
    for m in range(1, 1 << 16):
        R = frozenset(s for i, s in enumerate(H4) if m >> i & 1)
        if F.is_knot(R):
            out.append(R)
    return out


def classes():
    """list of (canonical relation, sorted members), in the fixed order"""
    cls = {}
    for R in all_knots():
        cls.setdefault(F.canonical(R), []).append(R)
    return [(c, sorted(m, key=sorted)) for c, m in sorted(cls.items(), key=lambda kv: (len(kv[0]), sorted(kv[0])))]


def class_index(R, CL):
    c = F.canonical(R)
    return next(i for i, (cc, _) in enumerate(CL) if cc == c)


def forcing_places(R):
    """places j with a value v such that every state with x_j = v is allowed"""
    return [j for j in range(4) if any(all(s in R for s in H4 if s[j] == v) for v in (0, 1))]


# ------------------------------------------------------------------------------------------------ the clause (Tovey's argument)
def matching_solution(lines, rels):
    """a perfect matching of lines to points (Hall, 4-regular), each matched point set to a forcing value of its line"""
    n = len(lines)
    g = nx.Graph()
    g.add_nodes_from([("l", i) for i in range(n)] + [("p", p) for p in range(n)])
    g.add_edges_from((("l", i), ("p", p)) for i, L in enumerate(lines) for p in L)
    M = nx.bipartite.maximum_matching(g, top_nodes=[("l", i) for i in range(n)])
    col = [0] * n
    for i, (L, R) in enumerate(zip(lines, rels)):
        p = M[("l", i)][1]
        j = L.index(p)
        col[p] = next(v for v in (0, 1) if all(s in R for s in H4 if s[j] == v))
    return col


def satisfies(lines, rels, col):
    return all(tuple(col[p] for p in L) in R for L, R in zip(lines, rels))


# ------------------------------------------------------------------------------------------------ SAT helpers
def accepted_by_sat(lines, rels, k):
    """accepted port relation of a piece (ports k..k+3) by one SAT call per port assignment"""
    from pysat.solvers import Minisat22
    n = 1 + max(max(L) for L in lines)
    base = F.cnf(lines, rels, n)
    out = set()
    for s in H4:
        units = [[(k + j + 1) if s[j] else -(k + j + 1)] for j in range(4)]
        with Minisat22(bootstrap_with=base + units) as S:
            if S.solve():
                out.add(s)
    return frozenset(out)


# ------------------------------------------------------------------------------------------------ realizations and lifting
THREE_POINT = [(0, 1, 2, 3), (0, 1, 2, 4), (0, 1, 2, 5), (0, 1, 2, 6)]     # the only piece shape with three internal points


def realization_of_class(members, target_class_canonical):
    """a choice of member relations on THREE_POINT whose accepted relation lies in the target class, or None"""
    k = 3
    npts = k + 4
    per_line = [[(F.line_mask(L, npts, R), R) for R in members] for L in THREE_POINT]

    def dfs(i, acc, choice):
        if acc == 0:
            return None
        if i == 4:
            rel = F.port_relation(acc, k)
            return (list(choice), rel) if F.is_knot(rel) and F.canonical(rel) == target_class_canonical else None
        for m, R in per_line[i]:
            choice.append(R)
            got = dfs(i + 1, acc & m, choice)
            choice.pop()
            if got:
                return got
        return None
    return dfs(0, (1 << (1 << npts)) - 1, [])


def adapt(piece_lines, piece_rels, k, rel, target):
    """flip and permute the ports of a piece with accepted relation rel so that it accepts target (same class)"""
    for perm in itertools.permutations(range(4)):
        for f in H4:
            if F.flip(F.permute(rel, perm), f) == target:
                # new port i = old port perm[i]; then flip new port i where f[i] = 1
                relab = {k + perm[i]: k + i for i in range(4)}
                lines = [tuple(relab.get(p, p) for p in L) for L in piece_lines]
                rels = []
                for L, R in zip(lines, piece_rels):
                    for pos, p in enumerate(L):
                        if p >= k and f[p - k]:
                            R = F.flip(R, tuple(int(t == pos) for t in range(4)))
                    rels.append(R)
                return lines, rels
    return None


def lift(link_lines, link_rels, k_link, realizations):
    """replace every line of a link piece (internal 0..k_link-1, ports k_link..k_link+3) by a three-point piece accepting that line's
    relation; returns the lifted piece with internal points first and the same four ports last"""
    pts = {}
    order = list(range(k_link))
    nxt = 0
    for p in order:
        pts[("L", p)] = nxt
        nxt += 1
    lines, rels = [], []
    for li, (L, R) in enumerate(zip(link_lines, link_rels)):
        qlines, qrels = realizations[R]
        for q in range(3):
            pts[("Q", li, q)] = nxt
            nxt += 1
        for QL, QR in zip(qlines, qrels):
            out = []
            for q in QL:
                if q < 3:
                    out.append(("Q", li, q))
                else:
                    out.append(("L", L[q - 3]))
            lines.append(out)
            rels.append(QR)
    k_new = nxt
    for j in range(4):
        pts[("L", k_link + j)] = k_new + j
    return [tuple(pts[x] for x in L) for L in lines], rels, k_new


# ------------------------------------------------------------------------------------------------ regularization for any link piece
def regularize(nvars, constraints, piece):
    """as four_lib.regularize, for a link piece with any number k of internal points: piece = (lines over internal 0..k-1 and ports
    k..k+3, relations, k, kind, (a, b), (c, d)) with accepted relation (port a kind port b) x {0,1}^2 and free ports on different lines"""
    plines, prels, k, kind, (pa, pb), (pc, pd) = piece
    occ = {x: [] for x in range(nvars)}
    for ci, (vs, R) in enumerate(constraints):
        for j, x in enumerate(vs):
            occ[x].append((ci, j))
    lines, rels, nxt, copies = [], [], 0, {}
    for x in range(nvars):
        d = len(occ[x])
        if d == 0:
            continue
        m = max(d, 2)
        if kind == "!=" and m % 2:
            m += 1
        copies[x] = list(range(nxt, nxt + m))
        nxt += m
    slot = [[None] * 4 for _ in constraints]
    spare = {}
    for x, cs in copies.items():
        for i, (ci, j) in enumerate(occ[x]):
            slot[ci][j] = (cs[i], i % 2 if kind == "!=" else 0)
        for i, c in enumerate(cs):
            spare[c] = 2 - (1 if i < len(occ[x]) else 0)
    for ci, (vs, R) in enumerate(constraints):
        RR = R
        for j in range(4):
            if slot[ci][j][1]:
                RR = F.flip_place(RR, j)
        lines.append([slot[ci][j][0] for j in range(4)])
        rels.append(RR)
    free_ports = []
    for x, cs in copies.items():
        m = len(cs)
        for i in range(m):
            base = nxt
            nxt += k
            mp = {q: base + q for q in range(k)}
            mp[k + pa], mp[k + pb] = cs[i], cs[(i + 1) % m]
            for L, R in zip(plines, prels):
                idx = len(lines)
                pts = []
                for pos, q in enumerate(L):
                    if q in (k + pc, k + pd):
                        pts.append(None)
                        free_ports.append((idx, pos))
                    else:
                        pts.append(mp[q])
                lines.append(pts)
                rels.append(R)
    targets = [c for c in sorted(spare) for _ in range(spare[c])]
    unused = list(free_ports)
    for c in targets:
        i = next(t for t, (idx, pos) in enumerate(unused) if c not in lines[idx])
        idx, pos = unused.pop(i)
        lines[idx][pos] = c
    rest = sorted(unused)
    G = len(rest) // 4
    for g in range(G):
        for idx, pos in rest[g::G]:
            lines[idx][pos] = nxt
        nxt += 1
    return [tuple(L) for L in lines], rels


# ------------------------------------------------------------------------------------------------ exact search for a failing signing
def failing_signing(lines, members, limit=1500):
    """exists a choice of one member per line with no solution? counterexample-guided: returns (choice, n_cex), (None, n_cex) when no
    failing signing exists, or ('limit', n_cex)"""
    from pysat.card import CardEnc
    from pysat.solvers import Minisat22
    n = 1 + max(max(L) for L in lines)
    m, K = len(lines), len(members)

    def var(l, r):
        return l * K + r + 1
    top = m * K
    S = Minisat22()
    for l in range(m):
        enc = CardEnc.equals(lits=[var(l, r) for r in range(K)], bound=1, top_id=top)
        top = max(top, enc.nv)
        for cl in enc.clauses:
            S.add_clause(cl)
    excl = {pat: [r for r, R in enumerate(members) if pat not in R] for pat in H4}
    cex = 0
    while cex < limit:
        if not S.solve():
            S.delete()
            return None, cex
        model = set(v for v in S.get_model() if v > 0)
        choice = [next(r for r in range(K) if var(l, r) in model) for l in range(m)]
        rels = [members[r] for r in choice]
        with Minisat22(bootstrap_with=F.cnf(lines, rels, n)) as T:
            if not T.solve():
                S.delete()
                return choice, cex
            col = [1 if v > 0 else 0 for v in T.get_model()[:n]]
        S.add_clause([var(l, r) for l, L in enumerate(lines) for r in excl[tuple(col[p] for p in L)]])
        cex += 1
    S.delete()
    return "limit", cex
