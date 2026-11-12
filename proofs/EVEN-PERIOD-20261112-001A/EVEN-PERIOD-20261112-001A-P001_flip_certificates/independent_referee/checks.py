import sys, json, itertools
import numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from ref import *
from pysat.solvers import Minisat22

S = lambda s: tuple(int(ch) for ch in s)
src = json.load(open('/home/jscul/p-vs-np-contact-first/proofs/EVEN-PERIOD-20261112-001A/'
                     'EVEN-PERIOD-20261112-001A-P001_flip_certificates/result_census.json'))
rows = src['checks']['result']['rows']

# (2a) every listed certificate
tot = bad = 0
first17 = None
for row in rows:
    for e in row['certified by another word']:
        u, c, r0 = S(e['u']), S(e['c']), e['residue']
        p = len(u)
        ok = (p == row['p'] == len(c) and min_period(u) == p and u == min(u[i:] + u[:i] for i in range(p)))
        gp = gp_of(u)
        T = triples(p, gp)
        ok = ok and bool(gp) and compatible(c, T) and flippable(c, T, r0)
        # also confirm u is genuinely not its own certificate
        ok = ok and not any(flippable(u, T, r) for r in range(p))
        tot += 1; bad += (not ok)
        if p == 17 and first17 is None: first17 = (u, c, r0)
print('listed certificates checked', tot, 'failures', bad)
grand = sum(sum(r['tally'].values()) for r in rows)
print('author total words', grand)

# (3) controls, literal definition with ALL pairs (alpha,beta) in Z_p^2 (degenerate ones included)
def full_G(u):
    p = len(u)
    return [(a, b) for a in range(p) for b in range(p)
            if all(not (u[r] == u[(r + a) % p] == u[(r + b) % p]) for r in range(p))]

def literal_cert(u):
    p = len(u); G = full_G(u)
    if not G: return 'no kind'
    for r0 in range(p):
        s = Minisat22(); v = lambda i: i + 1
        for (a, b) in G:
            for r in range(p):
                t = (r, (r + a) % p, (r + b) % p)
                s.add_clause([v(x) for x in t]); s.add_clause([-v(x) for x in t])
                for q in range(3):
                    if t[q] != r0: continue
                    o = [t[j] for j in range(3) if j != q]
                    # forbid c[o0]==c[o1]!=c[r0]
                    for val in (0, 1):
                        lit = lambda x, want: v(x) if want else -v(x)
                        s.add_clause([-lit(o[0], val), -lit(o[1], val), -lit(r0, 1 - val)])
        if s.solve():
            m = s.get_model(); s.delete()
            return ('cert', ''.join('1' if m[i] > 0 else '0' for i in range(p)), r0)
        s.delete()
    return 'NO CERTIFICATE'

for w in ['01', '0011', '000111', '00001111', '00101101']:
    print('control', w, literal_cert(S(w)))

# (4) direct window check for one p=17 word
u, c, r0 = first17
p = 17
print('window test u=%s c=%s r0=%d' % (''.join(map(str, u)), ''.join(map(str, c)), r0))
R = 300
y = {i: c[i % p] for i in range(-R, R + 1)}
y[r0] = 1 - y[r0]
kinds = [(a, b) for a in range(1, 41) for b in range(a + 1, 41)
         if all(not (u[r] == u[(r + a) % p] == u[(r + b) % p]) for r in range(p))]
viol = [(a, b, i) for (a, b) in kinds for i in range(-R, R + 1 - b) if y[i] == y[i + a] == y[i + b]]
viol_u = [(a, b) for (a, b) in kinds if any(c[i % p] == c[(i + a) % p] == c[(i + b) % p] for i in range(p))]
print('kinds of span<=40 satisfied by u:', len(kinds), ' violations in flipped window:', len(viol),
      ' violations by periodic c:', len(viol_u))
# flip actually needed: confirm flipped y differs from c-periodic at exactly one place
print('positions differing from periodic c:', [i for i in y if y[i] != c[i % p]])

# (5) harmony test by graph on windows
def is_harmony(kinds):
    m = max(b for a, b in kinds)
    ok = lambda w: all(not (w[i] == w[i + a] == w[i + b]) for (a, b) in kinds for i in range(len(w) - b))
    E = [w for w in itertools.product((0, 1), repeat=m + 1) if ok(w)]
    V = set(w[:-1] for w in E) | set(w[1:] for w in E)
    while True:
        outs = {x: 0 for x in V}; ins = {x: 0 for x in V}
        E = [e for e in E if e[:-1] in V and e[1:] in V]
        for e in E: outs[e[:-1]] += 1; ins[e[1:]] += 1
        V2 = {x for x in V if outs[x] and ins[x]}
        if V2 == V: break
        V = V2
    if not V: return 'empty'
    return all(outs[x] == 1 and ins[x] == 1 for x in V), len(V)

for w, spans in [('0011', [4, 5, 6, 8]), ('01', [2, 3, 4]), ('000111', [6, 8]), ('00101101', [8, 9])]:
    uu = S(w); q = len(uu)
    for sp in spans:
        K = [(a, b) for a in range(1, sp) for b in range(a + 1, sp)
             if all(not (uu[r] == uu[(r + a) % q] == uu[(r + b) % q]) for r in range(q))]
        print('B_u for', w, 'span<', sp, 'kinds', len(K), 'harmony?', is_harmony(K) if K else 'no kinds')
