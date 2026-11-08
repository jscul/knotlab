"""Multi-label versions of LAST-BIT-20261108-001B's forcing_lib pieces (labels in range(len(sig)))."""
import importlib.util, itertools, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m
F = _load("last_bit_b_forcing_lib_4", ROOT / "proofs/LAST-BIT-20261108-001B/LAST-BIT-20261108-001B-P001_geometry_alone/forcing_lib.py")
D, BASE = F.D, F.BASE

def Q_of(S, sig):
    nl = len(sig)
    Q = {}
    for yi, Y in enumerate(F.G["sets"]):
        need = [(src, S.get(n, set()), max(j for j, _ in src)) for n, src in F.G["kids"][yi]]
        out, p = [], [0] * len(Y)
        def rec(j):
            if j == len(Y):
                out.append(tuple(p)); return
            for lab in range(nl):
                p[j] = lab
                if all(tuple(sig[p[jj]][mm] for jj, mm in src) in allowed for src, allowed, mj in need if mj == j):
                    rec(j + 1)
        rec(0)
        Q[yi] = out
    return Q

def parents_free(S, sig):
    """number of core collars whose centre's five children can carry a label vector that is no s(a), with collars in S (SAT, labels
    as binary words)"""
    from pysat.solvers import Cadical153
    nl = len(sig)
    nb = max(1, (nl - 1).bit_length())
    free = 0
    for yi, Y in enumerate(F.G["sets"]):
        cons = []
        var = {}
        def v(j, m, b):
            return var.setdefault((j, m, b), len(var) + 1)
        ok = True
        for n, src in F.G["kids"][yi]:
            allowed = sorted(S.get(n, ()))
            if not allowed:
                ok = False; break
            cons.append((src, allowed))
        if not ok:
            continue
        bpos = list(Y).index(BASE)
        Sv = Cadical153()
        top = [0]
        def fresh():
            top[0] += 1; return top[0] + 10 ** 6
        # labels must be < nl
        for (j, m) in {(j, m) for src, _ in cons for j, m in src} | {(bpos, m) for m in range(5)}:
            for lab in range(nl, 2 ** nb):
                Sv.add_clause([-v(j, m, b) if lab >> b & 1 else v(j, m, b) for b in range(nb)])
        for src, allowed in cons:
            ys = []
            for tup in allowed:
                y = fresh(); ys.append(y)
                for (j, m), lab in zip(src, tup):
                    for b in range(nb):
                        Sv.add_clause([-y, v(j, m, b) if lab >> b & 1 else -v(j, m, b)])
            Sv.add_clause(ys)
        for a in range(nl):
            # the centre's children differ from sig[a] somewhere
            ds = []
            for m in range(5):
                for b in range(nb):
                    lit = v(bpos, m, b)
                    ds.append(-lit if sig[a][m] >> b & 1 else lit)
            Sv.add_clause(ds)
        if Sv.solve():
            free += 1
        Sv.delete()
    return free


def Q_product(Lp, s1, s2, L1, L2):
    """the product's labelled level-one collars, from the factors' (a pair labelling's projections must lie in Q(s1), Q(s2))"""
    from forcing4 import F as _F
    Q1 = _F.Q_of(L1, s1)
    Q2 = _F.Q_of(L2, s2)
    sig = tuple(tuple(2 * s1[a][m] + s2[b][m] for m in range(5)) for a in (0, 1) for b in (0, 1))
    Q = {}
    for yi in range(len(_F.G["sets"])):
        need = [(src, Lp.get(n, set())) for n, src in _F.G["kids"][yi]]
        out = []
        for p1 in Q1.get(yi, ()):
            for p2 in Q2.get(yi, ()):
                p = tuple(2 * a + b for a, b in zip(p1, p2))
                if all(tuple(sig[p[jj]][mm] for jj, mm in src) in allowed for src, allowed in need):
                    out.append(p)
        Q[yi] = out
    return Q, sig


def arc_consistency(Q):
    """arc consistency on labelled level-one collars, with support counts (AC-4): (yi, p) stays alive while every neighbour slot of
    yi has some alive (m, p2) agreeing with p on their overlap. Same test as forcing_lib.joint's first stage, indexed."""
    from collections import defaultdict, deque
    from forcing4 import F as _F
    sup = _F.G["sup"]
    alive = {(yi, p): True for yi, ps in Q.items() for p in ps}
    # index: for each (m, pairs) the alive labellings of m grouped by their labels on the pairs' second coordinates
    keyed = {}
    def key2(m, pairs):
        k = (m, tuple(j for _, j in pairs))
        if k not in keyed:
            idx = defaultdict(set)
            for p2 in Q.get(m, ()):
                idx[tuple(p2[j] for j in k[1])].add(p2)
            keyed[k] = idx
        return k
    # watchers: which (item, slot) depend on each (m, label-projection) group
    count = {}
    watch = defaultdict(list)
    for (yi, p) in alive:
        for s, opts in sup[yi].items():
            c = 0
            for m, pairs in opts:
                k = key2(m, pairs)
                proj = tuple(p[i] for i, _ in pairs)
                grp = keyed[k].get(proj, ())
                c += len(grp)
                watch[(k, proj)].append(((yi, p), s))
            count[((yi, p), s)] = c
    dead = deque(k for k, c in count.items() if c == 0)
    killed = set()
    while dead:
        (item, s) = dead.popleft()
        if item in killed:
            continue
        killed.add(item)
        alive[item] = False
        m, p2 = item
        # every group containing p2 loses one member
        for (km, js), idx in keyed.items():
            if km != m:
                continue
            proj = tuple(p2[j] for j in js)
            grp = idx.get(proj)
            if grp is None or p2 not in grp:
                continue
            grp.discard(p2)
            for (it2, s2) in watch.get(((km, js), proj), ()):
                if it2 in killed:
                    continue
                count[(it2, s2)] -= 1
                if count[(it2, s2)] == 0:
                    dead.append((it2, s2))
    return alive


def Q_product_from(Q1, Q2, Lp, s1, s2):
    """the product's labelled level-one collars whose projections lie in the given factor sets (lists per core collar), kept when every
    child collar's labels lie in the product's law"""
    from forcing4 import F as _F
    sig = tuple(tuple(2 * s1[a][m] + s2[b][m] for m in range(5)) for a in (0, 1) for b in (0, 1))
    Q = {}
    for yi in range(len(_F.G["sets"])):
        need = [(src, Lp.get(n, set())) for n, src in _F.G["kids"][yi]]
        out = []
        for p1 in Q1.get(yi, ()):
            for p2 in Q2.get(yi, ()):
                p = tuple(2 * a + b for a, b in zip(p1, p2))
                if all(tuple(sig[p[jj]][mm] for jj, mm in src) in allowed for src, allowed in need):
                    out.append(p)
        Q[yi] = out
    return Q
