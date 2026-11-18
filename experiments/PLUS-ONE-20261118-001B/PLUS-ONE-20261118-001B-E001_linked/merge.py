"""Score PLUS-ONE-20261118-001B-E001.  python3 -B merge.py <run dir> [<out json>]"""
import json
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from longrun import load_results  # noqa: E402
R = load_results(sys.argv[1])
bad = [c for c, r in R.items() if r.get('status') != 'ok']
census = [x for c, r in R.items() if c.startswith('census') and r.get('status') == 'ok' for x in r['result']['rows']]
six = [r['result'] for c, r in R.items() if c.startswith('six') and r.get('status') == 'ok']
out = {'not_ok': bad}
# fitting (the census): matches, false positives (linked but dimension = largest class), unlinked exceptions, shapes
m = sum(1 for x in census if x['dim'] == x['linked_sum'])
fp = [x for x in census if x['linked_sum'] > x['largest_class'] and x['dim'] == x['largest_class']]
ue = [x for x in census if x['linked_sum'] == x['largest_class'] and x['dim'] != x['largest_class']]
other = [x for x in census if x['dim'] != x['linked_sum'] and x not in fp and x not in ue]
shapes = Counter((tuple(s[0]), s[1]) for x in census for s in x['shapes'])
out['census (fitting)'] = {'arrangements': len(census), 'rule matches': m, 'false positives': len(fp), 'unlinked exceptions': len(ue),
                           'other misses': [(x['key'], x['dim'], x['largest_class'], x['linked_sum'], x['shapes']) for x in other[:10]],
                           'n other misses': len(other), 'linked components (sizes, clique)': {str(k): v for k, v in shapes.items()}}
# P1 (six knots): among settled polynomial arrangements with a birth, dimension = linked sum; zero false positives
s1 = [x for x in six if x['any_birth'] and x['dim'] is not None and x['outcome'] in ('alive', 'big', 'timed')]
p1 = [x for x in s1 if x['dim'] != x['linked_sum']]
fp6 = [x for x in s1 if x['linked_sum'] > x['largest_class'] and x['dim'] == x['largest_class']]
out['P1'] = {'held': not p1, 'settled with a birth': len(s1), 'misses': [(x['key'], x['dim'], x['largest_class'], x['linked_sum'], x['shapes']) for x in p1[:10]],
             'false positives': len(fp6), 'plus-one cases': sum(1 for x in s1 if x['linked_sum'] > x['largest_class'])}
out['six outcomes'] = dict(Counter((x['outcome'], x['dim']) for x in six).most_common())
out['six shapes'] = {str(k): v for k, v in Counter((tuple(s[0]), s[1]) for x in six for s in x['shapes']).items()}
txt = json.dumps(out, indent=1, default=str)
print(txt)
if len(sys.argv) > 2:
    Path(sys.argv[2]).write_text(txt)
