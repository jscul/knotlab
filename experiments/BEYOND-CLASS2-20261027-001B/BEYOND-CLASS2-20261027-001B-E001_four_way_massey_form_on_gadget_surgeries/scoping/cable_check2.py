import sys, os
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/bc")
d = "/home/jscul/p-vs-np-contact-first/proofs/COPRIME-CLASS2-20261026-001B/"; sys.path.insert(0, d + os.listdir(d)[0])
import cp_lib as C
import mlib
from mlib import red, inv, artin, artin_conj, subst, magnus
st = artin_conj(mlib.P4, 4)
assert all(g == q for q, (W, g) in enumerate(st)), "not pure"
for q, (W, g) in enumerate(st):
    ab = [sum(s for h, s in W if h == k) for k in range(4)]
    print("strand", q, "conjugator length", len(W), "exponent sums", ab)
imgC = artin(C.cable(mlib.P4, 2), 8)
Y = lambda k: [(2 * k + 1, 1), (2 * k, 1)]
print("cabled action = substitution of geometric conjugators (Y_k = x_2k+1 x_2k):",
      all(red(subst(st[j][0], Y) + [(2 * j + t, 1)] + inv(subst(st[j][0], Y))) == imgC[2 * j + t] for j in range(4) for t in range(2)))
for j in range(4):
    M = magnus(st[j][0], 3, 10 ** 9 + 7)
    low = {k: v for k, v in M.items() if 0 < len(k) < 3}
    deg3 = {k: (v if v < 5 * 10 ** 8 else v - (10 ** 9 + 7)) for k, v in M.items() if len(k) == 3}
    print("W_%d: degree<3 terms" % j, low, "; degree-3 terms", deg3)
