"""Recount exact hiding from side-table row spans. Count available local explanations."""
import argparse
import itertools
import json
import math
import random
import time
from collections import Counter, defaultdict
from functools import cache
from fractions import Fraction
from pathlib import Path

import numpy as np

from side_catalogue import CATALOGUE
from c_arguments import has_common_group_weighting
from parity_scores import check_hiding, exact_score

SWAP = [((w & 4) | ((w & 1) << 1) | ((w & 2) >> 1)) for w in range(8)]
FLIP = [7-w for w in range(8)]
RENAME = [list(range(8)), SWAP, FLIP, [7-w for w in SWAP]]


def primitive(row):
    factor = math.gcd(*row)
    if not factor:
        return row
    if next(x for x in row if x) < 0:
        factor = -factor
    return tuple(x // factor for x in row)


@cache
def row_basis(rows):
    basis = {}
    for v in rows:
        for col, b in sorted(basis.items()):
            if v[col]:
                v = primitive(tuple(b[col]*y - v[col]*x for x, y in zip(b, v)))
        if any(v):
            j = next(i for i, x in enumerate(v) if x)
            basis[j] = primitive(v)
    for j, b in sorted(basis.items(), reverse=True):
        for col in [i for i in basis if i < j]:
            v = basis[col]
            if v[j]:
                basis[col] = primitive(tuple(b[j]*y-v[j]*x for x, y in zip(b, v)))
    return tuple(b for _, b in sorted(basis.items()))


def wedge(a, b):
    return tuple(a[i]*b[j]-a[j]*b[i] for i, j in itertools.combinations(range(len(a)), 2))


def summarise(table):
    basis = row_basis(tuple(sorted(set(tuple(int(i) for i in row) for row in table))))
    # Each old local word admits two fresh bits when its presented values differ.
    old_weights = [[1 + int((w >> 2) != (w >> bit & 1)) for w in range(8)] for bit in (1, 0)]
    totals = np.array(old_weights, dtype=np.int64) @ table
    w = primitive(wedge(*totals.tolist()))
    support = sum(1 << i for i, x in enumerate(totals[0]) if x)
    symmetric = np.array_equal(table[SWAP], table)
    return basis, w, support, symmetric


def classify(path, pilot):
    with np.load(path) as saved:
        tables = saved['T'].astype(np.int64)
    ordered = '_k3_' in path.name
    if pilot:
        idx = random.Random(20261126).sample(range(len(tables)), min(256, len(tables)))
        tables = tables[idx]
    seen, types = set(), Counter()
    representatives = defaultdict(list)
    attaining = None
    for t in tables:
        divisor = np.gcd.reduce(t.ravel())
        if divisor == 0:
            continue
        t = t // divisor
        key = t.tobytes() if ordered else min(t[p].tobytes() for p in RENAME)
        if key not in seen:
            seen.add(key)
            group = summarise(t)
            types[group] += 1
            representatives[group].append(t)
            if attaining is None:
                m = t @ t.T
                if check_hiding(m) and exact_score(m) == 2:
                    attaining = t.tolist()
    spans = sorted(set(g[0] for g in types))
    weights = sorted(set(g[1] for g in types))
    s_index = {s: i for i, s in enumerate(spans)}
    w_index = {w: i for i, w in enumerate(weights)}
    # Cauchy–Binet: the images of two weight vectors are proportional
    # iff each pair of basis rows has zero pairing with their exterior product.
    W = np.array(weights, dtype=np.int64).T
    hides = np.ones((len(spans), len(weights)), bool)
    largest = 0
    for i, span in enumerate(spans):
        tests = [wedge(a, b) for a, b in itertools.combinations(span, 2)]
        if tests:
            upper = max(sum(abs(int(z)) for z in row) for row in tests) * int(np.max(np.abs(W)))
            largest = max(largest, upper)
            arithmetic = np.int64 if upper < 2**62 else object
            hides[i] = np.all(np.array(tests, dtype=arithmetic) @ W == 0, axis=0)
    groups = list(types)
    S = np.array([s_index[g[0]] for g in groups])
    V = np.array([w_index[g[1]] for g in groups])
    mask = np.array([g[2] for g in groups])
    size = np.array([types[g] for g in groups], dtype=np.int64)
    low = np.array([len(g[0]) <= 2 for g in groups])
    swap = np.array([g[3] for g in groups])
    proportional = np.array([not any(g[1]) for g in groups])
    pairs = hidden = empty = certified = 0
    remaining = Counter()
    largest_direct = Fraction(0)
    exceeding = 0
    for i in range(len(groups)):
        count = size[i]*size.copy()
        if not ordered:
            count[:i] = 0
            count[i] = size[i]*(size[i]+1)//2
        valid = (mask & mask[i]) != 0
        mutual = valid & hides[S[i], V] & hides[S, V[i]]
        local = low | low[i] | swap | swap[i] | (proportional & proportional[i])
        for j in np.flatnonzero(mutual & ~local & (count != 0)):
            left = representatives[groups[i]]
            right = representatives[groups[j]]
            for k, a in enumerate(left):
                first = k if i == j and not ordered else 0
                for b in right[first:]:
                    m = a @ b.T
                    assert check_hiding(m)
                    if has_common_group_weighting(m) or has_common_group_weighting(m.T):
                        remaining["proportional_record_groups"] += 1
                    elif len(row_basis(tuple(sorted(set(map(tuple, m.tolist())))))) <= 2:
                        remaining["rank_at_most_two"] += 1
                    else:
                        score = exact_score(m)
                        remaining["direct_exact_scores"] += 1
                        largest_direct = max(largest_direct, score)
                        exceeding += int(score > 2)
        pairs += int(count.sum())
        hidden += int(count[mutual].sum())
        empty += int(count[~valid].sum())
        certified += int(count[mutual & local].sum())
    assert sum(remaining.values()) == hidden-certified
    if not pilot:
        assert attaining is not None
    return dict(pool=path.stem[6:], paired_tables=len(seen), types=len(groups), attempted=pairs,
                empty=empty, hidden=hidden, local_by_simple_certificate=certified,
                hidden_without_simple_certificate=hidden-certified, remaining=dict(remaining),
                direct_scores_above_two=exceeding, largest_direct_score=str(largest_direct) if remaining["direct_exact_scores"] else None,
                self_pair_attaining_two=attaining, integer_bound=largest)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pilot', action='store_true')
    args = p.parse_args()
    start = time.process_time()
    control = np.array(json.loads((CATALOGUE / "reference_final.json").read_text())["M"], dtype=np.int64)
    assert check_hiding(control) and exact_score(control) == Fraction(20, 9)
    rows = [classify(f, args.pilot) for f in sorted(CATALOGUE.glob('sides_*.npz'))]
    print(json.dumps(dict(results=rows, process_seconds=time.process_time()-start), indent=2))
