"""score.py: the frozen predictions of README.md, "Frozen", scored on the frozen runs; writes score.json."""
import json, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
def lines(fn): return [json.loads(l) for l in open(HERE / fn)]
out = {}
# P1
p1 = collections.defaultdict(list); rows = []
for x in lines('frozen_built.jsonl'):
    if 'new carriers' in x:
        r = x['new carriers']; fam = r['family']; R = int(fam.split()[0]); n = int(fam.split()[3].rstrip(','))
        for rd in r['rounds']:
            for k, a in rd.items():
                if not k.startswith('carriers born'): continue
                rows.append({'family': fam, 'round': rd['round'], 'tuples': a['tuples'], 'one rule': a['one rule'],
                             'SHORT': all(l and u for l, u in a['SHORT']), 'UPTO5': all(l and u for l, u in a['UPTO5']),
                             'unread SHORT': all(u for l, u in a['SHORT']),
                             'origin': all(a['origin']['each carrier a function of the start values']) and a['origin'].get("relation on the start's allowed states") and a['origin'].get('sum of the representatives a sum of start laws'),
                             'facts at the start SHORT': [l for l, u in a['origin'].get('facts at the start, SHORT', [])],
                             'facts at the start UPTO5': [l for l, u in a['origin'].get('facts at the start, UPTO5', [])],
                             'unread at the start': [u for l, u in a['origin'].get('facts at the start, SHORT', [])],
                             'R': R, 'n': n})
        ends = [rd for rd in r['rounds'] if 'end' in rd]
        if ends: p1['ended'].append((fam, ends[0]))
    elif 'start groups' in x:
        r = x['start groups']; R = int(r['family'].split()[0])
        for rd in r['rounds']:
            if 'tuples' in rd: p1['start groups'].append((r['family'], rd['round'], rd['tuples'] == 2 ** (R - 1) and rd['one rule']))
    elif x.get('part') == 'origin control':
        p1['origin control'].append((x['family'], x['one rule'], x['origin']))
out['P1 new-carrier rows'] = len(rows)
out['P1a one rule on every new-carrier row'] = all(r['one rule'] for r in rows)
out['P1a start groups one rule at every round read'] = all(ok for _, _, ok in p1['start groups'])
out['P1a start-group rows'] = len(p1['start groups'])
out['P1b n = 5, 7: class facts read by no single knot, both readings'] = all(r['SHORT'] and r['UPTO5'] for r in rows if r['n'] in (5, 7))
out['P1b by n (rows with all carriers class facts and unread, SHORT / UPTO5 / rows)'] = {
    n: [sum(r['SHORT'] for r in rows if r['n'] == n), sum(r['UPTO5'] for r in rows if r['n'] == n), sum(1 for r in rows if r['n'] == n)] for n in (4, 5, 6, 7)}
out['P1c origin on every row'] = all(r['origin'] for r in rows)
out['(c) before growth: start representatives class facts under SHORT (rows all / some / none)'] = [
    sum(all(r['facts at the start SHORT']) for r in rows), sum(any(r['facts at the start SHORT']) and not all(r['facts at the start SHORT']) for r in rows),
    sum(not any(r['facts at the start SHORT']) for r in rows)]
out['(c) before growth: start representatives class facts under UPTO5 (all / some / none)'] = [
    sum(all(r['facts at the start UPTO5']) for r in rows), sum(any(r['facts at the start UPTO5']) and not all(r['facts at the start UPTO5']) for r in rows),
    sum(not any(r['facts at the start UPTO5']) for r in rows)]
out['(c) before growth: start representatives read by no single knot on every row'] = all(all(r['unread at the start']) for r in rows)
out['ended runs'] = p1['ended']
out['P2 origin control: one rule and the first carrier not a start function, every member'] = all(o and not orig[0] for _, o, orig in p1['origin control'])
out['P2 origin control members'] = len(p1['origin control'])
prem = {}
for s in ('census', 'heldout', 'built', 'sampled', 'census_one_fewer', 'census_arity_floor'):
    L = lines('frozen_premises_%s.jsonl' % s); tot = L[-1]
    nostage = sum(1 for x in L[:-1] if not any('premises broken' in r for r in x['rounds']))
    prem[s] = {'starts': len(L) - 1, 'starts with no stage': nostage, **tot}
out['P2 premises and span'] = prem
# P3
p3 = []
for x in lines('frozen_controls.jsonl'):
    if 'start groups' in x:
        r = x['start groups']; R = int(r['family'].split()[0])
        reads = [rd for rd in r['rounds'] if 'tuples' in rd]; ends = [rd['end'] for rd in r['rounds'] if 'end' in rd]
        p3.append({'family': r['family'], 'all tuples at every round read': all(rd['tuples'] == 2 ** R for rd in reads),
                   'rounds read': [rd['round'] for rd in reads], 'end': ends})
out['P3 controls'] = {'members': len(p3), 'as predicted': sum(1 for c in p3 if c['all tuples at every round read']),
                      'not as predicted': [c for c in p3 if not c['all tuples at every round read']],
                      'stalled': sum(1 for c in p3 if c['end'])}
# P4
p4 = collections.defaultdict(dict)
for x in lines('frozen_cuts.jsonl'):
    r = x['start groups']; reads = {rd['round']: rd for rd in r['rounds'] if 'tuples' in rd}
    p4[r['family']][r['arm']] = {'tuples by round': {t: reads[t]['tuples'] for t in reads}, 'end': [rd['end'] for rd in r['rounds'] if 'end' in rd]}
def p4ok(f):
    a = p4[f]
    cut = all(a[arm]['tuples by round'].get(0) == 8 and a[arm]['tuples by round'].get(1) == 4 for arm in ('one_fewer', 'arity_floor'))
    return cut and all(v == 8 for v in a['ordinary']['tuples by round'].values())
out['P4 cuts'] = {'members': len(p4), 'as predicted': sum(p4ok(f) for f in p4), 'detail': dict(p4)}
# P5
p5 = []
for x in lines('frozen_nae.jsonl'):
    if 'start groups' in x:
        r = x['start groups']; p5.append((r['family'], [(rd['round'], rd.get('tuples'), rd.get('of'), rd.get('end')) for rd in r['rounds']]))
    elif 'new carriers' in x:
        r = x['new carriers']; p5.append((r['family'] + ' (new carriers)', [(rd['round'], {k: v for k, v in rd.items() if k.startswith('carriers')}, rd.get('end')) for rd in r['rounds']]))
out['P5 not-all-equal (read only)'] = p5
json.dump(out, open(HERE / 'score.json', 'w'), indent=1)
for k, v in out.items():
    if k not in ('P4 cuts', 'P5 not-all-equal (read only)', 'ended runs'): print(k, ':', json.dumps(v)[:600])
print('P4', out['P4 cuts']['members'], out['P4 cuts']['as predicted']); print('ended', out['ended runs'][:6])
