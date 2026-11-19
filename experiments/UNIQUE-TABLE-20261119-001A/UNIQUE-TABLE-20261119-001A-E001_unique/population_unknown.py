"""Writes population_unknown.json (Amendment 1): the 64 stages of CENSUS-READ's pass 5 whose symmetry enumeration stopped at its
limit and which that study's referee showed have no junction-moving symmetry: the 5 R3n misread (added to the population) and the
59 R3n read exactly (added to the controls).  Run: .venv/bin/python -B population_unknown.py"""
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC = ROOT / 'artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census/results_census-exact5.jsonl.gz'
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
            s = st.get('symmetry', {})
            if st['max_shared'] >= 2 or s.get('twins_across_junctions') or s.get('search') != 'unknown':
                continue
            row = {'key': a['key'], 'round': st['round'], 'junctions': st['junctions'], 'connectivity': st['connectivity']}
            (pop if st['r3n'] == 'misread' else ctrl if st['r3n'] == 'exact' else []).append(row)
(HERE / 'population_unknown.json').write_text(json.dumps({'source': str(SRC.relative_to(ROOT)), 'population': pop, 'controls': ctrl}))
print(len(pop), len(ctrl))
