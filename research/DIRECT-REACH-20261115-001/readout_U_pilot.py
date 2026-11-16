"""Read-out of the U pilot (DIRECT-REACH-20261115-001): the first 6 population-U descriptions by case id, 900 s per census-undecided
cell. The first comes from the Codex smoke (codex/case_results/U), the other five from thread/pilot_U (LONG_RUNNING DIRECT-REACH-A2).
The thread's own script, 2026-11-16; writes readout_U_pilot.json. Continue rule (predictions.md, P3): run the other 82 only if at least
2 of the 6 have every undecided cell decided."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[1] / 'experiments/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach'
rows = []
smoke = json.load(open(EXP / 'codex/case_results/U/00a344d3f150db37014b0d13d3ca12acf65eee4350350df05052e6df304ce805.json'))
cells = []
for f in smoke['U_followups']:
    lv = f['levels'][0] if 'levels' in f else f
    cells.append(dict(s=lv['s'], L_N=lv['L_N'], seconds=lv.get('seconds')))
rows.append(dict(case=smoke['case'], source='codex smoke', census=[x['L_N'] for x in smoke['census']['levels']], cells=cells))
for line in open(EXP / 'thread/pilot_U/results.jsonl'):
    r = json.loads(line)['result']
    rows.append(dict(case=r['case'], source='thread pilot', census=r['census_levels'],
                     cells=[dict(s=f['s'], L_N=f['L_N'], seconds=f.get('seconds')) for f in r['followups']]))
rows.sort(key=lambda r: r['case'])
for r in rows:
    r['decided_all'] = all(isinstance(c['L_N'], int) for c in r['cells'])
out = dict(descriptions=len(rows), decided_all=sum(r['decided_all'] for r in rows),
           cells=sum(len(r['cells']) for r in rows), cells_decided=sum(isinstance(c['L_N'], int) for r in rows for c in r['cells']),
           decided_values=sorted(c['L_N'] for r in rows for c in r['cells'] if isinstance(c['L_N'], int)),
           decided_seconds_max=max(c['seconds'] for r in rows for c in r['cells'] if isinstance(c['L_N'], int)),
           continue_rule_met=sum(r['decided_all'] for r in rows) >= 2, rows=rows)
json.dump(out, open(HERE / 'readout_U_pilot.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != 'rows'}))
for r in rows:
    print(r['case'][:12], r['census'], [(c['s'], c['L_N']) for c in r['cells']])
