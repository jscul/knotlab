# EXPLORATORY, by the thread, after the results of studies A and B and outside any frozen design.
# In each of the ten known two-holder starts (targets 135 to 144 less their knot nae(y3,Bh1,Bh2,Bh3)) the one live knot K
# holds the loose distinctions y2, y3 and the shared distinctions y1, s2.  Ordinary growth gives K two one-parent births,
# each with two fresh distinctions.  Variant tried here: each one-parent birth takes its loose distinction, takes one
# shared distinction of K as well, and gets one fresh distinction.
# Run from the repository root: .venv/bin/python -B research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001/thread_checks/one_parent_reread_exploratory.py
import sys, os, collections, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reach_enumeration as v
out = collections.Counter()
for tid in range(135, 145):
    ks = [v.parse(k) for k in v.targets[tid]['knots']]
    st = [k for k in ks if not (k[0] == 'nae' and 'y3' in k[1] and len(k[1]) == 4)]
    base = v.score(st)[:2]
    ordinary = v.score(st + [('nae', ('y2', 'f1', 'f2')), ('nae', ('y3', 'f3', 'f4'))])[:2]
    out[('start', str(base[0]), base[1])] += 1; out[('ordinary round 1, both births not-all-equal', str(ordinary[0]), ordinary[1])] += 1
    for a, b in itertools.product(('y1', 's2'), repeat=2):
        for la, lb in itertools.product(('nae', 'even'), repeat=2):
            s = v.score(st + [(la, ('y2', a, 'f1')), (lb, ('y3', b, 'f2'))])[:2]
            out[('re-read births with laws', la, lb, str(s[0]) if s[1] else 'not hidden')] += 1
for k, n in sorted(out.items(), key=str): print(k, n)
