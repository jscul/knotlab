# EXPLORATORY, by the thread, outside any frozen design.  Supersedes one_parent_reread_exploratory.py, which took 's2' as the
# second shared distinction in all ten parts; in four of them (targets 138, 140, 142, 144) the live knot holds s1 and not s2,
# so that script re-read a distinction of another knot there.  This version takes the live knot's own shared distinctions.
#
# In each of the ten known two-holder parts (targets 135 to 144 less their knot nae(y3,Bh1,Bh2,Bh3)) the one live knot K
# holds the loose distinctions y2, y3 and two shared distinctions.  Ordinary growth gives K two one-parent births, each
# with two fresh distinctions.  Variant: each one-parent birth takes its loose distinction and one shared distinction of
# K, and gets one fresh distinction.
# Run from the repository root: .venv/bin/python -B research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001/thread_checks/one_parent_reread_exploratory_v2.py
import sys, os, collections, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reach_enumeration as v
out = collections.Counter()
for tid in range(135, 145):
    ks = [v.parse(k) for k in v.targets[tid]['knots']]
    st = [k for k in ks if not (k[0] == 'nae' and 'y3' in k[1] and len(k[1]) == 4)]
    hold = collections.Counter(m for _, mem in st for m in mem)
    K = [k for k in st if 'y2' in k[1]][0]
    shared = [m for m in K[1] if hold[m] >= 2]
    assert sorted(m for m in K[1] if hold[m] == 1) == ['y2', 'y3'] and len(shared) == 2
    both = []
    for a, b in itertools.product(shared, repeat=2):
        for la, lb in itertools.product(('nae', 'even'), repeat=2):
            s = v.score(st + [(la, ('y2', a, 'f1')), (lb, ('y3', b, 'f2'))])[:2]
            out[('laws of the two births', la, lb, str(s[0]) if s[1] else 'not hidden')] += 1
            if (la, lb) == ('nae', 'nae'): both.append(f'{a},{b}: {s[0]}')
    print(tid, f"{K[0]}({','.join(K[1])})", '| both not-all-equal:', ' ; '.join(both))
for k, n in sorted(out.items(), key=str): print(k, n)
