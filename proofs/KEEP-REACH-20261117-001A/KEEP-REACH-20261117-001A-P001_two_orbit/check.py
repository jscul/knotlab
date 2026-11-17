"""Checks for proof.md (KEEP-REACH-20261117-001A-P001): reruns the gates (gate_two_orbit.py: brute force, Theorem W agreement, the
census) and the census classification (run_census.py, under a minute), then recounts the census, the fresh sample, the mutations and
the third class from the committed outputs (the sample and mutation runs take about 40 minutes and are not rerun here). Writes
result.json next to this file."""
import collections
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R = ROOT / 'research/KEEP-REACH-20261117-001'
PY = str(ROOT / '.venv/bin/python')
res = {}
for name in ('gate_two_orbit', 'run_census'):
    out = subprocess.run([PY, '-B', str(R / (name + '.py'))], cwd=ROOT, capture_output=True, text=True, timeout=3600)
    res[name] = out.returncode
gate = json.load(open(R / 'gate_two_orbit.json'))
census = json.load(open(R / 'census_keep.json'))['rows']
never = [c for c in census.values() if c.get('r_all') is None]
res['census'] = dict(descriptions=len(census), never_forget=len(never),
                     never_forget_two_orbit_every_s=sum(1 for c in never if c['two_orbit_every_s']),
                     forget_with_two_orbit_every_s=sum(1 for c in census.values() if c.get('r_all') is not None and c['two_orbit_every_s']),
                     four_tail=sorted(c['two_orbit_tail_max'] for c in never if c['name'] in ('other', 'undecided')))
for f in ('sample_keep.jsonl', 'mutants_keep.jsonl'):
    rows = [json.loads(l) for l in open(R / f)]
    alive = [r for r in rows if r.get('small_orbits') and r.get('alive_every_depth') and not r.get('timeout')]
    nf = [r for r in alive if r.get('r_all') is None]
    res[f] = dict(alive=len(alive), forget=len(alive) - len(nf), never_two_orbit=sum(1 for r in nf if r['two_orbit_every_s']),
                  third=sum(1 for r in nf if not r['two_orbit_every_s']))
res['third_kinds'] = json.load(open(R / 'third_class.json'))['tally']
ok = (gate['passed'] and res['census']['never_forget'] == 46 and res['census']['never_forget_two_orbit_every_s'] == 46
      and res['census']['forget_with_two_orbit_every_s'] == 0 and res['census']['four_tail'] == [4, 4, 5, 6])
res['status'] = 'passed' if ok and all(v == 0 for k, v in res.items() if k in ('gate_two_orbit', 'run_census')) else 'failed'
json.dump(res, open(HERE / 'result.json', 'w'), indent=1)
print(res['status'], json.dumps({k: v for k, v in res.items() if k != 'status'}))
