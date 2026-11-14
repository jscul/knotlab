"""Fresh target-type census; only the previous independent referee is reused.

No study Python is read or imported.  Inlining stops at self-holding calls;
the dependency closure is then followed through those retained calls.
"""
import collections
import gzip
import hashlib
import importlib.util
import json
import resource
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PREV = ROOT / 'research/FREE-TARGET-20261114-001/referee-R1/codex/relations_audit.py'
spec = importlib.util.spec_from_file_location('independent_referee', PREV)
ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ref)
CENSUS = ROOT / 'artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz'
RESULTS = ROOT / 'experiments/CENSUS-FORGET-20261114-001A/CENSUS-FORGET-20261114-001A-E001_forget_census/full/results.jsonl'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    with RESULTS.open() as f:
        results = {r['case']: r['result'] for r in map(json.loads, f)}
    selected = {key: r for key, r in results.items()
                if r['c'] == 1 and not r['chain']}
    assert len(selected) == 657
    census = {}
    with gzip.open(CENSUS, 'rt') as f:
        for row in map(json.loads, f):
            if row['key'] in results:
                census[row['key']] = row
    records = []
    for key, result in sorted(selected.items()):
        row = census[key]
        defs = ref.usual(json.loads(key))
        S, main_id = row['S'], len(defs) - 1
        types = set(ref.self_types(defs))
        blocks = {i: ref.flatten(defs, i) for i in types | {main_id}}

        # A separate raw-call calculation checks the inlining/closure count.
        # No flattened variable mapping is used in this independent check.
        def raw_reach(i):
            seen, queue = set(), [i]
            while queue:
                j = queue.pop()
                if j in seen:
                    continue
                seen.add(j)
                queue.extend(c for c, _ in defs[j][2] if isinstance(c, int))
            return seen

        def raw_flat_own(i):
            return defs[i][1] + sum(raw_flat_own(c) for c, _ in defs[i][2]
                                    if isinstance(c, int) and c not in types)

        for i in blocks:
            assert blocks[i][0] - defs[i][0] == raw_flat_own(i)

        def reach(start):
            pending, visited = [start], set()
            while pending:
                i = pending.pop()
                if i in visited:
                    continue
                visited.add(i)
                pending.extend(c for c, _ in blocks[i][1] if c != 'K' and c not in visited)
            return visited

        from_S, from_main = reach(S), reach(main_id)
        assert (from_S & types) == (raw_reach(S) & types)
        assert (from_main & types) == (raw_reach(main_id) & types)
        others = sorted((from_S | from_main) & types - {S})
        details = []
        for i in others:
            size, calls, owners = blocks[i]
            details.append({'definition': i, 'arity': defs[i][0],
                            'raw_own': defs[i][1], 'inlined_own': size - defs[i][0],
                            'reachable_from_S': i in from_S,
                            'reachable_from_main': i in from_main,
                            'inlined_calls': [[c, list(a)] for c, a in calls]})
        records.append({'key': key, 'key_sha256': hashlib.sha256(key.encode()).hexdigest(),
                        'S': S, 'main': main_id, 'main_equals_S': S == main_id,
                        'verdict': result['verdict'], 'r': result['r'],
                        's_size': blocks[S][0], 'main_size': blocks[main_id][0],
                        'other_definitions': details,
                        'has_other_own': any(d['inlined_own'] for d in details),
                        'has_other_own_from_S': any(d['inlined_own'] and d['reachable_from_S'] for d in details),
                        'has_other_own_from_main': any(d['inlined_own'] and d['reachable_from_main'] for d in details),
                        'L_ray': row['L_ray'], 'lambda': row['lambda']})
    summary = {'families': len(records),
               'certified': sum(r['verdict'] == 'certified' for r in records),
               'counts': {}}
    for group in ('all', 'certified', 'non-forgetting'):
        rs = records if group == 'all' else [r for r in records if r['verdict'] == group]
        summary['counts'][group] = {
            'families': len(rs),
            'other_own': sum(r['has_other_own'] for r in rs),
            'other_own_from_S': sum(r['has_other_own_from_S'] for r in rs),
            'other_own_from_main': sum(r['has_other_own_from_main'] for r in rs),
            'no_other_own': sum(not r['has_other_own'] for r in rs),
            'wrapper_main': sum(not r['main_equals_S'] for r in rs),
            'other_own_r_counts': dict(collections.Counter(r['r'] for r in rs if r['has_other_own'])),
        }
    # Quantify the inherited wrapper correction over all reported certificates.
    certified_wrappers = collections.Counter()
    all_certificate_scope = collections.defaultdict(collections.Counter)
    additional_scope_records = []
    delayed_S_records = []
    for key, r in results.items():
        if r['verdict'] != 'certified':
            continue
        defs = ref.usual(json.loads(key))
        main_id = len(defs) - 1
        if main_id not in ref.self_types(defs):
            certified_wrappers['all'] += 1
            certified_wrappers['chain' if r['chain'] else 'nonchain'] += 1
        S = census[key]['S']
        types = set(ref.self_types(defs))
        blocks = {i: ref.flatten(defs, i) for i in types | {main_id}}
        visited, pending = set(), [main_id, S]
        while pending:
            i = pending.pop()
            if i in visited:
                continue
            visited.add(i)
            pending.extend(c for c, _ in blocks[i][1] if c != 'K' and c not in visited)
        other_own = [i for i in sorted(visited & types - {S})
                     if blocks[i][0] > defs[i][0]]
        def can_reach_S(i, seen=None):
            seen = set() if seen is None else seen
            if i in seen:
                return False
            seen.add(i)
            return any(c == S or can_reach_S(c, seen)
                       for c, _ in blocks[i][1] if c != 'K' and c != i)
        delaying_types = [i for i in sorted(visited & types - {S}) if can_reach_S(i)]
        stratum = 'chain' if r['chain'] else ('c>=2' if r['c'] >= 2 else 'c=1 other')
        group = all_certificate_scope[stratum]
        group['families'] += 1
        group['other_own' if other_own else 'no_other_own'] += 1
        if delaying_types:
            group['other_recursion_can_delay_S'] += 1
            if not other_own:
                group['no_other_own_but_delayed_S'] += 1
            delayed_S_records.append({'key': key, 'S': S, 'main': main_id,
                'stratum': stratum, 'r': r['r'], 'delaying_types': delaying_types,
                'has_other_own': bool(other_own)})
        if other_own:
            additional_scope_records.append({'key': key, 'S': S, 'main': main_id,
                'stratum': stratum, 'r': r['r'], 'other_own_types': other_own})
    payload = {'summary': summary, 'certified_wrappers': dict(certified_wrappers),
               'all_certificate_scope': {k: dict(v) for k, v in all_certificate_scope.items()},
               'all_certified_with_other_own': additional_scope_records,
               'all_certified_with_delayed_S': delayed_S_records,
               'families': records,
               'input_sha256': {str(p.relative_to(ROOT)): digest(p) for p in (CENSUS, RESULTS, PREV)},
               'seconds': time.monotonic() - started,
               'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (OUT / 'target_inventory.json').write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps({'summary': summary, 'certified_wrappers': dict(certified_wrappers),
                      'seconds': payload['seconds']}, indent=2))


if __name__ == '__main__':
    main()
