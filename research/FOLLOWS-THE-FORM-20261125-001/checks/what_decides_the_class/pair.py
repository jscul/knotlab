"""Two second seeds side by side under one law and first seed: the members and the births of each round by descent.
Usage: pair.py '{"ration":"FLOOR1","treatment":"CANCEL-WAIT","take":null,"first":"M","show":4}' NAME NAME"""
import sys, json
import profile
from profile import eng, read, start, every_seed, swap_seeds
spec = json.loads(sys.argv[1]); a, b = sys.argv[2], sys.argv[3]
law = eng.Law(spec['ration'], spec['treatment'], spec.get('take'), 'nae')
seeds = {s['name']: s for s in every_seed() + swap_seeds()}
for n in (a, b):
    stars, nf = start(spec['first'], seeds[n])
    run = eng.Run(law, stars=stars, rounds=spec.get('rounds', 9), knot_bound=3000)
    bits = read.desc_bits(run, 0, {u: (0 if u < nf else 1) for u in range(len(stars))})
    S = run.S
    print('==', n, 'start', stars, '| first seed knots', nf)
    for t in range(1, min(run.rounds_read, int(spec.get('show', 4))) + 1):
        rec = run.recs[t - 1]
        short = [u for u in rec['members'] if rec['owe'].get(u, 0) > rec['h'].get(u, 0)]
        print('  round', t, 'members', [(u, {1: 'first', 2: 'second', 3: 'both'}.get(bits[u], '?'), 'h%d' % rec['h'][u], 'owes%d' % rec['owe'].get(u, 0)) for u in rec['members']][:14], 'short', short[:8])
        for bth in rec['births']:
            print('     ', {1: 'first ', 2: 'second', 3: 'both  '}[bits[bth['id']]], bth['kind'], 'parents', list(bth['parents']), 'places', len(S.places[bth['id']]), 'D', bth['D'], 'f', bth['f'], '-> knot', bth['id'])
