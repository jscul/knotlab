"""Checks for proof.md (BLOCK-REACH-20261116-001A-P001): reruns, from research/BLOCK-REACH-20261116-001/, the forgetting gate (window
relations against SAT; the bound against every decided census value), the census run (Corollary F) and the Lemma U gate (depth-9 bonds
at depths 10 and 11), then recomputes the corollary's table. Writes result.json next to this file."""
import collections
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R = ROOT / 'research/BLOCK-REACH-20261116-001'
PY = str(ROOT / '.venv/bin/python')
res = {}
for name in ('gate_forget', 'run_census', 'gate_upper'):
    out = subprocess.run([PY, '-B', str(R / (name + '.py'))], cwd=ROOT, capture_output=True, text=True, timeout=3600)
    res[name] = dict(exit=out.returncode)
res['gate_forget'].update(json.load(open(R / 'gate_forget.json')))
res['gate_upper'].update(json.load(open(R / 'gate_upper.json')))
rows = json.load(open(R / 'census_forget.json'))['rows']
table = collections.Counter((r['name'], r['cyclic'] if r['name'] == 'ruler' else None, r['r']) for r in rows.values())
res['corollary_F'] = {str(k): v for k, v in sorted(table.items(), key=str)}
res['r_all_equals_r_stable'] = all(r['r_all'] == r['r_stable'] for r in rows.values())
res['small_orbit_descriptions'] = len(rows)
res['status'] = 'passed' if (res['gate_forget'].get('passed') and res['gate_upper'].get('passed') and res['run_census']['exit'] == 0
                             and res['r_all_equals_r_stable'] and len(rows) == 786) else 'failed'
json.dump(res, open(HERE / 'result.json', 'w'), indent=1)
print(res['status'], res['corollary_F'])
