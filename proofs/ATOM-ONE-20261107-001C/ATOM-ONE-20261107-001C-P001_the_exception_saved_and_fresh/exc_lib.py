"""The exception, saved and fresh, for ATOM-ONE-20261107-001C.

For a removal a and a line b of a Fano atom B not holding it, with C the cut of B facing a and R the port relation the removal's side
shows on C:
- own: B's own verdict, in the space's coordinates: B's lines, each other closed side replaced by the relation it shows on its channels,
  and R on C's channels; masks from B's points and channels only (ticket B: by GLUE-READ A this is the closed atom's verdict).
- near: the real side of B (every point behind B's other cuts kept) with R on C's channels (GLUE-READ A's side test, far side by far side).
- exact: the creation map.
- far (only at the exception: a receiving cut whose relation has six patterns, at a line through a channel): B's own masks together with
  every deep point of the real removal's side.
"""
import collections
import importlib.util
import sys
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


PO = load("ao_c_port_lib", ROOT / "proofs/GLUE-READ-20261106-001A/GLUE-READ-20261106-001A-P001_creation_is_decided_by_the_receiving_cut/"
          "port_lib.py")
TL = PO.TL


def code_of(vecs):
    return "-" if vecs is None else "".join(ch if v else "." for ch, v in zip("KcFC", vecs))


def join_on(A, acols, B, bcols):
    """rows of A extended by every compatible row of B (equal on the given columns); returns (A part, B part) stacked"""
    keyA = (A[:, acols].astype(np.int64) << np.arange(len(acols))).sum(axis=1)
    keyB = (B[:, bcols].astype(np.int64) << np.arange(len(bcols))).sum(axis=1)
    groups = collections.defaultdict(list)
    for j, k in enumerate(keyB.tolist()):
        groups[k].append(j)
    ia, ib = [], []
    for i, k in enumerate(keyA.tolist()):
        for j in groups.get(k, ()):
            ia.append(i)
            ib.append(j)
    return A[ia], B[ib]


def space_report(S, exact):
    parts, types, pown, lown, xs = PO.structure(S)
    n = len(S.H)
    tree = nx.Graph()
    tree.add_nodes_from(range(len(parts)))
    for k, sides in xs.items():
        b1, b2 = sorted(sides)
        tree.add_edge(b1, b2, cut=k)
    paths = dict(nx.all_pairs_shortest_path(tree))

    def sols(lines, pts):
        rel = {q: j for j, q in enumerate(pts)}
        return TL.solutions([tuple(rel[q] for q in S.H[x]) for x in lines], [S.s[x] for x in lines], len(pts))

    c = collections.Counter()
    atoms = [B for B in range(len(parts)) if types[B] == "heawood"]
    for B in atoms:
        LB = [x for x in range(n) if lown[x] == B]
        cuts = [k for k in xs if B in xs[k]]
        info = {}
        for k in cuts:
            b2 = [bb for bb in xs[k] if bb != B][0]
            h = tree.copy()
            h.remove_edge(B, b2)
            comp = nx.node_connected_component(h, b2)
            far = [x for x in range(n) if lown[x] in comp]
            near = [x for x in range(n) if lown[x] not in comp]
            ports = sorted({q for x in far for q in S.H[x]} & {q for x in near for q in S.H[x]})
            info[k] = (b2, far, near, ports)
        V = sorted({q for x in LB for q in S.H[x]} | {q for k in cuts for q in info[k][3]})
        closed = {}
        for k in cuts:
            b2, far, near, ports = info[k]
            fpts = sorted({q for x in far for q in S.H[x]} | set(ports))
            AN = sols(far, fpts)
            on = [q for q in fpts if q in V]
            closed[k] = (on, {tuple(int(v) for v in row[[fpts.index(q) for q in on]]) for row in AN})
        ANB = sols(LB, V)                                   # B's lines (b among them) on B's points and every channel
        for k in cuts:
            b2, far, near, ports = info[k]
            keep = np.ones(len(ANB), dtype=bool)
            for j in cuts:
                if j != k:
                    on, Rj = closed[j]
                    idx = [V.index(q) for q in on]
                    keep &= np.array([tuple(int(v) for v in row[idx]) in Rj for row in ANB], dtype=bool)
            CL = ANB[keep]                                  # the closed atom before R
            npts = sorted({q for x in near for q in S.H[x]})
            ANn = sols(near, npts)                          # the real side of B, before R
            role = "receiver" if xs[k][B][0] == "P" else "emitter"
            for a in far:
                L = [x for x in far if x != a]
                fpts = sorted({q for x in L for q in S.H[x]} | set(ports))
                ANf = sols(L, fpts)
                R = {tuple(int(v) for v in row[[fpts.index(q) for q in ports]]) for row in ANf}
                pc = [V.index(q) for q in ports]
                own_rows = CL[np.array([tuple(int(v) for v in row[pc]) in R for row in CL], dtype=bool)]
                pn = [npts.index(q) for q in ports]
                near_rows = ANn[np.array([tuple(int(v) for v in row[pn]) in R for row in ANn], dtype=bool)]
                exception = role == "receiver" and len(ports) == 3 and len(R) == 6
                if exception:
                    c["receiving cuts where the relation has six patterns (removal, cut)"] += 1
                for b in LB:
                    Y = [V.index(q) for q in S.H[b]]
                    own = TL.verdict_of_near_side(own_rows, Y, S.s[b], [j for j in range(len(V)) if j not in Y])
                    Yn = [npts.index(q) for q in S.H[b]]
                    nv = TL.verdict_of_near_side(near_rows, Yn, S.s[b], [j for j in range(len(npts)) if j not in Yn])
                    ex = exact[a].get(b)
                    cre = lambda v: v is not None and any(v)  # noqa: E731
                    c["(removal, atom line) pairs"] += 1
                    c["exact = B's own verdict, far side by far side"] += ex == own
                    c["exact = B's own verdict, creation"] += cre(ex) == cre(own)
                    c["exact = the real side of B with R, far side by far side"] += ex == nv
                    if ex != own:
                        c["exact differs from B's own verdict: %s -> %s, %s" % (code_of(own), code_of(ex), role)] += 1
                    cutline = any(q in ports for q in S.H[b])
                    if exception and cutline:
                        c["... exception lines (a receiver's cut line, six patterns)"] += 1
                        # B's own masks with every deep point of the real removal's side
                        A1, A2 = join_on(own_rows, pc, ANf, [fpts.index(q) for q in ports])
                        allrows = np.concatenate([A1, A2[:, [j for j, q in enumerate(fpts) if q not in ports]]], axis=1)
                        Yf = Y
                        fv = TL.verdict_of_near_side(allrows, Yf, S.s[b], [j for j in range(allrows.shape[1]) if j not in Yf])
                        c["... exception lines where the real removal's side adds a far side to B's own verdict"] += fv != own
                        c["... exception lines where B's own verdict lacks census 6 or K4^(3) (room to add)"] += (own is not None
                                                                                                                 and not all(own))
    return c
