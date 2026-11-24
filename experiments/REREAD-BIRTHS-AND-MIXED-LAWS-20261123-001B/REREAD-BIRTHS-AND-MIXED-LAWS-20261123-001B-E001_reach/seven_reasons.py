"""Why each proper founder start of the seven-knot structure fails to reach its table (REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B,
"Runs and stop rule": "the reason each seven-knot founder start fails").

For each of its founder starts: the knots left out; the support of the start's observer table against the target's (growth
keeps the support: checked on every history in grow_t1.py); the history (stages, distinctions, outcome); and, for each
left-out knot, the structural facts that decide whether ordinary growth could make it: whether it holds a distinction no
other knot of the target holds (every newborn under the not-all-equal rule has a fresh distinction), whether it shares two
distinctions with one other knot (a newborn takes one distinction from each parent, so two knots sharing two distinctions
were both founders), and whether the start knots it meets are pairwise adjacent in the start's end (a newborn's parents
are pairwise adjacent).  Writes seven_reasons.json.
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402

targets = json.loads((c.ART / 'targets.json').read_text())
seven = [t for t in targets if 'seven' in t['tags']][0]
tk = {t['tid']: t['knots'] for t in c.load_targets()}
ks = tk[seven['tid']]
starts = [json.loads(l) for l in (c.ART / 'starts.jsonl').open() if json.loads(l)['tid'] == seven['tid']]
T1 = {}
for f in sorted(c.ART.glob('t1_c2_[0-9]*.jsonl')):
    for l in f.open():
        r = json.loads(l)
        if r['tid'] == seven['tid']:
            T1[r['mask']] = r
Ttar = np.array(seven['table'], dtype=np.int64)
sup_tar = set(c.support_key(Ttar))
hold = c.holders_of(ks)
knot_facts = []
for k, (law, mem) in enumerate(ks):
    own = [m for m in mem if len(hold[m]) == 1]
    share2 = [j for j in range(len(ks)) if j != k and len(set(mem) & set(ks[j][1])) >= 2]
    knot_facts.append(dict(knot=c.fmt_knot(law, mem), own_distinctions=own,
                           shares_two_with=[c.fmt_knot(*ks[j]) for j in share2]))
rows = []
for s in starts:
    stars, laws, names, obs, sub = c.start_stars(ks, s['mask'])
    T0 = c.stage_tables(stars, laws, len(stars), len(stars), np.zeros((1, 0), np.int8), obs)[0]
    sup0 = set(c.support_key(T0))
    end = c.from_stars_ext(stars)
    adj = c.EO.neighbors(end)
    missing = [k for k in range(len(ks)) if not s['mask'] >> k & 1]
    mfacts = []
    for k in missing:
        meets = [sub.index(j) for j in sub if set(ks[j][1]) & set(ks[k][1])]
        live = [m for m in meets if m in end.opens]
        pair_ok = all(b in adj.get(a, set()) for a, b in itertools.combinations(live, 2))
        mfacts.append(dict(knot=knot_facts[k]['knot'], own_distinctions=knot_facts[k]['own_distinctions'],
                           shares_two_with=knot_facts[k]['shares_two_with'],
                           start_knots_it_meets=[c.fmt_knot(laws[m], [names[d] for d in stars[m]]) for m in meets],
                           of_them_live=len(live), all_met_are_live=len(live) == len(meets),
                           live_ones_pairwise_adjacent=pair_ok))
    h = T1[s['mask']]
    can_be_newborn = [bool(f['own_distinctions']) and not f['shares_two_with'] and f['all_met_are_live']
                      and f['live_ones_pairwise_adjacent'] for f in mfacts]
    reason = []
    if sup0 != sup_tar:
        reason.append(f'the start already lacks the support: {len(sup0)} observer words allowed, the target {len(sup_tar)}'
                      f' ({"a superset" if sup_tar <= sup0 else "not a superset"}); growth keeps the support')
    elif not any(st['proportional'] for st in h['stages']):
        reason.append('same support; growth keeps it and changes only the numbers of completions, never to the target\'s')
    nb = [f['knot'] for f, ok in zip(mfacts, can_be_newborn) if not ok]
    if nb:
        reason.append('left-out knot(s) that no ordinary birth can make: ' + '; '.join(
            f['knot'] + ' (' + ', '.join(x for x in (
                'no distinction of its own' if not f['own_distinctions'] else '',
                'shares two distinctions with ' + ' and '.join(f['shares_two_with']) if f['shares_two_with'] else '',
                'meets a spent start knot' if not f['all_met_are_live'] else '',
                'the start knots it meets are not pairwise adjacent' if not f['live_ones_pairwise_adjacent'] else '')
                if x) + ')' for f, ok in zip(mfacts, can_be_newborn) if not ok))
    rows.append(dict(mask=s['mask'], founders=[c.fmt_knot(*ks[k]) for k in sub], left_out=[c.fmt_knot(*ks[k]) for k in missing],
                     start_support=len(sup0), target_support=len(sup_tar), superset=sup_tar <= sup0,
                     n_at=h['n_at'], D_at=h['D_at'], outcome=h['outcome'], assignments=h['assignments'],
                     proportional_any=any(st['proportional'] for st in h['stages']),
                     excess_any=any(st['excess'] for st in h['stages']),
                     best_hidden=max([st['best_hidden_float'] for st in h['stages'] if st['best_hidden_float'] is not None],
                                     default=None),
                     left_out_facts=mfacts, reason=reason))
out = dict(target=seven['knots'], knot_facts=knot_facts, starts=len(rows),
           start_support_sizes=dict(Counter(r['start_support'] for r in rows)),
           all_lack_support=all(r['start_support'] != r['target_support'] for r in rows), rows=rows)
(c.ART / 'seven_reasons.json').write_text(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k != 'rows'}, indent=1))
for r in rows:
    print(r['mask'], r['left_out'], r['start_support'], r['outcome'], r['n_at'], r['best_hidden'])
    for x in r['reason']:
        print('   ', x)
