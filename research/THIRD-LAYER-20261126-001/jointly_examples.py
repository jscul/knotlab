"""jointly_examples.py OUT.jsonl: the stricter test (jointly.judge) on every binding example the built-binding referee
found by its search over carriers of any shape (unrestricted_sampled.json, unrestricted_heldout.json): each stage as
recorded, its carriers and, where given, its carriers of new distinctions only."""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import jointly as JY
R = ROOT / 'research/BUILT-BINDING-20261126-001/referee-R1'
with open(sys.argv[1], 'w') as f:
    for fn in ('unrestricted_heldout.json', 'unrestricted_sampled.json'):
        d = json.load(open(R / fn))
        for reading, exs in d['examples'].items():
            for e in exs:
                st = tuple(tuple(k) for k in (json.loads(e['knots']) if isinstance(e['knots'], str) else e['knots']))
                sup = json.loads(e['supports']) if isinstance(e['supports'], str) else e['supports']
                rec = {'file': fn, 'found under': reading, 'start': e['start'], 'round': e['round'], 'supports': JY.judge(st, sup)}
                if 'new distinctions only' in e:
                    nd = json.loads(e['new distinctions only']) if isinstance(e['new distinctions only'], str) else e['new distinctions only']
                    rec['new'] = JY.judge(st, nd)
                f.write(json.dumps(rec) + '\n'); f.flush()
                tag = 'SHORT' if reading == 'shortest' else 'UPTO5'
                print(e['start'], e['round'], reading, 'jointly read', sum(r['a sum of single-knot facts'] for r in rec['supports'][tag]), 'of', len(sup),
                      '| class facts', sum(r['class fact'] for r in rec['supports'][tag]), flush=True)
