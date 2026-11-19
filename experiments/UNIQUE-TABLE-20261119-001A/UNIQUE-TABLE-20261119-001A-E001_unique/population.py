"""Writes population.json: the 522 stages (no pair sharing two distinctions, table symmetries all checked and none moving a
junction, R3n misread) and the 1,330 controls (same, R3n exact), from CENSUS-READ-20261118-001's pass 5 (results kept compressed in
its artifacts).  Run: .venv/bin/python -B population.py"""
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC = ROOT / 'artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census/results_census-exact5.jsonl.gz'


def sym(st):
    s = st.get('symmetry', {})
    if s.get('twins_across_junctions') or s.get('search') == 'moves':
        return 'moves'
    return s.get('search', 'not_checked')


latest = {}
for line in gzip.open(SRC, 'rt'):
    r = json.loads(line)
    latest[r['case']] = r
pop, ctrl = [], []
for cid, r in sorted(latest.items()):
    if r['status'] != 'ok' or not cid.startswith('census'):
        continue
    for a in r['result']['arrangements']:
        for st in a['stages']:
            if st['max_shared'] >= 2 or sym(st) != 'fixes':
                continue
            row = {'key': a['key'], 'round': st['round'], 'junctions': st['junctions'], 'connectivity': st['connectivity']}
            if st['r3n'] == 'misread':
                pop.append(row)
            elif st['r3n'] == 'exact':
                ctrl.append(row)
out = {'source': str(SRC.relative_to(ROOT)), 'population': pop, 'controls': ctrl}
(HERE / 'population.json').write_text(json.dumps(out))
print(len(pop), len(ctrl))
