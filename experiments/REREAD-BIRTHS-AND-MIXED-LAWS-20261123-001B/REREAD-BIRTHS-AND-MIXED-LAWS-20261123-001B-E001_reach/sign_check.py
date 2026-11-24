"""Check, once, the pre-registration's statement "a newborn has a fresh distinction, so its parity sign is a renaming of that
distinction: a newborn's law is parity or not-all-equal, two choices".

For the founder starts of the given targets (default: every 7-knot target and the pencil 9-knot target), at every stage of
growth, the set of observer tables (divided by their gcd) met under the three choices even / odd / not-all-equal for every
newborn is compared with the set met under the two choices even / not-all-equal.  Also compared: hidden tables, hidden
excess, largest hidden score.  The observer distinctions are never renamed.  Writes sign_check.json.
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> [--tids 0,1,...] [--maxnew 9]
"""
import argparse
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--tids', default=None)
ap.add_argument('--maxnew', type=int, default=9)
args = ap.parse_args()
t0 = time.time()
targets = json.loads((c.ART / 'targets.json').read_text())
tk = {t['tid']: t['knots'] for t in c.load_targets()}
if args.tids:
    tids = {int(x) for x in args.tids.split(',')}
else:
    tids = {t['tid'] for t in targets if t['n_knots'] == 7 or 'pencil' in t['tags']}
starts = [json.loads(l) for l in (c.ART / 'starts.jsonl').open()]
ev = c.Evaluator()
res = dict(tids=sorted(tids), histories=0, skipped_too_many_newborns=0, stages=0, stages_same_set=0,
           stages_three_has_more=0, stages_two_has_more=0, stages_same_hidden_set=0, excess_two=0, excess_three=0,
           best_hidden_two=None, best_hidden_three=None, examples=[])


def key(x):
    return x.tobytes() if x.dtype != object else repr(tuple(int(v) for v in x)).encode()


for si, s in enumerate(starts):
    if s['tid'] not in tids:
        continue
    stars, laws, names, obs, sub = c.start_stars(tk[s['tid']], s['mask'])
    h = c.grow(stars, 'nae')
    nf = h['n_at'][0]
    n_new = h['n_at'][-1] - nf
    if n_new > args.maxnew:
        res['skipped_too_many_newborns'] += 1
        continue
    res['histories'] += 1
    for t, n in enumerate(h['n_at']):
        nb = n - nf
        sets = {}
        for ch in (('even', 'nae'), ('even', 'odd', 'nae')):
            R = (np.array(list(itertools.product(range(len(ch)), repeat=nb)), dtype=np.int8).reshape(-1, nb) if nb
                 else np.zeros((1, 0), dtype=np.int8))
            T = c.stage_tables(h['stars'], laws, nf, n, R, obs, choices=ch)
            norm = [c.normalize(r) for r in T]
            evs = ev.run(norm)
            sets[len(ch)] = ({key(x) for x in norm}, {key(x) for x, e in zip(norm, evs) if e[0] and e[1]},
                             sum(c.is_excess(e) for e in evs),
                             max([e[2] for e in evs if e[0] and e[1] and e[2] is not None], default=None))
        res['stages'] += 1
        a2, a3 = sets[2], sets[3]
        if a2[0] == a3[0]:
            res['stages_same_set'] += 1
        res.setdefault('stages_by_t', {}).setdefault(str(t), 0)
        res['stages_by_t'][str(t)] += 1
        if a3[0] - a2[0]:
            res['stages_three_has_more'] += 1
            res.setdefault('three_has_more_by_t', {}).setdefault(str(t), 0)
            res['three_has_more_by_t'][str(t)] += 1
            if len(res['examples']) < 5:
                res['examples'].append(dict(si=si, tid=s['tid'], mask=s['mask'], t=t, two=len(a2[0]), three=len(a3[0]),
                                            only_three=len(a3[0] - a2[0])))
        if a2[0] - a3[0]:
            res['stages_two_has_more'] += 1
        res['stages_same_hidden_set'] += a2[1] == a3[1]
        res['excess_two'] += a2[2]
        res['excess_three'] += a3[2]
        for k, v in (('best_hidden_two', a2[3]), ('best_hidden_three', a3[3])):
            if v is not None and (res[k] is None or v > res[k]):
                res[k] = v
# brute-force confirmation of the first stage where three choices give more tables: one table met only under three
# choices, enumerated word by word, is compared with the word-by-word tables of every two-choice assignment
if res['examples']:
    x = res['examples'][0]
    s = starts[x['si']]
    stars, laws, names, obs, sub = c.start_stars(tk[s['tid']], s['mask'])
    h = c.grow(stars, 'nae')
    nf, n = h['n_at'][0], h['n_at'][x['t']]
    nb = n - nf
    two = {}
    for a in itertools.product(range(2), repeat=nb):
        L = list(laws) + [('even', 'nae')[i] for i in a]
        two.setdefault(key(c.normalize(c.brute_table(h['stars'][:n], L, obs))), a)
    found = None
    for a in itertools.product(range(3), repeat=nb):
        L = list(laws) + [('even', 'odd', 'nae')[i] for i in a]
        T = c.normalize(c.brute_table(h['stars'][:n], L, obs))
        if key(T) not in two:
            found = dict(assignment=[('even', 'odd', 'nae')[i] for i in a],
                         knots=[c.fmt_knot(L[k], [names[d] if d < len(names) else f'f{d}' for d in h['stars'][k]])
                                for k in range(n)], table=[int(v) for v in T])
            break
    res['brute_force_confirmation'] = dict(example=x, two_choice_tables=len(two), three_only_found=found)
res['seconds'] = round(time.time() - t0, 1)
(c.ART / 'sign_check.json').write_text(json.dumps(res, indent=1))
print(json.dumps(res))
