"""Torus atoms, for OTHER-ATOMS-20261110-001.

An atom is a lattice torus knot space less one point, spliced at a knot sphere's line by a compatible splice (GROW-HANDLE-20261110-001A:
one of three bijections and two chiralities, those that lower the Euler characteristic by 2). The atom's sides take a Kasteleyn law of
its torus, carried side by side (a dart keeps its torus side index, mirrored or not), the old signs are kept, and the three new sides take
signs that leave no even face. The atom's four classes are reached by flat changes on the atom's own sides (lemma A of
ATOM-RULE-20261110-001A), which keep every sphere side and every new side, so the replaced line's own patterns stay the reference."""
import importlib.util
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


G = load("grow_lib", "proofs/GROW-HANDLE-20261110-001A/GROW-HANDLE-20261110-001A-P001_a_fano_atom_grown_at_the_dissonance/grow_lib.py")
H, SL = G.H, G.SL


def lit(K, s, i, k):
    return (K.pt[i][k] + 1) * (1 if s[3 * i + k] == 0 else -1)


# ---------------------------------------------------------------------------------------------------- atoms up to isomorphism
def _code(m, d0):
    colour, rot, partner = m
    succ = {d: r[(j + 1) % 3] for r in rot.values() for j, d in enumerate(r)}
    num, order, out, i = {d0: 0}, [d0], [], 0
    while i < len(order):
        d = order[i]
        i += 1
        row = [colour[d[:2]]]
        for e in (succ[d], partner[d]):
            if e not in num:
                num[e] = len(order)
                order.append(e)
            row.append(num[e])
        out.append(tuple(row))
    return tuple(out)


def canon(S):
    """an exact canonical form of a connected two-coloured map up to isomorphism and mirror image"""
    R = G.rotation_of(S, "")
    return min(_code(m, d0) for m in (R, G.mirror(R)) for d0 in m[2])


def lattice_atom_types(max_all_sat=12, max_forced=16):
    """simple lattice tori grouped by canon: every type up to max_all_sat points, and class-forced ones up to max_forced"""
    types = {}
    for N in range(3, max_forced + 1):
        for t in SL.hnf_sublattices(N):
            if SL.torus_kind(*t) == "degenerate":
                continue
            S = SL.torus(*t)
            if not SL.KnotSpace(S).simple():
                continue
            forced = len(SL.satisfiable_classes(*t)) < 4
            if N > max_all_sat and not forced:
                continue
            types.setdefault(canon(S), []).append((t, SL.torus_kind(*t), forced))
    return list(types.values())


class Atom:
    def __init__(self, params):
        self.params = tuple(params)
        self.name = "torus(%d,%d,%d)" % self.params
        self.T = H.Torus(*params)
        self.S, self.K = self.T.S, self.T.K
        self.P = next(t for t in range(self.S.nt) if self.S.colour[t] == 0)
        self.forced = list(self.T.forced)
        self.base = self.forced[0] if self.forced else (0, 0)
        self.s = list(self.T.classes[self.base])
        assert self.K.even_faces(self.s) == []
        self.lid = {t: i for i, t in enumerate(self.K.lines)}
        self.points = self.K.n


