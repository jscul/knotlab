import sys, json, itertools, collections, time
sys.path.insert(0, '.')
import layers as LY
out = collections.Counter(); rows = []
specs = []
for a, b in [(3, 5), (5, 7), (7, 7), (3, 3), (4, 6), (5, 6)]:
    for j in ('share', 'touch', 'chain1'):
        jo = [('share', (0, 0), (1, 0))] if j == 'share' else ([('touch', (0, 0), (1, 0))] if j == 'touch' else [('chain', (0, 0), (1, 0), 1)])
        specs.append(('%s %d+%d' % (j, a, b), [a, b], jo))
    specs.append(('apart %d+%d' % (a, b), [a, b], []))
for t3 in [(5, 5, 5), (3, 5, 7)]:
    specs.append(('three share %s' % (t3,), list(t3), [('share', (0, 0), (1, 0)), ('share', (0, 0), (2, 0))]))
    specs.append(('three in a path of touches %s' % (t3,), list(t3), [('touch', (0, 0), (1, 0)), ('touch', (1, 2), (2, 0))]))
    specs.append(('three apart %s' % (t3,), list(t3), []))
for name, rings, joins in specs:
    t0 = time.time()
    start, rd = LY.build(rings, joins)
    st = start; got = []
    for t in (1, 2):
        nxt, status, births = LY.forbid.grown(st, 'parity', 'ordinary')
        if status != 'funded': got.append(status); break
        a = LY.analyse(nxt, rd)[0]; got.append((a['classes'], a['sums of ring parities that are labels'], LY.projection_kept(start, nxt)['same'])); st = nxt
    print(name, got, round(time.time() - t0, 1), flush=True)
