"""Hidden points and screening, for TWO-BIT-SCREEN-20261105-001A.

A near side is a complement-closed set of assignments (rows) on its points. Hidden points are extra near points attached through some
of the others: a receiving side (a knot space split at a point, standing in for a line), an abstract gadget given by its relation to a
line's three points, or a pendant line (one new point on one new not-all-equal line through two near points). The creation test is
join_lib's: splice the gluing line into a census far side and look for new crossing knots of up to three points (classes of tied points),
new meaning outside the elimination closure of the non-crossing knots.
"""
import collections
import itertools
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/NATIVE-GENUS-20261104-001A/NATIVE-GENUS-20261104-001A-P001_the_creation_map_splits_by_atom"))
import genus_lib as GL  # noqa: E402

G, J, E, CL = GL.G, GL.J, GL.E, GL.CL
FARS = GL.FARS


def bits(m):
    return [q for q in range(m.bit_length()) if m >> q & 1]


# ------------------------------------------------------------------------------------------------ the closure behind creation
def closure_data(AN, H, s, n_near, l, F):
    """the splice of a near side (rows AN on n_near points, line l of H kept) into far side F at line l: circuits up to three points,
    tie classes, knots (raw masks), class sets, crossing flags, base classes and the closure (elim_lib.closure), as a dict"""
    lines, signs, far, AF = J.far_side(G, H, s, n_near, l, *F)
    Y = list(H[l])
    n = n_near + F[2] - 1
    cs = J.circuits(AN, list(range(n_near)), AF, far, Y, 3)
    masks = [sum(1 << q for q in K) for K in cs]
    rep = E.tie_classes(n, [m for m in masks if bin(m).count("1") == 2])
    knots = [m for m in masks if bin(m).count("1") >= 3]
    inner = sum(1 << q for q in range(n_near) if q not in Y)
    outer = sum(1 << q for q in far)
    can = {m: E.canon(m, rep) for m in knots}
    cross = {m: bool(m & inner and m & outer) for m in knots}
    base = {can[m] for m in knots if not cross[m]}
    cset = set(can.values())
    gen = E.closure(cset, base, n)
    return dict(n=n, far=far, Y=Y, rep=rep, knots=knots, can=can, cross=cross, base=base, cset=cset, gen=gen,
                new={can[m] for m in knots if cross[m] and can[m] not in gen})


def tetra_closure(cset, base):
    """the least set containing base such that every four classes with two of their triples in the set have every triple that is a knot
    (in cset) in the set; computed independently of elim_lib"""
    cset = set(cset)
    gen = set(base) & cset
    pts = sorted({q for T in cset for q in bits(T)})
    by_pair = collections.defaultdict(set)
    for T in cset:
        for a, b in itertools.combinations(bits(T), 2):
            by_pair[(a, b)].add(T)
    changed = True
    while changed:
        changed = False
        for T in list(gen):
            for a, b in itertools.combinations(bits(T), 2):
                c = (T & ~(1 << a) & ~(1 << b)).bit_length() - 1
                # four-sets T + h through the pair (a, b): the other triple through a, b is {a, b, h}
                for U in list(by_pair[(a, b)]):
                    if U == T or U not in gen:
                        continue
                    h = (U & ~(1 << a) & ~(1 << b)).bit_length() - 1
                    Q = T | (1 << h)
                    for x in (a, b, c, h):
                        F = Q & ~(1 << x)
                        if F in cset and F not in gen:
                            gen.add(F)
                            changed = True
    return gen


def new_knots(AN, H, s, n_near, l, F):
    return J.new_knots(E, G, AN, H, s, n_near, l, F, 3)[0]


def split_new(newS, n_vis, n_hid):
    """new knots of a near side whose points are n_vis visible ones followed by n_hid hidden ones (then far points): (the new knots
    avoiding hidden points, relabelled as in the space without them; the new knots through hidden points)"""
    out, through = [], []
    for m in newS:
        o, hit = 0, False
        for q in bits(m):
            if q < n_vis:
                o |= 1 << q
            elif q >= n_vis + n_hid:
                o |= 1 << (q - n_hid)
            else:
                hit = True
        (through if hit else out).append(m if hit else o)
    return sorted(out), through


# ------------------------------------------------------------------------------------------------ hidden points
def gadget(Q, p):
    """a knot space Q split at its point p: rows on Q's points with p's column unused, plus three port columns n, n+1, n+2 (the copies of
    p on its three lines, in line order); returns (rows as int tuples, port columns, interior points)"""
    H, s, n = Q
    through = [i for i, m in enumerate(H) if p in m]
    lines = [tuple((n + through.index(i)) if q == p else q for q in m) for i, m in enumerate(H)]
    A = CL.solutions(lines, s, n + 3)
    rows = [tuple(int(x) for x in r) for r in A]
    return rows, [n, n + 1, n + 2], [q for q in range(n) if q != p]


def exclusions(rows, ports, pts):
    """for a set of interior points and each value pattern on them, the port patterns no row shows together with it"""
    P = sorted({tuple(r[q] for q in ports) for r in rows})
    seen = collections.defaultdict(set)
    for r in rows:
        seen[tuple(r[q] for q in pts)].add(tuple(r[q] for q in ports))
    return P, {v: set(P) - seen[v] for v in itertools.product((0, 1), repeat=len(pts))}


def subcube(S, P):
    """S (port patterns) equals {x in P : x agrees with some fixed values on some ports}, or is empty"""
    S = set(S)
    if not S:
        return True
    fixed = [i for i in range(3) if len({x[i] for x in S}) == 1]
    val = {i: next(iter(S))[i] for i in fixed}
    return S == {x for x in P if all(x[i] == val[i] for i in fixed)}


