"""Checks for proof.md (DIRECT-REACH-20261115-001B-P001). Reruns, from the committed code in research/DIRECT-REACH-20261115-001/:
(1) the block computation against SAT: joint relations of orbit pairs at depth 6 and life at depths 2..8, then at depth 10 and life at
    depths 2..12 (exploratory/gate_window_tree.py);
(2) the every-depth block verdicts against the certified depth-9 results of DIRECT-REACH-20261115-001A (crosscheck_window_tree.py);
(3) every descent's blocks against explicit addresses, its ties and three-member bonds against the depth-9 pattern, and its
    finite-reader states against the depth-12 pattern (gate_chain.py);
(4) the coverage tallies of Corollaries W and D from the committed JSON outputs.
Writes result.json next to this file."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R = ROOT / 'research/DIRECT-REACH-20261115-001'
PY = str(ROOT / '.venv/bin/python')


def run(script, *args):
    out = subprocess.run([PY, '-B', str(script), *args], cwd=ROOT, capture_output=True, text=True, timeout=3600)
    return out.returncode, out.stdout.strip().splitlines()[-1] if out.stdout.strip() else out.stderr[-500:]


res = {}
code, last = run(R / 'exploratory/gate_window_tree.py')
res['block_gate'] = dict(exit=code, summary=last, passed=code == 0 and 'mismatches 0' in last and 'life mismatches 0' in last)
code, last = run(R / 'exploratory/gate_window_tree.py', '10')
res['block_gate_depth10'] = dict(exit=code, summary=last, passed=code == 0 and 'mismatches 0' in last and 'life mismatches 0' in last)
code, last = run(R / 'crosscheck_window_tree.py')
cc = json.load(open(R / 'crosscheck_window_tree.json'))
res['block_crosscheck'] = dict(exit=code, tally=cc['tally'], disagreements=len(cc['disagreements']),
                               passed=code == 0 and not cc['disagreements'])
code, last = run(R / 'gate_chain.py')
gc = json.load(open(R / 'gate_chain.json'))
res['descent_gate'] = dict(exit=code, cases=len(gc['cases']), claims=sum(g['claims'] for g in gc['cases'].values()),
                           passed=code == 0 and gc['passed'])

# (4) coverage
wt = json.load(open(R / 'exploratory/window_tree_census.json'))['cases']
c2 = json.load(open(R / 'chain_ties_constant-2.json'))
c3 = json.load(open(R / 'chain_bounded3_constant-3.json'))
auto = json.load(open(R / 'exploratory/automatic_search.json'))
prof = {cid: tuple(row['profile']) for cid, row in wt.items()}
bounded = {cid for cid, row in wt.items() if 'k3' in row}
cov = {}
for p, name in (((2, 2, 2, 2), 'constant-2'), ((3, 3, 3, 3), 'constant-3'), ((3, 3, 4, 4), 'half-rate')):
    ids = [c for c in prof if prof[c] == p]
    verdicts = {}
    for c in ids:
        if c in bounded:
            verdicts.setdefault(wt[c]['k3']['verdict'], []).append(c)
    cov[name] = dict(total=len(ids), bounded_orbits=len([c for c in ids if c in bounded]),
                     block_verdicts={v: len(cs) for v, cs in verdicts.items()},
                     alive_every_depth_blocks=sum(1 for c in ids if c in bounded and wt[c]['k3']['alive_every_depth'] in (True, 'True')))
w2 = {c for c in prof if prof[c] == (2, 2, 2, 2) and c in bounded and wt[c]['k3']['verdict'] == 'tie at every s'}
d2 = {c for c, r in c2.items() if r['chain'] and auto.get(c)}
w3 = {c for c in prof if prof[c] == (3, 3, 3, 3) and c in bounded and wt[c]['k3']['verdict'] == 'no tie; two-orbit 3-bond at every s'}
d3 = {c for c, r in c3.items() if r['chain'] and r['machines']}
cov['constant-2']['every_depth_L2'] = dict(blocks=len(w2), descents=len(d2), descents_growing=len(d2 - bounded), union=len(w2 | d2))
cov['constant-3']['every_depth'] = dict(blocks_L3_exact=len(w3), descents_L_le_3=len(d3), descents_growing=len(d3 - bounded),
                                        union_L_le_3=len(w3 | d3))
cov['life_finite_reader'] = sum(1 for c in prof if auto.get(c))
res['coverage'] = cov
res['status'] = 'passed' if all(res[k]['passed'] for k in ('block_gate', 'block_gate_depth10', 'block_crosscheck', 'descent_gate')) else 'failed'
json.dump(res, open(HERE / 'result.json', 'w'), indent=1)
print(res['status'], json.dumps(cov))
