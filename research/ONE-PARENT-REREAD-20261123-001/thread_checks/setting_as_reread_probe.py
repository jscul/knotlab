# EXPLORATORY probe by the thread, outside any frozen design (sub-goal B321): can BOTH observers' setting births be births
# rule Q makes?  For a structure, an observer is a live knot K with a loose distinction l and two shared distinctions
# c0, c1 of K; setting a adds the knot nae(l, c_a, fresh).  Every pair of such observers on different knots with six
# different distinctions is scored with the recorded scorer; hidden excess = score above 2 with both records hidden.
# Run from the repository root:
#   .venv/bin/python -B research/ONE-PARENT-REREAD-20261123-001/thread_checks/setting_as_reread_probe.py MAXD
import sys, os, json, glob, gzip, collections, itertools
import numpy as np
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '../../REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001/thread_checks'))
import reach_enumeration as v
import added_knot_sample as aks
MAXD = int(sys.argv[1])
def probe(knots):
    names = sorted({m for _, mem in knots for m in mem}); n = len(names); idx = {x: i for i, x in enumerate(names)}
    if n > MAXD: return None
    W = np.arange(1 << n, dtype=np.int64); ok = np.ones(1 << n, dtype=bool)
    for law, mem in knots:
        s = sum((W >> idx[m]) & 1 for m in mem)
        ok &= ((s > 0) & (s < len(mem))) if law == 'nae' else ((s & 1) == (0 if law == 'even' else 1))
    words = W[ok]
    if len(words) == 0: return None
    bit = {x: (words >> idx[x]) & 1 for x in names}
    hold = collections.defaultdict(list)
    for i, (_, mem) in enumerate(knots):
        for m in mem: hold[m].append(i)
    obs = []
    for i, (_, mem) in enumerate(knots):
        lo = [m for m in mem if len(hold[m]) == 1]; sh = [m for m in mem if len(hold[m]) >= 2]
        for l in lo:
            for c0, c1 in itertools.combinations(sh, 2): obs.append((i, l, c0, c1))
    out = dict(observers=len(obs), pairs=0, hidden=0, best=None, gains=[])
    for (i, l, c0, c1), (j, m, d0, d1) in itertools.combinations(obs, 2):
        if i == j or len({l, c0, c1, m, d0, d1}) < 6: continue
        cell = (bit[l] * 4 + bit[c0] * 2 + bit[c1]) * 8 + bit[m] * 4 + bit[d0] * 2 + bit[d1]
        M = np.bincount(cell, minlength=64).reshape(8, 8).astype(np.int64)
        out['pairs'] += 1
        if not aks.hidden(M): continue
        out['hidden'] += 1
        sc = v.evaluate(M)
        fr = Fraction(sc[0]).limit_denominator(100000)
        if out['best'] is None or fr > Fraction(out['best']): out['best'] = str(fr)
        if sc[0] > 2 + 1e-9: out['gains'].append(((i, l, c0, c1), (j, m, d0, d1), str(fr)))
    return out
if __name__ == '__main__':
    tot = collections.Counter(); best = Fraction(0); found = []
    pops = [('target', [v.parse(k) for k in T['knots']], T['tid']) for T in v.targets]
    H = [json.loads(l) for f in sorted(glob.glob(v.A + 't1_c3_*.jsonl.gz')) for l in gzip.open(f, 'rt')]
    for h in H:
        tk = [v.parse(k) for k in v.targets[h['tid']]['knots']]
        pops.append(('part', [tk[i] for i in range(len(tk)) if h['mask'] >> i & 1], h['si']))
    for kind, ks, ident in pops:
        r = probe(ks)
        if r is None: tot[(kind, 'skipped (too many distinctions)')] += 1; continue
        tot[(kind, 'structures')] += 1; tot[(kind, 'observer pairs')] += r['pairs']; tot[(kind, 'hidden pairs')] += r['hidden']
        tot[(kind, 'structures with a pair of observers')] += r['pairs'] > 0
        if r['best'] is not None: best = max(best, Fraction(r['best']))
        if r['gains']:
            tot[(kind, 'structures with a hidden excess')] += 1; found.append((kind, ident, len(ks), r['gains'][:2]))
    for k, n in sorted(tot.items(), key=str): print(k, n)
    print('largest hidden score:', best)
    for f in found[:10]: print(f)
