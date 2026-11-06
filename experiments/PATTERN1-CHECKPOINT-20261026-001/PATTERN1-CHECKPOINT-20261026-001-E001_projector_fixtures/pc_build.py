"""Builders for the pattern-1 checkpoint: base knots, projector leaves, balanced band sums, Y-graphs as six-component links."""
import math

from pc_core import (Comp, BraidLayout, dedupe, dedupe_path, helix, copy_loop, projector_leaf, EPS, RW, PITCH, XRAIL, XSP,
                     HL, P, R, ZETA)


def multiplicities(chi, p=P, r=R):
    """m_j = r^-1 chi^-j mod p (representatives 0..p-1): the eigenprojector P_chi = r^-1 sum_j chi^-j t^j"""
    rinv = pow(r, p - 2, p)
    cinv = pow(chi, p - 2, p)
    return [rinv * pow(cinv, j, p) % p for j in range(r)]


# ------------------------------------------------------------------------------------------------ the Y-graph link

def ellipse(k, t):
    if k == 0:
        return (2 * math.cos(t), math.sin(t), 0.0)
    if k == 1:
        return (0.0, 2 * math.cos(t), math.sin(t))
    return (math.sin(t), 0.0, 2 * math.cos(t))


def b_component(k, vertex, target, zt, npts=48, dt=0.12, ex=0.03, rc=0.08, vertical_target=False):
    """Borromean component k (0, 1, 2) at vertex, with an excursion to a Hopf clasp around the root segment of a leaf.
    target = (X_mid, Y_root): the root segment runs along x through (X_mid, Y_root, 0)."""
    vx, vy, vz = vertex
    sh = lambda p: (p[0] + vx, p[1] + vy, p[2] + vz)
    ring = [sh(ellipse(k, dt + (2 * math.pi - 2 * dt) * s / npts)) for s in range(npts + 1)]   # from +dt to 2pi - dt
    s_ = math.sin(dt)
    if k == 0:      # E1 at (2, 0, 0): exit along +x, edges offset in y
        out_start = [sh((2 * math.cos(dt), -s_, 0.0)), sh((3.0, -s_, 0.0))]
        back_end = [sh((3.0, s_, 0.0)), sh((2 * math.cos(dt), s_, 0.0))]
        rise_out, rise_back = sh((3.0, -s_, 0.0)), sh((3.0, s_, 0.0))
    elif k == 1:    # E2 at (0, 2, 0): exit along +y, edges offset in z then in x
        out_start = [sh((0.0, 2 * math.cos(dt), -s_)), sh((-0.05, 3.0, -s_)), sh((-0.1, 3.2, -s_))]
        back_end = [sh((0.1, 3.2, s_)), sh((0.05, 3.0, s_)), sh((0.0, 2 * math.cos(dt), s_))]
        rise_out, rise_back = sh((-0.1, 3.2, -s_)), sh((0.1, 3.2, s_))
    else:           # E3 at (0, 0, 2): exit straight up, edges offset in x
        out_start = [sh((-s_, 0.0, 2 * math.cos(dt)))]
        back_end = [sh((s_, 0.0, 2 * math.cos(dt)))]
        rise_out, rise_back = sh((-s_, 0.0, 2 * math.cos(dt))), sh((s_, 0.0, 2 * math.cos(dt)))
    X, Y = target
    zo, zb = zt + 0.05, zt - 0.05
    path_out = out_start + [(rise_out[0], rise_out[1], zo), (X - ex, Y + rc, zo), (X - ex, Y + rc, 0.0)]
    clasp = [(X - ex + 2 * ex * s / 24, Y + rc * math.cos(2 * math.pi * s / 24), rc * math.sin(2 * math.pi * s / 24))
             for s in range(25)]
    path_back = [(X + ex, Y + rc, 0.0), (X + ex, Y + rc, zb), (rise_back[0], rise_back[1], zb)] + back_end
    pts = ring[:-1] + [ring[-1]] + path_out + clasp + path_back
    return dedupe(pts)


def y_graph(gi, vertex, targets, zbase):
    """three B components for Y-graph gi; targets = [(X_mid, Y_root)] * 3"""
    return [Comp(f"B{gi}_{k}", b_component(k, vertex, targets[k], zbase + 2 * k), 0, 0, "borromean") for k in range(3)]


# ------------------------------------------------------------------------------------------------ leaves

