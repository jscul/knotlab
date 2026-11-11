import json, sys
from sympy import Poly, symbols
s = symbols('s')
d = json.load(open("rows_training.json"))
for n in sys.argv[1:]:
    allsq = True; ex = set()
    for key, v in d[n].items():
        p = int(v["den"], 16)
        fl = Poly(sum(s**k for k in range(p.bit_length()) if (p >> k) & 1), s, modulus=2).factor_list()[1]
        for f, e in fl:
            ex.add(e)
            if e % 2: allsq = False
    print(n, "every reduced denominator a square:", allsq, "exponents", sorted(ex))
