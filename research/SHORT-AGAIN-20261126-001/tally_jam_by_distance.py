"""tally_jam_by_distance.py RUNS...: far hearings and the two rules' exceptions, by law and distance (2, 3, 4, 5 or more), and
which receivers hear from three steps or more."""
import sys, json, gzip, collections
def load(p): return [json.loads(l) for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p))]
for path in sys.argv[1:]:
    rows = [r for r in load(path) if 'changes' in r]
    far = collections.Counter(); tot = collections.Counter(); wex = collections.Counter(); sex = collections.Counter(); who = collections.defaultdict(set)
    for r in rows:
        law = r['law'][0] + (' (retires)' if r['law'][1] == 'CANCEL-RETIRE' else '')
        for c in r['changes']:
            k = (law, min(c['distance'], 5))
            if c['distance'] >= 2: tot[k] += 1
            if c['heard'] is None or c['distance'] < 2: continue
            far[k] += 1
            if not (c['waiting own without'] or c['waiting own with']): wex[k] += 1
            if not (c['jammed without'] or c['jammed with']): sex[k] += 1
            if c['distance'] >= 3: who[law].add(r['A'])
    print('##', path, '(%s)' % ', '.join(sorted({'d = %d, %s' % (r['d'], r.get('join', 'meeting')) for r in rows})))
    print('| law | distance | heard (of) | exceptions to the rule | to the weaker rule |'); print('|---|---|---|---|---|')
    for k in sorted(tot):
        if far[k]: print('| %s | %s | %d of %d | %d | %d |' % (k[0], '5 or more' if k[1] == 5 else k[1], far[k], tot[k], sex[k], wex[k]))
    for law, s in sorted(who.items()): print('receivers hearing from 3 or more under %s: %d %s' % (law, len(s), sorted(s)))
    print()
