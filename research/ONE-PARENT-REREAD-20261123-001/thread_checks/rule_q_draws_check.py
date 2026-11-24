# Thread's separate check of test (b) under not-all-equal: the 280 funded sparse draws under rule Q, both conventions,
# with the thread's own engine; compared with the study's records round by round while rounds stay small.
# Run from the repository root: .venv/bin/python -B research/ONE-PARENT-REREAD-20261123-001/thread_checks/rule_q_draws_check.py
import sys, os, json, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rule_q_engine as qe
A = 'artifacts/ONE-PARENT-REREAD-20261123-001A/ONE-PARENT-REREAD-20261123-001A-E001_one_parent_reread/'
rec = {}
for f in sorted(glob.glob(A + 'draws_nae_arm*.jsonl')):
    for l in open(f):
        r = json.loads(l); rec[(r['arm'], r['draw'])] = r
tot = collections.Counter()
for dr in qe.lib.p3_draws():
    r = rec.get((dr['arm'], dr['draw']))
    if r is None: continue
    for conv, key in (('O', 'QO'), ('N', 'QN'), ('off', 'ordinary')):
        g = qe.Q(dr['stars'], conv if conv != 'off' else 'O', reread=(conv != 'off'))
        hold = [g.max_holders()]
        while len(g.births) < 12 and g.round(max_live=60) and len(g.stars) <= 400: hold.append(g.max_holders())
        t = len(g.births); s = r[key]
        ok = (g.n_at[:t + 1] == s['n_at'][:t + 1] and hold[:t + 1] == s['holders_at'][:t + 1]
              and (conv == 'off' or [sum(b['reread'] for b in row) for row in g.births] == s['reread_births'][:t]))
        tot[(key, 'histories compared')] += 1; tot[(key, 'rounds compared')] += t; tot[(key, 'agree')] += bool(ok)
        tot[(key, 'compared through round 12')] += t == 12
        if not ok and tot[(key, 'shown')] < 2:
            tot[(key, 'shown')] += 1; print('DIFFERS', key, dr['arm'], dr['draw'], g.n_at, s['n_at'][:t + 1], hold, s['holders_at'][:t + 1])
for k, n in sorted(tot.items(), key=str): print(k, n)
