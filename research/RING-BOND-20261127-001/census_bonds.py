"""census_bonds.py LAW OUT.jsonl [--sample K --seed S] [--holders M] [--chunk I/N] [--exclude-seed S2 --exclude-count K2]:
bonds on census starts at rounds 0 and 1.
RING-BOND-20261127-001; README.md.

For each chosen census start under LAW ('nae' or 'parity'): the bonds held by a connected set of at most M knots
(ringbond.local_bonds) on the start (round 0) and on its stage after one ordinary round (when funded), with their holder
sizes, whether a birth is among the holders, their missing triples, and how many readings two or more bonds share.
Checks per bond: under not-all-equal, the count bound d(H) - merges <= |H| + (disagreeing triples) for each missing
triple (merges: |C| - 1 for each agreeing carrier, 1 for each disagreeing pair); under parity, whether some sum of the
holders' laws holds exactly two distinctions of each carrier and no other."""
import sys, json, random, collections, time, itertools
import ringbond as RB


def span_has(laws, mask):
    basis = []
    for v in laws:
        for b in basis: v = min(v, v ^ b)
        if v: basis.append(v)
    for b in basis: mask = min(mask, mask ^ b)
    return mask == 0


def checks(sup, law, b):
    H = b['holders']; dH = len({x for q in H for x in sup[q]}); shape = tuple(sorted(len(C) for C, lab in b['readings']))
    out = {'shape': shape}
    if law == 'nae':
        ok = True
        for w in b['missing']:
            merges = extra = 0
            for (C, lab), v in zip(b['readings'], w):
                if v == '1': merges += len(C) - 1
                elif len(C) == 2: merges += 1
                else: extra += 1
            ok &= dH - merges <= len(H) + extra
        out['bound'] = ok
    else:
        names = sorted({x for r in sup for x in r}); bit = {x: 1 << k for k, x in enumerate(names)}
        laws = [sum(bit[x] for x in sup[q]) for q in H]
        out['six-sum'] = any(span_has(laws, sum(bit[x] for p in pick for x in p))
                             for pick in itertools.product(*[list(itertools.combinations(C, 2)) for C, lab in b['readings']]))
    return out


def summary(sup, law, m, born):
    L = RB.local_bonds(sup, law, m)
    good = [b for b in L if b['same relation on the stage'] and not b['read at a knot of the stage']]
    share = collections.Counter((tuple(C), lab) for b in good for C, lab in b['readings'])
    ch = [checks(sup, law, b) for b in good]
    key = 'bound' if law == 'nae' else 'six-sum'
    return {'distinctions': len({x for r in sup for x in r}), 'knots': len(sup), 'bonds': len(good),
            'by shape and missing count': dict(collections.Counter('%s missing %d' % (''.join(map(str, c['shape'])), len(b['missing']))
                                                               for c, b in zip(ch, good))),
            'all agree missing': sum(1 for b in good if '111' in b['missing']),
            key + ' fails': sum(1 for c in ch if not c[key]),
            'with a birth among the holders': sum(1 for b in good if born and max(b['holders']) >= born),
            'missing counts': dict(collections.Counter(len(b['missing']) for b in good)),
            'holder sizes': dict(collections.Counter(len(b['holders']) for b in good)),
            'readings in two or more bonds': sum(1 for v in share.values() if v >= 2),
            'found on the holders but not a bond of the stage': len(L) - len(good),
            'examples': good[:3]}


if __name__ == '__main__':
    law, out = sys.argv[1], sys.argv[2]
    args = sys.argv[3:]
    get = lambda k, d: type(d)(args[args.index(k) + 1]) if k in args else d
    K, seed, m = get('--sample', 0), get('--seed', 20261127), get('--holders', 5)
    starts = RB.forbid.census(); order = list(range(len(starts)))
    if '--exclude-seed' in args:
        ex = set(random.Random(get('--exclude-seed', 1)).sample(order, get('--exclude-count', 10))); order = [i for i in order if i not in ex]
    if K: order = sorted(random.Random(seed).sample(order, K))
    if '--chunk' in args:
        ci, cn = map(int, args[args.index('--chunk') + 1].split('/')); order = order[ci::cn]
    with open(out, 'w') as f:
        for i in order:
            t0 = time.time(); S = RB.forbid.supports_of(starts[i])
            rec = {'start': 'census %d' % i, 'holders cap': m, 'round 0': summary(S, law, m, 0)}
            sts = RB.stages(S, law, 1)
            if len(sts) < 2: rec['round 1'] = 'not funded'
            else: rec['round 1'] = summary(sts[1][0], law, m, sts[1][1])
            rec['seconds'] = round(time.time() - t0, 2)
            f.write(json.dumps(rec) + '\n'); f.flush()
