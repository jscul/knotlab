"""From a run of form.py on the family of chains: for each law and first seed, how deep the first seed's making sees.
depth i : of the pairs of chains of one length that differ only in the loose count of the knot i steps from the link
          knot, how many are told apart (by what the first seed's descent makes, at the last round read by every form);
length  : of the pairs (a chain, the same chain with one more knot at its far end), how many are told apart, by the
          length of the shorter."""
import json, sys, collections, itertools
rows = [json.loads(l) for l in open(sys.argv[1])]
ok = [d for d in rows if 'error' not in d]
print('studies', len(rows), 'failed or over time', len(rows) - len(ok))
agg = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for d in ok:
    n = d['forms still read, by round']; full = max(i for i, x in enumerate(n) if x == n[0])
    C = d['classes by what it makes'][full]
    ch = {tuple(int(x) for x in f.split(':')[1].split(',')): c for f, c in C.items() if f.startswith('chain:')}
    sp = d['spec']; law = (str(sp['take']), sp['ration'], sp['treatment'])
    for a in ch:
        for i in range(len(a)):
            if a[i] == 2:
                b = a[:i] + (3,) + a[i + 1:]
                if b in ch:
                    cell = agg[law]['depth %d' % i]; cell[1] += 1; cell[0] += ch[a] != ch[b]
        for x in (2, 3):
            b = a + (x,)
            if b in ch:
                cell = agg[law]['length %d against %d' % (len(a), len(a) + 1)]; cell[1] += 1; cell[0] += ch[a] != ch[b]
keys = ['depth 0', 'depth 1', 'depth 2', 'depth 3', 'depth 4', 'length 1 against 2', 'length 2 against 3', 'length 3 against 4', 'length 4 against 5']
print('%-34s %s' % ('law (five first seeds together)', '  '.join('%-9s' % k.replace('length ', 'len ').replace(' against ', 'v') for k in keys)))
for law in agg:
    print('%-9s %-7s %-16s %s' % (law + ('  '.join('%-9s' % ('%d/%d' % tuple(agg[law][k])) for k in keys),)))
