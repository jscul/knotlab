"""Verify every distinct final structure of the reductions by full enumeration of its four finished structures, write each
out as a list of knots with its number of knots and of extra holders, and record why each single further removal fails.

usage: verify_reduced.py
"""
import json, glob, time
import numpy as np
import common as c, structures as st

t0 = time.time()
out = {}
for start, (KA0, KB0, cls) in st.STARTS.items():
    ALL = [('A', k) for k in KA0] + [('B', k) for k in KB0]
    finals = []
    for f in sorted(glob.glob(f'{c.ART}/reduce_{start}_*.json')):
        finals += json.load(open(f))['finals']
    seeds = sorted(f['seed'] for f in finals)
    distinct = {}
    for f in finals: distinct.setdefault(tuple(f['kept']), []).append(f['seed'])
    res = []
    for kept, sd in distinct.items():
        kA = [ALL[i][1] for i in kept if ALL[i][0] == 'A']; kB = [ALL[i][1] for i in kept if ALL[i][0] == 'B']
        fc = c.full_check(kA, kB)
        meas = c.structure_measures(kA, kB)
        # each single removal from the final structure
        rem = []
        for q in kept:
            k2 = [i for i in kept if i != q]
            a2 = [ALL[i][1] for i in k2 if ALL[i][0] == 'A']; b2 = [ALL[i][1] for i in k2 if ALL[i][0] == 'B']
            hA = c.holders(a2); hB = c.holders(b2)
            if not (all(hA.get(o, 0) >= 1 for o in c.OBS['A']) and all(hB.get(o, 0) >= 1 for o in c.OBS['B'])):
                rem.append(dict(knot=c.fmt_knots([ALL[q][1]])[0], side=ALL[q][0], result='leaves an observer distinction with no old holder')); continue
            M, TA, TB, sh = c.old_table(a2, b2)
            if M.sum() == 0:
                rem.append(dict(knot=c.fmt_knots([ALL[q][1]])[0], side=ALL[q][0], result='no allowed old word')); continue
            hA_, hB_ = c.exact_hidden(M)
            v = c.exact_best(M, slack=1e-9)[0]
            rem.append(dict(knot=c.fmt_knots([ALL[q][1]])[0], side=ALL[q][0], hidden=bool(hA_ and hB_), hidden_A=bool(hA_), hidden_B=bool(hB_),
                            score=str(v), change=str(c.exact_tv(M)), shared=sh))
        res.append(dict(kept=list(kept), seeds=len(sd), knots_A=c.fmt_knots(kA), knots_B=c.fmt_knots(kB), measures=meas,
                        full_enumeration=dict(hidden=fc['hidden'], score=str(fc['score']), change=str(fc['change']),
                                              agrees_with_side_tables=fc['agrees_with_side_tables'], finished_words=fc['words_finished'],
                                              finished_distinctions=fc['distinctions_finished']),
                        single_removals=rem))
        print(start, 'final', len(kept), 'knots; seeds', len(sd), '; full enumeration: hidden', fc['hidden'], 'score', fc['score'],
              'agrees', fc['agrees_with_side_tables'], f'[{time.time() - t0:.0f}s]', flush=True)
        for r in rem: print('   remove', r['side'], r['knot'], '->', r.get('result') or f"hidden {r['hidden']} (A {r['hidden_A']}, B {r['hidden_B']}), score {r['score']}")
    out[start] = dict(cls=cls, orders=len(finals), seeds=[seeds[0], seeds[-1]] if seeds else None, distinct_finals=res)
json.dump(out, open(f'{c.ART}/reduce_verified.json', 'w'), indent=1, default=str)
print(f'done {time.time() - t0:.0f}s')
