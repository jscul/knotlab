"""Several torus atoms grown on a knot sphere, for OTHER-ATOMS-20261110-001B and C.

`grow_one` is GROW-STUCK-20261110-001A's grow_any with a torus atom (atoms_lib.Atom) in place of the Fano atom: the first bijection that
lowers the Euler characteristic by 2, chirality 0, old signs kept, the atom's sides from its torus's Kasteleyn law (the Fano torus's is the
uniform law), the first completion with no even face, and the state extended to the atom's points by the first assignment that violates
the fewest lines. `Spaced` grows atoms at sphere lines in turn and keeps, for every triangle, its level (the sphere or atom j), the triangle
it comes from and how its sides map to the original ones, so each atom's sides can be read back on its torus."""
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "atoms_lib", ROOT / "proofs/OTHER-ATOMS-20261110-001A/OTHER-ATOMS-20261110-001A-P001_the_role_of_every_torus_atom/atoms_lib.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)
G, SL = A.G, A.SL


def first_growth(S, s, t, atom):
    for sg in itertools.permutations(range(3)):
        g = A.Grown(S, s, t, atom, sg, 0)
        if g.ok:
            return g, sg
    raise AssertionError("no bijection lowers chi by 2")


def grow_one(S, s, x, t, atom):
    """(S', s', x', chi') as GROW-STUCK-20261110-001A's grow_any, with the atom"""
    g, _ = first_growth(S, s, t, atom)
    assert g.completions
    s2, K2, KA = g.completions[0], g.K, SL.KnotSpace(S)
    x2 = [None] * K2.n
    for i, tt in enumerate(KA.points):
        x2[g.old_point[tt]] = x[i]
    pid = {gt: i for i, gt in enumerate(K2.points)}
    gvid = {v: i for i, v in enumerate(g.S.verts)}
    pts = [pid[gvid[v]] for v in g.S.verts if v[0] == "R" and g.S.colour[gvid[v]] == 0]
    arg = None
    for bits in itertools.product((0, 1), repeat=len(pts)):
        y = list(x2)
        for p, b in zip(pts, bits):
            y[p] = b
        v = K2.tallies(s2, y)[0]
        if arg is None or v < arg[0]:
            arg = (v, y)
    return g.S, s2, arg[1], K2.chi


class Spaced:
    """a knot sphere (surface S, Kasteleyn signing s0) with atoms grown at sphere lines in turn"""

    def __init__(self, S, s0):
        self.S0, self.s0, self.K0 = S, list(s0), SL.KnotSpace(S)
        self.S, self.s = S, list(s0)
        self.info = {t: ("U", t, (0, 1, 2)) for t in range(S.nt)}
        self.where = {t: t for t in range(S.nt)}
        self.atoms, self.lines = [], []

    def grow(self, orig_line, atom):
        t = self.where[orig_line]
        g, sg = first_growth(self.S, self.s, t, atom)
        assert g.completions
        m = G.splice(G.rotation_of(self.S, "A"), ("A", t), G.rotation_of(atom.S, "R"), ("R", atom.P), sg)[1]
        j = len(self.atoms)
        info, where = {}, {}
        inv = {cur: o for o, cur in self.where.items()}
        for v, name in enumerate(g.S.verts):
            darts = m[name]
            if name[0] == "A":
                lev, orig, sm = self.info[name[1]]
                info[v] = (lev, orig, tuple(sm[d[2]] for d in darts))
                if name[1] in inv:
                    where[inv[name[1]]] = v
            else:
                info[v] = (j, name[1], tuple(d[2] for d in darts))
        self.S, self.s, self.info, self.where = g.S, g.completions[0], info, where
        self.atoms.append(atom)
        self.lines.append(orig_line)

    def K(self):
        return SL.KnotSpace(self.S)

    def atom_parts(self, K, j):
        """atom j's lines, internal sides (line and point both in the atom), outer points in the order of the replaced line's sides,
        own patterns and region"""
        lev = lambda t: self.info[t][0]  # noqa: E731
        lines = [i for i in range(K.n) if lev(K.lines[i]) == j]
        inner = [3 * i + k for i in lines for k in range(3) if lev(K.points[K.pt[i][k]]) == j]
        pidx = {t: i for i, t in enumerate(K.points)}
        l = self.lines[j]
        ports = [pidx[self.where[self.S0.side[l][k][0]]] for k in range(3)]
        li = self.K0.lines.index(l)
        s0 = self.s0
        own = sorted(p for p in itertools.product((0, 1), repeat=3)
                     if not (p[0] ^ s0[3 * li] == p[1] ^ s0[3 * li + 1] == p[2] ^ s0[3 * li + 2]))
        region = sorted({self.S.vert[t][c] for t in range(self.S.nt) if lev(t) == j for c in range(3)})
        return lines, inner, ports, own, region

    def torus_label(self, K, j, s):
        """the class of atom j's torus read from atom j's sides of signing s (the point's three sides completed with no even face)"""
        atom = self.atoms[j]
        lines, inner, _, _, _ = self.atom_parts(K, j)
        ts = [None] * (3 * atom.K.n)
        for e in inner:
            i, k = divmod(e, 3)
            _, orig, sm = self.info[K.lines[i]]
            ts[3 * atom.lid[orig] + sm[k]] = s[e]
        miss = [e for e in range(len(ts)) if ts[e] is None]
        assert len(miss) == 3
        for bits in itertools.product((0, 1), repeat=3):
            for e, b in zip(miss, bits):
                ts[e] = b
            if atom.K.even_faces(ts) == []:
                return atom.T.label(ts)
        raise AssertionError("no completion of the point's sides")

    def classes(self, K):
        """[signing] for every class, reached by flat changes on each atom's own sides; with 2g label functionals checked"""
        Z = [int("".join(str(b) for b in reversed(z)), 2) for z in K.classes()]
        g2, m = len(Z), 3 * K.n
        assert g2 == 2 * len(self.atoms)
        gauge = K.gauge_vectors()
        cs = []
        for j in range(g2):
            sol = SL.solve_f2(gauge + Z, [0] * len(gauge) + [int(j == q) for q in range(g2)], m)
            cs.append([(sol >> e) & 1 for e in range(m)])
        label = lambda s: tuple(sum(s[e] & c[e] for e in range(m)) % 2 for c in cs)  # noqa: E731
        picks, span = [], SL.Basis()
        for j in range(len(self.atoms)):
            _, inner, _, _, _ = self.atom_parts(K, j)
            pos = {e: q for q, e in enumerate(inner)}
            rows = []
            for v in range(K.V):
                r = 0
                for i, c in K.corners_at[v]:
                    for e in (3 * i + (c + 1) % 3, 3 * i + (c + 2) % 3):
                        if e in pos:
                            r ^= 1 << pos[e]
                rows.append(r)
            got = 0
            for z in SL.kernel_f2(rows, len(inner)):
                full = [0] * m
                for e, q in pos.items():
                    full[e] = (z >> q) & 1
                lab = int("".join(map(str, label(full))), 2)
                if span.add(lab):
                    picks.append(full)
                    got += 1
                if got == 2:
                    break
            assert got == 2
        out = []
        for a in itertools.product((0, 1), repeat=g2):
            s = list(self.s)
            for ai, z in zip(a, picks):
                if ai:
                    s = [u ^ w for u, w in zip(s, z)]
            out.append(s)
        assert len({label(s) for s in out}) == 4 ** len(self.atoms)
        return out
