"""Native writing (research/NATIVE-WRITE-20261110-001/preregistration.md): the learner, its probe, the spaces and the readouts.

The learner sees its own dissonance (which lines are violated, how many corners agree at each face, W, and the change in W of each of
its moves), the floor |chi| (a count of its own points, lines and faces), and the address asked for: a bit per atom, each atom given
by its region (its lines and the faces they touch). It never reads a role, a class, a solver's answer or a target configuration.
Roles are read by SAT only to score the run afterwards."""
import importlib.util
import itertools
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NA = ROOT / "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


import sys
sys.path.insert(0, str(NA))
import spaces_lib as SP  # noqa: E402

N, G = SP.N, SP.G


# ---------------------------------------------------------------- spaces

def sphere(k):
    if k not in SP.SPH:
        SP.SPH[k] = SP.L.Sphere(SP.SL.octahedral_sphere(k), f"K_{k}")
    return SP.SPH[k]


def lines_at(k, dists):
    S = sphere(k).S
    l0 = G.line_orbits(S)[0][0]
    d = G.line_distance(S, l0)
    return [l0] + [min(t for t, dd in d.items() if dd == (max(d.values()) if q == "max" else q)) for q in dists]


def single(k, leaf, dists):
    """the knot sphere K_k with leaves grown at its first line and at the first lines at the given distances"""
    Y = N.Nested(sphere(k).S, sphere(k).s0)
    for l in lines_at(k, dists):
        Y.grow_leaf(Y.where[l], SP.ATOMS[leaf])
    return Y


def outer(k, groups, dists=("max",)):
    """the outer host K_k with closed composites grown at its first line and the given further lines, each less its standard point"""
    O = N.Nested(sphere(k).S, sphere(k).s0)
    for C, l in zip(groups, lines_at(k, dists)):
        O.grow_closed(O.where[l], C, SP.standard_point(C))
    return O


SPACES = {
    "dev thin": lambda: SP.outer_with([SP.C2("thin"), SP.C2("thin")]),
    "dev Fano": lambda: SP.outer_with([SP.C2("Fano"), SP.C2("Fano")]),
    "S1 single K_3 thin": lambda: single(3, "thin", (2, 3)),
    "S2 single K_3 Fano": lambda: single(3, "Fano", (2, 3)),
    "S3 two-level K_3 thin": lambda: outer(3, [SP.C2("thin"), SP.C2("thin")]),
    "S4 two-level K_3 Fano": lambda: outer(3, [SP.C2("Fano"), SP.C2("Fano")]),
    "S5 two-level K_3 thin, three composites": lambda: outer(3, [SP.C2("thin")] * 3, dists=(2, "max")),
}


class Space:
    def __init__(self, name):
        self.name = name
        self.O = SPACES[name]()
        self.K = self.O.K()
        O, K = self.O, self.K
        self.leaves = O.leaves()
        idx = {q: j for j, q in enumerate(self.leaves)}
        tris = {j: [t for t in range(O.S.nt) if O.path[t] == q] for q, j in idx.items()}
        tri_line = {t: i for i, t in enumerate(K.lines)}
        # an atom's region: its lines and every face they touch (lemma 3 of OTHER-ATOMS-20261110-001A: interior and junction faces)
        self.atoms = {j: (sorted({v for t in tris[j] for v in O.S.vert[t]}), sorted({tri_line[t] for t in tris[j] if t in tri_line}))
                      for j in tris}
        self.role_parts = {j: O.group_parts(K, q)[:2] for q, j in idx.items()}
        self.line_atom = {i: next((j for j in self.atoms if i in self.atoms[j][1]), None) for i in range(K.n)}
        self.floor2 = abs(K.chi)
        self.upper = [p for p in range(K.n) if O.path[K.points[p]] == ()]

    def acting(self, s):
        """scoring only: the atoms acting as their line, by SAT on each atom's outer points"""
        return tuple(j for j in sorted(self.role_parts) if N.group_role(self.K, s, *self.role_parts[j]) == "line")

    def start(self):
        """the first class (in O.classes order) where no atom acts, at the solver's first satisfying state"""
        s = next(s for s in self.O.classes(self.K) if not self.acting(s))
        ok, model = self.K.sat(s)
        assert ok
        return s, [int(model[p] > 0) for p in range(self.K.n)]


