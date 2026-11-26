"""Finite controls for the ring character, a nonzero pinning and a proposed parity test."""
import argparse
from collections import Counter
from itertools import islice, product
import json
import os
from pathlib import Path
import subprocess
import sys

from measure import combinations_of, incidence, kernel, moves_through, parity
from starts import grow, ring

HERE = Path(__file__).resolve().parent


def forgetting(allowed):
    clauses = []
    for state in product(range(2), repeat=3):
        if state not in allowed:
            clauses.append(' '.join(('~' if value else '') + name for value, name in zip(state, 'ABc')))
    cmd = [sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', ';'.join(clauses),
           '--loops', 'A', 'B', '--contact', 'c', '--erasure', 'forgetting', '--json']
    env = dict(os.environ, PYTHONPATH=str(HERE.parents[2] / 'tools'))
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)
    return json.loads(result.stdout)


def check(pilot):
    knots = grow(ring(5))
    names, _, laws, _ = incidence(knots, False)
    old = sum(1 << names.index(d) for d in range(5))
    # Pin the two loose distinctions of one new knot to one, all other loose ones to zero.
    holders = Counter(d for row in knots for d in row)
    loose = sum(1 << j for j, d in enumerate(names) if holders[d] == 1)
    chosen = [d for d in knots[-1] if holders[d] == 1]
    assert len(chosen) == 2
    pins = sum(1 << names.index(d) for d in chosen)
    assert all(parity(pins, law) == 0 for law in laws)
    assert all(parity(old, law) == 0 for law in laws)
    states = combinations_of(kernel(laws, len(names)))
    if pilot:
        states = islice(states, 256)
    free = Counter()
    sliced = Counter()
    for state in states:
        s = parity(state, old)
        assert parity(state ^ old, old) == 1 - s
        free[s] += 1
        if state & loose == pins:
            sliced[s] += 1
    out = dict(free_counts_by_old_parity=free, nonzero_pins=chosen, pinned_counts_by_old_parity=sliced)
    names_p, pairs_p, _, adj_p = incidence(knots, True)
    moves, _ = moves_through(pairs_p, adj_p)
    old_p = sum(1 << names_p.index(d) for d in range(5))
    assert all(not parity(old_p, w) for w in moves)
    tied_pair = {(a,a,b) for a,b in product(range(2), repeat=2)}
    whole_parity = {(a,b,a^b) for a,b in product(range(2), repeat=2)}
    out['tied_pair_control'] = forgetting(tied_pair)
    assert out['tied_pair_control']['loss_on_erasure'] is False
    if not pilot:
        assert free == {0:16384, 1:16384} and sliced == {0:32, 1:32}
        out['whole_parity_control'] = forgetting(whole_parity)
        assert out['whole_parity_control']['is_knot'] is True
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pilot', action='store_true')
    print(json.dumps(check(p.parse_args().pilot), indent=1))
