"""Referee R1, item (d) extra: fbb5c3cad5db... (constant 3; the second constant-3 that the depth-9 readout has above 3 from top
level 2 at s = 5 and 6). With my oracle (referee_check_s5.run): ties from level 2 and an exhaustive search for three-member
bonds meeting levels 2 and 7 (s = 5) at N = 9 (r = 2) and N = 10 (r = 3). Writes referee_fbb5.json."""
import json
import sys
import time

sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/DIRECT-REACH-20261115-001/referee-R1')
from referee_pattern import load_population, HERE  # noqa: E402
from referee_check_s5 import run  # noqa: E402

pop = {d['case'][:12]: d for d in load_population()}
res = {}
for N in (9, 10):
    t = time.time()
    r = run(pop['fbb5c3cad5db']['key'], N=N, k=2, s=5)
    r['seconds'] = time.time() - t
    res['N=%d' % N] = r
    print(N, json.dumps(r)[:500], flush=True)
json.dump(dict(case=pop['fbb5c3cad5db']['case'], k=2, s=5, results=res), open(HERE / 'referee_fbb5.json', 'w'), indent=1)
