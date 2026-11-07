"""Creation along chains of Fano atoms, for CHAIN-TRANSFER-20261106-001A.

A chain is built forward. A_0 is the Fano plane with a removal (line a); each next atom is spliced at an element of the last one:
- at a point (attach_point): the new atom loses a line and emits;
- at a line (attach_line): the new atom loses a point and receives.
Every element, every lost element of the new atom and every port permutation is a letter.

The profile of a prefix at the element where the next atom will be spliced is its solutions' projection onto the element's three ports
plus up to two further points: the port relation R0 (8 bits), the singles (relations on ports + one point, 16 bits) and the pairs (ports +
two points, 32 bits). Singles and pairs are taken up to complementing and swapping the further points, and the whole profile up to
permuting the ports, which the next letter's permutation absorbs. The rest of the chain meets the prefix only at those ports, so the
next profile is a function of this one and the letter, and so are the near side's relations on a last-atom line plus up to two points,
which decide creation there (PENDANT-LINE A's two-round rule, through its local engine).

Bit layouts: a port value p = p0 + 2 p1 + 4 p2; singles bit p + 8x; pairs bit p + 8x + 16w. All signs are zero (the Fano atom's are).
"""
import collections
import functools
import importlib.util
import itertools
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


PLA = ROOT / "proofs/PENDANT-LINE-20261106-001A/PENDANT-LINE-20261106-001A-P001_creation_is_decided_at_the_gluing_line"
TBB = ROOT / "proofs/TWO-BIT-SCREEN-20261105-001B/TWO-BIT-SCREEN-20261105-001B-P001_what_screening_gives_the_brace_dictionary"
sys.path.insert(0, str(PLA))
LL = load("ct_local_lib", PLA / "local_lib.py")
CH = load("ct_chain_lib", TBB / "chain_lib.py")
SL, GL, DL = LL.SL, CH.GL, CH.DL
PY = LL.PY
F = [tuple(L) for L in GL.FANO[0]]
PERMS = list(itertools.permutations(range(3)))
assert all(s == [0, 0, 0] for s in GL.FANO[1])


# ------------------------------------------------------------------------------------------------ the local verdict
CONFIGS = {}   # k near points -> [(far side index, Local engine for one or two far classes)]
for _k in (1, 2):
    CONFIGS[_k] = []
    for _fi, (_fname, _F) in enumerate(SL.FARS):
        _reps, _rows = LL.far_classes(_F)
        for _m in (1, 2):
            for _cols in itertools.combinations(_reps, _m):
                CONFIGS[_k].append((_fi, LL.Local(_k, LL.far_relation(_rows, list(_cols)), _m)))
_cache = {1: {}, 2: {}}


def evaluate(k, masks):
    """{mask: (non-degenerate, (new knot for each far side))} for near-relation masks on Y and k further points"""
    todo = sorted({int(m) for m in masks} - set(_cache[k]))
    if todo:
        arr = np.array(todo, dtype=np.uint64)
        new = np.zeros((4, len(arr)), dtype=bool)
        ok = None
        for fi, L in CONFIGS[k]:
            A = L.analyse(arr)
            R = L.two_rounds(A)
            ok = A["ok"] if ok is None else ok
            for tri, kn in A["knot"].items():
                if A["cross"][tri]:
                    new[fi] |= A["ok"] & kn & ~R[tri]
        for j, m in enumerate(todo):
            _cache[k][m] = (bool(ok[j]), tuple(bool(new[fi][j]) for fi in range(4)))
    return {int(m): _cache[k][int(m)] for m in masks}


def verdict_from_masks(m1, m2):
    """creation per far side: some non-degenerate configuration with a crossing knot the two-round rule does not reach"""
    out = [False] * 4
    for k, ms in ((1, m1), (2, m2)):
        for m, (ok, nk) in evaluate(k, ms).items():
            if ok:
                out = [a or b for a, b in zip(out, nk)]
    return tuple(out)


