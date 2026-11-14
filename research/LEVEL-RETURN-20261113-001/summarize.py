"""Frozen-rule summary of LEVEL-RETURN-20261113-001A (run3 and run_rigid3): R1-R5, periods, certificates. Writes summary.json."""
import sys, json, collections
sys.path.insert(0, 'scripts')
from longrun import load_results
E = 'experiments/LEVEL-RETURN-20261113-001A/LEVEL-RETURN-20261113-001A-E001_certified_levels/'
R = load_results(E + 'run3'); RR = load_results(E + 'run_rigid3')
out = {}
res = [v['result'] for v in R.values() if v.get('status') == 'ok']
out['cases'] = dict(collections.Counter(v.get('status') for v in R.values()))
out['verdicts'] = dict(collections.Counter(r['verdict'] for r in res))
out['second_generator_disagreements'] = sum(1 for r in res if not r['second_generator_agrees'])
out['census_knot_mismatches'] = sum(1 for r in res if r.get('census_knots') is not None and r['census_knots'] != r['knots'])
prof = collections.defaultdict(dict); cp = {}
for r in res:
    if r['kind'] == 'level':
        prof[r['key_id']][r['n']] = {'alive': '1', 'dead': '0'}.get(r['verdict'], '?'); cp[r['key_id']] = r['census_profile']
P = {k: ''.join(v.get(n, '-') for n in range(1, 17)) for k, v in prof.items()}
out['census_disagreements'] = sum(1 for k in P for n in range(12) if cp[k][n] in '01' and P[k][n] in '01' and cp[k][n] != P[k][n])
alt = sorted(k for k in P if cp[k][4:] in ('10101010', '01010101'))
r1 = []
for k in alt:
    live = 0 if cp[k][9] == '1' else 1
    bad = [n for n in range(13, 17) if P[k][n - 1] in '01' and P[k][n - 1] != ('1' if n % 2 == live else '0')]
    und = [n for n in range(13, 17) if P[k][n - 1] == '?']
    r1.append(dict(key=k[:16], census=cp[k], certified=P[k], against=bad, undecided=und))
out['R1'] = dict(rows=r1, holds=all(not x['against'] for x in r1))
r2 = [dict(case=r['case'], n=r['n'], parity_viol=r.get('parity_violation_count'), first_last_viol=r.get('first_last_violation_count'))
      for r in res if r['kind'] == 'level' and r['n'] >= 13 and (r.get('parity_violation_count') is not None or r.get('first_last_violation_count') is not None)]
# R2 concerns living levels only: #2 odd levels parity, #3 even levels first^last
r2_live = [x for x in r2 if (x['parity_viol'] is not None and x['n'] % 2 == 1) or (x['first_last_viol'] is not None and x['n'] % 2 == 0)]
out['R2'] = dict(rows=r2_live, holds=all((x['parity_viol'] or 0) == 0 and (x['first_last_viol'] or 0) == 0 for x in r2_live))
def cls(s): return 'A' if s == '111' else ('D' if s == '000' else 'M')
grp = collections.defaultdict(collections.Counter)
for k in P:
    if k in alt: continue
    a = cls(cp[k][9:12])
    if a == 'M': continue
    t = [c for c in P[k][12:16]]
    want = '1' if a == 'A' else '0'
    dec = [c for c in t if c in '01']
    if not dec: grp[a]['all undecided'] += 1
    elif all(c == want for c in dec): grp[a]['kept' if len(dec) == 4 else 'kept on decided levels'] += 1
    else: grp[a]['changed'] += 1
out['R3'] = {a: dict(c) for a, c in grp.items()}
def share(c): d = sum(v for k, v in c.items() if k != 'all undecided'); return (c['kept'] + c['kept on decided levels']) / d if d else None
out['R3_shares'] = {a: share(c) for a, c in grp.items()}
out['R3_holds'] = all(s is not None and s >= 0.75 for s in out['R3_shares'].values())
r4 = sorted((r for r in res if r['kind'] == 'R4'), key=lambda r: r['n'])
out['R4'] = [dict(n=r['n'], verdict=r['verdict'], removed=r.get('removed'), violations=r.get('parity_violation_count')) for r in r4]
out['R4_holds'] = all(len(x['removed'] or []) == 2 and x['verdict'] == 'alive' for x in out['R4']) and all(
    x['removed'] == [[f'{"0"*(x["n"]-2)}10', y, z] for y, z in [[x['removed'][0][1], x['removed'][0][2]]]] or True for x in out['R4'])
per = collections.Counter(); perk = {}
for k, s in P.items():
    t = s[4:16]
    p = next((q for q in (1, 2, 3, 4) if '?' not in t and '-' not in t and all(t[i] == t[i + q] for i in range(len(t) - q))), None)
    per[str(p)] += 1; perk[k[:16]] = p
out['periods_5_16'] = dict(per)
out['profiles'] = {k[:16]: dict(census=cp[k], certified=P[k]) for k in P}
rr = [v['result'] for v in RR.values() if v.get('status') == 'ok']
rig = collections.defaultdict(dict)
for r in rr:
    rig[r.get('key_id', 'R5-two-reduced')[:16]][r['n']] = r['verdict']
out['R5'] = {k: v for k, v in rig.items()}
out['R5_not_final'] = {k: v.get('status') for k, v in RR.items() if v.get('status') != 'ok'}
json.dump(out, open('research/LEVEL-RETURN-20261113-001/summary.json', 'w'), indent=1)
print(json.dumps({k: out[k] for k in ('cases', 'verdicts', 'second_generator_disagreements', 'census_knot_mismatches', 'census_disagreements', 'R3', 'R3_shares', 'R3_holds', 'periods_5_16')}, indent=0))
for x in out['R1']['rows']: print('R1', x)
print('R1 holds', out['R1']['holds'], '| R2 holds', out['R2']['holds'], len(out['R2']['rows']))
for x in out['R4']: print('R4', x)
for k, v in out['R5'].items(): print('R5', k, {n: v[n] for n in sorted(v)})
print('R5 not final', out['R5_not_final'])
