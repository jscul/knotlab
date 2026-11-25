"""Part 1: the gates.  Brute force against the engine; the score's merged method against the unmerged one and against
an independent enumeration of both sides; Known 1-3 reproduced (PR, "Known before the runs")."""
from __future__ import annotations

import itertools
import random
import sys
import time
from fractions import Fraction as Fr

import lemma
import specs
import tc

T0 = time.time()
tc.cap_memory()
S = tc.load_structures()
out = {'part': 1, 'checks': [], 'known': {}}
fail = []


def note(name, ok, **kw):
    out['checks'].append({'check': name, 'pass': bool(ok), **kw})
    if not ok:
        fail.append(name)
    print(('PASS ' if ok else 'FAIL ') + name, {k: (tc.fstr(v) if isinstance(v, Fr) else v) for k, v in kw.items()},
          flush=True)


# ---- G1: allowed states, brute force against the engine
specs.file_checks(S)
note('structures.json finished structures = start + the TD 4.1 setting knots', True)
for key in ['eleven (start)', 'eleven + settings 00', 'eleven + settings 01', 'eleven + settings 10',
            'eleven + settings 11', 'smallest gain: part', 'smallest gain: part + rule-Q round 1',
            'smallest gain finished 00', 'smallest gain finished 01', 'smallest gain finished 10',
            'smallest gain finished 11']:
    ks = S[key]
    order = tc.order_vars(ks)
    bt = tc.enum_backtrack(ks, order)
    bf = tc.enum_brute(ks, order)
    nu = [int(x) for x in tc.enum_numpy(ks, order)]
    note('allowed states, backtracking = knot-by-knot (numpy) = brute force: ' + key, bt == bf == nu, n=len(bt), distinctions=len(order))

# ---- G2: histories: completions and counting from the start against brute force
def brute_history(stages):
    """Brute-force reference: A(S_j) by enumerating every assignment of the distinctions of S_j; c_j by counting."""
    allk = [tc.as_knot(k) for st in stages for k in st]
    order = tc.variables_of([k for k in allk])
    idx = {v: i for i, v in enumerate(order)}
    A = []
    for j in range(len(stages)):
        ks = [tc.as_knot(k) for st in stages[:j + 1] for k in st]
        vs = tc.variables_of(ks)
        sub = tc.enum_brute(ks, vs)
        # re-express over the global order
        conv = []
        for s in sub:
            w = 0
            for i, v in enumerate(vs):
                if (s >> i) & 1:
                    w |= 1 << idx[v]
            conv.append(w)
        A.append((vs, set(conv)))
    return order, idx, A


for label, sp in [('eleven x2-x3/y2-y3', specs.eleven()), ('smallest gain', specs.smallest_gain())]:
    for a, b in lemma.PAIRS:
        st = list(sp['pre']) + [sp['KA'][a] + sp['KB'][b]]
        H = tc.History(st)
        order, idx, A = brute_history(st)
        # map engine states into the brute order
        def conv(w):
            x = 0
            for v, i in H.idx.items():
                if (w >> i) & 1:
                    x |= 1 << idx[v]
            return x
        same = all({conv(int(w)) for w in H.A[j]} == A[j][1] for j in range(len(st)))
        # completions: for each o of A(S_{j-1}) the number of w in A(S_j) restricting to o
        okc = True
        for j in range(1, len(st)):
            prev_vars = A[j - 1][0]
            pm = 0
            for v in prev_vars:
                pm |= 1 << idx[v]
            cnt = {}
            for w in A[j][1]:
                cnt[w & pm] = cnt.get(w & pm, 0) + 1
            for o, c in H.cdict(j).items():
                if cnt.get(conv(o), 0) != c:
                    okc = False
        # counting from the start by brute force
        W, kept = tc.counting(H, 0)
        W = tc.as_dict(H, W)
        okw = True
        n0 = len(A[0][1])
        for w, x in W.items():
            cw = conv(w)
            den = n0
            for j in range(1, len(st)):
                pm = 0
                for v in A[j - 1][0]:
                    pm |= 1 << idx[v]
                den *= sum(1 for y in A[j][1] if y & pm == cw & pm)
            if Fr(1, den) != x:
                okw = False
        note('history %s %d%d: A(S_j), completions and counting from the start = brute force' % (label, a, b),
             same and okc and okw, stages=len(st), final=len(H.A[-1]))

