"""tally_switch.py RUNS: the switch table (JAM.md, "The one receiver that hears under the cap")."""
import sys, json, gzip, collections
def load(p): return [json.loads(l) for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p))]
rows = load(sys.argv[1]); runs = [r for r in rows if 'changes' in r]; lost = [r for r in rows if 'not run' in r]
TN = {'CANCEL-WAIT': 'waits', 'CANCEL-RETIRE': 'retires', 'CANCEL-OFFSHOOT': 'offshoots'}
print('| cap | short knot | join | site | d | senders: leave the first way at round (count), or never | changes from 3 steps or more heard (of) | latest first hearing |')
print('|---|---|---|---|---|---|---|---|')
groups = collections.defaultdict(list)
for r in runs: groups[(r['law'][0], r['law'][1], r['join'], r['A'], r['d'])].append(r)
for k in sorted(groups, key=lambda k: (k[0], ['CANCEL-WAIT', 'CANCEL-RETIRE', 'CANCEL-OFFSHOOT'].index(k[1]), k[2], k[3], k[4])):
    rs = groups[k]
    lv = collections.Counter(r['leaves first way'] for r in rs)
    far = [c for r in rs for c in r['changes'] if c['distance'] >= 3]
    heard = [c for c in far if c['heard'] is not None]
    print('| %s | %s | %s | %s | %d | %s | %d of %d | %s |' % (k[0], TN[k[1]], k[2], k[3].split('@')[1], k[4],
          ', '.join('%s: %d' % ('never' if x is None else x, n) for x, n in sorted(lv.items(), key=lambda kv: (kv[0] is None, kv[0] or 0))),
          len(heard), len(far), max((c['heard'] for c in heard), default='-')))
print('\nruns read', len(runs), 'senders not run', sum(r['not run'] for r in lost), lost[:3])
