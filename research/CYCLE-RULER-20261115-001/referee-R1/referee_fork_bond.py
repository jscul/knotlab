"""Referee CYCLE-RULER-R1: is {0, 001, 011} (ids 1, 8, 10) a bond of the full pattern of the breaking case that contains the 7-knot
fork core? Pattern: RULER-LEVEL-R1's fresh rebuild (case_1.json, sample 20, N = 6). SAT projections with pysat."""
import itertools, json
from pathlib import Path
from pysat.solvers import Glucose4
ROOT = Path(__file__).resolve().parents[3]
d = json.load(open(ROOT / 'research/RULER-LEVEL-20261114-001/referee-R1/codex/breaking_audit/case_1.json'))
cl = []
for a, b, c in d['knots']:
    cl += [[a + 1, b + 1, c + 1], [-(a + 1), -(b + 1), -(c + 1)]]
s = Glucose4(bootstrap_with=cl)
proj = lambda idx: [bits for bits in itertools.product((0, 1), repeat=len(idx)) if s.solve(assumptions=[(v + 1) if b else -(v + 1) for v, b in zip(idx, bits)])]
W = [1, 8, 10]
res = {"case": d['case'], "key": d['key'], "claimed_L": d['claimed_L'], "triple_allowed": proj(W),
       "pairs_allowed": {str(p): len(proj(list(p))) for p in itertools.combinations(W, 2)}}
res["bond"] = len(res["triple_allowed"]) < 8 and all(v == 4 for v in res["pairs_allowed"].values())
print(json.dumps(res)); (Path(__file__).with_suffix('.json')).write_text(json.dumps(res, indent=1))
