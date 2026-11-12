"""Finite checks of NEST-COUNT-20261112-001A-P001 (proof.md beside this file).

K1  P3a: the inequality gadget NAE(x,y,a), NAE(x,y,b), NAE(x,y,c), NAE(a,b,c) allows exactly the states with x != y on (x, y);
    equality by two inequalities through m allows exactly x = y.
K2  P3b: each of the 16 complement-closed relations on three distinctions is defined by NAE knots on distinct distinctions with
    fresh distinctions (the definitions of proof.md), checked by enumerating every state.
K3  P3c: random Wang tile sets (2 to 4 tiles, 2 colours per side) on the n x n torus (n = 2, 3): the NAE encoding allows a state
    iff the tile set tiles the torus (direct enumeration of tilings), and decoding a state gives a tiling.
Run from the repository root:  .venv/bin/python -B proofs/NEST-COUNT-20261112-001A/NEST-COUNT-20261112-001A-P001_finite_state/check.py [--write]
"""
import itertools, json, os, random, sys
from pysat.solvers import Solver

HERE = os.path.dirname(os.path.abspath(__file__))


class Pattern:
    def __init__(self):
        self.n, self.knots = 0, []

    def new(self):
        self.n += 1
        return self.n - 1

    def nae(self, a, b, c):
        assert len({a, b, c}) == 3, "knots on distinct distinctions only"
        self.knots.append((a, b, c))

    def neq(self, x, y):
        a, b, c = self.new(), self.new(), self.new()
        self.nae(x, y, a); self.nae(x, y, b); self.nae(x, y, c); self.nae(a, b, c)

    def eq(self, x, y):
        m = self.new()
        self.neq(x, m); self.neq(m, y)

    def flipped(self, x):
        y = self.new()
        self.neq(x, y)
        return y

    def clause(self, lits, r):
        """A clause read relative to r: literal (v, True) holds when v differs from r, (v, False) when v equals r."""
        vs = [v if pos else self.flipped(v) for v, pos in lits]
        if len(vs) == 1:
            self.neq(vs[0], r)
        elif len(vs) == 2:
            self.nae(vs[0], vs[1], r)
        else:                                       # NAE on k + 1 places by chaining: NAE(w,x,a), NAE(a', y, ...), with a' != a
            cur = vs[0]
            for j in range(1, len(vs) - 1):
                a = self.new()
                self.nae(cur, vs[j], a)
                cur = self.flipped(a)
            self.nae(cur, vs[-1], r)

    def clauses(self):
        return [c for t in self.knots for c in ([v + 1 for v in t], [-(v + 1) for v in t])]


def projections(P, vs):
    out = set()
    with Solver(name="cadical153", bootstrap_with=P.clauses()) as s:
        for bits in itertools.product((0, 1), repeat=len(vs)):
            if s.solve(assumptions=[(v + 1) if b else -(v + 1) for v, b in zip(vs, bits)]):
                out.add(bits)
    return out


def k1():
    P = Pattern(); x, y = P.new(), P.new(); P.neq(x, y)
    ok1 = projections(P, [x, y]) == {(0, 1), (1, 0)}
    P = Pattern(); x, y = P.new(), P.new(); P.eq(x, y)
    ok2 = projections(P, [x, y]) == {(0, 0), (1, 1)}
    return ok1 and ok2


def define(rel):
    """NAE definition of a complement-closed relation on (x, y, z) given as a set of states (bit j = distinction j)."""
    P = Pattern(); x, y, z = P.new(), P.new(), P.new(); v = [x, y, z]
    pairs = {frozenset({s, 7 - s}) for s in rel}
    if len(pairs) == 4:
        return P, v
    if len(pairs) == 0:                             # a contradiction: the ten knots on five distinctions
        w = [P.new() for _ in range(5)]
        for t in itertools.combinations(w, 3):
            P.nae(*t)
        return P, v
    # a relation of three pairs is NAE with the excluded pair's flips; of one or two pairs, equalities and inequalities
    allowed = sorted(rel)
    if len(pairs) == 3:
        bad = [s for s in range(8) if s not in rel][0]          # excluded pair {bad, 7 - bad}: flip the ends where bad has a 1
        u = [P.flipped(v[j]) if (bad >> j) & 1 else v[j] for j in range(3)]
        P.nae(*u)
        return P, v
    for i, j in itertools.combinations(range(3), 2):           # constrain each pair that is fixed across the allowed states
        rel_ij = {((s >> i) & 1) ^ ((s >> j) & 1) for s in allowed}
        if rel_ij == {0}:
            P.eq(v[i], v[j])
        elif rel_ij == {1}:
            P.neq(v[i], v[j])
    return P, v


