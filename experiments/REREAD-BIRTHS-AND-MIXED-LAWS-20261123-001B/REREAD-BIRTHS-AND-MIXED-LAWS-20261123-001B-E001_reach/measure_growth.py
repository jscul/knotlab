"""Size survey of the growth (no tables): for every founder start, grow by the recorded operator (wrapper placement) and
record distinctions per stage, births per round and newborns.  Used to plan the runs of grow_t1.py; writes
growth_survey.json.  usage: timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402

t0 = time.time()
targets = {t['tid']: t for t in c.load_targets()}
starts = [json.loads(l) for l in (c.ART / 'starts.jsonl').open()]
out = Counter()
stages = Counter()
newb = Counter()
worst = []
for s in starts:
    ks = targets[s['tid']]['knots']
    stars, laws, names, obs, sub = c.start_stars(ks, s['mask'])
    h = c.grow(stars, 'nae')
    out[h['outcome']] += 1
    stages[len(h['n_at'])] += 1
    n = h['n_at'][-1] - h['n_at'][0]
    newb[n] += 1
    worst.append((h['D_at'][-1], n, s['tid'], s['mask']))
worst.sort(reverse=True)
res = dict(starts=len(starts), outcomes=dict(out), stages_per_history=dict(stages),
           newborns=dict(sorted(newb.items())), largest=worst[:20], seconds=round(time.time() - t0, 1))
(c.ART / 'growth_survey.json').write_text(json.dumps(res, indent=1))
print(json.dumps(res))
