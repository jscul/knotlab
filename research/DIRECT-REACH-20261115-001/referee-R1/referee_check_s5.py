"""Referee R1, item (d): the two constant descriptions said to leave their constant at s = 5 from top level 3, at depth 9.

For each, in P_9 (my builder and SAT oracle):
  ties from every level-3 address to every deeper address (exact backbone), reported per s;
  an exhaustive search for three-member bonds meeting level 3 and level 8: every set {x, y, z} with x at level 3, y at level 8
  and z any other address; a set seen with all 8 patterns in the sampled models is unconstrained; for the rest, a tied pair
  rules it out (exact SAT), otherwise its unseen patterns are decided by SAT.
Also at deeper N (the same s = 5 cell with more remaining depth below level 8), to see whether the change is in s or in the
remaining depth r = N - 3 - s.
Usage: referee_check_s5.py OUT.json max_bonds_to_list N [N ...]"""
import json
import sys
import time

import numpy as np

sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/DIRECT-REACH-20261115-001/referee-R1')
from referee_pattern import Oracle, hid, load_population  # noqa: E402

CASES = ['d50c90fa37ed', '5b906d33a1e9']


def run(key, N=9, k=3, s=5, nsamp=512, max_bonds=10**9):
    O = Oracle(key, N, seed=99)
    assert O.alive()
    X = O.samples(nsamp)
    others = np.array([v for v in range(O.nv) if (v + 1).bit_length() - 1 > k])
    tie_s = {}
    for u in range(1 << k):
        for v, sg in O.tie_partners(hid(u, k), others, X).items():
            lv = (v + 1).bit_length() - 1
            tie_s.setdefault(lv - k, []).append([hid(u, k), v, sg])
    # pairs
    pair_cache = {}

    def tied(a, b):
        a, b = min(a, b), max(a, b)
        if (a, b) not in pair_cache:
            col = X[:, a] ^ X[:, b]
            if col.min() != col.max():
                pair_cache[(a, b)] = False
            else:
                lit = -(b + 1) if col[0] else (b + 1)
                pair_cache[(a, b)] = O.solve([-(a + 1), lit]) is None
        return pair_cache[(a, b)]
    # bit-packed coverage
    P = np.packbits(X, axis=0)                     # (S/8, nv) uint8
    Pn = np.packbits(~X, axis=0)
    top = [hid(u, k) for u in range(1 << k)]
    deep = [hid(y, k + s) for y in range(1 << (k + s))]
    allv = np.arange(O.nv)
    uncovered = 0
    bonds = []
    checked_exact = 0
    for x in top:
        for y in deep:
            cnt = np.zeros(O.nv, dtype=np.int64)
            for a in (0, 1):
                for b in (0, 1):
                    m = (P[:, x] if a else Pn[:, x]) & (P[:, y] if b else Pn[:, y])
                    cnt += np.any((P & m[:, None]) != 0, axis=0)
                    cnt += np.any((Pn & m[:, None]) != 0, axis=0)
            for z in np.nonzero(cnt < 8)[0]:
                z = int(z)
                if z in (x, y):
                    continue
                uncovered += 1
                if tied(x, y) or tied(x, z) or tied(y, z):
                    continue
                checked_exact += 1
                pats = O.patterns((x, y, z), X)
                if len(pats) < 8:
                    bonds.append([x, y, z, sorted(pats)])
                    if len(bonds) >= max_bonds:
                        break
            if len(bonds) >= max_bonds:
                break
        if len(bonds) >= max_bonds:
            break
    O.close()
    return dict(ties_by_s={str(k_): len(v) for k_, v in sorted(tie_s.items())}, tie_examples_s5=tie_s.get(s, [])[:5],
                triples_total=len(top) * len(deep) * (O.nv - 2), uncovered_by_samples=uncovered, exact_checked=checked_exact,
                bonds_found=len(bonds), bond_examples=bonds[:5], exhaustive=len(bonds) < max_bonds, sat_calls=O.calls)


if __name__ == '__main__':
    out_path = sys.argv[1]
    max_b = int(sys.argv[2])
    Ns = [int(x) for x in sys.argv[3:]] or [9]
    pop = {d['case'][:12]: d for d in load_population()}
    res = {}
    for c in CASES:
        for N in Ns:
            t = time.time()
            r = run(pop[c]['key'], N=N, max_bonds=max_b if c == 'd50c90fa37ed' else 10**9)
            r['seconds'] = time.time() - t
            res['%s N=%d' % (pop[c]['case'], N)] = r
            print(c, N, json.dumps(r)[:700], flush=True)
            json.dump(res, open(out_path, 'w'), indent=1)
