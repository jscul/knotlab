"""Unit tests of what ticket C's engine writes afresh (PC, "What the gate cannot test"): the samplers and their calls,
the seeds' tokens, the pair rule, the roster read for the readings, the ties read birth by birth, the fully masked
filter, the placement of the planted case, the tests.  Writes test_mcc.json to the outputs."""
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mcc  # noqa: E402
from mcc import pm, mc, P  # noqa: E402

RESULTS = {}


def check(name, cond, info=None):
    RESULTS[name] = {'pass': bool(cond), 'info': info}
    print(('PASS ' if cond else 'FAIL ') + name, '' if info is None else json.dumps(info, default=str)[:300])
    return cond


def t_sampler():
    # take-by-take: one randrange per take, a single candidate also calls
    s = mcc.Sampler('x', 'T1')
    lists = [[3, 5, 9], [7], [1, 2], [4]]
    got = [s(('take', i), c) for i, c in enumerate(lists)]
    r = random.Random('x')
    want = [c[r.randrange(len(c))] for c in lists]
    check('T1 sampler: one randrange per take, single candidates call too', got == want and s.calls == 4,
          {'got': got, 'want': want})
    # holder weighting: choices by holders at the start of the round
    S = pm.from_stars([[0, 1, 2], [0, 1, 3], [0, 4, 5], [1, 6, 7]])     # 0 held by 3, 1 by 3
    S2 = pm.from_stars([[0, 1, 2], [0, 3, 4], [1, 5, 6]])               # 0 held by 2, 1 by 2
    s = mcc.Sampler('y', 'T2')
    s.S = S
    lists = [[0, 1], [0], [1, 0]]
    got = [s(('take', i), c) for i, c in enumerate(lists)]
    r = random.Random('y')
    want = [r.choices(c, weights=[len(S.holders[d]) for d in c], k=1)[0] for c in lists]
    check('T2 sampler: choices weighted by holders, single candidates call too', got == want, {'got': got})
    # weights really are the holder counts: a candidate with 3 holders against one with 1
    S3 = pm.from_stars([[0, 2, 3], [0, 4, 5], [0, 6, 7], [1, 8, 9], [1, 10, 11]])   # 0: three holders, 1: two
    s = mcc.Sampler('z', 'T2')
    s.S = S3
    n0 = sum(1 for _ in range(20000) if s(('t', 0), [0, 1]) == 0)
    check('T2 sampler: chance in proportion to holders (3 against 2)', abs(n0 / 20000 - 0.6) < 0.015, n0 / 20000)
    check('T2 hand structure: holders 3 and 2', len(S3.holders[0]) == 3 and len(S3.holders[1]) == 2)
    del S2


def t_seeds():
    sp = mcc.Spec('FBP', 'CANCEL-WAIT', 'STEPS-1', 'parity')
    check('seed tokens, STEPS-1', mcc.growth_seed('n3-g6-122', sp, 0) == 'C|n3-g6-122|FBP|CANCEL-WAIT|parity|0|STEPS-1')
    sp2 = mcc.Spec('CAP-2', 'CANCEL-OFFSHOOT', 'MET', 'nae')
    check('seed tokens, MET, nae', mcc.growth_seed('n4-g17-3232', sp2, 3) == 'C|n4-g17-3232|CAP-2|CANCEL-OFFSHOOT|nae|3')
    sp3 = mcc.Spec('ORD', 'CANCEL-RETIRE', 'STEPS-1', 'parity', 'HOLD', 'T2')
    g = mcc.growth_seed('n5-g40-33323', sp3, 0)
    c = mcc.cont_seed(mcc.base_seed('n5-g40-33323', sp3, 0), sp3, 'BY', 2, 17)
    check('seed tokens, STEPS-1, HOLD, holder weighting last of all',
          g == 'C|n5-g40-33323|ORD|CANCEL-RETIRE|parity|0|STEPS-1|HOLD|T2'
          and c == 'C|n5-g40-33323|ORD|CANCEL-RETIRE|parity|0|STEPS-1|HOLD|BY|2|17|T2', {'g': g, 'c': c})
    fam = mcc.family_both('parity')
    check('the family: 42 laws in the order ration, treatment, taking rule',
          len(fam) == 42 and [f.key()[:3] for f in fam[:3]] == [('FLOOR1', 'CANCEL-RETIRE', 'MET'),
                                                                 ('FLOOR1', 'CANCEL-RETIRE', 'STEPS-1'),
                                                                 ('FLOOR1', 'CANCEL-OFFSHOOT', 'MET')])
    L = mcc.Spec('FBP', 'CANCEL-RETIRE', 'MET', 'parity').law()
    check('FBP is FLOOR1 with the fresh count by parents', L.ration == 'FLOOR1' and L.fresh_by_parents)


