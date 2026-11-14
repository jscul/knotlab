"""Direct unfolded-CNF attacks on growth; exact-prefix and global are separate.

Only the eight consecutive-triple shapes obtain the stated global closure.
Every other row explicitly retains its finite member universe and time caps.
"""
import argparse
import gzip
import hashlib
import json
import resource
import sys
import time
from pathlib import Path
from growth_core import ROOT, HERE, old, read, verify, sources

def gzrows(path):
    return [json.loads(line) for line in gzip.decompress(read(path)).splitlines() if line]

def load_inputs():
    digest = gzrows(ROOT / 'artifacts/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/window_digest.jsonl.gz')
    census = {row['key']: row for row in gzrows(ROOT / 'artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz')}
    older = json.loads(read(ROOT / 'research/CARRY-BOUND-20261114-001/referee-R1/codex/grow_sample.json'))
    return digest, census, older

def separators(blank_count):
    n = blank_count + 4
    clauses = []
    for j in range(n - 2):
        clauses.extend(([j + 1, j + 2, j + 3], [-(j + 1), -(j + 2), -(j + 3)]))
    _, allowed = __import__('growth_core').projection(clauses, [0, 1, n - 2, n - 1])
    return allowed

def shape(defs, masks, S, wrapper):
    """Check the hypotheses of the earlier referee's global finite-support lemma."""
    size, body = old.flatten(defs, S)
    assert defs[S][0] == 3 and size == 4
    steps = [args for c, args in body if c == S]
    constraints = [(c, args) for c, args in body if c != S]
    assert len(steps) == 1 and constraints
    supports = []
    for c, args in constraints:
        if c != 'K':
            assert defs[c][0] == old.flatten(defs, c)[0] == 3
            assert masks[c] == {1, 2, 3, 4, 5, 6}
        assert len(set(args)) == 3 and 3 in args
        supports.append(frozenset(args))
    assert len(set(supports)) == 1
    live = sorted(supports[0] - {3})
    step = steps[0]
    new_at = [j for j in live if step[j] == 3]
    carried_old = [step[j] for j in live if step[j] != 3]
    assert len(new_at) == len(carried_old) == 1 and carried_old[0] == new_at[0]
    assert masks[S] == set(range(8))
    other = {i for i, d in enumerate(defs) if i != S and any(c == 'SELF' for c, _ in d[2])}
    assert all(old.flatten(defs, i)[0] == defs[i][0] for i in other)
    if wrapper:
        main_size, main_body = old.flatten(defs, len(defs) - 1)
        assert main_size == defs[-1][0]
        assert all(c == 'K' or c == S for c, _ in main_body)
        assert all(len({a[j] for j in live}) == 2 for c, a in main_body if c == S)
    assert separators(2) == list(range(16))
    assert len(separators(1)) < 16
    return {'live_positions': live, 'next_arguments': list(step),
            'one_NAE_consecutive_triple_chain_per_wrapper_entry': True,
            'two_blank_separator_all_16_assignments': True,
            'one_blank_negative_control_rejected': True}

