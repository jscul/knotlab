"""Plain exhaustive allowed-state enumeration control for N=4 tie classes."""
import itertools
import random
import time
from reuse import pattern
from ties import SignedUnionFind, compute_ties


def random_key(index):
    rng = random.Random(2026111501000 + index)
    s = rng.randrange(1, 4)
    sw = [rng.randrange(2) for _ in range(s)]
    d0 = [rng.randrange(s) for _ in range(s)]
    d1 = [rng.randrange(s) for _ in range(s)]
    terms = range(3 * (1 + s + s*s))
    placements = {tuple(sorted(rng.sample(terms, 3))) for _ in range(rng.randrange(4, 13))}
    return [s, sw, d0, d1, sorted(placements)]


def enumerate_states(K, nvars):
    """Exhaust all assignments; collapse only fully unconstrained completions.

    Each completion subcube is checked for all its assignments at once: every
    knot already has two fixed, different values, so all remaining bits are
    free. Its cardinality and every pair's possible parities are exact.
    No SAT solver, samples, or producer's tie algorithm is used here.
    """
    pairs = list(itertools.combinations(range(nvars), 2))
    possible = [0] * len(pairs)
    state = [-1] * nvars
    count = cubes = 0

    def visit(knots):
        nonlocal count, cubes
        pending, degrees = [], [0] * nvars
        for knot in knots:
            values = {state[v] for v in knot if state[v] != -1}
            if len(values) == 2:
                continue
            free = [v for v in knot if state[v] == -1]
            if not free:
                return
            pending.append(knot)
            for v in free:
                degrees[v] += 1
        if not pending:
            free_count = state.count(-1)
            count += 1 << free_count
            cubes += 1
            for i, (u, v) in enumerate(pairs):
                if state[u] == -1 or state[v] == -1:
                    possible[i] = 3
                else:
                    possible[i] |= 1 << (state[u] ^ state[v])
            return
        v = max(range(nvars), key=lambda v: degrees[v])
        for value in (0, 1):
            state[v] = value
            visit(pending)
        state[v] = -1

    visit([tuple(map(int, row)) for row in K])
    if not count:
        return {'verdict': 'undefined_dead_union', 'classes': [], 'states': 0, 'completion_subcubes': 0}
    # Independent construction of classes directly from all pair parity sets.
    classes, signs, seen = [], [], set()
    relation = {(u, v): mask for (u, v), mask in zip(pairs, possible)}
    for u in range(nvars):
        if u in seen:
            continue
        members = [u] + [v for v in range(u+1, nvars) if relation[u, v] in (1, 2)]
        seen.update(members)
        if len(members) > 1:
            classes.append(members)
            signs.append([0] + [int(relation[u, v] == 2) for v in members[1:]])
    return {'verdict': 'complete', 'classes': classes, 'class_signs': signs,
            'states': count, 'completion_subcubes': cubes}


def run_one(index, work, store):
    start = time.monotonic()
    key = random_key(index)
    K = pattern.pattern(key, 4)
    truth = enumerate_states(K, 31)
    actual = compute_ties(K, 31, work, f'G-tie-{index}', store=store)
    passed = actual['verdict'] == truth['verdict'] and actual['classes'] == truth['classes']
    if truth['verdict'] == 'complete':
        passed &= actual['class_signs'] == truth['class_signs']
    return {'gate': 'G-tie', 'index': index, 'key': key, 'N': 4,
            'passed': bool(passed), 'truth': truth, 'actual': actual,
            'seconds': time.monotonic()-start}
