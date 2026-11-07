"""How the four census far sides are glued, for GENUS-READ-20261107-001A.

The creation test splits a far side at its point 0 and glues the i-th line through that point to the i-th listed point of the gluing
line (PENDANT-LINE A's local engine, through HANDLE-LOCALITY B's far_side). A signed symmetry of the far side that fixes the split point
and permutes its three lines carries one gluing onto another, so the verdict cannot depend on the gluing line's order when every
permutation is realized. Census 6 realizes only two.
"""
import collections
import importlib.util
import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


FL = load("gr_a_far_lib", ROOT / "proofs/FAR-READ-20261106-001A/FAR-READ-20261106-001A-P001_the_far_side_map/far_lib.py")
G = FL.G
TL = G.TR.TL if hasattr(G.TR, "TL") else None
PL = load("gr_a_port_lib", ROOT / "proofs/GLUE-READ-20261106-001A/GLUE-READ-20261106-001A-P001_creation_is_decided_by_the_receiving_cut/"
          "port_lib.py")
TL = PL.TL
FARS = TL.LL.SL.FARS
ORDERS = list(itertools.permutations(range(3)))


def signed_automorphisms(H, s, n):
    """point permutations preserving the lines as sets whose signs agree after flipping some points and lines"""
    H = [tuple(l) for l in H]
    lidx = {frozenset(l): i for i, l in enumerate(H)}
    out = []
    for g in itertools.permutations(range(n)):
        img = {}
        for i, l in enumerate(H):
            j = lidx.get(frozenset(g[q] for q in l))
            if j is None:
                break
            img[i] = j
        else:
            adj = collections.defaultdict(list)
            for i, l in enumerate(H):
                for k, p in enumerate(l):
                    c = s[i][k] ^ s[img[i]][H[img[i]].index(g[p])]
                    adj[("P", p)].append((("L", i), c))
                    adj[("L", i)].append((("P", p), c))
            val, good = {}, True
            for st in adj:
                if st in val:
                    continue
                val[st] = 0
                stack = [st]
                while stack and good:
                    u = stack.pop()
                    for w, c in adj[u]:
                        if w not in val:
                            val[w] = val[u] ^ c
                            stack.append(w)
                        elif val[w] != val[u] ^ c:
                            good = False
                            break
            if good:
                out.append(g)
    return out


def symmetry_report():
    """for each far side: (name, points, signed automorphisms, sizes of point orbits, the orbit of the split point, how many of the six
    permutations of the split point's lines its stabilizer realizes)"""
    rows = []
    for name, Fs in FARS:
        H, s, n = [tuple(l) for l in Fs[0]], [list(x) for x in Fs[1]], Fs[2]
        A = signed_automorphisms(H, s, n)
        orbits = sorted({frozenset(g[p] for g in A) for p in range(n)}, key=len)
        lidx = {frozenset(l): i for i, l in enumerate(H)}
        thr = [i for i, l in enumerate(H) if 0 in l]
        acts = {tuple(lidx[frozenset(g[q] for q in H[i])] for i in thr) for g in A if g[0] == 0}
        rows.append((name, n, len(A), [len(o) for o in orbits], len(next(o for o in orbits if 0 in o)), len(acts)))
    return rows


def orders_verdicts(AN, S, b):
    """the far-side vector at gluing line b for each of the six orders of its points (None where b shows fewer than six patterns)"""
    Y, sig = list(S.H[b]), list(S.s[b])
    out = []
    for pi in ORDERS:
        Yp, sp = [Y[k] for k in pi], [sig[k] for k in pi]
        out.append(TL.verdict_of_near_side(AN, Yp, sp, [q for q in range(S.n) if q not in Yp]))
    return out


def native(vs):
    """(K4^(3), the number of orders out of six at which census 6 creates, the Fano plane, census 58); None if degenerate"""
    if vs[0] is None:
        return None
    return (vs[0][0], sum(v[1] for v in vs), vs[0][2], vs[0][3])