def near_masks(AN, Y, sig, others):
    """the masks of a real near side's relations on Y and each one or two of the other points; None if Y shows fewer than six"""
    AN = np.asarray(AN).astype(np.int64)
    pat = {p: i for i, p in enumerate(PY)}
    yv = [tuple(int(r[Y[j]]) ^ sig[j] for j in range(3)) for r in AN]
    if len(set(yv)) != 6:
        return None
    yi = np.array([pat[v] for v in yv], dtype=np.int64)
    m1, m2 = set(), set()
    for x in others:
        m1.add(int(np.bitwise_or.reduce(np.left_shift(np.int64(1), yi * 2 + AN[:, x]))))
    for x, w in itertools.combinations(others, 2):
        m2.add(int(np.bitwise_or.reduce(np.left_shift(np.int64(1), yi * 4 + AN[:, x] + 2 * AN[:, w]))))
    return m1, m2


def verdict_of_near_side(AN, Y, sig, others):
    mm = near_masks(AN, Y, sig, others)
    return None if mm is None else verdict_from_masks(*mm)


# ------------------------------------------------------------------------------------------------ fragments
def _sub(L, old, new):
    return tuple(new if q == old else q for q in L)


def frag_init(a, e):
    """A_0: the Fano plane minus line a, with ports at element e (a point: its copies on its three lines; a line: its points)"""
    lines = [tuple(("n", q) for q in F[i]) for i in range(7)]
    keep = [i for i in range(7) if i != a]
    if e[0] == "pt":
        q = e[1]
        through = [i for i in range(7) if q in F[i]]
        for j, i in enumerate(through):
            lines[i] = _sub(lines[i], ("n", q), ("c", j))
        ports, drop = [("c", j) for j in range(3)], {("n", q)}
    else:
        assert e[1] != a
        keep.remove(e[1])
        ports, drop = [("n", q) for q in F[e[1]]], set()
    vars_ = [("n", q) for q in range(7) if ("n", q) not in drop] + [p for p in ports if p[0] == "c"]
    return dict(vars=vars_, lines=[lines[i] for i in keep], slots=None, ports=ports)


def frag_step(kind, perm, x, ep):
    """the next atom. kind 'point': the old element is a point and the new atom minus its line x emits, old slot i being its point
    F[x][perm[i]]; kind 'line': the old element is a line and the new atom minus its point x receives, its k-th line through x getting
    old slot perm[k]. ep: the new atom's element for the next splice, ('pt', q) or ('ln', l), or None for the last atom."""
    if kind == "point":
        li = x
        lines = {i: tuple(("n", q) for q in F[i]) for i in range(7) if i != li}
        slots = [("n", F[li][perm[i]]) for i in range(3)]
        atom_pts, extra = [("n", q) for q in range(7)], []
    else:
        pt = x
        through = [i for i in range(7) if pt in F[i]]
        lines = {i: (tuple(("s", perm[through.index(i)]) if q == pt else ("n", q) for q in F[i]) if pt in F[i]
                     else tuple(("n", q) for q in F[i])) for i in range(7)}
        slots = [("s", t) for t in range(3)]
        atom_pts, extra = [("n", q) for q in range(7) if q != pt], list(slots)
    if ep is None:
        return dict(vars=atom_pts + extra, lines=lines, slots=slots, ports=None)
    drop = set()
    if ep[0] == "pt":
        q = ep[1]
        assert ("n", q) in atom_pts
        thr = [i for i in sorted(lines) if ("n", q) in lines[i]]
        if kind == "point" and q in F[li]:
            # q is a port of the old cut: its copy on the old line is the old slot itself, now free of q
            i0 = [i for i in range(3) if F[li][perm[i]] == q][0]
            slots = list(slots)
            slots[i0] = ("s", i0)
            extra = [("s", i0)]
            assert len(thr) == 2
            for j, i in enumerate(thr):
                lines[i] = _sub(lines[i], ("n", q), ("c", j + 1))
            ports = [("s", i0), ("c", 1), ("c", 2)]
        else:
            assert len(thr) == 3
            for j, i in enumerate(thr):
                lines[i] = _sub(lines[i], ("n", q), ("c", j))
            ports = [("c", 0), ("c", 1), ("c", 2)]
        drop = {("n", q)}
        extra = extra + [c for c in ports if c[0] == "c"]
    else:
        assert ep[1] in lines
        ports = list(lines.pop(ep[1]))
    vars_ = [v for v in atom_pts if v not in drop] + [v for v in extra if v not in atom_pts]
    return dict(vars=vars_, lines=lines, slots=slots, ports=ports)