# ---------------------------------------------------------------------------------------------------- growing an atom
class Grown:
    """knot space S with signing s0 (indexed as KnotSpace(S)) and an atom spliced at line triangle l; ok is False when the splice does not
    lower the Euler characteristic by 2"""

    def __init__(self, S, s0, l, atom, sigma, chirality):
        KA = SL.KnotSpace(S)
        A = G.rotation_of(S, "A")
        R = G.rotation_of(atom.S, "R")
        if chirality:
            R = G.mirror(R)
        m = G.splice(A, ("A", l), R, ("R", atom.P), sigma)
        self.ok = G.euler_of(m) == KA.chi - 2
        if not self.ok:
            return
        GS = G.build("grown", *m)
        KG = SL.KnotSpace(GS)
        lidA = {t: i for i, t in enumerate(KA.lines)}
        s, new, inner, back = [None] * (3 * KG.n), [], [], {}
        for gi, gt in enumerate(KG.lines):
            for j, d in enumerate(m[1][GS.verts[gt]]):
                e, ge = m[2][d], 3 * gi + j
                if d[0] == "A" and e[0] == "A":
                    s[ge] = s0[3 * lidA[d[1]] + d[2]]
                elif d[0] == "R" and e[0] == "R":
                    back[ge] = 3 * atom.lid[d[1]] + d[2]
                    s[ge] = atom.s[back[ge]]
                    inner.append(ge)
                else:
                    new.append(ge)
        assert len(new) == 3
        self.completions = []
        for bits in itertools.product((0, 1), repeat=3):
            t = list(s)
            for e, b in zip(new, bits):
                t[e] = b
            if KG.even_faces(t) == []:
                self.completions.append(t)
        self.S, self.K, self.atom, self.new, self.inner, self.back = GS, KG, atom, new, inner, back
        pid = {gt: i for i, gt in enumerate(KG.points)}
        gvid = {v: i for i, v in enumerate(GS.verts)}
        self.old_point = {t: pid[gvid[("A", t)]] for t in KA.points}
        self.atom_lines = [i for i, gt in enumerate(KG.lines) if GS.verts[gt][0] == "R"]
        self.ports = [self.old_point[S.side[l][k][0]] for k in range(3)]
        li = KA.lines.index(l)
        self.own = sorted(p for p in itertools.product((0, 1), repeat=3)
                          if not (p[0] ^ s0[3 * li] == p[1] ^ s0[3 * li + 1] == p[2] ^ s0[3 * li + 2]))
        self.region = sorted({GS.vert[t][c] for t in range(GS.nt) if GS.verts[t][0] == "R" for c in range(3)})

    def label_fn(self):
        """the grown torus's class label: two linear functionals that vanish on gauge (as GrownTorus)"""
        K = self.K
        Z = [int("".join(str(b) for b in reversed(z)), 2) for z in K.classes()]
        assert len(Z) == 2
        gauge, m = K.gauge_vectors(), 3 * K.n
        cs = []
        for j in range(2):
            sol = SL.solve_f2(gauge + Z, [0] * len(gauge) + [int(j == 0), int(j == 1)], m)
            cs.append([(sol >> e) & 1 for e in range(m)])
        return lambda s: tuple(sum(s[e] & cs[j][e] for e in range(m)) % 2 for j in (0, 1))

    def classes(self, s_nat):
        """{grown label: (signing, torus label)} for the four classes, reached by flat changes on the atom's own sides"""
        K, pos = self.K, {e: i for i, e in enumerate(self.inner)}
        rows = []
        for v in range(K.V):
            r = 0
            for i, c in K.corners_at[v]:
                for e in (3 * i + (c + 1) % 3, 3 * i + (c + 2) % 3):
                    if e in pos:
                        r ^= 1 << pos[e]
            rows.append(r)
        label = self.label_fn()
        picks = []
        for z in SL.kernel_f2(rows, len(self.inner)):
            full = [0] * (3 * K.n)
            for e, i in pos.items():
                full[e] = (z >> i) & 1
            lab = label(full)
            span = {(0, 0)} | {p[1] for p in picks} | ({tuple(a ^ b for a, b in zip(picks[0][1], picks[1][1]))} if len(picks) == 2 else set())
            if lab not in span:
                picks.append((full, lab))
            if len(picks) == 2:
                break
        assert len(picks) == 2, "the atom's own sides do not reach every class"
        out = {}
        for a in itertools.product((0, 1), repeat=2):
            s = list(s_nat)
            for ai, (z, _) in zip(a, picks):
                if ai:
                    s = [u ^ w for u, w in zip(s, z)]
            ts = list(self.atom.s)
            for e, ae in self.back.items():
                ts[ae] ^= s[e] ^ s_nat[e]
            out[label(s)] = (s, self.atom.T.label(ts))
        assert len(out) == 4
        return out

    def relation(self, s):
        """the patterns of the three outer points that some assignment of the atom's points completes on the atom's lines"""
        from pysat.solvers import Solver
        cl = []
        for i in self.atom_lines:
            L = [lit(self.K, s, i, k) for k in range(3)]
            cl += [L, [-a for a in L]]
        out = []
        with Solver(name="cadical153", bootstrap_with=cl) as so:
            for pat in itertools.product((0, 1), repeat=3):
                if so.solve(assumptions=[(p + 1) if b else -(p + 1) for p, b in zip(self.ports, pat)]):
                    out.append(pat)
        return out


def role(rel, own):
    if rel == own:
        return "line"
    if len(rel) == 8:
        return "transparent"
    return "%d patterns" % len(rel) + (" (a line, other signs)" if len(rel) == 6 else "")
