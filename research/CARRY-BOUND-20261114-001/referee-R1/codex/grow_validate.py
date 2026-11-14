"""Recheck every emitted positive bond with a different SAT solver."""
import collections
import json
import resource
import time
from grow_core import HERE, READS, read, usual, limits, unfold, Solver


def main():
    begin = time.monotonic()
    measurements = []
    for name in ('grow_results.jsonl', 'grow_halo6.jsonl', 'grow_branching.jsonl'):
        for line in read(HERE / name).splitlines():
            row = json.loads(line)
            row['source'] = name
            measurements.append(row)
    verified = []
    failures = []
    queries = 0
    for row in measurements:
        if row['status'] != 'exact':
            continue
        defs = usual(json.loads(row['key']))
        G, _ = limits(defs)
        clauses, n, roots, targets, copies, origin, boundary = unfold(
            defs, G, row['S'], row['cutoff'], row['depth'])
        support = row['witness']
        assert len(set(support)) == row['minimum']
        assert set(support) & roots and set(support) & targets
        with Solver(name='glucose42', bootstrap_with=clauses) as sat:
            def shattered(vs):
                nonlocal queries
                bad = []
                for state in range(1 << len(vs)):
                    cube = [v + 1 if (state >> j) & 1 else -(v + 1)
                            for j, v in enumerate(vs)]
                    queries += 1
                    if not sat.solve(assumptions=cube):
                        bad.append(state)
                return bad
            bad = shattered(support)
            assert bad
            deletions = [shattered([w for w in support if w != v]) for v in support]
            assert not any(deletions)
            if 'forbidden_states' in row:
                assert bad == row['forbidden_states']
        assert row['minimum'] >= row['claimed_bound']
        verified.append({'source': row['source'], 'case': row['case'], 'sha': row['sha'],
                         'depth': row['depth'], 'halo': row['halo'],
                         'minimum': row['minimum'], 'forbidden_states': bad,
                         'all_one_deleted_shattered': True})
    global_cert = json.loads(read(HERE / 'grow_global_exact.json'))
    result = {'total_direct_cells': len(measurements),
              'positive_bonds_reverified': len(verified),
              'timeouts': [{k: r[k] for k in ('source', 'case', 'sha', 'depth', 'proved_lower_bound')}
                           for r in measurements if r['status'] == 'timeout'],
              'family_count': len({r['key'] for r in measurements}),
              'independent_global_exact_depth_cases': global_cert['global_exact_depth_cases'],
              'global_exact_uses_G': False, 'counterexamples_to_claimed_bound': failures,
              'queries_alternate_solver': queries, 'rows': verified,
              'inputs': READS, 'seconds': time.monotonic()-begin,
              'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (HERE / 'grow_validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('rows', 'inputs')}))


if __name__ == '__main__':
    main()
