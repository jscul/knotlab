import json, sys, time, signal
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import stagelib as SL
res = json.load(open(HERE / 'grown_long.json'))
class TO(Exception): pass
def handler(*a): raise TO()
signal.signal(signal.SIGALRM, handler)
out = []
for i, r in enumerate(res):
    c = r['counts'] or []
    row = {'i': i, 'n': len(r['sizes'])}
    for s in range(0, 5):
        if s + 2 >= len(c):
            break
        signal.alarm(120)
        try:
            status, pred = SL.stage_rule(r['sizes'], [tuple(x) for x in r['edges']], s, len(c) - s - 1)
        except TO:
            status, pred = 'timeout', None
        signal.alarm(0)
        if pred is not None:
            tail = c[s + 1:]
            fd = next((k for k in range(len(tail)) if pred[k] != tail[k]), None)
            row[s] = (status, 'equal' if fd is None else f'differs at round {s + 1 + fd}')
            if fd is None:
                break
        else:
            row[s] = (status,)
    out.append(row)
    print(row, flush=True)
json.dump(out, open(HERE / 'stage_pilot.json', 'w'))
