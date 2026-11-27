"""ring.py OUT.json: the grown ring's bonds round by round.  RING-BOND-20261127-001; README.md, "Frozen".

Full search (ringbond.bonds, agreement readings, essential laws counted on the whole stage) at rounds 0-4: counts, bonds
with every law essential and their carrier shapes and missing triples, bonds with a newest birth essential, persistence
of every bond of the round before (same readings, same missing triples), readings shared by two or more bonds, and
whether the birth is essential in every round-1 bond.  Local search (holders <= 4) at rounds 4 and 5.  The swaps of the
reading class (all readings unchanged by a global flip) at rounds 1-2 and of the carrier cap (four) at round 2.  The
knot checker on the clause of each round-1 bond with every law essential, each reading in turn as the contact."""
import sys, json, collections, subprocess, time
from pathlib import Path
import ringbond as RB
ROOT = Path(__file__).resolve().parents[2]


def key(b): return RB.bond_key(b)


if __name__ == '__main__':
    S = ((0, 1, 3), (1, 2, 4), (2, 0, 5)); out = {'full': [], 'local': [], 'swaps': {}, 'checker': []}
    sts = RB.stages(S, 'nae', 5); prev = None
    for t, (sup, born) in enumerate(sts[:5]):
        t0 = time.time(); b = RB.bonds(RB.Stage(sup, 'nae'), 'agree', born=born)['bonds']
        every = [x for x in b if len(x['essential']) == len(sup)]
        cur = {key(x): x for x in b}
        rec = {'round': t, 'knots': len(sup), 'distinctions': len({x for r in sup for x in r}), 'bonds': len(b),
               'newest birth essential': sum(1 for x in b if x['new']) if born else None,
               'every law essential': len(every),
               'every-law shapes and missing': dict(collections.Counter(
                   '%s missing %s' % (''.join(str(len(C)) for C, l in sorted(x['readings'], key=lambda r: len(r[0]))), ','.join(x['missing'])) for x in every)),
               'missing counts': dict(collections.Counter(len(x['missing']) for x in b)),
               'readings in two or more bonds': sum(1 for v in collections.Counter(r for x in b for r in key(x)).values() if v >= 2)}
        if prev is not None:
            rec['bonds of the round before kept'] = sum(1 for k, x in prev.items() if k in cur and cur[k]['missing'] == x['missing'])
            rec['bonds of the round before'] = len(prev)
        if t == 1: rec['birth essential in every bond'] = all(3 in x['essential'] for x in b)
        rec['seconds'] = round(time.time() - t0, 1); out['full'].append(rec); prev = cur
        print(json.dumps(rec), flush=True)
    for t in (4, 5):
        if t >= len(sts): out['local'].append({'round': t, 'not funded': True}); continue
        sup, born = sts[t]; t0 = time.time(); L = RB.local_bonds(sup, 'nae', 4)
        good = [x for x in L if x['same relation on the stage'] and not x['read at a knot of the stage']]
        rec = {'round': t, 'holders cap': 4, 'bonds': len(good), 'with a newest birth among the holders': sum(1 for x in good if max(x['holders']) >= born),
               'holder sizes': dict(collections.Counter(len(x['holders']) for x in good)), 'missing counts': dict(collections.Counter(len(x['missing']) for x in good)),
               'seconds': round(time.time() - t0, 1)}
        out['local'].append(rec); print(json.dumps(rec), flush=True)
    for t in (1, 2):
        sup, born = sts[t]; b = RB.bonds(RB.Stage(sup, 'nae'), 'sym', born=born)['bonds']
        out['swaps']['all flip-unchanged readings, round %d' % t] = {
            'bonds': len(b), 'every law essential': sum(1 for x in b if len(x['essential']) == len(sup)),
            'missing counts': dict(collections.Counter(len(x['missing']) for x in b))}
    sup, born = sts[2]; b = RB.bonds(RB.Stage(sup, 'nae'), 'agree', sizes=(2, 3, 4), born=born)['bonds']
    out['swaps']['carriers up to four, round 2'] = {'bonds': len(b), 'with a carrier of four': sum(1 for x in b if any(len(C) == 4 for C, l in x['readings'])),
                                                   'missing counts': dict(collections.Counter(len(x['missing']) for x in b))}
    print(json.dumps(out['swaps']), flush=True)
    sup, born = sts[1]
    for x in RB.bonds(RB.Stage(sup, 'nae'), 'agree', born=born)['bonds']:
        if len(x['essential']) != len(sup): continue
        names = ['r' + '_'.join(map(str, C)) for C, l in x['readings']]
        lits = [n if m == '0' else '~' + n for n, m in zip(names, x['missing'][0])]   # the clause forbidding the missing triple
        for c in range(3):
            loops = [names[i] for i in range(3) if i != c]
            r = subprocess.run([sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', ' '.join(lits), '--loops', *loops,
                                '--contact', names[c], '--json'], capture_output=True, text=True, env={'PYTHONPATH': str(ROOT / 'tools')})
            d = json.loads(r.stdout); out['checker'].append({'readings': x['readings'], 'clause': ' '.join(lits), 'contact': names[c], 'is_knot': d['is_knot']})
    print(json.dumps(out['checker']), flush=True)
    json.dump(out, open(sys.argv[1], 'w'), indent=1)
