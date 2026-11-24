# Thread's separate check of the census under rule Q, round 1, on every part hidden at exactly 2 (27 liftable + 24 others):
# the thread's own engine makes round 1 under every choice of the re-read distinctions; every law assignment to the
# newborns is scored by the thread's own enumeration of words.  Compared with the study's gain records.
# Run from the repository root: .venv/bin/python -B research/ONE-PARENT-REREAD-20261123-001/thread_checks/rule_q_census_check.py
import sys, os, json, glob, gzip, collections, itertools
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '../../REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001/thread_checks'))
import rule_q_engine as qe
import reach_enumeration as v
A = 'artifacts/ONE-PARENT-REREAD-20261123-001A/ONE-PARENT-REREAD-20261123-001A-E001_one_parent_reread/'
def lines(pat):
    for f in sorted(glob.glob(A + pat)):
        for l in gzip.open(f, 'rt'): yield json.loads(l)
parts = [r for r in lines('census_parts_c_*.jsonl.gz')]
at2 = [r for r in parts if r['stage0_eval'][0] and r['stage0_eval'][1] and r['stage0_eval'][3] == '2']
print('parts in the census:', len(parts), '| hidden at exactly 2:', len(at2), '| liftable:', sum(r['liftable'] for r in at2))
gains = collections.defaultdict(list)
for g in lines('census_gains_c_*.jsonl.gz'): gains[g['si']].append(g)
print('parts with a gain in the study:', len(gains), '| gain tables by arm and stage:', sorted(collections.Counter((g['arm'], g['t']) for gs in gains.values() for g in gs).items()))
tot = collections.Counter(); uni = {}
for r in at2:
    tk = [v.parse(k) for k in v.targets[r['tid']]['knots']]
    fk = [tk[i] for i in range(len(tk)) if r['mask'] >> i & 1]
    names = {}
    stars = [tuple(names.setdefault(m, len(names)) for m in mem) for _, mem in fk]
    back = {i: n for n, i in names.items()}
    g0 = qe.Q(stars, 'O'); g0.round()
    rr = [b for b in g0.births[0] if b['reread']]
    hold = collections.Counter(d for s in stars for d in s)
    opts = [sorted(d for d in stars[b['parents'][0]] if hold[d] >= 2) for b in rr]
    mine_uniform = set(); mine_mixed = set(); mine_any = False
    for ch in itertools.product(*opts):
        g = qe.Q(stars, 'O', choice=list(ch)); g.round()
        nb = g.births[0]
        new = [tuple(back.get(d, f'f{d}') for d in s) for s in g.stars[len(stars):]]
        same = len(set(ch)) < len(ch)
        for laws in itertools.product(('even', 'odd', 'nae'), repeat=len(new)):
            s = v.score(list(fk) + list(zip(laws, new)))
            if s[1] and s[0] > 2:
                key = (tuple(back[d] for d in ch), laws, str(s[0]))
                mine_mixed.add(key)
                if all(l == 'nae' for l in laws): mine_uniform.add((key[0], key[2], same))
        tot['round-1 choices tried'] += 1; tot['round-1 structures scored'] += 3 ** len(new)
        tot[('fresh counts of re-reading births', tuple(sorted(b['fresh'] for b in nb if b['reread'])))] += 1
    # the study's stage-1 gains for this part
    st = gains.get(r['si'], [])
    theirs_mixed = set(); theirs_uniform = set()
    for g in st:
        if g['t'] != 1: continue
        laws = tuple(k.split('(')[0] for k in g['knots'][len(fk):])
        ch = tuple(back[b['shared']] if isinstance(b['shared'], int) else b['shared'] for b in g['births'][0] if b['reread'])
        if g['arm'] == 'mixed': theirs_mixed.add((ch, laws, g['eval'][3]))
        else: theirs_uniform.add((ch, g['eval'][3], len(set(ch)) < len(ch)))
    kind = 'liftable' if r['liftable'] else 'other part at 2'
    tot[(kind, 'parts')] += 1
    tot[(kind, 'gain at round 1 for some choice and assignment (thread)')] += bool(mine_mixed)
    tot[(kind, 'gain at round 1 with every newborn not-all-equal (thread)')] += bool(mine_uniform)
    tot[(kind, 'uniform gains with siblings on the same distinction (thread)')] += sum(1 for x in mine_uniform if x[2])
    tot[(kind, 'same mixed-arm gains at round 1 as the study')] += mine_mixed == theirs_mixed
    tot[(kind, 'same uniform-arm gains at round 1 as the study')] += mine_uniform == theirs_uniform
    for x in mine_uniform: uni.setdefault(r['tid'], set()).add(x[1])
for k, n in sorted(tot.items(), key=str): print(k, n)
print('uniform-arm scores by target:', sorted((t, sorted(s)) for t, s in uni.items()))
