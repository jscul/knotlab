"""The named spaces of research/NEST-ATOMS-20261110-001/preregistration.md, built with nest_lib."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_spec = importlib.util.spec_from_file_location("nest_lib", HERE / "nest_lib.py")
N = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(N)
A, G, SL = N.A, N.G, N.SL
L = A.load("steer", "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py")
SPH = {k: L.Sphere(SL.octahedral_sphere(k), f"K_{k}") for k in (2, 3)}
ATOMS = {"Fano": A.Atom((7, 2, 1)), "thin": A.Atom((2, 1, 2))}


def lines_of(k, dists=None):
    """l0, the first line-orbit representative, with the first line at the largest distance (or at each given distance)"""
    S = SPH[k].S
    l0 = G.line_orbits(S)[0][0]
    d = G.line_distance(S, l0)
    if dists is None:
        m = max(d.values())
        return [l0, min(t for t, dd in d.items() if dd == m)]
    return [l0] + [min(t for t, dd in d.items() if dd == q) for q in dists]


def composite(k, atom, lines):
    Y = N.Nested(SPH[k].S, SPH[k].s0)
    for l in lines:
        Y.grow_leaf(Y.where[l], atom)
    return Y


def points_kind(Y):
    K = Y.K()
    ports = set()
    for g in Y.groups:
        if len(g) == 1:
            ports |= set(Y.group_parts(K, g)[1])
    return {t: "inside a group" if Y.path[t] != () else "on a replaced line" if p in ports else "off the replaced lines"
            for p, t in enumerate(K.points)}


def standard_point(Y):
    kinds = points_kind(Y)
    return next(t for t in Y.K().points if kinds[t] == "off the replaced lines")


def C2(leaf):
    return composite(2, ATOMS[leaf], lines_of(2))


def D2(leaf):
    inner = composite(2, ATOMS[leaf], lines_of(2)[:1])
    Y = N.Nested(SPH[2].S, SPH[2].s0)
    l0, l1 = lines_of(2)
    Y.grow_closed(Y.where[l0], inner, standard_point(inner))
    Y.grow_leaf(Y.where[l1], ATOMS[leaf])
    return Y


def outer_with(groups):
    """the outer host K_2 with closed composites grown at L0 and then L1, each less its standard point"""
    O = N.Nested(SPH[2].S, SPH[2].s0)
    for C, l in zip(groups, lines_of(2)):
        O.grow_closed(O.where[l], C, standard_point(C))
    return O