def cell(family, census, depth, cutoff, seconds, max_size, label, global_shape=False):
    begin = time.monotonic()
    key = family['key']
    S = census['S']
    defs = old.usual(json.loads(key))
    masks, history = old.limits(defs)
    row = {'sample': label, 'key': key, 'key_sha256': hashlib.sha256(key.encode()).hexdigest(),
           'S': S, 'wrapper': family['wrapper'],
           'absolute_depth': depth, 'S_call_length': depth - int(family['wrapper']),
           'cutoff': cutoff, 'time_cap_seconds': seconds, 'size_cap': max_size,
           'recorded_verdict': family.get('verdict'), 'recorded_G_r': family.get('G_r'),
           'recorded_caps': family.get('caps'), 'boundary_port_masks': [sorted(g) for g in masks],
           'limit_history': history,
           'scope': 'all covered S targets at the stated absolute depth; every member allocated in the entire explicit prefix is eligible',
           'global_exact': False}
    if global_shape:
        row['global_closure_shape'] = shape(defs, masks, S, family['wrapper'])
    # Refuse exponential allocations before constructing them.
    c = family.get('c', 1)
    predicted_copies = (cutoff + 1 if c == 1 else (c ** (cutoff + 1) - 1) // (c - 1))
    if predicted_copies * max(1, census.get('s_block_size', 20)) > 120000:
        row.update(status='construction_cap', predicted_size_proxy=predicted_copies * max(1, census.get('s_block_size', 20)))
        return row
    clauses, n, roots, targets, copies, origin, boundary = old.unfold(defs, masks, S, cutoff, depth)
    row.update(variables=n, clauses=len(clauses), copies=len(copies),
               targets=len(targets), roots=sorted(roots), boundaries=len(boundary))
    if n > 10000 or len(clauses) > 80000:
        row.update(status='construction_cap')
        return row
    search = old.DirectSearch(clauses, n, roots, targets, seconds,
                              old.preferred_pools(copies, roots, S, depth))
    try:
        row.update(search.run(max_size=min(max_size, n), seeds=min(90, 20 + n // 3)))
        row['status'] = 'exact_prefix' if row['minimum'] is not None else 'lower_bound_only_prefix'
        if row.get('witness'):
            row['verification'] = verify(clauses, row['witness'], roots, targets)
            row['witness_origins'] = [origin.get(v, {'root_port': v}) for v in row['witness']]
            row['witness_target_members'] = sorted(set(row['witness']) & targets)
            row['deepest_witness_member'] = max((origin[v]['depth'] for v in row['witness'] if v in origin), default=0)
            if row['minimum'] <= 3:
                # Every possible smaller 2-bond consists exactly of one root
                # and one target, both already in this prefix. No arbitrary
                # third member beyond the prefix can make a smaller bond.
                row['global_exact'] = True
                row['global_reason'] = 'minimum at most 3; all root-target pairs are present and exhaustively tested, and every singleton is full by living complement closure'
                row['status'] = 'exact_global'
            if global_shape:
                # A hypothetical smaller root-containing bond has k <= B-1
                # members and therefore deepest absolute depth <=2k-3+wrapper.
                radius = 2 * row['minimum'] - 5 + int(family['wrapper'])
                row['all_smaller_bonds_depth_radius'] = radius
                row['global_exact'] = cutoff >= radius
                if row['global_exact']:
                    row['status'] = 'exact_global'
            if row.get('recorded_G_r'):
                row['recorded_growth_lower_bound'] = 2 + row['S_call_length'] // row['recorded_G_r']
                row['does_not_violate_recorded_lower_bound'] = row['minimum'] >= row['recorded_growth_lower_bound']
    except old.SearchTimeout:
        row.update(status='timeout', minimum=None, by_size=search.by_size,
                   proved_lower_bound_prefix=max([r['size'] + 1 for r in search.by_size if r['exhausted']] + [2]))
    finally:
        row.update(seconds=time.monotonic() - begin, queries=search.queries,
                   iterations=search.iterations, models=len(search.models),
                   peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        search.close()
    return row

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['simple', 'other', 'unresolved'], default='simple')
    parser.add_argument('--cases', default='0,5')
    parser.add_argument('--ids', default='2c048723bc85,a4b93391c243,714cdee7811a,d418f587a3d6')
    parser.add_argument('--depths', default='7,8,10,12')
    parser.add_argument('--seconds', type=float, default=45)
    parser.add_argument('--size', type=int, default=11)
    parser.add_argument('--halo', type=int, default=2)
    parser.add_argument('--out', default='growth_simple.jsonl')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    digest, census, older = load_inputs()
    if args.mode == 'unresolved':
        families = [(i, next(r for r in digest if r['key_sha256'].startswith(i))) for i in args.ids.split(',')]
    else:
        families = [(int(i), older[int(i)]) for i in args.cases.split(',')]
    out = HERE / args.out
    assert not out.exists(), 'Use a fresh owned output path; never overwrite a prior run'
    for label, family in families:
        for depth in map(int, args.depths.split(',')):
            cutoff = depth + args.halo
            if args.mode == 'simple':
                cutoff = max(cutoff, 2 * args.size - 5 + int(family['wrapper']))
            row = cell(family, census[family['key']], depth, cutoff,
                       args.seconds, args.size, label, args.mode == 'simple')
            with out.open('a') as f:
                f.write(json.dumps(row, sort_keys=True) + '\n')
            print(json.dumps({k: row.get(k) for k in ['sample', 'absolute_depth', 'S_call_length', 'cutoff', 'variables', 'minimum', 'status', 'global_exact', 'seconds']}), flush=True)
    meta = {'sources_sha256': sources(), 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'python': sys.executable, 'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'args': vars(args)}
    (HERE / (args.out + '.meta.json')).write_text(json.dumps(meta, indent=2, sort_keys=True) + '\n')

if __name__ == '__main__':
    main()
