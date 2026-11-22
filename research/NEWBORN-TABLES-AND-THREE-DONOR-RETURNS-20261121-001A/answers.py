"""Exact three-reader tables and checkable 64-list explanations."""
from fractions import Fraction as F
from functools import cache
from itertools import product
from math import gcd, lcm, prod

BITS = tuple(product((0, 1), repeat=3))
LISTS = tuple(product((0, 1), repeat=6))
INDEX = {row: i for i, row in enumerate(BITS)}
DETERMINISTIC = tuple(tuple(INDEX[tuple(row[2*i+s[i]] for i in range(3))]
                            for s in BITS) for row in LISTS)


def bits_to_int(t):
    return sum(b << (len(t)-1-i) for i, b in enumerate(t))


def joint(gram):
    """Expand products of the three two-answer indicators into signed moments."""
    trace = sum(gram[i][i] for i in range(8))
    if not trace:
        raise ValueError("zero-weight branch")
    rows = []
    for setting in range(8):
        moments = []
        for keep in range(8):
            flip = setting & keep
            read = (7 ^ setting) & keep
            signed = sum((-1)**((w & read).bit_count()) * gram[w][w ^ flip]
                         for w in range(8))
            moments.append(F(signed, trace))
        terms = tuple(sum((-1)**((a & keep).bit_count()) * moments[keep]
                          for keep in range(8))/8 for a in range(8))
        assert sum(terms) == 1 and min(terms) >= 0
        rows.append(terms)
    return tuple(rows)


def reconstruct(weights):
    out = [[F(0) for _ in range(8)] for _ in range(8)]
    for weight, picks in zip(weights, DETERMINISTIC):
        for s, a in enumerate(picks):
            out[s][a] += weight
    return tuple(tuple(row) for row in out)


def sign_score(rows, plus=False):
    moments = [sum((-1)**a.bit_count()*p for a,p in enumerate(row)) for row in rows]
    return moments[7] + (1 if plus else -1)*sum(moments[s] for s in (1,2,4))


def z_mixed(a):
    return a not in (0,7)


def forbidden(s,a):
    return s.bit_count() == 1 and bool(a & s) and (a & (7 ^ s)).bit_count() == 1


def inequality(coeff, rows):
    values = [sum(coeff[s][a] for s,a in enumerate(picks)) for picks in DETERMINISTIC]
    val = sum(c*p for cr,pr in zip(coeff,rows) for c,p in zip(cr,pr))
    return {"type":"separating inequality", "coefficients":coeff,
            "deterministic_values":values, "maximum":max(values), "minimum":min(values),
            "table_value":val, "gap":val-max(values)}


BOUND = [[int(s == 0 and z_mixed(a)) - int(s == 7 and a.bit_count() <= 1)
          - int(forbidden(s,a)) for a in range(8)] for s in range(8)]


def symmetric_weights(rows, use_one=True):
    """Use the complement/permutation symmetry only when all raw cells agree."""
    px = rows[7]
    m = sum(rows[0][1:7])
    plus = min(m,px[0])
    one = m - plus
    singles = sum(px[1<<i] for i in range(3))
    if one and (not use_one or one > singles):
        return None
    weights = []
    for row in LISTS:
        z, x = row[::2], row[1::2]
        i = bits_to_int(x)
        selected = plus if i == 0 else (one*px[i]/singles if one and sum(x) == 1 else 0)
        if len(set(z)) == 1:
            weight = (px[i]-selected)/2
        elif i == 0:
            weight = plus/6
        elif sum(x) == 1 and z[x.index(1)] == (1 if sum(z) == 1 else 0):
            # The negative X belongs on the ordinary minority position.
            weight = selected/2
        else:
            weight = 0
        weights.append(F(weight))
    assert all(w>=0 for w in weights) and sum(weights)==1
    return weights if reconstruct(weights) == rows else None


def product_weights(rows):
    return [rows[0][bits_to_int(t[::2])]*rows[7][bits_to_int(t[1::2])] for t in LISTS]


def _lp_certificate(rows):
    """A floating search proposes support; only exact rational arithmetic issues a verdict."""
    import numpy as np
    import sympy as sp
    from scipy.optimize import linprog

    data = np.zeros((64,64),dtype=int)
    for i,picks in enumerate(DETERMINISTIC):
        for s,a in enumerate(picks):
            data[8*s+a,i] = 1
    target = [p for row in rows for p in row]
    target_f = np.array(list(map(float,target)))
    res = linprog(np.zeros(64), A_eq=data, b_eq=target_f, bounds=(0,None), method="highs")
    if res.success:
        ix = np.flatnonzero(res.x>1e-10)
        support = sp.Matrix(data[:,ix].tolist())
        sol,free = support.gauss_jordan_solve(sp.Matrix(target))
        if free:
            sol = sol.subs({q:0 for q in free})
        weights = [F(0)]*64
        for i,v in zip(ix,sol):
            weights[int(i)] = F(int(v.p),int(v.q))
        assert sum(weights)==1 and min(weights)>=0 and reconstruct(weights)==rows
        return {"type":"common", "construction":"exact feasible support", "weights":weights}
    dual = linprog(-target_f, A_ub=data.T, b_ub=np.zeros(64), bounds=(-1,1), method="highs")
    assert dual.success
    coef = [F(float(x)).limit_denominator(1000000) for x in dual.x]
    den = lcm(*(x.denominator for x in coef))
    ints = [int(den*x) for x in coef]
    unit = gcd(*ints)
    answer = inequality([[v//unit for v in ints[i:i+8]] for i in range(0,64,8)],rows)
    assert answer["gap"]>0
    return answer


@cache
def certify(rows):
    bad = inequality(BOUND,rows)
    if bad["gap"]>0:
        return bad
    weights = symmetric_weights(rows)
    if weights is not None:
        return {"type":"common", "construction":"ordinary minority assigned to eligible change list",
                "weights":weights}
    weights = product_weights(rows)
    if reconstruct(weights)==rows:
        return {"type":"common", "construction":"independent ordinary and change sign words",
                "weights":weights}
    return _lp_certificate(rows)


def gram_from_vectors(vectors):
    out = [[0]*8 for _ in range(8)]
    for w,v in vectors:
        for i,x in enumerate(v):
            for j,y in enumerate(v):
                out[i][j] += w*x*y
    return out


def all_physical_words(rows, law, marks):
    """Direct exhaustive full-support reduction for small historical controls."""
    names = sorted(set(i for row in rows for i in row))
    used = [v for row in rows for v in row]
    loose = [v for v in names if used.count(v)==1]
    # The retained table is defined even for a marked name now spent.
    idx = {v:i for i,v in enumerate(names)}
    rr = [tuple(idx[v] for v in r) for r in rows]
    orthogonal = {}
    counts = {}
    for word in product((0,1), repeat=len(names)):
        if not all((sum(word[i] for i in r)%2==0 if law=='parity' else
                    0<sum(word[i] for i in r)<len(r)) for r in rr):
            continue
        x = bits_to_int(tuple(word[idx[v]] for v in marks))
        h = tuple(word[idx[v]] for v in names if v not in marks)
        orthogonal.setdefault(h,[0]*8)[x] = 1
        if set(marks).issubset(loose):
            unasked = tuple(word[idx[v]] for v in loose if v not in marks)
            counts.setdefault(unasked,[0]*8)[x] += 1
    d = gram_from_vectors((1,v) for v in orthogonal.values())
    q = gram_from_vectors((1,v) for v in counts.values()) if counts else None
    return d,q
