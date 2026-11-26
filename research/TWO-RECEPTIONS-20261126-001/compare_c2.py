"""compare_c2.py: the parity census again with the mark that renews the parity equations (parity2.py; R2's second
Block), against the first parity census (parity_runs.jsonl.gz): for each pair and law read in both, does any far
change's first hearing differ, and is any change made after round 3 now heard after round 6?"""
import sys, json, gzip, collections
def load(paths):
    out, lost = {}, []
    for p in paths:
        for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p)):
            if not l.strip(): continue
            r = json.loads(l)
            if 'not run' in r: lost.append(r); continue
            out[(r['A'], r['B'], json.dumps(r['law']))] = r
    return out, lost
old, lost_old = load(['parity_runs.jsonl.gz'])
new, lost_new = load(sys.argv[1:])
both = sorted(set(old) & set(new))
c = collections.Counter(); diffs = []
for k in both:
    a, b = old[k]['changes'], new[k]['changes']
    if len(a) != len(b) or old[k]['rounds'] != new[k]['rounds']: c['growth or placements differ'] += 1
    for x, y in zip(a, b):
        c['changes compared'] += 1
        c['heard before'] += bool(x['heard']); c['heard now'] += bool(y['heard'])
        if x['heard'] != y['heard']:
            c['first hearing differs'] += 1; diffs.append((k, x, y))
        if y['heard'] and y['heard'] > 6: c['heard after round 6 now'] += 1
print('pairs and laws read in both:', len(both), '; only in the first:', len(set(old) - set(new)), '; only now:', len(set(new) - set(old)))
print('not run: first', len(lost_old), 'now', len(lost_new))
for k, v in c.items(): print(' ', k, v)
for d in diffs[:10]: print('  ', d)