def t_pairs():
    # ten lone members, each its own part, wholly apart (no shared distinction): 90 ordered pairs, X made
    stars = [[i * 3, i * 3 + 1, i * 3 + 2] for i in range(10)]
    S = pm.from_stars(stars)
    S.made = [1] * 10
    R = mcc.light_roster(S)
    pairs, n_all, removed = mcc.pairs_of_round(S, R, 'sampled', 'SEED', 2)
    lst = [(i, j) for i in range(10) for j in range(10) if i != j]
    want = sorted(random.Random('SEED|P|2').sample(lst, 8))
    got = sorted((R.parts.index(x), R.parts.index(y)) for x, y in pairs)
    check('pair rule: more than eight pairs, eight sampled with the registered call', got == want and n_all == 90
          and removed == 0, {'got': got})
    # not made: start knots are never X
    S.made = [0] * 5 + [1] * 5
    pairs, n_all, removed = mcc.pairs_of_round(S, R, 'sampled', 'SEED', 2)
    check('pair rule: X a made pattern only', n_all == 5 * 9, n_all)
    # wholly apart: two parts sharing a distinction (a member holding a distinction another member holds)
    S = pm.from_stars([[0, 1, 2], [0, 3, 4], [5, 6, 7]])
    S.made = [1, 1, 1]
    R = mcc.light_roster(S)
    pairs, n_all, removed = mcc.pairs_of_round(S, R, 'sampled', 'SEED', 1)
    check('pair rule: parts that share a distinction are not wholly apart (removed counted)',
          len(R.parts) == 3 and n_all == 4 and removed == 2, {'parts': R.parts, 'n': n_all, 'removed': removed})


def grown_states(n=60, seed=7):
    """States from sampled growths of census starts under several laws (both taking rules, both knot laws)."""
    C = mcc.census()
    rnd = random.Random(seed)
    out = []
    specs = mcc.family_both('parity')
    for k in range(n):
        st = C[rnd.randrange(len(C))]
        sp = specs[rnd.randrange(len(specs))]
        g = mcc.Grown(mcc.start_state(st['stars']), sp.law(), mcc.Sampler('test|%d' % k), rounds=6, knot_bound=300)
        out.append((st['id'], sp, g))
    return out


def t_roster(states):
    bad = 0
    n = 0
    for sid, sp, g in states:
        for t, S in enumerate(g.snaps):
            A = pm.roster_of(S, sp.law())
            B = mcc.light_roster(S)
            n += 1
            if (A.members != B.members or A.parts != B.parts or sorted(map(sorted, A.maxsets)) !=
                    sorted(map(sorted, B.maxsets)) or A.h != B.h or A.k != B.k):
                bad += 1
            cl = pm.roster_classes(A)
            cl2 = mcc.classes(B)
            if len(set(cl)) != len(set(cl2)) or any((cl[i] == cl[j]) != (cl2[i] == cl2[j])
                                                    for i in range(len(cl)) for j in range(len(cl))):
                bad += 1
    check('reading roster equals the fold engine\'s roster (members, h, k, maximal met sets, parts, classes)',
          bad == 0, {'states': n, 'bad': bad})


def t_ties(states):
    """Eligible places and made distinctions tied to them: residues against mc.ties_parity (a basis of the allowed
    states, D 3.3), on every state of the growths, for a pair of parts or a part and a knot set."""
    nchk = nbad = ntied = 0
    for sid, sp, g in states:
        if sp.knot_law != 'parity':
            continue
        for s in range(1, min(4, g.R)):
            Ss = g.snaps[s]
            R = mcc.light_roster(Ss)
            if len(R.parts) < 1:
                continue
            Y = list(R.parts[-1])
            X = list(R.parts[0]) if len(R.parts) > 1 else []
            el = mcc.eligible_places(Ss, X, Y)
            T = mc.ties_parity(Ss)
            xp = {d for u in X for d in Ss.places[u]}
            el2 = [v for v in sorted({d for u in Y for d in Ss.places[u]}) if v not in T.frozen
                   and not any(T.tied(v, w) for w in xp)]
            nchk += 1
            if el != el2:
                nbad += 1
            tc = mcc.TieCache(g.snaps, g.records)
            acc = {v: [] for v in el}
            for t in range(s + 1, g.R + 1):
                for v, fs in tc.new_ties(t, el).items():
                    acc[v].extend(fs)
                Tt = mc.ties_parity(g.snaps[t])
                nd_s = Ss.n_distinctions
                for v in el:
                    want = sorted(d for d in Tt.members(v) if d >= nd_s)
                    if sorted(acc[v]) != want:
                        nbad += 1
                    ntied += len(want)
                    nchk += 1
    check('ties read birth by birth equal the basis of the allowed states (eligible places and made ties)',
          nbad == 0, {'checks': nchk, 'bad': nbad, 'made distinctions tied': ntied})