def k2():
    bad = 0
    for keep in itertools.product((0, 1), repeat=4):
        rel = set()
        for p, kp in zip([(0, 7), (1, 6), (2, 5), (4, 3)], keep):
            if kp:
                rel |= set(p)
        P, v = define(rel)
        got = {sum(b << j for j, b in enumerate(bits)) for bits in projections(P, v)}
        bad += got != rel
    return bad == 0


def tiles_torus(tiles, n):
    """Direct: is there a tiling of the n x n torus (E of a tile = W of its right neighbour, N = S of the upper one)?"""
    for assign in itertools.product(range(len(tiles)), repeat=n * n):
        ok = True
        for i in range(n):
            for j in range(n):
                t = tiles[assign[i * n + j]]
                if t[1] != tiles[assign[i * n + (j + 1) % n]][3] or t[0] != tiles[assign[((i + 1) % n) * n + j]][2]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return True
    return False


def encode(tiles, n):
    P = Pattern()
    sites = [(i, j) for i in range(n) for j in range(n)]
    r = {s: P.new() for s in sites}
    x = {(s, k): P.new() for s in sites for k in range(len(tiles))}
    for (i, j) in sites:
        s = (i, j)
        P.eq(r[s], r[(i, (j + 1) % n)]); P.eq(r[s], r[((i + 1) % n, j)])
        P.clause([(x[(s, k)], True) for k in range(len(tiles))], r[s])                # some tile
        for k, l in itertools.combinations(range(len(tiles)), 2):                        # at most one
            P.clause([(x[(s, k)], False), (x[(s, l)], False)], r[s])
        right, up = (i, (j + 1) % n), ((i + 1) % n, j)
        for k, a in enumerate(tiles):
            for l, b in enumerate(tiles):
                if a[1] != b[3]:
                    P.clause([(x[(s, k)], False), (x[(right, l)], False)], r[s])
                if a[0] != b[2]:
                    P.clause([(x[(s, k)], False), (x[(up, l)], False)], r[s])
    return P, r, x, sites


def k3(trials=300, seed=2026):
    rng = random.Random(seed)
    bad, seen = 0, {True: 0, False: 0}
    for _ in range(trials):
        n = rng.choice((2, 3))
        tiles = [tuple(rng.randrange(2) for _ in range(4)) for _ in range(rng.randint(2, 4))]
        tiles = list(dict.fromkeys(tiles))
        direct = tiles_torus(tiles, n)
        P, r, x, sites = encode(tiles, n)
        with Solver(name="cadical153", bootstrap_with=P.clauses()) as s:
            lives = s.solve()
            if lives:                                  # decode and verify a tiling
                m = set(l for l in s.get_model() if l > 0)
                val = lambda v: (v + 1) in m
                dec = {}
                for st in sites:
                    on = [k for k in range(len(tiles)) if val(x[(st, k)]) != val(r[st])]
                    if len(on) != 1:
                        bad += 1
                    dec[st] = on[0] if on else 0
                for (i, j) in sites:
                    t = tiles[dec[(i, j)]]
                    if t[1] != tiles[dec[(i, (j + 1) % n)]][3] or t[0] != tiles[dec[((i + 1) % n, j)]][2]:
                        bad += 1
        bad += lives != direct
        seen[direct] += 1
    return bad == 0, seen


def main():
    ok1, ok2 = k1(), k2()
    ok3, seen = k3()
    out = dict(K1=ok1, K2=ok2, K3=ok3, K3_tilings=seen["True"] if "True" in seen else seen[True], K3_no_tiling=seen[False],
               status="passed" if ok1 and ok2 and ok3 else "failed")
    print(json.dumps(out))
    if "--write" in sys.argv:
        json.dump(dict(schema_version=3, artifact_id="NEST-COUNT-20261112-001A-P001", kind="proof", ticket="NEST-COUNT-20261112-001A", proof="NEST-COUNT-20261112-001A-P001", **out), open(os.path.join(HERE, "result.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
