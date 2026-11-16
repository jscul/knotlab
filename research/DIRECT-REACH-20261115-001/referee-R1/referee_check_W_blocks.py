"""Referee R1, item (a), block side: my own block DP (referee_blocks.py) against explicit addresses, against the study's stored
every-depth sequences (window_tree_census.json, READ as data under test), and my own every-depth prediction against my exact
per-depth DP at large depth.
Usage: referee_check_W_blocks.py OUT.json Nexact smax [case-prefix ...]"""
import json
import random
import sys
import time

import numpy as np

sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/DIRECT-REACH-20261115-001/referee-R1')
from referee_pattern import Aut, hid, load_population, STUDY  # noqa: E402
from referee_blocks import Blocks  # noqa: E402

CENSUS_W = json.load(open(STUDY / 'exploratory/window_tree_census.json'))['cases']


def census_cell(row, k, N, s):
    e = row['k%d' % k]
    r0, period = e['r0'], e['period']
    r = N - k - s
    P = e['sequences']['r=%d' % r if r < r0 else 'r>=%d' % r0]
    while s > len(P):
        s -= period
    return tuple(P[s - 1])


def validate_types(B, A, key, nmax, rng):
    """Expand the explicit orbit tree to level nmax and check orbits, images, sections and block knots against my builder."""
    bad = []
    level = [(0, [0])]                     # (type, addresses as ints at level n), element order = type order
    for n in range(nmax + 1):
        # (a) the partition of level n
        mine = sorted(tuple(sorted(a)) for _, a in level)
        expl = sorted(tuple(o.tolist()) for o in A.orbits(n))
        if mine != expl:
            bad.append(('partition', n))
        for t, addrs in level:
            T = B.types[t]
            m = len(T)
            for j, wi in enumerate(B.used):
                img = A.act(A.W[wi], n, np.array(addrs, dtype=np.int64))
                for i in range(m):
                    if int(img[i]) != addrs[T[i][j][0]]:
                        bad.append(('image', n, t, i, j))
                    # (b) the section: map(addr_i . z) = map(addr_i) . section(z) for a random suffix z
                    L = 6
                    z = rng.getrandbits(L)
                    full = A.act(A.W[wi], n + L, np.array([(addrs[i] << L) | z], dtype=np.int64))[0]
                    sec, out = T[i][j][1], 0
                    for pos in range(L - 1, -1, -1):
                        c, sec = B.read(sec, (z >> pos) & 1)
                        out |= c << pos
                    if int(full) != ((addrs[T[i][j][0]] << L) | out):
                        bad.append(('section', n, t, i, j))
            # (c) block knots, mapped to heap ids, against knots placed at the orbit's addresses (explicit, any N > n)
            mk = set()
            for a, b, c in B.block_knots(T):
                mk.add(tuple(sorted(hid(addrs[v], n) if v < m else hid(2 * addrs[(v - m) // 2] + (v - m) % 2, n + 1)
                                    for v in (a, b, c))))
            ek = set()
            X = np.array(addrs, dtype=np.int64)
            imgs = {wi: A.act(A.W[wi], n, X) for wi in A.used}
            for p in A.placements:
                for idx in range(m):
                    mem = []
                    for tt in p:
                        wi, e = divmod(tt, 3)
                        y = int(imgs[wi][idx])
                        mem.append(hid(y, n) if e == 0 else hid(2 * y + e - 1, n + 1))
                    if len(set(mem)) == 3:
                        ek.add(tuple(sorted(mem)))
            if mk != ek:
                bad.append(('knots', n, t))
        nxt = []
        for t, addrs in level:
            for c, pos in B.kids[t]:
                nxt.append((c, [2 * addrs[p // 2] + p % 2 for p in pos]))
        level = nxt
    return bad


if __name__ == '__main__':
    out_path, Nexact, smax = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    prefixes = sys.argv[4:]
    rng = random.Random(7)
    pop = load_population()
    if prefixes:
        pop = [d for d in pop if any(d['case'].startswith(p) for p in prefixes)]
    res, mism = {}, []
    t0 = time.time()
    for d in pop:
        row = CENSUS_W[d['case']]
        t1 = time.time()
        try:
            B = Blocks(d['key'])
        except ValueError as e:
            res[d['case']] = dict(profile=d['profile'], blocks=str(e), census_small='k3' in row)
            if 'k3' in row:
                mism.append(dict(case=d['case'], what='small in census, not mine', err=str(e)))
            continue
        if 'k3' not in row:
            mism.append(dict(case=d['case'], what='small for me, not in census'))
            continue
        A = Aut(d['key'])
        rec = dict(profile=d['profile'], types=len(B.types), orbit_sizes=sorted(set(B.m)))
        rec['type_validation_failures'] = validate_types(B, A, d['key'], 9, rng)
        if rec['type_validation_failures']:
            mism.append(dict(case=d['case'], what='type validation', detail=rec['type_validation_failures'][:5]))
        for k in (2, 3):
            ev = B.every_depth(k, smax)
            e = row['k%d' % k]
            rec['k%d' % k] = dict(r0=ev['r0'], census_r0=e['r0'], period=ev['period'], census_period=e['period'],
                                  alive_every_depth=ev['alive_every_depth'], census_alive=e['alive_every_depth'])
            if ev['r0'] != e['r0'] or ev['alive_every_depth'] != e['alive_every_depth']:
                mism.append(dict(case=d['case'], k=k, what='r0/alive', mine=(ev['r0'], ev['alive_every_depth']),
                                 census=(e['r0'], e['alive_every_depth'])))
            # my every-depth prediction against the census, for every s <= smax and r = 0 .. r0 + 2
            npred = 0
            for r in range(ev['r0'] + 3):
                P = ev['pred'][min(r, ev['r0'])]
                for s in range(1, smax + 1):
                    npred += 1
                    if tuple(P[s - 1]) != census_cell(row, k, k + s + r, s):
                        mism.append(dict(case=d['case'], k=k, what='every-depth prediction vs census', N=k + s + r, s=s, r=r,
                                         mine=P[s - 1], census=census_cell(row, k, k + s + r, s)))
            # my exact per-depth DP at every N <= Nexact against both
            F = B.feas(Nexact)
            nex = 0
            for N in range(k + 1, Nexact + 1):
                ex = B.exact_cells(N, k, F[: N + 1])
                for s, v in ex.items():
                    nex += 1
                    r = N - k - s
                    pv = ev['pred'][min(r, ev['r0'])][s - 1] if s <= smax else None
                    cv = census_cell(row, k, N, s)
                    if tuple(v) != tuple(cv) or (pv is not None and tuple(v) != tuple(pv)):
                        mism.append(dict(case=d['case'], k=k, what='exact DP', N=N, s=s, r=r, exact=v, pred=pv, census=cv))
            rec['k%d' % k].update(prediction_cells=npred, exact_cells=nex)
            ties = {tuple(x) for P in ev['pred'].values() for x in P}
            rec['k%d' % k]['flag_values'] = sorted(ties)
        rec['seconds'] = time.time() - t1
        res[d['case']] = rec
        print(d['case'][:12], d['profile'], 'types', len(B.types), 'r0', rec['k3']['r0'], rec['k2']['r0'],
              'mismatches so far', len(mism), '%.1fs' % rec['seconds'], flush=True)
        json.dump(dict(Nexact=Nexact, smax=smax, mismatches=mism, cases=res, seconds=time.time() - t0), open(out_path, 'w'), indent=0)
    json.dump(dict(Nexact=Nexact, smax=smax, mismatches=mism, cases=res, seconds=time.time() - t0), open(out_path, 'w'), indent=0)
    print('done', len(res), 'mismatches', len(mism), '%.0fs' % (time.time() - t0))
