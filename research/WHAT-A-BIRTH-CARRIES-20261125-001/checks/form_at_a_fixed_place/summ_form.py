import json, sys, collections, itertools
rows = [json.loads(l) for l in open(sys.argv[1])]
bad = [d for d in rows if 'error' in d]
print('studies', len(rows), 'failed or over time', [(d['spec']['take'], d['spec']['ration'], d['spec']['treatment'], d['spec']['first'], d['returncode']) for d in bad])
ok = [d for d in rows if 'error' not in d]
bylaw = collections.defaultdict(dict)
for d in ok:
    sp = d['spec']; bylaw[(str(sp['take']), sp['ration'], sp['treatment'])][sp['first']] = d
def part_at(d, key, R):
    C = d[key]; return C[min(R, len(C)) - 1] if C else {}
for law, D in bylaw.items():
    print('==', *law)
    for f, d in D.items():
        fates = collections.Counter(d['fate'].values())
        print('   %-24s forms %d read %s' % (f, d['forms'], d['forms still read, by round']))
        print('   %-24s   classes by course        %s' % ('', d['classes by round']))
        print('   %-24s   classes by what it makes %s   fates %s' % ('', d['classes by round, by what it makes'], dict(fates)))
    # do two first seeds draw the same lines among the forms?  pairs of forms told apart by both, by one only, by neither
    fs = list(D)
    for a, b in itertools.combinations(fs, 2):
        Pa, Pb = part_at(D[a], 'classes by what it makes', 99), part_at(D[b], 'classes by what it makes', 99)
        common = [n for n in Pa if n in Pb and n != '(none)']
        both = one = neither = 0
        for x, y in itertools.combinations(common, 2):
            sa, sb = Pa[x] != Pa[y], Pb[x] != Pb[y]
            both += sa and sb; one += sa != sb; neither += (not sa) and (not sb)
        print('      %-22s vs %-22s pairs told apart by both %4d, by one only %4d, by neither %4d' % (a, b, both, one, neither))
