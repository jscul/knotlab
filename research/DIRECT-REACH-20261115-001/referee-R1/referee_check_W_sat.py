"""Referee R1, item (a), SAT side: for the small-orbit descriptions, the every-depth sequences of window_tree_census.json (READ as
data under test) against my own SAT oracle on the explicit P_N (referee_pattern.py), cell by cell:
  tie(N, k, s): some level-k address tied to some level-(k+s) address in P_N (exact backbone under one assumption);
  b3(N, k, s):  some three-member set inside O_u ∪ O_v (O_u an orbit of level k, O_v of level k + s, the set meeting both), with
                each pair free in P_N and the set constrained in P_N (exact: sampled models, then SAT for every unseen pattern);
  life(N):      P_N satisfiable.
Orbits are computed explicitly (union-find on the images of the used words, my own action).
Usage: referee_check_W_sat.py OUT.json Nmax|Nmin:Nmax k [case-prefix ...]   (no prefixes: all descriptions with orbits <= 4 to level Nmax)."""
import itertools
import json
import sys
import time

import numpy as np

sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/DIRECT-REACH-20261115-001/referee-R1')
from referee_pattern import Aut, Oracle, hid, load_population, HERE, STUDY  # noqa: E402

CENSUS_W = json.load(open(STUDY / 'exploratory/window_tree_census.json'))['cases']


def census_cell(row, k, N, s):
    """The census's claimed (tie, b3) at (N, s) from its per-r sequences (my own reading of the stored format: key 'r=<r>' for
    r < r0, 'r>=<r0>' otherwise; entry s - 1; beyond the stored prefix reduce s by whole periods)."""
    e = row['k%d' % k]
    r0, period = e['r0'], e['period']
    r = N - k - s
    P = e['sequences']['r=%d' % r if r < r0 else 'r>=%d' % r0]
    while s > len(P):
        s -= period
    return tuple(P[s - 1])


def triples_mixed(nu, nv):
    out = []
    for tri in itertools.combinations(range(nu + nv), 3):
        if min(tri) < nu <= max(tri):
            out.append(tri)
    return out


def cells(O, k, X):
    """(tie, b3) for s = 1 .. N - k, exactly. Pair ties are exact (SAT); a triple with a tied pair is not a bond; every other
    triple not seen with all 8 patterns in the models gets its unseen patterns decided by SAT."""
    N, A = O.N, O.A
    others = np.array([v for v in range(O.nv) if (v + 1).bit_length() - 1 >= k])
    partners = {}                 # level-k heap id -> {var: sign} (exact)
    for u in range(1 << k):
        hu = hid(u, k)
        rep = next((h for h, pt in partners.items() if hu in pt), None)
        if rep is not None:       # u tied to an earlier top address: same partners, signs composed
            sg = partners[rep][hu]
            pt = {v: sv ^ sg for v, sv in partners[rep].items() if v != hu}
            pt[rep] = sg
            partners[hu] = pt
            continue
        partners[hu] = O.tie_partners(hu, others[others != hu], X)
    tie_s = {(v + 1).bit_length() - 1 - k for pt in partners.values() for v in pt if (v + 1).bit_length() - 1 > k}
    pair_cache = {}

    def tied(a, b):
        a, b = min(a, b), max(a, b)
        if a in partners:
            return b in partners[a]
        if (a, b) not in pair_cache:
            col = X[:, a] ^ X[:, b]
            if col.min() != col.max():
                pair_cache[(a, b)] = False
            else:
                lit = -(b + 1) if col[0] else (b + 1)      # flip the observed XOR, with a = 0
                pair_cache[(a, b)] = O.solve([-(a + 1), lit]) is None
        return pair_cache[(a, b)]

    orb_k = [np.array([hid(y, k) for y in o]) for o in A.orbits(k)]
    res = {}
    O.found = []
    tri_cache = {}
    for s in range(1, N - k + 1):
        orb_v = [np.array([hid(y, k + s) for y in o]) for o in A.orbits(k + s)]
        cols = np.concatenate([np.arange((1 << k) - 1, (1 << (k + 1)) - 1), np.arange((1 << (k + s)) - 1, (1 << (k + s + 1)) - 1)])
        colpos = {int(v): i for i, v in enumerate(cols)}
        Xs = X[:, cols].astype(np.int8)
        b3 = False
        for ou in orb_k:
            for ov in orb_v:
                U = np.concatenate([ou, ov])
                T = triples_mixed(len(ou), len(ov))
                if not T:
                    continue
                if O.found:
                    F = np.array(O.found, dtype=bool)
                    O.found = []
                    X = np.concatenate([X, F, ~F])
                    Fs = F[:, cols].astype(np.int8)
                    Xs = np.concatenate([Xs, Fs, 1 - Fs])
                Xu = Xs[:, [colpos[int(v)] for v in U]].astype(np.int64)
                codes = np.stack([4 * Xu[:, a] + 2 * Xu[:, b] + Xu[:, c] for a, b, c in T], axis=1)   # (S, |T|)
                seen = np.zeros((len(T), 8), dtype=bool)
                for p in range(8):
                    seen[:, p] = np.any(codes == p, axis=0)
                for ti in np.nonzero(seen.sum(axis=1) < 8)[0]:
                    tri = tuple(int(U[i]) for i in T[ti])
                    if any(tied(tri[i], tri[j]) for i, j in ((0, 1), (0, 2), (1, 2))):
                        continue
                    if tri not in tri_cache:
                        tri_cache[tri] = O.patterns(tri, X)
                    pats = tri_cache[tri]
                    if len(pats) < 8:
                        # all pairs untied; with complement closure an untied pair is free (4 patterns): a bond of size 3
                        for i, j in ((0, 1), (0, 2), (1, 2)):
                            assert len({(((p >> i) & 1), ((p >> j) & 1)) for p in pats}) == 4
                        b3 = True
                        break
                if b3:
                    break
            if b3:
                break
        res[s] = (int(s in tie_s), int(b3))
    return res


