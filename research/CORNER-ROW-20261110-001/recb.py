"""Does b -> rho_(X,b)(s) satisfy a short linear recurrence over GF(2)(s)? Evaluate at random points s0 of GF(2^31) and run
Berlekamp-Massey over that field; the order at a random point is the order over GF(2)(s) with high probability."""
import json, random, sys
d = json.load(open("rows_training.json"))
MOD = (1 << 31) | (1 << 3) | 1         # x^31 + x^3 + 1, irreducible over GF(2)
def mul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a >> 31: a ^= MOD
    return r
def power(a, e):
    x = 1
    while e:
        if e & 1: x = mul(x, a)
        a = mul(a, a); e >>= 1
    return x
inv = lambda a: power(a, (1 << 31) - 2)
def ev(p, s0):
    v, x = 0, 1
    for k in range(p.bit_length()):
        if (p >> k) & 1: v ^= x
        x = mul(x, s0)
    return v
def bm_field(seq):
    C, B, L, m, bb = [1], [1], 0, 1, 1
    for i in range(len(seq)):
        dlt = seq[i]
        for j in range(1, L + 1):
            if j < len(C): dlt ^= mul(C[j], seq[i - j])
        if dlt == 0:
            m += 1
        else:
            coef = mul(dlt, inv(bb))
            T = C[:]
            C = C + [0] * max(0, len(B) + m - len(C))
            for j, x in enumerate(B): C[j + m] ^= mul(coef, x)
            if 2 * L <= i:
                L = i + 1 - L; B = T; bb = dlt; m = 1
            else:
                m += 1
    return L
random.seed(5)
for n in sys.argv[1:]:
    row = d[n]; nn = int(n)
    for X in "LR":
        orders = []
        for trial in range(3):
            s0 = random.getrandbits(31) | 2
            seq = []
            for b in range(nn - 1):
                v = row[f"{X}{b}"]
                seq.append(mul(ev(int(v["num"], 16), s0), inv(ev(int(v["den"], 16), s0))))
            orders.append(bm_field(seq))
        print("n", n, X, "block: recurrence order in b at random points", orders, "of", nn - 1, "entries")
