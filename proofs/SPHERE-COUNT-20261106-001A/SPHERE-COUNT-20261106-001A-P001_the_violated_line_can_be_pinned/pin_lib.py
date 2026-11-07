"""Single-defect states, local moves of the violated line, and label states, for SPHERE-COUNT-20261106-001A.

Bulk model. Away from the six corners, a Kasteleyn-signed octahedral knot space is, after complementing points (a gauge that changes
no clause width), the not-all-equal system on the triangular lattice whose lines are the up-triangles U(x, y) = {(x,y),(x+1,y),(x,y+1)};
the faces of the incidence graph are the down-triangles D(x, y) = {(x+1,y),(x,y+1),(x+1,y+1)}. In a state violating only the line M,
every face has exactly one agreeing corner, i.e. every down-triangle is not-all-equal too: the state is a ground state of the
triangular-lattice antiferromagnet with one defect triangle.

Moves. The violated line moves from M to an adjacent line M' within radius r when some recolouring of the points at distance <= r from
M u M' makes M' the only violated line among those touching them.

Label states. Give every point a label in Z6 and colour it by the label's pattern on its sublattice (patterns S0..S5 below, the six
not-all-equal colourings of the three sublattices, consecutive ones differing on one sublattice). When adjacent labels differ by at most
one, every triangle is not-all-equal. A point whose six neighbours carry the labels 0..5 in cyclic order is a vortex: either colour of it
violates exactly one of its six triangles."""
import itertools
import random
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "proofs/TWO-ROUND-BRIDGE-20261106-001B/TWO-ROUND-BRIDGE-20261106-001B-P001_three_fold_spaces_are_an_euler_count"))
import count_lib as C  # noqa: E402
from pysat.solvers import Solver  # noqa: E402
from pysat.formula import IDPool  # noqa: E402

NB = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]


# ------------------------------------------------------------------------------------------------ the bulk lattice
def U(x, y):
    return ((x, y), (x + 1, y), (x, y + 1))


def D(x, y):
    return ((x + 1, y), (x, y + 1), (x + 1, y + 1))


def ball(seed, r):
    B, fr = set(seed), set(seed)
    for _ in range(r):
        fr = {(a + dx, b + dy) for a, b in fr for dx, dy in NB} - B
        B |= fr
    return B


def triangles_within(S):
    out = []
    xs, ys = [p[0] for p in S], [p[1] for p in S]
    for x in range(min(xs) - 1, max(xs) + 1):
        for y in range(min(ys) - 1, max(ys) + 1):
            for kind, T in (("U", U(x, y)), ("D", D(x, y))):
                if all(p in S for p in T):
                    out.append((kind, T))
    return out


def _nae(add, var, T):
    a, b, c = (var(p) for p in T)
    add([a, b, c])
    add([-a, -b, -c])


def _equal(add, var, T):
    a, b, c = (var(p) for p in T)
    add([a, -b]); add([b, -c]); add([c, -a])


def can_move_bulk(cfg, M, Mp, r):
    """from the colouring cfg (dict point -> 0/1, covering the ball of radius r+1 around M u M'), can the violated line move to Mp by
    recolouring the points within distance r?"""
    seed = set(M) | set(Mp)
    Br, Br1 = ball(seed, r), ball(seed, r + 1)
    pe = IDPool()
    ev = lambda p: pe.id(p)  # noqa: E731
    S = Solver(name="cadical153")
    for p in Br1 - Br:
        S.add_clause([ev(p) if cfg[p] else -ev(p)])
    for kind, T in triangles_within(Br1):
        if not any(p in Br for p in T):
            continue
        (_equal if T == Mp else _nae)(S.add_clause, ev, T)
    ok = S.solve()
    S.delete()
    return ok