def solve(fr):
    vs = fr["vars"]
    idx = {v: i for i, v in enumerate(vs)}
    lines = fr["lines"].values() if isinstance(fr["lines"], dict) else fr["lines"]
    L3 = [tuple(idx[q] for q in L) for L in lines]
    sols = [m for m in range(1 << len(vs))
            if all(len({(m >> a) & 1, (m >> b) & 1, (m >> c) & 1}) == 2 for a, b, c in L3)]
    return sols, idx


def _val(m, idx, v):
    return (m >> idx[v]) & 1


def _bits3(m, idx, vs):
    return sum(_val(m, idx, v) << i for i, v in enumerate(vs))


def _tables(sols, idx, slots, target, local):
    """img[s]: target values (as a mask over 8); imgw[w][s]: masks over target + 8w; imgxw[(x, w)][s]: masks over target + 8x + 16w"""
    img = [0] * 8
    imgw = {w: [0] * 8 for w in local}
    imgxw = {k: [0] * 8 for k in itertools.combinations(local, 2)}
    for m in sols:
        s, p = _bits3(m, idx, slots), _bits3(m, idx, target)
        img[s] |= 1 << p
        for w in local:
            imgw[w][s] |= 1 << (p + 8 * _val(m, idx, w))
        for (a, b) in imgxw:
            imgxw[(a, b)][s] |= 1 << (p + 8 * _val(m, idx, a) + 16 * _val(m, idx, b))
    return tuple(img), {w: tuple(t) for w, t in imgw.items()}, {k: tuple(t) for k, t in imgxw.items()}


@functools.lru_cache(maxsize=None)
def step_tables(kind, perm, x, ep):
    fr = frag_step(kind, perm, x, ep)
    sols, idx = solve(fr)
    local = tuple(sorted({v for v in fr["vars"] if v not in fr["ports"]}, key=str))
    return _tables(sols, idx, fr["slots"], fr["ports"], local) + (local,)


@functools.lru_cache(maxsize=None)
def final_tables(kind, perm, x, b):
    fr = frag_step(kind, perm, x, None)
    sols, idx = solve(fr)
    Y = list(fr["lines"][b])
    local = tuple(sorted({v for v in fr["vars"] if v not in Y}, key=str))
    return _tables(sols, idx, fr["slots"], Y, local) + (local,)


# ------------------------------------------------------------------------------------------------ canonical forms
def canon1(r):
    return min(r, ((r & 0xFF) << 8) | (r >> 8))


def _t2(r, cx, cw, sw):
    out = 0
    for b in range(32):
        if (r >> b) & 1:
            p, x, w = b & 7, (b >> 3) & 1, (b >> 4) & 1
            if sw:
                x, w = w, x
            out |= 1 << (p + 8 * (x ^ cx) + 16 * (w ^ cw))
    return out


@functools.lru_cache(maxsize=None)
def canon2(r):
    return min(_t2(r, cx, cw, sw) for cx in (0, 1) for cw in (0, 1) for sw in (0, 1))


def _perm_p(p, pi):
    return sum(((p >> pi[i]) & 1) << i for i in range(3))


def _permute(r, nbits, pi):
    out = 0
    for b in range(nbits):
        if (r >> b) & 1:
            out |= 1 << (_perm_p(b & 7, pi) + (b & ~7))
    return out


def canon_state(st):
    kind, R0, R1, R2 = st
    best = None
    for pi in PERMS:
        cand = (kind, _permute(R0, 8, pi), tuple(sorted(canon1(_permute(r, 16, pi)) for r in R1)),
                tuple(sorted(canon2(_permute(r, 32, pi)) for r in R2)))
        if best is None or cand < best:
            best = cand
    return (best[0], best[1], frozenset(best[2]), frozenset(best[3]))