def max_orbit(A, n):
    return max(len(o) for o in A.orbits(n))


if __name__ == '__main__':
    out_path, k = sys.argv[1], int(sys.argv[3])
    Nmin, Nmax = (int(x) for x in sys.argv[2].split(':')) if ':' in sys.argv[2] else (k + 1, int(sys.argv[2]))
    prefixes = sys.argv[4:]
    pop = load_population()
    todo = [d for d in pop if d['case'] in CENSUS_W and 'k%d' % k in CENSUS_W[d['case']]]
    if prefixes:
        todo = [d for d in todo if any(d['case'].startswith(p) for p in prefixes)]
    results, mism = {}, []
    import os
    if os.path.exists(out_path):                 # resume: keep finished descriptions
        prev = json.load(open(out_path))
        results, mism = prev['cases'], prev['mismatches']
    t0 = time.time()
    for d in todo:
        if d['case'] in results:
            continue
        row = CENSUS_W[d['case']]
        A = Aut(d['key'])
        t1 = time.time()
        rec = dict(profile=d['profile'], max_orbit_to_Nmax=max(max_orbit(A, n) for n in range(Nmax + 1)), cells={}, life={})
        for N in range(Nmin, Nmax + 1):
            O = Oracle(d['key'], N, seed=N)
            alive = O.alive()
            rec['life'][N] = alive
            if not alive:
                O.close()
                continue
            X = O.samples(160)
            c = cells(O, k, X)
            for s, v in c.items():
                cl = census_cell(row, k, N, s)
                rec['cells']['%d,%d' % (N, s)] = [v, list(cl), N - k - s]
                if tuple(v) != tuple(cl):
                    mism.append(dict(case=d['case'], k=k, N=N, s=s, r=N - k - s, referee=v, census=cl))
            rec.setdefault('sat_calls', {})[N] = O.calls
            O.close()
        rec['seconds'] = time.time() - t1
        results[d['case']] = rec
        print(d['case'][:12], d['profile'], 'r0', row['k%d' % k]['r0'], 'cells', len(rec['cells']),
              'mismatches so far', len(mism), '%.1fs' % rec['seconds'], flush=True)
        json.dump(dict(k=k, Nmax=Nmax, mismatches=mism, cases=results, seconds=time.time() - t0), open(out_path, 'w'), indent=0)
    print('done', len(results), 'descriptions; mismatches', len(mism), '%.0fs' % (time.time() - t0))