def blocking_configuration(Mp, r, max_iter=100000):
    """counterexample-guided search for a colouring of the ball of radius r+1 around M = U(0,0) and Mp, in which every triangle is
    not-all-equal except M, from which the violated line cannot move to Mp within radius r; returns (config or None, iterations)"""
    M = U(0, 0)
    seed = set(M) | set(Mp)
    Br, Br1 = ball(seed, r), ball(seed, r + 1)
    L = Br1 - Br
    pool = IDPool()
    uv = lambda p: pool.id(("u", p))  # noqa: E731
    SA = Solver(name="cadical153")
    tris = triangles_within(Br1)
    for kind, T in tris:
        (_equal if T == M else _nae)(SA.add_clause, uv, T)
    SA.add_clause([uv((0, 0))])
    touch = [T for kind, T in tris if any(p in Br for p in T)]
    for it in range(1, max_iter + 1):
        if not SA.solve():
            return None, it
        m = set(l for l in SA.get_model() if l > 0)
        u = {p: int(uv(p) in m) for p in Br1}
        pe = IDPool()
        ev = lambda p: pe.id(("e", p))  # noqa: E731
        SE = Solver(name="cadical153")
        for p in L:
            SE.add_clause([ev(p) if u[p] else -ev(p)])
        for T in touch:
            (_equal if T == Mp else _nae)(SE.add_clause, ev, T)
        if not SE.solve():
            SE.delete()
            return u, it
        em = set(l for l in SE.get_model() if l > 0)
        e = {p: (ev(p) in em) for p in Br}
        SE.delete()
        disj = []
        for T in touch:
            if T == Mp:
                continue
            inner = [p for p in T if p in Br]
            outer = [p for p in T if p not in Br]
            if not outer:
                continue
            vals = {e[p] for p in inner}
            if len(vals) == 2:
                continue
            v = vals.pop()
            t = pool.id(("blk", it, T))
            for p in outer:
                SA.add_clause([-t, uv(p) if v else -uv(p)])
            disj.append(t)
        SA.add_clause(disj)
    return None, max_iter


def local_validity(cfg, M):
    """every triangle inside cfg's domain is not-all-equal except M, which is monochromatic"""
    for kind, T in triangles_within(set(cfg)):
        vals = {cfg[p] for p in T}
        if (T == M) != (len(vals) == 1):
            return False
    return True


# ------------------------------------------------------------------------------------------------ the octahedral spaces
def octahedral(k):
    lines, signs, n = C.signed_space(C.octa_dual(k))
    adj = [set() for _ in range(n)]
    for L in lines:
        for a, b in itertools.combinations(L, 2):
            adj[a].add(b)
            adj[b].add(a)
    return lines, signs, n, adj


def dist_from(adj, srcs):
    d = {s: 0 for s in srcs}
    dq = deque(srcs)
    while dq:
        u = dq.popleft()
        for v in adj[u]:
            if v not in d:
                d[v] = d[u] + 1
                dq.append(v)
    return d


def central_line(lines, n, adj):
    cs, fpts = C.corners(lines, n)
    corner_pts = [p for U_ in fpts if len(U_) == 2 for p in U_]
    dc = dist_from(adj, corner_pts)
    return max(range(len(lines)), key=lambda i: (min(dc[p] for p in lines[i]), -i))


def _lits(L, s):
    return [(p + 1) * (-1 if sg else 1) for p, sg in zip(L, s)]


