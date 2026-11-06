"""Which longitude word commutes with the meridian in the independent presentation? Test via homomorphisms to S5."""
import itertools, sys
sys.path.insert(0, '.')
import knotlib as KL

def pmul(p, q):  # (p*q)(i) = p(q(i)) -- any fixed convention works for commutation tests
    return tuple(p[i] for i in q)
def pinv(p):
    r = [0] * len(p)
    for i, x in enumerate(p):
        r[x] = i
    return tuple(r)
ID = tuple(range(5))
def peval(word, img):
    out = ID
    for a, s in word:
        g = img[a] if s > 0 else pinv(img[a])
        for _ in range(abs(s)):
            out = pmul(out, g)
    return out

def homs(word, n, cls):
    K = KL.closure(word, n)
    U = K["n_arcs"]
    res = []
    for top in itertools.product(cls, repeat=n):
        img = [None] * U
        cur = list(top)
        ok = True
        for q in range(n):
            a = K["arc_at"][(0, q)]
            if img[a] is not None and img[a] != cur[q]:
                ok = False
            img[a] = cur[q]
        if not ok:
            continue
        for (L, o, ui, uo, s, pb, pa) in K["cross"]:
            xo = img[o]; xi = img[ui]
            assert xo is not None and xi is not None
            new = pmul(pmul(pinv(xo) if s > 0 else xo, xi), xo if s > 0 else pinv(xo))   # x_uo = x_o^-s x_ui x_o^s
            if img[uo] is not None and img[uo] != new:
                ok = False; break
            img[uo] = new
        if ok and all(x is not None for x in img):
            # verify all Wirtinger relations
            if all(peval([(o, -s), (ui, 1), (o, s), (uo, -1)], img) == ID for (L, o, ui, uo, s, pb, pa) in K["cross"]):
                res.append(img)
    return res, K

transp = [p for p in itertools.permutations(range(5)) if sum(1 for i in range(5) if p[i] != i) == 2]
three = [p for p in itertools.permutations(range(5)) if sum(1 for i in range(5) if p[i] != i) == 3 and pmul(pmul(p, p), p) == ID]
knots = {"trefoil s1^3": ([1, 1, 1], 2), "fig8": (KL.fig8_sum(1), 3), "5_2-ish s1^3 s2 s1^-1 s2": ([1, 1, 1, 2, -1, 2], 3),
         "3_1 # 4_1": ([1, 1, 1] + [x + (1 if x > 0 else -1) for x in KL.fig8_sum(1)], 4), "4_1#4_1": (KL.fig8_sum(2), 5)}
for name, (w, n) in knots.items():
    for cname, cls in (("transpositions", transp), ("3-cycles", three)):
        hs, K = homs(w, n, cls)
        mu = K["start_arc"]
        wr = sum(c[4] for c in K["cross"])
        res = {}
        for sgn in (+1, -1):
            lam = [(c[1], sgn * c[4]) for c in K["visits"]] + [(mu, -sgn * wr)]
            bad = sum(1 for img in hs if pmul(peval(lam, img), img[mu]) != pmul(img[mu], peval(lam, img)))
            res[sgn] = bad
        print(f"{name:28s} {cname:15s} homs={len(hs):6d} noncommuting: sign+1 -> {res[1]}, sign-1 -> {res[-1]}")
