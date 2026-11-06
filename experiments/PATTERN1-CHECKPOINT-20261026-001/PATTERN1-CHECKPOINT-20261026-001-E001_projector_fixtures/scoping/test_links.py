import time, itertools, math
import numpy as np
import pc_core as PC
from pc_core import Comp, BraidLayout, Diagram, cohomology, obstruction_bimap, counts_from_bimaps, P, R, smith_diagonal
from pc_build import ellipse, y_graph, leaf_bundle
import cp_lib as C

def perm_group(gens, deg):
    els = {tuple(range(deg))}; fr = list(els)
    while fr:
        new = []
        for a in fr:
            for g in gens:
                b = tuple(a[g[i]] for i in range(deg))
                if b not in els: els.add(b); new.append(b)
        fr = new
    els = sorted(els); ix = {e: i for i, e in enumerate(els)}
    mul = [[ix[tuple(a[b[i]] for i in range(deg))] for b in els] for a in els]
    inv = [ix[tuple(sorted(range(deg), key=lambda i: a[i]))] for a in els]
    return els, mul, inv

def brute(ngen, rels, mul, inv):
    G = len(mul); e = next(i for i in range(G) if all(mul[i][j] == j for j in range(G)))
    cnt = 0
    for tup in itertools.product(range(G), repeat=ngen):
        ok = True
        for rel in rels:
            x = e
            for g, s in rel:
                y = tup[g] if s > 0 else inv[tup[g]]
                for _ in range(abs(s)):
                    x = mul[x][y]
            if x != e: ok = False; break
        if ok: cnt += 1
    return cnt

A5 = perm_group([(1, 2, 0, 3, 4), (0, 1, 3, 4, 2)], 5)
S3 = perm_group([(1, 0, 2), (1, 2, 0)], 3)
assert len(A5[0]) == 60 and len(S3[0]) == 6
# V2 chirality: trefoil with framings +1 and -1, my diagram vs cp_lib's presentation, maps to A5
word, n = PC.T31
for f in (1, -1):
    L = BraidLayout(word, n)
    D = Diagram([Comp("K", L.pts, 1, f, "knot")])
    rels = D.crossing_rels + D.framing_rels()
    mine = brute(len(D.gens), rels, A5[1], A5[2])
    Uc, relc, _ = C.presentation(word, n, f)
    theirs = brute(Uc, relc, A5[1], A5[2])
    print("trefoil framing", f, "A5 maps: mine", mine, "cp_lib", theirs, "ok" if mine == theirs else "MISMATCH")
# V3 Borromean rings: link group and 0-surgery (T^3), maps to S3 (expected 138 and 48)
comps = [Comp(f"E{k}", [ellipse(k, 2 * math.pi * s / 48) for s in range(48)], 0, 0, "b") for k in range(3)]
D = Diagram(comps)
print("Borromean crossings", len(D.crossings), "lk", D.lk.tolist())
link = brute(len(D.gens), D.crossing_rels, S3[1], S3[2])
t3 = brute(len(D.gens), D.crossing_rels + D.framing_rels(), S3[1], S3[2])
print("Borromean S3 maps: link", link, "(expect 138), 0-surgery", t3, "(expect 48)")