def leaf_projector(name, xa, ytop, chi, wdir, mult=None):
    pts, ybot, info = projector_leaf(xa, ytop, mult or multiplicities(chi), wdir)
    return Comp(name, pts, 0, 0, "leaf"), ybot, info


def band_path(p_from, p_to, zc, eps=EPS, wind=None):
    """centerline of a connecting band from rail point p_from = (x, y) to p_to at depth zc; optional winding
    wind = (x_s, y_w, turns, direction) once around the vertical strand x = x_s at height y_w"""
    (x0, y0), (x1, y1) = p_from, p_to
    pts = [(x0, y0, 0.0), (x0, y0, zc)]
    if wind is not None:
        xs, yw, turns, d = wind
        pts += [(xs - 0.35, yw, zc), (xs - 0.35, yw, 0.0)]
        pts += helix(xs, yw, 0.35, turns, PITCH, d)
        yend = yw + turns * PITCH
        pts += [(xs - 0.35, yend, zc)]
    pts += [(x1, y1, zc), (x1, y1, 0.0)]
    return pts


def leaf_band_sum(name, xa_u, ytop_u, xa_v, ytop_v, chi, wdir, zc, wind=None, mult=None):
    """x_u - x_v: projector leaf at u, connecting band (above the diagram), projector leaf at v traversed backwards.
    Position 0 is the root-segment midpoint of u (where the clasp sits)."""
    m = mult or multiplicities(chi)
    cut_u, cut_v = ytop_u - 0.3, ytop_v - 0.3
    path_u, ybot_u, info_u = projector_leaf(xa_u, ytop_u, m, wdir, cut=cut_u)
    path_v, ybot_v, info_v = projector_leaf(xa_v, ytop_v, m, wdir, cut=cut_v)
    xr_u, xr_v = xa_u + XRAIL, xa_v + XRAIL
    cl = band_path((xr_u, cut_u), (xr_v, cut_v), zc, wind=wind)
    # edges offset in y, and also in depth while travelling above the diagram (so they never overlap in space)
    out_edge = [(x, y - EPS, z - 0.05 if z > 0.5 else z) for x, y, z in cl]
    back_edge = [(x, y + EPS, z + 0.05 if z > 0.5 else z) for x, y, z in reversed(cl)]
    pts = path_u + out_edge + list(reversed(path_v)) + back_edge
    pts = dedupe_path(pts)
    if max(abs(a - b) for a, b in zip(pts[0], pts[-1])) < 1e-12:
        pts.pop()
    root = (info_u["root_mid"][0], info_u["root_mid"][1], 0.0)
    k0 = min(range(len(pts)), key=lambda k: sum((a - b) ** 2 for a, b in zip(pts[k], root)))
    assert sum((a - b) ** 2 for a, b in zip(pts[k0], root)) < 1e-18
    pts = pts[k0:] + pts[:k0]
    return Comp(name, pts, 0, 0, "leaf"), (ybot_u, ybot_v), info_u


def leaf_simple(name, xa, yc):
    """one copy loop with a short root on its left (no projector): for scoping and unit tests"""
    loop = copy_loop(xa, yc)
    att = loop[0][0]
    root = [(att - 0.25, yc + EPS, 0.0)]
    pts = [((att - 0.25 + att) / 2, yc + EPS, 0.0)] + loop + [(att - 0.25, yc - EPS, 0.0)] + root
    return Comp(name, dedupe(pts), 0, 0, "leaf"), ((att - 0.25 + att) / 2, yc + EPS)


def leaf_bundle(name, x_lo, x_hi, y, eps=0.15):
    """a loop around the bundle of vertical strands x_lo..x_hi at height y (under at the top, over at the bottom),
    with a horizontal root segment on its upper left"""
    pts = [(x_lo - 0.475, y + eps, 0.0), (x_lo - 0.35, y + eps, 0.0), (x_lo - 0.2, y + eps, -HL), (x_hi + 0.2, y + eps, -HL),
           (x_hi + 0.35, y, 0.0), (x_hi + 0.2, y - eps, HL), (x_lo - 0.2, y - eps, HL), (x_lo - 0.6, y - eps, 0.0),
           (x_lo - 0.6, y + eps, 0.0)]
    return Comp(name, dedupe(pts), 0, 0, "leaf"), (x_lo - 0.475, y + eps)
