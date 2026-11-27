"""fourclause.py: the four-clause form of the step one layer up.  FOUR-CLAUSE-20261127-001 (the form of UPPER-GROWN-20261127-001 referee R1).

Six agreement readings on pairwise disjoint carriers, in three pairs (A0, A1), (B0, B1), (C0, C1), each with a fixed
value a_i, b_j, c_k, such that (Ai, Bj, Ck) is a bond of the stage missing exactly the triple (a_i, b_j, c_k) whenever
i = j + k modulo two: four bonds.  Then for each choice of one pair as the 'both' pair, say A,
U_A = [A0 = a_0 and A1 = a_1], U_B = [B0 = b_0 or B1 = b_1], U_C = [C0 = c_0 or C1 = c_1] cannot all hold (the
referee's form).  The pattern is the same from each pair's side, so each pattern gives three upper relations, each read
on the stage's allowed states: its words, whether every pair of upper readings is free, whether some upper reading is a
function of one lower bond's three readings, and which laws are needed (removing the law lets 111 occur)."""
import itertools, collections
import numpy as np


def find_patterns(bonds, limit=None):
    """bonds: RING-BOND bond records.  Returns patterns ((A0, A1), (B0, B1), (C0, C1)), each reading a (key, value)."""
    def key(r): return (tuple(r[0]), r[1])
    T = collections.defaultdict(set)                      # ((b, vb), (c, vc)) -> {(a, va)}, unordered pair as sorted
    by = collections.defaultdict(set)                     # (a, va) -> {((b, vb), (c, vc))}
    for b in bonds:
        if len(b['missing']) != 1: continue
        rs = [key(r) for r in b['readings']]; w = [int(ch) for ch in b['missing'][0]]
        lab = [(r, v) for r, v in zip(rs, w)]
        for i in range(3):
            o = sorted(lab[:i] + lab[i + 1:])
            T[tuple(o)].add(lab[i]); by[lab[i]].add(tuple(o))
    mask = {}
    def m(x):
        if x[0] not in mask: mask[x[0]] = sum(1 << d for d in x[0][0])
        return mask[x[0]]
    out, seen = [], set()
    for a0, pairs in by.items():
        pl = sorted(pairs)
        for p, (b0, c0) in enumerate(pl):
            for (b1, c1) in pl[p + 1:]:
                ms = [m(a0), m(b0), m(c0), m(b1), m(c1)]
                if any(ms[x] & ms[y] for x, y in itertools.combinations(range(5), 2)): continue
                # A1 completes (A1, B0, C1) and (A1, B1, C0); the second pair's two readings may take either role
                for (x0, y0, x1, y1) in ((b0, c0, b1, c1), (b0, c0, c1, b1)):
                    A1 = T.get(tuple(sorted([x0, y1])), set()) & T.get(tuple(sorted([x1, y0])), set())
                    for a1 in A1:
                        if a1 == a0 or m(a1) & (ms[0] | ms[1] | ms[2] | ms[3] | ms[4]): continue
                        k = frozenset([frozenset([a0, a1]), frozenset([x0, x1]), frozenset([y0, y1])])
                        if k in seen: continue
                        seen.add(k); out.append(((a0, a1), (x0, x1), (y0, y1)))
                        if limit and len(out) >= limit: return out
    return out


def read_pattern(stage, pat, n_start):
    """the three upper relations of a pattern on the stage (a ringbond.Stage)"""
    A = stage.A
    def val(r):
        (C, lab), v = r
        b = [stage.bits(x, A) for x in C]; ag = np.ones(len(A), dtype=bool)
        for y in b[1:]: ag &= (y == b[0])
        return ag if v else ~ag
    (a0, a1), (b0, b1), (c0, c1) = pat
    V = {r: val(r) for r in (a0, a1, b0, b1, c0, c1)}
    # the four lower bonds: (A_i, B_j, C_k) with i = j + k mod 2
    lower = [(a0, b0, c0), (a0, b1, c1), (a1, b0, c1), (a1, b1, c0)]
    out = []
    pairs = [(a0, a1), (b0, b1), (c0, c1)]
    for both in range(3):
        U = [V[p[0]] & V[p[1]] if i == both else V[p[0]] | V[p[1]] for i, p in enumerate(pairs)]
        code = U[0].astype(int) * 4 + U[1].astype(int) * 2 + U[2].astype(int)
        words = sorted(set(code.tolist()))
        free = all(len({(int(x), int(y)) for x, y in zip(U[i], U[j])}) == 4 for i, j in ((0, 1), (0, 2), (1, 2)))
        read_by_one = False
        for lb in lower:
            cell = V[lb[0]].astype(int) * 4 + V[lb[1]].astype(int) * 2 + V[lb[2]].astype(int)
            for u in U:
                if len(set(zip(cell.tolist(), u.tolist()))) == len(set(cell.tolist())): read_by_one = True
        rec = {'both pair': both, 'upper words': words, 'pairs free': free, 'an upper reading read at one lower bond': read_by_one}
        if 7 not in words:
            need = []
            for q in range(len(stage.sup)):
                Sq = stage.states[stage.allowed | (stage.broken == q)]
                def v2(r):
                    (C, lab), v = r
                    b = [stage.bits(x, Sq) for x in C]; ag = np.ones(len(Sq), dtype=bool)
                    for y in b[1:]: ag &= (y == b[0])
                    return ag if v else ~ag
                W2 = {r: v2(r) for r in (a0, a1, b0, b1, c0, c1)}
                U2 = [W2[p[0]] & W2[p[1]] if i == both else W2[p[0]] | W2[p[1]] for i, p in enumerate(pairs)]
                if (U2[0] & U2[1] & U2[2]).any(): need.append(q)
            rec['laws needed'] = need; rec['a birth needed'] = any(q >= n_start for q in need)
        out.append(rec)
    return out
