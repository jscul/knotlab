"""Reconcile every literal birth and check each saved world with its actual allocation."""
import gzip
import json

from by_deletion import ARCHIVE, HERE, ROOT, build


def lawful(word, rows, law):
    for row in rows:
        bits = [int(word[i]) for i in row]
        if law == 'parity' and sum(bits) % 2:
            return False
        if law == 'nae' and min(bits) == max(bits):
            return False
    return True


def verify():
    leaf = HERE.name+'A'
    output = ROOT/'artifacts'/leaf/(leaf+'-E001_payment_trace')
    receipts = json.loads((output/'results.json').read_text())['laws']
    raw = json.loads(gzip.decompress((output/'physical_trace.json.gz').read_bytes()))
    sources = json.loads(ARCHIVE.read_text())['both_laws']
    structural = json.loads((HERE/'by_deletion.json').read_text())
    value_witnesses = json.loads((HERE/'same_prefix.json').read_text())
    checked = {}
    for law in ('parity','nae'):
        checked[law] = {}
        for i, (old_key,new_key) in enumerate((('base','plain'),('extra','loaded'))):
            trace = raw[law][new_key]
            source = sources[law]['near_right_spare']['sources'][i]
            assert trace['source'] == source
            predicted, levels = build(source,bool(i))
            saved = structural[law][old_key].copy()
            tested = saved.pop('canonical_relations')
            assert all(row['is_knot'] for row in tested)
            assert [row['arity'] for row in tested] == predicted['arities']
            assert json.loads(json.dumps(predicted)) == saved
            n = 0
            for age, cohort in enumerate(levels,2):
                actual = trace['cohorts'][str(age)]
                assert len(cohort) == len(actual)
                for left,right in zip(cohort,actual,strict=True):
                    for lk,rk in [('knot','knot'),('inputs','paid'),('parents','parents'),('fresh','fresh')]:
                        assert left[lk] == right[rk],(law,age,lk)
                    assert max(right['demand'], 3-len(left['parents']), 1) == len(left['fresh'])
                    n += 1
            h = predicted['first_common']; bank = h['fresh']
            receipt = receipts[law]['arms'][new_key]
            budget = receipt['H_eligible_roster_and_funding']
            assert budget['through_H_before_its_grant'] == predicted['forecast_before_grant']
            assert budget['eligible_group_count'] == budget['actual_fresh_grant'] == len(bank)
            assert budget['arity_based_fresh_minimum'] == 1 and budget['unary_surplus'] == 0
            read = receipt['H_local_holding_and_actual_owners']['name_free_read_at_birth']
            assert read == {'held':2+len(bank),'inherited_shared':2,'own_singly_held':len(bank)}
            slots = {r['knot'] for r in predicted['next_common']}
            assert slots == {r['knot'] for r in levels[-1] if h['knot'] in r['parents']}
            pure = [receipt['both_pure_opportunities'][role]['size_nine_pure_child'] for role in ('left','right')]
            assert pure == predicted['pure_next']
            shortage = receipt['one_short_diagnostic']
            assert shortage['status'] == 'stall' and shortage['shortages'] == [[h['knot'],1]]
            assert shortage['all_size_nine_births_suppressed'] == len(levels[-1])
            controls = receipt['allocation_controls']
            assert controls['coherent_naming_sham']['anonymous_read'] == read
            assert controls['fixed_plan_order_control']['same_completed_cut']
            prefix_world = controls['fixed_lawful_value_word_each_size_before_change']['8']
            prefix_rows = [*source, *(r['inputs']+r['fresh'] for group in levels[:-1] for r in group)]
            assert lawful(prefix_world,prefix_rows,law)
            found_routes = set()
            for r in controls['all_actual_allocation_bijections']:
                routed = {int(k):v for k,v in r['H_to_size_nine_child'].items()}
                assert set(routed) == slots and set(routed.values()) == set(bank)
                found_routes.add(tuple(sorted(routed.items())))
                world = r['complete_size_nine_value_word']
                assert r['both_pure_opportunities_preserved'] and world.startswith(prefix_world)
                assert r['size_nine_births'] == len(levels[-1])
                for later in levels[-1]:
                    inputs = later['inputs'].copy()
                    if later['knot'] in routed:
                        inputs[later['parents'].index(h['knot'])] = routed[later['knot']]
                    assert lawful(world,[inputs+later['fresh']],law)
            independent = value_witnesses[law][old_key]
            independent_routes = {tuple(sorted((child,int(token)) for token,child in assignment.items()))
                                  for assignment in independent['allocation_routes_from_each_H_distinction']}
            assert found_routes == independent_routes
            for word,value_prefix in independent['common_prefix_by_H_fresh_word'].items():
                assert lawful(value_prefix,prefix_rows,law)
                assert word == ''.join(value_prefix[d] for d in bank)
            assert len(independent['common_prefix_by_H_fresh_word']) == 2**len(bank)
            if i:
                assert ((111,231),(118,232),(120,233)) in found_routes
                assert ((111,233),(118,232),(120,231)) in found_routes
                assert receipts[law]['differing_size_nine_common_descendant']['knot'] == 111
                paths = predicted['extra_source_route']
                first = paths['first_payment']['knot']
                assert first == 17 and paths['first_payment']['inputs'] == [27]
                assert first not in paths['size_two_ancestors_of_H']
                assert all(first in paths['size_two_ancestors_of_three_payers'][k] for k in (90,92))
            checked[law][new_key] = dict(physical_births_reconciled=n, eligible_groups_through_H=len(slots),
                    H_allocation_worlds_verified=len(found_routes), all_H_fresh_words=len(independent['common_prefix_by_H_fresh_word']),
                    pure_size_nine_children=pure, total_size_nine_births=len(levels[-1]))
    assert checked['parity'] == checked['nae']
    return checked


if __name__ == '__main__':
    answer=verify()
    (HERE/'verification.json').write_text(json.dumps(answer,indent=2)+'\n')
    print(answer)
