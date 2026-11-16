"""Read-out of population D (DIRECT-REACH-20261115-001A, 146 descriptions, finished 2026-11-15 06:14 UTC). The thread's own read-out
script, 2026-11-16. Reads codex/case_results/D/*.json and writes readout_D.json next to this file."""
import collections
import glob
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CODEX = ROOT / 'experiments/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach/codex'


def lvl(v):
    return (int(v) + 1).bit_length() - 1


def name(p):
    return {(2, 2, 2, 2): 'constant-2', (3, 3, 3, 3): 'constant-3', (3, 3, 4, 4): 'half-rate'}[tuple(p)]


rows = []
for f in sorted(glob.glob(str(CODEX / 'case_results/D/*.json'))):
    d = json.load(open(f))
    cen = [lv['L_N'] for lv in d['census']['levels']]
    th = {t['k0']: [lv['L_N'] for lv in t['levels']] for t in d['threshold_reach']}
    classes = d['ties'].get('classes', [])
    spans = [sorted({lvl(v) for v in c}) for c in classes]
    chain_3_8 = any(set(range(3, 9)) <= set(s) for s in spans)
    chain_2_8 = any(set(range(2, 9)) <= set(s) for s in spans)
    rows.append(dict(case=d['case'], profile=name(cen), census=cen, top2=th[2], top3=th[3],
                     chain_3_8=chain_3_8, chain_2_8=chain_2_8, forced_pairs=d['ties']['forced_pair_count'],
                     tie_verdict=d['ties']['verdict'], life=[x['verdict'] for x in d['life']],
                     hom_accepted=d['homomorphisms']['accepted_count'],
                     hom_maps=[m['name'] for m in d['homomorphisms']['accepted_maps']],
                     cls=d['census']['classes']['relative']['class'],
                     incomplete=len(d['incomplete_certifications']), seconds=d['seconds']))

by = collections.defaultdict(list)
for r in rows:
    by[r['profile']].append(r)
out = {'n': len(rows), 'profiles': {k: len(v) for k, v in by.items()}}
out['tie_verdicts'] = dict(collections.Counter(r['tie_verdict'] for r in rows))
out['incomplete_certifications'] = sum(r['incomplete'] for r in rows)
out['life_N10_12'] = dict(collections.Counter(tuple(r['life']) for r in rows).most_common())
out['life_N10_12'] = {str(k): v for k, v in out['life_N10_12'].items()}

# P1: one tie class meeting every level 3..8 among the constant-2 descriptions
c2 = by['constant-2']
out['P1'] = dict(constant2=len(c2), chain_3_8=sum(r['chain_3_8'] for r in c2), chain_2_8=sum(r['chain_2_8'] for r in c2),
                 chain_3_8_in_others=sum(r['chain_3_8'] for r in rows if r['profile'] != 'constant-2'))

# Control: top 3 recomputed at s = 1..4 against the census; top 2 at s = 1..4 against the top-3 profile
out['control'] = {}
for p, rs in by.items():
    out['control'][p] = dict(top3_equals_census=sum(r['top3'][:4] == r['census'] for r in rs),
                             top2_equals_top3=sum(r['top2'][:4] == r['census'] for r in rs),
                             top2_profiles=dict(collections.Counter(str(r['top2'][:4]) for r in rs if r['top2'][:4] != r['census'])))

# P2: deeper s from top 2 (s = 5, 6) and top 3 (s = 5)
out['deep'] = {}
for p, rs in by.items():
    agree = [r for r in rs if r['top2'][:4] == r['census']]
    out['deep'][p] = dict(agree=len(agree),
                          top2_s5_s6=dict(collections.Counter(str(r['top2'][4:6]) for r in agree)),
                          top3_s5=dict(collections.Counter(str(r['top3'][4]) for r in rs)),
                          top2_full=dict(collections.Counter(str(r['top2']) for r in agree)))
c3 = [r for r in by['constant-3'] if r['top2'][:4] == r['census']]
hr = [r for r in by['half-rate'] if r['top2'][:4] == r['census']]
out['P2'] = dict(constant3_agree=len(c3), constant3_le3_at_s5_s6=sum(all(x == 3 for x in r['top2'][4:6]) for r in c3),
                 halfrate_agree=len(hr), halfrate_ge5_at_s6=sum(r['top2'][5] == '> 4' for r in hr))

# Homomorphisms
out['hom'] = {p: dict(with_map=sum(r['hom_accepted'] > 0 for r in rs),
                      maps=dict(collections.Counter(m for r in rs for m in r['hom_maps']).most_common(8))) for p, rs in by.items()}
out['by_class'] = {p: dict(collections.Counter(r['cls'] for r in rs)) for p, rs in by.items()}
out['seconds_total'] = sum(r['seconds'] for r in rows)
out['rows'] = rows
json.dump(out, open(HERE / 'readout_D.json', 'w'), indent=1)
show = {k: v for k, v in out.items() if k != 'rows'}
print(json.dumps(show, indent=1))
