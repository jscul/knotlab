"""Check for TWO-ENDS-20261117-001A-P001 (the thread's own code, 2026-11-17).
1. The composite automaton of 8db5da810c00-73: 88 states, threshold 5, period 2; exactly two periodic composites are not products,
   both from the self-similar type (children both of its own type) to itself, sending each all-equal assignment to an all-equal one.
2. The census (composite.json, recomputed for every small-orbit description alive at every depth): the product test holds exactly for
   the descriptions that forget, with l0 <= r + 1; it fails for all 25 open patterns of KEEP-REACH.
3. Theorem G's lower bound never exceeds a decided census value at depth 9 (top level 3, s = 1..4).
Writes result.json."""
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = ROOT / 'research/TWO-ENDS-20261117-001'
sys.path.insert(0, str(RUN))
from composite import WindowTree, automaton, is_product  # noqa: E402

fails = []
third = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/third_class.json'))['third']
tree = WindowTree(third['8db5da810c00-73']['key'])
a = automaton(tree)
if (a['states'], a['threshold'], a['period'], a['periodic_nonproduct']) != (88, 5, 2, 2):
    fails.append(('automaton -73', a['states'], a['threshold'], a['period'], a['periodic_nonproduct']))
for t0, t, T in a['nonproduct_examples']:
    self_similar = [c for c, _ in tree.children[t]] == [t, t] and t0 == t
    full = (1 << tree.m[t]) - 1
    const = all({z for x, z in T if x == e} <= {0, full} and len({z for x, z in T if x == e}) == 1 for e in (0, full))
    if not (self_similar and const):
        fails.append(('non-product mode', t0, t, self_similar, const))

stored = json.load(open(RUN / 'composite.json'))
census = {k: v for k, v in stored.items() if k.startswith('census')}
forget = {k: v for k, v in census.items() if v['r_forget'] is not None}
never = {k: v for k, v in census.items() if v['r_forget'] is None}
if any(v['l0'] is None or v['l0'] > v['r_forget'] + 1 for v in forget.values()):
    fails.append('a forgetting census description fails the product test or needs l0 > r + 1')
if any(v['l0'] is not None for v in never.values()):
    fails.append('a census description that never forgets passes the product test')
if any(v['l0'] is not None for k, v in stored.items() if not k.startswith('census')):
    fails.append('an open pattern passes the product test')

checked = below = 0
recs = {}
for line in gzip.open(ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt'):
    r = json.loads(line)
    if 'key' in r and ('census:' + r.get('case', '')[:12]) in forget:
        recs['census:' + r['case'][:12]] = r
for cid, rec in recs.items():
    v = forget[cid]
    R = v['r0'] + 1
    for cell in rec['levels']:
        if isinstance(cell['L_N'], int):
            s, r = cell['s'], 9 - 3 - cell['s']
            n = min(s - 1, s + r - R)
            bound = (max(n, 0) // v['l0'] + 3) / 2 if n > 0 else 0
            checked += 1
            if bound > cell['L_N']:
                below += 1
                fails.append(('G above census', cid, s, bound, cell['L_N']))
res = dict(automaton_73={k: a[k] for k in ('states', 'threshold', 'period', 'periodic_states', 'periodic_nonproduct')},
           census_alive=len(census), forgetting=len(forget), never_forgetting=len(never), open_patterns=len(stored) - len(census),
           g_cells_checked=checked, failures=fails[:10], passed=not fails)
json.dump(res, open(HERE / 'result.json', 'w'), indent=1)
print(json.dumps(res))
