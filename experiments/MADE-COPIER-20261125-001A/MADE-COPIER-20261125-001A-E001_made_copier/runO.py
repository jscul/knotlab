"""Run O (PO2; B1's edge, D 7.9): made-2 to made-6 and the designs with Y present from round 0; FLOOR0 and ONE-FEWER with
the three treatments; MET and STEPS-1 with four rules; both knot laws; 5 rounds; at most 300 knots.

usage: python -B runO.py [--procs 4]
"""
import argparse
import os
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import mc  # noqa: E402

pm, K, P = mc.pm, mc.K, mc.P
DESIGNS_O = mc.DESIGNS_MADE + mc.DESIGNS_YSTART


def measure(S, D0, kl):
    return mc._proj_rank(S, D0) if kl == 'parity' else mc._nae_count(S, D0)


def without(S, knots_):
    T = S.copy()
    for u in knots_:
        for d in T.places[u]:
            T.holders[d].remove(u)
        T.places[u] = []
        T.removed.add(u)
        T.cand.discard(u)
    return T


def do(job):
    C.cap_memory(6)
    t0 = time.time()
    try:
        d = mc.design(job['design'])
        kl = job['knot_law']
        law = mc.make_law(job['base'], job['take'], job['choice'], kl)
        A = mc.grow(d, law, rounds=5, knot_bound=300)
        s = d.s
        out = dict(job, law=law.name(), rounds=A.rounds_done, stop=A.stop, guard=A.guard, knots=A.S.n_knots)
        if A.rounds_done < s + 2:
            out['read'] = False
            out['note'] = 'ends before round s + 2'
            return out
        S1 = A.snap[s + 1]
        xd = P.side_of(S1, d.X, s)
        D0 = sorted(mc.places_of(S1, xd))
        if len(D0) > 10:
            D0 = D0[:10]
        if len(D0) < 2:
            out['read'] = False
            out['note'] = 'fewer than two distinctions in D0'
            return out
        out['read'] = True
        out['D0'] = D0
        prev = measure(S1, D0, kl)
        change = None
        for t in range(s + 2, A.rounds_done + 1):
            cur = measure(A.snap[t], D0, kl)
            if cur != prev:
                change = (t, prev, cur)
                break
            prev = cur
        out['change'] = change
        if change:
            t = change[0]
            St = A.snap[t]
            desc = mc.descent_map(St, d.X, d.Y, s)
            rec = A.records[t - 1]
            nofresh = [b for b in rec['births'] if b['f'] == 0 and not b['implied']]
            ds = [desc.get(b['id']) for b in nofresh]
            by_y = bool(nofresh) and all(x == 'Y only' for x in ds)
            restored = None
            if by_y:
                restored = measure(without(St, [b['id'] for b in nofresh]), D0, kl) == change[1]
            out['births_with_nothing'] = [{'id': b['id'], 'kind': b['kind'], 'parents': b['parents'],
                                           'inputs': b['inputs'], 'descent': x} for b, x in zip(nofresh, ds)][:10]
            out['by births descended from Y only'] = bool(by_y and restored)
            kt = K.test_run(A.snap, law, rounds=[t])
            out['knot test at the round of the change'] = {'verdicts': kt['verdicts'], 'n_fails': len(kt['fails']),
                                                           'fails': kt['fails'][:6]}
        if kl == 'nae':
            # S1 does not hold under FLOOR0 and ONE-FEWER: read at every round (deviations 34)
            nd_s = A.snap[s].n_distinctions
            per = []
            for t in range(s + 1, A.rounds_done + 1):
                T = mc.ties(A.snap[t], 'nae', seed=t)
                per.append([c for c in T.classes if any(x >= nd_s for x in c)][:6])
            out['tie classes with a made distinction, per round'] = per
        out['seconds'] = round(time.time() - t0, 2)
        return out
    except Exception as e:
        return dict(job, error=repr(e), trace=traceback.format_exc())


def jobs():
    js = []
    for name in DESIGNS_O:
        for r in ('FLOOR0', 'ONE-FEWER'):
            for t in mc.T3:
                base = '%s(%s)' % (r, mc.TS[t])
                for take in ('MET', 'STEPS-1'):
                    for ch in mc.RULES:
                        for kl in ('nae', 'parity'):
                            js.append({'design': name, 'base': base, 'take': take, 'choice': ch, 'knot_law': kl})
    return js


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=4)
    args = ap.parse_args()
    js = jobs()
    C.log('run O:', len(js), 'runs')
    out = C.JsonLines('runO.jsonl.gz')
    with ProcessPoolExecutor(max_workers=args.procs) as ex:
        for i, f in enumerate(as_completed([ex.submit(do, j) for j in js])):
            r = f.result()
            out.write(r)
            if 'error' in r or (i + 1) % 200 == 0:
                C.log(i + 1, r.get('design'), r.get('base'), r.get('error', ''))
    out.close()


if __name__ == '__main__':
    main()
