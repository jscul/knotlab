"""The README's tables from a sweep of profile.py."""
import sys, json, gzip, collections
rows = [json.loads(l) for l in (gzip.open(sys.argv[1], 'rt') if sys.argv[1].endswith('.gz') else open(sys.argv[1])) if l.strip()]
bad = [r for r in rows if 'error' in r]; rows = [r for r in rows if 'error' not in r]
print(len(rows), 'finished;', len(bad), 'stopped at the time limit:', sorted((b['spec']['ration'], b['spec']['treatment'], b['spec']['take'], b['spec']['first']) for b in bad))
print('pairs a study', {r['pairs'] for r in rows}, '| R*', sorted(collections.Counter(r['R*'] for r in rows).items()), '| classes', min(r['classes'] for r in rows), 'to', max(r['classes'] for r in rows))
profs = list(rows[0]['profiles'])
def line(rs, p):
    d = [r['profiles'][p] for r in rs]
    return '%3d of %3d | %9s sharing | %7s apart | %5.1f%%' % (sum(1 for x in d if x['of those told apart'] == 0), len(d),
            format(sum(x['pairs sharing it'] for x in d), ','), format(sum(x['of those told apart'] for x in d), ','),
            100 * sum(x['of those told apart'] for x in d) / max(1, sum(x['pairs sharing it'] for x in d)))
G = collections.OrderedDict([
    ('all', rows),
    ('no taking rule', [r for r in rows if not r['spec']['take']]),
    ('no taking rule; retire or offshoot', [r for r in rows if not r['spec']['take'] and r['spec']['treatment'] != 'CANCEL-WAIT']),
    ('no taking rule; wait', [r for r in rows if not r['spec']['take'] and r['spec']['treatment'] == 'CANCEL-WAIT']),
    ('take of a sole candidate', [r for r in rows if r['spec']['take']]),
    ('held-out first seeds K-O', [r for r in rows if r['first'] in 'KLMNO']),
    ('first seeds A-J', [r for r in rows if r['first'] in 'ABCDEFGHIJ']),
])
for g, rs in G.items():
    print('\n==', g, '|', len(rs), 'studies | pairs', format(sum(r['pairs'] for r in rs), ','), '| told apart', format(sum(r['pairs told apart'] for r in rs), ','))
    for p in profs: print('  %-58s %s' % (p[:58], line(rs, p)))
p = [q for q in profs if q.startswith('reach 3')][0]
print('\nthree steps do not decide:', sorted(collections.Counter((r['spec']['ration'], r['spec']['treatment'], r['spec']['take']) for r in rows if r['profiles'][p]['of those told apart']).items(), key=str))
p = [q for q in profs if q.startswith('reach 2')][0]
print('two steps do not decide, no take:', [(r['spec']['ration'], r['spec']['treatment'], r['first'], r['profiles'][p]['of those told apart']) for r in rows if r['profiles'][p]['of those told apart'] and not r['spec']['take']])
p = [q for q in profs if q.startswith('knots')][0]
print('same knots: studies with at least one such pair told apart', sum(1 for r in rows if r['profiles'][p]['of those told apart']), 'of', len(rows))
p = [q for q in profs if q.startswith('counts 1')][0]
print('registered profile decides in:', [(r['spec']['ration'], r['spec']['treatment'], r['spec']['take'], r['first'], r['classes'], r['profiles'][p]['pairs sharing it']) for r in rows if r['profiles'][p]['of those told apart'] == 0])
