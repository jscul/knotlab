"""Exploratory, on committed census records: the direct profiles, their weight, activity class, and whether the pattern (levels 0..7)
ties a level-3 address to a level-(3+s) address for s = 1..4 (a size-2 bond), and whether each level is rigid on its own."""
import sys, gzip, json, collections
import numpy as np
from pysat.solvers import Cadical195
sys.path.insert(0, 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex')
from pattern import pattern
recs = [json.loads(l) for l in gzip.open('artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt')]
def lvl(i): return (int(i) + 1).bit_length() - 1
prof = collections.Counter(); rows = []
for a in recs:
    if 'key' not in a or a['flags']['no_join'] or a['union'] != 'alive': continue
    Ls = [l['L_N'] for l in a['levels']]
    if all(isinstance(x, int) for x in Ls) and len(set(Ls)) == 1:
        prof[(tuple(Ls), a['classes']['relative']['class'])] += 1; rows.append(a)
print('direct profiles by class:', dict(prof))
# ties at N = 7 between level 3 and level 3+s for the L = 2 ones
tie_share = collections.Counter()
for a in rows:
    if a['levels'][0]['L_N'] != 2: continue
    K = [tuple(int(x) for x in k) for k in pattern(a['key'], 7)]
    S = Cadical195()
    for x, y, z in K: S.add_clause([x + 1, y + 1, z + 1]); S.add_clause([-x - 1, -y - 1, -z - 1])
    def tied(u, v):
        return not (S.solve(assumptions=[u + 1, v + 1]) or S.solve(assumptions=[-u - 1, -v - 1])) or not (S.solve(assumptions=[u + 1, -v - 1]) or S.solve(assumptions=[-u - 1, v + 1]))
    top = [x for x in range(255) if lvl(x) == 3]
    n_tied = sum(tied(top[0], v) for v in range(255) if lvl(v) == 7)
    tie_share[n_tied] += 1
print('L=2 descriptions: number of level-7 addresses tied to the first level-3 address (of 16):', dict(tie_share))
