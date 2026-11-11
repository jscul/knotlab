"""For a training side n = 2^m: the irreducible factors of the row's reduced denominators (in s), their exponents per entry, and the
Kloosterman sum K(a) at their roots in GF(2n)."""
import json, sys
from sympy import Poly, symbols
s = symbols('s')
n = int(sys.argv[1]); r = n.bit_length()      # GF(2n) = GF(2^(m+1)), m + 1 = bit_length of n
d = json.load(open("rows_training.json"))[str(n)]
def topoly(p): return Poly(sum(s**k for k in range(p.bit_length()) if (p >> k) & 1), s, modulus=2)
def toint(P):
    c = P.all_coeffs(); out = 0
    for i, a in enumerate(reversed(c)):
        if int(a) % 2: out |= 1 << i
    return out
# field arithmetic
def pmod(a, b):
    db = b.bit_length() - 1
    while a and a.bit_length() - 1 >= db: a ^= b << (a.bit_length() - 1 - db)
    return a
def pmul(a, b):
    x = 0
    while b:
        if b & 1: x ^= a
        a <<= 1; b >>= 1
    return x
def irred(f):
    dd = f.bit_length() - 1
    return all(pmod(f, g) for g in range(2, 1 << (dd // 2 + 1)))
mod = next(f for f in range((1 << r) + 1, 1 << (r + 1), 2) if irred(f))
mul = lambda a, b: pmod(pmul(a, b), mod)
def power(a, e):
    x = 1
    while e:
        if e & 1: x = mul(x, a)
        a = mul(a, a); e >>= 1
    return x
q = 1 << r
inv = lambda a: power(a, q - 2) if a else 0
def tr(a):
    t, x = 0, a
    for _ in range(r): t ^= x; x = mul(x, x)
    return t
Ktab = [sum((-1) ** tr(x ^ mul(a, inv(x))) for x in range(q)) for a in range(q)]
def evalp(f, a):
    v, p = 0, 1
    for k in range(f.bit_length()):
        if (f >> k) & 1: v ^= p
        p = mul(p, a)
    return v
factors = {}
per = {}
for key, v in d.items():
    fl = topoly(int(v["den"], 16)).factor_list()[1]
    per[key] = {}
    for f, e in fl:
        fi = toint(f)
        if fi not in factors:
            rts = [a for a in range(q) if evalp(fi, a) == 0]
            factors[fi] = (f.degree(), sorted(set(Ktab[a] for a in rts)), sorted(set(tr(a) for a in rts)))
        per[key][fi] = e
print("n =", n, "GF(2^%d)" % r)
# all classes with K != 0 vs the factors seen
seen = set(factors)
allK = {}
done = set()
for a in range(1, q):
    if a in done: continue
    orb = set(); x = a
    while x not in orb: orb.add(x); x = mul(x, x)
    done |= orb
    allK.setdefault(Ktab[a], 0); allK[Ktab[a]] += 1
print("classes by K value (nonzero elements):", dict(sorted(allK.items())))
for fi, (deg, Ks, trs) in sorted(factors.items(), key=lambda t: t[1][1]):
    exps = sorted(set(per[k].get(fi, 0) for k in per))
    print("  factor deg %d K %s Tr %s : exponents over entries %s, in %d of %d entries" % (deg, Ks, trs, exps, sum(1 for k in per if fi in per[k]), len(per)))
