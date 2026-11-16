"""Checks for proof.md (MARK-RATE-20261116-001A-P001): reruns the signature-family gate (gate_marks.py, real signatures against the
computed families by SAT) and recounts Corollary M and the consistency gates from research/MARK-RATE-20261116-001/census_marks.json
(the census run itself, about 23 minutes, is run_census.py). Writes result.json next to this file."""
import collections
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R = ROOT / 'research/MARK-RATE-20261116-001'
out = subprocess.run([str(ROOT / '.venv/bin/python'), '-B', str(R / 'gate_marks.py')], cwd=ROOT, capture_output=True, text=True,
                     timeout=3600)
gate = json.load(open(R / 'gate_marks.json'))
rows = json.load(open(R / 'census_marks.json'))['rows']
table = collections.Counter((r['name'], r['cyclic'] if r['name'] == 'ruler' else None, r['r'], r['no_skip']) for r in rows.values())
gates = dict(r1_all_pass=all(r['no_skip'] for r in rows.values() if r['r'] == 1),
             no_half_rate_passes=not any(r['no_skip'] for r in rows.values() if r['name'] == 'half-rate'),
             no_pass_below_s_plus_1=not any(r['no_skip'] and isinstance(L, int) and L < s + 1
                                            for r in rows.values() for s, L in enumerate(r['profile'], 1)))
res = dict(gate_exit=out.returncode, gate=gate, consistency=gates, descriptions=len(rows),
           corollary_M={str(k): v for k, v in sorted(table.items(), key=str)},
           status='passed' if out.returncode == 0 and gate['passed'] and all(gates.values()) and len(rows) == 779 else 'failed')
json.dump(res, open(HERE / 'result.json', 'w'), indent=1)
print(res['status'], gates)
