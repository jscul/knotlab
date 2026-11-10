"""A learner that grows only when stuck, for GROW-STUCK-20261110-001A.

The dissonance weight of a law s and a state x on a knot space is W = violated lines + E + |D| / 2 (E = sum of floor(agree / 2) over faces,
D the even faces); `weight2` returns 2W. The learner GROW-r holds x fixed. It looks at every sequence of at most r learning steps (a sign
change on a side of a violated line, or on a side with an end at an even face, A26) and takes the first step of a shortest one that lowers
W. When none does and W > 0 it grows a Fano atom at a violated line (`grow_any`, the move of GROW-HANDLE-20261110-001A on any orientable
knot space: the first bijection that lowers the Euler characteristic by 2, chirality 0, old signs kept, the atom's signs 0, the three new
sides signed to add the fewest even faces, the state extended to the atom's points by the first assignment that violates the fewest lines)."""
import importlib.util
import itertools
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_spec = importlib.util.spec_from_file_location(
    "grow_lib", ROOT / "proofs/GROW-HANDLE-20261110-001A/GROW-HANDLE-20261110-001A-P001_a_fano_atom_grown_at_the_dissonance/grow_lib.py")
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)
SL = G.SL
FANO = SL.torus(7, 2, 1)
P_STAR = next(t for t in range(FANO.nt) if FANO.colour[t] == 0)


def ends(S, K, i, k):
    t = K.lines[i]
    return S.vert[t][(k + 1) % 3], S.vert[t][(k + 2) % 3]


def tally(K, s, x):
    """(violated lines, agree per face)"""
    viol, agree = [], [0] * K.V
    for i in range(K.n):
        L = [x[K.pt[i][k]] ^ s[3 * i + k] for k in range(3)]
        if L[0] == L[1] == L[2]:
            viol.append(i)
    for v in range(K.V):
        for i, c in K.corners_at[v]:
            agree[v] += (x[K.pt[i][(c + 1) % 3]] ^ s[3 * i + (c + 1) % 3]) == (x[K.pt[i][(c + 2) % 3]] ^ s[3 * i + (c + 2) % 3])
    return viol, agree


def weight2(K, s, x):
    viol, agree = tally(K, s, x)
    return 2 * len(viol) + 2 * sum(a // 2 for a in agree) + sum(1 for a in agree if a % 2 == 0)


def steps_at(S, K, s, x):
    viol, agree = tally(K, s, x)
    even = {v for v in range(K.V) if agree[v] % 2 == 0}
    out = set(3 * i + k for i in viol for k in range(3))
    for i in range(K.n):
        for k in range(3):
            u, w = ends(S, K, i, k)
            if u in even or w in even:
                out.add(3 * i + k)
    return sorted(out)


def search(S, K, s, x, r):
    """the first step of a shortest sequence of at most r learning steps that lowers W, or None"""
    w0 = weight2(K, s, x)
    start = frozenset()
    prev, dq = {start: None}, deque([(start, 0)])
    while dq:
        node, d = dq.popleft()
        if d == r:
            continue
        cur = list(s)
        for e in node:
            cur[e] ^= 1
        for e in steps_at(S, K, cur, x):
            nxt = node ^ {e}
            if nxt in prev:
                continue
            prev[nxt] = (node, e)
            cur[e] ^= 1
            low = weight2(K, cur, x) < w0
            cur[e] ^= 1
            if low:
                first, n2 = e, nxt
                while prev[n2][0] != start:
                    n2 = prev[n2][0]
                return prev[n2][1]
            dq.append((nxt, d + 1))
    return None


def grow_any(S, s, x, l):
    """grow a Fano atom at line triangle l of S; returns (S', s', x', chi')"""
    KA = SL.KnotSpace(S)
    A = G.rotation_of(S, "A")
    R = G.rotation_of(FANO, "R")
    for sg in itertools.permutations(range(3)):
        m = G.splice(A, ("A", l), R, ("R", P_STAR), sg)
        if G.euler_of(m) == KA.chi - 2:
            break
    else:
        raise AssertionError("no bijection lowers chi by 2")
    S2 = G.build("grown", *m)
    K2 = SL.KnotSpace(S2)
    lid = {t: i for i, t in enumerate(KA.lines)}
    s2, new = [None] * (3 * K2.n), []
    for gi, gt in enumerate(K2.lines):
        for j, d in enumerate(m[1][S2.verts[gt]]):
            e = m[2][d]
            if d[0] == "A" and e[0] == "A":
                s2[3 * gi + j] = s[3 * lid[d[1]] + d[2]]
            elif d[0] == "R" and e[0] == "R":
                s2[3 * gi + j] = 0
            else:
                new.append(3 * gi + j)
    best = None
    for bits in itertools.product((0, 1), repeat=3):
        t = list(s2)
        for e, b in zip(new, bits):
            t[e] = b
        nd = len(K2.even_faces(t))
        if best is None or nd < best[0]:
            best = (nd, t)
    s2 = best[1]
    pid = {gt: i for i, gt in enumerate(K2.points)}
    gvid = {v: i for i, v in enumerate(S2.verts)}
    x2 = [None] * K2.n
    for i, t in enumerate(KA.points):
        x2[pid[gvid[("A", t)]]] = x[i]
    atom = [pid[gvid[v]] for v in S2.verts if v[0] == "R" and S2.colour[gvid[v]] == 0]
    arg = None
    for bits in itertools.product((0, 1), repeat=len(atom)):
        y = list(x2)
        for p, b in zip(atom, bits):
            y[p] = b
        v = len(tally(K2, s2, y)[0])
        if arg is None or v < arg[0]:
            arg = (v, y)
    return S2, s2, arg[1], K2.chi


def grow_r(S, s, x, r, cap_growths=3, cap_steps=60):
    """run GROW-r; returns a record of what it did, with W checked against |chi| / 2 at every configuration"""
    S, s, x = S, list(s), list(x)
    rec = {"growths": [], "sign changes": 0, "floor respected": True, "first decision stuck": None}
    while True:
        K = SL.KnotSpace(S)
        w2 = weight2(K, s, x)
        rec["floor respected"] &= w2 >= abs(K.chi)
        if w2 == 0:
            rec["resolved"] = True
            break
        if rec["sign changes"] >= cap_steps:
            rec["resolved"] = False
            rec["stopped"] = "step cap"
            break
        e = search(S, K, s, x, r)
        if rec["first decision stuck"] is None:
            rec["first decision stuck"] = e is None
        if e is not None:
            s[e] ^= 1
            rec["sign changes"] += 1
            continue
        if len(rec["growths"]) >= cap_growths:
            rec["resolved"] = False
            rec["stopped"] = "stuck at the growth cap"
            break
        viol, agree = tally(K, s, x)
        if viol:
            i = viol[0]
            at = "violated line"
        else:
            even = {v for v in range(K.V) if agree[v] % 2 == 0}
            i = next(i for i in range(K.n) if any(S.vert[K.lines[i]][c] in even for c in range(3)))
            at = "line at an even face"
        rec["growths"].append({"at": at, "line": K.lines[i], "chi before": K.chi, "W before": w2 / 2,
                               "after sign changes": rec["sign changes"]})
        S, s, x, chi = grow_any(S, s, x, K.lines[i])
    K = SL.KnotSpace(S)
    rec["chi"] = K.chi
    rec["W"] = weight2(K, s, x) / 2
    return rec
