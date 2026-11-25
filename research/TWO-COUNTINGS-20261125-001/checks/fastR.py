"""Faster recount of rule R's 214 records: both countings (finish; start from stage 0 and 1), score, hiding, knot test.
Same definitions as myscore.py / mykt_np.py, vectorised."""
import glob
import gzip
import json
import sys
import time
from fractions import Fraction as Fr

import numpy as np

sys.path.insert(0, 'CHECK_SCRATCH')
from mykt_np import popcount, test_structure
from myscore import score, change, setting_knots

OP = 'REPO_ROOT/artifacts/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001_reread_reach/'
RA = ('x1', 'x2', 'x3', 'za')
RB = ('y1', 'y2', 'y3', 'zb')


def allowed_fixed(rules, gpos):
    remaining = list(range(len(rules)))
    held = set()
    states = np.zeros(1, dtype=np.int64)
    while remaining:
        best = max(remaining, key=lambda i: (sum(p in held for p in rules[i][1]), -i))
        remaining.remove(best)
        law, P = rules[best]
        new = [p for p in P if p not in held]
        held |= set(new)
        if new:
            ext = np.zeros(2 ** len(new), dtype=np.int64)
            for e in range(2 ** len(new)):
                for q, p in enumerate(new):
                    if (e >> q) & 1:
                        ext[e] |= np.int64(1) << np.int64(gpos[p])
            states = (states[:, None] | ext[None, :]).ravel()
        m = np.int64(0)
        for p in P:
            m |= np.int64(1) << np.int64(gpos[p])
        s = popcount(states & m)
        keep = (s % 2 == 0) if law == 'even' else ((s % 2 == 1) if law == 'odd' else ((s > 0) & (s < len(P))))
        states = states[keep]
    return held, np.sort(states)


def code(states, names, gpos):
    c = np.zeros(len(states), dtype=np.int64)
    for q, p in enumerate(names):
        c |= ((states >> np.int64(gpos[p])) & 1) << np.int64(q)
    return c


def joint_from(states, D, gpos):
    """states of the finish and their integer denominators D (weight 1/D); returns {(u,v): Fraction} renormalised."""
    u = code(states, RA, gpos)
    v = code(states, RB, gpos)
    key = u * 16 + v
    P = {}
    # group (key, D) with counts
    arr = np.stack([key, D], axis=1)
    uniq, cnt = np.unique(arr, axis=0, return_counts=True)
    for (k, d), c in zip(uniq.tolist(), cnt.tolist()):
        uu = tuple((k // 16 >> q) & 1 for q in range(4))
        vv = tuple(((k % 16) >> q) & 1 for q in range(4))
        P[(uu, vv)] = P.get((uu, vv), 0) + Fr(c, d)
    tot = sum(P.values())
    return {k: x / tot for k, x in P.items()}, tot


def run(stages_ab, s):
    """stages_ab[(a,b)] = list of stage rule lists. s = 'finish' or an int stage."""
    Ps = {}
    kept = {}
    for ab, stages in stages_ab.items():
        allv = sorted({p for st in stages for _, P in st for p in P})
        gpos = {v: i for i, v in enumerate(allv)}
        cum = []
        acc = []
        for st in stages:
            acc = acc + list(st)
            cum.append(list(acc))
        if s == 'finish':
            _, fin = allowed_fixed(cum[-1], gpos)
            Ps[ab], kept[ab] = joint_from(fin, np.ones(len(fin), dtype=np.int64), gpos)
            continue
        en = [allowed_fixed(c, gpos) for c in cum]
        fin = en[-1][1]
        D = np.full(len(fin), len(en[s][1]), dtype=np.int64)
        for j in range(s + 1, len(stages)):
            m = np.int64(0)
            for p in en[j - 1][0]:
                m |= np.int64(1) << np.int64(gpos[p])
            proj = en[j][1] & m
            uq, cnt = np.unique(proj, return_counts=True)
            idx = np.searchsorted(uq, fin & m)
            D = D * cnt[idx]
        assert (D < 2 ** 62).all()
        Ps[ab], kept[ab] = joint_from(fin, D, gpos)
    return score(Ps), change(Ps), kept


def parse(x):
    law, rest = x.split('(')
    return (law, tuple(rest.rstrip(')').split(',')))


if __name__ == '__main__':
    R = []
    for f in sorted(glob.glob(OP + 'arm1_gains_three_*.jsonl.gz')):
        R += [json.loads(l) for l in gzip.open(f, 'rt')]
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    KA, KB = setting_knots()
    out = []
    t0 = time.time()
    for i in range(lo, min(hi, len(R))):
        r = R[i]
        ks = [parse(k) for k in r['knots']]
        nb = len(r['births'][0])
        part, births = ks[:len(ks) - nb], ks[len(ks) - nb:]
        st = {(a, b): [part, births, [KA[a], KB[b]]] for a in (0, 1) for b in (0, 1)}
        f = run(st, 'finish')
        s0 = run(st, 0)
        s1 = run(st, 1)
        fails = {}
        for a in (0, 1):
            for b in (0, 1):
                T = test_structure(ks + [KA[a], KB[b]])
                fails['%d%d' % (a, b)] = [x['rule'] for x in T['rules'] if not x['whole']]
        fails['part'] = [x['rule'] for x in test_structure(part)['rules'] if not x['whole']]
        fails['part+round'] = [x['rule'] for x in test_structure(ks)['rules'] if not x['whole']]
        rec = {'i': i, 'tid': r.get('tid'), 'recorded': r['eval'][3], 'finish': str(f[0]), 'finish_change': str(f[1]),
               'start': str(s0[0]), 'start_change': str(s0[1]), 'start_kept': [str(x) for x in s0[2].values()],
               'stage1': str(s1[0]), 'stage1_change': str(s1[1]), 'fails': fails}
        out.append(rec)
        print(i, rec['finish'], rec['recorded'], rec['start'], rec['stage1'], round(time.time() - t0, 1), flush=True)
    json.dump(out, open('fastR_%d_%d.json' % (lo, hi), 'w'))
