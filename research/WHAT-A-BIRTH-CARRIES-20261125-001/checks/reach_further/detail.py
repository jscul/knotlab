"""For one test of scan2.py: the four runs again, with a signature of the course from X only that uses none of ticket
B's course reading (knots descended from X only, by round made, with their numbers of places and of fresh distinctions),
ticket B's attribution of the first differing value, and the knot test of every run."""
import sys, os, json, collections
from collections import Counter
import scan2
from scan2 import eng, read, View, classes_by_course, stars_of
spec = json.loads(sys.argv[1]); which = int(sys.argv[2]) if len(sys.argv) > 2 else 0
law = eng.Law(spec['ration'], spec['treatment'], spec['take'], spec['knot_law'])
o = scan2.scan(law, spec['start'], stars_of(spec['start']), max_tests=which + 1)
t = [x for x in o['tests']][which]
s = t['s']
runA = eng.Run(law, stars=stars_of(spec['start']), rounds=7); keysA = read.Keys(runA)
R_s = runA.recs[s]['roster']
parts = eng.roster_parts(R_s) if R_s.parts is None else R_s.parts
member_part = {u: i for i, P in enumerate(parts) for u in P}
pi = {tuple(P): i for i, P in enumerate(parts)}
i, j, k = pi[tuple(t['X'])], pi[tuple(t['Y1'])], pi[tuple(t['Y2'])]
print('test:', {a: t[a] for a in ('why', 's', 'X', 'Y1', 'Y2', 'meets', 'classes', 'first differs')}, 'm', (t.get('m') or {}).get('m'))
S0 = runA.snaps[s]
for nm, P in (('X', parts[i]), ('Y1', parts[j]), ('Y2', parts[k])):
    print(' ', nm, [(u, 'made %d' % S0.made[u], S0.kind[u], 'parents', S0.parents[u], 'places', len(S0.places[u])) for u in P])
runs = {}
for nm, bar in (('neither', ()), ('Y1 barred', (j,)), ('Y2 barred', (k,)), ('both barred', (j, k))):
    if not bar: r, bits = runA, read.desc_bits(runA, s, member_part)
    else:
        r = eng.Run(law, base=runA, base_round=s, bar=[u for p in bar for u in parts[p]], rounds=7)
        bits = read.desc_bits(r, s, member_part)
    runs[nm] = (r, bits)
    S = r.S; sig = []
    for rd in range(s + 1, r.rounds_read + 1):
        ks = [u for u in range(S.n_knots) if S.made[u] == rd and bits[u] == (1 << i)]
        takes = sum(len(b['takes']) for b in r.recs[rd - 1]['births'] if bits[b['id']] == (1 << i))
        fresh = sorted(Counter(b['f'] for b in r.recs[rd - 1]['births'] if bits[b['id']] == (1 << i)).items())
        sig.append((rd, len(ks), sorted(Counter(len(S.places[u]) for u in ks).items()), 'takes %d' % takes, 'fresh', fresh))
    kt = read.knot_test_full(r) if not bar else read.knot_test_barred(r, s, full=True)
    print(nm, '| rounds', r.rounds_read, 'knots', S.n_knots, '| knot test', {a: kt[a] for a in ('verdicts', 'n_fail', 'n_disagree', 'n_untested')})
    for x in sig: print('    ', x)
# attribution: the first value at one of X's births that differs, each barred run against the run with neither barred
vA = View(runA, keysA, runs['neither'][1], i, j, s, parts[i], parts[j]); vA.mj = (1 << j) | (1 << k)
for nm in ('Y1 barred', 'Y2 barred', 'both barred'):
    r, bits = runs[nm]
    v = View(r, read.Keys(r, base=keysA), bits, i, j, s, parts[i], parts[j]); v.mj = (1 << j) | (1 << k)
    last = min(r.rounds_read, runA.rounds_read)
    fd = read.attribution(v, vA, s, last)
    print('attribution,', nm, ':', json.dumps(fd, default=str)[:600] if fd else None)
    if fd: print('   ', {a: fd[a] for a in fd if a not in ('value_A', 'value_O', 'pos')}, '| keys', sorted(fd))
def lab(bits, u):
    b = bits[u]; out = ''
    if b & (1 << i): out += 'X'
    if b & (1 << j): out += 'Y1'
    if b & (1 << k): out += 'Y2'
    if b & ~((1 << i) | (1 << j) | (1 << k)): out += '+'
    return out or 'old'
if os.environ.get('BIRTHS'):
    for nm in ('neither', 'Y1 barred', 'Y2 barred', 'both barred'):
        r, bits = runs[nm]; S = r.S
        print('==', nm)
        for rd in range(s + 1, min(r.rounds_read, 6) + 1):
            for b in r.recs[rd - 1]['births']:
                if not any(bits[p] & (1 << i) for p in b['parents']): continue
                print('   round', rd, b['kind'], 'parents', [(p, lab(bits, p)) for p in b['parents']], 'loose', len(b['loose']),
                      'cands', [(d, len(b_h), [lab(bits, w) for w in sup]) for (d, sup), b_h in zip(b['cands'], [r.snaps[rd - 1].holders[d] for d, _ in b['cands']])][:8],
                      'takes', [(d, [(w, lab(bits, w)) for w in b['take_holders'][d]]) for d in b['takes']], 'D', b['D'], 'f', b['f'], '-> knot', b['id'], lab(bits, b['id']))
