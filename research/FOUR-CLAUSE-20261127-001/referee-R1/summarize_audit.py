"""Combine start, stage and pattern counts without changing their weightings."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    return json.loads((HERE/name).read_text())


def rate(n,m):
    return {'positive':n,'total':m,'percent':round(100*n/m,5)}


def main():
    small = load('read_stages_0.json')['rows']
    large = [json.loads(s) for s in (HERE/'omitted_stages.jsonl').read_text().splitlines()]
    other = load('alternative_full.json')
    starts = {r['start'] for r in small}
    grown = {r['start'] for r in small if r['round']}
    read = [r for r in small if 'bonds' in r]
    checked = {r['start'] for r in read if r['round']}
    key = 'a birth needed, proper, free, not read at one lower bond'
    old_pos = {r['start'] for r in read if r[key]}
    new_pos = {r['start'] for r in large if r['first_step_needing_a_birth']}
    other_pos = set(other['distinct starts with any new birth-essential positive'])
    always = old_pos | new_pos
    active = [r for r in large if r['patterns']]
    direct = load('direct_crosscheck.json')
    chain = load('common_source.json')['opportunities']['stages_with_at_least_one_chain']
    assert {(r['start'],r['round']) for r in small if 'bonds' not in r} == {(r['start'],r['round']) for r in large}
    assert {(r['start'],r['round']) for r in read} == {(r['start'],r['round']) for r in other['rows']}
    assert {r['census_entry'] for r in direct} == new_pos
    assert {r['start'] for r in chain} == always
    assert not load('read_counts.json')['archive_field_mismatches']
    assert new_pos <= checked
    assert not (other_pos & old_pos)
    small_roles = sum(r[key] for r in read)
    large_roles = sum(len(p['qualifying_roles']) for r in active for p in r['patterns'])
    assert sum(r['matched_roles_and_all_individual_deletions'] for r in direct) == large_roles
    report = {
        'target':'Four single-word exclusions on six disjoint two- or three-distinction agreement carriers forbid upper 111 with one signed pair read both and two read either. Count birth-essential steps with free upper pairs and no determination by a defining lower bond.',
        'original_alternating_starts':rate(len(old_pos),len(checked)),
        'omitted_alternating_stages':rate(len(active),len(large)),
        'completed_alternating_original_roster':rate(len(always & checked),len(checked)),
        'completed_alternating_funded_starts':rate(len(always),len(grown)),
        'completed_alternating_all_starts':rate(len(always),len(starts)),
        'original_starts_with_any_qualifying_four_clause_assignment':rate(len(old_pos | other_pos),len(checked)),
        'original_alternating_patterns':sum(r['patterns'] for r in read),
        'omitted_alternating_patterns':sum(len(r['patterns']) for r in active),
        'original_and_omitted_alternating_qualifying_roles':[small_roles,large_roles],
        'original_qualifying_roles_with_non_alternating_assignments_added':small_roles + other['counts']['three and one birth-essential steps'],
        'positive_census_entries':{'original_alternating':sorted(old_pos),'omitted_alternating':sorted(new_pos),
                                   'other_assignment_on_original_stages':sorted(other_pos)},
        'minimum_original_F2_successes':load('record_counts.json')['archive']['F2_min_starts'],
        'all_funded_stage_count':len(small),'originally_read_stage_count':len(read),
        'stages_with_eight_law_chain':len(chain),
    }
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