# ------------------------------------------------------------------------------------------------ profiles
@functools.lru_cache(maxsize=None)
def init_state(a, e):
    fr = frag_init(a, e)
    sols, idx = solve(fr)
    ports = fr["ports"]
    local = [v for v in fr["vars"] if v not in ports]
    R0, s1, s2 = 0, {w: 0 for w in local}, {k: 0 for k in itertools.combinations(local, 2)}
    for m in sols:
        p = _bits3(m, idx, ports)
        R0 |= 1 << p
        for w in local:
            s1[w] |= 1 << (p + 8 * _val(m, idx, w))
        for (u, v) in s2:
            s2[(u, v)] |= 1 << (p + 8 * _val(m, idx, u) + 16 * _val(m, idx, v))
    return canon_state(("point" if e[0] == "pt" else "line", R0, frozenset(canon1(r) for r in s1.values()),
                        frozenset(canon2(r) for r in s2.values())))


def _image(rel, nextra, img):
    out = 0
    for b in range(8 << nextra):
        if (rel >> b) & 1:
            pm = img[b & 7]
            for p in range(8):
                if (pm >> p) & 1:
                    out |= 1 << (p + 8 * (b >> 3))
    return out


def _carry(R0, R1, R2, img, imgw, imgxw, local):
    """relations on (target, x) and (target, x, w): deep pairs, a deep single with a local point, and two local points"""
    n1, n2 = set(), set()
    for r in R1:
        n1.add(_image(r, 1, img))
    for w in local:
        acc = 0
        for s in range(8):
            if (R0 >> s) & 1:
                acc |= imgw[w][s]
        n1.add(acc)
    for r in R2:
        n2.add(_image(r, 2, img))
    for r in R1:
        for w in local:
            acc = 0
            for b in range(16):
                if (r >> b) & 1:
                    t, xv = imgw[w][b & 7], b >> 3
                    for c in range(16):
                        if (t >> c) & 1:
                            acc |= 1 << ((c & 7) + 8 * xv + 16 * (c >> 3))
            n2.add(acc)
    for t in imgxw.values():
        acc = 0
        for s in range(8):
            if (R0 >> s) & 1:
                acc |= t[s]
        n2.add(acc)
    return n1, n2


def step(st, perm, x, ep):
    kind, R0, R1, R2 = st
    img, imgw, imgxw, local = step_tables(kind, perm, x, ep)
    n1, n2 = _carry(R0, R1, R2, img, imgw, imgxw, local)
    return canon_state(("point" if ep[0] == "pt" else "line", _image(R0, 0, img), frozenset(canon1(r) for r in n1),
                        frozenset(canon2(r) for r in n2)))


PYI = {sum(v << i for i, v in enumerate(p)): j for j, p in enumerate(PY)}


def _mask1(r):
    return sum(1 << (PYI[b & 7] * 2 + (b >> 3)) for b in range(16) if (r >> b) & 1)


def _mask2(r):
    return sum(1 << (PYI[b & 7] * 4 + ((b >> 3) & 1) + 2 * ((b >> 4) & 1)) for b in range(32) if (r >> b) & 1)


def final_relations(st, perm, x, b, deep=True):
    """masks of the near side's relations on Y (line b of the last atom) plus one or two points; None when Y shows < 6 patterns.
    deep=False keeps only the last atom's own points and its ports (no point behind the last cut)."""
    kind, R0, R1, R2 = st
    imgY, imgw, imgxw, local = final_tables(kind, perm, x, b)
    Yp = _image(R0, 0, imgY)
    if bin(Yp).count("1") != 6 or Yp & 0b10000001:
        return None
    n1, n2 = _carry(R0, R1 if deep else frozenset(), R2 if deep else frozenset(), imgY, imgw, imgxw, local)
    return {_mask1(r) for r in n1}, {_mask2(r) for r in n2}


