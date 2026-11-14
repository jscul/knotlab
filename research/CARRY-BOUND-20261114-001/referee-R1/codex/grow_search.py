"""Exact finite-prefix least bonds, using only unfolded CNF and direct SAT.

No producer Python, call relation, composition, semigroup, window or path DP
is imported. 'exact' qualifies the stated finite member universe; the allowed
states on it are the infinite pattern's exact projection by boundary limits.
"""
import argparse
import json
import resource
import time
from grow_core import (ROOT, HERE, READS, rows, read, usual, limits, flatten,
                       unfold, preferred_pools, DirectSearch, SearchTimeout, controls)


def population():
    path = ROOT / 'artifacts/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/window_digest.jsonl.gz'
    digest = rows(path)
    grows = [r for r in digest if r['verdict'] == 'growing']
    keys = {r['key'] for r in grows}
    census = {r['key']: r for r in rows(ROOT / 'artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz') if r['key'] in keys}
    grows.sort(key=lambda r: (census[r['key']]['s_block_size'], r['c'],
                              len(json.loads(r['key'])), r['G_r'] or 99, r['key']))
    selected = grows[:8]
    for gap in (1, 2, 3):
        extra = next(r for r in grows if r['G_r'] == gap and r not in selected)
        selected.append(extra)
    for gap in (1, 2, 3):
        extra = next(r for r in grows if r['G_r'] == gap and r['c'] >= 2 and r not in selected)
        selected.append(extra)
    return selected, census


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cases', default='0,1,2,3,4,5,6,7')
    parser.add_argument('--depths', default='1,2,3,4,5,6')
    parser.add_argument('--halo', type=int, default=2)
    parser.add_argument('--seconds', type=float, default=30)
    parser.add_argument('--max-size', type=int, default=9)
    parser.add_argument('--out', default='grow_results.jsonl')
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    if args.controls:
        result = controls()
        (HERE / 'grow_controls.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result), flush=True)
        return
    selected, census = population()
    (HERE / 'grow_sample.json').write_text(json.dumps(selected, indent=2) + '\n')
    for index in map(int, args.cases.split(',')):
        family = selected[index]
        defs = usual(json.loads(family['key']))
        G, history = limits(defs)
        S = census[family['key']]['S']
        for s in map(int, args.depths.split(',')):
            begin = time.monotonic()
            clauses, n, roots, targets, copies, origin, boundary = unfold(defs, G, S, s + args.halo, s)
            rec = {'case': index, 'key': family['key'], 'sha': family['key_sha256'][:12],
                   'S': S, 'depth': s, 'halo': args.halo, 'cutoff': s + args.halo,
                   'r': family['G_r'], 'wrapper': family['wrapper'],
                   'claimed_bound': 2 + (s - int(family['wrapper'])) // family['G_r'],
                   'variables': n, 'clauses': len(clauses), 'copies': len(copies),
                   'target_count': len(targets), 'boundary_count': len(boundary),
                   'boundary_port_masks': [sorted(g) for g in G], 'limit_history': history,
                   'scope': 'all members in explicit prefix, exact projection of infinite allowed states'}
            pools = preferred_pools(copies, roots, S, s)
            search = DirectSearch(clauses, n, roots, targets, args.seconds, pools)
            try:
                rec.update(search.run(max_size=min(args.max_size, n), seeds=min(90, 20+n//3)))
                rec['status'] = 'exact' if rec['minimum'] is not None else 'lower_bound_only'
                if rec.get('witness'):
                    rec['witness_origins'] = [origin.get(v, {'root': v}) for v in rec['witness']]
                    rec['claimed_bound_holds'] = rec['minimum'] >= rec['claimed_bound']
            except SearchTimeout:
                rec.update(status='timeout', minimum=None, by_size=search.by_size,
                           proved_lower_bound=max([r['size'] + 1 for r in search.by_size if r['exhausted']] + [2]))
            finally:
                rec.update(seconds=round(time.monotonic()-begin, 4), queries=search.queries,
                           iterations=search.iterations, models=len(search.models),
                           peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
                search.close()
            with (HERE / args.out).open('a') as f:
                f.write(json.dumps(rec, sort_keys=True) + '\n')
            print(json.dumps({k: rec.get(k) for k in ('case', 'sha', 'depth', 'halo', 'variables', 'minimum', 'proved_lower_bound', 'claimed_bound', 'status', 'seconds')}), flush=True)
    (HERE / 'grow_inputs.json').write_text(json.dumps(READS, indent=2) + '\n')


if __name__ == '__main__':
    main()
