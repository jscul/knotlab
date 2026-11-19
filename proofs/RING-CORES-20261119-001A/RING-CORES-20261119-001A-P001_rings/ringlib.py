"""RING-CORES-20261119-001A-P001: decorated rings within five places, their counts and rates (a separate algorithm, same task).

A decorated ring of L knots (L = 5 or L >= 7) is a cyclic word over the core knots:
- ('L', b): the knot carries one hung knot (a leaf) with b spares, b in {0, 1, 2};
- ('N',): a neighbour of a leafed knot;
- ('P', a): a plain knot, with a in {0, 1} spares.

Leafed knots are at least three apart. The start realizing a word is simple:
- core knots have bare sizes, plus a for a plain knot;
- each leaf has 3 + b places.

The count is computed from the word alone, by the formula of the proof:

F(z) = sum over pieces of
  sum_{i} lambda_{i-1} sum_{m=0}^{n-1} prod_{k=i}^{i+m} v_k / (1 - W)  +  sum over leaves of z (1+z)^b,

where v_k = z (1+z)^{a_k} lambda_k, lambda_k = 1 + z (1+z)^b for a leaf on the line edge (x_k, x_{k+1}) (else 1), and
W = prod_k v_k.  Round t's count is [z^(t+1)] F."""
import itertools
import math

NS = 64  # series length


def pmul(a, b):
    c = [0] * NS
    nb = [(j, y) for j, y in enumerate(b) if y]
    for i, x in enumerate(a):
        if x:
            for j, y in nb:
                if i + j >= NS:
                    break
                c[i + j] += x * y
    return c


def padd(a, b):
    return [x + y for x, y in zip(a, b)]


def mono(coefs):
    p = [0] * NS
    for i, x in enumerate(coefs):
        p[i] = x
    return p


ONE, Z, ONEZ = mono([1]), mono([0, 1]), mono([1, 1])


def ppow(p, k):
    r = ONE
    for _ in range(k):
        r = pmul(r, p)
    return r


def series_inverse(p):
    """1 / p for p[0] = 1."""
    assert p[0] == 1
    q = [0] * NS
    q[0] = 1
    for m in range(1, NS):
        q[m] = -sum(p[k] * q[m - k] for k in range(1, m + 1))
    return q


def words(L):
    """Every decorated ring of L knots, up to rotation and reflection (canonical tuples)."""
    seen = set()
    for k in range(L // 3 + 1):
        for S in itertools.combinations(range(L), k):
            if any(min((x - y) % L, (y - x) % L) < 3 for x, y in itertools.combinations(S, 2)):
                continue
            near = {(s + d) % L for s in S for d in (-1, 1)}
            plain = [i for i in range(L) if i not in S and i not in near]
            for bs in itertools.product((0, 1, 2), repeat=k):
                for sp in itertools.product((0, 1), repeat=len(plain)):
                    w = [None] * L
                    for s, b in zip(S, bs):
                        w[s] = ('L', b)
                    for i in near:
                        w[i] = ('N',)
                    for i, a in zip(plain, sp):
                        w[i] = ('P', a)
                    w = tuple(w)
                    c = min(min(w[r:] + w[:r], tuple(reversed(w[r:] + w[:r]))) for r in range(L))
                    if c not in seen:
                        seen.add(c)
                        yield c


def pieces_of(word):
    """Pieces of the relayed map: per piece (n, a, leaves) with leaves {line edge k: [b]}."""
    L = len(word)
    out = []
    for s0 in ([0] if L % 2 else [0, 1]):
        order, k = [], s0
        while k not in order:
            order.append(k)
            k = (k + 2) % L
        n = len(order)
        a = [word[c][1] if word[c][0] == 'P' else 0 for c in order]
        leaves = {}
        for i in range(n):
            mid = (order[i] + 1) % L  # the core knot between x_i and x_{i+1} on the step-2 walk
            if (order[(i + 1) % n] - order[i]) % L == 2 and word[mid][0] == 'L':
                leaves[i] = [word[mid][1]]
        out.append((n, a, leaves))
    return out


def piece_W_N(n, a, leaves):
    lam = []
    for k in range(n):
        f = ONE
        for b in leaves.get(k, []):
            f = pmul(f, padd(ONE, pmul(Z, ppow(ONEZ, b))))
        lam.append(f)
    v = [pmul(pmul(Z, ppow(ONEZ, a[k])), lam[k]) for k in range(n)]
    W = ONE
    for k in range(n):
        W = pmul(W, v[k])
    num = [0] * NS
    for i in range(n):
        acc, prod = [0] * NS, ONE
        for m in range(n):
            prod = pmul(prod, v[(i + m) % n])
            acc = padd(acc, prod)
        num = padd(num, pmul(lam[(i - 1) % n], acc))
    loose = [0] * NS
    for bs in leaves.values():
        for b in bs:
            loose = padd(loose, pmul(Z, ppow(ONEZ, b)))
    return W, num, loose


def formula(word):
    """Per-round counts c(0..NS-2) from the closed form, the per-piece round-weights, and the rate (1 if none grows)."""
    tot = [0] * NS
    Ws = []
    for n, a, leaves in pieces_of(word):
        W, num, loose = piece_W_N(n, a, leaves)
        one_minus_W = [(1 if i == 0 else 0) - W[i] for i in range(NS)]
        tot = padd(tot, padd(pmul(num, series_inverse(one_minus_W)), loose))
        Ws.append(W)
    return [tot[t + 1] for t in range(NS - 1)], Ws


def direct(word, T):
    """The same count by summing intervals directly (the cluster description), to round T."""
    tot = [0] * NS
    for n, a, leaves in pieces_of(word):
        lam = []
        for k in range(n):
            f = ONE
            for b in leaves.get(k, []):
                f = pmul(f, padd(ONE, pmul(Z, ppow(ONEZ, b))))
            lam.append(f)
        for i in range(n):
            w = lam[(i - 1) % n]
            for j in range(i, i + T + 2):
                w = pmul(pmul(w, pmul(Z, ppow(ONEZ, a[j % n]))), lam[j % n])
                tot = padd(tot, w)
        for bs in leaves.values():
            for b in bs:
                tot = padd(tot, pmul(Z, ppow(ONEZ, b)))
    return [tot[t + 1] for t in range(T + 1)]


def rate(W):
    """The root x > 1 of W(1/x) = 1, or 1 if W = z^n."""
    f = lambda z: sum(c * z ** i for i, c in enumerate(W) if c)  # noqa: E731
    if abs(f(1.0) - 1) < 1e-12:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) < 1:
            lo = mid
        else:
            hi = mid
    return 1 / ((lo + hi) / 2)


def start_of(word, bare_sizes):
    """The simple start realizing a word: (sizes, edges)."""
    L = len(word)
    e = [tuple(sorted((i, (i + 1) % L))) for i in range(L)]
    leaf_b = []
    for c in range(L):
        if word[c][0] == 'L':
            e.append((c, L + len(leaf_b)))
            leaf_b.append(word[c][1])
    n = L + len(leaf_b)
    sizes = bare_sizes(n, e)
    for c in range(L):
        if word[c][0] == 'P':
            sizes[c] += word[c][1]
    for j, b in enumerate(leaf_b):
        sizes[L + j] += b
    return sizes, e


def bare(word):
    return all((w[0] == 'P' and w[1] == 0) for w in word)