def t_cached_candidates():
    """The candidates computed once per parent within a round (dev 40) equal the fold engine's on every call: growths
    of every law of both taking rules on a sample of census starts, every take checked."""
    C = mcc.census()
    mcc._TC_VERIFY[0] = True
    n = 0
    ok = True
    try:
        for k, st in enumerate(C[::53]):
            for sp in (mcc.family_both('parity')[k % 42], mcc.family_both('parity')[(k * 7 + 3) % 42],
                       mcc.Spec('ORD', 'CANCEL-RETIRE', 'MET', 'parity'), mcc.Spec('ORD', 'CANCEL-WAIT', 'STEPS-1',
                                                                                  'parity')):
                try:
                    g = mcc.Grown(mcc.start_state(st['stars']), sp.law(), mcc.Sampler('cc|%d' % k), 5, 300)
                    n += sum(len(r['births']) for r in g.records)
                except AssertionError as e:
                    ok = False
                    print(e)
                    break
    finally:
        mcc._TC_VERIFY[0] = False
    check('cached take candidates equal the fold engine\'s on every call', ok, {'births': n})


def t_row():
    """St.row built in one pass (dev 41) equals the fold engine's on every knot."""
    rnd = random.Random(41)
    bad = n = 0
    for k in range(300):
        S = pm.St()
        S.places = [sorted(rnd.sample(range(rnd.randint(300, 5000)), rnd.randint(1, 300))) if rnd.random() < 0.5
                    else rnd.sample(range(200000), rnd.randint(60, 400))]
        n += 1
        if mcc._row(S, 0) != mcc._ORIG_ROW(S, 0):
            bad += 1
    check('St.row in one pass equals the engine\'s', bad == 0, {'rows': n, 'bad': bad})


def t_identity_wrapper():
    """The take wrapper, inactive, returns the engine's own lists: growths equal with pm's original function."""
    C = mcc.census()
    same = True
    for k, st in enumerate(C[::97]):
        sp = mcc.Spec('FLOOR1', 'CANCEL-OFFSHOOT', 'STEPS-1' if k % 2 else 'MET', 'parity')
        g1 = mcc.Grown(mcc.start_state(st['stars']), sp.law(), mcc.Sampler('w|%d' % k), 6, 300)
        pm.take_candidates = mcc._ORIG_TC
        try:  # the engine's own function, no wrapper, no cache
            g2 = mcc.Grown(mcc.start_state(st['stars']), sp.law(), mcc.Sampler('w|%d' % k), 6, 300)
        finally:
            pm.take_candidates = mcc._take_candidates
        if g1.S.places != g2.S.places or g1.S.parents != g2.S.parents:
            same = False
    check('the take wrapper, inactive, changes nothing (growths equal with the original function)', same)


def t_chooser_order(states):
    """The sampler's calls are the round's takes in birth order (FD 2.1), each one of its candidates."""
    ok = True
    n = 0
    for sid, sp, g in states[:20]:
        st = mcc.start_by_id(sid)
        smp = mcc.Sampler('order|%s' % sid)
        smp.log = []
        g2 = mcc.Grown(mcc.start_state(st['stars']), sp.law(), smp, 6, 300)
        calls = iter(smp.log)
        for rec in g2.records:
            for bi, b in enumerate(rec['births']):
                for d in b['rule_takes']:
                    key, cands, got = next(calls)
                    n += 1
                    if key != ('take', bi) or got != d or d not in cands:
                        ok = False
        if next(calls, None) is not None:
            ok = False
    check('sampler calls follow birth order, one per take, each a candidate', ok, {'takes': n})


def t_full_mask():
    """Fully masked: no birth with a parent on X's side has a candidate held by Y's side (and the reverse)."""
    # X's member 3 (an offshoot of 0) meets dead knot 0, which holds e = 0 with Y's member 4's parent 1 ... built by
    # hand: knots 0 (dead), 1 (X member), 2 (Y member); 0 holds a with 1 and b with 2, and c with both? Use the engine.
    S = pm.from_stars([[0, 1, 2], [0, 3, 4], [1, 3, 5, 6]])   # knot 2 holds 1 (with 0) and 3 (with 1)
    S.made = [0, 0, 0]
    law = mcc.Spec('FLOOR1', 'CANCEL-OFFSHOOT', 'MET', 'parity').law()
    b = {'kind': 'offshoot', 'parents': (0,), 'inputs': [2]}
    full = pm.take_candidates(S, 'MET', b)
    mask = pm.Mask('XY', {0}, {2})
    mcc._TC_MASK[0] = mask
    try:
        masked = pm.take_candidates(S, 'MET', b)
    finally:
        mcc._TC_MASK[0] = None
    # knot 0 meets 1 and 2; MET candidates: eligible distinctions held by 1 or 2 not held by 0: 3 (held by 1 and 2)
    check('fully masked filter removes a candidate held by the other side', full == [[3]] and masked == [[]],
          {'full': full, 'masked': masked})
    b2 = {'kind': 'offshoot', 'parents': (1,), 'inputs': [4]}
    mcc._TC_MASK[0] = mask
    try:
        other = pm.take_candidates(S, 'MET', b2)
    finally:
        mcc._TC_MASK[0] = None
    check('fully masked filter leaves a birth with no parent on a side alone',
          other == pm.take_candidates(S, 'MET', b2), other)
    del law


