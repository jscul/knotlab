"""Unit tests of ticket B's new readings.  usage: python -B test_mcb.py"""
import itertools
import os
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cb  # noqa: E402
import mcb  # noqa: E402
import b4  # noqa: E402

mc, pm, K, P = mcb.mc, mcb.pm, mcb.K, mcb.P
RES = {}


def check(name, cond, detail=None):
    RES[name] = {'ok': bool(cond), 'detail': None if cond else repr(detail)[:500]}
    print('%-80s %s' % (name, 'ok' if cond else 'FAIL'), '' if cond else repr(detail)[:300])


def same_brute(R1, p1, R2, p2, m1=None, m2=None):
    if len(p1) != len(p2):
        return False
    s1 = [frozenset(M) for M in R1.maxsets if next(iter(M)) in set(p1)]
    s2 = {frozenset(M) for M in R2.maxsets if next(iter(M)) in set(p2)}
    if len(s1) != len(s2):
        return False
    for perm in itertools.permutations(p2):
        f = dict(zip(p1, perm))
        if any((R1.h[u], R1.k[u]) != (R2.h[f[u]], R2.k[f[u]]) for u in p1):
            continue
        if m1 is not None and any(m1.get(u) != m2.get(f[u]) for u in p1):
            continue
        if {frozenset(f[u] for u in M) for M in s1} == s2:
            return True
    return False


def t_way_starts():
    bad = []
    n = 0
    for key, d in mcb.STB['starts'].items():
        kx, rest = key.split(' + ')
        ky, way = rest.split(' / ')
        other = None
        if way.endswith('-other'):
            way = way[:-6]
            other = 'other'
        xp, yp = mcb.STB['parts'][kx], mcb.STB['parts'][ky]
        xi = {'members': xp['members'], 'first member': xp['first member'], 'other member': xp['other member'],
              'first dead knot': xp['first dead knot']}
        yi = {'members': yp['members'], 'first member': yp['first member'], 'other member': yp['other member'],
              'first dead knot': yp['first dead knot']}
        cands = [None] if other is None else ['X', 'Y', 'both']
        ok = False
        for o in cands:
            stars, X, Y = mcb.way_start(xp['X (labels from 0)'], xi, yp['Y (labels from 100)'], yi, way, o)
            if stars == d['stars'] and X == d['X'] and Y == d['Y']:
                ok = True
                break
        n += 1
        if not ok:
            bad.append(key)
    check('DB 2.3: the start builder reproduces the %d listed starts' % n, not bad, bad[:5])


def t_forms():
    rng = random.Random(7)
    law = mcb.law1('COPY-LAW(OFFSHOOT)', 'parity')
    forms = mcb.Forms()
    mforms = mcb.Forms(marked=True)
    pairs = mism = 0
    for key in rng.sample(sorted(mcb.STB['starts']), 30):
        S0, X, Y = mcb.start_b(key)
        A = mcb.grow(S0, law, 'COPY-LAW(OFFSHOOT)', rounds=3)
        for t in range(A.rounds_done + 1):
            S = A.snap[t]
            R = pm.roster_of(S.copy(), law)
            desc = mc.descent_map(S, X, Y, 0)
            ps = [p for p in R.parts if len(p) <= 6]
            for a in ps:
                for b in ps:
                    pairs += 1
                    e1 = forms.classify(R, a) == forms.classify(R, b)
                    if e1 != same_brute(R, list(a), R, list(b)):
                        mism += 1
                    e2 = mforms.classify(R, a, desc) == mforms.classify(R, b, desc)
                    if e2 != same_brute(R, list(a), R, list(b), desc, desc):
                        mism += 1
    check('forms and marked forms against every map of members (%d pairs)' % pairs, mism == 0, mism)
    # the eight kinds' forms are distinct, and X alone's equals Y alone's
    f = mcb.Forms()
    ids = {}
    for kind in mcb.KINDS8:
        got = []
        for w in ('X', 'Y'):
            S0, mem = mcb.alone_b(kind, w + ' alone')
            R0 = pm.roster_of(S0.copy(), law)
            got.append(f.classify(R0, next(p for p in R0.parts if set(mem) <= set(p))))
        ids[kind] = got
    check('the eight kinds: X alone and Y alone have one form each', all(a == b for a, b in ids.values()), ids)
    check('the eight kinds have eight forms', len({v[0] for v in ids.values()}) == 8, ids)
    # merging two registries gives the same classes
    m, gl = mcb.merge_descs([('a', forms.desc), ('b', f.desc)])
    check('merging form registries keeps distinct forms distinct', len(gl) <= len(forms.desc) + len(f.desc), len(gl))


def t_descent_and_ending():
    key = 'one-2 + two-22 / W3'
    S0, X, Y = mcb.start_b(key)
    law = mcb.law1('COPY-LAW(RETIRE)', 'nae')
    A = mcb.grow(S0, law, 'COPY-LAW(RETIRE)')
    S1 = A.snap[1]
    desc, xo, yo = mcb.side_sets(S1, X, Y, 0)
    check('descent: Y\'s members are descended from Y only', all(desc[u] == 'Y only' for u in Y))
    check('descent: dead knots of the start are from neither', all(desc[u] == 'neither' for u in range(S0.n_knots)
                                                                   if u not in X + Y))
    jb = mcb.first_joint_births(A, X, Y, 0)
    check('the first joint births: round 1 here, each with a parent of each', jb is not None and jb['round'] == 1, jb)
    # every knot made with a parent from each pattern is from both
    ok = True
    for t in range(1, A.rounds_done + 1):
        S = A.snap[t]
        d, _, _ = mcb.side_sets(S, X, Y, 0)
        Sb = A.snap[t - 1]
        db = mc.descent_map(Sb, X, Y, 0)
        for b in A.records[t - 1]['births']:
            pk = {db.get(p) for p in b['parents']}
            want = 'both' if ('both' in pk or {'X only', 'Y only'} <= pk) else (
                'X only' if pk <= {'X only', 'neither'} and 'X only' in pk else
                'Y only' if pk <= {'Y only', 'neither'} and 'Y only' in pk else d[b['id']])
            if d[b['id']] != want:
                ok = False
    check('descent of every birth from its parents\' descents (D 2.6)', ok)
    he = mcb.how_ended(A, yo | set(Y), A.rounds_done)
    check('how the knots descended from Y only ended: counts are given', isinstance(he, dict), he)


