"""Post hoc check by the thread, 2026-11-23, after ticket C had closed.  Exploratory; not frozen, not the engine.

Ticket C found no hidden pair above 2 with two holders per distinction, and named the missing operation: handing one
value to two users.  This script allows some internal distinctions three or four holders and builds the 20/9
distribution of ticket C from parity and not-all-equal knots of three places.  Ordinary growth never makes a
distinction with more than two holders.

Alice's side (13 knots), with x1, x2, x3 each held once so that a birth can still take them:
  even(x1,a,b) even(c1,a,b) even(k1,a,b)            c1 = k1 = x1               (a, b held three times)
  even(x2,d,e) odd(x3,d,e) even(c2,d,e) odd(c3,d,e) x3 != x2, c2 = x2, c3 = x3 (d, e held four times)
  nae(c1,c2,n2)  nae(k1,c3,n1)                      x1 = x2 forces n2 != x1;  x1 = x3 forces n1 != x1
  even(n2,g,h) odd(s2,g,h)   even(n1,u,v) odd(s1,u,v)   s2 != n2, s1 != n1
Bob's side (5 knots):
  even(y1,p,q) even(s1,p,q)                         s1 = y1
  even(y2,r,t) even(s2,r,t) odd(y3,r,t)             s2 = y2, y3 != y2          (r, t held three times)
"""
import itertools, importlib.util
import numpy as np
src = open('docs/prompts/missed_leads_checks/finished_weighting_chsh.py').read().split('# ---- 1.')[0]
ns = {}; exec(src, ns)
def side(names, knots, own, cut):
    idx = {n: i for i, n in enumerate(names)}
    T = np.zeros((8, 4), dtype=np.int64)
    for w in itertools.product((0, 1), repeat=len(names)):
        ok = True
        for law, mem in knots:
            v = [w[idx[m]] for m in mem]
            if law == 'nae': good = not (v[0] == v[1] == v[2])
            else: good = (sum(v) % 2 == (0 if law == 'even' else 1))
            if not good: ok = False; break
        if ok: T[w[idx[own[0]]] * 4 + w[idx[own[1]]] * 2 + w[idx[own[2]]], w[idx[cut[0]]] * 2 + w[idx[cut[1]]]] += 1
    return T
A_names = 'x1 x2 x3 s1 s2 a b c1 k1 d e c2 c3 n1 n2 g h u v'.split()
A_knots = [('even', ('x1','a','b')), ('even', ('c1','a','b')), ('even', ('k1','a','b')),
           ('even', ('x2','d','e')), ('odd', ('x3','d','e')), ('even', ('c2','d','e')), ('odd', ('c3','d','e')),
           ('nae', ('c1','c2','n2')), ('nae', ('k1','c3','n1')),
           ('even', ('n2','g','h')), ('odd', ('s2','g','h')), ('even', ('n1','u','v')), ('odd', ('s1','u','v'))]
B_names = 'y1 y2 y3 s1 s2 p q r t'.split()
B_knots = [('even', ('y1','p','q')), ('even', ('s1','p','q')), ('even', ('y2','r','t')), ('even', ('s2','r','t')), ('odd', ('y3','r','t'))]
for nm, kn in (('Alice', A_knots), ('Bob', B_knots)):
    holders = {}
    for _, mem in kn:
        for m in mem: holders[m] = holders.get(m, 0) + 1
    print(nm, 'knots', len(kn), '; holders on this side:', dict(sorted(holders.items())))
TA = side(A_names, A_knots, ('x1','x2','x3'), ('s1','s2')); TB = side(B_names, B_knots, ('y1','y2','y3'), ('s1','s2'))
print('Alice side table (rows x1x2x3, columns s1s2):'); print(TA)
print('Bob side table:'); print(TB)
M = TA @ TB.T
score, hidden, change, _ = ns['evaluate'](M)
print(f'old words {int(M.sum())}; four-correlation score {score:.6f} (20/9 = {20/9:.6f}); both complete records hide the far setting: {hidden}; largest change {change}')