def final_verdict(st, perm, x, b, deep=True):
    rel = final_relations(st, perm, x, b, deep)
    return None if rel is None else verdict_from_masks(*rel)


def touching(kind, x, b):
    """the touching rule for line b of the last atom: it emits at its cut (kind 'point'), or b passes through its lost point x"""
    return kind == "point" or x in F[b]


def role(kind, x, b):
    return "emitter's line" if kind == "point" else ("cut line" if x in F[b] else "intact line")


def letters(kind):
    out = []
    for perm in PERMS:
        for x in range(7):
            eps = ([("pt", q) for q in range(7)] + [("ln", l) for l in range(7) if l != x] if kind == "point"
                   else [("pt", q) for q in range(7) if q != x] + [("ln", l) for l in range(7)])
            out += [(perm, x, ep) for ep in eps]
    return out


def final_letters(kind):
    return [(perm, x, b) for perm in PERMS for x in range(7)
            for b in ([l for l in range(7) if l != x] if kind == "point" else range(7))]


def init_elements(a):
    return [("pt", q) for q in range(7)] + [("ln", l) for l in range(7) if l != a]


def initial_states():
    return {init_state(a, e) for a in range(7) for e in init_elements(a)}


def expand(st):
    return st, {step(st, *let) for let in letters(st[0])}


def closure(pool):
    """every profile reachable from the initial ones by every letter: (set, depth of first appearance, new profiles per depth)"""
    seen = set(initial_states())
    depth = {s: 0 for s in seen}
    frontier, per_depth, d = list(seen), [len(seen)], 0
    while frontier:
        d += 1
        new = []
        for st, succ in pool.imap_unordered(expand, frontier, chunksize=1):
            for s2 in succ:
                if s2 not in seen:
                    seen.add(s2)
                    depth[s2] = d
                    new.append(s2)
        per_depth.append(len(new))
        frontier = new
    return seen, depth, per_depth


# ------------------------------------------------------------------------------------------------ built chains, for validation
def kind_of(e):
    return "point" if e[0] == "pt" else "line"


def build(a, e, steps, last):
    """the chain as a space, by GL's splices: base Fano minus line a, element e; steps [(perm, x, ep)]; last (perm, x, b).
    Returns the space, the removal's index, b's index and the atom names in order."""
    S = GL.base(*GL.FANO)
    cur, kind, names = ("g", e[1]), kind_of(e), ["g"]
    for j, (perm, x, ep) in enumerate(list(steps) + [(last[0], last[1], None)]):
        name = "A%d" % (j + 1)
        S = (GL.attach_point if kind == "point" else GL.attach_line)(S, cur, GL.FANO, x, name, perm)
        names.append(name)
        if ep is not None:
            cur, kind = (name, ep[1]), kind_of(ep)
    return S, S.line(("g", a)), S.line((names[-1], last[2])), names


def random_chain(r, k):
    """a random chain of k + 1 atoms: (a, e, steps, last, kind of the last splice)"""
    a = r.randrange(7)
    e = r.choice(init_elements(a))
    kind, steps = kind_of(e), []
    for _ in range(k - 1):
        let = r.choice(letters(kind))
        steps.append(let)
        kind = kind_of(let[2])
    return a, e, steps, r.choice(final_letters(kind)), kind


def run_chain(a, e, steps):
    st, kind = init_state(a, e), kind_of(e)
    for let in steps:
        st = step(st, *let)
    return st


def prefix_ports(S, names, M):
    """for each cut along a forward-built chain: how many points the prefix (the lines of the atoms before the cut, minus the removal
    M) shares with the rest, and how many patterns it shows on them. A port missing from the shared points lies only on the removed
    line, so the prefix leaves it free."""
    own = [n if n is not None else "g" for n in S.owner]
    out = []
    for j in range(1, len(names)):
        left = [k for k in range(len(S.H)) if own[k] in names[:j] and k != M]
        right = [k for k in range(len(S.H)) if own[k] not in names[:j]]
        ports = sorted({q for k in left for q in S.H[k]} & {q for k in right for q in S.H[k]})
        pts = sorted({q for k in left for q in S.H[k]} | set(ports))
        rel = {q: i for i, q in enumerate(pts)}
        AN = solutions([tuple(rel[q] for q in S.H[k]) for k in left], [S.s[k] for k in left], len(pts))
        out.append((len(ports), len({tuple(r) for r in AN[:, [rel[q] for q in ports]]})))
    return out


