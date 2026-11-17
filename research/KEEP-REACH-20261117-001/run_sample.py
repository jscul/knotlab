"""Conjecture C on a fresh held-out sample (KEEP-REACH-20261117-001, the thread's own code, 2026-11-17). Sampler (fair coins, seed
'KEEP-1117-<i>'): s uniform in {1, 2, 3} automaton states, each with an output flip and two transitions uniform; r uniform in {1, 2, 3, 4}
placements, each a sorted triple of distinct slots uniform among the 3 (1 + s + s^2) slots (a word of at most two states and a child
letter or none), as in the LEVEL-REACH keys. Kept: orbits of at most four addresses (blocks). Draws continue until 40 kept draws
are alive at every depth and never forget (the advisor's power floor) or 200,000 draws. `run_sample.py mutants` instead classifies
every one-slot change of one placement of the four non-direct cases. Classified by classify.py, 60 s each. Run only after
predictions.md is committed. Writes sample_keep.jsonl or mutants_keep.jsonl, one line per kept draw."""
import json
import random
import signal
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from classify import classify  # noqa: E402

MAX_DRAWS = 200000
TARGET_NEVER = 40      # stop once this many kept draws never forget (the advisor's power floor), or at MAX_DRAWS


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def draw(i):
    rng = random.Random('KEEP-1117-%d' % i)
    s = rng.choice([1, 2, 3])
    sw = [rng.randrange(2) for _ in range(s)]
    d0 = [rng.randrange(s) for _ in range(s)]
    d1 = [rng.randrange(s) for _ in range(s)]
    slots = 3 * (1 + s + s * s)
    placements = [sorted(rng.sample(range(slots), 3)) for _ in range(rng.choice([1, 2, 3, 4]))]
    return [s, sw, d0, d1, placements]


def mutants(key):
    """Every one-slot change of one placement of a key (the advisor's mutations of the four non-direct cases)."""
    s, sw, d0, d1, placements = key
    slots = 3 * (1 + s + s * s)
    for pi, p in enumerate(placements):
        for j in range(3):
            for v in range(slots):
                q = list(p)
                if v in q:
                    continue
                q[j] = v
                yield [s, sw, d0, d1, [sorted(q) if k == pi else list(x) for k, x in enumerate(placements)]]


def run(stream, path):
    never = 0
    with open(path, 'w') as f:
        for i, key in stream:
            t0 = time.time()
            signal.alarm(60)
            try:
                c = classify(key)
            except Timeout:
                c = dict(small_orbits=True, timeout=True)
            except Exception as e:  # a draw the block code cannot build (recorded, not dropped)
                c = dict(small_orbits=None, error=type(e).__name__ + ': ' + str(e)[:60])
            signal.alarm(0)
            if c.get('small_orbits') is False:
                continue
            c.update(index=i, key=key, seconds=round(time.time() - t0, 2))
            f.write(json.dumps(c) + '\n')
            f.flush()
            if c.get('small_orbits') and c.get('alive_every_depth') and c.get('r_all') is None and not c.get('timeout'):
                never += 1
            yield never


signal.signal(signal.SIGALRM, _alarm)
if sys.argv[1:] == ['mutants']:
    import gzip
    ROOT = HERE.parents[1]
    four = ['8db5da810c00', 'a9a1c941de1a', 'bace53f8f952', 'ca1efb37ad88']
    keys = {}
    for line in gzip.open(ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt'):
        r = json.loads(line)
        if r['case'][:12] in four:
            keys[r['case'][:12]] = r['key']
    stream = ((f'{c}-{m}', k) for c in four for m, k in enumerate(mutants(keys[c])))
    for _ in run(stream, HERE / 'mutants_keep.jsonl'):
        pass
else:
    for never in run(((i, draw(i)) for i in range(MAX_DRAWS)), HERE / 'sample_keep.jsonl'):
        if never >= TARGET_NEVER:
            break
