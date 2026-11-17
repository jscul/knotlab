"""Check for MODE-BOND-20261117-001A-P001 (the thread's own code, 2026-11-17).
1. For each of the 5 patterns, recompute: the joined children of types 4, 5 and 7 (only the first child joined), the joined automaton
   on the top's component (l0 = 5, no periodic non-product), and, at depth 9, that no self-similar address shares a component with a
   level-3 address.
2. Read joined_census.json: the joined product test passes for exactly the 740 census descriptions that forget and none of the 46,
   and for the 13 of KEEP-REACH's third class only.
3. Read gate_growth.json: passed.
Writes result.json."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = ROOT / 'research/MODE-BOND-20261117-001'
sys.path.insert(0, str(RUN))
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
from growth13 import PATTERNS, joined_children, joined_automaton  # noqa: E402
from joined_census import light  # noqa: E402
from mode_bond import orbit_tree, aid  # noqa: E402
from pattern import pattern, components  # noqa: E402

fails = []
third = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/third_class.json'))['third']
for idx in PATTERNS:
    D = light(third[idx]['key'])
    tree = D.tree
    for t in (4, 5, 7):
        if joined_children(tree, t) != [0] or tree.children[t][1][0] != 7:
            fails.append(('block', idx, t))
    a = joined_automaton(D)
    if a['l0'] != 5 or a['periodic_nonproducts'] != 0 or 7 in a['component_types']:
        fails.append(('automaton', idx, a['l0'], a['component_types']))
    N = 9
    lab = components(pattern(third[idx]['key'], N), (1 << (N + 1)) - 1)
    ot = orbit_tree(tree, N)
    top = {lab[aid(x)] for _, aa in ot[3] for x in aa}
    if any(lab[aid(x)] in top for n in range(N + 1) for t, aa in ot[n] if t == 7 for x in aa):
        fails.append(('component', idx))
jc = json.load(open(RUN / 'joined_census.json'))
if jc['tally'] != {'forget_pass': 740, 'forget_fail': 0, 'never_pass': 0, 'never_fail': 46}:
    fails.append(('census', jc['tally']))
passing = sorted(i for i, v in jc['third'].items() if v['l0'] is not None)
if len(passing) != 13 or not all(i.startswith('8db5da810c00') for i in passing):
    fails.append(('third', passing))
if not json.load(open(RUN / 'gate_growth.json'))['passed']:
    fails.append('gate_growth')
res = dict(patterns=PATTERNS, census=jc['tally'], third_passing=len(passing), failures=fails, passed=not fails)
json.dump(res, open(HERE / 'result.json', 'w'), indent=1)
print(json.dumps(res))