def leaf_clearable(K, s, faces, lines):
    """scoring only: is there a state with the atom's lines satisfied and each face of its region agreeing at exactly one corner?"""
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Solver
    cl, top = [], K.n
    for i in lines:
        L = [N.lit(K, s, i, k) for k in range(3)]
        cl += [L, [-a for a in L]]
    for v in faces:
        gs = []
        for (i, c) in K.corners_at[v]:
            top += 1
            a, b = N.lit(K, s, i, (c + 1) % 3), N.lit(K, s, i, (c + 2) % 3)
            cl += [[-top, -a, b], [-top, a, -b], [top, a, b], [top, -a, -b]]
            gs.append(top)
        e = CardEnc.equals(lits=gs, bound=1, top_id=top, encoding=EncType.seqcounter)
        top = max(top, e.nv)
        cl += e.clauses
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        return so.solve()


def has_floor_state(K, s, units):
    """scoring only: a state of law s satisfying every line with at most `units` units"""
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Solver
    cl, top, gs = list(K.clauses(s)), K.n, []
    for v in range(K.V):
        for (i, c) in K.corners_at[v]:
            top += 1
            a, b = N.lit(K, s, i, (c + 1) % 3), N.lit(K, s, i, (c + 2) % 3)
            cl += [[-top, -a, b], [-top, a, -b], [top, a, b], [top, -a, -b]]
            gs.append(top)
    e = CardEnc.atmost(lits=gs, bound=K.V + 2 * units, top_id=top, encoding=EncType.seqcounter)
    cl += e.clauses
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        return so.solve()


# ---------------------------------------------------------------- the learner's own dissonance