def t_plant():
    """The planted parts (DC 4.7): two parts of Y's form (two members holding one usable loose distinction each in one
    met set), descended from X only, read on the placed copy only."""
    g = mcc.Growth(mcc.start_by_id('n4-g17-3232')['stars'], mcc.Spec('FLOOR1', 'CANCEL-OFFSHOOT', 'MET', 'parity'),
                   'n4-g17-3232', 0)
    R3 = g.roster(3)
    X, Y = [19, 20, 22, 23, 24], [18, 21]
    ok_parts = tuple(X) in R3.parts and tuple(Y) in R3.parts
    ref = g.ref(3, X, Y)
    got, c = mcc.placed_form_reading(g.G.snaps, g.G.records, ref, 4, 19)
    T, extra = mcc.placed_state(g.G.snaps[4], 4, 19)
    check('planted case: X and Y as listed after round 3, Y one met set of two members holding one',
          ok_parts and ref.yform.sig == (2, ((1, 0), (1, 0)), (2,)), {'parts': R3.parts[:12], 'ysig': ref.yform.sig})
    check('planted placement gives two parts of Y\'s form from X only (the form reading met)',
          'form' in got and c.get('X only', 0) >= 2, {'got': sorted(got), 'counts': c, 'extra': extra})
    check('planted placement leaves the state itself unchanged', g.G.snaps[4].n_knots + 6 == T.n_knots)


def t_reduced_parity(states):
    """The parity knot test on the reduced structure (dev 39) against the fold engine's test on the whole structure:
    every knot of every state of the sampled growths, and of drawn structures with many loose places."""
    n = bad = 0
    for sid, sp, g in states:
        for S in g.snaps:
            a = mcc.K.parity_test(S)
            b = mcc.parity_verdicts(S)
            n += a['n']
            if a['pass'] != b['pass'] or b['disagree']:
                bad += 1
    rnd = random.Random(39)
    for k in range(400):
        nk = rnd.randint(2, 8)
        nd = rnd.randint(3, 14)
        stars = []
        for _ in range(nk):
            stars.append(sorted(rnd.sample(range(nd), rnd.randint(2, min(6, nd)))))
        used = sorted({d for st in stars for d in st})
        m = {d: i for i, d in enumerate(used)}
        S = pm.from_stars([[m[d] for d in st] for st in stars])
        a = mcc.K.parity_test(S)
        bt, _ = mcc.K.brute(S, 'parity') if S.n_distinctions <= 16 else (None, None)
        b = mcc.parity_verdicts(S)
        n += a['n']
        if a['pass'] != b['pass'] or (bt is not None and bt != b['pass']):
            bad += 1
    check('parity verdicts on the reduced structure equal the fold engine\'s on the whole (and brute force)',
          bad == 0, {'knots': n, 'bad': bad})


def t_fisher():
    p = mcc.fisher_greater(7, 100, 0, 100)
    p6 = mcc.fisher_greater(6, 100, 0, 100)
    check('Fisher one-sided: 7 of 100 against 0 passes at 0.01, 6 does not', p <= 0.01 < p6, {'p7': p, 'p6': p6})
    ac = mcc.agresti_caffo(10, 100, 0, 100)
    check('Agresti-Caffo interval', ac[0] > 0, ac)


def main():
    t0 = time.time()
    t_sampler()
    t_seeds()
    t_pairs()
    st = grown_states()
    t_roster(st)
    t_ties(st)
    t_row()
    t_identity_wrapper()
    t_cached_candidates()
    t_chooser_order(st)
    t_full_mask()
    t_reduced_parity(st)
    t_plant()
    t_fisher()
    allp = all(v['pass'] for v in RESULTS.values())
    print('ALL PASS' if allp else 'SOME FAIL', round(time.time() - t0, 1), 's')
    os.makedirs(mcc.OUT, exist_ok=True)
    with open(os.path.join(mcc.OUT, 'test_mcc.json'), 'w') as f:
        json.dump({'all_pass': allp, 'tests': RESULTS}, f, indent=1, default=str)


if __name__ == '__main__':
    main()
