"""Independent Q3 direct CNF search and exact inequality-gadget check."""
import hashlib
import itertools
import json
import resource
import sys
import time
from growth_core import ROOT, HERE, old, read, verify, projection, controls, sources

def main():
    started = time.monotonic()
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    producer_path = ROOT / 'experiments/READ-RULE-20261114-001B/READ-RULE-20261114-001B-E001_coverage/codex/counterexample.json'
    producer = json.loads(read(producer_path))
    control_records = controls()
    rows = []
    gadgets = {}
    for label, raw in producer['variants'].items():
        key = raw['key']
        defs = old.usual(json.loads(key))
        masks, history = old.limits(defs)
        assert len(defs) == 1 and raw['S'] == 0 and raw['main_equals_S']
        assert masks[0] == set(range(8))
        # Enumerate just the inequality's own finite gadget, independently of
        # the infinite-tail limit and all per-call/window machinery.
        body = json.loads(key)[0][2]
        gadget_calls = body[:1] if label.startswith('a_') else body[:4]
        gadget_vars = sorted({a for _, args in gadget_calls for a in args})
        ext = {(a, u): [] for a, u in itertools.product(range(2), repeat=2)}
        for values in itertools.product(range(2), repeat=len(gadget_vars)):
            env = dict(zip(gadget_vars, values))
            if all(len({env[i] for i in args}) > 1 for _, args in gadget_calls):
                ext[(env[0], env[3])].append({str(i): env[i] for i in gadget_vars})
        assert {pair for pair, xs in ext.items() if xs} == {(0, 1), (1, 0)}
        gadgets[label] = {'key': key, 'key_sha256': hashlib.sha256(key.encode()).hexdigest(),
                          'a_u_extension_counts': {str(pair): len(xs) for pair, xs in ext.items()},
                          'a_u_extensions': {str(pair): xs for pair, xs in ext.items()},
                          'exactly_inequality': True}
        for depth in range(1, 7):
            clauses, n, roots, targets, copies, origin, boundary = old.unfold(
                defs, masks, 0, depth + 2, depth)
            search = old.DirectSearch(clauses, n, roots, targets, seconds=30,
                                      preferred_pools=old.preferred_pools(copies, roots, 0, depth))
            begin = time.monotonic()
            try:
                answer = search.run(max_size=2, seeds=0)
                assert answer['minimum'] == 2
            finally:
                search.close()
            witness = answer['witness']
            check = verify(clauses, witness, roots, targets)
            target_copy = next(c for c in copies if c['definition'] == 0 and c['depth'] == depth)
            explicit = [0, target_copy['own'][0]]
            explicit_check = verify(clauses, explicit, roots, targets)
            assert explicit_check['allowed'] == [1, 2]
            # u, x, w are the first three own distinctions in both variants;
            # w is in exactly one constraint and no SELF arguments.
            pendant_local_index = defs[0][0] + 2
            occurrences = [(c, list(args)) for c, args in defs[0][2]
                           if pendant_local_index in args]
            assert occurrences == [('K', [2, 4, 5])]
            # a and x are free: accepting their pair as a bond would falsely
            # endorse the advisor's reading mechanism.
            free_pair = [0, target_copy['own'][1]]
            free_check = verify(clauses, free_pair, roots, targets, require=False)
            assert not free_check['is_bond'] and len(free_check['allowed']) == 4
            # A supersupport containing the tie cannot pass minimality.
            supersupport = explicit + [target_copy['own'][2]]
            assert not verify(clauses, supersupport, roots, targets, require=False)['is_bond']
            rows.append({'variant': label, 'key': key,
                         'key_sha256': hashlib.sha256(key.encode()).hexdigest(),
                         'S': 0, 'main_equals_S': True,
                         'absolute_depth': depth, 'S_call_length': depth,
                         'cutoff': depth + 2, 'variables': n, 'clauses': len(clauses),
                         'boundary_port_masks': [sorted(m) for m in masks],
                         'limit_history': history, 'minimum': 2,
                         'global_exact': True,
                         'global_reason': 'Witness size 2; complement closure and nonempty usual limit make every singleton full, including members beyond the prefix.',
                         'witness': witness, 'witness_check': check,
                         'explicit_root_a_target_u': explicit,
                         'explicit_check': explicit_check,
                         'witness_origins': [origin.get(v, {'root_port': v}) for v in witness],
                         'a_target_x_shattered_control': free_check,
                         'pendant_w_occurrences': occurrences,
                         'nonminimal_supersupport_rejected': True,
                         'seconds': time.monotonic() - begin})
    result = {'scope': 'READ-RULE-20261114-001 Q3 independent referee',
              'no_per_call_relations_or_window_code_used': True,
              'controls': control_records, 'gadgets': gadgets, 'rows': rows,
              'all_twelve_L_values_equal_two': all(r['minimum'] == 2 for r in rows),
              'Q3_prediction_rejected': True,
              'sources_sha256': sources(),
              'script_sha256': hashlib.sha256(__import__('pathlib').Path(__file__).read_bytes()).hexdigest(),
              'python': sys.executable, 'seconds': time.monotonic() - started,
              'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (HERE / 'q3_results.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: result[k] for k in ['all_twelve_L_values_equal_two', 'Q3_prediction_rejected', 'seconds', 'peak_rss_kib']}))

if __name__ == '__main__':
    main()
