"""Count within r unit transfers on the proposed finite roster, without growing it."""

from collections import Counter
from functools import lru_cache
from hashlib import sha256
from itertools import product
import json

import numpy as np


def compositions(total, length):
    if length == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in compositions(total - first, length - 1):
            yield (first, *tail)


def count_vector(distances, radius):
    relevant = distances[distances <= radius]
    return tuple(int(n) for n in np.cumsum(np.bincount(relevant, minlength=radius + 1)))


@lru_cache(maxsize=None)
def describe(m, k, t, radius, attachments=True):
    """m unbounded entries, k binary entries, fixed total t-1, m possible attachments."""
    s = t - 1
    core = []
    for bits in product((0, 1), repeat=k):
        for ordered in compositions(s - sum(bits), m):
            core.append(ordered + bits)
    arr = np.array(core, dtype=np.int32)
    # Permutations of the m entries, and separately of the k bits, preserve steps.
    types = Counter(tuple(sorted(x[:m])) + tuple(sorted(x[m:])) for x in core)
    hist = Counter()
    for key, multiplicity in types.items():
        x = np.array(key, dtype=np.int32)
        # All tuples have the same sum. Each transfer removes exactly one unit
        # of surplus, and moving surplus to deficit stays inside the bounds.
        distances = np.maximum(x - arr, 0).sum(axis=1)
        if attachments:
            distances = np.concatenate((distances, 1 + s - x[:m]))
        hist[count_vector(distances, radius)] += multiplicity
    if attachments:
        distances = np.concatenate((1 + s - arr[:, 0], [0] + [s + 2] * (m - 1)))
        hist[count_vector(distances, radius)] += m
    vectors = [v for v, n in sorted(hist.items()) for _ in range(n)]
    digest = sha256(json.dumps(vectors, separators=(',', ':')).encode('ascii')).hexdigest()
    degree = Counter()
    for v, n in hist.items():
        degree[v[1] - 1] += n
    return {
        'members': len(vectors),
        'pairs': sum(d * n for d, n in degree.items()) // 2,
        'greatest_counts': list(map(max, zip(*hist))),
        'part_sizes': [len(vectors)],
        'degree_histogram': {str(d): n for d, n in sorted(degree.items())},
        'reach_sha256': digest,
    }
