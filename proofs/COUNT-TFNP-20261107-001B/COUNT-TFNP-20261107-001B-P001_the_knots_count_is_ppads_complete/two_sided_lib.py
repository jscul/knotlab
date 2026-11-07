"""The knot's count in TFNP, for COUNT-TFNP-20261107-001B.

FLAT-STATES-20261107-001B's map Phi sends a Sperner_m colouring c to an assignment of the knot sphere K_k (k >= 2m + 4). Its violated
lines lie exactly inside c's counterclockwise fully labelled triangles. This module checks the other half: its monochromatic faces (a
three-point face whose three corners all agree, the corner face count of TWO-ROUND-BRIDGE-20261106-001B) lie exactly inside c's
clockwise fully labelled triangles, so Phi also reduces two-sided Sperner to the two-sided count (a violated line or a monochromatic
face). It also reads the boundary that Phi expects: the canonical Sperner boundary up to a cyclic shift of the colours."""
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/FLAT-STATES-20261107-001B/FLAT-STATES-20261107-001B-P001_the_knot_sphere_contains_sperner"))
import sperner_lib as S  # noqa: E402
import window_lib as SW  # noqa: E402

F = S.F
C = F.C


def boundary_shift(red):
    """the shift s with bcol = canonical + s (mod 3), or None if there is none"""
    m = red["m"]
    can = SW.boundary_colours(m)
    shifts = {(red["bcol"][v] - can[v]) % 3 for v in can}
    return shifts.pop() if len(shifts) == 1 and set(can) == set(red["bcol"]) else None


def face_corners(K):
    byf = defaultdict(list)
    for (l, a, b, f) in K["corners"]:
        byf[f].append((l, a, b))
    return byf


def mono_faces(K, x, byf):
    sg = K["sgn"]
    return [f for f, crn in byf.items() if len(K["fpts"][f]) == 3 and all((x[a] ^ sg[l][a]) == (x[b] ^ sg[l][b]) for l, a, b in crn)]


def violated_lines(K, x):
    return F.violated(K, x)


def coarse_of_points(red, pts):
    R = red["R"]
    if not all(p in R for p in pts):
        return None
    vs = set()
    for p in pts:
        vs.update(S.coarse_of(R[p]))
    return tuple(sorted(vs))


def orientation(col, t):
    """+1 when the triangle's colours read 0, 1, 2 counterclockwise; t as listed by window_lib.grid (counterclockwise)"""
    cs = [col[v] for v in t]
    i = cs.index(0)
    return 1 if cs[(i + 1) % 3] == 1 else -1


def audit(red, col_int, byf):
    """for one Sperner colouring: where the violated lines and monochromatic faces of Phi(c) sit"""
    K, m = red["K"], red["m"]
    x, col = S.image(red, col_int)
    full = {}
    for t in SW.grid(m)[1]:
        if len({col[v] for v in t}) == 3:
            full[tuple(sorted(t))] = orientation(col, t)
    vl = violated_lines(K, x)
    mf = mono_faces(K, x, byf)
    where_l = [coarse_of_points(red, K["lines"][l]) for l in vl]
    where_f = [coarse_of_points(red, K["fpts"][f]) for f in mf]
    ok_lines = all(w in full and full[w] == 1 for w in where_l)
    ok_faces = all(w in full and full[w] == -1 for w in where_f)
    covered = all((t in where_l) if o == 1 else (t in where_f) for t, o in full.items())
    return dict(full=len(full), positive=sum(o == 1 for o in full.values()), negative=sum(o == -1 for o in full.values()),
                violated=len(vl), mono=len(mf), lines_in_positive=ok_lines, faces_in_negative=ok_faces,
                every_full_triangle_holds_one=covered, count_identity=len(vl) - len(mf) == 1)
