"""The snub and elongated tilings as networks of rings (FLIP-RULE-20261109-001A-E001), on PLANE-PLAIN-20261109-001A-E001's tiling_lib.

The Conway snub of a map has a vertex per dart d (the corner from d to sigma d) and edges d - sigma d (vertex polygons), d - sigma^-1
alpha d (face polygons) and d - alpha d, one per edge of the map; at d its five edges lie, counterclockwise, towards sigma^-1 alpha d,
alpha sigma d, sigma d, sigma^-1 d and alpha d. The snub of the cube is the snub cube (24 vertices, 32 triangles, 6 squares), of the
square torus the snub square tiling 3.3.4.3.4, of the triangular torus the snub hexagonal tiling 3.3.3.3.6. The elongated triangular
tiling 3.3.3.4.4 is Z^2 with rows of squares (strips y odd to y + 1) and of triangles (strips y even to y + 1, diagonal from (x, y) to
(x + 1, y + 1)), on tori of lattices inside Z x 2Z."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/PLANE-PLAIN-20261109-001A/PLANE-PLAIN-20261109-001A-E001_tilings"))
import tiling_lib as TL  # noqa: E402

P = TL.P


def snub(rot, edges):
    sig, inv, at = TL.darts(rot, edges)
    alpha = lambda d: (d[0], 1 - d[1])
    eid, sedges = {}, []

    def edge(a, b, kind):
        key = (kind, a, b) if kind != "C" else (kind,) + tuple(sorted([a, b]))
        if key not in eid:
            eid[key] = len(sedges)
            sedges.append((a, b))
        return eid[key]
    srot = {}
    for d in sig:
        srot[d] = [edge(d, inv[alpha(d)], "B"), edge(alpha(sig[d]), d, "B"), edge(d, sig[d], "A"), edge(inv[d], d, "A"),
                   edge(d, alpha(d), "C")]
    return srot, sedges


def elongated(B):
    """the elongated triangular tiling on the torus Z^2 / L, L with basis rows B inside Z x 2Z; None if a contact joins a ring to itself"""
    assert all(v[1] % 2 == 0 for v in B)
    det = B[0][0] * B[1][1] - B[0][1] * B[1][0]
    red = lambda v: P.reduce_mod(v, B)
    pts = sorted({red((i, j)) for i in range(-2 * abs(det), 2 * abs(det) + 1) for j in range(-2 * abs(det), 2 * abs(det) + 1)})
    edges, eid = [], {}
    for (x, y) in pts:
        for tag, d in (("E", (1, 0)), ("N", (0, 1))) + ((("NE", (1, 1)),) if y % 2 == 0 else ()):
            w = red((x + d[0], y + d[1]))
            if w == (x, y):
                return None
            eid[((x, y), tag)] = len(edges)
            edges.append(((x, y), w))
    rot = {}
    for (x, y) in pts:
        E, N = eid[((x, y), "E")], eid[((x, y), "N")]
        W, S = eid[(red((x - 1, y)), "E")], eid[(red((x, y - 1)), "N")]
        if y % 2 == 0:
            rot[(x, y)] = [E, eid[((x, y), "NE")], N, W, S]
        else:
            rot[(x, y)] = [E, N, W, eid[(red((x - 1, y - 1)), "NE")], S]
    return rot, edges
