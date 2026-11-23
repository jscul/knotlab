"""Independent re-enumeration of small side classes by itertools over knot subsets (cut 1 with I <= 3, cut 2 with I <= 1), for comparison with sides.py."""
import itertools, json, sys
import numpy as np
sys.path.insert(0, 'experiments/REVIEW-LEADS-20261123-001C/REVIEW-LEADS-20261123-001C-E001_present_words')
import common as c
def enum(cut, i, kmax):
    n = 3 + cut + i
    knots = [(mem, law) for ar in (3, 4) for mem in itertools.combinations(range(n), ar) for law in ('even', 'odd', 'nae')]
    tabs = set(); cnt = 0
    for k in range(1, kmax + 1):
        for comb in itertools.combinations(range(len(knots)), k):
            h = [0] * n
            for q in comb:
                for m in knots[q][0]: h[m] += 1
            if any(h[j] != 1 for j in range(3 + cut)) or any(h[j] not in (1, 2) for j in range(3 + cut, n)): continue
            cnt += 1
            ok = np.ones(2 ** n, dtype=bool)
            idx = np.arange(2 ** n)
            for q in comb:
                mem, law = knots[q]
                s = sum(((idx >> (n - 1 - j)) & 1) for j in mem)
                ok &= ((s != 0) & (s != len(mem))) if law == 'nae' else ((s % 2) == (0 if law == 'even' else 1))
            tabs.add(ok.reshape(8, 2 ** cut, 2 ** i).sum(-1).astype(np.int16).tobytes())
    return cnt, tabs
for cut, imax in ((1, 2), (2, 1), (1, 3)):
    tot = 0; allt = set()
    for i in range(imax + 1):
        cnt, t = enum(cut, i, 3); tot += cnt; allt |= t
    print(cut, imax, 'structures', tot, 'tables', len(allt))
