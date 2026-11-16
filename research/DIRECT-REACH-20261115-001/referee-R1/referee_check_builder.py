"""Referee R1: my builder against the census builder (pattern.py, CALLED HERE ONLY AS THE THING UNDER TEST) and my population
against the study's population_D (also called only as the thing under test). Writes referee_builder.json."""
import json
import sys
import time

import numpy as np

sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/DIRECT-REACH-20261115-001/referee-R1')
from referee_pattern import Aut, load_population, HERE, ROOT, STUDY  # noqa: E402

sys.path.insert(0, str(STUDY / 'exploratory'))
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
from pattern import pattern  # noqa: E402  (under test)
from window_types import population_D  # noqa: E402  (under test)

t0 = time.time()
mine = load_population()
theirs = population_D()
pop_same = [(d['case'], d['key']) for d in mine] == [(c, k) for c, k, _, _ in theirs]
counts = {}
for d in mine:
    counts[d['profile']] = counts.get(d['profile'], 0) + 1
bad = []
for d in mine:
    A = Aut(d['key'])
    for N in (1, 4, 7):
        a = A.knots(N)
        b = pattern(d['key'], N)
        if not (a.shape == b.shape and np.array_equal(a, b)):
            bad.append((d['case'][:12], N, a.shape, b.shape))
out = dict(population_size=len(mine), counts=counts, population_equal_to_study=pop_same,
           builder_mismatches=bad, depths=[1, 4, 7], seconds=time.time() - t0)
json.dump(out, open(HERE / 'referee_builder.json', 'w'), indent=1)
print(out)
