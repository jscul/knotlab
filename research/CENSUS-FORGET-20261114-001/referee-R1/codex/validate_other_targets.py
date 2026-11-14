"""Independent truth-table controls and retained witness rechecks."""
import hashlib
import importlib.util
import itertools
import json
import random
import resource
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('new_direct_audit', OUT / 'direct_other_targets.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
direct = audit.direct


def truth_minimum(clauses, n, roots, targets):
    states = [s for s in range(1 << n)
              if all(any(bool(s >> (abs(x)-1) & 1) == (x > 0) for x in c)
                     for c in clauses)]
    assert states

    def full(vs):
        return len({sum(((s >> v) & 1) << j for j, v in enumerate(vs))
                    for s in states}) == 1 << len(vs)

    for k in range(2, n+1):
        for support in itertools.combinations(range(n), k):
            if not set(support) & roots or not set(support) & targets:
                continue
            if not full(support) and all(full([w for w in support if w != v]) for v in support):
                return k
    return None


def main():
    started = time.monotonic()
    controls = direct.controls()
    rng = random.Random(818009)
    truth_rows = []
    for i in range(16):
        n = 5 + i % 3
        clauses = []
        for _ in range(1 + i % 5):
            edge = rng.sample(list(range(1, n+1)), 3)
            clauses.extend([edge, [-v for v in edge]])
        expected = truth_minimum(clauses, n, {0}, {n-1})
        search = direct.DirectSearch(clauses, n, {0}, {n-1}, seconds=10)
        try:
            actual = search.run(n, seeds=10)['minimum']
        finally:
            search.close()
        assert actual == expected
        truth_rows.append({'case': i, 'n': n, 'clauses': clauses,
                           'truth_minimum': expected, 'sat_minimum': actual})
    rows = []
    for name in ('direct_other_targets.jsonl', 'direct_other_targets_odd.jsonl',
                 'direct_delayed_S.jsonl'):
        for row in map(json.loads, (OUT / name).read_text().splitlines()):
            defs, limits = direct.usual_and_limit(json.loads(row['key']))
            clauses, n, roots, targets, copies, origins = direct.unfold(defs, limits, row['cutoff'], row['s'])
            assert row['variables'] == n and row['targets'] == len(targets)
            assert row['minimum'] == 3
            support = row['witness']
            assert set(support) & roots and set(support) & targets
            audit.verify(clauses, n, support)
            # This exhausts every possible size-two endpoint bond in the
            # infinite system: no third member can lie outside the cutoff.
            with direct.Solver(name='glucose42', bootstrap_with=clauses) as sat:
                pair_count = 0
                for a in roots:
                    for b in targets:
                        for x, y in itertools.product((False, True), repeat=2):
                            assert sat.solve(assumptions=[a+1 if x else -a-1,
                                                          b+1 if y else -b-1])
                        pair_count += 1
            rows.append({'family_sha256': row['key_sha256'], 's': row['s'], 'h': row['h'],
                         'endpoint_pairs_exhausted': pair_count,
                         'witness_projection_verified': True,
                         'global_minimum': 3})
    result = {'passed': True, 'search_controls': controls, 'fresh_truth_controls': truth_rows,
              'retained_points': rows, 'point_count': len(rows),
              'all_global_minima_are_three': True,
              'scope_of_exactness': 'All depth-s target variables occur explicitly. Every singleton is free by nonempty complement symmetry. Every root/target pair is tested in the exact boundary projection. The three-member witness proves the global minimum, even when arbitrary deeper support members are admitted.',
              'seconds': time.monotonic() - started,
              'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (OUT / 'direct_validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('retained_points','search_controls','fresh_truth_controls')}, indent=2))


if __name__ == '__main__':
    main()
