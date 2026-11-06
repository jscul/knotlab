"""Linear algebra over the local ring Z/p^k: Smith form with transforms, cokernel classes, all solutions, circuits."""
import itertools, math

def val(x, p, k):
    x %= p ** k
    if x == 0:
        return k
    v = 0
    while x % p == 0:
        x //= p
        v += 1
    return v

def snf_local(A, p, k):
    """P A Q = D (mod p^k), P, Q invertible mod p^k, D diagonal with entries p^v; returns valuations, P, Q"""
    q = p ** k
    A = [[x % q for x in row] for row in A]
    n, m = len(A), len(A[0]) if A else 0
    P = [[int(i == j) for j in range(n)] for i in range(n)]
    Q = [[int(i == j) for j in range(m)] for i in range(m)]
    vals = []
    for t in range(min(n, m)):
        best = None
        for i in range(t, n):
            for j in range(t, m):
                v = val(A[i][j], p, k)
                if v < k and (best is None or v < best[0]):
                    best = (v, i, j)
        if best is None:
            vals += [k] * (min(n, m) - t)
            break
        v, i, j = best
        A[t], A[i] = A[i], A[t]
        P[t], P[i] = P[i], P[t]
        for r in A:
            r[t], r[j] = r[j], r[t]
        for r in Q:
            r[t], r[j] = r[j], r[t]
        u = (A[t][t] // p ** v) % q
        ui = pow(u, -1, q)
        A[t] = [(x * ui) % q for x in A[t]]
        P[t] = [(x * ui) % q for x in P[t]]
        pv = p ** v
        for i in range(n):
            if i != t and A[i][t]:
                w = (A[i][t] // pv) % q
                A[i] = [(a - w * b) % q for a, b in zip(A[i], A[t])]
                P[i] = [(a - w * b) % q for a, b in zip(P[i], P[t])]
        for j in range(m):
            if j != t and A[t][j]:
                w = (A[t][j] // pv) % q
                for r in A:
                    r[j] = (r[j] - w * r[t]) % q
                for r in Q:
                    r[j] = (r[j] - w * r[t]) % q
        vals.append(v)
    return vals, P, Q, A

def coker(A, p, k):
    """cokernel of a square A over Z/p^k: component orders, and the class map"""
    n = len(A)
    vals, P, Q, D = snf_local(A, p, k)
    comps = [i for i in range(n) if vals[i] >= 1]
    g = [p ** vals[i] for i in comps]
    def cls(vec):
        return tuple(sum(P[i][j] * vec[j] for j in range(n)) % gi for i, gi in zip(comps, g))
    return g, cls

def order_of(x, g):
    o = 1
    for xi, gi in zip(x, g):
        o = math.lcm(o, gi // math.gcd(xi, gi))
    return o

def cyclic_span(x, g):
    S, y = set(), tuple(0 for _ in x)
    while y not in S:
        S.add(y)
        y = tuple((a + b) % gi for a, b, gi in zip(y, x, g))
    return S

def global_classes(A, p, k):
    n = len(A)
    g, cls = coker(A, p, k)
    gens = [cls([int(j == L) for j in range(n)]) for L in range(n)]
    inter = None
    for x in gens:
        s = cyclic_span(x, g)
        inter = s if inter is None else inter & s
    zero = tuple(0 for _ in g)
    return g, gens, sorted(inter - {zero}) if inter else []

def solutions(rows, rhs, p, k, n):
    """all x in (Z/p^k)^n with rows x = rhs"""
    q = p ** k
    if not rows:
        return [tuple(t) for t in itertools.product(range(q), repeat=n)]
    m = len(rows)
    vals, P, Q, D = snf_local(rows, p, k)
    b = [sum(P[i][j] * rhs[j] for j in range(m)) % q for i in range(m)]
    choices = []
    for i in range(n):
        if i < len(vals):
            v = vals[i]
            pv = p ** v
            if b[i] % pv:
                return []
            base = (b[i] // pv) % q if v < k else 0
            step = p ** (k - v) if v < k else 1
            cnt = pv if v < k else q
            choices.append([(base + step * s) % q for s in range(cnt)])
        else:
            choices.append(list(range(q)))
    for i in range(len(vals), m):
        if b[i] % q:
            return []
    out = set()
    for w in itertools.product(*choices):
        out.add(tuple(sum(Q[i][j] * w[j] for j in range(n)) % q for i in range(n)))
    return sorted(out)

def circuits(sol, n):
    ranges = [len({s[v] for s in sol}) for v in range(n)]
    cons = []
    for r in range(1, n + 1):
        for Y in itertools.combinations(range(n), r):
            prod = 1
            for v in Y:
                prod *= ranges[v]
            if prod > 1 and len({tuple(s[v] for v in Y) for s in sol}) < prod:
                cons.append(frozenset(Y))
    return [C for C in cons if not any(D < C for D in cons)]
