import json, sys, collections
rows = [json.loads(l) for l in open(sys.argv[1])]
print('studies', len(rows), 'failed or over time', [(d['spec']['take'], d['spec']['ration'], d['spec']['treatment'], d['spec']['first'], d['returncode']) for d in rows if 'error' in d])
for d in rows:
    if 'error' in d: continue
    sp = d['spec']
    cell = collections.defaultdict(list)
    for r in d['rows']:
        cell[r['depth']].append('%s:%s' % (r['loose'].replace(' -> ', '>'), r['course first differs'] if r['course first differs'] else '-'))
    agree = all(r['course first differs'] == r['crude first differs'] for r in d['rows'])
    print('%-9s %-7s %-16s %-22s read %-2s %-6s | %s%s' % (sp['take'], sp['ration'], sp['treatment'], sp['first'], d.get('rounds read (base)'), d.get('stop'),
          '  '.join('d%d[%s]' % (k, ' '.join(v)) for k, v in sorted(cell.items())), '' if agree else '   (crude signature differs from course)'))
