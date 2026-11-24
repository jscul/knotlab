# Thread's reading of study B's records, made after its results were seen:
# holders in the starts that gain a hidden excess, the split of all starts by holders, and the ten two-holder starts
# that a single added knot with a fresh distinction lifts above 2.
# Run from the repository root: .venv/bin/python -B research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001/thread_checks/reach_holders.py
import gzip, json, glob, collections, itertools, os, sys
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reach_enumeration as v
A = v.A
starts = v.starts; targets = v.targets
for tag in ('c2', 'c3'):
    H = [json.loads(l) for f in sorted(glob.glob(A + f't1_{tag}_*.jsonl.gz')) for l in gzip.open(f, 'rt')]
    c = collections.Counter()
    for h in H:
        key = 'two-holder' if starts[h['si']]['max_holders'] <= 2 else 'three-holder'
        c[(key, 'starts')] += 1
        c[(key, 'grew')] += len(h['n_at']) > 1
        c[(key, 'stalled at round 1')] += h['outcome'] == 'stall' and len(h['n_at']) == 1
        c[(key, 'hidden excess at stage 0')] += bool(h['stage0_excess'])
        c[(key, 'gains a hidden excess')] += sum(s['new_excess'] for s in h['stages']) > 0
        if key == 'two-holder' and len(h['n_at']) > 1: c[('two-holder', 'grown tables')] += sum(s['tables'] for s in h['stages'][1:])
    print(tag, sorted(c.items()))
pairs = collections.Counter()
for T in targets:
    ks = [v.parse(k) for k in T['knots']]
    hold = collections.Counter(m for _, mem in ks for m in mem)
    pairs[(max(hold.values()) >= 3, any(len(set(a[1]) & set(b[1])) >= 2 and a[0] != 'nae' and b[0] != 'nae' for a, b in itertools.combinations(ks, 2)))] += 1
print('targets by (a distinction held three times, two parity knots sharing two distinctions):', sorted(pairs.items()))
for tid in range(135, 145):
    ks = [v.parse(k) for k in targets[tid]['knots']]
    left = [k for k in ks if k[0] == 'nae' and 'y3' in k[1] and len(k[1]) == 4]; assert len(left) == 1
    st = [k for k in ks if k != left[0]]
    soft = ('nae', left[0][1] + ('fz',))
    print(tid, 'whole', v.score(ks)[:2], '| start', v.score(st)[:2], '| start with the left-out knot given one fresh distinction', v.score(st + [soft])[:2])
