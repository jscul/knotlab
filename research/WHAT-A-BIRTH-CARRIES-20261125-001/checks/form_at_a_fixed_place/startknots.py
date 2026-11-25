"""For every study of the mixed family: the last round at which a start knot is still a member of the roster."""
import sys, json, collections
import form
from form import eng, seed, build, FIRSTS, forms
out = collections.defaultdict(collections.Counter)
for take in (None, 'MET-SOLE'):
    for ration in ('ORD', 'CAP-3', 'FLOOR1'):
        for tr in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT'):
            law = eng.Law(ration, tr, take, 'nae')
            for fn, (shape, loose, site) in FIRSTS.items():
                for name, sh, lo, at in forms():
                    stars, nf = build(seed(shape, loose), site, seed(sh, lo), at)
                    run = eng.Run(law, stars=stars, rounds=6, knot_bound=3000)
                    ls = max([t for t in range(1, run.rounds_read + 1) if any(u < len(stars) for u in run.recs[t - 1]['members'])] or [0])
                    out[(str(take), tr)][ls] += 1
for k in sorted(out): print(k, sorted(out[k].items()))
