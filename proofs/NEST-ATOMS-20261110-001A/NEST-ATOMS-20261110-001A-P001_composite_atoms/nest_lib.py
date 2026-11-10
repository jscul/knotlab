"""Nested atoms, for NEST-ATOMS-20261110-001.

A `Nested` knot space keeps, for every triangle, its **path**: () for the outermost host, and for a triangle inside a grown group the
group's index under its parent followed by its path inside the group. A group is a leaf (a torus atom of OTHER-ATOMS-20261110-001) or a
composite (a closed `Nested` space less one point). Growth splices a closed knot space less a point into a line by the first compatible
bijection (chirality 0: the bijections that lower the Euler characteristic of the union by 2), keeps the old signs on both sides, and signs
the three new sides by the first completion with no even face. Classes are reached by flat changes on the sides inside each top-level group
(sides whose line and point are both in the group), which keep every side of the outermost host and every new side at its cut; by
Mayer-Vietoris over the separating three-side cuts they reach every class."""
import importlib.util
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location(
    "multi_lib", ROOT / "proofs/OTHER-ATOMS-20261110-001B/OTHER-ATOMS-20261110-001B-P001_holding_a_unit_with_other_atoms/multi_lib.py")
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)
A, G, SL = M.A, M.G, M.SL


def lit(K, s, i, k):
    return (K.pt[i][k] + 1) * (1 if s[3 * i + k] == 0 else -1)


def splice_closed(S, s, t, S2, s2, P2):
    """splice the closed knot space (S2, s2) less point triangle P2 into (S, s) at line triangle t; returns (surface, signing, back), back
    mapping each side with line and point both from S2 to its side index in S2"""
    KA, K2 = SL.KnotSpace(S), SL.KnotSpace(S2)
    RA, RR = G.rotation_of(S, "A"), G.rotation_of(S2, "R")
    for sg in itertools.permutations(range(3)):
        m = G.splice(RA, ("A", t), RR, ("R", P2), sg)
        if G.euler_of(m) == KA.chi + K2.chi - 2:
            break
    else:
        raise AssertionError("no compatible bijection")
    GS = G.build("grown", *m)
    KG = SL.KnotSpace(GS)
    lidA = {u: i for i, u in enumerate(KA.lines)}
    lidR = {u: i for i, u in enumerate(K2.lines)}
    out, new, back = [None] * (3 * KG.n), [], {}
    for gi, gt in enumerate(KG.lines):
        for j, d in enumerate(m[1][GS.verts[gt]]):
            e, ge = m[2][d], 3 * gi + j
            if d[0] == "A" and e[0] == "A":
                out[ge] = s[3 * lidA[d[1]] + d[2]]
            elif d[0] == "R" and e[0] == "R":
                back[ge] = 3 * lidR[d[1]] + d[2]
                out[ge] = s2[back[ge]]
            else:
                new.append(ge)
    assert len(new) == 3
    for bits in itertools.product((0, 1), repeat=3):
        t2 = list(out)
        for e, b in zip(new, bits):
            t2[e] = b
        if KG.even_faces(t2) == []:
            return GS, t2, back
    raise AssertionError("no completion with no even face")


