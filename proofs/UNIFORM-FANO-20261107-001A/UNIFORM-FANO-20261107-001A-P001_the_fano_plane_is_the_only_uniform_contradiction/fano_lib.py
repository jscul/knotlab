"""The Fano plane is the only uniform law that contradicts itself, for UNIFORM-FANO-20261107-001A.

Laws are the Cayley laws of UNIFORM-SPHERES-20261107-001A: points G, lines L(g) = (g, gx, gxy). Matching every point g with the line
L(g) that starts at it gives the digraph D(H, M) of THREEFOLD-SPACES-20261030-001A: g -> gx and g -> gxy, the Cayley digraph of
{x, xy}. The incidence graph is a brace iff this digraph is strongly 2-connected (Lovasz-Plummer; Robertson-Seymour-Thomas 1999, 7.5),
and a Cayley digraph is strongly 2-connected iff it stays strongly connected after deleting the identity."""
import itertools
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/UNIFORM-SPHERES-20261107-001A/UNIFORM-SPHERES-20261107-001A-P001_uniform_laws_never_contradict_themselves"))
sys.path.insert(0, str(ROOT / "proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane"))
import uniform_lib as U  # noqa: E402
import threefold_lib as T  # noqa: E402
L = U.L


def cayley_lines(x, y):
    """the law's lines as point triples (indices into the group's sorted element list) and the group"""
    G = U.closure([x, y])
    idx = {g: i for i, g in enumerate(G)}
    lines = [(idx[g], idx[U.mul(g, x)], idx[U.mul(U.mul(g, x), y)]) for g in G]
    return G, lines


def simple(lines):
    return all(len(set(l)) == 3 for l in lines)


def brace(x, y):
    """is the Cayley digraph of {x, xy} strongly connected after deleting the identity?"""
    G = U.closure([x, y])
    e = tuple(range(len(G[0])))
    steps = [x, U.mul(x, y)]
    back = [U.inv(s) for s in steps]

    def reach(moves):
        start = next(g for g in G if g != e)
        seen, st = {start}, [start]
        while st:
            g = st.pop()
            for s in moves:
                h = U.mul(g, s)
                if h != e and h not in seen:
                    seen.add(h)
                    st.append(h)
        return len(seen)
    return reach(steps) == len(G) - 1 and reach(back) == len(G) - 1


def colourable(lines, n):
    """a proper 2-colouring (no monochromatic line), by SAT"""
    from pysat.solvers import Solver
    cl = []
    for l in lines:
        v = [p + 1 for p in l]
        cl.append(v)
        cl.append([-a for a in v])
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        return bool(s.solve())


def constant_assignment_works(lines, sigma):
    """with uniform signs sigma, the all-zero assignment gives each line the literals sigma: not all equal iff sigma is not constant"""
    return all(len({sigma[0], sigma[1], sigma[2]}) > 1 for _ in lines)


# ------------------------------------------------------------------------------------------------ the census of Cayley laws
def census(rng, random_pairs=300):
    """(name, x, y) for: every cyclic law on Z_n (n <= 30, up to affine equivalence of the line set), abelian Z_a x Z_b, dihedral,
    A4, S4, A5, S5, PSL(2,7), wallpaper quotients, and random 2-generated subgroups of S_5..S_7"""
    out = []
    import math
    for n in range(3, 31):
        seen = set()
        for a in range(1, n):
            for b in range(1, n):
                if math.gcd(math.gcd(a, b), n) != 1:
                    continue
                ds = {0, a % n, (a + b) % n}
                if len(ds) < 3:
                    continue
                canon = min(tuple(sorted((u * t - u * s0) % n for t in ds)) for u in range(1, n) if math.gcd(u, n) == 1 for s0 in ds)
                if canon in seen:
                    continue
                seen.add(canon)
                out.append((f"Z{n}({a},{b})", tuple((i + a) % n for i in range(n)), tuple((i + b) % n for i in range(n))))
    for p_ in range(2, 7):
        for q_ in range(2, 7):
            m = p_ * q_
            def tr(da, db):
                return tuple(((i // q_ + da) % p_) * q_ + (i % q_ + db) % q_ for i in range(m))
            out.append((f"Z{p_}xZ{q_}", tr(1, 0), tr(0, 1)))
            out.append((f"Z{p_}xZ{q_}'", tr(1, 1), tr(0, 1)))
    for d in range(3, 13):
        x, y = U.dihedral(d)
        out.append((f"D{d}", x, y))
        r = tuple((i + 1) % d for i in range(d))
        out.append((f"D{d}'", x, r))
    for nm, G, types in [("A4", U.alternating(4), [(2, 3, 3), (3, 3, 2)]), ("S4", U.symmetric(4), [(2, 3, 4), (2, 4, 3), (3, 4, 4)]),
                         ("A5", U.alternating(5), [(2, 3, 5), (3, 3, 5), (2, 5, 5), (3, 5, 5)]),
                         ("S5", U.symmetric(5), [(2, 4, 5), (2, 5, 6), (4, 5, 6)]), ("PSL(2,7)", U.gl32(), [(2, 3, 7), (3, 3, 4), (2, 4, 7)])]:
        for t in types:
            pr = U.find_pair(G, *t, rng=rng)
            if pr:
                out.append((f"{nm}{t}", *pr))
    for kind in [(3, 3, 3), (2, 4, 4), (2, 3, 6)]:
        for k in (2, 3, 4, 5):
            out.append((f"{kind}/Z{k}^2", *U.wallpaper_pair(kind, k)))
    for i in range(random_pairs):
        m = rng.choice((5, 6, 7))
        out.append((f"random S{m} #{i}", tuple(rng.sample(range(m), m)), tuple(rng.sample(range(m), m))))
    return out
