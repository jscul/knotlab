"""Cross-check the units used in the report against the independent row archives."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
from time import perf_counter

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE/name).read_text())


def records(name):
    with gzip.open(HERE/name,'rt') as src:
        yield from map(json.loads,src)


def counts(pilot):
    cohort = {87,90,2030,3609} if pilot else None
    stages = [r for r in records('stages.jsonl.gz') if cohort is None or r['start'] in cohort]
    strong = read('other_bonds_summary.json')
    round_six = {r['census_entry']:r['witness_knot_ids'] for r in records('census_six.jsonl.gz')}
    distinct = {'all':set(),'checked':set()}
    occurrences = Counter()
    stage_count = Counter()
    round_six_matches = 0
    qualifying_with_all_laws = set()
    weighted_chains = Counter()
    for stage in stages:
        k = stage['start']
        age = stage['round']
        all_chains = stage['all_chains']
        prefix = stage['checked_chains']
        assert prefix == all_chains[:3]
        stage_count[age] += bool(all_chains)
        for label, items in (('all',all_chains),('checked',prefix)):
            occurrences[label] += len(items)
            distinct[label].update((k,tuple(sorted(ch))) for ch in items)
        weighted_chains['checks_on_stages_with_more_than_eight_laws'] += len(prefix)*(len(stage['supports'])>8)
        if age == 6:
            assert (k in round_six) == bool(all_chains)
            if all_chains:
                assert round_six[k] in all_chains
                round_six_matches += 1
        for run in stage['recorded'].get('mapped',()):
            if run['a step'] and run['every chain law needed']:
                qualifying_with_all_laws.add(k)
    finite = read('record_check.json')['census']['rounds']['all']['6']
    census = read('census_six.json')['totals']
    assert finite['holds_chain']==len(round_six)==census['certified_starts']==census['chain_positive']
    assert finite['stages']==census['grew_through_six']
    result={'stage_roster':len(stages),'sample_starts':len({r['start'] for r in stages}),
            'chain_occurrences':dict(occurrences),'distinct_start_and_knot_sets':{k:len(v) for k,v in distinct.items()},
            'sample_chain_positive_stages_by_round':stage_count,'other_laws_present':weighted_chains,
            'round_six_census_certificates_matching_sampled_chain_supports':round_six_matches,
            'sample_starts_with_any_archived_step_needing_all_eight':len(qualifying_with_all_laws)}
    if not pilot:
        a=read('stage_readings_omitted_summary.json')
        rows=a['stage_scope_counts']
        assert rows['all']['chain_occurrences']==occurrences['all']
        assert rows['originally_checked']['chain_occurrences']==occurrences['checked']
        assert rows['additional']['chain_occurrences']==occurrences['all']-occurrences['checked']
        for key,v in rows['all'].items():
            assert v==rows['originally_checked'][key]+rows['additional'][key]
        assert strong['counts']['all']['checked_chains']==occurrences['checked']
        assert strong['counts']['6']['starts_holding_all_checks_on_checked_chains']==round_six_matches
        assert not read('converse.json')['converse_differences']
        result['three_chain_limit_vs_all']=rows
        result['complete_census_round_six']=census
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--pilot',action='store_true')
    args=parser.parse_args()
    begin=perf_counter()
    result=counts(args.pilot)
    result['seconds']=round(perf_counter()-begin,3)
    filename='report_counts_pilot.json' if args.pilot else 'report_counts.json'
    (HERE/filename).write_text(json.dumps(result,indent=2)+'\n')
    print(filename,result['distinct_start_and_knot_sets'],result['seconds'])
