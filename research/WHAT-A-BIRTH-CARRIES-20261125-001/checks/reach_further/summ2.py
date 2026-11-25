import json, sys, collections
rows = [json.loads(l) for l in open(sys.argv[1])]
err = [d for d in rows if 'error' in d]; ok = [d for d in rows if 'error' not in d]
print('runs', len(rows), 'failed or over time', len(err), dict(collections.Counter((d['spec']['take'], d['returncode']) for d in err)))
tab = collections.defaultdict(collections.Counter); tests = collections.Counter()
for d in ok:
    sp = d['spec']; key = (sp['take'], sp['ration'], sp['treatment'])
    T = tab[key]; T['runs'] += 1; T['takes'] += d['takes made']; T['stop:%s' % d['stop']] += 1
    hx = False
    for r in d['by_s']:
        T['X'] += r['X with two or more']; T['X diff rounds'] += r['X met in different rounds']; hx = hx or r['X with two or more'] > 0
        for k, v in r['pairs']: T['pairs ' + k] += v
        for k, v in r['first meetings (round, made only)']:
            t, st = eval(k); T['meet later' if t > r['s'] + 1 else 'meet next'] += v; T['meet made-only' if st else 'meet via start'] += v
    T['runs with X'] += hx
    for t in d['tests']:
        cls = tuple(t['classes']); kind = 'no difference' if len(set(cls)) == 1 else ('differs with which' if cls[1] != cls[2] else 'how many')
        tests[(key, t['why'], kind, cls, tuple(t['meets']), str((t.get('m') or {}).get('m')))] += 1
show = [k for k in sorted(tab) if tab[k]['X'] or tab[k]['meet later'] or tab[k]['meet next']]
print('laws with any meeting of parts wholly apart:', len(show), 'of', len(tab))
for k in show: print(' ', k, {a: b for a, b in tab[k].items() if b})
print('quiet laws (no such meeting):', collections.Counter(k[0] for k in tab if k not in show))
print('TESTS')
for k, v in sorted(tests.items(), key=str): print(' ', v, k)