# ---- G3: the score
def brute_score(P):
    """Every f0, f1, g0, g1 enumerated (tiny tables only)."""
    Uv = {a: sorted({u for b in (0, 1) for (u, v), x in P[(a, b)].items() if x}) for a in (0, 1)}
    Vv = {b: sorted({v for a in (0, 1) for (u, v), x in P[(a, b)].items() if x}) for b in (0, 1)}
    best = None
    for f0 in itertools.product((1, -1), repeat=len(Uv[0])):
        for f1 in itertools.product((1, -1), repeat=len(Uv[1])):
            for g0 in itertools.product((1, -1), repeat=len(Vv[0])):
                for g1 in itertools.product((1, -1), repeat=len(Vv[1])):
                    f = {0: dict(zip(Uv[0], f0)), 1: dict(zip(Uv[1], f1))}
                    g = {0: dict(zip(Vv[0], g0)), 1: dict(zip(Vv[1], g1))}
                    E = {ab: sum((f[ab[0]][u] * g[ab[1]][v] * x for (u, v), x in P[ab].items()), Fr(0))
                         for ab in P}
                    for p in tc.PLACEMENTS:
                        s = sum(((-1 if ab == p else 1) * E[ab] for ab in P), Fr(0))
                        if best is None or s > best:
                            best = s
    return best


rnd = random.Random('TWO-COUNTINGS|gate|scores')
ok_rand = True
for trial in range(60):
    P = {}
    for ab in lemma.PAIRS:
        t = {}
        for u in range(rnd.choice([2, 3])):
            for v in range(rnd.choice([2, 3])):
                t[(u, v)] = Fr(rnd.randint(0, 6))
        tot = sum(t.values()) or Fr(1)
        P[ab] = {k: x / tot for k, x in t.items() if x}
    s1, s2, s3 = tc.score_all(P), tc.score_all(P, merged=False), brute_score(P)
    if not (s1 == s2 == s3):
        ok_rand = False
        print('score mismatch', P, s1, s2, s3)
note('score: merged = unmerged = every f and g enumerated, on 60 drawn small tables', ok_rand)


def par_brute(P, kA, kB):
    """Every (T0, T1, T0', T1') enumerated with every placement (no best response)."""
    E = {}
    for (a, b), t in P.items():
        for TA in range(1, 1 << kA):
            for TB in range(1, 1 << kB):
                E[(a, b, TA, TB)] = sum((x * (-1) ** (((u & TA).bit_count() + (v & TB).bit_count()) & 1)
                                         for (u, v), x in t.items()), Fr(0))
    best = None
    for T in itertools.product(range(1, 1 << kA), range(1, 1 << kA), range(1, 1 << kB), range(1, 1 << kB)):
        vals = {(a, b): E[(a, b, T[a], T[2 + b])] for a in (0, 1) for b in (0, 1)}
        for p in tc.PLACEMENTS:
            s = sum(((-1 if ab == p else 1) * vals[ab] for ab in vals), Fr(0))
            if best is None or s > best:
                best = s
    return best


for label, sp in [('eleven x2-x3/y2-y3', specs.eleven()), ('smallest gain', specs.smallest_gain())]:
    Hs = lemma.histories(sp, {}, 'one')
    for sf, cname in ((0, 'from the start'), (-1, 'from the finish')):
        P, _ = lemma.tables(Hs, sf, sp['recA'], sp['recB'])
        m, u = tc.score_all(P), tc.score_all(P, merged=False)
        note('score merged = unmerged: %s %s' % (label, cname), m == u, merged=m, unmerged=u)
        pa, pb = tc.score_parity(P, 4, 4), par_brute(P, 4, 4)
        note('parity score = every choice enumerated directly: %s %s' % (label, cname), pa == pb, fast=pa, direct=pb)

