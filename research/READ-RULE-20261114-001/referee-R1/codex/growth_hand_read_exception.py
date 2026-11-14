"""Parent-suggested read-but-killed-by-exception family, direct CNF only.

The opposite tie belongs to main, rather than tying an own S distinction to
a main port. This avoids the exact failure of the advisor's Q3 family.
"""
import hashlib
import json
import resource
import sys
import time
from pathlib import Path
from growth_core import ROOT, HERE, old, verify, sources
from growth_search import cell

def definitions(gadget):
    S = [3, 2, [['K', [0, 3, 1]], ['K', [2, 3, 4]], ['SELF', [0, 1, 3]]]]
    if gadget:
        main = [3, 3, [['K', [0, 1, 3]], ['K', [0, 1, 4]],
                       ['K', [0, 1, 5]], ['K', [3, 4, 5]], [0, [0, 1, 2]]]]
    else:
        main = [3, 0, [['K', [0, 1, 1]], [0, [0, 1, 2]]]]
    return [S, main]

def main():
    begin = time.monotonic()
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    result = {'rows': [], 'construction_author': 'parent referee suggested wrapper placement of the opposite tie',
              'scope': 'living finite-key S-only covered targets; no other recursive definition',
              'proposed_uniform_value': 'L(d)=d+2, where d is absolute S-copy depth and S-call length is d-1',
              'scripts_use_per_call_relations': False}
    for gadget in (False, True):
        variant = 'main_positive_gadget' if gadget else 'main_repeated_argument'
        raw = definitions(gadget)
        key = json.dumps(raw, separators=(',', ':'))
        family = {'key': key, 'wrapper': True, 'c': 1, 'verdict': 'synthetic converse attack'}
        defs = old.usual(raw)
        masks, history = old.limits(defs)
        assert masks[0] == set(range(8))
        assert masks[1] == {1, 2, 5, 6}
        for depth in range(1, 7):
            # The explicit d+2 upper witness is checked below. Ask the exact
            # search only to exclude all smaller supports, avoiding an
            # unnecessary positive-witness CEGAR search at the top size.
            row = cell(family, {'S': 0, 's_block_size': 5}, depth, depth + 2,
                       60, depth + 1, variant)
            assert row.get('minimum') is None, row
            lower = row.get('proved_lower_bound', row.get('proved_lower_bound_prefix', 2))
            assert lower >= depth + 2, row
            clauses, n, roots, targets, copies, origin, boundary = old.unfold(
                defs, masks, 0, depth + 2, depth)
            path = sorted((c for c in copies if c['definition'] == 0), key=lambda c: c['depth'])
            target = next(c for c in path if c['depth'] == depth)
            # The attained witness contains r, one pendant at each of the d
            # constraints from r to this copy, and the copy's own x.
            explicit = [2] + [c['own'][1] for c in path if c['depth'] <= depth] + [target['own'][0]]
            row['explicit_chain_witness'] = explicit
            row['explicit_chain_witness_check'] = verify(clauses, explicit, roots, targets)
            row['minimum'] = depth + 2
            row['finite_minimum_method'] = 'exact exclusion of every smaller support plus independently enumerated explicit upper witness'
            row['root_p_target_x_projection'] = verify(clauses, [0, target['own'][0]], roots, targets, require=False)
            row['root_q_target_x_projection'] = verify(clauses, [1, target['own'][0]], roots, targets, require=False)
            assert len(row['root_p_target_x_projection']['allowed']) == 4
            assert len(row['root_q_target_x_projection']['allowed']) == 4
            # The p-q bond exists, but it fails the covered-own endpoint gate.
            wrong = verify(clauses, [0, 1], roots, targets, require=False)
            assert not wrong['is_bond'] and not wrong['endpoints_valid']
            row['main_tie_wrong_target_control_rejected'] = True
            row['NAE_a_x_b_always_vacuous'] = True
            row['uniform_global_argument'] = 'After the forced p!=q tie, the allowed system factors into the main tie/gadget component and the one-link chain NAE(r,x0,w0), NAE(x0,x1,w1), ... . Any bond crossing d links must include each earlier pendant w, since omitting one makes that link existentially full and separates root and target. Root r together with all d pendants is still shattered, so another distinction is required. The explicit witness of d+2 members attains this.'
            row['global_exact'] = True
            row['global_reason'] = 'uniform factorization and pendant-count argument, independently checked finite direct minimum'
            row['status'] = 'exact_global_by_explicit_argument'
            result['rows'].append(row)
            print(json.dumps({k: row.get(k) for k in ['sample', 'absolute_depth', 'S_call_length', 'minimum', 'status', 'seconds']}), flush=True)
    result.update(counterexample_to_syntactic_unread_necessity=True,
                  counterexample_to_exception_free_R=False,
                  counterexample_to_dichotomy=False,
                  classification='fresh mathematical counterexample candidate with explicit uniform argument; no lifecycle promotion',
                  all_twelve_direct_minima_match_d_plus_two=True,
                  sources_sha256=sources(),
                  imported_growth_search_sha256=hashlib.sha256((HERE / 'growth_search.py').read_bytes()).hexdigest(),
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  seconds=time.monotonic() - begin,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  python=sys.executable)
    result['initial_probe'] = {'source': 'growth_hand_read_exception_initial.py',
                               'status': 'positive-gadget depth6 positive-witness CEGAR timed out after 66.334s, after exhausting all sizes 2 through 7',
                               'lesson': 'Supply the explicit upper witness and use exact search only for smaller-size exclusion; no mathematical value changed.'}
    (HERE / 'growth_hand_read_exception_results.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'all_twelve_direct_minima_match_d_plus_two': True,
                      'seconds': result['seconds'], 'peak_rss_kib': result['peak_rss_kib']}))

if __name__ == '__main__':
    main()
