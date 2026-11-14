"""Separate certificate audit; never consumed by grow_search.py.

Rebuild liveness and per-call relations from the mathematics using SAT, then
check the live quotient's claimed uniform rectangular length on all growers.
This file does NOT supply any answer to the relation-free direct search.
"""
import collections
import hashlib
import itertools
import json
import resource
import time
from grow_core import ROOT, HERE, READS, rows, usual, limits, flatten, forbid, Solver


def live_positions(defs):
    live = [set() for _ in defs]
    rounds = 0
    while True:
        fresh = []
        for i, (arity, own, calls) in enumerate(defs):
            touched = set()
            for c, args in calls:
                if c == 'K':
                    touched.update(args)
                else:
                    used = live[i] if c == 'SELF' else live[c]
                    touched.update(args[j] for j in used)
            fresh.append({j for j in touched if j < arity})
        rounds += 1
        assert all(live[i] <= fresh[i] for i in range(len(defs)))
        if fresh == live:
            return live, rounds
        live = fresh


def call_pairs(size, body, G, chosen):
    clauses = []
    for j, (callee, args) in enumerate(body):
        if j == chosen:
            continue
        clauses.extend(forbid(args, {1, 2, 3, 4, 5, 6} if callee == 'K' else G[callee]))
    output = body[chosen][1]
    pairs = set()
    with Solver(name='cadical195', bootstrap_with=clauses) as sat:
        for a, b in itertools.product(range(8), repeat=2):
            cube = [j + 1 if (a >> j) & 1 else -(j + 1) for j in range(3)]
            cube += [v + 1 if (b >> j) & 1 else -(v + 1) for j, v in enumerate(output)]
            if sat.solve(assumptions=cube):
                pairs.add((a, b))
    return frozenset(pairs)


def compose(a, b):
    return frozenset((x, z) for x, y in a for yy, z in b if y == yy)


def rectangular(pairs):
    first = {x for x, y in pairs}
    second = {y for x, y in pairs}
    return len(pairs) == len(first) * len(second)


def project(state, live):
    return sum(((state >> v) & 1) << j for j, v in enumerate(live))


def main():
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    begin = time.monotonic()
    digest = rows(ROOT / 'artifacts/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/window_digest.jsonl.gz')
    grows = [r for r in digest if r['verdict'] == 'growing']
    keys = {r['key'] for r in grows}
    census = {r['key']: r for r in rows(ROOT / 'artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz') if r['key'] in keys}
    results = []
    for index, row in enumerate(grows):
        defs = usual(json.loads(row['key']))
        S = census[row['key']]['S']
        live, rounds = live_positions(defs)
        assert sorted(live[S]) == row['live_S'], row['key_sha256']
        G, history = limits(defs)
        assert G[-1] and G[S]
        size, body = flatten(defs, S)
        generators = [call_pairs(size, body, G, j) for j, (c, a) in enumerate(body) if c == S]
        ls = sorted(live[S])
        reduced = {frozenset((project(a, ls), project(b, ls)) for a, b in rel) for rel in generators}
        length_set = set(reduced)
        levels = []
        first_r = None
        for depth in range(1, row['G_r'] + 1):
            good = all(rectangular(rel) for rel in length_set)
            levels.append({'length': depth, 'products': len(length_set), 'all_rectangular': good})
            if good and first_r is None:
                first_r = depth
            if depth != row['G_r']:
                length_set = {compose(left, right) for left in length_set for right in reduced}
        assert first_r == row['G_r'], (row['key_sha256'], first_r, row['G_r'])
        # The deletion is legitimate as a lower-subtree deletion. Each reduced
        # input/output tuple has every allowed dead-coordinate lift subject
        # only to identity equalities; no descendant knot reads such positions.
        rec = {'sha': row['key_sha256'][:12], 'key': row['key'], 'S': S,
               'live_all_definitions': [sorted(x) for x in live], 'rounds': rounds,
               'r_recorded': row['G_r'], 'r_recomputed': first_r,
               'block_size': size, 'calls': len(generators), 'levels': levels,
               'usual_limit_alive': True, 'wrapper': row['wrapper']}
        results.append(rec)
        if (index + 1) % 100 == 0:
            print(json.dumps({'families': index + 1, 'seconds': round(time.monotonic()-begin, 2)}), flush=True)
    # A dead lower coordinate can be constrained above; deleting its identity
    # from an entire formula would be WRONG. Concrete matched control.
    # upper NAE(p,a,b), lower NAE(u,v,w), with p carried in an unread slot.
    clauses = [[1,2,3],[-1,-2,-3],[4,5,6],[-4,-5,-6]]
    with Solver(name='cadical195', bootstrap_with=clauses) as sat:
        actual = {state for state in range(64) if sat.solve(assumptions=[
            j + 1 if (state >> j) & 1 else -(j + 1) for j in range(6)])}
    product = {a | (b << 3) for a in (1,2,3,4,5,6) for b in (1,2,3,4,5,6)}
    assert actual == product
    assert not any((state & 7) == 0 for state in actual)
    # An unread label does not make p globally free; upper NAE is retained.
    globally_free_mutant = {a | (b << 3) for a in range(8) for b in (1,2,3,4,5,6)}
    assert actual != globally_free_mutant
    output = {'families': len(results), 'r_counts': dict(collections.Counter(r['r_recomputed'] for r in results)),
              'all_liveness_match': True, 'all_rectangular_lengths_match': True,
              'constrained_above_factor_control': True, 'global_free_mutant_rejected': True,
              'rows': results, 'inputs': READS, 'seconds': time.monotonic()-begin,
              'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (HERE / 'grow_lemma_audit.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({k: v for k, v in output.items() if k not in ('rows', 'inputs')}), flush=True)


if __name__ == '__main__':
    main()
