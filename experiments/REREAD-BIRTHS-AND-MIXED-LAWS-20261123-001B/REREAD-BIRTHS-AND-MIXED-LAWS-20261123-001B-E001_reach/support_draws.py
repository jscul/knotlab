"""Row G, part 3, on the histories grown in T2's draw population: along every history (funded draw, law of the founders,
assignment of the newborns' laws, 2 or 3 choices) the set of allowed words on the start's distinctions, after forgetting the
fresh ones, is the same at stage 1 as at stage 0 (it never shrinks, and growth adds no word).  Exact, by contraction
(int64 counts): the founders hold no fresh distinction and the round-1 newborns hold only the start's loose distinctions and
fresh ones, so the projection on the start's distinctions is the founders' allowed set times G(loose values), G the
newborns' product summed over the fresh distinctions; the support is unchanged iff G > 0 at every loose pattern the founders
allow.  The round-1 newborns hold disjoint inputs and fresh distinctions, so G is a product of one factor per newborn and
G > 0 for every assignment iff each newborn's factor (each law) is positive at every input pattern; that is what is
checked.  The closing births (parity rule, implied sign) are checked on the whole start.  Writes support_draws.json.
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402
import t2  # noqa: E402

t0 = time.time()
res = dict(histories=0, assignments=0, shrinks=0, grows=0, closing=0, D0_max=0)
for dr, f in t2.funded_draws():
    stars = [tuple(s) for s in dr['stars']]
    D0 = sorted({d for s in stars for d in s})
    res['D0_max'] = max(res['D0_max'], len(D0))
    for flaw in ('parity', 'nae'):
        if not f[flaw]:
            continue
        founders = ['even' if flaw == 'parity' else 'nae'] * len(stars)
        counts = {}
        for st_ in stars:
            for d in st_:
                counts[d] = counts.get(d, 0) + 1
        loose = tuple(sorted(d for d, v in counts.items() if v == 1))
        base = c.contract([(s, c.lt(l, len(s))) for s, l in zip(stars, founders)], loose).reshape(-1) > 0
        hn = c.grow(stars, 'nae', rounds=1, dmax=10 ** 9)
        hp = c.grow(stars, 'parity', rounds=1, dmax=10 ** 9) if flaw == 'parity' else None
        res['histories'] += 1
        nb = hn['n_at'][-1] - len(stars)
        assert all(d in loose or d > max(counts) for kk in range(len(stars), hn['n_at'][-1]) for d in hn['stars'][kk])
        # the round-1 newborns hold disjoint loose inputs and disjoint fresh distinctions, so G is the product of one
        # factor per newborn (its law summed over its fresh distinctions): G > 0 everywhere, for every assignment, iff
        # each newborn's factor is positive at every input pattern under each law
        ins = [d for kk in range(len(stars), hn['n_at'][-1]) for d in hn['stars'][kk] if d in loose]
        assert len(ins) == len(set(ins))
        ok_all = True
        for kk in range(len(stars), hn['n_at'][-1]):
            sk = hn['stars'][kk]
            inp = tuple(d for d in sk if d in loose)
            for law in ('even', 'odd', 'nae'):
                g = c.contract([(sk, c.lt(law, len(sk)))], inp).reshape(-1)
                ok_all &= bool((g > 0).all())
        for k in (2, 3):
            n_as = k ** nb
            res['assignments'] += n_as
            res['shrinks'] += 0 if ok_all else n_as
        if hp is not None and hp['closing']:
            # the closing birth with its implied sign adds no constraint
            sclose = hp['stars'][len(stars)]
            nm, Bw = t2.allowed_words(stars, founders)
            pos = {d: i for i, d in enumerate(nm)}
            par = Bw[:, [pos[d] for d in sclose]].sum(1) % 2
            imp = 'even' if int(par[0]) == 0 else 'odd'
            fs = [(s, c.lt(l, len(s))) for s, l in zip(stars, founders)]
            b0 = c.contract(fs, tuple(D0)).reshape(-1) > 0
            row = c.contract(fs + [(sclose, c.lt(imp, len(sclose)))], tuple(D0)).reshape(-1) > 0
            res['closing'] += 1
            res['assignments'] += 1
            res['shrinks'] += bool((b0 & ~row).any())
            res['grows'] += bool((row & ~b0).any())
res['seconds'] = round(time.time() - t0, 1)
(c.ART / 'support_draws.json').write_text(json.dumps(res, indent=1))
print(json.dumps(res))