def solutions(lines, signs, n, skip=None):
    """every solution, by extending assignments one point at a time (points in breadth-first order through shared lines) and
    discarding those that make a completed line constant in literals; rows in ascending code, as TL.sat_solutions gives them"""
    act = [(L, s) for i, (L, s) in enumerate(zip(lines, signs)) if i != skip]
    adj = collections.defaultdict(set)
    for L, s in act:
        for p in L:
            adj[p] |= set(L) - {p}
    order, seen = [], set()
    for start in range(n):
        if start in seen:
            continue
        seen.add(start)
        queue = [start]
        while queue:
            p = queue.pop(0)
            order.append(p)
            for q in sorted(adj[p]):
                if q not in seen:
                    seen.add(q)
                    queue.append(q)
    pos = {p: i for i, p in enumerate(order)}
    done_at = collections.defaultdict(list)
    for L, s in act:
        done_at[max(pos[p] for p in L)].append((L, s))
    rows = np.zeros((1, 0), dtype=np.int8)
    for i, p in enumerate(order):
        rows = np.concatenate([np.concatenate([rows, np.full((len(rows), 1), v, dtype=np.int8)], axis=1) for v in (0, 1)])
        for L, s in done_at[i]:
            lit = [rows[:, pos[q]] ^ s[j] for j, q in enumerate(L)]
            rows = rows[~((lit[0] == lit[1]) & (lit[1] == lit[2]))]
    out = np.zeros((len(rows), n), dtype=np.int8)
    for p in range(n):
        out[:, p] = rows[:, pos[p]]
    codes = (out.astype(np.int64) << np.arange(n)).sum(axis=1)
    return out[np.argsort(codes)]


def sat_solutions(lines, signs, n, skip=None):
    """every solution by SAT model enumeration (as BRACE-TREE C, which checked it identical to brute force on 665 cases)"""
    from pysat.solvers import Solver
    clauses = []
    for i, (L, sg) in enumerate(zip(lines, signs)):
        if i == skip:
            continue
        lit = [(q + 1) if s == 0 else -(q + 1) for q, s in zip(L, sg)]
        clauses += [lit, [-v for v in lit]]
    with Solver(name="cadical153", bootstrap_with=clauses) as s:
        codes = sorted({sum(1 << (abs(v) - 1) for v in m if 0 < v <= n) for m in s.enum_models()})
    codes = np.array(codes, dtype=np.int64)
    if len(codes) == 0:
        return np.zeros((0, n), dtype=np.int8)
    return ((codes[:, None] >> np.arange(n)) & 1).astype(np.int8)


def random_tree(r, natoms, shape="any"):
    """a random Fano tree: each new atom spliced at a random element of a random atom (the last one for a path)"""
    S = GL.base(*GL.FANO)
    atoms = ["g"]
    for j in range(1, natoms):
        name = "A%d" % j
        host = atoms[-1] if shape == "path" else r.choice(atoms)
        cands = [("pt", k) for k in S.pkey if k[0] == host] + [("ln", k) for k in S.lkey if k[0] == host]
        kind, key = r.choice(cands)
        S = (GL.attach_point if kind == "pt" else GL.attach_line)(S, key, GL.FANO, r.randrange(7), name, r.choice(PERMS))
        atoms.append(name)
    return S


def relation_by_theorem(S, t=None):
    """creation on a Fano tree by the block lemma and the touching rule: {a: {b: bool}}"""
    t = t or DL.Tree(S)
    return {a: {b: (lambda p: p[0] == "same" or p[6] != "intact")(t.place(a, b)) for b in range(len(S.H)) if b != a}
            for a in range(len(S.H))}