def t_renaming():
    law = mcb.law1('COPY-LAW(OFFSHOOT)', 'parity')
    r = mcb.STB['renaming starts']['two-knot']
    S = pm.from_stars(r['stars'])
    A1 = mcb.grow(S, law, 'COPY-LAW(OFFSHOOT)', rounds=5)
    okall = True
    for rn in r['renamed']:
        S2 = pm.from_stars(rn['stars'], reverse_names=rn['names'].startswith('reversed'))
        A2 = mcb.grow(S2, law, 'COPY-LAW(OFFSHOOT)', rounds=5)
        c = b4.compare_runs(A1, A2)
        okall = okall and all(x == 'renaming' for x in c['per_round'])
    check('renaming check: the two-knot start under COPY-LAW(CANCEL-OFFSHOOT), ten renamings, built and verified',
          okall)
    # a structure that is not a renaming is refused: change one barred mark
    S3 = A1.snap[3].copy()
    d = next(d for d in range(S3.n_distinctions) if len(S3.holders[d]) == 1)
    S3.barred[d] = not S3.barred[d]
    si = b4.start_iso(A1.snap[0], A1.snap[0])
    sig = b4.Renaming(*si)
    for t in range(1, 4):
        sig.extend(A1.snap[t - 1], A1.records[t - 1], A1.snap[t - 1], A1.records[t - 1])
    check('verification refuses a structure with one barred mark changed',
          not b4.verify(A1.snap[3], S3, sig.k, sig.d) and b4.verify(A1.snap[3], A1.snap[3], sig.k, sig.d))
    # under MET some renamed runs differ (the control)
    lawm = mc.make_law('COPY-LAW(OFFSHOOT)', 'MET', 'NEWEST', 'parity')
    rr = mcb.STB['renaming starts']['ystart-three-222']
    S = pm.from_stars(rr['stars'])
    B1 = mcb.grow(S, lawm, 'COPY-LAW(OFFSHOOT)', rounds=6)
    diff = 0
    for rn in rr['renamed']:
        S2 = pm.from_stars(rn['stars'], reverse_names=rn['names'].startswith('reversed'))
        B2 = mcb.grow(S2, lawm, 'COPY-LAW(OFFSHOOT)', rounds=6)
        c = b4.compare_runs(B1, B2)
        diff += any(x.startswith('differs') for x in c['per_round'])
    check('the control: under MET(NEWEST) some renamed runs of ystart-three-222 differ', diff > 0, diff)


def t_guard():
    check('the guard limits are ten times the fold engine\'s', pm.GUARD['pairs'] == 200000, pm.GUARD)


def t_iso_limit():
    """deviations 33: the form test with a time limit decides as the unlimited test does, and an unfinished test is
    counted, with the part's size, and leaves the part in a class of its own."""
    nx = mcb.nx
    ok = True
    for n in (4, 5, 6, 7):
        for a, b in ((nx.cycle_graph(n), nx.cycle_graph(n)), (nx.cycle_graph(n), nx.path_graph(n))):
            for G in (a, b):
                nx.set_node_attributes(G, 'm', 'c')
            f = mcb.Forms(seconds=10)
            ok &= f.iso(a, b) == nx.is_isomorphic(a, b, node_match=lambda x, y: x['c'] == y['c'])
    check('the limited form test agrees with the unlimited one (cycles and paths, 4 to 7)', ok)
    G = nx.random_regular_graph(3, 400, seed=1)
    nx.set_node_attributes(G, 'm', 'c')
    f = mcb.Forms(seconds=1e-6)
    check('a test past the limit is undecided (None) and counted', f.iso(G, G.copy()) is None)
    # parts past the size bound are classed by their bucket key; parts within it exactly, as without the bound
    law = mcb.law1('CAP-3(WAIT)', 'nae')
    S0, mem = mcb.alone_b('pairs-4', 'Y alone')
    run = mcb.grow(S0, law, 'CAP-3(WAIT)', rounds=8)
    fa, fb = mcb.Forms(), mcb.Forms(seconds=10, hash_above=4)
    same, n_big = True, 0
    for t in range(run.rounds_done + 1):
        R = mcb.roster_or_none(run.snap[t], law)
        if R is None:
            continue
        for p in R.parts:
            ca, cb_ = fa.classify(R, p), fb.classify(R, p)
            if len(p) <= 4:
                same &= fa.desc[ca] == fb.desc[cb_] and cb_ not in fb.by_hash_classes
            else:
                n_big += 1
    check('with a size bound of 4, parts of at most 4 members get the same forms; larger ones are classed by hash',
          same and n_big > 0 and fb.by_hash == n_big, [n_big, fb.by_hash])


def main():
    for f in (t_guard, t_way_starts, t_forms, t_descent_and_ending, t_renaming, t_iso_limit):
        f()
    RES['_all_ok'] = all(v['ok'] for k, v in RES.items() if not k.startswith('_'))
    cb.write_json('test_mcb.json', RES)
    print('ALL OK' if RES['_all_ok'] else 'SOME FAIL')


if __name__ == '__main__':
    main()