def exclusion_type(S, P):
    """empty, a subcube named by its size (one pattern, two patterns = two ports fixed unequal, three patterns = one port fixed), an
    antipodal class, or other"""
    S = set(S)
    if not S:
        return "empty"
    if subcube(S, P):
        return "subcube of %d" % len(S)
    if len(S) == 2 and all(tuple(1 - b for b in x) in S for x in S):
        return "antipodal class"
    return "other (%d patterns)" % len(S)


def extend(AN, X, R):
    """join near rows AN with an abstract gadget R: {raw pattern on the points X: list of hidden-value tuples}"""
    rows = []
    for r in AN:
        x = tuple(int(r[q]) for q in X)
        for b in R.get(x, []):
            rows.append(list(r) + list(b))
    return np.array(rows, dtype=np.int8)


def pendant(AN, s_, u_, sig):
    """one new point b after the near points, on the not-all-equal line (b + sig0, s + sig1, u + sig2)"""
    rows = []
    for r in AN:
        ls, lu = int(r[s_]) ^ sig[1], int(r[u_]) ^ sig[2]
        for bv in (0, 1):
            if not (bv ^ sig[0] == ls == lu):
                rows.append(list(r) + [bv])
    return np.array(rows, dtype=np.int8)


def profile_gadget(sig, prof):
    """the one-point gadget with a given profile on L0 (signs sig): for each antipodal class of literal patterns (named by the odd port),
    the hidden point is free, the majority or the minority"""
    P = [t for t in itertools.product((0, 1), repeat=3) if t != sig and t != tuple(1 - b for b in sig)]
    R = {}
    for x in P:
        L = tuple(a ^ b for a, b in zip(x, sig))
        odd = [i for i in range(3) if L[i] != L[(i + 1) % 3] and L[i] != L[(i + 2) % 3]][0]
        maj = L[(odd + 1) % 3]
        t = prof[odd]
        R[x] = [(0,), (1,)] if t == "free" else [(maj,)] if t == "majority" else [(1 - maj,)]
    return R, P


def two_point_gadgets(sig):
    """every complement-closed two-point gadget on L0's six patterns whose single points have subcube exclusion sets, up to swapping and
    complementing the two hidden points"""
    P = [t for t in itertools.product((0, 1), repeat=3) if t != sig and t != tuple(1 - b for b in sig)]
    reps = []
    for x in P:
        if tuple(1 - b for b in x) not in reps:
            reps.append(x)
    subsets = [S for r in range(1, 5) for S in itertools.combinations(list(itertools.product((0, 1), repeat=2)), r)]
    seen, out = set(), []
    for choice in itertools.product(subsets, repeat=3):
        R = {}
        for x, S in zip(reps, choice):
            R[x] = sorted(S)
            R[tuple(1 - b for b in x)] = sorted(tuple(1 - c for c in t) for t in S)
        forms = []
        for sw in (False, True):
            for c1 in (0, 1):
                for c2 in (0, 1):
                    forms.append(tuple(tuple(sorted(((t[1] if sw else t[0]) ^ c1, (t[0] if sw else t[1]) ^ c2) for t in R[x])) for x in P))
        key = min(forms)
        if key in seen:
            continue
        seen.add(key)
        ok = all(subcube({x for x in P if all(t[k] != v for t in R[x])}, P) for k in range(2) for v in (0, 1))
        if ok:
            out.append(R)
    return out, P


def pair_types(R, P):
    """exclusion types of the four value pairs of a two-point gadget"""
    return [("subcube" if subcube(S, P) else "antipodal" if (len(S) == 2 and all(tuple(1 - b for b in x) in S for x in S)) else "other")
            for S in ({x for x in P if v not in R[x]} for v in itertools.product((0, 1), repeat=2))]


def compare_hidden(AN_closed, AN_hidden, H, s, n, n_hid, l, F):
    """creation with and without hidden points at gluing line l and far side F: (W-new equal, creation equal, closed creates, hidden
    creates, new knots through hidden points exist)"""
    newN = new_knots(AN_closed, H, s, n, l, F)
    newS = new_knots(AN_hidden, H, s, n + n_hid, l, F)
    inW, through = split_new(newS, n, n_hid)
    return inW == sorted(newN), bool(newS) == bool(newN), bool(newN), bool(newS), bool(through)


def local_closure(points, cset, seed):
    """the tetrahedron closure inside a point set, seeded"""
    pts = sorted(set(points))
    tri = {sum(1 << q for q in t) for t in itertools.combinations(pts, 3)} & set(cset)
    gen = {t for t in tri if t in seed}
    changed = True
    while changed:
        changed = False
        for Q in itertools.combinations(pts, 4):
            qm = sum(1 << q for q in Q)
            fk = [qm & ~(1 << q) for q in Q if (qm & ~(1 << q)) in tri]
            if sum(1 for f in fk if f in gen) >= 2:
                for f in fk:
                    if f not in gen:
                        gen.add(f)
                        changed = True
    return gen


def restricted_closure(cset, base, n, allowed):
    """elim_lib.closure, eliminating only through the classes in allowed"""
    gen = set(base)
    targets = sorted(set(cset) - gen)
    while targets:
        through = {h: [A for A in gen if A >> h & 1] for h in allowed}
        added, kept = [], []
        for T in targets:
            ok = False
            for h in allowed:
                if T >> h & 1:
                    continue
                goal = T | (1 << h)
                inside = [A for A in through[h] if (A & ~goal) == 0]
                if any(A | B == goal for A, B in itertools.combinations(inside, 2)):
                    ok = True
                    break
            (added if ok else kept).append(T)
        if not added:
            break
        gen.update(added)
        targets = kept
    return gen