def global_blocking(k, r, max_iter=5000):
    """for the line M farthest from the corners and each adjacent line M': search for a whole-sphere state violating only M from which
    the violated line cannot move to M' within radius r; returns {M': (found, iterations)}"""
    lines, signs, n, adj = octahedral(k)
    M = central_line(lines, n, adj)
    out = {}
    for Mp in [j for j, L in enumerate(lines) if j != M and set(L) & set(lines[M])]:
        dd = dist_from(adj, list(lines[M]) + list(lines[Mp]))
        inner = {p for p, t in dd.items() if t <= r}
        pool = IDPool(start_from=n + 1)
        SA = Solver(name="cadical153")
        for i, (L, s) in enumerate(zip(lines, signs)):
            l3 = _lits(L, s)
            if i == M:
                a, b, c = l3
                SA.add_clause([a, -b]); SA.add_clause([b, -c]); SA.add_clause([c, -a])
            else:
                SA.add_clause(l3); SA.add_clause([-x for x in l3])
        SA.add_clause([lines[M][0] + 1])
        touch = [i for i, L in enumerate(lines) if any(p in inner for p in L)]
        res = (False, max_iter)
        for it in range(1, max_iter + 1):
            if not SA.solve():
                res = (False, it)
                break
            st = [1 if l > 0 else 0 for l in SA.get_model()[:n]]
            SE = Solver(name="cadical153")
            for i in touch:
                l3 = _lits(lines[i], signs[i])
                if i == Mp:
                    a, b, c = l3
                    SE.add_clause([a, -b]); SE.add_clause([b, -c]); SE.add_clause([c, -a])
                else:
                    SE.add_clause(l3); SE.add_clause([-x for x in l3])
            assum = sorted({(p + 1) if st[p] else -(p + 1) for i in touch for p in lines[i] if p not in inner})
            if not SE.solve(assumptions=assum):
                SE.delete()
                res = (True, it)
                break
            em = SE.get_model()
            e = {p: (em[p] > 0) for p in inner}
            SE.delete()
            disj = []
            for i in touch:
                if i == Mp:
                    continue
                ins = [(p, sg) for p, sg in zip(lines[i], signs[i]) if p in inner]
                outs = [(p, sg) for p, sg in zip(lines[i], signs[i]) if p not in inner]
                vals = {e[p] ^ sg for p, sg in ins}
                if not outs or len(vals) == 2:
                    continue
                v = vals.pop()
                t = pool.id(("blk", it, i))
                for p, sg in outs:
                    SA.add_clause([-t, (p + 1) if (v ^ sg) else -(p + 1)])
                disj.append(t)
            SA.add_clause(disj)
        SA.delete()
        out[Mp] = res
    return M, out


def random_state_moves(k, trials, seed, radii=(0, 1, 2, 3)):
    """from random states violating one line (solver phases random), the least radius at which the violated line reaches each
    adjacent line"""
    lines, signs, n, adj = octahedral(k)
    rng = random.Random(seed)
    tally = {}
    for t in range(trials):
        M = rng.randrange(len(lines))
        S = Solver(name="cadical153")
        for i, (L, s) in enumerate(zip(lines, signs)):
            if i != M:
                l3 = _lits(L, s); S.add_clause(l3); S.add_clause([-x for x in l3])
        S.set_phases([v if rng.random() < 0.5 else -v for v in range(1, n + 1)])
        assert S.solve()
        st = [1 if l > 0 else 0 for l in S.get_model()[:n]]
        S.delete()
        for Mp in [j for j, L in enumerate(lines) if j != M and set(L) & set(lines[M])]:
            dd = dist_from(adj, list(lines[M]) + list(lines[Mp]))
            least = None
            for r in radii:
                inner = {p for p, d in dd.items() if d <= r}
                S2 = Solver(name="cadical153")
                for i, (L, s) in enumerate(zip(lines, signs)):
                    if i != Mp:
                        l3 = _lits(L, s); S2.add_clause(l3); S2.add_clause([-x for x in l3])
                ok = S2.solve(assumptions=[(p + 1) if st[p] else -(p + 1) for p in range(n) if p not in inner])
                S2.delete()
                if ok:
                    least = r
                    break
            tally[least] = tally.get(least, 0) + 1
    return tally


# ------------------------------------------------------------------------------------------------ label states
SUB = lambda p: (p[0] - p[1]) % 3  # noqa: E731   sublattice of a lattice point: every triangle meets all three
PATTERNS = [(0, 1, 1), (0, 0, 1), (1, 0, 1), (1, 0, 0), (1, 1, 0), (0, 1, 0)]   # S0..S5 on sublattices (0, 1, 2)


def colour(label, sub):
    return PATTERNS[label % 6][sub]
