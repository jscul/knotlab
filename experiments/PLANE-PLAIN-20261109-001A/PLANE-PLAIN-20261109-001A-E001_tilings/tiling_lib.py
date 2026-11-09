"""Periodic plane tilings as networks of rings (PLANE-PLAIN-20261109-001A-E001).

Maps are rotation systems (rot: {vertex: [edge ids counterclockwise]}, edges: [(u, w)]); a dart is (edge, side), side 0 at edges[e][0].
Tori of the three regular lattices of every shape come from plain_lib.reduce_mod; medial, truncation and duality turn them into tori of
the Archimedean tilings 3.6.3.6, 4.8.8, 3.12.12, 3.4.6.4, 4.6.12 and their Laves duals. Rings are the vertices, contacts the edges, every
ring of m contacts holding m g cells with its contacts equally spaced (loopnet_lib.network). A contact persists exactly when no closed
walk from it back to it has an odd count at any length (LOOP-NET-20261108-001A, Theorem 2 (a), at equal spacing); a flip at a contact is
an orientation-preserving automorphism of the map fixing it and exchanging its two rings (LOOP-NET-20261108-001A, Theorem 3)."""
import collections
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/PLAIN-TIME-20261108-001A/PLAIN-TIME-20261108-001A-E001_map_census"))
import plain_lib as P  # noqa: E402

LN = P.LN
DIRS = {"square": ((1, 0), (0, 1), (-1, 0), (0, -1)),
        "triangular": ((1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1))}


def torus(kind, B):
    """the torus of the lattice with basis rows B, or None if a contact joins a ring to itself"""
    det = B[0][0] * B[1][1] - B[0][1] * B[1][0]
    red = lambda v: P.reduce_mod(v, B)
    pts = sorted({red((i, j)) for i in range(-2 * det, 2 * det + 1) for j in range(-2 * det, 2 * det + 1)})
    if kind != "honeycomb":
        dirs = DIRS[kind]
        edges, eid = [], {}
        for v in pts:
            for d in dirs[:len(dirs) // 2]:
                w = red((v[0] + d[0], v[1] + d[1]))
                if w == v:
                    return None
                eid[(v, d)] = eid[(w, (-d[0], -d[1]))] = len(edges)
                edges.append((v, w))
        return {v: [eid[(v, d)] for d in dirs] for v in pts}, edges
    verts = [(p, s) for p in pts for s in (0, 1)]
    edges, rot = [], {v: [None] * 3 for v in verts}
    for p in pts:
        for k, q in enumerate((p, red((p[0] - 1, p[1])), red((p[0], p[1] - 1)))):
            rot[(p, 0)][k] = rot[(q, 1)][k] = len(edges)
            edges.append(((p, 0), (q, 1)))
    return rot, edges

def darts(rot, edges):
    """sigma: dart -> next dart ccw at its vertex; a dart is (e, side), side 0 at edges[e][0]"""
    sig, at = {}, {}
    for v, lst in rot.items():
        ds = []
        for e in lst:
            u, w = edges[e]
            if u == v and w == v:
                raise ValueError("loop")
            ds.append((e, 0) if u == v else (e, 1))
        # an edge listed twice at v (multi) is fine; a dart appears once per listing
        for i, d in enumerate(ds):
            sig[d] = ds[(i + 1) % len(ds)]
            at[d] = v
    inv = {b: a for a, b in sig.items()}
    return sig, inv, at

def medial(rot, edges):
    sig, inv, at = darts(rot, edges)
    corner_id, medges = {}, []
    for d in sig:
        corner_id[d] = len(medges)
        medges.append((d[0], sig[d][0]))   # joins edge(d) and edge(sigma d)
    mrot = {}
    for e in range(len(edges)):
        d0, d1 = (e, 0), (e, 1)
        mrot[e] = [corner_id[inv[d1]], corner_id[d0], corner_id[inv[d0]], corner_id[d1]]
    return mrot, medges

def truncation(rot, edges):
    sig, inv, at = darts(rot, edges)
    tedges, tid = [], {}
    for e in range(len(edges)):
        tid[("e", e)] = len(tedges); tedges.append(((e, 0), (e, 1)))
    for d in sig:
        tid[("c", d)] = len(tedges); tedges.append((d, sig[d]))
    trot = {d: [tid[("e", d[0])], tid[("c", d)], tid[("c", inv[d])]] for d in sig}
    return trot, tedges

def faces_of(rot, edges):
    sig, inv, at = darts(rot, edges)
    alpha = lambda d: (d[0], 1 - d[1])
    seen, sizes = set(), []
    for d in sig:
        if d in seen: continue
        k, x = 0, d
        while x not in seen:
            seen.add(x); k += 1; x = sig[alpha(x)]
        sizes.append(k)
    return collections.Counter(sizes)

def network(rot, edges, g=2):
    sizes, contacts = LN.network(rot, edges, g)
    n, out, rc = P.network_map(sizes, contacts)
    return sizes, contacts, n, out, rc

def persistent_all(sizes, contacts, n, out):
    """every contact persists iff no closed walk c -> c of length k >= 1 is odd (LOOP-NET-20261108-001A, Theorem 2 (a), equal spacing);
    the sequence (A^k)_cc satisfies A's minimal recurrence of order <= n, so k = 1 .. n + 1 decide it"""
    ins = [0] * n
    for d in range(n):
        for e in out[d]:
            ins[e] ^= 1 << d
    bad = []
    for c in range(n):
        row = 1 << c
        for k in range(1, n + 2):
            v, x = 0, row
            while x:
                low = x & -x
                v ^= ins[low.bit_length() - 1]
                x ^= low
            row = v
            if row >> c & 1:
                bad.append(c); break
    return bad

def on_time_all(n, out, rc):
    late = 0
    for t in range(n):
        v = P.verdicts(n, out, rc, t)
        late += v["rings late"] + v["rings never"]
    return late

def dual(rot, edges):
    """vertices = faces of the map (orbits of sigma . alpha), edges the same; at a face, its edges in ccw order"""
    sig, inv, at = darts(rot, edges)
    alpha = lambda d: (d[0], 1 - d[1])
    face_of, faces = {}, []
    for d in sig:
        if d in face_of: continue
        cyc, x = [], d
        while x not in face_of:
            face_of[x] = len(faces); cyc.append(x); x = sig[alpha(x)]
        faces.append(cyc)
    # the face to the left of dart d (going around face by sigma . alpha); dual edge e joins the faces of its two darts
    dedges = [(face_of[(e, 0)], face_of[(e, 1)]) for e in range(len(edges))]
    # rotation at a face: walking the face by phi = sigma . alpha gives its edges in one cyclic order; use the reverse for ccw
    drot = {}
    for f, cyc in enumerate(faces):
        drot[f] = [d[0] for d in reversed(cyc)]
    return drot, dedges

def has_flip(rot, edges, e):
    """an orientation-preserving automorphism of the map sending dart (e, 0) to (e, 1): determined by that image, built by sigma and alpha"""
    sig, inv, at = darts(rot, edges)
    alpha = lambda d: (d[0], 1 - d[1])
    phi = {(e, 0): (e, 1)}
    stack = [(e, 0)]
    while stack:
        d = stack.pop()
        for op in (lambda x: sig[x], alpha):
            a, b = op(d), op(phi[d])
            if a in phi:
                if phi[a] != b:
                    return False
            else:
                phi[a] = b
                stack.append(a)
    return len(phi) == len(sig) and len(set(phi.values())) == len(sig)