# ---- G4: Known 1-3
K = {}
for oa in specs.OPT_A:
    for ob in specs.OPT_B:
        r = lemma.run_spec(specs.eleven(oa, ob), mixed=False,
                           extra_marginals={'(s1,s2)': ['s1', 's2']} if (oa, ob) == (('x2', 'x3'), ('y2', 'y3')) else None)
        v = r['variants'][0]
        K['eleven %s/%s' % ('-'.join(oa), '-'.join(ob))] = {
            'finish': (v['rows']['from the finish']['score_all'], v['rows']['from the finish']['hidden'],
                       v['rows']['from the finish']['score_parity']),
            'start': (v['rows']['from the start']['score_all'], v['rows']['from the start']['hidden'],
                      v['rows']['from the start']['score_parity']),
            'allowed': v['info']['allowed at the finish']}
        if 'marginals' in v['info']:
            K['eleven (s1,s2)'] = v['info']['marginals']
k1 = K['eleven x2-x3/y2-y3']
note('Known 1: 11-knot (x2,x3)/(y2,y3) from the finish 20/9 hidden', k1['finish'][0] == Fr(20, 9) and k1['finish'][1],
     score=k1['finish'][0], parity=k1['finish'][2])
note('Known 1: 11-knot (x2,x3)/(y2,y3) from the start 2 hidden', k1['start'][0] == 2 and k1['start'][1],
     score=k1['start'][0], parity=k1['start'][2])
others = [v for k, v in K.items() if k.startswith('eleven ') and k != 'eleven x2-x3/y2-y3' and k != 'eleven (s1,s2)']
note('Known 1: the other eight pairs 19/9 or 37/18 from the finish, hidden; 2 from the start, hidden',
     len(others) == 8 and all(v['finish'][0] in (Fr(19, 9), Fr(37, 18)) and v['finish'][1] for v in others)
     and all(v['start'][0] == 2 and v['start'][1] for v in others),
     finish=sorted({tc.fstr(v['finish'][0]) for v in others}), start=sorted({tc.fstr(v['start'][0]) for v in others}))
mg = K['eleven (s1,s2)']
note('Known 1: (s1,s2) moves by 1/3 from the finish under the second observer, 0 from the start',
     mg['(s1,s2) from the finish']["change under the second observer's setting"] == Fr(1, 3)
     and mg['(s1,s2) from the start']["change under the second observer's setting"] == 0
     and mg['(s1,s2) from the finish']["change under the first observer's setting"] == 0,
     finish=mg['(s1,s2) from the finish']["change under the second observer's setting"],
     start=mg['(s1,s2) from the start']["change under the second observer's setting"])
r = lemma.run_spec(specs.smallest_gain(), mixed=False)
v = r['variants'][0]['rows']
K['smallest gain'] = {k: (x['score_all'], x['hidden'], x['score_parity']) for k, x in v.items()}
note('Known 2: smallest gain 2 hidden from the part and from after the rule-Q round; 61/30 hidden from the finish',
     v['from the start']['score_all'] == 2 and v['from the start']['hidden'] and v['from stage 1']['score_all'] == 2
     and v['from stage 1']['hidden'] and v['from the finish']['score_all'] == Fr(61, 30) and v['from the finish']['hidden'],
     part=v['from the start']['score_all'], after_round=v['from stage 1']['score_all'],
     finish=v['from the finish']['score_all'], finish_parity=v['from the finish']['score_parity'])
for key, name, want in [('seven (start)', 'seven', Fr(19, 9)), ('eight (start)', 'eight', Fr(20, 9)),
                        ('nine, the pencil (start)', 'nine', Fr(20, 9))]:
    r = lemma.run_spec(specs.simple(key, name), mixed=False)
    v = r['variants'][0]['rows']
    K[name] = {k: (x['score_all'], x['hidden'], x['score_parity']) for k, x in v.items()}
    note('Known 3: %s from the finish %s hidden, from the start 2 hidden' % (name, tc.fstr(want)),
         v['from the finish']['score_all'] == want and v['from the finish']['hidden'] and v['from the start']['score_all'] == 2
         and v['from the start']['hidden'], finish=v['from the finish']['score_all'],
         finish_parity=v['from the finish']['score_parity'], start=v['from the start']['score_all'])
out['known'] = K
out['failed'] = fail
out['wall_s'] = round(time.time() - T0, 1)
tc.dump('part1_gates.json', out)
print('gates failed:', fail, 'wall', out['wall_s'])
sys.exit(1 if fail else 0)
