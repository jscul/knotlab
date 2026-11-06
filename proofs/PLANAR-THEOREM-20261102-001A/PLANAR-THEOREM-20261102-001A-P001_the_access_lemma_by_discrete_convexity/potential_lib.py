"""Potentials of line-face matchings on a plane knot space minus a line, for PLANAR-THEOREM-20261102-001A.

After a line M is removed from a plane knot space with Kasteleyn signs, the solutions up to complement are the perfect matchings of the
other lines to the faces not touching M: each line is matched to the face of the corner opposite its odd point (HANDLE-EMERGENCE C).
In the plane, the line-face incidence graph B has one face per point not on M's faces, and one face (the hole) holding M's points and
every point on M's faces. Crossing the edge of B from line L into face f, which passes through the corner of f at L between its
incidences p (before L along f) and q (after L), the height jumps by mu(L, f) - mu0(L, f) from p's region to q's region. Integrating
from the hole (height 0) gives the potential c_mu, an integer on each point (0 on the hole)."""
import collections

import networkx as nx


def faces_with_corners(H):
    g = nx.Graph()
    g.add_edges_from((("p", p), ("l", k)) for k, L in enumerate(H) for p in L)
    ok, emb = nx.check_planarity(g)
    assert ok
    seen, faces = set(), []
    for v, w in emb.edges():
        if (v, w) not in seen:
            faces.append(emb.traverse_face(v, w, mark_half_edges=seen))
    corners = []                                      # (line, face index, p before, q after)
    for fi, f in enumerate(faces):
        for i, v in enumerate(f):
            if v[0] == "l":
                corners.append((v[1], fi, f[i - 1][1], f[(i + 1) % len(f)][1]))
    return faces, corners


class Plane:
    """one removal M from a plane knot space"""

    def __init__(self, H, s, n, M):
        self.H, self.s, self.n, self.M = H, s, n, M
        self.faces, corners = faces_with_corners(H)
        self.mfaces = {fi for (L, fi, p, q) in corners if L == M}
        hole = {v[1] for fi in self.mfaces for v in self.faces[fi] if v[0] == "p"}
        self.hole = hole
        self.region = {p: ("hole" if p in hole else p) for p in range(n)}
        # edges of B: lines other than M to faces off M
        self.edges = [(L, fi, p, q) for (L, fi, p, q) in corners if L != M and fi not in self.mfaces]
        self.line_face = {(L, fi) for (L, fi, p, q) in self.edges}

    def matching(self, x):
        """the matched face of each line (the corner opposite its odd point) for a solution x"""
        mu = {}
        for k, L in enumerate(self.H):
            if k == self.M:
                continue
            v = [x[p] ^ self.s[k][j] for j, p in enumerate(L)]
            odd = next(L[j] for j in range(3) if v[j] != v[(j + 1) % 3] and v[j] != v[(j + 2) % 3])
            fs = [fi for (LL, fi, p, q) in self.edges if LL == k and odd not in (p, q)]
            assert len(fs) == 1
            mu[k] = fs[0]
        return mu

    def heights(self, mu, mu0):
        """integrate the jumps from the hole; returns (potential per point, consistent?)"""
        adj = collections.defaultdict(list)
        for (L, fi, p, q) in self.edges:
            d = int(mu[L] == fi) - int(mu0[L] == fi)
            a, b = self.region[p], self.region[q]
            adj[a].append((b, d))
            adj[b].append((a, -d))
        h = {"hole": 0}
        todo = ["hole"]
        consistent = True
        while todo:
            a = todo.pop()
            for b, d in adj[a]:
                if b not in h:
                    h[b] = h[a] + d
                    todo.append(b)
                elif h[b] != h[a] + d:
                    consistent = False
        return [h.get(self.region[p]) for p in range(self.n)], consistent