def fw(a):
    """a face's dissonance: 0 at one agreeing corner, an even face 1 more than the odd count below it (as LEARN-RISE-20261110-001A)"""
    return 2 * (a // 2) + (a % 2 == 0)


class Engine:
    """A site (i, k) holds the literal x[pt[i][k]] ^ s[3i+k]. A state flip of point p toggles its three sites; a learning move toggles one
    sign. W = 2 * violated lines + sum of fw over faces (LEARN-RISE-20261110-001A's Space, kept incrementally)."""

    def __init__(self, K, S, s, x):
        self.n, self.V = K.n, K.V
        self.pt = [list(K.pt[i]) for i in range(K.n)]
        self.face = [[S.vert[K.lines[i]][c] for c in range(3)] for i in range(K.n)]
        self.corners = [[] for _ in range(K.V)]
        for i in range(K.n):
            for c in range(3):
                self.corners[self.face[i][c]].append((i, c))
        self.sites_of_point = [[(i, k) for i in range(K.n) for k in range(3) if self.pt[i][k] == p] for p in range(K.n)]
        self.s, self.x = list(s), list(x)
        self.L = [[self.x[self.pt[i][k]] ^ self.s[3 * i + k] for k in range(3)] for i in range(K.n)]
        self.viol = [self.L[i][0] == self.L[i][1] == self.L[i][2] for i in range(K.n)]
        self.ag = [sum(self.L[i][(c + 1) % 3] == self.L[i][(c + 2) % 3] for (i, c) in self.corners[v]) for v in range(K.V)]
        self.W = 2 * sum(self.viol) + sum(fw(a) for a in self.ag)

    def delta(self, sites):
        """the change in W, the changed lines' new violation, and the face changes, if these sites' literals were toggled"""
        by_line = {}
        for (i, k) in sites:
            by_line.setdefault(i, []).append(k)
        d, dag, nv = 0, {}, {}
        for i, ks in by_line.items():
            new = list(self.L[i])
            for k in ks:
                new[k] ^= 1
            nv[i] = new[0] == new[1] == new[2]
            d += 2 * (nv[i] - self.viol[i])
            for c in range(3):
                old_eq = self.L[i][(c + 1) % 3] == self.L[i][(c + 2) % 3]
                new_eq = new[(c + 1) % 3] == new[(c + 2) % 3]
                if old_eq != new_eq:
                    v = self.face[i][c]
                    dag[v] = dag.get(v, 0) + (1 if new_eq else -1)
        for v, dv in dag.items():
            d += fw(self.ag[v] + dv) - fw(self.ag[v])
        return d, nv, dag

    def apply(self, sites, d, nv, dag):
        for (i, k) in sites:
            self.L[i][k] ^= 1
        for i, b in nv.items():
            self.viol[i] = b
        for v, dv in dag.items():
            self.ag[v] += dv
        self.W += d

    def flip(self, p):
        sites = self.sites_of_point[p]
        self.x[p] ^= 1
        self.apply(sites, *self.delta(sites))

    def learn_sites(self):
        """A21: a sign changes only where dissonance shows, at a violated line or on an edge ending at an even face"""
        out = []
        for i in range(self.n):
            if self.viol[i]:
                out += [(i, 0), (i, 1), (i, 2)]
                continue
            f = self.face[i]
            e = [self.ag[f[c]] % 2 == 0 for c in range(3)]
            for k in range(3):
                if e[(k + 1) % 3] or e[(k + 2) % 3]:
                    out.append((i, k))
        return out

    def snapshot(self):
        return list(self.s), list(self.x), [list(l) for l in self.L], list(self.viol), list(self.ag), self.W

    def restore(self, snap):
        self.s, self.x, L, self.viol, self.ag, self.W = snap
        self.L = L

    def region_dissonant(self, faces, lines):
        """dissonance in an atom's region: a violated atom line, or a region face with at least two agreeing corners or an even count"""
        return any(self.viol[i] for i in lines) or any(self.ag[v] >= 2 or self.ag[v] % 2 == 0 for v in faces)


def outside_dissonance(E, nf, nl):
    return 2 * sum(E.viol[i] for i in range(E.n) if i not in nl) + sum(fw(E.ag[v]) for v in range(E.V) if v not in nf)


def outside_delta(E, nv, dag, nf, nl):
    d = sum(2 * (b - E.viol[i]) for i, b in nv.items() if i not in nl)
    return d + sum(fw(E.ag[v] + dv) - fw(E.ag[v]) for v, dv in dag.items() if v not in nf)


# ---------------------------------------------------------------- the probe and the learner

def probe(E, atoms, bits, rng, tau):
    """The learner's test of its own memory: tau steps of a state-only walk on the floor plateau (a random point flipped when W does not
    rise), on a copy, with no bias. An atom asked 1 fails if its region is ever free of dissonance; an atom asked 0 fails if its region
    is never free of it. Returns the failing atoms."""
    snap = E.snapshot()
    held = {a: E.region_dissonant(*atoms[a]) for a in atoms if bits[a]}
    clear = {a: not E.region_dissonant(*atoms[a]) for a in atoms if not bits[a]}
    for _ in range(tau):
        p = rng.randrange(E.n)
        sites = E.sites_of_point[p]
        d, nv, dag = E.delta(sites)
        if d <= 0:
            E.x[p] ^= 1
            E.apply(sites, d, nv, dag)
            for a in held:
                if held[a] and not E.region_dissonant(*atoms[a]):
                    held[a] = False
            for a in clear:
                if not clear[a] and not E.region_dissonant(*atoms[a]):
                    clear[a] = True
    E.restore(snap)
    return {a for a in held if not held[a]} | {a for a in clear if not clear[a]}


def instant_check(E, atoms, bits):
    """control U: the same test read at one instant, with no walk"""
    return {a for a in atoms if E.region_dissonant(*atoms[a]) != bool(bits[a])}


PARAMS = dict(T_hot=2.0, T_cold=0.7, lam=1.0, probe_every=200, tau=20000, envelope=4, budget=2_000_000)


def write(E, sp, bits, rng, params=PARAMS, check=probe):
    """Native writing with attention. Moves are proposed at random: a state flip of a random point (probability 1/2) or a sign change at
    a random A21 site, allowed only on a line of an atom whose request is unmet ("hot"). A move is accepted by the Metropolis rule on
    phi = W + lam * (dissonance outside the regions of atoms asked 1), at temperature T_hot when it touches a hot atom's line and T_cold
    otherwise, never above floor + envelope. Every probe_every steps at the floor the learner tests its memory and resets the hot set; it
    stops when nothing is hot. Returns (steps, probes) or (None, probes) when the budget runs out."""
    atoms, floor2 = sp.atoms, sp.floor2
    ones = [a for a in atoms if bits[a]]
    nf = set().union(*[set(atoms[a][0]) for a in ones]) if ones else set()
    nl = set().union(*[set(atoms[a][1]) for a in ones]) if ones else set()
    hot, probes = set(atoms), 0
    tau = params["tau"]
    for t in range(params["budget"]):
        if t % params["probe_every"] == 0 and E.W == floor2:
            hot = check(E, atoms, bits, rng, tau) if check is probe else check(E, atoms, bits)
            probes += 1
            if not hot:
                return t, probes
        if rng.random() < 0.5:
            p = rng.randrange(E.n)
            sites, mv, touched = E.sites_of_point[p], ("flip", p), {sp.line_atom[i] for (i, _) in E.sites_of_point[p]}
        else:
            ls = E.learn_sites()
            if not ls:
                continue
            site = rng.choice(ls)
            if sp.line_atom[site[0]] not in hot:
                continue
            sites, mv, touched = [site], ("learn",) + site, {sp.line_atom[site[0]]}
        T = params["T_hot"] if touched & hot else params["T_cold"]
        d, nv, dag = E.delta(sites)
        if E.W + d > floor2 + params["envelope"]:
            continue
        dphi = d + params["lam"] * outside_delta(E, nv, dag, nf, nl)
        if dphi <= 0 or rng.random() < math.exp(-dphi / T):
            if mv[0] == "flip":
                E.x[mv[1]] ^= 1
            else:
                E.s[3 * mv[1] + mv[2]] ^= 1
            E.apply(sites, d, nv, dag)
    return None, probes


def m1(E, floor2, rng, rounds=2000):
    """ADDRESS-STEER-20261110-001C's learner M1: a random move lowering W, else one keeping it, until the floor"""
    for _ in range(rounds):
        if E.W == floor2:
            break
        moves = [(E.delta(E.sites_of_point[p]), ("flip", p), E.sites_of_point[p]) for p in range(E.n)]
        moves += [(E.delta([st]), ("learn",) + st, [st]) for st in E.learn_sites()]
        pick = [m for m in moves if m[0][0] < 0] or [m for m in moves if m[0][0] == 0]
        if not pick:
            break
        (d, nv, dag), mv, sites = rng.choice(pick)
        if mv[0] == "flip":
            E.x[mv[1]] ^= 1
        else:
            E.s[3 * mv[1] + mv[2]] ^= 1
        E.apply(sites, d, nv, dag)
    return E.W


def sequence(writable, n, seed):
    """n targets drawn uniformly from the writable addresses, each different from the one before, starting from ()"""
    rng, cur, out = random.Random(seed), (), []
    for _ in range(n):
        cur = rng.choice([a for a in writable if a != cur])
        out.append(cur)
    return out


def run_sequence(sp, targets, seed, params=PARAMS, check=probe):
    """write each target in turn from the start; after each stopped write flip one random point of the outermost host and run M1"""
    rng = random.Random(seed)
    s, x = sp.start()
    E = Engine(sp.K, sp.O.S, s, x)
    m1(E, sp.floor2, rng)
    rows = []
    for tg in targets:
        bits = {j: int(j in tg) for j in sp.atoms}
        steps, probes = write(E, sp, bits, rng, params, check)
        act = sp.acting(E.s)
        row = {"target": tg, "stopped": steps is not None, "steps": steps, "probes": probes, "acting at the stop": act}
        if steps is None:
            row["outcome"] = "not stopped"
        else:
            E.flip(rng.choice(sp.upper))
            w = m1(E, sp.floor2, rng)
            after = sp.acting(E.s) if w == sp.floor2 else None
            row["acting after the disturbance"] = after
            row["outcome"] = ("inexact stop" if act != tg else "exact, held" if after == tg else "exact, not held")
        rows.append(row)
    return rows
