"""Sparse-level counterexample attempts, using fresh explicit finite keys.

The stall family can place arbitrarily many levels between selected advances;
the minimum over all covered targets then uses a carried root and remains 3.
The fixed-lag family gives a long staircase, but its lag is fixed, not growing.
No asymptotic conclusion is promoted from these finite direct checks.
"""
import hashlib
import json
import resource
import sys
import time
from pathlib import Path
from growth_core import ROOT, HERE, old, sources, verify
from growth_search import cell

def fixed_lag(q):
    return [[q, 2, [['K', [0, q, q + 1]],
                    ['SELF', list(range(1, q)) + [q]]]]]

def reduced_strand(q, depth, halo_steps=2):
    """Direct root-bearing constraint component of the fixed-lag unfolding.

    Each residue of copy depth modulo q is a separate component. At depth s,
    both target own distinctions belong to residue s mod q. Other components
    are products and cannot occur in a minimal non-shattered set with them.
    """
    h = depth // q + 1
    steps = h + halo_steps
    clauses = []
    for j in range(steps):
        parent = 0 if j == 0 else 2 * j - 1
        u, w = 2 * j + 1, 2 * j + 2
        clauses.extend(([parent + 1, u + 1, w + 1],
                        [-(parent + 1), -(u + 1), -(w + 1)]))
    n = 1 + 2 * steps
    targets = {2 * h - 1, 2 * h}
    search = old.DirectSearch(clauses, n, {0}, targets, seconds=45,
                              preferred_pools=[set(range(1 + 2 * h))])
    begin = time.monotonic()
    try:
        answer = search.run(max_size=h + 2, seeds=20)
        status = 'exact_reduced_prefix' if answer.get('minimum') else 'lower_sizes_only_reduced_prefix'
        if answer.get('witness'):
            check = verify(clauses, answer['witness'], {0}, targets)
        else:
            check = None
    except old.SearchTimeout:
        answer = {'minimum': None, 'by_size': search.by_size}
        check = None
        status = 'timeout'
    finally:
        search.close()
    return {'arity': q, 'absolute_depth': depth, 'S_call_length': depth,
            'strand_residue': depth % q, 'root_to_target_constraints': h,
            'size_expected_from_pendant_count': h + 2,
            'variables': n, 'halo_steps': halo_steps, 'status': status,
            'answer': answer, 'verification': check,
            'seconds': time.monotonic() - begin,
            'global_exact': False,
            'scope': 'all members of explicit causal strand through target plus halo; other q-1 strands factor independently'}

def main():
    begin = time.monotonic()
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    stall_raw = [[3, 2, [['K', [1, 3, 4]],
                        ['SELF', [0, 1, 3]], ['SELF', [0, 3, 2]]]]]
    key = json.dumps(stall_raw, separators=(',', ':'))
    stall = {'key': key, 'wrapper': False, 'c': 2, 'verdict': 'synthetic attempt'}
    stall_rows = [cell(stall, {'S': 0, 's_block_size': 5}, s, s + 1,
                       20, 3, 'stall_then_advance') for s in [1, 2, 4, 6, 8]]
    assert all(r['minimum'] == 3 and r['global_exact'] for r in stall_rows)
    lag_rows = []
    q = 8
    lagkey = json.dumps(fixed_lag(q), separators=(',', ':'))
    lagfamily = {'key': lagkey, 'wrapper': False, 'c': 1, 'verdict': 'synthetic attempt'}
    # Complete full-prefix search remains inexpensive at short depths.
    for s in [1, 7, 8, 15, 16]:
        lag_rows.append(cell(lagfamily, {'S': 0, 's_block_size': q + 2},
                             s, s + 1, 30, 5, 'fixed_lag_8'))
    reduced = [reduced_strand(q, s) for s in [7, 8, 16, 24, 32]]
    result = {'scope': 'READ independent exploratory counterexample attempts',
              'stall_key': key, 'stall_key_sha256': hashlib.sha256(key.encode()).hexdigest(),
              'stall_rows': stall_rows,
              'stall_failure_reason': 'A SELF letter can retain b for any number of levels; its descendant has the pendant NAE(b,u,w), so minimizing over covered targets gives a 3-bond rather than intermediate growth.',
              'fixed_lag_key': lagkey,
              'fixed_lag_key_sha256': hashlib.sha256(lagkey.encode()).hexdigest(),
              'fixed_lag_scope_limit': 'arity q=8 is an explicitly broader diagnostic outside the three-port census grammar; it cannot refute the in-scope theorem',
              'fixed_lag_full_prefix_rows': lag_rows,
              'fixed_lag_reduced_rows': reduced,
              'fixed_lag_failure_reason': 'The delay is the fixed arity q=8. Each residue is a one-link NAE chain; crossing another link needs its pendant w. The resulting fixed-width staircase has h=floor(s/8)+1 constraints, rather than increasingly long square-depth gaps.',
              'counterexample_found': False,
              'nonclaims': ['No theorem is inferred from capped finite support search.',
                            'The reduced-strand minima exclude all smaller supports only in the stated explicit strand prefix.',
                            'These examples do not exhaust possible slow-growth constructions.'],
              'sources_sha256': sources(),
              'imported_growth_search_sha256': hashlib.sha256((HERE / 'growth_search.py').read_bytes()).hexdigest(),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'seconds': time.monotonic() - begin,
              'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              'python': sys.executable}
    (HERE / 'growth_handdesigned.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'stall': [r['minimum'] for r in stall_rows],
                      'fixed_lag_full': [(r['absolute_depth'], r.get('minimum'), r['status']) for r in lag_rows],
                      'fixed_lag_reduced': [(r['absolute_depth'], r['answer'].get('minimum'), r['status']) for r in reduced],
                      'seconds': result['seconds'], 'peak_rss_kib': result['peak_rss_kib']}))

if __name__ == '__main__':
    main()
