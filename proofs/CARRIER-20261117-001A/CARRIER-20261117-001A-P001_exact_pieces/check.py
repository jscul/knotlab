"""Check for CARRIER-20261117-001A-P001 (the thread's own code, 2026-11-17).
1. Recompute five of the stored every-depth results and compare: orbit-and-block bonds of bace53f8f952-147 and -111, stem bonds of
   depth 2 of bace53f8f952-58, ca1efb37ad88-361 and 8db5da810c00-73.
2. From the stored results (block_25.json, head/*.json): for each of the 25, the least of the two carriers at every s and every depth
   tier (s to past every preperiod and common period); the twelve with an unexposed dependence bounded at every s and depth with
   maximum 5; the thirteen mutants of 8db5da810c00 with stem bonds 5, 5, 6, 6 at s = 3..6 and none of at most 8 from s = 7.
3. From the threshold run: no bond of at most 5 members at s = 5 and 6 at depth 11 for the twelve mutants besides -73; with the stems,
   L_11(3, 5) = L_11(3, 6) = 6 for all thirteen (-73's from KEEP-REACH's exact reading).
Writes result.json."""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = ROOT / 'research/CARRIER-20261117-001'
sys.path.insert(0, str(RUN))
from two_block import WindowTree, every_depth_block  # noqa: E402
from head_bond import every_depth_head  # noqa: E402

third = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/third_class.json'))['third']
open25 = [i for i, r in third.items() if not r['kind'].startswith('forget')]
block = json.load(open(RUN / 'block_25.json'))
stems = {json.load(open(f))['index']: json.load(open(f)) for f in (RUN / 'head').glob('*_d2.json')}
fails = []

for idx in ('bace53f8f952-147', 'bace53f8f952-111'):
    e = every_depth_block(WindowTree(third[idx]['key']), 3, cap=8)
    if e['sequences'] != block[idx]['sequences']:
        fails.append(('recompute block', idx))
for idx in ('bace53f8f952-58', 'ca1efb37ad88-361', '8db5da810c00-73'):
    e = every_depth_head(WindowTree(third[idx]['key']), 3, 2, cap=8)
    if e['sequences'] != stems[idx]['sequences']:
        fails.append(('recompute stem', idx))


def at(e, r, s, first, R):
    P = e['sequences']['r=%d' % r if r < R else 'r>=%d' % R]
    j = s - first
    if j < 0:
        return None
    while j >= len(P):
        j -= e['period']
    return P[j]


table = {}
for idx in open25:
    b, h = block[idx], stems.get(idx)
    reach = (b['start'] + b['period'] + (h['start'] + h['period'] + 3 if h else 0)) * 2
    reach += math.lcm(b['period'], h['period'] if h else 1)
    rows = []
    for s in range(1, reach + 1):
        row = []
        for r in range(0, 4):
            vals = [at(b, r, s, 1, b['r0'] + 1)]
            if h:
                vals.append(at(h, r, s, h['first_s'], h['r0']))
            vals = [v for v in vals if v is not None]
            row.append(min(vals) if vals else None)
        rows.append(row)
    flat = [v for row in rows for v in row]
    table[idx] = dict(bounded=all(v is not None for v in flat), max=max(v for v in flat if v is not None),
                      first_missing=next((i + 1 for i, row in enumerate(rows) if None in row), None))
unexposed = [i for i in open25 if third[i]['kind'].startswith('top joints stay')]
products = [i for i in open25 if third[i]['kind'].startswith('top joints become')]
for idx in unexposed:
    if not (table[idx]['bounded'] and table[idx]['max'] == 5):
        fails.append(('unexposed not bounded at 5', idx, table[idx]))
for idx in products:
    P = stems[idx]['sequences']['r>=0']
    if P[:4] != [5, 5, 6, 6] or any(v is not None for v in P[4:]) or table[idx]['first_missing'] != 7:
        fails.append(('mutant stem profile', idx, P[:8], table[idx]))

exact = {}
for idx in products:
    if idx == '8db5da810c00-73':
        d = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/exact_third_8db5da810c00-73_N11.json'))
        low = {c['s']: c['L_N'] for c in d['levels']}
        ok = low.get(5) == 6 and low.get(6) == 6
    else:
        d = json.load(open(RUN / ('threshold_%s.json' % idx)))
        ok = all(c['within_bound'] == 'no' and c['L_N'] == '> 5' for c in d['cells']) and {c['s'] for c in d['cells']} == {5, 6}
    up = stems[idx]['sequences']['r>=0'][2:4] == [6, 6]
    exact[idx] = ok and up
    if not exact[idx]:
        fails.append(('exact 6', idx))

res = dict(open_patterns=len(open25), unexposed=len(unexposed), unexposed_bounded=sum(table[i]['bounded'] for i in unexposed),
           products=len(products), products_exact_6=sum(exact.values()), table=table, failures=fails, passed=not fails)
json.dump(res, open(HERE / 'result.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'table'}))
