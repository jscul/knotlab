"""CORNER-ROW-20261110-001A: test the held-out predictions P1 to P5 (committed in 128b2e30d) on the exact row at side 64, and the same
statements on the training rows. Run with the workspace's .venv (sympy factors over GF(2))."""
import json, random, sys
from pathlib import Path
from sympy import Poly, symbols
HERE = Path(__file__).resolve().parent
s = symbols('s')

def topoly(p): return Poly(sum(s**k for k in range(p.bit_length()) if (p >> k) & 1), s, modulus=2)
def toint(P):
    out = 0
    for i, a in enumerate(reversed(P.all_coeffs())):
        if int(a) % 2: out |= 1 << i
    return out
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

class Field:
    def __init__(f, r):
        f.r, f.q = r, 1 << r
        irred = lambda g: all(pmod(g, h) for h in range(2, 1 << ((g.bit_length() - 1) // 2 + 1)))
        f.mod = next(g for g in range((1 << r) + 1, 1 << (r + 1), 2) if irred(g))
    def mul(f, a, b): return pmod(pmul(a, b), f.mod)
    def pow(f, a, e):
        x = 1
        while e:
            if e & 1: x = f.mul(x, a)
            a = f.mul(a, a); e >>= 1
        return x
    def inv(f, a): return f.pow(a, f.q - 2) if a else 0
    def tr(f, a):
        t, x = 0, a
        for _ in range(f.r): t ^= x; x = f.mul(x, x)
        return t
    def kloosterman(f):
        return [sum((-1) ** f.tr(x ^ f.mul(a, f.inv(x))) for x in range(f.q)) for a in range(f.q)]
    def ev(f, poly, a):
        v, p = 0, 1
        for k in range(poly.bit_length()):
            if (poly >> k) & 1: v ^= p
            p = f.mul(p, a)
        return v

def tests(n, row):
    r = n.bit_length()
    F = Field(r)
    K = F.kloosterman()
    # P1, P2, P3
    maxexp, allsq, outside = {}, True, False
    for key, v in row.items():
        for f, e in topoly(int(v["den"], 16)).factor_list()[1]:
            fi = toint(f)
            if (r % f.degree()) != 0: outside = True
            maxexp[fi] = max(maxexp.get(fi, 0), e)
            if e % 2: allsq = False
    classes = {}
    seen = set()
    for a in range(1, F.q):
        if a in seen: continue
        orb, x = set(), a
        while x not in orb: orb.add(x); x = F.mul(x, x)
        seen |= orb
        classes[a] = K[a]
    def minpoly_of(a):
        for fi in maxexp:
            if F.ev(fi, a) == 0: return fi
        return None
    p1 = not outside and all((minpoly_of(a) is not None) == (Kv != 0) for a, Kv in classes.items())
    p3 = all(maxexp[minpoly_of(a)] == 2 * (-(-abs(Kv) // 8)) for a, Kv in classes.items() if Kv != 0 and minpoly_of(a))
    # P4: recurrence order along each wall at random points of GF(2^31)
    MOD = (1 << 31) | (1 << 3) | 1
    def m31(a, b):
        x = 0
        while b:
            if b & 1: x ^= a
            b >>= 1; a <<= 1
            if a >> 31: a ^= MOD
        return x
    def p31(a, e):
        x = 1
        while e:
            if e & 1: x = m31(x, a)
            a = m31(a, a); e >>= 1
        return x
    def e31(poly, a):
        v, p = 0, 1
        for k in range(poly.bit_length()):
            if (poly >> k) & 1: v ^= p
            p = m31(p, a)
        return v
    def bm31(seq):
        C, B, L, m, bb = [1], [1], 0, 1, 1
        for i in range(len(seq)):
            d = seq[i]
            for j in range(1, min(L, len(C) - 1) + 1): d ^= m31(C[j], seq[i - j])
            if d == 0: m += 1; continue
            coef = m31(d, p31(bb, (1 << 31) - 2)); T = C[:]
            C = C + [0] * max(0, len(B) + m - len(C))
            for j, x in enumerate(B): C[j + m] ^= m31(coef, x)
            if 2 * L <= i: L, B, bb, m = i + 1 - L, T, d, 1
            else: m += 1
        return L
    random.seed(11)
    orders = set()
    for X in "LR":
        for _ in range(2):
            s0 = random.getrandbits(31) | 2
            seq = [m31(e31(int(row[f"{X}{b}"]["num"], 16), s0), p31(e31(int(row[f"{X}{b}"]["den"], 16), s0), (1 << 31) - 2)) for b in range(n - 1)]
            orders.add(bm31(seq))
    p4 = orders == {n // 2}
    # P5
    def frac(k): return int(row[k]["num"], 16), int(row[k]["den"], 16)
    def eq_mono(a, b, e):     # rho_a = s^e rho_b
        na, da = frac(a); nb, db = frac(b)
        return pmul(na, db) == pmul(nb, da) << e
    p5 = (eq_mono(f"L{n-2}", "L0", n) and eq_mono("R1", "L0", n) and eq_mono(f"R{n-2}", "L0", 2 * n - 1) and eq_mono(f"L{n-3}", "R0", 0))
    return {"P1": p1, "P2": allsq, "P3": p3, "P4": p4, "P5": p5, "recurrence orders": sorted(orders),
            "classes with K != 0": sum(1 for Kv in classes.values() if Kv), "classes": len(classes)}

if __name__ == "__main__":
    out = {}
    train = json.load(open(HERE / "rows_training.json"))
    for n in ("4", "8", "16", "32"):
        out[n] = tests(int(n), train[n]); print(n, out[n], flush=True)
    held = json.load(open(HERE / "rows_heldout64.json"))
    out["64"] = tests(64, held["64"]); print("64 (held out)", out["64"])
    json.dump(out, open(HERE / "heldout64_tests.json", "w"), indent=1)
