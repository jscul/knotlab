"""Direct unfolded-CNF bond minima, including every recursive target type.

Reuse is limited to the previous referee's fresh DirectSearch and input-language
unfolder. No per-call relation, composition, semigroup or producer code enters
this computation. Limit boundaries use only the permitted dlang input module.
"""
import argparse
import hashlib
import importlib.util
import json
import resource
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'research/FREE-TARGET-20261114-001/referee-R1/codex/direct_bonds.py'
spec = importlib.util.spec_from_file_location('previous_direct_referee', SOURCE)
direct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(direct)


def verify(clauses, n, support):
    """Separate SAT-solver backend checks the complete allowed projection."""
    allowed = []
    with direct.Solver(name='glucose42', bootstrap_with=clauses) as sat:
        for state in range(1 << len(support)):
            assumptions = [(v + 1) if state >> j & 1 else -(v + 1)
                           for j, v in enumerate(support)]
            if sat.solve(assumptions=assumptions):
                allowed.append(state)
    deletions = []
    for drop in range(len(support)):
        keep = [j for j in range(len(support)) if j != drop]
        projected = {sum(((a >> j) & 1) << p for p, j in enumerate(keep))
                     for a in allowed}
        deletions.append(len(projected) == 1 << len(keep))
    assert 0 < len(allowed) < 1 << len(support) and all(deletions)
    return {'allowed_states': allowed, 'every_deletion_full': deletions,
            'backend': 'glucose42 (search backend cadical195)'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ids', default='f25a8e17968d,3fe70047c198,f3c4843e45fa,ec647c80edb0,c6cbc657bedb')
    parser.add_argument('--depths', default='1,2,3,4,6,10')
    parser.add_argument('--extras', default='1,2')
    parser.add_argument('--seconds', type=float, default=20)
    parser.add_argument('--max-size', type=int, default=5)
    parser.add_argument('--output', default='direct_other_targets.jsonl')
    args = parser.parse_args()
    inventory = json.loads((OUT / 'target_inventory.json').read_text())['families']
    ids = args.ids.split(',')
    selected = [next(r for r in inventory if r['key_sha256'].startswith(i)) for i in ids]
    path = OUT / args.output
    assert not path.exists(), 'refuse overwrite: use a fresh output name'
    total_start = time.monotonic()
    for family in selected:
        raw = json.loads(family['key'])
        defs, limits = direct.usual_and_limit(raw)
        for s in map(int, args.depths.split(',')):
            for h in map(int, args.extras.split(',')):
                started = time.monotonic()
                clauses, n, roots, targets, copies, origins = direct.unfold(defs, limits, s + h, s)
                # Stop before exponential construction exhausts task resources.
                assert n < 15000 and len(clauses) < 100000
                pool = roots | targets
                search = direct.DirectSearch(clauses, n, roots, targets,
                                             seconds=args.seconds,
                                             preferred_pools=[pool])
                row = {'key': family['key'], 'key_sha256': family['key_sha256'],
                       'S': family['S'], 'main': family['main'], 'r': family['r'],
                       's': s, 'h': h, 'cutoff': s+h,
                       'variables': n, 'clauses': len(clauses), 'targets': len(targets),
                       'target_definitions': sorted({origins[t]['definition'] for t in targets}),
                       'limits': {str(i): [j for j, b in enumerate(g) if b] for i, g in limits.items()},
                       'unshifted_bound': 2 + s // family['r'],
                       'S_only_corrected_bound': 2 + (s if family['main_equals_S'] else s-1) // family['r']}
                try:
                    answer = search.run(args.max_size, seeds=30)
                    row['status'] = 'exact_minimum' if answer.get('minimum') else 'lower_sizes_excluded'
                    row.update(answer)
                    if answer.get('minimum'):
                        support = answer['witness']
                        row['witness_detail'] = [{'variable': v,
                            'is_top_port': v in roots, 'is_target': v in targets,
                            'origin': origins.get(v, {'top_port': v})} for v in support]
                        row['verification'] = verify(clauses, n, support)
                        row['below_S_certificate_numeric_bound'] = answer['minimum'] < row['S_only_corrected_bound']
                except direct.SearchTimeout:
                    row['status'] = 'timeout'
                    row['completed_lower_sizes'] = list(search.by_size)
                finally:
                    row['sat_queries'] = search.queries
                    row['seconds'] = time.monotonic() - started
                    row['peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                    search.close()
                with path.open('a') as f:
                    f.write(json.dumps(row, sort_keys=True) + '\n')
                print(json.dumps({k: row.get(k) for k in ('key_sha256','s','h','status','minimum','variables','seconds','below_S_certificate_numeric_bound')}), flush=True)
    print(json.dumps({'total_seconds': time.monotonic()-total_start,
                      'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}), flush=True)


if __name__ == '__main__':
    main()