class Nested:
    def __init__(self, S, s):
        self.S0, self.s0, self.K0 = S, list(s), SL.KnotSpace(S)
        self.S, self.s = S, list(s)
        self.path = {t: () for t in range(S.nt)}
        self.where = {t: t for t in range(S.nt)}
        self.nchild = {}
        self.groups = {}  # group path -> {"kind": "leaf" | "composite", "line": host line triangle replaced (in its parent's own host)}

    def _grow(self, t, S2, s2, P2, paths2, groups2, kind, label):
        parent = self.path[t]
        idx = self.nchild.get(parent, 0)
        self.nchild[parent] = idx + 1
        root = parent + (idx,)
        GS, s_new, self.last_back = splice_closed(self.S, self.s, t, S2, s2, P2)
        inv = {cur: o for o, cur in self.where.items()}
        path, where = {}, {}
        for v, name in enumerate(GS.verts):
            if name[0] == "A":
                path[v] = self.path[name[1]]
                if name[1] in inv:
                    where[inv[name[1]]] = v
            else:
                path[v] = root + paths2[name[1]]
        self.S, self.s, self.path, self.where = GS, s_new, path, where
        self.groups[root] = {"kind": kind, "label": label}
        for g, info in groups2.items():
            self.groups[root + g] = info
        return root

    def grow_leaf(self, t, atom):
        """grow torus atom `atom` (atoms_lib.Atom) at current line triangle t"""
        return self._grow(t, atom.S, atom.s, atom.P, {u: () for u in range(atom.S.nt)}, {}, "leaf", atom.name)

    def grow_closed(self, t, other, P2):
        """grow the closed Nested space `other` less its point triangle P2 at current line triangle t"""
        return self._grow(t, other.S, other.s, P2, other.path, other.groups, "composite", "composite")

    def K(self):
        return SL.KnotSpace(self.S)

    def leaves(self):
        return sorted(g for g, info in self.groups.items() if info["kind"] == "leaf")

    def genus(self, g):
        return sum(1 for q in self.leaves() if q[:len(g)] == g)

    def inside(self, t, g):
        return self.path[t][:len(g)] == g

    def group_parts(self, K, g):
        """lines, outer points and region faces of group g"""
        lines = [i for i in range(K.n) if self.inside(K.lines[i], g)]
        pts = {K.pt[i][k] for i in lines for k in range(3)}
        outer = sorted(p for p in pts if not self.inside(K.points[p], g))
        region = sorted({self.S.vert[t][c] for t in range(self.S.nt) if self.inside(t, g) for c in range(3)})
        return lines, outer, region

    def classes(self, K):
        """a signing for each of the 4^G classes, by flat changes on each leaf's own sides"""
        Z = [int("".join(str(b) for b in reversed(z)), 2) for z in K.classes()]
        g2, m = len(Z), 3 * K.n
        leaves = self.leaves()
        assert g2 == 2 * len(leaves)
        gauge = K.gauge_vectors()
        cs = []
        for j in range(g2):
            sol = SL.solve_f2(gauge + Z, [0] * len(gauge) + [int(j == q) for q in range(g2)], m)
            cs.append([(sol >> e) & 1 for e in range(m)])
        picks, span = [], SL.Basis()
        tops = sorted({q[:1] for q in leaves})
        for q in tops:
            inner = [3 * i + k for i in range(K.n) for k in range(3)
                     if self.path[K.lines[i]][:1] == q and self.path[K.points[K.pt[i][k]]][:1] == q]
            pos = {e: r for r, e in enumerate(inner)}
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
                for e, r in pos.items():
                    full[e] = (z >> r) & 1
                lab = int("".join(str(sum(full[e] & c[e] for e in range(m)) % 2) for c in cs), 2)
                if span.add(lab):
                    picks.append(full)
                    got += 1
                if got == 2 * self.genus(q):
                    break
            assert got == 2 * self.genus(q)
        out = []
        for a in itertools.product((0, 1), repeat=g2):
            s = list(self.s)
            for ai, z in zip(a, picks):
                if ai:
                    s = [u ^ w for u, w in zip(s, z)]
            out.append(s)
        return out


def relation(K, s, lines, ports):
    from pysat.solvers import Solver
    cl = []
    for i in lines:
        L = [lit(K, s, i, k) for k in range(3)]
        cl += [L, [-a for a in L]]
    out = []
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        for pat in itertools.product((0, 1), repeat=3):
            if so.solve(assumptions=[(p + 1) if b else -(p + 1) for p, b in zip(ports, pat)]):
                out.append(pat)
    return out


def role_of(rel):
    return {6: "line", 8: "transparent"}.get(len(rel), "%d patterns" % len(rel))


def group_role(K, s, lines, ports):
    """the role of a group with three outer points; a group with more (a leaf cut open by the removed point) has none"""
    if len(ports) != 3:
        return "cut open (%d outer points)" % len(ports)
    return role_of(relation(K, s, lines, ports))


def units_at_most(K, s, region, k):
    """is there a state satisfying every line with at most k units in region (faces odd: units = (agreeing corners - faces) / 2)?"""
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Solver
    cl, top, gs = list(K.clauses(s)), K.n, []
    for v in region:
        for (i, c) in K.corners_at[v]:
            top += 1
            a, b = lit(K, s, i, (c + 1) % 3), lit(K, s, i, (c + 2) % 3)
            cl += [[-top, -a, b], [-top, a, -b], [top, a, b], [top, -a, -b]]
            gs.append(top)
    enc = CardEnc.atmost(lits=gs, bound=len(region) + 2 * k, top_id=top, encoding=EncType.seqcounter)
    cl += enc.clauses
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        return so.solve()


def one_violated(K, s, i):
    """a state violating line i and no other line?"""
    from pysat.solvers import Solver
    cl = [c for j in range(K.n) if j != i for c in ([lit(K, s, j, k) for k in range(3)], [-lit(K, s, j, k) for k in range(3)])]
    L = [lit(K, s, i, k) for k in range(3)]
    cl += [[L[0], -L[1]], [-L[0], L[1]], [L[1], -L[2]], [-L[1], L[2]]]
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        return so.solve()
